# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/gtest/include/gtest/gtest.h lines 6479-12711

## Scope

This chunk is a large middle slice of Hadoop's vendored, fused Google Test public header. It starts inside the generated typed-test template-list utilities, beginning at the tail of the `Templates31`/`Templates32` area, and continues through core internal assertion helpers, test registration macros, death-test public/internal APIs, value-parameterized test infrastructure, the `linked_ptr` helper, universal value printers, and the beginning of generated `ValueArray` helpers for `Values(...)`. The range ends inside `internal::ValueArray24`, so later chunks are needed for the rest of the generated parameter helper arities and user-facing parameter-test macros.

The code is mostly header-only declarations, templates, and macros. Many exported `GTEST_API_` functions and classes are declared here but implemented in the compiled Google Test library. Runtime behavior below is therefore split between behavior encoded directly in templates/macros and contracts implied by declarations.

## Purpose and Major API Surface

The initial typed-test section provides generated compile-time lists for template template parameters. `Templates32` through `Templates50` are linked-list-like structures with `Head` as `TemplateSel<Tn>` and `Tail` as the next shorter `TemplatesN`. The user-facing `Templates<...>` wrapper accepts up to 50 template template parameters defaulted to `NoneT` and maps the visible list length to a precise `TemplatesN<...>::type` specialization. `TypeList<T>` normalizes either a single type or a generated `Types<...>` list into the internal type-list representation used by `TYPED_TEST_CASE` and `INSTANTIATE_TYPED_TEST_CASE_P`.

The core internal section begins after the fused `gtest-type-util.h` guard. It defines token-concatenation helpers, forward declarations for major public types, null-literal detection (`IsNullLiteralHelper`, `GTEST_IS_NULL_LITERAL_`), user-message composition (`AppendUserMessage`), optional `GoogleTestFailureException`, and `ScopedTrace`. It also declares diff helpers under `internal::edit_distance`, `DiffStrings`, equality failure formatting via `EqFailure`, and boolean assertion failure formatting via `GetBoolAssertionFailureMessage`.

`FloatingPoint<RawType>` is the chunk's central numeric helper. It stores a `float` or `double` in a union, exposes bit masks, sign/exponent/fraction accessors, `Infinity()`, `Max()`, `ReinterpretBits`, `is_nan()`, and `AlmostEquals()`. `AlmostEquals()` rejects NaN and compares values by converting IEEE sign-and-magnitude bit patterns into a biased representation, then checking whether the distance is within `kMaxUlps`. `Float` and `Double` are typedefs for the float and double instantiations.

Test identity and registration helpers include `TypeId`, `TypeIdHelper<T>`, `GetTypeId<T>()`, `GetTestTypeId()`, `TestFactoryBase`, `TestFactoryImpl<TestClass>`, setup/teardown function typedefs, `CodeLocation`, and `MakeAndRegisterTestInfo`. `TypeId` is an opaque `const void*` backed by the address of a per-type static `dummy_` variable, allowing Google Test to detect accidental reuse of a test-case name with different fixture classes.

Typed-test registration support includes `TypedTestCasePState`, `SkipComma`, `GetPrefixUntilComma`, `SplitString`, `TypeParameterizedTest`, and `TypeParameterizedTestCase`. `TypedTestCasePState` records defined type-parameterized test names and source locations, rejects test definitions after registration, and verifies that names passed to `REGISTER_TYPED_TEST_CASE_P` match defined tests. `TypeParameterizedTest` registers one test selector against every type in a type list, while `TypeParameterizedTestCase` iterates over every registered test selector and then every type.

General internal utility templates cover type traits and array support: `CompileAssertTypesEqual`, `RemoveReference`, `RemoveConst`, `AddReference`, `ImplicitlyConvertible`, `IsAProtocolMessage`, container detection through `IsContainerTest`, `EnableIf`, recursive `ArrayEq`, `ArrayAwareFind`, `CopyArray`, and `NativeArray<Element>`. `NativeArray` adapts C arrays to a minimal read-only STL-style container and can either reference or copy the source array.

