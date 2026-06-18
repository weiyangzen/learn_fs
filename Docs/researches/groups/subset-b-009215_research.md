# subset-b-009215 research

Grouped research report for CrashMonkey generated workloads, user-tool APIs, utility classes, VM orchestration scripts, XFSMonkey runner code, and two Cthon04 build files. Each section title preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang95.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang95.cpp

Purpose: ACE-generated CrashMonkey workload that creates directory `A`, writes 32 KiB of deterministic data to `A/foo`, zeroes a 5,000-byte range near the end with `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, creates `A/bar`, fsyncs `A/bar`, and records a CrashMonkey checkpoint. It is meant to exercise persistence behavior around sparse/zero-range data operations plus an unrelated synced file in the same directory.

Important APIs/types/functions: `BaseTestCase`, `RecordCmFsOps` through `cm_`, `WriteData`, `fallocate`, `CmOpen`, `CmFsync`, `CmCheckpoint`, `CmClose`, and plugin exports `test_case_get_instance`/`test_case_delete_instance`. The class stores canonical workload paths for root, `A`, `A/C`, `B`, and several file names, although only `A`, `A/foo`, and `A/bar` are active.

Control flow: `setup` initializes paths only. `run` recreates those paths, makes `A`, opens and writes `A/foo`, performs zero-range keep-size fallocate, creates `A/bar`, fsyncs `A/bar`, calls `CmCheckpoint`, optionally exits at checkpoint `1`, then closes both descriptors. `check_test` only resets paths and reports success, so semantic checking is delegated to the CrashMonkey replay/diff harness.

State/persistence behavior: recorded state includes directory creation, file creation, data write, zero-range extent change, fsync of a sibling file, and checkpoint marker. The test intentionally asks whether the checkpoint/replay machinery and target filesystem preserve the state implied by the ordering, not whether this file independently validates bytes.

Dependencies/integration: depends on the crash harness loading the shared object, `BaseTestCase::mnt_dir_`, user-tool wrappers, Linux fallocate flags, and external diff generation. Risks/test signals: no local oracle in `check_test`, direct `mkdir`/`fallocate` calls bypass some wrapper recording, and error paths sometimes close invalid descriptors; failures surface as harness errors or diff artifacts after replay.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang95.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang96.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang96.cpp

Purpose: ACE-generated workload that creates `A/foo`, writes 32 KiB, zeroes a keep-size range starting at byte 30,768, then issues a whole-system sync before the CrashMonkey checkpoint. It isolates zero-range persistence when global sync, rather than file or directory fsync, is the durability signal before crash-state enumeration.

Important APIs/types/functions: `BaseTestCase`, `WriteData`, `CmOpen`, `CmSync`, `CmCheckpoint`, `CmClose`, Linux `fallocate`, and the dynamic loader exports. The path fields mirror the other generated `seq1` workloads and provide a stable naming convention used by generated code.

Control flow: `setup` records mount-relative names; `run` creates directory `A`, opens `A/foo`, writes a deterministic 32 KiB range, calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 30768, 5000)`, calls `cm_->CmSync()`, records one checkpoint, optionally returns at checkpoint `1`, and closes the file. `check_test` performs no direct checks.

State/persistence behavior: the workload combines data writes, extent zeroing, global sync, and a checkpoint marker. The global sync becomes a `DiskMod::kSyncMod` through the wrapper, so replay logic can distinguish it from fsync/fdatasync and sync-file-range.

Dependencies/integration: requires kernel fallocate zero-range support, user-tool checkpoint IPC, and CrashMonkey diff comparison. Risks/test signals: the fallocate call is direct rather than `CmFallocate`, so wrapper metadata may not capture the range in the user-level mod list; the test is still useful when block-level logging observes the actual IO.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang96.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang97.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang97.cpp

Purpose: ACE-generated workload for hole punching under a directory fsync. It creates `A/foo`, writes 32 KiB, punches a keep-size 32 KiB hole starting at byte 32,768, opens directory `A`, fsyncs the directory, and records a checkpoint.

Important APIs/types/functions: `BaseTestCase`, `WriteData`, `CmOpen`, `CmFsync`, `CmCheckpoint`, direct `mkdir` and `fallocate`, and dynamic test-case factory exports. It uses `O_DIRECTORY` to obtain a directory descriptor for `A`.

Control flow: `setup` initializes mount-relative paths. `run` makes `A`, creates/writes `A/foo`, calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 32768, 32768)`, opens `A` as a directory, fsyncs that directory descriptor, checkpoint-exits if requested, then closes file and directory descriptors. `check_test` is a no-op path reset.

State/persistence behavior: the key durable state is a punched sparse range and directory fsync before the checkpoint. The workload targets filesystem behavior where directory fsync may persist namespace metadata but not necessarily file extent contents.

Dependencies/integration: needs Linux hole-punch support and a filesystem that permits directory fsync. Risks/test signals: local validation is absent; direct fallocate is not wrapper-recorded; if directory fsync is unsupported on a target filesystem the workload returns `errno` and is reported as harness failure rather than content mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang97.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang98.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang98.cpp

Purpose: ACE-generated workload that tests hole punching followed by fsync of the modified file itself. It creates `A/foo`, writes 32 KiB, punches a 32 KiB keep-size hole beyond the original write range, fsyncs `A/foo`, then records a checkpoint.

Important APIs/types/functions: `BaseTestCase`, `WriteData`, `CmOpen`, `CmFsync`, `CmCheckpoint`, `CmClose`, and direct Linux `fallocate`. Factory functions expose the class to `ClassLoader`.

Control flow: after path initialization, `run` creates `A`, opens `A/foo`, writes deterministic data, performs `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, fsyncs the file descriptor, takes a checkpoint, optionally exits at checkpoint `1`, and closes the descriptor. `check_test` resets paths and returns success.

State/persistence behavior: the file fsync is the explicit persistence boundary for both data and extent metadata, followed by CrashMonkey checkpointing. This contrasts with sibling generated tests that use global sync, sibling-file fsync, or directory fsync.

Dependencies/integration: uses crash harness replay, Linux fallocate flags, and external diffing. Risks/test signals: fallocate bypasses `CmFallocate`, check logic is external, and the punched range begins at EOF for a 32 KiB file, so behavior may largely reflect allocation/metadata side effects rather than visible file bytes.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang98.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang99.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang99.cpp

Purpose: ACE-generated workload pairing hole punching on `A/foo` with creation and fsync of a separate `A/bar` before checkpoint. It explores whether syncing a sibling file leaves the hole-punch and file creation state vulnerable across simulated crashes.

Important APIs/types/functions: `BaseTestCase`, `WriteData`, `CmOpen`, `CmFsync`, `CmCheckpoint`, `CmClose`, direct `mkdir` and `fallocate`, plus plugin factory exports. It uses the same path inventory as adjacent `j-lang` cases.

Control flow: `run` creates `A`, opens/writes `A/foo`, punches a keep-size hole, creates `A/bar`, fsyncs `A/bar`, checkpoints, optionally stops at checkpoint `1`, and closes both descriptors. `setup` and `check_test` only populate path strings.

State/persistence behavior: logged state includes namespace creation, data write, extent mutation, sibling file creation, fsync, and checkpoint. The intended persistence question is whether fsync on `A/bar` interacts with directory or inode ordering for `A/foo`.

Dependencies/integration: loaded by the C++ harness and evaluated by CrashMonkey diff files. Risks/test signals: no in-test data oracle, direct syscalls bypass the recording wrapper for mkdir/fallocate, and semantics vary by filesystem journaling and delayed allocation behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang99.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/sub_dir_mmap.cpp -->
# sources/test-tools/crashmonkey/code/tests/sub_dir_mmap.cpp

Purpose: handwritten CrashMonkey workload that writes one 1 KiB random payload into a file under a synced subdirectory using `mmap`. It verifies, after crash/replay, that file metadata and byte contents match the generated random buffer.

Important APIs/types/functions: `BaseTestCase`, `DataTestResult`, `mkdir`, `open`, `fsync`, `/dev/urandom`, `ftruncate`, `mmap`, `memcpy`, `munmap`, `stat`, `read`, `memcmp`, and factory exports. Constants fix `/mnt/snapshot/test_dir`, one `test_file0`, 0777 permissions, and 1 KiB data size.

Control flow: `setup` creates and fsyncs the directory and fills `text` from `/dev/urandom`. `run` creates/truncates each test file, maps it shared writable, copies `text`, unmaps, closes, and returns `1` to signal a checkpoint boundary. `check_test` stats each file, validates type and permissions, reads exactly 1 KiB, and compares bytes to `text`.

State/persistence behavior: setup persists the directory before the test operation; the test write is through shared mmap without explicit msync. The oracle expects the file to exist with correct mode and full random contents after the tested crash state.

Dependencies/integration: assumes `/mnt/snapshot`, POSIX mmap, readable `/dev/urandom`, and CrashMonkey's BaseTestCase lifecycle preserving the in-memory `text` for checking. Risks/test signals: no `msync` means success can depend on implicit writeback timing; `if (file_data <= 0)` is a weak mmap failure check compared with `MAP_FAILED`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/sub_dir_mmap.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/sub_dir_odirect.cpp -->
# sources/test-tools/crashmonkey/code/tests/sub_dir_odirect.cpp

Purpose: handwritten workload that writes one 1 KiB random payload into a file under a synced subdirectory using `O_DIRECT`. It tests direct-IO persistence and later validates file mode and data.

Important APIs/types/functions: `BaseTestCase`, `DataTestResult`, `mkdir`, directory `fsync`, `/dev/urandom`, `posix_memalign`, `open(...|O_DIRECT)`, 512-byte aligned `write`, `stat`, `read`, `memcmp`, and plugin exports. Constants use 1 KiB test data and 512-byte alignment.

Control flow: `setup` creates/fsyncs `test_dir` and fills `text`. `run` allocates aligned memory, copies `text`, creates `test_file0` with `O_DIRECT`, writes two 512-byte chunks until 1 KiB is written, closes, frees, and returns `1`. `check_test` stats the file, validates regular-file permissions, reads the full file, and compares data.

State/persistence behavior: direct writes bypass page cache, so the operation probes block-device and filesystem direct-IO ordering. Directory creation is synced separately; the file's data write has no explicit fsync after close.

Dependencies/integration: requires a filesystem/device accepting 512-byte aligned direct writes of 1 KiB. Risks/test signals: partial writes are handled, but allocation failure check uses `< 0` even though `posix_memalign` returns positive errno values on failure; failure modes are reported through `DataTestResult`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/sub_dir_odirect.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/sync_file_range_inconsistency.cpp -->
# sources/test-tools/crashmonkey/code/tests/sync_file_range_inconsistency.cpp

Purpose: generated/handwritten CrashMonkey workload for a suspected `sync_file_range` inconsistency. It creates `A/foo`, preallocates/zeroes 8 KiB, syncs, checkpoints, writes 4 KiB at offset 4096, calls `sync_file_range` with wait/write flags, then checkpoints again.

Important APIs/types/functions: `BaseTestCase`, `WriteData`, `CmOpen`, `CmSync`, `CmSyncFileRange`, `CmCheckpoint`, `CmClose`, `fallocate`, and `SYNC_FILE_RANGE_WAIT_BEFORE|WRITE|WAIT_AFTER`. It includes a commented `CmFdatasync` alternative, documenting that the range sync is the behavior under test.

