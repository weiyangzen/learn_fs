# sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/gtest.h lines 6520-12679

## Chunk Scope

This chunk is a large fused Google Test 1.8.1 header slice. It starts in the generated typed-test template list utilities and runs through internal assertion helpers, typed-test registration, death-test public/internal APIs, parameterized-test internals, universal value printers, and the beginning of generated `ValueArrayN` helpers for `Values(...)`. The slice begins mid generated `TemplatesN` series and ends mid `ValueArray15`; adjacent chunks are needed for the complete generated ranges and public macro definitions that reference these internals.

## Purpose

The code provides much of Google Test's test declaration and diagnostics machinery:

- Typed-test and type-parameterized-test infrastructure that maps user-friendly `Types<...>`/`Templates<...>` declarations into recursive type lists and registers every fixture/test/type combination.
- Assertion plumbing for boolean, exception, fatal/nonfatal, and test declaration macros.
- Death-test interfaces and macros, including parent/child role selection, child process execution, exit-status predicates, unsupported-platform fallbacks, and debug-only death assertions.
- Parameterized-test generator, iterator, factory, and registry internals used by `TEST_P` and `INSTANTIATE_TEST_CASE_P`.
- Universal printing and comparison formatting used in assertion failure messages.
- A small reference-counted `linked_ptr` implementation used to share immutable generator and test metadata.

## Important APIs, Types, and Functions

### Typed Template Utilities

- `Templates24` through `Templates50` and `Templates<...>::type` build recursive type-list-like structures for template template parameters. Each `TemplatesN` exposes `Head = TemplateSel<T1>` and `Tail = TemplatesN-1<...>`.
- The `Templates<...>` primary template defaults all 50 parameters to `NoneT` and maps full input to `Templates50`. Its generated partial specializations collapse trailing `NoneT` parameters to `Templates0` through `Templates49`, improving compiler diagnostics by avoiding huge default-argument dumps.
- `TypeList<T>` maps either a single type or a `Types<...>` pack into an internal `TypesN` list so typed-test macros can accept both forms.
- `DefaultNameGenerator`, `NameGeneratorSelector`, `GenerateNamesRecursively`, and `GenerateNames` generate type-name suffixes for typed-test instantiations. Default names are integer indexes unless a user-provided generator is selected.
- `TypedTestCasePState` tracks names and source locations of type-parameterized tests defined before `REGISTER_TYPED_TEST_CASE_P`. `AddTestName()` aborts if definitions are attempted after registration; `VerifyRegisteredTestNames()` is declared here for cross-checking macro-provided names.
- `TypeParameterizedTest<Fixture, TestSel, Types>::Register()` recursively registers one typed test for every type in `Types`.
- `TypeParameterizedTestCase<Fixture, Tests, Types>::Register()` recursively walks test templates and calls `TypeParameterizedTest` for each test/type combination.

### Assertion and Test Registration Internals

- `GTEST_CONCAT_TOKEN_`, `GTEST_STRINGIFY_`, `GTEST_MESSAGE_AT_`, `GTEST_FATAL_FAILURE_`, `GTEST_NONFATAL_FAILURE_`, and `GTEST_SUCCESS_` are low-level macro helpers for generated assertion code.
- `GoogleTestFailureException` is the exception type thrown when `throw_on_failure` is enabled and exceptions are available.
- `AppendUserMessage`, `EqFailure`, `GetBoolAssertionFailureMessage`, `DiffStrings`, and the `edit_distance` functions are declared diagnostic builders for assertion messages and unified string diffs.
- `FloatingPoint<RawType>` wraps `float`/`double` bit patterns and implements ULP-based comparison via `AlmostEquals()`. It exposes masks for sign, exponent, and fraction bits, handles NaN as never equal, and treats signed zero correctly through sign-and-magnitude to biased conversion.
- `TypeId`, `TypeIdHelper<T>`, `GetTypeId<T>()`, and `GetTestTypeId()` provide fixture identity checking by using the address of a per-template static `dummy_`.
- `TestFactoryBase` and `TestFactoryImpl<TestClass>` abstract construction of test objects for normal and parameterized registration.
- `MakeAndRegisterTestInfo()` is the central integration point that records test case name, test name, type/value parameters, source location, fixture type id, setup/teardown hooks, and a factory.
- `GTEST_TEST_` expands a user test into a generated subclass, static `TestInfo* const test_info_`, registration through `MakeAndRegisterTestInfo()`, and the `TestBody()` definition point.

