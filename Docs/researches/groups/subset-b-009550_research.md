# Research: subset-b-009550

Grouped source research for xfstests generic, nfs, ocfs2, and overlay test scripts. Each section preserves the source path and is intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/747 -->

# sources/test-tools/xfstests/tests/generic/747


Purpose: Stresses zoned/GC behavior by filling an 8GiB scratch filesystem to 95 percent with random-size direct writes, then mixing direct and buffered writes with random deletes to force reclaim and fragmentation.


Important APIs, helpers, and commands: Shell helpers `_create_file`, `_total_M`, `_used_percent`, `_delete_random_file`, `_get_random_fsz`, `_direct_fillup`, `_mixed_write_delete`; xfstests gates `_require_scratch` and `_require_no_compress`.
 Local helper functions detected in the file include `_create_file`, `_delete_random_file`, `_direct_fillup`, `_get_random_fsz`, `_mixed_write_delete`, `_total_M`, `_used_percent`.
 It imports `./common/preamble`.
 Capability gates include `_require_no_compress`, `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: Seeds `$RANDOM`, formats and mounts scratch, fills with direct I/O until the target usage, runs a direct mixed write/delete pass, runs a buffered pass, then syncs. The state is scratch files `data_$testseq`, filesystem free-space counters, and the PRNG seed in `$seqres.full`; all persistent effects are disposable scratch contents. Dependencies are `dd`, `stat -f`, `find`, `shuf`, scratch mkfs/mount/sync helpers, and a non-compressed filesystem. Main risks are space accounting drift, random delete finding no file, direct-I/O alignment, and runtime on slow zoned devices. Success is absence of write failures plus the printed phase markers and final sync. Source size is 119 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/747 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/748 -->

# sources/test-tools/xfstests/tests/generic/748


Purpose: Regression loop for a Btrfs fsync crash involving preallocation beyond i_size, xattr updates, direct writes that extend i_size, and fdatasync/logging races.


Important APIs, helpers, and commands: Uses `common/attr`, `_require_attrs`, `_require_odirect`, `_require_xfs_io_command falloc -k`, `SETFATTR_PROG`, and `XFS_IO_PROG` with `-ftd`/`-d` command sequences.
 It imports `./common/attr`, `./common/preamble`.
 Capability gates include `_require_attrs`, `_require_odirect`, `_require_scratch`, `_require_xfs_io_command`.
 Regression annotations include `_fixed_by_fs_commit btrfs 9d274c19a71b \`.



Control flow, state, dependencies, risks, and test signals: After mkfs/mount it removes `-i` from `XFS_IO_PROG` to make startup faster, obtains the block size, and repeats 5000 falloc/write/xattr/direct-write cycles against one file. State is the scratch file, its prealloc extents, xattrs, ordered extents, and filesystem log state. It depends on xfs_io fallocate/direct write support and user xattrs. Risks are race sensitivity, long loop cost, and filesystem-specific behavior outside Btrfs. The only expected signal is no crash and `Silence is golden`. Source size is 44 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/748 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/749 -->

# sources/test-tools/xfstests/tests/generic/749


Purpose: Validates mmap POSIX partial-page behavior: bytes beyond EOF up to page boundary read as zero, writes there do not change file size/content, and access beyond the mapped page boundary SIGBUSes.


Important APIs, helpers, and commands: Defines `filter_xfs_io_data_unique`, `setup_zeroed_file`, `mwrite`, `do_mmap_tests`, and `test_block_size`; uses `_mread`, `_round_up_to_page_boundary`, `_md5_checksum`, `truncate`, `falloc`, `mmap`, `mread`, and `mwrite` xfs_io commands.
 Local helper functions detected in the file include `do_mmap_tests`, `filter_xfs_io_data_unique`, `mwrite`, `setup_zeroed_file`, `test_block_size`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch_nocheck`, `_require_test`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The test creates sparse or preallocated files, writes data at varied offsets/lengths, remounts to drop cache effects, verifies zero-filled tails, compares checksums and file sizes, and probes valid and invalid read/write ranges. State includes page-cache mappings, file size, checksums, and temp stderr/stdout used to detect `Bus error`. Dependencies are scratch filesystem, xfs_io mmap/truncate/falloc support, bash subprocess SIGBUS handling, and filter helpers. Risks are architecture page-size differences, shell signal text differences, and stale cache effects if cycle mounts fail. Test signals are explicit failure messages or final silence. Source size is 258 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/749 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/750 -->

# sources/test-tools/xfstests/tests/generic/750


Purpose: Runs fsstress while repeatedly triggering kernel memory compaction to expose folio migration and compaction deadlocks or crashes during filesystem write load.


Important APIs, helpers, and commands: Uses `_require_vm_compaction`, `_run_fsstress`, `_kill_fsstress`, `/proc/sys/vm/compact_memory`, and soak controls `LOAD_FACTOR`, `TIME_FACTOR`, `SOAK_DURATION`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_vm_compaction`.
 Regression annotations include `_fixed_by_git_commit kernel d99e3140a4d3 \, _fixed_by_git_commit kernel 2e6506e1c4ee \`.



Control flow, state, dependencies, risks, and test signals: The script formats/mounts scratch, starts a background loop writing `1` to the compaction knob every five seconds while a runfile exists, then runs fsstress with write workload sized by CPU and time factors. State is the scratch tree, background compaction PID, runfile, and kernel VM compaction activity; no durable repo state is kept. Dependencies include writable proc compaction knob and fsstress. Risks include cleanup leaving compaction running, requiring root/proc permissions, and long runtime. Success is fsstress completion without kernel failure. Source size is 61 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/750 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/751 -->

# sources/test-tools/xfstests/tests/generic/751


Purpose: Stresses page-cache truncation, large folio splitting, and writeback by running buffered fio writes while continuously forcing huge-page split operations.


Important APIs, helpers, and commands: Defines `proc_vmstat`; uses `_require_split_huge_pages_knob`, `_split_huge_pages_all`, `_require_fio`, `FIO_PROG`, and vmstat counters `thp_split_page`/`thp_split_page_failed`.
 Local helper functions detected in the file include `_cleanup`, `proc_vmstat`.
 It imports `./common/preamble`.
 Capability gates include `_require_fio`, `_require_scratch`, `_require_split_huge_pages_knob`, `_require_test`.
 Regression annotations include `_fixed_by_git_commit kernel 2a0774c2886d \`.



Control flow, state, dependencies, risks, and test signals: It writes a fio config for many 4MiB buffered writers, mounts scratch, starts a runfile-controlled background split loop, records split counters, runs fio time-based writes, stops the loop, records counter deltas, and tolerates ENOSPC. State includes fio temp files, scratch files, huge-page split counters, and the split-loop PID. Dependencies are fio, THP split controls, buffered IO, and scratch capacity. Risks are intentionally aggressive system-wide split pressure, ENOSPC interpretation, and cleanup of background work. Signals are fio non-ENOSPC failure or kernel/writeback crash. Source size is 167 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/751 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/752 -->

# sources/test-tools/xfstests/tests/generic/752


Purpose: Checks that `exchangerange` refuses to operate on an active swap file.


Important APIs, helpers, and commands: Uses `_require_xfs_io_command exchangerange`, `MKSWAP_PROG`, `swapon`, `swapoff`, `punch-alternating`, and cleanup that turns swap off before deleting temp files.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_test`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The test creates a fragmented 32MiB file, makes it a swap file, creates a donor file, enables swap, and invokes xfs_io `exchangerange` from the swap file to the donor. State is the active swapfile and donor file under `$TEST_DIR`; cleanup must call swapoff. Dependencies are mkswap/swapon privileges and exchangerange support. Risks are leaving swap active on failure and differences in expected errno/output. Test signal is the exchangerange command output and no successful data exchange on swap-backed file. Source size is 44 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/752 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/753 -->

# sources/test-tools/xfstests/tests/generic/753


Purpose: Exercises metadata-journal recovery under repeated simulated disk failures while fsstress emphasizes xattr creation, listing, and removal.


