# subset-b-009676 research

Grouped research for Boost configuration and container-hash headers under `sources/user-network-fs/mergerfs/vendored/boost`. Each section preserves the source path and is intended to be split into the corresponding source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/pathscale.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/pathscale.hpp

Purpose: configures Boost for the PathScale EKOPath C++ compiler. It sets `BOOST_COMPILER` and then chooses one of two paths: PathCC 6 and newer delegate to `boost/config/compiler/clang.hpp`, while PathCC 4 and 5 define an explicit legacy feature profile.

Important APIs/macros: the file exports only preprocessor configuration macros. The legacy branch enables POSIX and math capability macros such as `BOOST_HAS_UNISTD_H`, `BOOST_HAS_PTHREADS`, `BOOST_HAS_STDINT_H`, `BOOST_HAS_CLOCK_GETTIME`, `BOOST_HAS_EXPM1`, and `BOOST_HAS_LOG1P`; it also marks many C++11 features and headers unavailable with `BOOST_NO_CXX11_*`. C++14 and C++17 support is tested with SD-6 feature-test macros such as `__cpp_constexpr`, `__cpp_structured_bindings`, and `__cpp_if_constexpr`.

Control flow/dependencies: selected by `detail/select_compiler_config.hpp` when `__PATHSCALE__` and `__PATHCC__ >= 4` are present. The `__PATHCC__ >= 6` branch reuses Clang configuration, so downstream behavior depends on `clang.hpp`; older branches are local macro assignments.

State and persistence: all behavior is compile-time macro state. There is no runtime state or persistence.

Integration points: `boost/config.hpp` consumes the feature macros, and `detail/suffix.hpp` later normalizes implication macros and thread availability.

Risks and test signals: risk is stale feature assumptions for a rare compiler. Useful tests are preprocessing with representative `__PATHCC__` values and compiling Boost.Config feature probes for PathCC 4/5 versus the Clang-based PathCC 6 path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/pathscale.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/pgi.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/pgi.hpp

Purpose: adapts Boost.Config to the PGI/NVIDIA HPC C++ compiler. It treats PGI as mostly GCC-compatible, includes the GCC compiler configuration, and then corrects known PGI deviations.

Important APIs/macros: defines `BOOST_COMPILER_VERSION` from `__PGIC__` and `__PGIC_MINOR__`, and defines `BOOST_COMPILER` from that value. It then undefines `BOOST_HAS_FLOAT128` because PGI exposes `__float128` as a typedef rather than as a distinct type, and undefines `BOOST_HAS_INT128` because `__int128` is not supported.

Control flow/dependencies: selected by `detail/select_compiler_config.hpp` when `__PGI` is defined. The primary dependency is `boost/config/compiler/gcc.hpp`; this file is a correction layer on top of GCC-compatible defaults.

State and persistence: compile-time macro state only.

Integration points: the corrected `BOOST_HAS_*128` macros protect Boost code that overloads or specializes on extended arithmetic types. The compiler identity feeds diagnostics and optional `BOOST_ASSERT_CONFIG` reporting.

Risks and test signals: the main risk is inheriting too much from GCC if PGI diverges in newer releases. Test by compiling Boost.Config arithmetic-type probes and overload-resolution checks under PGI/NVIDIA HPC releases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/pgi.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/sgi_mipspro.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/sgi_mipspro.hpp

Purpose: configures Boost for the SGI IRIX MIPSpro C++ compiler.

Important APIs/macros: defines `BOOST_COMPILER` from `_COMPILER_VERSION`, includes `boost/config/compiler/common_edg.hpp`, enables `BOOST_HAS_THREADS`, and disables two-phase name lookup with `BOOST_NO_TWO_PHASE_NAME_LOOKUP`. It explicitly undefines `BOOST_NO_SWPRINTF` and `BOOST_DEDUCED_TYPENAME`, overriding defaults inherited from EDG/common configuration.

Control flow/dependencies: selected when `__sgi` is detected by `detail/select_compiler_config.hpp`. The meaningful compiler feature baseline comes from `common_edg.hpp`; this file applies SGI-specific threading and language corrections.

State and persistence: compile-time macro configuration only.

Integration points: platform selection will usually pair this with `platform/irix.hpp`, which contributes POSIX feature macros and may disable threads for GNU-on-IRIX builds. `detail/suffix.hpp` later validates whether an actual threading API was detected.

Risks and test signals: MIPSpro is legacy and hard to validate. Risks include mismatches between EDG defaults and the SGI front end. Test signals are Boost.Config compile probes for `swprintf`, dependent typename handling, thread macros, and two-phase lookup assumptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/sgi_mipspro.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/sunpro_cc.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/sunpro_cc.hpp

Purpose: configures Boost for Sun/Oracle Studio C++ (`__SUNPRO_CC`). It encodes version-specific workarounds from early SunPro 5.x through Oracle Studio 12.6-era values.

Important APIs/macros: exports `BOOST_COMPILER`, `BOOST_SYMBOL_EXPORT`, `BOOST_SYMBOL_IMPORT`, `BOOST_SYMBOL_VISIBLE`, and `BOOST_DEPRECATED(msg)`. It defines many `BOOST_NO_*` and `BOOST_NO_CXX11/14/17_*` macros for missing or unreliable features, including in-class initialization, SFINAE expressions, two-phase lookup, variadic templates, ref qualifiers, thread-local storage, and C++17 structured bindings/inline variables/fold expressions. It also enables `BOOST_HAS_LONG_LONG` and conditionally `BOOST_HAS_THREADS` for Solaris 12 with Studio 12.4+.

Control flow/dependencies: selected by `detail/select_compiler_config.hpp` on `__SUNPRO_CC`. The flow is a sequence of version thresholds, then shared object/deprecation support, then modern feature-test macro checks, then version validation.

State and persistence: compile-time-only macro state.

Integration points: pairs with Solaris platform configuration and `suffix.hpp` normalization. Visibility/deprecation macros are consumed by exported Boost libraries.

Risks and test signals: risk is over-disabling features for newer Oracle Developer Studio or under-disabling broken partial implementations. Test via Boost.Config feature tests across `__SUNPRO_CC` versions, especially value initialization, SFINAE, deprecation attributes, visibility, and thread support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/sunpro_cc.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/vacpp.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/vacpp.hpp

Purpose: configures Boost for IBM VisualAge and older IBM XL C++ identified by `__IBMCPP__`.

Important APIs/macros: defines `BOOST_COMPILER`, version gates for unsupported compilers, `BOOST_MAY_ALIAS` for `__IBMCPP__ >= 1310`, and `_THREAD_SAFE`-based `BOOST_HAS_THREADS`. It disables older IBM defects including member template friends, in-class integral initialization, pointer-to-member template parameters, complete value initialization, and partial specialization default arguments. C++11 feature availability is driven by IBM-specific macros such as `__IBMCPP_AUTO_TYPEDEDUCTION`, `__IBMCPP_DECLTYPE`, `__IBMCPP_RVALUE_REFERENCES`, and `__IBMCPP_VARIADIC_TEMPLATES`; C++14/17 features are checked with SD-6 macros.

Control flow/dependencies: selected after z/OS XL and Linux clang-based XL checks, so it covers VisualAge and big-endian/legacy IBM XL configurations. It is a local macro table with no includes.

State and persistence: compile-time macros only.

Integration points: commonly pairs with `platform/aix.hpp` and `stdlib/vacpp.hpp`. `suffix.hpp` derives portable helpers such as `BOOST_DEFAULTED_FUNCTION`, `BOOST_MAY_ALIAS`, and thread validation from these macros.

Risks and test signals: risk is confusion between old `vacpp.hpp`, clang-based `xlcpp.hpp`, and z/OS `xlcpp_zos.hpp`. Test by preprocessing compiler selection and running Boost.Config probes for IBM-specific feature macros and thread flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/vacpp.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/visualc.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/visualc.hpp

Purpose: configures Boost for Microsoft Visual C++ and compatible compilers that define `_MSC_VER`.

Important APIs/macros: defines `BOOST_MSVC`, `BOOST_MSVC_FULL_VER`, `BOOST_COMPILER`, `BOOST_UNREACHABLE_RETURN`, `BOOST_HAS_MS_INT64`, `BOOST_HAS_LONG_LONG`, `BOOST_HAS_NRVO`, `BOOST_HAS_PRAGMA_ONCE`, `BOOST_HAS_PRAGMA_DETECT_MISMATCH`, `BOOST_DEPRECATED(msg)`, ABI prefix/suffix headers, and `BOOST_CXX_VERSION`. It disables features by `_MSC_VER`, `_MSC_FULL_VER`, and `_MSVC_LANG`, including older C++11 constructs, value initialization, two-phase lookup, SFINAE expressions, C++14 constexpr, and early C++17 features. It also handles exception/RTTI mode macros and WinCE/CLR special cases.

Control flow/dependencies: selected last in compiler selection because many compilers emulate `_MSC_VER`. The file is ordered from core version normalization, to language/runtime features, to ABI, language-version reporting, and diagnostic messages for future versions.

State and persistence: compile-time macro state only.

Integration points: pairs with `platform/win32.hpp` and usually `stdlib/dinkumware.hpp`. ABI macros include `boost/config/abi/msvc_prefix.hpp` and suffix when not overridden.

