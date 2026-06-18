# sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/gtest.h lines 18783-22095

## Scope

This chunk is the tail of the fused Google Test 1.8.1 public header embedded under RocksDB's third-party sources. It starts at the end of value-parameterized test support, including `Combine()` overloads and the `TEST_P` / `INSTANTIATE_TEST_CASE_P` registration macros. It then contains the fused `gtest_prod.h`, `gtest-test-part.h`, `gtest-typed-test.h`, generated predicate assertion macro header, and the final public `gtest.h` API surface through `RUN_ALL_TESTS()`.

The code is mostly declarations, inline helpers, and macros. Its behavior is completed by the compiled Google Test implementation elsewhere in the fused distribution, but this header defines the user-visible testing DSL, the test metadata model, event listener interfaces, assertion result plumbing, typed/value-parameterized registration hooks, and the singleton `UnitTest` interface used by RocksDB tests.

## Purpose

This range exposes the core Google Test contracts used by RocksDB's C++ test binaries:

- value-parameterized tests are declared with `TEST_P`, instantiated with `INSTANTIATE_TEST_CASE_P`, and can combine up to ten parameter generators when `GTEST_HAS_COMBINE` is enabled;
- production classes can grant friendship to a generated Google Test fixture class through `FRIEND_TEST`;
- individual assertion outcomes are represented as `TestPartResult` objects and delivered through `TestPartResultReporterInterface`;
- typed tests and type-parameterized tests register generated test classes for a list of types via `TYPED_TEST_CASE`, `TYPED_TEST`, `TYPED_TEST_CASE_P`, `TYPED_TEST_P`, `REGISTER_TYPED_TEST_CASE_P`, and `INSTANTIATE_TYPED_TEST_CASE_P`;
- global Google Test flags are declared for filtering, repetition, shuffling, XML output, exception handling, colored output, stack traces, disabled tests, and result streaming;
- `AssertionResult` provides rich Boolean/predicate assertion results with lazily allocated streamed messages;
- generated predicate assertion macros reduce `EXPECT_PRED*` and `ASSERT_PRED*` calls to `GTEST_ASSERT_`;
- `Test`, `TestResult`, `TestInfo`, `TestCase`, `Environment`, `TestEventListener`, `TestEventListeners`, and `UnitTest` describe the runtime test graph and lifecycle;
- public assertion macros map user code (`EXPECT_EQ`, `ASSERT_TRUE`, `SCOPED_TRACE`, etc.) onto internal helper functions and `AssertHelper`;
- `RUN_ALL_TESTS()` is the final global entry point that dispatches to `UnitTest::GetInstance()->Run()`.

## Important APIs, Types, And Macros

- `Combine()` overloads for arities 4 through 10 return `internal::CartesianProductHolderN` objects. They are part of value-parameterized test generator composition and depend on `GTEST_HAS_COMBINE`.
- `TEST_P(test_case_name, test_name)` creates a generated subclass of the parameterized fixture, registers a `TestMetaFactory` in `UnitTest::parameterized_test_registry()`, and leaves the user's test body as the generated `TestBody()` definition.
- `INSTANTIATE_TEST_CASE_P(prefix, test_case_name, generator, ...)` stores an evaluated `ParamGenerator<ParamType>` function and a test-name generator function, then registers the instantiation under the parameterized test case registry. The optional name generator is selected through `internal::GetParamNameGen`.
- `FRIEND_TEST(test_case_name, test_name)` expands to friendship for the generated `test_case_name_test_name_Test` class. This is a production-code hook used when tests need private or protected access.
- `TestPartResult` stores assertion outcome type, source file, line, summary, and full message. It distinguishes success, non-fatal failure, and fatal failure. It normalizes unknown file names to an empty string internally and returns `NULL` from `file_name()` when unknown.
- `TestPartResultArray` owns a `std::vector<TestPartResult>` and exposes append/index/size operations.
- `TestPartResultReporterInterface` is the reporting sink for assertion results. `internal::HasNewFatalFailureHelper` temporarily installs itself as the active reporter for `{ASSERT|EXPECT}_NO_FATAL_FAILURE`, delegates to the previous reporter, records whether a new fatal failure occurred, and restores the original reporter in its destructor.
- Typed-test macros synthesize generated fixture subclasses and registration state:
  - `GTEST_TYPE_PARAMS_` and `GTEST_NAME_GENERATOR_` create hidden typedef names.
  - `TYPED_TEST_CASE` builds an internal type list and selected name generator.
  - `TYPED_TEST` registers one test body for all types in a known type list.
  - `TYPED_TEST_CASE_P`, `TYPED_TEST_P`, `REGISTER_TYPED_TEST_CASE_P`, and `INSTANTIATE_TYPED_TEST_CASE_P` support abstract type-parameterized test patterns that are later instantiated by type list and prefix.
