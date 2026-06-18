# Research: subset-b-009675

Grouped research for vendored Acutest and Boost.Config/Assert headers under `sources/user-network-fs/mergerfs`. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/acutest/acutest.h -->
# sources/user-network-fs/mergerfs/vendored/acutest/acutest.h

## Purpose
This is a single-header C/C++ unit test framework vendored into mergerfs. Test translation units define `TEST_LIST` as an array of `{name, function}` entries and include this header; unless `TEST_NO_MAIN` is set, the header supplies the whole test runner including `main`. It exposes assertion, case labeling, skip, message, dump, and optional C++ exception-checking macros while keeping implementation symbols private with `acutest_*_` names.

## Important APIs, Types, And Control Flow
Public macros include `TEST_LIST`, `TEST_CHECK`, `TEST_CHECK_`, `TEST_ASSERT`, `TEST_ASSERT_`, `TEST_EXCEPTION`, `TEST_CASE`, `TEST_MSG`, `TEST_DUMP`, `TEST_SKIP`, plus optional `TEST_INIT` and `TEST_FINI` hooks. Internal types include `acutest_test_`, `acutest_test_data_`, and `enum acutest_state_` with selected, need-to-run, excluded, success, failed, and skipped states. `main` counts `acutest_list_`, parses command-line options, selects tests by exact/word/substr match, decides whether to fork or run inline, runs each test through `acutest_run_`, prints summary, optionally emits XUnit XML, and returns failure if any test failed.

## State And Persistence
The runner maintains static process state for argv0, test metadata, verbosity, TAP/color/timer modes, current test/case, failure counts, skip reason, XML file handle, child-worker index, and `setjmp` abort recovery. Persistence is limited to stdout/stderr output and optional XML output opened by `--xml-output=FILE`; no repository state is modified.

## Dependencies And Integration Points
The header depends on the C runtime and conditionally on POSIX fork/wait/signal/timers, Linux `/proc/self/status`, Windows process/console/SEH APIs, macOS `sysctl`, C++ exceptions, and Valgrind's `RUNNING_ON_VALGRIND` when `<valgrind.h>` is available. It integrates with mergerfs tests by compiling into test binaries, and its child-process mode isolates crashing tests on Unix/Windows where available.

## Risks And Test Signals
Risks include command-line quoting on Windows child re-exec, static global state making nested/concurrent runner use unsuitable, abort paths skipping normal cleanup, `TEST_SKIP` reading the last byte of an empty formatted reason, TAP verbosity constraints, and XML escaping not being applied to test names. Test signals are direct: compile test binaries with and without `TEST_NO_MAIN`, run `--list`, selected and excluded tests, `--no-exec`, TAP, timers, skipped tests, assertion failures, crash isolation, and `--xml-output` generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/acutest/acutest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/assert.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/assert.hpp

## Purpose
This Boost.Assert header defines the assertion macro surface used by Boost and downstream code: `BOOST_ASSERT`, `BOOST_ASSERT_MSG`, `BOOST_VERIFY`, `BOOST_VERIFY_MSG`, and `BOOST_ASSERT_IS_VOID`. It intentionally has no include guard so different assertion policy macros can be changed before reinclusion.

## Important APIs, Types, And Control Flow
The file first undefines prior assertion macros. If `BOOST_DISABLE_ASSERTS` is set, or debug-handler asserts are enabled under `NDEBUG`, assertions expand to `((void)0)` and `BOOST_ASSERT_IS_VOID` is defined. If handler mode is enabled through `BOOST_ENABLE_ASSERT_HANDLER` or debug-handler mode without `NDEBUG`, it includes `boost/config.hpp` and `boost/current_function.hpp`, declares user-provided `boost::assertion_failed` and `boost::assertion_failed_msg`, and routes failed expressions through them with expression text, function, file, and line. Otherwise it delegates to C `assert`.

## State And Persistence
The header has no runtime state of its own. Runtime behavior is controlled entirely by preprocessor state and by a user-supplied handler implementation when handler mode is selected.

## Dependencies And Integration Points
It depends on Boost.Config for `BOOST_LIKELY`/`BOOST_NORETURN`, Boost.CurrentFunction for function names, or `<assert.h>` for default behavior. It integrates broadly with Boost headers and mergerfs C++ code as a policy layer over C assertions.

## Risks And Test Signals
The no-guard design is intentional but risky if a translation unit expects stable macro definitions after later includes. Handler mode requires exactly matching user-defined functions or link failures occur. Test signals are preprocessor/compile tests under `NDEBUG`, `BOOST_DISABLE_ASSERTS`, `BOOST_ENABLE_ASSERT_HANDLER`, `BOOST_ENABLE_ASSERT_DEBUG_HANDLER`, and default assert mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/assert.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/assert/source_location.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/assert/source_location.hpp

## Purpose
This header supplies `boost::source_location`, a small value type for file/function/line/column data, plus `BOOST_CURRENT_LOCATION` for capturing the current call site across C++ standards and compilers.

## Important APIs, Types, And Control Flow
`boost::source_location` stores `char const* file_`, `char const* function_`, and `boost::uint_least32_t` line/column fields. It has a default unknown-location constructor, a direct constructor, and an optional constructor from `std::source_location`. Accessors return file name, function name, line, and column. `to_string()` formats unknown locations specially, otherwise appends `:line`, optional `:column`, and optional function text. Equality compares string contents plus numeric fields, and `operator<<` is provided when iostreams are available.

## State And Persistence
Instances are plain values referencing string literals or caller-provided character storage. The header stores no global state and performs no persistence beyond temporary string formatting.

