# File Research: sources/cow-pools/bcachefs-tools/fs/init/fs.c

Primary filesystem setup, open/start/stop, RO/RW transition, and module lifecycle implementation for bcachefs.

Key responsibilities:
- Defines module metadata, global filesystem list, sysfs kobject types, filesystem flag/write-ref string tables, and bcachefs module init/exit.
- Implements logging/printing helpers that honor mount verbosity, kernel loglevel prefixes, and optional stdio redirection.
- Maintains global lookup by filesystem UUID through `bch2_fs_list`, `__bch2_uuid_to_fs()`, and `bch2_uuid_to_fs()`.
- Owns read-only transition in `bch2_fs_read_only()` and `__bch2_fs_read_only()`:
  - Stops EC, open buckets, copygc, write buffer, discard/invalidate scheduling, and journal reclaim.
  - Flushes write buffer, key cache, btree interior updates, journal pins, and btree writes until clean.
  - Handles dead-journal shutdown by cancelling dirty btree writes.
  - Persists error counters/superblock state when shutdown is not clean.
  - Verifies clean accounting, replicas, btree cache, key cache, and write buffers when clean shutdown is expected.
- Owns emergency read-only transition through `bch2_fs_emergency_read_only()` and locked variant:
  - Halts the journal.
  - Queues async read-only work.
  - Wakes allocator waiters and RO waiters.
  - Emits the emergency sequence once.
- Owns read-write transition in `__bch2_fs_read_write()`:
  - Requires `BCH_FS_may_go_rw` and upgrade/downgrade permission.
  - Rejects RW for no alloc info, unfixed errors, unresized small image, or unmigrated default superblock.
  - Initializes RW subsystems, device allocators, write refs, journal reclaim, write buffer, copygc, reconcile, discard/invalidate/stripe-delete repair work, journal scrub repairs, and btree bitmap GC scheduling.
- Provides `bch2_fs_init_rw()` to allocate RW workqueues and initialize RW btree, write IO, journal, VFS, reclaim, write buffer, copygc, and reconcile state.
- Implements filesystem allocation/free/stop/exit:
  - `bch2_fs_init()` initializes early subsystem state, superblock-derived options, devices, btree/journal/data/VFS subsystems, Unicode/casefolding, journal entry reservations, and sysfs exposure.
  - `bch2_fs_stop()` serializes shutdown, transitions RO, stops READ refs, unlinks devices, removes sysfs/debug/chardev state, drains btree reads and interior update work, and reports shutdown error categories.
  - `bch2_fs_exit()` combines stop and free.
- Handles mount-time version/option setup in `bch2_fs_opt_version_init()`:
  - Converts `norecovery` into a limited read-only/nochanges mode.
  - Enables fsck for journal rewind.
  - Sets upgrade/downgrade permission when safe.
  - Logs non-default mount options, features, devices, and incompatible-version allowance.
  - Imports required recovery passes from the superblock.
  - Schedules topology/backpointer repair for topology errors and too-small `extent_bp_shift`.
  - Rejects unsupported initialized filesystems missing `new_extent_overwrite` or with too-old `version_min`.
- Handles metadata version upgrades/downgrades through `check_version_upgrade()` and downgrade helpers.
- Starts a filesystem through `bch2_fs_start()` / `__bch2_fs_start()`:
  - Adds online devices to allocator state.
  - Checks degraded/missing-device policy.
  - Initializes reconcile and late counters.
  - Requests no-superblock-user-data-replicas incompat feature.
  - Pre-initializes RW resources if recovery will go RW.
  - Runs recovery or new filesystem initialization.
  - Transitions to final read-only or read-write state according to mount options.
- Implements device missing/degraded checks via `bch2_fs_may_start()` and `bch2_missing_devs_to_text()`.
- Implements resize-on-mount for devices with `resize_on_mount`, updating member fields, clearing `small_image`, writing the superblock, and resizing allocation metadata if initialized.
- Opens devices and chooses the best superblock in `__bch2_fs_open()`:
  - Reads all supplied superblocks.
  - Picks highest sequence/write-time superblock.
  - Filters removed/splitbrain devices.
  - Allocates the filesystem object.
  - Optionally starts it.
  - Logs initialization/startup messages.
- Defines global module init/exit:
  - Initializes dirent code, global kobject, lock graph, key cache, chardev, VFS, and debug.
  - Exposes debug static-key module parameters.

Important interactions:
- Coordinates almost every major subsystem: allocator, btree, journal, data IO, EC, copygc, reconcile, snapshots, subvolumes, quota, VFS, sysfs, chardev, debug, superblock IO, downgrade/upgrade, and recovery passes.
- `go_rw_in_recovery()` from `passes.h` determines whether RW resources are preloaded during recovery.
- `bch2_fs_recovery()` and `bch2_fs_initialize()` are invoked from startup after options and device availability checks.
- Journal clean/dirty state drives clean shutdown validation and read-only behavior.
- Device IO refs protect devices during mount-time resize, journal allocation, and startup/shutdown.

Notable invariants:
- New foreground writes are blocked before write refs are stopped during RO transition.
- Clean shutdown requires no journal error, no filesystem error, replay done, clean superblock, no dirty btree/key-cache/write-buffer state, and clean accounting/replicas refs.
- RW transition is forbidden before `BCH_FS_may_go_rw`.
- `set_may_go_rw` recovery pass must not be excluded.
- `small_image` and `no_default_sb` force or preserve read-only behavior until fixed.
