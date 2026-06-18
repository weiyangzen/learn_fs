# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/fpsp.S lines 7887-16684

## Scope

This chunk covers a large middle section of the Motorola 68060 FPSP assembly source. It starts at the tail of a previous hyperbolic sine path and then covers:

- Transcendental kernels and denormal variants for `tanh`, natural log, `log1p`, `atanh`, `log10`, `log2`, `2**x`, `10**x`, and `fmovcr` ROM constants.
- The `fscale`, `fmod`, and `frem` implementations and their source/destination type dispatch wrappers.
- Shared default-result and exception helpers for divide-by-zero, operand error, denormal returns, underflow, overflow, inexact status, NaN propagation, infinities, zeros, ones, and `pi/2`.
- The second-level unsupported-instruction dispatch table that maps decoded FPU opcodes to emulation entry points.
- Core arithmetic emulators for `fmul`, `fdiv`, `fneg`, `ftst`, `fint`, `fintrz`, `fabs`, `fcmp`, `fsglmul`, `fsgldiv`, `fadd`, `fsub`, and `fsqrt`.
- Shared scaling helpers for arithmetic exception avoidance and the beginning of `_fdbcc` conditional-branch emulation through the start of the IEEE-aware test section.

The range is hand-written 68k/FPU assembly for the m68k 68060 floating-point support package, not filesystem logic. It is still relevant to the source tree because the Ceph client snapshot includes this architecture support code.

## Purpose

The code emulates 680x0 floating-point operations and transcendental instructions that are unsupported, exceptional, or need software correction on 68060-class hardware. It receives decoded operand descriptors and scratch areas through the FPSP exception frame anchored at `%a6`, uses `%a0` and `%a1` as source/destination operand pointers, and returns the default result in `%fp0`; when a trapped exceptional operand is required, many paths also return an EXOP in `%fp1`.

The transcendental routines implement numerically controlled approximations using table reduction, polynomial evaluation, and explicit rounding-mode restoration. The arithmetic routines use real FPU instructions on scaled operands where possible, then reconstruct exponent ranges and synthesize IEEE exception results when the original operation would overflow, underflow, divide by zero, signal invalid operation, or propagate NaNs.

## Important APIs, Types, And Functions

The callable labels in this chunk are the effective API. `stanh`/`stanhd`, `slogn`/`slognd`, `slognp1`/`slognp1d`, `satanh`/`satanhd`, `slog10`/`slog10d`, `slog2`/`slog2d`, `stwotox`/`stwotoxd`, and `stentox`/`stentoxd` are normalized/denormalized transcendental entry points. They expect an extended-precision input at `%a0` and the saved user FPCR rounding/precision bits in `%d0`.

`smovcr` implements the 68881/68882 `fmovcr` constant ROM behavior. It decodes a ROM offset in `%d1`, maps valid offsets to PI, small constants such as `log10(2)`, `e`, `log2(e)`, `log10(e)`, and larger constants such as `ln(2)`, `ln(10)`, and powers of ten, then chooses rounding tables for RN, RP, or RZ/RM. For non-extended precision it calls `_round` with `FP_SCR1`.

`sscale`, `smod`, and `srem` implement dyadic operations using `%a0` as source and `%a1` as destination. Their wrappers (`sscale_snorm`, `smod_szero`, `srem_sinf`, etc.) dispatch by `STAG(%a6)` and `DTAG(%a6)` to handle normals, zeros, infinities, denormals, QNaNs, and SNaNs before entering the core algorithm.

Shared exception/default-result helpers include `t_dz`, `t_dz2`, `t_operr`, `t_resdnrm`, `t_extdnrm`, `t_unfl`, `t_unfl2`, `t_ovfl`, `t_ovfl2`, `t_ovfl_sc`, `t_catch`, `t_catch2`, `t_inx2`, `t_pinx2`, and `t_minx2`. They update `USER_FPSR(%a6)`, `FPSR_CC(%a6)`, and related exception/accrued masks, then load default results such as signed zero, infinity, quiet NaN, underflow result, overflow result, or EXOP.

`fgen_except` is the bridge from a trapped final transcendental instruction back into regular instruction emulation. It inspects the saved `fsave` frame, marks unsupported inputs as denormal if needed, stores `%fp0` as `FP_DST`, and dispatches to `fin`, `fadd`, or `fmul` depending on the last instruction opcode in `%d1`.

`tbl_unsupp` is the opcode-extension jump table used after instruction decode. It routes operations such as `fsinh`, `flognp1`, `fetoxm1`, `ftanh`, `fatan`, `fasin`, `fatanh`, `fsine`, `ftan`, `fetox`, `ftwotox`, `ftentox`, `flogn`, `flog10`, `flog2`, `fcosh`, `facos`, `fcos`, `fgetexp`, `fgetman`, dyadic arithmetic, `fsincos`, compare/test, single/double move/sqrt, abs/neg, and single/double arithmetic variants to their handlers.