Assertion and test-definition macros include `GTEST_MESSAGE_AT_`, `GTEST_FATAL_FAILURE_`, `GTEST_NONFATAL_FAILURE_`, `GTEST_SUCCESS_`, exception assertion helpers (`GTEST_TEST_THROW_`, `GTEST_TEST_NO_THROW_`, `GTEST_TEST_ANY_THROW_`), boolean assertion helper `GTEST_TEST_BOOLEAN_`, no-fatal-failure helper `GTEST_TEST_NO_FATAL_FAILURE_`, `GTEST_TEST_CLASS_NAME_`, and `GTEST_TEST_`. `GTEST_TEST_` expands a test declaration into a concrete subclass, static `TestInfo*` registration through `MakeAndRegisterTestInfo`, and the `TestBody()` definition.

The death-test section declares internal flags, the abstract `DeathTest` controller, `DeathTestFactory`, `DefaultDeathTestFactory`, `ExitedUnsuccessfully`, `InternalRunDeathTestFlag`, `ParseInternalRunDeathTestFlag`, and the core macros that implement `ASSERT_EXIT`, `EXPECT_EXIT`, `ASSERT_DEATH`, `EXPECT_DEATH`, debug death tests, and unsupported-platform fallbacks. User-facing predicate classes `ExitedWithCode` and, on non-Windows platforms, `KilledBySignal` model exit-status checks.

The parameterized-test introduction documents `TEST_P`, `INSTANTIATE_TEST_CASE_P`, `Range`, `Values`, `ValuesIn`, `Bool`, and `Combine`. The internal parameter utilities then define `TestParamInfo`, `PrintToStringParamName`, iterator and generator interfaces, concrete `RangeGenerator`, concrete `ValuesInIteratorRangeGenerator`, default and user-supplied parameter-name generator selection, parameterized test factories, `ParameterizedTestCaseInfo`, and `ParameterizedTestCaseRegistry`.

`linked_ptr<T>` is a test-internal reference-tracking smart pointer used by parameterized-test infrastructure. Its `linked_ptr_internal` nodes form a circular list of all references to the same raw object, protected by the global `g_linked_ptr_mutex`. The last departing pointer deletes the raw object.

The printer section implements the universal Google Test value printer. It provides fallback formatting for raw bytes, protobuf messages, integer-convertible values, STL-style containers, pointers, char and wchar strings, arrays, pairs, TR1 tuples, std tuples, references, and terse printing. Public `PrintToString<T>` wraps `UniversalTersePrinter<T>` into a string.

The final generated parameter utility section begins with declarations for `ValuesIn(...)` overloads, then defines `internal::ValueArray1` through the start of `ValueArray24`. Each `ValueArrayN` stores N constructor arguments and provides a polymorphic conversion operator to `ParamGenerator<T>` by `static_cast<T>`-ing each stored value into a temporary C array and returning `ValuesIn(array)`.

## Control Flow and Behavioral Contracts

Typed-test template-list control flow is compile-time recursion. The generated `TemplatesN` structures decompose a list into `Head` and `Tail`; the `Templates<...>` wrapper chooses the shortest exact representation by specializing on the first trailing `NoneT`. This keeps user syntax compact while improving compiler diagnostics by avoiding giant lists of defaulted `NoneT` arguments in error messages.

Test registration flow is static-initialization driven. `GTEST_TEST_` creates a derived test class, declares a static `test_info_`, initializes that static by calling `MakeAndRegisterTestInfo`, and leaves the following user block as the `TestBody()` implementation. Fixture identity is recorded with `TypeId`, setup and teardown callbacks are taken from the parent fixture, and a `TestFactoryImpl` is allocated for later per-test object creation.

Assertion macro control flow uses generated labels, `goto`, and `GTEST_AMBIGUOUS_ELSE_BLOCKER_` to preserve macro syntax and streamed-message support. Exception assertions execute the statement inside `try`/`catch`, distinguish expected exception, different exception, and no exception, then route failures through the supplied fatal or nonfatal failure macro. `GTEST_TEST_NO_FATAL_FAILURE_` snapshots thread-local fatal-failure state through `HasNewFatalFailureHelper` and fails if the statement introduced a new fatal result.