Control flow: `setup` initializes paths. `run` creates directory `A`, opens `A/foo`, zero-ranges 8 KiB, global-syncs, records checkpoint 1, optionally exits, writes 4 KiB into the second page, calls `CmSyncFileRange` for that page, records checkpoint 2, closes, and returns `1` if the caller requested the second checkpoint. `check_test` is a no-op.

State/persistence behavior: the two checkpoint boundaries separate initial preallocation from later range-flushed data. The wrapper records `kSyncFileRangeMod` with offset, length, path, and post-stat metadata but no data payload.

Dependencies/integration: relies on Linux `sync_file_range`, CrashMonkey checkpoint IPC, and external diffing. Risks/test signals: no local oracle, direct fallocate bypasses wrapper recording, and `sync_file_range` durability semantics are intentionally subtle and filesystem/kernel dependent.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/sync_file_range_inconsistency.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/test_get_log_ent_size.c -->
# sources/test-tools/crashmonkey/code/tests/test_get_log_ent_size.c

Purpose: tiny C helper that creates `/mnt/snapshot/test_file` and writes a fixed string, apparently for exercising or estimating log-entry sizes in the disk-wrapper/high-water-mark module. It assumes the kernel module is loaded and running.

Important APIs/types/functions: `open`, `write`, `close`, `strlen`, `printf`, and constants `TEXT` and `TEST_FILE`. It includes ioctl/stat headers but does not actually issue ioctls.

Control flow: `main` opens the test file with `O_RDWR|O_CREAT`, writes until the fixed string length is reached, closes, and returns 0; on open/write failure it prints a message, closes if needed, and returns -1. The `fsync` call is present but commented out.

State/persistence behavior: creates or updates one file under `/mnt/snapshot`; without fsync, persistence is left to normal kernel writeback and any active logging module. Dependencies/integration: likely run manually or by harness code outside the shared-object workload loader.

Risks/test signals: the write loop assigns `written = write(...)` rather than accumulating bytes, so partial writes can produce incorrect offsets or loops; file mode is omitted for `O_CREAT`, which is undefined for the three-argument `open` contract.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/test_get_log_ent_size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/api/actions.h -->
# sources/test-tools/crashmonkey/code/user_tools/api/actions.h

Purpose: public user-tool API header declaring `Checkpoint()`, the small operation workloads call to ask the CrashMonkey harness to mark a checkpoint in the disk log. It is the C++ facade used by generated workloads and the `cm_checkpoint` CLI.

Important APIs/types/functions: namespace `fs_testing::user_tools::api` and function `int Checkpoint()`. The header has only include guards and no dependencies beyond namespace declarations.

Control flow: none in the header; implementation lives in `src/actions.cpp`, where `Checkpoint` sends a socket command and waits for `kCheckpointDone`. State/persistence behavior: calling this API records harness state rather than directly mutating the filesystem.

Dependencies/integration: integrated by `wrapper.cpp`, generated tests, and `cm_checkpoint.cpp`. Risks/test signals: its return contract is integer-only and does not expose detailed socket or harness failure causes.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/api/actions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/api/workload.h -->
# sources/test-tools/crashmonkey/code/user_tools/api/workload.h

Purpose: public API for deterministic workload data writes. It declares direct `pwrite` and mmap/msync helpers used by tests to write known byte patterns at specified file offsets.

Important APIs/types/functions: `int WriteData(int fd, unsigned int offset, unsigned int size)` and `int WriteDataMmap(int fd, unsigned int offset, unsigned int size)` in `fs_testing::user_tools::api`. Comments define return values as 0 on success and -1 on error.

Control flow: implementation in `src/workload.cpp` generates a 4 KiB repeated test-data block, handles unaligned starts and trailing partial pages, and either uses `pwrite` loops or mmap/memcpy/msync. State/persistence behavior: these helpers mutate an already-open file and, for mmap, explicitly call `msync(MS_SYNC)`.

Dependencies/integration: used by generated C++ workloads and WorkloadTest. Risks/test signals: offset/size are `unsigned int`, limiting very large writes; the API does not accept caller-provided data, so all tests share one deterministic pattern.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/api/workload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/api/wrapper.h -->
# sources/test-tools/crashmonkey/code/user_tools/api/wrapper.h

Purpose: central user-tool wrapper interface for filesystem operations. It abstracts raw POSIX/syscall functions behind `FsFns`, records mutations as `DiskMod` objects in `RecordCmFsOps`, and offers `PassthroughCmFsOps` for execution without recording.

Important APIs/types/functions: abstract `FsFns`, concrete `DefaultFsFns`, abstract `CmFsOps`, recording `RecordCmFsOps`, passthrough `PassthroughCmFsOps`, fd-to-path map `fd_map_`, mmap tracking map `mmap_map_`, `mods_`, `Serialize`, `CmOpenCommon`, and `WriteWhole`. The API covers mknod/mkdir/open/lseek/write/pwrite/mmap/msync/munmap/fallocate/close/rename/unlink/remove/fsync/fdatasync/sync/sync_file_range/checkpoint.

Control flow: callers use the `Cm*` interface. `RecordCmFsOps` forwards to `FsFns`, records relevant metadata/data into `DiskMod`, and serializes the mod stream; `PassthroughCmFsOps` simply delegates to `FsFns`. The header exposes protected internals for tests.

State/persistence behavior: records create, truncate, data, metadata, mmap, fallocate, fsync, sync, sync-file-range, and checkpoint intent, plus maps open descriptors to paths and writable shared mmaps to file ranges. Dependencies/integration: depends on POSIX headers and `DiskMod`; used by generated tests, harness code, and gtests.

Risks/test signals: the abstraction is broad and manually maintained; unsupported syscalls or direct syscalls in tests bypass recording. Tests in `CmFsOpsTest.cpp` cover many but not all operations, especially rename and fallocate corner cases.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/api/wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/begin_log.cpp -->
# sources/test-tools/crashmonkey/code/user_tools/begin_log.cpp

Purpose: command-line shim that tells the CrashMonkey harness to begin logging. It is a small executable front-end around the socket command sender.

Important APIs/types/functions: `ClientCommandSender`, `kSocketNameOutbound`, `SocketMessage::kBeginLog`, and expected reply `kBeginLogDone`. `main` ignores CLI arguments.

Control flow: constructs a command sender for `/tmp/crash_monkey_harness`, sends `kBeginLog`, waits for `kBeginLogDone`, and returns the sender's status. State/persistence behavior: no filesystem mutation directly; it changes harness logging state.

Dependencies/integration: used by scripts or harness phases that need to bracket logging. Risks/test signals: failure detail is collapsed into numeric exit codes from `ClientCommandSender::Run`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/begin_log.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/begin_tests.cpp -->
# sources/test-tools/crashmonkey/code/user_tools/begin_tests.cpp

Purpose: command-line shim that asks the harness to run loaded tests. It wraps one socket command and expected acknowledgement.

Important APIs/types/functions: `ClientCommandSender`, `kSocketNameOutbound`, `SocketMessage::kRunTests`, and `kRunTestsDone`. There is only `main`.

Control flow: connects to the harness socket, sends `kRunTests`, waits for `kRunTestsDone`, and exits according to command-sender status. State/persistence behavior: no direct persistence; it advances harness control flow into test execution.

Dependencies/integration: used by CrashMonkey orchestration around compiled workloads. Risks/test signals: if the harness returns an error command or wrong command, the process only reports nonzero status.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/begin_tests.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/cm_checkpoint.cpp -->
# sources/test-tools/crashmonkey/code/user_tools/cm_checkpoint.cpp

Purpose: command-line checkpoint trigger for the CrashMonkey harness. It exposes the `Checkpoint()` API as an executable.

Important APIs/types/functions: `fs_testing::user_tools::api::Checkpoint` and `main`. There are no arguments or local helpers.

Control flow: `main` directly returns `Checkpoint()`, which sends the harness checkpoint socket command and waits for `kCheckpointDone`. State/persistence behavior: inserts a logical checkpoint marker into the harness/log stream rather than writing user data.

Dependencies/integration: useful for shell-driven workloads and for wrapper `DefaultFsFns::CmCheckpoint`. Risks/test signals: the executable has no usage checks and no diagnostic output on failure.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/cm_checkpoint.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/end_log.cpp -->
# sources/test-tools/crashmonkey/code/user_tools/end_log.cpp

Purpose: command-line shim that tells the harness to end logging. It closes the logging bracket started by `begin_log`.

Important APIs/types/functions: `ClientCommandSender`, `kSocketNameOutbound`, `SocketMessage::kEndLog`, and expected reply `kEndLogDone`.

Control flow: `main` constructs the sender, connects, sends `kEndLog`, waits for `kEndLogDone`, and returns status. State/persistence behavior: direct filesystem state is unchanged; harness logging state changes.

Dependencies/integration: used by test orchestration and any scripts coordinating log capture. Risks/test signals: socket connection failure, wrong reply, or harness error are reduced to generic negative/nonzero exit codes.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/end_log.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/src/actions.cpp -->
# sources/test-tools/crashmonkey/code/user_tools/src/actions.cpp

Purpose: implements the checkpoint user API by sending a command to the CrashMonkey harness over the local control socket. It is the bridge between workload code and harness-side checkpoint handling.

Important APIs/types/functions: `Checkpoint()`, `ClientCommandSender`, `kSocketNameOutbound`, `SocketMessage::kCheckpoint`, and `kCheckpointDone`. It lives in `fs_testing::user_tools::api`.

Control flow: `Checkpoint` constructs `ClientCommandSender` with the outbound socket and command pair, then returns `Run()`. `Run` performs connect, send, receive, and response-type validation.

State/persistence behavior: no direct file writes; success indicates the harness acknowledged a checkpoint marker, which later affects epoch/crash-state generation. Dependencies/integration: used by wrapper `DefaultFsFns::CmCheckpoint`, generated workloads, and `cm_checkpoint.cpp`.

Risks/test signals: assumes one fixed socket path and a responsive harness. Return codes preserve only coarse failure stages, so callers generally treat any nonzero as workload failure.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/src/actions.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/src/workload.cpp -->
# sources/test-tools/crashmonkey/code/user_tools/src/workload.cpp

Purpose: implements deterministic data-writing helpers for workload tests. It writes a 4 KiB repeated pattern at arbitrary offsets by either `pwrite` or mmap plus `msync`.

Important APIs/types/functions: `WriteData`, `WriteDataMmap`, static `kTestDataSize`, `kTestDataBlock`, compile-time `REP` macros, `pwrite`, `mmap`, `memcpy`, `msync`, and `munmap`. The pattern is `"abcdefghijklmnopqrstuvwxyz123456"` repeated to 4096 bytes.

Control flow: `WriteData` calculates the next 4 KiB boundary, writes an unaligned prefix if needed, writes full aligned pages, then writes a trailing partial range. `WriteDataMmap` maps the page-aligned covering range, copies the corresponding pattern bytes for unaligned and aligned segments, calls synchronous msync, and unmaps.

State/persistence behavior: direct writes change file data; mmap writes request persistence with `MS_SYNC`. The data pattern is offset-sensitive so later validators can infer correct placement.

Dependencies/integration: used by generated workloads and `WorkloadTest.cpp`. Risks/test signals: `WriteDataMmap` maps `size` rather than `map_size`, yet calls `msync/munmap` with `map_size`; this can be problematic for unaligned offsets. Tests currently focus on `WriteData`, not mmap.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/src/workload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/src/wrapper.cpp -->
# sources/test-tools/crashmonkey/code/user_tools/src/wrapper.cpp

Purpose: implementation of the filesystem operation abstraction declared in `wrapper.h`. It both delegates raw filesystem operations and records an ordered stream of logical `DiskMod` objects used by CrashMonkey replay and analysis.

