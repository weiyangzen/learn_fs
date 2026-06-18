# Group Research: group_1193_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_gdtoa_dtoa_c_sources__a7d676ad15da

Scope: `Docs/research_subset_a.md`; all listed files are under `sources/os/bsd/netbsd-src`, which is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/dtoa.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/dtoa.c

Purpose: Implements David Gay's classic `dtoa()` conversion from native `double` to a decimal digit string.

Core behavior:
- Handles sign, zero, infinity, and NaN before numeric conversion.
- Supports modes 0-9 for shortest, ecvt-style, fcvt-style, and debug variants.
- Estimates decimal exponent `k = floor(log10(d))`, then corrects it when needed.
- Uses a fast floating-point path for small requested digit counts when correctness can be guaranteed.
- Falls back to multiprecision `Bigint` arithmetic for exact stopping and rounding decisions.
- Honors IEEE round-to-nearest/even and optional `Honor_FLT_ROUNDS` directed rounding.
- Returns allocated strings via `rv_alloc`/`nrv_alloc`; callers release with `freedtoa`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `d2b`, `i2b`, `pow5mult`, `lshift`, `multadd`, `quorem`, `cmp`, `diff`, `Balloc`, and `Bfree`.
- Depends on native double layout macros such as `word0`, `word1`, exponent masks, and endian definitions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/dtoa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_Qfmt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_Qfmt.c

Purpose: Formats a 128-bit IEEE-style quad value into a general decimal string.

Core behavior:
- Defines endian-specific word order for four `ULong` words.
- Extracts sign, exponent, and 113-bit significand bits.
- Handles zero, infinity, and NaN directly.
- Uses `FPI {113, ...}` and `gdtoa()` for finite numbers.
- Uses mode 0 when `ndig <= 0`, otherwise mode 2 for requested significant digits.
- Passes the generated digit string to `g__fmt()` for final decimal/exponent formatting.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `gdtoa`, `g__fmt`, `strcp`, and optional `gdtoa_fltrnds.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_Qfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g__fmt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g__fmt.c

Purpose: Shared final formatter for `g_*fmt` decimal output.

Core behavior:
- Converts a raw digit buffer plus decimal point position into printable form.
- Emits fixed notation when the decimal point is in a compact range.
- Emits exponent notation when `decpt <= -4` or the exponent is far beyond the digit count.
- Inserts sign and locale decimal point when `USE_LOCALE` is enabled.
- Checks `bufsize` before writing and returns `NULL` on insufficient space.
- Frees the temporary `gdtoa` digit buffer before returning.

Dependencies:
- Includes `gdtoaimp.h` and optionally `locale.h`.
- Uses `localeconv`, `MALLOC`, `strcpy`, `strlen`, and `freedtoa`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g__fmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_ddfmt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_ddfmt.c

Purpose: Formats a double-double value held as two `double`s.

Core behavior:
- Handles NaN, infinity, signed zero, and infinity-minus-infinity cases.
- Orders the two components by magnitude, converts each to `Bigint`, aligns exponents, then sums or subtracts.
- Normalizes trailing zero bits before formatting.
- Chooses an `FPI` width based on the computed significand, with a minimum of 106 bits.
- Uses `gdtoa()` and `g__fmt()` for final output.

Dependencies:
- Includes `gdtoaimp.h` and `string.h`.
- Uses `d2b`, `lshift`, `diff`, `sum`, `rshift`, `lo0bits`, `hi0bits`, `gdtoa`, and `Bfree`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_ddfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_dfmt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_dfmt.c

Purpose: Formats a native IEEE double into a general decimal string.

Core behavior:
- Extracts sign, exponent, and 53-bit significand from two `ULong` words.
- Handles zero, infinity, and NaN directly.
- Converts finite values through `gdtoa()` with an IEEE double `FPI`.
- Uses shortest mode when `ndig <= 0`, otherwise requested significant digits.
- Sends the result through `g__fmt()`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `gdtoa`, `g__fmt`, `strcp`, and optional `gdtoa_fltrnds.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_dfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_ffmt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_ffmt.c

