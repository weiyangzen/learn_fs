# Group Research: group_1222_netbsd_src_sources_os_bsd_netbsd_src_lib_libm_noieee_src_n_log_c_so_8c22f1ca7528

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log.c

Implements no-IEEE natural logarithm entry points for `log`, `logf`, and long-double aliases using Peter Tang's table-driven logarithm algorithm.

Key behavior:
- Handles zero, negative, infinity, and NaN differently for IEEE versus VAX/Tahoe paths.
- Reduces `x` into `2^m * F * (1 + f/F)`, with `F` chosen from a 129-entry table.
- Uses split `logF_head`/`logF_tail` tables and polynomial correction terms `A1` through `A4`.
- Provides `__log__D(double)` returning a `struct Double` split result for extended-precision consumers such as `pow`.
- `logf` delegates to double `log`.

Notable risks:
- The IEEE truncation macro type-puns through `int *` and is endian-sensitive.
- The file exposes both public aliases and internal helper behavior, so changes can affect `pow`/gamma-style split-precision code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log10.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log10.c

Implements no-IEEE `log10`, `log10f`, and long-double aliases.

Key behavior:
- Uses `log(x)` as the kernel.
- On VAX/Tahoe, divides by a high-precision `ln10hi`.
- On IEEE-style targets, multiplies by `ivln10`.
- `log10f` delegates through `logf` on VAX/Tahoe and through double `log` otherwise.

Special cases are inherited from `log`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log1p.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log1p.c

Implements no-IEEE `log1p`, `log1pf`, and long-double aliases using K.C. Ng's argument-reduction algorithm.

Key behavior:
- Reduces `1+x` into `2^k * (1+f)` and computes a correction term for lost low bits.
- Uses `s = f/(2+f)` and the shared `__log__L(s*s)` kernel.
- Splits `k*ln2` into `ln2hi` and `ln2lo` for accuracy.
- Handles `x == -1`, `x < -1`, NaN, and infinities with IEEE or VAX/Tahoe-specific signaling behavior.
- `log1pf` delegates to double `log1p`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log1p.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log2.c

Implements no-IEEE `log2`, `log2f`, and long-double aliases.

Key behavior:
- Computes base-2 logarithm by dividing natural log by a static `ln2`.
- `log2` calls `log(x)`.
- `log2f` calls `logf(x)`.
- Special cases are inherited from the underlying natural logarithm routines.

The header comment incorrectly says “base 10 logarithm,” but the code implements base 2.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log__L.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log__L.c

Provides the no-IEEE internal polynomial kernel `__log__L(double z)` used by `log1p`, `log`, and `pow`-related code.

Key behavior:
- Approximates `(log(1+x) - 2s) / s` where `z = s*s` and `s = x/(2+x)`.
- Uses Remez-derived coefficients `L1` through `L8` for VAX/Tahoe and `L1` through `L7` for IEEE-style builds.
- Coefficients are declared through `vc` and `ic` macros from `mathimpl.h`.

This file has no public entry point; it is an internal accuracy helper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log__L.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_lround.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_lround.c

Implements no-IEEE `lround(double)`.

Key behavior:
- Rounds halfway cases away from zero.
- Uses `ceil(x)` for positive values and `ceil(-x)` for negative values.
- Converts the intermediate result to `long`.

Notable risk:
- There is no explicit overflow handling before converting to `long`; behavior follows the platform conversion semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_lround.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_lroundf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_lroundf.c

Implements no-IEEE `lroundf(float)`.

Key behavior:
- Mirrors `n_lround.c` for float inputs.
- Uses `ceilf` on the absolute magnitude and applies the original sign.
- Rounds halfway cases away from zero.

Notable risk:
- Does not guard `long` overflow or NaN/infinity conversion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_lroundf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_pow.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_pow.c

Implements no-IEEE `pow`, `powf`, and long-double aliases using K.C. Ng's algorithm with split-precision `log` and `exp`.

Key behavior:
- Handles special cases for zero exponent, exponent one/two/minus one, NaNs, infinities, signed zero, and negative bases.
- Uses `drem(y, 2)` to classify negative-base exponents as even integer, odd integer, or non-integer.
- Positive-base kernel `pow_P` computes `exp(y*log(x))` using `__log__D` and `__exp__D`.
- Splits `y` into truncated high/low parts before multiplying by the split log result.
- `powf` delegates to double `pow`.

