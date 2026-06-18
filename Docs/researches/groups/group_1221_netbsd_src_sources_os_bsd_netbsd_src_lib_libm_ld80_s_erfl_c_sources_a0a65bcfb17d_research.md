# Group Research: group_1221_netbsd_src_sources_os_bsd_netbsd_src_lib_libm_ld80_s_erfl_c_sources_a0a65bcfb17d

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_erfl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_erfl.c

Implements Intel 80-bit `long double` `erfl()` and `erfcl()`, converted from Sun/FDLIBM-style double code. It uses interval-specific rational approximations for small, medium, and large magnitudes, with coefficients encoded through `LD80C()` unions from `math_private.h`.

Key behavior:
- Handles NaN and infinities directly: `erfl(+-inf)` returns `+-1`, and `erfcl(+-inf)` returns `0` or `2`.
- For `|x| < 0.84375`, evaluates `erf(x)` as `x + x*P(x^2)/Q(x^2)` and uses special tiny-input paths to avoid spurious underflow.
- For `0.84375 <= |x| < 1.25`, approximates around `erx`.
- For larger finite values, approximates `erfc` via asymptotic forms involving `exp(-x*x)` split with a float truncation of `ax`; `erfl()` saturates near `+-1` for `|x| >= 7`.
- `erfcl()` has an additional coefficient interval for `7 <= |x| < 108`, and underflows/rounds to `0` or `2` beyond that.

Important dependencies: `math.h`, `math_private.h`, `fabsl()`, `expl()`, `EXTRACT_LDBL80_WORDS`, `ENTERI`, `RETURNI`, and `LD80C`.

Notable risks:
- Accuracy depends on 80-bit representation and on the `math_private.h` ld80 word macros.
- Uses volatile `tiny` to force status flags and avoid compiler folding; removing it would change floating-point exception behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_erfl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_exp2l.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_exp2l.c

Implements Intel 80-bit `long double` `exp2l()`. The algorithm is table-driven: reduce `x` into an integer exponent `k`, table index `i`, and small residual `z`, then compute `2^k * exp2(i/TBLSIZE) * polynomial(z)`.

Key behavior:
- Uses a 128-entry table, stored as high/low double pairs, for `exp2(i/128)`.
- Uses a degree-6 minimax polynomial for the small residual.
- Handles `+Inf`, `-Inf`, NaNs, overflow, underflow, and very small inputs before entering the main rounding-sensitive path.
- Builds powers of two by setting ld80 exponent/significand fields directly; uses a `+10000` scaling path for subnormal-range results.

Important dependencies: `math_private.h`, ld80 `union ieee_ext_u`, `GET_EXPSIGN`, `GET_LDBL80_MAN`, `SET_EXPSIGN`, `SET_LDBL80_MAN`, `ENTERI`, and `RETURNI`.

Notable risks:
- The range-reduction bit extraction depends on 80-bit layout and assumes signed right shift for negative exponents, as noted in the source.
- The `redux` trick and direct fraction-word access are format-specific and not portable outside the intended ld80 environment.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_exp2l.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_expl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_expl.c

Implements Intel 80-bit `expl()` and `expm1l()`. `expl()` delegates core argument reduction and table/polynomial evaluation to `__k_expl()` from `k_expl.h`; `expm1l()` has its own careful small- and medium-range logic to preserve cancellation-sensitive accuracy.

Key behavior:
- `expl()` filters exceptional inputs, uses `__k_expl(x, &hi, &lo, &k)`, sums the high/low result, and scales by `2^k`.
- Overflow and underflow thresholds are encoded as ld80 constants rounded toward zero.
- `expm1l()` uses a direct Taylor/minimax path for roughly `[-0.1659, 0.1659]`.
- Outside that small interval, `expm1l()` reduces by table intervals from `k_expl.h`, evaluates lower terms, and handles special `k == 0`, `k == -1`, large positive `k`, and negative `k` cases to avoid cancellation.

Important dependencies: `math_private.h`, `k_expl.h`, `fabsl()`, `rnintl()`, `irint()`, `SUM2P`, `ENTERI`, and `RETURNI/RETURNF`.

