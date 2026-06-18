# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/gtest/gtest-all.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007375`: lines 1-7098, `Docs/researches/chunks/subset-b-007375_research.md`
- `subset-b-007376`: lines 7099-10403, `Docs/researches/chunks/subset-b-007376_research.md`

## Chunk Research

### subset-b-007375: lines 1-7098

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/gtest/gtest-all.cc lines 1-7098

## Scope and Purpose

This chunk is the first 7098 lines of Hadoop's vendored, fused Google Test implementation. It begins with `gtest-all.cc` including `gtest/gtest.h`, then inlines major portions of Google Test's SPI helpers, private internal declarations, core test execution engine, result formatting/listening, XML/stream output, flag parsing, sharding, initialization, and the opening of death-test support.

The code exists so Hadoop native C/C++ tests can compile Google Test as a single translation unit. Within this chunk, the effective runtime purpose is to collect registered tests, parse `--gtest_*` flags and `GTEST_*` environment variables, decide which tests should run, execute fixtures and test bodies with exception/SEH handling, report assertion results to listeners, and optionally emit console, XML, socket-stream, sharded, repeated, shuffled, and death-test-aware output.

## Important APIs, Types, and Functions

- `testing::ScopedFakeTestPartResultReporter` and `testing::internal::SingleFailureChecker` implement the SPI used by `EXPECT_FATAL_FAILURE`, `EXPECT_NONFATAL_FAILURE`, and their all-thread variants. They temporarily replace either the per-thread or global `TestPartResultReporterInterface`, capture failures into `TestPartResultArray`, and validate that exactly one expected failure occurred.
- Internal flag names and defaults are declared for `also_run_disabled_tests`, `break_on_failure`, `catch_exceptions`, `color`, `filter`, `list_tests`, `output`, `print_time`, `random_seed`, `repeat`, `shuffle`, `stack_trace_depth`, `stream_result_to`, `throw_on_failure`, and optional `flagfile`; death-test flags begin near the end of the chunk.
- `testing::internal::UnitTestImpl` is the central private state holder behind `testing::UnitTest`. It owns test cases, environments, listeners, ad hoc results, stack trace getter, random seed/generator, death-test control information, reporter pointers, and per-thread trace/reporting stacks.
- `testing::internal::UnitTestOptions` handles output format/path resolution and filter matching. It implements glob-style matching with `?`, `*`, colon-separated positive filters, and dash-separated negative filters.
- `testing::Message`, `testing::AssertionResult`, and comparison helpers (`EqFailure`, `CmpHelperEQ`, `CmpHelperSTREQ`, `DoubleNearPredFormat`, `FloatLE`, `DoubleLE`, substring helpers, HRESULT helpers) construct user-facing assertion diagnostics.
- `testing::internal::edit_distance::CalculateOptimalEdits` and `CreateUnifiedDiff` generate unified diffs for multiline equality failures.
- String/encoding utilities include null-safe C-string comparison, wide-string UTF-8 conversion, case-insensitive comparisons, integer/byte formatting, and `StringStreamToString` NUL escaping.
- `testing::TestResult`, `Test`, `TestInfo`, and `TestCase` implement the result container, fixture lifecycle, individual test instance execution, and grouped test-case execution.
- `PrettyUnitTestResultPrinter`, `TestEventRepeater`, `XmlUnitTestResultPrinter`, `StreamingListener`, and `TestEventListeners` form the event-listener and output stack.
- `testing::UnitTest` exposes the singleton public facade and delegates most behavior to `UnitTestImpl`; important methods include `GetInstance`, result/count accessors, `AddEnvironment`, `AddTestPartResult`, `RecordProperty`, and `Run`.
- Initialization and flag functions include `ParseGoogleTestFlag`, `ParseGoogleTestFlagsOnly`, `InitGoogleTestImpl`, and public `InitGoogleTest` overloads for `char**` and `wchar_t**`.
- Sharding functions include `WriteToShardStatusFileIfNeeded`, `ShouldShard`, `Int32FromEnvOrDie`, and `ShouldRunTestOnShard`.
- Death-test support starts with `death_test_style`, `death_test_use_fork`, `internal_run_death_test`, `InDeathTestChild`, `ExitedWithCode`, POSIX `KilledBySignal`, `ExitSummary`, `ExitedUnsuccessfully`, `DeathTestThreadWarning`, death-test status characters, `DeathTestOutcome`, and the start of `DeathTestAbort`.

