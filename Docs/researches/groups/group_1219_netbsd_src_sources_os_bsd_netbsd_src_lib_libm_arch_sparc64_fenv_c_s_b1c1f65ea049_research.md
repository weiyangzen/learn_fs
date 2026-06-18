# Group Research: group_1219_netbsd_src_sources_os_bsd_netbsd_src_lib_libm_arch_sparc64_fenv_c_s_b1c1f65ea049

Scope: subset A from `Docs/research_subset_a.md`, covering the listed NetBSD `lib/libm` architecture, compatibility, complex, compiler-rt make, conversion, and `ld128` files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/sparc64/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/sparc64/fenv.c

Implements the C99 floating-point environment API for SPARC/SPARC64 by reading and writing the floating-point state register `%fsr`.

Provides weak aliases for standard `fenv.h` entry points, exception flag operations, rounding-mode get/set, environment save/restore/update, and NetBSD exception-mask extensions. It uses `ldx/stx %fsr` on 64-bit SPARC and `ld/st %fsr` otherwise. `feraiseexcept` deliberately performs volatile floating-point operations to raise invalid, divide-by-zero, overflow, underflow, and inexact.

Dependencies and risks: relies on `<fenv.h>` SPARC bit definitions matching the FSR layout. Raw environment loads assume valid `fenv_t` objects or environment macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/sparc64/fenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_argred.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_argred.S

Provides hidden VAX helper entry points `__libm_argred` and `__libm_sincos` for `_sin`, `_cos`, and `_tan`.

`__libm_argred` reduces an argument to a `[-pi/4, pi/4]`-style interval and returns a quadrant, reduced D-format argument, F-format extension, and sine/cosine selector. Small arguments use split tables for multiples of `pi/2`; larger arguments use `trigred`, which multiplies selected bits of `2/pi`, handles cancellation by generating additional bits, computes the quadrant, and converts the product back to VAX floating formats. `__libm_sincos` selects sine or cosine polynomial coefficients, applies extension correction, and fixes signs by quadrant.