- Google Test flags declared here include `also_run_disabled_tests`, `break_on_failure`, `catch_exceptions`, `color`, `filter`, `install_failure_signal_handler`, `list_tests`, `output`, `print_time`, `print_utf8`, `random_seed`, `repeat`, `show_internal_stack_frames`, `shuffle`, `stack_trace_depth`, `throw_on_failure`, `stream_result_to`, and optionally `flagfile`.
- `AssertionResult` is copyable and contextually convertible to `bool`. It supports `operator!`, `message()`, deprecated `failure_message()`, and streaming through `operator<<`. Message storage uses `internal::scoped_ptr<std::string>` to keep common assertion stack usage small.
- `AssertionSuccess()`, `AssertionFailure()`, and deprecated `AssertionFailure(const Message&)` are factory functions for predicate results.
- Generated predicate helpers `AssertPred1Helper` through `AssertPred5Helper` build failure messages that include predicate text, expression text, and evaluated values. Public macros cover both raw Boolean predicates and predicate-format functions for arities 1 through 5.
- `Test` is the base fixture class. It exposes static `SetUpTestCase()`, `TearDownTestCase()`, failure query helpers, and `RecordProperty()`, while the private runtime path calls `SetUp()`, `TestBody()`, `TearDown()`, and `DeleteSelf_()`.
- `TestProperty` stores a key/value pair for XML output and supports value replacement for duplicate keys.
- `TestResult` owns assertion results, test properties, death-test count, and elapsed time. It exposes aggregate failure queries and indexed access, while friends mutate it during test execution.
- `TestInfo` stores immutable test identity and factory metadata plus mutable `TestResult`. It tracks whether a test should run, is disabled, matches filters, or belongs to another shard.
- `TestCase` owns `TestInfo` objects, setup/teardown function pointers, a shuffle indirection vector, per-test-case ad hoc properties, and elapsed time. It computes counts for successful, failed, disabled, reportable, runnable, and total tests.
- `Environment` is the base class for global setup/teardown hooks registered through `AddGlobalTestEnvironment()`.
- `AssertionException` is available when exceptions are enabled and wraps a `TestPartResult` for listeners that throw on assertion failure.
- `TestEventListener` defines the full event sequence from program start through iterations, environments, test cases, individual tests, assertion parts, and program end. `EmptyTestEventListener` supplies no-op overrides.
- `TestEventListeners` owns listener registration, default result printer, default XML generator, and an internal repeater used to broadcast events.
- `UnitTest` is the process-wide singleton. It runs tests, exposes current test/test case, aggregate counts, timing, random seed, ad hoc result, listeners, and the internal parameterized-test registry. Its mutable implementation state is protected by `internal::Mutex`.
- Comparison helpers include `CmpHelperEQ`, `EqHelper`, `CmpHelperNE/LE/LT/GE/GT`, C-string and wide-string comparison helpers, substring predicates, floating-point equality helpers, `DoubleNearPredFormat`, `FloatLE`, and `DoubleLE`.
- `AssertHelper` is the small assertion failure adapter used by failure macros to support streaming messages into assertions.
- `WithParamInterface<T>` exposes `GetParam()` for value-parameterized fixtures through a static `parameter_` pointer set by `internal::ParameterizedTestFactory`. `TestWithParam<T>` combines `Test` and `WithParamInterface<T>`.
- Public user macros include `ADD_FAILURE`, `ADD_FAILURE_AT`, `FAIL`, `SUCCEED`, exception assertions, Boolean assertions, equality/ordering assertions, string assertions, floating-point assertions, HRESULT assertions on Windows, no-fatal-failure assertions, `SCOPED_TRACE`, `GTEST_TEST`, `TEST`, and `TEST_F`.
- `ScopedTrace` pushes file/line/message trace context on construction and pops it on destruction; `SCOPED_TRACE` creates a unique local trace variable using the current line.
- `StaticAssertTypeEq<T1, T2>()` triggers a compile-time type equality check by instantiating `internal::StaticAssertTypeEqHelper`.
- `TempDir()` declares the platform-specific temporary-directory helper.
- `RUN_ALL_TESTS()` is declared in the global namespace and inlined to call the singleton `UnitTest` runner.

