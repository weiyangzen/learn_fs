# Group Research: group_1150_mdadm_sources_block_storage_mdadm_Grow_c_sources_block_storage_mdad_375424b53c98

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/Grow.c -->
# File Research: sources/block-storage/mdadm/Grow.c

This file implements most of `mdadm --grow`: online array shape changes, component-size changes, linear array extension, internal/clustered/lockless bitmap changes, PPL consistency-policy changes, reshape continuation, backup/restore of reshape critical sections, and container-wide reshapes for external metadata.

Main public entry points:
- `restore_backup()` rebuilds a critical reshape section after interruption, using either external metadata `recover_backup()` or native `Grow_restart()`.
- `Grow_Add_device()` extends active linear arrays by preparing metadata on the new device, issuing `ADD_NEW_DISK`, then updating existing member superblocks.
- `Grow_addbitmap()` adds or removes internal, clustered, or lockless bitmaps, validating array level, bitmap size, PPL conflicts, clustered RAID10 constraints, write-mostly incompatibility, and sysfs bitmap-location support.
- `Grow_consistency_policy()` switches RAID5 arrays between resync and PPL consistency policy, updates external subarray metadata when needed, writes initial PPL areas, and sets sysfs `consistency_policy`.
- `Grow_reshape()` is the top-level shape-change orchestrator. It validates requested size/level/layout/chunk/raid-disks/data-offset combinations, freezes arrays or containers, applies metadata-side checks, updates size if requested, and delegates actual reshape work to `reshape_array()` or `reshape_container()`.
- `Grow_continue_command()` and `Grow_continue()` resume interrupted reshapes from CLI or boot/systemd continuation paths.
- `Grow_restart()` restores backed-up critical sections from a backup file or spare-device backup area, verifies backup metadata checksums/UUID/timestamps, restores stripes, and advances reshape progress in superblocks.
- `make_backup()` and `locate_backup()` manage mdadm’s backup-file symlink naming under `MAP_DIR`.

Reshape planning:
- `analyse_change()` is the core compatibility and transformation planner. It validates RAID level transitions and computes intermediate reshape level, before/after data-disk counts, before/after layouts, parity count, backup block requirements, minimum data-offset movement, and new logical size.
- It handles RAID1 to RAID0/RAID5, RAID10 to RAID0 or RAID10 reshapes, RAID0 to RAID10/RAID4/5/6, RAID4/5/6 conversions, RAID5 to RAID1 for two-device arrays, RAID6 layout preservation/normalization, and immediate no-restripe cases.
- `compute_backup_blocks()` computes the least-common-multiple-sized critical section that aligns to both old and new stripe geometry.
- `remove_disks_for_takeover()` selects one working disk per mirror-copy group when converting RAID1/RAID10 to RAID0 and removes the remaining devices from the active set.
- `reshape_super_size()` and `reshape_super_non_size()` wrap external metadata callbacks so size-only changes can be rolled back but non-size changes are treated as committed metadata changes.

Kernel/sysfs orchestration:
- The file uses md sysfs attributes heavily: `component_size`, `array_size`, `chunk_size`, `layout`, `new_level`, `raid_disks`, `new_offset`, `sync_action`, `sync_min`, `sync_max`, `sync_completed`, `reshape_position`, `suspend_lo`, `suspend_hi`, `reshape_direction`, `array_state`, `stripe_cache_size`, `bitmap/location`, `ppl_sector`, `ppl_size`, and `consistency_policy`.
- `freeze()`, `unfreeze()`, `freeze_container()`, and `unfreeze_container()` stop background resync/recovery or block mdmon-managed external containers before multi-step changes.
- `start_reshape()` sets suspend ranges, sync bounds, and starts sysfs `sync_action=reshape`; `abort_reshape()` stops reshape and resets suspend/sync state.
- `verify_reshape_position()` compares metadata reshape progress with md’s sysfs position to detect stale metadata or unsafe continuation.
- `set_new_data_offset()` tries to avoid user-space backup by moving component data offsets, checking all member superblocks for head/tail room and writing per-device `new_offset`.
- `raid10_reshape()` handles RAID10 separately because RAID10 reshape is driven by data-offset movement rather than mdadm critical-section backup.