Important APIs/types/functions: `DefaultFsFns` syscall wrappers, `RecordCmFsOps` recording methods, `PassthroughCmFsOps`, `CmOpenCommon`, `CmWrite`, `CmPwrite`, `CmMmap`, `CmMsync`, `CmFallocate`, `CmFsync`, `CmSync`, `CmSyncFileRange`, `CmCheckpoint`, `Serialize`, and helper `WriteWhole`. Recording uses `DiskMod::ModType` and `ModOpts`.

Control flow: `DefaultFsFns` maps methods to POSIX syscalls and checkpoint IPC. `RecordCmFsOps` records creates/truncates on open, captures write data and file-extension metadata, tracks writable shared mmaps and records msync ranges, classifies fallocate mode flags, records sync/fsync/checkpoint operations, and serializes mods. `PassthroughCmFsOps` forwards each operation without updating maps or mods.

State/persistence behavior: stateful members are fd-to-path mappings, mmap address mappings, and the accumulated mod vector. The serialized mod stream encodes the intended user-level operation order, while actual disk state is still governed by the filesystem and kernel.

Dependencies/integration: depends on Linux/POSIX syscalls, `DiskMod`, `actions.cpp` checkpoint IPC, and gtest coverage in `CmFsOpsTest.cpp`. Risks/test signals: rename only updates fd maps and does not append a `DiskMod`; `CmPwrite` contains unreachable code after return; `PassthroughCmFsOps::CmSyncFileRange` has no explicit return; direct syscalls by workloads bypass recording.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/user_tools/src/wrapper.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/ClassLoader.h -->
# sources/test-tools/crashmonkey/code/utils/ClassLoader.h

Purpose: header-only template for dynamically loading test-case classes from shared libraries. CrashMonkey uses this to load workload `.so` files exposing factory and deleter symbols.

Important APIs/types/functions: template `ClassLoader<T>`, `load_class<F>`, `unload_class<DF>`, `get_instance`, `dlopen`, `dlsym`, `dlclose`, and status macros `SUCCESS`, `CASE_HANDLE_ERR`, `CASE_INIT_ERR`, `CASE_DEST_ERR`.

Control flow: `load_class` opens a shared object, resolves factory and defactory symbols, creates an instance through the typed factory function pointer, and stores handles. `unload_class` calls the typed deleter and closes the handle if both handle and instance exist.

State/persistence behavior: maintains in-process dynamic loader state: library handle, function pointers, and one live object pointer. No persistent filesystem state is changed after loading.

Dependencies/integration: depends on `libdl` and test shared libraries exporting matching names. Risks/test signals: type safety is caller-enforced via template casts, error paths print to `stderr`, symbol names are stringly typed, and a factory returning null is not treated as load failure.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/ClassLoader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/DiskMod.cpp -->
# sources/test-tools/crashmonkey/code/utils/DiskMod.cpp

Purpose: serializes and deserializes logical filesystem mutations represented by `DiskMod`. It provides a compact big-endian binary format consumed by CrashMonkey components and tests.

Important APIs/types/functions: `DiskMod::Serialize`, `Deserialize`, `GetSerializeSize`, `SerializeHeader`, `SerializeChangeHeader`, `SerializeDataRange`, `SerializeDirectoryMod`, constructor, and `Reset`. It uses `htobe16/64`, `be16/64toh`, `shared_ptr<char>`, and enum values from `DiskMod.h`.

Control flow: serialization computes the entry size, writes size/type/options, optionally writes path and directory flag, then writes range metadata and data when applicable. Checkpoint and sync mods contain only headers; fsync/create/remove stop after change headers; fallocate and sync-file-range carry offset/length but no payload. Deserialization walks the same format, reconstructing path strings and optional data.

State/persistence behavior: the serialized buffer is an in-memory binary representation of logical operations, not direct disk persistence. Endianness is normalized for portable logs.

Dependencies/integration: used by `RecordCmFsOps::Serialize` and `DiskModTest.cpp`. Risks/test signals: `SerializeDirectoryMod` asserts unimplemented, `Deserialize` does not bounds-check malformed buffers, and remove mods are serialized like create/fsync but deserialization only early-returns for fsync/create, so remove handling deserves scrutiny.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/DiskMod.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/DiskMod.h -->
# sources/test-tools/crashmonkey/code/utils/DiskMod.h

Purpose: declares the `DiskMod` data model for logical filesystem changes recorded by user-tool wrappers. It is the schema for create, data, metadata, remove, sync, checkpoint, fallocate, mmap, and sync-file-range operations.

Important APIs/types/functions: class `DiskMod`, static `Serialize`/`Deserialize`, enums `ModType` and `ModOpts`, fields `path`, `mod_type`, `mod_opts`, `post_mod_stats`, `directory_mod`, `file_mod_data`, `file_mod_location`, `file_mod_len`, and `directory_added_entry`. Private helpers define serialization internals.

Control flow: no runtime flow in the header; it defines which fields are meaningful for different operation types. Comments explain that parent-directory changes are inferred from `kCreateMod` rather than represented as separate directory mods.

State/persistence behavior: `DiskMod` instances are transient C++ objects until serialized into the operation log. They preserve enough state to replay or reason about file ranges and synchronization boundaries.

Dependencies/integration: included by wrappers, utilities, and tests. Risks/test signals: directory modifications are only partially modeled, permissions are TODO, and consumers must understand which enum/field combinations include payload bytes.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/DiskMod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/BaseSocket.cpp -->
# sources/test-tools/crashmonkey/code/utils/communication/BaseSocket.cpp

Purpose: implements low-level serialization for CrashMonkey control messages over sockets. It reads and writes command-only `SocketMessage` instances using network byte order.

Important APIs/types/functions: `ReadMessageFromSocket`, `WriteMessageToSocket`, `GobbleData`, `ReadIntFromSocket`, `WriteIntToSocket`, `ReadStringFromSocket`, `WriteStringToSocket`, `recv`, `send`, `htonl`, and `ntohl`. Current message handling accepts only command types with no payload.

Control flow: reads type and size, switches over known commands, gobbles unexpected payload bytes, and returns -1 for unknown types. Writing sends type, validates it is a known command, writes size 0, and returns status.

State/persistence behavior: no persistent state; the functions consume or emit bytes on a connected socket. Dependencies/integration: used by `ClientSocket` and `ServerSocket`.

Risks/test signals: zero-length `recv` is not handled as disconnect and can spin, variable-length stack arrays are used, string helpers are unused by current command path, and error reporting is coarse. Socket tests are not present in this subset.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/BaseSocket.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/BaseSocket.h -->
# sources/test-tools/crashmonkey/code/utils/communication/BaseSocket.h

Purpose: declares shared socket message encoding helpers for CrashMonkey client and server sockets. It centralizes command message read/write behavior.

Important APIs/types/functions: class `BaseSocket`, public static `ReadMessageFromSocket` and `WriteMessageToSocket`, private helpers for ints, strings, and payload discard, plus `SocketMessage` from `SocketUtils.h`.

Control flow: the header exposes only static utility entry points; implementations perform blocking socket reads/writes and command validation. State/persistence behavior: stateless utility with no owned resources.

Dependencies/integration: included by `ClientSocket.h` and `ServerSocket.h`. Risks/test signals: private string helpers are declared despite the current protocol using no string payloads, which can hide untested code paths if payload-bearing commands are later added.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/BaseSocket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/ClientCommandSender.cpp -->
# sources/test-tools/crashmonkey/code/utils/communication/ClientCommandSender.cpp

Purpose: implements a one-shot command client for harness control operations. It connects, sends one command, waits for one response, and reports whether the expected response arrived.

Important APIs/types/functions: `ClientCommandSender` constructor, `Run`, `ClientSocket::Init`, `SendCommand`, `WaitForMessage`, and `SocketMessage`. It stores socket path, command to send, command expected back, and a `ClientSocket`.

Control flow: `Run` returns -1 if connect fails, -2 if send fails, -3 if receive fails, otherwise returns boolean negation of `ret.type == return_command` so success is 0 and wrong reply is 1.

State/persistence behavior: owns only transient socket connection state through `ClientSocket`. Dependencies/integration: used by begin/end log/test shims and checkpoint API.

Risks/test signals: the wrong-reply path loses the actual command received; no retry or timeout is implemented at this layer; lifecycle is one command per instance.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/ClientCommandSender.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/ClientCommandSender.h -->
# sources/test-tools/crashmonkey/code/utils/communication/ClientCommandSender.h

Purpose: declares the one-shot command sender used by CrashMonkey user tools. It wraps the lower-level `ClientSocket` into a simple send/expect API.

Important APIs/types/functions: class `ClientCommandSender`, constructor taking socket address, send command, and expected receive command, `Run`, `socket_address`, `send_command`, `return_command`, and `conn`.

Control flow: no implementation here; `Run` handles connect/send/wait in the `.cpp`. State/persistence behavior: stores immutable command parameters and one client socket object.

Dependencies/integration: depends on `ClientSocket.h` and `SocketUtils.h`; used by command-line shims and `actions.cpp`. Risks/test signals: the class only supports command messages and cannot send payload-bearing requests without extending BaseSocket and SocketMessage handling.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/ClientCommandSender.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/ClientSocket.cpp -->
# sources/test-tools/crashmonkey/code/utils/communication/ClientSocket.cpp

Purpose: implements a simple AF_UNIX stream client socket for CrashMonkey control communication.

Important APIs/types/functions: constructor, destructor, `Init`, `SendCommand`, `SendMessage`, `WaitForMessage`, `CloseClient`, `socket`, `connect`, `close`, `sockaddr_un`, and `BaseSocket`.

Control flow: `Init` creates a local stream socket and connects to the configured path. `SendCommand` wraps a command into `SocketMessage`; `SendMessage` delegates encoding to `BaseSocket`; `WaitForMessage` delegates decoding; `CloseClient` closes and resets the descriptor.

State/persistence behavior: owns one socket fd and immutable socket address. No durable state is changed. Dependencies/integration: used by `ClientCommandSender`.

Risks/test signals: `strcpy` into `sun_path` has no length guard, destructor closes `-1` harmlessly but may double-close if `CloseClient` was called and fd reused elsewhere, and no connection timeout exists.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/ClientSocket.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/ClientSocket.h -->
# sources/test-tools/crashmonkey/code/utils/communication/ClientSocket.h

Purpose: declares the CrashMonkey AF_UNIX client socket abstraction. It provides command send and message receive methods for user tools.

Important APIs/types/functions: `ClientSocket`, `Init`, `SendCommand`, `SendMessage`, `WaitForMessage`, `CloseClient`, `socket_fd`, and `socket_address`. It is explicitly documented as not thread-safe.

Control flow: header-only declarations; implementation connects to a Unix socket and uses `BaseSocket` encoding. State/persistence behavior: one mutable file descriptor tracks connection state.

Dependencies/integration: included by `ClientCommandSender`. Risks/test signals: no copy/move controls are declared, so accidental copying could duplicate fd ownership.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/ClientSocket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/ServerSocket.cpp -->
# sources/test-tools/crashmonkey/code/utils/communication/ServerSocket.cpp

Purpose: implements the harness-side AF_UNIX server socket for receiving CrashMonkey control commands and sending acknowledgements.

Important APIs/types/functions: `ServerSocket`, `Init`, `SendCommand`, `SendMessage`, `WaitForMessage`, `TryForMessage`, `CloseClient`, `CloseServer`, `socket`, `bind`, `listen`, `poll`, `accept`, `unlink`, and `BaseSocket`. `TryForMessage` uses a 25 ms poll timeout.

