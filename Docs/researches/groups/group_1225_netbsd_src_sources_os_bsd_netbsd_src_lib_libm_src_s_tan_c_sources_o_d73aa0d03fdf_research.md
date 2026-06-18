# Group Research: group_1225_netbsd_src_sources_os_bsd_netbsd_src_lib_libm_src_s_tan_c_sources_o_d73aa0d03fdf

Scope verified against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tan.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tan.c

Implements public `double tan(double x)` with NetBSD weak aliasing to `_tan`.

The function is the fdlibm/SunPro tangent wrapper. It reads the high word of `x`, handles small arguments directly via `__kernel_tan(x, 0, 1)`, returns NaN for Inf/NaN through `x - x`, and otherwise reduces by `__ieee754_rem_pio2` before calling `__kernel_tan(y[0], y[1], odd ? -1 : 1)`.

Key dependencies are `math_private.h` bit macros, `__kernel_tan`, and `__ieee754_rem_pio2`. Precision and quadrant behavior depend on those lower-level routines.

Risk points: argument reduction correctness for large finite values, NaN signaling behavior from `x - x`, and ABI alias consistency.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanf.c

Implements `float tanf(float x)` as the float version of `s_tan.c`, with weak alias `_tanf`.

It uses `GET_FLOAT_WORD`, fast-paths `|x| <= pi/4` to `__kernel_tanf(x, 0, 1)`, returns NaN for Inf/NaN with `x - x`, and otherwise applies `__ieee754_rem_pio2f` before selecting tangent or reciprocal form through the kernel’s sign/control argument.

Dependencies are `__kernel_tanf`, `__ieee754_rem_pio2f`, and float bit encodings from `math_private.h`.

Risk points mirror `s_tan.c`, with float-specific thresholds and large-argument reduction.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanh.c

Implements `double tanh(double x)`.

The function follows fdlibm’s piecewise hyperbolic tangent algorithm: preserve odd symmetry, return +/-1 for infinities and NaN propagation for NaN, approximate tiny inputs with `x * (1 + x)`, use `expm1(-2|x|)` for `|x| < 1`, use `expm1(2|x|)` for `1 <= |x| < 22`, and return `1 - tiny` for larger finite magnitudes to raise inexact.

Dependencies are `GET_HIGH_WORD`, `fabs`, and `expm1`.

Risk points: floating exception behavior is intentional, especially tiny/inexact and saturated large values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanhf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanhf.c

Implements `float tanhf(float x)`.

It is the float analogue of `s_tanh.c`: detects Inf/NaN, returns tiny inputs as `x * (1 + x)`, uses `expm1f` formulas for midrange inputs, and saturates to signed `1 - tiny` for `|x| >= 22`.

Dependencies are `GET_FLOAT_WORD`, `fabsf`, and `expm1f`.

Risk points: threshold constants are float-specific; exception behavior is encoded by arithmetic rather than explicit `feraiseexcept`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanhf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanhl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanhl.c

Implements `long double tanhl(long double x)` when `__HAVE_LONG_DOUBLE` is available, otherwise falls back to `tanh(x)`.

For 80-bit and 128-bit long double formats it selects matching `k_expl.h` support and polynomial coefficients. Tiny inputs return signed zero or a scaled expression that raises inexact. Inputs below `0.25` use a polynomial approximation. Larger inputs below about `40` use `k_hexpl(2|x|)` and either a compensated division helper `divl` or `1 - 1/(lo + 0.5 + hi)`. Very large finite inputs return signed `1 - tiny`.

Dependencies include long-double layout macros, `ENTERI`/`RETURNI`, `_2sumF`, `k_hexpl`, and architecture-specific `ld80`/`ld128` headers.

Risk points: format assumptions are guarded by compile-time errors; correctness is highly dependent on long-double ABI and rounding-mode handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanhl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanl.c

Implements `long double tanl(long double x)` with weak alias `_tanl` when long double support exists; otherwise it falls back to `tan(x)`.

The implementation handles zero/subnormal by returning `x`, Inf/NaN by returning NaN, fast-paths `|x| < pi/4` through `__kernel_tanl`, and otherwise uses `__ieee754_rem_pio2l` followed by quadrant selection in `__kernel_tanl`.

Dependencies are long-double IEEE layout, `e_rem_pio2l.h`, and `k_tanl.c` from the selected `ld80` or `ld128` directory.

Risk points: included C implementation files are architecture-format specific; quadrant handling relies on `e0 & 3`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanpi.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanpi.c

Implements `double tanpi(double x)`, computing `tan(pi*x)` with careful argument handling.

The file defines split `pi_hi`/`pi_lo`, a `__kernel_tanpi` helper, and a piecewise public function. It handles tiny inputs by scaled pi multiplication, `|x| < 1` directly, `1 <= |x| < 2^52` by extracting the integer part with `FFLOOR`, half-integers by division by volatile zero to raise divide-by-zero, huge integral inputs as signed zero, and Inf/NaN as invalid NaN.