Purpose: Formats a native IEEE float into a general decimal string.

Core behavior:
- Extracts sign, exponent, and 24-bit significand from one `ULong`.
- Handles zero, infinity, and NaN directly.
- Uses `FPI {24, ...}` and `gdtoa()` for finite values.
- Requires extra buffer space for shortest-mode float output.
- Delegates final decimal/exponent layout to `g__fmt()`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `gdtoa`, `g__fmt`, `strcp`, and optional `gdtoa_fltrnds.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_ffmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_xLfmt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_xLfmt.c

Purpose: Formats an 80-bit extended value stored in three `ULong` words.

Core behavior:
- Defines endian-specific word layout.
- Extracts sign, 15-bit exponent, and 64-bit significand.
- Handles zero, infinity, and NaN directly.
- Uses `FPI {64, ...}` and `gdtoa()` for finite values.
- Emits shortest or requested-significant-digit output through `g__fmt()`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `gdtoa`, `g__fmt`, `strcp`, and optional `gdtoa_fltrnds.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_xLfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_xfmt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_xfmt.c

Purpose: Formats an 80-bit extended value stored as five `UShort` words.

Core behavior:
- Defines endian-specific five-word layout.
- Extracts sign, 15-bit exponent, and 64-bit significand.
- Handles zero, infinity, and NaN directly.
- Uses `FPI {64, ...}` and `gdtoa()` for finite values.
- Delegates final printable layout to `g__fmt()`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `gdtoa`, `g__fmt`, `strcp`, and optional `gdtoa_fltrnds.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_xfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa.c

Purpose: Generalized binary-floating-to-decimal formatter for arbitrary formats described by `FPI`.

Core behavior:
- `bitstob()` converts caller-supplied significand words into a `Bigint`.
- `gdtoa()` accepts an `FPI`, binary exponent, significand bits, result-kind flags, mode, and requested digits.
- Handles zero, finite, infinity, and NaN result kinds.
- Computes a decimal exponent estimate, tries a fast floating-point digit path where valid, and otherwise uses multiprecision arithmetic.
- Supports shortest, ecvt-style, fcvt-style, and debug modes.
- Tracks inexact direction by OR-ing `STRTOG_Inexlo` or `STRTOG_Inexhi` into `*kindp`.
- Handles directed rounding via `fpi->rounding`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses the shared `Bigint` helpers, `quorem`, powers-of-five scaling, and allocation helpers.
- Called by type-specific formatters such as `g_dfmt`, `g_ffmt`, `g_Qfmt`, `ldtoa`, and double-double formatting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa.h

Purpose: Public interface for the gdtoa conversion library.

Core behavior:
- Defines integer aliases `Long`, `ULong`, and `UShort`.
- Defines `FPI`, which describes binary precision, exponent limits, rounding mode, and sudden-underflow behavior.
- Defines `STRTOG_*` result flags for parsed value class, sign, inexactness, underflow, overflow, and no-memory.
- Provides symbol renaming to NetBSD-private libc names such as `__dtoa`, `__gdtoa`, and `__strtodg_D2A`.
- Declares formatting APIs, parsing APIs, interval APIs, and conversion helpers.

Dependencies:
- Includes generated `arith.h`, `<stddef.h>`, and `<stdint.h>`.
- Provides C++ extern guards and K&R compatibility macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa_fltrnds.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa_fltrnds.h

Purpose: Inline include fragment for selecting an `FPI` adjusted to the current floating-point rounding mode.

Core behavior:
- Declares local `fpi`, `fpi1`, and `Rounding` variables for callers.
- Uses `Flt_Rounds` when `Trust_FLT_ROUNDS` is defined.
- Otherwise maps `fegetround()` to gdtoa rounding values.
- Reuses `fpi0` for round-to-nearest and copies it into `fpi1` for directed rounding.

Dependencies:
- Must be included inside functions that already define `fpi0`.
- Relies on `Flt_Rounds`, `fegetround`, and `FPI` definitions from `gdtoaimp.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa_fltrnds.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa_locks.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa_locks.c

