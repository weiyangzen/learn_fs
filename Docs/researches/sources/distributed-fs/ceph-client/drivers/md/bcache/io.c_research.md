# sources/distributed-fs/ceph-client/drivers/md/bcache/io.c

Purpose: provides low-level bcache metadata bio allocation/submission helpers and shared I/O error/congestion accounting for cache and backing devices.

Important APIs/functions: `bch_bbio_alloc()` and `bch_bbio_free()` allocate/free `struct bbio` objects from the cache-set metadata bio mempool. `bch_submit_bbio()` copies a single pointer from a key into the bbio and submits it; `__bch_submit_bbio()` submits an already-prepared bbio. `bch_count_backing_io_errors()` counts backing-device failures and ignores failed read-ahead as non-media failures. `bch_count_io_errors()` applies decayed cache-device error accounting and can fail the cache set. `bch_bbio_count_io_errors()` adds latency-based congestion tracking around cache I/O. `bch_bbio_endio()` combines accounting, `bio_put()`, and closure completion.

Control flow: metadata callers allocate an inline bio sized for metadata bucket pages, map pages, set end I/O, and call `bch_submit_bbio()` with the key pointer to target. End I/O paths typically call `bch_bbio_endio()`, which updates errors and releases the closure reference. Cache error accounting decays historical errors every `error_decay` operations by multiplying by 127/128, then adds new errors scaled by `IO_ERROR_SHIFT`.

State and persistence: tracks `bbio->key` and `submit_time_us`, cache-set congestion fields, cache `io_count`/`io_errors`, and backing-device `io_errors`. It does not persist metadata itself, but it is used by B-tree, journal, moving-GC, and request paths that do.

Dependencies/integration: depends on `bcache.h`, `bset.h`, `debug.h`, Linux block APIs, closures, mempools, and cache-set/device error handlers. `btree.c`, `journal.c`, `movinggc.c`, and `request.c` rely on these helpers for consistent metadata I/O behavior.

Risks/test signals: incorrect closure/bio ref handling can hang metadata writes or free bios early. Congestion uses signed deltas from microsecond timestamps and negative counters, so wrap and threshold behavior should be stressed. Backing read-ahead error suppression should be tested with md degraded arrays. Cache set failure thresholds, latency bypass feedback, and `REQ_OP_READ` vs write error messages are important test signals.
