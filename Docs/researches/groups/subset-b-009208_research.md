# Research: subset-b-009208

This grouped report covers the CrashMonkey disk wrapper, harness, permuter, result, utility test, and selected test-case sources assigned to `subset-b-009208`. Each file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/disk_wrapper.c -->
# sources/test-tools/crashmonkey/code/disk_wrapper.c

Purpose: implements the `hwm` kernel block-device wrapper used by CrashMonkey to intercept bios, pass them through to a target block device, and keep an in-memory log of persistence-relevant operations for user-space replay.

Important APIs, types, and functions: module parameters `target_device_path` and `flags_device_path` select the wrapped device and queue-flag source. `struct disk_write_op` stores `disk_write_op_meta`, copied data, and a next pointer. The singleton `Device` tracks the gendisk, target device handle, log flags, write-log linked list, current read cursor, and checkpoint counter. `disk_wrapper_ioctl()` exposes `HWM_LOG_ON`, `HWM_LOG_OFF`, `HWM_GET_LOG_META`, `HWM_GET_LOG_DATA`, `HWM_NEXT_ENT`, `HWM_CLR_LOG`, and `HWM_CHECKPOINT`. `convert_flags()` normalizes Linux request/bio flags into stable CrashMonkey flags. `should_log()` filters bios to writes, flushes, FUA, discard, secure erase, write-same, and write-zeroes depending on kernel version. `disk_wrapper_bio()` logs selected bios then submits them to the real target. `disk_wrapper_init()` registers `/dev/hwm`, allocates the queue/disk, clones queue flags, and opens the wrapped devices. `hello_cleanup()` frees logs, releases target devices, queue, gendisk, and major number.

Control flow: initialization validates module paths, creates a default checkpoint entry, registers a block major, grabs the target and flags devices, creates a gendisk named `hwm`, installs `disk_wrapper_bio()` as the make-request function, and publishes the disk. Runtime bios enter `disk_wrapper_bio()`: if logging is enabled and `should_log()` accepts the bio, metadata is converted and appended to the linked list under `Device.lock`, bio page segments are copied into kernel memory, and the original bio is retargeted to the underlying device before `submit_bio()`. User space reads logs by repeatedly getting metadata, getting data, and advancing with `HWM_NEXT_ENT`. Checkpoints are synthetic log entries with `HWM_CHECKPOINT_FLAG`.

State and persistence behavior: all recorded write data is volatile kernel memory; nothing is persisted by the wrapper itself. Checkpoints are monotonically numbered in `metadata.write_sector`, while logged real writes preserve sector and size. `HWM_CLR_LOG` frees old entries and seeds a new first checkpoint. The module copies payload bytes before passthrough, so replay sees the data originally submitted to the block layer rather than later page contents.

Dependencies and integration points: this file depends on Linux block-layer APIs across narrow tested kernel ranges, `bio_alias.h` compatibility macros, and `disk_wrapper_ioctl.h` for the user/kernel ABI. `Tester.cpp` loads this module with `insmod`, opens `/dev/hwm`, toggles logging, fetches log entries, and creates checkpoints. The device must be used with `cow_brd` snapshots for crash-state construction.

Risks and edge cases: the file explicitly notes that ioctl/log handling is not thread-safe. The linked-list node is appended before data allocation succeeds; if `kmalloc()` for data fails, the code frees the node without unlinking it, leaving a potential dangling list entry. `copy_to_user()` loops use pointer arithmetic on structure pointers (`&(metadata) + offset`) rather than byte pointers, which is fragile. Init failure paths commonly return `-ENOMEM` and do not consistently release partially acquired devices or disks. Kernel-version conditionals are narrow and reject untested kernels at compile time. `should_log()` for newer kernels compares `bio_op(bio)` with `BIO_DISCARD_FLAG`, which appears suspicious because discard is usually an operation, not a flag. The queue-cloning and passthrough path assumes old make-request semantics and may not survive modern block-layer changes.

Test signals: `testing/log_on_off.c`, `testing/test_get_log_ent_size.c`, `ioctl_test.c`, and the harness exercise the ioctl surface. Meaningful validation requires privileged kernel-module insertion, a target block device, `/dev/hwm`, and workload replay through `Tester`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/disk_wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/disk_wrapper_ioctl.h -->
# sources/test-tools/crashmonkey/code/disk_wrapper_ioctl.h

Purpose: defines the shared ioctl ABI and stable CrashMonkey flag encoding used by the kernel wrapper, cow RAM block device controls, and user-space harness/tests.

Important APIs/types: `HWM_LOG_OFF`, `HWM_LOG_ON`, `HWM_GET_LOG_META`, `HWM_GET_LOG_DATA`, `HWM_NEXT_ENT`, `HWM_CLR_LOG`, and `HWM_CHECKPOINT` are the wrapper commands. `COW_BRD_SNAPSHOT`, `COW_BRD_UNSNAPSHOT`, `COW_BRD_RESTORE_SNAPSHOT`, and `COW_BRD_WIPE` are cow_brd commands. `enum flag_shifts` defines a kernel-version-independent bit namespace for request semantics such as write, FUA, flush, discard, metadata, no-idle, integrity, and write-zeroes. `struct disk_write_op_meta` is the fixed metadata transferred to user space.

Control flow and integration: kernel code fills `disk_write_op_meta` for every logged write/checkpoint, and user-space code reads the structure before requesting the matching payload. Harness utilities construct `disk_write`/`DiskWriteData` objects from this metadata for serialization, replay, and permutation.

State and persistence behavior: this header does not store state, but it defines the interpretation of persisted profile logs saved by `Tester::log_profile_save()`. ABI changes here can make existing binary logs unreadable or semantically wrong.

Dependencies: included from kernel C code and user-space C/C++ code, so the definitions avoid Linux-only types in exported structures. It assumes `unsigned long` and `unsigned int` sizes are compatible between producer and consumer on the tested platform.

Risks: ioctl command numbers overlap (`HWM_CHECKPOINT` and `COW_BRD_SNAPSHOT` are both `0xff06`) and are not encoded with `_IO`, `_IOR`, or `_IOW`, so type checking and namespace separation are weak. The header lacks currently referenced stale commands such as `HWM_GET_LOG_ENT_SIZE` and `HWM_GET_LOG_ENT`, making older tests fail to compile. `disk_write_op_meta` uses architecture-sized `unsigned long` for sectors, which is less portable than fixed-width types.