Purpose: Provides global locks for gdtoa in threaded NetBSD libc builds.

Core behavior:
- Defines `mutex_t __gdtoa_locks[2]` only when `_REENTRANT` is enabled.
- The two locks protect Bigint freelists/private allocation and lazy powers-of-five cache construction.

Dependencies:
- Includes `gdtoaimp.h`, which maps `ACQUIRE_DTOA_LOCK` and `FREE_DTOA_LOCK` to these locks under `MULTIPLE_THREADS`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa_locks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoaimp.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoaimp.h

Purpose: Internal implementation header for the gdtoa library.

Core behavior:
- Describes supported architecture modes: IEEE big/little endian, VAX, and IBM floating point.
- Enables NetBSD defaults: `INFNAN_CHECK`, `USE_LOCALE`, and thread support under `_REENTRANT`.
- Defines double word access macros, exponent/significand masks, constants, `Bigint`, packing mode, lock macros, and symbol renames.
- Declares all internal helpers and shared power-of-ten tables.
- Defines NaN word selection based on endian and generated `gd_qnan.h`.

Dependencies:
- Includes `gdtoa.h`, `gd_qnan.h`, libc headers, optional `fenv.h`, and `reentrant.h`.
- Requires exactly one architecture floating-point format macro from generated `arith.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoaimp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gethex.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gethex.c

Purpose: Parses hexadecimal floating constants for `strtod` and `strtodg`.

Core behavior:
- Parses `0x`/`0X` significands, optional locale decimal point, and binary `p`/`P` exponent.
- Builds a `Bigint` from hexadecimal digits in little-endian word order.
- Scales to `fpi->nbits`, computes lost bits, and applies rounding mode.
- Handles huge exponents by returning infinity or max finite depending on rounding direction.
- Handles tiny exponents by returning zero or the smallest denormal according to rounding and sign.
- Returns `STRTOG_*` flags and writes the parsed significand/exponent through `bp` and `expt`.

Dependencies:
- Includes `gdtoaimp.h` and optionally `locale.h`.
- Uses `hexdig`, `hexdig_init_D2A`, `Balloc`, `Bfree`, `rshift`, `lshift`, `any_on`, `increment`, and `errno`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gethex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gmisc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gmisc.c

Purpose: Provides bit-level `Bigint` helpers used by generalized conversion paths.

Core behavior:
- `rshift()` shifts a `Bigint` right in-place and compacts its word count.
- `trailz()` counts trailing zero bits in a `Bigint`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `lo0bits`, `ULbits`, `kshift`, `kmask`, and NetBSD `_DIAGASSERT`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gmisc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/hd_init.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/hd_init.c

Purpose: Initializes the hexadecimal digit lookup table used by hex parsing.

Core behavior:
- `htinit()` fills `hexdig` entries for a digit sequence with a fixed increment.
- `hexdig_init_D2A()` initializes mappings for `0-9`, `A-F`, and `a-f`.
- Encodes hex digit values offset so zero/non-hex can be distinguished cheaply.

Dependencies:
- Includes `gdtoaimp.h`.
- Writes the global `hexdig[]` declared in `gdtoaimp.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/hd_init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/hdtoa.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/hdtoa.c

Purpose: Converts `double` and `long double` values to hexadecimal digit strings.

Core behavior:
- `roundup()` increments a hexadecimal digit buffer and reports exponent carry.
- `dorounding()` applies `FLT_ROUNDS` to a generated hex digit buffer.
- `hdtoa()` handles double sign, zero, normal, subnormal, infinity, and NaN values.
- `hdtoa()` emits nibble-aligned hexadecimal significand digits and binary exponent `decpt`.
- `hldtoa()` provides the same behavior for `long double` when it has greater precision than double; otherwise it delegates to `hdtoa`.
- Uses `INT_MAX` as the special exponent for infinity/NaN instead of dtoa's `9999`.