Backup and monitoring:
- `struct mdp_backup_super` describes on-disk backup metadata, including magic, set UUID, timestamp, backup device offsets, array offsets, lengths, and checksums. Two global aligned instances, `bsb` and `bsb2`, are used for write/read verification.
- `reshape_prepare_fdlist()` opens active source devices and spare/backup destinations, recording data offsets.
- `reshape_open_backup_file()` creates and sizes a backup file, rejects files on the same raw array device, fsyncs it, and records a symlink in `MAP_DIR` when appropriate.
- `reshape_array()` is the main worker. It validates spares, imposes intermediate levels and shape, adds devices, chooses between data-offset reshape and backup-file/spare backup, forks or delegates to systemd, starts reshape, and monitors to completion.
- `handle_forking()` either continues in an already forked worker, asks systemd to continue, or forks a child.
- `progress_reshape()` is the safety controller for a running reshape. It advances `sync_max`, manages suspend regions, reads `sync_completed`, converts per-device progress back to array progress, and decides when more backup is needed, when reshape completed, or when it aborted.
- `grow_backup()` saves stripes to backup destinations and writes backup-superblocks before and after the data area.
- `forget_backup()` clears backup metadata when a backed-up section is no longer needed.
- `child_monitor()` performs native metadata reshape monitoring: alternates backup slots for sliding-window reshapes, calls `progress_reshape()`, saves/restores suspension state, optionally validates backup data under `MDADM_GROW_VERIFY`, and eventually releases sync limits.
- `validate()` is a regression-test-only backup verifier that compares backup contents with array data.

External metadata and containers:
- External metadata is integrated through `struct supertype` callbacks: `reshape_super`, `manage_reshape`, `recover_backup`, `container_content`, `sync_metadata`, `write_init_ppl`, `kill_subarray` indirectly elsewhere, and update queues via `st->update_tail`.
- `prepare_external_reshape()` loads the container, rejects blocked volumes/container reshapes, rejects PPL or bitmap consistency policies, and enables mdmon update queuing when mdmon is active.
- `reshape_container()` forks a background container reshape manager. It loops over container content, finds each active member array with `reshape_active`, opens it, initializes sysfs, and calls `reshape_array()` for one member at a time.
- External metadata paths ping or start mdmon, flush mdmon updates, and reload container metadata before final level changes or array-size updates.

Important implementation notes:
- Size changes are intentionally separated from shape changes; the file rejects component-size changes combined with chunk/level/layout/raid-disk changes.
- Bitmap and PPL interactions are guarded: PPL cannot be enabled during reshape, bitmaps conflict with PPL, and bitmaps often must be removed before size/shape/level changes when the kernel returns `EBUSY`.
- The code contains compatibility workarounds for old kernels, including suspend range reset ordering, v0.90 2TB component limits, `sync_completed` reset behavior, and missing or restrictive `new_offset` support.
- Error handling is conservative before starting reshape, but once metadata/shape changes begin, rollback is limited. Size-only external metadata changes attempt rollback; non-size external changes explicitly do not.
- This file is tightly coupled to mdadm core helpers in `mdadm.h`, sysfs helpers, metadata backends, mdmon, mdstat parsing, stripe save/restore code, map-file backup naming, and kernel md ioctl/sysfs semantics.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/Grow.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/Incremental.c -->
# File Research: sources/block-storage/mdadm/Incremental.c

This file implements `mdadm --incremental` behavior for udev-style device arrival, array auto-assembly, spare-device admission, scan/start of previously mapped arrays, container member assembly, and device removal from arrays.

Main entry points:
- `Incremental()` handles a newly seen block device. It validates policy, reads metadata, matches `mdadm.conf`, chooses or creates an md device, adds the component, updates the map file, and starts the array when enough safe devices are present.
- `IncrementalScan()` walks the mdadm map file and starts inactive mapped arrays or delegates container activation.
- `Incremental_remove()` handles device removal by failing and removing the member from native arrays or external containers.
- `incremental_external_test_spare_criteria()` checks external metadata spare criteria before adding a bare disk to a container.
- `Incremental_container()` assembles member arrays inside an external metadata container.