## Dependencies And Integration Points
It includes Boost.Config, Boost.Cstdint, `<string>`, `<cstdio>`, `<cstring>`, optional `<iosfwd>`, and optional `<source_location>`. `BOOST_CURRENT_LOCATION` selects among disabled mode, MSVC builtins, standard `std::source_location`, Clang/GCC builtins, `__PRETTY_FUNCTION__`, or a `__FILE__/__LINE__` fallback. It feeds Boost assertion diagnostics and any mergerfs code that wants source locations without hard requiring C++20.

## Risks And Test Signals
Risks include pointer lifetime when direct constructors receive non-static strings, compiler-specific builtin availability, NVCC constexpr limitations, and string comparison cost. Test signals include compile tests on C++03 through C++20, MSVC `/ZI`, GCC/Clang builtins, `BOOST_DISABLE_CURRENT_LOCATION`, iostream-disabled builds, and formatting equality checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/assert/source_location.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config.hpp

## Purpose
This is the root Boost.Config include. It centralizes platform, compiler, standard-library, user, and suffix configuration so other Boost headers can test portable `BOOST_NO_*`, `BOOST_HAS_*`, and feature-helper macros.

## Important APIs, Types, And Control Flow
The header defines `BOOST_CONFIG_HPP`, selects a default `BOOST_USER_CONFIG` of `<boost/config/user.hpp>` unless disabled, includes user config first, then selects and includes compiler, standard library, and platform configs through detail selector headers unless they are already set or disabled. It always includes `boost/config/detail/suffix.hpp` last to derive secondary macros and fallback definitions, and uses `#pragma once` when `BOOST_HAS_PRAGMA_ONCE` is available.

## State And Persistence
All behavior is preprocessor state. It does not define runtime objects, functions, or persisted data.

## Dependencies And Integration Points
It integrates every vendored Boost header with the local compiler by including user, compiler, stdlib, platform, and suffix config headers. Mergerfs inherits Boost portability decisions through any include of Boost.Assert or other vendored Boost headers.

## Risks And Test Signals
Risks are macro-order dependent: user config must come first, suffix must come last, and disabling selector phases can leave required macros undefined. Test signals include preprocessing with `BOOST_NO_USER_CONFIG`, custom `BOOST_USER_CONFIG`, forced `BOOST_COMPILER_CONFIG`, and representative GCC/Clang builds that include headers depending on `BOOST_CONSTEXPR`, `BOOST_NOEXCEPT`, `BOOST_LIKELY`, and visibility macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/borland_prefix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/abi/borland_prefix.hpp

## Purpose
This ABI prefix header normalizes Borland/C++Builder compiler options around Boost declarations so separately compiled Boost binaries and consuming code use compatible structure layout, enum sizing, calling convention, member pointer layout, and name mangling.

## Important APIs, Types, And Control Flow
The file emits Borland pragmas: `#pragma nopushoptwarn` and `#pragma option push -a8 -Vx- -Ve- -b- -pc -Vmv -VC- -Vl- -w-8027 -w-8026`. It pushes the current option state and applies the ABI settings Boost expects. There are no C++ declarations or runtime control paths.

## State And Persistence
The state is compiler option state on the include stack. It persists only until the matching Borland suffix header pops the options.

## Dependencies And Integration Points
It is selected through `BOOST_ABI_PREFIX` by Borland/CodeGear compiler config headers and included by `boost/config/abi_prefix.hpp` when `BOOST_HAS_ABI_HEADERS` is active.

## Risks And Test Signals
Risks are unmatched prefix/suffix includes, accidental use outside Borland-family compilers, and ABI mismatch if user code changes the same options around Boost headers. Test signals are compile-only ABI-header balance tests and binary compatibility checks for compiled Boost libraries under C++Builder.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/borland_prefix.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/borland_suffix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/abi/borland_suffix.hpp

## Purpose
This header is the matching suffix for Borland ABI configuration. It restores compiler option state after Boost declarations that were wrapped by `borland_prefix.hpp`.

## Important APIs, Types, And Control Flow
The entire operational body is `#pragma option pop` followed by `#pragma nopushoptwarn`. There are no exported macros, types, or functions beyond compiler pragma effects.

## State And Persistence
It unwinds compiler option state previously pushed by the prefix. After inclusion, no runtime state or persistent file output remains.

## Dependencies And Integration Points
It is referenced by `BOOST_ABI_SUFFIX` and included indirectly by `boost/config/abi_suffix.hpp`. It must be paired with `borland_prefix.hpp` in the same declaration region.

## Risks And Test Signals
Risk is structural: missing the suffix leaves changed ABI options active for later user code; using the suffix without a prefix can pop unrelated compiler state. Test signals are preprocessor/include-balance tests and compilation of Boost declarations surrounded by `abi_prefix.hpp`/`abi_suffix.hpp` on Borland-family compilers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/borland_suffix.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/msvc_prefix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/abi/msvc_prefix.hpp

## Purpose
This ABI prefix header forces MSVC packing for compiled Boost declarations to match Boost binary layout regardless of project-level packing settings.

## Important APIs, Types, And Control Flow
The header checks `_M_X64`: on x64 it emits `#pragma pack(push,16)`, otherwise `#pragma pack(push,8)`. No declarations or functions are introduced. The paired suffix restores the prior packing.

## State And Persistence
The only state is compiler packing state. It persists across following declarations until `msvc_suffix.hpp` pops it.

## Dependencies And Integration Points
It is selected by MSVC compiler config through `BOOST_ABI_PREFIX` and reached via `boost/config/abi_prefix.hpp` for Boost libraries with separately compiled components. Header-only code generally does not need it when all translation units share compiler options.

## Risks And Test Signals
Risks include unbalanced include pairs, mixed pack settings around exported structs/classes, and ABI mismatch when separately built Boost binaries do not match consumer layout. Test signals include pack-balance compile tests, x86 vs x64 object layout checks, and builds with user project packing overridden before including Boost headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/msvc_prefix.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/msvc_suffix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/abi/msvc_suffix.hpp

