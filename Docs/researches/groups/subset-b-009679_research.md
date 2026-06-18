# subset-b-009679 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/unix.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/unix.h

Purpose: Detects generic Unix and SVR4 compilation environments for Boost.Predef. It defines `BOOST_OS_UNIX` and `BOOST_OS_SVR4`, plus availability/name macros, using only preprocessor feature macros.

Important APIs, types, and functions: Public API is macro-only: `BOOST_OS_UNIX`, `BOOST_OS_UNIX_AVAILABLE`, `BOOST_OS_UNIX_NAME`, `BOOST_OS_SVR4`, `BOOST_OS_SVR4_AVAILABLE`, and `BOOST_OS_SVR4_NAME`. It declares Predef tests with `BOOST_PREDEF_DECLARE_TEST`.

Control flow: Both macros start as `BOOST_VERSION_NUMBER_NOT_AVAILABLE`. `BOOST_OS_UNIX` becomes available when `unix`, `__unix`, `_XOPEN_SOURCE`, or `_POSIX_SOURCE` is defined. `BOOST_OS_SVR4` becomes available for System V markers such as `__sysv__`, `__SVR4`, `__svr4__`, or `_SYSTYPE_SVR4`.

State and persistence behavior: No runtime state or persistence exists; all behavior is compile-time macro state. Unlike more specific OS detectors, this file does not include `os_detected.h`, so it can coexist as an environment tag.

Dependencies and integration points: Depends on `boost/predef/version_number.h`, `boost/predef/make.h`, and `boost/predef/detail/test.h`. It is normally pulled by broader `boost/predef/os.h` or `boost/predef.h`.

Risks: Detection is intentionally broad; POSIX/X/Open feature macros can be defined on non-traditional Unix targets. Consumers needing a specific kernel or OS should prefer specific Predef OS macros.

Test signals: Boost.Predef self-test declarations exercise the resulting macro values when generated tests are enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/unix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/vms.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/vms.h

Purpose: Detects OpenVMS/VMS as the active operating system for Boost.Predef.

Important APIs, types, and functions: Defines `BOOST_OS_VMS`, `BOOST_OS_VMS_AVAILABLE`, and `BOOST_OS_VMS_NAME`. If `__VMS_VER` exists, it converts that native version to Boost's numeric representation with `BOOST_PREDEF_MAKE_10_VVRR00PP00`.

Control flow: The macro starts as not available. If no prior OS detector has set `BOOST_PREDEF_DETAIL_OS_DETECTED` and either `VMS` or `__VMS` exists, the file sets `BOOST_OS_VMS` to the converted `__VMS_VER` or generic available value. A successful detection includes `boost/predef/detail/os_detected.h` to reserve the OS slot.

State and persistence behavior: Compile-time-only. The detection side effect is the shared OS-detected marker, preventing later OS headers from claiming the same compilation target.

Dependencies and integration points: Uses Boost.Predef version/make helpers and the test declaration header. It integrates with the one-OS selection convention used by `boost/predef/os.h`.

Risks: If another OS detector is included first and marks the target, VMS detection is suppressed. Version parsing depends on `__VMS_VER` keeping the expected decimal layout.

Test signals: `BOOST_PREDEF_DECLARE_TEST(BOOST_OS_VMS, BOOST_OS_VMS_NAME)` provides the generated-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/vms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/windows.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/windows.h

Purpose: Detects Microsoft Windows as the active operating system for Boost.Predef.

Important APIs, types, and functions: Defines `BOOST_OS_WINDOWS`, `BOOST_OS_WINDOWS_AVAILABLE`, and `BOOST_OS_WINDOWS_NAME`.

Control flow: The detector starts with `BOOST_VERSION_NUMBER_NOT_AVAILABLE`. If no previous OS was detected and `_WIN32`, `_WIN64`, `__WIN32__`, `__TOS_WIN__`, or `__WINDOWS__` is defined, it sets `BOOST_OS_WINDOWS` to `BOOST_VERSION_NUMBER_AVAILABLE` and includes `os_detected.h`.

State and persistence behavior: No runtime state. The only state is preprocessor state, especially the shared `BOOST_PREDEF_DETAIL_OS_DETECTED` marker that serializes OS detection.

Dependencies and integration points: Uses Boost.Predef version/make support and generated test hooks. Windows platform-family headers such as `windows_uwp.h` and `windows_desktop.h` depend on this macro before making finer-grained platform decisions.

Risks: The macro reports the Windows OS but not SDK family, desktop/UWP capabilities, or MinGW flavor. Consumers must combine it with platform detectors for those distinctions.

Test signals: The declared Predef test checks the final `BOOST_OS_WINDOWS` value in Boost's generated test mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/windows.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/other.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/other.h

Purpose: Aggregates miscellaneous Boost.Predef detectors that are not operating-system, compiler, language, architecture, or library detectors.

Important APIs, types, and functions: It does not define new direct feature macros. It includes `boost/predef/other/endian.h`, `boost/predef/other/wordsize.h`, and `boost/predef/other/workaround.h`.

Control flow: The include guard permits normal one-time inclusion and also supports `BOOST_PREDEF_INTERNAL_GENERATE_TESTS`, matching other Boost.Predef aggregator headers.

State and persistence behavior: No runtime state. It introduces compile-time macro state from its included child headers.

Dependencies and integration points: Used by broader Boost.Predef aggregation to expose endianness, architecture word size, and workaround comparison helpers from one include.

Risks: Including this header can transitively include architecture and platform headers through `endian.h` and `wordsize.h`; this is expected but can alter available detection macros in translation units.

Test signals: Child headers carry their own `BOOST_PREDEF_DECLARE_TEST` declarations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/other.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/other/endian.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/other/endian.h

Purpose: Conservatively detects byte and word endianness for Boost.Predef. It exposes four mutually searched categories: big-byte, big-word, little-byte, and little-word.

Important APIs, types, and functions: Defines `BOOST_ENDIAN_BIG_BYTE`, `BOOST_ENDIAN_BIG_WORD`, `BOOST_ENDIAN_LITTLE_BYTE`, `BOOST_ENDIAN_LITTLE_WORD`, corresponding `*_AVAILABLE` macros, and name macros. Public behavior is macro-only.