Important APIs, helpers, and commands: Imports `common/dmerror`; uses `_dmerror_init/mount/unmount/load_error_table/load_working_table`, `_run_fsstress_bg`, `_kill_fsstress`, `_require_metadata_journaling`, and soak loop helpers.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmerror`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: After mkfs and dm-error setup, the script builds fsstress weights biased toward xattrs, starts fsstress, randomly sleeps 0-2 seconds, flips the device to error without lockfs quiescing, kills fsstress, remounts through the working table for log replay, and repeats. State includes the dm-error mapping, scratch metadata log, fsstress process, and created xattrs. Dependencies are device-mapper error target and journaling filesystem. Risks include destructive error injection, unmount failures, and xattr workload variance. Success is repeated remount/recovery without check failures. Source size is 85 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/753 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/754 -->

# sources/test-tools/xfstests/tests/generic/754


Purpose: Regression test that adding/removing xattrs on symlinks of many target lengths does not corrupt symlink targets after remount.


Important APIs, helpers, and commands: Uses `_require_symlinks`, `_scratch_cycle_mount`, `attr -Rs/-Rr`, `readlink`, and XFS-specific `_fixed_by_git_commit` annotations.
 It imports `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_symlinks`.
 Regression annotations include `_fixed_by_git_commit kernel 38de567906d95 \, _fixed_by_git_commit xfsprogs XXXXXXXXXXXXX \`.



Control flow, state, dependencies, risks, and test signals: It creates symlinks with targets growing from 32 to under 1024 bytes, sets and removes three root namespace attrs on each symlink, cycles the mount, then reconstructs expected targets and compares readlink output. State is symlink inode data and any remote/inline target representation on scratch. Dependencies are symlink and attr support. Risks are attr tool availability/permissions and silent attr failures being redirected. Signal is any `target is corrupt` message; otherwise silence. Source size is 61 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/754 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/755 -->

# sources/test-tools/xfstests/tests/generic/755


Purpose: Verifies that unlinking one hardlink updates the target inode ctime.


Important APIs, helpers, and commands: Uses `_require_hardlinks`, `stat -c %Z`, `ln`, `unlink`, and a two-second sleep to cross timestamp granularity.
 It imports `./common/preamble`.
 Capability gates include `_require_hardlinks`, `_require_test`.
 Regression annotations include `_fixed_by_fs_commit btrfs 3bc2ac2f8f0b \`.



Control flow, state, dependencies, risks, and test signals: The test creates a file and hardlink in `$TEST_DIR`, records ctime, sleeps, unlinks one name, records ctime through the remaining name, and reports if it did not change. State is link count and ctime in the test filesystem. Dependencies are hardlinks and second-resolution timestamp visibility. Risks are coarse or frozen timestamps and clock behavior. Success signal is only `Silence is golden`. Source size is 40 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/755 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/756 -->

# sources/test-tools/xfstests/tests/generic/756


Purpose: Checks exportfs file handles for linked and unlinked files while verifying unique 64-bit mount IDs through statx/open_by_handle.


Important APIs, helpers, and commands: Defines `create_test_files` and `test_file_handles`; requires `open_by_handle`, exportfs, `STATX_MNT_ID_UNIQUE`, and `AT_HANDLE_MNT_ID_UNIQUE` support.
 Local helper functions detected in the file include `create_test_files`, `test_file_handles`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_exportfs`, `_require_open_by_handle_unique_mountid`, `_require_statx_unique_mountid`, `_require_test`, `_require_test_program`.



Control flow, state, dependencies, risks, and test signals: The script creates 1024 handle-test files, runs the helper with stale-after-delete mode, then with normal linked files, then with hardlink/original-delete and unlink modes. State is generated file handles, hardlink topology, mount IDs, and the test directory. Dependencies are the xfstests `open_by_handle` helper and filesystem export support. Risks are privilege requirements and filesystems with unstable handles. Signals are helper output filtered through `_filter_test_dir` and any stale/non-stale mismatch. Source size is 65 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/756 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/757 -->

# sources/test-tools/xfstests/tests/generic/757


Purpose: Uses log-writes plus thin provisioning to replay every FUA point from an async direct-I/O fdatasync workload, targeting Btrfs checksum/log-tree recovery bugs.


Important APIs, helpers, and commands: Imports `dmthin` and `dmlogwrites`; uses fio `libaio` direct random writes with `fdatasync=1`, `_log_writes_*`, `_dmthin_*`, and `_soak_loop_running`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmlogwrites`, `./common/dmthin`, `./common/preamble`.
 Capability gates include `_require_aiodio`, `_require_dm_target`, `_require_fio`, `_require_log_writes`, `_require_scratch_nocheck`.
 Regression annotations include `_fixed_by_fs_commit btrfs e917ff56c8e7 \`.



Control flow, state, dependencies, risks, and test signals: The test configures a thin device under log-writes, mkfs/mounts it, runs fio against a 1GiB file, removes log-writes, finds FUA entries after mkfs, replays ranges to the thin volume, mounts/checks as needed, and advances through FUA points. State includes the log-writes journal, thin volume, replay cursor, and filesystem recovery state. Dependencies are dm-thin, log-writes, fio async DIO, and filesystem check helpers. Risks are replay slowness, missing FUA markers, and XFS dirty-log handling. Success is all replay checkpoints passing filesystem checks. Source size is 94 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/757 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/758 -->

# sources/test-tools/xfstests/tests/generic/758


Purpose: Checks that mmap writes after `fzero` over a range spanning pages preserve the intended data before and after remount.


Important APIs, helpers, and commands: Uses xfs_io `pwrite`, `mmap`, `mwrite`, `fzero`, `_hexdump`, `_get_page_size`, `_scratch_cycle_mount`, and `_filter_xfs_io`.
 Local helper functions detected in the file include `_dump_files`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: It builds a verify file with baseline bytes and overwritten range, builds the test file through mmap write, zero-range, and mmap rewrite, compares the two files before remount, cycles mount, and compares again. State is file content, zeroed extents, page cache mappings, and post-remount disk state. Dependencies are scratch and xfs_io fzero/mmap support. Risks center on page-size/filesystem-block-size interactions and mmap cache coherency. Signals are cmp mismatches plus hexdumps. Source size is 68 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/758 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/759 -->

# sources/test-tools/xfstests/tests/generic/759


Purpose: Runs fsx with userspace buffers backed by transparent huge pages to stress buffered read/write paths.


Important APIs, helpers, and commands: Uses `_require_thp`, `_require_hugepage_fsx`, and `_run_hugepage_fsx` with varied operation offsets.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_hugepage_fsx`, `_require_test`, `_require_thp`.



Control flow, state, dependencies, risks, and test signals: The control flow is three fsx runs of 10000 operations and 500000-byte maximum length, with offsets 0, 8192, and 128000. State is fsx-generated test files in the test area and THP-backed user buffers. Dependencies are THP and the hugepage fsx helper. Risks are nondeterminism and THP allocation availability. Success is fsx completing without data model mismatch. Source size is 23 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/759 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/760 -->

# sources/test-tools/xfstests/tests/generic/760


Purpose: Runs direct-I/O fsx using hugepage-backed buffers, aligning read/truncate/write sizes to page and device DIO limits.


Important APIs, helpers, and commands: Uses `_require_odirect`, `_require_thp`, `_require_hugepage_fsx`, `feature -s`, `min_dio_alignment`, and `_run_hugepage_fsx` with `-Z -R -W` direct options.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_hugepage_fsx`, `_require_odirect`, `_require_test`, `_require_thp`.



Control flow, state, dependencies, risks, and test signals: It computes system page size and DIO block size, then performs three direct hugepage fsx runs at different offsets. State is direct I/O test files and helper model state. Dependencies are O_DIRECT, THP, and correct min alignment. Risks are alignment mismatch and devices with strict DIO constraints. Success is no fsx corruption or I/O failure. Source size is 27 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/760 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/761 -->

# sources/test-tools/xfstests/tests/generic/761


Purpose: Verifies that direct writes cannot race mutable user buffers into bad data checksums; checksum filesystems should fall back to buffered writes when required.


Important APIs, helpers, and commands: Requires `dio-writeback-race`, scratch, and O_DIRECT; uses `_get_file_block_size` and a 64MiB target file.
 It imports `./common/preamble`.
 Capability gates include `_require_odirect`, `_require_scratch`, `_require_test_program`.
 Regression annotations include `_fixed_by_fs_commit btrfs 968f19c5b1b7 \`.



Control flow, state, dependencies, risks, and test signals: The test mkfs/mounts scratch, records block size and file size, runs the helper to mutate a direct-I/O buffer during writeback, then reads the file to force checksum verification. State is file data and filesystem checksum metadata. Dependencies are the compiled helper and checksum-capable behavior on affected filesystems. Risks are helper timing sensitivity and filesystems without data checksums simply not exercising the bug. Signal is helper or read failure; otherwise silence. Source size is 42 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/761 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/762 -->

# sources/test-tools/xfstests/tests/generic/762


Purpose: Validates statfs/statvfs reporting when project quota limits apply to a directory tree and whole-filesystem free space changes.


Important APIs, helpers, and commands: Uses `common/quota`, `_scratch_enable_pquota`, `_qmount_option prjquota`, `_force_vfs_quota_testing`, xfs_io `statfs`/`chproj`, `setquota`, `fallocate`, and `_within_tolerance`.
 Local helper functions detected in the file include `bavail`, `blocks`, `bsize`.
 It imports `./common/filter`, `./common/preamble`, `./common/quota`.
 Capability gates include `_require_prjquota`, `_require_quota`, `_require_scratch`, `_require_xfs_io_command`.
 Regression annotations include `_fixed_by_fs_commit xfs 4b8d867ca6e2 \`.



Control flow, state, dependencies, risks, and test signals: It mounts with project quotas, captures root statfs, assigns project 55 to a directory with a limit of half available blocks, checks root vs directory blocks/bavail, consumes most global free space, writes 10 blocks inside the project, and checks statfs after each stage. State is project quota accounting, file allocations, and statfs values. Dependencies are quota tooling and project quota support. Risks are tolerance mismatches due to metadata overhead and quota activation failures. Signals are `_within_tolerance` failures and diagnostic quota/df output. Source size is 114 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/762 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/763 -->

# sources/test-tools/xfstests/tests/generic/763


Purpose: Confirms that a zero-byte write succeeds on a regular file, guarding against exfat returning EFAULT.


Important APIs, helpers, and commands: Uses xfs_io `pwrite 0 0`, `_filter_xfs_io`, and `_require_test`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_test`.
 Regression annotations include `_fixed_by_fs_commit exfat dda0407a2026 \`.



Control flow, state, dependencies, risks, and test signals: The test writes zero bytes to a new file under `$TEST_DIR` and filters the result. State is minimal: the test file may be created but no data should be written. Dependencies are xfs_io and normal write support. Risks are command output differences. Success is normal pwrite output with no error. Source size is 29 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/763 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/764 -->

# sources/test-tools/xfstests/tests/generic/764


Purpose: Crash-consistency test that fsyncing an unlinked-but-open file persists deletion after simulated power failure.


Important APIs, helpers, and commands: Imports `dmflakey`; uses `_init_flakey`, `_flakey_drop_and_remount`, `multi_open_unlink -F -S`, and `_require_metadata_journaling`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`, `_require_test_program`.
 Regression annotations include `_fixed_by_fs_commit btrfs 5e85262e542d \`.



Control flow, state, dependencies, risks, and test signals: It creates a directory, runs a helper that opens, unlinks, fsyncs, and closes a file with no hardlinks, drops/remounts through dm-flakey, and lists the directory expecting it empty. State is log/journal state for an orphaned inode and the dm-flakey mapping. Dependencies are flakey target, journaling, scratch, and helper binary. Risks are destructive crash simulation and helper semantics. Signal is any remaining directory entry or remount failure. Source size is 50 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/764 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/765 -->

# sources/test-tools/xfstests/tests/generic/765


Purpose: Broad atomic write support validator across filesystem block sizes, testing filesystem/device limits and data integrity for supported configurations.


Important APIs, helpers, and commands: Imports `common/atomicwrites`; defines `get_supported_bsize`, `get_mkfs_opts`, and `test_atomic_writes`; uses `_require_scratch_write_atomic`, `_require_atomic_write_test_commands`, atomic write unit sysfs/statx helpers, and `_test_atomic_file_writes`.
 Local helper functions detected in the file include `get_mkfs_opts`, `get_supported_bsize`, `test_atomic_writes`.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_atomic_write_test_commands`, `_require_scratch_write_atomic`.



