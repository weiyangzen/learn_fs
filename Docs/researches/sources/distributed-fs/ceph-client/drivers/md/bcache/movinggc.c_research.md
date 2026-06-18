# sources/distributed-fs/ceph-client/drivers/md/bcache/movinggc.c

Purpose: implements moving/copying garbage collection. After normal GC identifies partially used buckets, this code selects the least-full movable buckets, scans matching extents, reads their data, reinserts it elsewhere with replace semantics, and frees the old references through normal B-tree update behavior.

Important APIs/functions: `bch_moving_gc()` is the main entry point called after B-tree GC. `bch_moving_init_cache_set()` initializes the moving-GC keybuf and in-flight semaphore. `moving_pred()` selects keys whose cache bucket has `GC_MOVE` set. `read_moving()` drives the scan/read/insert pipeline. `read_moving_submit()`, `read_moving_endio()`, `write_moving()`, and `write_moving_finish()` are closure stages for each moved extent.

Control flow: `bch_moving_gc()` builds a heap of non-metadata, non-full, unpinned buckets with live sectors, trims the selected set so it fits `RESERVE_MOVINGGC` capacity, marks selected buckets with `GC_MOVE`, resets the keybuf scan to zero, and calls `read_moving()`. For each matching key, `read_moving()` skips already stale pointers, allocates a `moving_io`, reads the old data at idle priority, and chains into `write_moving()`. The write stage sets `replace`, copies the original key as `replace_key`, preserves dirty and checksum flags, and calls `bch_data_insert()`. Completion logs replace collisions, deletes the keybuf entry, releases the in-flight semaphore, and frees the operation.

State and persistence: uses `cache_set->moving_gc_keys`, `moving_in_flight`, `moving_gc_wq`, bucket `GC_MOVE` flags, and normal data insertion/B-tree replacement persistence. Dirty moved extents remain dirty by setting `op->writeback` from the original key.

Dependencies/integration: depends on keybuf scanning in `btree.c`, data insertion in `request.c`, bbio helpers in `io.c`, bucket marks from GC, and tracepoints. It is invoked by `bch_btree_gc()` after bucket marks are finalized.

Risks: the source comment warns that background writeback could stall indefinitely on errors. Moving uses non-journaled replace operations, so correctness depends on collision detection and surrounding GC flush behavior. Reading clean data checks for stale pointers after I/O, but dirty data handling is more sensitive. Test signals include copy-GC enable/disable, bucket-selection reserve math, replace collisions during concurrent writes, stale pointer after read, checksum-preserving moves, dirty writeback moves, and in-flight semaphore throttling.
