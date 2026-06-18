# subset-b-009209 research

Grouped research report for CrashMonkey C++ workload tests under `sources/test-tools/crashmonkey/code/tests`. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/bug2_f2fs_fzero_fdatasync.cpp -->
# sources/test-tools/crashmonkey/code/tests/bug2_f2fs_fzero_fdatasync.cpp

Purpose: regression workload for an f2fs `FALLOC_FL_ZERO_RANGE | FALLOC_FL_KEEP_SIZE` recovery bug where a post-crash file size incorrectly expands to the zeroed EOF range instead of remaining at the pre-crash 16 KiB size.

Important APIs/types/functions: `F2fsFzero` derives from `BaseTestCase`; it uses `WriteData`, `syncfs`, `fallocate`, `fdatasync`, `Checkpoint`, `stat`, and `DataTestResult::kIncorrectBlockCount`/`kFileMetadataCorrupted`.

Control flow: `setup()` creates `/mnt/snapshot/test_file`, writes 8 KiB at offset 8 KiB so size becomes 16 KiB, then `syncfs()` persists it. `run()` opens the file, zero-ranges 8 KiB at offset 4,202,496 with keep-size, calls `fdatasync()`, checkpoints, and optionally stops at checkpoint 1.

State/persistence behavior: after checkpoint 1 the durable state should include extra allocated blocks but preserve `st_size == 16384`. The test specifically separates logical size from allocated block count.

Dependencies/integration: integrates Linux fallocate flags, f2fs recovery expectations, CrashMonkey checkpoint recording, and the common test plugin entry points.

Risks/test signals: hard-coded `/mnt/snapshot` and expected `st_blocks == 16` baseline can be filesystem/block-size sensitive. Failure is reported when the file is missing, size changes, or block count does not increase after `fdatasync`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/bug2_f2fs_fzero_fdatasync.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/checkpoint_example.cpp -->
# sources/test-tools/crashmonkey/code/tests/checkpoint_example.cpp

Purpose: example CrashMonkey test showing how user checkpoints divide a workload and how `check_test()` interprets the last durable checkpoint. It creates a directory, writes a text file, checkpoints after directory/file persistence, then renames the file.

Important APIs/types/functions: `CheckpointExample`, `BaseTestCase`, `Checkpoint`, POSIX `mkdir`, `open`, `write`, `fsync`, `rename`, `stat`, `read`, and `memcmp`. It reports `kFileMissing`, `kOldFilePersisted`, metadata corruption, and data corruption through `DataTestResult`.

Control flow: `run()` fsyncs the new directory and root, takes checkpoint 1, writes the War and Peace text into `old_file`, fsyncs the file and root, takes checkpoint 2, then renames `old_file` to `new_file`. `check_test()` decides whether to inspect the old or new pathname based on checkpoint reachability.

State/persistence behavior: checkpoint 1 requires the directory to exist; checkpoint 2 requires the file contents, type, and permissions to be durable. The rename is intentionally after checkpoint 2, so recovery may validly show either name unless the checkpoint implies otherwise.

Dependencies/integration: exercises checkpoint accounting, file data validation, directory fsync ordering, and CrashMonkey's replay/oracle split.

Risks/test signals: the test has static `/mnt/snapshot` paths and uses a large UTF-8 string literal. Its strongest signal is detecting missing files, stale old name persistence after rename is expected to have landed, or byte mismatches in recovered content.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/checkpoint_example.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/create_delete.cpp -->
# sources/test-tools/crashmonkey/code/tests/create_delete.cpp

Purpose: creates multiple randomly-filled files in a subdirectory, checkpoints after each create/write, then deletes them with checkpoints after each removal. It is a general crash-consistency oracle for create, fsync, writeback, delete, and cleanup ordering.

Important APIs/types/functions: `create_delete`, `Checkpoint`, `/dev/urandom` reads, `mkdir`, `open`, `write`, `fsync`, `sync`, `remove`, `stat`, and `DataTestResult`. The class stores generated text in a member buffer used by `check_test()`.

Control flow: `setup()` creates and fsyncs the test directory and fills an in-memory random buffer. `run()` creates a fixed sequence of files, fsyncs the new inode, writes the buffer, fsyncs again, and checkpoints. It then removes the same files, calls global `sync()`, and checkpoints after each delete.

State/persistence behavior: before delete checkpoints, each expected file must have the correct regular-file metadata, size, and exact byte contents. After delete checkpoints, old files should no longer remain.

Dependencies/integration: depends on the CrashMonkey snapshot mount and POSIX namespace/data operations; no `cm_` wrapper is used for the main syscalls, so it is closer to a direct workload.

Risks/test signals: random data makes oracle state process-local; rerunning `check_test()` without the same object state would be invalid. Failure modes include missing expected files, corrupt size/mode/data, or old files persisting after deletion.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/create_delete.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/echo_sub_dir.cpp -->
# sources/test-tools/crashmonkey/code/tests/echo_sub_dir.cpp

Purpose: simple file-in-subdirectory persistence test. It creates `test_dir`, writes a small constant text string to `test_dir/foo`, fsyncs the file, and expects the file and data to survive recovery.

Important APIs/types/functions: `echo_sub_dir`, `BaseTestCase`, POSIX `mkdir`, `open`, `write`, `fsync`, `stat`, `read`, and `DataTestResult`.

Control flow: `setup()` creates and fsyncs the directory. `run()` opens the file with `O_RDWR | O_CREAT`, writes the complete `TEXT` string in a loop, calls `fsync(fd)`, then returns success. `check_test()` stats and reads the file.

State/persistence behavior: after the file fsync, the file should be regular, have the expected mode/size, and contain the exact text bytes. The directory is persisted before the workload, so the check is focused on file data and inode metadata.

Dependencies/integration: uses fixed `/mnt/snapshot/test_dir/foo` paths and direct syscalls rather than `cm_` wrappers.

Risks/test signals: because there is no explicit CrashMonkey `Checkpoint()`, the harness records no intermediate user checkpoint; the workload is best as a basic fully-run crash image. Errors are file missing, metadata mismatch, read failure, or byte corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/echo_sub_dir.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/echo_sub_dir_big.cpp -->
# sources/test-tools/crashmonkey/code/tests/echo_sub_dir_big.cpp

Purpose: larger variant of the echo-in-subdirectory test. It writes a sizeable random buffer to one or more files under a pre-synced directory and validates full content persistence after recovery.

Important APIs/types/functions: `echo_sub_dir_big`, `/dev/urandom`, `mkdir`, `open`, `write`, `fsync`, `stat`, `read`, and `DataTestResult`.

Control flow: `setup()` creates and fsyncs `test_dir`, then fills the test buffer from `/dev/urandom`. `run()` creates each target file under the directory, writes the whole buffer, fsyncs the file, and closes it. `check_test()` walks the expected file names and compares recovered contents against the saved random buffer.

State/persistence behavior: the test validates that file size, mode/type, and every byte of a larger buffered write reach durable state after `fsync`. It also covers parent-directory persistence because the directory is fsynced before file creation.

Dependencies/integration: direct POSIX workload with fixed `/mnt/snapshot` paths; uses process memory as the expected-content oracle.

Risks/test signals: random oracle state means the same object instance must perform run and check. The main signals are missing files, wrong size/mode, short reads, and byte mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/echo_sub_dir_big.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/echo_sub_dir_huge.cpp -->
# sources/test-tools/crashmonkey/code/tests/echo_sub_dir_huge.cpp

Purpose: stress-size version of the subdirectory echo workload. It is structured like `echo_sub_dir_big.cpp` but uses a larger `TEST_TEXT_SIZE` to pressure writeback, allocation, and recovery over a bigger file extent set.

Important APIs/types/functions: class name is still `echo_sub_dir_big` in the source, with `BaseTestCase`, `/dev/urandom`, `mkdir`, `open`, `write`, `fsync`, `stat`, `read`, and `DataTestResult`.

Control flow: setup persists the containing directory and fills a random text buffer. `run()` creates target files and writes the full huge buffer before fsync. `check_test()` stats each recovered file and reads it back for byte-for-byte comparison.

State/persistence behavior: the persisted state must include full file length and random content, not just metadata. Larger size increases exposure to delayed allocation, partial writeback, and extent recovery issues.