Dependencies and risks: exact VAX D/F-format layout, register contracts, table constants, and PSL/FPA behavior are integral to correctness. This file is directly consumed by `n_sincos.S` and `n_tan.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_argred.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_atan2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_atan2.S

Implements VAX `atan2`, `atan2f`, and `atan2l` aliases in assembly.

The float wrapper promotes to double and converts back; long double aliases to the double implementation. The routine rejects VAX reserved operands, handles zero `x`/`y`, exponent-difference shortcuts, and quadrant signs explicitly. It reduces `|y/x|` into ranges around 0, 1/2, 1, 3/2, or infinity, evaluates an arctangent polynomial table, then applies `pi`, `pi/2`, and sign corrections.

Dependencies and risks: accuracy depends on the interval constants and polynomial table. The special-case comments describe IEEE-style NaN/Inf behavior, but actual VAX behavior is reserved-operand oriented.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_atan2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_cabs.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_cabs.S

Implements VAX `hypot`, `hypotf`, `hypotl`, compatibility `_cabs`, Fortran `z_abs`, and hidden helper `__libm_cdabs_r6`.

The code orders absolute component magnitudes, scales by exponent to avoid overflow/underflow, ignores negligible smaller components, computes scaled `x*x + y*y`, and jumps into the internal double square-root helper. Reserved operands are propagated for public calls and copied through for internal complex-square-root use.

Dependencies and risks: depends on `__libm_dsqrt_r5` in `n_sqrt.S` and a register protocol using `%r6` for scaling. Overflow recovery intentionally halves and re-doubles to produce meaningful VAX overflow behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_cabs.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_cbrt.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_cbrt.S

Implements VAX cube root for double, float wrapper, long-double alias, and Fortran-style by-reference entry.

Zero and reserved operands return unchanged. The implementation preserves sign, builds an initial estimate from exponent/bias arithmetic, refines it with single-precision rational correction, then applies a final double-precision correction. The sign is restored at return.

Dependencies and risks: assumes VAX D-format exponent and fraction layout. Comments claim maximum error below 0.667 ulp.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_cbrt.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_infnan.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_infnan.S

Provides the old VAX `infnan(int)` helper used by assembly math error paths.

It sets global `errno` to `ERANGE` only for positive `ERANGE`; all other inputs set `EDOM`. It then executes `emodd` with a reserved-operand pattern to trigger a reserved operand fault, returning only if execution continues.

Dependencies and risks: assumes writable `_C_LABEL(errno)` and VAX reserved-operand fault semantics rather than IEEE NaN/Inf returns.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_infnan.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_scalbn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_scalbn.S

Implements VAX `scalbn`, `ldexp`, and float/long-double aliases.

The float wrapper converts through double; long double aliases to double. The routine bounds-checks exponent changes, handles zero/reserved operands specially, adjusts the VAX exponent field, underflows to signed zero, and calls `infnan(ERANGE)` on overflow while preserving the input sign if execution resumes.

Dependencies and risks: depends on VAX exponent-field extraction/insertion and `infnan` for overflow signalling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_scalbn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_sincos.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_sincos.S

Implements VAX `sin`, `cos`, float wrappers, and long-double aliases.

Public float entries promote to double and convert back. Double entries return zero/reserved operands unchanged where appropriate, save PSL invalid/floating-underflow bits, clear them during internal reduction, call `__libm_argred`, then call `__libm_sincos` with `%r4` selecting sine or cosine.

Dependencies and risks: tightly coupled to `n_argred.S` register conventions and PSL status-bit handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_sincos.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_sqrt.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_sqrt.S

Implements VAX `sqrt`, `sqrtf`, long-double aliases, by-reference `d_sqrt`, and hidden helper `__libm_dsqrt_r5`.

Zero and reserved operands return unchanged. Positive inputs use W. Kahan-style initial approximation, two Heron iterations, scaling, and a cubic refinement. Negative nonzero input calls `infnan(EDOM)`. The hidden helper is used by complex absolute value support and has guard `halt` instructions before its local entry.

Dependencies and risks: assumes VAX D-format layout and VAX fault semantics for domain errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_sqrt.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_support.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_support.S

Implements assorted VAX support functions: `copysign`, `copysignf`, `logb`, `logbf`, `finite`, `finitef`, `isnanf`, `scalb`, and `drem`.

`copysign*` copy sign bits unless the magnitude is zero/reserved. `logb` extracts and unbiases the VAX exponent, returning a large negative sentinel for zero and the operand for reserved values. `finite` is false only for reserved operands; `isnanf` always returns false. `scalb` adjusts the exponent using a double exponent argument, underflows to zero, or calls `infnan`. `drem` implements IEEE-style rounded remainder with scaling, reduction loops, tie-to-even handling, and reserved-operand checks.

Dependencies and risks: all behavior is VAX-format-specific, with error paths routed through reserved-operand faults.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_support.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_tan.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_tan.S

Implements VAX `tan`, `tanf`, and long-double aliases.

The double entry returns zero/reserved operands unchanged, saves and clears PSL invalid/floating-underflow bits, calls `__libm_argred`, evaluates sine and cosine via `__libm_sincos`, then returns their quotient. The float wrapper promotes to double and converts back.

Dependencies and risks: depends on `n_argred.S` helper ABI and exposes the same VAX polynomial/range-reduction accuracy limits; comments report observed maximum error around 2.15 ulp.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_tan.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/x86_64/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/x86_64/fenv.c

Implements C99 floating-point environment APIs for x86_64 using both x87 and SSE/MXCSR state.

Defines inline assembly helpers for x87 control/status/environment and MXCSR load/store. A constructor records the runtime x87 control word into `__fe_dfl_env`. Exception flag functions keep x87 status and MXCSR in sync. Rounding mode checks that x87 and SSE agree, returning `-1` if not. Environment functions preserve reserved x87 upper bits around `FE_DFL_ENV`, and extension functions enable/disable exception masks in both x87 and SSE.

Dependencies and risks: correctness requires x87 and SSE masks/rounding bits to remain synchronized. `fnstenv` side effects are explicitly compensated by restoring the x87 control word.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/x86_64/fenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/compat/compat_cabs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/compat/compat_cabs.c

Provides a legacy ABI `cabs(struct complex)` wrapper for old code expecting a struct argument rather than C99 complex.

Defines a local `{ double x; double y; }` struct and returns `hypot(z.x, z.y)`. Emits a linker warning for references to compatibility `cabs()`.

Dependencies and risks: intentionally separate from the C99 `double complex` `cabs`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/compat/compat_cabs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/compat/compat_cabsf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/compat/compat_cabsf.c

Provides a legacy ABI `cabsf(struct complex)` wrapper for old float complex struct callers.

Defines a local `{ float x; float y; }` struct and returns `hypotf(z.x, z.y)`. Emits a linker warning for references to compatibility `cabsf()`.

Dependencies and risks: intended for compatibility, not the C99 `float complex` ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/compat/compat_cabsf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/compiler_rt/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/compiler_rt/Makefile.inc

Makefile fragment adding selected compiler-rt complex multiply/divide builtins to libm.

Computes compiler-rt source paths from `${MACHINE_CPU}` and `${MACHINE_ARCH}`, with a powerpc special case. Adds generic complex support sources for `mul*3` and `div*3`, and conditionally adds quad/long-double complex builtins for powerpc, sparc64, and aarch64. Prefers architecture assembly implementations when present, otherwise adds C sources with missing-prototype warnings disabled.

Dependencies and risks: depends on compiler-rt layout under `sys/external/bsd/compiler_rt` and includes compiler-rt ABI settings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/compiler_rt/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/Makefile.inc

Build fragment for NetBSD libm complex functions.

Adds `.PATH` for `complex`, lists core complex sources and catrig wrapper sources, then expands each core source into double/float/long-double variants. It also installs manpages and MLINKs, excluding internal `catrig*` and `cephes_*` helper files from manpage generation. Separate `CATRIG_SRCS` adds long-double wrapper variants for inverse trig/hyperbolic functions.

Dependencies and risks: relies on filename convention where `foo.c`, `foof.c`, and `fool.c` exist for most entries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cabs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cabs.c

Implements C99 `cabs(double complex)`.

Returns `hypot(__real__ z, __imag__ z)`, relying on `hypot` for scaling and special cases.

Dependencies and risks: uses GCC complex component extensions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cabs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cabsf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cabsf.c

Implements C99 `cabsf(float complex)`.

Returns `hypotf(__real__ z, __imag__ z)`, relying on `hypotf` for numerical robustness.

Dependencies and risks: uses GCC complex component extensions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cabsf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cabsl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cabsl.c

Implements C99 `cabsl(long double complex)`.

Returns `hypotl(__real__ z, __imag__ z)`.

Dependencies and risks: uses GCC complex component extensions and long-double `hypotl`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cabsl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cacos.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cacos.c

Implements Moshier-derived double `cacos`.

Computes `casin(z)`, then returns `(pi/2 - Re(casin(z))) - Im(casin(z))*I`.

Dependencies and risks: inherits branch behavior and special cases from `casin`/`clog`/`csqrt`; newer `catrig.c` also provides a more careful implementation when selected by build configuration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cacos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cacosf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cacosf.c

Implements Moshier-derived float `cacosf`.

Computes `casinf(z)`, then returns `((float)M_PI_2 - crealf(w)) - cimagf(w)*I`.

Dependencies and risks: inherits numerical and branch behavior from `casinf`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cacosf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cacosh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cacosh.c

Implements double `cacosh`.

Uses principal-value formula `clog(z + csqrt(z + 1) * csqrt(z - 1))`; the alternative `I * cacos(z)` is disabled because it does not give the principal value.

Dependencies and risks: special-case behavior is delegated to `clog` and `csqrt`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cacosh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cacoshf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cacoshf.c

Implements float `cacoshf`.

Uses `clogf(z + csqrtf(z + 1) * csqrtf(z - 1))`; disabled code notes `I * cacosf(z)` does not produce the principal value.

Dependencies and risks: delegated to float complex log and square root implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cacoshf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cacoshl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cacoshl.c

Implements long-double `cacoshl`.

Uses `clogl(z + csqrtl(z + 1) * csqrtl(z - 1))`, with the non-principal `I * cacosl(z)` path disabled.

Dependencies and risks: delegated to `clogl` and `csqrtl`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cacoshl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cacosl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cacosl.c

Implements Moshier-derived long-double `cacosl`.

Computes `casinl(z)`, then returns `(M_PI_2L - creall(w)) - cimagl(w)*I`.

Dependencies and risks: includes `cephes_subrl.h` for long-double constants; inherits behavior from `casinl`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cacosl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/carg.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/carg.c

Implements C99 `carg(double complex)`.

Returns `atan2(__imag__ z, __real__ z)`.

Dependencies and risks: uses GCC complex component extensions and platform `atan2` semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/carg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cargf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cargf.c

Implements C99 `cargf(float complex)`.

Returns `atan2f(__imag__ z, __real__ z)`.

Dependencies and risks: uses GCC complex component extensions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cargf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cargl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cargl.c

Implements C99 `cargl(long double complex)`.

Returns `atan2l(__imag__ z, __real__ z)`.

Dependencies and risks: uses GCC complex component extensions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cargl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/casin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/casin.c

Implements Moshier-derived double `casin`.

Uses the identity `asin(z) = -i log(i*z + sqrt(1 - z*z))`. A small-argument power series and a real-domain shortcut are present but disabled. Weak alias maps public `casin` to `_casin`.

Dependencies and risks: branch and special-case handling depend on `csqrt` and `clog`; the disabled shortcut notes that `casin(>1)` is defined for complex inputs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/casin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/casinf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/casinf.c

Implements Moshier-derived float `casinf`.

Uses `-i log(i*z + sqrt(1 - z*z))` with float complex operations. Disabled code contains a power series and an incorrect real-domain test.

Dependencies and risks: depends on `csqrtf` and `clogf`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/casinf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/casinh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/casinh.c

Implements double `casinh`.

Returns `-I * casin(z * I)`.

Dependencies and risks: simple identity wrapper; inherits all behavior from `casin`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/casinh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/casinhf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/casinhf.c

Implements float `casinhf`.

Returns `-I * casinf(z * I)`.

Dependencies and risks: simple identity wrapper over `casinf`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/casinhf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/casinhl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/casinhl.c

Implements long-double `casinhl`.

Returns `-I * casinl(z * I)`.

Dependencies and risks: simple identity wrapper over `casinl`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/casinhl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/casinl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/casinl.c

Implements Moshier-derived long-double `casinl`.

Uses the same `-i log(i*z + sqrt(1 - z*z))` formula as the double version. Disabled code includes a small-argument power series and incorrect real-domain shortcut.

Dependencies and risks: depends on `csqrtl`, `clogl`, and long-double math support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/casinl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catan.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catan.c

Implements Moshier-derived double `catan`.

Computes real part as reduced `0.5 * atan2(2*x, 1 - x*x - y*y)` via `_redupi`, and imaginary part as `0.25 * log(((x*x + (y+1)^2) / (x*x + (y-1)^2)))`. Singular/overflow cases return `DBL_MAX + DBL_MAX*I`.

Dependencies and risks: uses Cephes helper `_redupi`; special cases are coarse compared with newer `catrig.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catanf.c