Control flow: All endian macros begin as not available. The detector first tries system headers (`endian.h`, `machine/endian.h`, or `sys/endian.h`) for GNU libc, Android, OpenBSD, macOS, and BSD targets. It then checks `__BYTE_ORDER` or `_BYTE_ORDER`. If still unknown, it checks compiler/architecture markers such as ARM/MIPS endian variants, LoongArch, RISC-V, and E2K. It finally falls back to known fixed-endian Boost architecture macros and treats Windows on ARM as little-endian.

State and persistence behavior: Compile-time-only. It stops further detection once any endian category is set, so earlier reliable OS headers take precedence over generic architecture assumptions.

Dependencies and integration points: Depends on Boost.Predef C library, OS, platform, and architecture detectors. Hash-table code in this vendored Boost tree indirectly benefits from correct endian and architecture detection through `boost/predef.h`.

Risks: It explicitly avoids reporting bi-endianness. Cross-compilers or unusual libc header combinations may leave all endian macros unavailable or choose the OS-header result over architecture defaults. A minor naming oddity exists in `BOOST_ENDIAN_BIG_WORD_BYTE_AVAILABLE` and `BOOST_ENDIAN_LITTLE_WORD_BYTE_AVAILABLE`.

Test signals: Four Predef test declarations expose each endian macro to generated tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/other/endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/other/wordsize.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/other/wordsize.h

Purpose: Derives the native architecture word size in bits from Boost.Predef architecture headers.

