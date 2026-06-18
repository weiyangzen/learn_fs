# subset-b-009539 research

This grouped report covers the requested xfstests common helpers and btrfs tests. Each section preserves the source path in the title and is bounded by the markers consumed by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/common/dmthin -->
## sources/test-tools/xfstests/common/dmthin

Purpose: this shell library builds a dm-thin stack on top of `SCRATCH_DEV` for fstests that need thin provisioning behavior. It derives deterministic mapper names from `$seq`: `thin-data.$seq`, `thin-meta.$seq`, `thin-provision-pool.$seq`, and `thin-vol.$seq`, with corresponding `/dev/mapper/*` paths.

Important APIs: `_dmthin_init` creates linear metadata/data devices, zeros the metadata device, creates a `thin-pool`, sends `create_thin`, and creates the thin volume. `_dmthin_cleanup` tears all mapper devices down after unmounting `SCRATCH_MNT`. `_dmthin_check_fs` temporarily redirects `SCRATCH_DEV` to the thin volume before calling `_check_scratch_fs`. `_dmthin_grow` reloads the data and pool device tables with additional sectors. `_dmthin_set_queue` and `_dmthin_set_fail` choose queue-on-full versus `error_if_no_space` pool behavior. `_dmthin_mount`, `_dmthin_mkfs`, and `_dmthin_try_mkfs` redirect normal scratch mount/mkfs helpers to `DMTHIN_VOL_DEV`.

Control flow: initialization calculates default sizes from `blockdev --getsz`, reserves an offset for metadata, validates the backing device is large enough, cleans previous state, creates mapper targets, and records each table in global variables. Growth queries current tables with `dmsetup table`, computes new sizes, and uses `_dmthin_reload_table` to suspend/load/resume mapper devices.

State and persistence: all device-mapper state is kernel-global and named by `$seq`. The backing scratch device is partitioned logically by table offsets but not partitioned on disk. The helper mutates global `SCRATCH_DEV` only inside `_dmthin_check_fs` and restores it.

Dependencies and integration: it depends on `common/rc` for `_unmount`, `_dmsetup_create`, `_dmsetup_remove`, `_scratch_options`, `_common_dev_mount_options`, `_mount`, `_mkfs_dev`, `_try_mkfs_dev`, `_notrun`, and `_fail`; it also depends on `$DMSETUP_PROG`, `dd`, and `blockdev`. Tests using it must have required the `thin-pool` dm target.

Risks: table parsing uses unanchored `grep` in set-queue/fail paths and field positions from `dmsetup table`, so naming collisions or format changes can misread sizes. `_dmthin_init` contains a likely typo `_notun` on thin-pool creation failure. Cleanup is destructive for devices named with the current `$seq`, so `$seq` uniqueness matters.

Test signals: successful runs should show clean mkfs/mount on `DMTHIN_VOL_DEV`, correct behavior under full-pool mode changes, and clean `_dmthin_check_fs` after unmount. Failures surface as dmsetup errors, stale `/dev/mapper` nodes, or scratch fs check failures.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/common/dmthin -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/common/f2fs -->
## sources/test-tools/xfstests/common/f2fs

Purpose: this library provides f2fs-specific requirement checks and fsck integration for the generic fstests harness.

Important APIs: `_require_scratch_f2fs_compression [algorithm]` verifies scratch availability, kernel compression feature exposure at `/sys/fs/f2fs/features/compression`, mkfs support for `-O compression,extra_attr`, and optionally mount support for `compress_algorithm=<algorithm>`. `_check_f2fs_filesystem device` unmounts or remounts the device read-only, runs `fsck.f2fs --dry-run`, logs failures to `$seqres.full`, restores the mount when appropriate, and returns success/failure. `_require_inject_f2fs_command metaarea member` validates `inject.f2fs` availability and that a specific meta area/member appears in the command help.

Control flow: compression probing is prerequisite oriented: check kernel feature, try mkfs, optionally try mount and immediately unmount. The fsck helper mirrors `common/rc` generic checking: detect mounted f2fs, transition it to a checkable state, run dry-run fsck into `$tmp.fsck.f2fs`, record diagnostics, and remount read-write if the filesystem was originally mounted and fsck passed.

State and persistence: no persistent state is created except temporary `$tmp.fsck.f2fs` and appended diagnostics in `$seqres.full`. It may reformat scratch during compression probing. It mutates mount state only through shared rc helpers.

Dependencies and integration: it expects `common/rc` globals and helpers such as `_require_scratch`, `_scratch_mkfs`, `_scratch_mount`, `_scratch_unmount`, `_fs_type`, `_umount_or_remount_ro`, `_mount_or_remount_rw`, `_mount`, `_log_err`, `_require_command`, `_notrun`, and `_exit`. It depends on `$F2FS_FSCK_PROG` and `$F2FS_INJECT_PROG`.

Risks: `_require_inject_f2fs_command` uses implicit globals `metaarea`, `member`, and `val` rather than local variables, which can leak into caller scope. `ssa`, `node`, and `dent` do not initialize `val`, so the constructed help invocation depends on shell state or empty expansion. Compression probing formats scratch, so callers must not expect existing scratch contents to survive.

Test signals: passing checks are silent or return zero. Failure evidence is a notrun reason for unsupported compression/injection features or `*** fsck.f2fs output ***` in `$seqres.full` when the filesystem is inconsistent.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/common/f2fs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/common/filter -->
## sources/test-tools/xfstests/common/filter

Purpose: this is the generic output-normalization library for fstests. It removes host paths, device names, timing, UUIDs, version-dependent utility wording, block offsets, and other nondeterministic output so golden output comparisons remain stable.

Important APIs: `_within_tolerance` compares numeric values using `bc` and supports absolute or percent tolerances. Core path filters include `_filter_test_dir`, `_filter_scratch`, `_filter_testdir_and_scratch`, and `_filter_scratch_pool`. Command-specific filters include `_filter_dd`, `_filter_xfs_io`, `_filter_xfs_io_offset`, `_filter_xfs_io_error`, `_filter_xfs_io_fiemap`, `_filter_filefrag`, `_filter_quota`, `_filter_project_quota`, `_filter_quota_report`, `_filter_ro_mount`, `_filter_error_mount`, `_filter_busy_mount`, `_filter_mknod`, `_filter_mv`, `_filter_stat`, `_filter_touch`, `_filter_getcap`, `_filter_bash`, and `_filter_sysfs_error`. Attribute filters are split between `__filter_file_attributes` and `_filter_vfs_file_attributes`.

Control flow: most functions are simple stdin-to-stdout pipelines using `sed`, `awk`, `perl`, `grep`, or `tr`. The path filters intentionally replace longer mount paths before shorter device paths to avoid partial substitutions. Mount filters encode multiple historical util-linux message forms into a canonical message. File extent filters parse structured command output into compact machine-comparable tuples.

State and persistence: there is no durable state. `_within_tolerance` creates `$tmp.bc.1` and `$tmp.bc.2` and removes them. Several filters rely on global environment such as `TEST_DIR`, `TEST_DEV`, `SCRATCH_MNT`, `SCRATCH_DEV`, `SCRATCH_DEV_POOL`, `OVL_*`, `FSTYP`, `$AWK_PROG`, `$PERL_PROG`, and helper functions from `common/rc`.

Dependencies and integration: every test that emits environment-sensitive output can source this file. Btrfs tests in this subset use it to hide scratch/test paths, normalize xfs_io byte-rate summaries, and stabilize `dd`, `md5sum`, mount, and filesystem utility output.

Risks: the filters are regular-expression based and can over-filter if user data resembles device paths or error text. `_filter_size_to_bytes` assumes a one-character suffix and does not handle suffixless values. `_filter_xfs_io` has a broad sed pattern that may miss new units or format changes. `_filter_quota_report` uses environment-sensitive arithmetic and hidden root-file adjustments, so quota golden output depends on correct caller setup.

