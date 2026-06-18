# sources/distributed-fs/beegfs/client_module/source/filesystem/FsFileInfo.c

## Purpose
Implements per-open-file state for BeeGFS client operations: access flags, handle type, append mode, cache hit heuristics, sequential offsets, and entry-lock cleanup markers.

## Important APIs and Functions
`FsFileInfo_init()` and `FsFileInfo_construct()` initialize file-private state. `FsFileInfo_incCacheHits()`/`decCacheHits()` clamp the cache heuristic between configured thresholds. Getters/setters expose append, caching, last read/write offsets, handle type, access flags, and entry-lock usage. `FsFileInfo_getIOInfo()` derives a `RemotingIOInfo` from the associated `FhgfsInode`.

## Control Flow
Open paths allocate and initialize `FsFileInfo`, then file operations update offsets and cache hit counters as reads/writes occur. Remote I/O paths call `FsFileInfo_getIOInfo()` before communicating with storage targets. Cleanup uses the virtual `FsFileInfo_uninit()`, currently a no-op.

## State and Persistence
State is in-memory per file descriptor/open file and disappears on close. `cacheHits`, `allowCaching`, and last offsets are adaptive hints, not persisted. `usedEntryLocking` records whether entry lock methods were used and thus whether close cleanup must unlock remotely.

## Dependencies and Integration Points
Depends on `FsObjectInfo`, `FhgfsInode`, `RemotingIOInfo`, and handle/access flag types. It integrates with file open/close, read/write, cache selection, and lock cleanup paths.

## Risks
The cache heuristic is mutable and likely used without extra locking in file-private contexts; sharing assumptions should remain per-open. `FsFileInfo_getIOInfo()` depends on inode state and remote handle validity. The no-op uninit is correct only while no owned allocations are added.

## Test Signals
Open/close tests for all handle types and access modes, sequential/random read heuristic transitions, append-mode writes, O_DIRECT/cache-disabled behavior, entry-lock cleanup, and remote I/O info population from inodes.