Dependencies are `__kernel_tan`, `_2sumF`, `FFLOOR`, bit extraction macros, and `copysign`.

Risk points: signed-zero parity rules and half-integer infinities are part of the API semantics; changes to bit-level thresholds can regress special cases.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanpi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanpif.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanpif.c

Implements `float tanpif(float x)`.

This is the float version of `tanpi`: it includes `k_tandf.c`, defines split float pi constants, uses `__kernel_tandf`, handles tiny inputs with scaled pi multiplication, handles half-integers by division by volatile zero, reduces finite inputs below `2^23` by `FFLOORF`, and returns signed zero for large integral floats.

Dependencies include `INLINE_KERNEL_TANDF`, `k_tandf.c`, float bit macros, and `copysignf`.

Risk points are float parity detection near `2^23`, signed-zero preservation, and intentional floating exceptions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanpif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanpil.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanpil.c

Provides `long double tanpil(long double x)`.

When long double is available, the file includes the format-specific implementation from `../ld80/s_tanpil.c` or `../ld128/s_tanpil.c`. If long double is not available, it falls back to `tanpi(x)`.

Dependencies are `machine/float.h`, `machine/ieee.h`, long-double mantissa detection, and the selected external implementation file.

Risk points: this file is mainly a dispatcher; behavior depends on the included long-double implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tanpil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tgammaf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tgammaf.c

Implements `float tgammaf(float x)`.

The function deliberately delegates to double-precision `tgamma(x)` and casts the result to float, with a comment explaining that a float-optimized gamma is not worth the library size because gamma grows superexponentially and float range is limited.

Dependencies are only `<math.h>` and the double `tgamma` implementation.

Risk points: no float-specific optimization or exception tailoring; behavior follows double `tgamma` then conversion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_tgammaf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_trunc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_trunc.c

Implements `double trunc(double x)` and aliases `truncl` to `trunc` when long double is unavailable.

The algorithm rounds toward zero by bit manipulation. It extracts exponent and mantissa words, masks fractional bits according to exponent range, preserves signed zero for `|x| < 1`, returns infinities/NaNs as `x + x`, and uses `huge + x` to raise inexact for non-integral finite inputs.

Dependencies are `EXTRACT_WORDS` and `INSERT_WORDS`.

Risk points: exact IEEE bit layout assumptions and deliberate exception side effects.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_trunc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_truncf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_truncf.c

Implements `float truncf(float x)`.

It extracts the float word, computes the unbiased exponent, masks fractional bits for non-integral values, returns signed zero for `|x| < 1`, propagates Inf/NaN with `x + x`, and uses `huge + x` to raise inexact.

Dependencies are `GET_FLOAT_WORD` and `SET_FLOAT_WORD`.

Risk points: float exponent thresholds and signed-zero preservation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_truncf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_truncl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_truncl.c

Implements `long double truncl(long double x)` when long double support exists.

It uses `union ieee_ext_u` to inspect long-double exponent, sign, and fraction fields. Depending on exponent position, it masks high or low fraction bits, returns signed zero for `|x| < 1`, returns integral inputs unchanged, and uses `huge + x` to raise inexact before clearing fraction bits.

Dependencies are `<machine/ieee.h>`, `LDBL_IMPLICIT_NBIT`, and extended-precision fraction layout macros.

Risk points: only valid for supported NetBSD extended long-double layouts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_truncl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_acos.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_acos.c

Wraps `double acos(double x)` around `__ieee754_acos`.

Under IEEE libm mode it returns the raw kernel result. Otherwise it maps `|x| > 1` to `__kernel_standard(x, x, 1)` while returning NaN inputs and valid-domain results unchanged. It also provides long-double fallback aliases when long double is unavailable.

Dependencies are `__ieee754_acos`, `__kernel_standard`, `_LIB_VERSION`, and alias macros.

Risk points: compatibility error reporting depends on `_LIB_VERSION`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_acos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_acosf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_acosf.c

Wraps `float acosf(float x)` around `__ieee754_acosf`.

It returns raw IEEE results in IEEE mode or for NaN. For finite out-of-domain `|x| > 1`, it calls `__kernel_standard` with the float-specific error code `101`.

Dependencies are float kernel math and standard error mapping.

Risk points: float cast around `__kernel_standard` and domain detection.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_acosf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_acosh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_acosh.c

Wraps `double acosh(double x)` around `__ieee754_acosh`.

In compatibility modes, finite `x < 1` maps to `__kernel_standard(x, x, 29)`; IEEE mode and NaN return the raw result.

Dependencies are `__ieee754_acosh` and `__kernel_standard`.