Implements Moshier-derived float `catanf`.

Float analogue of `catan`, using `_redupif`, `atan2f`, and `logf`. Singular/overflow cases return `FLT_MAX + FLT_MAX*I`.

Dependencies and risks: depends on `cephes_subrf` helpers and has simplified overflow handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catanh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catanh.c

Implements double `catanh`.

Returns `-I * catan(z * I)`.

Dependencies and risks: simple identity wrapper over `catan`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catanh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catanhf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catanhf.c

Implements float `catanhf`.

Returns `-I * catanf(z * I)`.

Dependencies and risks: simple identity wrapper over `catanf`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catanhf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catanhl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catanhl.c

Implements long-double `catanhl`.

Returns `-I * catanl(z * I)`.

Dependencies and risks: simple identity wrapper over `catanl`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catanhl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catanl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catanl.c

Implements Moshier-derived long-double `catanl`.

Uses long-double versions of the same formulas as `catan`, with `_redupil` and `LDBL_MAX` overflow sentinel.

Dependencies and risks: depends on `cephes_subrl.h`; singular handling returns finite maximums rather than nuanced IEEE special cases.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catanl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catrig.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catrig.c

Provides careful double implementations of `casinh`, `casin`, `cacos`, `cacosh`, `catanh`, and `catan`, with weak aliases for `casin` and `catan`.