Control flow: `Init` creates a nonblocking local stream socket, binds it to the configured path, and listens. `WaitForMessage` blocks in `poll`, accepts one client, reads one message, and leaves `client_socket` open for response. `TryForMessage` is the nonblocking variant. Send methods write to the accepted client, and close methods tear down fds.

State/persistence behavior: owns server and current client descriptors and unlinks the socket pathname in the destructor. Dependencies/integration: used by the harness control loop.

Risks/test signals: only one client at a time is supported, stale socket files before bind are not removed, `strcpy` can overflow `sun_path`, and caller must close each client before accepting another.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/ServerSocket.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/ServerSocket.h -->
# sources/test-tools/crashmonkey/code/utils/communication/ServerSocket.h

Purpose: declares the CrashMonkey harness server socket abstraction. It accepts command messages and sends command replies.

Important APIs/types/functions: `ServerSocket`, `Init`, `SendCommand`, `SendMessage`, `WaitForMessage`, `TryForMessage`, `CloseClient`, `CloseServer`, `server_socket`, `client_socket`, and `socket_address`.

Control flow: declarations only; `.cpp` handles poll/accept/read/write. State/persistence behavior: one listening fd and one active client fd represent state, with socket-file cleanup on destruction.

Dependencies/integration: included by harness code outside this subset. Risks/test signals: non-thread-safe, single-client design; tests in this subset do not exercise server behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/ServerSocket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/SocketUtils.h -->
# sources/test-tools/crashmonkey/code/utils/communication/SocketUtils.h

Purpose: shared constants and data structures for CrashMonkey control socket communication.

Important APIs/types/functions: `kSocketDir`, `kSocketNameOutbound`, `SocketMessage`, `SocketMessage::CmCommand`, and `SocketError`. Command enum values cover harness error, invalid command, prepare, begin/end log, run tests, checkpoint, and done/failed acknowledgements.

Control flow: no executable flow; consumers use the enum to build protocol messages. State/persistence behavior: fixed socket path `/tmp/crash_monkey_harness` is the integration point between tools and harness.

Dependencies/integration: included throughout `utils/communication` and user tool shims. Risks/test signals: comments warn that socket directory and full path must be kept manually in sync; adding payload-bearing commands requires extending BaseSocket handling.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/communication/SocketUtils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/utils.cpp -->
# sources/test-tools/crashmonkey/code/utils/utils.cpp

Purpose: implements disk-write utility types used to represent block IO log entries and crash-state data fragments. It provides flag classification, binary serialization, deserialization, formatting, and data ownership helpers.

Important APIs/types/functions: `disk_write` constructors, `is_async_write`, `is_barrier`, `is_meta`, `is_checkpoint`, equality operators, `serialize`, `deserialize`, `flags_to_string`, flag setters/clearers, `set_data`, `get_data`, `clear_data`, `DiskWriteData`, and `GetData`. It depends on `disk_wrapper_ioctl.h` flag definitions.

Control flow: serialization writes a 4 KiB metadata block in big-endian fields followed by zero-padded 4 KiB data blocks. Deserialization reads the same blocks, reconstructs metadata, allocates data, and returns a `disk_write`. Flag helpers test HWM bits for write, flush, FUA, soft barrier, metadata, and checkpoint semantics.

State/persistence behavior: serializes kernel-observed writes into log files and provides pointers into shared data for replay. `DiskWriteData` avoids copies by retaining a shared base pointer and offset.

Dependencies/integration: used by permuters, tests, and harness snapshot/replay code. Risks/test signals: deserialization uses asserts rather than recoverable errors, allocates even for zero-sized data, and binary streams are opened without explicit `ios::binary` in tests on POSIX.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/utils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/utils.h -->
# sources/test-tools/crashmonkey/code/utils/utils.h

Purpose: declares utility structures for block-level disk write logs and replay data slices. These are lower-level than `DiskMod`, representing actual write operations captured from the disk wrapper.

Important APIs/types/functions: class `disk_write`, `disk_write_op_meta metadata`, flag/query methods, static `serialize`/`deserialize`, data ownership methods, equality/stream operators, and struct `DiskWriteData` with `full_bio`, indexes, offset, size, and `GetData`.

Control flow: no implementation in the header; callers construct writes, classify them into epochs, serialize logs, and pass `DiskWriteData` into replay paths. State/persistence behavior: `disk_write` owns optional write payload through `shared_ptr<char>`, while `DiskWriteData` shares a larger buffer.

Dependencies/integration: includes `disk_wrapper_ioctl.h` and is used by permuter and utils tests. Risks/test signals: comments warn pointer lifetime depends on object lifetime, and metadata struct has C layout with manual initialization in constructors.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/utils/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/copy_diff.sh -->
# sources/test-tools/crashmonkey/copy_diff.sh

Purpose: shell helper that classifies a CrashMonkey diff output as pass/fail/could-not-run, appends failing diffs to `diff_results/<target>`, optionally invokes detailed diff parsing, and cleans transient `build/diff*` files.

Important APIs/types/functions: positional args `_file`, `_target`, optional `_demo`, `tput` colors, file tests `-f`/`-s`, `cat`, `source find_diff.sh`, and `rm build/diff*`.

Control flow: validates input file, if non-empty prints failed, appends content, optionally parses it for demo output, and removes diffs. If empty, it checks whether diff files existed in `build`; if so, removes them and prints passed; otherwise prints could-not-run.

State/persistence behavior: mutates `diff_results`, deletes `build/diff*`, and may update bug counters through `find_diff.sh`. Dependencies/integration: called by `xfsMonkey.py` and demo workflows.

Risks/test signals: unquoted variables can break on spaces/globs, `rm build/diff*` can error when no files match, and sourcing `find_diff.sh` runs it in the caller shell with shared variables.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/copy_diff.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/demo.sh -->
# sources/test-tools/crashmonkey/demo.sh

Purpose: end-to-end demo driver for generating ACE workloads, compiling them, running XFSMonkey on a selected filesystem, and printing a timing/bug summary.

Important APIs/types/functions: argument `FS`, ACE invocation `python ace.py -l 1 -n False -d True`, `make gentests`, `xfsMonkey.py`, summary files `bugs`, `stat`, `missing`, `others`, and directories `code/tests/seq1_demo`, `generated_workloads`, `build/tests/generated_workloads`, `diff_results`.

Control flow: validates one filesystem argument, removes old generated workload dir, runs ACE, clears/copies generated `j-lang*.cpp`, compiles generated tests, initializes counters, removes old reports, runs `xfsMonkey.py`, then computes generation/compile/test durations and prints counts.

State/persistence behavior: deletes and recreates workload/report directories, writes counter files, writes `out_compile`, and creates logs/diffs through XFSMonkey. Dependencies/integration: requires ACE, make targets, root-capable XFSMonkey environment, and `bc`.

Risks/test signals: destructive cleanup is broad, paths are relative to repository root, summary says `diff-results` while variable is `diff_results`, and failures in generation/compile are not explicitly checked before running tests.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/demo.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/docs/_config.yml -->
# sources/test-tools/crashmonkey/docs/_config.yml

Purpose: Jekyll documentation configuration file for CrashMonkey docs. In this checkout it is zero bytes, so it currently supplies no theme or site options.

Important APIs/types/functions: none; YAML content is empty. Control flow: none.

State/persistence behavior: no runtime effect unless a documentation build reads it as an empty config. Dependencies/integration: conventionally consumed by Jekyll/GitHub Pages when building the `docs` folder.

Risks/test signals: the empty file may mean defaults are intended, or it may be a placeholder/accidental truncation. Documentation builds should be checked if site theming or metadata is expected.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/docs/_config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/find_diff.sh -->
# sources/test-tools/crashmonkey/find_diff.sh

Purpose: parses a CrashMonkey diff file to print concise bug details and update bug-type counters. It distinguishes metadata/content mismatches from missing-file failures.

Important APIs/types/functions: input `_file`, counters `bugs`, `missing`, `stat`, patterns `DIFF: Content Mismatch` and `Failed stating`, arrays for inode/size/blocksize/block count/link count, `grep`, `cut`, and `tput`.

Control flow: validates the file, increments total bug count, scans each line. On metadata mismatch it captures paired actual/expected fields; on missing-file text it prints subsequent lines. After scanning, it increments the metadata or missing counter and prints the first differing metadata attribute.

State/persistence behavior: updates plain counter files in the current directory and prints diagnostic output. Dependencies/integration: sourced by `copy_diff.sh` during demo mode and assumes CrashMonkey diff formatting.

Risks/test signals: numeric comparisons assume captured fields are present and numeric, arrays hold only the first pair of entries, and unquoted variables can break on whitespace. It does not update `others` despite demo summary reading that file.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/find_diff.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/setup/create_vm.sh -->
# sources/test-tools/crashmonkey/setup/create_vm.sh

Purpose: sudo shell script to build an Ubuntu KVM VM image with vmbuilder and project-specific network/user/package settings. It moves the generated qcow2 to a named workspace image on success.

Important APIs/types/functions: arguments `NAME` and `IP`, variables `CUR_DIR`, `DIR`, `WORKSPACE`, `sudo vmbuilder kvm ubuntu`, package options, bridge/network settings, `--copy rcs`, `mv`, and `chown`.

Control flow: computes paths, invokes vmbuilder with fixed architecture, memory, root size, Ubuntu Trusty suite, packages, bridge `br0`, IP/gateway/DNS, hostname, and copied files. If vmbuilder exits 0, it renames the qcow2 and chowns the workspace back to the invoking user.

State/persistence behavior: creates VM disk images and modifies filesystem ownership under the workspace. Dependencies/integration: requires sudo, vmbuilder/libvirt/KVM, bridge network, placeholder `<USER_NAME>` replacement, and an `rcs` file/directory.

Risks/test signals: no argument validation, hard-coded network/device/user placeholders, and destructive `--overwrite`. Failures are visible through vmbuilder exit and shell trace from `set -x`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/setup/create_vm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/test/Makefile -->
# sources/test-tools/crashmonkey/test/Makefile

Purpose: self-contained Google Test/Google Mock makefile for building CrashMonkey unit tests. It compiles gtest/gmock libraries and selected project test binaries.

Important APIs/types/functions: variables `GTEST_DIR`, `GMOCK_DIR`, `CPPFLAGS`, `CXXFLAGS`, `TESTS`, `CODE_DIR`, targets for `gtest.a`, `gmock.a`, `RandomPermuterTest`, `PermuterTest`, `DiskWriteTest`, `DiskModTest`, `CmFsOpsTest`, `WorkloadTest`, and `TesterTest`.

Control flow: `all` builds `$(TESTS)`, currently `DiskModTest CmFsOpsTest WorkloadTest`; additional test targets are defined but not in the default list. Each object target compiles a test source with gtest headers, and each binary links project implementation files plus gtest/gmock libraries.

State/persistence behavior: creates object files, static gtest/gmock libraries, and test executables in the test directory; `clean` removes them. Dependencies/integration: relies on vendored googletest at `../googletest`, C++11, pthread, optional `SYS_HEADERS`, and Linux kernel headers for block flag tests.

Risks/test signals: default `TESTS` omits several defined tests, dependency rules are conservative, and some targets may need `-ldl` or kernel headers depending on environment.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/test/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/test/harness/TestTester.cpp -->
# sources/test-tools/crashmonkey/test/harness/TestTester.cpp