Floating-point comparison flow maps raw IEEE bits into an ordering where adjacent representable values are adjacent unsigned integers even across negative and positive zero. NaN short-circuits to false. This is the basis for `EXPECT_FLOAT_EQ`, `EXPECT_DOUBLE_EQ`, and related assertions that compare within a fixed ULP budget rather than by exact equality.

Type-parameterized test registration is a two-level compile-time recursion. For each registered test selector, `TypeParameterizedTestCase` verifies the selector name exists in `TypedTestCasePState`, fetches the selector's source location, and calls `TypeParameterizedTest` to register that selector once per type. Each concrete registration builds a synthesized test-case name from optional prefix, base case name, and type index, records the type name via `GetTypeName<Type>()`, and uses a `TestFactoryImpl<TestClass>`.

Death-test macro control flow is parent/child role based. `GTEST_DEATH_TEST_` creates a `DeathTest`, then calls `AssumeRole()`. In `OVERSEE_TEST`, the parent waits and asks `Passed(predicate(status))`; failure jumps to a label that emits `DeathTest::LastMessage()`. In `EXECUTE_TEST`, the child installs a `ReturnSentinel`, executes the statement with exception trapping when enabled, and aborts with `TEST_DID_NOT_DIE` if execution reaches the end. `ReturnSentinel` marks an unexpected `return` from the statement as `TEST_ENCOUNTERED_RETURN_STATEMENT`.

Unsupported death-test flow compiles but does not execute the statement and regex. `GTEST_UNSUPPORTED_DEATH_TEST_` logs a warning, places the statement and regex in an always-false branch to preserve compile-time checking, and returns a streamable `Message` object for syntax compatibility.

Parameterized generator flow is iterator based. `ParamGenerator<T>` owns an immutable `ParamGeneratorInterface<T>` through `linked_ptr`, creates `ParamIterator<T>` wrappers from `Begin()` and `End()`, and supports copying by sharing the underlying generator. `RangeGenerator` computes an end index up front and advances by repeated `value_ + step_`. `ValuesInIteratorRangeGenerator` copies all source values into an internal `std::vector<T>`, then its iterator lazily caches the current value in a `scoped_ptr<const T>` so `operator->` can return a stable pointer even when dereferencing the underlying iterator would create a temporary.

Parameterized test registration flow is deferred until `RUN_ALL_TESTS`. `TEST_P` adds test patterns to `ParameterizedTestCaseInfo<TestCase>`, and `INSTANTIATE_TEST_CASE_P` records generator factories and name generators. `ParameterizedTestCaseInfo::RegisterTests()` loops over every test pattern, every instantiation, and every generated parameter; validates generated parameter names as non-empty alphanumeric/underscore strings; rejects duplicate names inside one instantiation; then calls `MakeAndRegisterTestInfo` with the value parameter string and a freshly allocated `ParameterizedTestFactory`.

Printer control flow is intentionally layered. `UniversalPrinter<T>::Print` calls unqualified `PrintTo(value, os)`, allowing argument-dependent lookup to find user printers before internal fallbacks. Internal `PrintTo` selects container, pointer, or scalar fallback via `IsContainerTest<T>(0)` and `is_pointer<T>()`. Scalar fallback uses `operator<<` lookup with `testing::internal2::operator<<` as a last resort, and that last resort selects protobuf debug strings, integer conversion, or raw-byte output. Arrays, references, strings, pairs, tuples, and terse char-pointer printing are handled by partial or full specializations.

Generated `ValueArrayN` flow is conversion-time polymorphism. `Values(v1, ..., vN)` returns a `ValueArrayN` with the original argument types; conversion to `ParamGenerator<T>` happens later when the target fixture parameter type is known. The conversion allocates a stack array of converted `T` values, then immediately calls `ValuesIn(array)`, whose implementation copies values into a generator, avoiding dangling stack references.

## State, Persistence, and Side Effects

Most state in this chunk is in compile-time types, static registration records, generator objects, and transient assertion helpers. The file itself is a vendored fused header; changes to declarations and macros affect every native Hadoop test that includes Google Test.