## Control Flow

Static test registration reaches `MakeAndRegisterTestInfo`, which constructs `TestInfo` and calls `UnitTestImpl::AddTestInfo`. The first registration captures the original working directory for later XML output and death-test re-exec behavior. `UnitTestImpl::GetTestCase` creates or reuses a `TestCase`; death-test cases matching `*DeathTest:*DeathTest/*` are inserted before non-death cases so they run first.

`InitGoogleTest` copies original arguments into `g_argvs`, parses and removes recognized Google Test flags from `argv`, loads optional flagfiles, sets `g_help_flag` for help or unrecognized Google Test-prefixed flags, and runs `PostFlagParsingInit`. Post-flag initialization is idempotent; it registers custom listeners, parses death-test subprocess control, suppresses child-process event forwarding, expands parameterized tests, configures XML output, and configures stream output.

`UnitTest::Run` captures `catch_exceptions`, sets Windows error modes when needed, manages the `TEST_PREMATURE_EXIT_FILE` protocol outside death-test children, and delegates to `UnitTestImpl::RunAllTests` through the exception wrapper. `RunAllTests` verifies initialization, handles `--help`, writes the shard-status file if requested, disables sharding inside death-test subprocesses, filters tests, optionally lists tests, initializes shuffle seed, emits `OnTestProgramStart`, and loops over repeats.

Each iteration clears non-ad-hoc results, shuffles test cases and tests if enabled, emits iteration and environment setup events, runs each selected `TestCase`, tears down environments in reverse registration order, records elapsed time, emits iteration end, tracks failure, unshuffles for reproducibility, and advances the random seed for the next iteration.

`TestCase::Run` sets the current test case, emits start/end events, runs `SetUpTestCase`, executes every selected `TestInfo`, and runs `TearDownTestCase`. `TestInfo::Run` sets the current test info, emits start/end events, creates a fixture via its factory, runs `Test::Run` if construction succeeded without fatal failure, destroys the fixture, and stores elapsed time. `Test::Run` validates fixture-class consistency, invokes `SetUp`, conditionally invokes `TestBody`, and always invokes `TearDown`, all through exception/SEH wrappers.

Assertions flow through `AssertHelper::operator=`, then `UnitTest::AddTestPartResult`. This appends active `SCOPED_TRACE` context and optional OS stack trace, creates a `TestPartResult`, routes it to the current per-thread reporter, and optionally breaks into a debugger, throws `GoogleTestFailureException`, or exits depending on flags.

## State and Persistence Behavior

The dominant runtime state is process-local and owned by the singleton `UnitTest`/`UnitTestImpl`. `UnitTestImpl` owns `TestCase*`, `Environment*`, default listeners, ad hoc results, current test pointers, per-thread reporters, per-thread trace stack, random seed/generator, and death-test factory/control data. `TestCase` owns `TestInfo` instances and preserves original order through index vectors so shuffle can be undone. `TestInfo` owns its fixture factory and stores per-test `TestResult`.

Persistent side effects are limited to test runner outputs:

- XML output creates directories and writes the selected XML file, defaulting to `test_detail.xml` in the original working directory when `--gtest_output=xml` omits a file.
- `GTEST_SHARD_STATUS_FILE` is opened and overwritten as a marker that the binary supports the sharding protocol.
- `TEST_PREMATURE_EXIT_FILE` is created with a single byte on entry to `UnitTest::Run` and removed on normal exit.
- Streaming output opens a TCP connection to `host:port` and sends URL-encoded event lines.
- Console output writes to stdout/stderr and may use ANSI or Windows console colors.
- Death-test child control uses flags and, after the chunk boundary, status descriptors/pipes; the chunk ends inside `DeathTestAbort` before the full propagation logic is visible.

