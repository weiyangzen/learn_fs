# sources/distributed-fs/openafs/src/WINNT/afsd/cm_buf.c

## Purpose
`cm_buf.c` implements the Windows cache manager buffer package. It maintains fixed-size cache buffers keyed by AFS FID and file offset, LRU/free queues, dirty-buffer writeback, memory-mapped cache initialization, redirector-held extents, buffer reservation, validation/debug dumps, and checksum helpers. It is the local page cache layer used by directory, vnode, SMB/raw/direct I/O, dcache, and scache synchronization code.

## Important APIs, globals, and functions
Global state includes `buf_globalLock`, `buf_rdrReleaseExtentsLock`, `buf_logp`, `cm_buf_opsp`, and the process-wide `cm_data` cache fields such as buffer counts, hash tables, all/free/dirty/redirector lists, mapped header/data addresses, and counters.

Lifecycle and reference APIs are `buf_Init`, `buf_Shutdown`, `buf_Hold`, `buf_HoldLocked`, `buf_Release`, and `buf_ReleaseLocked`. Lookup/allocation APIs are `buf_FindLocked`, `buf_Find`, `buf_FindAllLocked`, `buf_FindAll`, `buf_GetNewLocked`, `buf_Get`, and `buf_Recycle`.

Dirty/writeback APIs are `buf_SetDirty`, `buf_CleanLocked`, `buf_Clean`, `buf_CleanWait`, `buf_Sync`, `buf_CleanAndReset`, `buf_CleanVnode`, `buf_FlushCleanPages`, `buf_DirtyBuffersExist`, and `buf_Truncate`. Version/invalidation helpers are `buf_InvalidateBuffers` and `buf_ForceDataVersion`.

Capacity and validation APIs are `buf_SetNBuffers`, `buf_AddBuffers`, `buf_ReserveBuffers`, `buf_TryReserveBuffers`, `buf_UnreserveBuffers`, `buf_ValidateBuffers`, `buf_ValidateBufQueues`, `cm_DumpBufHashTable`, and `buf_ForceTrace`.

Redirector integration APIs are `buf_RDRShakeAnExtentFree`, `buf_RDRShakeFileExtentsFree`, `buf_RDRShakeSomeExtentsFree`, `buf_RDRBuffersExist`, `buf_ClearRDRFlag`, `buf_InsertToRedirQueue`, `buf_RemoveFromRedirQueue`, and `buf_MoveToHeadOfRedirQueue`. Checksum helpers are `buf_ComputeCheckSum`, `buf_ValidateCheckSum`, and `buf_HexCheckSum`.

## Control flow
`buf_Init` installs the operation callback table, initializes locks once, and either builds a new mapped buffer pool or reinitializes volatile fields from an existing mapped cache. For a new cache it sizes hash tables, initializes `cm_buf_t` headers and data pointers, adds every buffer to the free/LRU list, and starts a detached incremental sync thread. Existing-cache initialization resets wait/user/error state and cleans up redirector-held extents that survived restart.

`buf_Get` page-aligns the requested offset, tries to find an existing buffer, and otherwise calls `buf_GetNewLocked`. New buffers are removed from the LRU queue, hashed by FID/offset and by FID-only chain, locked, and optionally read through `cm_buf_opsp->Readp`. Short reads are zero-padded and zero-byte reads mark EOF.

`buf_GetNewLocked` scans the LRU tail for a recyclable zero-ref clean buffer. It skips buffers with references, buffers in the same valid chunk as the requester, buffers with active read/write flags, and buffers held by the redirector. Dirty candidates are held, cleaned outside the global lock, then rechecked because another thread may have created the requested buffer. If no buffer is usable and the redirector is initialized, it requests extent releases before sleeping and retrying.

`buf_SetDirty` merges dirty byte ranges within a buffer, records the last writer user, clears EOF, and, for non-redirector writes, adds the buffer to the dirty list with a hold. `buf_IncrSyncer` wakes periodically and calls `buf_Sync`, which walks the dirty list, asks the redirector to return held extents as needed, and invokes `buf_CleanLocked` for online or unknown volumes.

`buf_CleanLocked` resolves or creates the matching scache when needed, obtains callbacks/status through `cm_SyncOp`, calls the configured `Writep` callback over the dirty subrange, and clears dirty state or records `CM_BUF_ERROR` for fatal errors. Transient server/network failures leave dirty data in place unless the request forbids retries.

