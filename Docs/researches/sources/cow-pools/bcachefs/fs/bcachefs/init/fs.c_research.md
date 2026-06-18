# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/fs.c

This file implements module initialization, filesystem object allocation/free, superblock/device open, mount startup/recovery, read-write/read-only transitions, sysfs registration, and global print/log helpers.

Logging and globals:
- Defines module metadata.
- Exposes string tables for filesystem flags and write refs.
- `bch2_print_str_loglevel()`, `bch2_print_str()`, `bch2_print_opts()`, and `__bch2_print()` implement loglevel filtering and optional stdio redirection.
- Defines sysfs kobject types via `KTYPE()`.
- Maintains global `bch2_fs_list` and `bch2_fs_list_lock`.
- `bch2_uuid_to_fs()` and `__bch2_uuid_to_fs()` find open filesystems by UUID.

Read-only transition:
- `__bch2_fs_read_only()` stops background writers, drains open buckets/copygc/write buffer/EC, repeatedly flushes discards, write buffers, key cache, interior updates, journal pins, and btree writes until stable, handles journal-error dirty-node cancellation, marks clean shutdown when safe, stops journal, and stops per-device write refs/allocators.
- `bch2_fs_read_only()` sets `BCH_FS_going_ro`, stops reconcile before disabling write refs, waits for outstanding writes unless emergency read-only interrupts the wait, calls the low-level transition, clears RW flags, verifies clean invariants when possible, or persists error counters when unclean.
- `bch2_fs_emergency_read_only()` and locked variant halt the journal, queue async read-only work, wake allocators/waiters, and annotate the error message once.

Read-write transition:
- `__bch2_fs_read_write()` rejects RW when required feature/allocation/version/error conditions are not satisfied, initializes RW subsystems, starts device allocators/write refs, marks the journal running, starts global write refs, starts journal reclaim/write-buffer/copygc/reconcile, and kicks pending discard/invalidate/stripe/scrub/bitmap-GC work.
- `bch2_fs_read_write()` enforces no-recovery/nochanges/no-alloc-info restrictions.
- `bch2_fs_read_write_early()` performs the same under `state_lock`.

Filesystem shutdown/free:
- `__bch2_fs_free()` tears down all subsystems in reverse-style order, destroys workqueues, frees the superblock, and drops the module reference.
- `bch2_fs_stop()` serializes shutdown, goes read-only, stops read refs, unlinks devices/sysfs/chardev/debugfs, waits for read-only refs, flushes reads and work, and returns error codes if shutdown followed emergency RO or unresolved/fixed errors.
- `bch2_fs_free()` removes the fs from the global list, waits for closure completion, frees devices, and releases the fs kobject.
- `bch2_fs_exit()` combines stop and free.

Online/sysfs and RW init:
- `bch2_fs_online()` checks duplicate UUIDs, creates chardev/debug/sysfs objects, creates device sysfs nodes, and adds the fs to the global list.
- `bch2_fs_init_rw()` allocates workqueues and initializes RW btree, write IO, journal, VFS, journal reclaim, write buffer, copygc, and reconcile.

Version/mount option handling:
- `check_version_upgrade()` determines compatible or incompatible metadata upgrade target, records required recovery passes, and updates superblock upgrade state.
- `bch2_fs_opt_version_init()` handles `norecovery`, `nochanges`, `journal_rewind`, upgrade/downgrade eligibility, mount log output, recovery-pass requirements, lost-btree metadata, error-action compatibility, extent backpointer shift repair requirements, clean/fsck/recovery flags, Unicode/casefold messages, unsupported old features, and member field upgrades.

Filesystem object initialization:
- `bch2_fs_init()` initializes kobjects, locks, refs, time stats, early subsystem state, superblock fields, compatibility defaults, options, block size, names, write refs, blacklist table, btree/compress/counters/data/discard/EC/errors/encryption/read/VFS/IO clocks, Unicode casefold encoding, member devices, journal reservations, attaches opened block devices, performs version option init, and brings the fs online.
- `bch2_fs_alloc()` allocates `struct bch_fs`, runs init, and cleans up on failure.

Start/recovery:
- `bch2_missing_devs_to_text()` prints missing data-bearing devices.
- `bch2_fs_may_start()` enforces degraded/missing device policy and read/write capability.
- `__bch2_fs_start()` adds RW devices to allocator, checks start eligibility, initializes reconcile/counters, requests feature upgrades, optionally initializes RW early, runs option hooks, performs recovery or fresh initialization, marks started, then either remains read-only or goes read-write.
- `bch2_fs_start()` wraps start with formatted logging and clears `recovery_task`.

Resize-on-mount:
- `bch2_dev_will_resize_on_mount()` detects member resize requests when the block device is larger.
- `bch2_fs_will_resize_on_mount()` checks all online devices.
- `bch2_fs_resize_on_mount()` grows bucket arrays, updates member `nbuckets`, clears small-image/resize flags, writes superblock, and initializes new freespace if needed.

Open path:
- `__bch2_fs_open()` reads all supplied device superblocks, chooses the best by sequence/write_time, filters removed/splitbrain devices, allocates the filesystem from the best superblock, logs version messages, and starts unless `nostart`.
- `bch2_fs_open()` wraps open with user-facing error printing.

Module lifecycle:
- `bcachefs_init()` runs bkey pack tests, creates the global sysfs kobject, and initializes lock graph, key cache, chardev, VFS, and debug subsystems.
- `bcachefs_exit()` tears down global subsystems.
- Static-key module parameters are generated for debug parameters.
- Exposes a read-only metadata version module parameter.