Risks and test signals: risk centers on MSVC compatibility modes, clang-cl, and future `_MSC_VER` values. Tests should cover `/permissive-`, `/std:` modes, exceptions/RTTI toggles, CLR, WinCE, and Boost auto-link/ABI behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/visualc.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/xlcpp.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/xlcpp.hpp

Purpose: configures Boost for IBM XL C/C++ for Linux little-endian, which is clang based and identified separately from legacy `__IBMCPP__`.

Important APIs/macros: defines `BOOST_HAS_PRAGMA_ONCE`, optional `BOOST_HAS_PRAGMA_DETECT_MISMATCH`, `BOOST_NO_EXCEPTIONS`, `BOOST_NO_RTTI`, `BOOST_NO_TYPEID`, `BOOST_HAS_MS_INT64`, `BOOST_HAS_NRVO`, `BOOST_HAS_LONG_LONG`, `BOOST_SYMBOL_EXPORT/IMPORT/VISIBLE`, `BOOST_LIKELY`, `BOOST_UNLIKELY`, and optionally `BOOST_FALLTHROUGH`. Feature gates are based on Clang `__has_feature`, `__has_extension`, `__has_cpp_attribute`, `__has_builtin`, and SD-6 macros.

Control flow/dependencies: selected when `__ibmxl__` is set and not treated as generic Clang. The file locally defines compatibility fallbacks for `__has_extension` and `__has_cpp_attribute`, then tests C++11/14/17 features one by one.

State and persistence: compile-time macros only.

Integration points: integrates with Boost visibility, branch-prediction, exception/RTTI, and feature-selection helpers. `suffix.hpp` consumes the feature macros to define portable wrappers such as `BOOST_NOEXCEPT` and `BOOST_CONSTEXPR`.

Risks and test signals: risk is that IBM's clang fork reports features differently from upstream Clang. Test with `__has_feature` probes for exceptions, RTTI, constexpr, generic lambdas, relaxed constexpr, and visibility attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/xlcpp.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/xlcpp_zos.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/xlcpp_zos.hpp

Purpose: configures Boost for IBM z/OS XL C/C++ V2R1.

Important APIs/macros: validates `__IBMCPP__`, `__COMPILER_VER__`, and minimum supported `0x42010000`, defines `BOOST_COMPILER` and `BOOST_XLCPP_ZOS`, includes `<features.h>`, and marks many unsupported C++11/14/17 language features. It enables `BOOST_HAS_LOG1P`, `BOOST_HAS_EXPM1`, `BOOST_HAS_STDINT_H`, `BOOST_HAS_NRVO`, `BOOST_HAS_LONG_LONG`, `BOOST_HAS_MS_INT64`, `BOOST_HAS_VARIADIC_TMPL`, `BOOST_HAS_STATIC_ASSERT`, `BOOST_HAS_RVALUE_REFS`, and `BOOST_HAS_DECLTYPE` when z/OS feature macros permit. It defines `BOOST_FORCEINLINE`, `BOOST_NOINLINE`, `BOOST_MAY_ALIAS`, `BOOST_LIKELY`, and `BOOST_UNLIKELY` when IBM attributes/builtins are available.

Control flow/dependencies: selected before generic IBM compiler configuration when `__MVS__` and `__COMPILER_VER__` are present. The file is strict about known compiler versions and emits `BOOST_ASSERT_CONFIG` errors for newer versions.

State and persistence: compile-time-only macros.

Integration points: pairs with `platform/zos.hpp` and `stdlib/xlcpp_zos.hpp`. The branch-prediction macros and type/feature flags feed generic Boost code.

Risks and test signals: risk is stale V2R1 assumptions and strict version rejection. Test z/OS builds with feature macros for RTTI, exceptions, long long, defaulted/deleted functions, attributes, and threading.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/xlcpp_zos.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/detail/cxx_composite.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/detail/cxx_composite.hpp

Purpose: automatically generated Boost.Config composite-feature header. It condenses many individual `BOOST_NO_*` macros into aggregate standard-level macros.

Important APIs/macros: defines `BOOST_NO_CXX03`, `BOOST_NO_CXX11`, `BOOST_NO_CXX14`, `BOOST_NO_CXX17`, `BOOST_NO_CXX20`, and `BOOST_NO_CXX23` when any required language or standard-library feature for that level is missing. It covers language features, standard headers, library functions, and historical Boost.Config defect macros.

Control flow/dependencies: included near the end of `detail/suffix.hpp`, after compiler/platform/stdlib headers and suffix normalization have defined individual feature macros. The file is a set of large `#if defined(...) || ...` conditionals; there are no includes or runtime functions.

State and persistence: derived compile-time macro state only.

Integration points: downstream Boost libraries can test a broad language level (`BOOST_NO_CXX17`) rather than enumerating all missing C++17 pieces. It is generated by Boost.Config tooling, so source-of-truth changes likely live in generator metadata rather than manual edits.

Risks and test signals: risk is incomplete aggregation when new feature macros are introduced or obsolete macros remain. Test by comparing generated output from Boost.Config tools and validating representative compilers where only one feature in a level is missing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/detail/cxx_composite.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/detail/posix_features.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/detail/posix_features.hpp

Purpose: derives POSIX and X/Open capability macros from `<unistd.h>` feature macros.

Important APIs/macros: when `BOOST_HAS_UNISTD_H` is already set, includes `<unistd.h>` and may define `BOOST_HAS_NL_TYPES_H`, `BOOST_HAS_STDINT_H`, `BOOST_HAS_DIRENT_H`, `BOOST_HAS_SIGACTION`, `BOOST_HAS_PTHREADS`, `BOOST_HAS_NANOSLEEP`, `BOOST_HAS_CLOCK_GETTIME`, `BOOST_HAS_SCHED_YIELD`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_LOG1P`, and `BOOST_HAS_EXPM1`.

Control flow/dependencies: platform headers opt in by defining `BOOST_HAS_UNISTD_H` and including this file. Tests use `_XOPEN_VERSION`, `_POSIX_VERSION`, `_POSIX_THREADS`, `_POSIX_TIMERS`, `_XOPEN_REALTIME`, `_POSIX_PRIORITY_SCHEDULING`, `_POSIX_THREAD_PRIORITY_SCHEDULING`, and `_XOPEN_SOURCE`.

State and persistence: compile-time macro derivation only.

Integration points: reused by Unix-like platform configs such as AIX, BSD, Linux, macOS, Solaris, VxWorks, QNX, and generic Unix fallback.

Risks and test signals: risk is false positives from platforms that define POSIX macros but ship stubs or require feature macros before system headers. Test with preprocess-only and compile/link checks for pthreads, timers, directory headers, and math functions under each platform mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/detail/posix_features.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/detail/select_compiler_config.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/detail/select_compiler_config.hpp

Purpose: selects the compiler-specific Boost.Config header by defining `BOOST_COMPILER_CONFIG`.

Important APIs/macros: emits only `BOOST_COMPILER_CONFIG` and, for CUDA, directly includes `boost/config/compiler/nvcc.hpp`. It recognizes GCC-XML, Cray, Comeau, PathScale, Intel, Clang, Digital Mars, Diab, PGI, GCC, Kai, SGI MIPSpro, Compaq, Green Hills, CodeGear, Borland, Metrowerks, SunPro, HP aCC, MPW, IBM z/OS XL, IBM clang-based XL, IBM VisualAge/legacy XL, and MSVC.

Control flow/dependencies: an ordered `#if/#elif` chain. Ordering is critical: compiler emulation cases appear before the compilers they emulate, and `_MSC_VER` is last because many vendors define it. A disabled `#if 0` block lists all possible includes for dependency scanners.

State and persistence: compile-time selection only.

Integration points: `boost/config.hpp` includes the selected header unless user config bypasses compiler detection.

Risks and test signals: risk is detection-order regression for emulating compilers. Test by preprocessing under clang-cl, Intel, IBM XL, PGI, PathScale, and MSVC and verifying the selected `BOOST_COMPILER_CONFIG`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/detail/select_compiler_config.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/detail/select_platform_config.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/detail/select_platform_config.hpp

Purpose: selects the platform-specific Boost.Config header by defining `BOOST_PLATFORM_CONFIG`.

Important APIs/macros: detects Linux/glibc, BSD variants, Solaris, IRIX, HP-UX, Cygwin, Win32, Haiku, BeOS, macOS, z/OS, AIX, AmigaOS, QNX, VxWorks, Symbian, Cray, VMS, CloudABI, WebAssembly, and generic Unix. Generic Unix defines `BOOST_HAS_UNISTD_H` and includes `detail/posix_features.hpp`.

Control flow/dependencies: ordered `#elif` chain. Cygwin intentionally precedes Win32 because it is not treated as native Win32. Cray is excluded from the Linux/glibc branch. The file uses quoted header names to avoid macro expansion in include names and contains a disabled dependency-scanner include list.

State and persistence: compile-time platform selection only.

Integration points: selected by `boost/config.hpp` unless disabled or overridden by `BOOST_PLATFORM_CONFIG` in user config.

Risks and test signals: risk is ambiguous platform macros, especially Cygwin/Win32, Cray/Linux, Apple/BSD, and z/OS/AIX IBM macros. Test by preprocessing target triples and verifying selected config plus POSIX feature macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/detail/select_platform_config.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/detail/select_stdlib_config.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/detail/select_stdlib_config.hpp