Important APIs, types, and functions: Defines `BOOST_ARCH_WORD_BITS` as `64`, `32`, `16`, or `0`, plus `BOOST_ARCH_WORD_BITS_64`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_WORD_BITS_16`, and name macros.

Control flow: The header includes `boost/predef/architecture.h`, then checks whether architecture-specific headers already defined a `BOOST_ARCH_WORD_BITS_*` macro. The first available size in the order 64, 32, 16 sets `BOOST_ARCH_WORD_BITS`; missing indicator macros are explicitly defaulted to not available.

State and persistence behavior: Compile-time-only; no runtime state or storage. It produces a single numeric macro usable in preprocessor and compiler expressions.

Dependencies and integration points: Pulls all architecture detection headers, so it can be used by platform code requiring coarse data model decisions.

Risks: Word size is manually maintained in architecture detectors and may be unavailable for newer or uncommon architectures, leaving `BOOST_ARCH_WORD_BITS` as `0`. It should not be treated as pointer width on exotic ABIs without checking platform documentation.

Test signals: Test declarations cover the aggregate word-bit macro and each size-specific indicator.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/other/wordsize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/other/workaround.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/other/workaround.h

Purpose: Provides version-comparison macros for conditional compiler/platform workarounds.

Important APIs, types, and functions: Defines `BOOST_PREDEF_WORKAROUND(symbol, comp, major, minor, patch)` and `BOOST_PREDEF_TESTED_AT(symbol, major, minor, patch)`.

Control flow: Under `BOOST_STRICT_CONFIG`, both macros expand to false-like `0`, disabling workaround branches. Otherwise `BOOST_PREDEF_WORKAROUND` checks that a detector symbol is nonzero and compares it to `BOOST_VERSION_NUMBER(major, minor, patch)`. `BOOST_PREDEF_TESTED_AT` normally returns whether the symbol is available; when `BOOST_DETECT_OUTDATED_WORKAROUNDS` is set, it allows versions up to the tested value and intentionally triggers a compile-time error for newer matching symbols.

State and persistence behavior: Pure preprocessor logic; no runtime state.

Dependencies and integration points: Uses `boost/predef/version_number.h` unless strict config disables comparisons. It mirrors Boost.Config-style workaround gates while using Boost.Predef version symbols.

Risks: The intentional `(1%0)` diagnostic for outdated workarounds is disruptive by design. Macro arguments must be detector numeric values, not arbitrary version strings.

Test signals: No direct `BOOST_PREDEF_DECLARE_TEST`; behavior is validated by compile-time use in consumers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/other/workaround.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform.h

Purpose: Aggregates Boost.Predef platform-family detectors.

Important APIs, types, and functions: It defines no standalone macros, but includes platform detectors for Android, CloudABI, MinGW variants, Windows UWP/families, deprecated Windows Runtime, and iOS device/simulator.

Control flow: A normal include guard is combined with `BOOST_PREDEF_INTERNAL_GENERATE_TESTS`, allowing test-generation passes to re-enter included headers.

State and persistence behavior: No runtime state. Inclusion updates compile-time platform-detection macro state through child headers and `platform_detected.h`.

Dependencies and integration points: Used by `boost/predef.h` and consumers that need platform categories separate from OS detection. Windows-specific child headers depend on `BOOST_OS_WINDOWS` and each other.

Risks: Include order matters for platform emulation markers because some child headers define `*_EMULATED` when another platform has already claimed detection. Aggregating all platform headers is convenient but can expose multiple related Windows-family macros.

Test signals: Each included child detector declares its own generated Predef test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/android.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/android.h

Purpose: Detects Android as a platform layer.

Important APIs, types, and functions: Defines `BOOST_PLAT_ANDROID`, `BOOST_PLAT_ANDROID_AVAILABLE`, and `BOOST_PLAT_ANDROID_NAME`.

Control flow: Starts unavailable, then sets `BOOST_PLAT_ANDROID` to available when `__ANDROID__` is defined. Successful detection includes `platform_detected.h`.

State and persistence behavior: Compile-time-only. The platform-detected marker can influence later platform headers that support emulated-platform reporting.

Dependencies and integration points: Used by `endian.h` to choose `<endian.h>` on Android and by the `platform.h` aggregator.

Risks: Android also defines Linux-oriented macros in many toolchains, so OS and platform detectors should be interpreted together.

Test signals: Declares a generated Boost.Predef test for `BOOST_PLAT_ANDROID`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/android.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/cloudabi.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/cloudabi.h

Purpose: Detects the CloudABI platform.

Important APIs, types, and functions: Defines `BOOST_PLAT_CLOUDABI`, `BOOST_PLAT_CLOUDABI_AVAILABLE`, and `BOOST_PLAT_CLOUDABI_NAME`.

Control flow: The macro starts unavailable and becomes available when `__CloudABI__` is defined. On success it includes `platform_detected.h`.

State and persistence behavior: Compile-time-only; no persistent or runtime behavior.

Dependencies and integration points: Included by `boost/predef/platform.h` and can be combined with compiler/architecture detectors for target-specific code.

Risks: CloudABI is a niche target; stale or missing compiler predefined macros would leave detection unavailable. It reports availability, not a version.

Test signals: The file declares the standard Boost.Predef test macro for generated validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/cloudabi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/ios.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/ios.h

Purpose: Splits Apple's iOS OS detection into device and simulator platform categories.

Important APIs, types, and functions: Defines `BOOST_PLAT_IOS_DEVICE`, `BOOST_PLAT_IOS_DEVICE_AVAILABLE`, `BOOST_PLAT_IOS_DEVICE_NAME`, `BOOST_PLAT_IOS_SIMULATOR`, `BOOST_PLAT_IOS_SIMULATOR_AVAILABLE`, and `BOOST_PLAT_IOS_SIMULATOR_NAME`.

Control flow: If `BOOST_OS_IOS` is true, it includes `<TargetConditionals.h>`. `TARGET_OS_SIMULATOR == 1` or `TARGET_IPHONE_SIMULATOR == 1` selects simulator; otherwise it selects device.

State and persistence behavior: Compile-time-only. Successful device or simulator detection includes `platform_detected.h`.

Dependencies and integration points: Depends on `boost/predef/os/ios.h` for the OS-level Apple mobile target and on Apple's TargetConditionals header for simulator distinction.

Risks: The fallback treats any iOS target without simulator markers as device. SDK macro changes or non-Apple toolchains can affect precision.

Test signals: Declares separate generated tests for simulator and device macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/ios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/mingw.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/mingw.h

Purpose: Detects any MinGW family platform and, where possible, its version.

Important APIs, types, and functions: Defines `BOOST_PLAT_MINGW`, `BOOST_PLAT_MINGW_AVAILABLE`, `BOOST_PLAT_MINGW_EMULATED`, and `BOOST_PLAT_MINGW_NAME`.

Control flow: If `__MINGW32__` or `__MINGW64__` is defined, it includes `<_mingw.h>`, prefers `__MINGW64_VERSION_MAJOR/MINOR`, then attempts 32-bit version macros, and falls back to generic availability. If another platform was already detected, it records `BOOST_PLAT_MINGW_EMULATED`; otherwise it assigns `BOOST_PLAT_MINGW` and includes `platform_detected.h`.

State and persistence behavior: Compile-time-only. It may leave both a primary platform marker and an emulation marker depending on include order.

Dependencies and integration points: Used by Windows and platform aggregation paths; MinGW compilers also interact with `BOOST_OS_WINDOWS`.

Risks: The 32-bit fallback condition checks `__MINGW32_VERSION_MAJOR/MINOR` but the value expression uses `__MINGW32_MAJOR_VERSION/MINOR_VERSION`, so version precision depends on those aliases existing in `_mingw.h`.

Test signals: Declares tests for the primary macro and, when present, the emulated macro.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/mingw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/mingw32.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/mingw32.h

Purpose: Detects the classic 32-bit MinGW platform.

Important APIs, types, and functions: Defines `BOOST_PLAT_MINGW32`, `BOOST_PLAT_MINGW32_AVAILABLE`, `BOOST_PLAT_MINGW32_EMULATED`, and `BOOST_PLAT_MINGW32_NAME`.

Control flow: When `__MINGW32__` exists, it includes `<_mingw.h>`, builds a version from `__MINGW32_VERSION_MAJOR/MINOR` if available, otherwise uses generic availability. It writes an emulated macro if another platform has already been detected; otherwise it becomes the active platform.

State and persistence behavior: Compile-time-only. Platform-detected state is shared with other Boost.Predef platform headers.

Dependencies and integration points: Included by the platform aggregator and complements the aggregate `mingw.h` and `mingw64.h` headers.

Risks: MinGW-w64 can define `__MINGW32__` for compatibility, so this macro may indicate the API family rather than exclusively a 32-bit binary target. Use with architecture macros for bitness.

Test signals: Declares primary and optional emulated Predef tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/mingw32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/mingw64.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/mingw64.h

Purpose: Detects MinGW-w64.

Important APIs, types, and functions: Defines `BOOST_PLAT_MINGW64`, `BOOST_PLAT_MINGW64_AVAILABLE`, `BOOST_PLAT_MINGW64_EMULATED`, and `BOOST_PLAT_MINGW64_NAME`.

Control flow: When `__MINGW64__` exists, it includes `<_mingw.h>` and uses `__MINGW64_VERSION_MAJOR/MINOR` to build a Boost version if available. It records emulation if another platform detector already claimed the platform; otherwise it sets `BOOST_PLAT_MINGW64`.

State and persistence behavior: Compile-time macro state only.

Dependencies and integration points: Included by `platform.h`, related to aggregate `mingw.h`, and used by `windows_uwp.h` as a UWP capability signal for MinGW-w64 version 3 or later.

Risks: It does not distinguish 32-bit versus 64-bit code generation by itself; MinGW-w64 can target both. Combine with architecture macros when data model matters.

Test signals: Primary and optional emulated Predef test declarations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/mingw64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_desktop.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_desktop.h

Purpose: Detects Windows Desktop application targeting.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_DESKTOP`, `BOOST_PLAT_WINDOWS_DESKTOP_AVAILABLE`, and `BOOST_PLAT_WINDOWS_DESKTOP_NAME`.

Control flow: If `BOOST_OS_WINDOWS` is true and either `WINAPI_FAMILY == WINAPI_FAMILY_DESKTOP_APP` or UWP support is unavailable, it marks desktop as available.

State and persistence behavior: Compile-time-only. Successful detection includes `platform_detected.h`.

