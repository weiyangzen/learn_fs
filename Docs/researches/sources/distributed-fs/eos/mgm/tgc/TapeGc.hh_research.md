# sources/distributed-fs/eos/mgm/tgc/TapeGc.hh

## Purpose
Declares `TapeGc`, the per-space tape-aware disk-replica garbage collector. It combines an access LRU, cached tape-GC configuration, space statistics, worker-thread lifecycle, and eviction counters.

## Important APIs, types, and functions
Public APIs are construction, destruction, `startWorkerThread()`, `fileAccessed(fid)`, `getStats()`, and `toJson()`. Protected internals include `workerThreadEntryPoint()`, `getLruQueueSize()`, `tryToGarbageCollectASingleFile()`, and `diskReplicaQueuedForDeletion()`. Data members include `ITapeGcMgm&`, `m_spaceName`, `BlockingFlag m_stop`, `m_worker`, `Lru m_lruQueue`, `CachedValue<SpaceConfig> m_config`, `SmartSpaceStats m_spaceStats`, and atomic `m_nbEvicts`.

## Control flow
The header establishes the lifecycle: file-access notifications feed the LRU, `startWorkerThread()` runs the worker once, the worker consults config/stats before popping an LRU fid, and successful evictions update counters and cached space accounting.

## State and persistence behavior
All direct state is process-local and protected by mutexes or atomics. Persistent side effects happen through the MGM abstraction: eviction changes replica state and space queries/config come from external MGM views.

## Dependencies and integration points
Includes EOS logging, namespace/file metadata interfaces, console proto headers, TGC helpers (`BlockingFlag`, `CachedValue`, `Lru`, `SmartSpaceStats`, `SpaceConfig`, `TapeGcStats`), and threading primitives. It is owned by `SpaceToTapeGcMap` and tested through `TestingTapeGc`.

## Risks and test signals
Because copy/move/assignment are deleted, ownership is intentionally unique. Tests should assert worker startup is idempotent, stats are sane after exceptions, lock ordering does not deadlock with `ITapeGcMgm`, and the protected eviction method remains deterministic under a fake MGM.