Notable risks:
- Correctness relies on the shared `k_expl.h` constants, interval count, and polynomial coefficients.
- Several branches are specifically tuned for floating-point exception and rounding behavior; simple algebraic simplification would be unsafe.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_expl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_logl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_logl.c

Implements Intel 80-bit `logl()`, `log1pl()`, `log10l()`, and `log2l()`. The core algorithm decomposes the argument into `X * 2^k`, selects one of 128 centered intervals for `X`, uses tabulated reciprocal/log pieces, and evaluates a minimax polynomial for `log(1+d)`.

Key behavior:
- The main kernel `k_logl()` returns either a single high result or a high/low pair through `struct ld` when structure return is enabled.
- Handles zero, negative values, subnormals, infinities, NaNs, pseudo-infinities, pseudo-NaNs, and unnormals via ld80 word inspection.
- Uses tables `T[]` for reciprocal and split log constants; optionally uses `U[]` to compute reduced `d` with exact correction terms.
- `log1pl()` forms `1+x` as a high/low decomposition, preserving precision for small `x` and rejecting `x <= -1` correctly.
- `log10l()` and `log2l()` reuse `k_logl()` and multiply the high/low natural-log result by split reciprocal constants.

Important dependencies: `math_private.h`, ld80 extraction/insertion macros, `_2sumF`, `_3sumF`, `ENTERI`, `RETURNI`, and optional debug `fenv.h`.

Notable risks:
- The file is heavily tied to Intel 80-bit encoding and to exact cancellation properties in the tables.
- The `STRUCT_RETURN` path is selected through macros and affects how `logl()` shares work with `log10l()` and `log2l()`.
- Comments note difficult rounding-mode and underflow subtleties; table edits would require numerical revalidation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_logl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_nanl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_nanl.c

Implements `nanl(const char *s)` for 80-bit long double. It scans a NaN payload string into raw words, sets the ld80 exponent to all ones, and forces the quiet-NaN bits in the high fraction word.

Key behavior:
- Uses `_scan_nan(u.bits, 3, s)` to parse payload bits.
- Writes the exponent and quiet bit through `union ieee_ext_u`.
- Returns the constructed `long double` NaN.

Important dependencies: `fpmath.h`, `../src/math_private.h`, and `_scan_nan`.

Notable risks:
- Assumes the three-word storage arrangement used by NetBSD/FreeBSD ld80 support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_nanl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_sinpil.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_sinpil.c

Implements `sinpil(long double x)`, computing `sin(pi*x)` directly for Intel 80-bit inputs. It uses quadrant/range reduction in units of integer and fractional parts of `x`, avoiding general multiplication by pi except in tiny-input paths.

Key behavior:
- For `|x| < 0.25`, uses `__kernel_sinpil()` except for tiny values, where it computes a split `pi*x`.
- For other fractions below 1, maps to `__kernel_cospil()` or `__kernel_sinpil()` based on proximity to half/integer points.
- For `1 <= |x| < 2^63`, removes the integer part with `FFLOORL80()`, evaluates the fractional component, and flips sign for odd integer parts.
- For infinities and NaNs, returns NaN; for `|x| >= 2^63`, treats the value as an integer and returns signed zero.

Important dependencies: `math_private.h`, `k_cospil.h`, `k_sinpil.h`, `FFLOORL80`, and ld80 extraction/insertion macros.

Notable risks:
- Sign handling for large integral values depends on recovering parity before integer precision is lost.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_sinpil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_tanpil.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_tanpil.c

Implements `tanpil(long double x)`, computing `tan(pi*x)` directly. It uses a small internal `__kernel_tanpil()` wrapper that maps fractions around quarter/half periods into `__kernel_tanl()` calls with split `pi` constants.

Key behavior:
- Tiny inputs return a split `pi*x` result while preserving signed zero.
- For `|x| < 0.5`, evaluates tangent directly or through the `0.5 - x` identity.
- At half-integers, returns signed infinity via division by volatile zero.
- For `1 <= |x| < 2^63`, strips the integer part, tracks parity for signed zero/infinity, and evaluates the fractional part.
- For infinities/NaNs, returns NaN; for very large integers, returns signed zero based on the remaining representable parity.

