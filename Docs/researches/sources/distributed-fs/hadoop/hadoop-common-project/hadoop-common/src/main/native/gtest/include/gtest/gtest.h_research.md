# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/gtest/include/gtest/gtest.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007377`: lines 1-6478, `Docs/researches/chunks/subset-b-007377_research.md`
- `subset-b-007378`: lines 6479-12711, `Docs/researches/chunks/subset-b-007378_research.md`
- `subset-b-007379`: lines 12712-19024, `Docs/researches/chunks/subset-b-007379_research.md`
- `subset-b-007380`: lines 19025-21192, `Docs/researches/chunks/subset-b-007380_research.md`

## Chunk Research

### subset-b-007377: lines 1-6478

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/gtest/include/gtest/gtest.h lines 1-6478

## Chunk Scope

This chunk is the opening 1-6478 line slice of Hadoop's vendored, amalgamated Google Test header. The physical file is much larger; this range covers the outer `gtest/gtest.h` include guard and then inlines several Google Test internal headers: `gtest/internal/gtest-port.h`, `gtest/internal/gtest-port-arch.h`, `gtest/internal/custom/gtest-port.h`, the optional generated `gtest-tuple.h` fallback, `gtest-message.h`, `gtest-string.h`, `gtest-filepath.h`, and the beginning of generated `gtest-type-util.h`.

The chunk is mostly declarations, templates, macros, and portability shims rather than runtime implementation bodies. It defines the platform and feature detection layer that all later Google Test declarations depend on; a 10-element TR1 tuple fallback for older C++ libraries; message/string/path helper APIs; synchronization and thread-local abstractions; POSIX/Windows wrapper functions; and generated typed-test type/template-list machinery. It ends in the middle of `Templates31`, so later type-list/template-list utilities and the public `Test`, assertion, parameterized-test, and `RUN_ALL_TESTS` surfaces are outside this chunk.

## Purpose and Major Areas

The first purpose is to make a single vendored Google Test header portable across many compilers and operating systems used by Hadoop's native tests. The range detects operating systems (`GTEST_OS_LINUX`, `GTEST_OS_WINDOWS`, `GTEST_OS_MAC`, `GTEST_OS_CYGWIN`, `GTEST_OS_FREEBSD`, `GTEST_OS_QNX`, and others), compiler capabilities, C++11 language/library availability, exception support, RTTI, pthread support, regex support, death-test support, stream redirection, shared-library symbol visibility, and sanitizer attributes.

The second purpose is to provide low-level internal support APIs used by later Google Test code. This includes `testing::internal::scoped_ptr`, `RE`, `GTestLog`, `Mutex`, `MutexLock`, `ThreadLocal`, `Notification`, file and stream helpers, integer-size traits, environment parsing declarations, and safe casting helpers. These are implementation details but live in the public header because Google Test is heavily macro- and template-driven.

The third purpose is to expose early user-facing utilities that later assertions build on. `testing::Message` provides the assertion message stream buffer and normalizes problematic values such as null C string pointers and wide strings. `testing::Types<...>` begins the typed-test public API by mapping a user-written list of up to 50 types onto generated internal `TypesN` lists.

The fourth purpose is generated compatibility scaffolding. The chunk contains a generated fallback `std::tr1::tuple` implementation with arities 0-10 and generated typed-test helpers with arities up to 50. These sections avoid relying on variadic templates or modern tuple support, which was important for older compilers targeted by this vendored Google Test version.

## Important APIs, Types, and Macros

### Platform and Feature Detection

`gtest-port-arch.h` defines platform macros by inspecting compiler/OS predefines. Windows is subdivided into desktop, mobile, MinGW, phone, and WinRT; Apple may also define iOS; Linux may also define Android. These macros are intentionally either defined to 1 or absent, and downstream feature macros use them to choose includes and implementations.

`gtest-port.h` defines user-overridable feature knobs such as `GTEST_HAS_EXCEPTIONS`, `GTEST_HAS_RTTI`, `GTEST_HAS_PTHREAD`, `GTEST_HAS_POSIX_RE`, `GTEST_HAS_TR1_TUPLE`, `GTEST_USE_OWN_TR1_TUPLE`, `GTEST_LANG_CXX11`, `GTEST_HAS_STREAM_REDIRECTION`, `GTEST_LINKED_AS_SHARED_LIBRARY`, and `GTEST_CREATE_SHARED_LIBRARY`. It also derives public feature macros including `GTEST_HAS_DEATH_TEST`, `GTEST_HAS_PARAM_TEST`, `GTEST_HAS_TYPED_TEST`, `GTEST_HAS_TYPED_TEST_P`, `GTEST_HAS_COMBINE`, `GTEST_IS_THREADSAFE`, `GTEST_USES_POSIX_RE`, `GTEST_USES_SIMPLE_RE`, and `GTEST_CAN_COMPARE_NULL`.

