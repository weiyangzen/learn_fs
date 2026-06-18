# File Research: sources/block-storage/linux-dm/drivers/md/bcache/io.c

`io.c` provides low-level bcache bio helpers and error accounting. The `bbio` helpers allocate metadata bios from the cache-set mempool, initialize them with inline vectors sized for metadata buckets, copy a single pointer from a bkey when needed, set the target cache block device, record submission time, and submit through `closure_bio_submit()`.

The backing-device error path is handled by `bch_count_backing_io_errors()`. It intentionally ignores failed read-ahead bios because md raid recovery/degraded paths can fail speculative read-ahead without implying media failure. Non-read-ahead backing errors increment `cached_dev.io_errors` and call `bch_cached_dev_error()` after the configured device limit.

Cache-device errors are handled by `bch_count_io_errors()`. It implements decaying error accounting with `io_count`, `io_errors`, `error_decay`, and `error_limit`; when errors exceed the limit it escalates to `bch_cache_set_error()`. `bch_bbio_count_io_errors()` also maintains the cache-set congestion signal by comparing elapsed microseconds against read/write congestion thresholds and adjusting `c->congested`.

`bch_bbio_endio()` is the standard completion helper for `bbio` I/O: it updates congestion/error counters, drops the bio reference, and drops the closure. This file is depended on by journal, UUID/prio metadata I/O, request reads, moving GC, and writeback.
