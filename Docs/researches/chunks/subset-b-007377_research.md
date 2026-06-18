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