Control flow, state, dependencies, risks, and test signals: The script determines min/max filesystem block sizes for XFS or ext4, formats scratch at candidate block sizes, mounts, obtains atomic write unit min/max and segment limits, and runs atomic file write helper coverage. State includes scratch format options, atomic-write capability values, and generated test files. Dependencies are kernel atomic write support, block device capability, xfs/ext4 mkfs options, and helper programs. Risks are filesystem-specific skip logic, device queue capability interpretation, and incomplete coverage if mount probes fail. Signals are helper failures or unsupported skips. Source size is 130 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/765 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/766 -->

# sources/test-tools/xfstests/tests/generic/766


Purpose: Tests readonly norecovery behavior with an external log device after filesystem shutdown, ensuring mounts with and without the external logdev fail/succeed as expected.


Important APIs, helpers, and commands: Uses `_require_logdev`, `_require_norecovery`, `_require_scratch_shutdown`, `_try_scratch_mount`, `_filter_ro_mount`, `_filter_ending_dot`, and scratch shutdown/unmount helpers.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_local_device`, `_require_logdev`, `_require_metadata_journaling`, `_require_norecovery`, `_require_scratch_nocheck`, `_require_scratch_shutdown`.
 Regression annotations include `_fixed_by_fs_commit ext4 273108fa5015 \, _fixed_by_fs_commit xfs bfecc4091e07 \`.



Control flow, state, dependencies, risks, and test signals: The test formats scratch with log device, mounts, shuts the filesystem down, unmounts, then attempts readonly/norecovery mount variants using the proper and improper device configuration. State is the external log metadata and shutdown log state. Dependencies are local block devices, metadata journaling, and logdev support. Risks are mount option output variance and destructive shutdown. Signals are filtered mount success/failure lines matching expected behavior. Source size is 136 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/766 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/767 -->

# sources/test-tools/xfstests/tests/generic/767


Purpose: Validates atomic write reporting and simple atomic writes on a scsi_debug device wired in as scratch storage.


Important APIs, helpers, and commands: Uses `_require_scsi_debug`, `_get_scsi_debug_dev`, `_put_scsi_debug_dev`, `_require_scratch_write_atomic`, `_simple_atomic_write`, `_test_atomic_file_writes`, and statx atomic fields.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/atomicwrites`, `./common/preamble`, `./common/scsi_debug`.
 Capability gates include `_require_block_device`, `_require_scratch`, `_require_scratch_write_atomic`, `_require_scsi_debug`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The flow provisions a scsi_debug block device with atomic write capability, assigns it to scratch, mkfs/mounts, checks min/opt/max atomic units, performs simple atomic writes at multiple sizes, and tears the device down in cleanup. State is external scratch block device identity and scratch contents. Dependencies are scsi_debug module access, block-device scratch, xfs/ext4 support, and atomic write helpers. Risks include module cleanup leaks and device capability mismatch. Signals are statx/capability mismatches or write verification failures. Source size is 104 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/767 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/768 -->

# sources/test-tools/xfstests/tests/generic/768


Purpose: Exercises multi-filesystem-block atomic writes on a normal scratch block device.


Important APIs, helpers, and commands: Uses `_require_scratch_write_atomic_multi_fsblock`, `_simple_atomic_write`, `_test_atomic_file_writes`, xfs_io, and atomic write unit helpers.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_atomic_write_test_commands`, `_require_block_device`, `_require_scratch`, `_require_scratch_write_atomic_multi_fsblock`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: It formats and mounts scratch, discovers atomic write unit min/max, runs simple atomic writes at boundary sizes, then invokes the common atomic write file tests. State is the scratch file data and atomic write capability metadata. Dependencies are block-device scratch with multi-fsblock atomic writes. Risks are device capability drift and filesystem block-size interactions. Success is silent helper completion. Source size is 68 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/768 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/769 -->

# sources/test-tools/xfstests/tests/generic/769


Purpose: Combines reflinked extents with multi-fsblock atomic writes to ensure atomic write restrictions and data integrity survive shared extent layouts.


Important APIs, helpers, and commands: Uses `_require_cp_reflink`, `_require_scratch_reflink`, `_require_scratch_write_atomic_multi_fsblock`, `_weave_reflink_rainbow`, and atomic write helpers.
 It imports `./common/atomicwrites`, `./common/filter`, `./common/preamble`, `./common/reflink`.
 Capability gates include `_require_atomic_write_test_commands`, `_require_block_device`, `_require_cp_reflink`, `_require_scratch`, `_require_scratch_reflink`, `_require_scratch_write_atomic_multi_fsblock`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The test sizes scratch, mounts with reflink support, creates a woven reflink pattern, performs atomic writes across selected ranges, and filters scratch paths. State is shared extent topology and post-write file data. Dependencies are reflink plus atomic write support on the same filesystem. Risks are copy-on-write interactions, insufficient space, and feature combinations that are rare. Signals are helper verification errors or unexpected output. Source size is 88 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/769 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/770 -->

# sources/test-tools/xfstests/tests/generic/770


Purpose: Exercises atomic writes across a deliberately fragmented file layout without reflink, stressing allocation boundaries and free-space constraints.


Important APIs, helpers, and commands: Uses `_weave_file_rainbow`, `_get_available_space`, `_require_scratch_write_atomic_multi_fsblock`, and atomic write helpers.
 It imports `./common/atomicwrites`, `./common/filter`, `./common/preamble`, `./common/reflink`.
 Capability gates include `_require_atomic_write_test_commands`, `_require_block_device`, `_require_scratch`, `_require_scratch_write_atomic_multi_fsblock`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The flow mkfs-sizes scratch, computes atomic unit and block size values, builds a woven file extent pattern, then performs atomic writes over those ranges. State is fragmented extent mapping and written data. Dependencies are scratch block device and atomic write support. Risks are available-space calculations, allocator differences, and atomic unit alignment. Test signals are helper data-integrity failures. Source size is 129 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/770 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/771 -->

# sources/test-tools/xfstests/tests/generic/771


Purpose: Crash-consistency regression around flakey remount after operations captured by xfs_io output, targeting metadata journaling behavior.


Important APIs, helpers, and commands: Uses `common/dmflakey`, `_init_flakey`, `_flakey_drop_and_remount`, `_filter_xfs_io`, and metadata journaling requirements.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`, `_require_test_program`.
 Regression annotations include `_fixed_by_fs_commit btrfs 0a32e4f0025a \`.



Control flow, state, dependencies, risks, and test signals: The script formats scratch, sets up flakey, performs file operations that are then crash-tested via drop/remount, and validates expected post-replay state through filtered xfs_io output. State lives in the journal/log and scratch files. Dependencies are flakey device-mapper target, scratch, and helper programs. Risks are crash timing and filesystem-specific replay semantics. Signals are filtered mismatches or remount/check failure. Source size is 60 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/771 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/772 -->

# sources/test-tools/xfstests/tests/generic/772


Purpose: Tests VFS file attribute get/set behavior for FS_XFLAG_NODUMP on directories, special files, sockets, and symlinks including broken symlink no-follow handling.


Important APIs, helpers, and commands: Uses `file_getattr`, `file_setattr`, `file_attr`, `_filter_vfs_file_attributes`, `_require_file_attr`, `_require_mknod`, and symlink support.
 Local helper functions detected in the file include `file_attr`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_file_attr`, `_require_mknod`, `_require_scratch`, `_require_symlinks`, `_require_test_program`.



