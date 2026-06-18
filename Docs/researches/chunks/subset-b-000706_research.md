# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/fplsp.S lines 9822-10980

## Scope

This chunk covers the shared helper tail of Motorola's 68060 floating-point library support package assembly file. The range starts at `t_dz`, the divide-by-zero exception helper used by logarithm and inverse-hyperbolic-tangent emulation, and ends at `unnorm_fix`, the helper that converts an extended-precision unnormalized operand into a normalized, denormalized, or zero representation.

The code in this chunk is not one independent algorithm. It is a collection of exported branch targets used by the earlier transcendental, remainder/modulo, scale, and native-instruction entry points in `fplsp.S`. It provides:

- Exception synthesis for divide-by-zero, operand error, underflow, overflow, and inexact result paths.
- Shared special-value result loaders for signed zero, signed infinity, signed one, signed pi/2, and quiet NaNs.
- `fsincos`, `fmod`, `frem`, and `fscale` special-case dispatch helpers.
- Native 68060 convenience entry points for add, subtract, multiply, divide, absolute, negate, square root, integer-round, and truncate-to-integer operations in single, double, and extended formats.
- Mantissa normalization helpers for extended-precision denormal and unnormalized operands.

The chunk depends on definitions near the top of the file for the local variable frame offsets (`USER_FPCR`, `USER_FPSR`, `FPSR_CC`, `FPSR_EXCEPT`, `FPSR_QBYTE`, `FP_SCR0`, `SRC`, `DST`, `LOCAL`, and `FTEMP`), operand type tags (`NORM`, `ZERO`, `INF`, `QNAN`, `DENORM`, `UNNORM`), and FPCR/FPSR bit masks (`dzinf_mask`, `opnan_mask`, `unfinx_mask`, `ovfinx_mask`, `ovfl_inx_mask`, `inx2a_mask`, `neg_mask`, `z_bmask`, `inf_bmask`, and `nan_bmask`).

## Purpose

The purpose of this chunk is to centralize architectural floating-point edge behavior for the 060FPLSP software package. Earlier emulation routines compute the main transcendental or dyadic result, then branch into these labels when the input class or final result requires a precise Motorola 68060-style exception, condition code, or special value.

The helpers deliberately distinguish between setting software-visible FPSR bits and causing an actual hardware FPU exception. If a relevant exception is disabled in the user's FPCR, the helper returns the IEEE default value directly, such as signed infinity for divide-by-zero or a quiet NaN for operand error. If the exception is enabled, the helper restores the user's FPCR and performs a small synthetic floating-point operation on a scratch FP register so the processor raises/logs the exception while the intended result register is preserved.

This chunk also supplies the branch-table targets for native operations that the 68060 already supports. Those wrappers make the large library entry table complete for systems that expect every operation to have an exported routine even when no full software emulation is needed.

## Important APIs, Types, And Entry Points

### Exception Helpers

`t_dz` and `t_dz2` handle divide-by-zero cases. `t_dz` derives the sign from the source operand at `SRC_EX(%a0)`. `t_dz2` is the negative-result entry used by paths such as `fatanh`. Both update `USER_FPSR` with divide-by-zero and infinity bits, plus the negative bit for negative results. If the divide-by-zero enable bit in `FPCR_ENABLE(%a6)` is clear, they return `+INF` or `-INF` in `fp0`. If it is set, they restore saved `fp0` from `EXC_FP0(%a6)`, load the user's FPCR, and divide `+1` or `-1` by zero in `fp1` to raise the real exception.

`t_operr` handles operand errors. It sets NAN, OPERR, and accrued illegal-operation bits in `USER_FPSR`. With OPERR disabled, it returns the local `qnan` constant in `fp0`. With OPERR enabled, it restores `fp0`, loads the user's FPCR, saves `fp2`, computes `+INF * 0` in `fp2` to raise the operand error, restores `fp2`, and returns.

