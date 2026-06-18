# sources/distributed-fs/ceph-client/block/bdev.c

## Purpose
`bdev.c` implements the VFS-facing block-device object model: internal block-device inodes, pseudo-filesystem setup, open and close paths, exclusive claims, block-size management, cache invalidation, freeze/thaw hooks, device lookup, write-access policy, and statx reporting.

## Important APIs, types, and functions
The central private type is `struct bdev_inode`, which embeds `struct block_device` with its VFS inode. Conversion helpers include `BDEV_I`, `BD_INODE`, exported `I_BDEV`, and exported `file_bdev`. Public functions include `invalidate_bdev`, `truncate_bdev_range`, `bdev_validate_blocksize`, `set_blocksize`, `sb_set_blocksize`, `sb_min_blocksize`, `sync_blockdev_nowait`, `sync_blockdev`, `sync_blockdev_range`, `bdev_freeze`, `bdev_thaw`, `bdev_cache_init`, `bdev_alloc`, `bdev_set_nr_sectors`, `bdev_add`, `bdev_unhash`, `bdev_drop`, `bd_prepare_to_claim`, `bd_abort_claiming`, `bdev_permission`, `blkdev_get_no_open`, `blkdev_put_no_open`, `bdev_open`, `bdev_file_open_by_dev`, `bdev_file_open_by_path`, `bdev_release`, `bdev_fput`, `lookup_bdev`, `bdev_mark_dead`, `sync_bdevs`, `bdev_statx`, `disk_live`, and `block_size`.

## Control flow
Initialization starts in `bdev_cache_init`, creating a slab cache, registering the `bdev` pseudo-fs, mounting it, and storing `blockdev_superblock`. `bdev_alloc` creates an inode, initializes locks and mappings, attaches the request queue and disk, allocates per-CPU stats, and returns the embedded `block_device`. `bdev_add` assigns the `dev_t`, inode number, and hash entry.

Open flow begins with permission checks, no-open lookup by `dev_t`, pseudo-file allocation, and `bdev_open`. `bdev_open` optionally prepares an exclusive claim, blocks disk events, serializes on `disk->open_mutex`, verifies disk liveness and module ownership, enforces mounted-write restrictions, opens whole disks or partitions, claims write access, finalizes exclusive holder state, sets file flags/mapping/private data, and unblocks events. Error paths release claims, modules, mutexes, and event blocks.

Release flow in `bdev_release` syncs early if it appears to be the last opener, yields write access, ends claims, flushes media-change events, decrements whole or partition openers, releases the module, and drops the no-open device reference. `bdev_fput` proactively yields claims before deferred `fput`. Freeze/thaw paths count nested freezes and either call holder operations or sync the blockdev.

## State and persistence behavior
Persistent kernel state includes hashed block-device inodes, open counts, holder and claiming fields, write counters, freeze counts, block size bits, mapping folio order, sector count, device stats, and superblock-wide inode lists. Dirty data persists through the block-device mapping until explicit sync, invalidation, or final close flushes it. The global `bdev_allow_write_mounted` starts from `CONFIG_BLK_DEV_WRITE_MOUNTED` and can be overridden by the `bdev_allow_write_mounted=` boot parameter.

## Dependencies and integration points
This file sits between VFS, block core, gendisk drivers, device cgroups, security hooks, writeback, buffer heads, partitions, mount/pseudo-fs code, and statx. Holder operations allow filesystems or volume managers to freeze, thaw, mark dead, and coordinate exclusive ownership. Disk event blocking integrates with media-change polling and exclusive write holders.

## Risks
Open/close ordering is delicate: missing cleanup on any error path leaks claims, module refs, event blocks, or device refs. Write restriction depends on `bd_writers` sign conventions and correct pairing in yield paths. Block-size changes must flush and invalidate before changing folio minimum order; races here can corrupt page-cache assumptions. Exclusive claim behavior spans whole disks and partitions, so holder identity and `bd_claiming` wakeups are high-risk. `bdev_mark_dead` may call into holder ops with lock handoff assumptions.

## Test signals
Signals include block-device open/close stress, exclusive claim nesting and contention, whole-disk versus partition opens, module removal races, mounted-block-device write policy tests with both config and boot parameter, block-size change tests around page-cache folios, freeze/thaw nesting, hot unplug/media-change tests, `lookup_bdev` namespace checks, and statx direct-IO/atomic-write field validation.