Test signals: these helpers are not normally tested directly; regressions show up as golden output diffs across util-linux/coreutils/xfsprogs/kernel versions. Stable expected output from the btrfs tests is a direct signal that the relevant filters still cover current tool wording.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/common/filter -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/common/gcov -->
## sources/test-tools/xfstests/common/gcov

Purpose: this library captures kernel gcov data after fstests runs and optionally generates lcov/genhtml reports.

Important APIs: `__gcov_find_topdirs` finds the shallowest directories under `/sys/kernel/debug/gcov` that contain `.gcno` files. `_gcov_generate_report output_dir` copies raw gcov source directories, runs `lcov --capture`, optionally runs `genhtml`, and optionally renders `index.html` to text using `lynx`, `links`, or `elinks`. `_gcov_reset` writes `1` to the gcov reset knob. `_gcov_check_report_gcov` disables `REPORT_GCOV` if the running kernel does not expose a writable reset knob.

Control flow: report generation is entirely conditional. It returns immediately if no output directory was requested, kernel gcov support is absent, no `.gcno` directories exist, or `lcov` is unavailable. If supported, it copies `/sys/kernel/debug/gcov/*` into `raw/`, builds an lcov command with every top gcno directory, prepares optional HTML/text commands, and runs them with stdout/stderr captured under the output directory.

State and persistence: raw gcov trees are persisted under `<output_dir>/raw/`, the summary is `<output_dir>/gcov.report`, command logs are `gcov.stdout` and `gcov.stderr`, generated HTML lives under `output_dir`, and `index.txt` may be created. `_gcov_reset` mutates kernel coverage counters.

Dependencies and integration: it depends on debugfs gcov at `$GCOV_DIR`, `find`, `sort`, `uniq`, `$AWK_PROG`, `cp`, `lcov`, and optionally `genhtml` and terminal web browsers. `fstests_start_time` is used to title reports when available.

Risks: copying the full gcov tree can consume disk space and time. The topdir finder assumes the shallowest `.gcno` hierarchy is the desired lcov directory set. Missing optional tools silently reduce output. `_gcov_reset` does not guard against missing write permission; callers should use `_gcov_check_report_gcov`.

Test signals: the primary signals are non-empty `gcov.report`, successful `gcov.stdout`, lack of fatal messages in `gcov.stderr`, and optional `index.txt` with coverage summaries. If `REPORT_GCOV` is unset after checking, the kernel or permissions do not support collection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/common/gcov -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/common/parent -->
## sources/test-tools/xfstests/common/parent

Purpose: this XFS helper validates parent pointer records reported by `xfs_io parent`, including positive and negative checks around hardlinks, renames, and moves.

Important APIs: `_xfs_parse_parent_pointer parents pino name` parses colon-separated parent pointer records in `inode/generation/name_length/name` shape and exports parsed values in `PPINO`, `PPGEN`, `PPNAME_LEN`, and `PPNAME`. `_xfs_verify_parent parent_path parent_pointer_name child_path` checks filesystem objects, retrieves parent pointers for a child, validates the matching record, checks that the name resolves to the same inode as the child, and verifies path printing via `parent -p`. `_xfs_verify_no_parent parent_name pino child_path` asserts that no matching parent pointer exists.

Control flow: positive verification first checks existence of the parent directory, child file, and parent/name path. It obtains parent and child inodes with `stat`, queries `xfs_io -x -c "parent -s -i ... -n ..."`, parses the output, compares inodes, then iterates paths returned by `parent -p` and checks each with `test -ef`. Negative verification returns success when `xfs_io parent` fails or parsing cannot find the matching record.

State and persistence: no persistent state is created. The parser intentionally sets global shell variables for callers and diagnostic output. All checks operate below `$SCRATCH_MNT`.

Dependencies and integration: it requires `common/rc`, `$SCRATCH_MNT`, `$XFS_IO_PROG`, `stat`, and tests that have verified XFS parent pointer support. It integrates with golden output by printing `*** ... OK` and `*** Verified parent pointer` status lines.

Risks: array assignment `parents=($(...))` and unquoted path tests make spaces or special characters in test names unsafe. Error diagnostics include a likely typo `$PPPINO` instead of `$pppino`. `_xfs_parse_parent_pointer` reads from `echo "$parents"`, so records containing shell word splits can be damaged.

Test signals: successful positive checks end with `*** Parent pointer OK for child ...`; failures print missing objects, missing parent pointer records, bad name length, mismatched inode resolution, or bad path printing. Negative checks are silent unless a forbidden record is found.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/common/parent -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/common/preamble -->
## sources/test-tools/xfstests/common/preamble

Purpose: this file is the standard setup entry point for modern fstests scripts. It initializes per-test globals, installs cleanup, sources the common runtime, and records basic QA output.

Important APIs: `_cleanup` is the default cleanup that kills fsstress if available, changes to `/`, and removes `$tmp.*`. `_register_cleanup cleanup [signals...]` installs a trap for EXIT, HUP, INT, QUIT, TERM, and optional extra signals, appending `exit $status`. `_begin_fstest group...` is the canonical bootstrap called near the top of tests.

Control flow: `_begin_fstest` sources `common/exit` and `common/test_names`, rejects double invocation when `$seq` is already set, derives `seq` from `$0`, sets `seqres`, prints the QA output banner, initializes `here`, `tmp`, and `status=1`, registers cleanup, sources `./common/rc`, calls `init_rc`, and removes previous `$seqres.full` and `$seqres.hints`.

State and persistence: it creates no durable data directly, but it defines the core per-test state consumed by the rest of fstests: `seq`, `seqres`, `here`, `tmp`, and default failing `status`. It also removes stale full logs/hints for the current sequence and installs process-global shell traps.

Dependencies and integration: every test in this subset sources it first and calls `_begin_fstest` with group tags such as `auto`, `quick`, `snapshot`, `send`, `raid`, and `qgroup`. It depends on `common/exit`, `common/test_names`, `common/rc`, `_kill_fsstress`, and `_exit`.

Risks: cleanup is string-evaluated in `trap`, so callers must pass valid shell fragments. Because `status=1` is the default, tests must explicitly set `status=0` before exit. Removing `$tmp.*` assumes `$tmp` is always well-formed; `_begin_fstest` sets it to `${TMPDIR:-/tmp}/$$`.

Test signals: a correctly initialized test emits `QA output created by <seq>`, has a mounted/validated test device through `init_rc`, and exits with status zero only after setting `status=0`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/common/preamble -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/common/rc -->
## sources/test-tools/xfstests/common/rc

Purpose: this is the central fstests runtime library. It sources `common/config`, selects filesystem-specific helpers, mounts the test filesystem, manages scratch formatting/mounting/checking, performs requirement gating, normalizes environment-sensitive operations, and supplies shared workload, device, dmesg, fsck, sysfs, and utility helpers.

Important APIs and helper groups: synchronization uses `_sync_fs`, `_scratch_sync`, and `_test_sync`. Workload helpers include `_run_fsstress_bg`, `_run_fsstress`, `_wait_for_fsstress`, `_kill_fsstress`, `_populate_fs`, `_run_fsx`, `run_fsx`, `_run_hugepage_fsx`, `_pwrite_byte`, `_mread`, `_mwrite_byte`, and `_create_file_sized`. Mount and mkfs APIs include `_mount`, `_get_mount`, `_put_mount`, `_clear_mount_stack`, `_scratch_options`, `_test_options`, `_scratch_mount_options`, `_try_scratch_mount`, `_scratch_mount`, `_scratch_mount_idmapped`, `_scratch_unmount`, `_scratch_cycle_mount`, `_test_mount`, `_test_unmount`, `_scratch_mkfs`, `_scratch_mkfs_sized`, `_scratch_mkfs_geom`, `_scratch_mkfs_blocksized`, `_scratch_pool_mkfs`, `_try_mkfs_dev`, and `_mkfs_dev`.