Flag state is global static state initialized from environment variables and then overridden by command-line parsing. `GTestFlagSaver`, created by each `Test` fixture, snapshots and restores all Google Test flags around a test instance so tests modifying flags do not leak changes.

## Dependencies and Integration Points

This file depends on `gtest/gtest.h` for public declarations, macros, type aliases, and platform feature macros. It uses C/POSIX/Windows APIs conditionally: time APIs (`gettimeofday`, `_ftime64`, `localtime_r/localtime_s`), filesystem APIs via `FilePath`, sockets (`getaddrinfo`, `socket`, `connect`, `write`, `close`) for result streaming, Windows SEH and console APIs, process status macros (`WIFEXITED`, `WTERMSIG`) for death tests, and environment access through Google Test's `posix` wrapper.

The main integration point for Hadoop native tests is the standard Google Test lifecycle: C++ test files register tests at static initialization, call `InitGoogleTest`, and run `RUN_ALL_TESTS`. Build integration compiles this fused file instead of separate upstream `.cc` files. Runtime integration with test infrastructure happens through XML reports, sharding environment variables, status files, premature-exit markers, and process exit code `0` or `1`.

Event listeners are the internal extension point: the default pretty printer, XML generator, optional stream listener, and custom `GTEST_CUSTOM_TEST_EVENT_LISTENER_` all receive lifecycle events through `TestEventRepeater`. SPI helpers replace reporters for tests that assert on Google Test's own failure behavior.

## Risks and Edge Cases

- This is vendored, older Google Test code. Changing it locally risks diverging from upstream semantics and from Hadoop's existing native-test build assumptions.
- The fused file contains multiple inlined upstream source sections and feature-gated code. Small edits can break one platform even if the active platform builds successfully.
- `UnitTestImpl::GetTestCase(int)` appears to compute `index` from `test_case_indices_` but returns `test_cases_[i]` rather than `test_cases_[index]`; the mutable accessor uses `index`. If this is not an upstream intentional quirk for this version, reflection order under shuffle/listener access is a risk.
- The `ScopedPrematureExitFile` constructor ignores `FOpen` failure but still calls `fwrite`/`fclose` unconditionally on `pfile`; if `FOpen` returns null, this can crash while trying to create the premature-exit marker.
- XML property validation rejects reserved attribute names by adding failures; code using `RecordProperty` with keys like `name`, `time`, or `classname` will affect test results.
- `ShouldShard` treats inconsistent shard variables as fatal process errors. Misconfigured CI environments can fail before running any tests.
- Filter matching is recursive and simple, not regex-based; unusual or very long patterns could be inefficient, but test names are expected to be short.
- `break_on_failure` deliberately crashes or invokes `DebugBreak`; `throw_on_failure` can throw or exit. These flags alter control flow and can surprise embedding frameworks.
- Death-test code is highly platform-specific and begins in this chunk. The chunk documents only the setup and initial helpers; full risk assessment requires later chunks covering process spawning, status pipes, and regex matching of child output.
- Streaming output logs warnings on socket failures but otherwise does not make tests fail; consumers relying on stream delivery need separate monitoring.

## Test Signals

Relevant behavioral signals for this chunk come from compiling and running Hadoop native Google Test binaries with combinations of:

- Basic pass/fail tests to exercise `TestInfo::Run`, `TestCase::Run`, `UnitTestImpl::RunAllTests`, and pretty printer output.
- Fatal and nonfatal assertion tests, including `SCOPED_TRACE`, custom messages, wide strings, multiline equality failures, and `EXPECT_*_FAILURE` SPI macros.
- Fixture lifecycle tests verifying `SetUp`, `TestBody`, `TearDown`, `SetUpTestCase`, and `TearDownTestCase`, including exception paths and fatal setup failure behavior.
- `--gtest_filter`, disabled tests, `--gtest_also_run_disabled_tests`, `--gtest_list_tests`, `--gtest_repeat`, `--gtest_shuffle`, and `--gtest_random_seed` to validate selection/order/reproducibility.
- XML output tests checking directory creation, escaping, invalid XML character removal, test properties, typed/value parameter attributes, timestamps, elapsed time, and failure CDATA.
- Sharding tests with valid and invalid `GTEST_TOTAL_SHARDS`, `GTEST_SHARD_INDEX`, and `GTEST_SHARD_STATUS_FILE`.
- Premature-exit-file tests that verify marker creation/removal on normal runs and persistence on abnormal termination.
- Death-test smoke tests for `ASSERT_DEATH`, `ExitedWithCode`, and signal predicates, with later chunks needed for full subprocess coverage.