Purpose: selects the standard-library-specific Boost.Config header by defining `BOOST_STDLIB_CONFIG`.

Important APIs/macros: includes `<version>`, `<cstddef>`, or `<stddef.h>` to expose library macros, then detects STLPort, Comeau STL, Rogue Wave, libc++, GNU libstdc++ 3, generic SGI STL, Metrowerks MSL, IBM z/OS XL stdlib, IBM VisualAge stdlib, Modena, and Dinkumware/MSVC STL.

Control flow/dependencies: STLPort is checked first because it can sit on top of another library. If no library macro is visible after the first probe, it includes `<utility>` to expose C++-specific library macros. A disabled include list exists for dependency scanners.

State and persistence: compile-time selection only.

Integration points: `boost/config.hpp` includes the selected stdlib config unless disabled or overridden. The selected header contributes `BOOST_NO_CXX*_HDR_*`, namespace, allocator, locale, and extension container macros.

Risks and test signals: risk is accidental detection of an underlying vendor library instead of an adapter library. Test with libc++, libstdc++, MSVC STL, STLPort-over-Dinkumware, IBM, and Rogue Wave by verifying `BOOST_STDLIB_CONFIG` and `BOOST_STDLIB`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/detail/select_stdlib_config.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/detail/suffix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/detail/suffix.hpp

Purpose: final normalization layer for Boost.Config. After user, compiler, platform, and standard-library headers have contributed raw feature macros, this file derives implications, defines portable helper macros/types, checks standard headers, and adds compatibility aliases.

Important APIs/macros: defines defaults for `BOOST_SYMBOL_EXPORT/IMPORT/VISIBLE`, `BOOST_STD_EXTENSION_NAMESPACE`, `BOOST_STATIC_CONSTANT`, `BOOST_USE_FACET`, `BOOST_HAS_FACET`, `BOOST_NESTED_TEMPLATE`, `BOOST_UNREACHABLE_RETURN`, `BOOST_DEDUCED_TYPENAME`, `BOOST_CTOR_TYPENAME`, `BOOST_RESTRICT`, `BOOST_MAY_ALIAS`, `BOOST_FORCEINLINE`, `BOOST_NOINLINE`, `BOOST_NORETURN`, `BOOST_DEPRECATED`, `BOOST_LIKELY`, `BOOST_UNLIKELY`, `BOOST_OVERRIDE`, `BOOST_ALIGNMENT`, `BOOST_DEFAULTED_FUNCTION`, `BOOST_DELETED_FUNCTION`, `BOOST_FINAL`, `BOOST_NOEXCEPT`, `BOOST_CONSTEXPR`, `BOOST_CXX14_CONSTEXPR`, `BOOST_INLINE_VARIABLE`, `BOOST_IF_CONSTEXPR`, `BOOST_ATTRIBUTE_UNUSED`, `BOOST_ATTRIBUTE_NODISCARD`, `BOOST_NULLPTR`, and type aliases such as `boost::long_long_type`, `boost::int128_type`, and `boost::float128_type` when supported.

Control flow/dependencies: includes `<limits.h>`, sometimes `<cstddef>`, `<typeinfo>`, `boost/config/helper_macros.hpp`, `<version>`, and `detail/cxx_composite.hpp`. It first repairs implications among legacy feature macros, then validates thread APIs, then defines helper wrappers, then maps deprecated macro names, then probes C++17/20/23 headers with `__has_include` and feature-test macros.

State and persistence: compile-time-only macro state and a few compile-time typedefs in namespace `boost`. No runtime persistence.

Integration points: every Boost library that includes `boost/config.hpp` receives these helpers. It is also the enforcement point for deprecated minimum requirements such as no template partial specialization.

Risks and test signals: high risk because it globally affects all Boost headers. Test with Boost.Config's full matrix: thread on/off modes, deprecated aliases, C++ standard modes, `__has_include` availability, MSVC `_MSVC_LANG`, CUDA/device compilation, no-exception/no-RTTI modes, and standard header feature-test coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/detail/suffix.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/header_deprecated.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/header_deprecated.hpp

Purpose: provides a portable macro for marking a header as deprecated.

Important APIs/macros: defines `BOOST_HEADER_DEPRECATED(a)`. Unless `BOOST_ALLOW_DEPRECATED_HEADERS` or `BOOST_ALLOW_DEPRECATED` is defined, the macro emits a pragma message saying that the header is deprecated and naming the replacement argument `a`.

Control flow/dependencies: includes `boost/config/pragma_message.hpp`, then conditionally defines the macro. It is C-compatible and has a normal include guard.

State and persistence: no runtime state; it only affects compile diagnostics.

Integration points: deprecated Boost headers include this file and pass the replacement header string. `BOOST_PRAGMA_MESSAGE` handles compiler-specific diagnostic syntax.

