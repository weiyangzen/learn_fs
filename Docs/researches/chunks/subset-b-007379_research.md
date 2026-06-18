# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/gtest/include/gtest/gtest.h lines 12712-19024

## Scope

This chunk is a mid-to-late slice of Hadoop's vendored, amalgamated Google Test header. It is dependency infrastructure for native C/C++ tests under `hadoop-common/src/main/native`, not Hadoop filesystem implementation logic. The range starts inside generated value-parameter support, covers the public value-parameterized test API, includes production-test friendship and test-part result declarations, defines typed-test and type-parameterized-test macros, declares Google Test command-line flags, and ends at the start of the core `testing::Test` fixture API.

Most code in this range is header-only templates and macros. Runtime behavior is coordinated with implementation code elsewhere in the same amalgamated Google Test distribution, especially the parameterized-test registry, `UnitTestImpl`, result reporters, and assertion implementation.

## Purpose and Major API Surface

The generated `internal::ValueArray24` tail through `ValueArray50` supports `testing::Values(...)` with explicit parameter lists up to 50 arguments. Each holder stores constructor arguments as `const` typed members and exposes `operator ParamGenerator<T>()`, which casts each stored value to the requested parameter type, builds a local C array, and delegates to `ValuesIn(array)`. Assignment is intentionally declared private and undefined.

When `GTEST_HAS_COMBINE` is enabled, `internal::CartesianProductGenerator2` through `CartesianProductGenerator10` implement tuple-valued generators for `testing::Combine(...)`. Each generator owns `ParamGenerator<TN>` inputs, returns heap-allocated iterator objects from `Begin()` and `End()`, and produces `testing::tuple<T1, ... TN>` values representing the Cartesian product of component generators.

Each Cartesian generator has a nested `Iterator` implementing `ParamIteratorInterface<ParamType>`. The iterator stores begin/end/current iterators for each component generator, caches the current tuple in `current_value_`, advances the last component first, rolls over exhausted components back to their begin iterators, and compares equality by base-generator identity plus component iterator positions. If any component iterator is at its end, `AtEnd()` reports the whole Cartesian iterator as past-the-end.

`internal::CartesianProductHolder2` through `CartesianProductHolder10` are polymorphic wrapper objects returned by `Combine(...)`. They store the original generator expressions by value and provide conversion operators to `ParamGenerator<tuple<...>>`, instantiating the matching `CartesianProductGeneratorN` after statically converting each holder member to the requested `ParamGenerator<TN>`.

The public value-parameterized API under `namespace testing` includes `Range(start, end[, step])`, `ValuesIn(...)`, `Values(...)`, `Bool()`, and `Combine(...)`. `Range` creates an internal `RangeGenerator`; `ValuesIn` supports iterator pairs, C arrays, and STL-style containers; `Values` overloads from 1 through 50 arguments return the corresponding `ValueArrayN`; `Bool` is a shorthand for `Values(false, true)`; `Combine` overloads from 2 through 10 generators return Cartesian-product holders.

`TEST_P(test_case_name, test_name)` defines a concrete test class derived from the parameterized fixture, registers a `TestMetaFactory` in `UnitTest::GetInstance()->parameterized_test_registry()`, and emits the user-authored `TestBody()` definition. `INSTANTIATE_TEST_CASE_P(prefix, test_case_name, generator, ...)` defines helper functions for evaluating the generator and optional parameter-name generator, then registers the instantiation with the same registry.

`FRIEND_TEST(test_case_name, test_name)` is the production-code helper for declaring Google Test-generated test classes as friends. It expands to a friend declaration of `test_case_name##_##test_name##_Test`.

`TestPartResult` represents one assertion or explicit test result. It records a `Type` enum (`kSuccess`, `kNonFatalFailure`, `kFatalFailure`), optional file name, line number, extracted summary, and full message. It exposes pass/fail predicates and accessors, plus `operator<<` for stream printing. `TestPartResultArray` owns a vector of results with append, indexed access, and size APIs. `TestPartResultReporterInterface` is the reporting abstraction, and `internal::HasNewFatalFailureHelper` temporarily installs itself as a reporter to detect whether a statement produced a new fatal failure while forwarding reports to the previous reporter.