The code follows Hull, Fairgrieve, and Tang algorithms for complex arcsine/arccosine, using helper `f(a,b,hypot)` and `do_hard_work` to avoid cancellation, underflow, and overflow near branch cuts. It has explicit NaN/Inf handling, inexact raising, small-argument shortcuts, large-value `clog` optimization, and reciprocal scaling for `catanh`.

Dependencies and risks: complex and numerically delicate; depends on `math_private.h` word access macros and exact thresholds for IEEE/VAX formats.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catrig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catrigf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catrigf.c

Provides float implementations of `casinhf`, `casinf`, `cacosf`, `cacoshf`, `catanhf`, and `catanf`, mirroring `catrig.c`.

Uses float-specific thresholds, `hypotf`, `log1pf`, `atan2f`, and float word access. Handles NaN/Inf cases explicitly, raises inexact for nontrivial finite cases, and rescales near underflow/overflow boundaries.

Dependencies and risks: comments note most detailed explanation lives in `catrig.c`; correctness depends on float-specific constants and `math_private.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catrigf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catrigl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catrigl.c

Intended long-double version of the Hull/Fairgrieve/Tang complex inverse trig implementation.

Most implementation is inside `#ifdef notyet` because long-double support such as `log1pl`/format plumbing is not enabled here. In the compiled fallback, long-double inverse trig/hyperbolic symbols are strong aliases to the double implementations: `_casinl -> casin`, `_catanl -> catan`, `cacoshl -> cacosh`, `cacosl -> cacos`, `casinhl -> casinh`, and `catanhl -> catanh`.

