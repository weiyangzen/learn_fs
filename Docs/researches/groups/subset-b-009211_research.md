# subset-b-009211 grouped research

This grouped report covers the exact source files assigned to work item `subset-b-009211`. Each source section is bounded by reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang156.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang156.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` buffered overlapping-write crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates directory `/A`, creates `/A/foo`, writes 32768 bytes at offset 0, then writes 5000 bytes at offset 30768 so the second write overlaps the tail and extends past the first range. Barrier: global `CmSync()` before the single checkpoint.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. file data and directory creation for `/A/foo` are expected to be durable after sync; close happens after the checkpoint. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang156.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang157.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang157.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, reopens it with `O_DIRECT|O_SYNC`, writes 32768 aligned bytes at offset 0 with `pwrite`, closes it, opens the mount root as a directory. Barrier: `CmFsync(fd_test)` on the mount root directory.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests whether the direct-I/O file creation and data write are recoverable when only the parent directory is fsynced after the direct write. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang157.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang158.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang158.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, reopens it with `O_DIRECT|O_SYNC`, writes 32768 aligned bytes at offset 0, closes it, reopens `/foo` normally. Barrier: `CmFsync(fd_foo)` on the target file.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests direct-write durability when the file itself, not the directory, is the post-write fsync target. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang158.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang159.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang159.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo and /bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, direct-writes 32768 bytes to it, closes it, creates a separate `/bar`. Barrier: `CmFsync(fd_bar)` on the unrelated newly created file.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. exercises whether fsyncing another file can accidentally mask or fail to persist the earlier direct-written file. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang159.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang160.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang160.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, reopens it with `O_DIRECT|O_SYNC`, writes 32768 aligned bytes at offset 0, and closes it. Barrier: global `CmSync()`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. global sync should flush file data, inode size, and directory metadata before the checkpoint. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang160.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang161.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang161.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, buffered-writes 32768 bytes, closes and reopens with `O_DIRECT|O_SYNC`, then overwrites the first 8192 bytes with aligned direct I/O. Barrier: `CmFsync(fd_test)` on the mount root directory.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests mixed buffered/direct writes where the parent directory, rather than the modified file, is fsynced. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang161.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang162.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang162.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, writes 32768 buffered bytes, reopens with `O_DIRECT|O_SYNC`, overwrites 8192 bytes at offset 0, closes and reopens the same file. Barrier: `CmFsync(fd_foo)` on `/foo`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests recovery of a mixed buffered/direct first-block overwrite with explicit file fsync. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang162.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang163.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang163.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo and /bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, writes 32768 buffered bytes, overwrites its first 8192 bytes with direct I/O, closes it, then creates `/bar`. Barrier: `CmFsync(fd_bar)` on the other file.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. probes cross-file fsync isolation after mixed data paths. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang163.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang164.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang164.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, writes 32768 buffered bytes, reopens with `O_DIRECT|O_SYNC`, and overwrites the first 8192 bytes directly. Barrier: global `CmSync()`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. global sync is the intended persistence point for mixed buffered/direct state. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang164.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang165.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang165.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A`, creates `/A/foo`, reopens it with `O_DIRECT|O_SYNC`, writes 32768 aligned bytes at offset 0, closes it, opens `/A` as a directory. Barrier: `CmFsync(fd_A)` on the containing directory.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. checks nested-file creation and direct-write recovery with containing-directory fsync. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang165.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang166.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang166.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A`, direct-writes 32768 bytes to `/A/foo`, closes and reopens `/A/foo` normally. Barrier: `CmFsync(fd_Afoo)` on the target file.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. checks direct-write recovery through explicit fsync of the nested file. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang166.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang167.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang167.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo and /A/bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo`, direct-writes 32768 bytes, closes it, creates sibling `/A/bar`. Barrier: `CmFsync(fd_Abar)` on the sibling file.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests whether sibling-file fsync affects persistence of `/A/foo` direct-write state. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang167.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang168.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang168.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A`, creates `/A/foo`, reopens with `O_DIRECT|O_SYNC`, writes 32768 bytes, and closes it. Barrier: global `CmSync()`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. global sync should persist nested directory metadata, inode size, and direct-written data. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang168.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang169.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang169.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo`, buffered-writes 32768 bytes, then overwrites the first 8192 bytes using `O_DIRECT|O_SYNC`. Barrier: `CmFsync(fd_A)` on containing directory `/A`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. checks mixed buffered/direct nested-file persistence when only the directory receives fsync. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang169.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang170.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang170.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo`, writes 32768 buffered bytes, overwrites 8192 bytes at offset 0 through direct I/O, then reopens `/A/foo`. Barrier: `CmFsync(fd_Afoo)` on the modified file.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. validates file fsync after mixed buffered/direct writes in a subdirectory. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang170.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang171.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang171.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo and /A/bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo`, writes 32768 buffered bytes, overwrites the first 8192 bytes directly, then creates `/A/bar`. Barrier: `CmFsync(fd_Abar)` on sibling `/A/bar`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. cross-file durability probe inside the same directory after mixed data paths. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang171.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang172.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang172.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` direct-I/O data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo`, writes 32768 buffered bytes, overwrites 8192 bytes at offset 0 with direct I/O. Barrier: global `CmSync()`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. global sync should cover the nested mixed-write file and directory metadata. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang172.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang173.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang173.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, writes 32768 buffered bytes, allocates another 32768 bytes beginning at offset 32768, mmaps the 65536-byte range, writes mmap data into the second half. Barrier: `CmMsync(filep_foo + 32768, 8192, MS_SYNC)` before checkpoint.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. only the first 8192 bytes of the mmap-written extension are explicitly msynced; file-size and unwritten parts of the extension remain important crash-recovery edges. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang173.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang174.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang174.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: same root-file append mmap sequence as j-lang173: buffered 32768-byte prefix, fallocate at 32768 for 32768 bytes, mmap write into the second half. Barrier: `CmMsync` of 8192 bytes at offset 32768.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. generated duplicate/variant for the mmap extension persistence case, useful for sequence-table coverage even though check logic is identical. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang174.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang175.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang175.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: same as j-lang173: buffered initial extent plus mmap writes into a fallocated extension. Barrier: `CmMsync` on the first 8192 bytes of the extension.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. focuses on partial msync of newly allocated blocks after extending a root-level file. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang175.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang176.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang176.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: same root-level fallocate-extension and mmap-write sequence as j-lang173. Barrier: `CmMsync(filep_foo + 32768, 8192, MS_SYNC)`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. another generated member of the partial-msync extension family. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang176.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang177.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang177.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, writes 32768 bytes, fallocates 8192 bytes at offset 0, mmaps the first 8192 bytes, and overwrites that range through the mapping. Barrier: `CmMsync(filep_foo + 0, 8192, MS_SYNC)`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests mmap overwrite of the first block range with explicit msync and no later fsync/sync. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang177.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang178.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang178.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: same root-file mmap overwrite sequence as j-lang177. Barrier: `CmMsync` of the first 8192 bytes.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. generated duplicate/variant for first-range mmap overwrite persistence. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang178.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang179.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang179.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: same as j-lang177: buffered 32768-byte file followed by mmap overwrite of bytes 0..8191. Barrier: `CmMsync(filep_foo + 0, 8192, MS_SYNC)`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. checks recovered contents after a synced mmap overwrite without closing before checkpoint. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang179.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang180.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang180.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: same first-8192-byte mmap overwrite pattern as j-lang177. Barrier: `CmMsync` on the overwritten range.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. another generated member of the mmap overwrite family. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang180.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang181.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang181.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo`, writes 32768 buffered bytes, fallocates 32768 bytes at offset 32768, mmaps 65536 bytes, and writes into the second half. Barrier: `CmMsync(filep_Afoo + 32768, 8192, MS_SYNC)`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests partial msync of an mmap-written extension in a nested directory. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang181.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang182.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang182.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: same nested extension mmap sequence as j-lang181. Barrier: `CmMsync` on 8192 bytes starting at offset 32768.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. covers the nested-file partial-extension-msync case with the generated sequence variant. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang182.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang183.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang183.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: same as j-lang181: create `/A`, create `/A/foo`, buffered prefix write, fallocate extension, mmap second half. Barrier: partial `CmMsync` of the extension range.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. focuses on persistence interaction among nested directory metadata, fallocate extension, and mmap data. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang183.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang184.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang184.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: same nested fallocate-extension plus mmap-write sequence as j-lang181. Barrier: `CmMsync(filep_Afoo + 32768, 8192, MS_SYNC)`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. generated member of the nested partial-msync extension family. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang184.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang185.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang185.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo`, writes 32768 bytes, fallocates 8192 bytes at offset 0, mmaps the first 8192 bytes, and overwrites that range. Barrier: `CmMsync(filep_Afoo + 0, 8192, MS_SYNC)`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests nested-file mmap overwrite durability with only range msync before checkpoint. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang185.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang186.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang186.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: same nested first-range mmap overwrite as j-lang185. Barrier: `CmMsync` of bytes 0..8191.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. generated variant for synced mmap overwrite in a subdirectory. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang186.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang187.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang187.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: same as j-lang185: buffered file followed by mmap overwrite of the first 8192 bytes. Barrier: `CmMsync(filep_Afoo + 0, 8192, MS_SYNC)`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. checks recovery of nested mmap-overwritten data without a separate fsync. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang187.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang188.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang188.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` mmap/msync data crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: same nested first-8192 mmap overwrite pattern as j-lang185. Barrier: range `CmMsync` only.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. another generated member of the nested mmap overwrite family. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang188.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang189.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang189.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo -> /bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, creates a hard link `/bar` to the same inode, then opens the mount root directory. Barrier: `CmFsync(fd_test)` on the root directory.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests root-directory fsync as persistence barrier for creating a hard link in the same directory. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang189.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang190.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang190.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo -> /bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo` and hard-links it to `/bar`. Barrier: `CmFsync(fd_foo)` on the original file descriptor.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. probes whether source-file fsync is sufficient for hard-link metadata durability. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang190.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang191.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang191.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo -> /bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, links `/bar`, opens `/bar` normally. Barrier: `CmFsync(fd_bar)` on the destination name.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests destination-file fsync after hard-link creation. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang191.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang192.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang192.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo -> /bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo` and links `/bar` in the root directory. Barrier: global `CmSync()`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. global sync should persist both directory entry names and inode link count. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang192.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang193.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang193.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo -> /A/bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates directory `/A`, creates root file `/foo`, and hard-links it into `/A/bar`. Barrier: `CmFsync(fd_A)` on destination directory `/A`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests cross-directory hard-link persistence with destination-directory fsync. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang193.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang194.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang194.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo -> /A/bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A`, creates `/foo`, links it to `/A/bar`, then creates unrelated root `/bar`. Barrier: `CmFsync(fd_bar)` on unrelated `/bar`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. negative/control-style variant for hard-link metadata when fsync targets another file. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang194.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang195.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang195.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo -> /A/bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A`, creates `/foo`, links it to `/A/bar`, opens `/A/bar`. Barrier: `CmFsync(fd_Abar)` on the destination link.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests hard-link persistence when fsync targets the linked inode through the destination name. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang195.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang196.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang196.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo -> /A/bar plus /A/foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A`, creates `/foo`, links it to `/A/bar`, then creates `/A/foo`. Barrier: `CmFsync(fd_Afoo)` on sibling `/A/foo`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. checks that sibling-file fsync is not confused with destination-directory persistence. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang196.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang197.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang197.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo -> /A/bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A`, creates `/foo`, links it to `/A/bar`, opens the mount root directory. Barrier: `CmFsync(fd_test)` on the root directory.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests whether fsyncing the source parent/root directory is enough for a destination inside `/A`. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang197.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang198.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang198.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo -> /A/bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A`, creates `/foo`, links it to `/A/bar`. Barrier: `CmFsync(fd_foo)` on the source file.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. probes file-fsync semantics for cross-directory hard-link creation. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang198.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang199.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang199.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo -> /A/bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A`, creates `/foo`, hard-links into `/A/bar`. Barrier: global `CmSync()`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. global sync should persist both directories and link count. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang199.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang200.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang200.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo -> /bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A`, creates `/A/foo`, links it into root as `/bar`, opens `/A`. Barrier: `CmFsync(fd_A)` on the source directory.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests source-directory fsync for a hard link whose destination is the root directory. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang200.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang201.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang201.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo -> /bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo`, links it to root `/bar`, opens `/bar`. Barrier: `CmFsync(fd_bar)` on the destination link.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests destination-file fsync for nested-source/root-destination hard link. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang201.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang202.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang202.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo -> /bar plus /A/bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo`, links it to root `/bar`, then creates `/A/bar`. Barrier: `CmFsync(fd_Abar)` on nested sibling `/A/bar`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. cross-file control for hard-link persistence across directories. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang202.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang203.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang203.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo -> /bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo` and links it to root `/bar`. Barrier: `CmFsync(fd_Afoo)` on the source file.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests source-file fsync after cross-directory hard-link creation. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang203.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang204.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang204.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo -> /bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo`, links it to root `/bar`, opens the mount root directory. Barrier: `CmFsync(fd_test)` on root directory.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests destination-parent directory fsync for root-level link creation from a nested source. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang204.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang205.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang205.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo -> /bar plus /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo`, links it to `/bar`, then creates unrelated root `/foo`. Barrier: `CmFsync(fd_foo)` on unrelated `/foo`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. negative/control-style hard-link variant for unrelated file fsync. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang205.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang206.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang206.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo -> /bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo` and hard-links it into the root directory as `/bar`. Barrier: global `CmSync()`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. global sync should persist source and destination directory metadata plus link count. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang206.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang207.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang207.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo -> /A/bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A`, creates `/A/foo`, and links it to sibling `/A/bar`. Barrier: `CmFsync(fd_A)` on containing directory `/A`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests same-directory nested hard-link creation with parent-directory fsync. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang207.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang208.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang208.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo -> /A/bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo` and links sibling `/A/bar` in the same directory. Barrier: `CmFsync(fd_Afoo)` on source file.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. probes whether source-file fsync is enough for same-directory hard-link metadata. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang208.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang209.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang209.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo -> /A/bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A/foo`, links `/A/bar`, opens `/A/bar`. Barrier: `CmFsync(fd_Abar)` on destination link.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests destination-file fsync for same-directory nested hard link. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang209.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang16.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang16.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` fallocate zero-range crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, writes 32768 bytes, then uses `fallocate(FALLOC_FL_ZERO_RANGE, 32768, 32768)` to zero/extend the next 32768 bytes. Barrier: global `CmSync()`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests persistence of a zero-range extension and inode size after global sync. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang16.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang17.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang17.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` fallocate zero-range crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, writes 32768 bytes, then zeroes the first 5000 bytes with `FALLOC_FL_ZERO_RANGE`. Barrier: `CmFsync(fd_test)` on the mount root directory.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests whether directory fsync is unrelated/insufficient for data-range zeroing persistence. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang17.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang18.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang18.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` fallocate zero-range crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, writes 32768 bytes, then zeroes bytes 0..4999. Barrier: `CmFsync(fd_foo)` on the modified file.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests file fsync after an in-place zero-range operation. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang18.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang19.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang19.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` fallocate zero-range crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo and /bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, writes 32768 bytes, zeroes bytes 0..4999, then creates `/bar`. Barrier: `CmFsync(fd_bar)` on unrelated `/bar`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. cross-file control for zero-range persistence. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang19.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang20.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang20.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` fallocate zero-range crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, writes 32768 bytes, zeroes bytes 0..4999. Barrier: global `CmSync()`.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. global sync should persist the in-place zeroed range. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang20.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang21.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang21.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` fallocate zero-range crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo`, writes 32768 bytes, then zeroes 5000 bytes at offset 30768, overlapping the tail and extending beyond the original write. Barrier: `CmFsync(fd_test)` on the mount root directory.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests tail-overlap zeroing and possible size extension when only the parent directory is fsynced. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang21.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang2.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang2.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` baseline file-creation crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /foo.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/foo` with `O_RDWR|O_CREAT` and does not write data. Barrier: `CmFsync(fd_foo)` on the empty file.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. baseline single-checkpoint test for empty-file creation and file fsync. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang2.cpp -->