Requirement APIs: the file exposes dozens of `_require_*` gates for scratch/test devices, minimum sizes, external log/realtime devices, loop devices, zoned devices, dm targets, direct I/O, io_uring, mount_setattr, idmapped mounts, xfs_io commands, users/groups, chown/chmod, sparse files, freeze, open_by_handle/exportfs, shutdown, dax, metadata journaling, fstrim, filefrag/FIBMAP, statx mount ids, btime, kernel config, reflink-adjacent in-place writes, fio/atomic writes, file attributes, fanotify ioerrors, and more.

Check and repair flow: `_repair_scratch_fs`, `_repair_test_fs`, `_check_generic_filesystem`, `_check_udf_filesystem`, `_check_test_fs`, `_check_dev_fs`, and `_check_scratch_fs` dispatch by `FSTYP`. XFS, btrfs, overlay, f2fs, UDF, ext*, network filesystems, tmpfs, ubifs, and bcachefs get special handling. Mounted filesystems are unmounted or remounted read-only for checks and restored afterwards.

State and persistence: the library sets and reads global harness state including `FSTYP`, `TEST_DEV`, `TEST_DIR`, `SCRATCH_DEV`, `SCRATCH_MNT`, `SCRATCH_DEV_POOL`, `SCRATCH_OPTIONS`, `TEST_OPTIONS`, `MOUNTED_POINT_STACK`, `RESULT_DIR`, `seqres`, `tmp`, `status`, `USE_EXTERNAL`, `MOUNT_OPTIONS`, `MKFS_OPTIONS`, `REPORT_LIST`, `REPORT_GCOV`, `IDMAPPED_MOUNTS`, and many tool path variables. It writes diagnostic data to `$seqres.full`, hints to `$seqres.hints`, dmesg/kmemleak/core artifacts beside `$seqres`, and marker files such as `${RESULT_DIR}/require_scratch`, `require_test`, and `check_dmesg`.

Control flow: at source time it establishes `BC`, sets umask, sources filesystem-specific helpers via `_source_specific_fs $FSTYP`, and optionally sources reporting. `init_rc` validates and mounts `TEST_DEV`, verifies mount placement and type, checks scratch is not unexpectedly mounted elsewhere, and adjusts `XFS_IO_PROG` for foreign filesystems and idle-thread support. Tests then call requirement helpers, format/mount scratch, run workloads, and rely on check/cleanup code to validate state.

Dependencies and integration: it is the integration spine for `common/preamble`, all btrfs tests in this subset, and filesystem-specific common files. It depends on core Unix tools, xfsprogs, btrfs-progs, e2fsprogs, f2fs-tools, util-linux, debugfs/sysfs/procfs, optional test binaries under `$here/src`, and many functions supplied by filesystem-specific common files.

Risks: the file is large and heavily global, so helper side effects can interact in subtle ways. Several helpers parse command output by field number or regex. Many device operations are destructive to scratch devices. Some code paths use `eval` (`_scratch_do_mkfs`, `_do`) and unquoted shell expansions, requiring trusted test inputs. Requirement helpers sometimes perform real mkfs/mount/write probes, which can alter scratch state.