Notable risks:
- Relies on old no-IEEE support routines such as `drem`, `finite`, and `copysign`.
- Uses pointer-based truncation macros on IEEE-style targets.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_pow.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_round.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_round.c

Implements no-IEEE `round(double)` and aliases `roundl` to `round`.

Key behavior:
- Uses `ceil(x)` for positive values and `ceil(-x)` for negative values.
- Adjusts down by one when the distance from the ceiling exceeds `0.5`.
- Rounds halfway cases away from zero.

The implementation is simple and inherits NaN/infinity behavior from `ceil`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_round.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_roundf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_roundf.c

Implements no-IEEE `roundf(float)`.

Key behavior:
- Mirrors `round(double)` with `ceilf`.
- Handles signs by rounding the absolute magnitude then reapplying sign.
- Rounds halfway cases away from zero.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_roundf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_sincos.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_sincos.c

Implements no-IEEE `sin`, `cos`, `sinf`, `cosf`, and long-double aliases.

Key behavior:
- Reduces arguments with `drem` into `[-pi, pi]`.
- Uses quadrant transforms around `pi/4`, `pi/2`, and `3pi/4`.
- Uses polynomial kernels `sin__S` and `cos__C` from `trig.h`.
- Returns NaN for NaN/infinity by `x - x`.
- Float functions delegate to double implementations.