Risk points: domain boundary at exactly `1.0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_acosh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_acoshf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_acoshf.c

Wraps `float acoshf(float x)` around `__ieee754_acoshf`.

It mirrors the double wrapper, mapping finite `x < 1` to float error code `129` outside IEEE mode.

Dependencies are float IEEE kernel and standard error handling.

Risk points: domain error behavior depends on `_LIB_VERSION`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_acoshf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_asin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_asin.c

Wraps `double asin(double x)` around `__ieee754_asin`.

Valid-domain and NaN inputs return the kernel result; finite `|x| > 1` in non-IEEE modes maps to `__kernel_standard(x, x, 2)`. It also has no-long-double aliases for `asinl`.

Dependencies are fdlibm kernel asin and standard error mapping.

Risk points: domain compatibility behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_asin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_asinf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_asinf.c

Wraps `float asinf(float x)` around `__ieee754_asinf`.

It returns raw kernel results for IEEE mode or NaN, and maps finite `|x| > 1` to `__kernel_standard(..., 102)`.

Dependencies are float kernel asin and `_LIB_VERSION`.

Risk points: correct float domain conversion into double error API.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_asinf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_atan2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_atan2.c

Wraps `double atan2(double y, double x)` around `__ieee754_atan2`.

In non-IEEE compatibility mode, it treats `(x == 0 && y == 0)` as a standard exception via code `3`; NaN inputs and other cases return the kernel result.

Dependencies are `__ieee754_atan2`, `isnan`, and `__kernel_standard`.

Risk points: signed-zero behavior is delegated to the kernel except for compatibility error reporting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_atan2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_atan2f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_atan2f.c

Wraps `float atan2f(float y, float x)`.

It calls `__ieee754_atan2f`, returning raw results in IEEE mode or for NaNs. In compatibility mode, the `(0,0)` case maps to `__kernel_standard(..., 103)`.

Dependencies are float atan2 kernel and standard error handling.

Risk points: float signed-zero semantics around the special `(0,0)` compatibility case.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_atan2f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_atanh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_atanh.c

Wraps `double atanh(double x)` around `__ieee754_atanh`.

Outside IEEE mode, it distinguishes `|x| > 1` as domain error code `30` and `|x| == 1` as singularity code `31`; NaN and valid-domain inputs return the raw result.

Dependencies are `fabs`, `__ieee754_atanh`, and `__kernel_standard`.

Risk points: exact boundary behavior at `|x| == 1`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_atanh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_atanhf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_atanhf.c

Wraps `float atanhf(float x)`.

It mirrors the double wrapper, using float error codes `130` for `|x| > 1` and `131` for `|x| == 1`.

Dependencies are `fabsf`, `__ieee754_atanhf`, and `__kernel_standard`.

Risk points: boundary classification in float precision.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_atanhf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_cosh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_cosh.c

Wraps `double cosh(double x)` around `__ieee754_cosh`.

Non-IEEE compatibility mode reports overflow with `__kernel_standard(x, x, 5)` when `|x|` exceeds the double overflow threshold. NaN and valid values return the kernel result.

Dependencies are `fabs`, finite checks through kernel behavior, and standard error handling.

Risk points: hard-coded overflow threshold.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_cosh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_coshf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_coshf.c

Wraps `float coshf(float x)` around `__ieee754_coshf`.

It uses a float overflow threshold near `89.415985107` and maps overflow to error code `105` outside IEEE mode.

Dependencies are `fabsf`, `__ieee754_coshf`, and `__kernel_standard`.

Risk points: threshold accuracy and compatibility mode behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_coshf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_drem.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_drem.c

Implements legacy `double drem(double x, double y)`.

The function simply returns `remainder(x, y)`.

Dependencies are the public `remainder` wrapper.

Risk points: any compatibility/error semantics come from `remainder`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_drem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_dremf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_dremf.c

Implements legacy `float dremf(float x, float y)`.

The function simply returns `remainderf(x, y)`.

Dependencies are the public `remainderf` wrapper.

Risk points: no independent behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_dremf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_exp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_exp.c

Wraps `double exp(double x)` around `__ieee754_exp`.

In compatibility modes, finite inputs above `o_threshold` map to overflow error code `6`, and finite inputs below `u_threshold` map to underflow code `7`. IEEE mode returns raw results.

Dependencies are `__ieee754_exp`, `finite`, and `__kernel_standard`.

Risk points: hard-coded overflow/underflow thresholds and exception compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_exp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_expf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_expf.c

Wraps `float expf(float x)` around `__ieee754_expf`.

It applies float overflow/underflow thresholds and maps them to float-specific standard error codes outside IEEE mode.

Dependencies are `__ieee754_expf`, `finitef`, and `__kernel_standard`.

Risk points: float thresholds and casted error returns.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_expf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_fmod.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_fmod.c

Wraps `double fmod(double x, double y)` around `__ieee754_fmod`.

In non-IEEE modes, `y == 0` maps to `__kernel_standard(x, y, 27)` unless `x` is NaN; otherwise it returns the raw kernel result.

Dependencies are `__ieee754_fmod`, `isnan`, and standard error handling.

Risk points: divide-by-zero/domain compatibility case.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_fmod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_fmodf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_fmodf.c

Wraps `float fmodf(float x, float y)` around `__ieee754_fmodf`.

It mirrors `w_fmod.c`, using the float error code for `fmodf(x, 0)` outside IEEE mode.

Dependencies are `__ieee754_fmodf`, `isnanf`, and `__kernel_standard`.

Risk points: zero divisor handling and float conversion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_fmodf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_fmodl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_fmodl.c

Wraps `long double fmodl(long double x, long double y)` when long double is available.

It calls `__ieee754_fmodl`; outside IEEE mode it reports `fmodl(x, 0)` through `__kernel_standard` with the long-double error code while passing NaN cases through.

Dependencies are `__ieee754_fmodl`, `isnan`, and long-double libm configuration.

Risk points: available only under `__HAVE_LONG_DOUBLE`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_fmodl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_gamma.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_gamma.c

Implements legacy `double gamma(double x)` as `__ieee754_lgamma_r(x, &signgam)`.

Compatibility-mode code maps finite inputs that produce non-finite results to either pole code `41` for non-positive integers or overflow code `40`; IEEE mode returns raw lgamma result.

Dependencies are `signgam`, `floor`, `finite`, and `__ieee754_lgamma_r`.

Risk points: legacy `gamma` here behaves like log-gamma, not C99 `tgamma`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_gamma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_gamma_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_gamma_r.c

Implements `double gamma_r(double x, int *signgamp)`.

It delegates to `__ieee754_lgamma_r(x, signgamp)` and has compatibility handling for poles and overflow analogous to `w_gamma.c`.

Dependencies are caller-provided `signgamp`, `floor`, `finite`, and `__kernel_standard`.

Risk points: legacy log-gamma semantics and external sign storage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_gamma_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_gammaf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_gammaf.c

Implements `float gammaf(float x)` as a legacy log-gamma wrapper using `__ieee754_lgammaf_r(x, &signgam)`.

Outside IEEE mode, finite pole/overflow cases map to float standard error codes `141` and `140`.

Dependencies are `signgam`, `floorf`, `finitef`, and float lgamma kernel.

Risk points: legacy naming and float cast of error handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_gammaf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_gammaf_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_gammaf_r.c

Implements `float gammaf_r(float x, int *signgamp)`.

It delegates to `__ieee754_lgammaf_r` and reports non-positive integer poles or overflow outside IEEE mode.

Dependencies are caller sign storage and float lgamma internals.

Risk points: same legacy log-gamma behavior as `gammaf`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_gammaf_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_hypot.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_hypot.c

Wraps `double hypot(double x, double y)` around `__ieee754_hypot`.

In compatibility mode it maps finite-input overflow to `__kernel_standard(x, y, 4)`; IEEE mode returns raw results.

Dependencies are finite checks and hypot kernel.

Risk points: overflow reporting only when both inputs are finite.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_hypot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_hypotf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_hypotf.c

Wraps `float hypotf(float x, float y)` around `__ieee754_hypotf`.

It maps finite-input overflow to float code `104` outside IEEE mode.

Dependencies are `finitef`, `__ieee754_hypotf`, and `__kernel_standard`.

Risk points: float overflow compatibility behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_hypotf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_j0.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_j0.c

Wraps Bessel functions `double j0(double x)` and `double y0(double x)`.

`j0` reports total loss of significance for `|x| > X_TLOSS` outside IEEE mode. `y0` additionally reports `x == 0` and `x < 0` with standard error codes before checking `X_TLOSS`.

Dependencies are `__ieee754_j0`, `__ieee754_y0`, `X_TLOSS`, and `__kernel_standard`.

Risk points: legacy SVID/XOPEN error semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_j0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_j0f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_j0f.c

Wraps float Bessel functions `j0f` and `y0f`.

It mirrors `w_j0.c` with float kernels and float-specific standard error codes for TLOSS and non-positive `y0f` arguments.

Dependencies are `__ieee754_j0f`, `__ieee754_y0f`, and `X_TLOSS`.

Risk points: float TLOSS threshold comparisons.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_j0f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_j1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_j1.c

Wraps Bessel functions `double j1(double x)` and `double y1(double x)`.

`j1` reports TLOSS for large magnitude outside IEEE mode. `y1` reports zero, negative, and TLOSS cases with standard error codes.

Dependencies are `__ieee754_j1`, `__ieee754_y1`, `X_TLOSS`, and compatibility error handling.

Risk points: same domain/TLOSS behavior as other Bessel wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_j1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_j1f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_j1f.c

Wraps float Bessel functions `j1f` and `y1f`.

It uses float IEEE kernels and maps TLOSS plus non-positive `y1f` arguments to float standard error codes.

Dependencies are `__ieee754_j1f`, `__ieee754_y1f`, and `X_TLOSS`.

Risk points: compatibility-only error handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_j1f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_jn.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_jn.c

Wraps integer-order Bessel functions `double jn(int n, double x)` and `double yn(int n, double x)`.

`jn` reports TLOSS for `|x| > X_TLOSS`; `yn` reports zero, negative, and TLOSS cases. Standard error calls pass `n` as the first argument converted to double.

Dependencies are `__ieee754_jn`, `__ieee754_yn`, and `X_TLOSS`.

Risk points: parameter reporting for error handlers and legacy semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_jn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_jnf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_jnf.c

Wraps float integer-order Bessel functions `jnf` and `ynf`.

It mirrors `w_jn.c` with float kernels and float error codes for TLOSS, zero, and negative `ynf` inputs.

Dependencies are `__ieee754_jnf`, `__ieee754_ynf`, and `X_TLOSS`.

Risk points: float conversion around standard error handler.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_jnf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_lgamma.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_lgamma.c

Implements `double lgamma(double x)` using `__ieee754_lgamma_r(x, &signgam)`.

Outside IEEE mode it reports non-positive integer poles with code `15` and overflow with code `14`.

Dependencies are global `signgam`, `floor`, `finite`, and lgamma kernel.

Risk points: global sign state is not thread-local here unless handled elsewhere by namespace/runtime.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_lgamma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_lgamma_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_lgamma_r.c

Implements reentrant `double lgamma_r(double x, int *signgamp)`.

It delegates to `__ieee754_lgamma_r` and applies the same pole/overflow compatibility checks as `lgamma`, writing sign through the supplied pointer.

Dependencies are `__ieee754_lgamma_r`, `floor`, and `finite`.

Risk points: caller must supply a valid sign pointer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_lgamma_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_lgammaf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_lgammaf.c

Implements `float lgammaf(float x)` using `__ieee754_lgammaf_r(x, &signgam)`.

It maps finite pole and overflow cases to float standard error codes `115` and `114` outside IEEE mode.

Dependencies are global `signgam`, `floorf`, `finitef`, and float lgamma kernel.

Risk points: global sign state and float error casting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_lgammaf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_lgammaf_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_lgammaf_r.c

Implements `float lgammaf_r(float x, int *signgamp)`.

It delegates to `__ieee754_lgammaf_r` and maps finite pole/overflow conditions to compatibility errors.

Dependencies are caller sign storage and float lgamma kernel.

Risk points: no validation of `signgamp`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_lgammaf_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_log.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_log.c

Wraps `double log(double x)` around `__ieee754_log`.

Outside IEEE mode, `x == 0` maps to code `16` and `x < 0` maps to code `17`; NaN and positive inputs return raw kernel results. It also aliases `logl` to `log` when long double is unavailable.

Dependencies are log kernel and standard error handler.

Risk points: compatibility behavior for signed zero and negative inputs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_log10.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_log10.c

Wraps `double log10(double x)` around `__ieee754_log10`.

In non-IEEE mode, `x == 0` maps to code `18` and `x < 0` maps to code `19`; NaNs pass through. It includes no-long-double aliases for `log10l`.

Dependencies are base-10 log kernel and standard error mapping.

Risk points: domain reporting only outside IEEE mode.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_log10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_log10f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_log10f.c

Wraps `float log10f(float x)` around `__ieee754_log10f`.

It uses float standard error codes `118` for zero and `119` for negative inputs outside IEEE mode.

Dependencies are float log10 kernel and compatibility handling.

Risk points: signed-zero behavior via `x == 0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_log10f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_log2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_log2.c