Dependencies:
- Uses `<machine/ieee.h>` or VAX floating definitions, `<float.h>`, `<math.h>`, and `gdtoaimp.h`.
- Uses `rv_alloc` and `nrv_alloc`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/hdtoa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/hexnan.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/hexnan.c

Purpose: Parses hexadecimal NaN payloads such as `NaN(...)`.

Core behavior:
- Allows optional whitespace and optional `0x` prefixes inside the payload.
- Accumulates hex digits into the target significand word array.
- Supports multiple whitespace-separated hex fields.
- Truncates payload bits to the target `FPI` precision.
- Ensures a nonzero payload for `STRTOG_NaNbits`.
- Falls back to plain `STRTOG_NaN` for invalid or absent payloads.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `hexdig`, `hexdig_init_D2A`, and internal `L_shift`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/hexnan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/ldtoa.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/ldtoa.c

Purpose: Provides `ldtoa()` as a `long double` wrapper around `gdtoa()`.

Core behavior:
- Builds an `FPI` from `LDBL_MANT_DIG`, `LDBL_MIN_EXP`, and `LDBL_MAX_EXP`.
- Extracts sign, binary exponent, and significand bits using machine long-double layout macros.
- Classifies zero, normal, subnormal, infinity, and NaN.
- Sets implicit integer/significand bits when required by the platform format.
- Converts through `gdtoa()` and maps `gdtoa`'s `-32768` special decimal point to `INT_MAX`.
- Falls back to casting through `double` when no extended long double is available.

Dependencies:
- Uses `<machine/ieee.h>`, `<float.h>`, `<math.h>`, and `gdtoaimp.h`.
- Depends on `EXT_TO_ARRAY32` and related machine floating-point layout macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/ldtoa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/makefile

Purpose: Standalone upstream-style makefile for building gdtoa outside the NetBSD libc build.

Core behavior:
- Builds generated `arith.h` with `arithchk.c`.
- Builds generated `gd_qnan.h` with `qnan.c`.
- Compiles the gdtoa source list into `gdtoa.a`.
- Provides optional `Printf` target and `xsum.out` source integrity check.
- Provides `clean` target for generated headers, objects, archive, and checksum files.

Dependencies:
- Assumes `cc`, `ar`, and optional `ranlib`.
- Lists the upstream source distribution files in `xs0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/misc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/misc.c

Purpose: Implements core multiprecision arithmetic and shared constants for gdtoa.

Core behavior:
- Provides `Balloc`/`Bfree` with freelists and optional private memory pool.
- Implements low/high zero-bit counting, multiply-add, integer-to-Bigint, multiplication, powers-of-five multiplication, left shift, compare, difference, `b2d`, and `d2b`.
- Provides power-of-ten tables `tens`, `bigtens`, and `tinytens`.
- Provides `strcp_D2A` and a private `memcpy_D2A` fallback.
- Handles 32-bit and 16-bit limb packing modes and optional 64-bit multiplication.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses lock macros for shared freelists and lazy power-of-five cache.
- Used by nearly every conversion file in this directory.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/qnan.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/qnan.c

Purpose: Build-time helper that generates quiet-NaN bit-pattern definitions.

Core behavior:
- Detects IEEE endian mode from `arith.h`.
- Constructs float and double infinities and subtracts them to produce quiet NaNs.
- Prints `#define` lines for float, double, and long-double NaN words.
- Emits all-ones long-double fallback patterns when `NO_LONG_LONG` is defined.