### Type Traits, Containers, and Native Arrays

- `RemoveReference`, `RemoveConst`, and `GTEST_REMOVE_REFERENCE_AND_CONST_` normalize types for static checks and array wrappers.
- `ImplicitlyConvertible<From, To>` uses overload resolution and `sizeof` to compute implicit convertibility at compile time.
- `IsAProtocolMessage<T>` detects classic protobuf message pointers by implicit conversion to forward-declared `ProtocolMessage` or `proto2::Message`.
- `IsContainerTest`, `IsHashTable`, `HasValueType`, `IsRecursiveContainerImpl`, and `IsRecursiveContainer` identify STL-like containers while avoiding recursive container printing traps.
- `ArrayEq`, `ArrayAwareFind`, and `CopyArray` recursively compare/search/copy native arrays, including multidimensional arrays.
- `NativeArray<Element>` adapts native arrays to a read-only STL-like container. It can either reference the source (`RelationToSourceReference`) or deep-copy it (`RelationToSourceCopy`), and its destructor deletes only copied storage.

### Death Test APIs

- `DeathTest` is the abstract controller for `ASSERT_DEATH`, `EXPECT_DEATH`, `ASSERT_EXIT`, and `EXPECT_EXIT`. `Create()` chooses a concrete implementation based on death-test flags, `AssumeRole()` returns parent/child role, `Wait()` obtains child status, `Passed()` evaluates exit and stderr matching, and `Abort()` reports child-side failures.
- `DeathTest::ReturnSentinel` aborts a child death test if the tested statement returns normally out of a scope where it should terminate.
- `DeathTestFactory` and `DefaultDeathTestFactory` provide a factory seam for concrete death-test creation.
- `InternalRunDeathTestFlag` owns parsed `--gtest_internal_run_death_test` fields and closes `write_fd_` in its destructor.
- `GTEST_DEATH_TEST_` is the core macro: it creates a `DeathTest`, switches on `OVERSEE_TEST` versus `EXECUTE_TEST`, waits and validates in the parent, executes the statement under a sentinel in the child, and streams `DeathTest::LastMessage()` on failure.
- `GTEST_EXECUTE_DEATH_TEST_STATEMENT_` wraps death-test statements in exception handling when exceptions are enabled and aborts the death test if exceptions escape.
- `ASSERT_EXIT`, `EXPECT_EXIT`, `ASSERT_DEATH`, `EXPECT_DEATH`, `EXPECT_DEBUG_DEATH`, `ASSERT_DEBUG_DEATH`, `EXPECT_DEATH_IF_SUPPORTED`, and `ASSERT_DEATH_IF_SUPPORTED` are public-facing death-test macros in this slice.
- `ExitedWithCode` and, on supported non-Windows/non-Fuchsia platforms, `KilledBySignal` are predicate functors for exit status validation.

### linked_ptr

- `linked_ptr_internal` maintains a circular linked list of all smart pointers sharing an object. `join_new()` starts a one-element ring, `join()` inserts into another ring under global `g_linked_ptr_mutex`, and `depart()` removes from the ring and returns whether the departing pointer was last.
- `linked_ptr<T>` owns a raw pointer collectively with other `linked_ptr` copies. Destruction/reset/assignment call `depart()` and delete when the last ring member leaves. This is used where pre-C++11 shared ownership is needed without depending on `shared_ptr`.
- `make_linked_ptr()` is a convenience wrapper around `linked_ptr<T>(ptr)`.

### Universal Printers