Incremental assembly flow:
- The incoming device must be a block device and allowed by `mdadm.conf` device rules.
- Container devices are detected early with `must_be_container()` and delegated to `Incremental_container()` after `load_container()`.
- Non-container devices are probed with `guess_super_type()` and `load_super()`. If no usable md metadata is found, `try_spare()` attempts to treat the device as a spare according to policy.
- `conf_match()` and homehost matching classify the array name as trusted local, local-any, foreign, or metadata-derived. Foreign arrays avoid trusting array names unless policy allows.
- The map file is locked while selecting or creating the md device to avoid races with concurrent incremental events.
- Existing arrays are found by UUID in the map file; otherwise `create_mddev()` chooses a new md device name from config, metadata name, or an automatically assigned name.
- New arrays are initialized with `set_array_info()` and receive the first device through `add_disk()`.
- Existing arrays are checked against one already attached member via duplicated supertype and `compare_super()` before accepting the new disk.
- For active native arrays, non-spare in-sync components are generally not re-added unless `--run` or policy allows re-add.
- Clustered arrays are skipped for normal incremental auto-start because cluster resource agents should control them.

Start decision:
- After a disk is attached, `count_active()` rereads each component superblock to determine the best event count, available slots, replacement devices, stale devices, and journal cleanliness.
- `enough()` decides whether the collected devices can start the array, with PPL treated as clean enough by setting the clean state bit.
- Arrays are started with `RUN_ARRAY` when sufficiently complete and trusted; otherwise sysfs `array_state=read-auto` is used for partial/foreign cases.
- Reshaping arrays that require backup are not started by `--incremental`; the user is directed to `--assemble`.
- Lockless bitmap metadata can set sysfs `bitmap_type=llbitmap` before start.
- After a successful start, devices rejected by the kernel due to age may be re-added if their policy allows `re-add`.

Container behavior:
- `Incremental_container()` loads container content, checks whether enough container devices are present, matches the container against config/homehost, and iterates member arrays.
- It skips metadata-blocked volumes, reuses existing map entries when present, or creates member md devices when allowed.
- Member naming can be matched through `mdadm.conf` `container` plus `member` rules, using `container2devname()` to resolve configured container references.
- Each member is assembled by `assemble_container_content()`, then udev is unblocked and a sysfs change event is emitted.
- `IncrementalScan()` detects map entries that represent container members and restarts scanning at the parent container when a specific member device is requested.

Spare handling:
- `try_spare()` is used when a device has no md component metadata or when metadata loading fails but policy permits spare use.
- Spare eligibility requires a policy domain and an action allowing `spare`.
- `is_bare()` checks whether the first and last 4 KiB are uniformly blank-like (`0x00`, `0x5a`, or `0xff`); non-bare devices require a same-slot target policy.
- `array_try_spare()` scans mapped arrays/containers for compatible metadata type, domain, size, target UUID, and degradation, preferring the target array or most degraded candidate.
- For containers, `incremental_external_test_spare_criteria()` can ask the metadata backend for size/domain criteria and verify the disk.
- `partition_try_spare()` supports virtual partition metadata by scanning `/dev/disk/by-path`, finding a compatible disk whose partition metadata fits, and copying its metadata to the new device.

Device rejection and active counting:
- `find_reject()` removes an older attached device with the same metadata disk number when a newer event-count device arrives and `add_disk()` reports `EBUSY`.
- `count_active()` loads all attached member superblocks, tracks maximum event count, records per-slot availability, rejects devices that think the best device is failed, rejects spare devices with future event counts, and returns active plus replacement count.
- Journal-device state is tracked with `max_journal_events`; a journal is considered clean when it is no more than one event behind the data devices.