Important dependencies: `math_private.h`, `__kernel_tanl`, `FFLOORL80`, `_2sumF`, and ld80 word macros.

Notable risks:
- Correct poles and signed zeros depend on exact half-integer detection.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_tanpil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/mathimpl.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/mathimpl.h

Private support header for the old `noieee_src` libm implementation. It abstracts constant declarations for VAX/Tahoe versus IEEE targets and declares shared helper functions.

Key behavior:
- Defines `vc()` for VAX/Tahoe constants assembled from 16-bit chunks, with endian-specific concatenation.
- Defines `ic()` for IEEE constants as ordinary `double` values.
- Provides `_TINY`, `_TINYER`, and `_HUGE` constants tuned by target.
- Declares shared internal helpers: `__exp__E`, `__exp__D`, `__log__L`, `__log__D`, `infnan`, and `struct Double`.

Important dependencies: `<sys/cdefs.h>`, `<math.h>`, and `<stdint.h>`.

Notable risks:
- Many no-IEEE source files depend on `_LIBM_STATIC` or `_LIBM_DECLARE` being set before inclusion to choose storage class.
- The header exists to keep legacy non-IEEE formats working; constants and casts are intentionally target-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/mathimpl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_acosh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_acosh.c

Implements legacy double `acosh()`. It uses stable `log1p()`-based formulas to avoid overflow and cancellation.

Key behavior:
- Returns NaN unchanged on IEEE targets.
- For very large `x`, computes `log1p(x) + ln2`.
- Otherwise computes `log1p(sqrt(x-1) * (sqrt(x-1) + sqrt(x+1)))`.
- Relies on invalid results from `sqrt(x-1)` for `x < 1`.

Important dependencies: `mathimpl.h`, `sqrt()`, and `log1p()`.

Notable risks:
- Domain signaling is mostly delegated to underlying arithmetic rather than explicit checks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_acosh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_asincos.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_asincos.c

Implements legacy `asin()`, `asinf()`, `acos()`, and `acosf()`. The double functions reduce inverse trig to `atan2()` and `sqrt()` identities; float functions call the double versions and cast.

Key behavior:
- `asin(x)` computes `atan2(x, sqrt(1-x*x))` for `|x| <= 0.5`, and uses `2*(1-|x|) - (1-|x|)^2` near `|x| = 1` for better accuracy.
- `acos(x)` computes `2*atan2(sqrt((1-x)/(1+x)), 1)`, with a special `x == -1` path.
- NaNs are returned unchanged on IEEE targets.
- Weak aliases map public names to internal names.

Important dependencies: `namespace.h`, `mathimpl.h`, `atan2()`, `sqrt()`, and `copysign()`.

Notable risks:
- Modern domain handling is implicit; `|x| > 1` reaches invalid `sqrt()`/division behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_asincos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_asinh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_asinh.c

Implements legacy double `asinh()`. It uses `log1p()` identities with different paths for tiny, normal, and very large magnitudes.

Key behavior:
- Returns NaN unchanged on IEEE targets.
- For tiny `|x|`, returns `x`.
- For moderate values, computes `sign(x) * log1p(t + t/(1/t + sqrt(1+(1/t)^2)))`.
- For very large values, computes `sign(x) * (log1p(|x|) + ln2)`.

Important dependencies: `mathimpl.h`, `copysign()`, `sqrt()`, and `log1p()`.

Notable risks:
- Thresholds are legacy constants tuned for VAX/IEEE double behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_asinh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atan.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atan.c

Implements legacy `atan()` and `atanf()` as wrappers around `atan2(x, 1.0)`.

Key behavior:
- `atan()` calls `atan2(x, one)`.
- `atanf()` calls `atan2(x, one)` and casts to float.
- Weak aliases map `atan` and `atanf` to internal names.

Important dependencies: `namespace.h`, `mathimpl.h`, and `atan2()`.

