# sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/gtest-all.cc lines 1-7108

## Scope and Purpose

This chunk is the first chunk of RocksDB's vendored, fused Google Test 1.8.1 implementation. It starts with the amalgamated `gtest-all.cc` wrapper, includes `gtest/gtest.h`, embeds the SPI header used for testing Google Test itself, declares internal runtime facilities, and implements most of the core Google Test engine through the opening of command-line flag parsing.

Within this line range, the file provides the runtime used by RocksDB C++ tests when Google Test is built as one translation unit: it registers statically declared tests, stores test cases and test metadata, parses and applies most `--gtest_*` options and `GTEST_*` environment defaults, filters/shards/reorders test execution, runs fixtures and test bodies with exception handling, records assertion results, dispatches event listeners, and emits console/XML/JSON/socket-stream output.

The chunk ends at line 7108 inside the beginning of `ParseBoolFlag`; the remainder of boolean/string flag parsing, `InitGoogleTest`, temporary directory support, scoped traces, death tests, filesystem helpers, threading helpers, and regex helpers are in later lines/chunk(s).

## Important APIs, Types, and Functions

- `testing::ScopedFakeTestPartResultReporter` temporarily replaces either the current thread's result reporter or the global reporter. It is used by SPI macros that assert on Google Test failures.
- `testing::internal::SingleFailureChecker` validates, in its destructor, that a captured `TestPartResultArray` contains exactly one failure of the expected type and message substring.
- `EXPECT_FATAL_FAILURE`, `EXPECT_FATAL_FAILURE_ON_ALL_THREADS`, `EXPECT_NONFATAL_FAILURE`, and `EXPECT_NONFATAL_FAILURE_ON_ALL_THREADS` use the fake reporter plus `SingleFailureChecker` to test code that should generate Google Test failures.
- Internal flag constants cover `also_run_disabled_tests`, `break_on_failure`, `catch_exceptions`, `color`, `filter`, `list_tests`, `output`, `print_time`, `print_utf8`, `random_seed`, `repeat`, `shuffle`, `stack_trace_depth`, `stream_result_to`, `throw_on_failure`, and optional `flagfile`. The matching `GTEST_DEFINE_*` blocks initialize flag globals from environment variables or defaults.
- `testing::internal::GTestFlagSaver` snapshots all Google Test flags in a fixture constructor and restores them in the fixture destructor, preventing test-local flag changes from leaking between tests.
- `testing::internal::UnitTestOptions` resolves the requested output format/path and implements Google Test's glob-style filter grammar: colon-separated positive patterns, optional dash-separated negative patterns, `*`, and `?`.
- `testing::internal::UnitTestImpl` is the central private state object behind the `testing::UnitTest` singleton. It owns test cases, environments, listeners, current-test pointers, ad hoc results, reporters, thread-local trace stacks, parameterized-test registry state, random seed/generator, elapsed-time state, and optional death-test state.
- `DefaultGlobalTestPartResultReporter` records assertion results into the current `TestResult` and forwards part-result events to listeners. `DefaultPerThreadTestPartResultReporter` delegates thread-local reporting to the global reporter.
- `AssertHelper::operator=` is the assertion macro sink: it appends user messages and an OS stack trace, then calls `UnitTest::AddTestPartResult`.
- `testing::Message`, `testing::AssertionResult`, `AssertionSuccess`, `AssertionFailure`, comparison helpers, string comparison helpers, substring helpers, floating-point helpers, and Windows HRESULT helpers implement assertion diagnostics.
- `testing::internal::edit_distance::CalculateOptimalEdits` and `CreateUnifiedDiff` generate unified diffs for multiline equality failures.
- String and encoding utilities include UTF-8 conversion for wide strings, null-safe C/wide string comparisons, case-insensitive comparisons, integer/byte formatting, NUL escaping for stringstreams, and user-message concatenation.
- `testing::TestResult` stores assertion part results, user properties, death-test count, and elapsed time. It validates `RecordProperty` keys against XML/JSON reserved attributes for `testsuites`, `testsuite`, and `testcase`.
- `testing::Test`, `TestInfo`, and `TestCase` implement fixture lifecycle, registered test metadata/factories, per-test execution, per-case setup/teardown, ordering, shuffling, and aggregate counts.
- `PrettyUnitTestResultPrinter` implements the default stdout printer. `TestEventRepeater` owns listener fan-out and forwards start/end events in forward or reverse order depending on lifecycle phase.
- `XmlUnitTestResultPrinter` writes JUnit-like XML and test-list XML. `JsonUnitTestResultPrinter` writes the equivalent JSON output. Both share reserved-key validation and use `OpenFileForWriting` for parent directory creation.
- `StreamingListener` is compiled when `GTEST_CAN_STREAM_RESULTS_` is enabled and emits URL-encoded lifecycle events to a TCP socket.
- `OsStackTraceGetterInterface` and `OsStackTraceGetter` provide stack traces, using Abseil stacktrace/symbolization when `GTEST_HAS_ABSL` is enabled and returning an empty trace otherwise.
- `ScopedPrematureExitFile` implements the `TEST_PREMATURE_EXIT_FILE` protocol by creating a marker on test-program entry and deleting it on normal exit.
- `UnitTest::GetInstance`, `UnitTest::AddEnvironment`, `UnitTest::AddTestPartResult`, `UnitTest::RecordProperty`, and `UnitTest::Run` are the main public facade methods implemented in this chunk.
- `UnitTestImpl::PostFlagParsingInit`, `ConfigureXmlOutput`, `ConfigureStreamingOutput`, `RegisterParameterizedTests`, `GetTestCase`, `RunAllTests`, `FilterTests`, `ListTestsMatchingFilter`, `ShuffleTests`, and `UnshuffleTests` form the main runtime control plane.
- Sharding helpers `WriteToShardStatusFileIfNeeded`, `ShouldShard`, `Int32FromEnvOrDie`, and `ShouldRunTestOnShard` implement Google Test's environment-variable sharding protocol.
- Flag parsing begins with `SkipPrefix`, `ParseFlagValue`, and the first lines of `ParseBoolFlag`.