Purpose: test helper implementation for reaching into `Tester` internals during gtests. It provides a wrapper object and a method to replace the tester's device snapshot buffer.

Important APIs/types/functions: `TestTester::TestTester`, `set_tester_snapshot`, member `tester`, `Tester(false)`, `device_clone`, and `device_size`.

Control flow: constructor initializes `tester` with `false`. `set_tester_snapshot` deletes any existing `device_clone`, then assigns the caller-provided buffer pointer and size.

State/persistence behavior: mutates in-memory `Tester` snapshot ownership; the passed pointer becomes owned by `Tester`/helper and may be deleted later. Dependencies/integration: used by `TesterTest.cpp` to test snapshot save behavior.

Risks/test signals: ownership transfer is implicit and dangerous when passed stack storage; in the current test, a stack array is assigned, which can be unsafe if destructor later deletes it.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/test/harness/TestTester.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/test/harness/TestTester.h -->
# sources/test-tools/crashmonkey/test/harness/TestTester.h

Purpose: declares a small gtest helper around CrashMonkey `Tester`. It exposes a method for installing a synthetic device snapshot.

Important APIs/types/functions: class `TestTester`, constructor, `set_tester_snapshot(char *sn, size_t size)`, and public member `Tester tester`.

Control flow: implementation constructs `Tester(false)` and sets internal snapshot pointers. State/persistence behavior: in-memory only, but used to drive snapshot serialization in tests.

Dependencies/integration: includes `../../code/harness/Tester.h`. Risks/test signals: public `tester` breaks encapsulation intentionally for tests, and snapshot ownership conventions are not documented in the header.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/test/harness/TestTester.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/test/harness/TesterTest.cpp -->
# sources/test-tools/crashmonkey/test/harness/TesterTest.cpp

Purpose: gtest for `Tester::log_snapshot_save`. It verifies that a synthetic device snapshot is written byte-for-byte to a file.

Important APIs/types/functions: `TestTester`, `log_snapshot_save`, `mkstemp`, `ifstream`, `std::equal`, and `SUCCESS`. The test uses an 8 KiB buffer filled with byte value 42.

Control flow: create temp file, fill snapshot buffer, install it into `TestTester`, call `log_snapshot_save`, read the file back, assert EOF and byte equality.

State/persistence behavior: writes a temporary snapshot file under `/tmp`; no cleanup is performed after reading. Dependencies/integration: links `Tester.cpp`, utils, gtest/gmock, and `-ldl`.

Risks/test signals: passes stack memory to a helper that may delete previous/owned snapshots, and it does not unlink the temp file. The core signal is file content equality and `SUCCESS` return.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/test/harness/TesterTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/test/permuter/PermuterTest.cpp -->
# sources/test-tools/crashmonkey/test/permuter/PermuterTest.cpp

Purpose: comprehensive gtest coverage for the base permuter's epoch construction, barrier handling, checkpoint numbering, overlap detection, sector coalescing, and `epoch_op` sector splitting. It uses a small `TestPermuter` subclass to expose protected internals.

Important APIs/types/functions: `Permuter`, `epoch`, `epoch_op`, `EpochOpSector`, `PermuteTestResult`, `disk_write`, `InitDataVector`, `CoalesceSectors`, `GetEpochs`, `VerifyEpoch`, and HWM flags. Tests cover flush and FUA barriers, unterminated epochs, overlapping writes, split flushes, checkpoint edge cases, metadata counts, sector coalescing, and `ToSectors`.

Control flow: each test builds vectors of synthetic `disk_write` entries with checkpoint/write/barrier flags, initializes a `TestPermuter`, inspects internal epoch vectors, and asserts metadata, barrier, overlap, abs-index, and sector fields. The coalescing tests build `EpochOpSector` vectors directly.

State/persistence behavior: no disk persistence; the state under test is in-memory interpretation of block log entries into crash permutation epochs. Dependencies/integration: validates assumptions used by random and exhaustive crash-state generation.

Risks/test signals: tests rely on synthetic metadata rather than real disk-wrapper logs; `TestPermuter` stubs permutation generation, so only common base behavior is covered. Failures identify regressions in epoch boundary and sector math.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/test/permuter/PermuterTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/test/permuter/RandomPermuterTest.cpp -->
# sources/test-tools/crashmonkey/test/permuter/RandomPermuterTest.cpp

Purpose: lightweight gtests for `RandomPermuter`. It checks construction and basic behavior when generating one random crash state from single- and multi-epoch synthetic write streams.

Important APIs/types/functions: `RandomPermuter`, `disk_write`, `init_data`, `gen_one_state`, Linux block flags `REQ_WRITE`, `REQ_SYNC`, `REQ_FUA`, and gtest assertions.

Control flow: tests create vectors of writes and barriers, initialize the random permuter, request one state, and assert coarse properties. `FindOverlaps` expects output to differ when an overlapping barrier/write exists; `FindNoOverlapsMultiEpoch` expects the first non-overlapping epoch to be preserved.

State/persistence behavior: in-memory only; it tests permutation selection logic rather than actual replay. Dependencies/integration: depends on kernel block headers and `RandomPermuter` implementation.

Risks/test signals: because output is random, assertions are intentionally weak; no seed is controlled here, so reproducibility depends on implementation defaults. Still, it catches gross failures in overlap-aware randomization.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/test/permuter/RandomPermuterTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/test/user_tools/CmFsOpsTest.cpp -->
# sources/test-tools/crashmonkey/test/user_tools/CmFsOpsTest.cpp

Purpose: gtest/gmock suite for `RecordCmFsOps`, validating that wrapped filesystem calls update fd/mmap maps and append correct `DiskMod` records. It uses fake and mock `FsFns` implementations to avoid real filesystem effects.

Important APIs/types/functions: `FakeFsFns`, `MockFsFns`, `TestCmFsOps`, `RecordCmFsOps`, `DiskMod`, `CmOpen`, `CmClose`, `CmWrite`, `CmCheckpoint`, `CmMsync`, `CmMmap`, parameterized write-size and mmap tests, and gmock `EXPECT_CALL`/`ON_CALL`.

Control flow: tests simulate open/create/truncate cases, close success/failure, zero-byte writes, checkpoint recording, msync at different mmap offsets/pointers, writes that do or do not extend file size, and mmap flag combinations that should or should not be tracked. Parameterized tests cover full and partial write sizes plus shared/private/anonymous mapping behavior.

State/persistence behavior: exercises in-memory `fd_map_`, `mmap_map_`, and `mods_`; fake `stat` sizes model file extension decisions. No durable files are created.

Dependencies/integration: validates the wrapper layer that generated workloads use to produce logical operation logs. Risks/test signals: rename, unlink/remove, fallocate, pwrite, fsync/fdatasync/sync/sync_file_range, and serialization paths have little or no coverage here; the fake `FnPathExists` returns `0` as false in all default cases.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/test/user_tools/CmFsOpsTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/test/user_tools/WorkloadTest.cpp -->
# sources/test-tools/crashmonkey/test/user_tools/WorkloadTest.cpp

Purpose: gtests for `WriteData`, verifying deterministic byte placement for sub-4 KiB aligned and unaligned writes. It ensures holes before an offset are zero and written bytes match the shared test pattern.

Important APIs/types/functions: `WriteData`, `open`, `unlink`, `read`, `close`, `memcmp`, constants `kTestDataSize` and `kTestDataBlock`, and gtest assertions.

Control flow: each test opens/truncates a temporary `test_file`, unlinks it for cleanup, calls `WriteData` with a specific offset/size, reads the expected file span, checks EOF, validates zero-filled holes where expected, and compares written data to the deterministic block at the expected offset.

State/persistence behavior: creates an unlinked temporary file and writes data through `pwrite`; persistence beyond the open fd is not relevant. Dependencies/integration: tests the helper used by generated CrashMonkey workloads.

Risks/test signals: no tests cover writes larger than 4 KiB, exact 4 KiB boundary crossings, error returns, or `WriteDataMmap`. The read loop can spin if `read` returns 0 before expected bytes.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/test/user_tools/WorkloadTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/test/utils/DiskModTest.cpp -->
# sources/test-tools/crashmonkey/test/utils/DiskModTest.cpp

Purpose: gtest/gmock suite for `DiskMod` serialization and deserialization. It validates binary sizes, endian-converted headers, enum fields, paths, range metadata, and optional payload bytes for major mod types and options.

Important APIs/types/functions: `DiskMod::Serialize`, `DiskMod::Deserialize`, `be16toh`, `be64toh`, `shared_ptr<char>`, parameterized path tests, option tests, fallocate option/type combinations, and gtest assertions.

Control flow: individual tests build a `DiskMod`, serialize it, manually inspect size/type/option fields, deserialize into a new object, and assert all relevant fields. Parameterized tests cover short and long paths, all `ModOpts`, and both data/data-metadata fallocate-style mods.

State/persistence behavior: all state is in-memory serialized buffers; no files are written. Dependencies/integration: protects the binary contract consumed by wrapper serialization and replay tools.

Risks/test signals: malformed input, remove mods, directory data mods, and `SerializeDirectoryMod` are not covered. The tests encode current size formulas, so intentional format changes require synchronized updates.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/test/utils/DiskModTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/test/utils/DiskWriteTest.cpp -->
# sources/test-tools/crashmonkey/test/utils/DiskWriteTest.cpp

Purpose: gtests for block-level `disk_write` serialization/deserialization. It verifies that metadata flags, sector, size, and payload survive round-trip through temporary files.

Important APIs/types/functions: `disk_write`, `set_data`, `get_data`, `serialize`, `deserialize`, `mkstemp`, `ofstream`, `ifstream`, `memcmp`, `REQ_WRITE`, and `REQ_SYNC`.

Control flow: `Serialize_Deserialize` writes one 8 KiB record to a temp file and reads it back. `Serialize_Deserialize_Epoch` writes two records with different sizes/data bytes, reads until EOF, and compares each record field and payload.

State/persistence behavior: writes temporary serialized log files under `/tmp` and frees temp path strings, but does not unlink the files. Dependencies/integration: validates utility format used by disk log processing and permuters.

Risks/test signals: file streams are not explicitly binary, tests depend on Linux block headers, and the EOF loop can be fragile because serialized records are block padded. There is debug output in the epoch test.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/test/utils/DiskWriteTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/check_server_status.sh -->
# sources/test-tools/crashmonkey/vm_scripts/check_server_status.sh

Purpose: checks whether servers listed in a file respond to a one-packet ping. It is an operator utility for CrashMonkey cluster/VM orchestration.

Important APIs/types/functions: one argument `file`, `cat`, loop over IPs, `ping -c1 -W1`, and status `echo` output. Control flow validates exactly one parameter, then prints a banner and up/down result for each IP.

State/persistence behavior: read-only; no files or VMs are changed. Dependencies/integration: expects a newline-delimited IP list and local `ping`.

Risks/test signals: variable `file` is assigned but the loop still uses `$1`; ping reachability may be blocked even when SSH is available; unquoted command substitution can mishandle whitespace.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/check_server_status.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/clone_vms.sh -->
# sources/test-tools/crashmonkey/vm_scripts/clone_vms.sh

Purpose: clones a base VirtualBox VM `ubuntu16-vm1` into a numbered range and assigns incrementing NAT SSH port forwards.

Important APIs/types/functions: args `start`, `end`, `port`, `VBoxManage clonevm`, `modifyvm --natpf1 delete ssh`, and `modifyvm --natpf1 "ssh,tcp,,<port>,,22"`.

Control flow: validates three args, loops from start to end, clones/registers each VM, replaces the `ssh` NAT rule, then increments port. State/persistence behavior: creates registered VirtualBox VMs and mutates their NAT configuration.