Notable risks:
- Accuracy and special-case behavior are inherited entirely from `n_atan2.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atan2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atan2.c

Implements legacy double `atan2(y, x)` using K.C. Ng's argument-reduction scheme. It reduces by quadrant and by ratio interval, then evaluates a polynomial for atan on a small interval.

Key behavior:
- Handles NaNs, zero axes, infinities, and signed quadrants explicitly.
- Reduces `t = y/x` into one of several intervals: near `0`, `1/2`, `1`, `3/2`, or infinity.
- Uses split constants for `atan(1/2)`, `atan(3/2)`, `pi/4`, `pi/2`, and `pi`.
- Evaluates an odd polynomial in reduced `t`, with an additional `a12` term on VAX/Tahoe.
- Applies quadrant correction through `PI - z` and `copysign()`.

Important dependencies: `mathimpl.h`, `copysign()`, `finite()`, `logb()`, and `scalb()`.

Notable risks:
- The file intentionally uses machine-rounded `PI`, so results are consistent with the old trig system rather than necessarily modern correctly rounded libm expectations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atan2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atanh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atanh.c

Implements legacy double `atanh()`. It applies the identity `atanh(x) = 0.5 * log1p(2*x/(1-x))` with sign separated through `copysign()`.

Key behavior:
- Copies the sign into the multiplier `z = +/-0.5`.
- Computes with `|x|` in the quotient.
- On VAX/Tahoe, explicitly handles `|x| == 1` through `infnan(ERANGE)`.
- IEEE invalid/infinite cases are mostly delegated to division and `log1p()`.

Important dependencies: `mathimpl.h`, `copysign()`, and `log1p()`.

Notable risks:
- No explicit IEEE NaN/domain checks for `|x| > 1`; behavior follows arithmetic side effects.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atanh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atanhf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atanhf.c

Implements float `atanhf()` using the same identity as `n_atanh.c`, but with `float`, `copysignf()`, and `log1pf()`.

Key behavior:
- Separates sign as `z = +/-0.5f`.
- Computes `x = |x|/(1-|x|)` and returns `z * log1pf(x+x)`.
- Keeps the VAX/Tahoe explicit `|x| == 1` path.

Important dependencies: `mathimpl.h`, `copysignf()`, and `log1pf()`.

Notable risks:
- Domain and NaN behavior are largely inherited from float arithmetic and `log1pf()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atanhf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_cabs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_cabs.c

Implements legacy `hypot()`, `cabs()`, and `z_abs()`. The main `hypot()` avoids overflow/underflow by comparing magnitudes and using Kahan-style formulas.

Key behavior:
- Normalizes `x` and `y` to nonnegative, swaps so `x >= y`, and handles zeros.
- If exponents differ enough, returns `x` while raising inexact.
- Uses different formulas for `x/y > 2` and `1 <= x/y <= 2`.
- Handles infinities and NaNs explicitly.
- `cabs(struct complex)` and `z_abs(struct complex *)` delegate to `hypot()`.

Important dependencies: `mathimpl.h`, `finite()`, `copysign()`, `logb()`, and `sqrt()`.