## Chunk Boundary Notes

The source window ends at line 7098 inside `testing::internal::DeathTestAbort`, immediately after it reads `GetUnitTestImpl()->internal_run_death_test_flag()` and tests `flag != NULL`. Later chunks are required to describe how the abort message is sent to the death-test parent process, how child status is read, and how death-test pass/fail conditions are completed.

### subset-b-007376: lines 7099-10403

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/gtest/gtest-all.cc lines 7099-10403

## Scope

This chunk is the final range of Hadoop's vendored fused Google Test implementation, `gtest-all.cc`. It starts in the middle of the death-test implementation and continues through several embedded Google Test source sections: platform-specific death-test process management, `FilePath` helpers, internal POSIX/Windows thread and synchronization helpers, regular expression support for death tests, source-location/logging and stream-capture utilities, environment-backed flag parsing, universal value printers, `TestPartResult` helpers, and typed-test registration validation.

The code is infrastructure for Hadoop native C/C++ tests rather than Hadoop filesystem logic. Its behavior still affects Hadoop's native test reliability, diagnostics, XML/log output paths, death-test behavior, and assertion message rendering.

## Purpose and Major API Surface

The death-test tail provides the concrete machinery behind `ASSERT_DEATH`, `EXPECT_DEATH`, and related Google Test APIs when `GTEST_HAS_DEATH_TEST` is enabled. It defines internal fatal-check macros, shared `DeathTestImpl` state, Windows and POSIX death-test subclasses, child-process command-line construction, status-byte transport, and parsing for the internal rerun flag.

`DeathTest::Create`, `DeathTest::LastMessage`, and `DeathTest::set_last_death_test_message` delegate to `UnitTestImpl` and maintain the last diagnostic string. `DeathTestImpl` stores the tested statement, expected `RE`, spawn status, exit status, outcome, and parent/child pipe descriptors. `ReadAndInterpretStatusByte()` translates child pipe data into `DIED`, `RETURNED`, `THREW`, `LIVED`, or fatal internal errors. `Passed(bool status_ok)` combines child outcome, exit status, captured stderr, and regex matching into the final success decision.

On Windows, `WindowsDeathTest` uses `CreatePipe`, inheritable handles, `CreateEvent`, `CreateProcessA`, `WaitForMultipleObjects`, `WaitForSingleObject`, `GetExitCodeProcess`, and handle duplication through `GetStatusFileDescriptor()`. Windows death tests are treated as threadsafe regardless of the `fast` setting because they always launch a new process.

On POSIX-like platforms, `ForkingDeathTest` provides common `waitpid` handling. `NoExecDeathTest` implements fast death tests with `fork()` and direct child execution. `ExecDeathTest` implements threadsafe death tests by re-executing the current test binary with `--gtest_filter` and `--gtest_internal_run_death_test` flags. It builds argv through the `Arguments` helper, supports injectable argv vectors, optionally appends platform-provided extra death-test arguments, and spawns children through `fork`, `clone`, or QNX `spawn`.

`DefaultDeathTestFactory::Create` selects `WindowsDeathTest`, `ExecDeathTest`, or `NoExecDeathTest` based on `GTEST_FLAG(death_test_style)`, while also filtering internal reruns to the one death-test instance encoded in `InternalRunDeathTestFlag`.

`FilePath` implements platform-aware path utilities used heavily by Google Test output generation. It exposes current-directory detection, extension removal, last separator lookup, basename/dirname extraction, output filename construction, path concatenation, file/directory existence checks, root and absolute path checks, unique filename generation, recursive directory creation, single folder creation, trailing-separator removal, and separator normalization.

