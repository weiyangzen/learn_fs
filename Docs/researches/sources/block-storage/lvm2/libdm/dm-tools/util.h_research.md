# File Research: sources/block-storage/lvm2/libdm/dm-tools/util.h

Purpose: provides small shared utility macros and portability helpers for device-mapper tools.

Read coverage: complete file read, 169 lines.

Key contents:
- Includes `libdm/libdevmapper.h`.
- Defines GCC analyzer diagnostic suppression macros for file-descriptor, malloc-leak, and buffer warnings on GCC 10+ non-Clang builds.
- Defines type-checked GNU-style `min()` and `max()` expression macros.
- Defines `is_power_of_2()`.
- Wraps `dm_strncpy()` as `_dm_strncpy()` with `warn_unused_result`.
- Provides `clz()` and `clzll()` using compiler builtins when available, with fallback implementations for older compilers.
- Requires either system `ffs()` or `__builtin_ffs`; otherwise compilation fails.
- Defines `KERNEL_VERSION()` and printf-format helper macros for sizes, signed/unsigned integer widths, pid values, pointers, and LVM VG IDs.

Dependencies:
- Relies on configuration macros such as `HAVE___BUILTIN_CLZ`, `HAVE___BUILTIN_CLZLL`, `HAVE_FFS`, and `HAVE___BUILTIN_FFS`.
- Relies on libdevmapper macros such as `DM_TO_STRING()` and `ID_LEN`.

Risk and edge cases:
- `min()` and `max()` rely on GNU statement expressions and compile-time type comparison, so they are not ISO C portable.
- `_dm_strncpy()` enforces checked return values only when callers use this wrapper rather than `dm_strncpy()` directly.
- The fallback `clzll()` delegates to `clz()` for 32-bit halves and assumes the configured `clz()` behavior returns bit-width for zero.
- Missing `ffs()` support is a hard build-time error.