Test signals: correct operation is observed indirectly through tests reaching `status=0`, clean `$seqres.full`, no `_notrun` unless prerequisites are absent, clean `_check_scratch_fs`, and no dmesg/kmemleak/core findings. Failures are usually explicit `_fail`/`_exit`, fsck diagnostics, command logs, or guard files left in `RESULT_DIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/common/rc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/common/ubifs -->
## sources/test-tools/xfstests/common/ubifs

Purpose: this tiny UBIFS helper exposes the usable logical eraseblock size for a UBI volume.

Important API: `_get_leb_size ubivol` prints `/sys/class/ubi/<basename(ubivol)>/usable_eb_size`.

Control flow: it takes one argument, strips any directory prefix with `basename`, and cats the corresponding sysfs attribute.

State and persistence: no state is created or mutated. It reads kernel sysfs only.

Dependencies and integration: callers must pass a valid UBI volume path, typically `$SCRATCH_DEV` or `$TEST_DEV` for `FSTYP=ubifs`. It depends on sysfs UBI class layout and `cat`.

Risks: missing arguments or invalid devices produce a raw `cat` error rather than `_notrun` or `_fail`. The function assumes UBI volume basename matches the sysfs directory name.

Test signals: success is a numeric usable eraseblock size on stdout. Failure indicates an invalid UBI volume, missing sysfs, or insufficient kernel UBIFS/UBI support.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/common/ubifs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/Makefile -->
## sources/test-tools/xfstests/tests/Makefile

Purpose: this makefile coordinates building and installing test subdirectories under `tests/`.

Important variables and targets: `TOPDIR = ..` and `include $(TOPDIR)/include/builddefs` pull in project build definitions. `TESTS_SUBDIRS` discovers lowercase child directories with `$(wildcard $(CURDIR)/[[:lower:]]*/)` and normalizes/sorts them. `SUBDIRS` is the relative lowercase directory list. The default target builds all `$(SUBDIRS)`. `install` depends on every `%-install` target derived from `TESTS_SUBDIRS` and creates `$(PKG_LIB_DIR)/$(TESTS_DIR)`. `install-dev` and `install-lib` intentionally do nothing. `%-install` recurses into each test subdir with `$(MAKE) $(MAKEOPTS) -C $* install`.

Control flow: `default` delegates to directory targets supplied by included build rules. `install` recurses into absolute-ish discovered subdirectories and then ensures the package test directory exists.

State and persistence: build/install state is external to the file and controlled by the included build system. Installation creates directories and files under package paths configured by `builddefs`.

Dependencies and integration: it depends on `include/builddefs`, `$(BUILDRULES)`, make recursion support in each lowercase subdirectory, and standard install tooling.

Risks: only lowercase-named subdirectories are discovered, so mixed-case test directories would be ignored. `TESTS_SUBDIRS` includes `$(CURDIR)` paths while `SUBDIRS` is relative, so included rules must tolerate that split. Recursive make failures propagate through the pattern target.

Test signals: `make -C tests` should recurse through every lowercase test directory. `make -C tests install` should install each subdirectory and create `$(PKG_LIB_DIR)/$(TESTS_DIR)` with mode 755.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/001 -->
## sources/test-tools/xfstests/tests/btrfs/001

Purpose: this quick btrfs test exercises basic subvolume and snapshot behavior, default subvolume selection, and subvolume deletion.

Control flow: after `_begin_fstest auto quick subvol snapshot`, it sources generic and btrfs filters, requires scratch, reformats and mounts it, creates `foo`, snapshots the root to `snap`, verifies root and snapshot directory listings diverge after removing `foo`, creates `subvol`, writes `bar`, sets `subvol` as the default using `_btrfs_get_subvolid`, remounts to verify the default view, mounts `subvolid=0` to restore root access, resets the default to root, lists subvolumes, deletes `snap`, and checks listings across a remount.

Important dependencies: `common/preamble`, `common/filter`, `common/filter.btrfs`, `_scratch_mkfs`, `_scratch_mount`, `_scratch_cycle_mount`, `_scratch_unmount`, `$BTRFS_UTIL_PROG`, `_btrfs`, `_btrfs_get_subvolid`, `_filter_scratch`, and `_filter_btrfs_subvol_delete`.

State and persistence: all state is on the scratch filesystem: `foo`, `snap`, `subvol`, default-subvolume metadata, and the file `bar`. The test resets the default subvolume to root before exit.

Risks: directory listing order can affect output if filesystem/tool behavior changes. A failed reset of the default subvolume can leave scratch in a confusing state until reformatted. The text contains a harmless typo in the printed "sbuvolid".

Test signals: expected stdout describes each operation and stable `ls` output. Failures are command errors from btrfs subvolume operations, mount failures after changing the default, or mismatched golden output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/002 -->
## sources/test-tools/xfstests/tests/btrfs/002

Purpose: this extended snapshot test verifies that modifying snapshots through allocation, append, read-modify-write, nested snapshots, and source deletion does not corrupt the original subvolume contents.

Important local APIs: `_save_checksum fs sumfile` records SHA256 checksums for all files under a tree. `_verify_checksum fs sumfile` runs `sha256sum -c` and prints failures. `_create_snap dest` creates a uniquely named snapshot under scratch and stores it in `SNAPNAME`. `_read_modify_write`, `_fill_blk`, and `_append_file` apply different write patterns to files in a target tree.

Control flow: it creates subvolume `sv1`, populates a deep compressible tree with `_populate_fs`, snapshots it, records checksums, modifies only the snapshot through block filling, appending, and read-modify-write, and repeatedly verifies the original. It then creates seven nested snapshots and verifies each against the original checksum. Finally it snapshots again, records the snapshot checksum, deletes all original files, and verifies the snapshot still matches.

State and persistence: scratch contains `sv1`, multiple `snap.*` snapshots, temporary checksum files under `$tmp`, and populated file trees. The test unmounts scratch at the end.

Dependencies: `common/preamble`, `common/filter`, `_require_scratch`, `_scratch_mkfs`, `_scratch_mount`, `_populate_fs`, `$BTRFS_UTIL_PROG`, `_ddt`, `dd`, `sha256sum`, `find`, and `stat`.

Risks: unquoted `find` results and checksum paths are unsafe for filenames with whitespace, though `_populate_fs` generates simple names. Background `dd` jobs use `wait $!`, which only waits for the last background job in some helpers; this is adequate for the generated workload but fragile as a pattern.

Test signals: the test prints `Silence is golden`; any `FAILED` checksum line or explicit `_fail` is a regression signal.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/003 -->
## sources/test-tools/xfstests/tests/btrfs/003

Purpose: this btrfs volume test covers multi-device mkfs profiles, device add, balance, physical device removal/re-addition, replace-like recovery, and device delete.

Important local APIs: `deletable_scratch_dev_pool` checks whether all scratch pool block devices expose a sysfs delete knob. `_test_raid0`, `_test_raid1`, `_test_raid10`, and `_test_single` format the scratch pool with corresponding data/metadata profiles and populate it. `_test_add` starts single-device, adds more devices, and balances. `_test_replace` simulates disk disappearance, verifies a missing device, adds another device, and balances. `_test_remove` deletes the last pool device and verifies `filesystem show` no longer lists it.

Control flow: after requiring scratch, a 4-device scratch pool, and `wipefs`, it skips RAID profiles on zoned btrfs, then runs the single, add, optional replace, and remove paths. Cleanup remounts/re-adds a removed SCSI device if needed.

State and persistence: it repeatedly reformats `SCRATCH_DEV_POOL`, writes populated trees, mutates btrfs device membership, and may remove/re-add a SCSI device via sysfs. Globals `dev_removed` and `removed_dev_htl` coordinate cleanup.

Dependencies: `common/rc` device-pool helpers, `_scratch_pool_mkfs`, `_scratch_mount`, `_populate_fs`, `_run_btrfs_balance_start`, `_devmgt_remove`, `_devmgt_add`, `$BTRFS_UTIL_PROG`, `$WIPEFS_PROG`, and sysfs block device management.

Risks: this is destructive to all devices in `SCRATCH_DEV_POOL`. Sysfs device removal is hardware/environment sensitive and skipped only if delete knobs are absent. The replace test assumes device ordering and can reduce coverage on zoned devices.

Test signals: the test should emit only `Silence is golden` plus full-log diagnostics. Failures include mkfs/add/delete/balance errors, missing-device detection failure, or a deleted device still appearing in `filesystem show`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/004 -->
## sources/test-tools/xfstests/tests/btrfs/004

Purpose: this metadata/fiemap test validates btrfs backreference walking by mapping file extents to physical addresses and resolving them back to the expected inode and path inside a snapshot.

Important local APIs: `_filter_extents` parses `filefrag -v` into `physical#length#logical#flags`. `_check_file_extents` logs and returns parsed extents. `_btrfs_inspect_addr` uses `btrfs inspect-internal logical-resolve` and checks the expected inode, logical offset, and root. `_btrfs_inspect_inum` uses `inode-resolve` to check the path. `_btrfs_inspect_check` combines `stat`, logical resolve, and inode resolve. `workout` drives the filesystem workload.

Control flow: it formats a 2 GiB scratch filesystem, runs write-heavy fsstress, snapshots it, remounts with compression, runs metadata noise, remounts with atime, optionally starts background fsstress noise, then samples files from the snapshot and validates every non-inline extent through btrfs backref resolution.

State and persistence: scratch contains random fsstress trees, snapshot `snap1`, a `next` directory, and transient `bgnoise`. `$tmp.running` controls the background noise loop. Diagnostics are appended to `$seqres.full`.

Dependencies: `filefrag`, `btrfs inspect-internal logical-resolve`, `inode-resolve`, fsstress, `_scratch_mkfs_sized`, `_run_fsstress`, `_btrfs`, and generic filters.

Risks: sampling files with `shuf` introduces runtime variability, though output is mostly diagnostic. Inline extents are skipped because logical-resolve cannot map them. Background noise increases race coverage but can make failures timing-dependent. The cleanup `rm $tmp.running` can complain if the file is already gone.

Test signals: stdout should show `*** test backref walking` and `*** done`. Any unexpected logical/inode resolve output or accumulated extent errors triggers `_fail`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/005 -->
## sources/test-tools/xfstests/tests/btrfs/005

Purpose: this online defragmentation test checks file, directory, and filesystem defrag paths, including compressed defrag and invalid/edge range arguments.

Important local APIs: `_create_file mode` writes a fragmented file backward and records its md5sum. `_btrfs_online_defrag object range compress` builds `btrfs filesystem defragment` options and tolerates historical return code 20 as success. `_checksum` validates the md5sum. `_setup_defrag`, `_cleanup_defrag`, and `_rundefrag` compose mkfs, mount, file creation, defrag, checksum, unmount, and fs check.

Control flow: it first verifies scratch and defrag support, then runs a matrix: single file default with compression off/on; single file invalid negative start; start beyond EOF; negative length; length beyond file size; partial length; directory defrag; and whole filesystem defrag.

State and persistence: scratch is reformatted for each matrix row. `/tmp/checksum` is a global checksum side effect outside `$tmp`, which is a legacy risk. `$seqres.full` captures defrag diagnostics.

Dependencies: `common/defrag`, `$BTRFS_UTIL_PROG`, `_require_defrag`, `_scratch_mkfs`, `_scratch_mount`, `_scratch_cycle_mount`, `_check_scratch_fs`, `md5sum`, and `dd`.

Risks: storing checksum at `/tmp/checksum` can conflict with parallel tests. Cases labelled "should fail" do not require the command to fail; they only report unexpected non-success based on return code, so golden output captures behavior. Range option semantics can vary with btrfs-progs versions.

Test signals: printed matrix labels and no checksum failures are expected. Regressions show as `btrfs filesystem defragment failed!`, `md5 checksum failed!`, or scratch fs check failures.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/006 -->
## sources/test-tools/xfstests/tests/btrfs/006

Purpose: this quick volume sanity test exercises basic btrfs informational commands across a multi-device scratch pool.