Compiler and portability macros include `GTEST_GCC_VER_`, `GTEST_DISABLE_MSC_WARNINGS_PUSH_`, `GTEST_DISABLE_MSC_WARNINGS_POP_`, `GTEST_ATTRIBUTE_UNUSED_`, `GTEST_MUST_USE_RESULT_`, `GTEST_NO_INLINE_`, `GTEST_API_`, `GTEST_ATTRIBUTE_NO_SANITIZE_MEMORY_`, `GTEST_ATTRIBUTE_NO_SANITIZE_ADDRESS_`, `GTEST_ATTRIBUTE_NO_SANITIZE_THREAD_`, `GTEST_AMBIGUOUS_ELSE_BLOCKER_`, `GTEST_DISALLOW_ASSIGN_`, and `GTEST_DISALLOW_COPY_AND_ASSIGN_`.

### Tuple Compatibility

If the platform lacks a usable `std::tuple` or `std::tr1::tuple`, the generated fallback defines `std::tr1::tuple` for arities 0 through 10. It provides:

- `tuple<>` and `tuple<T0...T9>` specializations with field members `f0_` through `f9_`.
- `make_tuple` overloads from 0 to 10 arguments.
- `tuple_size`, `tuple_element`, and `get<k>()`.
- `operator==` and `operator!=` using recursive `SameSizeTuplePrefixComparator`.
- internal support templates `ByRef`, `AddRef`, `TupleElement`, and `Get<k>`.

If C++11 `std::tuple` is available, the header aliases `std::tuple`, `std::get`, `std::make_tuple`, `std::tuple_size`, and `std::tuple_element` into `std::tr1` and then imports the chosen tuple namespace into `testing`. This is a deliberate compatibility bridge for code expecting tuple names under `testing`.

### Internal Memory, Regex, Logging, and Casting

`testing::internal::scoped_ptr<T>` is a minimal owning pointer with `operator*`, `operator->`, `get`, `release`, `reset`, and `swap`. It is non-copyable and deletes the current object on reset/destruction after checking `T` is complete.

`testing::internal::RE` wraps regex matching. With POSIX regex support it owns `regex_t` members for full and partial matches; otherwise it stores simple-regex pattern state. It supports construction from `std::string`, optional global `::string`, and `const char*`, exposes `pattern()`, and declares `FullMatch` and `PartialMatch` overloads for strings and C strings.

`testing::internal::GTestLog` formats log messages by severity (`GTEST_INFO`, `GTEST_WARNING`, `GTEST_ERROR`, `GTEST_FATAL`) and writes through `std::cerr`; fatal logs abort in the implementation. `GTEST_LOG_` streams into this object, and `GTEST_CHECK_` is an always-on fatal assertion macro for internal invariants. `GTEST_CHECK_POSIX_SUCCESS_` is a fatal check specialized for POSIX-style zero-on-success return codes.

`ImplicitCast_`, `DownCast_`, and `CheckedDowncastToActualType` are internal casting helpers. `DownCast_` uses `dynamic_cast` under RTTI for debug validation and `static_cast` for the actual cast. `CheckedDowncastToActualType` can enforce exact dynamic type equality when RTTI is present, then selects `::down_cast`, `dynamic_cast`, or `static_cast` depending on platform support.

### Synchronization and Thread-Local Storage

The chunk defines portable synchronization types only when `GTEST_IS_THREADSAFE` is true. On pthread platforms, `Notification` uses a `pthread_mutex_t` plus a polling sleep loop, `ThreadWithParam<T>` wraps `pthread_create`/`pthread_join`, `MutexBase` and `Mutex` wrap `pthread_mutex_t`, `MutexLock` is an RAII lock, and `ThreadLocal<T>` uses `pthread_key_create`, `pthread_getspecific`, and `pthread_setspecific` with a destructor callback.

On Windows desktop platforms, the declarations avoid including `windows.h` by forward-declaring `_RTL_CRITICAL_SECTION` and treating `HANDLE` as `void*`. `AutoHandle`, `Notification`, `Mutex`, `ThreadLocalRegistry`, `ThreadWithParamBase`, `ThreadWithParam<T>`, and `ThreadLocal<T>` are declared for the Windows implementation in the `.cc` file. Static mutex macros are provided for both pthread and Windows implementations.

When threading is unavailable, dummy `Mutex`, `MutexLock`, and `ThreadLocal<T>` implementations compile but do not provide cross-thread protection. This preserves source compatibility on constrained platforms while clearly making concurrent Google Test use unsupported there.