Dependencies/integration: used by `setup.sh` after importing a base OVA. Risks/test signals: assumes base VM and rule name exist, does not stop on individual VBoxManage failure, and can leave partially configured clones.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/clone_vms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/cm_cleanup.sh -->
# sources/test-tools/crashmonkey/vm_scripts/cm_cleanup.sh

Purpose: cleanup helper for CrashMonkey kernel modules and mount state inside a VM or host.

Important APIs/types/functions: `umount /mnt/snapshot`, `rmmod disk_wrapper.ko`, and `rmmod cow_brd.ko`. Control flow is linear with no argument validation.

State/persistence behavior: unmounts the snapshot mount and unloads kernel modules, affecting the running system. Dependencies/integration: called by remote trigger scripts and `xfsMonkey.py` equivalent cleanup.

Risks/test signals: ignores errors, assumes module names/paths, and may fail if busy or if modules are named without `.ko` after insertion.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/cm_cleanup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/cssh_file.sh -->
# sources/test-tools/crashmonkey/vm_scripts/cssh_file.sh

Purpose: opens a ClusterSSH session to all hosts listed in a file as user `cc`.

Important APIs/types/functions: one argument `file`, `cat`, `tr` to flatten newlines, and `cssh -l cc`. Control flow validates one argument, reads host list, and launches cssh.

State/persistence behavior: no persistent repo state; starts interactive SSH sessions. Dependencies/integration: operator utility for managing nodes in `live_nodes`-style files.

Risks/test signals: requires `cssh`, assumes username `cc`, and unquoted host expansion can behave unexpectedly with malformed files.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/cssh_file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/extract_core_workload.sh -->
# sources/test-tools/crashmonkey/vm_scripts/extract_core_workload.sh

Purpose: filters generated workload C++ source down to core filesystem operations for easier inspection.

Important APIs/types/functions: one argument `file`, `cat`, `grep -v user_tools`, and grep patterns for link/unlink/mkdir/sync/Rename/WriteData/Open/checkpoint/FALLOC.

Control flow: validates one argument, then streams matching lines from the file. State/persistence behavior: read-only; prints to stdout.

Dependencies/integration: useful for reviewing generated ACE workloads. Risks/test signals: pattern matching is approximate, case-sensitive except separate `sync`/`Sync`, and it can miss operations not in the hard-coded grep list.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/extract_core_workload.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/force_stop_all_vms.sh -->
# sources/test-tools/crashmonkey/vm_scripts/force_stop_all_vms.sh

Purpose: forcibly kills local processes whose command line matches `startvm`, stopping running VirtualBox VMs at the process level.

Important APIs/types/functions: `ps aux`, `grep startvm`, `cut`, and `kill`. Control flow loops over matching PIDs and kills each.

State/persistence behavior: abruptly terminates VM processes and can leave VM state unclean. Dependencies/integration: emergency operator utility paired with start/stop scripts.

Risks/test signals: process matching is broad and could kill unrelated commands containing `startvm`; no confirmation or graceful shutdown is attempted.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/force_stop_all_vms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/force_stop_vm.sh -->
# sources/test-tools/crashmonkey/vm_scripts/force_stop_vm.sh

Purpose: forcibly kills the local process for one numbered VM named `ubuntu16-vm<N>`.

Important APIs/types/functions: one argument `vm`, `ps aux`, `grep ubuntu16-vm"$vm"`, `cut`, and `kill`. Control flow validates one arg, prints a timestamped message, finds matching PID(s), and kills them.

State/persistence behavior: abrupt VM termination with possible dirty VM disk state. Dependencies/integration: used by restart scripts when VMs are unresponsive or read-only.

Risks/test signals: broad grep matching can return multiple or unintended PIDs, no check if no process is found, and no graceful VBoxManage poweroff is attempted.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/force_stop_vm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/install-4.15.sh -->
# sources/test-tools/crashmonkey/vm_scripts/install-4.15.sh

Purpose: downloads and installs Ubuntu mainline Linux kernel 4.15 packages inside a VM/host.

Important APIs/types/functions: `cd /tmp`, three `wget` URLs for headers/image `.deb` files, and `sudo dpkg -i *.deb`. Control flow is linear with no args.

State/persistence behavior: writes packages to `/tmp` and installs kernel packages system-wide. Dependencies/integration: likely used to prepare CrashMonkey test VMs for a target kernel.

Risks/test signals: wildcard `*.deb` installs all debs in `/tmp`, URLs may become unavailable, no checksum verification, and no reboot/default-kernel selection is handled.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/install-4.15.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/install-4.16.sh -->
# sources/test-tools/crashmonkey/vm_scripts/install-4.16.sh

Purpose: downloads and installs Ubuntu mainline Linux kernel 4.16 packages.

Important APIs/types/functions: `wget` for 4.16 headers/image packages and `sudo dpkg -i *.deb`. Control flow mirrors `install-4.15.sh`.

State/persistence behavior: installs kernel packages on the system and leaves downloads in `/tmp`. Dependencies/integration: VM/kernel setup for filesystem crash testing.

Risks/test signals: unpinned wildcard install, no checksum verification, potential stale URLs, and no error handling or reboot orchestration.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/install-4.16.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/pull_diff_files_and_xfsmonkey_log.sh -->
# sources/test-tools/crashmonkey/vm_scripts/pull_diff_files_and_xfsmonkey_log.sh

Purpose: collects diff result files and XFSMonkey logs from a selected server range and all VMs on each server.

Important APIs/types/functions: args `run`, `st`, `end`, directories `$run/diff_files` and `$run/xfsmonkey_logs`, `live_nodes`, fixed `num_vms=12`, `sshpass scp`, user `user`, password `password`, NAT ports starting at 3022.

Control flow: creates output directories, iterates IPs from `live_nodes` with server index, skips outside the requested range, then loops VM ports to scp diff files and one log per VM with a server/vm-specific name.

State/persistence behavior: creates local collection directories and copies remote artifacts. Dependencies/integration: used after distributed XFSMonkey runs.

Risks/test signals: hard-coded credentials, unquoted paths, fixed VM count, no scp failure handling, and copying all diff files into one directory can collide on names.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/pull_diff_files_and_xfsmonkey_log.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/pull_diff_files_and_xfsmonkey_log_parallel.sh -->
# sources/test-tools/crashmonkey/vm_scripts/pull_diff_files_and_xfsmonkey_log_parallel.sh

Purpose: launches batched background collectors for diff files and XFSMonkey logs across multiple servers.

Important APIs/types/functions: args `run`, `batch_size`, `num_servers`, loop variables `st`/`end`, `nohup ./pull_diff_files_and_xfsmonkey_log.sh ... > out<i>.log &`.

Control flow: computes server ranges of `batch_size` and starts one collector process per range until all servers are covered. State/persistence behavior: creates background jobs and per-batch logs; actual artifact collection is delegated.

Dependencies/integration: wrapper around the nonparallel pull script. Risks/test signals: no wait/join or failure aggregation, overlapping output directories can race, and `end` can exceed `num_servers`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/pull_diff_files_and_xfsmonkey_log_parallel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/restart_read_only_vms.sh -->
# sources/test-tools/crashmonkey/vm_scripts/restart_read_only_vms.sh

Purpose: probes local NAT-forwarded VMs for read-only filesystem symptoms and restarts affected VMs.

Important APIs/types/functions: environment `num_vms`, ports from 3022, `timeout rsh`, remote `touch /home/user/a`, grep `Read-only`, `force_stop_vm.sh`, `start_particular_vm.sh`, and sleeps.

Control flow: loops VMs, executes a remote touch command, treats empty output or output containing `Read-only` as bad, kills/restarts the VM and waits; otherwise prints fine. State/persistence behavior: creates `/home/user/a` on healthy VMs and restarts unhealthy ones.

Dependencies/integration: maintenance script for long distributed runs. Risks/test signals: `num_vms=$num_vms` relies on exported environment, unquoted tests can misbehave, and restart is forceful.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/restart_read_only_vms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/restart_scp_non_working_vms.sh -->
# sources/test-tools/crashmonkey/vm_scripts/restart_scp_non_working_vms.sh

Purpose: checks whether SCP to each local NAT-forwarded VM works and restarts VMs where SCP fails.

Important APIs/types/functions: environment `num_vms`, `sshpass scp`, timeout 10, files `~/vm_remote_*`, `force_stop_vm.sh`, `start_particular_vm.sh`, and NAT ports from 3022.

Control flow: loops over VM ports, attempts to copy remote scripts to each VM, checks exit status, restarts failing VMs, waits, and increments the port. State/persistence behavior: copies scripts to VM home directories and force-restarts failing VMs.

Dependencies/integration: used before distributing workloads. Risks/test signals: hard-coded password/user, broad source glob, no cleanup of copied files, and failure may be due to network/load rather than VM health.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/restart_scp_non_working_vms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/restart_unresponsive_vms.sh -->
# sources/test-tools/crashmonkey/vm_scripts/restart_unresponsive_vms.sh

Purpose: probes each local NAT-forwarded VM with a simple `rsh echo` and restarts VMs that do not respond.

Important APIs/types/functions: environment `num_vms`, `timeout -s KILL 10 rsh`, `force_stop_vm.sh`, `start_particular_vm.sh`, ports starting at 3022, and sleeps.

Control flow: loops VM indices, executes remote `echo abc`, if output is empty force-stops and restarts the VM, otherwise prints healthy. State/persistence behavior: can abruptly restart VMs; otherwise read-only.

Dependencies/integration: maintenance utility for the VirtualBox farm. Risks/test signals: empty output can reflect transient rsh failure rather than VM hang; no graceful shutdown or retry before kill.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/restart_unresponsive_vms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/scp_file_to_vms.sh -->
# sources/test-tools/crashmonkey/vm_scripts/scp_file_to_vms.sh

Purpose: copies one local file to the home directory of every local NAT-forwarded VM.

Important APIs/types/functions: one argument `file_to_scp`, environment `num_vms`, `scp -P`, user `user@127.0.0.1`, and ports from 3022.

Control flow: validates one arg, loops VM count, scps the file, and increments port. State/persistence behavior: writes a copy of the file into each VM home directory.

Dependencies/integration: ad hoc distribution helper. Risks/test signals: no password automation here unlike other scripts, no error handling, and unquoted file path can fail on spaces.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/scp_file_to_vms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/scp_remote_scripts_to_vms.sh -->
# sources/test-tools/crashmonkey/vm_scripts/scp_remote_scripts_to_vms.sh

Purpose: copies all `vm_remote_*` scripts and `cm_cleanup.sh` to each local NAT-forwarded VM.

Important APIs/types/functions: environment `num_vms`, `sshpass -p "password" scp`, `StrictHostKeyChecking no`, files `~/vm_remote_*` and `~/cm_cleanup.sh`, user `user`, ports from 3022.

Control flow: prints target VM count, loops VMs, copies remote scripts and cleanup script, then increments port. State/persistence behavior: updates scripts in VM home directories.

Dependencies/integration: run during setup and before workload distribution. Risks/test signals: hard-coded password, broad globs, no failure checks, and assumes scripts live in the caller's home directory.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/scp_remote_scripts_to_vms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/scp_segregated_workloads.sh -->
# sources/test-tools/crashmonkey/vm_scripts/scp_segregated_workloads.sh

Purpose: copies pre-segregated workload directories to selected remote server nodes.

Important APIs/types/functions: args start server, end server, segregated workload path, `live_nodes`, `scp -r -i ~/crashmonkey.pem`, user `cc`, and destination `~/seq2/`.

