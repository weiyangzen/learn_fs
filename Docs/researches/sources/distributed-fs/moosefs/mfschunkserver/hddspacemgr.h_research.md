# sources/distributed-fs/moosefs/mfschunkserver/hddspacemgr.h

## Purpose
`hddspacemgr.h` is the public chunkserver storage interface. It hides disk layout, chunk metadata scanning, damaged/lost/new/changed chunk queues, and all local chunk I/O behind a compact API consumed by `masterconn.c`, `mainserv.c`, `replicator.c`, background jobs, and startup code.

## Important APIs and behavior
Statistics and chart APIs expose byte counters, operation counters, disk health, error counters, and `hdd_sendingchunks()`. Master registration/reporting uses lock-paired query/fill calls for damaged, lost, new, changed, nonexistent, and disk-info data. The comments are important: callers must invoke the matching data function after a count function to release the internal lock.

The data plane consists of `hdd_open()`, `hdd_close()`, `hdd_read()`, `hdd_write()`, `hdd_precache_data()`, `hdd_emergency_read()`, and `hdd_get_chunk_info()`. Mutations are centralized in `hdd_chunkop()`, with macros for delete, create, test, replication-local create/delete, version, truncate, duplicate, and duplicate-truncate. Replication promotes a temporary chunk through `hdd_rep_setversion()`.

## Integration, persistence, and risks
Startup calls `hdd_init()`, optional `hdd_restore()`, then `hdd_late_init()`. Master registration calls `hdd_get_chunks_begin()`, repeated next-list calls, and `hdd_get_chunks_end()`. Persistent state includes chunk files, versions, disk accounting, meta id, and report queues.

Risks center on the lock-pair contract and sentinel-heavy `hdd_chunkop()` arguments. Tests should cover every report path with zero/nonzero counts, invalid macro argument combinations, data-plane error propagation, fsync close behavior, and cleanup/promotion of version-0 replication chunks.
