# Group Research: group_1202_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_softfloat_bits64_soft_68df1ac7c9b8

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every listed source file was read completely and summarized separately.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/bits64/softfloat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/bits64/softfloat.c

Read completely: 5647 lines, 192064 bytes.

This is NetBSD libc's 64-bit-integer implementation of John Hauser's SoftFloat Release 2a, adapted for NetBSD and for GCC `-msoft-float` helper generation. It implements IEC/IEEE software floating-point conversions, arithmetic, rounding, exception flagging, NaN propagation hooks, and comparisons for `float32`, `float64`, optional `floatx80`, and optional `float128`.

The file defines default software FP state when architecture hooks do not override it: `float_rounding_mode = float_round_nearest_even`, `float_exception_flags = 0`, and `floatx80_rounding_precision = 80` when extended precision is enabled. It includes `softfloat-macros` for low-level multiword integer arithmetic and `softfloat-specialize` for target-specific tininess detection, exception behavior, NaN representation, default NaNs, and NaN propagation.

The implementation is organized around format-specific helper families: bit extraction and packing, subnormal normalization, round-and-pack helpers, integer conversion helpers, format-to-format conversion, round-to-integer, add/subtract via separated-significand helpers, multiply, divide, remainder, square root, and ordered/quiet/signaling comparisons. It handles exact IEEE cases such as signed zero, infinities, subnormals, invalid operations, divide-by-zero, overflow, underflow, inexact results, round-to-nearest-even tie handling, and directed rounding.

`SOFTFLOAT_FOR_GCC` changes the build surface through `softfloat-for-gcc.h`, renaming SoftFloat entry points to GCC/libgcc helper symbols such as `__addsf3`, `__adddf3`, `__fixsfsi`, and `__truncdfsf2`, and excluding routines that GCC or libgcc provides elsewhere. Architecture and ABI conditionals include `FLOAT64_DEMANGLE`/`FLOAT64_MANGLE`, `X80SHIFT`, `X80M68K`, `SOFTFLOAT_NEED_FIXUNS`, `SOFTFLOATSPARC64_FOR_GCC`, `FLOATX80`, and `FLOAT128`.

Notable risk: this file is foundational arithmetic code where small bit-level changes can alter ABI-visible compiler helper behavior. Correctness depends on sticky-bit jamming, normalization shifts, tie-to-even masks, NaN classification, target-specific exception hooks, and global or remapped FP state semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/bits64/softfloat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/eqdf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/eqdf2.c

Read completely: 24 lines, 513 bytes.

Defines GCC helper `__eqdf2(float64, float64)` for double-precision equality. It includes `softfloat-for-gcc.h`, `milieu.h`, and `softfloat.h`, then returns `!float64_eq(a, b)`.

The return convention follows the local comment from `libgcc1.c`: `!(a == b)`, so equal operands return `0`; unequal or unordered comparisons return nonzero according to `float64_eq` behavior.

Risk: thin ABI adapter; correctness depends on preserving GCC's inverted equality convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/eqdf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/eqsf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/eqsf2.c

Read completely: 24 lines, 513 bytes.

Defines GCC helper `__eqsf2(float32, float32)` for single-precision equality. It returns `!float32_eq(a, b)`.

Risk: adapter only; NaN and signed-zero semantics are delegated to `float32_eq`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/eqsf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/eqtf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/eqtf2.c

Read completely: 26 lines, 555 bytes.

Defines GCC helper `__eqtf2(float128, float128)` when `FLOAT128` is enabled. It returns `!float128_eq(a, b)`.

Risk: contributes no symbol unless quadruple precision is compiled in; otherwise behavior is the same inverted equality convention as the single and double wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/eqtf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/flt_rounds.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/flt_rounds.c

Read completely: 33 lines, 685 bytes.

Implements `__flt_rounds()`, mapping `fpgetround()` values to C `FLT_ROUNDS` return values. The normal map is nearest `1`, toward zero `0`, upward `2`, downward `3`; on `__m68k__`, upward/downward map entries are swapped to match that platform's rounding-mode encoding.

Risk: indexes directly with `fpgetround()`, so it assumes the current rounding mode is a valid enum value.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/flt_rounds.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpgetmask.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpgetmask.c

