# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/dev.c

This file implements bcachefs device membership, online/offline transitions, add/remove/resize operations, sysfs integration, splitbrain checks, and block-layer hot-remove handling. It also contains a long design comment documenting multi-device behavior.

Documentation block:
- Explains per-device metadata, member states, durability, caching, add/remove workflows, hot-remove behavior, data-type restrictions, degraded modes, resize, error tracking, and consistency/self-healing.

Device identity and validation:
- `bch2_devs_list_to_text()` prints device lists by name.
- `bch2_dev_may_add()` validates block size and bucket size compatibility.
- `bch2_dev_to_fs()` finds an open filesystem by block dev_t.
- `bch2_dev_in_fs()` validates UUID membership, removed slots, block size, and member sequence/write-time splitbrain conditions.

IO reference and state transitions:
- `bch2_dev_io_ref_stop()` stops read/write refs and clears online read mask for reads.
- `__bch2_dev_read_only()` removes allocator access, recalculates capacity, drains write refs, stops per-device journal use, schedules discards, and flushes EC operations.
- `__bch2_dev_read_write()` re-adds allocator access, restarts write refs, recalculates capacity, and schedules discards.
- `bch2_dev_state_allowed()` checks whether changing a RW device to non-RW leaves the filesystem writable under the given force flags.
- `__bch2_dev_set_state()` persists member state changes, triggers reconcile scans, and queues stripe scans when RW membership changes.
- `bch2_dev_set_state()` wraps state changes under `state_lock`.

Device allocation and attachment:
- `__bch2_dev_alloc()` allocates `bch_dev`, initializes kobject, refs, latency stats, buckets, discard state, journal early state, and IO counters.
- `bch2_dev_attach()` assigns index/name, links into `c->devs`, and creates sysfs objects.
- `bch2_dev_alloc()` allocates a member from the filesystem superblock.
- `__bch2_dev_attach_bdev()` attaches an opened superblock/block device to an offline member, checks capacity, initializes journal, records device/model/serial strings, installs holder backpointer, and starts read refs.
- `bch2_dev_attach_bdev()` handles attach under state lock, updates online mask, sysfs, and reconcile wakeup.

Device removal:
- `bch2_dev_remove()` transitions the member to evacuating, drops data via backpointers or legacy scans, verifies usage is empty, flushes btree/journal pins, offlines the device before removing alloc info, runs replicas GC/accounting checks, removes the `c->devs` pointer, waits for refs, frees the device, and marks the member UUID deleted/zeroed.
- It restores RW allocator state on some failure paths when possible.

Device add/online/offline:
- `bch2_dev_add()` reads a new device superblock, validates compatibility, allocates a new member slot, attaches the device, writes updated superblocks, initializes usage/freespace/journal for started filesystems, creates labels, sends UUID change uevent, and schedules reconcile.
- `bch2_dev_online()` reads an existing member superblock, validates membership/splitbrain, attaches it, marks device superblock, initializes freespace/journal if needed, updates `last_mount`, and schedules pending reconcile.
- `bch2_dev_may_offline()` verifies remaining online/RW devices can satisfy read/write requirements.
- `bch2_dev_offline()` checks permission and calls `__bch2_dev_offline()`.

Resize:
- `bch2_dev_resize()` supports grow-only resize, validates maximum bucket count and underlying block capacity, resizes bucket arrays, marks device superblock, persists new bucket count, initializes new freespace, recalculates capacity, and schedules reconcile for new space.
- `__bch2_dev_resize_alloc()` adjusts disk accounting and initializes freespace for new buckets.

Lookup and hot-remove:
- `bch2_dev_lookup()` finds a member by name or `/dev/`-stripped name.
- Block holder ops use `bdev_get_fs()` and `bdev_to_bch_dev()` to find the owning filesystem/device.
- `bch2_fs_bdev_mark_dead()` responds to block-layer death by attempting forced-degraded offline; if not safe, it syncs/shrinks/evicts and puts the whole filesystem emergency read-only.
- `bch2_fs_bdev_sync()` syncs the VFS superblock for a held block device.

Important invariants:
- Device state changes are serialized by `state_lock`.
- Superblock mutations use `sb_lock` and `PF_MEMALLOC_NOFS`.
- Device removal is conservative about journal flush ordering to avoid stale pointers and writes after IO refs are stopped.
