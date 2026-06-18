# sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/gtest.h lines 1-6519

## Scope And Purpose

This chunk is the opening portion of RocksDB's vendored, fused Google Test 1.8.1 public header. It begins with the public `gtest/gtest.h` include guard, but because this is a fused distribution it immediately inlines several normally separate Google Test internal headers: `gtest/internal/gtest-port.h`, `gtest/internal/gtest-port-arch.h`, `gtest/internal/custom/gtest-port.h`, the optional generated tuple fallback, `gtest-message.h`, `gtest-string.h`, `gtest-filepath.h`, and the beginning of the generated `gtest-type-util.h`.

The chunk's main job is to make the rest of Google Test portable and self-contained. It detects operating systems, compilers, C++ language/library capabilities, regular-expression support, RTTI, exceptions, pthreads, death-test support, typed-test support, tuple implementations, stream redirection, DLL visibility, sanitizer attributes, and filesystem path conventions. It also declares the internal utility types that later public assertions, death tests, typed tests, XML output, and test registration code build on.

This is mostly infrastructure and declarations rather than executable test logic. The code exists so RocksDB's C++ tests can include a single vendored header without relying on a system Google Test installation. The chunk ends mid-way through the generated type-template list machinery, at the start of the `Templates24` declaration; later chunks continue the generated type utilities and the public Google Test API.

## Fused Header Layout

The file preserves the original Google Test header boundaries with their own include guards. Important boundaries in this chunk are:

