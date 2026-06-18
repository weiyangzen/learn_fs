# File Research: sources/block-storage/lvm2/lib/misc/util.h

This header defines common compiler, math, bit, version, and printf-format utilities.

Content:
- GCC analyzer suppression pragmas for fd, leak, and buffer warnings.
- Type-checking `min()` and `max()` macros.
- `is_power_of_2()`.
- Checked `_dm_strncpy()` wrapper marked `warn_unused_result`.
- `clz()` and `clzll()` using builtins or portable fallbacks.
- `ffs()` fallback requirement.
- `KERNEL_VERSION()`.
- Portable printf format macro aliases such as `FMTu64`, `FMTsize_t`, `FMTVGID`.

Dependencies:
- `libdm/libdevmapper.h`.

Correctness notes:
- `min`/`max` use GNU statement expressions and type comparison tricks.
- Fallback `clz()` returns 32 for zero; `clzll()` returns 64 for zero via fallback path.

Role:
- Widely included low-level helper header.