File-level operations walk the FID-only hash chain. `buf_CleanVnode` returns redirector extents, cleans all dirty buffers for a vnode, and propagates fatal errors. `buf_FlushCleanPages` stabilizes the object before flushing dirty pages and recycles clean pages when refcount permits. `buf_Truncate` zeroes partial tail data or invalidates whole pages past EOF and notifies the redirector when needed.

Redirector queue operations move buffers between the normal LRU/free list and global/per-scache redirector queues. Shake functions batch `AFSFileExtentCB` records and call `RDR_RequestExtentRelease` with per-file or global pressure. `buf_ClearRDRFlag` forcibly removes redirector ownership and releases the associated holds.

## State and persistence behavior
Buffer headers and data live in the mapped cache area described by `cm_data.bufHeaderBaseAddress`, `cm_data.bufDataBaseAddress`, and `cm_data.bufEndOfData`. The buffer cache cannot be resized after creation because the virtual/persistent mapped file contains complex fixed-layout structures.

`cm_buf_t` identity is `(fid, offset)` while hashed; `dataVersion` records the file version represented by the buffer or `CM_BUF_VERSION_BAD` when unknown/invalid. Dirty state is tracked by `CM_BUF_DIRTY`, `dirty_offset`, `dirty_length`, `dirtyCounter`, `error`, and `userp`. Queue membership is tracked separately in `qFlags` (`QINHASH`, `QINLRU`, `QINDL`, `QREDIR`).

The dirty list holds an extra buffer reference until `buf_Sync` removes the clean buffer from the dirty list. Redirector-held buffers are removed from the LRU list, put on redirector queues, counted separately, and also held until returned/cleared.

Some volatile state is reset on existing-cache initialization: user pointer, wait counters, waiting flag, error, redirector queue membership, release timestamps, and bad data version for unrecovered redirector extents.

## Dependencies and integration points
The implementation depends on Windows APIs, pthreads, OpenAFS lock and queue primitives, `cm_data`, `cm_scache_t`, `cm_user_t`, `cm_req_t`, FID helpers, volume lookup/status, scache lookup/status synchronization, server priority updates, event logging, redirector APIs (`RDR_RequestExtentRelease`, `RDR_InvalidateObject`), `cm_buf_ops_t` callbacks for file data read/write/stabilize/unstabilize, optional `DISKCACHE95`, and MD5 from hcrypto.

Major consumers are `cm_dcache.c`, `cm_direct.c`, `cm_dir.c`, `cm_vnodeops.c`, `rawops.c`, SMB/SMB3 handlers, scache synchronization, and redirector code. Those consumers are responsible for setting `CM_BUF_READING`, `CM_BUF_WRITING`, and `cmFlags` consistently around asynchronous fetch/store/write paths.

## Risks and edge cases
The locking hierarchy is strict: reservations, I/O flags, buffer mutex, then `buf_globalLock`. Some recycling paths intentionally grab a buffer mutex while holding the global lock only when refcount is zero; changing that assumption can deadlock.

`buf_RDRBuffersExist` sets a local `found` flag when it sees a redirector-held buffer but returns `0` unconditionally. That appears to defeat its advertised existence test.

`buf_CleanLocked` does not itself set `CM_BUF_WRITING`; lower-level write paths and scache sync code coordinate `CM_BUF_CMSTORING`/`CM_BUF_CMWRITING` and `CM_BUF_WRITING`. New writers must preserve the wait/wakeup contract or `buf_WaitIO` callers can sleep incorrectly.

Dirty writeback clears dirty data on fatal errors to avoid endless retries, records `CM_BUF_ERROR`, and marks the data version bad. This protects liveness but can discard local dirty data after server-side fatal errors; callers need to surface the stored error.

`buf_GetNewLocked` can spin/sleep indefinitely under heavy pinning, redirector retention, or repeated dirty-clean failures. The redirector release path uses `CM_REQ_NORETRY` to return `CM_ERROR_WOULDBLOCK`, but normal paths retry.

The all-buffer and file-hash walkers hold and release buffers while traversing mutable chains. Any change to hash/list mutation must preserve the hold-next-before-release-current pattern.

## Test signals
High-value tests include buffer get/find race where another thread creates the page, LRU recycle after clean zero-ref release, dirty range coalescing, dirty-list hold/release accounting, fatal write error handling, retryable write error preservation, truncate whole and partial page behavior, `buf_FlushCleanPages` stabilization, scache recycle with valid buffers, redirector insert/remove/move queue accounting, extent shake `CM_ERROR_RETRY` and `CM_REQ_NORETRY` behavior, checksum validation, persistent-cache restart cleanup of redirector state, and validation failures from deliberately corrupted queue/hash pointers.