Dependencies/integration: direct syscall workload using `/mnt/snapshot`; expected bytes are held in the test object's memory.

Risks/test signals: memory and runtime cost are higher than the small echo test. Any partial persistence shows as wrong `st_size`, read failure, or data corruption against the random buffer.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/echo_sub_dir_huge.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/echo_sub_dir_no_sync.cpp -->
# sources/test-tools/crashmonkey/code/tests/echo_sub_dir_no_sync.cpp

Purpose: contrast workload for the synced echo test. It writes the same small file in a synced directory but intentionally omits the file `fsync`, probing what the checker currently assumes for unflushed data.

Important APIs/types/functions: `echo_sub_dir_no_sync`, `mkdir`, directory `fsync`, `open`, `write`, `stat`, `read`, and `DataTestResult`.

Control flow: `setup()` creates and fsyncs `test_dir`. `run()` opens `test_dir/foo`, writes the constant text in a loop, and closes/returns without forcing file data to stable storage. `check_test()` still expects the file to exist with the full size and contents.

State/persistence behavior: only the parent directory is durably established before the file write. The file contents are deliberately not synchronized, so this test is useful for observing filesystem behavior but has a stricter oracle than POSIX crash semantics would normally guarantee.

Dependencies/integration: direct POSIX syscalls and fixed `/mnt/snapshot` paths; no CrashMonkey checkpoint calls.

Risks/test signals: because the file data is not fsynced, failures may be expected on conservative filesystems. Signals remain missing file, metadata mismatch, read failure, or text mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/echo_sub_dir_no_sync.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/example.cpp -->
# sources/test-tools/crashmonkey/code/tests/example.cpp

Purpose: minimal example of a CrashMonkey workload using the `cm_` filesystem wrapper rather than raw syscalls for key operations. It creates `A/foo`, then creates `B`, hard-links `A/foo` into `B/foo`, fsyncs the source file, and checkpoints.

Important APIs/types/functions: `Example`, `BaseTestCase`, `cm_->CmFsync`, `cm_->CmCheckpoint`, raw `mkdir`, `open`, `link`, `sync`, `stat`, and plugin entry points `test_case_get_instance`/`test_case_delete_instance`.

Control flow: `setup()` builds directory `A`, creates `A/foo`, and globally syncs. `run()` creates `B`, creates a hard link from `A/foo` to `B/foo`, fsyncs the original file through the CrashMonkey wrapper, checkpoints, and returns at checkpoint 1. `check_test()` stats both paths.

State/persistence behavior: after the checkpoint, both the original and linked names are expected to resolve to a file. The workload targets link persistence through fsync of one inode.

Dependencies/integration: demonstrates interaction with `RecordCmFsOps`/`PassthroughCmFsOps` selected by `BaseTestCase::Run`.

Risks/test signals: the directory creation and link call are raw syscalls, so only wrapper-covered operations are recorded in the same way as other `cm_` workloads. Missing `A/foo` or `B/foo` is the main signal.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/example.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_002.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_002.cpp

Purpose: CrashMonkey reproduction of xfstests generic/002. It exercises hard-link count durability while creating ten links to `foo` and then removing them, with a checkpoint after every fsync.

Important APIs/types/functions: `Generic002`, `link`, `remove`, `fsync`, `Checkpoint`, `stat`, `st_nlink`, `chmod`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: `setup()` creates `test_dir_a/foo` and syncs. `run()` loops over `foo_link_0` through `foo_link_9`, creates each hard link, fsyncs `foo`, checkpoints, then removes each link with another fsync and checkpoint. Return value 1 marks the final checkpoint.

State/persistence behavior: recovered `st_nlink` should match the number of links implied by `last_checkpoint`, allowing a one-operation delta because the crash may occur after fsync but before the user checkpoint record.

Dependencies/integration: uses `mnt_dir_` from `init_values`, raw POSIX hard-link operations, and CrashMonkey user checkpoints.

Risks/test signals: the oracle subtracts one link for the original file and uses checkpoint arithmetic; off-by-one errors in checkpoint interpretation are the main risk. Failure means recovered link count is outside the allowed range.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_002.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_034.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_034.cpp

Purpose: reproduction of xfstests generic/034 for a btrfs directory-log replay bug. After creating `foo`, creating and fsyncing `bar`, and fsyncing the parent directory, recovered directory state should be removable after deleting entries.

Important APIs/types/functions: `Generic034`, `mkdir`, `open`, `fsync` on directory and file descriptors, `Checkpoint`, `remove`, `rmdir`, `errno == ENOTEMPTY`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: `setup()` creates `test_dir_a/foo` and syncs. `run()` creates `bar`, opens `test_dir_a`, fsyncs the directory, fsyncs `bar`, then checkpoints. `check_test()` removes `foo` and `bar` if present, then attempts to remove the directory.

State/persistence behavior: the expected durable state must not leave stale directory index/i_size information. Even if files are present and removable, `rmdir(test_dir_a)` must succeed once entries are deleted.

Dependencies/integration: fixed `/mnt/snapshot` paths, raw syscalls, and btrfs-inspired log replay semantics.

Risks/test signals: the check mutates recovered state while validating it. Failure signal is `rmdir` returning `ENOTEMPTY` after cleanup, meaning directory metadata is inconsistent.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_034.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_035_1.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_035_1.cpp

Purpose: file rename variant of xfstests generic/035. It renames one file over another in the same directory and fsyncs the destination name, then checks that directory metadata is clean after removing the surviving file.

Important APIs/types/functions: source class is named `Generic321_1`; it uses `mkdir`, `open`, `rename`, `fstat`, `fsync`, `Checkpoint`, `remove`, `rmdir`, and `DataTestResult`.

Control flow: `setup()` creates a directory and two files, then syncs. `run()` opens the original destination, renames `file1` over `file2`, uses `fstat` for sanity, reopens/fsyncs `file2`, and checkpoints. `check_test()` removes `file2` and expects `rmdir` of the parent to succeed.

State/persistence behavior: the renamed-over entry should not leave stale directory state or hidden references after recovery. Persistence focus is namespace replacement and destination inode logging.

Dependencies/integration: direct POSIX rename/fsync workload with `/mnt/snapshot`-derived paths.

Risks/test signals: class naming is misleading because it says `Generic321_1`. The primary signal is inability to remove an apparently empty directory, reported as metadata corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_035_1.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_035_2.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_035_2.cpp

Purpose: directory rename variant of xfstests generic/035. It renames one child directory over another and fsyncs the destination directory to catch stale directory-entry replay issues.

Important APIs/types/functions: source class is named `Generic321_2`; it uses `mkdir`, `open(..., O_DIRECTORY)`, `rename`, `fstat`, `fsync`, `Checkpoint`, `rmdir`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: `setup()` creates a parent plus two child directories and syncs. `run()` opens the destination directory, renames the first child to the destination path, checks the open fd with `fstat`, reopens/fsyncs the destination directory, and checkpoints. `check_test()` removes the destination and then the parent.

State/persistence behavior: after replay, there should be exactly one child directory and no stale references that keep the parent non-empty after cleanup.

Dependencies/integration: raw Linux directory rename and fsync semantics.

Risks/test signals: overwriting directories is filesystem-sensitive and can fail if directories are not empty. The check focuses on `rmdir` cleanup rather than enumerating all names.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_035_2.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_037.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_037.cpp

Purpose: xattr persistence workload based on xfstests generic/037. It verifies that an extended attribute set on a file remains available with the expected value after crash recovery and checkpointed fsync.

Important APIs/types/functions: `Generic037`, xattr headers selected by `NEW_XATTR_INC`, `fsetxattr`/`getxattr`, `open`, `fsync`, `Checkpoint`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: setup creates `foo` and syncs. The run path sets an xattr value, fsyncs the file, checkpoints, and returns. The checker reads the attribute and compares it against the expected `val1` value.

State/persistence behavior: attribute name/value metadata is the durable state under test. The file itself is pre-created, so the interesting persistence boundary is xattr logging during file fsync.

Dependencies/integration: depends on user xattr support and either `<sys/xattr.h>` or `<attr/xattr.h>`.

Risks/test signals: the workload can be skipped or fail on filesystems/mounts without user xattrs. Signal is missing or mismatched recovered xattr.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_037.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_039.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_039.cpp