Internal thread helpers include `GetThreadCount()` implementations for Linux, macOS, QNX, AIX, and a portable fallback. On Windows, the chunk also implements `AutoHandle`, `Notification`, `Mutex`, `ThreadWithParamBase`, and the `ThreadLocalRegistry` implementation that tracks per-thread values and cleans them up when threads exit.

The regex section implements `testing::internal::RE`. When POSIX regex is available, it compiles full and partial extended regexes with `regcomp` and matches with `regexec`. When simple regex is used, it implements a small custom matcher supporting anchors, `.`, escapes, word/digit/space classes, and `?`, `*`, `+` repetition.

Utility APIs include `FormatFileLocation`, `FormatCompilerIndependentFileLocation`, `GTestLog`, stream capture helpers (`CaptureStdout`, `CaptureStderr`, `GetCapturedStdout`, `GetCapturedStderr`), temporary-directory discovery, whole-file reads, injectable death-test argv storage, environment flag readers (`BoolFromGTestEnv`, `Int32FromGTestEnv`, `StringFromGTestEnv`), and `ParseInt32`.

The universal printer section implements byte fallback printing and char/string-specialized printers. It prints opaque object bytes in grouped hex, formats `char`, `signed char`, `unsigned char`, `wchar_t`, char arrays, wide char arrays, C strings, `std::string`, and wide strings with escaping that is stable across platforms and locales.

The result-helper section implements `TestPartResult::ExtractSummary`, `operator<<` for `TestPartResult`, `TestPartResultArray::Append`, indexed lookup and size access, plus `HasNewFatalFailureHelper`, which temporarily swaps the current thread's result reporter to detect new fatal failures.

The typed-test section, guarded by `GTEST_HAS_TYPED_TEST_P`, validates that `REGISTER_TYPED_TEST_CASE_P` names exactly match tests registered in `TypedTestCasePState`, detecting duplicates, missing names, and unknown names before aborting with a source location.

## Control Flow and Behavioral Contracts

Death-test control flow is parent/child driven. The parent constructs a concrete `DeathTest`, resets the last message, captures stderr, flushes logs, creates a pipe or Windows handle pair, then spawns a child. The parent role returns `OVERSEE_TEST`; it later reads the child status byte, waits for process exit, stores status, restores captured stderr, and evaluates the result.

The child role returns `EXECUTE_TEST`. If the tested statement returns normally, throws, or otherwise fails to die as expected, `DeathTestImpl::Abort()` writes one byte to the status pipe and calls `_exit(1)`. If the statement actually dies, the pipe closes without data and the parent interprets EOF as `DIED`. Internal implementation failures write `kDeathTestInternalError` followed by an explanatory message for the parent to log fatally.

Fast POSIX death tests run after a plain `fork()` without `exec`. They warn when more than one thread is detected, close the read end of the pipe in the child, redirect logging to stderr, suppress event forwarding, set `g_in_fast_death_test_child`, and execute the statement in the child copy of the process.

Threadsafe POSIX death tests re-exec the test program. The parent creates a pipe, clears close-on-exec on the write end, builds a narrow rerun filter for the current test, appends the internal flag containing file, line, death-test index, and write descriptor, and then launches a child. The child changes back to the original working directory and calls `execve` with the original environment. Linux may use `clone()` with a one-page temporary stack unless `--gtest_death_test_use_fork` forces `fork`.

Windows death tests use the parent executable path and command line, append filter and internal flags, create an inheritable pipe and event, and launch a child inheriting standard handles. The child duplicates the parent's pipe and event handles, signals the event after acquiring the write side, and then executes the target test. The parent waits for either child exit or event signal before releasing its duplicate write handle so pipe reads can terminate correctly.

Internal rerun filtering is essential. `ParseInternalRunDeathTestFlag()` parses the encoded flag. During rerun, `DefaultDeathTestFactory::Create()` increments the death-test count for each encountered death-test macro, skips all non-target instances by returning `*test = NULL`, and constructs only the death test whose file, line, and index match the encoded target.