Control flow: it identifies the first and last scratch pool devices, counts pool devices, formats the whole pool, sets and reads a filesystem label while unmounted, mounts scratch, shows the filesystem by label and UUID, syncs by mountpoint, and displays device stats by mountpoint, scratch device, first pool device, and last pool device.

State and persistence: scratch pool devices are formatted as one btrfs filesystem with label `TestLabel.$seq`. The UUID is discovered from `filesystem show` and used for filtered output.

Dependencies: `common/preamble`, `common/filter.btrfs`, `_require_scratch`, `_require_scratch_dev_pool`, `_scratch_pool_mkfs`, `_scratch_mount`, `$BTRFS_UTIL_PROG`, `_filter_btrfs_filesystem_show`, `_filter_btrfs_device_stats`, and `_filter_spaces`.

Risks: the test assumes pool devices are valid and visible by btrfs-progs both mounted and unmounted. Device stats formatting changes require filter updates. Labels derived from `$seq` must be accepted by btrfs label constraints.

Test signals: stable headings such as `== Set filesystem label`, filtered filesystem-show output with the expected device count, and zeroed/normalized device stats. Failures are direct btrfs command errors or output diffs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/007 -->
## sources/test-tools/xfstests/tests/btrfs/007

Purpose: this send/receive test verifies full and incremental btrfs send streams preserve filesystem content generated by fsstress.

Control flow: `workout` formats a 2 GiB scratch filesystem, mounts with `noatime`, runs fsstress while creating a read-only `base` snapshot, creates a read-only `incr` snapshot, sends both snapshots to files in `$TEST_DIR/btrfs-test-$seq`, records fssum manifests for base and incr, reformats scratch, receives the base and incremental streams, and verifies received trees against the saved fssum manifests.

State and persistence: send streams and fssum files live under `TEST_DIR`, not scratch, so they survive scratch reformat. Scratch is overwritten midway. Cleanup removes the send directory and kills fsstress.

Dependencies: `_require_scratch`, `_require_fssum`, `_require_seek_data_hole`, `_scratch_mkfs_sized`, `_run_fsstress`, `$BTRFS_UTIL_PROG send/receive`, `_btrfs`, `run_check`, and `$FSSUM_PROG`.

Risks: the test depends on enough space in `TEST_DIR` to hold send streams. fsstress randomness can change coverage. SELinux/xattr behavior is not explicitly disabled here, so fssum options must be sufficient for stable comparison. Send stream failures may leave large files until cleanup.

Test signals: expected stdout is `*** test send / receive` and `*** done`; failures come from send/receive nonzero exits or fssum mismatches.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/007 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/008 -->
## sources/test-tools/xfstests/tests/btrfs/008

Purpose: this quick send regression test checks a historical ENOENT failure path by sending a read-only snapshot with nested directories/files and receiving it onto scratch.

Control flow: it requires test and scratch filesystems, reformats scratch, disables `SELINUX_MOUNT_OPTIONS` so receive can set security xattrs, mounts scratch, creates a test-side subvolume `send`, populates directories and random files, creates two read-only snapshots `backup2` and `backup3`, sends `backup3` to a dump file, and receives it into scratch.

State and persistence: the source subvolume and snapshots are created under `TEST_DIR/send_temp_$seq`, while the receive target is scratch. Cleanup deletes snapshots/subvolumes and the temp directory.

Dependencies: `_require_test`, `_require_scratch`, `_scratch_mkfs`, `_scratch_mount`, `$BTRFS_UTIL_PROG subvolume/send/receive`, `_ddt`, and generic filters.

Risks: source data is created on `TEST_DIR`, so the test assumes the test filesystem itself is btrfs-capable enough for subvolume creation. SELinux option override is required for receive; without it, xattr restoration can fail. Cleanup assumes specific snapshot names exist but suppresses errors.

Test signals: the intended output is `Silence is golden`. Any failure in subvolume creation, snapshot, send, or receive triggers `_fail`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/008 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/009 -->
## sources/test-tools/xfstests/tests/btrfs/009

Purpose: this quick subvolume regression test verifies that deleting the current default subvolume does not make the filesystem unmountable.

Control flow: it formats and mounts scratch, creates subvolume `newvol`, obtains its subvolume id, sets it as default, attempts to delete the subvolume, unmounts, and then requires that mounting scratch still succeeds.

State and persistence: scratch default subvolume metadata is changed. The delete command output is logged but not asserted directly; the final mount is the behavioral check.

Dependencies: `_require_scratch`, `_scratch_mkfs`, `_scratch_mount`, `_scratch_unmount`, `_try_scratch_mount`, `$BTRFS_UTIL_PROG`, and `_btrfs_get_subvolid`.

Risks: if deletion behavior changes to a different error message but mount still works, the test still passes. A successful delete followed by mount success would be surprising but not separately checked beyond btrfs semantics and golden output.

Test signals: expected stdout is `Silence is golden`. Failure occurs if create/set-default fail or the post-delete mount fails.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/009 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/010 -->
## sources/test-tools/xfstests/tests/btrfs/010

Purpose: this delayed allocation accounting regression test checks that many outstanding extents merged into one do not leak btrfs metadata reservation.

Control flow: it requires a mounted test filesystem and btrfs sysfs, writes 32K separated 4K extents to `$TEST_DIR/$seq`, writes the 32K gaps to force extent merging while reservations exist, runs `sync`, finds the filesystem UUID with `findmnt`, enters `/sys/fs/btrfs/$uuid/allocation`, and prints a leak message only if `metadata/bytes_may_use - global_rsv_reserved` is nonzero.

State and persistence: it creates one large test file and removes it in cleanup. It reads btrfs sysfs allocation counters and writes no scratch state.

Dependencies: `_require_test`, `_require_btrfs_fs_sysfs`, `$XFS_IO_PROG`, `findmnt`, sysfs btrfs allocation files, and shell arithmetic.

Risks: the loop performs 65,536 xfs_io invocations, so it is slow and sensitive to filesystem size. The sysfs counter expression assumes `bytes_may_use` and `global_rsv_reserved` semantics remain comparable. Cleanup removes the file but not partial sysfs state because none is created.

Test signals: success prints `0 bytes leaked` filtered away by `grep -v`, followed by `Silence is golden`. Any nonzero leak line is a regression signal.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/010 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/011 -->
## sources/test-tools/xfstests/tests/btrfs/011

Purpose: this broad replace test exercises btrfs device replace across multiple data/metadata profiles, with optional cancellation, scrub validation, btrfs check, and remount validation.

Important local APIs: `fill_scratch fssize with_cancel` creates inline/data extents and a filler file large enough to keep replace active. `workout mkfs_options num_devs with_cancel fssize` configures a scratch pool plus spare, formats, fills, and invokes replace scenarios. `btrfs_replace_test source target options with_cancel quick` runs replace, optionally cancels it, kills background noise, scrubs, unmounts, checks the filesystem, and remounts with the appropriate source/target device.

Control flow: it requires scratch without final automatic check, five equal-sized scratch devices, at least 10 GiB scratch, and `wipefs`. It filters supported profile configs, then iterates single, dup, raid0, raid1, raid10, mixed, raid5, and raid6 cases where supported. Mirror profiles also test reverse replace with `-r` unless cancellation was involved.

State and persistence: all scratch pool devices are repeatedly wiped and reformatted. `SPARE_DEV`, `SCRATCH_DEV_POOL_SAVED`, and `SCRATCH_DEV_NAME` are managed by rc helpers. Background noise writes `$SCRATCH_MNT/noise`. `$tmp.tmp` stores replace status.

Dependencies: btrfs-progs replace/scrub/filesystem show, `_btrfs_get_profile_configs`, device-pool helpers, `_require_fs_space`, `_check_btrfs_filesystem`, `_scratch_pool_mkfs`, and `$XFS_IO_PROG`.