Read completely: 61 lines, 2184 bytes.

Implements `fpgetmask()`, returning the current software floating-point exception mask from `float_exception_mask`. It provides a weak alias from `fpgetmask` to `_fpgetmask`.

For `SOFTFLOATM68K_FOR_GCC`, this file also defines `_softfloat_float_exception_flags`, `_softfloat_float_exception_mask`, and `_softfloat_float_rounding_mode`, the remapped global state used by the GCC softfloat namespace.

Risk: direct software FP state accessor; thread-local or hardware-synchronized behavior must come from architecture-specific remapping or hooks outside this file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpgetmask.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpgetround.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpgetround.c

Read completely: 55 lines, 2026 bytes.

Implements `fpgetround()`, returning `float_rounding_mode`. It includes namespace handling, `ieeefp.h`, optional GCC softfloat remapping, and provides weak alias `_fpgetround`.

Risk: returns the raw software rounding enum with no validation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpgetround.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpgetsticky.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpgetsticky.c

Read completely: 55 lines, 2036 bytes.

Implements `fpgetsticky()`, returning current software floating-point sticky exception flags from `float_exception_flags`. It provides weak alias `_fpgetsticky`.

Risk: direct state read; concurrency or per-thread semantics depend on surrounding libc or machine integration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpgetsticky.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpsetmask.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpsetmask.c

Read completely: 60 lines, 2173 bytes.

Implements `fpsetmask(fp_except mask)`. If `set_float_exception_mask` is defined, it delegates to that hook; otherwise it stores `mask` in `float_exception_mask` and returns the previous mask. It provides weak alias `_fpsetmask`.

Risk: fallback path accepts the mask unchanged; validation or hardware synchronization must be supplied by an override hook.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpsetmask.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpsetround.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpsetround.c

Read completely: 60 lines, 2174 bytes.

Implements `fpsetround(fp_rnd rnd_dir)`. If `set_float_rounding_mode` exists, it delegates there; otherwise it swaps `float_rounding_mode` with `rnd_dir` and returns the old mode. It provides weak alias `_fpsetround`.

Risk: fallback path does not validate `rnd_dir`, so invalid enum values would affect later SoftFloat rounding.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpsetround.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpsetsticky.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpsetsticky.c

Read completely: 60 lines, 2196 bytes.

Implements `fpsetsticky(fp_except except)`. If `set_float_exception_flags` exists, it calls `set_float_exception_flags(except, 1)`; otherwise it replaces `float_exception_flags` and returns the previous flags. It provides weak alias `_fpsetsticky`.

Risk: replacement rather than merge is intentional for this API, but callers clearing flags must account for it.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpsetsticky.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gedf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/gedf2.c

Read completely: 24 lines, 519 bytes.

Defines GCC helper `__gedf2(float64, float64)` for double greater-or-equal comparison. It implements `(a >= b) - 1` as `float64_le(b, a) - 1`.

Risk: comparison exceptions and unordered behavior are delegated to `float64_le`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gedf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gesf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/gesf2.c

Read completely: 24 lines, 519 bytes.

Defines GCC helper `__gesf2(float32, float32)` for single greater-or-equal comparison. It returns `float32_le(b, a) - 1`.

Risk: adapter only; correctness is ABI convention plus SoftFloat comparison behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gesf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/getf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/getf2.c

Read completely: 28 lines, 563 bytes.

Defines GCC helper `__getf2(float128, float128)` when `FLOAT128` is enabled. It implements `(a >= b) - 1` as `float128_le(b, a) - 1`.

Risk: compiled only with quadruple support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/getf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gexf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/gexf2.c

Read completely: 31 lines, 623 bytes.

Defines GCC helper `__gexf2(floatx80, floatx80)` when `FLOATX80` is enabled. Normal builds return `floatx80_le(b, a) - 1`; `X80M68K` builds return `floatx80_le(b, a) ? -1 : 0`.

Risk: extended-precision m68k comparison uses architecture-specific result encoding.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gexf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gtdf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/gtdf2.c

Read completely: 24 lines, 508 bytes.

Defines GCC helper `__gtdf2(float64, float64)` for double greater-than comparison. It returns `float64_lt(b, a)`.