Dependencies and integration points: Depends on Windows OS detection and `windows_uwp.h`. It provides a fallback for old SDKs lacking UWP family definitions.

Risks: The `!BOOST_PLAT_WINDOWS_UWP` fallback means old SDKs are assumed desktop. This is practical but can obscure newer Windows-family distinctions when SDK headers are incomplete.

Test signals: Declares a Boost.Predef generated test for the desktop macro.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_desktop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_phone.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_phone.h

Purpose: Detects Windows Phone UWP-family targeting.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_PHONE`, `BOOST_PLAT_WINDOWS_PHONE_AVAILABLE`, and `BOOST_PLAT_WINDOWS_PHONE_NAME`.

Control flow: On Windows, if `WINAPI_FAMILY_PHONE_APP` exists and `WINAPI_FAMILY` equals it, the macro becomes available and includes `platform_detected.h`.

State and persistence behavior: Compile-time-only. It participates in shared platform detection.

Dependencies and integration points: Depends on `windows_uwp.h` to include `winapifamily.h` when SDK support exists. The deprecated `windows_runtime.h` uses this macro.

Risks: Windows Phone family macros are SDK-era-specific and obsolete for modern Windows development, so absence does not imply a non-mobile app in all historical toolchains.

Test signals: Declares the generated Predef test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_phone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_runtime.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_runtime.h

Purpose: Provides deprecated Windows Runtime detection for compatibility with older Boost.Predef users.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_RUNTIME`, `BOOST_PLAT_WINDOWS_RUNTIME_AVAILABLE`, and `BOOST_PLAT_WINDOWS_RUNTIME_NAME`.

Control flow: On Windows, it becomes available if either `BOOST_PLAT_WINDOWS_STORE` or `BOOST_PLAT_WINDOWS_PHONE` is available.

State and persistence behavior: Compile-time-only. Successful detection includes `platform_detected.h`.

Dependencies and integration points: Depends on `windows_phone.h` and `windows_store.h`. New code should use the specific Windows platform-family macros instead.

Risks: The header is explicitly deprecated and models an older UWP/runtime taxonomy. It may conflate distinct Store and Phone targets.

Test signals: Declares a generated test for `BOOST_PLAT_WINDOWS_RUNTIME`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_runtime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_server.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_server.h

Purpose: Detects Windows Server UWP-family targeting.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_SERVER`, `BOOST_PLAT_WINDOWS_SERVER_AVAILABLE`, and `BOOST_PLAT_WINDOWS_SERVER_NAME`.

Control flow: On Windows, if `WINAPI_FAMILY_SERVER` is defined and selected by `WINAPI_FAMILY`, the platform macro becomes available.

State and persistence behavior: Compile-time macro state only; successful detection includes `platform_detected.h`.

Dependencies and integration points: Relies on `windows_uwp.h` and Windows SDK family macros from `winapifamily.h`.

Risks: Depends on SDK support for `WINAPI_FAMILY_SERVER`; older SDKs cannot report it. It says nothing about runtime OS edition outside compile target family.

Test signals: Standard Boost.Predef generated test declaration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_store.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_store.h

Purpose: Detects Windows Store application targeting.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_STORE`, `BOOST_PLAT_WINDOWS_STORE_AVAILABLE`, and `BOOST_PLAT_WINDOWS_STORE_NAME`.

Control flow: On Windows, it checks `WINAPI_FAMILY_PC_APP` and deprecated `WINAPI_FAMILY_APP` against `WINAPI_FAMILY`. A match sets the macro to available and includes `platform_detected.h`.

State and persistence behavior: Compile-time-only.

Dependencies and integration points: Depends on `windows_uwp.h` for SDK family support. `windows_runtime.h` uses this macro as one of its deprecated runtime inputs.

Risks: Includes a deprecated family macro for compatibility; consumers should understand which SDK family is actually being targeted.

Test signals: Declares the generated test for the Store macro.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_system.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_system.h

Purpose: Detects Windows System, drivers, and tools targeting.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_SYSTEM`, `BOOST_PLAT_WINDOWS_SYSTEM_AVAILABLE`, and `BOOST_PLAT_WINDOWS_SYSTEM_NAME`.

Control flow: On Windows, if `WINAPI_FAMILY_SYSTEM` is defined and selected by `WINAPI_FAMILY`, it marks the system platform as available.

State and persistence behavior: Compile-time-only. Successful detection writes the platform-detected marker.

Dependencies and integration points: Depends on `windows_uwp.h` and Windows SDK family macros.

Risks: This is a compile-target family detector, not a runtime capability probe. Missing SDK macros leave it unavailable.

Test signals: Declares the standard generated Predef test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_uwp.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_uwp.h

Purpose: Detects whether the Windows build environment can target Universal Windows Platform families and records the Windows SDK build version.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_UWP`, `BOOST_PLAT_WINDOWS_UWP_AVAILABLE`, `BOOST_PLAT_WINDOWS_UWP_NAME`, and `BOOST_PLAT_WINDOWS_SDK_VERSION`.

Control flow: On Windows, non-MinGW32, non-WinCE, non-Wine builds include `<ntverp.h>` and convert `VER_PRODUCTBUILD` to a Boost version. UWP is available when the SDK build is at least 9200 or when MinGW-w64 major version is at least 3. If available, it includes `platform_detected.h` and `<winapifamily.h>`.

State and persistence behavior: Compile-time-only. It also exposes SDK version state to dependent Windows platform-family headers.

Dependencies and integration points: Central dependency for Windows Desktop, Store, Phone, Server, System, and Runtime detectors.

Risks: Header inclusion is conditional to avoid missing `ntverp.h` on some toolchains. SDK version availability does not mean a particular family is selected; it only means family targeting support exists.

Test signals: Declares a generated Predef test for UWP.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_uwp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/version.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/version.h

Purpose: Publishes the Boost.Predef component version.

Important APIs, types, and functions: Defines `BOOST_PREDEF_VERSION` as `BOOST_VERSION_NUMBER(1,15,1)`.

Control flow: Straight include guard plus inclusion of `version_number.h`; no conditional branches beyond the guard.

State and persistence behavior: Compile-time constant only.