### POSIX/Windows Wrappers and Utility Types

`testing::internal::posix` wraps common C/POSIX calls behind stable names: `FileNo`, `IsATTY`, `Stat`, `StrCaseCmp`, `StrDup`, `StrNCpy`, `ChDir`, `FOpen`, `FReopen`, `FDOpen`, `FClose`, `Read`, `Write`, `Close`, `StrError`, `GetEnv`, `RmDir`, `IsDir`, and `Abort`. Windows variants call `_fileno`, `_stat`, `_rmdir`, `_stricmp`, `_strdup`, and related functions where applicable; mobile Windows stubs out unavailable environment and filesystem APIs.

Integer support includes `BiggestInt`, `TypeWithSize<4>`, `TypeWithSize<8>`, `Int32`, `UInt32`, `Int64`, `UInt64`, and `TimeInMillis`. `kMaxBiggestInt` computes the maximum signed value without relying on `numeric_limits` support for non-standard integer types.

String and character helpers include `IsAlpha`, `IsAlNum`, `IsDigit`, `IsLower`, `IsSpace`, `IsUpper`, `IsXDigit`, `ToLower`, `ToUpper`, and `StripTrailingSpaces`. Each narrow-character predicate casts through `unsigned char` before calling C library functions, avoiding undefined behavior on negative signed `char` values.

Flag and environment declarations include `GTEST_FLAG(name)`, `GTEST_DECLARE_bool_`, `GTEST_DECLARE_int32_`, `GTEST_DECLARE_string_`, `GTEST_DEFINE_bool_`, `GTEST_DEFINE_int32_`, `GTEST_DEFINE_string_`, `ParseInt32`, `BoolFromGTestEnv`, `Int32FromGTestEnv`, and `StringFromGTestEnv`. The declarations are used later by command-line parsing and environment fallback logic.

### Message and String APIs

`testing::Message` is an assertion-message builder around an owned `std::stringstream`. It supports stream insertion for arbitrary streamable values, pointer-specific insertion that renders null pointers as `(null)`, `bool` insertion as `true`/`false`, basic narrow I/O manipulators, wide C strings, and wide strings when supported. `GetString()` returns the accumulated text, replacing embedded NUL bytes with visible `\\0` sequences.

The global `operator<<(const testing::internal::Secret&, int)` declaration exists to ensure there is at least one global `operator<<`; `Message::operator<<` then uses `using ::operator<<` so argument-dependent lookup can find user-defined global stream operators. `testing::internal::StreamableToString` builds on `Message` to produce string forms of arbitrary values.

`testing::internal::String` is a static utility class. This chunk declares cloning of C strings, null-safe C string and wide C string equality, UTF-8 rendering of wide C strings, case-insensitive comparisons, case-insensitive suffix checks, substring checks, and `ShowCStringQuoted`. On Windows CE it also declares ANSI/UTF-16 conversion helpers.

### FilePath API

`testing::internal::FilePath` wraps pathname manipulation for XML output and temporary files. It stores a normalized `std::string pathname_` and exposes immutable-style methods such as `GetCurrentDir`, `MakeFileName`, `ConcatPaths`, `GenerateUniqueFileName`, `RemoveTrailingPathSeparator`, `RemoveDirectoryName`, `RemoveFileName`, `RemoveExtension`, `CreateDirectoriesRecursively`, `CreateFolder`, `FileOrDirectoryExists`, `DirectoryExists`, `IsDirectory`, `IsRootDirectory`, and `IsAbsolutePath`.

Normalization collapses repeated path separators and, on Windows, converts alternate `/` separators to primary `\\`. The class treats a path ending in a separator as directory-intent metadata; many methods are string transformations and do not require the path to exist.

### Typed-Test Type Utilities

`testing::internal::GetTypeName<T>()` returns a human-readable type name. With RTTI it uses `typeid(T).name()` and optionally demangles through `abi::__cxa_demangle` or HP aCC demangling support; without RTTI it returns `"<type>"`.

When typed tests are enabled, `AssertTypeEq<T1,T2>` is defined only for identical types, supporting compile-time type equality checks. `internal::None` is a sentinel for missing variadic type arguments. Generated `Types0` through `Types50` form linked type lists with `Head` and `Tail`; public `testing::Types<T1,...,T50>` maps user-provided defaulted template arguments to the correct internal `TypesN` specialization.

The chunk then starts generated template-list support. `GTEST_TEMPLATE_` represents a single-parameter class template, `TemplateSel<Tmpl>` turns such a template into a type with a nested `Bind<T>::type`, `GTEST_BIND_` binds the selector to a concrete type, `NoneT<T>` is the sentinel for missing template-list entries, and `Templates0` through the beginning of `Templates31` build linked lists of template selectors. The chunk stops before `Templates31` is fully defined.