Notable risks:
- Uses old K&R-style function definitions for complex wrappers.
- A faster alternative `hypot()` is left under `#if 0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_cabs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_cbrt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_cbrt.c

Implements IEEE-only `cbrt()`, plus `cbrtf()` and `cbrtl()` wrappers. It uses Kahan's cube-root approximation with direct word manipulation and one Newton refinement.

Key behavior:
- Returns NaN/Inf and zero unchanged.
- Clears and later restores the sign bit.
- Builds a rough 5-bit cube-root approximation from exponent/mantissa words, with a subnormal path.
- Applies a rational refinement to about 23 bits, chops upward, then performs one Newton step to double precision.
- `cbrtf()` casts `cbrt()`, and `cbrtl()` calls double `cbrt()` when long double is not separately implemented.

Important dependencies: IEEE double layout and optional `national` word-order macro.

Notable risks:
- Violates modern strict-aliasing expectations by viewing doubles as `unsigned long *`.
- Only compiled for non-VAX/Tahoe targets.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_cbrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_cosh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_cosh.c

Implements legacy `cosh()` and `coshf()`. It uses different formulas for small, medium, and overflow-edge inputs.

Key behavior:
- Reduces to `|x|`; returns NaN unchanged on IEEE targets.
- For `x < 0.3465`, computes `1 + (exp(x)-1)^2/(2*exp(x))` using `__exp__E()`.
- For `0.3465 <= x <= 22`, computes `(exp(x) + 1/exp(x))/2`.
- Near overflow threshold, scales `exp((x-mln2hi)-mln2lo)` by `EXPMAX` to avoid unnecessary overflow.
- For large values, returns `exp(x)/2`.
- `coshf()` delegates to double `cosh()`.

Important dependencies: `../src/namespace.h`, `mathimpl.h`, `exp()`, `__exp__E()`, `scalb()`, and `copysign()`.

Notable risks:
- Threshold constants differ for VAX/Tahoe versus IEEE.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_cosh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_erf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_erf.c

Implements legacy double `erf()`, `erfc()`, and float wrappers. The file uses multiple polynomial/rational approximations selected by `|x|`, with McIlroy modifications for accuracy.

Key behavior:
- Handles infinities and NaNs explicitly.
- For `|x| < 0.84375`, uses `x + x*P(x^2)` for `erf()` and stable `1-erf(x)` forms for `erfc()`.
- For `0.84375 <= |x| < 1.25`, uses rational approximation around a single-precision constant `c`.
- For larger values, evaluates asymptotic `erfc` forms over `[1.25,2]`, `[2,4]`, and `[4,28]`.
- Uses `__exp__D()` with split exponent terms to reduce cancellation and overflow risk.
- `erff()` and `erfcf()` cast the double results.

Important dependencies: `mathimpl.h`, `finite()`, `isnan()`, `exp()`, `__exp__D()`, and target-specific `TRUNC`.

Notable risks:
- Uses type-punning `TRUNC()` on IEEE targets.
- Many constants include folded tail terms such as `lsqrtPI_lo`, so coefficient changes are tightly coupled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_erf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp.c

Implements legacy `exp()`, `expf()`, and internal `__exp__D()`. It performs `ln2` argument reduction and evaluates a rational correction for `exp(r)`.

Key behavior:
- Handles NaNs, `-Inf`, overflow, and underflow through threshold checks.
- Reduces `x` to `k*ln2 + r`, where `r` is split into high/low pieces.
- Computes `exp(r)` using a polynomial/rational expression involving coefficients `p1` through `p5`.
- Scales the result by `scalb(..., k)`.
- `__exp__D(x,c)` computes `exp(x+c)` for a correction term `c`, used by other legacy functions.
- `expf()` delegates to double `exp()`.

Important dependencies: `../src/namespace.h`, `mathimpl.h`, `finite()`, `copysign()`, and `scalb()`.

Notable risks:
- Overflow/underflow forcing uses very large `scalb()` exponents and relies on legacy floating-point behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp2.c

Implements double `exp2()` using a FreeBSD-derived accurate table method. It reduces the input into an integer power of two, a table index, and a small residual.

Key behavior:
- Uses `TBLBITS=8`, giving 256 table slots interleaved as `exp2t` and epsilon values.
- Filters large positive/negative inputs for overflow/underflow and tiny inputs for `1+x`.
- Uses the `redux` trick to extract integer and table-index bits from a rounded floating-point value.
- Evaluates a degree-5 polynomial for the residual after subtracting the table epsilon.
- Builds scaling factors by writing exponent bits with `memcpy`.

Important dependencies: `<stdint.h>`, `<float.h>`, `<string.h>`, and `math.h`.

Notable risks:
- Contains pointer casts to volatile double and word-index assumptions in addition to `memcpy`; portability is tied to expected double layout.
- The underflow path uses a volatile small value to preserve status behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp2f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp2f.c

Implements float `exp2f()` using a smaller table-driven method. Computation is mostly performed in double precision after float argument reduction.

Key behavior:
- Uses `TBLBITS=4` and a 16-entry `exp2ft[]` table.
- Handles overflow, underflow, and tiny inputs explicitly.
- Reduces using `redux`, extracts `k` and table index, and evaluates a degree-4 polynomial.
- Builds the `2^k` scaling double by writing exponent bits with `memcpy`.
- Returns the scaled double result as float.

Important dependencies: `<stdint.h>`, `<float.h>`, `<string.h>`, and `math.h`.

Notable risks:
- Reduction depends on IEEE float bit behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp2f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp__E.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp__E.c

Implements internal kernel `__exp__E(x, c)`, returning `exp(x+c) - 1 - x` for small `x` where `c` is a correction term.

Key behavior:
- Uses rational approximations to sinh/cosh-derived expressions.
- For `|x| > 1e-19`, evaluates polynomial terms `P`, `Q`, and correction `W`.
- For tiny nonzero `x`, attempts to raise inexact and returns signed zero.
- Has different `Q` polynomial degree on VAX/Tahoe versus IEEE.

Important dependencies: `mathimpl.h` and `copysign()`.

Notable risks:
- Assumes `c << x` and `fl(x+c) == x`; callers must satisfy this contract.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp__E.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_expm1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_expm1.c

Implements legacy `expm1()` and `expm1f()`. It shares the `ln2` argument reduction model with `exp()` but uses formulas that avoid cancellation near zero.

Key behavior:
- Returns NaNs unchanged on IEEE targets.
- Reduces `x` to `k*ln2 + z + c`.
- For `k == 0`, returns `z + __exp__E(z,c)`.
- For `k == 1`, uses two separate forms depending on `z < -0.25`.
- For larger `k`, handles `1 - 2^-k` carefully based on precision and range.
- Returns `-1` for large negative finite values and overflows for large positive finite values.
- `expm1f()` casts the double result.

Important dependencies: `mathimpl.h`, `__exp__E()`, `scalb()`, `finite()`, and `copysign()`.

Notable risks:
- Several branches are tuned to old `PREC` constants and legacy inexact/overflow behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_expm1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_floor.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_floor.c

Implements legacy `floor`, `ceil`, `rint`, `lrint`, `llrint`, float variants, and `trunc` variants. The core technique adds and subtracts a large power of two to force rounding to an integer.

Key behavior:
- `floor()` and `ceil()` use volatile temporaries to force storage rounding.
- Negative cases delegate to the opposite function with sign negation.
- `rint()` uses `copysign(L, x)` to round according to the current rounding mode.
- Integer-returning `lrint*`/`llrint*` use the same large-add technique and return the converted result.
- `trunc()` chooses `ceil()` for negative and `floor()` for nonnegative values.

Important dependencies: `mathimpl.h`, `copysign()`, and weak aliases for long-double names where long double matches double.

Notable risks:
- The implementation intentionally raises inexact for non-integer inputs.
- Returning `x` from `lrint`/`llrint` on NaN or huge values depends on implicit conversion behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_floor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmax.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmax.c

Implements double `fmax()` as a minimal comparison helper.

Key behavior:
- Returns `x` if `x > y`; otherwise returns `y`.
- Defines a weak alias from `fmaxl` to `fmax` where applicable.

Important dependencies: `<math.h>` and `<sys/cdefs.h>`.

Notable risks:
- This does not implement full modern `fmax` NaN preference semantics; behavior follows the raw comparison expression.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmaxf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmaxf.c

Implements float `fmaxf()` as a minimal comparison helper.

Key behavior:
- Returns `x` if `x > y`; otherwise returns `y`.

Important dependencies: `<math.h>` and `<sys/cdefs.h>`.

Notable risks:
- Like `n_fmax.c`, NaN handling follows ordinary comparison behavior rather than full modern `fmaxf` semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmaxf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmin.c

Implements double `fmin()` as a minimal comparison helper.

Key behavior:
- Returns `x` if `x < y`; otherwise returns `y`.

Important dependencies: `<math.h>` and `<sys/cdefs.h>`.

Notable risks:
- NaN and signed-zero behavior follow the comparison expression, not a fully specified modern implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fminf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fminf.c

Implements float `fminf()` as a minimal comparison helper.

Key behavior:
- Returns `x` if `x < y`; otherwise returns `y`.

Important dependencies: `<math.h>` and `<sys/cdefs.h>`.

Notable risks:
- NaN and signed-zero behavior follow ordinary comparison behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fminf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmod.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmod.c

Implements legacy `fmod()` and `fmodf()`. It computes the floating-point remainder by repeated scaled subtraction based on exponents.

Key behavior:
- Rejects zero divisor, NaN divisor, and nonfinite dividend on IEEE targets by returning invalid NaN expression.
- Works with absolute values of `x` and `y`, preserving the original sign of `x` at return.
- Uses `frexp()` to compare exponents and `ldexp()` to align the divisor before subtracting.
- Loops until the remainder magnitude is below the divisor.
- `fmodf()` delegates to double `fmod()`.

Important dependencies: `mathimpl.h`, `fabs()`, `frexp()`, `ldexp()`, `isnan()`, and `finite()`.

Notable risks:
- The repeated subtraction loop can be slow for hostile exponent/mantissa combinations.
- Test harness code remains under `TEST_FMOD`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_frexpf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_frexpf.c

Implements `frexpf()` by delegating to double `frexp()` and casting the result back to float.

Key behavior:
- Assumes every `float` value is representable as `double`.
- Relies on the normalized `frexp()` result being representable as float.
- Cannot be a simple symbol alias because the float ABI differs from the double ABI.

Important dependencies: `namespace.h` and `<math.h>`.

Notable risks:
- The implementation is intentionally simple and ABI-driven; it assumes no float-only edge cases beyond double coverage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_frexpf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_frexpl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_frexpl.c

Implements `frexpl()` for machines where `long double` is the same format as `double`.

Key behavior:
- Compile-time errors if `__HAVE_LONG_DOUBLE` is defined.
- Delegates to `frexp(x, e)`.
- Exists because `frexp` is in libc while `frexpl` is in libm, so ELF symbol aliases cannot cross libraries.

Important dependencies: `namespace.h` and `<math.h>`.

Notable risks:
- Only valid on platforms without a distinct long-double format.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_frexpl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_gamma.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_gamma.c

Implements legacy `gamma()` returning the gamma function, not log-gamma. It combines rational approximation, Stirling expansion, and reflection for negative inputs.

Key behavior:
- For `x >= 6`, computes a split log-gamma approximation via `large_gam()` and exponentiates with `__exp__D()`.
- For moderate positive values, reduces to a rational approximation around the gamma minimum.
- For very small `x`, returns approximately `1/x`, with zero producing infinity.
- For negative nonintegers, uses the reflection formula with sine/cosine of the fractional distance to the nearest integer.
- Negative integers and overflow return infinity or legacy `infnan()` depending on target.

Important dependencies: `mathimpl.h`, `__log__D()`, `__exp__D()`, `floor()`, `ceil()`, `sin()`, `cos()`, and `M_PI`.

Notable risks:
- Uses global/static endian detection and `TRUNC()` word manipulation for extra-precision splitting.
- Calls `gamma()` recursively in reflection paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_gamma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_ilogb.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_ilogb.c

Implements `ilogb()` and `ilogbf()`, plus an `ilogbl` alias when long double is not distinct.

Key behavior:
- Returns `FP_ILOGB0` for zero.
- Returns `FP_ILOGBNAN` for NaN.
- Returns `INT_MAX` for infinities.
- Otherwise casts `logb(x)` to `int`.
- `ilogbf()` delegates to double `ilogb()`.

Important dependencies: `math.h`, `logb()`, `finite()`, and strong aliases.

Notable risks:
- Finite nonzero behavior depends on `logb()` being available and correct for the target format.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_ilogb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_j0.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_j0.c

Implements Bessel functions `j0()` and `y0()` for order zero, adapted from early FDLIBM/SunPro code for non-IEEE support. It uses small-argument rational approximations and large-argument asymptotic expansions.

Key behavior:
- `j0()` is even; it reduces to `|x|`.
- For `|x| < 2`, `j0()` uses `1 - x^2/4 + x^4*R/S`.
- For `|x| >= 2`, it computes asymptotic forms using `sin(x)`, `cos(x)`, cancellation-avoidance identities, and helper approximations `pzero()`/`qzero()`.
- `y0()` rejects zero and negative inputs with infinity/NaN behavior, and for `x < 2` evaluates `U/V + (2/pi)*j0(x)*log(x)`.
- `pzero()` and `qzero()` select coefficient arrays by ranges `[2,2.857]`, `[2.857,4.545]`, `[4.545,8]`, and `[8,inf]`.

Important dependencies: `mathimpl.h`, `sin()`, `cos()`, `sqrt()`, `log()`, `fabs()`, `finite()`, and `<float.h>`.

Notable risks:
- IEEE versus VAX/Tahoe behavior is controlled by `_IEEE` and `infnan`.
- Very large-argument fast paths omit correction helpers to avoid overflow/cost.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_j0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_j1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_j1.c

Implements Bessel functions `j1()` and `y1()` for order one, adapted from FDLIBM/SunPro code. It mirrors the structure of `n_j0.c` with order-one approximations and sign handling.

Key behavior:
- `j1()` is odd; it computes on `|x|` and restores sign.
- For tiny `x`, returns `0.5*x`; for `|x| < 2`, uses `x/2 + x*x^2*R/S`.
- For `|x| >= 2`, uses asymptotic sine/cosine combinations for `x - 3*pi/4` and helper functions `pone()`/`qone()`.
- `y1()` rejects `x <= 0`, handles infinities/NaNs, and for `x < 2` evaluates `x*U/V + (2/pi)*(j1(x)*log(x)-1/x)`.
- `pone()` and `qone()` select coefficient arrays by the same large-argument ranges as `n_j0.c`.

Important dependencies: `mathimpl.h`, `sin()`, `cos()`, `sqrt()`, `log()`, `fabs()`, `copysign()`, and `<float.h>`.

Notable risks:
- Special values vary by `_IEEE` mode.
- The asymptotic combination code is sensitive to cancellation and sign choices.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_j1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_jn.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_jn.c

Implements integer-order Bessel functions `jn(int n, double x)` and `yn(int n, double x)`. It builds on `j0/j1` and `y0/y1`, using recurrence and asymptotic shortcuts.

Key behavior:
- Handles negative `n` using parity identities.
- `jn()` delegates to `j0()`/`j1()` for orders 0 and 1.
- If `n <= x`, `jn()` uses forward recurrence from `j0()` and `j1()`.
- If `n > x`, it uses a continued-fraction estimate and backward recurrence, scaling intermediate values to avoid overflow.
- Tiny `x` uses the first Taylor term `(x/2)^n / n!` with underflow cutoff.
- `yn()` uses forward recurrence for all `n > 1`, starting from `y0()` and `y1()`.
- Very large `x` uses direct asymptotic sine/cosine phase patterns.

Important dependencies: `mathimpl.h`, `j0()`, `j1()`, `y0()`, `y1()`, `sin()`, `cos()`, `sqrt()`, `log()`, `fabs()`, `finite()`, and optional `snan()`.

Notable risks:
- Backward recurrence has scaling heuristics (`BMAX`) and a continued-fraction stopping threshold tuned for double precision.
- The loop in `yn()` appears to continue while `!finite(b)`, matching legacy code but worth treating cautiously in maintenance.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_jn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_lgamma.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_lgamma.c

Implements legacy `lgamma()`, `lgamma_r()`, and long-double aliases where applicable. It computes log-gamma with sign reporting through `signgam` or an explicit pointer.

Key behavior:
- `lgamma()` calls `lgamma_r(x, &signgam)`.
- For large positive `x`, `large_lgam()` applies a Stirling-style expansion using split log results from `__log__D()`.
- For positive `x < 6`, `small_lgam()` reduces via gamma recurrence and chooses between two rational approximations.
- For tiny nonzero `x`, returns `-log(|x|)` and sets negative sign for negative values.
- For negative values, `neg_lgam()` uses either `gamma(x)` for not-too-negative inputs or a reflection formula for large negative values.
- Nonpositive integers return infinity; nonfinite inputs return NaN/Inf per target mode.

Important dependencies: `mathimpl.h`, `gamma()`, `__log__D()`, `log()`, `log1p()`, `sin()`, `cos()`, `floor()`, `ceil()`, and `M_PI`.

Notable risks:
- Shares old global `signgam` state.
- Uses target-specific `TRUNC()` word manipulation and endian detection for precision splitting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_lgamma.c -->