Risks and test signals: risk is warning noise or unsupported pragma syntax, both delegated to `pragma_message.hpp`. Test by preprocessing or compiling a deprecated wrapper with and without `BOOST_ALLOW_DEPRECATED_HEADERS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/header_deprecated.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/helper_macros.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/helper_macros.hpp

Purpose: provides minimal C-compatible preprocessor helpers used by Boost.Config and other Boost headers.

Important APIs/macros: `BOOST_STRINGIZE(X)` expands macro arguments before stringizing through `BOOST_DO_STRINGIZE(X)`. `BOOST_JOIN(X, Y)` expands macro arguments before token pasting through `BOOST_DO_JOIN` and `BOOST_DO_JOIN2`.

Control flow/dependencies: no includes and no runtime code. The only flow is macro indirection to force the preprocessor expansion order required by the C/C++ macro rules.

State and persistence: none beyond preprocessor expansion.

Integration points: used by compiler-name strings, pragma message construction, generated identifiers, and config diagnostics.

Risks and test signals: low risk but central. Incorrect indirection would break version strings and token-paste based macros. Test with macro-valued arguments such as `BOOST_STRINGIZE(__LINE__)` and `BOOST_JOIN(foo_, BAR)` where `BAR` is itself a macro.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/helper_macros.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/cmath.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/cmath.hpp

Purpose: includes the real standard `<cmath>` while preventing recursive inclusion through Boost.TR1 wrapper paths.

Important APIs/macros: defines include guard `BOOST_CONFIG_CMATH`. If `BOOST_TR1_NO_RECURSION` is not already defined, it defines it and records ownership with `BOOST_CONFIG_NO_CMATH_RECURSION`; after including `<cmath>`, it undefines both ownership macros.

Control flow/dependencies: the control flow is guard, temporary recursion block, standard include, cleanup. It depends only on `<cmath>` and Boost's TR1 recursion convention.

State and persistence: temporary preprocessor state during inclusion. It restores `BOOST_TR1_NO_RECURSION` only when this header set it.

Integration points: standard-library detection headers use `no_tr1` wrappers when probing vendor macros without accidentally including Boost.TR1 replacements.

Risks and test signals: risk is leaking `BOOST_TR1_NO_RECURSION` or recursing when include paths prioritize Boost.TR1. Test by placing Boost.TR1 paths before the standard library and including this wrapper twice.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/cmath.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/complex.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/complex.hpp

Purpose: includes the real standard `<complex>` while blocking recursive Boost.TR1 replacement headers.

Important APIs/macros: defines `BOOST_CONFIG_COMPLEX`; temporarily defines `BOOST_TR1_NO_RECURSION` and `BOOST_CONFIG_NO_COMPLEX_RECURSION` when needed; includes `<complex>`; then undoes the temporary definitions it owns.

Control flow/dependencies: same pattern as the other `no_tr1` wrappers. It depends on `<complex>` and the Boost.TR1 recursion guard macro.

State and persistence: temporary compile-time macro state only.

Integration points: used by configuration probes that need vendor standard-library macros from the real standard header, not Boost.TR1 forwarding headers.

Risks and test signals: risk is include-path recursion or macro leakage. Test with repeated includes and with `BOOST_TR1_NO_RECURSION` pre-defined by a caller.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/complex.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/functional.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/functional.hpp

Purpose: safely includes standard `<functional>` without routing through Boost.TR1 wrapper headers.

Important APIs/macros: defines `BOOST_CONFIG_FUNCTIONAL`; temporarily defines `BOOST_TR1_NO_RECURSION` and `BOOST_CONFIG_NO_FUNCTIONAL_RECURSION` only if the caller has not already requested no recursion.

Control flow/dependencies: include guard, temporary recursion macro setup, `<functional>` include, conditional cleanup.

State and persistence: temporary preprocessor state only; no runtime behavior.

Integration points: standard-library detection and compatibility headers can include this wrapper when they need real standard-library declarations/macros while Boost.TR1 include directories are active.

Risks and test signals: risk is accidental recursion through `boost/tr1/tr1/functional` or failing to preserve caller-owned `BOOST_TR1_NO_RECURSION`. Test with the macro pre-set and unset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/functional.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/memory.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/memory.hpp

Purpose: safely includes standard `<memory>` while avoiding recursive Boost.TR1 memory wrappers.

Important APIs/macros: defines `BOOST_CONFIG_MEMORY`; temporarily sets `BOOST_TR1_NO_RECURSION` and `BOOST_CONFIG_NO_MEMORY_RECURSION`; includes `<memory>`; and unsets the temporary macros when this wrapper created them.

Control flow/dependencies: no logic beyond the standard `no_tr1` wrapper pattern. Depends on `<memory>`.

State and persistence: temporary preprocessor-only state.

Integration points: used during library detection or compatibility includes where Boost must inspect the vendor standard library directly.

Risks and test signals: macro lifetime bugs can affect later Boost.TR1 headers. Test repeated inclusion and caller-owned `BOOST_TR1_NO_RECURSION` preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/memory.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/utility.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/utility.hpp

Purpose: safely includes standard `<utility>` without recursively including Boost.TR1 utility wrappers.

Important APIs/macros: defines `BOOST_CONFIG_UTILITY`; temporarily sets `BOOST_TR1_NO_RECURSION` and `BOOST_CONFIG_NO_UTILITY_RECURSION`; includes `<utility>`; and restores macro state when the wrapper owns the temporary guard.

Control flow/dependencies: simple guard/setup/include/cleanup pattern. Depends only on `<utility>`.

State and persistence: temporary preprocessor state only.

Integration points: heavily used by standard-library selectors because `<utility>` is a small C++ standard header that exposes many vendor library macros.

Risks and test signals: risk is recursive inclusion or leaked recursion suppression. Test include path setups where Boost.TR1 appears before system headers and verify vendor macros remain visible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/utility.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/aix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/aix.hpp

Purpose: configures Boost platform macros for IBM AIX.

Important APIs/macros: defines `BOOST_PLATFORM "IBM Aix"`, POSIX/header capability macros including `BOOST_HAS_UNISTD_H`, `BOOST_HAS_NL_TYPES_H`, `BOOST_HAS_NANOSLEEP`, `BOOST_HAS_CLOCK_GETTIME`, and `BOOST_HAS_STDINT_H`, plus pthread-related macros `BOOST_HAS_PTHREADS`, `BOOST_HAS_PTHREAD_DELAY_NP`, and `BOOST_HAS_SCHED_YIELD`.

Control flow/dependencies: static macro definitions followed by inclusion of `boost/config/detail/posix_features.hpp` to derive any additional POSIX capabilities from `<unistd.h>`.

State and persistence: compile-time-only platform state.

Integration points: selected by `detail/select_platform_config.hpp` for `_AIX` or IBM compiler contexts not already matched by z/OS. Works with IBM compiler and standard-library configs.

Risks and test signals: risk is assuming pthread and timer APIs across AIX version/libc modes. Test compile/link checks for pthread delay/yield, `clock_gettime`, `nanosleep`, and `<stdint.h>` integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/aix.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/amigaos.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/amigaos.hpp

Purpose: declares a conservative Boost platform profile for AmigaOS.

Important APIs/macros: defines `BOOST_PLATFORM "AmigaOS"`, disables threading with `BOOST_DISABLE_THREADS`, and marks wide-character support unavailable with `BOOST_NO_CWCHAR`, `BOOST_NO_STD_WSTRING`, and `BOOST_NO_INTRINSIC_WCHAR_T`.

Control flow/dependencies: no includes and no conditionals beyond normal preprocessing. It is a fixed capability profile.

State and persistence: compile-time macro state only.

Integration points: selected by `detail/select_platform_config.hpp` when `__amigaos__` is defined. `suffix.hpp` expands the wide-character implications and removes thread detail macros.

Risks and test signals: risk is underrepresenting newer AmigaOS ports with better C++ runtime support. Test with Boost.Config probes for wchar, std::wstring, and thread support if a maintained AmigaOS toolchain is available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/amigaos.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/beos.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/beos.hpp

Purpose: configures Boost platform macros for BeOS.

Important APIs/macros: defines `BOOST_PLATFORM "BeOS"`, disables `<cwchar>` and `<cwctype>` with `BOOST_NO_CWCHAR` and `BOOST_NO_CWCTYPE`, enables `BOOST_HAS_UNISTD_H`, `BOOST_HAS_BETHREADS`, and conditionally `BOOST_HAS_THREADS` unless `BOOST_DISABLE_THREADS` is set.

Control flow/dependencies: static macros plus `boost/config/detail/posix_features.hpp` for POSIX feature derivation.

State and persistence: compile-time macro state only.

Integration points: selected when `__BEOS__` is present. Thread normalization in `suffix.hpp` recognizes `BOOST_HAS_BETHREADS` as a valid threading API.

Risks and test signals: risk is thread support mismatch when BeOS headers or libraries differ. Test with Be threading primitives, POSIX header probes, and wide-character compile tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/beos.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/bsd.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/bsd.hpp

Purpose: configures Boost for FreeBSD, NetBSD, OpenBSD, and DragonFly BSD.

Important APIs/macros: validates BSD identity, defines `BOOST_PLATFORM` with the specific BSD and version macro, conditionally enables `BOOST_HAS_NL_TYPES_H` and `BOOST_HAS_PTHREADS`, handles NetBSD libstdc++ `swprintf` visibility, and sets POSIX capabilities such as `BOOST_HAS_SCHED_YIELD`, `BOOST_HAS_NANOSLEEP`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_SIGACTION`, and `BOOST_HAS_CLOCK_GETTIME`. It may define `BOOST_NO_CWCHAR` and `BOOST_NO_CTYPE_FUNCTIONS`.

Control flow/dependencies: BSD-specific conditionals, then `BOOST_HAS_UNISTD_H` and `detail/posix_features.hpp`.

State and persistence: compile-time platform macros only.

Integration points: selected by platform selector for BSD macros. It feeds POSIX/thread availability into `suffix.hpp`.

Risks and test signals: risk is version checks lagging newer BSD releases or OpenBSD/DragonFly ctype differences. Test cwchar, ctype functions, pthreads, timers, and platform string generation per BSD.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/bsd.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/cloudabi.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/cloudabi.hpp

Purpose: declares Boost platform capabilities for Nuxi CloudABI.

Important APIs/macros: defines `BOOST_PLATFORM "CloudABI"` and enables headers/functions including `BOOST_HAS_DIRENT_H`, `BOOST_HAS_STDINT_H`, `BOOST_HAS_UNISTD_H`, `BOOST_HAS_CLOCK_GETTIME`, `BOOST_HAS_EXPM1`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_LOG1P`, `BOOST_HAS_NANOSLEEP`, `BOOST_HAS_PTHREADS`, and `BOOST_HAS_SCHED_YIELD`.

Control flow/dependencies: fixed macro table with no includes.

State and persistence: compile-time platform state only.

Integration points: selected when `__CloudABI__` is defined. `suffix.hpp` validates threading and derives standard helpers.

Risks and test signals: CloudABI is discontinued/niche, so the risk is stale feature declarations. Test by compiling probes for directory, pthread, clock, and math APIs with the CloudABI SDK if supported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/cloudabi.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/cray.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/cray.hpp

Purpose: provides a minimal platform configuration for Cray systems.

Important APIs/macros: defines `BOOST_PLATFORM "Cray"` and `BOOST_HAS_UNISTD_H`, then includes POSIX feature detection.

Control flow/dependencies: static definition plus `boost/config/detail/posix_features.hpp`. The detailed capabilities are derived from Cray's POSIX macros in `<unistd.h>`.

State and persistence: compile-time macro state only.

Integration points: selected by `detail/select_platform_config.hpp` when `_CRAYC` is defined, and compiler selection separately chooses the Cray compiler config.

Risks and test signals: risk is under-specificity across Cray programming environments. Test POSIX feature derivation, pthread availability, timers, and standard headers under the target Cray compiler/runtime modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/cray.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/cygwin.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/cygwin.hpp

Purpose: configures Boost for Cygwin, treating it as POSIX-like rather than native Win32.

Important APIs/macros: defines `BOOST_PLATFORM "Cygwin"`, `BOOST_HAS_DIRENT_H`, `BOOST_HAS_LOG1P`, `BOOST_HAS_EXPM1`, and `BOOST_HAS_UNISTD_H`. It includes `<unistd.h>` to choose pthreads versus Win32 threads, may define `BOOST_HAS_PTHREADS`, `BOOST_HAS_SCHED_YIELD`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_WINTHREADS`, and `BOOST_HAS_FTIME`. It detects `<stdint.h>` through `<sys/types.h>`, handles older Cygwin `BOOST_NO_FENV_H`, and disables shared mutex when pthread visibility macros are insufficient.

Control flow/dependencies: includes `<unistd.h>`, `<sys/types.h>`, `<cygwin/version.h>`, possibly `<pthread.h>`, then `detail/posix_features.hpp`; finally undefines `BOOST_HAS_NL_TYPES_H`.

State and persistence: compile-time platform state only.

Integration points: selected before Win32. Feeds both POSIX and Windows-adjacent thread behavior into Boost.

Risks and test signals: risk is Cygwin version and feature macro dependence. Test pthread versus WinThread selection, `shared_mutex` availability, fenv, stdint, and `nl_types` absence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/cygwin.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/haiku.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/haiku.hpp

Purpose: configures Boost platform macros for Haiku.

Important APIs/macros: defines `BOOST_PLATFORM "Haiku"`, `BOOST_HAS_UNISTD_H`, `BOOST_HAS_STDINT_H`, and conditionally `BOOST_HAS_THREADS`. It marks several C++11 features/headers unavailable: `BOOST_NO_CXX11_HDR_TYPE_TRAITS`, `BOOST_NO_CXX11_ATOMIC_SMART_PTR`, `BOOST_NO_CXX11_STATIC_ASSERT`, and `BOOST_NO_CXX11_VARIADIC_MACROS`. It explicitly enables `BOOST_HAS_SCHED_YIELD` and `BOOST_HAS_GETTIMEOFDAY`.