`TypeIdHelper<T>::dummy_` is a per-instantiation static boolean whose address persists for the life of the program and acts as an opaque fixture identity. `GetTestTypeId()` is declared separately because the generic template may be unreliable for `::testing::Test` under an old Mac OS X framework linker issue.

`ScopedTrace` pushes trace metadata on construction and pops it on destruction. The actual stack is maintained by Google Test internals outside this chunk. `kStackTraceMarker` is an exported marker string used in failure output to separate stack traces from failure text.

`TypedTestCasePState` persists type-parameterized test names and source locations in a `std::map`. Its `registered_` flag makes `REGISTER_TYPED_TEST_CASE_P` a boundary: after registration, additional `TYPED_TEST_P` definitions are rejected with a message to `stderr`, `fflush`, and `posix::Abort()`.

`DeathTest::last_death_test_message_` stores the last death-test outcome message as static process state. `InternalRunDeathTestFlag` owns a file descriptor and closes it in its destructor if it is nonnegative. Death tests create child processes or re-execute the test program depending on style, so they can have process-level side effects, file-descriptor handoff, and output captured from child `stderr`.

`linked_ptr` state is a raw pointer plus a `linked_ptr_internal` ring node. Copying joins the source ring under `g_linked_ptr_mutex`; destruction or reset departs from the ring and deletes the pointee only if this was the last reference. The implementation is thread-safe for copying and assigning linked pointers, but it has global mutex contention and does not protect the pointed object's own state.

`NativeArray` either references external array storage or owns a heap copy. It records which behavior applies by storing a member-function pointer (`clone_`) to `InitRef` or `InitCopy`; the destructor deletes the backing array only for copied arrays. Equality is size plus recursive element equality.

Parameterized generator state is immutable once constructed. `RangeGenerator` stores begin, end, step, and computed end index. `ValuesInIteratorRangeGenerator` owns a copied vector of source values. `ParamGenerator` shares immutable generator implementations through `linked_ptr`. Iterators own cloneable iterator implementations through `scoped_ptr`.

`ParameterizedTestCaseRegistry` owns a vector of `ParameterizedTestCaseInfoBase*` and deletes them in its destructor. Each `ParameterizedTestCaseInfo<TestCase>` owns test pattern metadata, meta factories through `scoped_ptr`, and instantiation metadata. `MakeAndRegisterTestInfo` takes ownership of `TestFactoryBase*` returned by factories.

Printer functions have no persistent storage in this range, but they produce failure-message strings and streams that are part of the observable test output. Container printing truncates after 32 elements, array printing truncates long arrays to head and tail chunks, protobuf formatting switches from one-line to multi-line output after 50 characters, and char-pointer formatting differs between comparison formatting and terse printing.

The `ValueArrayN` objects store constructor arguments by value as `const` data members. They are non-assignable. The generated arity boundary is externally visible because this Google Test version supports `Values(...)` only up to the generated maximum, and this chunk covers arities 1 through the start of 24.

## Dependencies and Integration Points

This header depends on many earlier fused Google Test definitions: platform macros such as `GTEST_HAS_TYPED_TEST`, `GTEST_HAS_PARAM_TEST`, `GTEST_HAS_DEATH_TEST`, `GTEST_HAS_EXCEPTIONS`, OS feature macros, `GTEST_API_`, `GTEST_CHECK_`, `GTEST_DISALLOW_COPY_AND_ASSIGN_`, `GTEST_LOCK_EXCLUDED_`, `MutexLock`, `scoped_ptr`, `RE`, `Message`, `AssertionResult`, `AssertHelper`, `TestPartResult`, `HasNewFatalFailureHelper`, `StaticAssertTypeEqHelper`, `bool_constant`, `true_type`, `false_type`, `is_pointer`, `IteratorTraits`, `CheckedDowncastToActualType`, `StreamableToString`, `StripTrailingSpaces`, `FormatFileLocation`, `GetTypeName`, and `GTEST_BIND_`.