This file owns the exported `__zero`, `__one`, `__half`, `__small`, and related constants by defining `_LIBM_DECLARE` before including `trig.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_sincos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_sincos1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_sincos1.c

Implements convenience wrappers `sincos` and `sincosf`.

Key behavior:
- `sincos(double x, double *s, double *c)` stores `sin(x)` and `cos(x)`.
- `sincosf(float x, float *s, float *c)` stores `sinf(x)` and `cosf(x)`.
- When long double is unavailable, `sincosl` aliases to `sincos`.

There is no shared argument reduction; this file intentionally delegates to existing sine/cosine functions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_sincos1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_sinh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_sinh.c

Implements no-IEEE `sinh`, `sinhf`, and aliases.

Key behavior:
- Reduces to positive magnitude and restores the original sign.
- For ordinary magnitudes, computes `(expm1(x) + expm1(x)/(1+expm1(x))) / 2`.
- Near overflow, subtracts a split `ln(2^(max+1))` and scales to avoid unnecessary overflow.
- For huge finite values, overflows through `expm1(x)*sign`.
- `sinhf` delegates to double `sinh`.

Special constants differ for VAX/Tahoe and IEEE-style targets.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_sinh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_support.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_support.c

Provides old no-IEEE support routines for elementary functions: `scalb`, `copysign`, `logb`, `finite`, `drem`, and `sqrt`.

Key behavior:
- Manipulates floating-point sign/exponent words directly, with separate VAX/Tahoe, IEEE, and `national` word-order paths.
- `scalb` scales by powers of two and handles subnormal normalization, overflow, and underflow.
- `copysign` transfers the sign bit.
- `logb` returns unbiased exponent and special values for zero, infinity, and NaN.
- `finite` tests exponent fields.
- `drem` implements IEEE remainder by recursive scaling and subtractive reduction.
- `sqrt` implements a bit-by-bit square-root algorithm with final rounding decisions.
- Contains disabled alternative `drem` and `sqrt` implementations that require machine-dependent floating-point status hooks.

Notable risks:
- The active code depends on strict object representation assumptions and pointer casts to integer word types.
- Comments warn these routines are slow and intended as temporary C fallbacks where machine-specific assembly is unavailable.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_support.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_tan.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_tan.c

Implements no-IEEE `tan(double)`.

Key behavior:
- Rejects NaN/infinity by returning `x - x`.
- Reduces argument with `drem(x, PI)` into `[-pi/2, pi/2]`.
- Uses symmetry around `pi/4` to switch between `sin/cos` and `cos/sin`.
- Uses `sin__S` and `cos__C` polynomial macros from `trig.h`.
- Has a `national` special case for no-infinity hardware.

No `tanf` wrapper is defined in this file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_tan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_tanh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_tanh.c

Implements no-IEEE `tanh` and `tanhf`.

Key behavior:
- Uses sign/magnitude reduction.
- For tiny values, returns `x` while trying to raise inexact for nonzero inputs.
- For `0 < |x| <= 1`, uses `-expm1(-2x) / (2 - (-expm1(-2x)))`.
- For `1 < |x| <= 22`, uses `1 - 2/(expm1(2x)+2)`.
- For large finite values, returns signed one with an inexact trigger.
- For infinities, returns signed one.
- `tanhf` delegates to double `tanh`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_tanh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/trig.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/trig.h

Defines no-IEEE trigonometric constants, exported common constants, and polynomial kernels for `sin`, `cos`, and `tan`.

Key contents:
- Pi-related constants `PIo4`, `PIo2`, `PI3o4`, `PI`, and `PI2`, plus `thresh`.
- Shared constants `__zero`, `__one`, `__negone`, `__half`, `__small`, and `__big`.
- `sin__S(z)` macro approximates `(sin(x)-x)/x` on the primary interval.
- `cos__C(z)` macro approximates `cos(x)-1+x*x/2`.
- Uses different coefficient counts for VAX/Tahoe versus IEEE-style targets.
- Uses `vc`, `ic`, and optional `vccast` macros supplied by `mathimpl.h`.

This header is not just declarations; including it with `_LIBM_DECLARE` emits storage for shared constants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/noieee_src/trig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/feclearexcept.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/feclearexcept.c

Implements `feclearexcept` for the softfloat fenv layer.

Key behavior:
- Converts C fenv exception bits with `__FPE`.
- Clears those bits from the softfloat sticky flags using `fpgetsticky()` and `fpsetsticky()`.
- Always returns 0.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/feclearexcept.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fedisableexcept.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fedisableexcept.c

Implements `fedisableexcept`.

Key behavior:
- Reads the current exception enable mask with `fpgetmask()`.
- Clears requested exception-enable bits after translating with `__FPE`.
- Returns the previous enabled exception set translated back with `__FEE`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fedisableexcept.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/feenableexcept.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/feenableexcept.c

Implements `feenableexcept`.

Key behavior:
- Reads current softfloat exception mask.
- Enables requested exceptions via `fpsetmask(omask | __FPE(excepts))`.
- Returns previous enabled exceptions using `__FEE`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/feenableexcept.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetenv.c

Implements `fegetenv`.

Key behavior:
- Stores sticky exception flags, exception mask, and rounding mode into `fenv_t`.
- Uses `__FENV_SET_FLAGS`, `__FENV_SET_MASK`, and `__FENV_SET_ROUND`.
- Always returns 0.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetexcept.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetexcept.c

Implements `fegetexcept`.

Key behavior:
- Returns the currently enabled floating-point exception mask.
- Translates from softfloat mask bits to fenv bits with `__FEE(fpgetmask())`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetexcept.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetexceptflag.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetexceptflag.c

Implements `fegetexceptflag`.

Key behavior:
- Reads softfloat sticky flags.
- Converts them to fenv exception bits with `__FEE`.
- Masks with the caller-requested `excepts` and stores into `*flagp`.
- Always returns 0.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetexceptflag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetround.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetround.c

Implements `fegetround`.

Key behavior:
- Reads current softfloat rounding mode using `fpgetround()`.
- Converts it to fenv rounding constants with `__FER`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetround.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/feholdexcept.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/feholdexcept.c

Implements `feholdexcept`.

Key behavior:
- Saves sticky flags, exception mask, and rounding mode to `fenv_t`.
- Clears sticky flags.
- Disables all exception traps by setting mask to zero.
- Always returns 0.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/feholdexcept.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/feraiseexcept.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/feraiseexcept.c

Implements `feraiseexcept`.

Key behavior:
- Sets requested sticky exception bits.
- Intersects requested exceptions with the enabled exception mask.
- If any enabled exception remains, builds a `siginfo_t` for `SIGFPE`.
- Chooses one `si_code` in priority order: underflow, overflow, divide-by-zero, invalid, inexact.
- Delivers the signal to the current process with `sigqueueinfo`.
- Always returns 0.

Notable detail:
- Includes `<stdio.h>` although the file does not use it.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/feraiseexcept.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fesetenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fesetenv.c

Implements `fesetenv`.

Key behavior:
- Restores sticky flags, exception mask, and rounding mode from `fenv_t`.
- Uses `fpsetsticky`, `fpsetmask`, and `fpsetround`.
- Always returns 0.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fesetenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fesetexceptflag.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fesetexceptflag.c

Implements `fesetexceptflag`.

Key behavior:
- Converts requested exception set to softfloat mask bits.
- Replaces only those sticky bits with the translated contents of `*flagp`.
- Preserves unrelated sticky flags.
- Always returns 0.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fesetexceptflag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fesetround.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fesetround.c

Implements `fesetround`.

Key behavior:
- Converts the fenv rounding mode with `__FPR`.
- Sets the softfloat rounding mode through `fpsetround`.
- Always returns 0.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fesetround.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fetestexcept.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fetestexcept.c

Implements `fetestexcept`.

Key behavior:
- Reads softfloat sticky exception flags with `fpgetsticky()`.
- Converts to fenv exception bits with `__FEE`.
- Returns only requested bits.
- Includes softfloat headers, including optional `softfloat-for-gcc.h`, but the function itself only uses `ieeefp.h` state access.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/fetestexcept.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/feupdateenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/feupdateenv.c

Implements `feupdateenv`.

Key behavior:
- Saves current exception flags.
- Restores rounding mode and exception mask from the supplied environment.
- Raises the previously saved exception flags with `feraiseexcept`.

Notable risk:
- The code sets sticky flags from `__FENV_GET_MASK(envp)` rather than `__FENV_GET_FLAGS(envp)`, which is surprising for an environment restore path and may be intentional only if the fenv layout macros encode differently.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/softfloat/feupdateenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/b_exp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/b_exp.c

Provides BSD helper `__exp__D(double x, double c)`, computing `exp(x+c)` for split inputs.

Key behavior:
- Handles NaN, underflow, overflow, and infinities.
- Reduces `x` by `k*ln2` using split `ln2hi`/`ln2lo`.
- Uses a degree-5 polynomial correction for `exp(r)`.
- Scales the final result with `scalb`.
- Intended for callers that maintain extra precision in high/low parts, such as old `pow` and gamma code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/b_exp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/b_log.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/b_log.c

Provides BSD helper `__log__D(double x)` returning a split natural logarithm.

Key behavior:
- Uses the same 129-entry table-driven algorithm as the no-IEEE `n_log.c` helper.
- Reduces input to `2^m * F * (1+f/F)`.
- Uses split table values and polynomial correction terms.
- Returns `struct Double { a, b }`, where `a` is truncated and `a+b` gives extra precision.
- Handles subnormal exponent adjustment through `logb`/`ldexp`.

This is a kernel helper, not a public `log` implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/b_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/b_tgamma.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/b_tgamma.c

Implements BSD `tgamma(double)`.

Key behavior:
- For large positive `x`, computes a Stirling-style approximation in split precision and feeds it to `__exp__D`.
- For moderate positive `x`, reduces to a rational approximation near the gamma minimum.
- For small positive `x`, uses argument reduction around zero.
- For negative non-integers, applies the reflection formula using `sin`/`cos`, `large_gam`, and recursive `tgamma`.
- Handles negative integers, zero, infinities, overflow, and underflow.

Important helpers:
- `large_gam`
- `small_gam`
- `smaller_gam`
- `ratfun_gam`
- `neg_gam`
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/b_tgamma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/b_tgammal.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/b_tgammal.c

Implements or dispatches `tgammal`.

Key behavior:
- If `__HAVE_LONG_DOUBLE` is defined, includes the long-double implementation matching `LDBL_MANT_DIG == 64` or `113`.
- Rejects unsupported long-double formats at compile time.
- If long double support is unavailable, implements `tgammal` by delegating to double `tgamma`.
- Exports weak alias `tgammal` to `_tgammal`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/b_tgammal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_acos.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_acos.c

Implements fdlibm kernel `__ieee754_acos(double)`.

Key behavior:
- Handles `|x| == 1`, `|x| > 1`, and NaN through bit inspection.
- For `|x| < 0.5`, computes `pi/2 - asin(x)` using a rational approximation.
- For `x < -0.5`, transforms to `pi - 2*asin(sqrt((1-|x|)/2))`.
- For `x > 0.5`, computes `2*asin(sqrt((1-x)/2))` with a split square-root correction.
- Uses `__ieee754_sqrt`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_acos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_acosf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_acosf.c

Implements fdlibm kernel `__ieee754_acosf(float)`.

Key behavior:
- Float conversion of `e_acos.c`.
- Uses float constants and bit macros.
- Splits into `|x| < 0.5`, `x < -0.5`, and `x > 0.5` cases.
- Uses `__ieee754_sqrtf` and truncates part of `sqrt` for correction in the `x > 0.5` case.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_acosf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_acosh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_acosh.c

Implements fdlibm kernel `__ieee754_acosh(double)`.

Key behavior:
- Returns NaN for `x < 1`.
- Returns zero for `x == 1`.
- For huge `x`, returns `log(x) + ln2`.
- For `x > 2`, uses `log(2x - 1/(x + sqrt(x*x-1)))`.
- For `1 < x < 2`, uses `log1p(t + sqrt(2t+t*t))` with `t = x - 1`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_acosh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_acoshf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_acoshf.c

Implements fdlibm kernel `__ieee754_acoshf(float)`.

Key behavior:
- Float version of `e_acosh.c`.
- Handles `x < 1`, `x == 1`, huge finite values, infinities, and NaNs.
- Uses `__ieee754_logf`, `__ieee754_sqrtf`, and `log1pf` depending on range.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_acoshf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_acoshl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_acoshl.c

Implements long-double `acoshl` when long double support is available, otherwise delegates to double `acosh`.

Key behavior:
- Uses long-double exponent/sign inspection.
- Supports 64-bit and 113-bit long-double mantissas.
- Uses `logl`, `sqrtl`, and `log1pl` range formulas matching `acosh`.
- Defines `EXP_LARGE` thresholds by long-double format.
- Returns through `ENTERI`/`RETURNI` macros for floating-point environment handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_acoshl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_acosl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_acosl.c

Implements long-double `acosl`.

Key behavior:
- Active only under `__HAVE_LONG_DOUBLE`.
- Pulls rational approximation coefficients from `../ld80/invtrig.h` or `../ld128/invtrig.h`.
- Handles `|x| >= 1`, tiny inputs, negative and positive large halves.
- Uses `sqrtl` and long-double significand truncation for the correction term.
- Has an i386 workaround for long-double pi constants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_acosl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_asin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_asin.c

Implements fdlibm kernel `__ieee754_asin(double)`.

Key behavior:
- Handles `|x| >= 1`, returning signed `pi/2` for exactly `|x| == 1` and NaN outside domain.
- For `|x| < 0.5`, uses a rational approximation to `(asin(x)-x)/x^3`.
- For larger magnitudes, transforms through `sqrt((1-|x|)/2)`.
- Uses separate near-one and middle-range formulas to reduce cancellation.
- Restores sign at the end.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_asin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_asinf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_asinf.c

Implements fdlibm kernel `__ieee754_asinf(float)`.

Key behavior:
- Float version of `e_asin.c`.
- Uses float constants and bit macros.
- Returns `x` for tiny inputs while triggering inexact for nonzero values.
- Uses `__ieee754_sqrtf` for the transformed large-magnitude cases.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_asinf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_asinl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_asinl.c

Implements long-double `asinl`.

Key behavior:
- Active only with `__HAVE_LONG_DOUBLE`.
- Uses format-specific inverse-trig coefficient headers.
- Handles domain, tiny-linear range, `|x| < 0.5`, and `|x| >= 0.5` transformations.
- Uses `sqrtl` and truncates the low significand part for correction.
- Restores sign using the long-double exponent/sign word.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_asinl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_atan2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_atan2.c

Implements fdlibm kernel `__ieee754_atan2(double y, double x)`.

Key behavior:
- Handles NaNs, signed zeros, zero `x`, infinities, and all quadrant cases.
- Fast-paths `x == 1.0` to `atan(y)`.
- Builds quadrant index from the signs of `x` and `y`.
- Avoids unsafe division when `|y/x|` is extremely large or small.
- Uses `atan(fabs(y/x))` for the core angle.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_atan2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_atan2f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_atan2f.c

Implements fdlibm kernel `__ieee754_atan2f(float y, float x)`.

Key behavior:
- Float version of `e_atan2.c`.
- Handles NaNs, signed zeros, infinities, and quadrants by bit inspection.
- Uses `atanf(fabsf(y/x))` when division is safe.
- Uses small `tiny` additions/subtractions to trigger inexact in boundary cases.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_atan2f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_atan2l.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_atan2l.c

Implements long-double `atan2l`.

Key behavior:
- With long double support, inspects exponent/sign and significand fields directly.
- Handles NaNs via `nan_mix`, signed zeros, zero `x`, infinities, and quadrants.
- Uses format-specific `invtrig.h` constants for `pio2_hi`, `pio2_lo`, and `pi_lo`.
- Avoids unsafe division based on exponent difference and `LDBL_MANT_DIG`.
- Falls back to double `atan2` when long double support is absent.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_atan2l.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_atanh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_atanh.c

Implements fdlibm kernel `__ieee754_atanh(double)`.

Key behavior:
- Returns NaN for `|x| > 1`.
- Returns signed infinity for `|x| == 1`.
- Returns `x` for tiny inputs while triggering inexact for nonzero values.
- Uses `0.5*log1p(2x + 2x*x/(1-x))` for `|x| < 0.5`.
- Uses `0.5*log1p(2x/(1-x))` for larger in-domain inputs.
- Restores the original sign.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_atanh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_atanhf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_atanhf.c

Implements fdlibm kernel `__ieee754_atanhf(float)`.

Key behavior:
- Float version of `e_atanh.c`.
- Handles out-of-domain, exact `|x| == 1`, tiny, small, and large in-domain cases.
- Uses `log1pf` formulas and restores sign.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_atanhf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_atanhl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_atanhl.c

Implements long-double `atanhl` when available, otherwise delegates to double `atanh`.

Key behavior:
- Checks long-double exponent/sign for domain and NaN-like cases.
- Uses format-specific tiny thresholds for 64-bit and 113-bit mantissas.
- Applies the same `log1pl` formulas as double `atanh`.
- Restores sign using the high sign bit.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_atanhl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_cosh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_cosh.c

Implements fdlibm kernel `__ieee754_cosh(double)`.

Key behavior:
- Uses `|x|` because cosh is even.
- For small `|x|`, uses `expm1` to compute `1 + expm1(x)^2/(2*exp(x))`.
- For medium `|x|`, computes `(exp(x) + 1/exp(x))/2`.
- For larger safe values, returns `exp(|x|)/2`.
- Near overflow threshold, computes `exp(x/2)/2 * exp(x/2)`.
- Overflows through `huge*huge` past the threshold.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_cosh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_coshf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_coshf.c

Implements fdlibm kernel `__ieee754_coshf(float)`.

Key behavior:
- Float version of `e_cosh.c`.
- Handles NaN/infinity, tiny, medium, large, near-overflow, and overflow ranges.
- Uses `expm1f` and `__ieee754_expf`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_coshf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_coshl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_coshl.c

Contains a long-double `coshl` implementation guarded by `__HAVE_LONG_DOUBLE`, plus a fallback.

Key behavior:
- If `__HAVE_LONG_DOUBLE` is not defined, `coshl` delegates to double `cosh`.
- Under `__HAVE_LONG_DOUBLE`, the file currently contains `#error SHOULD STOP HERE!!!` before the implementation, intentionally preventing that path from compiling.
- The disabled path includes long-double polynomial handling for `|x| < 1`, `k_hexpl`/`hexpl` for larger ranges, and overflow threshold handling.