Purpose: btrfs-inspired reproduction of generic/039. It creates a hard link, syncs, removes the link, fsyncs the remaining file, and expects the containing directory to be removable after cleanup.

Important APIs/types/functions: `Generic039`, `link`, `remove`, `fsync`, `Checkpoint`, `rmdir`, optional `btrfs check` via `popen`, and `DataTestResult`.

Control flow: `setup()` creates `test_dir_a` and syncs. `run()` creates `foo`, hard-links `bar`, syncs all state, removes `bar`, fsyncs `foo`, and checkpoints. `check_test()` chmods paths, removes directory entries with `rm -f`, attempts `rmdir`, and if needed runs `btrfs check` against `/dev/cow_ram_snapshot1_0`.

State/persistence behavior: the deleted hard-link directory entry must not reappear as stale metadata during log replay. Directory i_size/index state must match actual entries.

Dependencies/integration: fixed btrfs tooling/device path is used only for enhanced diagnostics after failure.

Risks/test signals: the check is destructive and btrfs-specific diagnostics may not exist. Failure is `ENOTEMPTY` after deleting all visible files.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_039.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_041.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_041.cpp

Purpose: xfstests generic/041 reproduction for btrfs hard-link/extref replay. It creates thousands of hard links, mutates link names, fsyncs the inode, and checks directory cleanup after crash recovery.

Important APIs/types/functions: `Generic041`, `link`, `remove`, `fsync`, `Checkpoint`, `rmdir`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: `setup()` creates `test_dir_a/foo`, creates links `foo_link_0` through `foo_link_2999`, syncs, and closes. `run()` removes `foo_link_0`, creates `foo_link_3000`, recreates `foo_link_0`, fsyncs `foo`, and checkpoints. `check_test()` removes all entries and attempts `rmdir`.

State/persistence behavior: durable inode reference tracking must survive conversion between regular refs and extended refs. Replay must not leave unremovable stale link metadata.

Dependencies/integration: direct POSIX workload with a high link count; relies on filesystem hard-link limits and btrfs historical behavior for motivation.

Risks/test signals: setup is expensive and may exceed link-count limits on some filesystems. The signal is directory cleanup failure after all visible entries are removed.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_041.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_base.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_base.cpp

Purpose: shared implementation for the generic/042 fallocate, punch-hole, and zero-range workloads. It creates a stale-data-sensitive environment, runs one parameterized fallocate operation, and provides reusable data-oracle helpers.

Important APIs/types/functions: `Generic042Base::setup`, `run`, `CheckBase`, `CheckDataNoZeros`, `CheckDataWithZeros`, `ReadData`, `HexdumpFile`, `WriteData`, `fallocate`, `fsync`, `Checkpoint`, and `DataTestResult`.

Control flow: `setup()` fills the filesystem by repeatedly writing 4 KiB chunks until `ENOSPC`, syncs, unlinks the filler file, syncs again, and creates an empty `foo`. `run()` writes `start_file_size_` bytes of `0xff`, applies `fallocate(fd, falloc_mode_, falloc_offset_, falloc_len_)`, fsyncs, checkpoints, and closes.

State/persistence behavior: recovered `foo` is allowed to be empty if the checkpoint did not fully replay, or full-sized with expected data once replay is complete. Derived classes decide whether the fallocated range should remain `0xff` or become zeros.

Dependencies/integration: integrates the base CrashMonkey lifecycle with Linux allocation flags and helper APIs from `user_tools/api/workload.h` and `actions.h`.

Risks/test signals: setup intentionally fills the filesystem, so capacity and ENOSPC behavior matter. `ReadData()` assumes reads make progress; unexpected short EOF behavior could loop. Failures include partial file size and stale data or missing zeros with hexdump diagnostics.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_base.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_base.h -->
# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_base.h

Purpose: declaration for the generic/042 shared base class. It defines the constructor parameters and protected verification helpers used by all fallocate/zero/punch subclasses.

Important APIs/types/functions: `Generic042Base` inherits `BaseTestCase`; declares `setup()`, `run(int checkpoint)`, pure virtual `check_test`, constructor `(start_file_size, falloc_offset, falloc_len, mode)`, and helpers `CheckBase`, `CheckDataNoZeros`, `CheckDataWithZeros`, `ReadData`, and `HexdumpFile`.

Control flow: the header enforces a template method shape: subclasses only supply `check_test()` and constructor constants while the base handles setup and run.

State/persistence behavior: stores immutable `start_file_size_`, `falloc_offset_`, `falloc_len_`, and `falloc_mode_` used for workload state and recovery checks.

Dependencies/integration: includes `../BaseTestCase.h` and `cstdint`; exposes helper methods to derived source files in the same directory.

Risks/test signals: because `check_test()` remains pure virtual, each derived workload must choose the correct zero/nonzero expectations. A mismatch in constructor constants directly changes the persistence oracle.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate.cpp

Purpose: aligned plain `fallocate` variant of generic/042. It verifies that prewritten file data remains `0xff` after allocating an already-covered aligned range without zeroing or punching.

Important APIs/types/functions: `Generic042Fallocate`, `Generic042Base(64 KiB, 60 KiB, 4 KiB, 0)`, `CheckBase`, and `CheckDataNoZeros`.

Control flow: the inherited run writes 64 KiB, calls `fallocate` with mode `0` at offset 60 KiB for 4 KiB, fsyncs, and checkpoints. `check_test()` first accepts empty-or-complete state via `CheckBase`; if complete, it checks the full 64 KiB for `0xff`.

State/persistence behavior: no zeros should be introduced, and file size should remain 64 KiB when the checkpoint has replayed.

Dependencies/integration: thin plugin wrapper around `Generic042Base` plus CrashMonkey factory functions.

Risks/test signals: detects stale or zeroed data in the full data range, but not block count changes. Signal is `kFileDataCorrupted` from base helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate_keep_size.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate_keep_size.cpp

Purpose: aligned `FALLOC_FL_KEEP_SIZE` allocation variant. It ensures keep-size allocation does not alter existing data bytes in the written file.

Important APIs/types/functions: `Generic042FallocateKeepSize`, `Generic042Base(64 KiB, 60 KiB, 4 KiB, FALLOC_FL_KEEP_SIZE)`, `CheckBase`, and `CheckDataNoZeros`.

Control flow: inherited setup/run create the stale-data environment, write 64 KiB of `0xff`, call keep-size fallocate in the final 4 KiB, fsync, and checkpoint. `check_test()` validates base size state and the full file data.

State/persistence behavior: since the fallocate range is inside the existing file, logical size remains 64 KiB and every byte should still be `0xff`.

Dependencies/integration: relies on Linux fallocate keep-size semantics and base helper validation.

Risks/test signals: this is not checking unwritten extent exposure outside EOF; it is an in-file no-data-change oracle. Any zero/stale mismatch is reported through base data corruption diagnostics.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate_keep_size.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate_keep_size_unaligned.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate_keep_size_unaligned.cpp

Purpose: unaligned keep-size allocation variant of generic/042. It stresses allocation/recovery when the file size and fallocate offset are not block-aligned to the same 64 KiB boundary as the simpler case.

Important APIs/types/functions: `Generic042FallocateKeepSizeUnaligned`, `Generic042Base(65 KiB, 60 KiB + 128, 4 KiB, FALLOC_FL_KEEP_SIZE)`, `CheckBase`, and `CheckDataNoZeros`.

Control flow: base run writes 65 KiB of `0xff`, applies keep-size fallocate at an offset 128 bytes past 60 KiB, fsyncs, and checkpoints. The checker validates complete base state and then verifies all 65 KiB remain nonzero `0xff`.

State/persistence behavior: unaligned allocation must not corrupt surrounding file data or truncate/extend the visible file beyond the written size.

Dependencies/integration: uses the generic/042 base and Linux fallocate flags.

Risks/test signals: useful for boundary bugs around partial blocks. Failure is any byte not equal to `0xff` or a partial-size recovered file.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate_keep_size_unaligned.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate_unaligned.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate_unaligned.cpp

Purpose: unaligned plain fallocate variant. It checks that allocation of an unaligned in-file range does not expose stale data or zero data over the already written `0xff` content.

Important APIs/types/functions: `Generic042FallocateUnaligned`, `Generic042Base(65 KiB, 60 KiB + 128, 4 KiB, 0)`, `CheckBase`, and `CheckDataNoZeros`.