Control flow, state, dependencies, risks, and test signals: It creates a project directory with fifo, char/block devices, socket, symlink, and broken symlink, reads initial attributes, sets nodump on each, reads back filtered attributes, then compares follow vs no-follow behavior for broken symlinks. State is inode flag metadata on heterogeneous file types. Dependencies are file attribute test helper, mknod, socket creation, and symlink support. Risks are privilege requirements for device nodes and filesystem flag support differences. Signals are normalized attribute output. Source size is 75 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/772 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/773 -->

# sources/test-tools/xfstests/tests/generic/773


Purpose: fio-based atomic write verification for single-fsblock-capable filesystems using incremental, min/max, and verify jobs.


Important APIs, helpers, and commands: Defines `create_fio_aw_config`, `create_fio_verify_config`, and `create_fio_configs`; uses `_require_fio_atomic_writes`, `_require_aio`, O_DIRECT, xfs_io, and atomic unit helpers.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_aio`, `_require_fio`, `_require_fio_atomic_writes`, `_require_odirect`, `_require_scratch_write_atomic`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The test creates fio configs for atomic write workloads and verify passes, records min/max units, formats/mounts scratch, runs direct atomic write sequences, and verifies the written pattern. State includes fio state files/configs and scratch data. Dependencies are fio atomic write support and filesystem atomic write capability. Risks are fio version differences, direct-I/O alignment, and runtime scaling. Signals are fio or verify failures. Source size is 108 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/773 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/774 -->

# sources/test-tools/xfstests/tests/generic/774


Purpose: fio atomic write stress for multi-fsblock atomic writes with unwritten/written block transitions and verification.


Important APIs, helpers, and commands: Uses fio config generation for write and verify jobs, `_require_scratch_write_atomic_multi_fsblock`, `_get_block_size`, `_require_fio_atomic_writes`, and xfs_io preparation.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_aio`, `_require_fio`, `_require_fio_atomic_writes`, `_require_odirect`, `_require_scratch_write_atomic_multi_fsblock`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The flow computes block and atomic unit sizes, prepares file regions with unwritten and written blocks, runs fio atomic write jobs at several sizes/increments, and verifies content. State is file extent state, fio configs, and verification output. Dependencies are fio AIO/direct atomic writes and multi-fsblock filesystem support. Risks are alignment, unwritten extent conversion bugs, and fio semantics. Signals are verify mismatches or fio errors. Source size is 128 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/774 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/775 -->

# sources/test-tools/xfstests/tests/generic/775


Purpose: Checks atomic-write crash consistency across mixed mappings by issuing atomic writes with sync modes, forcing shutdown/remount, and verifying no torn data.


Important APIs, helpers, and commands: Defines `prep_mixed_mapping`, `verify_atomic_write`, `check_data_integrity`, and `mixed_mapping_test`; uses `_require_scratch_shutdown`, atomic write commands, and hexdump verification.
 Local helper functions detected in the file include `check_data_integrity`, `mixed_mapping_test`, `prep_mixed_mapping`, `verify_atomic_write`.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_atomic_write_test_commands`, `_require_scratch_shutdown`, `_require_scratch_write_atomic_multi_fsblock`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: It prepares files with written, unwritten, hole, and mixed mappings, performs atomic writes with different sync flags, cycles through filesystem shutdown/remount, and validates that old or new complete data appears but not mixed torn bytes. State is file extent layout, expected data pattern, and shutdown journal state. Dependencies are atomic writes, scratch shutdown support, and xfs_io. Risks are destructive shutdown and exact data-pattern assumptions. Signals are hexdump/data integrity failures. Source size is 139 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/775 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/776 -->

# sources/test-tools/xfstests/tests/generic/776


Purpose: Runs fsx with atomic-write avoidance settings on filesystems/devices advertising atomic writes.


Important APIs, helpers, and commands: Defines `set_fsx_avoid`; uses `_run_fsx_on_file`, `_require_scratch_write_atomic`, `_require_odirect`, atomic write unit helpers, and FSX_AVOID flags.
 Local helper functions detected in the file include `set_fsx_avoid`.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_odirect`, `_require_scratch_write_atomic`.



Control flow, state, dependencies, risks, and test signals: The test mounts scratch, derives block and atomic max values, sets fsx avoid flags appropriate to the filesystem, then runs fsx against a scratch file. State is fsx model/data file and atomic write capability values. Dependencies are fsx, O_DIRECT, and scratch atomic support. Risks are filesystem-specific avoid flags and test coverage being too conservative. Success is fsx model consistency. Source size is 68 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/776 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/777 -->

# sources/test-tools/xfstests/tests/generic/777


Purpose: Basic exportfs/open-by-handle test for linked and unlinked files, without the unique mount ID requirements of generic/756.


Important APIs, helpers, and commands: Defines `create_test_files` and `test_file_handles`; uses `_require_open_by_handle`, `_test_cycle_mount`, and the `open_by_handle` helper.
 Local helper functions detected in the file include `create_test_files`, `test_file_handles`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_open_by_handle`, `_require_test`.



Control flow, state, dependencies, risks, and test signals: It creates handle-test files in `$TEST_DIR`, runs decode checks, cycles the test mount, and exercises stale/non-stale handle behavior across deletion/linking scenarios. State is generated handles and test files. Dependencies are open_by_handle support and exportable filesystem behavior. Risks are privilege requirements and filesystem handle instability. Signals are helper output and stale-handle failures. Source size is 70 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/777 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/778 -->

# sources/test-tools/xfstests/tests/generic/778


Purpose: Comprehensive atomic-write torn-write detector that races repeated atomic writes with forced shutdowns across written, unwritten, hole, mixed, and append cases.


Important APIs, helpers, and commands: Defines many helpers including `atomic_write_loop`, `start_atomic_write_and_shutdown`, `test_torn_write*`, `test_append_torn_write`, `populate_expected_data`, and `verify_data_blocks`; uses `_soak_loop_running`, scratch shutdown, xfs_io, and atomic write helpers.
 Local helper functions detected in the file include `_cleanup`, `atomic_write_loop`, `create_mixed_mappings`, `dry_run`, `kill_awloop`, `populate_expected_data`, `start_atomic_write_and_shutdown`, `test_append_torn_write`, `test_torn_write`, `test_torn_write_hole`, `test_torn_write_mixed`, `test_torn_write_unwritten`.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_atomic_write_test_commands`, `_require_scratch_shutdown`, `_require_scratch_write_atomic_multi_fsblock`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: It dry-runs expected layouts, starts background atomic write loops, shuts the filesystem down at controlled points, remounts/cycles, and checks every block against old/new/zero expected data. State includes run/kill files, background writer PID, expected data arrays, and crash-recovered scratch contents. Dependencies are multi-fsblock atomic writes and shutdown support. Risks are timing sensitivity, long runtime, and cleanup of background loops. Signals are explicit torn-write data mismatch reports. Source size is 413 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/778 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/779 -->

# sources/test-tools/xfstests/tests/generic/779


Purpose: Crash-consistency test for symlink inode-copy logging across dm-flakey power failure.


Important APIs, helpers, and commands: Uses `dmflakey`, `_require_symlinks`, `_flakey_drop_and_remount`, `_INODE_COPY_EVERYTHING`-related regression annotation, and scratch journaling.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`, `_require_symlinks`.
 Regression annotations include `_fixed_by_fs_commit btrfs 953902e4fb4c \`.



Control flow, state, dependencies, risks, and test signals: The test creates symlink-related metadata, forces relevant inode changes, drops/remounts through flakey, and verifies expected symlink/directory state. State is symlink inode metadata and filesystem log. Dependencies are symlinks, metadata journaling, and flakey target. Risks are filesystem-specific log replay and limited visible output. Signals are missing/corrupt symlink state or remount failure. Source size is 60 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/779 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/780 -->

# sources/test-tools/xfstests/tests/generic/780


Purpose: Extends file attribute nodump testing to special files and symlinks, including no-follow behavior.


Important APIs, helpers, and commands: Uses `file_attr`, `_require_file_attr_special`, `_require_mknod`, `_filter_vfs_file_attributes`, AF_UNIX socket helper, and symlink support.
 Local helper functions detected in the file include `create_af_unix`, `file_attr`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_file_attr`, `_require_file_attr_special`, `_require_mknod`, `_require_scratch`, `_require_symlinks`, `_require_test_program`.