## Control Flow and Lifecycle

Most code in this span is selected at compile time. Preprocessor control flow first detects the OS, then chooses compiler/library features, then includes platform headers, then defines Google Test feature macros. Downstream code uses `#if GTEST_HAS_*` rather than `#ifdef` because many feature macros are always defined to either 0 or 1.

Tuple control flow is also compile-time. Google Test prefers C++11 `std::tuple` when both the language mode and standard library are good enough, otherwise tries TR1 tuple, and finally falls back to its own generated TR1 tuple. The fallback tuple's runtime behavior is simple value storage: constructors initialize fields, assignment calls `CopyFrom`, `get<k>` returns field references through generated accessor classes, and tuple equality recursively compares fields from left to right.

Regex matching flow is split by platform. POSIX-capable builds compile full and partial `regex_t` forms in `RE::Init`; matching calls use the selected regex backend. Windows and other non-POSIX builds use a simple regex implementation declared here and implemented elsewhere. Death tests, filtering, and assertion helpers later depend on these regex APIs.

Threading flow is platform-specific. Pthread `ThreadWithParam<T>` creates the native thread after all fields except `thread_` are initialized, optionally waits on a `Notification`, invokes the user function, and joins on destruction. Pthread `ThreadLocal<T>` lazily creates a per-thread `ValueHolder` using a factory, stores it under a pthread key, and relies on the pthread key destructor to delete per-thread holders when threads exit.

Message-building flow is stream based. Assertion macros later create a `Message`, stream diagnostic values into it, and pass its `GetString()` output into failure reporting. The pointer overload ensures null pointer output is stable across compilers; the global-operator lookup workaround allows user types with global stream operators to participate in assertion diagnostics.

Path flow is value-object style. `FilePath` constructors normalize the path string once; static factories compose new path strings; transformation methods return new `FilePath` objects; filesystem-observing methods such as `FileOrDirectoryExists`, `DirectoryExists`, `CreateFolder`, and `CreateDirectoriesRecursively` delegate to platform-specific stat/mkdir behavior in the implementation.

Typed-test flow is compile-time list construction. User-facing `Types<T1,...>` hides the generated `TypesN` internals; each specialization strips trailing `None` sentinel parameters and exposes a `type` alias to a compact linked list. Template lists apply the same idea to class templates via `TemplateSel` and `Bind`.

## State, Persistence, and Side Effects

Most state in this chunk is transient process memory or compile-time type state. The header declares no durable Hadoop filesystem state and no Hadoop-specific native state. Runtime state includes `Message` stringstream buffers, `RE` pattern strings and compiled regex objects, `scoped_ptr` ownership, mutex ownership metadata, thread-local value holders, `FilePath` pathname strings, and per-thread keys or Windows registry entries.

Persistent side effects are limited to testing support behavior declared here. Stream capture APIs (`CaptureStdout`, `GetCapturedStdout`, `CaptureStderr`, `GetCapturedStderr`) redirect process stdout/stderr when supported. `FilePath::CreateFolder` and `CreateDirectoriesRecursively` create directories. `posix::RmDir`, `ChDir`, file open/read/write/close wrappers, and `TempDir` declarations support file-system side effects used by Google Test internals and tests.

Thread-local persistence is intentionally scoped to thread lifetime. Pthread `ThreadLocal<T>` deletes the current thread's value in its destructor and deletes other threads' values on thread exit via pthread destructors. The comments warn that destroying a `ThreadLocal` before all threads using it have exited can leak or skip destruction on some platforms.

Static mutex state is link-time initialized where possible. Pthread static mutexes are POD `MutexBase` objects initialized with `PTHREAD_MUTEX_INITIALIZER`. Windows static mutexes rely on zero-initialized fields and lazy initialization. This matters because some Google Test global state may be touched before `main()`.

Configuration state comes from macros and environment. Feature macros are set by the build environment or by this header's auto-detection. Flag declarations later correspond to process-global `FLAGS_gtest_*` variables. Environment parsers read `GTEST_*` variables through `posix::GetEnv`.

Generated type-list state is entirely compile-time. `TypesN`, `Types<...>`, `TemplatesN`, and `TemplateSel` create types and aliases; they do not allocate, mutate, or persist runtime data.

## Dependencies and Integration Points

The chunk depends on standard C and C++ headers including `<limits>`, `<ostream>`, `<vector>`, `<ctype.h>`, `<stddef.h>`, `<stdlib.h>`, `<stdio.h>`, `<string.h>`, `<sys/types.h>`, `<sys/stat.h>`, `<algorithm>`, `<iostream>`, `<sstream>`, `<string>`, `<utility>`, `<iomanip>`, `<map>`, and `<set>`. It conditionally includes `<unistd.h>`, `<strings.h>`, `<regex.h>`, `<pthread.h>`, `<time.h>`, `<tuple>`, `<tr1/tuple>`, `<cxxabi.h>`, and platform-specific Apple, Android, Windows, Symbian, and HP headers.

