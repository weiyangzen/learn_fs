<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/writeback.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/writeback.h

## Purpose
`writeback.h` defines bcache writeback constants, dirty-init coordination structs, dirty-sector helpers, writeback admission logic, queue helpers, dirty-state transition helpers, and prototypes.

## Important APIs, Types, And Functions
Constants cover cutoff thresholds, pass limits, rate update limits, auto-GC and fragmentation thresholds, dirty-init thread limits, and writeback share scaling. `struct bch_dirty_init_state` coordinates dirty-init workers. `bcache_dev_sectors_dirty()`, `offset_to_stripe()`, and `bcache_dev_stripe_dirty()` query dirty accounting. `should_writeback()` decides whether writes become dirty cache data. `bch_writeback_queue()` wakes the thread, and `bch_writeback_add()` marks dirty state and writes the backing superblock.

## Control Flow
Request code calls `should_writeback()` for write decisions. Dirty insertions call `bch_writeback_add()`, which atomically sets `has_dirty`, marks the backing device dirty, persists the superblock, and wakes writeback.

## State And Persistence
The header mutates caller-owned stripe counters and dirty flags. `bch_writeback_add()` persists dirty backing-device state. Cutoff thresholds are external module parameters in `super.c`.

## Dependencies, Integration Points, Risks, And Test Signals
It depends on bcache core types, bio flags, stripe arrays from device initialization, writeback thread fields, and request-path cache modes. Risks include invalid stripe ranges, admission mistakes near cutoff thresholds, detach behavior, and asynchronous dirty superblock writes. Test all cache modes, discard/sync/meta/priority writes, detaching, full dirty stripes, `would_skip`, threshold boundaries, and missing writeback thread cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/writeback.h -->