Control flow, state, dependencies, risks, and test signals: It creates a directory with fifo, char/block device, socket, symlink, and broken symlink, reads attributes, sets nodump across all, and verifies follow/no-follow semantics. State is VFS inode flags on special inode types. Dependencies are helper binaries, mknod permissions, and filesystem file-attribute support. Risks are special-file creation permissions and filesystems that reject flags on some inode types. Signals are normalized attribute listings. Source size is 86 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/780 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/781 -->

# sources/test-tools/xfstests/tests/generic/781


Purpose: Smoke-tests zoned block device support by creating a zloop device inside scratch and running fsx on a filesystem built on that zloop device.


Important APIs, helpers, and commands: Imports `common/zoned`; uses `_create_zloop`, `_destroy_zloop`, `_try_mkfs_dev`, `_mount`, `_unmount`, and `FSX_PROG`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/preamble`, `./common/zoned`.
 Capability gates include `_require_block_device`, `_require_scratch_size`, `_require_zloop`.



Control flow, state, dependencies, risks, and test signals: The script creates and mounts scratch, creates zloop backing storage under scratch, mkfs/mounts the zoned device, runs fsx, and cleans up mounts/devices. State is nested filesystem content and zloop device. Dependencies are zloop support, scratch block device, and fsx. Risks are nested mount cleanup and zloop availability. Success is fsx completion and `Silence is golden`. Source size is 44 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/781 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/782 -->

# sources/test-tools/xfstests/tests/generic/782


Purpose: Btrfs-oriented log replay test ensuring fsync of root directory persists a newly created directory after linking an fsynced file into it.


Important APIs, helpers, and commands: Uses `dmflakey`, xfs_io `pwrite`/`fsync`, `_hexdump`, `_scratch_sync`, and `_flakey_drop_and_remount`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`.
 Regression annotations include `_fixed_by_fs_commit btrfs bfe3d755ef7c \`.



Control flow, state, dependencies, risks, and test signals: It creates and syncs a file, creates a directory, writes/fsyncs the file, hardlinks it into the new directory, fsyncs root, simulates power failure, and verifies root content and file data. State is directory entries, hardlink metadata, file data, and log replay state. Dependencies are journaling and flakey target. Risks are crash simulation and filesystem-specific lost+found filtering. Signals are root listing and hexdump after replay. Source size is 73 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/782 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/783 -->

# sources/test-tools/xfstests/tests/generic/783


Purpose: Tests overlayfs mount and lookup error cases when underlying layers are casefold-capable or casefold-enabled with matching, strict, or inconsistent encodings.


Important APIs, helpers, and commands: Imports `common/casefold`; defines `mount_casefold_version`, `mount_overlay`, and `unmount_overlay`; uses `_scratch_mkfs_casefold*`, `_casefold_set_attr`, `_casefold_unset_attr`, tmpfs `casefold=` mounts, and overlay mount options.
 Local helper functions detected in the file include `_cleanup`, `mount_casefold_version`, `mount_overlay`, `unmount_overlay`.
 It imports `./common/casefold`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_extra_fs`, `_require_scratch_casefold`.



Control flow, state, dependencies, risks, and test signals: The test creates casefold-capable scratch layers, probes whether overlay supports enabled layers, then exercises disabled/enabled transitions before/after mount, lower subdir mismatches, upper/work enabled failures, strict encoding cases, and mismatched UTF-8 versions. State is casefold directory attributes, overlay mount state, and temp mountpoints. Dependencies are overlayfs, casefold filesystem support, tmpfs casefold versions, and extra overlay fs availability. Risks are kernel-version-dependent expected skips and mount error wording. Signals are filtered ls/mount failures for ESTALE/EREMOTE/EINVAL scenarios. Source size is 242 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/783 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/784 -->

# sources/test-tools/xfstests/tests/generic/784


Purpose: Log replay test for conflict between a moved directory and a new file created at the old path, followed by file rename and fsync.


Important APIs, helpers, and commands: Defines `list_fs_contents`; uses dmflakey, xfs_io fsync, `_scratch_sync`, and recursive filtered listing.
 Local helper functions detected in the file include `_cleanup`, `list_fs_contents`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`.
 Regression annotations include `_fixed_by_fs_commit btrfs 266273eaf4d9 \`.



Control flow, state, dependencies, risks, and test signals: It creates two dirs, syncs, moves dir1 into dir2, creates a file at the old dir1 path and fsyncs it, moves that file to dir2/foo, fsyncs again, records contents, crashes/remounts, and compares contents by output. State is conflicting inode/name history and log replay metadata. Dependencies are metadata journaling and flakey. Risks are path conflict replay bugs and output normalization. Signals are before/after filesystem listings. Source size is 76 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/784 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/785 -->

# sources/test-tools/xfstests/tests/generic/785


Purpose: Log replay test ensuring fsyncing a parent directory after renaming an fsynced file also persists a newly created sibling directory and its entry.


Important APIs, helpers, and commands: Uses `dmflakey`, `fssum`, xfs_io pwrite/fsync, and `_scratch_sync`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_fssum`, `_require_metadata_journaling`, `_require_scratch`.
 Regression annotations include `_fixed_by_fs_commit btrfs 5630f7557de6 \`.



Control flow, state, dependencies, risks, and test signals: The script creates file1, syncs, writes/fsyncs it, creates dir/foo, renames file1 to file2, fsyncs root, records an fssum digest, simulates power failure, and validates the digest. State is file data, directory entries, and filesystem log. Dependencies are fssum, journaling, and flakey target. Risks are fssum availability and filesystem-specific metadata ordering. Signal is fssum verification success. Source size is 73 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/785 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/786 -->

# sources/test-tools/xfstests/tests/generic/786


Purpose: Thin wrapper test for directory delegation support through the locktest common helpers.


Important APIs, helpers, and commands: Imports `common/locktest`; requires `_require_test_fcntl_setdeleg` and calls `_run_dirdelegtest`.
 It imports `./common/filter`, `./common/locktest`, `./common/preamble`.
 Capability gates include `_require_test`, `_require_test_fcntl_setdeleg`.



Control flow, state, dependencies, risks, and test signals: The control flow is capability gate then helper execution. State is whatever delegation locks the helper establishes in the test filesystem. Dependencies are fcntl delegation support and compiled locktest helpers. Risks are kernel/filesystem support gaps and helper-specific output. Success is helper exit 0. Source size is 19 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/786 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/787 -->

# sources/test-tools/xfstests/tests/generic/787


Purpose: Thin wrapper test for file delegation support through locktest helpers.


Important APIs, helpers, and commands: Imports `common/locktest`; requires `_require_test_fcntl_setdeleg` and calls `_run_filedelegtest`.
 It imports `./common/filter`, `./common/locktest`, `./common/preamble`.
 Capability gates include `_require_test`, `_require_test_fcntl_setdeleg`.



Control flow, state, dependencies, risks, and test signals: The script delegates all behavior to the file delegation helper after checking support. State is file delegation/lease state in the kernel. Dependencies are fcntl delegation support. Risks are support being experimental and helper output changes. Signal is helper success. Source size is 20 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/787 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/788 -->

# sources/test-tools/xfstests/tests/generic/788


Purpose: Verifies that truncate(2) is blocked on fsverity-enabled files.


Important APIs, helpers, and commands: Imports `common/verity`; uses `_disable_fsverity_signatures`, `_scratch_mkfs_verity`, `_fsv_create_enable_file`, `_fsv_scratch_begin_subtest`, and the `truncate` helper.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`, `./common/verity`.
 Capability gates include `_require_scratch_verity`, `_require_test_program`.



Control flow, state, dependencies, risks, and test signals: It disables signature enforcement for the test, creates a verity-capable scratch filesystem, enables fsverity on a file, then invokes the compiled truncate helper expecting failure. State is fsverity metadata and signature policy restored by cleanup. Dependencies are fsverity scratch support and helper binary. Risks are cleanup of signature policy and filesystems without verity. Signal is the helper’s expected failure output under the subtest. Source size is 38 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/788 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/789 -->

# sources/test-tools/xfstests/tests/generic/789


Purpose: Log replay test that truncating a file to zero, fsyncing it, hardlinking it, and fsyncing the directory persists zero size and link after crash.