Dependencies and integration points: Consumers compare this macro when they need a minimum Boost.Predef feature set.

Risks: It is the vendored Predef version, not the whole Boost distribution version and not mergerfs's version.

Test signals: No direct test hook; correctness is visible through compilation and version comparisons.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/version_number.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/version_number.h

Purpose: Defines Boost.Predef's compact numeric version encoding and extraction macros.

Important APIs, types, and functions: Public macros are `BOOST_VERSION_NUMBER(major, minor, patch)`, `BOOST_VERSION_NUMBER_MAX`, `BOOST_VERSION_NUMBER_ZERO`, `BOOST_VERSION_NUMBER_MIN`, `BOOST_VERSION_NUMBER_AVAILABLE`, `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, and `BOOST_VERSION_NUMBER_MAJOR/MINOR/PATCH`.

Control flow: Macro arithmetic encodes a two-digit major, two-digit minor, and five-digit patch as `MMmmppppp`; inputs are modulo-truncated to their supported ranges.

State and persistence behavior: No runtime state. This file underpins nearly every Boost.Predef detection macro.

Dependencies and integration points: Standalone include used by OS, platform, architecture, library, and workaround detectors.

Risks: Values outside documented ranges are silently modulo-truncated. Callers needing semantic-version precision beyond two/two/five digits cannot use this representation directly.

Test signals: No direct generated test declaration, but all detector tests depend on these constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/version_number.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/throw_exception.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/throw_exception.hpp

Purpose: Centralizes Boost exception throwing, exception wrapping, source-location capture, and no-exception customization.

Important APIs, types, and functions: Exposes `boost::throw_exception`, `BOOST_THROW_EXCEPTION(x)`, `boost::wrapexcept<E>`, `boost::throw_with_location`, and `boost::get_throw_location`. In `BOOST_NO_EXCEPTIONS` builds, users must provide `throw_exception(std::exception const&)` overloads.

Control flow: With exceptions enabled and `BOOST_EXCEPTION_DISABLE` unset, `throw_exception` checks that `E` is compatible with `std::exception` and throws `wrapexcept<E>`, which inherits from `E`, conditionally from `boost::exception`, and conditionally from `clone_base`. Location-aware overloads attach file, line, function, and column through Boost.Exception metadata. `throw_with_location` throws a lightweight `with_throw_location<E>` wrapper, and `get_throw_location` recovers that location via RTTI or Boost.Exception metadata.

State and persistence behavior: No global state. Exception objects persist throw metadata inside the thrown object. `clone()` uses heap allocation guarded by a local deleter for exception safety.

Dependencies and integration points: Depends on Boost.Exception, Boost.Assert source locations, Boost.Config, standard `<exception>`, and type traits. Used broadly by Boost code, including unordered archive validation.

Risks: Requires thrown Boost exceptions to derive from `std::exception`. Behavior differs materially under `BOOST_NO_EXCEPTIONS`, `BOOST_EXCEPTION_DISABLE`, and `BOOST_NO_RTTI`. Wrapping changes the dynamic type caught by exact-type handlers.

Test signals: Compile tests should cover normal throw/catch, source-location recovery, no-RTTI fallback, disabled Boost.Exception wrapping, and no-exceptions user hooks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/throw_exception.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/concurrent_flat_map.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/concurrent_flat_map.hpp

Purpose: Provides the public `boost::unordered::concurrent_flat_map` container, a thread-safe open-addressing hash map without iterators, built around visitation and composite operations.

Important APIs, types, and functions: Exposes constructors, assignment, `size`, `empty`, `visit`, `cvisit`, bulk visit, `visit_all`, `visit_while`, `insert`, `insert_or_assign`, `insert_or_visit`, `insert_and_visit`, `emplace`, `try_emplace`, `erase`, `erase_if`, `merge`, `count`, `contains`, `rehash`, `reserve`, `get_allocator`, `hash_function`, `key_eq`, optional stats, `operator==`, `swap`, free `erase_if`, serialization, deduction guides, and a `pmr` alias from the forward header.

Control flow: The class is mostly a thin API adapter over `detail::foa::concurrent_table<flat_map_types<...>>`. Operations validate callback invocability with static-assert macros, then delegate to table methods. Insert-or-assign uses `try_emplace_or_visit` and mutates the mapped value in the visit path. Range insert loops call table emplacement one element at a time. Serialization delegates the table as an NVP.

State and persistence behavior: Persistent container state is entirely `table_`: allocator, hash, predicate, slot arrays, locks, size, and optional stats. No iterators are exposed because concurrent access is mediated through callbacks under table locks.

Dependencies and integration points: Integrates Boost.ContainerHash, allocator access, Boost.Serialization, `unordered_flat_map` move construction, FOA type policy, and concurrent table internals.

Risks: User callbacks execute while element/group access is controlled by the table, so reentrant operations are restricted by the lower-level reentrancy check. The API intentionally differs from standard containers; code expecting iterators cannot be ported mechanically. Parallel algorithms are only available when execution support is detected.

Test signals: Tests should cover concurrent inserts/lookups/erases, callback constness, heterogeneous lookup, range and initializer construction, merge, serialization, deduction guides, stats builds, and reentrancy assertions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/concurrent_flat_map.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/concurrent_flat_map_fwd.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/concurrent_flat_map_fwd.hpp

Purpose: Forward-declares `concurrent_flat_map` and associated free functions without including the full implementation.

Important APIs, types, and functions: Declares the class template with default `boost::hash`, `std::equal_to`, and `std::allocator<std::pair<Key const,T>>`; declares `operator==`, `operator!=`, `swap`, `erase_if`; defines `boost::unordered::pmr::concurrent_flat_map` when `<memory_resource>` is available; imports `boost::unordered::concurrent_flat_map` into namespace `boost`.

Control flow: Compile-time declarations only, with conditional PMR aliasing gated by `BOOST_NO_CXX17_HDR_MEMORY_RESOURCE`.

State and persistence behavior: No state; this header reduces include cost and breaks declaration cycles.

Dependencies and integration points: Includes Boost.Config, Boost.ContainerHash forward declarations, `<functional>`, `<memory>`, and optionally `<memory_resource>`.

Risks: The include-guard closing comment names `BOOST_UNORDERED_CONCURRENT_FLAT_MAP_HPP` instead of the actual forward header guard, a harmless maintenance typo. Consumers still need the full header for definitions.

Test signals: Compile tests should verify forward declaration usability in pointers/references and PMR alias availability under C++17 memory-resource support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/concurrent_flat_map_fwd.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/allocator_constructed.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/allocator_constructed.hpp

Purpose: RAII helper for constructing a stack-resident object through an allocator and destroying it reliably.

Important APIs, types, and functions: Defines `allocator_policy` with `construct` and `destroy`, and `allocator_constructed<Allocator,T,Policy>` with constructor, destructor, and `value()`.

Control flow: The constructor stores an allocator copy and calls `Policy::construct` on an `opt_storage<T>` address. The destructor calls `Policy::destroy`. `value()` returns the live object reference.

State and persistence behavior: Owns a single object lifetime in local storage plus an allocator copy. It never allocates its own storage.

Dependencies and integration points: Uses `boost/core/allocator_traits.hpp` and unordered `opt_storage`. FOA insertion paths use similar allocator-aware construction patterns to preserve allocator semantics.

Risks: The class assumes construction succeeds; if `Policy::construct` throws, the destructor is not run and no object exists, which is normal C++ construction behavior. Copy/move are not explicitly disabled, so use as a local non-copied guard.

Test signals: Allocator-aware tests should verify construct/destroy calls and behavior with custom policies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/allocator_constructed.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/archive_constructed.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/archive_constructed.hpp

Purpose: RAII helper for loading an object from a Boost.Serialization archive into uninitialized stack storage.

Important APIs, types, and functions: Defines noncopyable `archive_constructed<T>` with `archive_constructed(name, ar, version)`, destructor, and `get()`.

Control flow: Construction calls `core::load_construct_data_adl` on the storage address, then deserializes an NVP into `get()`. If archive extraction throws, it explicitly destroys the partially constructed object and rethrows. Destructor destroys the loaded object.

State and persistence behavior: Owns one temporary `T` in `opt_storage<T>` until consumed by table loading. It does not persist archive data.

Dependencies and integration points: Uses Boost.Core serialization hooks, no-exceptions support macros, `noncopyable`, and `opt_storage`. `concurrent_table` uses it when loading set values and map keys/mapped values.

Risks: Correctness depends on archive `load_construct_data` constructing a valid object at the storage address. Strict-aliasing diagnostics are suppressed for affected GCC versions around `get()`.

Test signals: Serialization tests should cover throwing archives, non-default-constructible value types, and object-address reset paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/archive_constructed.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/bad_archive_exception.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/bad_archive_exception.hpp

Purpose: Reports invalid or corrupted Boost.Unordered serialization archives.

Important APIs, types, and functions: Defines `boost::unordered::detail::bad_archive_exception`, deriving from `std::runtime_error`, with the fixed message `Invalid or corrupted archive`.

Control flow: No branching; default construction initializes the base error message.

State and persistence behavior: Exception object contains only `std::runtime_error` message state.

Dependencies and integration points: Included by concurrent table serialization loading; thrown via `boost::throw_exception` when duplicate keys are found in an archive.

Risks: The exception does not include the offending key or archive position, so diagnostics are intentionally minimal.

Test signals: Load tests should feed duplicate/corrupted archive entries and assert this exception path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/bad_archive_exception.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/concurrent_static_asserts.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/concurrent_static_asserts.hpp

Purpose: Centralizes compile-time validation macros for concurrent unordered container APIs.

Important APIs, types, and functions: Defines macros for invocable callbacks, const-invocable callbacks, sequenced execution policies, last/penultimate variadic argument validation, forward iterators, key-compatible iterators, and bulk-visit iterators. Provides `detail::is_invocable`.

Control flow: Macros expand to `static_assert`s. In C++20, execution policy checks reject both unsequenced and parallel-unsequenced policies; in earlier modes only parallel-unsequenced is checked. MP11 utilities select callback positions in variadic APIs.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used heavily by `concurrent_flat_map` before delegating to `concurrent_table`. Depends on Boost.MP11 and unordered type traits including transparent-key compatibility.

Risks: These diagnostics are template-heavy and can be noisy, but they catch unsafe callbacks and iterator misuse early. Execution policy checks rely on standard library policy type traits.

Test signals: Negative compile tests should cover non-invocable callbacks, incompatible bulk iterators, and rejected unsequenced policies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/concurrent_static_asserts.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/concurrent_table.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/concurrent_table.hpp

Purpose: Implements the thread-safe fast open-addressing table core used by concurrent flat/node maps and sets.

Important APIs, types, and functions: Key internals include `cache_aligned_array`, `multimutex`, `shared_lock`, `lock_guard`, `scoped_bilock`, `atomic_integral`, `group_access`, `concurrent_table_arrays`, `atomic_size_control`, and `concurrent_table<TypePolicy,Hash,Pred,Allocator>`. Public table operations include visitation, insertion/composite insertion, erasure, merge, clear, assignment, reserve/rehash, stats, equality, and serialization.

Control flow: The table extends `table_core` with atomic group metadata and group-access locks. Container-level access uses a striped `multimutex<rw_spinlock>`; group-level access uses per-group `rw_spinlock`s. Lookups probe by reduced hash, lock only candidate groups, double-check occupancy, then invoke callbacks. Insertions optimistically record the initial group's insertion counter, search for an equivalent key, reserve size and a slot, then roll back and restart if another insertion from the same initial group raced. Rehash and assignment acquire exclusive container access. Serialization takes exclusive access and saves set values or map key/mapped pairs separately; loading clears, reserves, checks duplicates, and throws `bad_archive_exception` on corruption.

State and persistence behavior: Persistent state includes FOA arrays, per-group locks/counters, striped container locks, atomic max-load/size, hash/predicate/allocator state, and optional cumulative stats. Serialization persists elements and version metadata, not lock state.

Dependencies and integration points: Depends on FOA `core.hpp`, reentrancy checks, `rw_spinlock`, tuple rotation helpers, Boost.Serialization hooks, `archive_constructed`, `bad_archive_exception`, and `boost::throw_exception`. Public containers wrap this class.

Risks: Concurrency correctness depends on lock ordering, insertion-counter rollback, atomic metadata, and reentrancy guards. User callbacks must not perform unsupported reentrant table operations. Parallel algorithms depend on standard execution support and still take per-group locks. Archive load rejects duplicates but cannot diagnose all semantic corruption.

Test signals: High-value tests are concurrent insert/find/erase stress, callback mutation, bulk visit, rehash under load, merge with allocator equality, serialization round trips and duplicate archive failures, TSan builds, stats-enabled builds, and exception-safety tests during construction and rehash.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/concurrent_table.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/core.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/core.hpp

Purpose: Provides the common fast open-addressing implementation shared by Boost.Unordered flat and concurrent containers.

Important APIs, types, and functions: Major internals include `group15`, `pow2_size_policy`, `pow2_quadratic_prober`, hash mixing policies, `table_arrays`, stats structs/macros, allocator-construction traits, `table_locator`, `alloc_cted_insert_type`, `alloc_cted_or_fwded_key_type`, and `table_core`. `table_core` manages allocation, construction/destruction, lookup, insertion, erase, clear, swap, rehash, reserve, equality, stats, and element traversal.

Control flow: Metadata is organized in groups of 15 slots plus an overflow byte. `group15::match` uses SSE2, little-endian NEON, or portable bit operations to find candidate reduced-hash slots. Lookup probes groups quadratically and stops at non-overflowed groups. Insertions find an available slot, construct the element, set metadata, and update size; full tables allocate larger arrays and transfer elements with move-if-noexcept semantics. Erase destroys the element and recovers the slot, reducing max load when the erased slot may have caused overflow to limit probe drift.

State and persistence behavior: Stores hash, predicate, allocator via empty-base optimization; arrays of groups/elements; size/max-load control; and optional cumulative stats. It does not persist externally but supplies traversal and serialization support to higher layers.

Dependencies and integration points: Depends on Boost.Config, Boost.Predef, container hash traits, allocator/pointer traits, FOA stats, unordered diagnostics, and low-level bit/narrow/mulx helpers. `concurrent_table` specializes it with atomic metadata and atomic size control.

Risks: This is performance-critical unsafe-adjacent code: SIMD assumptions, metadata sentinel layout, fancy pointer support, exception-safety during transfer, and allocator construct behavior are all sensitive. Hash/predicate must be nothrow swappable for swap. Poor hash quality increases probing despite mixing policy support.

Test signals: Tests should cover SIMD and portable paths, heterogeneous lookup, allocator/fancy-pointer behavior, nontrivial move/copy exception paths, erase/insert drift, rehash/reserve invariants, equality, stats, sanitizer builds, and multiple architectures/endian configurations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/core.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/cumulative_stats.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/cumulative_stats.hpp

Purpose: Implements one-pass cumulative statistics for FOA instrumentation.

Important APIs, types, and functions: Defines `sequence_stats_data`, `welfords_algorithm`, `sequence_stats_summary`, `cumulative_stats<N>`, and thread-safe `concurrent_cumulative_stats<N>` when threads are enabled.

Control flow: `add` increments a sample count and uses MP11 tuple transformation to apply Welford's algorithm to N sequences. `get_summary` returns count, average, biased variance, and standard deviation for each sequence. Count wraparound resets the accumulator.

State and persistence behavior: Stores count and per-sequence running mean/prior mean/sum-of-squares. The concurrent variant protects the base stats with `rw_spinlock` and `std::lock_guard`.

Dependencies and integration points: Used when `BOOST_UNORDERED_ENABLE_STATS` is set in FOA table cores. Depends on Boost.MP11 tuple support and optionally `rw_spinlock`.

Risks: Variance is biased by design (`s / n`). Concurrent copies take a lock, but readers should still treat stats as diagnostic, not synchronization state.

Test signals: Numeric tests should check averages/variance/deviation, reset, wraparound behavior where practical, and concurrent add/get under `BOOST_HAS_THREADS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/cumulative_stats.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/flat_map_types.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/flat_map_types.hpp