The arithmetic emulators are `fmul`/`fsmul`/`fdmul`, `fdiv`/`fsdiv`/`fddiv`, `fneg`/`fsneg`/`fdneg`, `fin`/`fsin`/`fdin`, `ftst`, `fint`, `fintrz`, `fabs`/`fsabs`/`fdabs`, `fcmp`, `fsglmul`, `fsgldiv`, `fadd`/`fsadd`/`fdadd`, `fsub`/`fssub`/`fdsub`, and `fsqrt`/`fssqrt`/`fdsqrt`.

Important scratch/storage symbols are aliases into the FPSP local frame: `FP_SCR0`, `FP_SCR1`, `L_SCR1`, `L_SCR2`, `L_SCR3`, `USER_FPSR`, `FPSR_CC`, `FPSR_EXCEPT`, `FPCR_ENABLE`, `SRC_*`, `DST_*`, `STAG`, `DTAG`, `FP_SRC`, `FP_DST`, and `EXC_CMDREG`. The code treats them as persistent state for the current exception emulation only.

## Control Flow

The transcendental routines first classify magnitude and sign from the extended-precision representation, choose a numerically stable formula, compute under default extended precision with FPCR cleared when necessary, then restore the caller's `%d0` FPCR before the final operation. For example, `stanh` uses `expm1(2|x|)` for moderate inputs, `exp(2|x|)` for larger inputs, returns `x` for tiny values, and returns signed one minus a tiny epsilon for huge values. `slogn` uses a near-one odd polynomial or a table-driven `k*log2 + log(F) + log(1+u)` reconstruction; `slognp1` has extra care paths to preserve `1+z` precision around `[1/2, 3/2]`.

`stwotox` and `stentox` reduce the exponent to `N/64 + r`, split `N` into `64(M + M') + j`, fetch split `2**(j/64)` table entries from `TEXPTBL`, approximate `exp(r)-1`, and reconstruct with an adjustment factor. Small inputs return `1 + x`; large inputs branch to overflow or underflow helpers based on sign.

`smod` and `srem` normalize source and destination magnitudes into integer exponent/mantissa triples, iteratively subtract shifted divisors, accumulate quotient bits in `FPSR_QBYTE`, and then perform IEEE remainder tie handling. `srem` differs from `smod` by comparing the remainder against `Y/2` and adjusting on greater-than or exact-half/odd-quotient cases.

Arithmetic emulators follow a common pattern. They combine `DTAG` and `STAG` to index a per-operation jump table for special cases. For normal/denormal arithmetic, they copy operands into scratch slots, call `scale_to_zero_src`, `scale_to_zero_dst`, `scale_sqrt`, or `addsub_scaler2` so the hardware instruction can execute without immediate overflow/underflow, execute the real FPU operation with controlled FPCR/FPSR, merge hardware status into `USER_FPSR`, then restore the result exponent by subtracting the scale factor. Boundary cases branch to "may overflow" or "may underflow" paths, often re-executing with round-to-zero to determine whether the pre-rounded result was truly exceptional.

`_fdbcc` begins by saving the branch displacement, extracting the predicate from `EXC_CMDREG`, loading stacked FPSR condition codes into the hardware FPSR, and dispatching through `tbl_fdbcc`. The covered predicate handlers either return when the branch condition is true, call `fdbcc_false` to decrement/test the data register and apply the displacement, or set BSUN/AIOP when a NaN condition makes the predicate unordered and BSUN is relevant.

## State And Persistence Behavior

There is no durable filesystem or database persistence in this chunk. All state is per-exception, stored in registers, the stack, FPU registers, and the FPSP frame behind `%a6`.

The most important persistent-within-emulation state is `USER_FPSR(%a6)`, which accumulates condition codes, exception status, and accrued exception bits that must be written back to architectural state. `FPSR_CC(%a6)`, `FPSR_EXCEPT(%a6)`, `FPSR_QBYTE(%a6)`, and `FPCR_ENABLE(%a6)` are read or written throughout exception generation, quotient reporting, and branch-condition logic.

Operand type tags `STAG` and `DTAG` drive special-case dispatch. Source and destination extended operands live at `SRC(%a0)` and `DST(%a1)` or in copied scratch slots such as `FP_SCR0` and `FP_SCR1`. Denormal handling commonly normalizes a mantissa into scratch storage, tracks exponent adjustment in `%d0`, and may produce an EXOP in `%fp1` if the relevant trap is enabled.