Control flow: loops indexed IPs from `live_nodes`, skips outside the requested server range, and copies `$seg_path/node<i>-<ip>/*` to the node. State/persistence behavior: writes workload files into remote `seq2` directories.

Dependencies/integration: follows `segregate_workloads*` output layout. Risks/test signals: assumes node directory names include IP exactly, no destination cleanup here, no error handling, and unquoted glob/source issues.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/scp_segregated_workloads.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/scp_segregated_workloads_parallel.sh -->
# sources/test-tools/crashmonkey/vm_scripts/scp_segregated_workloads_parallel.sh

Purpose: starts multiple background SCP jobs to distribute segregated workloads across server batches.

Important APIs/types/functions: args `batch_size`, `num_servers`, `seg_path`, range variables, and `nohup ./scp_segregated_workloads.sh ... > out<i>.log &`.

Control flow: partitions server indices into ranges and launches the nonparallel copy script for each range in the background. State/persistence behavior: creates logs and remote workload copies via child scripts.

Dependencies/integration: wrapper around `scp_segregated_workloads.sh`. Risks/test signals: no synchronization or failure aggregation, and parallel jobs may overload network or remote SSH.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/scp_segregated_workloads_parallel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/scp_update_hostname.sh -->
# sources/test-tools/crashmonkey/vm_scripts/scp_update_hostname.sh

Purpose: copies `update_hostname.sh` to VM numbers 9 through 16 using NAT SSH ports 3030 through 3037.

Important APIs/types/functions: fixed port start 3030, loop `seq 9 16`, `scp -P`, and destination `user@127.0.0.1:~/`.

Control flow: loops VM numbers, copies the script, increments port. State/persistence behavior: writes the hostname update script into selected VM home directories.

Dependencies/integration: older/specialized hostname setup helper. Risks/test signals: hard-coded VM range and ports, no password automation or error handling.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/scp_update_hostname.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/scp_workloads_to_vms.sh -->
# sources/test-tools/crashmonkey/vm_scripts/scp_workloads_to_vms.sh

Purpose: distributes local `~/seq2/vm<N>` workload sets to each local NAT-forwarded VM after first copying remote helper scripts.

Important APIs/types/functions: environment `num_vms`, `scp_remote_scripts_to_vms.sh`, `rsh` cleanup/create commands, `scp -P`, user `user`, ports from 3022.

Control flow: copies remote scripts to all VMs, loops VMs, removes and recreates `~/seq2` remotely, copies workload files for that VM, increments port, and prints completion. State/persistence behavior: replaces per-VM remote workload directories.

Dependencies/integration: expects local workload partitioning under `~/seq2/vm<i>`. Risks/test signals: no error handling, destructive `rm -r ~/seq2`, hard-coded user/ports, and no quoting around globs.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/scp_workloads_to_vms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/segregate_workloads.sh -->
# sources/test-tools/crashmonkey/vm_scripts/segregate_workloads.sh

Purpose: partitions generated `j-lang<N>.cpp` workloads across servers and VMs into a directory tree suitable for later SCP distribution.

Important APIs/types/functions: args `num_per_vm`, start workload `k`, max workload, workload base path, output path, `live_nodes`, fixed `num_vms=12`, `mkdir -p`, `cp`.

Control flow: removes the output path, loops nodes from `live_nodes`, creates `node<i>-<ip>/vm<j>` directories, copies `num_per_vm` sequential workloads into each VM directory, and stops once `k > max`.

State/persistence behavior: deletes and recreates local workload partition directories. Dependencies/integration: feeds `scp_segregated_workloads.sh`.

Risks/test signals: destructive `rm -r` without existence/guard, no missing-file checks, fixed 12 VMs per node, and no quoting of paths.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/segregate_workloads.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/segregate_workloads_range.sh -->
# sources/test-tools/crashmonkey/vm_scripts/segregate_workloads_range.sh

Purpose: partitions workloads for only a selected range of server indices while preserving global workload numbering offsets for skipped servers.

Important APIs/types/functions: args `num_per_vm`, `max`, workload base path, start server, end server, fixed `num_vms=12`, `live_nodes`, and output `workloads/seg/node<i>-<ip>/vm<j>`.

Control flow: loops all live nodes with global server index and workload counter. For skipped servers it advances `k` by `num_vms * num_per_vm`; for included servers it creates directories and copies sequential `j-lang<k>.cpp` files until max.

State/persistence behavior: creates/updates `workloads/seg` subdirectories but does not remove the root. Dependencies/integration: used by the parallel range wrapper.

Risks/test signals: arithmetic uses escaped `expr` multiplication, missing source files are not handled, fixed VM count, and output from parallel invocations can interleave.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/segregate_workloads_range.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/segregate_workloads_range_parallel.sh -->
# sources/test-tools/crashmonkey/vm_scripts/segregate_workloads_range_parallel.sh

Purpose: removes the shared segmented workload directory and starts background range partitioners for batches of servers.

Important APIs/types/functions: args `num_per_vm`, `max_workload`, workload base path, `batch_size`, `num_servers`, `rm -r workloads/seg`, and `nohup ./segregate_workloads_range.sh ...`.

Control flow: deletes `workloads/seg`, computes server ranges, launches one background range script per batch, and increments the range. State/persistence behavior: destructively resets and recreates local workload partitions via children.

Dependencies/integration: used before parallel SCP distribution. Risks/test signals: multiple background scripts write under the same tree without coordination, no wait/failure handling, and `rm -r` can fail or remove unintended content if run from the wrong directory.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/segregate_workloads_range_parallel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/setup.sh -->
# sources/test-tools/crashmonkey/vm_scripts/setup.sh

Purpose: large provisioning script for a server that will host multiple CrashMonkey VirtualBox VMs. It installs dependencies, clones CrashMonkey, installs VirtualBox, imports a base VM, clones more VMs, starts them, distributes helper scripts, and updates hostnames.

Important APIs/types/functions: appending `vm_aliases` to `.bashrc`, `apt-get`, `git clone`, VirtualBox `.deb` and extension pack downloads, `VBoxManage import`, `clone_vms.sh`, `start_all_vms.sh`, `scp_remote_scripts_to_vms.sh`, and `trigger_remote_script_update_hostname.sh`.

Control flow: update shell aliases, create `projects`, install packages, clone repo, install filesystem tools and VirtualBox dependencies, install VirtualBox packages/extension pack, import OVA, clone VMs 2-16, export/read `num_vms`, start VMs, sleep, copy scripts, update hostnames, and print completion.

State/persistence behavior: heavily mutates the host system, home directory, bashrc, installed packages, VirtualBox registry, and VM state. Dependencies/integration: assumes Ubuntu/Xenial-era package names, an OVA in home, scripts in the current directory, and passwordless/interactive sudo as needed.

Risks/test signals: highly environment-specific, appends aliases repeatedly, no `set -e`, hard-coded VirtualBox version, and broad side effects make it unsuitable for unattended reruns without cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/start_all_vms.sh -->
# sources/test-tools/crashmonkey/vm_scripts/start_all_vms.sh

Purpose: starts all configured local VirtualBox VMs headlessly, spacing startups by 15 seconds.

Important APIs/types/functions: environment `num_vms`, loop `seq 1 $num_vms`, `VBoxManage startvm ubuntu16-vm<i> --type headless`, and `sleep 15`.

Control flow: loops VM numbers, starts each, prints sleep message, and sleeps. State/persistence behavior: transitions VMs to running state.

Dependencies/integration: used by setup and restart workflows. Risks/test signals: no validation that `num_vms` is set, no check if a VM is already running, and no failure handling.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/start_all_vms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/start_particular_vm.sh -->
# sources/test-tools/crashmonkey/vm_scripts/start_particular_vm.sh

Purpose: starts one numbered VirtualBox VM headlessly.

Important APIs/types/functions: argument `vm`, `VBoxManage startvm ubuntu16-vm"$vm" --type headless`, and timestamped echo. Control flow validates one arg, then starts the VM.

State/persistence behavior: changes VM runtime state. Dependencies/integration: called by restart scripts after force-stopping a VM.

Risks/test signals: no check for already-running or missing VM; failure is only visible through VBoxManage output/exit.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/start_particular_vm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/stop_all_vms.sh -->
# sources/test-tools/crashmonkey/vm_scripts/stop_all_vms.sh

Purpose: powers off all configured VirtualBox VMs.

Important APIs/types/functions: environment `num_vms`, `VBoxManage controlvm ubuntu16-vm<i> poweroff`. Control flow loops from 1 to `num_vms` and powers off each VM.

State/persistence behavior: abruptly powers off VM runtime state, similar to pulling power. Dependencies/integration: operator utility for shutting down a VM farm.

Risks/test signals: no validation or graceful ACPI shutdown, and no error handling for stopped/missing VMs.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/stop_all_vms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script.sh -->
# sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script.sh

Purpose: runs a named remote script with sudo on every local NAT-forwarded VM.

Important APIs/types/functions: one argument `remote_script`, environment `num_vms`, `rsh -p`, fixed password piped to `sudo -S bash`, and ports from 3022.

Control flow: validates one arg, loops VMs, prints a banner, runs the remote script, and increments the port. State/persistence behavior: depends entirely on the remote script; this wrapper initiates remote side effects.

Dependencies/integration: generic trigger for the VM farm. Risks/test signals: hard-coded password, command quoting permits argument/shell issues, no failure handling, and rsh is insecure.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_trigger_xfsMonkey.sh -->
# sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_trigger_xfsMonkey.sh

Purpose: starts `vm_remote_trigger_script.sh` for a given filesystem on each local NAT-forwarded VM in the background, then checks process status.

Important APIs/types/functions: arg `fs`, environment `num_vms`, `rsh`, `nohup`, `sudo -S`, remote `/home/user/vm_remote_trigger_script.sh`, `ps aux | grep -e xfsMonkey -e vm_remote_trigger`, and sleeps.

Control flow: validates filesystem arg, loops VMs, launches remote trigger with output to `trigger_<fs>.log`, sleeps 10 seconds, checks remote processes, sleeps 5 seconds, and increments port. State/persistence behavior: starts long-running remote CrashMonkey tests.

Dependencies/integration: used to fan out XFSMonkey runs across local VMs. Risks/test signals: complex nested quoting/backgrounding, hard-coded password/user, and no verification that the background job actually survives after the shell exits.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_trigger_xfsMonkey.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_trigger_xfsMonkey_parallel.sh -->
# sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_trigger_xfsMonkey_parallel.sh

Purpose: launches batched background trigger scripts to start XFSMonkey across VM ranges.

Important APIs/types/functions: args `fs` and `batch_size`, environment `num_vms`, range variables, and `nohup ./trigger_remote_script_trigger_xfsMonkey_range.sh ... > out_trigger_log_<fs>_<st>_<end>.log &`.

Control flow: validates args, partitions VM indices into batches, starts one range trigger per batch, and increments the range. State/persistence behavior: creates local logs and starts remote XFSMonkey jobs via child scripts.

Dependencies/integration: parallel wrapper for the range trigger script. Risks/test signals: no wait/failure aggregation, potential overlapping VM ranges if arguments are wrong, and background jobs can overload local/remote resources.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_trigger_xfsMonkey_parallel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_trigger_xfsMonkey_range.sh -->
# sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_trigger_xfsMonkey_range.sh

Purpose: triggers XFSMonkey runs only for a selected VM index range.