Dependencies and risks: actual precision is reduced to double in fallback builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/catrigl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ccos.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ccos.c

Implements double `ccos`.

Uses `_cchsh(cimag(z), &ch, &sh)` and returns `cos(x)*cosh(y) - i*sin(x)*sinh(y)`.

Dependencies and risks: depends on Cephes helper `_cchsh`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ccos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ccosf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ccosf.c

Implements float `ccosf`.

Uses `_cchshf` and returns `cosf(x)*coshf(y) - i*sinf(x)*sinhf(y)`.

Dependencies and risks: depends on `cephes_subrf`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ccosf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ccosh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ccosh.c

Implements double `ccosh`.

Returns `cosh(x)*cos(y) + i*sinh(x)*sin(y)`.

Dependencies and risks: direct formula can inherit overflow behavior from real hyperbolic functions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ccosh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ccoshf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ccoshf.c

Implements float `ccoshf`.

Returns `coshf(x)*cosf(y) + i*sinhf(x)*sinf(y)`.

Dependencies and risks: direct formula with real float math overflow behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ccoshf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ccoshl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ccoshl.c

Implements long-double `ccoshl`.

Returns `coshl(x)*cosl(y) + i*sinhl(x)*sinl(y)`.

Dependencies and risks: direct long-double formula.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ccoshl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ccosl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ccosl.c

Implements long-double `ccosl`.

Uses `_cchshl` and returns `cosl(x)*coshl(y) - i*sinl(x)*sinhl(y)`.