Wraps `double log2(double x)` around `__ieee754_log2`.

It maps zero and negative inputs to standard error codes `48` and `49` outside IEEE mode, while NaNs and positive values return the kernel result. It aliases `log2l` when long double is unavailable.

Dependencies are base-2 log kernel and standard error handling.

Risk points: newer wrapper with compatibility codes distinct from `log` and `log10`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_log2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_log2f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_log2f.c

Wraps `float log2f(float x)` around `__ieee754_log2f`.

It maps zero and negative inputs to float standard error codes `148` and `149` outside IEEE mode.

Dependencies are float base-2 log kernel and standard error mapping.

Risk points: compatibility behavior for non-positive inputs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_log2f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_logf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_logf.c

Wraps `float logf(float x)` around `__ieee754_logf`.

It maps `x == 0` to code `116` and `x < 0` to code `117` outside IEEE mode, passing NaNs and positive values through.

Dependencies are float log kernel and `__kernel_standard`.

Risk points: float signed-zero classification.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_logf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_pow.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_pow.c

Wraps `double pow(double x, double y)` around `__ieee754_pow`.

Compatibility handling covers `pow(NaN,0)`, `pow(0,0)`, zero to negative finite exponent, negative base to non-integer exponent, overflow, and underflow using standard error codes `42`, `20`, `23`, `24`, `21`, and `22`.