Important APIs/types/functions: args filesystem, start VM, end VM, environment `num_vms`, `rsh`, `sudo -S`, remote `vm_remote_trigger_script.sh`, and ports from 3022.

Control flow: loops all VM indices, skips those outside range while still advancing port, runs the remote trigger synchronously for included VMs, sleeps one second, and increments port. State/persistence behavior: starts or runs remote CrashMonkey workflows on selected VMs.

Dependencies/integration: used by the parallel trigger wrapper. Risks/test signals: no backgrounding here, so long remote runs can serialize per VM in a batch; hard-coded password and no failure capture.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_trigger_xfsMonkey_range.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_update_hostname.sh -->
# sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_update_hostname.sh

Purpose: runs the remote hostname-update script on every local NAT-forwarded VM, passing the VM number.

Important APIs/types/functions: environment `num_vms`, fixed `remote_script=vm_remote_update_hostname_script.sh`, `sshpass rsh`, `StrictHostKeyChecking no`, password piped to `sudo`, and ports from 3022.

Control flow: loops VM numbers, invokes the remote script with the current VM number, and increments port. State/persistence behavior: changes `/etc/hostname`, `/etc/hosts`, and runtime hostname inside each VM.

Dependencies/integration: called by `setup.sh` after cloning VMs. Risks/test signals: hard-coded password, no success checks, and hostname replacement assumes old name `ubuntu16-vm1`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_update_hostname.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/update_hostname.sh -->
# sources/test-tools/crashmonkey/vm_scripts/update_hostname.sh

Purpose: local/remote script to set a cloned VM's hostname to `ubuntu16-vm<N>`.

Important APIs/types/functions: one argument `num`, writes `/etc/hostname`, `sed -i` replacement in `/etc/hosts`, and `sudo hostname`. Control flow validates one arg and applies the changes.

State/persistence behavior: mutates system hostname files and runtime hostname. Dependencies/integration: copied or invoked by hostname update workflows.

Risks/test signals: assumes old hostname appears as `ubuntu16-vm1`, requires root for `/etc` writes, and can replace unintended text in `/etc/hosts`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/update_hostname.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_check_running.sh -->
# sources/test-tools/crashmonkey/vm_scripts/vm_remote_check_running.sh

Purpose: remote VM status helper that reports whether any `xfsMonkey` process is running.

Important APIs/types/functions: `ps aux`, `grep xfsMonkey`, `wc -l`, `uname -n`, and conditional echo. Control flow counts matching processes and prints either no run or some run in progress.

State/persistence behavior: read-only process inspection. Dependencies/integration: can be triggered remotely by operator scripts.

Risks/test signals: process matching may count unrelated grep-like command lines except it excludes grep; it does not check `c_harness` or remote trigger scripts.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_check_running.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_clear_diffs.sh -->
# sources/test-tools/crashmonkey/vm_scripts/vm_remote_clear_diffs.sh

Purpose: removes all remote CrashMonkey diff result files inside a VM.

Important APIs/types/functions: `rm -r /home/user/projects/crashmonkey/diff_results/*`. Control flow is a single command.

State/persistence behavior: destructively deletes diff artifacts. Dependencies/integration: remote cleanup helper.

Risks/test signals: no existence check, no quoting, and running as a user with unexpected path layout can fail or delete unintended glob matches.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_clear_diffs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_delete_snap.sh -->
# sources/test-tools/crashmonkey/vm_scripts/vm_remote_delete_snap.sh

Purpose: deletes CrashMonkey snapshot artifacts from a remote VM build directory using sudo.

Important APIs/types/functions: `echo password | sudo -S rm -r /home/user/projects/crashmonkey/build/snap_*` and `build/create_snap`. Control flow is two deletion commands.

State/persistence behavior: removes potentially large snapshot files/directories. Dependencies/integration: remote disk-space cleanup helper.

Risks/test signals: hard-coded password/path, destructive glob, no existence checks, and no protection against concurrent runs using snapshots.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_delete_snap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_kill_all_running.sh -->
# sources/test-tools/crashmonkey/vm_scripts/vm_remote_kill_all_running.sh

Purpose: kills all remote `xfsMonkey` and `c_harness` processes inside a VM.

Important APIs/types/functions: `ps aux`, `grep -e xfsMonkey -e c_harness`, PID extraction, and `sudo kill -9`. Control flow loops over matching PIDs and force kills each.

State/persistence behavior: terminates active tests abruptly and may leave mounts/modules/diffs in partial state. Dependencies/integration: emergency cleanup helper.

Risks/test signals: broad process matching, hard-coded password, no graceful cleanup, and no follow-up module unmount cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_kill_all_running.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_progress_script.sh -->
# sources/test-tools/crashmonkey/vm_scripts/vm_remote_progress_script.sh

Purpose: reports progress of a remote XFSMonkey run by scraping logs, workload count, diff count, and RAM disk errors.

Important APIs/types/functions: reads `/home/user/projects/crashmonkey/xfsmonkey*.log`, greps `Test` and `Error inserting RAM disk module`, counts `build/xfsMonkeyTests/j-lang*`, counts diff results, and prints host plus metrics.

Control flow: assigns `completed`, `ram_disk_error`, `total`, and `num_diffs`, then echoes a formatted one-line status. State/persistence behavior: read-only.

Dependencies/integration: remote operator status script. Risks/test signals: glob failures and missing logs can produce noisy errors; `completed` parsing assumes exact log format.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_progress_script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_trigger_script.sh -->
# sources/test-tools/crashmonkey/vm_scripts/vm_remote_trigger_script.sh

Purpose: remote VM script that prepares CrashMonkey, compiles copied workloads, and launches XFSMonkey for a requested filesystem.

Important APIs/types/functions: arg `fs`, process guards for `xfsMonkey` and `vm_remote_trigger_script`, `apt-get install`, `git checkout .`, `git pull`, `git checkout master`, log/diff cleanup, `cm_cleanup.sh`, `/mnt/snapshot`, workload copy from `~/seq2`, `make`, `build/xfsMonkeyTests`, and `nohup sudo python xfsMonkey.py`.

Control flow: validates filesystem arg, exits if a run/trigger appears active, installs packages, updates repo, removes logs/diffs, performs module/mount cleanup, recreates mount point, removes old j-lang sources and shared objects, copies new workloads, compiles, moves built `.so` files into `build/xfsMonkeyTests`, then starts XFSMonkey in the background with output log.

State/persistence behavior: heavily mutates the remote CrashMonkey checkout, installed packages, build outputs, logs, diff results, kernel module/mount state, and starts a long-running root test process. Dependencies/integration: central remote execution path for distributed workloads.

Risks/test signals: destructive `git checkout .` discards remote changes, hard-coded password/path/device, weak process guards, no `set -e`, and background command composition with `nohup echo password | sudo -S python ... &` is fragile.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_trigger_script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_update_hostname_script.sh -->
# sources/test-tools/crashmonkey/vm_scripts/vm_remote_update_hostname_script.sh

Purpose: remote VM hostname update script equivalent to `update_hostname.sh`.

Important APIs/types/functions: one argument `num`, constructed hostname `ubuntu16-vm<num>`, write `/etc/hostname`, `sed -i` in `/etc/hosts`, and `sudo hostname`.

Control flow: validates one arg, sets the hostname files and runtime hostname. State/persistence behavior: mutates system identity inside the VM.

Dependencies/integration: invoked by `trigger_remote_script_update_hostname.sh`. Risks/test signals: assumes `ubuntu16-vm1` appears in `/etc/hosts`, requires root privileges, and has no verification after setting.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/vm_scripts/vm_remote_update_hostname_script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/xfsMonkey.py -->
# sources/test-tools/crashmonkey/xfsMonkey.py

Purpose: Python 3 runner that executes a directory of compiled CrashMonkey test shared objects through `build/c_harness`, collects diff files, and produces console/log summaries. It is the main local runner used by demo and remote VM scripts.

Important APIs/types/functions: `Log` stdout tee class, `build_parser`, `cleanup`, time helpers, `print_setup`, `ensure_sudo`, `validate_setup`, and `main`. CLI arguments include filesystem type, disk size, iterations, test device, flag device, and test path.

Control flow: `main` opens a timestamped log, tees stdout, parses/validates args, prints setup, creates `diff_results` and counter files, loops over `.so` files in the test path, builds a `c_harness` command for each, calls cleanup before each run, retries harness execution up to four times on failure, trims harness output around `Reordering`, writes log summaries, copies the last diff file through `copy_diff.sh`, then restores stdout and closes the log.

State/persistence behavior: requires root, unmounts `/mnt/snapshot`, unloads modules, creates `diff_results`, writes counters and `out`, runs kernel-module-backed harnesses, and writes timestamped logs. Dependencies/integration: depends on `build/c_harness`, `copy_diff.sh`, CrashMonkey kernel modules, test `.so` files, and Linux devices `/dev/sda`/`/dev/cow_ram0` by default.

Risks/test signals: shell=True command construction and relative paths are fragile, retries hide some harness errors, `iterations` argument is parsed but not used in the command, diff selection uses `tail -n -1` rather than a clear last-file expression, and cleanup errors are ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/xfsMonkey.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/Makefile -->
# sources/test-tools/cthon04/Makefile

Purpose: top-level Makefile for the Connectathon 2004 testsuite. It builds helper programs and recursively builds/copies/distributes basic, general, special, tools, and lock test subdirectories.

Important APIs/types/functions: variables `DESTDIR`, `COPYFILES`, `include tests.init`, targets `all`, `lint`, `domount`, `getopt`, `clean`, `copy`, `dist`, `tar`, `rpm`, and `mknewdirs`. `domount` is built from `domount.c` and made setuid root.

Control flow: `all` builds `domount` and `getopt`, runs make in each subdirectory, and ensures `runtests` is executable. `copy` and `dist` create destination subdirectories and copy binaries or sources recursively. `tar` packages a distribution tree; `rpm` runs `rpmbuild`.

State/persistence behavior: creates binaries, changes ownership/mode of `domount`, copies files into `DESTDIR`, creates tarballs, and may invoke RPM build tooling. Dependencies/integration: expects `tests.init`, subdirectory makefiles, C compiler variables, and root permissions for chown/setuid.

Risks/test signals: default `DESTDIR` is invalid to prevent accidental copy, `-chown` ignores failure, recursive makes propagate environment assumptions, and setuid root helper creation is security-sensitive.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/Makefile -->
# sources/test-tools/cthon04/basic/Makefile

Purpose: Makefile for the Connectathon basic test programs. It builds original tests `test1` through `test9`, auxiliary tests, lint targets, copy targets, and source distribution artifacts.

Important APIs/types/functions: variables `TESTS`, `AUXTESTS`, `DOSRUNFILES`, `DOSBUILDFILES`, `DESTDIR`, `INCLUDES`, `include ../tests.init`, targets `all`, `origtests`, `auxtests`, individual `test*` link rules, `lint`, `clean`, `copy`, and `dist`.

Control flow: `all` builds original and auxiliary tests then makes `runtests` executable. Each test links its matching `.c` file with `subr.o` and `$(LIBS)`. `lint` runs lint over each source; `copy` copies runnable files to `DESTDIR`; `dist` copies sources and extracts DOS support files into the destination.

State/persistence behavior: creates test binaries/object files, removes them on clean, and copies sources/binaries into distribution directories. Dependencies/integration: consumes compiler flags and libs from `../tests.init` and shared helper `subr.c`.

Risks/test signals: repetitive rules make omissions easy, `copy` depends only on `$(TESTS)` but copies `$(AUXTESTS)` too, and DOS file tar pipeline assumes matching files exist.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/Makefile -->