Path control flow is string-based with platform conditionals. `ConcatPaths()` removes the directory's trailing separator before appending the relative path. `GenerateUniqueFileName()` loops through `base.ext`, `base_1.ext`, and so on until `FileOrDirectoryExists()` returns false. `CreateDirectoriesRecursively()` requires the receiver to syntactically denote a directory, recursively creates the parent, then creates the leaf directory.

Thread-local control flow on Windows uses a global map from thread ID to per-`ThreadLocalBase` values. Accessing a thread-local value lazily creates a holder and starts a watcher thread for the owning thread. When the watched thread exits, the watcher removes all holders for that thread under lock and destroys them after releasing the lock.

Regex control flow differs by backend. POSIX regex compiles one full-match pattern and one partial-match pattern, then rejects invalid expressions through a Google Test failure. Simple regex first validates syntax, then recursively matches prefixes and repetitions; `PartialMatch` searches at each position unless the pattern starts with `^`, and `FullMatch` wraps the pattern with anchors where needed.

Stream capture flow redirects a file descriptor to a temporary file with `dup`, `dup2`, `creat` or `mkstemp`, restores the original descriptor in `GetCapturedString()`, reads the temp file with `ReadEntireFile()`, and deletes the file in the capturer destructor. Only one stdout capturer and one stderr capturer can exist at a time.

Universal printer control flow first chooses specialized overloads for known character/string types. Character printing escapes C/C++ special characters, prints printable ASCII literally, prints non-printable values as `\x...`, and may append decimal and hex code points. Arrays ending in NUL are printed like source string literals; arrays without a terminating NUL include an explicit marker.

Typed-test validation parses a comma-separated registration list, strips whitespace, checks for duplicate names, confirms each named test was registered, then scans registered tests to find omissions. Any accumulated errors are written to stderr with `FormatFileLocation()` and abort the process.

## State, Persistence, and Side Effects

Death-test state is transient but crosses process boundaries through command-line flags, pipes, handles, process IDs, file descriptors, and captured stderr files. Parent-side `DeathTestImpl` owns the read descriptor and child process ID or handle; child-side state owns the write descriptor. The static `last_death_test_message_` stores the latest user-visible death-test failure message until replaced by the next death test.

The child process intentionally exits through `_exit(1)` for controlled death-test aborts, bypassing normal C++ destructors and exit hooks. This avoids running parent-oriented Google Test cleanup in the child, but it also means descriptor cleanup and buffered data flushing must be handled explicitly before forking or left to the OS.

`g_injected_test_argvs` is process-global and owned by Google Test. `SetInjectableArgvs()` deletes any previously stored vector if a new pointer is provided, and `GetInjectableArgvs()` falls back to the original argv list. This is used to reproduce command lines in exec-style death tests.

Path helpers touch the filesystem through `getcwd`, `_getcwd`, `stat`, Windows `GetFileAttributes`, `_mkdir`, and `mkdir`. Unique filename generation is explicitly race-prone because it checks existence before later use. Recursive directory creation persists directories with mode `0777` on POSIX platforms, subject to process umask.

Stream capture persists temporary files in Windows temp directories, `/tmp`, or `/sdcard` on Android. It globally mutates process stdout/stderr descriptors, flushes all streams before redirection/restoration, and relies on correct one-capturer-at-a-time discipline.

Windows synchronization state includes OS handles, events, critical sections, watcher threads, and global maps. Static Windows mutexes are intentionally leaked rather than destroyed because cleanup is not thread-safe during shutdown.

Regex objects own duplicated pattern strings. POSIX `RE` also owns compiled `regex_t` objects that are freed only if compilation succeeded. Simple `RE` owns both original and full-match pattern buffers allocated with `posix::StrDup`/`malloc`.

Environment flag readers do not persist state themselves but read process environment variables such as `GTEST_*` and, specially for output, `XML_OUTPUT_FILE`. Invalid integer environment values generate warnings on stdout and leave the default value in force.

Printer state is limited to output streams and temporary formatting buffers. The byte printer intentionally truncates large object dumps by printing the first and last 64 bytes when object size reaches the threshold, which affects diagnostic output shape but not test semantics.

