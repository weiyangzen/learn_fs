# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/fplsp.S lines 1-9821

## Purpose

This chunk is the front and main mathematical body of Motorola's M68060 floating-point library support package for the m68k Ceph client source import. It exposes branch-table entry points for unimplemented 68060 floating-point operations and implements most software transcendental and dyadic helpers for single, double, and extended operands.

The code is assembly for 68k/FPU state. It emulates operations that a caller enters through labels such as `_fsins_`, `_fcosd_`, `_fetoxx_`, `_flognp1s_`, `_fmods_`, and `_fscalex_`. Each wrapper normalizes the ABI into an internal extended-precision representation, classifies operands with `tag`, dispatches to a normal/denormal/special-case helper, restores saved registers, and returns the result in `fp0`; `fsincos` also returns a second value through `fp1` after a final register swap.

## Public Entry Surface In This Chunk

The file begins with a branch table for all library entry points. The implemented labels in this line range include:

- Trigonometric and inverse trigonometric wrappers: `_fsin{s,d,x}_`, `_fcos{s,d,x}_`, `_ftan{s,d,x}_`, `_fsincos{s,d,x}_`, `_fasin{s,d,x}_`, `_facos{s,d,x}_`, `_fatan{s,d,x}_`.
- Hyperbolic wrappers: `_fsinh{s,d,x}_`, `_fcosh{s,d,x}_`, `_ftanh{s,d,x}_`, `_fatanh{s,d,x}_`.
- Exponential/logarithmic wrappers: `_fetox{s,d,x}_`, `_fetoxm1{s,d,x}_`, `_ftwotox{s,d,x}_`, `_ftentox{s,d,x}_`, `_flogn{s,d,x}_`, `_flognp1{s,d,x}_`, `_flog10{s,d,x}_`, `_flog2{s,d,x}_`.
- Decomposition and dyadic wrappers: `_fgetexp{s,d,x}_`, `_fgetman{s,d,x}_`, `_frem{s,d,x}_`, `_fmod{s,d,x}_`, `_fscale{s,d,x}_`.

The arithmetic operations `_fadd*`, `_fsub*`, `_fmul*`, `_fdiv*`, `_fabs*`, `_fneg*`, `_fsqrt*`, `_fint*`, and `_fintrz*` are present in the top branch table but their actual labels start after this requested line range, so this chunk only establishes their dispatch slots.

## Shared Frame, State, And Operand Model

The wrappers allocate a fixed `LOCAL_SIZE` stack frame and use symbolic offsets for saved integer registers, saved FPU registers, user `FPCR/FPSR/FPIAR`, source/destination operands, scratch extended values, and local flags. `FP_SRC`, `FP_DST`, `FP_SCR0`, and `FP_SCR1` hold 12-byte extended values split into exponent/sign, high mantissa, and low mantissa fields.

Operand classification is stored as single-byte tags in `STAG` and `DTAG` using constants `NORM`, `ZERO`, `INF`, `QNAN`, `DENORM`, `SNAN`, and `UNNORM`. The `tag` routine at the end of this range inspects the exponent, j-bit, and mantissa words. It returns zero, denormal, normal, infinity, or quiet NaN, and calls `unnorm_fix` for unnormalized nonzero encodings. That helper is outside the requested range, so this chunk depends on the later tail for complete unnormalized handling.

The wrappers save `d0-d1/a0-a1`, `fp0/fp1`, and the user's `FPCR/FPSR`, then clear `FPCR` for internal extended, round-to-nearest work. Before the final operation that should set user-visible exception state, kernels restore the user's rounding mode and precision and branch to exception postprocessors such as `t_inx2`, `t_catch`, `t_catch2`, `t_pinx2`, `t_minx2`, `t_ovfl*`, `t_unfl*`, `t_dz*`, and `t_operr`. Those postprocessors mostly live after line 9821, so this chunk's correctness is tightly coupled to the later exception machinery.

## Control Flow Patterns

The monadic wrappers all follow the same control-flow template:

1. Load a single, double, or extended argument into `FP_SRC`.
2. Call `tag` and save the source tag in `STAG`.
3. Clear volatile FPSR exception bits in the saved user status.
4. Pass the saved user rounding/precision byte in `d0`.
5. Dispatch by tag to the normal kernel, zero handler, infinity handler, qNaN handler, or denormal kernel.
6. Restore saved registers/control state and return.

Special-case dispatch is operation-specific. For example, sine returns signed zero for zero, raises operand error for infinity, propagates qNaN, and treats denormals through `ssind`. Cosine maps zero and denormal to one, but infinity to operand error. Logs map zero to divide-by-zero, infinity to positive infinity, and qNaN to NaN propagation. Hyperbolic tangent maps infinity to signed one. These case tables are encoded directly in the wrapper branches, not data-driven.