Dependencies and risks: depends on `cephes_subrl`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ccosl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subr.c

Provides double Cephes-derived helper routines for complex trig.

`_cchsh` computes cosh/sinh together, using direct functions for small `|x|` and exponential identities otherwise. `_redupi` subtracts the nearest multiple of pi using split constants. `_ctans` computes a Taylor expansion for `cosh(2y) - cos(2x)` when the tangent denominator is small.

Dependencies and risks: `_ctans` loops until relative term size reaches `MACHEP`; callers rely on it near cancellation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subr.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subr.h

Declares double Cephes helper APIs `_cchsh`, `_redupi`, and `_ctans`.

Dependencies and risks: uses `double complex` in a prototype, so consumers must include `<complex.h>` before or through this header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrf.c

Provides float Cephes-derived helpers.

`_cchshf` jointly computes cosh/sinh, `_redupif` subtracts nearest multiple of pi using split float-friendly constants, and `_ctansf` evaluates the cancellation-safe tangent denominator series.

Dependencies and risks: float threshold `MACHEPF` controls series termination.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrf.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrf.h

Declares float Cephes helper APIs `_cchshf`, `_redupif`, and `_ctansf`.

Dependencies and risks: exposes `float complex` prototype for callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrl.c

Provides long-double Cephes-derived helpers.

`_cchshl` computes cosh/sinh together, `_redupil` reduces by split long-double pi constants, and `_ctansl` evaluates the cancellation-safe tangent denominator series. VAX uses a reduced constant set for `DP3` and `MACHEPL`.

Dependencies and risks: long-double behavior varies with `__vax__` and platform precision.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrl.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrl.h

Declares long-double Cephes helper APIs and defines `M_PIL` and `M_PI_2L`.

Dependencies and risks: constants are used by long-double complex wrappers that need pi values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cexp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cexp.c

Implements double `cexp`.

Computes `exp(x) * (cos(y) + i*sin(y))`.

Dependencies and risks: direct formula inherits overflow/underflow behavior from `exp`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cexp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cexpf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cexpf.c

Implements float `cexpf`.

Computes `expf(x) * (cosf(y) + i*sinf(y))`.

Dependencies and risks: direct formula.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cexpf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cexpl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cexpl.c

Implements long-double `cexpl`.

Computes `expl(x) * (cosl(y) + i*sinl(y))`.

Dependencies and risks: direct formula with long-double real math behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cexpl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cimag.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cimag.c

Implements `cimag(double complex)`.

Wraps the value in `double_complex` from `math_private.h` and returns `IMAG_PART(w)`.

Dependencies and risks: depends on NetBSD complex layout helpers in `math_private.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cimag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cimagf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cimagf.c

Implements `cimagf(float complex)`.

Wraps the value in `float_complex` and returns `IMAG_PART(w)`.

Dependencies and risks: depends on `math_private.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cimagf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cimagl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cimagl.c

Implements `cimagl(long double complex)`.

Wraps the value in `long_double_complex` and returns `IMAG_PART(w)`.

Dependencies and risks: depends on long-double complex layout helper macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cimagl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/clog.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/clog.c

Implements double `clog`.

Returns `log(cabs(z)) + i*atan2(cimag(z), creal(z))`.

Dependencies and risks: direct polar formula; robustness depends on `cabs`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/clog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/clogf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/clogf.c

Implements float `clogf`.

Returns `logf(cabsf(z)) + i*atan2f(cimagf(z), crealf(z))`.

Dependencies and risks: direct polar formula.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/clogf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/clogl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/clogl.c

Implements long-double `clogl`.

Returns `logl(cabsl(z)) + i*atan2l(cimagl(z), creall(z))`.

Dependencies and risks: direct polar formula.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/clogl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/conj.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/conj.c

Implements `conj(double complex)`.

Uses `double_complex` and negates the imaginary part in place.

Dependencies and risks: preserves real part and relies on `math_private.h` layout macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/conj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/conjf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/conjf.c