Notable risk:
- Enabling `__HAVE_LONG_DOUBLE` for this file without addressing the explicit compile-time stop will break the build.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_coshl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_exp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_exp.c

Implements fdlibm kernel `__ieee754_exp(double)`.

Key behavior:
- Handles NaN, positive/negative infinity, overflow, and underflow thresholds.
- Reduces input to `k*ln2 + r`, with split high/low `ln2` constants.
- Uses a degree-5 polynomial approximation for the primary interval.
- Reconstructs by directly adjusting the exponent of the computed significand.
- Handles subnormal scaling through a `2^-1000` multiplier.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_exp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_expf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_expf.c

Implements fdlibm kernel `__ieee754_expf(float)`.

Key behavior:
- Float version of `e_exp.c`.
- Uses float thresholds and split `ln2` constants.
- Adjusts float exponent bits directly for scaling.
- Handles subnormal scaling through a `2^-100` multiplier.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_expf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_fmod.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_fmod.c

Implements fdlibm kernel `__ieee754_fmod(double, double)`.

Key behavior:
- Returns NaN for zero divisor, non-finite dividend, or NaN divisor.
- Returns `x` when `|x| < |y|` and signed zero when `|x| == |y|`.
- Computes exponents for normal and subnormal operands.
- Normalizes significands and performs exact fixed-point shift/subtract reduction.
- Converts the remainder back to floating point and restores the dividend sign.
- Aliases `__ieee754_fmodl` to this function when long double is unavailable.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_fmod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_fmodf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_fmodf.c