`HasNewFatalFailureHelper` mutates the current thread's `TestPartResultReporterInterface` in `UnitTestImpl` for its lifetime, forwards all reported results to the original reporter, and restores the original reporter in its destructor.

## Dependencies and Integration Points

This chunk integrates deeply with Google Test internals declared earlier in the fused file and headers: `UnitTestImpl`, `UnitTest`, `TestInfo`, `TestResult`, `DeathTest`, `DefaultDeathTestFactory`, `InternalRunDeathTestFlag`, `RE`, `Message`, `FilePath`, `String`, `Mutex`, `ThreadLocalBase`, `ThreadLocalValueHolderBase`, `TestPartResult`, and `TypedTestCasePState`.

Death tests depend on platform process APIs. POSIX paths use `pipe`, `close`, `read`, `write`, `fork`, `waitpid`, `fcntl`, `chdir`, `execve`, `getcwd`, `stat`, `mkdir`, `dup`, `dup2`, `mkstemp`, `remove`, and optionally `clone`, `mmap`, `munmap`, `sigaction`, QNX `spawn`, and macOS `_NSGetEnviron`. Windows paths use `CreatePipe`, `CreateEvent`, `CreateProcessA`, `GetModuleFileNameA`, `GetCommandLineA`, `WaitForMultipleObjects`, `WaitForSingleObject`, `GetExitCodeProcess`, `DuplicateHandle`, `OpenProcess`, `_open_osfhandle`, `_getcwd`, `_mkdir`, `GetFileAttributes`, `CreateThread`, critical sections, events, and handles.

The regex layer depends either on POSIX `<regex.h>` semantics or the simple internal matcher selected by `GTEST_USES_POSIX_RE` / `GTEST_USES_SIMPLE_RE`. Death-test success depends on `RE::PartialMatch()` against captured stderr.

Diagnostics integrate with Google Test's log stream, result reporters, failure macros, source formatting, and printer customization points. `GTestLog` calls `posix::Abort()` on fatal severity. `TestPartResult::ExtractSummary()` depends on `internal::kStackTraceMarker` to strip stack trace text.

Hadoop integration is indirect: Hadoop native tests compile and link this vendored Google Test file from `hadoop-common/src/main/native/gtest`. Any platform behavior or diagnostic formatting here affects native test execution in Hadoop's build, especially tests that use death tests, stdout/stderr capture, XML output, or specialized value printing.

## Risks and Compatibility Notes

Death tests are the highest-risk behavior in this chunk. They combine process creation, file descriptor inheritance, signal handling, command-line reconstruction, stderr capture, and platform-specific cleanup. Small changes can cause hangs, leaked descriptors, double closes, child processes running the wrong test, or false death-test pass/fail results.

The status-byte protocol is fragile by design: EOF means the child died as expected, while any byte means a controlled failure or internal error. Accidentally closing or inheriting the wrong pipe end can make a living child look dead, keep the parent blocked forever, or hide internal failures.

Fast death tests with `fork()` are unsafe in multi-threaded processes. The implementation warns when it can detect multiple threads, flushes logs near the fork, redirects child logging, and suppresses event forwarding, but tests using locks, background threads, or non-async-signal-safe libraries can still deadlock or behave differently after fork.

Exec-style death tests require an executable path suitable for `execve`; the code explicitly does not search `PATH`. Test launchers that invoke binaries through unusual wrappers or without a path separator can break threadsafe death tests.

The Linux `clone()` path manually allocates a small stack and computes stack direction/alignment. Stack-size assumptions, sanitizer interactions, and platform ABI changes are risk points. The code includes sanitizer suppression and an opt-out flag via `death_test_use_fork`.

Windows handle passing depends on the child duplicating parent handles before the parent releases its copy. Event ordering and handle inheritability are critical; premature cleanup makes the child unable to report status, while delayed cleanup can keep reads from completing.

`FilePath::GenerateUniqueFileName()` has a known time-of-check/time-of-use race. It is adequate for test output naming in typical local test runs but can collide under concurrent processes writing to the same directory.