Typed-test support defines `TYPED_TEST_CASE` and `TYPED_TEST` when `GTEST_HAS_TYPED_TEST` is set. The macros create a typelist alias for fixture types, define per-type test classes, and register each typed test through `internal::TypeParameterizedTest<...>::Register`.

Type-parameterized-test support defines `TYPED_TEST_CASE_P`, `TYPED_TEST_P`, `REGISTER_TYPED_TEST_CASE_P`, and `INSTANTIATE_TYPED_TEST_CASE_P` when `GTEST_HAS_TYPED_TEST_P` is set. These macros store pattern state in a static `TypedTestCasePState`, define template test classes in generated namespaces, verify registered pattern names, and instantiate registered templates over a supplied typelist through `internal::TypeParameterizedTestCase<...>::Register`.

The final part of the chunk declares public Google Test flags with `GTEST_DECLARE_*`: disabled-test inclusion, break-on-failure, exception catching, color, filter, listing, XML output, per-test time printing, random seed, repeat count, internal stack frames, shuffle, stack-trace depth, throw-on-failure, and result streaming. It also declares `kMaxStackTraceDepth`, internal friend/implementation classes, `GetUnitTestImpl()`, `ReportFailureInUnknownLocation(...)`, forward declarations of `Test`, `TestCase`, `TestInfo`, and `UnitTest`, and most of `AssertionResult` plus the beginning of `Test`.

`AssertionResult` is the predicate-result object used by `EXPECT_TRUE`, `EXPECT_FALSE`, predicate assertions, and user-defined assertion helpers. It stores a success boolean and lazily allocated message string, supports contextual bool conversion, negation, copy-and-swap assignment, stream insertion of custom messages and ostream manipulators, and factory functions `AssertionSuccess()` and `AssertionFailure()`.

`Test` is the base fixture class. In this chunk it declares fixture setup/teardown hooks, failure-state queries, and `RecordProperty(...)` overloads. `RecordProperty` documents XML persistence behavior for properties recorded in test, test-case, or global contexts.

## Control Flow and Behavioral Contracts

Value-parameter construction is lazy and type-directed. A `Values(...)` call creates a `ValueArrayN` containing the literal arguments. The actual `ParamGenerator<T>` is only formed when the holder is converted in a typed context, usually by `INSTANTIATE_TEST_CASE_P`. At that point each value must be `static_cast<T>` compatible, and the copied array is passed to `ValuesIn`.

`ValuesIn` is copy-based. Iterator, array, and container overloads all create a `ValuesInIteratorRangeGenerator`, whose contract in this header says parameter values are copied from the source container and retained until `RUN_ALL_TESTS()`. This allows callers to pass temporaries such as a returned vector.

Cartesian-product iteration behaves like nested loops with the rightmost generator as the fastest-changing dimension. `Begin()` initializes every component to its begin iterator. `Advance()` increments the last component, rolls it over when it reaches its end, then increments the preceding component, repeating leftward as needed. If any component range is empty, `AtEnd()` makes the whole product empty.

Iterator comparison is intentionally strict. `Equals()` first checks that both iterators share the same base generator and aborts through `GTEST_CHECK_` if code compares iterators from different generators. Two iterators that are both past-the-end compare equal even if they reached that state through different component positions.

Parameterized-test registration occurs during static initialization. `TEST_P` defines a static dummy integer initialized by `AddToRegistry()`, and `INSTANTIATE_TEST_CASE_P` defines another static dummy initialized by `AddTestCaseInstantiation(...)`. The actual generator evaluation is deferred through generated helper functions so registration can capture factory callbacks and source locations before tests run.

Typed-test macros also rely on static registration. `TYPED_TEST` registers the template test against the typelist declared by `TYPED_TEST_CASE`. Type-parameterized tests are a two-stage flow: declare the pattern state, define one or more `TYPED_TEST_P` bodies, verify the complete list with `REGISTER_TYPED_TEST_CASE_P`, then instantiate the pattern with `INSTANTIATE_TYPED_TEST_CASE_P`.

Assertion result flow is message-accumulating. User predicates return `AssertionSuccess()` or `AssertionFailure()` and can stream detail into the returned `AssertionResult`. Boolean assertions inspect the bool conversion and, when the assertion expectation is not met, read `message()` to produce a richer failure message.

