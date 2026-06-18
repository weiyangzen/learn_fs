# Group Research: group_1155_mdadm_sources_block_storage_mdadm_super0_c_sources_block_storage_md_50fd2cf9b7b6

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/block-storage/mdadm`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/super0.c -->
# File Research: sources/block-storage/mdadm/super0.c

## Purpose
Implements the `superswitch super0` backend for legacy Linux md metadata format `0.90`, including superblock load/store, creation, examination, update, geometry validation, and internal bitmap placement.

## Main Responsibilities
- Computes and validates legacy superblock checksums with `calc_sb0_csum()`.
- Handles host-endian 0.90 metadata and byte-swapped legacy variants via `super0_swap_endian()`.
- Prints `--examine`, brief, export, and `--detail` views, including UUID/homehost matching and reshape details.
- Converts superblock state into `struct mdinfo` through `getinfo_super0()`.
- Initializes and writes 0.90 metadata through `init_super0()`, `add_to_super0()`, `write_init_super0()`, and `store_super0()`.
- Loads metadata from the reserved tail area of a component device with `load_super0()`.
- Updates metadata for assemble, force, UUID/homehost, super-minor, resync, bitmap removal, linear grow, metadata migration to v1.0, and reshape rollback.
- Supports fixed-location internal bitmap data immediately after the 0.90 superblock.

## Integration
The file exports `struct superswitch super0`, wiring mdadm’s common metadata interface to the legacy implementation. It depends heavily on shared mdadm helpers from `mdadm.h`, `xmalloc.h`, SHA1 homehost hashing, UUID helpers, bitmap structures, and `super1_make_v0()` for metadata conversion.

## Notable Behavior
- 0.90 metadata is limited by `MD_SB_DISKS`, tail-reserved placement, and older kernel size constraints.
- RAID0 creation rejects non-uniform device sizes unless explicit dangerous layout is requested.
- `match_metadata_desc0()` accepts `0`, `0.90`, default old metadata, `0.91` reshape metadata, and swapped `0.swap`/`0.9`.
- Internal bitmap allocation is constrained to the 60 KiB area after the superblock.

## Risks and Edge Cases
- 0.90 is host-endian, so cross-endian handling is special and easy to regress.
- Device size arithmetic is constrained by the legacy layout and can reject large arrays.
- `UOPT_SPEC_WRITEMOSTLY` and `UOPT_SPEC_READWRITE` manipulate `sb->state`; these names suggest per-device flags, so callers must rely on existing legacy semantics carefully.
- Metadata conversion to v1.0 is refused for unclean arrays or arrays with bitmaps.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/super0.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/super1.c -->
# File Research: sources/block-storage/mdadm/super1.c

## Purpose
Implements the `superswitch super1` backend for Linux md metadata formats `1.0`, `1.1`, and `1.2`. It covers superblock parsing, aligned IO, creation, update, examination, bitmap/PPL/bad-block-log handling, and v0-to-v1 conversion support.

## Main Responsibilities
- Computes v1 checksums over the variable-size superblock and device-role table.
- Provides 4K-safe aligned reads/writes for devices with larger physical sectors.
- Determines superblock placement:
  - `1.0`: near end of component device.
  - `1.1`: at start.
  - `1.2`: 4 KiB from start.
- Prints detailed, brief, export, and bad-block-list views.
- Converts metadata into `struct mdinfo`, including reshape state, replacement devices, consistency policy, PPL, bitmap, journal, and free-space hints.
- Initializes v1 metadata with UUID/name/homehost handling and RAID0 layout defaults.
- Writes initial metadata, preserves device UUIDs/events where appropriate, initializes journal meta blocks, bitmaps, and PPL headers.
- Updates metadata for assemble, force, UUID/name, bitmap/PPL/BBL changes, write-mostly/failfast flags, device-size refresh, RAID0 layout flags, and reshape rollback.
- Copies metadata, bitmap regions, and bad-block logs between devices.

## Integration
The file exports `struct superswitch super1`. It is central to mdadm’s modern native metadata flow and interacts with:
- shared mdadm metadata abstractions from `mdadm.h`;
- UUID helpers;
- bitmap and clustered bitmap structures;
- PPL/R5 journal structures and CRC32C;
- system geometry helpers from `util.c`;
- legacy conversion from `super0.c` through `super1_make_v0()`.

## Notable Behavior
- `load_super1()` can auto-detect the best 1.x minor version by trying all variants and choosing the newest creation time.
- `getinfo_super1()` derives usable/free space before and after data differently depending on whether metadata is before or after data.
- Bitmap support includes clustered bitmaps with per-node bitmap space calculations.
- PPL support excludes arrays with internal bitmap or journal and reserves up to the multi-PPL area size.
- RAID0 layout flags are conditional for older kernels but forced for Linux 5.4+ behavior.

## Risks and Edge Cases
- Many offsets are signed relative-sector fields stored in little-endian metadata; mistakes can corrupt bitmap, BBL, or data placement.
- `md_feature_any_ppl_on()` mixes CPU and little-endian conversions in a compact helper; callers must pass the expected representation.
- Device-size compatibility checks are bypassable through `ignore_hw_compat`, which is useful for probing but risky if misused.
- Reshape rollback has strict alignment requirements and special handling for no-backup offset reshape.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/super1.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/swap_super.c -->
# File Research: sources/block-storage/mdadm/swap_super.c

## Purpose
Standalone utility/test program that endian-swaps a legacy 0.90 md superblock in place on a device.

## Main Responsibilities
- Opens one block device read/write.
- Uses `BLKGETSIZE` to compute the 0.90 tail superblock offset.
- Reads 4096 bytes, swaps every 32-bit word, then separately swaps `events_hi/events_lo` and `cp_events_hi/cp_events_lo`.
- Writes the modified 4096-byte block back.

## Integration
This is not normal mdadm operational code. The file comment explicitly warns not to use it on real arrays and says to use mdadm instead.

## Risks and Edge Cases
- It mutates metadata in place with no checksum repair or validation.
- Uses old `BLKGETSIZE`, so it is only suitable for legacy/manual testing.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/swap_super.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/sysfs.c -->
# File Research: sources/block-storage/mdadm/sysfs.c

## Purpose
Provides mdadm’s sysfs access layer for reading md array/member state, writing md attributes, applying configured sysfs rules, adding disks, freezing arrays, and checking selected kernel/device parameters.

## Main Responsibilities
- Reads sysfs files with newline trimming through `load_sys()`.
- Builds and frees `struct mdinfo` trees from `/sys/block/<md>/md`.
- Reads array fields: metadata version, level, layout, raid disks, component size, chunk size, cache, mismatch count, safe-mode delay, bitmap location, array state, and consistency policy.
- Reads member devices under `dev-*`, including slot, major/minor, state, offsets, size, and errors.
- Provides typed helpers for sysfs string/numeric reads and writes.
- Adds disks to arrays through `new_dev`, then configures offsets, size, slot, PPL, recovery, state, and external bad blocks.
- Implements sysfs member-state helpers for `remove`, `faulty`, `in_sync`, `external_bbl`, etc.
- Parses `SYSFS` config lines and applies them by device name or UUID with path containment checks.
- Provides utility helpers such as SCSI ID extraction, holder uniqueness, array freeze, sysfs wait, and libata `allow_tpm` check.

## Integration
This file is used throughout assemble/manage/grow paths to prefer sysfs over older md ioctls. It depends on mdadm’s mapping tables, `struct mdinfo`, `xmalloc`, UUID comparison, and shared sysfs state enums.

## Notable Behavior
- External metadata versions are represented as `major=-1`, `minor=-2`, with `text_version` carrying the external metadata string.
- `sysfs_set_array()` preserves an external metadata readonly marker when updating metadata version during reshape.
- `sysfs_rules_apply_check()` resolves real paths and ensures configured sysfs writes stay under the md sysfs directory.

## Risks and Edge Cases
- Several functions use fixed-size path buffers; most use `snprintf`, but path length limits remain important.
- In the `GET_ERROR` branch of `sysfs_read()`, the code writes `"errors"` into `buf` rather than the path suffix pointer, which appears suspicious because `load_sys()` then reads the prior `fname`.
- Sysfs state can race hot removal; the reader has special cases for disappearing member devices, but callers must still tolerate `NULL`.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/systemd/mdadm-grow-continue@.service -->
# File Research: sources/block-storage/mdadm/systemd/mdadm-grow-continue@.service

## Purpose
Systemd template service for continuing an md reshape/grow operation on `/dev/%I`.

## Behavior
- `DefaultDependencies=no`.
- Runs `BINDIR/mdadm --grow --continue /dev/%I`.
- Suppresses standard input, output, and error.

## Integration
Referenced by mdadm/udev/systemd flows when an array has active reshape metadata and continuation should be delegated to systemd.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/systemd/mdadm-grow-continue@.service -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/systemd/mdadm-last-resort@.service -->
# File Research: sources/block-storage/mdadm/systemd/mdadm-last-resort@.service

## Purpose
One-shot systemd service that activates a degraded md array after a delay when safer assembly did not complete.

## Behavior
- Runs only if `/sys/devices/virtual/block/%i/md/sync_action` does not exist.
- Executes `BINDIR/mdadm --run /dev/%i`.

## Integration
Paired with `mdadm-last-resort@.timer` and triggered by udev assembly rules for unsafe-but-local arrays.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/systemd/mdadm-last-resort@.service -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/systemd/mdadm-last-resort@.timer -->
# File Research: sources/block-storage/mdadm/systemd/mdadm-last-resort@.timer

## Purpose
Timer companion for degraded last-resort md activation.

## Behavior
- Waits `OnActiveSec=30`.
- Conflicts with the corresponding block device unit, so the timer is cancelled if the device appears normally.

## Integration
Started by udev incremental assembly rules when mdadm reports an unsafe local start condition.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/systemd/mdadm-last-resort@.timer -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/systemd/mdcheck_continue.service -->
# File Research: sources/block-storage/mdadm/systemd/mdcheck_continue.service

## Purpose
Systemd service for continuing md array scrubbing/check work.

## Behavior
- Sets `MDADM_CHECK_DURATION=6 hours`.
- Runs `MISCDIR/mdcheck --start --duration ${MDADM_CHECK_DURATION}`.
- Comment explains that `--start` continues existing checks or starts from zero if no marker exists.

## Integration
Used with `mdcheck_continue.timer` and wanted by `mdmonitor.service`.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/systemd/mdcheck_continue.service -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/systemd/mdcheck_continue.timer -->
# File Research: sources/block-storage/mdadm/systemd/mdcheck_continue.timer

## Purpose
Timer for continuing md scrub/check operations.

## Behavior
- Runs daily at `1:00:00`.
- Installed as wanted by `mdmonitor.service`.

## Integration
Complements `mdcheck_start.timer`, allowing long checks to resume in bounded windows.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/systemd/mdcheck_continue.timer -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/systemd/mdcheck_start.service -->
# File Research: sources/block-storage/mdadm/systemd/mdcheck_start.service

## Purpose
Systemd service that starts or restarts md array scrubbing.

## Behavior
- Wants `mdcheck_continue.timer`.
- Runs `MISCDIR/mdcheck --restart`.

## Integration
Scheduled by `mdcheck_start.timer`, with continuation delegated to the continuation timer/service.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/systemd/mdcheck_start.service -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/systemd/mdcheck_start.timer -->
# File Research: sources/block-storage/mdadm/systemd/mdcheck_start.timer

## Purpose
Timer for initiating periodic md array scrubbing.

## Behavior
- Runs on the first Sunday of each month at `00:45:00`.
- Installed under `mdmonitor.service`.
- Also enables `mdcheck_continue.timer`.

## Integration
Provides the periodic entry point for scrub scheduling.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/systemd/mdcheck_start.timer -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/systemd/mdmon@.service -->
# File Research: sources/block-storage/mdadm/systemd/mdmon@.service

## Purpose
Systemd template service for running `mdmon` metadata monitor for an external metadata container.

## Behavior
- `DefaultDependencies=no`.
- Runs before `initrd-switch-root.target`.
- Uses `IgnoreOnIsolate=true`.
- Executes `BINDIR/mdmon --foreground --offroot --takeover %I`.
- Uses `Slice=system.slice` to avoid early shutdown conflicts.

## Integration
Triggered by udev rules for arrays with external containers, including initrd-prefixed instances.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/systemd/mdmon@.service -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/systemd/mdmonitor-oneshot.service -->
# File Research: sources/block-storage/mdadm/systemd/mdmonitor-oneshot.service

## Purpose
One-shot reminder service for degraded md arrays.

## Behavior
- Sets default `MDADM_MONITOR_ARGS=--scan`.
- Optionally reads `/run/sysconfig/mdadm`.
- Runs optional environment preparation script.
- Executes `BINDIR/mdadm --monitor --oneshot $MDADM_MONITOR_ARGS`.

## Integration
Scheduled by `mdmonitor-oneshot.timer` and associated with `mdmonitor.service`.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/systemd/mdmonitor-oneshot.service -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/systemd/mdmonitor-oneshot.timer -->
# File Research: sources/block-storage/mdadm/systemd/mdmonitor-oneshot.timer

## Purpose
Timer for periodic degraded-array reminder checks.

## Behavior
- Runs daily at `2:00:00`.
- Installed as wanted by `mdmonitor.service`.

## Integration
Triggers `mdmonitor-oneshot.service`.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/systemd/mdmonitor-oneshot.timer -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/systemd/mdmonitor.service -->
# File Research: sources/block-storage/mdadm/systemd/mdmonitor.service

## Purpose
Systemd service for the main mdadm array monitor.

## Behavior
- `DefaultDependencies=no`.
- Runs `BINDIR/mdadm --monitor --scan`.
- Comments document which monitor settings should come from `mdadm.conf` rather than downstream sysconfig files or service flags.

## Integration
Base service that other md check/monitor timers are wanted by.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/systemd/mdmonitor.service -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/test -->
# File Research: sources/block-storage/mdadm/test

## Purpose
Top-level bash runner for the mdadm test suite.

## Main Responsibilities
- Locates the system `mdadm`, sets default test directories, device names, log paths, loop/LVM/disk mode, and control flags.
- Wraps `mdadm()` to capture stderr, zero components before create/build, settle udev, and temporarily raise speed limits for stop operations.
- Parses command-line options for test selection, raid type filters, logging, loop count, broken/big test skips, device backend, and setup/cleanup.
- Sources `tests/func.sh` after resolving test directory.
- Runs each test script in a subshell with `set -ex`, captures logs, checks dmesg unless the test injects errors, and handles skip/broken/keep-going behavior.
- Provides `setup` and `cleanup` modes.

## Integration
This script is the user-facing entry point for the shell tests under `tests/` and `clustermd_tests/`.

## Risks and Edge Cases
- It intentionally operates on system mdadm and real kernel md state; it requires root and a clean RAID environment.
- The wrapper zeros any non-md `/dev/` argument for create/build commands, so it is destructive outside a controlled test environment.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/test -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/tests/00readonly -->
# File Research: sources/block-storage/mdadm/tests/00readonly

## Purpose
Regression test for switching arrays to readonly and back to read-write across metadata versions and RAID levels.

## Behavior
- Iterates metadata `0.9`, `1.0`, `1.1`, `1.2`.
- Iterates RAID levels `raid0`, `raid1`, `raid4`, `raid5`, `raid6`, `raid10`, and optionally `linear`.
- Skips RAID0 with metadata `0.9`.
- Creates a four-device clean array, verifies no sync, switches readonly with `mdadm -ro`, checks `/proc/mdstat` and sysfs `array_state`, switches back writable, and stops the array.

## Integration
Uses variables and helpers from `tests/func.sh` and the top-level `test` runner.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/tests/00readonly -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/tests/func.sh -->
# File Research: sources/block-storage/mdadm/tests/func.sh

## Purpose
Shared bash helper library for mdadm shell tests.

## Main Responsibilities
- Defines expected sizes for metadata formats and test devices.
- Provides colored output helpers and log preservation.
- Implements cleanup for loop, LVM, and disk backends.
- Verifies root, required commands, mdadm availability, absence of existing RAID arrays, and kernel support for multipath/linear.
- Sets up loop/LVM/ram/disk test devices and systemd environment variables for IMSM tests.
- Records/restores SELinux and RAID speed-limit settings.
- Provides test assertions through `check()`, covering RAID level, state, bitmap, readonly, inactive, chunk size, resync/recovery/reshape presence, and absence of sync.
- Provides filesystem/device validation helpers such as `testdev()` and `rotest()`.

## Integration
Sourced by `test`; individual tests rely on its globals (`dev0`, `md0`, sizes, flags) and assertions.

## Risks and Edge Cases
- Test setup is destructive to selected devices and requires a clean host md environment.
- `restore_system_speed_limit()` appears to write both saved min and max values to `speed_limit_max`, leaving `speed_limit_min` unrestored; this may be intentional typo-compatible behavior, but it looks like a bug.
- SELinux helpers assume `getenforce`/`setenforce` are available.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/tests/func.sh -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/udev-md-clustered-confirm-device.rules -->
# File Research: sources/block-storage/mdadm/udev-md-clustered-confirm-device.rules

## Purpose
udev rules for clustered md device confirmation.

## Behavior
- Applies only to block md disk change events with `EVENT=ADD_DEVICE`, `DEVICE_UUID`, and `RAID_DISK`.
- Uses `blkid -o device -t UUID_SUB=...` to find the new component.
- Runs `mdadm --manage <array> --cluster-confirm <raid_disk>:<device|missing>`.

## Integration
Supports clustered md membership confirmation when a node is asked to confirm a device by UUID.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/udev-md-clustered-confirm-device.rules -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/udev-md-raid-arrays.rules -->
# File Research: sources/block-storage/mdadm/udev-md-raid-arrays.rules

## Purpose
udev rules for active md array devices and partitions.

## Behavior
- Filters non-md and removed devices.
- Marks arrays not ready for systemd when `array_state` is missing, clear, or inactive.
- Imports `mdadm --detail --no-devices --export`.
- Creates `/dev/disk/by-id/md-name-*`, `md-uuid-*`, and `/dev/md/*` symlinks for arrays and partitions.
- Imports blkid data and creates filesystem UUID/label/partuuid links.
- Wants `mdmonitor.service` for RAID arrays.
- Starts `mdmon@...service` for external metadata containers.
- Starts `mdadm-grow-continue@...service` for active reshape.

## Integration
Connects mdadm metadata export to udev naming and systemd service activation.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/udev-md-raid-arrays.rules -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/udev-md-raid-assembly.rules -->
# File Research: sources/block-storage/mdadm/udev-md-raid-assembly.rules

## Purpose
udev rules for incremental md array assembly from component-device events.

## Behavior
- Skips anaconda contexts and non-block devices.
- Handles `linux_raid_member`, `ddf_raid_member`, and IMSM members unless blocked by kernel command-line flags.
- Avoids premature handling of md/dm change events.
- Runs `mdadm --incremental --export ... --offroot`.
- Starts degraded last-resort timer for unsafe local arrays.
- On remove events, runs `mdadm -If` with optional path information.

## Integration
Primary automatic assembly hook for udev-discovered RAID members.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/udev-md-raid-assembly.rules -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/udev-md-raid-creating.rules -->
# File Research: sources/block-storage/mdadm/udev-md-raid-creating.rules

## Purpose
udev guard rule for arrays currently being created by mdadm.

## Behavior
- If `/run/mdadm/creating-$kernel` exists for an `md*` device, sets `SYSTEMD_READY=0`.

## Integration
Pairs with `udev_block()`/`udev_unblock()` in `udev.c` to stop udev/systemd from treating a newly created array as ready too early.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/udev-md-raid-creating.rules -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/udev-md-raid-safe-timeouts.rules -->
# File Research: sources/block-storage/mdadm/udev-md-raid-safe-timeouts.rules

## Purpose
udev rule set that attempts to set safer drive timeouts for disks containing RAID members.

## Behavior
- Skips anaconda contexts and command-line-disabled dmraid/mdadm handling.
- Applies to partition devices with exported mdadm metadata.
- For RAID levels above 0, checks parent disk timeout sysfs file and `smartctl` SCTERC output.
- If SCTERC does not appear enabled, writes `180` to `/sys/block/$parent/device/timeout` and logs the change.

## Integration
Independent safety-oriented udev helper for disks used in mdraid.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/udev-md-raid-safe-timeouts.rules -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/udev.c -->
# File Research: sources/block-storage/mdadm/udev.c

## Purpose
Provides mdadm helpers for detecting udev, optionally waiting for udev block events, and blocking/unblocking udev handling while arrays are being created.

## Main Responsibilities
- `udev_is_available()` checks `/dev/.udev` or `/run/udev` and honors `MDADM_NO_UDEV`.
- When libudev is enabled, initializes a block-device udev monitor and waits for events with timeout.
- `udev_block()` creates `/run/mdadm/creating-<devnm>`.
- `udev_unblock()` removes the saved blocking file.

## Integration
Works with `udev-md-raid-creating.rules`, which marks matching md devices as not systemd-ready while the block file exists.

## Risks and Edge Cases
- `udev_block()` stores one global unblock path, so overlapping create operations in one process would need careful sequencing.
- The libudev monitor is process-global and released through `atexit()`.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/udev.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/udev.h -->
# File Research: sources/block-storage/mdadm/udev.h

## Purpose
Header for mdadm udev helpers.

## Contents
- Defines `enum udev_status` with no-udev, error, success, and timeout values.
- Declares `udev_is_available()`.
- Declares `udev_wait_for_events()` when libudev support is enabled.
- Declares `udev_block()` and `udev_unblock()`.

## Integration
Included by `udev.c` and consumers that need to block or wait for udev behavior.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/udev.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/util.c -->
# File Research: sources/block-storage/mdadm/util.c

## Purpose
Large shared utility module for mdadm. It covers md ioctl wrappers, device and partition helpers, metadata-supertype dispatch, mdmon/systemd integration, cluster library hooks, sizing/layout utilities, random IDs, file descriptor handling, and miscellaneous checks.

## Main Responsibilities
- Provides wrappers for md array/disk ioctls and sysfs fallbacks.
- Parses sizes, layouts, cluster-confirm args, mdadm/Linux version strings, major/minor strings, and RAID10/faulty layouts.
- Checks whether enough disks are available for different RAID levels.
- Detects existing ext2, reiserfs, RAID, MBR, and GPT signatures/partition overlap.
- Opens block devices by path or major:minor using temporary device nodes.
- Maps md device names to device IDs and validates md device names.
- Maintains the global `superlist` of metadata handlers: `super0`, `super1`, DDF, IMSM, MBR, GPT.
- Guesses metadata type, duplicates supertype state, opens subarrays, and maps metadata strings to superswitches.
- Gets device size and sector size.
- Adds/removes disks through sysfs for external metadata or ioctls for native arrays.
- Starts and waits for `mdmon`, with systemd delegation first and direct execution fallback.
- Handles metadata update queues for monitor communication.
- Loads DLM and corosync cmap hooks dynamically for clustered md.
- Provides zeroing, sleep, directory/file checks, md module loading, and md module parameter setup.

## Integration
This is a central dependency for the mdadm codebase. It ties together:
- `super0.c`/`super1.c` and other metadata backends;
- `sysfs.c` for modern kernel control;
- mdmon monitor/control socket paths;
- systemd service templates;
- cluster libraries loaded with `dlopen`;
- test and create/assemble/manage/grow operations.

## Notable Behavior
- `super_by_fd()` derives metadata version from sysfs, including external-subarray container resolution.
- `guess_super_type()` probes all registered metadata loaders and chooses the newest creation time.
- `continue_via_systemd()` forks and runs `systemctl restart <service>@<dev>.service`, then falls back to direct daemon startup if needed.
- `init_md_mod()` loads `md_mod` if absent and sets `legacy_async_del_gendisk` behavior for newer kernels.

## Risks and Edge Cases
- Many helpers operate on real block devices and can create temporary block nodes or issue destructive ioctls.
- Dynamic cluster hooks can leave allocated hook structs even when `dlopen` or `dlsym` partially fails.
- `open_dev()` forces `O_DIRECT`, which affects callers expecting buffered IO.
- Partition-table parsing manually reads MBR/GPT structures and depends on sector-size conversion.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/util.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/uuid.c -->
# File Research: sources/block-storage/mdadm/uuid.c

## Purpose
UUID helper implementation for mdadm metadata and configuration parsing.

## Main Responsibilities
- Defines `uuid_zero`.
- Compares UUIDs with optional 32-bit word byte swapping via `same_uuid()`.
- Copies UUIDs with optional byte swapping via `copy_uuid()`.
- Parses a 128-bit UUID from 32 hex digits while allowing `:`, `.`, space, and `-` separators.

## Integration
Used by metadata backends, sysfs rule parsing, config parsing, and export/detail code.

## Risks and Edge Cases
- Parsing accepts separators anywhere and succeeds only when exactly 32 hex digits are found.
- Swap mode is tailored to legacy host-endian vs on-disk byte-order compatibility.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/uuid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/xmalloc.c -->
# File Research: sources/block-storage/mdadm/xmalloc.c

## Purpose
Fail-fast allocation wrappers for mdadm.

## Main Responsibilities
- Provides `xmalloc`, `xrealloc`, `xcalloc`, `xstrdup`, and `xmemalign`.
- On allocation failure, prints a message and exits with `MDADM_STATUS_MEM_FAIL`.

## Integration
Used throughout mdadm where allocation failure is considered fatal and callers should not manually propagate `ENOMEM`.

## Risks and Edge Cases
- These helpers terminate the process rather than returning errors, so they are unsuitable for code paths requiring cleanup/recovery on allocation failure.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/xmalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/xmalloc.h -->
# File Research: sources/block-storage/mdadm/xmalloc.h

## Purpose
Header for mdadm fail-fast allocation helpers.

## Contents
Declares:
- `xmalloc`
- `xrealloc`
- `xcalloc`
- `xstrdup`
- `xmemalign`

## Integration
Included by mdadm modules that use fatal allocation wrappers.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/xmalloc.h -->