Stream capture is global process state. Capturing stdout/stderr while other threads write to those descriptors can interleave data or redirect unrelated output. Missing `GetCapturedStdout()`/`GetCapturedStderr()` calls leave global capturer pointers active and descriptors redirected.

`ReadEntireFile()` sizes files with `fseek`/`ftell` and allocates that exact byte count. It is intended for temporary capture files, not untrusted large files. Zero-sized files allocate `new char[0]`, which is legal but requires careful use.

Simple regex has limited syntax compared with POSIX extended regular expressions. Unsupported constructs such as grouping, alternation, and character classes are rejected. Matching can become exponential for rare pattern/string combinations, though recursion depth is bounded by regex length.

Universal printing intentionally reads object memory for byte fallback and character arrays for the supplied length. The sanitizer suppression attributes acknowledge that diagnostics may inspect otherwise uninitialized bytes. Incorrect lengths or invalid wide-string pointers can still be dangerous in callers.

Typed-test registration validation aborts the process on mismatch. This is appropriate for compile-time-style registration errors, but it means malformed typed-test metadata prevents all later tests from running.

Because this is a vendored fused third-party file, local Hadoop edits should be avoided unless necessary for build portability. Behavioral fixes are safest when mirrored from the corresponding upstream Google Test version or isolated behind existing `GTEST_OS_*` and `GTEST_HAS_*` conditionals.

## Test Signals

Death-test tests should cover successful death, statement returns, statement throws, statement lives, stderr regex mismatch, bad expected exit status, invalid death-test style, and internal flag parsing failures. Both `fast` and `threadsafe` styles matter on POSIX; Windows should cover handle duplication and event signaling where supported.

Process-control tests should verify that parent waits do not hang, child stderr is captured and formatted with `[  DEATH   ]`, log buffers are not duplicated across fork, file descriptors are closed on the correct side, `last_death_test_message_` is reset and then populated, and internal reruns execute only the encoded death-test index.

Path tests should cover current directory fallback, extension removal case-insensitivity, basename and dirname extraction with and without trailing separators, Windows alternate separators, root directories, absolute path detection, redundant separator normalization, directory creation success/failure, and unique XML filename generation.

Thread and synchronization tests on Windows should cover `AutoHandle` close/reset semantics, `Notification` wait/notify behavior, mutex lock/unlock/assert-held behavior, lazy static mutex initialization, thread creation/join, thread-local value creation, cleanup on thread exit, and cleanup when a `ThreadLocal` object is destroyed before its owning threads exit.

Regex tests should cover full and partial matches, empty regexes, anchors, dots, escaped punctuation, digit/word/space classes, repetition operators, invalid escapes, unsupported grouping/classes/alternation in simple regex mode, null regex handling, and invalid POSIX regex reporting.

Logging and capture tests should cover compiler-style and XML-style file locations for null and negative line inputs, fatal `GTestLog` abort behavior, stdout/stderr capture round trips, nested capture rejection, temporary-file cleanup, empty captured streams, and Android/Windows temporary-directory selection.

Environment flag tests should cover boolean values unset, `"0"`, and nonzero strings; valid and invalid `Int32` parsing including overflow; string flag defaults; `GTEST_OUTPUT`; and the `XML_OUTPUT_FILE` fallback that prefixes `xml:`.

Printer tests should cover signed/unsigned chars, `wchar_t`, printable ASCII, C escape characters, non-printable hex escapes, char arrays with and without terminating NUL, embedded NULs, C strings with pointer prefix, null C strings, `std::string`, wide strings, large object byte truncation, and disambiguation after `\x` escapes followed by hex digits.

Failure-result tests should cover stack trace summary extraction, result stream formatting for success/fatal/nonfatal failures, array append and valid index lookup, invalid index abort, and `HasNewFatalFailureHelper` detecting only newly reported fatal failures while forwarding original reports.

Typed-test registration tests should cover an exact registration list, duplicate listed names, missing registered names, unknown listed names, whitespace and comma handling, source-location formatting in stderr, and abort behavior when validation errors accumulate.