Implements fdlibm kernel `__ieee754_fmodf(float, float)`.

Key behavior:
- Float version of exact shift/subtract `fmod`.
- Handles zero divisor, non-finite dividend, NaN divisor, `|x| < |y|`, and equality.
- Normalizes subnormal values, reduces significands, then restores sign and exponent.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_fmodf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_fmodl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_fmodl.c

Implements long-double kernel `__ieee754_fmodl`.

Key behavior:
- Active under `__HAVE_LONG_DOUBLE`.
- Works directly with `union ieee_ext_u` exponent/significand fields.
- Handles explicit versus implicit integer-bit long-double formats.
- Normalizes subnormal operands by temporary scaling.
- Performs exact fixed-point shift/subtract reduction over high and low significand parts.
- Reconstructs the long-double result and restores dividend sign.

Assumptions are documented: low significand fits in `manl_t`, and high significand fits in signed 64-bit storage with carry room.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_fmodl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_hypot.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_hypot.c

Implements fdlibm kernel `__ieee754_hypot(double, double)`.

Key behavior:
- Orders inputs by magnitude and works with absolute values.
- Returns early when the ratio is so large that the smaller input cannot affect the result.
- Handles infinities and NaNs carefully, including signaling NaN quieting.
- Scales very large and very small inputs to avoid overflow/underflow.
- Uses compensated split products before `sqrt` to keep error below 1 ulp.
- Scales the result back if needed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_hypot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_hypotf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_hypotf.c