Operating-system integration points include POSIX file descriptors, `stat`, directory removal, `chdir`, file I/O, environment variables, `abort`, pthread mutexes/keys/threads, `nanosleep`, Windows critical sections and handles, Windows path separators, Android API-level detection, and Apple target-condition macros.

Compiler and library integration is extensive. The header works around GCC version quirks, libstdc++ tuple and C++11 support, clang feature probes, MSVC warning pragmas and DLL import/export attributes, C++Builder exception behavior, Sun/IBM/HP/Symbian template quirks, and sanitizer attributes.

Google Test integration points are internal and forward-looking. Later declarations in the same physical header rely on `Message`, `String`, `FilePath`, `RE`, `Mutex`, `ThreadLocal`, `GTestLog`, `TypeWithSize`, tuple imports, typed-test type lists, and the feature macros defined here. Native Hadoop tests include this vendored header to build Google Test based C++ tests, including Hadoop native/gtest sources.

## Risks and Compatibility Notes

This vendored header is an upstream Google Test snapshot embedded in Hadoop. Local edits carry broad compatibility risk because the same header supplies both public macros and internal implementation declarations used by the companion Google Test source files. Even changes that seem internal can break test registration, assertion expansion, typed tests, parameterized tests, death tests, or compiler portability.

The chunk contains generated code from Pump templates (`gtest-tuple.h.pump`, `gtest-type-util.h.pump`). Manual changes to one arity but not others can introduce inconsistent template behavior. Regenerating with a different generator or upstream version can also produce large mechanical diffs that need careful review against the rest of the vendored Google Test implementation.

Feature detection is fragile. Incorrect `GTEST_HAS_PTHREAD`, `GTEST_HAS_RTTI`, `GTEST_HAS_EXCEPTIONS`, `GTEST_HAS_TR1_TUPLE`, or `GTEST_HAS_STD_TUPLE_` values can produce compile failures, link failures, or subtly disabled test features. Android, old libstdc++, QNX, Symbian, SunPro, HP aCC, and Windows mobile/RT branches are especially compatibility-sensitive.

The tuple compatibility layer intentionally defines or aliases entities inside `std::tr1` and sometimes bridges `std` into `std::tr1`. Although comments acknowledge this is undefined behavior in strict C++, it is relied upon for compatibility with older compilers. Replacing it with modern tuple-only code would break old toolchains unless the supported compiler matrix is changed.

Threading abstractions have lifetime hazards. Static mutex initialization must be valid before dynamic initialization. `ThreadLocal<T>` instances must outlive all threads that use them. Pthread error handling is fatal through `GTEST_CHECK_POSIX_SUCCESS_`, so unexpected system errors abort the process rather than reporting ordinary test failures.

`Message` diagnostic behavior is compatibility-sensitive. Assertion output depends on null pointer rendering, bool rendering, wide-string conversion, embedded-NUL escaping, and global operator lookup. Changes here affect many test failure messages and golden-output tests.

`FilePath::GenerateUniqueFileName` has a documented race if multiple processes choose filenames concurrently. Directory creation and normalization depend on platform-specific separator rules, root-directory syntax, current working directory behavior, and stat semantics.

The chunk ends mid-definition of `Templates31`; it is not a complete report for `gtest.h`. The merge lane should combine this with later chunks before drawing conclusions about the full public Google Test API in Hadoop.

## Test Signals

Compile matrix tests are the most important signal for this range. At minimum, build Hadoop native tests on the primary supported Linux compiler with and without C++11 mode assumptions, with pthreads enabled, and with the vendored Google Test source compiled against this header. A stricter matrix would also exercise clang, GCC/libstdc++ tuple variants, and any Windows or macOS support claimed by the build.

Feature detection tests should assert expected macro values on supported build targets: OS macro selection, pthread support, exception/RTTI detection, POSIX regex selection, death-test enablement, stream redirection, typed-test enablement, and tuple namespace selection.

Tuple tests should cover arities 0 through 10, construction, copy construction across convertible field types, assignment, pair construction for 2-tuples, `make_tuple`, `tuple_size`, `tuple_element`, mutable and const `get<k>`, equality, inequality, references, and compilation failure for invalid indexes where feasible.

Internal utility tests should cover `scoped_ptr` ownership transfer/reset/release, `ImplicitCast_`, `DownCast_` runtime checks under RTTI, `CheckedDowncastToActualType`, integer type sizes, `kMaxBiggestInt`, character helpers with negative signed-char inputs, `StripTrailingSpaces`, and `GTEST_SNPRINTF_` behavior.