## Control Flow

Static test registration routes through `MakeAndRegisterTestInfo`, which allocates a `TestInfo`, gives it ownership of its factory, and adds it through `UnitTestImpl::AddTestInfo`. The first registration captures the original working directory so output file paths and death-test behavior remain anchored to process startup rather than to later directory changes. `UnitTestImpl::GetTestCase` reuses an existing case by name or allocates a new `TestCase`; cases matching the death-test-name filter are inserted before non-death cases to preserve death-test ordering.

Initialization state is split across flag parsing and post-flag parsing. This chunk declares the flag parsing pieces and implements `PostFlagParsingInit`: it is idempotent, appends a custom listener if configured at compile time, initializes death-test subprocess control when enabled, suppresses event forwarding in death-test children, expands parameterized tests, configures XML/JSON output, configures socket streaming, and optionally installs Abseil's failure signal handler.

`UnitTest::Run` is the public execution entry point. It detects death-test child context, manages the premature-exit marker outside child processes, snapshots `catch_exceptions`, applies Windows crash-dialog/error-mode suppression when appropriate, and delegates into `UnitTestImpl::RunAllTests` through the common exception-handling wrapper.

`UnitTestImpl::RunAllTests` performs the full run orchestration. It returns early for help, ensures post-flag initialization has happened even if the user forgot `InitGoogleTest`, writes the shard-status marker if requested, detects death-test child mode, computes whether sharding is active, filters tests, handles `--gtest_list_tests`, initializes the shuffle seed, and emits `OnTestProgramStart`. For each repeat iteration it clears non-ad-hoc results, optionally shuffles test cases and tests, emits iteration start, runs global environments, runs selected test cases, tears environments down in reverse registration order, records elapsed time, emits iteration end, records whether any iteration failed, restores original order, and advances the random seed for the next iteration.

`TestCase::Run` sets the current case, emits case start/end events, calls case-level setup and teardown through exception wrappers, and iterates over its selected `TestInfo` objects. `TestInfo::Run` sets the current test, emits test start/end, constructs the fixture through its factory, runs the fixture only if construction did not add a fatal failure, deletes the fixture through the same exception-handling wrapper, records elapsed time, and clears the current-test pointer.

`Test::Run` validates that all tests in a case use the same fixture class, calls `SetUp`, runs `TestBody` only if setup did not fatal-fail, and always calls `TearDown`. `HandleExceptionsInMethodIfSupported` wraps fixture/user/listener/environment calls and reports C++ exceptions and Windows SEH exceptions as fatal Google Test failures when exception catching is enabled for the run.

Assertion reporting flows through `AssertHelper::operator=`, `UnitTest::AddTestPartResult`, and the current thread's result reporter. `AddTestPartResult` appends `SCOPED_TRACE` entries and optional OS stack trace text, builds a `TestPartResult`, dispatches it to the reporter, and then honors `break_on_failure` or `throw_on_failure` for non-success results.