The dyadic wrappers for `frem`, `fmod`, and `fscale` load both destination and source operands into `FP_DST` and `FP_SRC`, tag both, then dispatch primarily on the source tag. Their normal paths pass `a0 = source` and `a1 = destination` to shared kernels. qNaN and exceptional source cases branch to shared special handlers defined later in the file.

## Main Mathematical Kernels

### Trigonometric Functions

`ssin`, `scos`, `ssincos`, `stan`, and their denormal variants implement sine, cosine, sincos, and tangent. For small inputs around `2**(-40)`, sine/tangent return the argument and cosine returns one with inexact behavior where appropriate. For normal-sized inputs below about `15*pi`, the code uses table-based argument reduction through `PITBL`, computing `N*pi/2` split into leading and trailing pieces. For larger finite inputs, `SREDUCEX` and `REDUCEX` implement iterative high-precision reduction using scaled `2/pi`, `pi/2` leading/trailing pieces, and a two-part remainder `(R,r)`.

Sine and cosine use polynomial coefficients `SINA*` and `COSB*`, choosing sine or cosine polynomial by quadrant and applying sign by manipulating sign bits in scratch memory. `ssincos` computes both polynomials in one path and stores cosine through `sto_cos`, which is outside this chunk. Tangent uses a rational approximation with `TANP*` and `TANQ*`; odd quadrants return `-cot(r)` by dividing the denominator by a sign-flipped numerator.

### Inverse Trigonometric Functions

`satan` uses three regimes. For `1/16 <= |x| < 16`, it constructs a nearby table value `F` from the exponent and leading fraction bits, computes `u = (x-F)/(1+xF)`, fetches `atan(F)` from `ATANTBL`, and adds a short polynomial in `u`. Small inputs use an odd polynomial directly; very large inputs compute `sign*pi/2 + atan(-1/x)` or return `pi/2 - tiny` for huge magnitudes.

`sasin` computes `atan(x / sqrt((1-x)(1+x)))` for `|x| < 1`, returns signed `pi/2` for `|x| == 1`, and raises operand error for `|x| > 1`. `sacos` computes `2*atan(sqrt((1-x)/(1+x)))`, returns zero for `x == 1`, returns `pi` for `x == -1`, and raises operand error outside the domain.

### Exponentials And Powers

`setox` implements `exp(x)` by reducing `x` to `N * log2/64 + R`, indexing `EEXPTBL` for `2**(J/64)`, evaluating a polynomial for `exp(R)-1`, and reconstructing with a generated scale factor `2**M`. Extreme inputs split the scale into `SCALE` and `ADJSCALE` to avoid premature overflow/underflow; too-large values branch to overflow/underflow helpers. `setoxm1` implements `exp(x)-1` with separate algorithms for medium, small, tiny, and very large negative inputs, preserving accuracy near zero using a dedicated polynomial and `-2**(-M)` reconstruction term.

`stwotox` and `stentox` share the `expr` reconstruction path. `stwotox` reduces base-2 powers by rounding `64*x`; `stentox` multiplies by `64*log10/log2` and then converts the residual with natural log constants. Both use `TEXPTBL`, scale exponents split into `M` and `M'`, and the same `exp(R)-1` polynomial before final multiplication by `ADJFACT`.

### Hyperbolic Functions

`scosh` computes `(exp(|x|) + 1/exp(|x|))/2` for ordinary inputs and uses `|x| - 16381*log2` with `TWO16380` for near-overflow cases. `ssinh` computes `sign(x) * (z + z/(1+z))/2` with `z = expm1(|x|)` for ordinary inputs and similarly scales near-overflow results. `stanh` has three regimes: an `expm1(2|x|)` formula for ordinary inputs, an `exp(2|x|)` formula for larger inputs, and signed `1 - tiny` for huge inputs.

`satanh` computes `sign(x) * 0.5 * log1p(2|x|/(1-|x|))` inside the domain, raises divide-by-zero for `|x| == 1`, and operand error for `|x| > 1`.

### Logarithms

`slogn` implements natural log. Near one it uses `u = 2(x-1)/(x+1)` and an odd polynomial. Otherwise it decomposes `x = 2**k * y`, selects a 7-bit table approximation `F`, multiplies by a table-stored `1/F`, evaluates `log(1+u)`, and reconstructs `k*log2 + log(F) + poly`. `slognd` normalizes denormal input manually with `bfffo` and adjusts `k` before re-entering the normal path.

