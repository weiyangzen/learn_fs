# subset-b-009210 Research Group

This grouped report covers exactly the source files assigned to work item `subset-b-009210`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/rename_root_to_sub.cpp -->
# sources/test-tools/crashmonkey/code/tests/rename_root_to_sub.cpp

## Purpose
`sources/test-tools/crashmonkey/code/tests/rename_root_to_sub.cpp` is a hand-written CrashMonkey test for renaming a file from the mount root into a subdirectory. It creates `/mnt/snapshot/test_file`, creates and fsyncs `/mnt/snapshot/test_dir`, writes a known `TEST_TEXT` payload with all permission bits enabled, then checkpoints immediately after `rename(old_path, new_path)`.

## Important APIs, Types, and Functions
- `rename_root_to_sub` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
- `setup()` creates `TEST_DIR`, fsyncs that directory, creates `TEST_FILE` with `TEST_FILE_PERMS`, writes the static text payload, fsyncs the file, and closes it.
- `run(int checkpoint)` performs `rename(old_path.c_str(), new_path.c_str())` and returns `1` to expose the post-rename crash point.
- `check_test(...)` stats both old and new paths, classifies missing/duplicated files with `DataTestResult`, verifies the surviving object is a regular file with expected permissions, reads the payload, and compares it with `memcmp`.
- `test_case_get_instance()` and `test_case_delete_instance()` provide the dynamic-loader ABI.

## Control Flow
Setup first ensures the target subdirectory is durable by calling `mkdir`, `open(..., O_RDONLY)`, and `fsync` on the directory descriptor. It then temporarily sets `umask(0000)`, opens the old file with `O_RDWR | O_CREAT`, restores the umask, writes until the full `TEST_TEXT` length is persisted, fsyncs, and closes the file. The run phase has a single operation: rename root-level `test_file` to `test_dir/test_file`. The check phase examines old/new path existence and chooses exactly one surviving path for metadata and data validation.

## State and Persistence Behavior
Persistent state consists of one directory and one regular file under the fixed `TEST_MNT` path `/mnt/snapshot`. The setup phase makes the directory and original file durable before the tested rename, isolating crash behavior to the rename itself. After a crash at the checkpoint, acceptable recovery should have either the old file or the new file, but not neither and not both. The file type, permission mask, and byte-for-byte payload are expected to survive regardless of which pathname remains.

## Dependencies and Integration Points
This test uses raw POSIX syscalls and libc helpers rather than the generated `cm_` wrapper calls in `seq1`. It depends on `BaseTestCase`, `DataTestResult`, and the CrashMonkey loader calling setup/run/check in the expected order. It hard-codes `/mnt/snapshot` rather than using `mnt_dir_`, so it integrates only with harness setups mounted at that path.

## Risks and Edge Cases
The fixed mount path is brittle and ignores `init_values`. The private member `char text[strlen(TEST_TEXT)]` is unused and has no extra byte for a NUL terminator, though it is not referenced. `check_test()` does not free the read buffer on the successful comparison path until after validation, which is fine, but allocation size is exactly `strlen(TEST_TEXT)` and assumes byte-count comparisons only. Directory `open` uses `O_RDONLY` without `O_DIRECTORY`. The test treats both old and new files existing as `kOldFilePersisted`, which is useful for rename atomicity but may not distinguish link-count or aliasing anomalies.

## Test Signals
Strong signals are `kFileMissing`, `kOldFilePersisted`, `kFileMetadataCorrupted`, and `kFileDataCorrupted` from `DataTestResult`. A clean run should create durable setup state, expose the rename checkpoint by returning `1`, and after recovery find exactly one valid regular file containing the full `TEST_TEXT` payload with mode `0777` masked to permission bits.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/rename_root_to_sub.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/BaseTestCase.h -->
# sources/test-tools/crashmonkey/code/tests/seq1/BaseTestCase.h

## Purpose
`sources/test-tools/crashmonkey/code/tests/seq1/BaseTestCase.h` declares the base interface used by CrashMonkey C++ test plugins. It is an identical copy of the parent `tests/BaseTestCase.h` in this tree, but because it lives under `tests/seq1`, its relative includes point to `tests/results/DataTestResult.h` and `tests/user_tools/api/wrapper.h`, which do not exist at those locations. The generated `seq1/j-lang*.cpp` files include `../BaseTestCase.h`, so they use the parent header rather than this local copy.