Purpose: Defines the type policy that adapts FOA table storage to flat map key/value semantics.

Important APIs, types, and functions: `flat_map_types<Key,T>` defines `key_type`, `mapped_type`, raw key/mapped types, `init_type`, `moved_type`, `value_type`, `element_type`, `constructibility_checker`, `value_from`, `extract`, `move`, `construct`, and `destroy`.

Control flow: `extract` returns `.first` from pair-like values. `move` converts mutable init or element pairs into rvalue key/mapped pairs, using `const_cast` to move from the stored `pair<Key const,T>`. Construction first runs map constructibility checks for standard allocators, then delegates to `boost::allocator_construct`; destruction delegates to allocator destroy.

State and persistence behavior: No state. It is a compile-time policy consumed by `table_core` and `concurrent_table`.

Dependencies and integration points: Depends on `types_constructibility.hpp` and allocator access. Used by `concurrent_flat_map` and unordered flat map internals.

Risks: Moving from a `const` key requires careful internal-only use while relocating elements. The TODO about laundering notes a potential object-model sensitivity.

Test signals: Tests should cover pair construction forms, piecewise construction, move relocation, non-copyable mapped values, and allocator construct diagnostics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/flat_map_types.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/ignore_wshadow.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/ignore_wshadow.hpp

Purpose: Suppresses GCC `-Wshadow` warnings around FOA templates that derive from user-provided types.