Regex tests should cover full vs partial matches, invalid patterns, POSIX and simple-regex behavior on the active platform, empty strings, escaped characters, and death-test/filter regex patterns used elsewhere in Google Test.

Threading tests should cover `Mutex` lock/unlock/assert-held, `MutexLock` RAII behavior, static mutex use before `main` where possible, `Notification` wait/notify, `ThreadWithParam` join-on-destruction, `ThreadLocal` default and instance factories, per-thread independence, destructor behavior for current thread values, and no-thread fallback compilation when threading is disabled.

Message and string tests should cover streaming custom types with global `operator<<`, null pointers, C strings, bools, wide C strings, `std::wstring` where available, embedded NUL replacement, copy construction, `StreamableToString`, `String::CloneCString`, null-safe equality, case-insensitive comparison, suffix checks, substring checks, and quoted C string rendering.

FilePath tests should cover normalization of repeated separators, alternate Windows separators where supported, current directory retrieval, filename generation with and without numeric suffixes, unique-name generation when files exist, directory/file component removal, extension removal case-insensitivity, recursive directory creation, root and absolute path detection, and race-aware behavior under concurrent unique-name generation.

Typed-test utility tests should compile representative `Types<>`, `Types<T>`, `Types<T1,T2>`, and high-arity `Types<...>` lists, verify `Head`/`Tail` chains, check `AssertTypeEq` success/failure behavior, confirm `GetTypeName<T>()` demangling where supported, and compile template-list selector/binding examples through the covered `TemplatesN` arities.

### subset-b-007378: lines 6479-12711

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

### subset-b-007379: lines 12712-19024

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

### subset-b-007380: lines 19025-21192

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/gtest/include/gtest/gtest.h lines 19025-21192

## Purpose

This chunk is the public-facing tail of the bundled Google Test header. It defines the fixture/result/test metadata layer, event listener interfaces, `UnitTest` singleton facade, value-parameterized test fixture helpers, and the user macros that most C++ tests consume (`EXPECT_*`, `ASSERT_*`, `TEST`, `TEST_F`, `SCOPED_TRACE`, and `RUN_ALL_TESTS`). In Hadoop's native test tree this header is vendored test infrastructure, so changes here affect C++ test compilation and runtime reporting rather than Hadoop production filesystem logic.

## Important APIs, Types, and Macros

- `testing::Test` completes its fixture contract in this range: subclasses override `SetUp()`, `TearDown()`, and the generated private `TestBody()` supplied by `TEST`/`TEST_F`; `Run()` owns the fixture execution sequence; `DeleteSelf_()` deletes the fixture instance; `gtest_flag_saver_` preserves flag state per test; and the private `Setup()` sentinel intentionally catches misspelled `Setup()` overrides at compile time.
- `testing::TestProperty` is a copyable key/value pair used for XML output. `key()` and `value()` return `c_str()` pointers into owned `std::string` members, and `SetValue()` mutates the value in place.
- `testing::TestResult` owns a vector of `TestPartResult`, a vector of `TestProperty`, a death-test count, and elapsed time. Public readers expose result counts, pass/fail predicates, elapsed time, and indexed accessors. Private friends such as `TestInfo`, `TestCase`, `UnitTest`, death-test classes, and reporters mutate or clear state through `RecordProperty()`, `AddTestPartResult()`, `ClearTestPartResults()`, and `Clear()`. A mutex protects test property mutation.
- `testing::TestInfo` is immutable test metadata plus mutable per-run result state. It stores test case name, test name, optional type/value parameters, source location, fixture type id, filter/disabled flags, the factory used to instantiate the test, and a `TestResult`. The private constructor is reached through `internal::MakeAndRegisterTestInfo()`, which is how generated test registration hooks enter the `UnitTest` model.
- `testing::TestCase` groups `TestInfo` entries, owns them through `test_info_list_`, supports shuffle/unshuffle through `test_indices_`, stores case-level setup/teardown function pointers, tracks whether any contained test should run, and keeps an ad-hoc `TestResult` for properties recorded during `SetUpTestCase()` and `TearDownTestCase()`.
- `testing::Environment` is the global setup/teardown extension point. It uses virtual `SetUp()` and `TearDown()` instead of constructor/destructor work and repeats the private `Setup()` misspelling sentinel pattern.
- `testing::TestEventListener` is the event callback interface in execution order, from program start through iterations, environment setup/teardown, test case start/end, test start/end, assertion result, and program end. `EmptyTestEventListener` supplies no-op implementations for selective overrides.
- `testing::TestEventListeners` owns the listener list via an internal repeater, exposes `Append()` and `Release()`, and provides handles for the default console result printer and XML generator. Private setters replace/delete defaults and can suppress event forwarding.
- `testing::UnitTest` is the singleton facade. It exposes `GetInstance()`, `Run()`, current test/case accessors, random seed, counts for test cases/tests/disabled/reportable/runnable results, start and elapsed timing, overall pass/fail, indexed `TestCase` access, global ad-hoc result, and listener access. Private methods add environments, route assertion part results and properties to the active result scope, manage scoped traces, and access the opaque `internal::UnitTestImpl`.
- `testing::AddGlobalTestEnvironment()` is an inline convenience wrapper that transfers an `Environment*` into `UnitTest`.
- `testing::InitGoogleTest()` overloads parse and remove Google Test flags from narrow or Windows wide-character argv before `RUN_ALL_TESTS()`.
- Internal assertion helpers include `CmpHelperEQFailure()`, `CmpHelperEQ()`, `EqHelper` and its null-literal specialization, generated comparison helpers for `NE/LE/LT/GE/GT`, C-string and wide-string comparison helper declarations, substring predicate declarations, `CmpHelperFloatingPointEQ()`, `DoubleNearPredFormat()`, and `internal::AssertHelper` for streaming assertion messages.
- Parameterized-test support, under `GTEST_HAS_PARAM_TEST`, defines `WithParamInterface<T>` with static per-type `parameter_` storage and guarded `GetParam()`, plus `TestWithParam<T>` as `Test` plus `WithParamInterface<T>`.
- User macros define failure/success (`ADD_FAILURE`, `ADD_FAILURE_AT`, `FAIL`, `SUCCEED`), exception assertions, boolean assertions, generated predicate assertions up to arity 5, equality/ordering assertions, string assertions, floating-point assertions, Windows HRESULT assertions, no-fatal-failure assertions, `SCOPED_TRACE`, `GTEST_TEST`/`TEST`, `TEST_F`, and global `RUN_ALL_TESTS()`.