Output is listener-driven. The default pretty printer receives events through `TestEventRepeater` and writes colorized stdout status lines and summaries. XML and JSON generators are installed as listeners based on `--gtest_output`, then write final output at iteration end. The streaming listener, when compiled and configured, connects to a host/port and sends URL-encoded lifecycle records.

Filtering and sharding happen before execution. `FilterTests` marks each `TestInfo` as disabled, matching the user filter, assigned to another shard, and selected/not selected. Disabled tests are excluded unless `also_run_disabled_tests` is set. Sharding uses a monotonically increasing runnable-test id and assigns `test_id % total_shards` to the shard index.

## State and Persistence Behavior

Most state is process-local and owned by the `UnitTest` singleton. `UnitTestImpl` owns `TestCase*` and `Environment*` objects and deletes them in its destructor. `TestCase` owns its `TestInfo` objects; `TestInfo` owns its `TestFactoryBase`; fixture instances are created and destroyed for each test run.

Ordering state is preserved through index vectors rather than by physically reordering the owning vectors. `UnitTestImpl::test_case_indices_` and each `TestCase::test_indices_` can be shuffled and then reset by `UnshuffleTests`, which supports reproducible reruns after a shuffled/repeated iteration fails. Death-test cases are tracked with `last_death_test_case_` so shuffling can keep death tests before non-death tests.

Failure/result state is kept in `TestResult` objects. The active destination is chosen by `UnitTestImpl::current_test_result`: current test result when inside a test, current case ad-hoc result during case-level setup/teardown, and global ad-hoc result outside a case. `RecordProperty` uses the same context to determine which XML/JSON element's reserved keys must be enforced.

Reporter state has both global and per-thread forms. The global reporter pointer is protected by `global_test_part_result_reporter_mutex_`; the per-thread reporter and `SCOPED_TRACE` stack are stored in `ThreadLocal` wrappers. SPI helpers rely on this split to intercept only current-thread failures or all-thread failures.

Flag state is global static state initialized from `GTEST_*` environment variables and later overridden by command-line parsing. `GTestFlagSaver` snapshots and restores flags around each fixture instance. `UnitTest::Run` also snapshots `catch_exceptions` once for the run so changing that flag after the run starts does not alter exception behavior mid-call.

Persistent/file/network side effects in this chunk include:

- XML/JSON output files written at the path resolved by `UnitTestOptions::GetAbsolutePathToOutputFile`, with parent directories created on demand.
- `GTEST_SHARD_STATUS_FILE`, if set, overwritten as a marker that the binary supports Google Test sharding.
- `TEST_PREMATURE_EXIT_FILE`, if set outside a death-test child, created on entry to `UnitTest::Run` and removed on normal exit.
- Optional socket streaming to the `--gtest_stream_result_to=host:port` endpoint.
- Console stdout output, optional Windows debugger output for failures, and possible process-breaking side effects from `break_on_failure` or `throw_on_failure`.

## Dependencies and Integration Points

The file includes `gtest/gtest.h` for public API declarations, macros, feature detection, `Test`, `UnitTest`, `TestPartResult`, `TestEventListener`, `FilePath`, `Random`, `ThreadLocal`, and platform abstraction declarations. Because this is the fused source file, it also embeds content corresponding to upstream internal headers and source files.

Platform dependencies are extensive and feature-gated. Time comes from `gettimeofday`, `_ftime64`, or Windows file-time conversion. Filesystem output uses Google Test's `FilePath` plus `posix::FOpen`. Console color uses ANSI escape codes on many POSIX terminals and `SetConsoleTextAttribute` on Windows consoles. Windows-only paths include SEH handling, HRESULT formatting, debugger breaks, and crash-dialog suppression. Socket streaming uses `getaddrinfo`, `socket`, `connect`, `write`, and `close` when enabled. Stack traces use Abseil only when compiled with `GTEST_HAS_ABSL`.

The primary RocksDB integration is build-time and runtime test infrastructure integration: RocksDB can compile this single `gtest-all.cc` translation unit, register tests through normal `TEST`/`TEST_F` macros in other files, call `InitGoogleTest`, and use `RUN_ALL_TESTS`. CI systems integrate through exit code, stdout, `--gtest_output=xml|json`, sharding environment variables, `GTEST_SHARD_STATUS_FILE`, and `TEST_PREMATURE_EXIT_FILE`.

