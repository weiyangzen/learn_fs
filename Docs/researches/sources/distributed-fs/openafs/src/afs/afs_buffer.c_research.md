# sources/distributed-fs/openafs/src/afs/afs_buffer.c

Purpose: Implements the directory-buffer package: a small in-memory cache of 2 KiB directory pages backed by dcache files. Directory code uses it to read, create, dirty, flush, zap, and release directory pages without directly managing cache-file I/O.

Important APIs and functions: `DInit` initializes buffers and hash buckets. `DReadWithErrno`/`DRead` fetch an existing directory page and return a `DirBuffer`. `DNew` creates a new page buffer and extends the dcache chunk if needed. `DRelease` drops a buffer reference and marks dirty. `DVOffset` computes the byte offset of a directory pointer. `DZap`, `DFlushDCache`, and `DFlush` invalidate or write dirty buffers. `shutdown_bufferpackage` flushes and frees buffer storage.

Control flow: Reads validate the dcache chunk, search `phTable[pHash(fid,page)]`, promote hits to the bucket front, and increment `lockers` under the global and per-buffer lock hierarchy. Misses call `afs_newslot`, which selects an unlocked least-recently-used buffer or grows by `NPB` buffers up to `afs_max_buffers`, writes any dirty victim to its stored inode, zeros the page, fills the new header, and rehashes it. `DNew` bypasses disk read and updates `chunkBytes` while the caller still holds the dcache lock, avoiding later lock-order inversions.

State and persistence: Volatile globals include `Buffers`, page backing allocations, `phTable`, `nbuffers`, `timecounter`, and `afs_bufferLock`. Dirty pages persist only when written through `afs_CFileWrite` during eviction or flush. Buffer metadata stores the dcache index and a copied `afs_dcache_id_t` inode so dirty writeback can happen without mapping back through dcache tables.

Dependencies and integration points: Depends on `afs_chunkops.h` cache-file operations, dcache metadata, directory package `DirBuffer`, OpenAFS locking, stats, and OS allocation. It is called from directory manipulation paths and shutdown.

Risks: Lock ordering is central: the code documents `afs_bufferLock -> buffer.lock` and deliberately avoids taking dcache locks during flushes. Bugs can cause deadlocks or dirty directory loss. `DZap` relies on `pHash` internals and scans only page hash variants. Physical I/O errors are collapsed to `EIO` unless callers use `DReadWithErrno`. Timecounter wrap temporarily degrades replacement behavior.

Test signals: Read cache hit/miss, short read and physical-error reporting, dirty release then global and per-dcache flush, eviction of dirty victims, all-buffers-locked growth/failure, `DNew` extending `chunkBytes`, zapping all pages for one dcache, shutdown after multiple growth allocations, and lock-order stress with concurrent directory operations.
