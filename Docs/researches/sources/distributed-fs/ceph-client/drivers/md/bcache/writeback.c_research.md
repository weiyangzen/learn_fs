<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/writeback.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/writeback.c

## Purpose
`writeback.c` implements bcache background writeback: rate control, dirty btree scanning, cache reads, ordered backing writes, dirty-bit clearing, dirty-sector accounting, recovery-time dirty initialization, and writeback thread startup/teardown.

## Important APIs, Types, And Functions
Rate functions include `__calc_target_rate()`, `__update_writeback_rate()`, `set_at_max_writeback_rate()`, `update_writeback_rate()`, and `writeback_delay()`. I/O uses `struct dirty_io`, `read_dirty_submit()`, `read_dirty_endio()`, `write_dirty()`, `dirty_endio()`, and `write_dirty_finish()`. Scanning/accounting uses `read_dirty()`, `dirty_pred()`, `refill_full_stripes()`, `refill_dirty()`, `bcache_dev_sectors_dirty_add()`, `bch_sectors_dirty_init()`, and dirty-init kthreads. Public setup is `bch_cached_dev_writeback_init()` and `bch_cached_dev_writeback_start()`.

## Control Flow
The writeback thread sleeps until dirty data, writeback enablement, or detach requires work. It fills a keybuf with dirty keys, batches contiguous keys, reads dirty data from cache, then uses sequence numbers and closure waits to write to the backing device in order. Completion clears dirty bits through btree insertion and updates success/failure counters. A full clean scan marks the backing superblock clean; detach drains dirty data, clears set UUID/state, writes synchronously, and exits.

## State And Persistence
Runtime state includes writeback rate fields, dirty keybuf, in-flight semaphore, ordering waitlist, delayed work flags, per-stripe dirty counters, full-stripe bitmap, `has_dirty`, writeback kthread, and writeback workqueue. Persistent state transitions are dirty, clean, and detached/none backing superblock states plus clean-key btree metadata updates.

## Dependencies, Integration Points, Risks, And Test Signals
It integrates btree map/insert, keybuf, bio submission, closures, tracepoints, superblock writes, GC, sysfs tunables, and ratelimiting helpers. Risks are data-integrity failures from read/write errors, ordered-write bugs, dirty accounting drift, delayed-work cancellation races, and dirty-init wait-list cleanup. Test fragmented/random/sequential writeback, partial stripes, failures, detach, high-utilization cutoff, idle max rate, GC-after-writeback, dirty recovery, sysfs tuning, and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/writeback.c -->