`t_unfl` and `t_unfl2` synthesize underflow with inexact. `t_unfl` chooses the sign from the source operand; `t_unfl2` is the always-positive/dyadic entry comment-wise, although the visible body at this entry sets the negative-bit path because `t_unfl` falls into it for negative source operands. The negative path multiplies `mns_tiny` by `pls_tiny`, while the positive path squares `pls_tiny`. Both load `USER_FPCR` into `%fpcr`, collect the hardware `%fpsr`, rotate condition-code bits into byte position, and store them in `FPSR_CC(%a6)`.

`t_ovfl`, `t_ovfl2`, and `t_ovfl_sc` synthesize overflow with inexact handling. `t_ovfl` selects sign from the source operand and multiplies huge extended constants. `t_ovfl2` is the positive-result dyadic entry. `t_ovfl_sc` is the `fscale`-specific overflow path: it first sets overflow/accrued bits without forcing `INEX2`, inspects the user's requested rounding precision from `%d0`, and for single or double precision normalizes a scratch copy of the destination mantissa to decide whether low bits imply inexactness. Only then does it set `inex2_mask` before falling into the common overflow work.

`t_catch` and `t_catch2` merge the live hardware `%fpsr` into `USER_FPSR` after an earlier final floating-point instruction has already produced overflow, underflow, or inexact status. `t_catch2` immediately falls into `inx2_work`; `t_catch` also falls through because the next complete block is the inexact handler.

`t_inx2`, `t_pinx2`, and `t_minx2` handle inexact-result signaling. `t_inx2` branches based on the current FPU condition (`fblt` for negative, `fbeq` for zero). Positive and negative paths set `INEX2/AINEX`, with the negative path also setting the negative condition bit in `USER_FPSR`. If inexact is enabled, `inx2_work` loads the user's FPCR and adds `pls_tiny` to `+1` in `fp1` to cause the inexact event. If the result is exactly zero, `inx2_zero` only marks the zero condition code and inexact/accrued-inexact bits, without synthesizing a floating instruction.

`t_extdnrm` and `t_resdnrm` handle denormal operands by loading the extended source operand through an FPU move, allowing enabled denormal/underflow behavior to be observed. `t_extdnrm` additionally ORs in `unfinx_mask`; `t_resdnrm`, used by `fscale` and related result-denormal handling, preserves only the hardware `%fpsr` contribution.

### Special Result Helpers

`dst_qnan` and `src_qnan` return the destination or source quiet NaN, respectively, in `fp0`. They set the FPSR condition-code byte to NAN and include the negative condition bit if the operand sign bit is set.

`src_zero`, `dst_zero`, `ld_pzero`, and `ld_mzero` return signed zero and set `FPSR_CC` to zero, with negative-zero paths setting both negative and zero condition-code bits.

`src_inf`, `dst_inf`, `ld_pinf`, and `ld_minf` return signed infinities and set `FPSR_CC` to infinity, with negative-infinity paths setting both negative and infinity bits.

`szr_inf` is used by exponential functions: negative source operands map to `+0`, positive source operands map to `+INF`.

`sopr_inf` is used by logarithm-family functions: positive infinity returns `+INF`, while negative infinity branches to `t_operr`.

`setoxm1i` is used by `fetoxm1`: negative infinity returns `-1`; positive infinity returns `+INF`.

`src_one`, `ld_pone`, and `ld_mone` return signed one according to source sign. Positive one clears `FPSR_CC`; negative one sets the negative condition bit.

`spi_2`, `ld_ppi2`, and `ld_mpi2` return signed pi/2 using local extended constants `ppiby2` and `mpiby2`. These paths load `%fpcr` from `%d0`, move the constant to `fp0`, and branch to the positive or negative inexact helper because pi/2 is represented as an inexact rounded constant.

### `fsincos`, `fmod`, `frem`, And `fscale` Dispatch Helpers

`sto_cos` is an intentionally empty hook used by `fsincos`; the sine and cosine values are already in `fp0` and `fp1`, so the helper returns immediately.

`ssincosz` handles zero input for `fsincos`: it sets cosine (`fp1`) to `+1` and returns a same-sign zero sine in `fp0`.