## Purpose
This is the matching MSVC ABI suffix header. It restores structure packing after declarations wrapped by the MSVC ABI prefix.

## Important APIs, Types, And Control Flow
The header contains `#pragma pack(pop)` and no C++ declarations. Its control flow is entirely compile-time pragma handling.

## State And Persistence
It mutates only the compiler pack stack, restoring the state present before `msvc_prefix.hpp`. There is no runtime state or persistence.

## Dependencies And Integration Points
It is selected through `BOOST_ABI_SUFFIX` and included by `boost/config/abi_suffix.hpp`. It is part of the Boost.Config ABI wrapping protocol.

## Risks And Test Signals
Risks are mismatched pack stack operations and accidental pop of user pack state if included without the corresponding prefix. Test signals are include-balance tests and ABI/object-size checks for compiled Boost declarations under MSVC packing overrides.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/msvc_suffix.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi_prefix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/abi_prefix.hpp

## Purpose
This wrapper begins a Boost ABI-controlled declaration region. It enforces single active prefix inclusion and delegates to the compiler-selected ABI prefix header when available.

## Important APIs, Types, And Control Flow
The header defines `BOOST_CONFIG_ABI_PREFIX_HPP` and errors on double inclusion. It includes `boost/config.hpp`, then includes `BOOST_ABI_PREFIX` when `BOOST_HAS_ABI_HEADERS` is defined. For Borland it also emits `#pragma nopushoptwarn`. It declares no runtime APIs.

## State And Persistence
The persistent state is a preprocessor sentinel indicating that an ABI prefix is active, plus any compiler pragma state pushed by the selected ABI header. The state must be released by `abi_suffix.hpp`.

## Dependencies And Integration Points
It depends on `boost/config.hpp` to choose compiler ABI headers. Boost compiled library headers include it after all other includes and before declarations whose binary ABI must match shipped libraries.

## Risks And Test Signals
Risks are double inclusion, forgetting `abi_suffix.hpp`, or including code before the prefix. Test signals include intentional double-prefix compile failures, balanced prefix/suffix compile tests, and ABI checks with MSVC/Borland configs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi_prefix.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi_suffix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/abi_suffix.hpp

## Purpose
This wrapper ends a Boost ABI-controlled declaration region started by `boost/config/abi_prefix.hpp`.

## Important APIs, Types, And Control Flow
The header verifies `BOOST_CONFIG_ABI_PREFIX_HPP` is defined, otherwise emits an error because suffix use without prefix is invalid. It undefines that sentinel, includes `BOOST_ABI_SUFFIX` when ABI headers are enabled, and issues Borland warning-control cleanup when needed. It declares no functions or types.

## State And Persistence
It clears the prefix sentinel and pops compiler ABI state through the selected suffix header. No runtime state remains.

## Dependencies And Integration Points
It depends on `boost/config.hpp` having selected ABI headers and on a prior prefix include. It is paired with compiled Boost declaration blocks.

## Risks And Test Signals
Risk comes from unbalanced include structure: suffix without prefix is a hard compile error; prefix without suffix leaks packing/options. Test signals are negative compile tests for suffix-only inclusion and positive tests around class/struct declarations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi_suffix.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx03.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx03.hpp

## Purpose
This generated Boost.Config assertion header fails compilation if the active compiler/stdlib configuration reports missing C++03 conformance features.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp`, then checks a long list of `BOOST_NO_*` defect macros such as ADL barriers, argument-dependent lookup, cv specializations, exceptions, function template ordering, `long long`, member templates, SFINAE, standard namespace/library facilities, template partial specialization, two-phase lookup, RTTI, and type traits-related support. Each detected defect produces a targeted `#error` naming the macro.

## State And Persistence
There is no runtime state. Its only output is a compile success or a preprocessing error.

## Dependencies And Integration Points
It depends on the entire Boost.Config selection stack to have defined accurate defect macros. It integrates as a validation include for builds that require C++03 support from the current toolchain.

## Risks And Test Signals
Risks include stale or overly conservative compiler configs causing false failures, or user configs masking defect macros. Test signals are compile-only checks under supported compilers and deliberate `-D BOOST_NO_*` injections to confirm the expected `#error` path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx03.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx11.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx11.hpp

## Purpose
This generated header validates that Boost.Config does not report missing C++11 compiler or standard-library features.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp` and `boost/config/assert_cxx03.hpp`, so C++03 validation is a prerequisite. It then checks `BOOST_NO_CXX11_*` macros for language features such as `auto`, `constexpr`, `decltype`, defaulted/deleted functions, lambdas, `nullptr`, range-for, rvalue references, scoped enums, SFINAE expressions, variadic templates/macros, `alignas`, `alignof`, `noexcept`, thread-local, and unrestricted unions. It also checks C++11 library headers such as `<array>`, `<atomic>`, `<chrono>`, `<condition_variable>`, `<future>`, `<mutex>`, `<thread>`, `<tuple>`, type traits, and unordered containers.

## State And Persistence
No runtime state exists; the header is a compile-time conformance gate.

## Dependencies And Integration Points
It relies on Boost.Config compiler and stdlib configs. It is useful in CI or configure probes where mergerfs or vendored Boost code requires a true C++11-capable environment.

## Risks And Test Signals
Risks are false failures on partial standard-library implementations and stale vendored compiler support tables. Test signals are C++11 compilation under GCC/Clang/MSVC and negative tests by defining representative `BOOST_NO_CXX11_*` macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx11.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx14.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx14.hpp

## Purpose
This generated header validates C++14 support according to Boost.Config.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp` and `boost/config/assert_cxx11.hpp`, then errors if C++14 defect macros are present. Checked features include aggregate NSDMI, binary literals, relaxed `constexpr`, `decltype(auto)`, digit separators, generic lambdas, `<shared_mutex>`, initialized lambda captures, return type deduction, `std::exchange`, and variable templates.