Fatal-failure detection flow for `ASSERT_NO_FATAL_FAILURE`/`EXPECT_NO_FATAL_FAILURE` uses `HasNewFatalFailureHelper`: construct helper, replace current result reporter, execute the statement, record whether any reported `TestPartResult` is fatal, forward all reports to the original reporter, and restore the original reporter in the destructor.

## State, Persistence, and Side Effects

The generator holder classes are immutable after construction. They store values and component generators in `const` members and disable assignment. Their main side effect is allocating generator or iterator objects with `new`; ownership is expected to pass into `ParamGenerator`/iterator wrappers defined earlier in the Google Test header.

Static registration is the main persistent in-process state. Parameterized and typed tests are registered into singleton Google Test state before `RUN_ALL_TESTS()`. The generated variable names include test case, test name, and prefix tokens, so duplicate macro uses or non-unique prefixes can collide at compile time or registration time.

`TestPartResult` persists assertion metadata in memory as strings and enum state. `TestPartResultArray` stores an ordered vector of results. `RecordProperty` does not persist directly in this chunk, but its documented side effect is writing key/value metadata into XML output at `<testcase>`, `<testsuite>`, or `<testsuites>` scope depending on when it is called.

Google Test flags are global process state. The declarations in this chunk expose command-line and programmatic controls for filtering, shuffling, repeats, random seed, stack traces, XML output, exception handling, and streaming results. Definitions and parsing behavior live elsewhere.

No filesystem or network I/O is implemented in this slice, but flags such as `output` and `stream_result_to` configure implementation code elsewhere to emit XML files or stream test events.

## Dependencies and Integration Points

This chunk depends on Google Test internal generator contracts declared earlier in the header: `ParamGenerator`, `ParamGeneratorInterface`, `ParamIteratorInterface`, `RangeGenerator`, `ValuesInIteratorRangeGenerator`, `CheckedDowncastToActualType`, `IteratorTraits`, `TestMetaFactory`, `ParameterizedTestCaseRegistry`, `TypedTestCasePState`, `TypeList`, `Types`, `Templates`, `TemplateSel`, `TypeParameterizedTest`, and `TypeParameterizedTestCase`.

It depends on Google Test tuple support through `::testing::tuple` and limits `Combine` to 10 inputs because this vendored Google Test tuple implementation supports that arity. It also depends on macro configuration gates such as `GTEST_HAS_PARAM_TEST`, `GTEST_HAS_COMBINE`, `GTEST_HAS_TYPED_TEST`, and `GTEST_HAS_TYPED_TEST_P`.

The public macros integrate with user C++ test source. `TEST_P`, `INSTANTIATE_TEST_CASE_P`, typed-test macros, and `FRIEND_TEST` generate concrete C++ types, functions, namespaces, static variables, and friend declarations. Their token-pasting behavior makes source identifiers part of the ABI-like compile-time surface.

`TestPartResult` and `HasNewFatalFailureHelper` integrate with the result-reporting pipeline used by assertions, event listeners, XML output, and failure-handling macros. `AssertionResult` integrates with assertion macros and user predicate functions via implicit bool conversion and streamed messages.

Standard library dependencies include `std::string`, `std::vector`, `std::ostream`, `std::endl`/ostream manipulators, and C++ iterators/containers. The code also uses C `assert`, raw pointers, and heap allocation, reflecting the older Google Test style vendored into Hadoop.

Hadoop integration is indirect: native tests compiled in the Hadoop tree include this header to define and register tests for native filesystem, JNI, or utility components. Changes here affect the native test harness rather than production Hadoop runtime.

## Risks and Compatibility Notes

This is generated and vendored third-party test infrastructure. Local edits are high-risk because macro expansions, generated arities, and old compiler compatibility details are easy to break and difficult to diagnose. Prefer replacing the vendored Google Test version wholesale over hand-editing individual generated classes.

`ValueArrayN` overloads require every stored value to be castable to the fixture parameter type. Mixed-type `Values(1, 2, 3.5)` works by delaying conversion, but narrowing, invalid casts, or temporaries with unsafe pointer lifetimes can still produce compile-time or runtime surprises.

`Values(...)` only supports up to 50 parameters in this vendored version, and `Combine(...)` only supports 2 through 10 generators. Tests needing more values or dimensions must use `ValuesIn` or custom generators.

Cartesian-product size grows multiplicatively. Large generators or many combined dimensions can create very large test suites, long static registration lists, and slow `RUN_ALL_TESTS()` execution. Empty component generators silently produce no tests for that instantiation.

