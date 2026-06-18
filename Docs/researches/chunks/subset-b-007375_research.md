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