Dependencies are `__ieee754_pow`, `isnan`, `finite`, and `__kernel_standard`.

Risk points: many edge cases depend on the kernel result classification.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_pow.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_powf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_powf.c

Wraps `float powf(float x, float y)`.

It mirrors the double wrapper with float predicates and float-specific standard error codes for NaN-zero, zero-zero, zero-negative, negative non-integer, overflow, and underflow.

Dependencies are `__ieee754_powf`, `isnanf`, `finitef`, and standard error conversion.

Risk points: float result classification and error-code mapping.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_powf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_remainder.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_remainder.c

Wraps `double remainder(double x, double y)` around `__ieee754_remainder`.

Outside IEEE mode, non-NaN `y == 0` maps to standard error code `28`.

Dependencies are remainder kernel and standard error handler.

Risk points: zero divisor behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_remainder.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_remainderf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_remainderf.c

Wraps `float remainderf(float x, float y)`.

It mirrors the double wrapper with float kernel and error code `128` for zero divisor outside IEEE mode.

Dependencies are `__ieee754_remainderf` and `__kernel_standard`.

Risk points: float zero divisor handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_remainderf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_scalb.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_scalb.c

Implements legacy `scalb`, with signature controlled by `_SCALB_INT`.

It delegates to `__ieee754_scalb`. Outside IEEE mode it maps finite-input overflow to code `32`, underflow to code `33`, and sets `errno = ERANGE` when the non-integer exponent argument is non-finite.

