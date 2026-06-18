# File Research: sources/cow-pools/bcachefs-tools/fs/init/dev.c

## Purpose
Implements bcachefs multi-device management: membership validation, splitbrain checks, device allocation/free, sysfs linkage, block-device attach/detach, device state transitions, add/remove/online/offline, resize, mount-time resize allocation, lookup by name, and block-layer holder callbacks for dead/sync events.

## Main Contents
- Long embedded documentation for multi-device behavior, per-device metadata, state meanings, durability/caching, add/remove/online/offline workflows, hot-remove handling, data restrictions, degraded mode, resize, errors, and self-healing.
- Read/write reference name arrays generated from `BCH_DEV_READ_REFS()` and `BCH_DEV_WRITE_REFS()`.
- `bch2_devs_list_to_text()` prints device names for a compact device list.
- Membership helpers:
  - `bch2_dev_may_add()` checks block size and bucket size compatibility.
  - `bch2_dev_to_fs()` finds a mounted filesystem by `dev_t`.
  - `bch2_dev_in_fs()` verifies UUID membership, removed-device state, block size, member sequence, superblock sequence/write-time, and splitbrain conditions.
- Startup/shutdown helpers:
  - `bch2_dev_io_ref_stop()`
  - `__bch2_dev_read_only()`
  - `__bch2_dev_read_write()`
  - `bch2_dev_unlink()`
  - `bch2_dev_free()`
  - `__bch2_dev_offline()`
  - `bch2_dev_sysfs_online()`
- Allocation/attach helpers:
  - `__bch2_dev_alloc()` allocates and initializes refs, kobject, IO latency stats, journal/discard/bucket state, error counters, and per-cpu IO counters from a superblock member.
  - `bch2_dev_attach()` installs a device in `c->devs`.
  - `bch2_dev_alloc()` allocates an existing member at mount/recovery.
  - sysfs identity readers fill device name/model/serial.
  - `__bch2_dev_attach_bdev()` and `bch2_dev_attach_bdev()` attach an open block device, initialize journal state, set read refs, mark it online, and wake reconcile.
- State management:
  - `bch2_dev_state_allowed()` verifies leaving RW does not violate write requirements unless forced.
  - `__bch2_dev_set_state()` handles read-only transition, superblock state update, allocator re-add for RW, and reconcile scans for pending/device/stripes.
  - `bch2_dev_set_state()` wraps it under `state_lock` and removal checks.
- Device removal:
  - `__bch2_dev_remove()` marks the device removing, moves it to evacuating, drops data by backpointers or legacy scanning, verifies usage is empty, flushes journal pins, offlines the device, removes allocation metadata, flushes again, GC-checks replicas, removes it from `c->devs`, and drains refs.
  - `bch2_dev_remove()` frees the device outside `state_lock` and marks the superblock member deleted or UUID-zeroed.
- Device add/online:
  - `bch2_dev_add_initialize()` advances partially initialized new devices through usage init, superblock marking, freespace init, and journal allocation.
  - `bch2_dev_add()` reads a new device superblock, allocates a member slot, attaches it, writes updated superblocks, initializes runtime metadata, invalidates device cache, emits UUID uevent, and wakes reconcile.
  - `bch2_dev_online()` reattaches an existing member, validates membership/splitbrain, marks device superblock, restores RW allocator state, initializes freespace/journal if needed, updates last mount, and schedules pending reconcile.
- Offline/resize:
  - `bch2_dev_may_offline()` checks whether remaining devices can read/write the filesystem.
  - `bch2_dev_offline()` validates state and calls `__bch2_dev_offline()`.
  - `bch2_dev_resize()` grows a device, updates bucket arrays, marks device superblock, writes new bucket count, initializes new freespace, recalculates capacity, and wakes reconcile.
  - `__bch2_dev_resize_alloc()` performs mount-time allocation accounting and freespace initialization for newly added buckets.
- `bch2_dev_lookup()` finds devices by name or `/dev/`-stripped path.
- Block holder ops:
  - `bch2_fs_bdev_mark_dead()` handles block-layer dead-device events by syncing/evicting when possible, emergency read-only fallback, and offlining the bcachefs device.
  - `bch2_fs_bdev_sync()` syncs filesystem on holder sync request.

## Integration Notes
This file is the implementation behind chardev device ioctls and mount/recovery device setup. It coordinates allocator state, journal state, discard, EC stripe flushing, reconcile scans, replicas accounting, superblock writes, sysfs, block holder callbacks, and global filesystem list membership. The code has careful lifetime separation between normal `ca->ref`, `ref_outer`, read/write IO refs, and `state_lock` to avoid deadlocks during removal and error work.

## Risks and Edge Cases
- `bch2_dev_may_offline()` builds `new_rw_devs` but clears `ca->dev_idx` from `new_devs` twice, not from `new_rw_devs`. This appears inconsistent with `bch2_dev_state_allowed()` and could make write-availability checks for offline overly permissive.
- Device removal intentionally consumes the caller's `ref_outer`; callers must not use `ca` afterward unless documented.
- Splitbrain checks can be bypassed by `no_splitbrain_check`, but the code logs the detected mismatch.
- Removal has several durability barriers: stripe flush, btree interior updates flush, journal pin flushes, journal flushes, allocation metadata removal, and replica GC. Skipping one could leave stale pointers or superblock replica entries.
- Shrinking is explicitly unsupported.