## Control Flow and Execution Model

The control path starts when `TEST` or `TEST_F` expands to `GTEST_TEST_`, which registers a factory and metadata through earlier internal machinery. `RUN_ALL_TESTS()` calls `UnitTest::GetInstance()->Run()`, and `UnitTestImpl` then traverses `TestCase` and `TestInfo` objects. Each `TestCase::Run()` wraps case-level setup/teardown, each `TestInfo::Run()` creates the fixture from its factory, and `Test::Run()` calls fixture setup, generated `TestBody()`, and teardown before `DeleteSelf_()` destroys the instance.

Assertions route through macros to helper functions returning `AssertionResult`. Success paths usually reduce to `AssertionSuccess()`. Failure paths build rich messages with expression text and formatted values, then invoke fatal or nonfatal failure handlers. Those handlers eventually call `UnitTest::AddTestPartResult()`, which records into the current `TestResult` and broadcasts `OnTestPartResult()` through listeners. `ASSERT_*` variants use fatal handlers to abort the current test function, while `EXPECT_*` variants continue after recording a nonfatal failure.

Result/property routing depends on current execution context. Properties recorded inside a test go to that test's `TestResult`; properties from case setup/teardown go to the `TestCase` ad-hoc result; properties outside cases go to `UnitTest`'s ad-hoc result. Listener callbacks bracket the same lifecycle: program start, iteration start, environment setup, case/test execution, environment teardown, iteration end, and program end.

## State and Persistence Behavior

Runtime state is in memory. `UnitTest` is a process singleton that is intentionally never deleted. `TestCase` owns its `TestInfo*` list, `TestInfo` owns a factory pointer and reusable mutable `TestResult`, and `TestResult` owns assertion part results, properties, death-test count, and timing. `TestEventListeners` owns appended listeners unless users `Release()` them. `AddGlobalTestEnvironment()` transfers environment ownership to `UnitTest`.

Persistent output is indirect: this chunk defines the data and listener/reporting hooks that default printers and XML generators consume, but it does not itself write files. XML-visible persistence surfaces include `TestProperty`, per-test and case/global ad-hoc results, reportable/disabled counts, source locations, value/type parameters, elapsed time, and listener-generated output.

Thread-safety is selective. `UnitTest` documents thread safety only when methods are called according to contract and protects mutable `impl_` state with `mutex_`. `TestResult` protects property vector/value mutation with `test_properites_mutex_`. `WithParamInterface<T>::parameter_` is static per parameter type and is valid only for the current parameterized test lifetime.

## Dependencies and Integration Points