Dependencies:
- Includes `<stdio.h>` and generated `arith.h`.
- Used by the standalone `makefile` to generate `gd_qnan.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/qnan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/smisc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/smisc.c

Purpose: Shared parser-side `Bigint` utilities.

Core behavior:
- `s2b()` converts decimal digits from a source string into a `Bigint`.
- `ratio()` computes an approximate floating ratio of two `Bigint`s.
- `match()` case-insensitively matches `inf`/`nan` suffixes when infinity/NaN parsing is enabled.
- `copybits()` copies a `Bigint` into a fixed-width word array.
- `any_on()` checks whether any discarded low bits are nonzero.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `multadd`, `b2d`, `lo0bits`, `Storeinc`, and bit packing macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/smisc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIQ.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIQ.c

Purpose: Parses a string into a quad-precision interval.

Core behavior:
- Uses `FPI {113, ...}` for IEEE quad precision.
- Allocates a first `Bigint` result buffer and calls `strtoIg`.
- Converts lower/upper interval endpoints with `ULtoQ`.
- If parsing is exact, duplicates the first endpoint into the second.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bfree`, `strtoIg`, and `ULtoQ`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIQ.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoId.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoId.c

Purpose: Parses a string into a double-precision interval.

Core behavior:
- Uses IEEE double `FPI {53, ...}`.
- Calls `strtoIg` to get one exact endpoint or two adjacent endpoints around an inexact value.
- Packs endpoints into `double` storage with `ULtod`.
- Copies the first endpoint to the second when parsing is exact.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bfree`, `strtoIg`, and `ULtod`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoId.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIdd.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIdd.c

Purpose: Parses a string into a double-double interval.

Core behavior:
- Uses a 106-bit `FPI`, with sudden-underflow parameters adjusted by platform.
- Calls `strtoIg` to obtain exact or bounding `Bigint` endpoints.
- Packs endpoints into two-double representations with `ULtodd`.
- Duplicates the first endpoint if no second endpoint is needed.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bfree`, `strtoIg`, and `ULtodd`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIdd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIf.c

Purpose: Parses a string into a single-precision interval.

Core behavior:
- Uses IEEE float `FPI {24, ...}`.
- Calls `strtoIg` to compute exact or adjacent interval bounds.
- Packs endpoints into float storage with `ULtof`.
- Copies the exact endpoint into both outputs when no interval widening is needed.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bfree`, `strtoIg`, and `ULtof`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIg.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIg.c

Purpose: Generic interval parser used by `strtoI*` wrappers.

Core behavior:
- Calls `strtodg` with the caller's `FPI` to produce one rounded result.
- If the parse is exact, returns only one endpoint.
- If inexact low, increments the significand to form the upper adjacent endpoint.
- If inexact high, decrements or clamps to form the lower adjacent endpoint.
- Handles zero, denormal, normal, infinity, sudden-underflow, exponent-boundary, and sign-order cases.
- Orders interval endpoints according to sign so output `[0]` is the lower bound.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg`, `Balloc`, `Bcopy`, `increment`, `decrement`, `set_ones`, `lshift`, and `rshift`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIx.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIx.c

Purpose: Parses a string into an interval for 80-bit extended format stored as five `UShort`s.

