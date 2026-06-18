# File Research: sources/block-storage/linux-dm/drivers/md/md.h

## Purpose
Internal header for the Linux MD software RAID driver. It defines the central runtime data structures, state flags, personality interface, sysfs helpers, thread wrappers, and exported MD core entry points used by MD personalities such as raid0/1/5/10, linear, multipath, and clustering code.

## Main Definitions
- `struct md_rdev`: per-component-device state, including data/superblock offsets, block devices, bad-block tracking, pending I/O count, read/write error counters, PPL journal placement, replacement/journal roles, sysfs handles, and raid-disk role fields.
- `enum flag_bits`: per-rdev state bits such as `Faulty`, `In_sync`, `Blocked`, `WriteMostly`, `WantReplacement`, `Replacement`, `Journal`, `FailFast`, and `CollisionCheck`.
- `struct mddev`: array-level state, including personality pointer, disks list, superblock metadata, reshape/recovery state, locking, bitmap information, biosets, flush handling, cluster state, and queue capability state.
- `enum mddev_flags` and `enum mddev_sb_flags`: array runtime and superblock-update flags.
- `enum recovery_flags`: sync/recovery/reshape control flags.
- `struct md_personality`: callback table implemented by each MD layout personality. It covers request handling, run/start/free, status, error handling, hot add/remove, spare activation, sync requests, resize, reshape, quiesce, takeover, and consistency-policy changes.
- `struct md_thread`, `struct md_io_acct`, `struct md_sysfs_entry`: MD-specific wrappers for kernel threads, accounting bios, and sysfs attributes.

## Important Behavior and Contracts
- Per-rdev state is modeled so `Faulty` and `In_sync` should not both be set.
- `MD_FAILFAST` deliberately excludes `REQ_FAILFAST_DRIVER`; the comments explain MD wants minimal retries for device/transport failures but not the driver category.
- `is_badblock()` offsets logical sectors by `rdev->data_offset` before calling the generic badblocks helper, then translates the result back to array-relative sectors.
- `mddev_lock()`, `mddev_lock_nointr()`, and `mddev_trylock()` wrap `reconfig_mutex`; comments document lock ordering with `disk->open_mutex` and `open_mutex`.
- `mddev->lock` protects a specific set of fields and state transitions: flush bio, rdev superblocks/events, `MD_CHANGE_*` clearing, `in_sync`, bitmap pointers, resync min/max, and recovery-running flag transitions.
- Sysfs link helpers skip replacement and journal devices and tolerate missing `kobj.sd`.
- `rdev_dec_pending()` triggers recovery-needed wakeup when the final pending I/O drains on a faulty rdev.
- `is_mddev_broken()` marks `MD_BROKEN` and warns when an rdev’s disk is no longer live.

## Dependencies
Includes block layer, badblocks, kobject/sysfs, mutex/timer/wait/workqueue, and `md-cluster.h`. Exports prototypes implemented in `md.c`, bitmap code, cluster code, and individual RAID personalities.

## Role in Repository
This is the public internal contract for MD code in `drivers/md`. It does not implement the array algorithms itself; it defines the shared state and callback surface that the implementation files depend on.