This chunk depends heavily on internal Google Test infrastructure declared earlier in the amalgamated header: `internal::scoped_ptr`, `GTEST_FLAG_SAVER_`, `internal::TimeInMillis`, `TestPartResult`, `internal::Mutex`, `internal::CodeLocation`, `internal::TypeId`, `internal::TestFactoryBase`, `internal::UnitTestImpl`, `internal::Random`, `internal::ParameterizedTestCaseRegistry`, `internal::TestEventRepeater`, `AssertionResult`, `AssertionSuccess()`, `AssertionFailure()`, `EqFailure()`, formatting helpers, floating-point helpers, trace helpers, and assertion backend macros such as `GTEST_FATAL_FAILURE_`.

Integration with user test code is macro-driven. Test authors include this header, declare fixtures derived from `testing::Test`, write `TEST`/`TEST_F`/parameterized tests, call assertion macros, optionally register environments/listeners, call `InitGoogleTest()`, and then invoke `RUN_ALL_TESTS()`. Integration with Hadoop's native tests is therefore at compile/link time through the vendored gtest library and at runtime through test binaries' process-wide `UnitTest` singleton.

Platform integration is guarded by compile-time flags: `GTEST_HAS_PARAM_TEST` controls parameterized fixture helpers, `GTEST_HAS_STD_WSTRING` controls wide string substring overloads, `GTEST_OS_WINDOWS` exposes HRESULT assertions, and `GTEST_DONT_DEFINE_*` flags allow users to suppress globally common macro names that may conflict with other libraries.

## Risks and Edge Cases

- Macro names are global and broad (`TEST`, `FAIL`, `SUCCEED`, many `ASSERT_*` names). The `GTEST_DONT_DEFINE_*` escape hatches reduce but do not remove collision risk in C++ test binaries.
- Assertion macro argument evaluation order is explicitly undefined for binary comparisons, though each argument is evaluated once. Tests with side effects in assertion operands can still be order-sensitive.
- `EXPECT_EQ` on C strings compares pointers, not string contents. The header documents `EXPECT_STREQ`/`ASSERT_STREQ` as the correct content comparison path.
- `EqHelper<true>` has delicate overload resolution for null literals and pointers. Changes here risk compiler warnings or wrong overload selection on older GCC/MSVC configurations.
- `WithParamInterface<T>::parameter_` is static and guarded only by lifecycle contract. Calling `GetParam()` outside a parameterized test fails a runtime check, and concurrent parameterized tests with the same parameter type would be unsafe if the framework tried to run them simultaneously.
- Listener and environment ownership is manual pointer ownership. Releasing a listener transfers deletion responsibility to the caller; adding environments or listeners transfers ownership to Google Test.
- `TestResult::GetTestPartResult()` comments say the valid range is based on total part count, but the visible comment says `test_property_count()` for part results. That looks like a documentation defect in this vendored snapshot and can mislead maintainers.
- The field name `test_properites_mutex_` is misspelled in the source. This is ABI/source-visible only internally but should not be casually renamed in a vendored library snapshot.
- `RUN_ALL_TESTS()` and `UnitTest::Run()` must be called from the main thread after `InitGoogleTest()`. Misordering affects flag parsing, environment registration, and listener configuration.

## Test Signals

Behavior covered by this chunk is best validated by compiling and running representative native gtest binaries rather than by unit testing this header directly. Useful signals include:

- Fixtures using `TEST`, `TEST_F`, `SetUp()`, `TearDown()`, case-level setup/teardown, and deliberate `Setup()` misspellings to verify compile-time diagnostics.
- Assertions for boolean, equality/order, string, substring predicate-format, floating-point, exception, no-fatal-failure, and Windows HRESULT paths where applicable, checking both fatal/nonfatal behavior and streamed failure messages.
- Result counting tests that inspect `UnitTest`, `TestCase`, `TestInfo`, and `TestResult` counts for successful, failed, disabled, reportable, and filtered tests.
- XML/property tests that call `RecordProperty()` from inside a test, from setup/teardown, and outside tests to confirm routing to testcase, testsuite, and testsuites scopes.
- Listener tests that append/release custom `TestEventListener` instances and assert callback order for repeated runs, environment setup/teardown, test case/test start/end, and assertion part reporting.
- Parameterized tests using `TestWithParam<T>`, `GetParam()`, and a misuse case such as `TEST_F` instead of `TEST_P` to verify the guard message.

## Chunk Boundary Notes

This chunk begins inside the `testing::Test` declaration, so earlier fixture constructors, public failure query APIs, and `RecordProperty()` overload comments are outside the requested range. Many bodies for exported methods are declarations here and are implemented elsewhere in the amalgamated gtest source/header. The merge lane should combine this report with earlier chunks for full coverage of `gtest.h` setup, internal macro definitions, and registration machinery.
