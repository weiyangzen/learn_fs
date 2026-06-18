# sources/distributed-fs/openafs/src/ubik/phys.c

## Purpose
Implements the default physical storage backend for ubik database files. It maps ubik file ids to on-disk pathnames, handles header offsets, caches file descriptors, performs read/write/truncate/sync/stat operations, and reads/writes database version labels.

## Important APIs, Types, And Functions
Public callbacks include `uphys_stat`, `uphys_read`, `uphys_write`, `uphys_truncate`, `uphys_getnfiles`, `uphys_getlabel`, `uphys_setlabel`, `uphys_sync`, `uphys_invalidate`, and `uphys_buf_append`. Internal helpers are `uphys_open`, `uphys_close`, `uphys_pread`, `uphys_pwrite`, `uphys_buf_append_open`, and `uphys_buf_flush`. File descriptor state lives in `fdcache[MAXFDCACHE]` and `buf_fdcache`.

## Control Flow
`uphys_open` lazily initializes the fd cache, reuses an idle cached descriptor for the requested file id, or opens/creates `<pathName>.DB[SYS]<id>` and inserts it into a free/reclaimable slot. Data reads/writes add `HDRSIZE` to logical offsets so database labels live in file headers. Labels are stored as `struct ubik_hdr` with network-order version, magic, and header size. Truncate and sync flush any buffered append stream first. `uphys_buf_append` uses a cached `FILE *` in append mode for log writes that can be buffered before an explicit sync.

## State And Persistence
Persistent state is the database files under `adbase->pathName`, including system log files and header labels. Process state includes fd cache entries, refcounts, a single buffered append stream, and a static pathname buffer. `uphys_invalidate` marks cached descriptors stale and closes idle ones.

## Dependencies And Integration Points
This backend is installed in ubik database structures and is called by `disk.c` and `recovery.c`. It depends on POSIX file APIs, optional `pread/pwrite`, LWP include context, `HDRSIZE`, `UBIK_MAGIC`, and ubik version/header definitions.

## Risks And Test Signals
Risks include static global fd caches not keyed by database path, no locking around caches, append stream interaction with descriptor cache, pathname truncation in `pbuffer`, open fallback to read-only while later write paths may fail, and `uphys_getnfiles` hardcoded to one data file. Tests should cover label read/write, logical offset header adjustment, log buffered append followed by sync/truncate, fd cache reuse/invalidate, read-only open failures, crash persistence via fsync, and multiple ubik database instances if supported.