Important APIs, types, and functions: No C++ APIs; it conditionally emits GCC diagnostic pragmas. Without `BOOST_UNORDERED_DETAIL_RESTORE_WSHADOW`, it pushes diagnostics and ignores `-Wshadow`; with that macro, it pops diagnostics.

Control flow: Only active under `BOOST_GCC`. The paired `restore_wshadow.hpp` header defines the restore macro and includes this file to pop the diagnostic state.

State and persistence behavior: Affects compiler diagnostic state for the current translation unit include region.

Dependencies and integration points: Included around `table_core`/`concurrent_table` definitions where empty-base inheritance from user hash/predicate/allocator types can trigger unavoidable shadow warnings.

Risks: Must be properly paired with restore to avoid suppressing warnings beyond the intended region. It is compiler-specific.

Test signals: Build tests with GCC and `-Wshadow` should compile FOA headers without warning leakage after restore.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/ignore_wshadow.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/reentrancy_check.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/reentrancy_check.hpp

Purpose: Provides debug-time protection against unsupported reentrant access to the same concurrent unordered container.

Important APIs, types, and functions: Defines `entry_trace`, `reentrancy_checked<LockGuard>`, and `reentrancy_bichecked<LockGuard>` when enabled; otherwise defines pass-through wrappers with the same interface.