## Control Flow

Test registration in this chunk is mostly static initialization driven by macros. `TEST_P` expands into a generated test class and a static dummy integer initialized by `AddToRegistry()`. That initializer calls `UnitTest::GetInstance()->parameterized_test_registry()`, obtains the `ParameterizedTestCaseInfo` holder for the fixture, and adds a test pattern with a `TestMetaFactory`. `INSTANTIATE_TEST_CASE_P` similarly creates static helper functions for the generator and parameter-name generator, then registers an instantiation with source file and line metadata. The actual concrete tests are materialized later by the Google Test runtime before execution.

Typed-test registration follows a similar pattern but routes through type-list helpers. `TYPED_TEST_CASE` fixes the type list and name generator for a fixture template. Each `TYPED_TEST` defines a templated generated test class and invokes `internal::TypeParameterizedTest<...>::Register()` with the case name, test name, code location, and generated type names. Type-parameterized tests split the process: `TYPED_TEST_CASE_P` creates a static `TypedTestCasePState`, each `TYPED_TEST_P` records a test name in that state, `REGISTER_TYPED_TEST_CASE_P` verifies that the listed names match the definitions, and `INSTANTIATE_TYPED_TEST_CASE_P` registers all templates for the selected type list and prefix.

Assertion macros reduce to a common reporting path. Predicate macros call predicate helper functions or predicate-format functions, producing an `AssertionResult`. `GTEST_ASSERT_` tests that result, does nothing on success, and invokes either fatal or non-fatal failure handlers with the assertion message on failure. Equality and ordering assertions reuse predicate-format macros so expression text and evaluated values can be formatted consistently. Fatal assertions route through failure macros that abort the current function according to Google Test's internal fatal-failure mechanism; non-fatal assertions record a result and continue.

During execution, `RUN_ALL_TESTS()` calls `UnitTest::Run()`. `UnitTest` delegates to its internal implementation to select tests according to flags, sharding, disabled-state rules, and filters. It iterates test cases, runs per-case setup, creates each test through the `TestInfo` factory, calls `Test::Run()` to execute fixture setup/body/teardown, records results, fires listener events, runs per-case teardown, and aggregates counts and elapsed time. The public declarations here expose the metadata and listener interfaces; the detailed implementation lives outside this header.

`ScopedTrace` and `HasNewFatalFailureHelper` are RAII control-flow adapters. `ScopedTrace` pushes trace context into `UnitTest` on construction and pops on destruction so failures inside the lexical scope include additional context. `HasNewFatalFailureHelper` temporarily replaces the current test-part reporter, watches delegated assertion results for fatal failures, and restores the previous reporter in its destructor, allowing `EXPECT_NO_FATAL_FAILURE` and `ASSERT_NO_FATAL_FAILURE` to test a statement's side effects on the failure stream.

## State And Persistence Behavior

The state in this header is process-local Google Test runtime state, not RocksDB on-disk persistence. Persistent storage in the application sense is not performed here. Important stateful behavior includes:

- `UnitTest` is a singleton created on first use and intentionally never deleted; it owns the global test registry, implementation object, listener set, environments, current-test pointers, result state, and flag-derived run configuration.
- Static initialization produced by `TEST`, `TEST_F`, `TEST_P`, typed-test macros, and instantiate macros registers test metadata before `main()` calls `RUN_ALL_TESTS()`. Linkage and initialization order are therefore part of the test discovery model.
- `TestCase` owns `TestInfo` pointers, preserves original test order, and maintains `test_indices_` so shuffling can be undone.
- `TestInfo` owns its factory pointer and contains a `TestResult` that must be cleared before repeated runs.
- `TestResult` accumulates `TestPartResult` entries, properties, death-test count, and elapsed time; property mutation is protected by `test_properites_mutex_` because duplicate keys update existing values.
- `WithParamInterface<T>::parameter_` is a static pointer per parameter type. The parameterized-test factory sets it for the lifetime of a running value-parameterized test; `GetParam()` checks that it is non-null and returns a const reference.
- `AssertionResult` lazily allocates a message string only when a caller streams diagnostic text into it.
- Listener ownership transfers to Google Test when appended to `TestEventListeners`; `Release()` transfers ownership back to the caller.
- Global environments registered with `AddGlobalTestEnvironment()` are owned by the `UnitTest` singleton, set up in registration order, and torn down in reverse order.
- Test properties recorded by `Test::RecordProperty()` are routed to the current test result, current test case ad hoc result, or global ad hoc result depending on where the call occurs.

The only file-related API declared here is `TempDir()` and XML/output flag plumbing. The actual XML report generation and temporary-directory resolution are implemented elsewhere.

## Dependencies And Integration Points

This chunk depends on the rest of fused Google Test for internal macros, type traits, containers, mutexes, factories, and implementations. It references `internal::UnitTestImpl`, `internal::ParameterizedTestCaseRegistry`, `internal::TypeParameterizedTest`, `internal::TypeParameterizedTestCase`, `internal::TypedTestCasePState`, `internal::NameGeneratorSelector`, `internal::TemplateSel`, `internal::Templates`, `internal::TypeList`, `internal::GenerateNames`, `internal::CodeLocation`, `internal::TypeId`, `internal::TestFactoryBase`, `internal::SetUpTestCaseFunc`, `internal::TearDownTestCaseFunc`, `internal::Random`, `internal::TraceInfo`, `internal::Mutex`, `internal::scoped_ptr`, and many assertion helper macros defined earlier in the same fused header.

The public integration point for RocksDB test code is broad. RocksDB tests include this header to define tests, fixtures, parameterized tests, typed tests, global environments, listeners, assertions, and `main()` bodies. `FRIEND_TEST` can also appear in production headers to expose internals to specific generated test classes. Because the header is vendored under RocksDB's third-party tree, changing it affects compilation of all tests that include RocksDB's bundled Google Test rather than a system-provided copy.

Platform integration appears through conditional macros. Windows-only HRESULT assertions depend on Windows SDK HRESULT conventions. Exception-specific APIs depend on `GTEST_HAS_EXCEPTIONS`. Wide-string substring helpers depend on `GTEST_HAS_STD_WSTRING`. Global `::string` support depends on `GTEST_HAS_GLOBAL_STRING`. `GTEST_DISABLE_MSC_WARNINGS_PUSH_` / `POP_` wrap declarations to quiet MSVC DLL-interface and unused-parameter warnings. `GTEST_DONT_DEFINE_*` switches allow users to avoid generic macro names such as `TEST`, `FAIL`, `SUCCEED`, and `ASSERT_EQ` when they conflict with other libraries.

The event listener interfaces are the main extension hooks for custom output, XML suppression/replacement, streaming results, failure behavior, and integration with external test harnesses. `UnitTest::listeners()` exposes the listener collection, while `UnitTest::parameterized_test_registry()` is documented as internal but is required by public parameterized-test macros.

## Risks And Edge Cases