Risk: unordered and invalid-exception behavior is entirely delegated to `float64_lt`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gtdf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gtsf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/gtsf2.c

Read completely: 24 lines, 508 bytes.

Defines GCC helper `__gtsf2(float32, float32)` for single greater-than comparison. It returns `float32_lt(b, a)`.

Risk: thin ABI wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gtsf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gttf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/gttf2.c

Read completely: 28 lines, 552 bytes.

Defines GCC helper `__gttf2(float128, float128)` when `FLOAT128` is enabled. It returns `float128_lt(b, a)`.

Risk: compiled only with quadruple support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gttf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gtxf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/gtxf2.c

Read completely: 31 lines, 618 bytes.

Defines GCC helper `__gtxf2(floatx80, floatx80)` when `FLOATX80` is enabled. Normal builds return `floatx80_lt(b, a)`; `X80M68K` builds map `floatx80_lt(b, a) == -1` to `1`, otherwise `-1`.

Risk: m68k extended comparison has non-boolean return encoding that must stay aligned with the internal x80 comparison wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/gtxf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/ledf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/ledf2.c

Read completely: 24 lines, 519 bytes.

Defines GCC helper `__ledf2(float64, float64)` for double less-or-equal comparison. It implements `1 - (a <= b)` as `1 - float64_le(a, b)`.

Risk: adapter only; comparison flags come from `float64_le`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/ledf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/lesf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/lesf2.c

Read completely: 24 lines, 519 bytes.

Defines GCC helper `__lesf2(float32, float32)` for single less-or-equal comparison. It returns `1 - float32_le(a, b)`.

Risk: ABI convention wrapper only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/lesf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/letf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/letf2.c

Read completely: 28 lines, 563 bytes.

Defines GCC helper `__letf2(float128, float128)` when `FLOAT128` is enabled. It returns `1 - float128_le(a, b)`.

Risk: compiled only with quadruple support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/letf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/ltdf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/ltdf2.c

Read completely: 24 lines, 512 bytes.

Defines GCC helper `__ltdf2(float64, float64)` for double less-than comparison. It implements `-(a < b)` as `-float64_lt(a, b)`.

Risk: relies on `float64_lt` returning `0` or `1`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/ltdf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/ltsf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/ltsf2.c

Read completely: 24 lines, 512 bytes.

Defines GCC helper `__ltsf2(float32, float32)` for single less-than comparison. It returns `-float32_lt(a, b)`.

Risk: thin ABI wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/ltsf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/lttf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/lttf2.c

Read completely: 28 lines, 556 bytes.

Defines GCC helper `__lttf2(float128, float128)` when `FLOAT128` is enabled. It returns `-float128_lt(a, b)`.

Risk: compiled only with quadruple support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/lttf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/nedf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/nedf2.c

Read completely: 24 lines, 510 bytes.

Defines GCC helper `__nedf2(float64, float64)` for double not-equal comparison. It returns `!float64_eq(a, b)`.

Risk: unordered comparisons follow `float64_eq`; NaNs compare not equal.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/nedf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/negdf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/negdf2.c

Read completely: 24 lines, 520 bytes.

Defines GCC helper `__negdf2(float64)` for double negation. It toggles the sign bit with XOR against `FLOAT64_MANGLE(0x8000000000000000ULL)`.

Risk: depends on `FLOAT64_MANGLE` matching the target double representation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/negdf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/negsf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/negsf2.c

Read completely: 24 lines, 501 bytes.

Defines GCC helper `__negsf2(float32)` for single negation. It toggles the sign bit with XOR against `0x80000000`.

Risk: direct bit operation; no NaN canonicalization or exception behavior is intended.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/negsf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/negtf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/negtf2.c

Read completely: 29 lines, 573 bytes.

Defines GCC helper `__negtf2(float128)` when `FLOAT128` is enabled. It toggles the sign bit in `a.high` using `FLOAT64_MANGLE(0x8000000000000000ULL)` and returns the modified value.

Risk: assumes the quadruple sign bit resides in the high 64-bit word in the expected layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/negtf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/negxf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/negxf2.c

Read completely: 27 lines, 543 bytes.