- `internal2::PrintBytesInObjectTo()` and `TypeWithoutFormatter<T, TypeKind>` implement last-resort formatting for unknown types, protobuf messages, integer-convertible types, and Abseil string-view-convertible types.
- `testing_internal::DefaultPrintNonContainerTo()` uses ADL plus the internal fallback `operator<<` so user-defined `operator<<` wins when available.
- `FormatForComparison<ToPrint, OtherOperand>` and `FormatForComparisonFailureMessage()` specialize C string formatting: raw pointers by default, actual string content when compared against string types.
- `DefaultPrintTo()` selects container, pointer, function-pointer, or other formatting using the container and pointer traits.
- `PrintTo()` overloads cover characters, booleans, C strings, wide strings, `std::string`, optional global string/wstring types, Abseil string views, `nullptr_t`, tuples, pairs, and raw arrays.
- `UniversalPrinter<T>`, `UniversalPrinter<T[N]>`, and `UniversalPrinter<T&>` format values, arrays, and references. Reference printing includes the address; terse printers omit reference addresses and print char/wchar pointers as strings.
- `UniversalPrintArray()` truncates long arrays by printing the first and last chunks; char and wchar arrays have compact overloads.
- `TuplePolicy`, `TuplePrefixPrinter`, `PrintTupleTo()`, and `UniversalTersePrintTupleFieldsToStrings()` bridge both TR1 and standard tuples.
- `PrintToString<T>()` is the public wrapper that returns terse formatting through a `stringstream`.

### Parameterized Test Internals

- `TestParamInfo<ParamType>` carries a parameter value plus its numeric index into user param-name generators.
- `PrintToStringParamName` names parameters using `PrintToString(info.param)`.
- `ParamIteratorInterface<T>`, `ParamIterator<T>`, `ParamGeneratorInterface<T>`, and `ParamGenerator<T>` define the iterator/generator abstraction used by all parameter sources. `ParamGenerator` shares immutable implementations through `linked_ptr`.
- `RangeGenerator<T, IncrementT>` generates `[begin, end)` by repeated `operator+` and `operator<`, computing `end_index_` up front so iterator comparison uses indexes.
- `ValuesInIteratorRangeGenerator<T>` copies an input iterator range into a `std::vector<T>` so generated tests can outlive stack-allocated input containers. Its iterator caches dereferenced values to support `operator->()` even when iterator dereference returns a temporary.
- `DefaultParamName`, `GetParamNameGen`, and `ParamNameGenFunc` select the default index-based naming function or a user-provided name generator.
- `ParameterizedTestFactory<TestClass>` stores one parameter, sets it on `TestClass` before construction, and creates the actual test instance.
- `TestMetaFactoryBase` and `TestMetaFactory<TestCase>` create fresh owned factories for each parameterized test instance.
- `ParameterizedTestCaseInfoBase` and `ParameterizedTestCaseInfo<TestCase>` accumulate `TEST_P` patterns and `INSTANTIATE_TEST_CASE_P` generator declarations, then register every test/generator/parameter combination in `RegisterTests()`.
- `ParameterizedTestCaseRegistry` stores all parameterized test case descriptors, verifies that repeated test case names use the same fixture type, and calls `RegisterTests()` on every descriptor.
- Generated `ValueArray1` through the start of `ValueArray15` implement polymorphic `Values(v1, ..., vN)` support. Each stores constructor arguments by value and converts to `ParamGenerator<T>` by building a local `T array[]` with `static_cast<T>(vi_)` and returning `ValuesIn(array)`.

## Control Flow

Typed-test registration is compile-time recursion expressed as static runtime registration calls. Macro expansion creates namespace-scope booleans or static pointers whose initializers call `Register()`/`MakeAndRegisterTestInfo()`. `TypeParameterizedTestCase` walks the list of test templates, and for each test, `TypeParameterizedTest` walks the list of types. Each leaf calls `MakeAndRegisterTestInfo()` with a generated case name containing optional prefix, case name, and type-name suffix.

Normal `TEST`/`TEST_F` flow is simpler: `GTEST_TEST_` declares a generated fixture subclass and statically registers a `TestFactoryImpl` for it. At run time, Google Test later calls the factory to create and destroy the test object.