Implements fdlibm kernel `__ieee754_hypotf(float, float)`.

Key behavior:
- Float version of `e_hypot.c`.
- Sorts magnitudes, handles extreme ratios, infinities, NaNs, and zero/subnormal inputs.
- Scales by powers of two to avoid overflow/underflow.
- Uses truncated high parts for compensated square summation before `sqrtf`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_hypotf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_hypotl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_hypotl.c

Implements long-double `hypotl` when available, otherwise delegates to double `hypot`.

Key behavior:
- Uses long-double exponent/sign word macros and significand access.
- Sorts magnitudes and returns early for huge ratios.
- Handles infinities and NaNs while trying to quiet signaling NaNs.
- Scales very large and tiny inputs using long-double exponent manipulation.
- Uses compensated products with low significand parts cleared before `sqrtl`.
- Restores scale via exponent adjustment.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_hypotl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_j0.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_j0.c

Implements fdlibm kernels `__ieee754_j0(double)` and `__ieee754_y0(double)` for Bessel functions of order zero.

Key behavior:
- `j0` is even; small inputs use polynomial/rational approximation near 1.
- For `|x| >= 2`, computes asymptotic forms using `sin`, `cos`, `sqrt`, and helper rational functions `pzero`/`qzero`.
- Uses cancellation-avoidance identities based on `cos(2x)`.
- `y0` handles zero as `-inf`, negative inputs as NaN, infinities as zero, and small positive inputs with `log(x)`.
- `pzero` and `qzero` select coefficient tables by input range.