## State And Persistence
The header has no runtime behavior. It either preprocesses cleanly or halts compilation with an explanatory `#error`.

## Dependencies And Integration Points
It depends on C++11 validation passing first and on Boost.Config's compiler/stdlib feature probes. It can be included by tests or build configuration checks before enabling code paths that rely on C++14.

## Risks And Test Signals
Risks include standard-library feature lag even when the compiler language mode is C++14, especially `<shared_mutex>` and `std::exchange`. Test signals include compiling under `-std=c++14`/equivalent and injected `BOOST_NO_CXX14_*` macros to verify failures are specific.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx14.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx17.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx17.hpp

## Purpose
This generated header validates C++17 support as represented by Boost.Config defect macros.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp` and `boost/config/assert_cxx14.hpp`, then checks `BOOST_NO_CXX17_*` macros. The checks cover auto non-type template parameters, class template deduction guides, fold expressions, `if constexpr`, inline variables, structured bindings, iterator traits, `std::apply`, `std::invoke`, and C++17 library headers including `<any>`, `<charconv>`, `<execution>`, `<filesystem>`, `<memory_resource>`, `<optional>`, `<string_view>`, and `<variant>`.

## State And Persistence
It has no runtime state or persistence. Its behavior is compile-time validation only.

## Dependencies And Integration Points
It depends on the lower standard assertion chain and current Boost.Config compiler/stdlib selections. It integrates with CI/configure checks for code paths that require full C++17 support.

## Risks And Test Signals
Risks are library-specific false failures, especially `<charconv>`, `<execution>`, and `<filesystem>` on older libstdc++/libc++ releases. Test signals are compile-only checks under explicit C++17 mode and targeted negative macro injection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx17.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx20.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx20.hpp

## Purpose
This generated header validates C++20 library/header coverage according to Boost.Config.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp` and `boost/config/assert_cxx17.hpp`, then errors for missing `BOOST_NO_CXX20_HDR_*` macros. Checked headers include `<barrier>`, `<bit>`, `<compare>`, `<concepts>`, `<coroutine>`, `<format>`, `<latch>`, `<numbers>`, `<ranges>`, `<semaphore>`, `<source_location>`, `<span>`, `<stop_token>`, `<syncstream>`, and `<version>`.

## State And Persistence
The header has no runtime state. It acts entirely through compile-time errors.

## Dependencies And Integration Points
It depends on all lower standard assertion headers and Boost.Config stdlib detection. It is a strict feature gate before relying on C++20 standard-library facilities.

## Risks And Test Signals
Risks are high because C++20 library support is uneven across compiler/stdlib combinations; `<format>`, `<ranges>`, and coroutine headers are common fault lines. Test signals are CI compile tests under C++20 mode on each supported toolchain and negative tests defining one `BOOST_NO_CXX20_HDR_*` macro at a time.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx20.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx23.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx23.hpp

## Purpose
This generated header validates selected C++23 standard-library header availability using Boost.Config.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp` and `boost/config/assert_cxx20.hpp`, then checks `BOOST_NO_CXX23_HDR_*` macros for `<expected>`, `<flat_map>`, `<flat_set>`, `<generator>`, `<mdspan>`, `<print>`, `<spanstream>`, `<stacktrace>`, and `<stdfloat>`. Any missing feature macro triggers an explanatory `#error`.

## State And Persistence
There is no runtime state. It is a compile-time feature assertion file.

## Dependencies And Integration Points
It depends on the full lower-standard assertion chain and up-to-date stdlib configuration. It should only be used in environments intending to require C++23 library coverage.

## Risks And Test Signals
C++23 support is still compiler/stdlib dependent, so this header is likely to fail on otherwise modern compilers. Test signals are compile-only checks under C++23 mode and per-header negative tests via `BOOST_NO_CXX23_HDR_*` definitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx23.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx98.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx98.hpp

## Purpose
This generated header validates a small set of C++98 standard-library facilities tracked by Boost.Config.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp` and emits `#error` if `BOOST_NO_CXX98_BINDERS`, `BOOST_NO_CXX98_FUNCTION_BASE`, or `BOOST_NO_CXX98_RANDOM_SHUFFLE` is defined. These correspond to older standard-library components that later standards deprecated or removed but Boost may still detect for compatibility.

## State And Persistence
The header has no runtime state, functions, or data. It only validates compile-time macro state.

## Dependencies And Integration Points
It depends on Boost.Config stdlib detection. It can be used by legacy compatibility checks that require C++98 library components.

## Risks And Test Signals
The main risk is using this as a gate in newer language modes where the standard library intentionally removed deprecated C++98 pieces. Test signals are compile checks under legacy language modes and targeted macro-injection failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx98.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/auto_link.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/auto_link.hpp

## Purpose
This header implements Boost's automatic library selection for MSVC, Borland/Embarcadero, Intel-on-MSVC, Metrowerks Windows, and Clang-cl on Windows. It emits compiler `#pragma comment(lib, ...)` directives so the linker picks the correct Boost binary.

## Important APIs, Types, And Control Flow
The caller must define `BOOST_LIB_NAME`; optional macros include `BOOST_LIB_TOOLSET`, `BOOST_DYN_LINK`, `BOOST_LIB_DIAGNOSTIC`, `BOOST_AUTO_LINK_NOMANGLE`, `BOOST_AUTO_LINK_TAGGED`, `BOOST_AUTO_LINK_SYSTEM`, and `BOOST_LIB_BUILDID`. The header selects a toolset tag, threading tag, runtime tag, architecture/address-model tag, library prefix, and suffix. It then emits a library name in one of the supported layouts: unmangled, tagged, system, build-id, or default full mangling. It errors on incompatible runtime/linkage combinations and missing required macros.

## State And Persistence
There is no runtime state. The persistent effect is a compiler/linker directive embedded in the object file. The header undefines most temporary macros afterward, while intentionally preserving user-supplied `BOOST_LIB_TOOLSET`.

