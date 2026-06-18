# subset-b-009214 Research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang35.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang35.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_bar` for `/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 30768, 5000)` on `/foo` regular file; opens `/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes `/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`, file `/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `30768..35767` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `30768` length `5000`; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang35.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang36.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang36.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 30768, 5000)` on `/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `30768..35767` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `30768` length `5000`; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang36.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang37.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang37.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_test` for mount-root directory `mnt_dir_`. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 32768, 32768)` on `/foo` regular file; opens mount-root directory `mnt_dir_` with `O_DIRECTORY` and mode `0777`; fsyncs mount-root directory `mnt_dir_`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes mount-root directory `mnt_dir_` after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. punches a sparse hole over bytes `32768..65535` (32768 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on mount-root directory `mnt_dir_` before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `32768` length `32768`; allocation or zeroing beyond the written 32 KiB region while preserving logical size; hole punching may leave sparse extents whose post-crash block accounting differs by filesystem; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang37.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang38.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang38.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 32768, 32768)` on `/foo` regular file; fsyncs `/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. punches a sparse hole over bytes `32768..65535` (32768 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `32768` length `32768`; allocation or zeroing beyond the written 32 KiB region while preserving logical size; hole punching may leave sparse extents whose post-crash block accounting differs by filesystem; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang38.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang39.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang39.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_bar` for `/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 32768, 32768)` on `/foo` regular file; opens `/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes `/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`, file `/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. punches a sparse hole over bytes `32768..65535` (32768 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `32768` length `32768`; allocation or zeroing beyond the written 32 KiB region while preserving logical size; hole punching may leave sparse extents whose post-crash block accounting differs by filesystem; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang39.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang4.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang4.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests metadata persistence for object creation in the mount root. It performs a compact create/fsync-or-sync sequence and records one checkpoint so the permutation engine can crash after the persistence boundary.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around namespace/object-creation metadata; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang4.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang40.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang40.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 32768, 32768)` on `/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. punches a sparse hole over bytes `32768..65535` (32768 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `32768` length `32768`; allocation or zeroing beyond the written 32 KiB region while preserving logical size; hole punching may leave sparse extents whose post-crash block accounting differs by filesystem; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang40.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang41.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang41.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_test` for mount-root directory `mnt_dir_`. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 0, 5000)` on `/foo` regular file; opens mount-root directory `mnt_dir_` with `O_DIRECTORY` and mode `0777`; fsyncs mount-root directory `mnt_dir_`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes mount-root directory `mnt_dir_` after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. punches a sparse hole over bytes `0..4999` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on mount-root directory `mnt_dir_` before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `0` length `5000`; hole punching may leave sparse extents whose post-crash block accounting differs by filesystem; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang41.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang42.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang42.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 0, 5000)` on `/foo` regular file; fsyncs `/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. punches a sparse hole over bytes `0..4999` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `0` length `5000`; hole punching may leave sparse extents whose post-crash block accounting differs by filesystem; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang42.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang43.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang43.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_bar` for `/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 0, 5000)` on `/foo` regular file; opens `/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes `/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`, file `/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. punches a sparse hole over bytes `0..4999` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `0` length `5000`; hole punching may leave sparse extents whose post-crash block accounting differs by filesystem; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang43.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang44.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang44.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 0, 5000)` on `/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. punches a sparse hole over bytes `0..4999` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `0` length `5000`; hole punching may leave sparse extents whose post-crash block accounting differs by filesystem; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang44.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang45.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang45.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_test` for mount-root directory `mnt_dir_`. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 30768, 5000)` on `/foo` regular file; opens mount-root directory `mnt_dir_` with `O_DIRECTORY` and mode `0777`; fsyncs mount-root directory `mnt_dir_`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes mount-root directory `mnt_dir_` after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. punches a sparse hole over bytes `30768..35767` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on mount-root directory `mnt_dir_` before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `30768` length `5000`; hole punching may leave sparse extents whose post-crash block accounting differs by filesystem; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang45.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang46.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang46.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 30768, 5000)` on `/foo` regular file; fsyncs `/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. punches a sparse hole over bytes `30768..35767` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `30768` length `5000`; hole punching may leave sparse extents whose post-crash block accounting differs by filesystem; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang46.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang47.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang47.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_bar` for `/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 30768, 5000)` on `/foo` regular file; opens `/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes `/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`, file `/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. punches a sparse hole over bytes `30768..35767` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `30768` length `5000`; hole punching may leave sparse extents whose post-crash block accounting differs by filesystem; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang47.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang48.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang48.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 30768, 5000)` on `/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. punches a sparse hole over bytes `30768..35767` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` at offset `30768` length `5000`; hole punching may leave sparse extents whose post-crash block accounting differs by filesystem; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang48.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang49.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang49.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_KEEP_SIZE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_test` for mount-root directory `mnt_dir_`. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_KEEP_SIZE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_KEEP_SIZE, 32768, 32768)` on `/foo` regular file; opens mount-root directory `mnt_dir_` with `O_DIRECTORY` and mode `0777`; fsyncs mount-root directory `mnt_dir_`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes mount-root directory `mnt_dir_` after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. allocates blocks while preserving the visible file size over bytes `32768..65535` (32768 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on mount-root directory `mnt_dir_` before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_KEEP_SIZE` at offset `32768` length `32768`; allocation or zeroing beyond the written 32 KiB region while preserving logical size; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang49.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang5.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang5.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests metadata persistence for object creation inside subdirectory `/A`. It performs a compact create/fsync-or-sync sequence and records one checkpoint so the permutation engine can crash after the persistence boundary.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_A` for `/A` directory. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; opens `/A` directory with `O_DIRECTORY` and mode `0777`; fsyncs `/A` directory; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A` directory after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. `CmFsync()` is issued on `/A` directory before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around namespace/object-creation metadata; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang5.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang50.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang50.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_KEEP_SIZE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_KEEP_SIZE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_KEEP_SIZE, 32768, 32768)` on `/foo` regular file; fsyncs `/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. allocates blocks while preserving the visible file size over bytes `32768..65535` (32768 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_KEEP_SIZE` at offset `32768` length `32768`; allocation or zeroing beyond the written 32 KiB region while preserving logical size; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang50.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang51.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang51.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_KEEP_SIZE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_bar` for `/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_KEEP_SIZE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_KEEP_SIZE, 32768, 32768)` on `/foo` regular file; opens `/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes `/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`, file `/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. allocates blocks while preserving the visible file size over bytes `32768..65535` (32768 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_KEEP_SIZE` at offset `32768` length `32768`; allocation or zeroing beyond the written 32 KiB region while preserving logical size; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang51.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang52.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang52.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_KEEP_SIZE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_KEEP_SIZE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_KEEP_SIZE, 32768, 32768)` on `/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. allocates blocks while preserving the visible file size over bytes `32768..65535` (32768 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_KEEP_SIZE` at offset `32768` length `32768`; allocation or zeroing beyond the written 32 KiB region while preserving logical size; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang52.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang53.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang53.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_KEEP_SIZE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_test` for mount-root directory `mnt_dir_`. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_KEEP_SIZE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_KEEP_SIZE, 0, 5000)` on `/foo` regular file; opens mount-root directory `mnt_dir_` with `O_DIRECTORY` and mode `0777`; fsyncs mount-root directory `mnt_dir_`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes mount-root directory `mnt_dir_` after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. allocates blocks while preserving the visible file size over bytes `0..4999` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on mount-root directory `mnt_dir_` before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_KEEP_SIZE` at offset `0` length `5000`; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang53.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang54.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang54.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_KEEP_SIZE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_KEEP_SIZE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_KEEP_SIZE, 0, 5000)` on `/foo` regular file; fsyncs `/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. allocates blocks while preserving the visible file size over bytes `0..4999` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_KEEP_SIZE` at offset `0` length `5000`; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang54.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang55.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang55.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_KEEP_SIZE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_bar` for `/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_KEEP_SIZE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_KEEP_SIZE, 0, 5000)` on `/foo` regular file; opens `/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes `/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`, file `/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. allocates blocks while preserving the visible file size over bytes `0..4999` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_KEEP_SIZE` at offset `0` length `5000`; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang55.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang56.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang56.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_KEEP_SIZE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_KEEP_SIZE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_KEEP_SIZE, 0, 5000)` on `/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. allocates blocks while preserving the visible file size over bytes `0..4999` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_KEEP_SIZE` at offset `0` length `5000`; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang56.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang57.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang57.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_KEEP_SIZE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_test` for mount-root directory `mnt_dir_`. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_KEEP_SIZE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_KEEP_SIZE, 30768, 5000)` on `/foo` regular file; opens mount-root directory `mnt_dir_` with `O_DIRECTORY` and mode `0777`; fsyncs mount-root directory `mnt_dir_`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes mount-root directory `mnt_dir_` after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. allocates blocks while preserving the visible file size over bytes `30768..35767` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on mount-root directory `mnt_dir_` before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_KEEP_SIZE` at offset `30768` length `5000`; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang57.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang58.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang58.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_KEEP_SIZE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_KEEP_SIZE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_KEEP_SIZE, 30768, 5000)` on `/foo` regular file; fsyncs `/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. allocates blocks while preserving the visible file size over bytes `30768..35767` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_KEEP_SIZE` at offset `30768` length `5000`; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang58.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang59.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang59.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_KEEP_SIZE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_bar` for `/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_KEEP_SIZE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_KEEP_SIZE, 30768, 5000)` on `/foo` regular file; opens `/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes `/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`, file `/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. allocates blocks while preserving the visible file size over bytes `30768..35767` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_KEEP_SIZE` at offset `30768` length `5000`; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang59.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang6.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang6.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests metadata persistence for object creation inside subdirectory `/A`. It performs a compact create/fsync-or-sync sequence and records one checkpoint so the permutation engine can crash after the persistence boundary.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/A/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. `CmFsync()` is issued on `/A/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around namespace/object-creation metadata; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang6.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang60.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang60.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_KEEP_SIZE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_KEEP_SIZE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_KEEP_SIZE, 30768, 5000)` on `/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. allocates blocks while preserving the visible file size over bytes `30768..35767` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_KEEP_SIZE` at offset `30768` length `5000`; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang60.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang61.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang61.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `0` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_test` for mount-root directory `mnt_dir_`. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `0`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(0, 32768, 32768)` on `/foo` regular file; opens mount-root directory `mnt_dir_` with `O_DIRECTORY` and mode `0777`; fsyncs mount-root directory `mnt_dir_`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes mount-root directory `mnt_dir_` after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. preallocates/extends blocks using default `fallocate` mode over bytes `32768..65535` (32768 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on mount-root directory `mnt_dir_` before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `0` at offset `32768` length `32768`; default fallocate may extend the file and allocate unwritten extents; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang61.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang62.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang62.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `0` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `0`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(0, 32768, 32768)` on `/foo` regular file; fsyncs `/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. preallocates/extends blocks using default `fallocate` mode over bytes `32768..65535` (32768 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `0` at offset `32768` length `32768`; default fallocate may extend the file and allocate unwritten extents; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang62.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang63.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang63.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `0` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_bar` for `/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `0`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(0, 32768, 32768)` on `/foo` regular file; opens `/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes `/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`, file `/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. preallocates/extends blocks using default `fallocate` mode over bytes `32768..65535` (32768 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `0` at offset `32768` length `32768`; default fallocate may extend the file and allocate unwritten extents; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang63.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang64.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang64.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `0` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `0`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(0, 32768, 32768)` on `/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. preallocates/extends blocks using default `fallocate` mode over bytes `32768..65535` (32768 bytes); the call may extend the file size if the range reaches beyond EOF. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `0` at offset `32768` length `32768`; default fallocate may extend the file and allocate unwritten extents; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang64.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang65.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang65.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `0` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_test` for mount-root directory `mnt_dir_`. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `0`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(0, 0, 5000)` on `/foo` regular file; opens mount-root directory `mnt_dir_` with `O_DIRECTORY` and mode `0777`; fsyncs mount-root directory `mnt_dir_`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes mount-root directory `mnt_dir_` after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. preallocates/extends blocks using default `fallocate` mode over bytes `0..4999` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on mount-root directory `mnt_dir_` before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `0` at offset `0` length `5000`; default fallocate may extend the file and allocate unwritten extents; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang65.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang66.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang66.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `0` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `0`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(0, 0, 5000)` on `/foo` regular file; fsyncs `/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. preallocates/extends blocks using default `fallocate` mode over bytes `0..4999` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `0` at offset `0` length `5000`; default fallocate may extend the file and allocate unwritten extents; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang66.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang67.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang67.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `0` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_bar` for `/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `0`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(0, 0, 5000)` on `/foo` regular file; opens `/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes `/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`, file `/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. preallocates/extends blocks using default `fallocate` mode over bytes `0..4999` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `0` at offset `0` length `5000`; default fallocate may extend the file and allocate unwritten extents; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang67.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang68.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang68.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `0` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `0`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(0, 0, 5000)` on `/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. preallocates/extends blocks using default `fallocate` mode over bytes `0..4999` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `0` at offset `0` length `5000`; default fallocate may extend the file and allocate unwritten extents; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang68.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang69.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang69.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `0` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_test` for mount-root directory `mnt_dir_`. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `0`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(0, 30768, 5000)` on `/foo` regular file; opens mount-root directory `mnt_dir_` with `O_DIRECTORY` and mode `0777`; fsyncs mount-root directory `mnt_dir_`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes mount-root directory `mnt_dir_` after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. preallocates/extends blocks using default `fallocate` mode over bytes `30768..35767` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on mount-root directory `mnt_dir_` before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `0` at offset `30768` length `5000`; default fallocate may extend the file and allocate unwritten extents; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang69.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang7.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang7.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests metadata persistence for object creation inside subdirectory `/A`. It performs a compact create/fsync-or-sync sequence and records one checkpoint so the permutation engine can crash after the persistence boundary.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_Abar` for `/A/bar` regular file. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; opens `/A/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/A/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`, file `/A/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. `CmFsync()` is issued on `/A/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around namespace/object-creation metadata; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang7.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang70.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang70.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `0` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `0`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(0, 30768, 5000)` on `/foo` regular file; fsyncs `/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. preallocates/extends blocks using default `fallocate` mode over bytes `30768..35767` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `0` at offset `30768` length `5000`; default fallocate may extend the file and allocate unwritten extents; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang70.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang71.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang71.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `0` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file, `fd_bar` for `/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `0`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(0, 30768, 5000)` on `/foo` regular file; opens `/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path; closes `/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`, file `/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. preallocates/extends blocks using default `fallocate` mode over bytes `30768..35767` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `0` at offset `30768` length `5000`; default fallocate may extend the file and allocate unwritten extents; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang71.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang72.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang72.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `0` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `0`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(0, 30768, 5000)` on `/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. preallocates/extends blocks using default `fallocate` mode over bytes `30768..35767` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `0` at offset `30768` length `5000`; default fallocate may extend the file and allocate unwritten extents; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang72.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang73.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang73.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_A` for `/A` directory. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE, 32768, 32768)` on `/A/foo` regular file; opens `/A` directory with `O_DIRECTORY` and mode `0777`; fsyncs `/A` directory; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A` directory after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `32768..65535` (32768 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/A` directory before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE` at offset `32768` length `32768`; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang73.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang74.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang74.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE, 32768, 32768)` on `/A/foo` regular file; fsyncs `/A/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `32768..65535` (32768 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/A/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE` at offset `32768` length `32768`; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang74.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang75.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang75.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_Abar` for `/A/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE, 32768, 32768)` on `/A/foo` regular file; opens `/A/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/A/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`, file `/A/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `32768..65535` (32768 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/A/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE` at offset `32768` length `32768`; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang75.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang76.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang76.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE, 32768, 32768)` on `/A/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `32768..65535` (32768 bytes); the call may extend the file size if the range reaches beyond EOF. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE` at offset `32768` length `32768`; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang76.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang77.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang77.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_A` for `/A` directory. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE, 0, 5000)` on `/A/foo` regular file; opens `/A` directory with `O_DIRECTORY` and mode `0777`; fsyncs `/A` directory; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A` directory after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `0..4999` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/A` directory before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE` at offset `0` length `5000`; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang77.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang78.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang78.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE, 0, 5000)` on `/A/foo` regular file; fsyncs `/A/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `0..4999` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/A/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE` at offset `0` length `5000`; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang78.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang79.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang79.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_Abar` for `/A/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE, 0, 5000)` on `/A/foo` regular file; opens `/A/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/A/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`, file `/A/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `0..4999` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/A/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE` at offset `0` length `5000`; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang79.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang8.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang8.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests metadata persistence for object creation inside subdirectory `/A`. It performs a compact create/fsync-or-sync sequence and records one checkpoint so the permutation engine can crash after the persistence boundary.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around namespace/object-creation metadata; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang8.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang80.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang80.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE, 0, 5000)` on `/A/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `0..4999` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE` at offset `0` length `5000`; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang80.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang81.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang81.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_A` for `/A` directory. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE, 30768, 5000)` on `/A/foo` regular file; opens `/A` directory with `O_DIRECTORY` and mode `0777`; fsyncs `/A` directory; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A` directory after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `30768..35767` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/A` directory before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE` at offset `30768` length `5000`; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang81.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang82.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang82.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE, 30768, 5000)` on `/A/foo` regular file; fsyncs `/A/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `30768..35767` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/A/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE` at offset `30768` length `5000`; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang82.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang83.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang83.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_Abar` for `/A/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE, 30768, 5000)` on `/A/foo` regular file; opens `/A/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/A/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`, file `/A/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `30768..35767` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmFsync()` is issued on `/A/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE` at offset `30768` length `5000`; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang83.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang84.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang84.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE, 30768, 5000)` on `/A/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `30768..35767` (5000 bytes); the call may extend the file size if the range reaches beyond EOF. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE` at offset `30768` length `5000`; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang84.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang85.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang85.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_A` for `/A` directory. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 32768, 32768)` on `/A/foo` regular file; opens `/A` directory with `O_DIRECTORY` and mode `0777`; fsyncs `/A` directory; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A` directory after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `32768..65535` (32768 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/A` directory before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `32768` length `32768`; allocation or zeroing beyond the written 32 KiB region while preserving logical size; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang85.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang86.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang86.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 32768, 32768)` on `/A/foo` regular file; fsyncs `/A/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `32768..65535` (32768 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/A/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `32768` length `32768`; allocation or zeroing beyond the written 32 KiB region while preserving logical size; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang86.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang87.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang87.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_Abar` for `/A/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 32768, 32768)` on `/A/foo` regular file; opens `/A/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/A/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`, file `/A/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `32768..65535` (32768 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/A/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `32768` length `32768`; allocation or zeroing beyond the written 32 KiB region while preserving logical size; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang87.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang88.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang88.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `32768` for `32768` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, offset `32768`, and length `32768`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 32768, 32768)` on `/A/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `32768..65535` (32768 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `32768` length `32768`; allocation or zeroing beyond the written 32 KiB region while preserving logical size; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang88.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang89.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang89.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_A` for `/A` directory. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 0, 5000)` on `/A/foo` regular file; opens `/A` directory with `O_DIRECTORY` and mode `0777`; fsyncs `/A` directory; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A` directory after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `0..4999` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/A` directory before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `0` length `5000`; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang89.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang9.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang9.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests metadata persistence for object creation inside subdirectory `/A`. It performs a compact create/fsync-or-sync sequence and records one checkpoint so the permutation engine can crash after the persistence boundary.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_A` for `/A` directory. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A` directory with `O_DIRECTORY` and mode `0777`; fsyncs `/A` directory; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A` directory after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. `CmFsync()` is issued on `/A` directory before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around namespace/object-creation metadata; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang9.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang90.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang90.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 0, 5000)` on `/A/foo` regular file; fsyncs `/A/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `0..4999` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/A/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `0` length `5000`; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang90.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang91.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang91.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_Abar` for `/A/bar` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 0, 5000)` on `/A/foo` regular file; opens `/A/bar` regular file with `O_RDWR|O_CREAT` and mode `0777`; fsyncs `/A/bar` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A/bar` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`, file `/A/bar`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `0..4999` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/A/bar` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `0` length `5000`; the fsync targets a sibling file, intentionally leaving the modified file without direct fsync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang91.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang92.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang92.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `0` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, offset `0`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 0, 5000)` on `/A/foo` regular file; runs `CmSync()`; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `0..4999` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmSync()` is the durability primitive, forcing a global sync after the workload setup and before the checkpoint. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `0` length `5000`; global sync makes the workload stronger than file-local fsync and may hide ordering bugs that require narrower flushes; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang92.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang93.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang93.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_A` for `/A` directory. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 30768, 5000)` on `/A/foo` regular file; opens `/A` directory with `O_DIRECTORY` and mode `0777`; fsyncs `/A` directory; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A` directory after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `30768..35767` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/A` directory before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `30768` length `5000`; directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang93.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang94.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang94.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update inside subdirectory `/A`. It combines file creation, a deterministic data write when present, and `fallocate` on /A/foo before a single checkpoint; the allocation variant is `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/A/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 30768, 5000)` on `/A/foo` regular file; fsyncs `/A/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/A/foo`. converts the byte range to zeros while exercising zero-range extent handling over bytes `30768..35767` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/A/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE` at offset `30768` length `5000`; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang94.cpp -->