Assertion macros use an `if/else` pattern with `GTEST_AMBIGUOUS_ELSE_BLOCKER_` and generated labels to support streaming syntax and avoid dangling-else issues. Exception assertions execute the statement under `try/catch`; boolean assertions convert the expression to `AssertionResult`; no-fatal-failure assertions snapshot the current thread's fatal-failure state with `HasNewFatalFailureHelper`.

Death-test flow is split by role. The overseeing process creates a concrete `DeathTest`, assumes `OVERSEE_TEST`, waits for the child, applies the user exit predicate, and evaluates captured stderr against the regex. The executing child assumes `EXECUTE_TEST`, runs the statement under `ReturnSentinel`, and aborts with a specific reason if the statement returns, throws, or fails to die. Unsupported death-test macros compile the statement/regex in an unreachable branch and emit a warning instead of executing the statement.

Parameterized tests are registered later, when the unit-test implementation asks the registry to register tests. `ParameterizedTestCaseInfo::RegisterTests()` nests loops over stored test patterns, instantiations, and generated parameters. It validates parameter names for non-empty alphanumeric/underscore content, rejects duplicates within an instantiation, builds names as `test_base_name/param_name`, and calls `MakeAndRegisterTestInfo()` with `value_param = PrintToString(*param_it)`.

Universal printing uses overload resolution first. `UniversalPrinter<T>::Print()` calls `PrintTo(value, os)` unqualified so user `PrintTo()` overloads found by ADL can override internal defaults. The generic internal `PrintTo()` then dispatches to container/pointer/function-pointer/other paths. If no user stream operator or printer exists, fallback formatting chooses protobuf debug strings, integer conversion, Abseil string view conversion, or raw bytes.

## State and Persistence Behavior

Most state in this chunk is process-local registration metadata held in static or registry-owned structures, not persisted to disk. Static initialization registers tests and type information before `RUN_ALL_TESTS()`. `ParameterizedTestCaseRegistry` owns dynamically allocated `ParameterizedTestCaseInfoBase` objects until destruction. `ParameterizedTestCaseInfo` owns test meta-factories and records instantiations as strings, function pointers, file names, and lines.

Death-test state includes `DeathTest::last_death_test_message_`, the parsed `internal_run_death_test` flag, and file descriptors used for parent/child communication. `InternalRunDeathTestFlag` is RAII for its write fd. Death tests may re-execute the binary in "threadsafe" style, so state observed by the child can differ from the parent except for command-line flag propagation and explicit IPC.

`linked_ptr` persists ownership state as an intrusive circular list among smart-pointer instances and uses a single global mutex for operations on all rings. `NativeArray` either holds a borrowed pointer or an owned heap copy, encoded by its `clone_` member function pointer. `RangeGenerator` and `ValuesInIteratorRangeGenerator` hold immutable copied parameter data so generators can be safely reused after the original input expression goes out of scope.

Floating-point helpers store raw value bits in a union. Printers and formatters are stateless except for local `stringstream`/vector accumulation.

## Dependencies and Integration Points

This chunk depends on earlier fused-header definitions for portability macros, `TypesN`/`TemplateSel`/`NoneT`, `Message`, `AssertionResult`, `TestPartResult`, `Test`, `UnitTest`, `scoped_ptr`, mutex primitives, type traits such as `AddReference`, `IteratorTraits`, `bool_constant`, and platform feature macros such as `GTEST_HAS_DEATH_TEST`, `GTEST_HAS_TYPED_TEST`, `GTEST_HAS_TR1_TUPLE`, `GTEST_HAS_STD_TUPLE_`, and `GTEST_HAS_ABSL`.

It integrates with later and external implementation units through `GTEST_API_` declarations: assertion message builders, diff functions, stack trace capture, random number generation, HRESULT predicates, death-test concrete factories, public string/wide-string printers, and parameterized-test invalid-type reporting are declared here but implemented elsewhere in the fused source.

Public user integration points include `TEST`, `TEST_F`, typed-test macros, death-test macros, parameterized-test macros, `ValuesIn`, `Values`, `Range`, `PrintToString`, user-defined `PrintTo(const T&, ostream*)`, user-defined `operator<<`, and param name generator functors. The code also optionally integrates with protobuf, Abseil `optional`/`variant`/`string_view`, TR1 tuples, standard tuples, Windows HRESULTs, and POSIX signal status semantics.