## Dependencies And Integration Points
It includes `boost/config.hpp` and `boost/version.hpp` for compiler identity and Boost version. It integrates with separately compiled Boost libraries; mergerfs on Unix-like platforms likely bypasses it because it only acts for known Windows-style compilers.

## Risks And Test Signals
Risks include silently choosing a nonexistent binary name, `BOOST_DYN_LINK` with static runtime, STLport/debug Python tag mismatches, and no include guard by design. Test signals include preprocessing diagnostics with `BOOST_LIB_DIAGNOSTIC`, MSVC/Clang-cl object inspection for default library directives, and matrix builds for debug/release, static/dynamic, x86/x64.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/auto_link.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/borland.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/borland.hpp

## Purpose
This Boost.Config compiler adapter describes classic Borland C++ capabilities and defects.

## Important APIs, Types, And Control Flow
It rejects unsupported compiler versions, classifies the bundled stdlib as Rogue Wave, STLport, or Dinkumware, and defines many `BOOST_NO_*` macros for known defects: member template friends, cv specializations, SFINAE, template templates, complete value initialization, int64 limitations, two-phase lookup, nested friendship, and broad C++11 feature gaps. It defines positives such as `BOOST_HAS_LONG_LONG`, `BOOST_HAS_STDINT_H`, `BOOST_HAS_MS_INT64`, `BOOST_HAS_DIRENT_H`, and ABI header paths when available.

## State And Persistence
All state is preprocessor state. It may include standard headers to patch missing constants or broken declarations, but no runtime objects are created.

## Dependencies And Integration Points
It is selected by Boost.Config compiler detection. It integrates with ABI wrappers through Borland prefix/suffix headers and with platform config by defining `BOOST_DISABLE_WIN32` under strict ANSI modes.

## Risks And Test Signals
Risks include stale version ranges, forced `#error` for newer versions, broad defect macros disabling usable features, and ABI pragma dependence. Test signals are Boost.Config check-suite compilation on each Borland version, especially exception handling, stdint, ABI prefix/suffix, and C++11 feature gates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/borland.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/clang.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/clang.hpp

## Purpose
This compiler adapter maps Clang's feature-test intrinsics and target environment to Boost.Config macros.

## Important APIs, Types, And Control Flow
It normalizes `__has_extension`, `__has_attribute`, and `__has_cpp_attribute`, detects exceptions, RTTI, thread-local, stdint, float128/int128, branch prediction, symbol visibility, fallthrough, deprecation, aliasing, and unreachable support. It defines `BOOST_NO_CXX11_*`, `BOOST_NO_CXX14_*`, and `BOOST_NO_CXX17_*` when Clang feature probes or SD-6 macros are absent. It sets `BOOST_CLANG`, `BOOST_COMPILER`, and includes `clang_version.hpp` for normalized Apple/non-Apple versioning.

## State And Persistence
No runtime state exists; this is a macro-only configuration file.

## Dependencies And Integration Points
It is included by `boost/config.hpp` for Clang and also by Embarcadero's Clang-based path. It affects Boost.Assert through `BOOST_LIKELY`, symbol/export attributes, and source-location builtin choices.

## Risks And Test Signals
Risks include vendor Clang version skew, MSVC-compatible Clang target quirks, CUDA/NVCC int128 restrictions, and reliance on precise feature probes. Test signals are preprocessing under Apple Clang, upstream Clang, Clang-cl, CUDA-wrapped Clang, and language modes from C++03 through C++20.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/clang.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/clang_version.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/clang_version.hpp

## Purpose
This helper defines a normalized `BOOST_CLANG_VERSION` integer for upstream Clang and Apple Clang.

## Important APIs, Types, And Control Flow
For non-Apple Clang it computes `__clang_major__ * 10000 + __clang_minor__ * 100 + __clang_patchlevel__ % 100`. For Apple Clang it first computes `BOOST_CLANG_REPORTED_VERSION`, then maps Apple/Xcode-reported ranges to approximate upstream Clang version numbers, finally undefining the temporary reported-version macro.

## State And Persistence
It creates only preprocessor macros. There is no runtime state.

## Dependencies And Integration Points
It depends on Clang predefined version macros and optional `__apple_build_version__`. `clang.hpp` includes it so downstream headers can gate features on `BOOST_CLANG_VERSION`, such as source-location builtins.

## Risks And Test Signals
Risks include stale Apple/Xcode mapping and patchlevel truncation. Test signals are preprocessing on representative Apple Clang releases and upstream Clang, verifying the numeric macro matches expected Boost feature gates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/clang_version.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/codegear.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/codegear.hpp

## Purpose
This adapter configures Boost for CodeGear/Embarcadero C++ compilers, covering both classic Borland-derived compilers and newer Clang-enhanced drivers.

## Important APIs, Types, And Control Flow
For Clang-based Embarcadero it includes `clang.hpp`, disables or corrects features known broken in the RTL/compiler, clears int128/float128 positives, marks missing cwchar/fenv/exception-header support, detects driver targets, and defines `BOOST_EMBTC_*` macros. For classic CodeGear it defines warning pragmas, defect macros for older versions, C++11 feature absences, TR1 support macros, stdint/MS int64/dirent support, ABI prefix/suffix paths, and compiler identity.

## State And Persistence
The file only modifies preprocessor and compiler-warning state. It may include `<cstring>` and `<errno.h>` to work around library issues; no runtime state is introduced.

## Dependencies And Integration Points
It is selected by Boost.Config and may delegate to Clang config. It integrates with Borland ABI headers and Windows platform selection through `BOOST_USE_WINDOWS_H`/`BOOST_DISABLE_WIN32`.