Core behavior:
- Uses `FPI {64, ...}` for 64-bit precision extended format.
- Calls `strtoIg` for exact or adjacent endpoint bits.
- Packs endpoints with `ULtox`.
- Copies the first endpoint to the second when exact.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bfree`, `strtoIg`, and `ULtox`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIxL.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIxL.c

Purpose: Parses a string into an interval for 80-bit extended format stored as three `ULong`s.

Core behavior:
- Uses `FPI {64, ...}`.
- Calls `strtoIg` for exact or adjacent interval endpoints.
- Packs endpoints with `ULtoxL`.
- Copies the first endpoint to the second when exact.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bfree`, `strtoIg`, and `ULtoxL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIxL.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtod.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtod.c

Purpose: Implements locale-aware `strtod`/`strtod_l` for native double.

Core behavior:
- Parses leading whitespace, sign, decimal digits, locale decimal point, and decimal exponent.
- Handles C99 hexadecimal floating constants via `gethex`.
- Handles `inf`, `infinity`, `nan`, and optional hex NaN payloads.
- Uses fast floating-point scaling for easy cases.
- Uses `Bigint` refinement for hard cases to produce the correctly rounded double.
- Handles overflow, underflow, denormals, directed rounding, and optional inexact flag behavior.
- Provides aliases for `strtold` when the platform lacks distinct long double.

Dependencies:
- Includes NetBSD namespace headers, `gdtoaimp.h`, optional `<fenv.h>`, locale headers, and `setlocale_local.h`.
- Uses `s2b`, `d2b`, `pow5mult`, `lshift`, `diff`, `ratio`, `ulp`, `gethex`, `hexnan`, and `ULtod`-style bit packing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtodI.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtodI.c

Purpose: Parses a string into a two-double interval bracketing the exact value.

Core behavior:
- Uses double `FPI` with `strtodg`.
- Packs the rounded result into `dd[0]`.
- Uses `STRTOG_Inexlo`/`STRTOG_Inexhi` to decide whether to set the other endpoint to the next higher or lower double.
- Handles sign by reversing inexact direction.
- Handles zero, denormal, normal, infinity, NaN, and NaN payload cases.
- Uses `ulpdown()` to step downward across exponent-boundary cases correctly.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg`, `ulp`, generated NaN constants, and word-level double access macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtodI.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtodg.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtodg.c

Purpose: Generic decimal/hex string parser for arbitrary binary formats described by `FPI`.

Core behavior:
- Provides helper routines `increment`, `decrement`, `all_on`, `set_ones`, `rvOK`, and `mantbits`.
- Parses whitespace, sign, decimal digits, locale decimal point, decimal exponent, hex floats, infinity, and NaN payloads.
- Produces result class flags, inexact direction flags, exponent, and packed significand words.
- Uses fast native-double approximation when possible and exact `Bigint` refinement otherwise.
- Handles all rounding modes, overflow, underflow, gradual/sudden underflow, denormal normalization, and boundary transitions.
- Used as the central parser by `strtof`, `strtod` wrappers, `strtop*`, `strtor*`, and interval APIs.

Dependencies:
- Includes `gdtoaimp.h` and optionally `locale.h`.
- Uses `gethex`, `hexnan`, `s2b`, `d2b`, `copybits`, `pow5mult`, `ratio`, `trailz`, `sum`, `diff`, and `errno`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtodg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtodnrp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtodnrp.c

Purpose: Alternate `strtod` implementation for ia32-style extended-precision arithmetic without forcing 53-bit precision control.

Core behavior:
- Parses through `strtodg` using IEEE double `FPI`.
- Packs the returned bits into native double manually.
- Handles no-number, zero, normal, denormal, infinity, NaN, and NaN payload cases.
- On no-memory, sets `errno = ERANGE` and returns a large finite value.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg`, `Big0`, `Big1`, generated NaN constants, and endian word macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtodnrp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtof.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtof.c

Purpose: Implements locale-aware `strtof`/`strtof_l` for IEEE float.

Core behavior:
- `_int_strtof_l()` parses with `strtodg` and `FPI {24, ...}`.
- Packs normal, denormal, infinity, NaN, and NaN payload results into one float word.
- Applies the sign bit from `STRTOG_Neg`.
- Returns `HUGE_VALF` and sets `errno` on no-memory.
- Public wrappers use `_current_locale()` or an explicit locale.

Dependencies:
- Includes NetBSD namespace headers, `gdtoaimp.h`, `<locale.h>`, and `setlocale_local.h`.
- Uses optional `gdtoa_fltrnds.h` for current rounding mode.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtof_vaxf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtof_vaxf.c

Purpose: VAX F_floating variant of `strtof`/`strtof_l`.

Core behavior:
- Parses with a VAX-specific 24-bit `FPI`.
- Packs normal results into VAX F_floating bit layout.
- Handles no-number, zero, infinity, and sign bit placement.
- Returns `HUGE_VALF` and sets `errno` on no-memory.

Dependencies:
- Includes NetBSD namespace headers, `gdtoaimp.h`, `<locale.h>`, and `setlocale_local.h`.
- Adapted specifically for VAX floating representation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtof_vaxf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_pQ.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_pQ.c

Purpose: Builds `strtold` for quad-precision long double.

Core behavior:
- Defines `GDTOA_LD_FMT` as `Q`.
- Includes `strtold_subr.c`, which expands to `strtold`/`strtold_l` calling `strtopQ`.

Dependencies:
- Depends entirely on `strtold_subr.c` and `strtopQ`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_pQ.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_px.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_px.c

Purpose: Builds `strtold` for extended long double stored in `x` format.

Core behavior:
- Defines `GDTOA_LD_FMT` as `x`.
- Includes `strtold_subr.c`, which expands to `strtold`/`strtold_l` calling `strtopx`.

Dependencies:
- Depends entirely on `strtold_subr.c` and `strtopx`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_px.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_pxL.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_pxL.c

Purpose: Builds `strtold` for extended long double stored in `xL` format.

Core behavior:
- Defines `GDTOA_LD_FMT` as `xL`.
- Includes `strtold_subr.c`, which expands to `strtold`/`strtold_l` calling `strtopxL`.

Dependencies:
- Depends entirely on `strtold_subr.c` and `strtopxL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_pxL.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_subr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_subr.c

