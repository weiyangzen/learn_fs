# Group research: subset-b-009212

This grouped report covers the requested CrashMonkey seq1 source files. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang210.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang210.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang210.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises hard link inside directory A from A/foo to A/bar, persisted by a whole-filesystem CmSync before the crash checkpoint. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/foo; hard-link A/foo to A/bar; CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang210.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang211.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang211.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang211.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory hard link from root file /bar into A/bar, with the destination directory A fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync directory A` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /bar; hard-link /bar to A/bar; open A as directory; CmFsync(A); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `fsync directory A`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang211.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang212.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang212.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang212.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory hard link from /bar to A/bar, with only the source file descriptor fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync source file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /bar; hard-link /bar to A/bar; CmFsync(/bar fd); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `fsync source file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang212.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang213.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang213.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang213.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory hard link from /bar to A/bar, with the linked destination file descriptor fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync linked destination file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /bar; hard-link /bar to A/bar; open A/bar; CmFsync(A/bar fd); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `fsync linked destination file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang213.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang214.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang214.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang214.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory hard link plus fsync of an unrelated newly created file in A. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync unrelated file in A` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /bar; hard-link /bar to A/bar; open A/foo; CmFsync(A/foo fd); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `fsync unrelated file in A`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang214.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang215.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang215.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang215.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory hard link with the mount root directory fsynced rather than A or the file. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync mount root directory` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /bar; hard-link /bar to A/bar; open mount root directory; CmFsync(root dir); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `fsync mount root directory`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang215.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang216.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang216.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang216.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory hard link plus fsync of an unrelated root file. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync unrelated root file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /bar; hard-link /bar to A/bar; create /foo; CmFsync(/foo fd); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `fsync unrelated root file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang216.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang217.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang217.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang217.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory hard link from /bar to A/bar, persisted by whole-filesystem sync. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /bar; hard-link /bar to A/bar; CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang217.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang218.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang218.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang218.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises hard link from nested file A/bar back to root /bar, with source directory A fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync directory A` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; hard-link A/bar to /bar; open A directory; CmFsync(A); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `fsync directory A`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang218.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang219.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang219.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang219.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises hard link from A/bar to root /bar, with destination/root file descriptor fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync linked root file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; hard-link A/bar to /bar; open /bar; CmFsync(/bar fd); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `fsync linked root file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang219.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang22.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang22.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang22.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises zero-range fallocate that overlaps the end of written data and extends beyond it, with the same file fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync modified file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; WriteData(/foo, offset 0, 32768); fallocate ZERO_RANGE at offset 30768 length 5000; CmFsync(/foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on file data and extent conversion via WriteData plus fallocate. The selected flush action is `fsync modified file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash state should reveal whether data blocks, zeroed ranges, file size, and allocation metadata reflect the intended fallocate durability boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang22.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang220.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang220.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang220.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises hard link from A/bar to /bar, with the source file descriptor fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync source file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; hard-link A/bar to /bar; CmFsync(A/bar fd); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `fsync source file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang220.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang221.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang221.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang221.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises hard link from A/bar to /bar plus fsync of another file in the same directory. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync unrelated file in A` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; hard-link A/bar to /bar; create A/foo; CmFsync(A/foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `fsync unrelated file in A`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang221.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang222.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang222.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang222.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises hard link from A/bar to /bar, with the root directory fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync mount root directory` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; hard-link A/bar to /bar; open mount root directory; CmFsync(root dir); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `fsync mount root directory`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang222.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang223.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang223.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang223.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises hard link from A/bar to /bar plus fsync of an unrelated root file. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync unrelated root file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; hard-link A/bar to /bar; create /foo; CmFsync(/foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `fsync unrelated root file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang223.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang224.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang224.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang224.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises hard link from A/bar to root /bar, persisted by whole-filesystem sync. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; hard-link A/bar to /bar; CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang224.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang225.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang225.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang225.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink of a root file after close, with parent/root directory fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync parent directory` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; close /foo; unlink /foo; open mount root directory; CmFsync(root dir); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `fsync parent directory`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang225.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang226.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang226.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang226.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink followed by recreation of the same root pathname, with the new inode fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync recreated file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; close /foo; unlink /foo; recreate /foo; CmFsync(new /foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `fsync recreated file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang226.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang227.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang227.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang227.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink of /foo followed by fsync of a different root file /bar. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync unrelated file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; close /foo; unlink /foo; create /bar; CmFsync(/bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `fsync unrelated file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang227.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang228.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang228.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang228.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink of a root file, persisted by whole-filesystem sync. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; close /foo; unlink /foo; CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang228.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang229.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang229.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang229.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink of nested A/foo, with parent directory A fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync parent directory A` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/foo; close A/foo; unlink A/foo; open A directory; CmFsync(A); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `fsync parent directory A`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang229.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang23.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang23.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang23.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises zero-range fallocate on /foo, but durability is driven by fsync of unrelated /bar. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync unrelated file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; WriteData(/foo, offset 0, 32768); fallocate ZERO_RANGE at offset 30768 length 5000; create /bar; CmFsync(/bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on file data and extent conversion via WriteData plus fallocate. The selected flush action is `fsync unrelated file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash state should reveal whether data blocks, zeroed ranges, file size, and allocation metadata reflect the intended fallocate durability boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang23.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang230.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang230.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang230.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink and recreate of the same nested pathname A/foo, with the recreated file fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync recreated nested file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/foo; close A/foo; unlink A/foo; recreate A/foo; CmFsync(new A/foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `fsync recreated nested file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang230.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang231.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang231.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang231.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink of A/foo followed by fsync of another file in A. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync sibling file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/foo; close A/foo; unlink A/foo; create A/bar; CmFsync(A/bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `fsync sibling file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang231.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang232.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang232.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang232.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink of nested A/foo, persisted by whole-filesystem sync. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/foo; close A/foo; unlink A/foo; CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang232.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang233.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang233.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang233.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink of root file /bar, with parent/root directory fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync parent directory` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /bar; close /bar; unlink /bar; open mount root directory; CmFsync(root dir); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `fsync parent directory`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang233.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang234.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang234.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang234.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink of /bar followed by fsync of a different root file /foo. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync unrelated file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /bar; close /bar; unlink /bar; create /foo; CmFsync(/foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `fsync unrelated file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang234.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang235.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang235.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang235.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink and recreate of the same root pathname /bar, with recreated file fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync recreated file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /bar; close /bar; unlink /bar; recreate /bar; CmFsync(new /bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `fsync recreated file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang235.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang236.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang236.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang236.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink of /bar, persisted by whole-filesystem sync. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /bar; close /bar; unlink /bar; CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang236.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang237.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang237.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang237.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink of nested A/bar, with parent directory A fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync parent directory A` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; close A/bar; unlink A/bar; open A directory; CmFsync(A); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `fsync parent directory A`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang237.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang238.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang238.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang238.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink of A/bar followed by fsync of sibling A/foo. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync sibling file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; close A/bar; unlink A/bar; create A/foo; CmFsync(A/foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `fsync sibling file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang238.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang239.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang239.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang239.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink and recreate of nested A/bar, with recreated file fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync recreated nested file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; close A/bar; unlink A/bar; recreate A/bar; CmFsync(new A/bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `fsync recreated nested file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang239.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang24.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang24.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang24.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises zero-range fallocate on /foo with whole-filesystem sync. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; WriteData(/foo, offset 0, 32768); fallocate ZERO_RANGE at offset 30768 length 5000; CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on file data and extent conversion via WriteData plus fallocate. The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash state should reveal whether data blocks, zeroed ranges, file size, and allocation metadata reflect the intended fallocate durability boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang24.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang240.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang240.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang240.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises unlink of nested A/bar persisted by whole-filesystem sync. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; close A/bar; unlink A/bar; CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through unlink(). The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang240.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang241.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang241.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang241.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises C library remove of root file /foo, with parent/root directory fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync parent directory` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; close /foo; remove /foo; open mount root directory; CmFsync(root dir); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `fsync parent directory`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang241.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang242.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang242.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang242.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove followed by recreation of root pathname /foo, with recreated file fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync recreated file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; close /foo; remove /foo; recreate /foo; CmFsync(new /foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `fsync recreated file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang242.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang243.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang243.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang243.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove of /foo followed by fsync of a different root file /bar. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync unrelated file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; close /foo; remove /foo; create /bar; CmFsync(/bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `fsync unrelated file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang243.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang244.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang244.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang244.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove of root file /foo persisted by whole-filesystem sync. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; close /foo; remove /foo; CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang244.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang245.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang245.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang245.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove of nested A/foo, with parent directory A fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync parent directory A` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/foo; close A/foo; remove A/foo; open A directory; CmFsync(A); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `fsync parent directory A`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang245.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang246.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang246.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang246.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove and recreate of nested A/foo, with recreated file fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync recreated nested file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/foo; close A/foo; remove A/foo; recreate A/foo; CmFsync(new A/foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `fsync recreated nested file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang246.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang247.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang247.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang247.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove of A/foo followed by fsync of sibling A/bar. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync sibling file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/foo; close A/foo; remove A/foo; create A/bar; CmFsync(A/bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `fsync sibling file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang247.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang248.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang248.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang248.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove of nested A/foo persisted by whole-filesystem sync. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/foo; close A/foo; remove A/foo; CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang248.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang249.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang249.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang249.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove of root file /bar, with parent/root directory fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync parent directory` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /bar; close /bar; remove /bar; open mount root directory; CmFsync(root dir); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `fsync parent directory`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang249.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang25.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang25.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang25.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises keep-size zero-range fallocate beyond the current file size, with root directory fsynced instead of /foo. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync root directory` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; WriteData(/foo, offset 0, 32768); fallocate ZERO_RANGE|KEEP_SIZE at offset 32768 length 32768; open mount root directory; CmFsync(root dir); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on file data and extent conversion via WriteData plus fallocate. The selected flush action is `fsync root directory`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash state should reveal whether data blocks, zeroed ranges, file size, and allocation metadata reflect the intended fallocate durability boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang25.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang250.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang250.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang250.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove of /bar followed by fsync of another root file /foo. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync unrelated file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /bar; close /bar; remove /bar; create /foo; CmFsync(/foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `fsync unrelated file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang250.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang251.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang251.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang251.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove and recreate of root pathname /bar, with recreated file fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync recreated file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /bar; close /bar; remove /bar; recreate /bar; CmFsync(new /bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `fsync recreated file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang251.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang252.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang252.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang252.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove of root file /bar persisted by whole-filesystem sync. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /bar; close /bar; remove /bar; CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang252.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang253.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang253.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang253.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove of nested A/bar, with parent directory A fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync parent directory A` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; close A/bar; remove A/bar; open A directory; CmFsync(A); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `fsync parent directory A`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang253.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang254.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang254.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang254.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove of A/bar followed by fsync of sibling A/foo. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync sibling file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; close A/bar; remove A/bar; create A/foo; CmFsync(A/foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `fsync sibling file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang254.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang255.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang255.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang255.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove and recreate of nested A/bar, with recreated file fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync recreated nested file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; close A/bar; remove A/bar; recreate A/bar; CmFsync(new A/bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `fsync recreated nested file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang255.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang256.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang256.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang256.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises remove of nested A/bar persisted by whole-filesystem sync. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/bar; close A/bar; remove A/bar; CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace deletion through C library remove(), which maps to unlink for these file paths. The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether the deleted name stays removed, reappears, or is replaced by a recreated inode according to the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang256.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang257.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang257.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang257.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises root-directory rename from /foo to /bar, with parent/root directory fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync parent directory` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; close /foo; CmRename(/foo -> /bar); open mount root directory; CmFsync(root dir); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace move through the CrashMonkey-wrapped CmRename() call. The selected flush action is `fsync parent directory`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether rename atomicity and source/destination directory persistence match the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang257.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang258.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang258.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang258.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises rename /foo to /bar followed by recreation/fsync of the old source pathname. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync recreated old source` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; close /foo; CmRename(/foo -> /bar); recreate/open /foo; CmFsync(/foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace move through the CrashMonkey-wrapped CmRename() call. The selected flush action is `fsync recreated old source`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether rename atomicity and source/destination directory persistence match the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang258.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang259.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang259.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang259.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises rename /foo to /bar, with the destination file descriptor fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync renamed destination` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; close /foo; CmRename(/foo -> /bar); open /bar; CmFsync(/bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace move through the CrashMonkey-wrapped CmRename() call. The selected flush action is `fsync renamed destination`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether rename atomicity and source/destination directory persistence match the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang259.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang260.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang260.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang260.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises rename /foo to /bar persisted by whole-filesystem sync. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; close /foo; CmRename(/foo -> /bar); CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace move through the CrashMonkey-wrapped CmRename() call. The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether rename atomicity and source/destination directory persistence match the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang260.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang261.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang261.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang261.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory rename from root /foo into A/bar, with destination directory A fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync destination directory` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /foo; close /foo; CmRename(/foo -> A/bar); open A directory; CmFsync(A); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace move through the CrashMonkey-wrapped CmRename() call. The selected flush action is `fsync destination directory`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether rename atomicity and source/destination directory persistence match the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang261.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang262.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang262.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang262.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory rename into A/bar followed by fsync of unrelated root /bar. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync unrelated root file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /foo; close /foo; CmRename(/foo -> A/bar); create /bar; CmFsync(/bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace move through the CrashMonkey-wrapped CmRename() call. The selected flush action is `fsync unrelated root file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether rename atomicity and source/destination directory persistence match the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang262.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang263.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang263.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang263.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory rename into A/bar, with destination file descriptor fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync renamed destination` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /foo; close /foo; CmRename(/foo -> A/bar); open A/bar; CmFsync(A/bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace move through the CrashMonkey-wrapped CmRename() call. The selected flush action is `fsync renamed destination`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether rename atomicity and source/destination directory persistence match the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang263.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang264.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang264.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang264.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory rename into A/bar followed by fsync of sibling A/foo. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync sibling file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /foo; close /foo; CmRename(/foo -> A/bar); create A/foo; CmFsync(A/foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace move through the CrashMonkey-wrapped CmRename() call. The selected flush action is `fsync sibling file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether rename atomicity and source/destination directory persistence match the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang264.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang265.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang265.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang265.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory rename into A/bar, with source/root directory fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync source/root directory` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /foo; close /foo; CmRename(/foo -> A/bar); open mount root directory; CmFsync(root dir); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace move through the CrashMonkey-wrapped CmRename() call. The selected flush action is `fsync source/root directory`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether rename atomicity and source/destination directory persistence match the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang265.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang266.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang266.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang266.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory rename into A/bar followed by recreation/fsync of old source /foo. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync recreated old source` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /foo; close /foo; CmRename(/foo -> A/bar); recreate/open /foo; CmFsync(/foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace move through the CrashMonkey-wrapped CmRename() call. The selected flush action is `fsync recreated old source`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether rename atomicity and source/destination directory persistence match the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang266.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang267.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang267.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang267.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory rename from /foo to A/bar persisted by whole-filesystem sync. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `sync` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /foo; close /foo; CmRename(/foo -> A/bar); CmSync; checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace move through the CrashMonkey-wrapped CmRename() call. The selected flush action is `sync`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether rename atomicity and source/destination directory persistence match the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang267.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang268.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang268.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang268.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory rename out of A into root /bar, with source directory A fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync source directory` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/foo; close A/foo; CmRename(A/foo -> /bar); open A directory; CmFsync(A); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace move through the CrashMonkey-wrapped CmRename() call. The selected flush action is `fsync source directory`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether rename atomicity and source/destination directory persistence match the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang268.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang269.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang269.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang269.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory rename out of A into /bar, with destination file descriptor fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync renamed destination` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create A/foo; close A/foo; CmRename(A/foo -> /bar); open /bar; CmFsync(/bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace move through the CrashMonkey-wrapped CmRename() call. The selected flush action is `fsync renamed destination`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether rename atomicity and source/destination directory persistence match the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang269.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang26.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang26.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang26.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises keep-size zero-range fallocate beyond current file size, with /foo fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync modified file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; WriteData(/foo, offset 0, 32768); fallocate ZERO_RANGE|KEEP_SIZE at offset 32768 length 32768; CmFsync(/foo); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on file data and extent conversion via WriteData plus fallocate. The selected flush action is `fsync modified file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash state should reveal whether data blocks, zeroed ranges, file size, and allocation metadata reflect the intended fallocate durability boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang26.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang27.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang27.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang27.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises keep-size zero-range fallocate on /foo, but fsync is applied to unrelated /bar. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync unrelated file` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: create /foo; WriteData(/foo, offset 0, 32768); fallocate ZERO_RANGE|KEEP_SIZE at offset 32768 length 32768; create /bar; CmFsync(/bar); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on file data and extent conversion via WriteData plus fallocate. The selected flush action is `fsync unrelated file`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash state should reveal whether data blocks, zeroed ranges, file size, and allocation metadata reflect the intended fallocate durability boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.

<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang27.cpp -->