## Risks And Test Signals
Risks include the malformed-looking `#elif` target-detection branch, stale Embarcadero driver detection, and feature positives inherited from Clang that must be undone for the RTL. Test signals are classic and Clang Embarcadero compile tests, atomic/int128 checks, wide-char/fenv probes, and ABI wrapping tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/codegear.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/comeau.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/comeau.hpp

## Purpose
This adapter configures Boost for Comeau C++, an EDG-based compiler.

## Important APIs, Types, And Control Flow
It includes `common_edg.hpp`, adds Comeau-specific fixes for older `__COMO_VERSION__` values, handles MSVC emulation quirks such as ADL and void returns, enables `BOOST_HAS_MS_INT64` under sufficiently new VC emulation, sets `BOOST_COMPILER`, and rejects unknown unsupported versions.

## State And Persistence
There is no runtime state; all effects are preprocessor macros.

## Dependencies And Integration Points
It depends on `__COMO_VERSION__`, optional `_MSC_VER`, and the common EDG config. It is selected by Boost.Config for Comeau and feeds all downstream Boost feature decisions.

## Risks And Test Signals
Risks include very narrow version support and reliance on EDG common assumptions. Test signals are compile-only Boost.Config checks under Comeau, with MSVC emulation variants for ADL, void return, and `__int64`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/comeau.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/common_edg.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/common_edg.hpp

## Purpose
This shared adapter defines Boost.Config defaults for EDG-front-end compilers.

## Important APIs, Types, And Control Flow
It requires `__EDG_VERSION__`, then defines defects for older EDG versions: missing int64, SFINAE, void returns, ADL, template templates, abstract detection, and function-scope using declaration ADL issues. It detects exception and long-long support, enables pragma once, and defines broad C++11 feature absences with SD-6 based exceptions for char types, Unicode literals, user literals, variadic templates, constexpr, lambdas, range-for, raw strings, C++14, and C++17 features.

## State And Persistence
All state is preprocessor-only. No functions or objects are emitted.

## Dependencies And Integration Points
It is included by Comeau, Intel fallback, Cray, and other EDG-derived compiler configs. It provides a conservative baseline that those compiler-specific files may refine or override.

## Risks And Test Signals
Risks include over-disabling features for newer EDG-based compilers and exception detection differences for KAI. Test signals are Boost.Config feature-check compilations before and after compiler-specific overrides, especially C++11/C++14 SD-6 gates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/common_edg.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/compaq_cxx.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/compaq_cxx.hpp

## Purpose
This small adapter configures Boost for Compaq C++.

## Important APIs, Types, And Control Flow
It defines `BOOST_COMPILER` from `__DECCXX_VER`, marks `BOOST_NO_CXX11_VARIADIC_MACROS`, and rejects compilers older than version 6.5 with `#error`. There are no type or function declarations.

## State And Persistence
The header only sets preprocessor macros. It has no runtime state.

## Dependencies And Integration Points
It depends on the Compaq predefined `__DECCXX_VER` and is selected by Boost.Config compiler detection. Downstream Boost code uses the resulting compiler identity and defect macro.

## Risks And Test Signals
Risks are minimal but include lack of detailed feature detection and stale assumptions for versions above the supported baseline. Test signals are preprocessing under Compaq C++ and a negative compile test for old version macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/compaq_cxx.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/cray.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/cray.hpp

## Purpose
This adapter configures Boost for Cray C++ Compiler Environment releases, with detailed version and language-mode handling.

## Important APIs, Types, And Control Flow
It computes `BOOST_CRAY_VERSION` from `_RELEASE_MAJOR`, `_RELEASE_MINOR`, and `_RELEASE_PATCHLEVEL`, including a special developer-build `x` patchlevel detector. It validates Cray version and EDG support, includes `common_edg.hpp`, defines a conservative baseline of missing C++11 features and Cray-specific threading/math macros, then conditionally undefines defects or adds positives for CCE 8.5, 8.6, 8.7, and later language modes. It also emulates `__GXX_EXPERIMENTAL_CXX0X__` in GCC mode and supplies atomic constants if absent.

## State And Persistence
The header is macro-only. It temporarily defines helper macros for version computation and undefines them at the end.

## Dependencies And Integration Points
It depends on Cray release macros, EDG markers, optional GCC-emulation macros, and `common_edg.hpp`. It feeds Boost libraries on Cray/HPC systems where compiler feature support changes sharply by release and language mode.

## Risks And Test Signals
Risks include incorrect developer-build patchlevel detection when `x` is user-defined, unsupported ISO dialects, and deliberately retained macros whose comments say tests are imperfect. Test signals are Boost.Config check-suite runs across CCE versions and C++03/11/14 modes, especially atomic, regex, value-initialization, and threading probes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/cray.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/diab.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/diab.hpp

## Purpose
This adapter configures Boost for the Diab C++ compiler.

## Important APIs, Types, And Control Flow
It includes `common_edg.hpp`, sets `BOOST_COMPILER` to `Diab C++ version` plus `__VERSION_NUMBER__`, and rejects versions earlier than 5.0.4.0. It otherwise relies on EDG common configuration for feature defects.

## State And Persistence
No runtime state is present. The header only defines preprocessor macros and errors on unsupported versions.

## Dependencies And Integration Points
It depends on EDG macros, `__VERSION_NUMBER__`, and `common_edg.hpp`. Boost.Config selects it for Diab and downstream code consumes the common EDG defect map.

## Risks And Test Signals
Risks are sparse Diab-specific overrides and stale version support. Test signals are compile-only Boost.Config checks under Diab, with emphasis on EDG features inherited from the common header and the version cutoff.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/diab.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/digitalmars.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/digitalmars.hpp

## Purpose
This adapter configures Boost for Digital Mars C++.