`ssincosi` handles infinity input for `fsincos`: it writes QNaN to `fp1` and branches to `t_operr`.

`ssincosqnan` copies the source/local NaN to `fp1` and then uses `src_qnan` for the sine/result path.

`smod_sdnrm`, `smod_snorm`, `smod_szero`, and `smod_sinf` dispatch `fmod` special cases based on destination tag `DTAG(%a6)`. Normal and denormal source paths go to `smod` for normal/denormal destinations, return signed zero for zero destinations, raise operand error for infinity destinations, or return destination QNaN. Zero-source paths are operand errors unless the destination is a QNaN. Infinity-source paths allow finite/denormal destination handling via `smod_fpn`, zero destination via `smod_zro`, and reject infinity destinations.

`srem_sdnrm`, `srem_snorm`, `srem_szero`, and `srem_sinf` mirror the same dispatch pattern for `frem`, branching to `srem`, `srem_zro`, `srem_fpn`, `t_operr`, or `dst_qnan`.

`smod_zro` and `srem_zro` compute `FPSR_QBYTE` sign from source-sign XOR destination-sign and return signed zero according to destination sign.

`smod_fpn` and `srem_fpn` also compute quotient-byte sign, then either route denormal destinations through `t_resdnrm` or load the destination operand into `fp0` with the caller's FPCR. A negative destination sets the negative condition code.

`sscale_snorm`, `sscale_sdnrm`, `sscale_szero`, and `sscale_sinf` dispatch `fscale` special cases. Normal, zero, and denormal source classes run `sscale` when destination is normal/denormal, return signed destination zero/infinity for those destination tags, or return destination QNaN. Infinity source raises operand error unless the destination is QNaN.

`sop_sqnan` chooses which QNaN wins when the source is QNaN in dyadic special-operand processing: destination QNaN is returned if `DTAG` says QNaN, otherwise the source QNaN is returned.

### Native Instruction Support

The `_fadds_`, `_faddd_`, `_faddx_`, `_fsubs_`, `_fsubd_`, `_fsubx_`, `_fmuls_`, `_fmuld_`, `_fmulx_`, `_fdivs_`, `_fdivd_`, and `_fdivx_` labels expose native arithmetic operations. The single and double wrappers temporarily save `%fpcr`, clear it for the operand load so loading the destination does not itself run under user exception state, restore `%fpcr`, then perform the arithmetic using the source stack argument. The extended-format wrappers load the extended destination via `fmovm.x` and perform the operation directly.

The `_fabss_`, `_fabsd_`, `_fabsx_`, `_fnegs_`, `_fnegd_`, `_fnegx_`, `_fsqrts_`, `_fsqrtd_`, `_fsqrtx_`, `_fints_`, `_fintd_`, `_fintx_`, `_fintrzs_`, `_fintrzd_`, and `_fintrzx_` labels are one-instruction wrappers around the native FPU operation for the requested input width.

### Normalization Helpers

`norm` normalizes the mantissa of an extended-precision memory operand pointed to by `%a0`. It saves `%d2` and `%d3`, loads the high and low mantissa longwords, uses `bfffo` to find the first set bit, shifts the combined 64-bit mantissa left so the first set bit moves into normalized position, stores the adjusted high/low mantissa words, returns the shift count in `%d0`, and restores scratch registers. If the high mantissa longword is zero, `norm_lo` shifts the low word into the high word, clears the low word, and returns a shift count offset by 32.

`unnorm_fix` converts an unnormalized extended operand into a correct operand class. It finds the shift count needed to normalize the mantissa. If both mantissa words are zero, it preserves only the sign bit in the exponent word and returns `ZERO`. Otherwise it compares the needed shift against the current unbiased exponent. If the exponent can absorb the normalization shift, it subtracts the shift from the exponent while preserving sign, calls `norm`, and returns `NORM`. If the shift would push the exponent below zero, it denormalizes only as far as exponent zero, rewrites the mantissa into denormal form, preserves the sign bit, and returns `DENORM`.

## Control Flow