Purpose: Shared include file for format-specific `strtold` implementations.

Core behavior:
- Requires the including file to define `GDTOA_LD_FMT`.
- Builds `STRTOP(GDTOA_LD_FMT)` into a call to `strtopQ`, `strtopx`, or `strtopxL`.
- Implements `_int_strtold_l()`, `strtold()`, and `strtold_l()`.
- Uses `_current_locale()` for the non-locale API.
- Requires `__HAVE_LONG_DOUBLE`.

Dependencies:
- Includes NetBSD namespace headers, `<math.h>`, `<stdlib.h>`, `gdtoa.h`, `<locale.h>`, and `setlocale_local.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopQ.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopQ.c

Purpose: Parses a string into quad-precision binary storage.

Core behavior:
- Defines endian-specific four-word layout.
- Uses `FPI {113, ...}` and `strtodg`.
- Packs zero, normal, denormal, infinity, NaN, and NaN payload results.
- Sets the sign bit from `STRTOG_Neg`.
- Uses generated long-double quiet-NaN words for plain NaN.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses optional `gdtoa_fltrnds.h`, `strtodg`, and `ld_QNAN*` constants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopQ.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopd.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopd.c

Purpose: Parses a string into double storage using current rounding when enabled.

Core behavior:
- Uses IEEE double `FPI {53, ...}`.
- Calls `strtodg`, then packs the result with `ULtod`.
- Returns `STRTOG_NoMemory` without packing on allocation failure.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses optional `gdtoa_fltrnds.h`, `strtodg`, and `ULtod`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopdd.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopdd.c

Purpose: Parses a string into double-double storage.

Core behavior:
- Uses a 106-bit `FPI`.
- Calls `strtodg` and packs the result as two doubles.
- Handles normal, denormal subcases, infinity, NaN, and sign propagation to both doubles.
- Splits the high and low portions of the significand into two IEEE double encodings.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses optional `gdtoa_fltrnds.h`, `strtodg`, and `hi0bits`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopdd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopf.c

Purpose: Parses a string into IEEE float storage.

Core behavior:
- Uses float `FPI {24, ...}`.
- Calls `strtodg`.
- Packs zero, normal, denormal, infinity, NaN, and NaN payload values into one `ULong`.
- Sets sign bit from `STRTOG_Neg`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses optional `gdtoa_fltrnds.h`, `strtodg`, and `f_QNAN`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopx.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopx.c

Purpose: Parses a string into 80-bit extended storage represented by five `UShort`s.

Core behavior:
- Defines endian-specific five-word layout.
- Uses `FPI {64, ...}` and `strtodg`.
- Packs zero, denormal, normal, infinity, NaN, and NaN payload results.
- Sets sign in the exponent word.
- Uses generated `ldus_QNAN*` constants for plain NaN.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses optional `gdtoa_fltrnds.h` and `strtodg`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopxL.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopxL.c

Purpose: Parses a string into 80-bit extended storage represented by three `ULong`s.

Core behavior:
- Defines endian-specific three-word layout.
- Uses `FPI {64, ...}` and `strtodg`.
- Packs zero, normal, denormal, infinity, NaN, and NaN payload values.
- Sets sign in the high exponent word.
- Uses generated `ld_QNAN*` constants for plain NaN.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses optional `gdtoa_fltrnds.h` and `strtodg`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopxL.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorQ.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorQ.c

Purpose: Parses with an explicit rounding mode into quad-precision storage.

Core behavior:
- `ULtoQ()` packs `strtodg` bits and result class into quad storage.
- `strtorQ()` copies the default quad `FPI` and overrides `rounding` when requested.
- Handles zero, denormal, normal, infinity, NaN, NaN payload, and sign.
- Returns the `STRTOG_*` parse flags.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg`, generated `ld_QNAN*` constants, and endian word macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorQ.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtord.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtord.c