Important APIs, helpers, and commands: Uses dmflakey, xfs_io pwrite/truncate/fsync, stat size/link count checks, and `_flakey_drop_and_remount`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`.
 Regression annotations include `_fixed_by_fs_commit btrfs 5254d4181add \`.



Control flow, state, dependencies, risks, and test signals: It writes and syncs a file, truncates/fsyncs it to zero, creates a sibling hardlink, fsyncs the directory, drops/remounts, and prints file size/link count plus missing-link diagnostics. State is file size, nlink, directory entry, and log replay. Dependencies are journaling and flakey target. Risks are crash simulation and filesystem-specific log replay. Signals are size 0, link count 2, and existing `dir/bar`. Source size is 59 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/789 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/790 -->

# sources/test-tools/xfstests/tests/generic/790


Purpose: Log replay test for replacing a persisted directory with a file of the same name while adding directories and hardlinks before parent fsync.


Important APIs, helpers, and commands: Uses dmflakey, xfs_io directory fsync, recursive ls filtering, and `_scratch_sync`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`.
 Regression annotations include `_fixed_by_fs_commit btrfs 9573a365ff9f \`.



Control flow, state, dependencies, risks, and test signals: The test persists `foo` as a directory, removes it, creates dir1/dir2, creates file `foo`, hardlinks it into dir2, fsyncs dir2 and root, crashes/remounts, and lists expected contents. State is name-type conflict history, hardlink metadata, and log. Dependencies are journaling and flakey. Risks are replay ordering around conflicting inodes. Signals are post-crash listing containing dir1, dir2/link, and file foo. Source size is 70 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/790 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/791 -->

# sources/test-tools/xfstests/tests/generic/791


Purpose: Checks fsnotify/fanotify delivery of file I/O errors by injecting a dm-error range into a file extent and reading/writing through buffered and direct I/O.


Important APIs, helpers, and commands: Imports `common/dmerror`, `common/systemd`, and filters; defines `filter_fsnotify_errors`; uses `fs-monitor`, xfs_io `fiemap`, `min_dio_alignment`, `_dmerror_mark_range_bad/good`, and `_require_fanotify_ioerrors`.
 Local helper functions detected in the file include `_cleanup`, `filter_fsnotify_errors`.
 It imports `./common/dmerror`, `./common/filter`, `./common/fuzzy`, `./common/preamble`, `./common/systemd`.
 Capability gates include `_require_dm_target`, `_require_fanotify_ioerrors`, `_require_odirect`, `_require_scratch`, `_require_test_program`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: It formats/mounts scratch, ensures XFS non-zoned when needed, writes a 4-block file, parses its physical extent, aligns a bad sector to device LBA, starts fs-monitor, marks that range bad, runs buffered/direct read and write probes, marks it good, kills monitor and reports errors, then remounts/restarts monitor to confirm errors do not persist. State is dm-error map, fsnotify event stream, victim file extent, and temp monitor logs. Dependencies are fanotify FS error support, dm-error, direct I/O, and fiemap. Risks are extent parsing, LBA alignment, and coalesced event semantics. Signals are normalized FAN_FS_ERROR records only during the bad-device phase. Source size is 213 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/791 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/792 -->

# sources/test-tools/xfstests/tests/generic/792


Purpose: Log replay test for fsyncing a directory file descriptor after rmdir of an empty directory, ensuring deletion persists after crash.


Important APIs, helpers, and commands: Uses dmflakey, xfs_io fsync, helper `unlink-fsync`, chmod/mv setup, and recursive listing filters.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`, `_require_test_program`.
 Regression annotations include `_fixed_by_fs_commit btrfs xxxxxxxxxxxx \`.



Control flow, state, dependencies, risks, and test signals: It creates dir1/dir2 and dir3, syncs, chmod/fsyncs dir1, moves dir2 into dir3, runs helper to open dir1, rmdir it, fsync the open fd, then crashes/remounts and lists contents. State is removed directory log state and moved child directory. Dependencies are helper binary, journaling, and flakey target. Risks are open-unlinked directory semantics and replay ordering. Signal is dir1 absent and dir3/dir2 present. Source size is 69 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/792 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/793 -->

# sources/test-tools/xfstests/tests/generic/793


Purpose: Stresses zoned filesystem garbage collection by overwriting the same 1GiB file once per sequential-write-required zone.


Important APIs, helpers, and commands: Uses `_require_zoned_device`, `blkzone report`, `_require_no_compress`, `_scratch_mkfs_sized`, and `dd`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_command`, `_require_no_compress`, `_require_scratch_size`, `_require_zoned_device`.
 Regression annotations include `_fixed_by_fs_commit btrfs 7bcb04de982f \, _fixed_by_fs_commit btrfs 258e46a6385c \, _fixed_by_fs_commit btrfs e2a7fd22378f \`.



Control flow, state, dependencies, risks, and test signals: The test selects scratch realtime device if present, otherwise scratch device, verifies zoned support, formats a 16GiB scratch filesystem, counts `SEQ_WRITE_REQUIRED` zones, and overwrites `$SCRATCH_MNT/test` with 1GiB of zeros that many times. State is zone write pointers, filesystem data allocation, and GC/reclaim metadata. Dependencies are blkzone and a zoned block device. Risks are long runtime, device wear, and compression invalidating space assumptions. Signal is no dd failure and final silence. Source size is 53 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/793 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/Makefile -->

# sources/test-tools/xfstests/tests/generic/Makefile


Purpose: Build/install glue for the xfstests generic test directory.


Important APIs, helpers, and commands: Includes `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`; sets `GENERIC_DIR`, `TARGET_DIR`, and `DIRT=group.list`; defines `install` and empty `install-dev install-lib` targets.



Control flow, state, dependencies, risks, and test signals: The default target builds `group.list`; install creates the package test target directory, installs executable tests as mode 755, installs group.list and golden output files as mode 644. State is build-generated `group.list` and installed files under `$(PKG_LIB_DIR)/$(TESTS_DIR)/generic`. Dependencies are the top-level xfstests build system variables and install tool. Risks are missing generated group.list or incorrect TESTS/OUTFILES expansion. Signals are make/install success. Source size is 24 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/nfs/001 -->

# sources/test-tools/xfstests/tests/nfs/001


Purpose: NFSv4 ACL regression test for `nfs4_getfacl` near page-sized ACL buffers, guarding against ERANGE from getxattr.


Important APIs, helpers, and commands: Uses `_require_test_nfs_version 4`, `_require_command` for `nfs4_setfacl`/`nfs4_getfacl`, and builds an ACL list with about 200 numeric ACEs.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_command`, `_require_test_nfs_version`.



Control flow, state, dependencies, risks, and test signals: It creates a file/list pair in `$TEST_DIR`, writes OWNER, many numeric, GROUP, and EVERYONE ACEs to make the ACL close to a 4KiB page, applies it with nfs4_setfacl, dumps it to full output, and counts lines beginning with `A`. State is the file’s NFSv4 ACL on the mounted NFS test export. Dependencies are NFSv4 mount and nfs4-acl tools. Risks are non-4K page assumptions and server ACL limits. Signal is the expected ACE count rather than ERANGE. Source size is 50 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/nfs/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/nfs/Makefile -->

# sources/test-tools/xfstests/tests/nfs/Makefile


Purpose: Build/install glue for the xfstests nfs test directory.


Important APIs, helpers, and commands: Includes `builddefs`, `buildgrouplist`, and `$(BUILDRULES)`; sets `NFS_DIR`, `TARGET_DIR`, and `DIRT=group.list`.



Control flow, state, dependencies, risks, and test signals: Default builds group.list; install creates the NFS package test directory, installs test scripts executable, and installs group.list/outfiles read-only. State is generated group.list and installed artifacts. Dependencies are top-level make variables and xfstests build rules. Risks are missing TESTS/OUTFILES or wrong target dir. Signals are make/install success. Source size is 24 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/nfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ocfs2/001 -->

# sources/test-tools/xfstests/tests/ocfs2/001


Purpose: OCFS2 reflink regression test ensuring inline-data files can participate correctly in clone/reflink operations with regular files and other inline files.


Important APIs, helpers, and commands: Imports `common/reflink`; uses `_scratch_mkfs --fs-features=local,unwritten,refcount,inline-data`, `tunefs.ocfs2 --query`, `_cp_reflink`, `_reflink_range`, and md5sum.
 It imports `./common/filter`, `./common/preamble`, `./common/reflink`.
 Capability gates include `_require_cp_reflink`, `_require_scratch_reflink`.



Control flow, state, dependencies, risks, and test signals: It formats OCFS2 with inline-data/refcount features, verifies inline-data support, creates regular and small inline files, remounts, reflinks a large file into small files at start/past EOF, reflinks inline data into regular and inline targets, remounts, and md5sums all files. State includes inline-data inodes, refcounted extents, and cloned file contents. Dependencies are OCFS2 tools and reflink support. Risks are feature availability and clone semantics across inline/regular conversion. Signal is stable md5sum output. Source size is 56 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ocfs2/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ocfs2/Makefile -->

# sources/test-tools/xfstests/tests/ocfs2/Makefile


Purpose: Build/install glue for the xfstests ocfs2 test directory.


Important APIs, helpers, and commands: Includes `builddefs`, `buildgrouplist`, and `$(BUILDRULES)`; sets `OCFS2_DIR`, `TARGET_DIR`, and `DIRT=group.list`.



