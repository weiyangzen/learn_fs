# sources/distributed-fs/openafs/src/afs/afs_chunkops.h

Purpose: Defines chunk geometry macros and the cache-backend operation vector used to abstract disk, memory, and platform-specific cache storage.

Important APIs and types: Chunk macros include `AFS_CHUNKOFFSET`, `AFS_CHUNK`, `AFS_CHUNKBASE`, `AFS_CHUNKSIZE`, `AFS_CHUNKTOBASE`, `AFS_CHUNKTOSIZE`, and `AFS_SETCHUNKSIZE`. `dslot_state` distinguishes new, unused, and valid dcache slot requests. `struct afs_cacheOps` contains backend callbacks for open/truncate/read/write/close, UIO read/write, dcache slot lookup, volume slot lookup, and link handling. Wrapper macros dispatch through global `afs_cacheType`. Inline helpers copy/reset inode ids and convert an inode id to a trace integer.

Control flow: Runtime behavior is macro-dispatched. Chunk mapping treats chunk zero specially with `afs_FirstCSize`; later chunks use power-of-two `afs_OtherCSize` and `afs_LogChunk`.

State and persistence: The header reads global chunk-size variables and global cache-backend pointer state. It does not persist data itself, but all cache-file I/O and dcache slot retrieval flow through this contract.

Dependencies and integration points: Core dependency for buffer, dcache, memcache, UFS cache, fetch/store, and volume-cache code. Cache backend implementations must fill every function pointer consistently.

Risks: Macros assume chunk sizes are powers of two; invalid values break bitmask and shift calculations. Function-pointer wrappers provide no null checks for `afs_cacheType` or operations. `afs_inode2trace` returns `i->mem`, which is explicitly a tracing hack and may not identify all backend inode forms.

Test signals: Offset-to-chunk boundary tests around first chunk and later chunk boundaries, large-offset tests, configured chunk sizes, every cache backend operation through the wrapper macros, dslot state behavior, and inode copy/reset for each platform inode representation.