This file contains substantial approximation tables for the large-argument asymptotic expansions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_j0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_j0f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_j0f.c

Implements fdlibm kernels `__ieee754_j0f(float)` and `__ieee754_y0f(float)`.

Key behavior:
- Float version of `e_j0.c`.
- Uses float polynomial/rational approximations for small inputs and asymptotic helper functions for `x >= 2`.
- `y0f` handles NaN/infinity, zero, negative input, tiny positive input, and ordinary positive input.
- Helper functions `pzerof` and `qzerof` select range-specific coefficient tables.
- Some extremely-large shortcuts are inside `DEAD_CODE` blocks and are not active.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_j0f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_j1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_j1.c

Implements fdlibm kernels `__ieee754_j1(double)` and `__ieee754_y1(double)` for Bessel functions of order one.

Key behavior:
- `j1` is odd; small inputs return approximately `x/2` with rational correction.
- For `|x| >= 2`, uses asymptotic forms with `sin`, `cos`, `sqrt`, and helper functions `pone`/`qone`.
- Uses cancellation-avoidance identities based on `cos(2x)`.
- `y1` handles zero as `-inf`, negative inputs as NaN, infinities as zero, tiny positives as `-2/(pi*x)`, and ordinary positives with a rational/log expression.
- `pone` and `qone` select range-specific coefficient tables for asymptotic corrections.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_j1.c -->