## Important APIs, Types, and Functions
- `fs_testing::tests::BaseTestCase` is an abstract base class with virtual `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult*)` hooks.
- `Run(int change_fd, int checkpoint)` is declared as the harness wrapper that chooses the CrashMonkey operation wrapper and invokes `run()`.
- `init_values(std::string mount_dir, long filesys_size)` stores mount and filesystem-size context for derived tests.
- Protected state consists of `mnt_dir_`, `filesys_size_`, and `fs_testing::user_tools::api::CmFsOps *cm_`.
- `test_create_t` and `test_destroy_t` define the C-compatible plugin factory/deleter signatures.

## Control Flow
This header has no implementation, but it defines the lifecycle expected by the harness: create a derived instance, initialize values, call `setup()`, execute `Run(change_fd, checkpoint)`, then call `check_test()` after replay or crash recovery. Derived tests implement only the workload-specific parts; `Run` centralizes wrapper selection and operation serialization in the corresponding `.cpp` implementation.

## State and Persistence Behavior
The header stores mount path and filesystem size but performs no persistence itself. The `cm_` pointer is the critical state handoff: derived tests call `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, and related wrappers so the harness can record or replay filesystem operations. If `init_values` is skipped, generated tests will build paths from an empty `mnt_dir_`.

## Dependencies and Integration Points
It depends on `DataTestResult` for post-crash outcome reporting and `CmFsOps` from the user-tools wrapper API for syscall mediation. The ABI is designed for dynamically loaded tests exposing `test_case_get_instance` and `test_case_delete_instance`. As a `seq1` copy, this file is a risky integration artifact: direct inclusion from the `seq1` directory would resolve relative includes differently from the parent copy and currently appears broken unless matching `seq1/results` and `seq1/user_tools` trees are supplied.

## Risks and Edge Cases
The destructor is virtual, which is correct for plugin deletion through the base pointer. The raw `cm_` pointer is non-owning and valid only during `Run`; derived code should not retain it beyond the call. The duplicated header can drift from the parent header or accidentally be included by new `seq1` files, causing build failures due to bad relative include paths.

## Test Signals
The main verification signal is compile/link behavior of CrashMonkey test plugins and successful dynamic loading through the factory typedefs. A focused guard should compare this file with the parent `tests/BaseTestCase.h` and either keep them intentionally synchronized or remove/avoid the duplicate include path.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/BaseTestCase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/base.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/base.cpp

## Purpose
`sources/test-tools/crashmonkey/code/tests/seq1/base.cpp` is a minimal generated `seq1` CrashMonkey test skeleton. It defines a `testName` subclass of `BaseTestCase` with no setup work, no workload operations, and no post-crash checks. It is useful as a template or placeholder, not as a substantive filesystem crash-consistency test.

## Important APIs, Types, and Functions
- `testName::setup()` returns 0 without initializing paths or creating files.
- `testName::run(int checkpoint)` returns 0 without touching `cm_`, calling `CmCheckpoint`, or using the `checkpoint` argument.
- `testName::check_test(...)` returns 0 without inspecting recovered filesystem state or updating `DataTestResult`.
- `test_case_get_instance()` and `test_case_delete_instance()` expose the standard C plugin ABI.
- The file imports POSIX headers, xattr support, `../BaseTestCase.h`, `workload.h`, and `actions.h`; almost all imports are unused in this skeleton.

## Control Flow
The loaded plugin constructs `testName`, then each lifecycle hook immediately succeeds. There are no branches, syscalls, wrapper calls, or checkpoints. Because `run()` never returns `1`, the harness will not see a workload-defined crash point from this file.

## State and Persistence Behavior
No filesystem state is created, modified, synced, or checked. `mnt_dir_`, `filesys_size_`, and `cm_` remain inherited context only. There is no serialized operation stream because no wrapper calls are made.

## Dependencies and Integration Points
The skeleton integrates with the same dynamic loader mechanism as the generated `j-lang` tests. It depends on the parent `tests/BaseTestCase.h` via `../BaseTestCase.h`. It can compile only in a build that supplies the CrashMonkey user-tools API and DataTestResult headers.

## Risks and Edge Cases
Treating this file as a real test would create a false-positive pass: it returns success without covering any crash point or oracle. The generic class name `testName` also means it must not be linked into a shared object with another generated `testName` translation unit unless symbol visibility/build isolation handles that pattern.

## Test Signals
The only useful signal is build and loader plumbing. A successful execution demonstrates that an empty plugin can be instantiated and destroyed, but it does not validate filesystem behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/base.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang1.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang1.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang1.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a file creation/open plus metadata persistence workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; opens `test_path.c_str()` as `fd_test` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_test` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `CmFsync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- opens `test_path.c_str()` as `fd_test` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_test` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.
- closes `fd_test` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a mount-root directory fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 148-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang1.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang10.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang10.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang10.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a directory creation and metadata persistence workload: creates directory `A_path.c_str()` with mode 0777; opens `test_path.c_str()` as `fd_test` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_test` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `test_path.c_str()` as `fd_test` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_test` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_test` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a mount-root directory fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 141-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang10.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang100.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang100.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang100.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 32768, length 32768; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmSync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 32768, length 32768.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 151-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang100.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang101.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang101.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang101.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 0, length 5000; opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_A` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 0, length 5000.
- opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_A` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_A` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a parent directory `A` fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang101.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang102.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang102.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang102.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 0, length 5000; fsyncs `fd_Afoo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 0, length 5000.
- fsyncs `fd_Afoo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 153-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang102.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang103.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang103.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang103.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 0, length 5000; opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_Abar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 0, length 5000.
- opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_Abar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_Abar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang103.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang104.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang104.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang104.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 0, length 5000; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmSync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 0, length 5000.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 151-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang104.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang105.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang105.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang105.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000; opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_A` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000.
- opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_A` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_A` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a parent directory `A` fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang105.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang106.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang106.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang106.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000; fsyncs `fd_Afoo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000.
- fsyncs `fd_Afoo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 153-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang106.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang107.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang107.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang107.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000; opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_Abar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000.
- opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_Abar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_Abar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang107.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang108.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang108.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang108.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmSync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 151-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang108.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang109.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang109.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang109.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 32768, length 32768; opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_A` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 32768, length 32768.
- opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_A` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_A` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a parent directory `A` fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang109.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang110.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang110.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang110.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 32768, length 32768; fsyncs `fd_Afoo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 32768, length 32768.
- fsyncs `fd_Afoo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 153-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang110.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang111.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang111.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang111.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 32768, length 32768; opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_Abar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 32768, length 32768.
- opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_Abar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_Abar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang111.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang112.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang112.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang112.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 32768, length 32768; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmSync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 32768, length 32768.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 151-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang112.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang113.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang113.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang113.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 0, length 5000; opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_A` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 0, length 5000.
- opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_A` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_A` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a parent directory `A` fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang113.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang114.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang114.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang114.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 0, length 5000; fsyncs `fd_Afoo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 0, length 5000.
- fsyncs `fd_Afoo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 153-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang114.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang115.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang115.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang115.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 0, length 5000; opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_Abar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 0, length 5000.
- opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_Abar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_Abar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang115.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang116.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang116.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang116.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 0, length 5000; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmSync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 0, length 5000.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 151-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang116.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang117.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang117.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang117.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000; opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_A` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000.
- opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_A` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_A` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a parent directory `A` fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang117.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang118.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang118.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang118.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000; fsyncs `fd_Afoo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000.
- fsyncs `fd_Afoo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 153-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang118.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang119.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang119.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang119.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000; opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_Abar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000.
- opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_Abar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_Abar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang119.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang120.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang120.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang120.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmSync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 151-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang120.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang121.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang121.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang121.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `0`, offset 32768, length 32768; opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_A` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `0`, offset 32768, length 32768.
- opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_A` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_A` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a parent directory `A` fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang121.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang122.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang122.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang122.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `0`, offset 32768, length 32768; fsyncs `fd_Afoo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `0`, offset 32768, length 32768.
- fsyncs `fd_Afoo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 153-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang122.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang123.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang123.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang123.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `0`, offset 32768, length 32768; opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_Abar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `0`, offset 32768, length 32768.
- opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_Abar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_Abar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang123.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang124.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang124.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang124.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `0`, offset 32768, length 32768; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmSync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `0`, offset 32768, length 32768.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 151-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang124.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang125.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang125.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang125.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `0`, offset 0, length 5000; opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_A` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `0`, offset 0, length 5000.
- opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_A` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_A` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a parent directory `A` fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang125.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang126.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang126.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang126.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `0`, offset 0, length 5000; fsyncs `fd_Afoo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `0`, offset 0, length 5000.
- fsyncs `fd_Afoo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 153-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang126.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang127.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang127.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang127.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `0`, offset 0, length 5000; opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_Abar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `0`, offset 0, length 5000.
- opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_Abar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_Abar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang127.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang128.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang128.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang128.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `0`, offset 0, length 5000; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmSync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `0`, offset 0, length 5000.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 151-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang128.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang129.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang129.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang129.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `0`, offset 30768, length 5000; opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_A` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `0`, offset 30768, length 5000.
- opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_A` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_A` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a parent directory `A` fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang129.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang130.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang130.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang130.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `0`, offset 30768, length 5000; fsyncs `fd_Afoo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `0`, offset 30768, length 5000.
- fsyncs `fd_Afoo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 153-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang130.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang131.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang131.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang131.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `0`, offset 30768, length 5000; opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_Abar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `0`, offset 30768, length 5000.
- opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_Abar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_Abar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang131.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang132.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang132.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang132.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `0`, offset 30768, length 5000; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmSync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `0`, offset 30768, length 5000.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 151-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang132.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang133.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang133.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang133.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; opens `test_path.c_str()` as `fd_test` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_test` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- opens `test_path.c_str()` as `fd_test` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_test` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.
- closes `fd_test` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a mount-root directory fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 154-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang133.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang134.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang134.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang134.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; fsyncs `fd_foo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- fsyncs `fd_foo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 142-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang134.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang135.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang135.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang135.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; opens `bar_path.c_str()` as `fd_bar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_bar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- opens `bar_path.c_str()` as `fd_bar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_bar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.
- closes `fd_bar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 154-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang135.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang136.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang136.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang136.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmSync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 140-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang136.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang137.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang137.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang137.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; writes deterministic data to `fd_foo` at offset 0 for 5000 bytes; opens `test_path.c_str()` as `fd_test` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_test` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_foo` at offset 0 for 5000 bytes.
- opens `test_path.c_str()` as `fd_test` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_test` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.
- closes `fd_test` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a mount-root directory fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 160-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang137.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang138.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang138.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang138.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; writes deterministic data to `fd_foo` at offset 0 for 5000 bytes; fsyncs `fd_foo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_foo` at offset 0 for 5000 bytes.
- fsyncs `fd_foo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 148-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang138.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang139.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang139.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang139.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; writes deterministic data to `fd_foo` at offset 0 for 5000 bytes; opens `bar_path.c_str()` as `fd_bar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_bar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_foo` at offset 0 for 5000 bytes.
- opens `bar_path.c_str()` as `fd_bar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_bar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.
- closes `fd_bar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 160-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang139.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang140.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang140.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang140.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; writes deterministic data to `fd_foo` at offset 0 for 5000 bytes; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmSync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_foo` at offset 0 for 5000 bytes.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 146-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang140.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang141.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang141.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang141.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; writes deterministic data to `fd_foo` at offset 30768 for 5000 bytes; opens `test_path.c_str()` as `fd_test` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_test` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_foo` at offset 30768 for 5000 bytes.
- opens `test_path.c_str()` as `fd_test` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_test` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.
- closes `fd_test` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a mount-root directory fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 160-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang141.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang142.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang142.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang142.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; writes deterministic data to `fd_foo` at offset 30768 for 5000 bytes; fsyncs `fd_foo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_foo` at offset 30768 for 5000 bytes.
- fsyncs `fd_foo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 148-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang142.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang143.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang143.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang143.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; writes deterministic data to `fd_foo` at offset 30768 for 5000 bytes; opens `bar_path.c_str()` as `fd_bar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_bar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_foo` at offset 30768 for 5000 bytes.
- opens `bar_path.c_str()` as `fd_bar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_bar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.
- closes `fd_bar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 160-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang143.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang144.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang144.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang144.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; writes deterministic data to `fd_foo` at offset 30768 for 5000 bytes; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmSync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_foo` at offset 30768 for 5000 bytes.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 146-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang144.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang145.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang145.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang145.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_A` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_A` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_A` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a parent directory `A` fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 159-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang145.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang146.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang146.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang146.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; fsyncs `fd_Afoo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- fsyncs `fd_Afoo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 147-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang146.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang147.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang147.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang147.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_Abar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_Abar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_Abar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 159-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang147.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang148.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang148.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang148.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmSync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 145-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang148.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang149.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang149.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang149.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; writes deterministic data to `fd_Afoo` at offset 0 for 5000 bytes; opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_A` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_Afoo` at offset 0 for 5000 bytes.
- opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_A` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_A` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a parent directory `A` fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang149.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang150.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang150.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang150.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; writes deterministic data to `fd_Afoo` at offset 0 for 5000 bytes; fsyncs `fd_Afoo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_Afoo` at offset 0 for 5000 bytes.
- fsyncs `fd_Afoo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 153-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang150.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang151.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang151.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang151.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; writes deterministic data to `fd_Afoo` at offset 0 for 5000 bytes; opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_Abar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_Afoo` at offset 0 for 5000 bytes.
- opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_Abar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_Abar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang151.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang152.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang152.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang152.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; writes deterministic data to `fd_Afoo` at offset 0 for 5000 bytes; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmSync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_Afoo` at offset 0 for 5000 bytes.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 151-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang152.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang153.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang153.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang153.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; writes deterministic data to `fd_Afoo` at offset 30768 for 5000 bytes; opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_A` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_Afoo` at offset 30768 for 5000 bytes.
- opens `A_path.c_str()` as `fd_A` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_A` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_A` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a parent directory `A` fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang153.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang154.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang154.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang154.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; writes deterministic data to `fd_Afoo` at offset 30768 for 5000 bytes; fsyncs `fd_Afoo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_Afoo` at offset 30768 for 5000 bytes.
- fsyncs `fd_Afoo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 153-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang154.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang155.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang155.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang155.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a deterministic data-write crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; writes deterministic data to `fd_Afoo` at offset 30768 for 5000 bytes; opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_Abar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- writes deterministic data to `fd_Afoo` at offset 30768 for 5000 bytes.
- opens `Abar_path.c_str()` as `fd_Abar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_Abar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.
- closes `fd_Abar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 165-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang155.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang11.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang11.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang11.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a directory creation and metadata persistence workload: creates directory `A_path.c_str()` with mode 0777; creates directory `B_path.c_str()` with mode 0777; opens `B_path.c_str()` as `fd_B` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_B` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- creates directory `B_path.c_str()` with mode 0777.
- opens `B_path.c_str()` as `fd_B` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_B` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_B` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a directory `B` fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 146-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang11.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang12.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang12.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang12.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a directory creation and metadata persistence workload: creates directory `A_path.c_str()` with mode 0777; issues a whole-filesystem `CmSync()` before the checkpoint; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmSync`, `CmCheckpoint`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- issues a whole-filesystem `CmSync()` before the checkpoint.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a whole-filesystem sync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 127-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang12.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang13.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang13.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang13.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_foo` with mode `FALLOC_FL_ZERO_RANGE`, offset 32768, length 32768; opens `test_path.c_str()` as `fd_test` with flags `O_DIRECTORY` and mode `0777`; fsyncs `fd_test` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_foo` with mode `FALLOC_FL_ZERO_RANGE`, offset 32768, length 32768.
- opens `test_path.c_str()` as `fd_test` with flags `O_DIRECTORY` and mode `0777`.
- fsyncs `fd_test` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.
- closes `fd_test` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a mount-root directory fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 160-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang13.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang14.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang14.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang14.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_foo` with mode `FALLOC_FL_ZERO_RANGE`, offset 32768, length 32768; fsyncs `fd_foo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_foo` with mode `FALLOC_FL_ZERO_RANGE`, offset 32768, length 32768.
- fsyncs `fd_foo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 148-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang14.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang15.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang15.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang15.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_foo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_foo` with mode `FALLOC_FL_ZERO_RANGE`, offset 32768, length 32768; opens `bar_path.c_str()` as `fd_bar` with flags `O_RDWR|O_CREAT` and mode `0777`; fsyncs `fd_bar` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - opens `foo_path.c_str()` as `fd_foo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_foo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_foo` with mode `FALLOC_FL_ZERO_RANGE`, offset 32768, length 32768.
- opens `bar_path.c_str()` as `fd_bar` with flags `O_RDWR|O_CREAT` and mode `0777`.
- fsyncs `fd_bar` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_foo` after the checkpoint path.
- closes `fd_bar` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a sibling file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 160-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang15.cpp -->