Dependencies are `errno`, `finite`, `isnan`, and scalb kernel.

Risk points: legacy API compatibility and conditional function signature.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_scalb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_scalbf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_scalbf.c

Implements legacy float `scalbf`, with signature controlled by `_SCALB_INT`.

It delegates to `__ieee754_scalbf`, mapping overflow and underflow to float standard error codes `132` and `133`, and setting `errno = ERANGE` for non-finite float exponent in the non-int signature.

Dependencies are `errno`, `finitef`, `isnanf`, and float scalb kernel.

Risk points: conditional ABI and compatibility errno behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_scalbf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_sinh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_sinh.c

Wraps `double sinh(double x)` around `__ieee754_sinh`.

Outside IEEE mode, finite inputs producing non-finite results map to standard overflow code `25`.

Dependencies are `__ieee754_sinh`, `finite`, and `__kernel_standard`.

Risk points: overflow reporting only for finite input.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_sinh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_sinhf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_sinhf.c

Wraps `float sinhf(float x)` around `__ieee754_sinhf`.

It maps finite-input overflow to float standard error code `125` outside IEEE mode.

Dependencies are float sinh kernel and standard error handler.

Risk points: float overflow classification.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_sinhf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_sqrt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_sqrt.c

Wraps `double sqrt(double x)` around `__ieee754_sqrt`.

Outside IEEE mode, finite negative inputs map to standard error code `26`; NaNs return the raw result. If long double support is absent, it aliases `sqrtl` to `sqrt`.

Dependencies are sqrt kernel, alias macros, and standard error handling.

Risk points: domain behavior for negative zero/negative values depends on comparisons and kernel.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_sqrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_sqrtf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_sqrtf.c

Wraps `float sqrtf(float x)` around `__ieee754_sqrtf`.

It maps negative non-NaN inputs to float standard error code `126` outside IEEE mode.

Dependencies are float sqrt kernel and standard error conversion.

Risk points: float domain compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_sqrtf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_sqrtl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_sqrtl.c

Wraps `long double sqrtl(long double x)` when long double support exists.

It delegates to `__ieee754_sqrtl`, mapping negative non-NaN inputs to long-double standard error code `226` outside IEEE mode.

Dependencies are long-double sqrt kernel and `__HAVE_LONG_DOUBLE`.

Risk points: compiled only when long double support is present.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/w_sqrtl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libmenu/Makefile

Builds NetBSD `libmenu`.

It sets include flags for the current directory, optional `DEBUG_MENUS` debug flags, library name `menu`, dependency on `libcurses`, source files `menu.c item.c userptr.c internals.c driver.c post.c attributes.c`, installed headers `menu.h eti.h`, and extensive manual page links for the menu API.

Dependencies are NetBSD make infrastructure, curses, and `bsd.lib.mk`.

Risk points: API documentation link coverage must stay synchronized with exported functions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/attributes.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libmenu/attributes.c

Implements menu attribute accessors.

Functions set and get foreground, background, grey/unselectable attribute, and pad character. Passing `NULL` operates on global `_menui_default_menu`; otherwise the given `MENU` is modified.

Dependencies are `menu.h` and `_menui_default_menu` from `menu.c`.

Risk points: return types for some attribute getters are `char` despite fields being `attr_t`, which can truncate curses attributes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/attributes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/driver.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libmenu/driver.c

Implements `menu_driver(MENU *menu, int c)`, the central input dispatcher for libmenu.

It validates posted/connected state, handles request constants for movement, scrolling, page movement, first/last/next/previous item, toggle selection, pattern editing, and next/previous match. Printable characters extend the pattern and search items. Movement adjusts top row to keep the target visible and calls `_menui_goto_item`.

Dependencies are `menu.h`, `ctype.h`, `stdlib.h`, and internal helpers `_menui_match_pattern`, `_menui_draw_item`, `_menui_goto_item`, and `pos_menu_cursor`.