Test signals: compile-time compatibility across kernel/user code is the first signal. Runtime signals come from successful log extraction in `Tester::get_wrapper_log()` and cow_brd snapshot operations in `Tester::clone_device()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/disk_wrapper_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/DiskContents.cpp -->
# sources/test-tools/crashmonkey/code/harness/DiskContents.cpp

Purpose: implements file-system image comparison helpers used by automated checkpoint checking. It mounts crash-state snapshots read-only, walks directory trees, captures file attributes and data hashes, compares them against `/mnt/snapshot`, and performs basic sanity mutations.

Important APIs/functions: `fileAttributes` stores `dirent`, `stat`, and `md5sum`; setters populate directory, stat, and md5 fields; comparison methods compare directory metadata, stat metadata, and hashes. `DiskContents::mount_disk()` mounts a device under `/mnt/<device suffix>`. `get_contents()` recursively collects relative-path attributes. `compare_disk_contents()` compares full namespace and file contents. `compare_entries_at_path()` compares metadata/data for a single path. `compare_file_contents()` compares a byte range at offset/length. `deleteFiles()`, `makeFiles()`, and `sanity_checks()` mutate `/mnt/snapshot` to verify recovered state remains writable/cleanable.

Control flow: a base `DiskContents` object is usually pointed at already mounted `/mnt/snapshot`, while the comparison object mounts another snapshot. The code gathers content maps keyed by relative path, checks entry counts, reports missing/mismatched entries to a diff file, compares md5s for regular files, then unmounts the comparison disk. Path-specific checks mount only the comparison disk and directly stat/read the relevant paths.

State and persistence behavior: object state is the `contents` map, mount path, disk path, fs type, and mount flag. The comparisons observe post-replay persisted state. `sanity_checks()` intentionally creates dummy files in directories and recursively deletes contents from `/mnt/snapshot`, so it is destructive and should run only on disposable crash-state images.

Dependencies and integration: depends on POSIX directory/stat/mount APIs, `md5sum` via `popen()`, C++ streams, and hard-coded `/mnt/snapshot`. `Tester::check_disk_and_snapshot_contents()` uses this class for automated checks based on `DiskMod` checkpoint data.

Risks: constructor initialization has a bug (`stat_attr.st_ino == -1`) that compares rather than assigns. `compare_md5sum()` returns the raw `std::string::compare()` integer as bool, so equal hashes return false and mismatches return true; callers compensate with `!= 0` in some places but the API is misleading. `unmount_and_delete_mount_point()` calls `unlink()` on a directory instead of `rmdir()`. Shelling out to `md5sum` with an unquoted path is injection- and whitespace-prone. `compare_file_contents()` uses C strings and `strcmp()` on binary buffers, so embedded NUL bytes can hide differences. `contents` is not cleared before scans, which can contaminate repeated comparisons.

Test signals: diff files named by checkpoint, failed automated data tests, and sanity-check console messages indicate comparison behavior. Unit-style coverage should include equal/mismatched hashes, binary files with NULs, symlinks, missing files, and mount cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/DiskContents.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/DiskContents.h -->
# sources/test-tools/crashmonkey/code/harness/DiskContents.h

Purpose: declares the `fileAttributes` and `DiskContents` helpers for comparing mounted file-system contents and validating crash-state images.

Important APIs/types: `fileAttributes` exposes captured `dirent`, `stat`, and md5 data plus setters/comparators. `DiskContents` exposes mount/unmount, mount-point setters, full-disk comparison, path comparison, range comparison, recursive deletion/creation helpers, and `sanity_checks()`.

Control flow and integration: `Tester` constructs these objects during automated check mode. The private `get_contents()` recursively builds the content map, while public comparison functions orchestrate mounting and reporting.

State: private fields track whether a disk was mounted, the source device path, mount point, fs type, and a map from relative path to attributes. The header implies objects are stateful and not reusable safely without clearing `contents`.

Dependencies: includes Linux/POSIX filesystem headers and C++ streams/maps. The interface is tied to Unix path strings and block-device mount semantics.

Risks and test signals: the private declaration `compare_contents()` is not implemented in the read file set, suggesting stale design. Tests should validate that repeated calls do not retain stale map entries, that mount-point lifecycle is correct, and that special files/symlinks are handled intentionally.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/DiskContents.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/FsSpecific.cpp -->
# sources/test-tools/crashmonkey/code/harness/FsSpecific.cpp

Purpose: implements filesystem-specific command generation, post-replay mount options, fsck return-code interpretation, UUID regeneration commands, and post-workload writeback delays.

Important APIs/functions: `GetFsSpecific()` returns a subclass for `ext2`, `ext3`, `ext4`, `btrfs`, `f2fs`, or `xfs`. `ExtFsSpecific` builds `mkfs`, mount options, `fsck`, `tune2fs`, and parses ext fsck bitmasks. `BtrfsFsSpecific`, `F2fsFsSpecific`, and `XfsFsSpecific` build their respective check/UUID commands and map coarse return codes into `FileSystemTestResult`.

Control flow: `Tester::set_fs_type()` creates an implementation based on CLI `--fs-type`. Formatting, post-replay mount, fsck, snapshot UUID changes, and post-run delay all dispatch through the polymorphic interface.

State and persistence behavior: `ExtFsSpecific` stores fs type and delay. Commands mutate disks by formatting, repairing/checking, and changing UUIDs. The post-replay mount options can trigger kernel recovery/orphan cleanup before fsck runs.

Dependencies: external tools include `mkfs`, `fsck`, `tune2fs`, `btrfs check`, `btrfstune`, `xfs_repair`, `xfs_admin`, and `fsck.f2fs`. Build macros such as `TWO_SEC`, `THREE_THIRTEEN`, `FOUR_FOUR`, `FOUR_FIFTEEN`, and `FOUR_SIXTEEN` tune delays.

Risks: command strings are shell-concatenated without escaping device paths. `ExtFsSpecific::GetFsTypeString()` always returns `ext4` even for ext2/ext3 objects. Btrfs maps return code `0` to `kFixed` rather than `kClean`, which affects result classification. F2fs and Xfs return-code interpretation is deliberately approximate. `yes | btrfs check` and repair-style tools may change the device, making results dependent on checker behavior.

Test signals: the main signals are harness phase success/failure for mkfs, mount, fsck/checker return classification, and timing delays sufficient to capture writeback on target kernels.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/FsSpecific.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/FsSpecific.h -->
# sources/test-tools/crashmonkey/code/harness/FsSpecific.h

Purpose: declares the filesystem-specific polymorphic interface and concrete classes used by the harness.

Important APIs/types: abstract `FsSpecific` requires methods for fs type string, mkfs command, post-replay mount options, fsck command, UUID command, fsck return mapping, and post-run delay. Concrete types include `ExtFsSpecific`, `Ext2FsSpecific`, `Ext3FsSpecific`, `Ext4FsSpecific`, `BtrfsFsSpecific`, `F2fsFsSpecific`, and `XfsFsSpecific`.

Control flow and integration: `GetFsSpecific()` constructs the matching implementation for `Tester`. `Tester` owns the returned pointer and uses it throughout setup, replay, and checking.

State and persistence behavior: concrete classes encode delays as compile-time constants keyed by kernel build macros. Commands generated by implementations mutate filesystem state by formatting, checking/repairing, and regenerating UUIDs.

Dependencies: depends on `FileSystemTestResult` for classification and on build-time macro definitions for kernel/version-specific delay choices.

Risks: the interface returns shell command strings rather than structured argv arrays, so callers inherit quoting risks. Delay constants are empirical and can make tests slow or flaky when kernel/storage behavior changes. Ownership is raw-pointer based.

Test signals: selecting every supported fs type should produce a non-null implementation and sane commands. Result mapping should be validated against expected checker exit codes.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/FsSpecific.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/Tester.cpp -->
# sources/test-tools/crashmonkey/code/harness/Tester.cpp

Purpose: implements CrashMonkey's core orchestration object. It manages cow_brd snapshots, the disk wrapper module, dynamically loaded tests/permuters, workload logging, crash-state replay, fsck/data checks, profile persistence, and timing/result accounting.

Important APIs/functions: setup methods include `set_fs_type()`, `set_device()`, `set_flag_device()`, `insert_cow_brd()`, `insert_wrapper()`, `format_drive()`, and mount/unmount helpers. Wrapper APIs include `get_wrapper_ioctl()`, `begin_wrapper_logging()`, `end_wrapper_logging()`, `get_wrapper_log()`, `clear_wrapper_log()`, and `CreateCheckpoint()`. Replay/check APIs include `test_check_random_permutations()`, `test_check_log_replay()`, `test_fsck_and_user_test()`, `test_write_data()`, `check_disk_and_snapshot_contents()`, and snapshot mapping helpers. Persistence APIs include `log_profile_save/load()` and `log_snapshot_save/load()`.

Control flow: phase setup inserts cow_brd, formats and snapshots a base image, inserts the wrapper around the first cow snapshot, runs a workload while logging, then removes the wrapper and replays captured bios. Random replay initializes a permuter from `log_data`, repeatedly restores the snapshot, writes a generated crash state, runs fsck/data checks, prints results, and tallies suite outcomes. In-order replay walks logged operations until checkpoints, restores a clean snapshot, writes the prefix crash state, and checks each checkpoint.

State and persistence behavior: persistent profiles are binary serialized `disk_write` entries plus full snapshot images. Runtime state includes raw device paths, snapshot path, `log_data`, `mods_` from user-tool serialized changes, checkpoint-to-snapshot map, open fds, module-insert flags, mount state, timing stats, and `TestSuiteResult`s. `clone_device_restore()` and `log_snapshot_load()` mutate cow_brd snapshots; `test_write_data()` writes raw bytes directly to block devices at recorded offsets.

Dependencies and integration: uses `disk_wrapper_ioctl.h`, `DiskContents`, `FsSpecific`, `ClassLoader`, `DiskMod`, `utils`, `BaseTestCase`, `Permuter`, Linux mount/ioctl/procfs APIs, `fdisk`, `insmod`, `rmmod`, and filesystem tools. `c_harness.cpp` drives this object.

Risks: many shell commands concatenate device paths. Hard-coded device names (`/dev/hwm`, `/dev/cow_ram0`, `/dev/cow_ram_snapshot1_0`, `/mnt/snapshot`) limit reusability. Cleanup has early returns that can skip later cleanup. Several error paths leak fds or skip closes after snapshot restore failures. `update_dirty_expire_time()` assumes `/proc/sys/vm/dirty_expire_centisecs` can be opened and restored. The code assumes `log_iter->is_checkpoint()` even when `log_iter` may be `end()` in one branch. `log_snapshot_save/load()` uses `unsigned int buf[4096]` while treating counts as bytes, which is odd though it over-allocates. Automated checking asserts checkpoint bounds and can abort.

Test signals: generated log files, printed timing stats, `TestSuiteResult` summaries, diff-at-check files, fsck output, and harness phase failures are the main observable signals. End-to-end validation needs root privileges, kernel modules, disposable block devices, and filesystem tools.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/Tester.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/Tester.h -->
# sources/test-tools/crashmonkey/code/harness/Tester.h

Purpose: declares the main CrashMonkey harness class and shared error codes/timing categories for orchestrating tests.

Important APIs/types: error macros categorize failures for cloning, formatting, mounting, wrapper/cow_brd insertion, cache clearing, and partitioning. `Tester::time_stats` indexes timing buckets. Public methods cover setup, module control, wrapper logging, test/permuter class loading, snapshot operations, workload replay, profile save/load, cleanup, and result printing.

Control flow and integration: `c_harness.cpp` calls methods in phase order. `Tester` hides lower-level interactions with kernel modules and loaded shared objects while exposing enough knobs for CLI-driven operation.

State: private fields include `FsSpecific*`, device paths, loaders, dirty-expire buffer, current suite pointer, module flags/fds, sector size, logged writes, disk modification groups, timing stats, result suites, checkpoint snapshot map, and active snapshot path.

Dependencies: depends on `FsSpecific`, `Permuter`, `TestSuiteResult`, `BaseTestCase`, `ClassLoader`, `DiskMod`, and `utils`. The class is Linux-specific because of mount/ioctl/proc/sysfs operations in the implementation.

Risks: raw pointer ownership and public constant member `verbose` initialized through constructor are non-idiomatic. Many public methods require an implicit state sequence; calling them out of order can fail or corrupt runtime state. Error codes are integer macros rather than a scoped enum. Some comments mention making private fields public for speed, indicating unresolved design debt.

Test signals: interface-level tests can mock loaded classes and verify state transitions, but realistic coverage requires full harness execution.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/Tester.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/c_harness.cpp -->
# sources/test-tools/crashmonkey/code/harness/c_harness.cpp

Purpose: provides the `main()` entry point for CrashMonkey. It parses CLI options, drives the `Tester` through setup/profiling/replay phases, optionally coordinates with an external client over a Unix socket, and writes run logs.

Important APIs/control flow: options select background mode, automated checks, devices, disk size, flag device, log save/load files, mount options, dry run, permuter shared object, iterations, fs type, verbosity, replay modes, full-bio replay, and sector size. Phase 0 validates arguments, opens a background socket, constructs `Tester`, inserts cow_brd, loads the test and permuter, sets environment variables, and changes dirty-expire timing. Phase 1 creates or loads a base disk image. Phase 2 records a workload through the wrapper or loads a saved profile. Phase 3 runs random and/or in-order replay tests. Phase 4 prints stats and cleans up.

State and persistence behavior: the program creates timestamped log files, optional profile/snapshot binary logs, `run_changes` serialized user-tool data, and environment variables `MOUNT_FS` and `FILESYS_SIZE`. It mutates kernel modules, procfs settings, mounted filesystems, and cow_brd snapshots.

Dependencies and integration: depends on `Tester`, `BaseTestCase` shared libraries, `RandomPermuter.so` by default, communication socket utilities, filesystem tools, `fdisk`, root privileges, and fixed mount/device paths.

Risks: `cout << "running " << argv` prints the pointer value, not argv contents. The fs-type lowercasing loop modifies a copy of each char (`for (auto c : fs_type)`) and has no effect. `path = argv[test_case_idx]` is evaluated before confirming `test_case_idx != argc`, so missing test argument can read out of bounds. Background socket is always initialized even when not needed. Several cleanup paths return without restoring dirty-expire settings. `change_fd` may be uninitialized for checkpoint-specific child runs. Command strings and `fdisk` parsing are brittle. The `no_lvm` and `dry_run` variables are mostly unused/misleading.

Test signals: phase banners and log files show progress; socket messages signal background checkpoint workflow; final `TestSuiteResult` output gives pass/fail counts. CLI smoke tests should cover missing args, reload-log mode, dry run, background protocol, and both replay modes.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/harness/c_harness.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/ioctl_test.c -->
# sources/test-tools/crashmonkey/code/ioctl_test.c

Purpose: small user-space smoke test that opens a cow_brd snapshot device and issues a restore ioctl.

Important APIs/control flow: `main()` opens `/dev/cow_ram_snapshot1_0`, calls `ioctl(fd, COW_BRD_RESTORE_SNAPSHOT)`, prints simple errors, closes the fd, and returns the ioctl result or negative error sentinel.

State and persistence behavior: restore mutates the cow_brd snapshot state by reverting it to the saved baseline. The program itself stores no persistent state.

Dependencies and integration: includes `disk_wrapper_ioctl.h` for the cow_brd ioctl number and assumes the cow_brd module/device already exists.

Risks: hard-coded device path, missing `stdio.h` and `unistd.h` includes for `printf()`/`close()` in strict builds, no command-line configurability, and overlapping ioctl numbers with wrapper commands.

Test signals: success is process exit `0`; open/ioctl failure prints a short message and returns negative values.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/ioctl_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/permuter/Permuter.cpp -->
# sources/test-tools/crashmonkey/code/permuter/Permuter.cpp

Purpose: implements common permutation machinery for converting a logged bio stream into persistence epochs and generating de-duplicated crash states.

Important APIs/functions: `BioVectorHash` and `BioVectorEqual` hash/check generated crash-state identities. `epoch_op::ToSectors()` splits a bio into sector-sized pieces. `epoch_op::ToWriteData()` and `EpochOpSector::ToWriteData()` produce replayable `DiskWriteData`. `Permuter::InitDataVector()` groups `disk_write` entries into epochs using barriers and checkpoints. `GenerateCrashState()` and `GenerateSectorCrashState()` invoke subclass generators and reject duplicate states. `CoalesceSectors()` keeps only the latest sector write for each disk offset.

Control flow: `InitDataVector()` scans the logged data, starts epochs, handles checkpoint entries by updating checkpoint epoch numbers, records overlap metadata, and splits flush-with-data operations into a zero-size flush half and a data half for the next epoch unless FUA is present. Generation calls the subclass for a candidate, builds a uniqueness vector from bio indices or sector indices, retries until unique or the retry heuristic expires, then fills result vectors and `PermuteTestResult`.

State and persistence behavior: the object stores `epochs_`, selected `sector_size_`, and an in-memory set of completed permutations. It does not persist choices; repeatability depends on subclass RNG.

Dependencies and integration: consumes `utils::disk_write` from the wrapper log and produces `utils::DiskWriteData` for `Tester::test_write_data()`. Subclasses such as `RandomPermuter` implement the abstract generation hooks.

Risks: overlap range math mixes sectors and byte sizes (`metadata.size`) and may mark ranges inaccurately unless sizes are in sectors. `epoch::num_meta` is incremented without visible initialization when `epochs_.emplace_back()` value-initializes a POD-like struct; this may be undefined if not zeroed. Duplicate detection stores only operation indexes, not data content. Retry cutoff is heuristic and can stop before exhausting state space.

Test signals: useful tests feed artificial logs with checkpoints, flush/FUA/data combinations, overlapping writes, and duplicate states, then verify epoch boundaries and generated replay vectors.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/permuter/Permuter.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/permuter/Permuter.h -->
# sources/test-tools/crashmonkey/code/permuter/Permuter.h

Purpose: declares the abstract permuter interface and shared epoch/sector data structures used to generate crash states from logged writes.

Important APIs/types: `epoch_op` wraps an absolute bio index plus `disk_write`; `epoch` groups operations with metadata about barriers, overlaps, and checkpoint association; `EpochOpSector` represents a sub-bio sector view. `Permuter` exposes `InitDataVector()`, `GenerateCrashState()`, and `GenerateSectorCrashState()`, while requiring subclasses to implement `init_data()`, `gen_one_state()`, and `gen_one_sector_state()`.

Control flow and integration: `Tester` loads a `Permuter` from a shared object and calls the public generation methods. The public layer handles common preprocessing and uniqueness; subclasses decide which prefix/subset/sectors to keep.

State: private state is the epoch vector and completed-permutation set. `sector_size_` is protected for subclasses.

Dependencies: depends on `utils.h` disk-write structures and `PermuteTestResult` for logging generated states.

Risks: raw pointers in `EpochOpSector` refer into `epochs_`, so vector reallocation or stale sector objects can invalidate parents. The abstract `init_data()` hook exists but the base `InitDataVector()` does not call it in the current implementation, making it effectively dead unless subclasses are used differently.

Test signals: subclass conformance can be tested by loading `RandomPermuter.so` and verifying generated `DiskWriteData` reflects the epoch model.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/permuter/Permuter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/permuter/RandomPermuter.cpp -->
# sources/test-tools/crashmonkey/code/permuter/RandomPermuter.cpp

Purpose: implements a deterministic pseudo-random permuter plugin that chooses a crash point and drops a random subset of bios or sectors from the final epoch.

Important APIs/functions: `GenRandom` wraps a fixed-seed mt19937 for `random_shuffle`. `RandomPermuter::gen_one_state()` chooses a number of epochs and operations, copies complete prior epochs, and subsets the final epoch. `gen_one_sector_state()` chooses a crash epoch, optionally coalesces sectors in the final epoch, drops a subset, and emits `DiskWriteData`. `subset_epoch()` selects bios from an epoch while preserving order. `AddEpochs()` copies full epochs into replay output. The `extern "C"` factory/defactory expose the plugin to `ClassLoader`.

Control flow: whole-bio generation picks `num_epochs` in `[1, epochs.size()]`, then picks a prefix length in the last epoch. Sector generation similarly picks a final epoch and request prefix, expands it into sectors, handles full barrier epochs as non-reorderable, coalesces duplicate sector offsets, and selects sectors by bitmap so temporal order is preserved.

State and persistence behavior: RNGs are fixed-seed (`42`) for repeatable runs. No generated state is persisted here; `Tester` logs and replays returned crash states.

Dependencies and integration: subclass of `Permuter`, uses C++ `<random>`, `<algorithm>`, `<numeric>`, and CrashMonkey `DiskWriteData`.

Risks: the default constructor does not seed `rand`, while the pointer-taking constructor does; the factory uses the pointer-taking constructor, but other construction paths may be nondeterministic. `std::random_shuffle` is removed in modern C++ standards. In sector mode, `num_sectors` is sampled before coalescing, so it can exceed the coalesced sector vector size; result size may then be larger than filled entries. Fixed seed improves reproducibility but limits exploration diversity across runs unless duplicate rejection changes the sequence.

Test signals: deterministic expected sequences can be asserted for small synthetic epoch sets. Tests should include empty epochs, barrier-ending epochs, duplicate sector offsets, and full-bio versus sector mode.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/permuter/RandomPermuter.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/permuter/RandomPermuter.h -->
# sources/test-tools/crashmonkey/code/permuter/RandomPermuter.h

Purpose: declares the deterministic random permuter plugin.

Important APIs/types: `GenRandom` is an adapter used by `random_shuffle`. `RandomPermuter` extends `Permuter`, providing constructors and overrides for whole-bio and sector crash-state generation.

Control flow and integration: `RandomPermuter.so` is the default permuter loaded by `c_harness.cpp`; factory symbols in the `.cpp` instantiate it for the harness.

State: stores one mt19937 for selecting crash points and one `GenRandom` for subset shuffling.

Dependencies: includes `Permuter.h`, `utils.h`, and `PermuteTestResult.h`.

Risks and test signals: stateful RNG means generation is order-dependent; fixed seeds make results reproducible. Header exposes no method to set a seed, so tests needing different exploration must change code or load another plugin.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/permuter/RandomPermuter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/DataTestResult.cpp -->
# sources/test-tools/crashmonkey/code/results/DataTestResult.cpp

Purpose: implements user-data consistency error tracking and formatting.

Important APIs/functions: constructor and `ResetError()` set the state to `kClean`; `SetError()` assigns the given error; `GetError()` returns it; `PrintErrors()` iterates bit flags; `operator<<` maps enum values to stable text tokens.

Control flow and state: test cases call `SetError()` and optionally fill `error_description`; `SingleTestInfo` later prints the data errors and uses them for result classification.

Dependencies: paired with `DataTestResult.h`, used by `BaseTestCase` implementations and `TestSuiteResult`.

Risks: `SetError()` overwrites rather than ORs, unlike `FileSystemTestResult`, so multiple data errors cannot be accumulated. `PrintErrors()` prints adjacent tokens without separators. Namespace-local bit constants in the header can create independent internal-linkage constants per translation unit, though they are compile-time values.

Test signals: unit tests should assert text output for every enum and behavior when setting multiple errors sequentially.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/DataTestResult.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/DataTestResult.h -->
# sources/test-tools/crashmonkey/code/results/DataTestResult.h

Purpose: declares `DataTestResult`, the data-consistency result object used by test cases.

Important APIs/types: `ErrorType` includes clean, old file persisted, file missing, data corrupted, metadata corrupted, incorrect block count, other, and automated-check failure bits. Public fields/methods include `ResetError()`, `SetError()`, `GetError()`, `PrintErrors()`, and `error_description`.

Control flow and integration: `BaseTestCase::check_test()` implementations receive a pointer and set errors; `SingleTestInfo` embeds one; `TestSuiteResult` tallies it.

State: private `error_summary_` plus public description string. State is not persisted except through log output.

Risks: the enum is bitmask-shaped but API and tallying mostly treat it as a single value. Header-level anonymous namespaces are unusual in headers and create per-translation-unit constants.

Test signals: compile/link tests across multiple translation units and tally tests for each error type.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/DataTestResult.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/FileSystemTestResult.cpp -->
# sources/test-tools/crashmonkey/code/results/FileSystemTestResult.cpp

Purpose: implements filesystem checker/mount/replay error accumulation and formatting.

Important APIs/functions: constructor and `ResetError()` set `kCheckNotRun`; `SetError()` ORs new error bits into the summary; `GetError()` returns the bitmask; `PrintErrors()` emits every set error; `operator<<` maps bits to text.

Control flow and state: `Tester::test_fsck_and_user_test()` sets mount, fsck, unmountable, snapshot restore, and bio-write errors. `SingleTestInfo` uses the bitmask to classify pass/fixed/required/failed outcomes.

Dependencies: used by `FsSpecific` return mapping, `SingleTestInfo`, and `TestSuiteResult`.

Risks: because `kClean` is bit `1` and `SetError()` ORs, a state can contain both clean and error bits if callers set clean after errors. `PrintErrors()` treats `error_summary_ == 0` as `fsck_not_run`, matching the enum but making "no bits set" distinct from clean. Some result classification checks exact equality and may misclassify combined states.

Test signals: tests should cover combined bits, clean plus error, and exact output strings for every enum.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/FileSystemTestResult.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/FileSystemTestResult.h -->
# sources/test-tools/crashmonkey/code/results/FileSystemTestResult.h

Purpose: declares filesystem-level result state and error vocabulary.

Important APIs/types: `ErrorType` covers check-not-run, clean, unmountable, check error, fixed, snapshot restore, bio write, other, kernel mount failure, and unfixed fsck errors. Public strings store an error description and raw fsck output.

Control flow and integration: `FsSpecific` returns `ErrorType` values from checker exit codes; `Tester` sets errors based on replay/mount/fsck outcomes; result printers consume the state.

State: private unsigned bitmask `error_summary_`, plus public description/output strings for logs.

Risks: anonymous namespace constants in a header, exact-equality assumptions elsewhere, and bitmask combinations that can include `kClean` alongside failures.

Test signals: result classification in `SingleTestInfo` is the key downstream behavior to validate.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/FileSystemTestResult.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/PermuteTestResult.cpp -->
# sources/test-tools/crashmonkey/code/results/PermuteTestResult.cpp

Purpose: implements formatting for the crash state selected by a permuter.

Important APIs/functions: `PrintCrashStateSize()` prints the count of bios/sectors; `PrintCrashState()` prints `(bio_index)` or `(bio_index, sector_index)` tuples depending on whether entries are full bios.

Control flow and state: `RandomPermuter` fills `crash_state`; `SingleTestInfo::PrintResults()` calls these methods for every test.

Dependencies: relies on `DiskWriteData` fields `bio_index`, `bio_sector_index`, and `full_bio`.

Risks: terminology "bios/sectors" is intentionally ambiguous for mixed modes. Empty state prints a size but no tuple list. Output is human-readable rather than machine-parseable.

Test signals: verify formatting for empty, full-bio, sector-only, and mixed crash states.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/PermuteTestResult.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/PermuteTestResult.h -->
# sources/test-tools/crashmonkey/code/results/PermuteTestResult.h

Purpose: declares the logged description of a generated crash state.

Important APIs/types: stores `last_checkpoint` and `std::vector<DiskWriteData> crash_state`; exposes printers for size and tuple list.

Control flow and integration: permuters populate it, `Tester` passes it through `SingleTestInfo`, and result logs record it.

State and persistence behavior: state is in-memory during a run and persisted only through text logs.

Risks: `last_checkpoint` is not default-initialized in the header, so generators must always set it before printing. The vector can be large for many-sector states.

Test signals: default construction followed by printing should be avoided or tested for initialization issues.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/PermuteTestResult.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/SingleTestInfo.cpp -->
# sources/test-tools/crashmonkey/code/results/SingleTestInfo.cpp

Purpose: implements per-crash-state result classification and detailed log printing.

Important APIs/functions: constructor resets embedded fs/data results. `GetTestResult()` classifies a test as passed, fsck fixed, fsck required, or failed based on exact fs/data states. `PrintResults()` writes test number, result, data/fsck error details, crash-state tuple list, last checkpoint, and raw fsck output. `operator<<` prints result labels.

Control flow and state: `Tester` creates one `SingleTestInfo` per random or checkpoint replay, fills `test_num`, `permute_data`, `fs_test`, and `data_test`, prints it, and tallies it in `TestSuiteResult`.

Dependencies: depends on `DataTestResult`, `FileSystemTestResult`, and `PermuteTestResult`.

Risks: exact equality against fsck bitmasks can misclassify combined states. `PrintResults()` prints data errors before fs errors, so fs-only failures may show a blank data-error field. If fsck returned `kCheck`, it prints `fs_test.error_description`; otherwise it prints data description, which can hide filesystem context for other fs errors.

Test signals: classification matrix tests are important for combinations of clean, fixed, kernel mount, unmountable, bio-write, and data errors.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/SingleTestInfo.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/SingleTestInfo.h -->
# sources/test-tools/crashmonkey/code/results/SingleTestInfo.h

Purpose: declares the per-test result container that combines crash-state, data-test, and filesystem-test information.

Important APIs/types: `ResultType` includes passed, fsck fixed, fsck required, and failed. Public fields are `test_num`, `fs_test`, `data_test`, and `permute_data`.

Control flow and integration: `Tester` fills and prints this object for each tested crash state, then passes it to `TestSuiteResult` tally methods.

State: no persistence beyond logs. Public mutable fields keep construction lightweight.

Risks: the header comments warn about memory consumption for very large test counts. Public fields make invalid partial states easy to construct. `test_num` is not visibly initialized in the header.

Test signals: ensure every `ResultType` prints correctly and downstream suite tallies match classifications.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/SingleTestInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/TestSuiteResult.cpp -->
# sources/test-tools/crashmonkey/code/results/TestSuiteResult.cpp

Purpose: implements aggregate counters and summary printing for reordering and timing/log-replay tests.

Important APIs/functions: `TallyResult()` increments pass/fixed/fsck-required/failed counters and failure subcategories. `TallyReorderingResult()` and `TallyTimingResult()` route to separate `ResultSet`s. `GetReorderingCompleted()`, `GetTimingCompleted()`, and `GetCompleted()` compute totals. `PrintResults()` emits human-readable summaries.

Control flow and state: `Tester` creates a suite at run start, tallies each `SingleTestInfo`, and prints summaries at the end.

Dependencies: consumes `SingleTestInfo`, `DataTestResult`, and `FileSystemTestResult`.

Risks: failed data-error tally uses a `switch` on exact `DataTestResult::GetError()`, so combined bitmask errors are not counted. There is no `default` in the inner switch. `total_tests` exists in `ResultSet` but is not updated. `auto_check_failed` is printed only for timing tests, not reordering tests.

Test signals: tally tests should cover every result category and data error, including combined errors and automated-check failures.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/TestSuiteResult.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/TestSuiteResult.h -->
# sources/test-tools/crashmonkey/code/results/TestSuiteResult.h

Purpose: declares aggregate suite counters for CrashMonkey runs.

Important APIs/types: `ResultSet` stores pass/fixed/failed/fsck-required counts and data-failure subcounts. `TestSuiteResult` exposes tally methods, completed-count accessors, and result printing.

Control flow and integration: owned by `Tester` in a vector, with `current_test_suite_` pointing at the active instance.

State and persistence behavior: in-memory counters are persisted only through printed summaries.

Risks: `total_tests` is unused; the structure is not self-validating; no machine-readable export is provided.

Test signals: verify completed counts equal the sum of tallied categories and summary output remains stable for log consumers.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/results/TestSuiteResult.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/testing/log_on_off.c -->
# sources/test-tools/crashmonkey/code/testing/log_on_off.c

Purpose: minimal utility to verify that the wrapper device can be opened and accepts log on/off ioctls.

Important APIs/control flow: opens `/dev/hwm1`, calls `HWM_LOG_ON`, calls `HWM_LOG_OFF`, closes the fd, and exits.

State and persistence behavior: toggles the kernel wrapper's volatile `Device.log_on` flag. It does not inspect logs or write workload data.

Dependencies and integration: assumes the hwm module is already inserted and exposes `/dev/hwm1`; includes `disk_wrapper_ioctl.h`.

Risks: the current wrapper names the disk `hwm` and `Tester` opens `/dev/hwm`, so `/dev/hwm1` may be stale. Return values from ioctls are ignored. Missing `unistd.h` for `close()` in strict builds.

Test signals: useful as a smoke test only; a stronger test should verify that writes are logged between on/off boundaries.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/testing/log_on_off.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/testing/test_get_log_ent_size.c -->
# sources/test-tools/crashmonkey/code/testing/test_get_log_ent_size.c

Purpose: older standalone test intended to clear logs, write a test file, fsync it, stop logging, and iterate log entries containing metadata plus data.

Important APIs/control flow: opens `/dev/hwm1`, opens `/mnt/snapshot/testing/test_file2`, clears/enables logging, writes `TEXT`, fsyncs, sleeps, disables logging, then calls `HWM_GET_LOG_ENT_SIZE` and `HWM_GET_LOG_ENT` in a loop to print operation flags and data.

State and persistence behavior: mutates a file under `/mnt/snapshot/testing`, relies on wrapper volatile logs, and reads entries until `ENODATA`.

Dependencies and integration: includes `disk_wrapper_ioctl.h`, but references ioctl names not defined in the current header. Assumes an inserted wrapper and mounted snapshot.

Risks: this file is stale relative to the current two-step `HWM_GET_LOG_META`/`HWM_GET_LOG_DATA` ABI. It also loops on `write()` incorrectly by assigning the return value to `written` instead of accumulating bytes, so partial writes can repeat from the wrong offset. It opens created files without an explicit mode argument despite `O_CREAT`, which is undefined/incorrect for POSIX `open()`.

Test signals: as written, compile failure is likely and is itself a compatibility signal. Updating it to the current ABI would make it a useful integration test for log payload extraction.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/testing/test_get_log_ent_size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/BaseTestCase.cpp -->
# sources/test-tools/crashmonkey/code/tests/BaseTestCase.cpp

Purpose: implements common initialization and tracked workload execution for dynamically loaded CrashMonkey test cases.

Important APIs/functions: `init_values()` stores mount directory and filesystem size. `Run()` selects recording wrappers for checkpoint `0` and passthrough wrappers for later checkpoint-specific reruns, calls the subclass `run(checkpoint)`, and serializes recorded filesystem modifications to `change_fd` on the full run.

Control flow and state: during the first workload execution, `cm_` points to `RecordCmFsOps`, so user-tool operations are recorded. During checkpoint reruns, `cm_` points to `PassthroughCmFsOps`, avoiding duplicate modification logging. Subclasses call `cm_` or direct POSIX APIs in `run()`.

Dependencies and integration: depends on `user_tools/api/wrapper.h` types `DefaultFsFns`, `RecordCmFsOps`, and `PassthroughCmFsOps`. `Tester::test_run()` calls `Run()`.

Risks: `cm_` points to stack objects inside `Run()`, so subclasses must not retain it after `run()` returns. Direct calls to global helpers like `Checkpoint()` bypass `cm_` and may not be recorded consistently. Serialization is skipped for checkpoint reruns by design.

Test signals: a mock subclass can verify that checkpoint `0` serializes changes and checkpoint `>0` does not.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/BaseTestCase.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/BaseTestCase.h -->
# sources/test-tools/crashmonkey/code/tests/BaseTestCase.h

Purpose: declares the abstract interface all dynamically loaded CrashMonkey test cases implement.

Important APIs/types: subclasses implement `setup()`, `run(checkpoint)`, and `check_test(last_checkpoint, DataTestResult*)`. `Run()` is the non-virtual wrapper around `run()`. `init_values()` injects mount dir and filesystem size. Factory typedefs define shared-object symbols.

Control flow and integration: `ClassLoader` loads `test_case_get_instance` and `test_case_delete_instance`; `c_harness.cpp` invokes setup/run/check through `Tester`.

State: protected `mnt_dir_`, `filesys_size_`, and `cm_` are available to tests.

Risks: raw pointer `cm_` has temporary lifetime during `Run()`. The interface mixes direct POSIX tests and user-tool-recorded tests, so test authors must understand when to use `cm_`.

Test signals: every `.so` test must export the factory symbols and behave correctly for checkpoint `0` plus checkpoint-specific reruns.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/BaseTestCase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/ace-base/base.cpp -->
# sources/test-tools/crashmonkey/code/tests/ace-base/base.cpp

Purpose: appears to be a template/stub C++ CrashMonkey test case for ACE-generated workloads.

Important APIs/control flow: defines a `testName` class deriving from `BaseTestCase` with empty `setup()` and `run()` implementations. It includes typical workload/action headers and imports common helper names.

State and persistence behavior: no meaningful state mutations are performed in the visible file; it is a scaffold.

Dependencies and integration: intended to compile as a test shared object after generated code fills in `check_test()` and factory symbols, though the visible snippet is incomplete/truncated at `check_test`.

Risks: as a base template, it is not a useful standalone test. If compiled directly in its current state, the incomplete method/body would fail. It includes broad headers and hard-coded permission macros used by generated tests.

Test signals: generated descendants should be validated after template expansion, not by this stub alone.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/ace-base/base.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/ace-base/base_xfstest.sh -->
# sources/test-tools/crashmonkey/code/tests/ace-base/base_xfstest.sh

Purpose: shell template for generating xfstests-style crash-consistency tests using dm-flakey and common output normalization helpers.

Important APIs/functions: initializes xfstests environment, requires scratch device and dm-flakey, creates a 256 MiB scratch filesystem, defines `rename()`, `general_stat()`, `_dwrite_byte()`, `_mwrite_byte_and_msync()`, `check_consistency()`, and `clean_dir()`, then exits with "Silence is golden".

Control flow: setup validates filesystem/OS, formats scratch, initializes flakey target, defines helper functions, and currently performs no test cases before successful exit.

State and persistence behavior: intended generated tests would mutate `$SCRATCH_MNT`, drop/remount via flakey, and compare before/after stats. This template cleans temporary files and flakey state in a trap.

Dependencies: xfstests `common/rc`, `common/filter`, `common/dmflakey`, `$XFS_IO_PROG`, scratch device environment, and dm-flakey kernel target.

Risks: destructive scratch-device operations; helper `rename()` shadows a common command name; unquoted paths in places; `clean_dir()` uses `rm -rf $(find ...)`, which is whitespace-sensitive. As-is, it is a no-op success template rather than a behavioral test.

Test signals: generated tests should be silent on success and print before/after diffs on inconsistency.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/ace-base/base_xfstest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/ace-base/base_xfstest_concise.sh -->
# sources/test-tools/crashmonkey/code/tests/ace-base/base_xfstest_concise.sh

Purpose: extended xfstests shell template with additional concise helpers for fallocate/fzero/fpunch/fsync consistency cases.

Important APIs/functions: includes all base xfstest helpers plus `ensure_file_size_one_block()`, `translate_range()`, `do_falloc()`, and `do_fsync_check()`. These map symbolic ranges/modes into `xfs_io` fallocate/fzero/fpunch commands and consistency checks.

Control flow: after standard scratch/flakey setup, helper definitions are loaded and the script currently exits successfully without generated test cases.

State and persistence behavior: intended generated tests would mutate files under `$SCRATCH_MNT`, use dm-flakey drop/remount, and compare data/metadata with `general_stat`.

Dependencies: xfstests framework, dm-flakey, `$XFS_IO_PROG`, stat/od/coreutils, and scratch-device variables.

Risks: `[[ size -lt 4192 ]]` omits `$` and likely tests a literal string, so `ensure_file_size_one_block()` is broken. Unquoted variables and `rm -rf $(find ...)` are whitespace-sensitive. `translate_range()` sets `length` to `offset + 32768` for append, which may be intended as a length but reads like an end offset.

Test signals: generated fallocate/fsync tests should produce no output on success and before/after detail on mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/ace-base/base_xfstest_concise.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/btrfs_inode_eexist.cpp -->
# sources/test-tools/crashmonkey/code/tests/btrfs_inode_eexist.cpp

Purpose: reproduces a Btrfs fsync-log replay bug where creating a new file after recovery can fail with `EEXIST` due to reused object IDs.

Important APIs/control flow: `setup()` creates `test_dir_a` and syncs. `run()` creates `foo`, fsyncs it through `cm_->CmFsync()`, creates a checkpoint through `cm_->CmCheckpoint()`, and optionally exits at checkpoint 1. `check_test()` attempts to create `bar`; `EEXIST` is reported as `kFileMetadataCorrupted`.

State and persistence behavior: the test persists a directory baseline, then relies on the fsync log for `foo` and crash replay at checkpoint 1. Correct recovery should allow creation of a new `bar`.

Dependencies: `BaseTestCase`, user-tool API wrappers, POSIX file APIs, Btrfs behavior, and the harness checkpoint mechanism.

Risks: path construction uses adjacent string literals in `mnt_dir_ + "/" TEST_DIR_A`, which is valid but easy to misread. If `open()` fails for reasons other than `EEXIST`, the code closes `fd_bar` even when negative and returns success without setting an error. The test only checks one post-recovery symptom.

Test signals: failure is a data-test metadata corruption with description "Cannot create new file bar : EEXIST error"; mount/fsck failures are caught by the harness.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/btrfs_inode_eexist.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/btrfs_link_unlink.cpp -->
# sources/test-tools/crashmonkey/code/tests/btrfs_link_unlink.cpp

Purpose: reproduces a Btrfs 4.16 bug where unlinking and recreating a hard-link name followed by fsync can leave the filesystem unmountable after crash.

Important APIs/control flow: `setup()` creates directory `A`, file `foo`, hard link `bar`, syncs, and closes `foo`. `run()` unlinks `bar`, recreates it as a new file, fsyncs `bar`, checkpoints, and optionally exits at checkpoint 1. `check_test()` returns clean and relies on harness fsck/mount results.

State and persistence behavior: baseline has two links to `foo`; workload changes `bar` from hard link to separate file and fsyncs it. Crash-state correctness is primarily filesystem mountability/consistency.

Dependencies: POSIX `link`, `unlink`, `open`, `fsync`, global `Checkpoint()`, Btrfs recovery behavior, and `BaseTestCase`.

Risks: uses direct POSIX and global `Checkpoint()` rather than `cm_` wrappers, so user-tool modification recording may be less complete. `fd_bar` is not closed before returning checkpoint `1`. No custom data validation checks link counts or file identity after recovery.

Test signals: expected failure appears as kernel mount/fsck failure in `FileSystemTestResult`, not `DataTestResult`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/btrfs_link_unlink.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/btrfs_rename_dev.cpp -->
# sources/test-tools/crashmonkey/code/tests/btrfs_rename_dev.cpp

Purpose: attempts to reproduce a Btrfs log-replay unmountable-filesystem bug involving renaming a device special file and hard-linking it back to the old name.

Important APIs/control flow: `setup()` creates directory `A`, then calls `mknod()` for `foo` with special-file bits, syncs, and returns. `run()` creates and fsyncs a dummy file to populate the log tree, renames `foo` to `bar`, links `bar` back to `foo`, removes the dummy file, fsyncs the dummy fd, checkpoints, and optionally exits.

State and persistence behavior: baseline contains a special file; workload logs rename/link operations in one transaction and uses dummy-file fsync/removal to persist the log tree. Correct behavior is mountable recovery.

Dependencies: root privileges for `mknod`, POSIX rename/link/fsync, Btrfs log-tree behavior, global `Checkpoint()`.

Risks: class name is `BtrfsRenameFifo` despite device-file semantics, suggesting copy/paste confusion. `S_IFCHR | S_IFBLK` combines mutually exclusive file-type bits and may make `mknod()` invalid. The code fsyncs `fd_dummy` after removing the path, which may be intentional but is subtle. No custom check validates recovered namespace.

Test signals: harness mount/fsck failures indicate reproduction; setup can fail early if `mknod()` is not permitted or invalid.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/btrfs_rename_dev.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/btrfs_rename_fifo.cpp -->
# sources/test-tools/crashmonkey/code/tests/btrfs_rename_fifo.cpp

Purpose: reproduces a Btrfs log-replay bug involving a FIFO that is renamed and hard-linked under the old name before crash.

Important APIs/control flow: `setup()` creates directory `A`, creates FIFO `foo` with `mkfifo()`, and syncs. `run()` creates/fsyncs a dummy file, renames `foo` to `bar`, links `bar` to `foo`, removes dummy, fsyncs the dummy fd, checkpoints, and optionally exits. `check_test()` performs no custom validation.

State and persistence behavior: correct behavior is that the replayed filesystem remains mountable/consistent after the logged FIFO rename/link sequence.

Dependencies: POSIX FIFO, rename/link/fsync, global `Checkpoint()`, Btrfs log replay, and harness fsck/mount checks.

Risks: hard-linking a FIFO may behave differently across filesystems and permissions. `fd_dummy` can leak on checkpoint return. The test relies exclusively on filesystem-level signals.

Test signals: failure is expected as mount/fsck/checker error, not data-test error.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/btrfs_rename_fifo.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/btrfs_rename_file.cpp -->
# sources/test-tools/crashmonkey/code/tests/btrfs_rename_file.cpp

Purpose: control-style test for the same rename/link/fsync sequence using a regular file, documented as not expected to fail.

Important APIs/control flow: `setup()` creates directory `A`, creates regular file `foo`, syncs, and closes it. `run()` creates/fsyncs dummy, renames `foo` to `bar`, hard-links `bar` to `foo`, removes dummy, fsyncs dummy fd, checkpoints, and optionally exits.

State and persistence behavior: baseline has a regular file. After replay, the filesystem should remain mountable and consistent; no custom data checks are performed.

Dependencies: POSIX file APIs, global `Checkpoint()`, Btrfs or other filesystem recovery behavior.

Risks: comments refer to "FIFO" in setup despite regular-file code. The test does not validate that both names exist or have expected link counts after recovery. `fd_dummy` can leak on early checkpoint return.

Test signals: successful mount/fsck with no data errors is the expected control signal.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/btrfs_rename_file.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/btrfs_rename_symlink.cpp -->
# sources/test-tools/crashmonkey/code/tests/btrfs_rename_symlink.cpp

Purpose: attempts to reproduce the Btrfs rename/link log-replay bug using a symlink as the original object.

Important APIs/control flow: `setup()` creates directory `A`, creates symlink `foo -> test`, and syncs. `run()` creates/fsyncs dummy, renames `foo` to `bar`, attempts to hard-link `bar` to `foo`, removes dummy, fsyncs dummy fd, checkpoints, and optionally exits.

State and persistence behavior: intended persisted state is a logged symlink rename plus recreation of the old name as a hard link. Correctness is measured by mountability/consistency.

Dependencies: POSIX symlink/rename/link behavior, Btrfs log replay, global `Checkpoint()`, and harness fsck.

Risks: class name is again `BtrfsRenameFifo`, masking the actual case. Hard-linking symlinks may follow or not follow symlinks depending on platform semantics and flags; this test uses plain `link()`. No custom namespace validation is done.

Test signals: reproduction appears through filesystem-level failure; setup/run return codes expose operation failures.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/btrfs_rename_symlink.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/bug1_btrfs_falloc_fsync.cpp -->
# sources/test-tools/crashmonkey/code/tests/bug1_btrfs_falloc_fsync.cpp

Purpose: reproduces a Btrfs fallocate/fsync bug where keep-size allocations or zero ranges beyond EOF are lost after crash despite a subsequent fsync.

Important APIs/control flow: `setup()` creates `/mnt/snapshot/foo`, writes 16 KiB with `WriteData()`, fsyncs, syncs, and closes. `run()` opens `foo` and performs six variants: three `FALLOC_FL_KEEP_SIZE` allocations and three `FALLOC_FL_ZERO_RANGE | FALLOC_FL_KEEP_SIZE` operations at different offsets/lengths. Each variant fsyncs, checkpoints, and can stop at its checkpoint. `check_test()` stats `foo` and compares `st_blocks` against checkpoint-specific thresholds, setting `kIncorrectBlockCount` when blocks are too low.

State and persistence behavior: baseline file size remains 16 KiB, but allocated block count should increase after each beyond-EOF allocation/zero. The test uses block count as the persistence signal, not file size/data bytes.

Dependencies: Linux `fallocate()`, Btrfs behavior, CrashMonkey `Checkpoint()`, `WriteData()`, POSIX stat, and fixed mount path `/mnt/snapshot`.

Risks: expected block thresholds are noted as ext4 counts while comments say other filesystems use slightly different values; this can make cross-filesystem use noisy. `foo_path` ignores injected `mnt_dir_` and hard-codes `/mnt/snapshot`. Checkpoint returns are inconsistent: variants 1-5 return `0`, variant 6 returns `1`, which affects harness last-checkpoint logic. Open fd can leak on checkpoint returns.

Test signals: data-test error `incorrect_block_count` with a checkpoint-specific description indicates the bug. Missing file is reported as `kFileMissing`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/bug1_btrfs_falloc_fsync.cpp -->