Control flow/dependencies: fixed macros followed by `detail/posix_features.hpp`.

State and persistence: compile-time macros only.

Integration points: selected when `__HAIKU__` is defined. Standard-library and compiler configs may override or add more specific C++ feature information.

Risks and test signals: risk is stale C++11 header assumptions as Haiku toolchains evolve. Test type_traits, atomic smart pointer, variadic macro, static assert, threads, and POSIX time APIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/haiku.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/hpux.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/hpux.hpp

Purpose: configures Boost for HP-UX.

Important APIs/macros: defines `BOOST_PLATFORM "HP-UX"`, conditionally enables `BOOST_HAS_STDINT_H`, marks `BOOST_NO_SWPRINTF` or `BOOST_NO_CWCTYPE` depending on compiler/source macros, and handles threading differently for GCC versus HP aCC. After POSIX detection it force-enables many capabilities such as `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_SCHED_YIELD`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_NL_TYPES_H`, `BOOST_HAS_NANOSLEEP`, `BOOST_HAS_DIRENT_H`, `BOOST_HAS_CLOCK_GETTIME`, `BOOST_HAS_SIGACTION`, `BOOST_HAS_LOG1P`, and `BOOST_HAS_EXPM1`. It sets `BOOST_HAS_NRVO` outside PA-RISC.

Control flow/dependencies: compiler/version conditionals, `BOOST_HAS_UNISTD_H`, `detail/posix_features.hpp`, then post-detection force macros.

State and persistence: compile-time platform state only.

Integration points: pairs with HP aCC or GCC compiler configs and drives POSIX/thread choices in `suffix.hpp`.

Risks and test signals: risk is HP-UX source-feature macro sensitivity and old GCC thread limitations. Test GCC versions, HP aCC, swprintf/cwctype, pthreads, timers, inttypes/stdint, and NRVO assumptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/hpux.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/irix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/irix.hpp

Purpose: configures Boost for SGI IRIX.

Important APIs/macros: defines `BOOST_PLATFORM "SGI Irix"`, disables `swprintf` with `BOOST_NO_SWPRINTF`, explicitly enables `BOOST_HAS_GETTIMEOFDAY` and `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, and disables threads for GNU C++ on IRIX.

Control flow/dependencies: small fixed configuration plus `BOOST_HAS_UNISTD_H` and `detail/posix_features.hpp`.

State and persistence: compile-time platform state only.

Integration points: pairs with `compiler/sgi_mipspro.hpp` for native compiler builds. `suffix.hpp` may remove thread support if no supported thread API remains.

Risks and test signals: risk is legacy toolchain scarcity and differences between native MIPSpro and GCC on IRIX. Test `swprintf`, pthread mutex attributes, gettimeofday, and thread-disable behavior under both compilers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/irix.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/linux.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/linux.hpp

Purpose: configures Boost platform macros for Linux and glibc-like systems.

Important APIs/macros: defines `BOOST_PLATFORM "linux"`, includes `<cstdlib>` or `<stdlib.h>` to expose glibc macros, enables `BOOST_HAS_STDINT_H` for suitable glibc/GCC combinations, handles old Comeau-on-Linux namespace and `swprintf` issues, enables `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_NANOSLEEP`, and optionally `BOOST_HAS_PTHREAD_YIELD`. It may define `BOOST_NO_SWPRINTF` when glibc or feature macros do not expose it.

Control flow/dependencies: libc/version checks, `BOOST_HAS_UNISTD_H`, `detail/posix_features.hpp`, GNU extension macro compatibility definitions for non-GCC compilers parsing glibc headers.

State and persistence: compile-time platform macro state only.

Integration points: selected for Linux, GNU, and glibc macros except Cray. Feeds standard POSIX/thread/math support to all Linux Boost builds.

Risks and test signals: risk is glibc feature macro dependence and non-GCC compiler parsing compatibility. Test under GCC, Clang, ICC/NVHPC, Android exclusions, old glibc, and strict C++ modes for `swprintf`, pthread yield, stdint, and GNU extension aliases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/linux.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/macos.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/macos.hpp

Purpose: configures Boost for classic Mac OS, macOS, and Metrowerks/MSL combinations.

Important APIs/macros: defines `BOOST_PLATFORM "Mac OS"`. For Mach builds outside MSL, it enables `BOOST_HAS_UNISTD_H`, includes POSIX features, forces `BOOST_HAS_STDINT_H`, `BOOST_HAS_SCHED_YIELD`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_SIGACTION`, and on GCC 4+ `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE` and `BOOST_HAS_NANOSLEEP`. It may define `BOOST_NO_STDC_NAMESPACE` for old GCC Apple modes. For Carbon/MSL it handles `BOOST_HAS_PTHREADS`, `BOOST_HAS_THREADS`, `BOOST_HAS_GETTIMEOFDAY`, and `BOOST_BIND_ENABLE_PASCAL`.

Control flow/dependencies: branches on `__MACH__` and `_MSL_USING_MSL_C`, then compiler/runtime-specific sections.

State and persistence: compile-time macros only.

Integration points: selected for `macintosh`, `__APPLE__`, or `__APPLE_CC__`. Works with compiler and MSL/libc++/libstdc++ stdlib configs.

Risks and test signals: risk is obsolete Carbon/MSL behavior versus modern Apple clang/libc++. Test POSIX APIs, pthread mutex attributes, namespace behavior, and platform selection on modern macOS and any supported legacy targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/macos.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/qnxnto.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/qnxnto.hpp

Purpose: configures Boost for QNX Neutrino.

Important APIs/macros: defines `BOOST_PLATFORM "QNX"`, `BOOST_HAS_UNISTD_H`, then includes POSIX feature detection. It deliberately undefines `BOOST_HAS_NL_TYPES_H`, `BOOST_HAS_LOG1P`, and `BOOST_HAS_EXPM1` because QNX advertises XOpen conformance without those facilities. It enables `BOOST_HAS_PTHREADS`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_CLOCK_GETTIME`, and `BOOST_HAS_NANOSLEEP`.

Control flow/dependencies: POSIX detection followed by corrective undefines and explicit QNX capabilities.

State and persistence: compile-time platform state only.

Integration points: selected by `__QNXNTO__`. Thread and time capability macros feed Boost.Thread, Chrono, and filesystem-adjacent code.

Risks and test signals: risk is XOpen macro overclaim or newer QNX versions adding removed facilities. Test nl_types, log1p/expm1, pthread mutex attrs, clock_gettime, and nanosleep.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/qnxnto.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/solaris.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/solaris.hpp

Purpose: configures Boost for Sun Solaris.

Important APIs/macros: defines `BOOST_PLATFORM "Sun Solaris"`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_UNISTD_H`, then includes POSIX detection. It removes `BOOST_HAS_PTHREADS` for GCC builds where `_POSIX_THREADS` is present but `_PTHREADS` is not, and explicitly enables `BOOST_HAS_STDINT_H`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_LOG1P`, and `BOOST_HAS_EXPM1`.

Control flow/dependencies: POSIX detection followed by Solaris/GCC thread correction and forced Solaris capabilities.

State and persistence: compile-time macros only.

Integration points: selected for `sun` or `__sun`; pairs with `compiler/sunpro_cc.hpp` or GCC/Clang configs.

Risks and test signals: risk is requiring correct compiler flags for pthreads, especially GCC `-pthreads`. Test thread detection with and without `_PTHREADS`, stdint, math functions, and mutex attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/solaris.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/symbian.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/symbian.hpp

Purpose: configures Boost for Symbian OS.

Important APIs/macros: defines Symbian platform identity and applies a constrained embedded/mobile platform profile. The file adjusts standard-library and system-feature availability for Symbian, including threading, POSIX-like APIs, wide-character/string support, and C++ standard library gaps.

Control flow/dependencies: platform-specific preprocessor checks for Symbian SDK/compiler variants and optional includes. It is selected by `detail/select_platform_config.hpp` when `__SYMBIAN32__` is defined.

State and persistence: compile-time configuration only.

Integration points: interacts with compiler and stdlib configs for older mobile toolchains and lets `suffix.hpp` normalize disabled standard-library and thread features.

Risks and test signals: Symbian is legacy; the primary risk is stale SDK assumptions and untested combinations. Test signals are Boost.Config probes for threading, filesystem-like POSIX functions, wide-character support, exception/RTTI compatibility, and C++ library headers on the target SDK.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/symbian.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/vms.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/vms.hpp

Purpose: configures Boost platform macros for OpenVMS.

Important APIs/macros: include guard `BOOST_CONFIG_PLATFORM_VMS_HPP`, defines `BOOST_PLATFORM "OpenVMS"`, undefines `BOOST_HAS_STDINT_H`, enables `BOOST_HAS_UNISTD_H`, `BOOST_HAS_NL_TYPES_H`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_DIRENT_H`, `BOOST_HAS_PTHREADS`, `BOOST_HAS_NANOSLEEP`, `BOOST_HAS_CLOCK_GETTIME`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_LOG1P`, `BOOST_HAS_EXPM1`, and `BOOST_HAS_THREADS`, and undefines `BOOST_HAS_SCHED_YIELD`.