Standard C and C++ dependencies include `std::runtime_error`, `std::string`, `std::vector`, `std::map`, `std::set`, `std::ostream`, `std::stringstream`, `std::pair`, `std::tr1::tuple`, `std::tuple`, `std::numeric` limits via `FLT_MAX`/`DBL_MAX`, `strchr`, `fprintf`, `fflush`, `isalnum`, `assert`, and pointer/integer casting.

Death tests integrate with process and OS behavior through wait-style exit statuses, signals on non-Windows platforms, child process management in implementation files, file descriptors, `stderr`, and platform-specific regex support. Public macros integrate with user code through `ASSERT_*`/`EXPECT_*` streaming syntax and with `--gtest_death_test_style`, `--gtest_death_test_use_fork`, and `--gtest_internal_run_death_test`.

Parameterized tests integrate with `UnitTestImpl` through `ParameterizedTestCaseRegistry::RegisterTests()`, with `TEST_P` through `AddTestPattern`, with `INSTANTIATE_TEST_CASE_P` through `AddTestCaseInstantiation`, and with normal test execution through `TestFactoryBase`. The generator APIs integrate with user containers and iterator ranges via `ValuesIn`, with custom naming through `TestParamInfo` and name functors, and with failure output through `PrintToString`.

Printers integrate deeply with assertion failure formatting. `EqFailure`, `FormatForComparisonFailureMessage`, and `PrintToString` determine what users see for `EXPECT_EQ`, string assertions, containers, pairs, tuples, protobufs, arrays, pointers, references, and values without custom output support. User extension points are `PrintTo(const T&, ostream*)` in the type's namespace and stream insertion operators found by ADL or global lookup.

For Hadoop specifically, this header is under `src/main/native/gtest/include`, so its direct consumers are native C/C++ unit tests in Hadoop's native code build. It is vendored infrastructure rather than Hadoop production runtime logic, but it gates how native tests are registered, named, filtered, executed, and diagnosed.

## Risks and Compatibility Notes

Generated arity scaffolding is brittle. Changing `TemplatesN`, `TypesN`, or `ValueArrayN` signatures can break typed tests and parameterized tests at compile time, often with difficult template diagnostics. This chunk starts and ends inside generated regions, so any per-file reconciliation should account for adjacent chunks before drawing final conclusions about maximum arities.

Static initialization order is a core risk. `GTEST_TEST_`, typed tests, and parameterized tests rely on namespace-scope static variables to register metadata before `RUN_ALL_TESTS`. Changes to macro expansion, factory ownership, or registration ordering can silently drop tests, duplicate tests, or attach the wrong fixture type.

Macro control flow is subtle. The assertion and death-test macros rely on `goto` labels formed with `__LINE__`, `GTEST_AMBIGUOUS_ELSE_BLOCKER_`, and streamable failure expressions. Refactoring these macros can introduce dangling-else bugs, duplicate-label problems, unreachable-code warnings, lost failure messages, or statements that execute more than once.

Death tests are platform-sensitive and process-sensitive. Risks include invalid death-test style flags, thread-safety warnings around fork/clone, child processes returning instead of dying, exceptions escaping test statements, regex feature differences between POSIX and fallback regex engines, `NDEBUG` behavior for debug death tests, and file descriptor lifetime in `InternalRunDeathTestFlag`.

`linked_ptr` ownership has sharp edges. Creating two independent `linked_ptr` rings from the same raw pointer can double-delete. Cycles leak. Assignment traverses the whole reference ring. The global mutex protects ring metadata but can add contention and does not make the pointee thread-safe.

Floating-point comparison depends on IEEE assumptions and bit widths. Bugs in masks, reinterpretation, biased-distance conversion, or `kMaxUlps` semantics would affect all approximate float/double assertions. NaN handling is intentionally false even when both operands are NaN.

Printer lookup is intentionally dependent on C++ name lookup rules. Moving namespaces, renaming fallback operators, or changing overload specificity can make user `PrintTo` functions stop working or make internal raw-byte printers override better user-provided printers. C-string formatting is especially nuanced: comparison output may print a pointer or a string depending on the other operand type.