Control flow, state, dependencies, risks, and test signals: Default builds group.list; install creates the OCFS2 package directory, installs executable tests, and installs group.list/outfiles. State is generated group.list and installed artifacts. Dependencies are top-level build variables. Risks are installation path mistakes or missing group data. Signals are successful make/install. Source size is 24 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ocfs2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/001 -->

# sources/test-tools/xfstests/tests/overlay/001


Purpose: Tests overlayfs copy-up of lower files at zero, below, equal to, and above 4GiB sizes using O_LARGEFILE paths.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_fs_space`, `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for copy-up of lower files at zero, below, equal to, and above 4GiB sizes using O_LARGEFILE paths, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 46 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/002 -->

# sources/test-tools/xfstests/tests/overlay/002


Purpose: Tests overlayfs fsync through merged overlay path after writing a lower-origin file.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for fsync through merged overlay path after writing a lower-origin file, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 38 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/003 -->

# sources/test-tools/xfstests/tests/overlay/003


Purpose: Tests overlayfs basic whiteout behavior for regular, directory, symlink, device, fifo, and hardlink lower entries.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for basic whiteout behavior for regular, directory, symlink, device, fifo, and hardlink lower entries, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 64 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/004 -->

# sources/test-tools/xfstests/tests/overlay/004


Purpose: Tests overlayfs copy-up triggered by chmod and permission behavior for privileged vs unprivileged users.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_user`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for copy-up triggered by chmod and permission behavior for privileged vs unprivileged users, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 65 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/005 -->

# sources/test-tools/xfstests/tests/overlay/005


Purpose: Tests overlayfs copy-up ENOSPC error handling using separate loop-mounted lower and small upper XFS filesystems.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_loop`, `_require_scratch_nocheck`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for copy-up ENOSPC error handling using separate loop-mounted lower and small upper XFS filesystems, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 91 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/006 -->

# sources/test-tools/xfstests/tests/overlay/006


Purpose: Tests overlayfs visible whiteout issue after renaming a lower file into an upper directory and deleting it.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for visible whiteout issue after renaming a lower file into an upper directory and deleting it, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 44 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/007 -->

# sources/test-tools/xfstests/tests/overlay/007


Purpose: Tests overlayfs getcwd after failed rmdir of the current parent directory.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_test`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for getcwd after failed rmdir of the current parent directory, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 40 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/007 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/008 -->

# sources/test-tools/xfstests/tests/overlay/008


Purpose: Tests overlayfs uid/gid ownership when creating files or directories over overlay whiteouts as another user.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_user`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for uid/gid ownership when creating files or directories over overlay whiteouts as another user, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 52 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/008 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/009 -->

# sources/test-tools/xfstests/tests/overlay/009


Purpose: Tests overlayfs default_permissions dentry leak regression during overlay unmount.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`.
 Regression annotations include `_fixed_by_kernel_commit a4859d75944a \`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for default_permissions dentry leak regression during overlay unmount, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 38 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/009 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/010 -->

# sources/test-tools/xfstests/tests/overlay/010


Purpose: Tests overlayfs removal of a merged directory containing a lower whiteout with multiple lowerdirs.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch_nocheck`.
 Regression annotations include `_fixed_by_kernel_commit 84889d493356 \`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for removal of a merged directory containing a lower whiteout with multiple lowerdirs, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 51 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/010 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/011 -->

# sources/test-tools/xfstests/tests/overlay/011


Purpose: Tests overlayfs filtering of trusted.overlay private xattrs from non-lowest lower layers.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/attr`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_attrs`, `_require_scratch`, `_require_test`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for filtering of trusted.overlay private xattrs from non-lowest lower layers, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 46 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/011 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/012 -->

# sources/test-tools/xfstests/tests/overlay/012


Purpose: Tests overlayfs stale upper dentry handling in ovl_remove_and_whiteout after direct upperdir deletion.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for stale upper dentry handling in ovl_remove_and_whiteout after direct upperdir deletion, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 44 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/012 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/014 -->

# sources/test-tools/xfstests/tests/overlay/014


Purpose: Tests overlayfs copy-up of an opaque lower directory without copying overlay private opaqueness.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch_nocheck`.
 Regression annotations include `_fixed_by_kernel_commit 0956254a2d5b "ovl: don't copy up opaqueness"`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for copy-up of an opaque lower directory without copying overlay private opaqueness, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 71 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/014 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/015 -->

# sources/test-tools/xfstests/tests/overlay/015


Purpose: Tests overlayfs SGID and group inheritance when creating over whiteouts.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_group`, `_require_scratch`, `_require_user`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for SGID and group inheritance when creating over whiteouts, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 63 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/015 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/016 -->

# sources/test-tools/xfstests/tests/overlay/016


Purpose: Tests overlayfs read-only file descriptor coherency after another descriptor triggers copy-up and writes.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_xfs_io_command`.
 Regression annotations include `_fixed_in_kernel_version "v4.19"`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for read-only file descriptor coherency after another descriptor triggers copy-up and writes, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 48 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/016 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/017 -->

# sources/test-tools/xfstests/tests/overlay/017


Purpose: Tests overlayfs stable overlay inode numbers across copy-up, rename, cache drop, and mount cycle.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_scratch_feature`, `_require_test_program`.
 Regression annotations include `_fixed_in_kernel_version "v4.14"`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for stable overlay inode numbers across copy-up, rename, cache drop, and mount cycle, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 119 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/017 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/018 -->

# sources/test-tools/xfstests/tests/overlay/018


Purpose: Tests overlayfs hardlink preservation with index=on across copy-up and mount cycle.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_scratch_feature`, `_require_test_program`.
 Regression annotations include `_fixed_in_kernel_version "v4.13"`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for hardlink preservation with index=on across copy-up and mount cycle, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 103 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/018 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/019 -->

# sources/test-tools/xfstests/tests/overlay/019


Purpose: Tests overlayfs concurrent fsstress on lowerdir and merged overlay directory.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch_nocheck`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for concurrent fsstress on lowerdir and merged overlay directory, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 79 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/019 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/020 -->

# sources/test-tools/xfstests/tests/overlay/020


Purpose: Tests overlayfs copy-up credentials in user namespace/unshare scenarios.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_unshare`.
 Regression annotations include `_fixed_by_kernel_commit 3fe6e52f0626 \`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for copy-up credentials in user namespace/unshare scenarios, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 40 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/020 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/021 -->

# sources/test-tools/xfstests/tests/overlay/021


Purpose: Tests overlayfs overlay fsstress and copy-up under low/free-space pressure.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_fs_space`, `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for overlay fsstress and copy-up under low/free-space pressure, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 100 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/021 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/022 -->

# sources/test-tools/xfstests/tests/overlay/022


Purpose: Tests overlayfs mount/unmount behavior with upper/work directories and offline upper changes.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`.
 Regression annotations include `_fixed_by_kernel_commit 76bc8e2843b6 "ovl: disallow overlayfs as upperdir"`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for mount/unmount behavior with upper/work directories and offline upper changes, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 57 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/022 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/023 -->

# sources/test-tools/xfstests/tests/overlay/023


Purpose: Tests overlayfs default ACL propagation to overlay workdir-created objects.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/attr`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_acls`, `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for default ACL propagation to overlay workdir-created objects, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 43 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/023 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/024 -->

# sources/test-tools/xfstests/tests/overlay/024


Purpose: Tests overlayfs overlay workdir cleanup and mount sanity.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for overlay workdir cleanup and mount sanity, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 46 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/024 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/025 -->

# sources/test-tools/xfstests/tests/overlay/025


Purpose: Tests overlayfs unprivileged overlay mount using extra filesystem lower/upper/work dirs.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_extra_fs`, `_require_user`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for unprivileged overlay mount using extra filesystem lower/upper/work dirs, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 55 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/025 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/026 -->

# sources/test-tools/xfstests/tests/overlay/026


Purpose: Tests overlayfs escaping and visibility of overlay xattr names through user/trusted xattr interfaces.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/attr`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_attrs`, `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for escaping and visibility of overlay xattr names through user/trusted xattr interfaces, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 92 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/026 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/027 -->

# sources/test-tools/xfstests/tests/overlay/027


Purpose: Tests overlayfs immutable upper file/dir handling with chattr during overlay operations.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_chattr`, `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for immutable upper file/dir handling with chattr during overlay operations, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 60 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/027 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/028 -->

# sources/test-tools/xfstests/tests/overlay/028


Purpose: Tests overlayfs flock/lock behavior on copied-up lower files.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_command`, `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for flock/lock behavior on copied-up lower files, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 47 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/028 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/029 -->

# sources/test-tools/xfstests/tests/overlay/029


Purpose: Tests overlayfs origin xattr verification and d_real behavior after offline or lower/upper changes.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`.
 Regression annotations include `_fixed_by_kernel_commit c4fcfc1619ea "ovl: fix d_real() for stacked fs"`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for origin xattr verification and d_real behavior after offline or lower/upper changes, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 81 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/029 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/030 -->

# sources/test-tools/xfstests/tests/overlay/030