Control flow/dependencies: fixed macro table with no POSIX feature include.

State and persistence: compile-time platform state only.

Integration points: selected by `__VMS`. Thread support is explicitly enabled and recognized by `suffix.hpp` because `BOOST_HAS_PTHREADS` is present.

Risks and test signals: risk is stdint absence and scheduler-yield behavior differing across OpenVMS versions. Test directory, pthread, clock, math, stdint, and sched_yield probes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/vms.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/vxworks.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/vxworks.hpp

Purpose: provides a deep Boost platform adaptation for VxWorks 6.9/7 and later-supported environments.

Important APIs/macros: validates `_WRS_VXWORKS_MAJOR >= 6`, defines `BOOST_PLATFORM "vxWorks"`, enables common headers and functions, pthreads, timers, `BOOST_LOCALE_WITH_ICU`, and ASIO serial/stream descriptor behavior. It corrects old VxWorks integer constant macros, declares or implements missing functions such as `getrlimit`, `setrlimit`, `truncate`, `symlink`, `readlink`, `gettimeofday`, `times`, `lstat`, and compatibility macros like `S_ISSOCK`, `FPE_FLTINV`, and `locale_t`. It disables many C++11 headers/features unless VxWorks 7 C++11 library configuration macros are present.

Control flow/dependencies: includes VxWorks headers (`version.h`, `<cstdint>`, `<sys/time.h>`, `<ioLib.h>`, `<tickLib.h>`, `<signal.h>` and others conditionally), defines inline C/C++ shim functions, then includes POSIX feature detection and cleans up misleading macros.

State and persistence: mostly compile-time macros, plus inline compatibility functions with no persisted state.

Integration points: selected by `__VXWORKS__`; affects Boost.Locale, Asio, Chrono, filesystem-like code, threading, and standard-library feature gates.

Risks and test signals: high risk because it declares replacement APIs and changes system macros. Test RTP versus DKM, VxWorks 6 versus 7, symlink/readlink failure semantics, truncate/gettimeofday/times shims, pthread priority inheritance notes, integer constants, and C++11 library configuration modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/vxworks.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/wasm.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/wasm.hpp

Purpose: configures Boost for WebAssembly targets.

Important APIs/macros: defines `BOOST_PLATFORM "Wasm"`, uses `__has_include(<unistd.h>)` to set `BOOST_HAS_UNISTD_H`, includes POSIX feature detection, and defines `BOOST_NO_FENV_H` because fenv lacks the expected C++11 macros.

Control flow/dependencies: optional unistd detection, then `boost/config/detail/posix_features.hpp`, then fenv correction.

State and persistence: compile-time macro state only.

Integration points: selected by `__wasm__`. Feeds platform identity and conservative fenv capability into Boost.Math and other numeric code.

Risks and test signals: WebAssembly environments vary by libc (Emscripten, WASI, custom). Test unistd presence, POSIX macro derivation, fenv header behavior, pthread modes, and standard-library header availability per target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/wasm.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/win32.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/win32.hpp

Purpose: configures Boost for native Win32 and related Windows targets.

Important APIs/macros: defines `BOOST_PLATFORM "Win32"`, may include `<_mingw.h>`, disables `swprintf` for GCC, defines default `BOOST_SYMBOL_EXPORT` and `BOOST_SYMBOL_IMPORT` as `__declspec(dllexport/dllimport)` plus `BOOST_HAS_DECLSPEC`, enables MinGW `BOOST_HAS_STDINT_H`, `BOOST_HAS_DIRENT_H`, `BOOST_HAS_UNISTD_H`, and `BOOST_HAS_GETTIMEOFDAY`, defaults to `BOOST_HAS_WINTHREADS` unless pthreads are already selected, handles WinCE/Windows Runtime with `BOOST_NO_ANSI_APIS`, and enables `BOOST_HAS_GETSYSTEMTIMEASFILETIME`, `BOOST_HAS_THREADEX`, `BOOST_HAS_FTIME`, and `BOOST_WINDOWS`.

Control flow/dependencies: Windows and MinGW conditionals; no POSIX feature include.

State and persistence: compile-time platform macros only.

Integration points: selected after Cygwin. Pairs with MSVC, MinGW GCC/Clang, and Dinkumware/MSVC STL configs. Symbol macros are used by Boost shared libraries.

Risks and test signals: risk is MinGW runtime version handling, WinCE/WinRT API restrictions, and symbol visibility defaults. Test native MSVC, clang-cl, MinGW, WinCE/WinRT, pthreads-for-Windows, auto-link, and dll import/export behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/win32.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/zos.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/platform/zos.hpp

Purpose: configures Boost platform macros for IBM z/OS.

Important APIs/macros: defines `BOOST_PLATFORM "IBM z/OS"`, includes `<features.h>`, conditionally enables `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_PTHREADS`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_THREADS`, and `BOOST_HAS_SCHED_YIELD`, and always enables `BOOST_HAS_SIGACTION`, `BOOST_HAS_UNISTD_H`, `BOOST_HAS_DIRENT_H`, and `BOOST_HAS_NL_TYPES_H`.

Control flow/dependencies: z/OS feature macros such as `__UU`, `_OPEN_THREADS`, `__SUSV3_THR`, and `__SUSV3` drive capability macros.

State and persistence: compile-time macro state only.

Integration points: pairs with `compiler/xlcpp_zos.hpp` and `stdlib/xlcpp_zos.hpp`. Thread and POSIX macros feed `suffix.hpp` validation.

Risks and test signals: risk is z/OS feature-mode dependence. Test with and without Unix System Services/thread feature macros, plus sigaction, dirent, nl_types, sched_yield, and gettimeofday probes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/platform/zos.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/pragma_message.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/pragma_message.hpp

Purpose: provides a portable `BOOST_PRAGMA_MESSAGE("message")` macro.

Important APIs/macros: if `BOOST_DISABLE_PRAGMA_MESSAGE` is set, the macro expands to nothing. Intel and MSVC use `__pragma(message(...))` with file and line context. GCC uses `_Pragma(BOOST_STRINGIZE(message(x)))`. Other compilers receive a no-op.

Control flow/dependencies: includes `boost/config/helper_macros.hpp` for `BOOST_STRINGIZE`, then compiler-specific macro branches.

State and persistence: no runtime state; affects compile diagnostics only.

Integration points: used by `header_deprecated.hpp`, `visualc.hpp`, and other config diagnostics that should not hard-code pragma syntax.

Risks and test signals: risk is malformed pragma syntax or too much diagnostic noise. Test with MSVC, GCC, Clang-as-GCC, Intel, disabled messages, and messages containing macro-expanded strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/pragma_message.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/requires_threads.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/requires_threads.hpp

Purpose: hard-fails compilation when a Boost component requiring threading is used without configured thread support.

Important APIs/macros: includes `boost/config.hpp` if needed, then emits compiler-specific `#error` messages when `BOOST_DISABLE_THREADS` is set or `BOOST_HAS_THREADS` is absent. Messages recommend flags for Comeau, Intel, GCC, SGI MIPSpro, DEC CXX, Borland, Metrowerks, SunPro, HP aCC, IBM VisualAge, and MSVC.

Control flow/dependencies: first handles explicit disable, including special GCC-on-HPUX/IRIX errors; otherwise checks missing `BOOST_HAS_THREADS` and selects a compiler-specific diagnostic branch.

State and persistence: compile-time error behavior only.

Integration points: Boost libraries that require threading include this header to fail early with an actionable message rather than compiling partially unsupported code.

Risks and test signals: risk is stale compiler flag advice and misspelled diagnostics. Test by compiling thread-requiring Boost headers with threads disabled or missing across major compilers, and with `BOOST_DISABLE_THREADS` explicitly set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/requires_threads.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/dinkumware.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/dinkumware.hpp

Purpose: configures Boost for Dinkumware and the Microsoft STL family.

Important APIs/macros: validates detection through `_YVALS` or `_CPPLIB_VER`, defines `BOOST_DINKUMWARE_STDLIB`, `BOOST_MSSTL_VERSION`, and `BOOST_STDLIB`, sets namespace/allocator/locale workarounds, maps `BOOST_STD_EXTENSION_NAMESPACE` to `stdext` for newer MSVC, and marks standard headers/features unavailable by `_CPPLIB_VER`, `_HAS_CXX17`, `_HAS_CXX20`, `_MSVC_STL_UPDATE`, `_MSVC_STL_VERSION`, and related macros. It handles deprecated C++98 facilities (`BOOST_NO_AUTO_PTR`, binders, `random_shuffle`), CLR exclusions, codecvt deprecation, pointer traits, addressof, shared mutex, C++17 apply/invoke/iterator traits, and C++20 concepts.

Control flow/dependencies: may include `no_tr1/utility.hpp`, `<exception>`, and `<typeinfo>` in special no-exception MSVC/clang-cl cases. Most logic is version thresholds.

State and persistence: compile-time standard-library state only.

Integration points: selected for MSVC STL/Dinkumware. Pairs with `compiler/visualc.hpp` and `platform/win32.hpp`, but also supports other compilers using Dinkumware.

Risks and test signals: high risk due to many MSVC STL version and language-mode combinations. Test VS2010 through current, clang-cl, `_HAS_CXX17/_HAS_CXX20`, CLR, no exceptions, deprecated facility toggles, codecvt, shared_mutex, pointer_traits, and feature-test macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/dinkumware.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/libcomo.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/libcomo.hpp