Most labels are branch targets rather than call-only subroutines. Earlier code reaches them with `bsr`, `bra`, or conditional FPU branches after classifying source and destination operands.

Exception-helper control flow generally follows the same pattern:

1. Set or merge expected FPSR bits in the saved user status block at `USER_FPSR(%a6)`.
2. Check the relevant exception-enable bit in `FPCR_ENABLE(%a6)` when the exception may need to trap.
3. If disabled, return the architectural default result directly in `fp0`.
4. If enabled, restore or preserve the intended result, load `USER_FPCR(%a6)` into the hardware `%fpcr`, and execute a controlled floating-point operation that raises the same exception class on a scratch register.

Special-result helpers are more direct. They inspect sign bytes in `SRC_EX(%a0)` or `DST_EX(%a1)`, load literal IEEE single-precision encodings or local extended constants into `fp0`/`fp1`, update only the FPSR condition-code byte needed by the caller, and return or tail-branch into another helper.

The modulo/remainder/scale dispatch helpers form tag matrices. They use the destination operand type tag `DTAG(%a6)` to select the correct finite operation, special return, operand error, or NaN propagation path for each source tag entry label. This keeps the earlier public entry wrappers compact: wrappers classify operands, then branch into one of these per-source-class dispatch labels.

`norm` and `unnorm_fix` mutate the operand structure in place. Their control flow is bit-position driven: find the first one bit, choose high-word or low-word handling, adjust exponent when possible, and otherwise generate a denormal or zero.

## State And Persistence Behavior

There is no persistent filesystem, kernel object, or Ceph state in this chunk. All state is CPU/FPU register state, stack state, and the exception frame/local-variable block addressed through `%a6`.

State modified by this chunk includes:

- `USER_FPSR(%a6)`, including condition codes, exception status bits, accrued exception bits, and quotient byte.
- Hardware `%fpcr` and `%fpsr`, usually restored from `USER_FPCR(%a6)` before synthetic exception operations.
- Floating-point registers `fp0`, `fp1`, and sometimes `fp2`. `fp0` is the primary return register; `fp1` is also an `fsincos` cosine result register and is used for inexact/DZ synthetic operations. `fp2` is saved and restored around operand-error synthesis.
- Operand memory pointed to by `%a0` for `norm` and `unnorm_fix`; those routines rewrite mantissa and, for `unnorm_fix`, exponent fields.
- `FPSR_QBYTE(%a6)` for `fmod`/`frem` quotient sign.
- The stack, for short-lived saves of `%fpcr`, `%fp2`, `%d0`, `%d1`, `%d2`, `%d3`, and `%a0`.

Because the helpers intentionally raise hardware FPU events when user FPCR enables them, their behavior is externally observable by the operating system exception machinery even though the source file is just a library routine. That is the main persistence-like side effect: exception status becomes part of the saved user FPU state and may be logged or delivered by the host 68060 exception path.

## Dependencies And Integration Points

This chunk depends on the Motorola 68k/68060 assembler syntax and FPU instruction set, including `fmov`, `fmovm.x`, `fadd`, `fsub`, `fmul`, `fdiv`, `fabs`, `fneg`, `fsqrt`, `fint`, `fintrz`, FPU conditional branches (`fblt`, `fbeq`), and bit-field instructions (`bfffo`, `bfextu`).

Internal dependencies within `fplsp.S` include:

- The local frame layout and operand offsets defined near the top of the file.
- `qnan`, `pls_huge`, `mns_huge`, `pls_tiny`, `mns_tiny`, `ppiby2`, and `mpiby2` constants.
- Main algorithm labels outside this chunk, such as `smod`, `srem`, and `sscale`.
- Earlier operand classification logic that writes `STAG`/`DTAG` and passes `%a0`, `%a1`, `%d0`, and `%a6` according to this file's calling convention.
- Earlier `is_unnorm_x` classification immediately before this range, which calls `unnorm_fix`.