Control flow: When reentrancy checking is enabled, `entry_trace` maintains a thread-local linked list of active container addresses. Construction asserts the address is not already present, and destruction/removal clears it. The checked wrappers acquire the underlying lock guard and clear traces when `unlock()` is called.

State and persistence behavior: Uses thread-local transient state only. No cross-thread persistence.

Dependencies and integration points: Used by `concurrent_table` access guards around operations that must not call back into the same table recursively. Depends on Boost.Assert.

Risks: Disabled when `BOOST_UNORDERED_DISABLE_REENTRANCY_CHECK` is set or assertions are void, so release builds may not catch misuse. It detects same-thread reentrancy, not all logical deadlock scenarios.

Test signals: Debug tests should trigger assertions for callbacks that reenter the same container and should allow operations on distinct containers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/reentrancy_check.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/restore_wshadow.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/restore_wshadow.hpp

Purpose: Restores GCC `-Wshadow` diagnostics after FOA internals temporarily suppress them.

Important APIs, types, and functions: No runtime API. It defines `BOOST_UNORDERED_DETAIL_RESTORE_WSHADOW`, includes `ignore_wshadow.hpp`, then undefines the marker.

Control flow: The included `ignore_wshadow.hpp` sees the restore marker and emits `#pragma GCC diagnostic pop` under GCC.

State and persistence behavior: Only compiler diagnostic state is affected.

Dependencies and integration points: Paired with `ignore_wshadow.hpp` in `core.hpp` and `concurrent_table.hpp`.

Risks: If included without a prior push on GCC, diagnostic stack handling would be mismatched; current usage pairs it directly after FOA template regions.

Test signals: GCC warning-configuration builds should verify no diagnostic suppression leaks past FOA includes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/restore_wshadow.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/rw_spinlock.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/rw_spinlock.hpp

Purpose: Implements a compact reader-writer spinlock for FOA concurrent containers and stats.

Important APIs, types, and functions: Class `rw_spinlock` provides `try_lock_shared`, `lock_shared`, `unlock_shared`, `try_lock`, `lock`, and `unlock`.

Control flow: A 32-bit atomic state uses bit 31 for exclusive lock, bit 30 for writer pending, and low 30 bits for reader count. Shared lock succeeds only when no writer/exclusive bit is present. Exclusive lock waits until no readers or writer, setting writer-pending when readers are active. The spin loop uses pause, yield, and eventual sleep through Boost.Core yield primitives.

State and persistence behavior: Holds only atomic lock state. No ownership tracking or recursion state exists.

Dependencies and integration points: Used by per-group concurrent table locks, striped container locks, and concurrent stats. Depends on `<atomic>`, `<cstdint>`, and Boost.Core yield primitives.

Risks: Non-reentrant and unfairness is possible under high contention despite writer-pending mitigation. Mispaired unlock calls are undefined by contract. Spinlocks are sensitive to oversubscription.

Test signals: Threaded tests should cover multiple readers, writer exclusion, try-lock behavior, contention progress, and sanitizer runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/rw_spinlock.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/tuple_rotate_right.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/tuple_rotate_right.hpp

Purpose: Provides a small tuple utility for rotating variadic argument packs so callback arguments can be moved to the front for internal dispatch.

Important APIs, types, and functions: Defines `tuple_rotate_right_return_type<Offset,Tuple>`, `tuple_rotate_right_aux`, and `tuple_rotate_right<Offset=1>`.

Control flow: Uses MP11 index sequences and `mp_rotate_right_c` to construct a tuple whose elements are fetched from `(Is + size - Offset) % size`, preserving forwarding.

State and persistence behavior: No persistent state; returns a new tuple value.

Dependencies and integration points: Used by `concurrent_table` to rearrange variadic `emplace_or_visit` and `emplace_and_visit` calls where callback arguments are syntactically last but internal helpers want them earlier.

Risks: Requires non-empty tuple types for modulo arithmetic. Forwarding through tuple construction can affect value categories according to tuple rules.

Test signals: Unit tests should rotate tuples of lvalues/rvalues and offsets 1 and 2, matching concurrent table callback dispatch patterns.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/tuple_rotate_right.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/types_constructibility.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/types_constructibility.hpp

Purpose: Supplies targeted static assertions for map/set key and mapped type construction when FOA containers use `std::allocator`.

Important APIs, types, and functions: Defines `check_key_type_t`, `check_mapped_type_t`, `map_types_constructibility<TypePolicy>`, and `set_types_constructibility<TypePolicy>`.

Control flow: General allocator overloads are no-ops because custom allocators may provide construction semantics not visible to type traits. `std::allocator<value_type>` overloads validate direct, pair, rvalue pair, and piecewise construction forms for keys and mapped values. Set policy asserts `key_type == value_type` and checks key constructibility.

State and persistence behavior: Compile-time-only; no objects or runtime state.

Dependencies and integration points: Used by `flat_map_types` before allocator construction, improving diagnostics for `concurrent_flat_map` and other FOA map/set containers.

Risks: Custom allocators bypass these checks, so diagnostics may occur later inside allocator construction. Trait checks must match the construction forms used by table policies.

Test signals: Compile-fail tests should cover non-copyable/non-movable keys, non-default-constructible mapped values for `try_emplace`, pair and piecewise construction, and custom allocator bypass behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/types_constructibility.hpp -->
