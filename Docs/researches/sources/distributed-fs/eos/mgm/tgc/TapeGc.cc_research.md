# sources/distributed-fs/eos/mgm/tgc/TapeGc.cc

## Purpose
Implements the tape-aware garbage collector for one EOS space. It tracks file accesses in an LRU queue and, when space pressure crosses configured thresholds, evicts disk replicas for files that also exist on tape.

## Important APIs, types, and functions
The constructor wires `ITapeGcMgm::getTapeGcSpaceConfig()` into `CachedValue<SpaceConfig>` and initializes `SmartSpaceStats`. `startWorkerThread()` uses an `atomic_flag` to start one worker. `workerThreadEntryPoint()` drains possible evictions then sleeps on `BlockingFlag`. `fileAccessed()` updates the `Lru` queue and logs the first max-queue threshold crossing. `tryToGarbageCollectASingleFile()` is the core policy loop. `getStats()`, `getLruQueueSize()`, `toJson()`, and `diskReplicaQueuedForDeletion()` expose status and update cached free-space accounting.

## Control flow
The worker repeatedly calls `tryToGarbageCollectASingleFile()` until it cannot evict more files, then waits one second or until stopped. A collection attempt loads cached config, queries space stats, returns early if available bytes are high enough or not all expected total bytes are online, pops the least-recently-used fid, reads its size, ignores zero-size or missing metadata as successful queue removal, calls `m_mgm.evictAsRoot(fid)`, and requeues the fid if eviction fails.

## State and persistence behavior
State includes the stop flag, one worker thread, `m_lruQueue` protected by `m_lruQueueMutex`, cached space config and stats, and atomic `m_nbEvicts`. The class itself persists nothing, but `evictAsRoot()` mutates EOS namespace/file replica state asynchronously and `diskReplicaQueuedForDeletion()` updates cached space stats before the next MGM poll.

## Dependencies and integration points
Depends on `ITapeGcMgm` for config, file sizes, and evict command execution; `SmartSpaceStats` for capacity state; `Lru` for access ordering; `SpaceNotFound` for missing spaces; `MaxLenExceeded` for bounded JSON; and EOS logging. `TestingTapeGc.hh` exposes the core collection method for unit tests.

## Risks and test signals
Important edge cases are exception swallowing, lost work if file size lookup fails, indefinite retention if eviction repeatedly fails and requeues the same fid, and thread shutdown joining while an MGM operation is blocked. `toJson()` does not escape string fields. Tests should simulate high/low free-space thresholds, offline total-bytes suppression, missing spaces, zero-size files, missing file size, eviction failure/requeue, successful eviction counter increments, destructor stop behavior, and concurrent `fileAccessed()` with worker eviction.