Control flow: inherited setup fills/frees the filesystem, inherited run writes 65 KiB, fallocates the unaligned range, fsyncs, and checkpoints. `check_test()` requires a complete recovered file to contain only `0xff` over the full written size.

State/persistence behavior: fallocate should be a metadata allocation operation here; it must not rewrite user-visible data bytes.

Dependencies/integration: generic/042 framework and Linux fallocate.

Risks/test signals: only content/size are checked, not extent layout. A failure indicates partial file recovery or data mismatch in the full range.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate_unaligned.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fpunch_keep_size.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fpunch_keep_size.cpp

Purpose: aligned punch-hole keep-size variant of generic/042. It verifies that a punched 4 KiB region becomes zero while surrounding file data remains `0xff`.

Important APIs/types/functions: `Generic042FpunchKeepSize`, `Generic042Base(64 KiB, 60 KiB, 4 KiB, FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)`, `CheckBase`, `CheckDataNoZeros`, and `CheckDataWithZeros`.

Control flow: base run writes 64 KiB, punches 4 KiB at offset 60 KiB, fsyncs, and checkpoints. `check_test()` validates the base state, checks bytes before the punched range for `0xff`, checks the punched range for zeros, then checks remaining bytes after the range.

State/persistence behavior: file size remains 64 KiB, but the hole reads as zeros. No stale pre-fill data should leak in the punched range.

Dependencies/integration: Linux hole punching semantics and base read/hexdump diagnostics.

Risks/test signals: catches both lost punch operations and over-broad zeroing of adjacent data.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fpunch_keep_size.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fpunch_keep_size_unaligned.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fpunch_keep_size_unaligned.cpp

Purpose: unaligned punch-hole keep-size variant. It stresses partial-block hole punching and recovery without permitting stale data leakage.

Important APIs/types/functions: `Generic042FpunchKeepSizeUnaligned`, `Generic042Base(65 KiB, 60 KiB + 128, 4 KiB, FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)`, `CheckDataNoZeros`, and `CheckDataWithZeros`.

Control flow: base writes 65 KiB of `0xff`, punches an unaligned 4 KiB range, fsyncs, and checkpoints. The checker validates complete state, `0xff` before the range, zeros across the range, and `0xff` after it.

State/persistence behavior: hole punching should affect only the selected range. Unaligned offsets make this a stronger check for edge zeroing and stale extent replay.

Dependencies/integration: generic/042 base class, Linux fallocate punch flags, and CrashMonkey checkpointing.

Risks/test signals: range math is central; a wrong offset or length would make the oracle misleading. Failure appears as stale bytes in the hole or corrupted adjacent bytes.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fpunch_keep_size_unaligned.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero.cpp

Purpose: aligned zero-range variant. It verifies that `FALLOC_FL_ZERO_RANGE` zeros the selected in-file extent and leaves surrounding data unchanged after crash recovery.

Important APIs/types/functions: `Generic042Fzero`, `Generic042Base(64 KiB, 60 KiB, 4 KiB, FALLOC_FL_ZERO_RANGE)`, `CheckBase`, `CheckDataNoZeros`, and `CheckDataWithZeros`.

Control flow: base run writes `0xff` data, zero-ranges the final 4 KiB, fsyncs, and checkpoints. `check_test()` accepts empty pre-replay state, otherwise checks nonzero prefix, zeroed range, and nonzero suffix.

State/persistence behavior: after checkpoint replay, the zero-range operation must be durable as zeros, not stale preexisting data or the original `0xff` bytes.

Dependencies/integration: generic/042 stale-block setup and Linux zero-range fallocate.

Risks/test signals: suffix length may be zero in the aligned final-range case; helpers still encode the expected byte classes. Failure is stale data leakage or incorrect zeroing.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero_keep_size.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero_keep_size.cpp

Purpose: aligned zero-range keep-size variant. It checks that keep-size zeroing of an in-file range persists zeros without changing logical file size.

Important APIs/types/functions: `Generic042FzeroKeepSize`, `Generic042Base(64 KiB, 60 KiB, 4 KiB, FALLOC_FL_ZERO_RANGE | FALLOC_FL_KEEP_SIZE)`, `CheckBase`, `CheckDataNoZeros`, and `CheckDataWithZeros`.

Control flow: the inherited workload writes 64 KiB, zero-ranges the last 4 KiB with keep-size, fsyncs, and checkpoints. The checker validates complete file state and byte classes around the zeroed range.

State/persistence behavior: file size should remain at `start_file_size_`, the selected range should read zeros, and nonselected bytes should remain `0xff`.

Dependencies/integration: shared generic/042 base and Linux fallocate semantics.

Risks/test signals: this is the generic counterpart to keep-size EOF bugs; it catches both missing zeroing and accidental size/data corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero_keep_size.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero_keep_size_unaligned.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero_keep_size_unaligned.cpp

Purpose: unaligned keep-size zero-range variant. It targets partial-block zeroing behavior with crash recovery.

Important APIs/types/functions: `Generic042FzeroKeepSizeUnaligned`, `Generic042Base(65 KiB, 60 KiB + 128, 4 KiB, FALLOC_FL_ZERO_RANGE | FALLOC_FL_KEEP_SIZE)`, `CheckBase`, `CheckDataNoZeros`, and `CheckDataWithZeros`.

Control flow: base setup/run write 65 KiB, zero an unaligned 4 KiB range with keep-size, fsync, and checkpoint. The check validates size, nonzero prefix, zeroed range, and nonzero suffix.

State/persistence behavior: the zero range must be persisted exactly, and keep-size must preserve logical length despite unaligned extent boundaries.

Dependencies/integration: generic/042 base, Linux fallocate flags, and CrashMonkey's checkpoint harness.

Risks/test signals: sensitive to filesystem support for unaligned zero-range. The oracle reports stale leaked bytes, over-zeroed surrounding data, or partial-size files.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero_keep_size_unaligned.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero_unaligned.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero_unaligned.cpp

Purpose: unaligned zero-range variant without keep-size. It stresses whether crash replay correctly records zeroing of a non-block-aligned in-file extent.

Important APIs/types/functions: `Generic042FzeroUnaligned`, `Generic042Base(65 KiB, 60 KiB + 128, 4 KiB, FALLOC_FL_ZERO_RANGE)`, `CheckBase`, `CheckDataNoZeros`, and `CheckDataWithZeros`.

Control flow: inherited code writes the file, performs the zero-range operation, fsyncs, checkpoints, and the derived checker verifies byte classes around the requested range.

State/persistence behavior: since the range lies inside the initial 65 KiB, size should remain complete and only the requested 4 KiB should become zeros.

Dependencies/integration: shared base class, Linux allocation APIs, and CrashMonkey plugin factory.

Risks/test signals: detects stale disk contents in zeroed ranges and unintended corruption in adjacent data.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero_unaligned.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_056.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_056.cpp

Purpose: xfstests generic/056 reproduction. It ensures data fsynced to `foo` remains durable even after later namespace changes involving a hard link and another file.

Important APIs/types/functions: `Generic056`, `WriteData`, `fsync`, `Checkpoint`, `link`, `open`, `md5sum` via `popen`, and `DataTestResult::kFileDataCorrupted`.

Control flow: `setup()` creates `test_dir_a/foo`, creates `foo_backup` with the expected 4 KiB data, syncs, and closes. `run()` writes 4 KiB to `foo`, fsyncs it, checkpoints, creates a hard link, creates/fsyncs `bar`, and checkpoints again. `check_test()` verifies `foo` exists and, after checkpoint 1, matches `foo_backup` by md5.

State/persistence behavior: the first checkpoint establishes durable file data for `foo`; later link and `bar` operations must not invalidate or hide that data.

Dependencies/integration: uses `mnt_dir_` paths, external `md5sum`, and CrashMonkey checkpoints.

Risks/test signals: external command parsing is brittle. Failure is missing `foo` or checksum mismatch after a checkpoint that should have persisted data.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_056.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_059.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_059.cpp

Purpose: btrfs generic/059 punch-hole regression. It writes and fsyncs a 16 KiB file, punches a 4 KiB hole, fsyncs again, and expects the hole to be visible after recovery.