Risks: destructive multi-device test with timing-sensitive cancellation. If replace finishes before cancel, the test performs a repair replace-back path but still reports a status mismatch. Large direct writes and `/dev/urandom` noise can stress storage heavily.

Test signals: expected stdout is `*** test btrfs replace` and `*** done`. Full-log evidence includes replace status `finished` or `canceled`, scrub success, btrfs check success, and remount success.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/011 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/012 -->
## sources/test-tools/xfstests/tests/btrfs/012

Purpose: this conversion test verifies `btrfs-convert` from ext4 to btrfs, archived ext image integrity, rollback to ext4, and rollback failure after deleting the saved image subvolume.

Control flow: it requires scratch without automatic check, `btrfs-convert`, `mkfs.ext4`, `e2fsck`, `fssum`, non-zoned scratch, loop support, and ext4 kernel support. It creates an ext4 filesystem with test block size, mounts it manually, populates it with fsstress, records fssum, unmounts, converts to btrfs, mounts as btrfs, verifies original data, fscks the archived image, loop-mounts and verifies archived image contents, writes new btrfs data, rolls back, fscks and mounts restored ext4, verifies original data, converts again, deletes `ext2_saved`, and expects rollback to fail.

State and persistence: scratch changes filesystem type multiple times. Fssum baseline is stored in `$tmp.original`. A loop mount is created inside scratch at `mnt`.

Dependencies: `btrfs-convert`, ext4 tools, `mount`, `_run_fsstress`, `$FSSUM_PROG`, `_try_scratch_mount`, `$BTRFS_UTIL_PROG`, `_require_loop`, and `_require_extra_fs`.

Risks: conversion is destructive and incompatible with zoned devices. Block sizes larger than page size can make ext4 mount unsupported and produce notrun. SELinux mount options are disabled to avoid xattr mismatches. The final expected failure asserts return code exactly 1.

Test signals: fssum comparisons must pass, e2fsck must pass on archived/restored images, and final rollback after deleting `ext2_saved` must fail with code 1.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/012 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/013 -->
## sources/test-tools/xfstests/tests/btrfs/013

Purpose: this quick balance/prealloc regression test ensures balancing a preallocated extent with checksummed data does not produce missing or failed checksum reports.

Control flow: it records current dmesg counts for `no csum found` and `csum failed`, creates a preallocated 1 MiB file with an 8 KiB write at 16 KiB, runs a btrfs balance, remounts scratch, reads the file back, and checks dmesg counts did not increase.

State and persistence: scratch contains `foo`; dmesg is read before and after. `$seqres.full` captures xfs_io and balance logs.

Dependencies: `_require_scratch`, `_require_xfs_io_command "falloc"`, `$XFS_IO_PROG`, `_run_btrfs_balance_start`, `_scratch_unmount`, `_scratch_mount`, and `dmesg`.

Risks: dmesg count comparison is global to the host and can be affected by unrelated btrfs activity. It relies on exact kernel log substrings. It reads post-remount to force checksum validation.

Test signals: expected output is `Silence is golden`. A pread error or increased checksum log count triggers `_fail`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/013 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/014 -->
## sources/test-tools/xfstests/tests/btrfs/014

Purpose: this balance stress test runs repeated snapshot create/delete operations concurrently with repeated balance operations.

Important local APIs: `_create_snapshot` loops 20 times creating and deleting `snapshot0`. `_balance` loops 20 times running `_run_btrfs_balance_start`.

Control flow: it requires scratch, formats and mounts it, prints a dmesg hint, starts `_create_snapshot` in the background, starts `_balance` in the background, and waits for both.

State and persistence: scratch is repeatedly modified by temporary snapshots and balance relocation. `$seqres.full` receives balance logs.

Dependencies: `$BTRFS_UTIL_PROG`, `_run_btrfs_balance_start`, `_scratch_mkfs`, `_scratch_mount`, and shell job control.

Risks: no explicit content verification is performed; the test is intended to expose crashes, warnings, or command failures. Both background functions operate on the same scratch root, so races are intentional. Snapshot command failures are not wrapped in `_fail`.

Test signals: exit success plus absence of dmesg errors is the primary signal. The printed hint tells humans to inspect dmesg on failure.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/014 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/015 -->
## sources/test-tools/xfstests/tests/btrfs/015

Purpose: this quick snapshot/remount regression test verifies that a filesystem mounted read-only and then remounted read-write can still create snapshots.

Control flow: it requires scratch, formats it, mounts with `-o ro`, remounts with `-o rw,remount`, and creates a snapshot of the scratch root at `$SCRATCH_MNT/snap`.

State and persistence: scratch contains the created `snap` subvolume. Mount state transitions from ro to rw in place.

Dependencies: `_scratch_mkfs`, `_scratch_mount`, `$BTRFS_UTIL_PROG subvolume snapshot`, and generic filters.

Risks: `_scratch_mount -o rw,remount` relies on the helper passing mount arguments in a way accepted by util-linux and btrfs. The test does not explicitly check mount flags after remount; snapshot success is the proof.

Test signals: success prints `Silence is golden`; failure is inability to create the snapshot after remount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/015 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/016 -->
## sources/test-tools/xfstests/tests/btrfs/016

Purpose: this send/prealloc regression test verifies that hole punching between two snapshots is represented correctly in incremental send/receive.

Control flow: it creates a btrfs subvolume under scratch, writes a 10 MiB file, snapshots it read-only as `snap`, punches a 1 MiB hole at offset 1 MiB in the live file, snapshots as `snap1`, records fssum manifests for both snapshots with atime and xattrs disabled, sends full and incremental streams to `$tmp`, reformats scratch, receives both streams, and verifies both received snapshots against their manifests.

State and persistence: send streams and fssum manifests are in a private temporary directory from `mktemp -d`; scratch is reformatted midway. The tested state is subvolume snapshots containing `foo` before and after hole punching.

Dependencies: `_require_fssum`, `_require_xfs_io_command "falloc"`, `$XFS_IO_PROG fpunch`, `$BTRFS_UTIL_PROG send/receive`, `_scratch_mkfs`, and `_scratch_mount`.

Risks: the script overrides `tmp` with `mktemp -d`, diverging from preamble's `$tmp` pattern and relying on the default cleanup. Xattr checks are disabled intentionally, so the signal is file data and hole layout, not metadata.