Purpose: Parses with an explicit rounding mode into double storage.

Core behavior:
- `ULtod()` packs `strtodg` bits and result class into IEEE double words.
- `strtord()` uses double `FPI` and overrides `rounding` when requested.
- Handles zero, denormal, normal, infinity, NaN, NaN payload, and sign.
- Locale is passed through to `strtodg`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg`, generated double NaN constants, and endian word macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtord.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtordd.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtordd.c

Purpose: Parses with an explicit rounding mode into double-double storage.

Core behavior:
- `ULtodd()` packs a 106-bit significand into two double words.
- Handles normal splitting, denormal subcases, infinity, NaN, NaN payload, and sign.
- `strtordd()` chooses a 106-bit `FPI`, optionally overrides rounding, calls `strtodg`, then packs via `ULtodd`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg`, `hi0bits`, generated double NaN constants, and endian word macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtordd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorf.c

Purpose: Parses with an explicit rounding mode into float storage.

Core behavior:
- `ULtof()` packs `strtodg` bits and result class into an IEEE float word.
- `strtorf()` uses float `FPI`, optionally overrides rounding, calls `strtodg`, then packs.
- Handles zero, denormal, normal, infinity, NaN, NaN payload, and sign.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg` and generated `f_QNAN`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorx.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorx.c

Purpose: Parses with an explicit rounding mode into five-`UShort` 80-bit extended storage.

Core behavior:
- Defines endian-specific five-word layout.
- `ULtox()` packs result bits into exponent/integer/significand words.
- `strtorx()` uses `FPI {64, ...}`, optionally overrides rounding, calls `strtodg`, then packs.
- Handles zero, denormal, normal, infinity, NaN, NaN payload, and sign.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg` and generated `ldus_QNAN*` constants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorxL.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorxL.c

Purpose: Parses with an explicit rounding mode into three-`ULong` 80-bit extended storage.

Core behavior:
- Defines endian-specific three-word layout.
- `ULtoxL()` packs result bits into exponent/significand words.
- `strtorxL()` uses `FPI {64, ...}`, optionally overrides rounding, calls `strtodg`, then packs.
- Handles zero, normal, denormal, infinity, NaN, NaN payload, and sign.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg` and generated `ld_QNAN*` constants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorxL.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/sum.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/sum.c

Purpose: Adds two `Bigint` values.

Core behavior:
- Swaps operands so the longer `Bigint` drives output sizing.
- Allocates a result with the larger operand's capacity.
- Adds shared limbs with carry, then remaining high limbs.
- Supports both packed-32 and packed-16 limb modes.
- Grows the result if a final carry exceeds current capacity.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bcopy`, `Bfree`, `Storeinc`, and packing macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/sum.c -->