Extension points include `TestEventListeners`, custom compile-time `GTEST_CUSTOM_TEST_EVENT_LISTENER_`, result reporter replacement through SPI helpers, parameterized-test registry expansion, and custom OS stack trace getter via `GTEST_OS_STACK_TRACE_GETTER_`.

## Risks and Edge Cases

- This is an older vendored Google Test implementation. Local edits can silently diverge from upstream 1.8.1 semantics and affect every RocksDB test binary that links this fused source.
- The file is platform-dense and preprocessor-heavy; a change that builds on Linux may still break Windows, MinGW, mobile, Abseil-enabled, exception-disabled, or death-test-enabled builds.
- `ScopedPrematureExitFile` ignores the documented possibility that `FOpen` fails but still calls `fwrite`/`fclose` on the returned pointer in this implementation, which is a null-pointer crash risk if the marker file cannot be created.
- `UnitTestImpl::GetTestCase(int) const` calculates a shuffled `index` but returns `test_cases_[i]` rather than `test_cases_[index]`, while `GetMutableTestCase` uses `index`. If not intentionally inherited behavior, listener/reflection ordering under shuffle is suspect.
- Filter matching is recursive and simple glob matching, not regex. It is suitable for short test names but can behave unexpectedly for users expecting regex syntax.
- `ShouldShard` treats incomplete or invalid shard environment configuration as a fatal process error. CI jobs with one missing variable can fail before any test runs.
- Test properties with reserved keys are converted into Google Test failures; RocksDB tests using keys like `name`, `time`, `status`, or `classname` in the wrong context can unexpectedly fail output validation.
- `break_on_failure` intentionally traps/crashes, and `throw_on_failure` throws or exits. Embedding this runner inside another framework must account for those nonlocal control flows.
- XML invalid characters are dropped rather than preserved in escaped form. Failure messages or properties with control bytes may lose information in XML output.
- JSON and XML output are generated by hand-written stream code. Escaping is explicit and mostly local; changes to allowed keys or nested output shape need careful validation.
- Socket streaming warnings do not fail tests. External consumers cannot assume stream delivery unless they monitor the receiver side separately.
- The chunk boundary cuts through flag parsing: `ParseBoolFlag` is only partially visible. Full command-line behavior, flagfile loading, `InitGoogleTest`, and help output must be reconciled with chunk 2.

## Test Signals

High-value validation signals for this chunk include:

- Compile RocksDB test binaries that link this fused Google Test source on the target platform.
- Run a basic passing and failing test binary to exercise registration, `UnitTest::Run`, fixture construction/destruction, `TestCase::Run`, `TestInfo::Run`, and pretty printer events.
- Exercise fatal and nonfatal assertions, assertion streaming, `SCOPED_TRACE`, wide strings, null C strings, multiline equality failures, floating-point comparisons, substring predicates, and SPI macros that expect failures.
- Run fixture lifecycle tests covering `SetUp`, `TestBody`, `TearDown`, case-level setup/teardown, fatal setup failure, constructor/destructor exception handling, and global environments.
- Validate filtering with `--gtest_filter`, negative filters, disabled tests, `--gtest_also_run_disabled_tests`, and `--gtest_list_tests`.
- Validate repeat/shuffle behavior with `--gtest_repeat`, `--gtest_shuffle`, and fixed/nonfixed `--gtest_random_seed`, checking that death-test case ordering is preserved and unshuffle restores original order after each iteration.
- Generate XML and JSON with normal tests, disabled tests, typed/value-parameterized tests, failures, custom properties, reserved property keys, invalid XML characters, and output directories that do not yet exist.
- Test sharding with valid and invalid `GTEST_TOTAL_SHARDS`, `GTEST_SHARD_INDEX`, and `GTEST_SHARD_STATUS_FILE` combinations.
- Verify `TEST_PREMATURE_EXIT_FILE` is removed on normal completion and remains after abnormal process termination.
- If socket streaming is enabled, run with a local receiver and confirm lifecycle events are URL-encoded and delivered without changing pass/fail status.
- On supported builds, test `break_on_failure`, `throw_on_failure`, exception-catching enabled/disabled, Windows SEH behavior, and Abseil stack-trace integration.

## Chunk Boundary Notes

This chunk ends at line 7108 immediately after `ParseBoolFlag` obtains `value_str` from `ParseFlagValue` and before the null check and bool conversion are included. The next chunk is required to complete flag parsing and to cover the rest of initialization and later subsystems.