- `GTEST_INCLUDE_GTEST_GTEST_H_`: outer public header guard.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_INTERNAL_H_`: internal declarations later used by the public API.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_PORT_H_`: the core portability layer.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_PORT_ARCH_H_`: platform macro detection.
- `GTEST_INCLUDE_GTEST_INTERNAL_CUSTOM_GTEST_PORT_H_`: empty customization injection point in this fused copy.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_TUPLE_H_`: generated in-header TR1 tuple fallback when the platform cannot provide one.
- `GTEST_INCLUDE_GTEST_GTEST_MESSAGE_H_`: declaration of the stream-accumulating `testing::Message`.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_STRING_H_`: internal string utilities.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_FILEPATH_H_`: internal filesystem path helper.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_TYPE_UTIL_H_`: generated typed-test support, started here and continued after this chunk.

Because the header is fused, comments saying "include this header" or "do not include separately" refer to the original upstream layout, not separate files in this vendored tree.

## Platform And Feature Detection

The portability layer defines `GTEST_OS_*` macros from compiler/platform predefined macros. Covered targets include Cygwin, Symbian, Windows desktop/mobile/phone/RT/MinGW, macOS/iOS, FreeBSD, Fuchsia, Linux/Android, z/OS, Solaris, AIX, HP-UX, Native Client, NetBSD, OpenBSD, and QNX. These macros drive most later conditional code.

Compiler and standard-library capability detection includes:

- `GTEST_GCC_VER_` for GCC-style version checks.
- `GTEST_LANG_CXX11` and `GTEST_STDLIB_CXX11` to distinguish language mode from standard-library feature availability.
- `GTEST_HAS_STD_BEGIN_AND_END_`, `GTEST_HAS_STD_FORWARD_LIST_`, `GTEST_HAS_STD_FUNCTION_`, `GTEST_HAS_STD_INITIALIZER_LIST_`, `GTEST_HAS_STD_MOVE_`, `GTEST_HAS_STD_UNIQUE_PTR_`, `GTEST_HAS_STD_SHARED_PTR_`, `GTEST_HAS_UNORDERED_MAP_`, and `GTEST_HAS_UNORDERED_SET_`.
- `GTEST_HAS_STD_TUPLE_`, `GTEST_HAS_TR1_TUPLE`, and `GTEST_USE_OWN_TR1_TUPLE`, which decide whether `std::tuple`, `std::tr1::tuple`, or Google Test's generated tuple fallback is used.
- `GTEST_HAS_EXCEPTIONS`, `GTEST_HAS_RTTI`, `GTEST_HAS_PTHREAD`, `GTEST_HAS_POSIX_RE`, `GTEST_USES_POSIX_RE`, `GTEST_USES_SIMPLE_RE`, `GTEST_HAS_CLONE`, `GTEST_HAS_STREAM_REDIRECTION`, `GTEST_HAS_DEATH_TEST`, `GTEST_HAS_TYPED_TEST`, `GTEST_HAS_TYPED_TEST_P`, and `GTEST_HAS_COMBINE`.
- `GTEST_HAS_CXXABI_H_` for demangling type names on libstdc++/libc++ platforms.
- `GTEST_HAS_SEH` and `GTEST_IS_THREADSAFE` for Windows structured exception handling and synchronization availability.

The detection code intentionally makes every user-tweakable capability macro resolve to `1` or `0` after inclusion. Users and build scripts can override the user-facing `GTEST_HAS_*` knobs before including the header, but the `GTEST_OS_*` platform macros are meant to be owned by Google Test.

## Export, Attribute, And Utility Macros

This chunk defines many internal macros used throughout the rest of the fused header and implementation:

- `GTEST_API_` controls DLL import/export on MSVC and default symbol visibility on GCC/Clang.
- `GTEST_DISABLE_MSC_WARNINGS_PUSH_`, `GTEST_DISABLE_MSC_WARNINGS_POP_`, `GTEST_DISABLE_MSC_DEPRECATED_PUSH_`, and `GTEST_DISABLE_MSC_DEPRECATED_POP_` wrap compiler warning suppression.
- `GTEST_ATTRIBUTE_UNUSED_`, `GTEST_ATTRIBUTE_PRINTF_`, `GTEST_MUST_USE_RESULT_`, `GTEST_NO_INLINE_`, and sanitizer suppression attributes annotate declarations portably.
- `GTEST_DISALLOW_ASSIGN_` and `GTEST_DISALLOW_COPY_AND_ASSIGN_` disable copying in pre-C++11 style, using `= delete` when available.
- `GTEST_AMBIGUOUS_ELSE_BLOCKER_` supports assertion macros in nested `if` statements.
- `GTEST_CHECK_` and `GTEST_CHECK_POSIX_SUCCESS_` provide internal fatal checks used by synchronization and runtime helpers.
- `GTEST_FLAG`, `GTEST_DECLARE_bool_`, `GTEST_DECLARE_int32_`, `GTEST_DECLARE_string_`, `GTEST_DEFINE_bool_`, `GTEST_DEFINE_int32_`, and `GTEST_DEFINE_string_` declare and define Google Test flags.
- `GTEST_SNPRINTF_`, `GTEST_PATH_SEP_`, and `GTEST_HAS_ALT_PATH_SEP_` abstract standard-library and filesystem differences.

These macros are the compile-time control plane for the rest of Google Test. Changes here have broad impact because public assertion macros, typed-test macros, death tests, XML output, and flag parsing depend on them.

## Tuple And Type-List Support

If the platform has usable `std::tuple`, the chunk imports tuple symbols from `std`. If TR1 tuple is available but `std::tuple` is not, it imports from `std::tr1`. If neither path is reliable, Google Test's generated fallback implementation is compiled under `namespace std { namespace tr1 { ... } }`.

The fallback tuple implementation supports arities 0 through 10. It defines:

- `tuple<>` and `tuple<T0, ..., T9>` storage classes with fields `f0_` through `f9_`.
- `make_tuple()` overloads for arities 0 through 10.
- `tuple_size` and `tuple_element`.
- `get<k>()` through `gtest_internal::Get<k>`.
- Equality and inequality through recursive `SameSizeTuplePrefixComparator`.
- Helper traits such as `ByRef`, `AddRef`, and `TupleElement`.

The tuple implementation is intentionally limited to what Google Test needs for parameterized and typed tests. It only implements `==` and `!=`, not the full TR1 relational-operator set. It also has compiler-specific escapes for Symbian, old Sun Studio, old GCC without RTTI, MSVC TR1 behavior, and Boost TR1 interactions on Symbian.

The generated `gtest-type-util.h` section begins at line 4613. In this chunk it defines:

- `CanonicalizeForStdLibVersioning()`, which normalizes names like `std::__1::vector` to reduce type-name noise across standard-library versions.
- `GetTypeName<T>()`, which uses RTTI plus `abi::__cxa_demangle` or HP aCC demangling when available, otherwise returns the raw `typeid` name or `"<type>"` when RTTI is disabled.
- `AssertTypeEq<T1, T2>` for compile-time type equality.
- `None`, `Types0`, and generated `Types1` through `Types50`, each represented as a cons-style list with `Head` and `Tail`.
- The public `Types<T1, ..., T50>` facade and partial specializations that translate trailing `None` defaults to the shorter internal `TypesN`.
- The start of template-list support: `TemplateSel`, `GTEST_BIND_`, `NoneT`, `Templates0`, and `Templates1` through the beginning of `Templates24`.

The generated sections are large and repetitive by design. They simulate variadic templates and template-template parameter lists for C++03-era compilers while keeping typed-test compiler diagnostics more readable.

## Important APIs, Types, And Functions

Key internal APIs and declarations introduced in this chunk include:

- `testing::Message`: a small stream accumulator used for assertion failure messages. It stores a `std::stringstream`, handles null pointers consistently, streams bools as `true`/`false`, supports narrow stream manipulators, and declares UTF-8 conversions for wide strings.
- `testing::internal::StreamableToString()`: converts a streamable value to a string via `Message`, preserving Google Test's null-pointer and embedded-NUL conventions.
- `testing::internal::RE`: a regular-expression wrapper over POSIX regex, PCRE when injected, or Google Test's simple regex engine. It exposes `FullMatch()` and `PartialMatch()` overloads for C strings and standard/global strings.
- `testing::internal::String`: static string utilities for C-string cloning, null-safe comparisons, wide-string display, case-insensitive comparisons, suffix checks, and numeric formatting.
- `testing::internal::StringStreamToString()`: extracts stream text while escaping embedded NUL characters.
- `testing::internal::FilePath`: a normalized path value object used by XML output and output-file naming. It handles current directory discovery, filename construction, path concatenation, unique-name generation, path component removal, extension stripping, recursive directory creation, existence checks, root checks, absolute-path checks, and platform path separators.
- `testing::internal::GTestLog`: RAII logging object used by `GTEST_LOG_`; fatal severity aborts in its destructor.
- `testing::internal::Mutex`, `MutexBase`, `MutexLock`, `Notification`, `ThreadWithParam`, `ThreadLocal`, and related thread-local value-holder classes: platform-specific synchronization and helper-thread primitives for death tests and Google Test's own internal concurrency.
- `testing::internal::AutoHandle`: Windows handle ownership wrapper used when Windows threading/death-test support is active.
- `testing::internal::TypeWithSize`, `Int32`, `UInt32`, `Int64`, `UInt64`, `TimeInMillis`, `BiggestInt`, and `kMaxBiggestInt`: fixed-size integer abstractions used by flags and later floating-point comparison code.
- `testing::internal::ImplicitCast_`, `DownCast_`, and `CheckedDowncastToActualType`: controlled cast helpers, with RTTI-backed validation when available.
- `testing::internal::bool_constant`, `true_type`, `false_type`, `is_same`, `is_pointer`, and `IteratorTraits`: small type traits used by message streaming, typed tests, and template utilities.
- `testing::internal::posix`: wrappers for `stat`, `isatty`, string comparison/duplication, directory removal, file descriptor operations, `fopen`, `freopen`, `fdopen`, `read`, `write`, `close`, `strerror`, `getenv`, and `abort`, with Windows and mobile variants hidden behind one namespace.
- Flag/environment declarations: `ParseInt32`, `BoolFromGTestEnv`, `Int32FromGTestEnv`, `OutputFlagAlsoCheckEnvVar`, and `StringFromGTestEnv`.
- Stream-capture declarations: `CaptureStdout`, `GetCapturedStdout`, `CaptureStderr`, and `GetCapturedStderr` when stream redirection is available.
- Death-test argv declarations: `GetInjectableArgvs`, `SetInjectableArgvs`, and `ClearInjectableArgvs` when death tests are available.

RocksDB has a local modification in this chunk: `testing::internal::scoped_ptr<T>` is changed to an alias of `std::unique_ptr<T>` to avoid clang-analyzer false reports, with the original partial `scoped_ptr` implementation left commented out. This means this vendored header assumes `std::unique_ptr` is available in RocksDB's build mode even though upstream Google Test 1.8.1 still carried C++03-era fallback code.

## Control Flow

Most control flow in this chunk is preprocessor-driven. Inclusion starts by setting platform and feature macros, then conditionally includes system headers, selects tuple support, selects regex support, and chooses synchronization implementations.

Runtime control flow is concentrated in small RAII and wrapper classes:

- `GTestLog` formats a log prefix on construction and flushes or aborts on destruction for fatal checks.
- `GTEST_CHECK_` evaluates a condition through `IsTrue`; on failure it constructs a fatal `GTestLog` stream and aborts at the end of the temporary object's lifetime.
- `RE` stores compiled regex state or simple-regex patterns and routes `FullMatch`/`PartialMatch` through implementation selected at compile time.
- `Message::operator<<` routes pointer types to a null-safe overload and non-pointer values through normal stream insertion plus argument-dependent lookup.
- `Notification` on pthread platforms spins with a mutex-protected `notified_` flag and short sleeps until `Notify()` is called. Windows uses an event handle through `AutoHandle`.
- `ThreadWithParam` constructs a native thread only after member initialization, waits on an optional `Notification`, calls the user-supplied function, and joins in `Join()` or the destructor.
- `MutexLock` locks in its constructor and unlocks in its destructor.
- `ThreadLocal<T>` lazily creates per-thread `ValueHolder<T>` instances. On pthreads it uses `pthread_key_create`, `pthread_getspecific`, and `pthread_setspecific`; on Windows it delegates to `ThreadLocalRegistry`; without thread support it collapses to a single stored value.
- `FilePath` constructors normalize paths immediately, while path-manipulation methods return new `FilePath` values or filesystem status booleans.
- `GetTypeName<T>()` branches on RTTI and demangling support to produce the best available human-readable type name.

Several declarations in this chunk are implemented later in the fused source, not here. This includes most non-inline methods for `RE`, `Message`, `String`, `FilePath`, Windows synchronization, stream capture, flag parsing, and environment parsing.

## State And Persistence Behavior

There is no application-level persistence in this chunk. The state is internal test-framework state, mostly scoped to a process and often scoped to an object lifetime:

- Preprocessor macros persist for the translation unit after inclusion and determine all later Google Test API availability.
- `Message` owns a heap-allocated `std::stringstream` through RocksDB's `scoped_ptr` alias and snapshots another `Message` by copying its rendered string.
- `RE` owns the copied pattern text plus compiled POSIX regex objects or simple-regex pattern state, depending on the selected backend.
- `GTestLog` stores only severity for its destructor behavior.
- `MutexBase` stores `pthread_mutex_t`, owner tracking, and `has_owner_`; static mutexes are link-time initialized.
- Windows `Mutex` stores owner thread ID, initialization phase, and a lazily initialized critical-section pointer.
- `Notification` stores a pthread mutex plus boolean flag on pthread platforms or an event handle on Windows.
- `ThreadLocal<T>` stores either a `pthread_key_t`, a Windows registry association, or a single fallback value. The comments explicitly warn that thread-local values on other threads may not be destroyed if the `ThreadLocal` object is destroyed while those threads are still alive.
- `FilePath` stores only its normalized `pathname_` string. Its methods may inspect or create filesystem directories but do not cache filesystem state.
- Death-test injectable argv declarations imply process-global argument state in later implementation code.
- Google Test flags declared through macros are process-global variables named with the `FLAGS_gtest_` prefix.

The only filesystem mutations declared in this chunk are `FilePath::CreateDirectoriesRecursively()` and `FilePath::CreateFolder()`, whose implementations are later. `GenerateUniqueFileName()` is explicitly documented as race-prone if multiple processes call it concurrently.

## Dependencies And Integration Points

This chunk integrates with several layers:

- C and C++ standard library headers: `stddef.h`, `stdlib.h`, `stdio.h`, `string.h`, `ctype.h`, `float.h`, `limits`, `memory`, `ostream`, `iostream`, `sstream`, `string`, `vector`, `algorithm`, `utility`, `map`, and `set`.
- POSIX APIs on Unix-like platforms: `unistd.h`, `strings.h`, `sys/types.h`, `sys/stat.h`, `pthread.h`, `time.h`, `regex.h`, `read`, `write`, `close`, `stat`, `rmdir`, `chdir`, `fileno`, and `nanosleep`.
- Windows C runtime and OS abstractions: `direct.h`, `io.h`, `_stat`, `_isatty`, `_stricmp`, `_strdup`, `_fileno`, `_rmdir`, `_snprintf_s`, `CRITICAL_SECTION` forward declarations, Windows family detection, and Windows handle/event abstractions without directly including `windows.h`.
- Apple and Android platform headers: `AvailabilityMacros.h`, `TargetConditionals.h`, and `android/api-level.h`.
- ABI demangling: `cxxabi.h` or HP aCC demangling headers when available.
- Boost TR1 tuple interactions on Symbian.
- Later Google Test fused implementation sections that define the declared methods and consume these macros and types.
- RocksDB's test build as a vendored third-party dependency. RocksDB test code normally includes this through Google Test headers rather than calling these internal APIs directly.

The public integration surface exposed by this chunk is still small: `testing::Message`, `testing::tuple`/`make_tuple`/`Types` when enabled, and flag/macros that public Google Test headers later use. Most symbols live in `testing::internal` and are documented as unstable implementation details.

## Risks And Edge Cases

This chunk is high risk because it sits below every Google Test assertion and registration macro:

- Feature-detection mistakes can silently disable death tests, typed tests, tuple support, stream capture, pthreads, or regex support on a platform.
- The RocksDB `scoped_ptr` alias to `std::unique_ptr` narrows compatibility compared with upstream's original C++03-friendly `scoped_ptr`. Builds that try to compile this vendored header without a usable C++11 `std::unique_ptr` will fail.
- The fallback tuple implementation defines symbols inside `std::tr1`; the code comments acknowledge this is only acceptable because it is acting like a standard-library vendor. It is a compatibility hack, not a pattern to extend casually.
- `GTEST_CHECK_POSIX_SUCCESS_` aborts on pthread and POSIX errors, so synchronization failures are process-fatal rather than reported as normal test failures.
- `Notification::WaitForNotification()` on pthreads polls every 10 ms instead of using a condition variable. It is simple but can delay tests or spin under scheduler stress.
- Thread-local lifetime rules are subtle. Destroying a `ThreadLocal` while other threads still have values can leak or leave platform-specific cleanup gaps.
- `DownCast_` and `CheckedDowncastToActualType` rely on RTTI only when enabled; without RTTI they fall back to static casts.
- `Message` null-pointer handling avoids undefined stream behavior, but custom `operator<<` lookup depends on ADL and the global `operator<<` declaration for `Secret`.
- Wide-string case-insensitive comparisons are locale-sensitive and explicitly differ across Windows, GNU, and macOS.
- `FilePath` normalization only collapses repeated separators and maps alternate separators on Windows. It intentionally does not resolve `.` or `..`, validate illegal characters, or guarantee that paths exist.
- `FilePath::GenerateUniqueFileName()` can race across processes because existence checking and creation are separate.
- `GetTypeName<T>()` depends on RTTI, ABI demangling availability, and standard-library inline namespace normalization. Type names can still vary across toolchains.
- The generated `Types` and `Templates` sections cap type-parameter lists at 50 entries. Tests exceeding that generated limit cannot be represented by this version's typed-test machinery.
- Because this is a fused vendored header, hand edits must preserve upstream-generated boundaries, include guards, and conditional compilation balance. A small preprocessor imbalance can break all RocksDB C++ tests.

## Test Signals

The most relevant validation signals for this chunk are compile-time and Google Test self-test style checks:

- RocksDB C++ test targets including this header should compile on the supported compiler matrix, proving the platform macros, headers, `std::unique_ptr`-based `scoped_ptr`, tuple selection, and synchronization declarations are compatible.
- Tests using ordinary assertions should render `testing::Message` output correctly, including bools, null pointers, wide strings, embedded NUL escaping, and types with stream operators found by ADL.
- Regex-dependent Google Test filters and death-test expectations should pass on POSIX-regex and simple-regex platforms.
- Typed and type-parameterized tests should compile and report readable type names through `GetTypeName<T>()`, `Types<>`, and the generated type-list machinery.
- Death-test builds should validate `GTEST_HAS_DEATH_TEST`, injectable argv handling, clone/Windows process support, and stream capture declarations on platforms where those features are enabled.
- Threaded Google Test internals should pass under pthread and Windows builds, especially mutex ownership checks, `ThreadWithParam`, `Notification`, and `ThreadLocal` cleanup.
- XML-output and output-file tests should exercise `FilePath` path joining, normalization, extension removal, unique-name generation, directory creation, and platform separators.
- Flag parsing tests should exercise `ParseInt32`, `BoolFromGTestEnv`, `Int32FromGTestEnv`, `StringFromGTestEnv`, and the `GTEST_FLAG` declaration/definition macros.
- Cross-platform builds are the strongest signal because much of the chunk is conditional. Linux-only success does not cover Windows, mobile Windows exclusions, Android API-level gates, Symbian/Sun/IBM compatibility paths, or the no-pthread fallback.
