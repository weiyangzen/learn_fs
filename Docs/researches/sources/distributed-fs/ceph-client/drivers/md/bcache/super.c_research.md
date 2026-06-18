<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/super.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/super.c

## Purpose
`super.c` is the bcache registration, lifetime, and metadata I/O core. It recognizes cache and backing-device superblocks, registers `/sys/fs/bcache` control files, creates cache sets, attaches cached devices, exposes flash-only volumes, writes bcache superblocks, maintains UUID and priority metadata buckets, and tears everything down during unregister or reboot.

## Important APIs, Types, And Functions
Global state includes `bcache_kobj`, `bch_register_lock`, `bcache_is_reboot`, `bch_cache_sets`, `uncached_devices`, block major/IDA state, unregister waitqueue, and workqueues. Key functions are `read_super()`, `read_super_common()`, `__write_super()`, `bch_write_bdev_super()`, `bcache_write_super()`, UUID I/O helpers, `bch_prio_write()`, `prio_read()`, `bcache_device_init()`, `bch_cached_dev_run()`, `bch_cached_dev_attach()`, `bch_cached_dev_detach()`, `register_bdev()`, `register_cache()`, `register_cache_set()`, `run_cache_set()`, `register_bcache()`, `bcache_reboot()`, `bcache_init()`, and `bcache_exit()`.

## Control Flow
User space writes a path to `/sys/fs/bcache/register`. The code opens the block device, validates the superblock and feature bits, allocates either a `cached_dev` or `cache`, reopens the device exclusive, and registers synchronously or through delayed work. Cache devices create or join a cache set; `run_cache_set()` either replays journal/priority/UUID metadata or initializes a new cache, starts allocator/GC threads, attaches waiting backing devices, and starts flash volumes. Stop/unregister paths set flags, queue closures, detach or stop member devices, flush metadata when safe, release kobjects, and wake waiters.

## State And Persistence
Persistent state includes superblock sequence/state/features/label, backing-device dirty/clean/stale state, UUID table entries, priority/generation buckets, journal roots, and replacement policy. Runtime state includes global registration lists, closures, kobjects, biosets, block holder links, kthreads, workqueues, bucket reservations, and sysfs links.

## Dependencies, Integration Points, Risks, And Test Signals
It integrates bcache btree, journal, allocation, request, writeback, debug, features, accounting, sysfs, block, folio, bio, closure, workqueue, kthread, debugfs, and reboot-notifier APIs. Risks center on registration/teardown ordering, metadata validation, priority bucket write ordering while dropping `bucket_lock`, dirty cache-set failure policy, and embedded superblock bio/folio lifetimes. Test with module init/exit, register/register_quiet, duplicate/busy devices, async registration, bad superblocks, fresh cache init, journal recovery, UUID migration, flash volumes, attach/detach, dirty failure policy, reboot, and metadata I/O fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/super.c -->
