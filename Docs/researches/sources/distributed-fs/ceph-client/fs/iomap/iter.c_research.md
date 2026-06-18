## sources/distributed-fs/ceph-client/fs/iomap/iter.c

Purpose: implements the generic `iomap_iter` state machine used by direct I/O, buffered I/O, fiemap, seeking, swap activation, and other iomap consumers.

Important APIs: `iomap_iter_advance` moves `iter->pos` and reduces `iter->len` with a bounds assertion. `iomap_iter` calls filesystem `iomap_begin` and optional `iomap_end`, resets mapping state between iterations, releases folio batches for `IOMAP_F_FOLIO_BATCH`, and traces destination/source maps.

Control flow: the first call enters `begin` because no current iomap exists. Subsequent calls compute bytes advanced since `iter_start_pos`, call `iomap_end` with the trimmed original mapping range, normalize old positive statuses to `-EIO`, and decide whether to stop on error, zero length, or no progress. Stale mappings (`IOMAP_F_STALE`) may be reprocessed even without progress. A fresh `iomap_begin` then fills `iter->iomap` and `iter->srcmap`.

State and persistence: runtime state lives in `struct iomap_iter`: position, remaining length, status, current mappings, start position, optional folio batch, and caller flags. No durable state is changed directly; persistence semantics are delegated to callers and filesystem ops.

Dependencies and integration points: relies on filesystem `iomap_ops`, public iomap helpers such as `iomap_length` and `iomap_length_trim`, folio-batch lifetime rules, and tracepoints. All iomap clients depend on the progress contract: callers must set `iter.status` or advance the iterator.

Risks and test signals: no-progress loops, stale mapping retry behavior, incorrect `iomap_end` byte counts, and leaked folio batches are primary risks. Test with filesystem callbacks that return holes, stale mappings, short advances, errors after partial progress, and folio-batch mappings.