The code intentionally saves and restores `%fpcr` around intermediate computations. Many transcendental paths force default extended precision/round-to-nearest for internal work and restore user precision/rounding for the final operation so IEEE result and inexact behavior match the original instruction.

## Dependencies And Integration Points

This file depends on the surrounding FPSP assembly definitions for operand layout macros, mask constants, type tags, condition-code bits, rounding-mode constants, and helper routines such as `_round`, `norm`, `unf_res`, `unf_res4`, `ovf_res`, `fdbcc_false`, `fdbcc_bsun`, `fetch_dreg`, and `store_dreg_l`. Some of those helpers are outside this chunk, so changes here must preserve their calling conventions.

Integration is through the m68k 68060 floating-point exception handler. Earlier decode code sets `%a6`, `STAG`, `DTAG`, `SRC`, `DST`, `EXC_CMDREG`, and FPCR/FPSR scratch state, then jumps into the entry points or `tbl_unsupp`. Later epilogue code consumes `%fp0`, optional `%fp1`, updated FPSR fields, and stack-frame flags.

The transcendental kernels call each other heavily: `stanh` depends on `setoxm1` and `setox`; `satanh` calls `slognp1`; `slog10`/`slog2` call `slogn`/`slognd`; power routines share the `expr` reconstruction path. Exception catchers use regular arithmetic emulators (`fin`, `fadd`, `fmul`) to synthesize results for final operations that trapped during a transcendental sequence.

## Risks And Edge Cases

This code is extremely sensitive to 68k stack layout, register preservation, condition code side effects, and PC-relative table offsets. Small edits can corrupt exception frames, return the wrong EXOP, or desynchronize opcode dispatch tables from instruction decode.

Magnitude thresholds and table constants are part of the numerical contract. The log, tanh, atanh, base conversion, exponential, and ROM-constant sections rely on carefully split constants, table indexing, and final-rounding decisions. Replacing them with simplified formulas would risk monotonicity, 68881/68882 compatibility, and the documented ulp bounds in comments.

The denormal paths are especially risky. Several functions return the input denormal while setting underflow/inexact, while arithmetic emulation normalizes denormals and conditionally returns an EXOP if traps are enabled. Confusing `t_extdnrm` with `t_resdnrm`, or using the wrong source/destination tag during `scale_to_zero_*`, changes visible exception behavior.

NaN and infinity precedence is encoded in jump tables and helper choices. Destination NaNs often take priority over source NaNs; SNaNs set `snan`/`aiop` bits; compare intentionally suppresses the negative condition-code bit for NaN inputs; infinity results sometimes preserve the original j-bit for 68881/68882 compatibility.

Boundary overflow/underflow paths depend on re-executing operations with alternate rounding modes. These paths are slower but necessary for correctly distinguishing rounded-normal from rounded-exceptional results near the smallest and largest representable values for extended, single, and double precision.

The `_fdbcc` section is only partially covered by this chunk; the IEEE-aware predicate handlers and the false/BSUN helper implementations continue after line 16684. Research for this chunk should therefore treat `_fdbcc` coverage as the setup and nonaware/miscellaneous predicate subset, not the complete branch instruction emulator.

## Test Signals

High-signal validation for this chunk is architecture/FPSP focused:

- Assemble this source for the expected m68k target and verify all PC-relative tables and labels resolve without relocation surprises.
- Run 68060 FPSP or emulator tests for `ftanh`, `flogn`, `flognp1`, `fatanh`, `flog10`, `flog2`, `ftwotox`, `ftentox`, and `fmovcr` across normal, tiny, huge, denormal, zero, infinity, QNaN, and SNaN inputs.
- Compare transcendental outputs against a high-precision reference with the documented ulp tolerances and check monotonicity for log/tanh/atanh/log10/log2.
- Exercise every rounding mode and precision field for ROM constants, underflow/overflow defaults, signed zero selection, `log2(2**k)` exactness, and final inexact-bit behavior.
- Test `fmod` and `frem` quotient byte/sign behavior, exact-divisor zero remainders, remainder half-tie cases, denormal operands, zero divisors, and infinity/NaN special cases.
- Test `fscale` with small source exponents, very large positive/negative source operands, normalized and denormal destinations, and trap-enabled underflow/overflow.
- Run arithmetic emulation cases for multiply, divide, add, subtract, move, neg, abs, sqrt, compare, integer conversion, and single-precision multiply/divide at exponent boundaries where "may overflow" and "may underflow" paths are selected.
- Verify NaN priority and status flags for dyadic operations, monadic operations, compare, source/destination SNaN combinations, and destination QNaN with source SNaN.
- Test `_fdbcc` predicates covered here with FPSR condition-code combinations for Z, N, I, and NAN, including BSUN-enabled and BSUN-disabled behavior.
