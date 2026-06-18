## sources/distributed-fs/ceph-client/include/linux/compiler-clang.h

Purpose: This compiler-specific header normalizes Clang behavior for the kernel after `compiler_types.h` has been included. It defines sanitizer attributes, diagnostic pragmas, inline assembly constraints, and feature compatibility macros.

Important APIs, types, and functions: It redefines `__cleanup(func)` with `__maybe_unused` to avoid older Clang unused-variable warnings for cleanup-only variables. It sets `KASAN_ABI_VERSION` to 5. It maps old `__has_feature` sanitizer results to GCC-style `__SANITIZE_ADDRESS__`, `__SANITIZE_HWADDRESS__`, and `__SANITIZE_THREAD__`. It defines `__no_sanitize_address`, `__no_sanitize_thread`, `__no_sanitize_undefined`, `__no_sanitize_memory`, `__no_kmsan_checks`, `__no_sanitize_coverage`, `__no_kstack_erase`, and optionally `__noscs`. Diagnostic helpers include `__diag_clang`, severity names, `_Pragma` wrappers, and `__diag_ignore_all`. Assembly constraint defaults are restricted to avoid known Clang `"g"` and `"rm"` constraint problems. `CC_HAS_TYPEOF_UNQUAL` models Clang support for `__typeof_unqual__`.

Control flow: This file is included only on Clang builds through `compiler_types.h`; it has no runtime control flow. Preprocessor decisions derive from Clang feature probes and kernel config. Sanitizer feature probes progressively refine attributes used by later headers and code.

State and persistence: No runtime state is stored. Persistent behavior is compile-time ABI and instrumentation selection: sanitizer attributes determine whether code is instrumented, KASAN ABI selection affects instrumentation compatibility, and assembly constraints affect generated code.

Dependencies and integration points: It depends on `__has_feature`, `__has_attribute`, Clang version macros, `CONFIG_ARCH_USE_BUILTIN_BSWAP`, sanitizer configs, `CONFIG_KCOV`, shadow call stack, and downstream compiler macros in `compiler_types.h` and `compiler.h`.

Risks and test signals: Risks include hiding sanitizer instrumentation where needed, failing to disable it in low-level paths, incorrect feature emulation for newer/older Clang, and bad inline-asm constraints producing invalid code. Test signals are allmodconfig builds under supported Clang versions, sanitizer boot tests, KCOV/KMSAN/KASAN builds, shadow-call-stack builds, and compile tests for cleanup variables and inline assembly.