Purpose: configures Boost for the Comeau standard library.

Important APIs/macros: validates `__LIBCOMO__`, defines `BOOST_STDLIB`, handles old `std::wstreambuf` and Windows `swprintf` issues, enables `BOOST_HAS_HASH` and `BOOST_HAS_SLIST` for newer versions, marks all C++11 headers and library facilities unavailable, disables C++14 shared mutex/exchange and C++17 apply/invoke/iterator traits, and defines `BOOST_HAS_SGI_TYPE_TRAITS`.

Control flow/dependencies: may include `boost/config/no_tr1/utility.hpp` to expose `__LIBCOMO__`; then uses `__LIBCOMO_VERSION__` thresholds and fixed missing-feature macros.

State and persistence: compile-time standard-library state only.

Integration points: selected by `select_stdlib_config.hpp` for `__LIBCOMO__`. Influences old extension container detection and type-traits paths.

Risks and test signals: risk is obsolete library support and broad disabling of C++11+ features. Test version detection, hash/slist availability, wstreambuf, swprintf on Windows, and absence of modern headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/libcomo.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/libcpp.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/libcpp.hpp

Purpose: configures Boost for LLVM libc++.

Important APIs/macros: validates `_LIBCPP_VERSION`, defines `BOOST_STDLIB`, enables `BOOST_HAS_THREADS`, and maps libc++ feature macros/version thresholds to `BOOST_NO_CXX11_*`, `BOOST_NO_CXX14_*`, `BOOST_NO_CXX17_*`, and newer header capability macros. It handles no variadics/template aliases, C++03 mode, old incomplete atomic/chrono/type_traits/future support, `BOOST_NO_STD_MESSAGES`, C++14 exchange/shared_mutex, C++17 optional/string_view/variant/execution/invoke, removed C++98 facilities, span issues, thread_local problems with old libc++abi/Linux, and iterator traits.

Control flow/dependencies: may include `<ciso646>` for detection and `<version>` when present. Uses `_LIBCPP_VERSION`, `__cplusplus`, `__has_include`, and `__cpp_lib_*` macros.

State and persistence: compile-time standard-library configuration only.

Integration points: selected by `_LIBCPP_VERSION`. Pairs with Clang, Apple Clang, and other libc++ users; `suffix.hpp` consumes its feature macros.

Risks and test signals: risk is version thresholds not matching vendor-patched libc++ distributions. Test across Apple and upstream libc++, C++03/11/14/17/20 modes, `<version>` presence, thread_local linking, shared_mutex, execution, invoke, and removed auto_ptr/binders/random_shuffle toggles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/libcpp.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/libstdcpp3.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/libstdcpp3.hpp

Purpose: configures Boost for GNU libstdc++ version 3 and newer.

Important APIs/macros: identifies libstdc++ through `__GLIBCPP__` or `__GLIBCXX__`, defines a `BOOST_STDLIB` string, handles extension namespace and C++ library header availability, and maps libstdc++ release macros, language mode, and feature-test macros to `BOOST_NO_CXX11/14/17/20/23_*`. It covers headers such as array, chrono, thread, tuple, type_traits, unordered containers, shared_mutex, optional, string_view, variant, any, filesystem, charconv, execution, memory_resource, and newer C++20/23 headers. It also handles deprecated C++98 facilities and special compiler/library combinations.

Control flow/dependencies: primarily preprocessor version and `__has_include` checks, sometimes relying on `<version>` having been included by the selector/suffix path.

State and persistence: compile-time standard-library state only.

Integration points: selected for GCC/libstdc++ and many Clang-on-Linux builds unless libc++ is used. Its macros are normalized by `suffix.hpp` and drive large parts of Boost's standard-library adaptation.

Risks and test signals: risk is distro-patched libstdc++ and mismatch between compiler language mode and library feature macros. Test GCC/Clang with libstdc++ in C++03 through C++23 modes, old dual ABI versions, filesystem/charconv/execution availability, shared_mutex, and deprecated auto_ptr/binders switches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/libstdcpp3.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/modena.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/modena.hpp

Purpose: configures Boost for the Modena C++ standard library.

Important APIs/macros: validates Modena detection through `MSIPL_COMPILE_H`, defines `BOOST_STDLIB`, and marks a broad set of standard-library facilities unavailable, especially C++11 headers, allocator/pointer traits/smart pointer/addressof/std::align, C++14 shared mutex/exchange, and C++17 apply/invoke/iterator traits.

Control flow/dependencies: may include `boost/config/no_tr1/utility.hpp` to expose the library macro, then applies a fixed legacy-library profile.

State and persistence: compile-time standard-library state only.

Integration points: selected by `select_stdlib_config.hpp` when `MSIPL_COMPILE_H` is found. Downstream Boost libraries use the `BOOST_NO_*` macros to avoid unavailable standard APIs.

Risks and test signals: risk is rare-library bit rot and unsupported modern standard facilities. Test detection, locale/iterator/allocator basics, and compile probes for all headers marked unavailable if supporting Modena remains a requirement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/modena.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/msl.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/msl.hpp

Purpose: configures Boost for Metrowerks MSL.

Important APIs/macros: validates `__MSL_CPP__`, defines `BOOST_STDLIB`, applies version-specific workarounds for C standard namespace, `swprintf`, `std::locale`, `std::messages`, `std::wstring`, and allocator behavior, and marks modern C++ standard headers and facilities unavailable where MSL lacks them.

Control flow/dependencies: detection may use a `no_tr1` wrapper to include a standard header, then conditionals use MSL version/configuration macros.

State and persistence: compile-time standard-library state only.

Integration points: commonly pairs with Metrowerks compiler and Mac platform configurations. `suffix.hpp` derives locale, wide-character, and allocator implication macros from this profile.

Risks and test signals: risk is old CodeWarrior/MSL version fragmentation. Test namespace imports, locale facets, wide strings, allocator/rebind support, `swprintf`, and modern header absence under supported MSL versions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/msl.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/roguewave.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/roguewave.hpp

Purpose: configures Boost for Rogue Wave standard libraries.

Important APIs/macros: defines `BOOST_RW_STDLIB`, normalizes `_RWSTD_VER` into `BOOST_RWSTD_VER`, defines `BOOST_STDLIB`, and applies version-specific workarounds for namespace support, allocator, iterator traits, locale/facet use, stringstream, wide-character support, long long numeric limits, and template instantiation behavior. It marks C++11 headers/facilities, C++14 shared mutex/exchange, and C++17 apply/invoke/iterator traits unavailable.

Control flow/dependencies: validates with `__STD_RWCOMPILER_H__` or `_RWSTD_VER`, possibly through `no_tr1/utility.hpp`; then uses version thresholds and compiler/library macros.

State and persistence: compile-time standard-library state only.

Integration points: selected by `select_stdlib_config.hpp` for Rogue Wave macros. Downstream Boost code uses its facet and locale macros through `suffix.hpp` helpers.

Risks and test signals: risk is old vendor variants with incompatible `_RWSTD_VER` encodings. Test version normalization, locale/use_facet macros, iterator traits, allocator, wstring/wstreambuf, and absence of C++11+ headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/roguewave.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/sgi.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/sgi.hpp

Purpose: configures Boost for the generic SGI STL.

Important APIs/macros: validates `__STL_CONFIG_H`, defines `BOOST_STDLIB "SGI standard library"`, marks missing iterator traits, stringstream, locale, messages facet, templated iterator constructors, std allocator, std iterator, limits, and std::wstring based on SGI STL/compiler macros. It enables `BOOST_HAS_HASH`, `BOOST_HAS_SLIST`, and `BOOST_HAS_SGI_TYPE_TRAITS`, and disables most C++11 standard headers/facilities plus C++14 shared mutex/exchange and C++17 apply/invoke/iterator traits.

Control flow/dependencies: may include `no_tr1/utility.hpp`, `<unistd.h>`, and `<string>` depending on platform/compiler checks.

State and persistence: compile-time standard-library state only.

Integration points: selected when `__STL_CONFIG_H` is detected and not STLPort. Feeds extension container and SGI type-trait support into older Boost code.

Risks and test signals: risk is old libstdc++2/SGI STL edge cases and Apple macros. Test hash/slist headers, type traits, iterator traits, locale/messages, stringstream, and wide string support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/sgi.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/stlport.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/stlport.hpp

Purpose: configures Boost for STLPort.

Important APIs/macros: validates `__SGI_STL_PORT` or `_STLPORT_VERSION`, defines `BOOST_STDLIB`, handles static constant initialization, partial specialization/iterator traits, stringstream/new iostreams, locale, TR1 unordered containers, member templates, allocator/rebind, wide-character/string support, SGI hash/slist extensions, standard C namespace imports, use_facet variants, Borland-specific fixes, and GCC 2 min/max ADL workarounds. It marks most C++11 headers/facilities, C++14 shared mutex/exchange, and C++17 apply/invoke/iterator traits unavailable.

Control flow/dependencies: may include `<cstddef>`, `<unistd.h>`, `<stdlib.h>`, `<string.h>`, and `<algorithm>` in targeted branches.

State and persistence: compile-time macros plus a few namespace using declarations for old Borland/GCC cases.

Integration points: selected before underlying libraries because STLPort may wrap another vendor STL. `suffix.hpp` uses its locale, allocator, wide-character, and extension container macros.