External integration points are the public branch-table entries at the top of `fplsp.S`, including both transcendental function emulation entry points and native operation wrappers. The assembly lives under the Linux/Ceph source import path for m68k 68060 support, so practical integration is with architecture-specific kernel or low-level compatibility builds that still include Motorola's FPSP/FPLSP package.

## Risks And Edge Cases

The exception helpers are sensitive to exact FPCR/FPSR bit placement. A wrong mask, byte offset, or operand size would silently report the wrong exception class or condition code to callers.

Several routines rely on the sign bit being available in the first byte of an extended operand (`SRC_EX` or `DST_EX`). Any caller that passes a pointer to a differently packed operand will return the wrong signed zero, infinity, NaN condition, quotient sign, overflow sign, or underflow sign.

Synthetic exception generation deliberately uses scratch FP registers. `t_operr` saves/restores `fp2`, but divide-by-zero and inexact paths use `fp1`; callers must treat `fp1` as volatile unless the path's contract explicitly preserves it. This is especially important around `fsincos`, where `fp1` can also carry cosine.

The single and double native arithmetic wrappers use stack offsets after pushing `%fpcr`. Their argument offsets depend on the exact 68k calling convention and return-address layout. Any ABI wrapper change would need to revalidate the `0x8(%sp)` and `0xc(%sp)` accesses.

`t_ovfl_sc` has precision-specific inexact detection for denormal destination scaling. It copies and normalizes the operand to avoid altering the caller's original value, but it temporarily replaces `%a0` with `FP_SCR0(%a6)` and relies on the `movm.l` save/restore masks being correct.

`norm` assumes the operand is not already normalized and that at least one mantissa bit is set on paths that enter `norm_hi` or `norm_lo`. `unnorm_fix` checks for all-zero mantissas before normalization, but other direct callers of `norm` must uphold the nonzero-denormal expectation.

The `unnorm_fix` exponent comparison is subtle because it decides whether subtracting the normalization shift keeps the operand normalized or forces denormalization to exponent zero. Off-by-one errors here would change operand class at the normal/denormal boundary, which is a high-risk IEEE-754 compatibility issue.

Some comments contain historical wording or typos, and one visible condition comment in `unnorm_fix` appears inverted relative to the branch mnemonic. The assembly behavior, not the prose, should be treated as authoritative when validating boundary cases.

## Test Signals

High-signal validation for this chunk would include assembler/build checks for the m68k 68060 target so that all exported labels, bit-field instructions, FPU instructions, and addressing modes assemble correctly.

Functional tests should exercise special-value entry points through the public math wrappers rather than only calling helpers directly:

- Logarithm-family zero and negative inputs should route through `t_dz`, `t_dz2`, `sopr_inf`, or `t_operr` and produce correct infinity, NaN, and FPSR exception/accrued bits with FPCR exceptions both enabled and disabled.
- Overflow and underflow cases in exponential, hyperbolic, and `fscale` emulation should verify returned sign, condition codes, `OVFL/UNFL/INEX2` status, and accrued exception bits.
- Inexact paths should cover positive, negative, and zero results, including pi/2 returns from inverse trigonometric special cases.
- Denormal input/result cases should cover `t_extdnrm`, `t_resdnrm`, `norm`, and `unnorm_fix`, especially all-zero mantissas, high-word-only mantissas, low-word-only mantissas, and exponent values at the normal/denormal boundary.
- NaN propagation tests should verify source-vs-destination QNaN selection for monadic and dyadic paths, including negative NaN condition-code handling.
- `fsincos` zero, infinity, and QNaN cases should check both `fp0` sine and `fp1` cosine outputs.
- `fmod` and `frem` special cases should verify quotient-byte sign from source XOR destination sign and correct operand-error behavior for zero or infinity combinations.
- Native instruction wrapper tests should confirm stack argument layout for single, double, and extended variants and ensure that clearing `%fpcr` for destination loads does not suppress the intended exception behavior of the subsequent arithmetic operation.

Regression evidence should include comparison against known Motorola 68060 FPSP behavior or hardware traces when available, because many failures in this chunk are not ordinary value mismatches but incorrect exception timing, accrued-bit state, or condition-code state.
