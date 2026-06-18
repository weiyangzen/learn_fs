# sources/distributed-fs/openafs/src/afs/afs_memcache.c

## Purpose
`afs_memcache.c` implements the in-memory cache-file backend used when the Cache Manager runs with memory cache instead of UFS cache files. It simulates open/read/write/truncate operations over an array of `struct memCacheEntry` blocks with per-entry locks.

## Important APIs, types, and functions
Core globals are `memCache`, `memCacheBlkSize`, and `memMaxBlkNumber`. `afs_InitMemCache` allocates entries and their initial buffers, initializes per-entry locks, and creates cache file slots. `afs_MemCacheOpen` maps a memory inode number to an entry. Read APIs include `afs_MemReadBlk`, `afs_MemReadvBlk`, and `afs_MemReadUIO`. Write APIs include `afs_MemWriteBlk`, `afs_MemWritevBlk`, and `afs_MemWriteUIO`. `_afs_MemExtendEntry` grows buffers. `afs_MemCacheTruncate` shrinks logical size and can return oversized zero-length buffers to the default block size. `shutdown_memcache` frees data and entries.

## Control flow
Initialization allocates a table of entries and one data buffer per entry, then calls `afs_InitCacheFile` for each logical cache file. Reads take a read lock, clamp requested bytes to available logical size, copy to the destination or iovecs while dropping the AFS global lock around `memcpy`, and return the byte count. Writes take a write lock, grow the data buffer if needed, zero-fill holes between old size and new offset, copy user/iovec data, and extend the logical size to the final offset. UIO paths perform equivalent operations through `AFS_UIOMOVE`.

## State and persistence behavior
Memory cache content is volatile. Each entry tracks logical `size`, allocated `dataSize`, data pointer, and lock. On shutdown, all entry buffers and the entry table are freed only if `cacheDiskType == AFS_FCACHE_TYPE_MEM`.

## Dependencies and integration points
The module depends on OSI allocation/free, AFS locking macros, UIO wrappers from `afs_osi.h`, ICL tracing, cache initialization (`afs_InitCacheFile`), and fetch/store memory-cache paths in `afs_fetchstore.c`.

## Risks and edge cases
`afs_MemCacheOpen` panics on invalid memory block numbers; the range check uses `> memMaxBlkNumber`, so the exact upper boundary deserves attention. Large directory support allows arbitrary entry growth, so memory pressure is a real failure mode. Allocation failure paths must preserve old buffers. Hole zeroing and offset arithmetic must avoid negative or overflowed lengths. Shutdown reinitializes locks just before freeing entries, which is harmless but unusual.

## Test signals
Exercise memory-cache initialization failure cleanup, read/write/readv/writev behavior, sparse writes with zero-filled gaps, UIO read/write offset and resid updates, truncation of oversized zero-length entries, fetch/store through memory cache, and shutdown in both memory and non-memory cache modes.