## Important APIs, Types, And Control Flow
It sets `BOOST_COMPILER`, enables long long and pragma once, marks several legacy defects outside strict config, enables dirent/stdint/WinThreads and selected math functions, detects std namespace issues by including `<cstddef>`, detects exceptions, and defines broad C++11/C++14/C++17 absence macros. It rejects `__DMC__ <= 0x840` and optionally errors on unknown versions with `BOOST_ASSERT_CONFIG`.

## State And Persistence
The header emits only macros and may include `<cstddef>` for namespace detection. No runtime objects exist.

## Dependencies And Integration Points
It depends on `__DMC__`, `__DMC_VERSION_STRING__`, `_CPPUNWIND`, and STL vendor macros. It feeds Boost feature selection for Digital Mars builds.

## Risks And Test Signals
Risks include broad disabling of modern C++ features, std namespace detection via included headers, and old compiler support. Test signals are Boost.Config compile checks for exception mode, std namespace, WinThreads, math functions, and C++ feature gates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/digitalmars.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/gcc.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/gcc.hpp

## Purpose
This adapter maps GNU C++ versions and language modes to Boost.Config feature macros.

## Important APIs, Types, And Control Flow
It computes `BOOST_GCC_VERSION`, defines `BOOST_GCC` unless compiling under CUDA, detects C++11 mode, handles GCC 3.x and pre-4.x defects, enables pragma once, long long, NRVO, branch prediction, visibility/import-export attributes, RTTI/typeid detection, int128/float128, C++11 feature availability by version thresholds, C++14 and C++17 SD-6 gates, fallthrough, unused, may-alias, unreachable, and deprecation attributes. It rejects GCC before 3.3 and optionally errors for versions newer than the known 8.1 table under `BOOST_ASSERT_CONFIG`.

## State And Persistence
State is preprocessor-only. It includes `<cstddef>` or `<stddef.h>` to detect libstdc++ float128 support.

## Dependencies And Integration Points
It depends on GCC predefined macros, `__cplusplus`, CUDA markers, MinGW/Darwin/platform macros, and libstdc++ macros. Boost.Assert uses its `BOOST_LIKELY` and source-location code may test `BOOST_GCC`.

## Risks And Test Signals
Risks include stale known-version ceiling, CUDA host-compiler exceptions, MinGW `thread_local` bugs, and mismatch between compiler language support and standard-library support. Test signals are preprocessing/compile tests across GCC versions, C++03-17 modes, MinGW 32-bit, CUDA host builds, and visibility/int128/float128 probes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/gcc.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/gcc_xml.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/gcc_xml.hpp

## Purpose
This adapter configures Boost for GCC-XML, an older source-analysis compiler front end.

## Important APIs, Types, And Control Flow
It disables abstract detection for older GCC-XML GNU emulation, conditionally enables threads for unknown non-Linux/non-MinGW/non-MSVC platforms, marks long long support, and defines broad C++11 absence macros plus SD-6-based C++14/C++17 absence checks. It sets no runtime functions.

## State And Persistence
All effects are preprocessor macros. There is no runtime state or persistence.

## Dependencies And Integration Points
It depends on `__GCCXML_GNUC__`, `__GCCXML_GNUC_MINOR__`, platform macros, and C++ feature-test macros. It is selected by Boost.Config for analysis-tool builds, not normal mergerfs runtime builds.

## Risks And Test Signals
Risks are conservative modern C++ disabling and unconditional thread assumptions on unknown platforms. Test signals are GCC-XML preprocessing of Boost headers and negative checks for unsupported C++11 constructs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/gcc_xml.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/greenhills.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/greenhills.hpp

## Purpose
This adapter configures Boost for the Green Hills C++ compiler.

## Important APIs, Types, And Control Flow
It defines `BOOST_COMPILER` from `__ghs`, enables long long, and marks `BOOST_NO_CXX11_VARIADIC_MACROS`. There are no functions or type declarations.

## State And Persistence
The file is macro-only and has no runtime state.

## Dependencies And Integration Points
It depends on the Green Hills predefined `__ghs` macro and is selected through Boost.Config compiler detection.

## Risks And Test Signals
Risks include very limited feature coverage and potential under-reporting of compiler defects. Test signals are Boost.Config compile checks on Green Hills targets, especially variadic macro and long-long behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/greenhills.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/hp_acc.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/hp_acc.hpp

## Purpose
This adapter configures Boost for HP aC++.

## Important APIs, Types, And Control Flow
It defines `BOOST_COMPILER`, marks `BOOST_NO_TWO_PHASE_NAME_LOOKUP`, detects exception support from `__HPACC_NOEH`, enables `BOOST_HAS_LONG_LONG`, and for older versions defines numerous defects such as ADL absence, member template limitations, standard library issues, function ordering, SFINAE, template templates, and using-template limitations. It defines a broad set of C++11 absence macros and SD-6 checks for C++14/C++17 features, and rejects versions older than A.03.45.

## State And Persistence
The header only sets preprocessor macros. No runtime state is emitted.

## Dependencies And Integration Points
It depends on `__HP_aCC`, exception macros, and Boost.Config selection. Downstream Boost code uses these macros to avoid unsupported templates and standard-library facilities.

## Risks And Test Signals
Risks include old-version specific behavior, unconditional two-phase lookup disablement, and broad modern feature disables. Test signals are compile checks under HP aC++ versions for exceptions, templates, stdlib components, and C++11 feature gates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/hp_acc.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/intel.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/intel.hpp

## Purpose
This adapter configures Boost for Intel C++, accounting for whether Intel is emulating MSVC, GCC, or using an older EDG path.

## Important APIs, Types, And Control Flow
For Intel 15+ with MSVC/GCC emulation, it includes the corresponding `visualc.hpp` or `gcc.hpp`, then undefines host compiler identity and applies Intel corrections. The fallback includes `common_edg.hpp` and performs detailed Intel version setup. It computes `BOOST_INTEL_CXX_VERSION`, C++0x mode, `BOOST_INTEL_GCC_VERSION`, `BOOST_COMPILER`, `BOOST_INTEL`, platform identity, legacy defects, wchar_t validation templates, RTTI/typeid detection, visibility, aliasing, C++11 feature undefines by Intel+host version combinations, known broken features, fenv support, stdint, int128, and known-version checks.