Important APIs/types/functions: `Generic059`, `WriteData`, `fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)`, `fsync`, `Checkpoint`, `fread`, `strlen`, `memcmp`, and `DataTestResult`.

Control flow: `setup()` creates `foo`, writes 16 KiB, fsyncs, stores the original bytes in `text`, syncs, and closes. `run()` punches 4 KiB at offset 8000, fsyncs, and checkpoints. `check_test()` reads 16 KiB and verifies the content differs from the original full-data state after checkpoint 1.

State/persistence behavior: the punched region should read as zeros after the second fsync. Seeing the original full buffer implies the punch-hole operation was lost.

Dependencies/integration: fixed `/mnt/snapshot/foo`, Linux fallocate punch flags, and CrashMonkey checkpointing.

Risks/test signals: using `strlen` on binary-ish data can be imprecise because punched holes introduce NULs by design. The robust signal is `memcmp` still matching the original buffer.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_059.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_066.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_066.cpp

Purpose: btrfs generic/066 xattr deletion regression. It creates three user xattrs, removes the second, fsyncs the file, and checks the deleted xattr does not reappear after recovery.

Important APIs/types/functions: `Generic066`, `fsetxattr`, `removexattr`, `getxattr`, `fsync`, `Checkpoint`, conditional xattr include, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: `setup()` creates `foo`, sets `user.xattr1`, `user.xattr2`, and `user.xattr3`, syncs, and closes. `run()` removes `user.xattr2`, fsyncs `foo`, and checkpoints. `check_test()` attempts to read `user.xattr2`; if it is still present with `val2` after checkpoint 1, it reports corruption.

State/persistence behavior: xattr deletion must be durably logged by file fsync, while other attrs are not explicitly checked.

Dependencies/integration: requires user xattr support and proper include path selection for kernel/libc versions.

Risks/test signals: only the removed xattr is checked; loss of xattr1/xattr3 would not be detected. Signal is deleted xattr resurrection.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_066.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_090.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_090.cpp

Purpose: xfstests generic/090 reproduction for append persistence with hard links. It ensures appended data fsynced after link creation survives crash recovery.

Important APIs/types/functions: `Generic090`, `WriteData`, `fsync`, `sync`, `link`, `Checkpoint`, `md5sum` via `popen`, and `DataTestResult`.

Control flow: `setup()` creates a 64 KiB `foo_backup` expected image. `run()` creates `foo`, writes 32 KiB and fsyncs it, syncs, creates a hard link, syncs again, appends/writes another 32 KiB at offset 32768, fsyncs, and checkpoints. `check_test()` compares `foo` against `foo_backup` when checkpoint 1 is reached.

State/persistence behavior: the final durable file should include both initial and appended extents despite the inode having an extra hard link.

Dependencies/integration: `mnt_dir_` paths, external `md5sum`, raw hard-link and fsync semantics.

Risks/test signals: the test assumes `WriteData` produces the same data pattern for `foo` and backup. Failure is missing file or checksum mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_090.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_104.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_104.cpp

Purpose: xfstests generic/104 reproduction. It creates `foo` and `bar`, adds hard links to both, fsyncs `bar`, and expects directory metadata to be clean enough for removal after recovery cleanup.

Important APIs/types/functions: `Generic104`, `link`, `open`, `fsync`, `Checkpoint`, `system("rm -f ...")`, `rmdir`, `errno`, and `DataTestResult`.

Control flow: `setup()` creates `test_dir_a/foo` and `bar`, closes them, and syncs. `run()` creates `foo_link_` and `bar_link_`, opens/fsyncs `bar`, and checkpoints. `check_test()` removes all visible entries in the directory and expects `rmdir` to succeed.

State/persistence behavior: link-count and directory-entry replay must not leave hidden references or stale index entries after cleanup.

Dependencies/integration: direct POSIX operations and CrashMonkey checkpointing; uses external shell `rm`.

Risks/test signals: the checker does not validate exact link counts, only cleanup consistency. Failure is `ENOTEMPTY` on directory removal.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_104.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_106.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_106.cpp

Purpose: xfstests generic/106 reproduction. It validates that unlinking a hard link, dropping caches, and fsyncing the remaining file does not leave stale unremovable directory entries.

Important APIs/types/functions: `Generic106`, `link`, `unlink`, `system("echo 2 > /proc/sys/vm/drop_caches")`, `open`, `fsync`, `Checkpoint`, `rmdir`, and `DataTestResult`.

Control flow: `setup()` creates `test_dir_a/foo` and syncs. `run()` creates `foo_link_`, syncs, unlinks the link, drops caches, opens/fsyncs `foo`, and checkpoints. `check_test()` removes directory contents and attempts to remove the directory.

State/persistence behavior: after checkpoint 1 the removed link should not survive as stale metadata, and deleting `foo` should make the directory empty.

Dependencies/integration: requires permission to write `/proc/sys/vm/drop_caches` in the test environment.

Risks/test signals: drop-caches command may fail outside privileged runs. The main failure signal is an unremovable directory after cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_106.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_177.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_177.cpp

Purpose: xfstests generic/177 reproduction for multiple overlapping hole punches. It checks that a sequence of punched ranges persists exactly after fsync and crash recovery.

Important APIs/types/functions: `Generic177`, `WriteData`, `fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)`, `fsync`, `Checkpoint`, `md5sum`, and `DataTestResult`.

Control flow: `setup()` builds `foo_backup` by writing 128 KiB, syncing, applying three hole punches, syncing, and closing. `run()` creates `foo`, writes 128 KiB, fsyncs, applies the same three hole punches, fsyncs again, and checkpoints. `check_test()` compares `foo` to `foo_backup` by md5 after checkpoint 1.

State/persistence behavior: durable state should include holes at 96-128 KiB, 64-192 KiB, and roughly 32-128 KiB according to the source offsets, with unchanged data elsewhere.

Dependencies/integration: Linux fallocate punch support and external `md5sum`.

Risks/test signals: one offset is `32786`, not a clean 32 KiB boundary, which may be intentional or a typo; it changes the exact expected image. Failure is checksum mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_177.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_321.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_321.cpp

Purpose: one copy of the xfstests generic/321 rename test. It creates `foo` at the mount root, creates directory `test_dir_a`, moves `foo` into that directory, fsyncs the directory/file, and expects the namespace to reflect the move after recovery.

Important APIs/types/functions: class name is `Generic321_2`; it uses `open`, `mkdir`, `fsync`, `rename`, `Checkpoint`, `opendir`/`readdir`, `stat`, and `DataTestResult`.

Control flow: setup creates the root file and target directory, fsyncs the file, and syncs. Run renames `foo` to `test_dir_a/foo`, fsyncs the destination directory and file, and checkpoints. Check enumerates root and `test_dir_a` to ensure the root only has the directory and the directory contains `foo`.

State/persistence behavior: old root name must disappear and new directory entry must be durable after checkpoint 1.

Dependencies/integration: direct POSIX namespace operations and CrashMonkey checkpointing.

Risks/test signals: this file duplicates much of `generic_321_2.cpp`. Signal is missing moved file, old file persistence, or unexpected directory contents.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_321.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_321_1.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_321_1.cpp

Purpose: directory creation subtest from xfstests generic/321. It verifies that a newly created directory survives recovery after the directory itself is fsynced.

Important APIs/types/functions: `Generic321_1`, `mkdir`, `open(..., O_DIRECTORY)`, `fsync`, `Checkpoint`, `stat`, and `DataTestResult`.

Control flow: `setup()` does nothing. `run()` creates `test_dir_a`, opens it as a directory, fsyncs it, checkpoints, and returns at checkpoint 1. `check_test()` validates the directory exists.

State/persistence behavior: the durable state is the presence of the newly created directory entry and directory inode after fsync/checkpoint.

Dependencies/integration: `mnt_dir_` path initialization and raw POSIX directory fsync support.

Risks/test signals: some filesystems have nuanced semantics for fsyncing a newly created directory without fsyncing its parent; the test expects persistence. Missing directory is the main failure.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_321_1.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_321_2.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_321_2.cpp

Purpose: explicit `generic_321_2` rename test. It moves a pre-fsynced root file into a pre-created directory and checks post-crash namespace placement.

Important APIs/types/functions: `Generic321_2`, `open`, `mkdir`, `fsync`, `rename`, `Checkpoint`, directory enumeration, and `DataTestResult`.