Implements `conjf(float complex)`.

Uses `float_complex` and negates `IMAG_PART`.

Dependencies and risks: depends on `math_private.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/conjf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/conjl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/conjl.c

Implements `conjl(long double complex)`.

Uses `long_double_complex` and negates the imaginary component.

Dependencies and risks: depends on long-double complex layout helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/conjl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cpow.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cpow.c

Implements double `cpow(a, z)`.

For `|a| == 0`, returns complex zero. Otherwise computes polar form: magnitude `pow(|a|, Re z)`, argument `Re z * carg(a)`, with additional `exp(-Im z * arg(a))` and `Im z * log(|a|)` adjustments.

Dependencies and risks: direct polar formula; branch behavior follows `carg` and `log`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cpow.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cpowf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cpowf.c

Implements float `cpowf`.

Float analogue of the polar power formula, returning zero for zero base.

Dependencies and risks: direct formula with float real math behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cpowf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cpowl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cpowl.c

Implements long-double `cpowl`.

Long-double analogue of the polar power formula, returning zero for zero base.

Dependencies and risks: branch behavior follows `cargl` and `logl`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cpowl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cproj.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cproj.c

Implements `cproj(double complex)`.

Returns finite inputs unchanged. If either component is infinite, projects to positive infinity on the real axis and signed zero on the imaginary axis, using `copysign(0.0, cimag(z))`.

Dependencies and risks: uses `REAL_PART`/`IMAG_PART` layout helpers and `HUGE_VAL`/`INFINITY`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cproj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cprojf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cprojf.c

Implements `cprojf(float complex)`.

Projects any complex infinity to positive real infinity plus signed imaginary zero.

Dependencies and risks: uses float layout helpers and `copysignf`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cprojf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cprojl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cprojl.c

Implements `cprojl(long double complex)`.

Projects infinite complex values to positive real infinity and signed imaginary zero.

Dependencies and risks: uses long-double layout helpers and `copysignl`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/cprojl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/creal.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/creal.c

Implements `creal(double complex)`.

Wraps the value in `double_complex` and returns `REAL_PART(w)`.

Dependencies and risks: depends on `math_private.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/creal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/crealf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/crealf.c

Implements `crealf(float complex)`.

Wraps the value in `float_complex` and returns `REAL_PART(w)`.