Test signals: fssum generation and restore must pass for both snapshots; send/receive failures trigger `_fail`; expected stdout is `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/016 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/017 -->
## sources/test-tools/xfstests/tests/btrfs/017

Purpose: this quick qgroup regression test checks accounting when shared extents are removed from a root and its snapshot.

Control flow: it requires scratch qgroup support and the `cloner` binary, formats btrfs with 64 KiB node size, mounts it, computes block/extent sizes, writes a direct-I/O extent to `foo`, snapshots scratch to `snap`, reflink-clones that extent into `foo-reflink` in both the root and snapshot plus a second snapshot clone, enables quotas, runs a quota rescan, removes all cloned files from both roots, syncs, and prints qgroup referenced/exclusive values.

State and persistence: scratch contains root and snapshot subvolumes, reflinked extents, qgroup metadata, and deleted extents. Output units come from `_btrfs_qgroup_units`.

Dependencies: `_require_scratch_qgroup`, `_require_cloner`, `$CLONER_PROG`, `_btrfs quota`, `_btrfs qgroup`, `$XFS_IO_PROG`, and `_filter_xfs_io_blocks_modified`.

Risks: qgroup output format and units depend on btrfs-progs helpers. The test primarily looks for warnings/accounting regressions, so exact numeric output is filtered but still version-sensitive. Requires reflink support through cloner.

Test signals: no warning/crash and stable qgroup output after deletions. Unexpected qgroup accounting or dmesg warnings indicate the targeted regression.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/017 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/018 -->
## sources/test-tools/xfstests/tests/btrfs/018

Purpose: this quick subvolume regression test verifies that one subvolume can be moved into another subvolume.

Control flow: it requires scratch, formats and mounts it, creates `test1` and `test2` subvolumes, then runs `mv $SCRATCH_MNT/test1 $SCRATCH_MNT/test2`.

State and persistence: scratch ends with `test1` nested under `test2` if the move succeeds.

Dependencies: `_scratch_mkfs`, `_scratch_mount`, `$BTRFS_UTIL_PROG subvolume create`, and standard `mv`.

Risks: the second create failure message incorrectly says "couldn't create test1". The test checks only the move command return code, not the final subvolume topology.

Test signals: expected output is `Silence is golden`; create or move failure triggers `_fail`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/018 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/019 -->
## sources/test-tools/xfstests/tests/btrfs/019

Purpose: this quick send regression test targets kernel bugzilla 60673, where incremental send could fail when identical directory contents were recreated in a different order with different inode numbers.

Control flow: it requires test and scratch filesystems, disables SELinux mount options for receive, mounts scratch, creates a source subvolume under `TEST_DIR`, builds a directory tree, snapshots it read-only as `snap1`, sends and receives it, deletes/recreates the tree in a different creation order, snapshots as `snap2`, sends an incremental stream from `snap1` to `snap2`, and receives it.

State and persistence: source subvolume, snapshots, and send dumps live under `TEST_DIR/send_temp_$seq`; received snapshots land on scratch. Cleanup deletes all subvolumes and temp files.

Dependencies: `$BTRFS_UTIL_PROG subvolume/send/receive`, `_require_test`, `_require_scratch`, `_scratch_mkfs`, `_scratch_mount`, and generic filters.

Risks: like btrfs/008, the source side assumes `TEST_DIR` supports btrfs subvolumes. The test validates successful receive but does not do a content checksum; the recreated topology is simple enough that receive success is the regression signal.

Test signals: expected output is `Silence is golden`; any send/receive or snapshot command failure triggers `_fail`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/019 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/020 -->
## sources/test-tools/xfstests/tests/btrfs/020

Purpose: this quick replace/volume regression test verifies btrfs refuses device replace on a read-only mounted filesystem.

Control flow: it requires a three-device scratch pool, records the kernel commit hint for the fix, takes two devices plus a spare, formats RAID1 data/metadata, mounts scratch read-only, runs `btrfs replace start -B 2 $SPARE_DEV $SCRATCH_MNT`, filters blank lines and scratch paths from the expected failure output, unmounts, and releases the spare/pool.

State and persistence: scratch pool devices are formatted as RAID1; no successful replace should occur. `SPARE_DEV` and scratch pool globals are restored.

Dependencies: `_require_scratch_dev_pool`, `_scratch_dev_pool_get`, `_spare_dev_get`, `_scratch_pool_mkfs`, `_scratch_mount -o ro`, `$BTRFS_UTIL_PROG replace`, and `_filter_scratch`.

Risks: the replace command is expected to fail, but the script does not explicitly assert nonzero return; golden output must reflect the failure message. Device id `2` assumes btrfs device numbering after mkfs.

Test signals: stable filtered error output is expected. A silent successful replace or changed error message can produce golden output differences.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/020 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/021 -->
## sources/test-tools/xfstests/tests/btrfs/021

Purpose: this quick balance/defrag regression test races balance against snapshot-aware defragmentation writeback to catch a historical crash path.

Important local API: `run_test` starts `_run_btrfs_balance_start` in the background, sleeps briefly, defragments all files found under scratch with `btrfs filesystem defrag -f`, syncs, and waits for balance completion.

Control flow: it formats and mounts scratch, creates 101 padding files to increase btree height, creates 51 fragmented files by writing 20 blocks backward with direct I/O, syncs metadata to disk, then runs the balance/defrag race.

State and persistence: scratch contains padding files and fragmented `foo-*` files. `$seqres.full` captures xfs_io and balance logs.

Dependencies: `_require_scratch`, `_scratch_mkfs`, `_scratch_mount`, `$XFS_IO_PROG`, `_filter_xfs_io`, `$BTRFS_UTIL_PROG filesystem defrag`, `find`, `xargs`, and `_run_btrfs_balance_start`.

Risks: race coverage depends on timing (`sleep 0.5`) and filesystem/device speed. Newer btrfs-progs defrag path output is redirected to `/dev/null` to avoid golden changes. No explicit content check is performed.

Test signals: success prints `Silence is golden`; crashes, command failures, dmesg warnings, or balance/defrag failures indicate regression.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/021 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/022 -->
## sources/test-tools/xfstests/tests/btrfs/022

Purpose: this qgroup limit test verifies that a subvolume with a 5 MiB qgroup limit rejects a 10 MiB write.

Important local API: `_limit_test_exceed` creates subvolume `a`, enables quotas, finds its subvolume id, applies `qgroup limit 5M`, attempts to write 10 MiB with `_ddt`, and fails the test if the write succeeds.

Control flow: it requires scratch, qgroup rescan support, qgroup report support, and no compression, then formats/mounts scratch, runs the exceed test, unmounts, and checks scratch.

State and persistence: scratch contains subvolume `a`, quota metadata, and a partially written or rejected file. `units` is initialized from `_btrfs_qgroup_units` for consistency with reporting helpers.

Dependencies: `_require_qgroup_rescan`, `_require_btrfs_qgroup_report`, `_require_no_compress`, `_btrfs subvolume/quota/qgroup`, `_btrfs_get_subvolid`, `_ddt`, and `_check_scratch_fs`.

Risks: compression must be disabled because compressed data usage can avoid the intended limit. The test only checks that the write command returns nonzero, not the exact errno. qgroup enforcement timing must be synchronous enough for the dd failure.

Test signals: expected output is `Silence is golden`; if the oversized write succeeds, `_fail "quota should have limited us"` is emitted.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/022 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/023 -->
## sources/test-tools/xfstests/tests/btrfs/023

Purpose: this quick RAID profile test verifies that mkfs creates requested btrfs data and metadata block group profiles.

Important local APIs: `create_group_profile profile` formats the scratch pool with `-d<profile> -m<profile>`. `check_group_profile expected` mounts scratch, captures `btrfs filesystem df`, unmounts, and verifies both `Data` and `Metadata` lines contain the expected profile string.

Control flow: it requires a four-device scratch pool and a non-zoned scratch device, then tests raid0, raid1, and raid10. If `/sys/fs/btrfs/features/raid56` exists, it also tests raid5 and raid6.

State and persistence: each profile test reformats the scratch pool and creates a new btrfs filesystem.

Dependencies: `_require_scratch_dev_pool`, `_require_non_zoned_device`, `_scratch_pool_mkfs`, `_scratch_mount`, `$BTRFS_UTIL_PROG filesystem df`, and sysfs btrfs feature files.

Risks: zoned btrfs supports only single profile, hence the non-zoned gate. RAID56 coverage is conditional on kernel feature exposure. Grep matching assumes `filesystem df` format includes `Data` and `Metadata` profile tokens exactly.

Test signals: expected output is `Silence is golden`; missing profile text for either data or metadata triggers `_fail`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/023 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/024 -->
## sources/test-tools/xfstests/tests/btrfs/024

Purpose: this quick compression regression test checks that setting a file compression flag while filesystem compression is disabled does not oops when writing data.

Important local API: `__workout` creates `tmpfile`, applies `chattr =c`, writes 1 MiB with xfs_io, and filters xfs_io output.

Control flow: it requires scratch and that btrfs is not mounted with nodatacow, then runs the workout on a filesystem mounted with `compress=no`, unmounts and checks scratch, then repeats with `compress-force=no`.

State and persistence: scratch is reformatted twice and contains `tmpfile` in each run. File attributes are mutated by `chattr`.

Dependencies: `_require_btrfs_no_nodatacow`, `$CHATTR_PROG`, `$XFS_IO_PROG`, `_filter_xfs_io`, `_scratch_mkfs`, `_scratch_mount`, `_scratch_unmount`, and `_check_scratch_fs`.

Risks: the command `$CHATTR_PROG =c` depends on btrfs chattr syntax for setting compression attribute. The second run does not call `_check_scratch_fs` after unmount, relying on framework behavior or prior checks.

Test signals: headings `*** test compress=no`, `*** test compress-force=no`, and `*** done`; failures are write errors, fs check failures, or kernel crashes/oopses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/024 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/025 -->
## sources/test-tools/xfstests/tests/btrfs/025

Purpose: this quick send/clone/prealloc regression test ensures incremental send does not emit unaligned clone operations that make receive fail.

Control flow: it creates `foo`, truncates and preallocates ranges, writes a short unaligned range, snapshots as `mysnap1`, truncates to a different unaligned size, snapshots as `mysnap2`, sends full and incremental streams to `$tmp`, records md5s for live and snapshot files, checks the filesystem, reformats scratch, receives both streams, and records md5s for received snapshots.

State and persistence: temporary send streams live in a `mktemp -d` directory. Scratch is reformatted between send and receive phases. Snapshots `mysnap1` and `mysnap2` preserve the tested file states.

Dependencies: `_require_scratch`, `_require_xfs_io_command "falloc"`, `$XFS_IO_PROG`, `_btrfs filesystem sync`, `_btrfs subvolume snapshot`, `_btrfs send/receive`, `_check_btrfs_filesystem`, and `_filter_scratch`.

Risks: md5 output is path-filtered but not compared programmatically; golden output is the oracle. The test targets precise unaligned offsets and lengths, so changing them could miss the bug. It overrides `tmp` with a directory and cleanup removes it.

Test signals: receive must succeed for both streams, filesystem checks must pass before and after receive, and md5 output should match expected golden values.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/025 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/026 -->
## sources/test-tools/xfstests/tests/btrfs/026

Purpose: this quick compression/preallocation regression test verifies direct I/O writes spanning preallocated and compressed extents complete correctly and persist across remount.

Control flow: it formats and mounts scratch with compression, creates a compressed extent in `foo` at 700K-800K, preallocates 600K-700K, writes 80K direct I/O across 640K-720K, then creates a large `bar` case with a 128M compressed extent, preallocation to 258M, and a 256M direct I/O write from 3M. It prints md5s for both files before and after `_scratch_cycle_mount`.

State and persistence: scratch contains `foo` and `bar` with mixed compressed, preallocated, direct, and buffered data. The remount checks persistence and page-cache independence.

Dependencies: `_require_xfs_io_command "falloc"`, `$XFS_IO_PROG`, `_filter_xfs_io`, `_scratch_mkfs`, `_scratch_mount "-o compress"`, `_scratch_cycle_mount`, and `md5sum`.

Risks: large writes require significant scratch space and time. The expected data ranges are documented in comments but validated only by md5 golden output. Compression behavior can vary by kernel/progs/mount options but the fixed byte patterns should force the intended extent types.

Test signals: stable md5s before and after remount and no direct I/O/writeback assertion or command failure.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/026 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/027 -->
## sources/test-tools/xfstests/tests/btrfs/027

Purpose: this replace/raid regression test verifies replacing a missing btrfs device across supported profile configurations.

Important local API: `run_test mkfs_opts` reserves one spare device, formats the remaining pool with the requested profile, writes data files, wipes the second device to simulate loss, remounts degraded, replaces the missing device id with the spare using `replace start -B -f -r`, scrubs, unmounts, checks the filesystem, and releases pool state.

Control flow: it requires scratch without automatic check, five equal-sized pool devices, profile configs for `replace-missing`, and `wipefs`, then loops over `_btrfs_profile_configs`.

State and persistence: each loop destroys and recreates scratch pool filesystems. One pool member is wiped to simulate a missing device; the spare becomes part of the filesystem if replace succeeds.

Dependencies: `_btrfs_get_profile_configs`, device-pool helpers, `$WIPEFS_PROG`, `$BTRFS_UTIL_PROG filesystem show/replace/scrub`, `_ddt`, `_check_scratch_fs`, and degraded btrfs mount support.

Risks: destructive to all pool devices. The missing device is selected as the second device and its btrfs device id is parsed from `filesystem show`, which is format-sensitive. Failed cases return from the loop after cleanup rather than failing globally, so coverage can be conditional.

Test signals: stdout starts with `Silence is golden`; full-log entries identify each profile. Replace, scrub, and fs check must succeed for effective coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/027 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/028 -->
## sources/test-tools/xfstests/tests/btrfs/028

Purpose: this qgroup/balance stress test checks qgroup accounting while extents are dereferenced during relocation.

Control flow: it requires scratch and btrfs qgroup report support, formats and mounts scratch, enables quota, runs qgroup rescan, starts fsstress in the background with operations weighted toward writes, unlinks, creates, and fsyncs, starts `_btrfs_stress_balance` in the background, sleeps for `30 * TIME_FACTOR`, kills fsstress and balance, and relies on post-test btrfs check to validate qgroup accounting.

State and persistence: scratch contains a stress directory with rapidly changing files and quota metadata. `balance_pid` tracks the background balance process for cleanup.

Dependencies: `_scale_fsstress_args`, `_run_fsstress_bg`, `_kill_fsstress`, `_btrfs_stress_balance`, `_btrfs_kill_stress_balance_pid`, `_qgroup_rescan`, and `_require_btrfs_qgroup_report`.

Risks: timing-sensitive stress test; 30 seconds may be insufficient on some systems or excessive on slow ones. There is no direct qgroup output comparison; validation is deferred to btrfs check after unmount. Cleanup must kill both background workload and balance to avoid spillover.

Test signals: expected output is `Silence is golden`; qgroup accounting failures are expected to surface during btrfs check/fsck or as kernel warnings.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/028 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/029 -->
## sources/test-tools/xfstests/tests/btrfs/029

Purpose: this quick clone test verifies reflink behavior across different filesystems and across different mountpoints of the same btrfs filesystem.

Control flow: it requires test, scratch, and `cp --reflink` support, creates a test output directory, formats and mounts scratch, writes an original file, tests copying from scratch to test filesystem with `--reflink=auto` and `--reflink=always`, then bind/mounts the scratch device at the test directory and repeats `--reflink=auto` and `--reflink=always` between two mountpoints of the same filesystem. It unmounts the extra mountpoint at the end.

State and persistence: scratch contains `original`; `TEST_DIR/test-$seq` contains copy targets and temporarily becomes a second mountpoint for `SCRATCH_DEV`.

Dependencies: `common/reflink`, `_require_cp_reflink`, `$XFS_IO_PROG`, `cp`, `_mount`, `$UMOUNT_PROG`, `_filter_testdir_and_scratch`, and `md5sum`.

Risks: comments say same-filesystem `--reflink=always` should succeed, but an in-code comment before that command still says "should fail outright"; the actual md5 check expects a copy to exist. Extra mount cleanup is manual via `$UMOUNT_PROG`, not `_unmount`. Coreutils versions differ in whether a failed destination file is created, so `ls` output is logged only to `$seqres.full`.

Test signals: different-device `--reflink=auto` should produce identical md5s via fallback, different-device `--reflink=always` should print `cp reflink failed`, and same-device different-mountpoint auto/always copies should yield matching md5s.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/029 -->