Control flow: setup creates `foo` and `test_dir_a`, fsyncs `foo`, syncs, and closes. Run renames `foo` into `test_dir_a/foo`, fsyncs the target directory and moved file, and checkpoints. Check verifies `foo` is absent at root and present under the directory.

State/persistence behavior: both unlink-from-old-parent and link-into-new-parent effects of rename must be durable once the target directory/file are fsynced.

Dependencies/integration: direct syscalls and CrashMonkey checkpointing.

Risks/test signals: parent fsync coverage is asymmetric; root may not be fsynced after rename. The checker treats old-name persistence or missing new name as failure.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_321_2.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_321_3.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_321_3.cpp

Purpose: replay-rename subtest from xfstests generic/321. It combines a root-to-directory rename with setting an xattr on the moved file and fsyncing it.

Important APIs/types/functions: `Generic321_3`, `rename`, `fsetxattr`, `fsync`, `Checkpoint`, xattr include selection, `stat`, and `DataTestResult`.

Control flow: setup creates root `foo` and `test_dir_a`, fsyncs the file, and syncs. Run renames `foo` into the directory, fsyncs the directory, sets `user.foo=blah` on the moved file, fsyncs the file, and checkpoints. Check validates namespace placement and usually the moved file's survival.

State/persistence behavior: replay must preserve the rename and the later xattr/inode update without resurrecting the old root name.

Dependencies/integration: requires user xattr support and directory/file fsync behavior.

Risks/test signals: if xattrs are unsupported, the workload fails before reaching its namespace oracle. Signals include missing moved file, old name persistence, and possibly xattr metadata loss depending on check path.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_321_3.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_322.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_322.cpp

Purpose: xfstests generic/322 rename-data test. It renames a data-containing `foo` to `bar`, fsyncs `bar`, and expects `bar` to exist with the original data after recovery.

Important APIs/types/functions: `Generic322`, `WriteData`, `rename`, `open`, `fsync`, `Checkpoint`, `md5sum` via `popen`, `stat/open` checks, and `DataTestResult`.

Control flow: setup creates `test_dir_a/foo` and `foo_backup`, writes matching 4 KiB data to both, syncs, and closes. Run renames `foo` to `bar`, opens/fsyncs `bar`, and checkpoints. Check ensures old and new names are mutually exclusive, requires `bar` after checkpoint 1, and compares `bar` to backup.

State/persistence behavior: the rename and file contents must both survive; having both names or neither name is invalid.

Dependencies/integration: direct POSIX operations, external `md5sum`, and CrashMonkey checkpointing.

Risks/test signals: checksum helper assumes `md5sum` output is available and parseable. Signals are old file persisted, file missing, or data checksum mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_322.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_322_2.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_322_2.cpp

Purpose: generic/322 write-after-fsync-rename variant. It tests whether data written and `sync_file_range`d before a rename is preserved when the renamed file is fsynced.

Important APIs/types/functions: `Generic322_2`, `WriteData`, `fsync`, `sync_file_range`, `rename`, `Checkpoint`, `md5sum`, and `DataTestResult`.

Control flow: setup creates `foo` and `foo_backup`, writes/fsyncs the first 4 KiB, writes another 4 KiB at offset 4096 to both, uses `sync_file_range` for `foo`, fsyncs backup, and syncs. Run renames `foo` to `bar`, fsyncs `bar`, and checkpoints. Check performs mutual-exclusion checks and md5 comparison against backup.

State/persistence behavior: both the initial fsynced data and the later range-synced data should be present in `bar` after checkpoint 1.

Dependencies/integration: Linux `sync_file_range`, external `md5sum`, and directory rename semantics.

Risks/test signals: `sync_file_range` does not provide the same metadata durability as fsync on all filesystems. Failures are missing `bar`, both names present, or checksum mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_322_2.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_325.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_325.cpp

Purpose: xfstests generic/325 mmap/msync persistence test. It writes a 256 KiB file, modifies the first and last 4 KiB through a shared mapping, msyncs the surrounding ranges, and expects the mapped writes to persist.

Important APIs/types/functions: `Generic325`, `WriteData`, `mmap`, `memcpy`, `msync(MS_SYNC)`, `munmap`, `Checkpoint`, `md5sum`, and `DataTestResult`.

Control flow: setup builds `foo_backup` with the same write and mmap/msync sequence, then syncs. Run creates `foo`, writes 256 KiB, syncs, mmaps it, writes repeated text at offsets 0 and 258048, msyncs 0-64 KiB and 192-256 KiB, unmaps, and checkpoints. Check compares `foo` to `foo_backup` by md5.

State/persistence behavior: dirty mmap pages at both file edges must be durable after `msync`, including the final page range near EOF.

Dependencies/integration: POSIX mmap/msync behavior and external `md5sum`.

Risks/test signals: `msync` lengths are larger ranges than the 4 KiB writes, and one `munmap` error path uses odd pointer/length values. The final signal is checksum mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_325.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_335.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_335.cpp

Purpose: xfstests generic/335 reproduction for directory rename plus sibling creation. It moves `A/B/foo` to `C/foo`, creates `A/bar`, fsyncs `A`, and checks both names are in their expected directories after recovery.

Important APIs/types/functions: `Generic335`, `mkdir`, `open`, `rename`, `fsync` on directory fd, `Checkpoint`, `opendir`/`readdir`, and `DataTestResult`.

Control flow: setup creates `A/B`, `C`, and `A/B/foo`, then syncs. Run renames `foo` from `A/B` into `C`, creates `A/bar`, fsyncs directory `A`, and checkpoints. Check enumerates `A`, `A/B`, and `C` to validate placement.

State/persistence behavior: after checkpoint 1, `foo` must be only in `C`, `bar` only in `A`, and `A/B` should not retain stale entries.

Dependencies/integration: uses `mnt_dir_`, raw directory operations, and CrashMonkey checkpointing.

Risks/test signals: fsyncing `A` rather than all affected directories is the intended stress. Failures include missing `foo`, duplicate old/new locations, or `bar` in the wrong directory.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_335.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_336.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_336.cpp

Purpose: btrfs generic/336 reproduction. It removes a hard link in `B`, renames `B/bar` to `C/bar`, fsyncs `A/foo`, and expects the renamed file not to be lost.

Important APIs/types/functions: `Generic336`, `link`, `unlink`, `rename`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, `opendir`/`readdir`, and `DataTestResult`.

Control flow: setup creates directories `A`, `B`, `C`, file `A/foo`, hard link `B/foo_link`, file `B/bar`, and syncs. Run unlinks `B/foo_link`, renames `B/bar` to `C/bar`, opens/fsyncs `A/foo` through `cm_`, and checkpoints. Check verifies `bar` is only in `C`, `foo` remains in `A`, and `B` is empty.

State/persistence behavior: replay of fsync on the linked inode must not lose unrelated renamed `bar` or resurrect removed link state.

Dependencies/integration: mixes raw namespace operations with `cm_` wrappers for the final fsync/checkpoint.

Risks/test signals: a source typo checks `stat_new_res_bar` against `foo_path_moved` in similar files, but this file's check is mostly explicit. Signals are missing bar, duplicate bar, missing foo, or nonempty `B`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_336.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_341.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_341.cpp

Purpose: btrfs generic/341 reproduction for directory rename and recreation. It renames `A/X` to `A/Y`, recreates an empty `A/X`, fsyncs the new `X`, and checks that old contents moved to `Y`.

Important APIs/types/functions: `Generic341`, `WriteData`, `rename`, `mkdir`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: setup creates `A/X` with `foo` and `bar`, writes 8 KiB to each, and syncs. Run renames `X` to `Y`, creates a new `X`, fsyncs the new directory through `cm_`, and checkpoints. Check stats old and moved paths for `foo` and `bar`.

State/persistence behavior: after recovery, the recreated `X` should be empty and `Y` should contain both original files. Files should not be missing or present in both directories.

Dependencies/integration: fixed `/mnt/snapshot`, raw rename/mkdir, and `cm_` wrapped fsync/checkpoint.

Risks/test signals: the check for `bar`'s new path appears to stat `foo_path_moved` instead of `bar_path_moved`, weakening bar-specific detection. Missing or duplicate moved files are reported.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_341.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_342.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_342.cpp

