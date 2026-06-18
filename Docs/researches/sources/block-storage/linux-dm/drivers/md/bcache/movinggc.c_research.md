# File Research: sources/block-storage/linux-dm/drivers/md/bcache/movinggc.c

`movinggc.c` implements copy/moving garbage collection for cache buckets that are partly used and worth compacting. The selection predicate `moving_pred()` matches bkeys with available pointers into buckets marked `GC_MOVE`.

`bch_moving_gc()` is the main entry point. It exits if copy GC is disabled, then scans buckets under `bucket_lock`, ignoring metadata, empty, full, and pinned buckets. It maintains a heap ordered by sectors used, accumulates the selected live-sector cost, trims selection to the moving-GC reserve capacity, marks selected buckets with `GC_MOVE`, resets the keybuf scan position, and starts the I/O loop.

The I/O loop in `read_moving()` refills `moving_gc_keys`, skips stale keys, allocates a `moving_io` large enough for inline bio vectors, initializes a read bio at idle priority, allocates pages, traces the copy, limits concurrency with `moving_in_flight`, and starts asynchronous read/write closures. Read completion checks for I/O failure and stale clean pointers; write submission uses `bch_data_insert()` with `replace=true`, preserves dirty/csum state, and sets writeback mode when the original key is dirty.

Completion frees bio pages, traces replace collisions, removes the keybuf entry, releases the moving-GC semaphore, and frees the `moving_io`. `bch_moving_init_cache_set()` initializes the cache-set keybuf and a 64-entry semaphore. This file depends on the request insertion path, keybuf infrastructure, btree replacement semantics, and cache bucket GC marks.