The iterators cache `current_value_` and return a pointer to that cache. Callers must not retain `Current()` pointers beyond iterator movement or lifetime. Equality checks across different generator instances intentionally fail fast through `GTEST_CHECK_`.

Static-initialization ordering is a practical risk. Parameterized and typed tests depend on static dummy registration variables being initialized before `RUN_ALL_TESTS()`. Code split across translation units must include the right declarations and must use unique instantiation prefixes to avoid duplicate test names.

The `INSTANTIATE_TEST_CASE_P` optional name generator must return non-empty unique suffixes containing only ASCII alphanumeric characters or underscores. Bad suffix generation is detected by Google Test registration/runtime checks and can make all tests in an instantiation fail to register or run.

`FRIEND_TEST` couples production classes to Google Test's generated test-class naming convention. Renaming a test case or test name requires updating friend declarations, and namespaces must match the generated test class scope.

`TestPartResult` stores file names as empty strings when unknown and exposes `NULL` for empty file names. Consumers must handle null file pointers and line number `-1`. `ExtractSummary` strips stack traces from messages, so tests that assert exact summaries can be sensitive to failure-message formatting.

`AssertionResult` lazily allocates its message string to reduce stack usage. Predicate helpers used in very hot assertions should avoid streaming success messages unless needed for negative assertions, as the comments explicitly note performance cost for informative success cases.

The chunk ends in the middle of `class Test`; fixture construction, `SetUp`, `TearDown`, `TestBody`, and assertion helper details continue in the next source chunk. The final per-file report should merge this chunk with neighboring chunks before drawing conclusions about the complete `testing::Test` API.

## Test Signals

Parameterized generator tests should cover `Range` with default and explicit step, integral and floating values, empty `start >= end` ranges, `ValuesIn` from arrays, containers, iterators, and temporaries, and `Values` overloads at low arity plus high arities near 50.

Type-conversion tests should instantiate fixtures with `Values` arguments whose stored types differ from `ParamType`, including safe numeric conversions, string-literal-to-`const char*`, and intentionally invalid casts that should fail compilation in negative compile tests.

Cartesian-product tests should cover `Combine` for 2, 3, and 10 generators; rightmost-fastest iteration order; empty component generators; equality of independently copied begin/end iterators; end iterator equality after different advancement paths; and failure when comparing iterators from different base generators.

Registration tests should cover `TEST_P` plus `INSTANTIATE_TEST_CASE_P`, multiple instantiations of the same pattern with unique prefixes, duplicate-name rejection, custom parameter-name generators, invalid suffix characters, empty suffixes, and use of `PrintToStringParamName` where supported.

Typed-test tests should cover `TYPED_TEST_CASE`/`TYPED_TEST` over multiple types and a single type, plus type-parameterized pattern declaration, `TYPED_TEST_P` definitions, `REGISTER_TYPED_TEST_CASE_P` verification, multiple `INSTANTIATE_TYPED_TEST_CASE_P` calls, and detection of unregistered or misspelled test pattern names.

Friendship tests should verify that `FRIEND_TEST` grants access to private members for the exact generated test class name and fails when the test case or test name differs.

Test-part result tests should cover success, nonfatal failure, fatal failure, unknown file names, line `-1`, full message versus summary extraction, stream formatting with `operator<<`, `TestPartResultArray` append/index/size, and reporter forwarding through `HasNewFatalFailureHelper`.

Assertion-result tests should cover bool construction, copy construction, assignment, negation, empty messages, streamed values, streamed ostream manipulators, `failure_message()` compatibility, `AssertionSuccess()`, `AssertionFailure()`, and predicate messages appearing in `EXPECT_TRUE` and `EXPECT_FALSE` diagnostics.

Flag-related tests should exercise command-line parsing and runtime effects in the implementation chunk: filters, disabled tests, repeat, shuffle with random seed, XML output, color mode, exception catching, break/throw on failure, stack-trace depth capped by `kMaxStackTraceDepth`, listing tests, and result streaming.

Native Hadoop test-harness smoke tests should compile representative native tests that use plain `TEST`, `TEST_F`, `TEST_P`, `ValuesIn`, `Combine`, typed tests, and `FRIEND_TEST`, then run them under the Hadoop native build to catch compiler-version and link compatibility regressions in this vendored header.