Risk points: mutates and frees pattern buffers; selection behavior differs for `O_RADIO`, `O_ONEVALUE`, and `O_SELECTABLE`; relies on neighbor links built by `internals.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/driver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/eti.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libmenu/eti.h

Defines common error codes for libmenu and libpanel-style APIs.

Constants include `E_OK`, `E_SYSTEM_ERROR`, `E_BAD_ARGUMENT`, `E_POSTED`, `E_CONNECTED`, `E_BAD_STATE`, `E_NO_ROOM`, `E_NOT_POSTED`, `E_UNKNOWN_COMMAND`, `E_NO_MATCH`, `E_NOT_SELECTABLE`, `E_NOT_CONNECTED`, `E_REQUEST_DENIED`, `E_INVALID_FIELD`, and `E_CURRENT`.

Dependencies: none beyond include guards.

Risk points: numeric negative error-code ABI must remain stable for callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/eti.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/internals.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libmenu/internals.c

Implements libmenu internal layout, matching, drawing, and navigation helpers.

`_menui_stitch_items` computes item grid positions and neighbor pointers according to row-major/column-major and cyclic/non-cyclic options. `_menui_calc_neighbours` fills left/right/up/down links. `_menui_goto_item` updates current item/top row and invokes menu/item hooks safely. Pattern helpers manage prefix matching with optional case-insensitivity. Drawing helpers render marks, names, descriptions, padding, foreground/grey/background attributes, and cursor position in curses windows.

Dependencies are curses APIs through `menu.h`, string functions, `ctype`, and `internals.h`.

Risk points: off-by-one navigation and redraw bugs can surface with partial last rows; pattern buffer length is compared to max item width; curses window dimensions affect layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/internals.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/internals.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libmenu/internals.h

Declares private libmenu helpers and match-direction constants.

It defines `MATCH_FORWARD`, `MATCH_REVERSE`, `MATCH_NEXT_FORWARD`, `MATCH_NEXT_REVERSE`, a local `max` macro, and prototypes for item drawing, menu drawing, item navigation, pattern matching, item-size calculation, and item stitching.

Dependencies are `menu.h`.

Risk points: private header is shared across implementation files; `max` macro may evaluate arguments multiple times.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/internals.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/item.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libmenu/item.c

Implements item lifecycle, item options, selection, current item, and item hook APIs.

It defines `_menui_default_item`, allocates `ITEM` objects with private copies of name/description, frees disconnected items, tracks parent menu/index, supports only `O_SELECTABLE` item options, returns item metadata, sets item value when menu options permit, and exposes item init/term hook setters/getters on menus.

Dependencies are `_menui_default_menu`, internal drawing for selected-value changes, and string allocation.

Risk points: `set_current_item` only sets `cur_item` directly and does not redraw or call hooks; `set_item_value` requires connected item and draws immediately; selection APIs allocate arrays caller must free.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/menu.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libmenu/menu.c

Implements most public `MENU` object APIs.

The file defines `_menui_default_menu`, manages mark/unmark strings, menu and subwindow pointers, format rows/columns, menu hooks, option flags, pattern buffers, construction/destruction, item attachment, scale calculation, top-row selection, item counts, and cursor placement. It copies defaults into new menus, sets default mark `"-"`, attaches item arrays, validates radio selection rules, and recalculates neighbor layout when options or items change.

Dependencies are `menu.h`, curses `stdscr`/window movement, string allocation, and internal stitch/match helpers.

Risk points: `set_menu_mark` and `set_menu_unmark` assume non-NULL string arguments; `free_menu` disconnects items but does not free `unmark.string`; item arrays are owned by caller, not freed by menu.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/menu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/menu.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libmenu/menu.h

Public header for NetBSD libmenu.

It defines driver request constants, option bit flags, `MENU_STR`, opaque typedefs that are then structurally defined, `ITEM` and `MENU` fields, hook type `Menu_Hook`, and prototypes for menu, item, attribute, pattern, cursor, post, and user-pointer APIs.

Dependencies are `<curses.h>` and `<eti.h>`.

Risk points: structs are exposed rather than opaque, so layout is ABI/API visible to consumers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/menu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/post.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libmenu/post.c

Implements `post_menu` and `unpost_menu`.

`post_menu` validates state, runs menu and item init hooks, checks window size with `getmaxyx`, clears selection for non-radio menus, marks the menu posted, and draws it. `unpost_menu` validates state, runs item/menu term hooks, clears `posted`, erases and refreshes the screen window.

Dependencies are curses window APIs and `_menui_draw_menu`.

Risk points: hooks run before size validation in `post_menu`; non-radio posting clears all selected flags.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/post.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/userptr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libmenu/userptr.c

Implements item and menu user pointer accessors.

`set_item_userptr`, `item_userptr`, `set_menu_userptr`, and `menu_userptr` store and return `char *` user data. Passing `NULL` targets default item/menu objects for setters/getters.

Dependencies are `_menui_default_menu` and `_menui_default_item`.

Risk points: user pointers are unowned raw pointers; type is `char *` rather than `void *`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libmenu/userptr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnpf/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libnpf/Makefile

Builds NetBSD `libnpf`.

It sets `USE_SHLIBDIR`, library name `npf`, manual page `libnpf.3`, source `npf.c`, installed header `npf.h`, includes the external BSD `libnv` source list, adds libnv sources to the build, adds include flags for libnv, and sets warning level 5.

Dependencies are NetBSD make infrastructure and external `libnv`.

Risk points: libnpf is tightly coupled to libnv source layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnpf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnpf/npf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libnpf/npf.c

Implements the userland libnpf API as an nvlist-based marshalling layer for NPF configuration and control.

Major areas:
- Configuration lifecycle: create/import/export/retrieve/submit/flush/destroy configs, build nested rules into flat arrays with `skip-to` markers, and track active/loaded state.
- Transport: `_npf_xfer_fd` sends requests through sockets on non-NetBSD or `nvlist_xfer_ioctl` to NPF character/block devices after version checking.
- Parameters: get/set/iterate named integer parameters and defaults.
- Dynamic rulesets: add/remove/remove-by-key/flush rules in named regular or NAT rulesets.
- Extensions and rprocs: construct extension call dictionaries, attach params, insert rprocs, and iterate them.
- Rules: create rules, set BPF code/key/info/priority/rproc/rid, insert top-level or subrules, iterate flattened rules with nesting levels, export/destroy/get fields.
- NAT: create NAT rules, set translation address/port/table/algo/NPT66, insert/iterate/get fields, and perform NAT lookup through connection lookup.
- Tables: create tables, add entries, build constant tables into CDB blobs via `cdbw`, insert/replace/iterate/get/destroy tables.
- Algorithms and connections: load ALG names, list connections, parse forward keys and NAT translated endpoints, and call a user callback.
- Private debug/dump helpers: add debug interface metadata and dump built nvlist config.

Dependencies include `<net/npf.h>`, libnv `nv.h`/`dnv.h`, ioctl constants, `cdbw`, sockets/ioctl transfer, address-family structures, and NPF kernel ABI versioning.

Risk points: ownership transfer is subtle because many insert functions append nvlist arrays then destroy/free wrapper objects; `_npf_rules_process` realloc failure is not checked before assignment; table CDB building uses temp files and mmap; iterator state is stored in `nl_config_t` and is not thread-safe; error extraction may allocate strings that callers must understand via `npf_error_t`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnpf/npf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnpf/npf.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libnpf/npf.h

Public libnpf API header.

It declares opaque types for configs, rules, rprocs, tables, NATs, and extensions; iterator type `nl_iter_t`; ruleset prefix `NPF_RULESET_MAP_PREF`; extension callback typedefs; connection callback typedef; and public APIs for configuration, ALG loading, parameters, dynamic rulesets, extension construction, rule construction/query/insertion/export/destruction, rproc construction/insertion/iteration, NAT construction/query/insertion/lookup, table construction/insertion/replacement, and connection listing. Under `_NPF_PRIVATE` it exposes iterators, ruleset listing, debug interface injection, and config dump.

Dependencies are `<sys/types.h>` and `<net/npf.h>`.

Risk points: ABI depends on opaque pointer typedefs and kernel NPF types; private API exposure is compile-flag controlled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnpf/npf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnvmm/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libnvmm/Makefile

Builds NetBSD `libnvmm`.

It sets library name `nvmm`, manual page `libnvmm.3`, source `libnvmm.c`, installed header `nvmm.h`, warning level 5, and suppresses dangling-pointer warnings for `libnvmm.c`.

Dependencies are NetBSD make infrastructure and the public NVMM header.

Risk points: warning suppression suggests known compiler diagnostics around pointer lifetimes in this low-level wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnvmm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnvmm/libnvmm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libnvmm/libnvmm.c

Implements the userland NVMM hypervisor library wrapper over `/dev/nvmm`.

The file maintains a global `nvmm_fd` and cached capability. `nvmm_init` opens `/dev/nvmm` read-only, while `nvmm_root_init` opens write-only; both verify kernel ABI version. Machine APIs create/destroy/configure machines and maintain a per-machine list of guest-physical mappings plus per-vCPU communication pages. VCPU APIs create/destroy/configure VCPUs, map comm pages, cache state/event/stop pointers, set/get state through comm-page flags and ioctl, inject events, run VCPUs, and copy exit state. Memory APIs map/unmap GPA and HVA ranges, track GPA-to-HVA translations locally, and abort if kernel GPA map/unmap fails after local state mutation. `nvmm_ctl` passes generic control requests, and `nvmm_vcpu_stop` sets the stop byte.

Dependencies include `/dev/nvmm`, NVMM ioctl ABI, `nvmm.h`, `sys/queue.h` lists, `mmap`, `PAGE_SIZE`, and architecture-specific `libnvmm_x86.c` on x86_64.

Risk points: global file descriptor is process-wide and not synchronized; GPA overlap validation ignores HVA collisions; GPA map/unmap aborts on kernel failure after local updates; vCPU IDs index the `pages` array and rely on capability bounds enforced elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnvmm/libnvmm.c -->