Defines GCC helper `__negxf2(floatx80)` when `FLOATX80` is enabled. Instead of toggling a sign bit directly, it returns `__mulxf3(a, __floatsixf(-1))`.

Risk: negation depends on extended multiply and integer-to-extended conversion helpers, so it can raise or propagate behavior through arithmetic rather than a pure sign-bit operation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/negxf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/nesf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/nesf2.c

Read completely: 24 lines, 510 bytes.

Defines GCC helper `__nesf2(float32, float32)` for single not-equal comparison. It returns `!float32_eq(a, b)`.

Risk: adapter only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/nesf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/netf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/netf2.c

Read completely: 28 lines, 554 bytes.

Defines GCC helper `__netf2(float128, float128)` when `FLOAT128` is enabled. It returns `!float128_eq(a, b)`.

Risk: compiled only with quadruple support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/netf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/nexf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/nexf2.c

Read completely: 31 lines, 613 bytes.

Defines GCC helper `__nexf2(floatx80, floatx80)` when `FLOATX80` is enabled. Normal builds return `!floatx80_eq(a, b)`; `X80M68K` builds return `floatx80_eq(a, b) ? 1 : 0`.

Risk: m68k extended comparison uses an architecture-specific convention that differs from the normal boolean inversion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/nexf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/softfloat-for-gcc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/softfloat-for-gcc.h

Read completely: 214 lines, 6308 bytes.

This header remaps SoftFloat symbols to implementation-private names and GCC/libgcc helper names. It first moves external-linkage SoftFloat state and comparison helpers into the `_softfloat_*` namespace, including exception flags, exception mask, rounding mode, `float_raise`, and selected `float32`/`float64`/`float128` comparisons.

It then maps arithmetic, conversion, integer-fix, unsigned-fix, extension, and truncation routines to compiler helper names such as `__addsf3`, `__adddf3`, `__mulsf3`, `__fixsfsi`, `__fixdfdi`, `__extendsfdf2`, and `__truncdfsf2`. Some comparison and negation macro groups are disabled with `#if 0`, while the extended `floatx80` comparison mapping is enabled because the comment notes it is not in libgcc.

For `__ARM_EABI__`, it remaps the generic GCC helper names to ARM AEABI names such as `__aeabi_fadd`, `__aeabi_dadd`, `__aeabi_i2f`, `__aeabi_f2iz`, and `__aeabi_d2f`, including optional VFP PCS header inclusion.

Risk: this file is ABI glue. Any macro mismatch can export the wrong compiler runtime symbol, collide with libgcc, or break architecture-specific calling conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/softfloat-for-gcc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/templates/milieu.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/templates/milieu.h

Read completely: 48 lines, 2040 bytes.

Template header from SoftFloat Release 2a. It includes the processor-specific generated header path `../../../processors/!!!processor.h`, which is expected to provide common integer types and `flag`.

It also defines symbolic Boolean literals `FALSE = 0` and `TRUE = 1`.

Risk: this is a template with `!!!processor` substitution placeholders; it is not directly usable until generated for a target processor profile.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/templates/milieu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/templates/softfloat.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/templates/softfloat.h

Read completely: 290 lines, 10816 bytes.

Template public header for SoftFloat Release 2a. It enables both `FLOATX80` and `FLOAT128` in the template, defines software FP types using generated placeholder types such as `!!!bits32`, `!!!bits64`, and `!!!flag`, and declares the optional `floatx80` and `float128` structures.

It declares global SoftFloat environment state: `float_detect_tininess`, `float_rounding_mode`, `float_exception_flags`, and `floatx80_rounding_precision`. It defines enum values for tininess detection, rounding modes, and exception flags, and declares `float_raise`.

The rest of the header is the API surface for conversions and operations across `int32`, `int64`, `float32`, `float64`, optional `floatx80`, and optional `float128`: conversions to integers, round-to-zero conversions, format conversions, round-to-int, add/subtract/multiply/divide/remainder/sqrt, ordered comparisons, signaling equality, quiet comparisons, and signaling-NaN predicates.

Risk: this is a generator template with `!!!` placeholders; generated architecture headers must substitute exact integer typedefs and flags or the implementation ABI will not match the C files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/templates/softfloat.h -->