- Static registration depends on object initialization across translation units. Parameterized and typed test patterns placed in headers can register in multiple translation units, so the macros use `static` state carefully; changing linkage or registration names can create duplicate, missing, or order-dependent tests.
- `TEST_P` and typed-test macros synthesize class names. User fixture names, test names, and `FRIEND_TEST` declarations must match those generated names exactly, including namespace placement.
- `INSTANTIATE_TEST_CASE_P` test-name generators must return non-empty, unique names containing only ASCII alphanumeric characters or underscore. The default `PrintToStringParamName` is not suitable for strings because quoting can create invalid names.
- `WithParamInterface<T>::parameter_` is a static pointer, not an owned value. The factory must guarantee parameter lifetime and must reset or replace it correctly for each running test.
- `GetParam()` intentionally checks that the parameter pointer is set; calling it from a fixture used with `TEST_F` instead of `TEST_P` trips a runtime check.
- Assertion macros note that argument evaluation order is undefined, even though each argument is evaluated once. Tests with side effects in assertion arguments can still be non-portable.
- Equality assertions compare C string pointers rather than string contents; tests must use `EXPECT_STREQ` and related macros for C-string content checks.
- `EqHelper<true>` has specialized overloads for null pointer literals to avoid bad overload resolution and compiler warnings. Refactoring null handling can reintroduce ambiguous overloads or `-Wconversion-null` warnings.
- `AssertionResult` supports implicit Boolean usage but uses a templated constructor guarded by `ImplicitlyConvertible` to avoid stealing copy construction. Changes to this overload set can break predicate assertion ergonomics or compiler compatibility.
- `TestResult::GetTestPartResult()` and `GetTestProperty()` abort on invalid indexes according to comments; callers should treat counts as authoritative.
- `TestEventListener::OnTestPartResult()` may throw only `AssertionException` or a subclass when using exceptions to skip to the next test. Throwing arbitrary exceptions from listeners risks undefined framework behavior.
- `UnitTest::Run()` and `AddEnvironment()` are documented as main-thread-only. Calling them from worker threads can race against runtime state despite some accessors being mutex protected.
- `ScopedTrace` assumes per-thread trace stacks. Cross-thread assertions are not automatically annotated by traces created in another thread.
- `StaticAssertTypeEq()` only fires when the containing template/function is instantiated, so unused template methods can hide type mismatches.
- The field name `test_properites_mutex_` is misspelled in this vendored version. External code should not depend on private names, but local patches should avoid accidental "cleanup" that changes ABI or conflicts with upstream.
- Fused generated predicate macros are limited to arity 5 in this version. Tests needing larger predicate arity must compose checks or use custom assertion helpers.

## Test Signals

This file is itself test infrastructure, so direct signals are primarily compile-time and framework-behavior signals from all tests that include it:

- successful compilation of ordinary tests using `TEST` and `TEST_F` confirms generated class names, fixture inheritance, and factory registration remain valid;
- value-parameterized tests using `TEST_P`, `INSTANTIATE_TEST_CASE_P`, `GetParam()`, `Range`, `Values`, `ValuesIn`, `Bool`, and `Combine` validate parameter registry, generator evaluation, parameter lifetime, and generated names;
- typed and type-parameterized tests validate type-list expansion, type-name generation, registration verification, and instantiation prefixes;
- assertion-heavy tests validate `AssertionResult`, predicate helpers, comparison helpers, fatal/non-fatal result reporting, message streaming, and source location capture;
- tests using `EXPECT_NO_FATAL_FAILURE` and `ASSERT_NO_FATAL_FAILURE` validate temporary reporter replacement and restoration;
- tests with `SCOPED_TRACE` validate trace stack push/pop and failure message annotation;
- listener customizations validate event ordering, listener ownership, default printer/XML generator release, and result forwarding;
- tests using `RecordProperty()` and XML output validate property routing to test, test-case, or global result scopes;
- shuffling, filtering, disabled tests, repeat counts, random seeds, exception handling, and XML/output flags validate the `UnitTest` run configuration exposed by this header.

For RocksDB specifically, regressions in this chunk usually surface as broad test binary compile failures, missing or duplicated tests, parameterized test instantiation errors, assertion messages losing useful diagnostics, incorrect fatal/non-fatal behavior, listener/XML output changes, or runtime failures in tests that depend on `FRIEND_TEST`, `SCOPED_TRACE`, or `TestWithParam`.