Purpose: Tests overlayfs immutable directory behavior during overlay copy-up/removal.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_chattr`, `_require_scratch`, `_require_test_program`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for immutable directory behavior during overlay copy-up/removal, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 52 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/030 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/031 -->

# sources/test-tools/xfstests/tests/overlay/031


Purpose: Tests overlayfs whiteout creation and removal variants over lower and upper paths.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `create_whiteout`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch_nocheck`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for whiteout creation and removal variants over lower and upper paths, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 115 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/031 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/032 -->

# sources/test-tools/xfstests/tests/overlay/032


Purpose: Tests overlayfs copy-up/link/rename command matrix with index feature.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `do_cmd`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_fs_space`, `_require_scratch`, `_require_scratch_feature`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for copy-up/link/rename command matrix with index feature, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 77 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/032 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/033 -->

# sources/test-tools/xfstests/tests/overlay/033


Purpose: Tests overlayfs overlay nlink accounting for indexed hardlinks.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `create_hardlinks`, `report_nlink`, `test_hardlinks`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_scratch_feature`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for overlay nlink accounting for indexed hardlinks, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 122 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/033 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/034 -->

# sources/test-tools/xfstests/tests/overlay/034


Purpose: Tests overlayfs hardlink index nlink drop/cleanup WARN_ON regression.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_scratch_feature`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for hardlink index nlink drop/cleanup WARN_ON regression, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 80 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/034 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/035 -->

# sources/test-tools/xfstests/tests/overlay/035


Purpose: Tests overlayfs readonly/remount behavior with immutable upper/work components.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_chattr`, `_require_scratch_nocheck`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for readonly/remount behavior with immutable upper/work components, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 62 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/035 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/036 -->

# sources/test-tools/xfstests/tests/overlay/036


Purpose: Tests overlayfs overlay mount busy behavior and feature interactions.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch_feature`, `_require_scratch_nocheck`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for overlay mount busy behavior and feature interactions, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 92 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/036 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/037 -->

# sources/test-tools/xfstests/tests/overlay/037


Purpose: Tests overlayfs ESTALE/error behavior when upper/work/lower directories do not match prior mount state.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch_feature`, `_require_scratch_nocheck`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for ESTALE/error behavior when upper/work/lower directories do not match prior mount state, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 62 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/037 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/038 -->

# sources/test-tools/xfstests/tests/overlay/038


Purpose: Tests overlayfs samefs overlay inode identity for lower files and directories with xino/origin data.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/attr`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_attrs`, `_require_scratch_nocheck`, `_require_test_program`.
 Regression annotations include `_fixed_in_kernel_version "v4.14"`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for samefs overlay inode identity for lower files and directories with xino/origin data, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 182 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/038 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/039 -->

# sources/test-tools/xfstests/tests/overlay/039


Purpose: Tests overlayfs relatime/access time behavior for lower-origin files through overlay.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_relatime`, `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for relatime/access time behavior for lower-origin files through overlay, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 54 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/039 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/040 -->

# sources/test-tools/xfstests/tests/overlay/040


Purpose: Tests overlayfs FS_IOC_SETFLAGS/chattr behavior for lower-origin files copied up to upper.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_chattr`, `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for FS_IOC_SETFLAGS/chattr behavior for lower-origin files copied up to upper, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 59 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/040 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/041 -->

# sources/test-tools/xfstests/tests/overlay/041


Purpose: Tests overlayfs non-samefs overlay inode identity for lower layers on test and upper/work on scratch.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/attr`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_attrs`, `_require_scratch_nocheck`, `_require_test`, `_require_test_program`.
 Regression annotations include `_fixed_in_kernel_version "v4.17"`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for non-samefs overlay inode identity for lower layers on test and upper/work on scratch, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 190 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/041 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/042 -->

# sources/test-tools/xfstests/tests/overlay/042


Purpose: Tests overlayfs creating lower hardlinks offline for previously copied-up files with index transitions.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_scratch_feature`.
 Regression annotations include `_fixed_by_kernel_commit 6eaf011144af \`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for creating lower hardlinks offline for previously copied-up files with index transitions, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 103 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/042 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/043 -->

# sources/test-tools/xfstests/tests/overlay/043


Purpose: Tests overlayfs non-samefs stable inode numbers across copy-up/rename/cache-drop/mount-cycle.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch_feature`, `_require_scratch_nocheck`, `_require_test`, `_require_test_program`.
 Regression annotations include `_fixed_in_kernel_version "v4.17"`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for non-samefs stable inode numbers across copy-up/rename/cache-drop/mount-cycle, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 140 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/043 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/044 -->

# sources/test-tools/xfstests/tests/overlay/044


Purpose: Tests overlayfs non-samefs hardlink nlink/inode preservation with index.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch_feature`, `_require_scratch_nocheck`, `_require_test`, `_require_test_program`.
 Regression annotations include `_fixed_in_kernel_version "v4.17"`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for non-samefs hardlink nlink/inode preservation with index, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 124 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/044 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/045 -->

# sources/test-tools/xfstests/tests/overlay/045


Purpose: Tests overlayfs fsck.overlay whiteout validation and repair across lower, upper, opaque, impure, and redirect dirs.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `check_whiteout`, `make_impure_dir`, `make_opaque_dir`, `make_redirect_dir`, `make_test_dirs`, `make_whiteout`.
 It imports `./common/attr`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_attrs`, `_require_command`, `_require_scratch_nocheck`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for fsck.overlay whiteout validation and repair across lower, upper, opaque, impure, and redirect dirs, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 199 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/045 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/046 -->

# sources/test-tools/xfstests/tests/overlay/046


Purpose: Tests overlayfs fsck.overlay redirect xattr validation, repair, duplicate detection, whiteout repair, and opaque marking.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `check_no_redirect`, `check_opaque`, `check_redirect`, `check_whiteout`, `make_impure_dir`, `make_redirect_dir`, `make_test_dirs`, `make_whiteout`.
 It imports `./common/attr`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_attrs`, `_require_command`, `_require_scratch_nocheck`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for fsck.overlay redirect xattr validation, repair, duplicate detection, whiteout repair, and opaque marking, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 232 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/046 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/047 -->

# sources/test-tools/xfstests/tests/overlay/047


Purpose: Tests overlayfs hardlink data preservation after unlink of copied-up indexed hardlink and mount cycle.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_scratch_feature`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for hardlink data preservation after unlink of copied-up indexed hardlink and mount cycle, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 72 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/047 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/048 -->

# sources/test-tools/xfstests/tests/overlay/048


Purpose: Tests overlayfs nlink accounting for overlay hardlinks when upper hardlinks are edited offline.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `create_hardlinks`, `report_nlink`, `test_hardlinks_offline`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_scratch_feature`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for nlink accounting for overlay hardlinks when upper hardlinks are edited offline, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 109 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/048 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/049 -->

# sources/test-tools/xfstests/tests/overlay/049


Purpose: Tests overlayfs duplicate redirect directories pointing to the same lower origin and diff/inode ambiguity.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `create_redirect`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch_feature`, `_require_scratch_nocheck`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for duplicate redirect directories pointing to the same lower origin and diff/inode ambiguity, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 75 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/049 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/050 -->

# sources/test-tools/xfstests/tests/overlay/050


Purpose: Tests overlayfs overlay file-handle encode/decode/read/write/unlink/link/rename coverage for samefs NFS export.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `create_dirs`, `create_test_files`, `link_test_files`, `mount_dirs`, `test_file_handles`, `unmount_dirs`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_scratch_overlay_features`, `_require_test_program`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for overlay file-handle encode/decode/read/write/unlink/link/rename coverage for samefs NFS export, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 207 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/050 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/051 -->

# sources/test-tools/xfstests/tests/overlay/051


Purpose: Tests overlayfs same file-handle export coverage as overlay/050 with lower on test fs and upper/work on scratch non-samefs layers.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`, `create_dirs`, `create_test_files`, `link_test_files`, `mount_dirs`, `test_file_handles`, `unmount_dirs`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch_nocheck`, `_require_scratch_overlay_features`, `_require_test`, `_require_test_program`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for same file-handle export coverage as overlay/050 with lower on test fs and upper/work on scratch non-samefs layers, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 237 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/051 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/052 -->

# sources/test-tools/xfstests/tests/overlay/052


Purpose: Tests overlayfs overlay file-handle decode after parent/grandparent rename and moves with redirect_dir.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `create_dirs`, `create_test_files`, `mount_dirs`, `test_file_handles`, `unmount_dirs`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_scratch_overlay_features`, `_require_test_program`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for overlay file-handle decode after parent/grandparent rename and moves with redirect_dir, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 152 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/052 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/053 -->

# sources/test-tools/xfstests/tests/overlay/053


Purpose: Tests overlayfs non-samefs variant of overlay/052 file-handle rename and redirect export coverage.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`, `create_dirs`, `create_test_files`, `mount_dirs`, `test_file_handles`, `unmount_dirs`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch_nocheck`, `_require_scratch_overlay_features`, `_require_test`, `_require_test_program`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for non-samefs variant of overlay/052 file-handle rename and redirect export coverage, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 181 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/053 -->
