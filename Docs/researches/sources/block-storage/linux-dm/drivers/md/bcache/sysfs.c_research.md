# File Research: sources/block-storage/linux-dm/drivers/md/bcache/sysfs.c

`sysfs.c` defines the user-facing and internal sysfs control surface for cached devices, flash volumes, cache sets, and cache devices. It uses macro helpers from `sysfs.h` to declare attributes and kobject types, with locked show/store wrappers where global registration state must be serialized by `bch_register_lock`.

Cached-device attributes expose cache mode, readahead cache policy, stop-on-cache-failure behavior, writeback controls, I/O error state, dirty data, stripe geometry, sequential cutoff, running/state/label, backing device name/UUID, and debug-only verification/torture controls. Stores can clear stats, run a stale/no-cache device, change cache mode and persist it to the backing superblock, attach to a cache set by UUID, detach, stop, update labels with uevents and UUID-table writes, tune writeback rate controller parameters, and toggle `io_disable`.

The cached-device store wrapper performs post-processing for `writeback_running` and `writeback_percent`: it wakes the writeback thread when the running flag changes and starts delayed writeback-rate updates once a device is attached and writeback percentage is set. All user stores reject writes while `bcache_is_reboot` is true.

Flash-volume attributes expose size, label, unregister, and disabled data checksum plumbing. Stores can resize the gendisk by updating UUID-entry sectors, relabel the UUID entry, or unregister by setting detach and stopping the bcache device.

Cache-set attributes expose synchronous mode, journal delay, flash volume creation, geometry, root/btree usage, btree cache metrics, average key size, error policy, I/O error tuning, congestion settings, and clear stats. Internal cache-set attributes add active journal entries, timing stats, btree node stats, bset tree stats, cache read races, journal reclaim counters, writeback key counters, GC/prune triggers, debug flags, copy GC, idle max writeback, auto-GC-after-writeback, I/O disable, writeback cutoff module parameters, and feature bit printers.

The cache-set show path computes live values by locking the root btree for root usage, summing cached btree memory under `bucket_lock`, scanning bucket hash chains, and using GC stats for btree utilization. The store path can unregister/stop the set, toggle sync and write the cache superblock, create flash volumes, clear counters, trigger GC, prune through the shrinker, change error action, tune error/congestion behavior, toggle cache-set I/O disable, and set debug/GC controls.

Cache-device attributes expose bucket/block geometry, bucket count, discard policy, written byte counters, I/O errors, replacement policy, priority stats, and stat clearing. Priority stats allocate a temporary priority array, count unused/clean/dirty/metadata buckets under the bucket lock, sort priorities, filter metadata/zero priorities, and print quantiles.

The file depends on `features.h` printers, `writeback.h` tunables, `request.h` congestion helper, `stats.c` accounting, `super.c` lifecycle functions, and btree/key statistics. Its major invariant is that sysfs state changes which affect global registration, attachment, or cache-set operation run under `bch_register_lock`.