Removal path:
- `Incremental_remove()` accepts either a kernel device name or direct `/dev/<name>` path, finds the containing array through `/proc/mdstat`, and initializes sysfs for that array.
- It tries an exclusive open to avoid racing active rebuild behavior, then may set active/clean arrays to `read-auto`.
- If `id_path` is supplied, the path is saved in policy state for bare replacement scenarios.
- External metadata arrays use `Incremental_remove_external()`, which marks the member faulty in each subarray and only removes it from the container if all subarray failure operations succeeded.
- Native arrays set the member state to faulty and then retry `remove` for up to 25 attempts with 200 ms sleeps, allowing kernel recovery/resync threads to quiesce.

Important implementation notes:
- The file is deliberately race-aware: it uses map-file locking, temporary exclusive opens, udev unblock/change events, and mdmon pings for external metadata.
- Policy is central. `mdadm.conf`, homehost, metadata enablement, path/domain rules, spare actions, same-slot rules, and re-add/force-spare actions all affect whether a device is used.
- The code avoids expensive full sysfs models in removal because disk-removal handling is considered critical and should not fail due to unrelated sysfs parsing issues.
- This file depends on mdadm metadata backends, policy/config parsing, map-file helpers, sysfs/mdstat helpers, udev integration, md device creation/open helpers, and shared assembly/manage routines.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/Incremental.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/Kill.c -->
# File Research: sources/block-storage/mdadm/Kill.c

This file implements destructive metadata removal operations for mdadm: zeroing a component superblock and deleting a subarray from external container metadata.

Functions:
- `Kill()` opens a component device for write, guesses metadata if no `supertype` is supplied, loads the superblock, reinitializes an empty superblock through the metadata backend, and stores it back to the device.
- `Kill_subarray()` opens a container subarray, verifies that the metadata backend supports subarray deletion, rejects deletion while the subarray is active, calls the backend `kill_subarray()` method, and flushes/syncs metadata.

`Kill()` behavior:
- The function is intentionally simple and unsafe by its own comment: it “just zeroes out a superblock.”
- `force` disables exclusive open by setting `noexcl`.
- Return codes distinguish success, write failure, open failure, and unrecognized/no superblock.
- If the supertype was guessed locally, the function frees both backend superblock state and the allocated `supertype`.
- It sets `st->ignore_hw_compat = 1` before loading so metadata can be zeroed even when hardware compatibility checks would otherwise object.
- With `force`, load errors of at least `2` still allow zeroing by reinitializing/storing the metadata area.

`Kill_subarray()` behavior:
- The subarray must be inactive; `is_subarray_active()` blocks deletion of active members.
- `open_subarray()` fills a stack `struct supertype` for the target container/subarray.
- If mdmon is running for the container, metadata updates are queued through `st->update_tail`; otherwise the backend’s `sync_metadata()` is called directly.
- The function warns that UUIDs may have changed after successful deletion.
- Return values distinguish successful deletion, metadata sync failure, and lookup/resource/support failures.

Important implementation notes:
- Actual metadata layout knowledge is delegated to backend callbacks: `load_super`, `free_super`, `init_super`, `store_super`, `kill_subarray`, `sync_metadata`, and mdmon update flushing.
- `Kill.c` does not do policy checks beyond open/load/activity checks; callers must ensure the destructive operation is appropriate.
- The file is used by both `mdadm` and `mdmon` builds according to the project Makefile.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/Kill.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/Makefile -->
# File Research: sources/block-storage/mdadm/Makefile

This Makefile builds, tests, installs, and packages the mdadm userspace tools. It covers the main `mdadm` binary, `mdmon`, static/optimized variants, manpage generation, udev rules, systemd units, helper test binaries, and distribution hooks.