Dependencies and risks: depends on `math_private.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/crealf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/creall.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/creall.c

Implements `creall(long double complex)`.

Wraps the value in `long_double_complex` and returns `REAL_PART(w)`.

Dependencies and risks: depends on long-double complex layout helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/creall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csin.c

Implements double `csin`.

Uses `_cchsh` and returns `sin(x)*cosh(y) + i*cos(x)*sinh(y)`.

Dependencies and risks: depends on `cephes_subr`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csinf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csinf.c

Implements float `csinf`.

Uses `_cchshf` and returns `sinf(x)*coshf(y) + i*cosf(x)*sinhf(y)`.

Dependencies and risks: depends on `cephes_subrf`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csinf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csinh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csinh.c

Implements double `csinh`.

Returns `sinh(x)*cos(y) + i*cosh(x)*sin(y)`.

Dependencies and risks: direct formula.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csinh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csinhf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csinhf.c

Implements float `csinhf`.

Returns `sinhf(x)*cosf(y) + i*coshf(x)*sinf(y)`.

Dependencies and risks: direct formula.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csinhf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csinhl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csinhl.c

Implements long-double `csinhl`.

Returns `sinhl(x)*cosl(y) + i*coshl(x)*sinl(y)`.

Dependencies and risks: direct long-double formula.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csinhl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csinl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csinl.c

Implements long-double `csinl`.

Uses `_cchshl` and returns `sinl(x)*coshl(y) + i*cosl(x)*sinhl(y)`.

Dependencies and risks: depends on `cephes_subrl`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csinl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csqrt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csqrt.c

Implements double `csqrt`.

Handles real inputs specially, preserving branch-cut behavior for negative zero imaginary parts. Pure imaginary inputs use symmetric square-root formulas. General inputs are rescaled up or down to avoid internal overflow/underflow, use `cabs` to compute magnitude, then choose formulas based on the sign of the real part.

Dependencies and risks: explicit scale constants assume IEEE double characteristics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csqrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csqrtf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csqrtf.c

Implements float `csqrtf`.

Float analogue of `csqrt`, with real/pure-imaginary fast paths, negative-zero branch-cut handling, and scaling by powers of two to avoid overflow/underflow.

Dependencies and risks: scale constants are float-specific.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csqrtf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csqrtl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csqrtl.c

Implements long-double `csqrtl`, imported from FreeBSD style code.

Handles zero, infinite imaginary part, NaN real part, and infinite real part explicitly before normal computation. Uses CACM Algorithm 312 with `hypotl`, scaling inputs above `LDBL_MAX / (1 + sqrt(2))`, and rescales the result.

Dependencies and risks: includes comments about compiler complex multiplication/division and C99 limited-range concerns; relies on explicit special-case handling for infinities.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/csqrtl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ctan.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ctan.c

Implements double `ctan`.

Computes denominator `cos(2x) + cosh(2y)`, switches to `_ctans(z)` when the denominator is small, returns `DBL_MAX + DBL_MAX*I` on zero denominator, otherwise returns `sin(2x)/d + i*sinh(2y)/d`.

Dependencies and risks: depends on Cephes `_ctans` for cancellation-sensitive cases.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ctan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ctanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ctanf.c

Implements float `ctanf`.

Float analogue of `ctan`, using `_ctansf` for small denominators and `FLT_MAX + FLT_MAX*I` for zero denominator.

Dependencies and risks: depends on `cephes_subrf`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ctanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ctanh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ctanh.c

Implements double `ctanh`.

Uses denominator `cosh(2x) + cos(2y)` and returns `sinh(2x)/d + i*sin(2y)/d`.

Dependencies and risks: direct formula without the cancellation helper used by `ctan`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ctanh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ctanhf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ctanhf.c

Implements float `ctanhf`.

Uses `coshf(2x) + cosf(2y)` denominator and returns the corresponding hyperbolic tangent components.

Dependencies and risks: direct formula.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ctanhf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ctanhl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ctanhl.c

Implements long-double `ctanhl`.

Uses denominator `coshl(2x) + cosl(2y)` and returns `sinhl(2x)/d + i*sinl(2y)/d`.

Dependencies and risks: direct long-double formula.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ctanhl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ctanl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ctanl.c

Implements long-double `ctanl`.

Long-double analogue of `ctan`, using `_ctansl` for small denominators and `LDBL_MAX + LDBL_MAX*I` on zero denominator.

Dependencies and risks: depends on `cephes_subrl`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/complex/ctanl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/convertFreeBSD -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/convertFreeBSD

Small shell script for mechanical conversion of imported FreeBSD libm sources.

Runs `sed -i` over passed files to rename FreeBSD long-double bit-structure identifiers and field names to NetBSD equivalents such as `ieee_ext_u`, `extu_frac`, `extu_ld`, `extu_exp`, and `extu_sign`.

Dependencies and risks: destructive in-place rewrite; assumes exact source token patterns.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/convertFreeBSD -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/b_expl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/b_expl.c

Contains a static long-double exponential kernel `__exp__D(x, c)` for extended/ld128-style libm code.

Defines polynomial coefficients and constants as `union ieee_ext_u` values. The kernel handles NaN, finite in-range reduction by `k*ln2`, evaluates a rational approximation for `exp` on the reduced argument, and returns `ldexpl(...)`. Very negative finite inputs underflow via `ldexpl(1., -5000)`; very positive finite inputs overflow via `ldexpl(1., 5000)`; infinities return mathematical infinity/zero behavior.

Dependencies and risks: this file only defines a static helper; inclusion context must use it. Depends on `math_private.h`, `LD80C`, `copysignl`, `ldexpl`, and `isfinite`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/b_expl.c -->