## Risks and Edge Cases

- The generated arity limits are hard-coded: typed templates and `Values` support up to 50 parameters in this file family, while `Combine` is documented as limited to 10. Calls beyond those limits require generated code outside this slice or will fail to compile.
- Static initialization order matters because test registration happens through namespace-scope variables. This is normal for Google Test, but unusual build/linker behavior can affect registration, which is why `GetTestTypeId()` has a special exported path.
- `linked_ptr` has known caveats: cycles leak, converting raw pointers back into new `linked_ptr` instances can double-delete, and assignment traverses a ring under one global mutex. This is acceptable for test metadata but risky as a general-purpose smart pointer.
- Death tests are platform-sensitive. Fork/thread interactions can be unsafe with multiple active threads; "threadsafe" style relies on `argv[0]` being a usable path; unsupported platforms only warn; child-side side effects are generally not visible in the parent.
- `GTEST_DEATH_TEST_` uses `goto` labels generated from `__LINE__`; macro use patterns that place multiple generated labels on one source line can be fragile.
- Universal printing can instantiate surprising overloads. Container detection is heuristic, recursive containers are suppressed, input iterators may print with inferred element types, and unknown types fall back to raw bytes, which may expose padding or implementation-specific representations.
- C string formatting intentionally changes depending on the comparison operand type. This improves string comparison diagnostics but can surprise users comparing raw pointers.
- `RangeGenerator::CalculateEndIndex()` assumes positive progress toward `end`; invalid `step` values or unusual `operator+`/`operator<` behavior can cause long or infinite loops.
- Parameterized test names must be unique and contain only alphanumeric characters or underscores. `PrintToStringParamName` can generate invalid names for many value types unless the printed form is sanitized by the user.
- `Values(...)` generated arrays use `static_cast<T>` for each stored argument, so narrowing, explicit conversions, or non-copyable parameter types can fail at compile time.
- This chunk ends before the full generated `ValueArray15` body and later `ValueArrayN` classes, so the merge lane should combine with following chunks before making whole-file conclusions about complete `Values` support.

## Test Signals

Good coverage for this chunk would come from compiling and running Google Test's own typed-test, type-parameterized-test, death-test, printer, and parameterized-test suites. Specific signals include:

- Typed-test cases with one type, multiple types, custom type-name generators, missing/extra registered names, and fixture type mismatches.
- `TEST`/`TEST_F` registration checks verifying fixture setup/teardown hooks and duplicate fixture class detection.
- Floating-point assertions around NaN, infinities, signed zero, values within four ULPs, and values outside tolerance.
- Death tests for `ASSERT_EXIT`, `EXPECT_EXIT`, `ASSERT_DEATH`, debug death behavior under both `NDEBUG` and non-`NDEBUG`, exception escaping from a death statement, unsupported-platform fallback compilation, and exit-by-signal predicates where available.
- Universal printer tests for user `PrintTo`, user `operator<<`, protobuf-like objects, enums, containers, recursive containers, hash containers, native arrays, char/wchar pointers, null pointers, function pointers, tuples, pairs, Abseil optional/variant/string_view, and unknown byte-formatted objects.
- Parameterized tests using `Range`, `ValuesIn` from stack arrays and containers, generated values with temporary dereference behavior, custom valid and invalid parameter names, duplicate names, multiple instantiations, and mismatched fixture classes across namespaces.

## Cross-Chunk Notes

Earlier chunks define the beginning of the `TemplatesN` and `TypesN` generated lists, core port/type traits, `Message`, `AssertionResult`, `Test`, and other prerequisites. Later chunks continue the generated `ValueArrayN` series and likely define the public `Values`, `Range`, `Bool`, `Combine`, `TEST_P`, and `INSTANTIATE_TEST_CASE_P` macro surfaces that consume the internals introduced here. This chunk should be merged as a middle slice of a single fused `gtest.h` report, not treated as an independent standalone header.