## State And Persistence
Almost all state is macro-only. In C++ mode it declares compile-time templates/typedefs to validate whether `wchar_t` is intrinsic, but they are type-only checks with no runtime storage.

## Dependencies And Integration Points
It depends on Intel, MSVC, GCC, EDG, platform, and CUDA macros and may include host compiler config headers. It is central for Boost portability under Intel compilers.

## Risks And Test Signals
Risks include complex host-emulation interactions, stale version ceiling, Intel version 9999 workaround, feature availability that depends on both Intel and host compiler versions, and CUDA C++03 int128 restrictions. Test signals are matrix compile tests under Intel/MSVC and Intel/GCC modes, C++03/11/14/17 modes, wchar_t validation, RTTI-off builds, and feature-specific tests for constexpr, rvalue refs, tuple/future, and int128.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/intel.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/kai.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/kai.hpp

## Purpose
This adapter configures Boost for KAI C++, another EDG-derived compiler.

## Important APIs, Types, And Control Flow
It includes `common_edg.hpp`, sets `BOOST_COMPILER`, and handles KAI-specific exception support with `__EXCEPTIONS`/`__KCC_EXCEPTIONS`. It rejects compilers older than 4.0 and optionally errors on versions newer than the known 4.0f table under `BOOST_ASSERT_CONFIG`.

## State And Persistence
It is preprocessor-only and has no runtime state.

## Dependencies And Integration Points
It depends on `__KCC_VERSION`, `__KCC`, exception macros, and common EDG config. It participates in Boost.Config compiler selection.

## Risks And Test Signals
Risks include narrow version coverage and reliance on common EDG defaults for most feature decisions. Test signals are KAI compile checks for exception mode, EDG inherited features, and version guard behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/kai.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/metrowerks.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/metrowerks.hpp

## Purpose
This adapter configures Boost for Metrowerks CodeWarrior C++.

## Important APIs, Types, And Control Flow
It disables locale when `_MSL_NO_LOCALE` is set, marks older-version template and SFINAE defects, detects intrinsic wchar and exception support through `__option`, maps `__MWERKS__` values to readable compiler versions, optionally enables rvalue references, defines broad C++11 absence macros, and uses SD-6 checks for C++14/C++17 features. It sets `BOOST_COMPILER`, rejects versions before 5.3, and optionally errors on unknown newer versions.

## State And Persistence
The header is macro-only. No runtime state exists.

## Dependencies And Integration Points
It depends on Metrowerks predefined macros and `__option`. Boost.Config uses it to select workaround paths for older CodeWarrior toolchains.

## Risks And Test Signals
Risks include old compiler support assumptions, strict-config differences, and feature detection tied to proprietary `__option` values. Test signals include compile checks across known CodeWarrior versions for templates, exceptions, wchar_t, rvalue references, and C++11 defect macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/metrowerks.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/mpw.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/mpw.hpp

## Purpose
This adapter configures Boost for classic MPW SCpp/MrCpp compilers.

## Important APIs, Types, And Control Flow
It sets `BOOST_COMPILER` based on `__SC__` or `__MRC__`, otherwise errors because the config was selected incorrectly. For MPW 8.90 or non-strict config it defines legacy defects covering cv specializations, dependent nested derivations, in-class member initialization, intrinsic wchar_t, partial specialization, using templates, cwchar, limits constants, and allocator quirks. It then defines broad C++11 absence macros and SD-6 checks for C++14/C++17 features.

## State And Persistence
All effects are preprocessor macros. There is no runtime state.

## Dependencies And Integration Points
It depends on MPW predefined macros and `MPW_CPLUS`. It is selected by Boost.Config for classic Mac MPW toolchains.

## Risks And Test Signals
Risks include old compiler assumptions, broad modern-feature disablement, and accidental selection for non-MPW compilers. Test signals are compile checks under SCpp/MrCpp, negative wrong-selection checks, and legacy template/stdlib feature tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/mpw.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/nvcc.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/nvcc.hpp

## Purpose
This adapter applies Boost.Config corrections when code is compiled through NVIDIA NVCC.

## Important APIs, Types, And Control Flow
It defines `BOOST_COMPILER` as `nvcc` plus `CUDART_VERSION`, marks `BOOST_GPU_ENABLED` as `__host__ __device__`, and disables features known to be problematic for CUDA compilation: `BOOST_NO_CXX11_VARIADIC_MACROS`, `BOOST_NO_CXX11_HDR_INITIALIZER_LIST`, `BOOST_NO_CXX11_HDR_CHRONO`, `BOOST_NO_CXX11_HDR_CODECVT`, `BOOST_NO_CXX11_HDR_ATOMIC`, and in device compilation, `BOOST_NO_CXX14_DIGIT_SEPARATORS`. If `__CUDACC_VER_MAJOR__` is available it conditionally disables extended lambdas, `std::allocator`, C++17 fold expressions, `if constexpr`, inline variables, structured bindings, and auto non-type template parameters by CUDA and `__cplusplus` thresholds.

## State And Persistence
It is macro-only and has no runtime state.

## Dependencies And Integration Points
It depends on CUDA version macros and NVCC host/device markers. It overlays host compiler configs by correcting features that host compilers may report but NVCC cannot compile reliably.

## Risks And Test Signals
Risks include CUDA version skew, host compiler feature leakage, and device-pass restrictions differing from host-pass restrictions. Test signals are NVCC compile tests for host and `__CUDA_ARCH__` device paths across CUDA versions, especially initializer lists, chrono, atomics, generic/extended lambdas, and C++17 constructs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/nvcc.hpp -->