Parameterized test naming is strict. Custom parameter-name generators must return non-empty names containing only alphanumeric characters and underscores, and names must be unique per instantiated test pattern. The default name generator uses the numeric index. `PrintToStringParamName` can generate invalid names for arbitrary parameter values unless the value's printer emits a valid identifier-like string.

Generator lifetime and conversion behavior matter. `ValuesInIteratorRangeGenerator` intentionally copies source values so arrays or stack containers can go out of scope. `ValueArrayN` converts every stored argument with `static_cast<T>` at generator conversion time; invalid or narrowing conversions surface as compile-time errors or compiler warnings depending on target type.

Because this is vendored Google Test, local modifications create upgrade and compatibility risk. Hadoop native tests may assume this exact older API spelling, including `TYPED_TEST_CASE`, `INSTANTIATE_TEST_CASE_P`, and generated non-variadic helper limits.

## Test Signals

Compile-time tests should cover typed-test lists with single type, `Types<...>` lists, template lists across the generated arity boundary visible here, and type-parameterized test registration with matching and mismatched `REGISTER_TYPED_TEST_CASE_P` names. Negative tests should verify that adding a typed test after registration aborts and that missing registered names are reported with source locations.

Core assertion tests should cover fatal, nonfatal, and success message macros; exception assertions for expected exception, no exception, wrong exception, and exception-disabled builds; boolean assertions with `AssertionResult`; no-fatal-failure detection; null-literal detection; diff output; equality failure formatting; and scoped trace output.

Floating-point tests should cover exact equality, values within and beyond the ULP budget, positive and negative zero, infinities, maximum finite values, NaN on either side, sign-bit behavior, and bit reinterpretation for both `Float` and `Double`.

Registration tests should cover `TypeId` uniqueness and stability, `GetTestTypeId()`, fixture mismatch detection for reused test-case names, `TestFactoryImpl` object creation, setup/teardown callback wiring, and `GTEST_TEST_` expansion behavior as observed through `UnitTest` test discovery.

Death-test tests should cover `ASSERT_DEATH`, `EXPECT_DEATH`, `ASSERT_EXIT`, `EXPECT_EXIT`, `ExitedWithCode`, `KilledBySignal` where supported, bad regex or style handling, statements that return, throw `std::exception`, throw non-standard exceptions, or do not die, debug death behavior under `NDEBUG` and non-`NDEBUG`, unsupported-platform warning behavior, and parsing/closing of `InternalRunDeathTestFlag`.

Array and type-trait tests should cover `ArrayEq` and `CopyArray` for scalar, one-dimensional, and multi-dimensional arrays; `NativeArray` reference versus copy semantics; equality; copied array destruction; non-const/non-reference static assertion constraints; `ImplicitlyConvertible`; container detection; protobuf-message detection; and `ArrayAwareFind`.

Parameterized generator tests should cover `Range` with normal, empty, and custom increment cases; `ValuesIn` from arrays, containers, and iterator ranges whose source goes out of scope; iterator clone, increment, equality, and cross-generator comparison failure; `ParamGenerator` copy sharing; `ParameterizedTestFactory` setting parameters before construction; duplicate and invalid parameter names; multiple instantiations; and registration before `RUN_ALL_TESTS`.

`linked_ptr` tests should cover default construction, raw-pointer ownership, copy across convertible pointer types, reset, assignment, last-reference deletion, self-assignment, null pointer copies, comparison operators, `make_linked_ptr`, and concurrent copy/assignment stress where test infrastructure supports it.

Printer tests should cover user `PrintTo`, user `operator<<`, protobuf one-line and multi-line outputs, enums/integer-convertible types, raw byte fallback, containers and 32-element truncation, null and non-null pointers, function pointers, char and wchar strings, signed/unsigned char pointers as void pointers, arrays and long-array truncation, references with addresses, terse printing, pairs, TR1 tuples, std tuples, `PrintToString`, and comparison formatting for `char*` versus `std::string` and versus pointer-like operands.

Generated `ValueArray` tests should cover `Values(...)` arities within this chunk, mixed source argument types converted to one fixture parameter type, copy from temporary stack arrays through `ValuesIn`, non-assignability assumptions, and compile failures for unsupported conversions.