Purpose: f2fs generic/342 reproduction. It renames a 16 KiB `foo` to `bar`, creates a new 4 KiB `foo`, fsyncs new `foo`, and expects both files with their distinct sizes after recovery.

Important APIs/types/functions: `Generic342`, `WriteData`, `rename`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: setup creates `test_dir_a/foo`, writes 16 KiB, and syncs. Run renames `foo` to `bar`, creates a new `foo`, writes 4 KiB, fsyncs new `foo` through `cm_`, and checkpoints. Check stats both paths and compares sizes against `FOO_NEW_SIZE` and `FOO_OLD_SIZE`.

State/persistence behavior: the old file's data/metadata must survive under `bar`, while the new `foo` must contain only the new 4 KiB data.

Dependencies/integration: fixed `/mnt/snapshot`, f2fs bug motivation, and CrashMonkey wrappers for final file operations.

Risks/test signals: one check references `stats_old.st_size` even when `stat_foo` failed, so missing-new-file paths can be brittle. Signals include missing `bar` or wrong sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_342.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_343.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_343.cpp

Purpose: btrfs generic/343 reproduction. It combines hard-link creation, moving a directory from `Y` to `X`, moving `foo_2` from `Y` to `X`, and fsyncing `X/foo`.

Important APIs/types/functions: `Generic343`, `mkdir`, `open`, `link`, `rename`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, `opendir`/`readdir`, and `DataTestResult`.

Control flow: setup creates `X`, `Y`, `X/foo`, `Y/Z`, and `Y/foo_2`, then syncs. Run links `X/foo` to `X/bar`, renames `Y/Z` into `X/Z`, renames `Y/foo_2` into `X/foo_2`, fsyncs `X/foo`, and checkpoints. Check verifies `X` contains `foo`, `bar`, `foo_2`, and `Z`, while `Y` no longer contains moved entries.

State/persistence behavior: replay must not duplicate moved entries in both directories or lose them entirely. The fsynced file's log must correctly carry related directory operations.

Dependencies/integration: raw namespace operations plus `cm_` final fsync/checkpoint.

Risks/test signals: check variable `empty_B` is unused legacy naming. Signals are missing moved file/dir or old entries persisting in `Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_343.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_348.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_348.cpp

Purpose: btrfs generic/348 symlink replay regression. It verifies that symlink targets are not recovered as empty strings after fsyncing the symlink parent directories.

Important APIs/types/functions: `Generic348`, `symlink`, `mkdir`, `open`, `fsync`, `Checkpoint`, `readlink`, `PATH_MAX`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: setup creates and syncs directory `A`. Run creates symlink `A/bar1 -> /mnt/snapshot/foo1`, fsyncs `A`, creates directory `B`, creates symlink `B/bar2 -> /mnt/snapshot/foo2`, fsyncs `B`, and checkpoints. Check reads both symlinks and verifies target strings are non-empty.

State/persistence behavior: after checkpoint 1, symlink inodes and their target payloads should be durable for both an already-persisted parent and a newly-created parent.

Dependencies/integration: fixed `/mnt/snapshot` paths and POSIX symlink/readlink behavior.

Risks/test signals: `ReadLink` returns the literal `"readlink error"` on failure, which is non-empty and can mask missing symlinks. The explicit signal only catches empty recovered targets.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_348.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_376.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_376.cpp

Purpose: btrfs generic/376 reproduction. It renames `test_dir/foo` to `bar`, creates a new `foo`, fsyncs `bar`, and expects both names to survive recovery.

Important APIs/types/functions: `Generic376`, `mkdir`, `open`, `fsync`, `rename`, `Checkpoint`, `opendir`/`readdir`, and `DataTestResult`.

Control flow: setup creates `test_dir/foo`, fsyncs the directory and file, then syncs. Run renames `foo` to `bar`, opens `bar`, creates a new `foo`, fsyncs only `bar`, checkpoints, and closes. Check enumerates `test_dir` for both `foo` and `bar`.

State/persistence behavior: the new file at the old name must not be lost just because only the renamed file was fsynced. The old and new inode names should coexist after checkpoint 1.

Dependencies/integration: direct POSIX operations and fixed `/mnt/snapshot`.

Risks/test signals: no content validation, only namespace presence. Failure reports missing `foo`, `bar`, or both.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_376.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_468.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_468.cpp

Purpose: EOF block allocation persistence test. It allocates blocks beyond EOF with keep-size after an initial fsync epoch and expects the increased block count to survive `fdatasync` and crash recovery.

Important APIs/types/functions: `EOFBlocksLoss`, `WriteData`, `syncfs`, `fsync`, `fallocate(FALLOC_FL_KEEP_SIZE)`, `fdatasync`, `Checkpoint`, `stat`, and `DataTestResult::kIncorrectBlockCount`.

Control flow: setup creates `test_file`, writes 8 KiB at offset 8 KiB, syncs, and closes. Run opens the file, fsyncs and checkpoints once, calls `syncfs` to force a separate epoch, keep-size fallocates 8 KiB at offset 4,202,496, calls `fdatasync`, checkpoints again, and closes.

State/persistence behavior: after checkpoint 2, logical size can remain 16 KiB but block count should increase beyond the original 16 blocks. If `st_blocks` remains 16, EOF allocation was lost.

Dependencies/integration: fixed mount path and Linux fallocate/fdatasync behavior.

Risks/test signals: expected block count baseline is filesystem-dependent. Signal is missing file or unchanged block count after checkpoint 2.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_468.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_ext4_direct_write.cpp -->
# sources/test-tools/crashmonkey/code/tests/generic_ext4_direct_write.cpp

Purpose: ext4 direct-write regression workload. It combines a delayed buffered write that extends i_size with a direct synchronous write to the first block, then checks recovered size/block metadata consistency.

Important APIs/types/functions: `genericDirectWrite`, `cm_->CmOpen`, `WriteData`, `O_DIRECT`, `O_SYNC`, `posix_memalign`, `pwrite`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: setup creates an empty durable `test_file`. Run opens it normally through `cm_`, writes 4 KiB at offset 16 KiB buffered, closes, reopens with `O_DIRECT | O_SYNC`, writes an aligned 4 KiB buffer at offset 0, sleeps, checkpoints without fsyncing the buffered write, and closes.

State/persistence behavior: if blocks are allocated after recovery, i_size must not be zero. The workload targets ext4 ordering where direct write block allocation could persist while i_size stayed stale.

Dependencies/integration: requires direct-I/O alignment, `posix_memalign`, and CrashMonkey wrapper operations.

Risks/test signals: intentionally avoids fsync because it would hide the bug, so the oracle is metadata consistency rather than full data durability. Failure is `st_blocks > 0 && st_size == 0`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/generic_ext4_direct_write.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-1.cpp -->
# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-1.cpp

Purpose: generated/new-bug namespace workload involving directories `A` and `B`, files named `foo` and `bar`, renaming `B/bar` over `A/bar`, then creating/fsyncing `A/foo`.

Important APIs/types/functions: class `testName`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmRename`, `cm_->CmCheckpoint`, raw `mkdir`, `stat`, and `DataTestResult`.

Control flow: setup initializes path strings only. Run creates `A`, creates/fsyncs `A/bar`, checkpoints, creates `B` and `B/bar`, renames `B/bar` to `A/bar`, creates `A/foo`, fsyncs `A/foo`, and checkpoints again. The comments note that an fsync of `A` may be required but is not part of the workload.

State/persistence behavior: it stresses overwrite/rename interaction with a previously fsynced file and later inode fsync in the same directory.

Dependencies/integration: heavily uses `cm_` wrappers for operations intended to be recorded, with raw `mkdir` for directory creation.

Risks/test signals: checker details are sparse and class name is generic. Expected signals are missing required names or stale overwritten names after checkpointed fsyncs.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-1.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-10.cpp -->
# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-10.cpp

Purpose: reduced directory rename workload. It creates `A`, checkpoints, renames `A` to `B`, creates/fsyncs `B/foo`, and checkpoints again.

Important APIs/types/functions: `testName`, `mkdir`, `cm_->CmRename`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: setup initializes root, `A`, `B`, and child paths. Run creates `A`, checkpoints, renames `A` to `B`, creates `B/foo`, fsyncs that file, and checkpoints. The checker reinitializes paths and validates the recovered namespace.