`slognp1` returns tiny arguments directly, otherwise forms `1+x` and chooses between the near-one odd polynomial and the table-driven log path. It has a special careful path for `1+x` in `[1/2, 3/2]` to preserve extra information in `x`. `slog10`/`slog10d` and `slog2`/`slog2d` call natural log then multiply by reciprocal constants; `slog2` has an exact fast path for positive powers of two.

### Getexp, Getman, Scale, Mod, And Remainder

`sgetexp` strips the extended exponent bias and returns it as an extended number; denormals are normalized before exponent extraction. `sgetman` rewrites the exponent to produce a mantissa in `[1,2)` while preserving sign, with a denormal path through `norm`.

`sscale` truncates the source to an integer scale factor, applies it to the destination by synthesizing an extended power-of-two multiplier, and handles denormal destinations and extreme source exponents through normalization or overflow/underflow helpers.

`smod` and `srem` share `Mod_Rem`. They manually normalize operands, strip signs, perform a binary shift/subtract remainder loop, accumulate the quotient bits for `FPSR_QBYTE`, and handle IEEE remainder tie-to-even behavior. The result sign is restored from the destination operand; optional rescaling uses a tiny `Scale` constant and `t_catch2` to surface underflow/rounding.

## Dependencies And Integration Points

This chunk depends on:

- m68k assembler syntax, FPU registers, `fmovm`, `fmov`, `fadd`, `fmul`, `fdiv`, `fsqrt`, `fintrz`, `ftest`, and bit-field instruction `bfffo`.
- Internal helper labels defined after line 9821, including exception handlers, zero/infinity/NaN loaders, `src_qnan`, `dst_qnan`, `src_zero`, `src_inf`, `src_one`, `ld_pone`, `ld_pzero`, `spi_2`, `sto_cos`, `sop_sqnan`, `smod_*`, `srem_*`, `sscale_*`, `norm`, and `unnorm_fix`.
- The public branch table at the beginning; external callers branch into those slots rather than calling C symbols directly.
- Saved `FPCR/FPSR` layout and exception status conventions. Several routines intentionally perform one final FPU instruction after restoring user FPCR so rounding and exception flags match hardware semantics.

There is no persistent storage beyond the current stack frame and FPU status registers. All constants are embedded read-only tables in the assembly stream.

## Risks And Maintenance Notes

- The wrappers duplicate large amounts of dispatch code. A one-line mistake in an offset, special-case branch, or restore mask can affect only one precision variant and be hard to spot.
- Many routines rely on exact stack layout and paired pushes/pops of FPU extended values. Any assembler syntax or ABI translation mistake can corrupt return state.
- The chunk boundary falls immediately before the exception helper implementations. Reviewing this chunk alone cannot prove correct exception enable, accrued-bit, qNaN, denormal result, or unnormalized operand behavior.
- Mathematical accuracy depends on table constants, split constants, and last-instruction exception sequencing. Refactoring or reassembling with a different assembler must preserve constant widths and instruction sizes.
- `tag` currently treats all NaNs as `QNAN` in this range; signaling NaN behavior appears to be completed by later exception/helper code, so tests must cover end-to-end behavior rather than `tag` alone.
- `smod`/`srem` manually manipulate quotient bits and tie cases; quotient sign and low seven bits in `FPSR_QBYTE` are a likely regression point.

## Test Signals

Useful validation signals include:

- Entry-wrapper ABI tests for every single/double/extended exported label: saved integer/FPU registers restored, `fp0`/`fp1` return conventions honored, and user `FPCR/FPSR` restored with expected exception bits.
- Special values for each function: signed zero, denormal, normal, infinity, qNaN/signaling NaN if supported by the later helper code, and unnormalized extended encodings.
- Accuracy sweeps around threshold boundaries used in integer compact comparisons: `2**(-40)`, `15*pi`, `1/16`, `16`, `1`, `1/4`, `2**(-65)`, `70*log2`, `16380*log2`, `16480*log2`, `(5/2)*log2`, and `50*log2`.
- Argument-reduction stress tests for very large trig/tan inputs, including the `0x7ffeffff` compact-form path.
- `log`, `log1p`, `expm1`, `asin`, `acos`, and `atanh` domain-edge tests around `-1`, `0`, `1`, and values one ulp inside/outside the domain.
- `fmod`/`frem` tests for exact multiples, `R == Y/2` tie-to-even quotient cases, denormal operands, negative operands, and quotient byte sign/low-bit encoding.
- `fscale` tests where source scale is just inside/outside `2**14`, destination is normal versus denormal, and scaling crosses into denormal, zero, overflow, or underflow.