Risks and test signals: risk is wrapper-library detection, namespace import side effects, and compiler-specific old STLPort configurations. Test STLPort 4/5, Borland, GCC 2.95, namespace modes, hash/slist, locale facets, allocator, and wide-character support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/stlport.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/vacpp.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/vacpp.hpp

Purpose: configures Boost for the IBM VisualAge default standard library.

Important APIs/macros: disables `BOOST_NO_STD_ALLOCATOR` for `__IBMCPP__ <= 501`, defines `BOOST_HAS_MACRO_USE_FACET` and `BOOST_NO_STD_MESSAGES`, optionally includes `<unistd.h>` on Unix-like systems, marks C++11 headers/facilities unavailable, disables C++14 shared mutex/exchange, disables C++17 apply/invoke/iterator traits, and defines `BOOST_STDLIB "Visual Age default standard library"`.

Control flow/dependencies: simple IBM version check, Unix platform include guard, then fixed legacy standard-library feature profile.

State and persistence: compile-time standard-library macros only.

Integration points: selected for `__IBMCPP__` when z/OS is not active. Pairs with `compiler/vacpp.hpp` and often `platform/aix.hpp`.

Risks and test signals: risk is assuming old VisualAge library limitations for newer IBM XL configurations. Test allocator, locale facet macros, messages facet, C++11 header availability, and Unix include behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/vacpp.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/xlcpp_zos.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/xlcpp_zos.hpp

Purpose: configures Boost for the IBM z/OS XL C/C++ standard library V2R1.

Important APIs/macros: validates `__TARGET_LIB__ >= 0x42010000`, emits `BOOST_ASSERT_CONFIG` for newer unknown library versions, defines `BOOST_STDLIB`, `BOOST_HAS_MACRO_USE_FACET`, and a conservative set of missing C++11/14/17 standard library facilities including type_traits, initializer_list, addressof, smart pointers, allocator/pointer_traits, most C++11 headers, std::align, shared_mutex, exchange, invoke, apply, and iterator traits.

Control flow/dependencies: version gate followed by a fixed missing-feature profile.

State and persistence: compile-time standard-library state only.

Integration points: selected with z/OS compiler/platform configs. Locale facet handling flows through `BOOST_USE_FACET` in `suffix.hpp`.

Risks and test signals: risk is strict version support and broad feature disabling if z/OS library updates add facilities. Test `__TARGET_LIB__` values, locale facet macros, all marked standard headers, allocator/smart pointer support, and C++14/17 library features.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/xlcpp_zos.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/user.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/user.hpp

Purpose: template site-configuration header for Boost users. It is intentionally unmodified in Boost distributions and documents user-overridable config macros.

Important APIs/macros: it does not define active macros by default. Comments describe overrides such as `BOOST_COMPILER_CONFIG`, `BOOST_STDLIB_CONFIG`, `BOOST_PLATFORM_CONFIG`, `BOOST_NO_*_CONFIG`, `BOOST_NO_CONFIG`, `BOOST_STRICT_CONFIG`, `BOOST_ASSERT_CONFIG`, `BOOST_DISABLE_THREADS`, `BOOST_DISABLE_WIN32`, ABI prefix/suffix overrides, dynamic-link controls (`BOOST_ALL_DYN_LINK`, `BOOST_WHATEVER_DYN_LINK`), auto-link disables (`BOOST_ALL_NO_LIB`, `BOOST_WHATEVER_NO_LIB`), and `BOOST_LIB_BUILDID`.

Control flow/dependencies: no includes or active conditionals. It is included by Boost.Config as a customization point.

State and persistence: none by default; if users edit/copy it, it controls compile-time configuration for all translation units that include Boost.

Integration points: the first policy layer for `boost/config.hpp`, preceding automatic compiler/platform/stdlib selection.

Risks and test signals: risk is inconsistent local edits across translation units, causing ABI or feature mismatches. Test by auditing build defines and ensuring user overrides are centralized and identical for all Boost-consuming targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/user.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/warning_disable.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/warning_disable.hpp

Purpose: disables selected overly-pedantic compiler warnings for test cases or library source files.

Important APIs/macros: for MSVC 1400+ it disables warning C4996 for deprecated standard-library functions. For Intel (`__INTEL_COMPILER` or `__ICL`) it disables warning 1786 for similar deprecated-library diagnostics.

Control flow/dependencies: include guard and compiler-specific `#pragma warning(disable:...)` branches. The file intentionally includes no headers so warning suppression can happen before standard-library headers emit warnings.

State and persistence: compiler diagnostic state for the including translation unit.

Integration points: intended for tests or source files, explicitly not for normal Boost headers. It complements but does not depend on `boost/config.hpp`.

Risks and test signals: risk is hiding warnings that should be fixed or including it too late to matter. Test by compiling affected MSVC/Intel standard-library uses with and without the header and verifying no unrelated warnings are suppressed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/warning_disable.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/workaround.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/workaround.hpp

Purpose: provides Boost's version-aware workaround macros for compiler/library defects.

Important APIs/macros: defines `BOOST_WORKAROUND(symbol, test)` and `BOOST_TESTED_AT(value)`. In non-`BOOST_STRICT_CONFIG` mode it includes `boost/config.hpp`, defines many `*_WORKAROUND_GUARD` macros so undefined version symbols are safe to test, and implements the workaround expression using arithmetic that evaluates to true only when the symbol exists and satisfies the test. With `BOOST_DETECT_OUTDATED_WORKAROUNDS`, `BOOST_TESTED_AT` can intentionally cause diagnostics/errors when a compiler version exceeds the last tested version. In strict mode `BOOST_WORKAROUND` always expands to `0`.

Control flow/dependencies: guard macro definitions for many compiler and library version symbols, then macro implementation. No runtime code.

State and persistence: compile-time macro logic only.

Integration points: used throughout Boost to gate small compiler/library-specific code paths while documenting the last tested version.

Risks and test signals: risk is brittle preprocessor arithmetic and missing guard symbols for new config macros. Test undefined symbol cases, normal comparisons, `BOOST_TESTED_AT`, strict config, outdated workaround detection, and compilers with unusual preprocessor behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/workaround.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_integral.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_integral.hpp

Purpose: implements `boost::hash_value` for integral types, including compiler-provided 128-bit integers not always recognized by standard type traits.

Important APIs/types/functions: in `boost::hash_detail`, defines wrappers `is_integral<T>`, `is_unsigned<T>`, and `make_unsigned<T>` over standard traits, with `__int128_t` and `__uint128_t` specializations when `__SIZEOF_INT128__` is defined. Defines primary template `hash_integral_impl<T, bigger_than_size_t, is_unsigned, size_t_bits, type_bits>` plus specializations for small values, signed larger-than-size_t values, unsigned 64-bit values on 32-bit `size_t`, unsigned 128-bit values on 32-bit `size_t`, and unsigned 128-bit values on 64-bit `size_t`. Public API is `template <typename T> enable_if<is_integral<T>::value, size_t>::type boost::hash_value(T v)`.

Control flow/dependencies: includes `hash_mix.hpp`, `<type_traits>`, `<cstddef>`, and `<climits>`. Small integral values cast directly to `size_t`. Large signed values convert through unsigned magnitude handling so negative values hash via bitwise complement. Large unsigned values split into 32- or 64-bit limbs and fold each limb with `hash_mix(seed)`.

State and persistence: stateless pure hashing; no persistent state.

Integration points: used by Boost.ContainerHash as the integral overload behind `boost::hash`. Depends on `hash_mix` avalanche quality for values wider than `size_t`.

Risks and test signals: risk is platform assumptions around `__int128_t` names, signed negative conversion, and unsupported `size_t` widths beyond 32/64. Tests should cover all standard integral types, bool/char variants, signed negatives, 64-bit integers on 32-bit targets, 128-bit integers on GCC/Clang, and SFINAE exclusion for non-integral types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_integral.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_mix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_mix.hpp

Purpose: provides the final avalanche/mixing function used by Boost.ContainerHash for `std::size_t` hash values.

Important APIs/types/functions: in `boost::hash_detail`, declares `template<std::size_t Bits> struct hash_mix_impl`, specializes it for 64-bit and 32-bit `size_t`, and exposes `inline std::size_t hash_mix(std::size_t v)`. The 64-bit specialization uses Jon Maiga's mx3-style multiply/xor mixer with constant `0xe9846af9b1a615d`. The 32-bit specialization uses a hash-prospector xmxmx mixer with constants `0x21f0aaad` and `0x735a2d97`.

Control flow/dependencies: includes `<cstdint>`, `<cstddef>`, and `<climits>`. `hash_mix` selects the specialization by `sizeof(std::size_t) * CHAR_BIT`; unsupported sizes fail at compile time because no specialization exists.

State and persistence: pure deterministic function; no state, allocation, IO, or persistence.

Integration points: consumed by `hash_integral.hpp` and other Boost.ContainerHash internals to avalanche seeds and limbs. Its behavior affects hash distribution and therefore unordered-container performance.

Risks and test signals: risks include lack of specialization for unusual `size_t` widths and accidental constant/type truncation if ported. Tests should verify deterministic outputs for known 32-bit and 64-bit inputs, avalanche/smhasher-style distribution checks, and successful integration with multi-limb integral hashing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_mix.hpp -->