State/persistence behavior: after the second checkpoint, `B/foo` should exist and the old `A` location should not reappear as an independent directory unless recovery legitimately stopped before the rename checkpoint.

Dependencies/integration: raw `mkdir` plus `cm_` rename/open/fsync/checkpoint wrappers.

Risks/test signals: no parent directory fsync is performed, so the workload intentionally probes whether file fsync captures enough rename context. Signals are missing new directory/file or stale old directory.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-10.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-2.cpp -->
# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-2.cpp

Purpose: generated workload for nested directory rename and later file rename. It moves `A/C` to `B`, creates/fsyncs `B/bar`, checkpoints, then renames `B/bar` to `A/bar` and fsyncs `A`.

Important APIs/types/functions: `testName`, `mkdir`, `cm_->CmOpen(..., O_DIRECTORY)`, `cm_->CmRename`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: setup initializes paths for `A`, `A/C`, `B`, and child file names. Run creates `A` and `A/C`, opens `A/C` as a directory, renames `A/C` to `B`, creates/fsyncs `B/bar`, checkpoints, renames `B/bar` to `A/bar`, opens/fsyncs `A`, and checkpoints again.

State/persistence behavior: recovery must preserve both directory move and later file move without duplicating or losing `bar`.

Dependencies/integration: relies on `cm_` wrappers for rename/fsync/checkpoints and raw directory creation.

Risks/test signals: complex path reuse means old `AC_*` and `B_*` names can be confused. Signals are missing `A/bar`, stale `B/bar`, or incorrect directory topology after checkpoints.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-2.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-3.cpp -->
# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-3.cpp

Purpose: generated workload mixing separate fsync epochs, hard-link creation, and parent directory fsync. It creates files in `B`, links `B/foo` into `A/C/foo`, and fsyncs `A`.

Important APIs/types/functions: `testName`, `mkdir`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, raw `link`, and `DataTestResult`.

Control flow: run creates `A`, `A/C`, and `B`; creates/fsyncs `B/foo` and checkpoints; creates/fsyncs `B/bar` and checkpoints; hard-links `B/foo` to `A/C/foo`; opens/fsyncs directory `A`; and checkpoints a third time.

State/persistence behavior: after final checkpoint, the link into the nested directory and the existing `B` files should be consistent. It probes whether fsyncing a parent captures child-directory link changes.

Dependencies/integration: raw hard-link call plus `cm_` file/directory fsyncs.

Risks/test signals: parent `A` fsync may not durably cover `A/C` changes on all filesystems, making the oracle intentionally aggressive. Failures likely include missing link or stale namespace state.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-3.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-4.cpp -->
# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-4.cpp

Purpose: generated workload for directory rename, recreating the old directory, and fsyncing the renamed directory. It is similar to generic/341 in a smaller `A`/`B` shape.

Important APIs/types/functions: `testName`, `mkdir`, `cm_->CmRename`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: run creates `A`, checkpoints, renames `A` to `B`, creates/fsyncs `B/foo`, checkpoints, recreates `A`, creates `A/foo`, opens/fsyncs directory `B`, and checkpoints again.

State/persistence behavior: after final checkpoint, both the recreated `A` state and renamed `B` state should be represented without losing `B/foo` or confusing the old and new `A`.

Dependencies/integration: raw `mkdir`, `cm_` rename/open/fsync/checkpoint, fixed path members initialized from `mnt_dir_`.

Risks/test signals: no explicit fsync of recreated `A`; the test is designed to expose rename replay ordering gaps. Signals are missing files or stale old directory state.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-4.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-5.cpp -->
# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-5.cpp

Purpose: generated hard-link and multi-file workload. It creates `A/foo`, links it as `B/foo`, fsyncs the original, then creates `A/bar`, opens `B/foo`, fsyncs the linked name, and checkpoints.

Important APIs/types/functions: `testName`, `mkdir`, raw `link`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: run creates `A` and `B`, creates `A/foo`, hard-links it to `B/foo`, fsyncs `A/foo`, checkpoints, creates `A/bar`, opens `B/foo`, fsyncs `B/foo`, and checkpoints again.

State/persistence behavior: the same inode is referenced from two directories and fsynced through both names at different times. Recovery should preserve the link relationship and the later `A/bar` creation according to checkpoint.

Dependencies/integration: raw hard-link operation and `cm_` wrapper fsync/checkpoint operations.

Risks/test signals: the checker must distinguish two names for one inode from duplicate independent files. Expected failures are missing link target, stale/missing `bar`, or bad namespace placement.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-5.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-6.cpp -->
# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-6.cpp

Purpose: generated workload involving root-level and directory-level files. It creates `foo` at the mount root and `A/foo`, fsyncs `A/foo`, then creates `A/bar` and fsyncs the mount root directory.

Important APIs/types/functions: `testName`, `mkdir`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, directory `O_DIRECTORY`, and `DataTestResult`.

Control flow: run creates `A`, creates root `foo`, creates `A/foo`, fsyncs `A/foo`, checkpoints, creates `A/bar`, opens the mount root as a directory, fsyncs it, and checkpoints again.

State/persistence behavior: the workload probes whether root-directory fsync captures creation inside a child directory and how root-level and child names coexist after replay.

Dependencies/integration: `cm_` wrappers for opens/fsyncs/checkpoints, raw `mkdir`, and initialized path members.

Risks/test signals: fsyncing the root may not imply persistence of `A/bar` on all filesystems, making this an aggressive crash oracle. Signals are missing root/child files or inconsistent directory contents.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-6.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-7.cpp -->
# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-7.cpp

Purpose: generated hard-link workload from a root file into directory `A`. It checks persistence of a link created in a child directory after fsyncing the original root file.

Important APIs/types/functions: `testName`, `mkdir`, `cm_->CmOpen`, raw `link`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: run creates `A`, creates root `foo`, hard-links `foo` as `A/bar`, fsyncs root `foo`, and checkpoints. The checker reinitializes paths and validates namespace expectations.

State/persistence behavior: after checkpoint 1, both names should be valid hard links to the same inode, or at least the linked child name should not be lost if the test oracle requires it.

Dependencies/integration: raw hard-link operation combined with `cm_` file fsync/checkpoint.

Risks/test signals: parent directory `A` is not fsynced after link creation, so behavior is filesystem-dependent. Main signals are missing original or linked name.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-7.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-8.cpp -->
# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-8.cpp

Purpose: generated keep-size fallocate workload. It writes 4 KiB to root `foo`, allocates another 4 KiB beyond EOF with `FALLOC_FL_KEEP_SIZE`, fsyncs, and checkpoints.

Important APIs/types/functions: `testName`, `cm_->CmOpen`, `WriteData`, `fallocate(FALLOC_FL_KEEP_SIZE)`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: run opens/creates `foo`, writes 4096 bytes at offset 0, keep-size fallocates 4096 bytes at offset 4096, fsyncs `foo`, checkpoints, and returns. Setup/check only initialize and validate path state.

State/persistence behavior: logical file size should remain 4 KiB while allocation metadata may include the next block. It is a compact version of EOF allocation persistence checks.

Dependencies/integration: Linux fallocate support and `cm_` wrappers for open/fsync/checkpoint.

Risks/test signals: checker details determine whether it validates size, block count, or only file presence. Main expected risks are incorrect size growth or lost allocation metadata.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-8.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-9.cpp -->
# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-9.cpp

Purpose: generated keep-size zero-range workload. It writes 4 KiB to root `foo`, zero-ranges the next 4 KiB with keep-size, fsyncs, and checkpoints.

Important APIs/types/functions: `testName`, `cm_->CmOpen`, `WriteData`, `fallocate(FALLOC_FL_ZERO_RANGE | FALLOC_FL_KEEP_SIZE)`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: run creates `foo`, writes 4096 bytes at offset 0, calls zero-range keep-size at offset 4096 for 4096 bytes, fsyncs, and checkpoints. The path initialization mirrors bug-8.

State/persistence behavior: the file should keep its original logical size while zero-range allocation metadata is handled durably. It targets the same size-vs-allocation class as the f2fs zero-range bug.

Dependencies/integration: Linux zero-range support and CrashMonkey wrapper operations.

Risks/test signals: if the checker does not inspect block count, it may only catch size expansion or file loss. Expected failure modes are incorrect size growth, missing file, or stale allocation accounting.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/new_bugs/bug-9.cpp -->