Build configuration:
- `CC` defaults to `$(CROSS_COMPILE)gcc` when not explicitly set.
- `CXFLAGS` defaults to optimized fortified builds; `CWFLAGS` enables strict warnings, format security, stack protector, PIE, and selected compiler-specific warning/optimizer flags.
- Feature probes add flags for implicit fallthrough, format overflow, stringop overflow, no strict overflow, no delete-null-pointer checks, and signed overflow wrapping when the compiler supports them.
- `DEFAULT_OLD_METADATA` selects default metadata `0.90`; otherwise default metadata is `1.2`.
- Paths such as `SYSCONFDIR`, `CONFFILE`, `RUN_DIR`, `MAP_DIR`, `MDMON_DIR`, `FAILED_SLOTS_DIR`, `SYSTEMD_DIR`, `LIB_DIR`, `BINDIR`, `MANDIR`, and `MISCDIR` are configurable.
- Corosync and libdlm availability are detected through `pkg-config`; missing packages add `-DNO_COROSYNC` or `-DNO_DLM`.
- libudev is linked unless `-DNO_LIBUDEV` appears in `CXFLAGS`.
- Version and release-date defines are generated from git when `.git` is present.
- `USE_PTHREADS=1` is enabled by default for glibc TLS ABI safety around clone-like behavior in mdmon.

Object groups:
- `OBJS` defines the main `mdadm` binary objects, including command modules (`Manage.o`, `Assemble.o`, `Build.o`, `Create.o`, `Detail.o`, `Examine.o`, `Grow.o`, `Kill.o`, `Query.o`, `Incremental.o`, `Dump.o`) plus metadata backends, sysfs, maps, platform, bitmap, checksums, and utility code.
- `MON_OBJS` defines the `mdmon` build and includes monitor/managemon code plus shared metadata and utility objects.
- `CHECK_OBJS` is used by `raid6check`.
- `STATICSRC`/`STATICOBJS` add `pwgr.o` for the static mdadm build.
- `SRCS` and `MON_SRCS` are derived from object lists.

Main targets:
- `all` builds `mdadm` and `mdmon`.
- `man` builds rendered manpage text outputs.
- `everything` and `everything-test` build normal tools, helper tools, optimized binaries, and manpages.
- `mdadm`, `mdadm.static`, `mdadm.Os`, `mdadm.O2`, `mdmon`, and `mdmon.O2` link the respective binaries.
- The generic `%.o: %.c` rule compiles with configured CFLAGS/CPPFLAGS/Coverity flags.
- `sha1.o` has a special compile rule adding `-DHAVE_STDINT_H`.
- `test_stripe`, `raid6check`, and `swap_super` are auxiliary/test tools.
- `check_rundir` verifies the parent of `RUN_DIR` exists unless `CHECK_RUN_DIR=0`.

Generated files:
- `mdadm.8` and `mdadm.conf.5` are generated from `.in` files by substituting default metadata, map path, and config paths.
- `.man` targets render manpages through `man -l`.

Install/uninstall:
- `install` runs `install-bin`, `install-man`, and `install-udev`.
- `install-static` installs the static binary and manpages.
- `install-bin` installs `mdadm` and `mdmon` into `$(DESTDIR)$(BINDIR)`.
- `install-man` installs mdadm, mdmon, md, and mdadm.conf manpages.
- `install-udev` installs md RAID udev rules after substituting `BINDIR`.
- `install-systemd` installs systemd units, shutdown hook, and the `mdcheck` helper after substituting configured paths.
- `uninstall` removes installed binaries, manpages, udev rules, systemd units, shutdown hook, and mdcheck helper.

Maintenance targets:
- `test` builds required tools and instructs the user to run `./test` as root.
- `clean` removes built binaries, objects, generated manpages, optimized/static variants, test tools, coverage output, and temporary merge/patch files.
- `dist` and `testdist` run `./makedist` after clean or full test-build preparation.
- `TAGS` generates Emacs tags for headers and C files.
- If `distropkg/Makefile` exists, it is included for distribution-specific packaging rules.

Important implementation notes:
- `Grow.o`, `Incremental.o`, and `Kill.o` are all part of the main `mdadm` binary; `Kill.o` is also part of `mdmon`.
- The build is intentionally security-hardened by default: PIE, immediate binding/noexecstack linker flags, stack protector, fortify defines, and format-security errors.
- Installation rules transform templates into temporary files before install, but echo the final install action depending on make’s silent flag.
- The Makefile is project-specific and does not use autotools here; compiler and feature detection are done inline with make shell probes.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/Makefile -->