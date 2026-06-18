## sources/distributed-fs/ceph-client/include/linux/compiler-gcc.h

Purpose: This GCC-specific header normalizes compiler behavior and capabilities for kernel builds after `compiler_types.h` has selected GCC. It defines version-dependent ABI, sanitizer, diagnostic, inline-assembly, and plugin-related macros.

Important APIs, types, and functions: `GCC_VERSION` encodes major/minor/patch. `RELOC_HIDE(ptr, off)` hides pointer arithmetic from GCC optimizers using empty asm. `__latent_entropy` is enabled for the GCC latent entropy plugin. `barrier_before_unreachable()` works around GCC stack-allocation issues before unreachable markers. Builtin byte-swap macros are exposed when configured. `KASAN_ABI_VERSION` is 5 for GCC 7+ and 4 for older GCC. The header defines `__noscs`, `__no_sanitize_address`, `__no_sanitize_thread`, `__no_sanitize_undefined`, `__no_sanitize_coverage`, `__no_sanitize_memory`, `__no_kmsan_checks`, diagnostic pragmas, `__diag_ignore_all`, and `CC_HAS_TYPEOF_UNQUAL`.

Control flow: There is no runtime flow. Compile-time gates select attributes from GCC version, sanitizer predefines, Kconfig, and `__has_attribute`. The `RELOC_HIDE` expression does execute as inline assembly in generated code contexts, returning a pointer adjusted by `off` while hiding provenance from optimizer assumptions.

State and persistence: The file stores no state. It affects generated code persistence through KASAN ABI version, sanitizer exclusion attributes, randomization/plugin attributes, and optimizer barriers.

Dependencies and integration points: It depends on GCC predefined macros, GCC plugin macros, sanitizer predefines, `CONFIG_ARCH_USE_BUILTIN_BSWAP`, `CONFIG_SHADOW_CALL_STACK`, `CONFIG_KCOV`, and the shared compiler attribute layer.

Risks and test signals: Risks include wrong version feature assumptions, missing sanitizer suppressions in low-level code, optimizer miscompilation when `RELOC_HIDE` is removed or changed, and plugin attribute drift. Test signals are GCC matrix builds, KASAN/KCSAN/KCOV combinations, builds with GCC plugins and randstruct, PPC or other architecture tests sensitive to pointer provenance, and warning-pragmas smoke tests.
