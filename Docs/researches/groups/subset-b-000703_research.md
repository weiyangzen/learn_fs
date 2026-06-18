# subset-b-000703 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/gen_except.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/gen_except.S

### Purpose
`gen_except.S` is the FPSP exception-reconciliation routine for Motorola 68040 floating-point emulation. It compares the user FPCR exception-enable byte with the FPSR exception-status byte accumulated by prior FPSP routines and decides whether to synthesize a reportable floating-point exception, silently complete the emulation, or rebuild an fsave frame so the kernel/user exception path can see the correct pending condition. The file is central to preserving IEEE exception priority after unimplemented or unsupported floating-point work has been emulated in software.

### Important APIs, Types, And Functions
The exported entry point is `gen_except`. It relies on `fpsp.h` frame offsets such as `USER_FPCR`, `USER_FPSR`, `FPSR_SHADOW`, `E_BYTE`, `CMDREG1B`, `CMDREG3B`, `ETEMP`, and FPU frame size constants including `IDLE_SIZE`, `UNIMP_40_SIZE`, `UNIMP_41_SIZE`, and `BUSY_SIZE`. Local dispatch labels include `exc_tbl`, `bsun_exc`, `commonE1`, `commonE3`, `ovfl_unfl`, `no_match`, `do_clean`, `do_restore`, `finish_up`, and `bug1384`. External integration labels are `real_trace`, `fpsp_done`, and `fpsp_fmt_error`.

### Control Flow
The routine first classifies the current fsave frame as idle, original unimplemented, revision unimplemented, or busy. Busy frames are patched with operand and command-register data from the previous unimplemented frame before exception processing continues. `do_check` intersects `FPCR_ENABLE` with `FPSR_EXCEPT`, scans the exception bits in priority order with `exc_tbl`, and routes to per-class handlers. BSUN, SNAN, OPERR, DZ, and INEX share the `commonE*` paths, while overflow and underflow use `ovfl_unfl` because IEEE requires inexact reporting if overflow is disabled and inexact is enabled. If no enabled exception matches, the routine either cleans the fsave state and returns through `fpsp_done` or preserves/restores a frame when unsupported-instruction state must be replayed.

### State, Persistence, And Dependencies
All state is stack-frame state, not persistent storage. The routine mutates the local FPSP frame, fsave frame bytes, `USER_FPSR`, `FPSR_SHADOW`, `CMDREG3B`, and exception-frame shape on `%sp`. It depends on Motorola 040 fsave layout semantics, on `fpsp.h` offsets, and on the surrounding FPSP handlers having populated exceptional operands in `ETEMP`/`FPTEMP` and status bits in `USER_FPSR`. It contains hardware-errata handling, including `bug1384`, which fixes certain 68040 mask revisions and idle-frame patterns.

### Integration Points
`gen_except` is called by emulation handlers after arithmetic, transcendental, or conversion code has set FPSR exception bits. It returns either to `fpsp_done` for handled operations, to `real_trace` if trace state must be reported, or to system exception handling after constructing an appropriate fsave frame. It shares contracts with `kernel_ex.S` `t_*` routines, result/store code that fills `USER_FPSR`, and the Linux-facing exception skeleton in `skeleton.S`.

### Risks
The main risk is wrong exception priority or wrong frame reconstruction. A bit-position mistake can report a lower-priority exception instead of BSUN/SNAN/OPERR/OVFL/UNFL/DZ/INEX, and incorrect busy/unimplemented frame copying can make `frestore` replay the wrong instruction. The frame-size checks are architecture-specific; relaxing them risks silent corruption, while overly strict checks can route valid CPU revisions to `fpsp_fmt_error`. Overflow/underflow plus inexact behavior is subtle and easy to regress.

### Test Signals
Useful validation includes m68k FPSP exception tests that toggle each FPCR enable bit, force simultaneous exception status bits, and verify the reported priority. Specific signals are correct handling of overflow-disabled/inexact-enabled cases, underflow-disabled/inexact-enabled cases, idle versus busy frame exits, trace returns, and no format errors for valid 68040 and 68040-revision fsave frames. Kernel boot or emulator tests should exercise unimplemented transcendental instructions with traps enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/gen_except.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/get_op.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/get_op.S

### Purpose
`get_op.S` decodes and normalizes operands for 68040 unsupported data/format and unimplemented instruction exceptions. It determines the instruction opclass, converts unnormalized and packed operands into the FPSP internal extended format, updates source/destination tags, and prepares the next module, typically `do_func` for unimplemented operations or `res_func` for unsupported data-format recovery.

### Important APIs, Types, And Functions
Exports are `get_op`, `uns_getop`, `uni_getop`, and rounding-sensitive constant tables `PIRN`, `PIRZRM`, `PIRP`, `SMALRN`, `SMALRZRM`, `SMALRP`, `BIGRN`, `BIGRZRM`, `BIGRP`, plus power-of-ten tables `PTENRN`, `PTENRM`, and `PTENRP`. Important internal helpers are `chk_dy_mo`, `mk_norm`, `unpack`, `fix_nan`, `move_unpack`, and `fix_stag`. It calls external `nrm_zero`, `decbin`, and `round`, and uses `fpsp.h` tags and fields such as `CMDREG1B`, `STAG`, `DTAG`, `ETEMP`, `FPTEMP`, `WBTEMP`, and `DY_MO_FLG`.

### Control Flow
`get_op` distinguishes unsupported and unimplemented entry paths, then branches on the opclass and move-out direction bits in `CMDREG1B`. Unsupported opclass 3 move-outs may pack a source operand immediately. Dyadic/monadic state is computed by `chk_dy_mo`. Extended, single, double, and packed operands flow through tag checks; unnormalized numbers are normalized with `mk_norm`, denormal tags are preserved for later handling, and packed decimal values are unpacked through `unpack` and `decbin`. The `fix_nan`/`move_unpack` path canonicalizes NaN, zero, normal, and infinity classifications and updates FPSR condition codes where fmove semantics require it.

### State, Persistence, And Dependencies
The routine mutates only the FPSP stack frame: source and destination tags, temporary operands, condition-code/status bytes, and scratch fields. The exported constant tables are read-only data consumed here and by `smovecr.S`. It depends on exact 68881/68882 opclass encodings carried in the 68040 command registers and on shared normalization semantics from `round.S`.

### Integration Points
The caller is the unsupported-format handler (`unsupp`, vector 55) or unimplemented-instruction handler (`unimp`, vector 11). Successful normalization feeds `do_func`, `res_func`, packed conversion helpers, or hardware replay through `frestore`. The move-constant implementation in `smovecr.S` uses the constant tables defined here, so table ordering and rounding variants are part of the local ABI.

### Risks
Risks cluster around tag accuracy and packed conversion. If `STAG`/`DTAG` is updated inconsistently with the actual temporary operand, later `res_func` or hardware replay will treat a denorm as normal or vice versa. Packed decimal unpacking depends on exact k-factor, sign, and exponent handling. The rounding-specific constants differ by one low bit in several entries; sharing the wrong table between RN/RZ/RM/RP changes required IEEE results.

### Test Signals
High-value tests include unsupported extended unnorm, single denorm, double denorm, packed move-in, packed move-out, and dyadic operations with only the source or destination denormalized. Compare output tags, saved operands, and FPSR condition codes before replay. FMOVECR tests should verify all constants under all four rounding modes because this file owns the canonical constant data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/get_op.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/kernel_ex.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/kernel_ex.S

### Purpose
`kernel_ex.S` provides helper routines that force FPSR status, condition codes, and default results for exceptional cases detected inside FPSP transcendental and arithmetic routines. Instead of immediately invoking OS traps, these helpers set the user FPSR/FPCR-facing state so `gen_except` can later decide whether the exception is enabled and reportable.

### Important APIs, Types, And Functions
Exports include `t_dz`, `t_dz2`, `t_operr`, `t_unfl`, `t_ovfl`, `t_ovfl2`, `t_inx2`, `t_frcinx`, `t_extdnrm`, `t_resdnrm`, `dst_nan`, `src_nan`, and `t_avoid_unsupp`. Static constants represent negative infinity, positive infinity, NaN, and huge finite extended values. External dependencies are `ovf_r_k`, `unf_sub`, and `nrm_set`. The code uses `USER_FPSR`, `FPCR_ENABLE`, `FPSR_CC`, `FPSR_EXCEPT`, `ETEMP`, `FPTEMP`, and scratch operands from `fpsp.h`.

### Control Flow
Each `t_*` entry handles one exception/result family. Divide-by-zero returns signed infinity when disabled or records enabled trap status when enabled. `t_operr` records invalid operation. Underflow and overflow paths inspect FPCR enable bits: disabled traps compute substitute rounded finite, zero, denormal, infinity, or huge results, while enabled traps preserve operands and mark status. `t_inx2` and `t_frcinx` set inexact/accrued bits. `dst_nan` and `src_nan` propagate NaNs and distinguish signaling from quiet NaNs. `t_extdnrm` and `t_resdnrm` normalize or underflow denormal results, and `t_avoid_unsupp` rewrites denormal operands to avoid repeated unsupported-data traps on hardware replay.

### State, Persistence, And Dependencies
The file mutates saved FPSR state and the temporary/result operand in the FPSP local frame. No persistent kernel state is kept. It depends on callers placing operands in `ETEMP` or `FPTEMP`, on FPCR enable bits being current, and on downstream `gen_except` interpreting the same FPSR status/accrued masks.

### Integration Points
Transcendental files call these helpers at exceptional boundaries: logs call `t_dz`/`t_operr`, trig/hyperbolic routines call `t_frcinx`, exp/cosh/scale call `t_ovfl`/`t_unfl`, and denorm-specific entries call `t_extdnrm` or `t_resdnrm`. `res_func.S` and lower-level underflow/overflow helpers also use the same result-normalization contract.

### Risks
The biggest risk is disagreement between result substitution and FPCR trap-enable state. Disabled traps must return the architecturally required value and set accrued bits; enabled traps must avoid corrupting the operand frame that will be reported. NaN propagation is another sensitive area because signaling NaNs must raise invalid operation while quiet NaNs generally propagate. `t_avoid_unsupp` touches nested fsave-frame state and can cause replay loops if it fails to recognize denorms correctly.

### Test Signals
Tests should run each exception helper with FPCR traps enabled and disabled and compare FPSR bits plus returned fp0/operand images. Useful cases are signed divide by zero, invalid operation from out-of-domain functions, overflow under each rounding mode, gradual underflow, denormal result normalization, quiet NaN propagation, signaling NaN invalid operation, and replay of denormal operands without an unsupported loop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/kernel_ex.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/res_func.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/res_func.S

### Purpose
`res_func.S` resolves unsupported data-format exceptions after operands have been decoded by `get_op`. Its core job is to normalize denormalized operands when that lets the 68040 replay and complete the instruction. It also implements the cases that cannot be replayed directly, notably packed move-out and several conversion/wraparound corner cases.

### Important APIs, Types, And Functions
Exports are `res_func` and `p_move`. Important internal regions are monadic/dyadic denorm handling, `wrap_div`, `wrap_add`, `wrap_sub`, `wrap_cmp`, `wrap_mul`, force-overflow/underflow paths, integer conversion helpers `li`, `wi`, `bi`, floating move-out helpers `xp`, `sgp`, `dp`, and packed output helpers `pack_out`, `p_movez`, `p_movei`, `p_moven`, `p_dyd0` through `p_dyd7`. External dependencies include `mem_write`, `bindec`, `get_fline`, `round`, `denorm`, `dest_ext`, `dest_dbl`, `dest_sgl`, `unf_sub`, `nrm_set`, `dnrm_lp`, `ovf_res`, `reg_dest`, `t_ovfl`, and `t_unfl`.

### Control Flow
`res_func` starts by clearing denorm/result flags and dispatches between dyadic destination handling, monadic source handling, and opclass 3 move-out. Denormal operands are converted into internal extended format, normalized with `nrm_set`, retagged, and usually written back so the hardware can retry. For operations that can generate wraparound or forced exceptions, opcode decoding routes through add/sub/mul/div/cmp-specific logic to decide whether to fix the stack, force overflow, force underflow, or finish in software. Move-out paths convert to integer or floating destination formats, check bounds (`sp_bnds`, `dp_bnds`), use rounding/denormal helpers, and call `mem_write` for memory destinations. Packed move-out routes through `bindec` and the `p_move*` dispatch tables.

### State, Persistence, And Dependencies
All mutable state is in FPSP local variables and the fsave frame: `DNRM_FLG`, `RES_FLG`, `CU_ONLY`, `DY_MO_FLG`, `STAG`, `DTAG`, `ETEMP`, `FPTEMP`, and scratch operands. It depends on `get_op.S` having tagged operands correctly and on `fpsp.h` command-register field definitions. Memory persistence occurs only when move-out instructions write to user memory through `mem_write`.

### Integration Points
The unsupported exception handler invokes `res_func` after `get_op`. Successful normalization flows back to hardware replay via the surrounding FPSP handler. Store and conversion flows integrate with `mem_write`, `reg_dest`, binary/decimal conversion, and destination-format routines. Exception generation is delegated to `kernel_ex.S` helpers and later `gen_except`.

### Risks
This is one of the densest FPSP files and has high regression risk. Small mistakes in tag transitions can produce repeated unsupported traps, incorrect replay, or corrupted user memory. Move-out conversion depends on destination size, rounding mode, signed range, and inexact/overflow status. Wraparound detection for arithmetic opcodes is highly branch-heavy and can easily force the wrong underflow/overflow behavior if command decoding changes.

### Test Signals
Tests should cover replay after source-only, destination-only, and both-operand denorms; packed decimal move-out to memory; integer byte/word/long conversion at boundaries; single/double/extended move-out under all rounding modes; denorm-to-zero and smallest-denorm results; arithmetic wrap cases for add, sub, mul, div, and cmp; and user-memory fault behavior through `mem_write`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/res_func.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/round.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/round.S

### Purpose
`round.S` supplies shared rounding, normalization, and denormalization primitives for the FPSP package. It rounds internal extended-format operands according to FPCR precision and rounding mode, extracts guard/round/sticky bits, normalizes mantissas, and constructs denormal results for underflow-sensitive code paths.

### Important APIs, Types, And Functions
Exports are `round`, `nrm_zero`, `nrm_set`, `denorm`, and `dnrm_lp`. The main caller contract for `round` is `%a0` pointing at an internal extended operand, `%d1` carrying precision in the high word and mode in the low word, and `%d0{31:29}` carrying guard/round/sticky bits. Internal tables `mode_tab`, `add_to_l`, and `trunct` dispatch by rounding mode or precision. It uses `USER_FPSR`, `LOCAL_EX`, `LOCAL_SGN`, `LOCAL_HI`, `LOCAL_LO`, `LOCAL_GRS`, and scratch space from `fpsp.h`.

### Control Flow
`round` first calls `ext_grs` to align guard/round/sticky bits for extended, single, or double precision. Exact results are truncated to the target precision. Inexact results set `inx2a_mask` in `USER_FPSR` and branch by rounding mode: toward plus/minus infinity conditionally increments based on sign, toward zero truncates, and round-to-nearest increments for guard-bit cases with tie-to-even behavior. `nrm_zero` and `nrm_set` shift mantissas and adjust exponents until normalized or zero. `denorm` and `dnrm_lp` shift a normalized internal value down to single/double/extended denormal thresholds while preserving sticky/inexact information.

### State, Persistence, And Dependencies
The routines mutate the operand at `%a0`, `%d0`/`%d1` scratch values, and inexact bits in `USER_FPSR`. There is no persistent state. All semantics depend on the internal extended operand layout and rounding constants in `fpsp.h`.

### Integration Points
The file is a shared dependency for `get_op.S`, `res_func.S`, `kernel_ex.S`, `sint.S`, `smovecr.S`, `scale.S`, and underflow helpers. It is also the normalization backend for denormal inputs and results throughout the FPSP tree.

### Risks
Rounding bugs are cross-cutting. A wrong guard/round/sticky extraction shifts all single/double results by one ulp, and tie-to-even mistakes show only on exact half-way cases. Denormalization must preserve sticky state across multiword shifts; losing it suppresses inexact/underflow flags. Carry propagation on increment can overflow the mantissa and must increment the exponent without dropping the hidden bit.

### Test Signals
High-signal tests include all four rounding modes, all three precisions, tie-to-even cases, carry-out from mantissa increment, exact truncation, inexact flag setting, zero normalization, leading-one normalization across high and low mantissa words, gradual underflow to denorm, catastrophic underflow to zero, and sticky-bit preservation for shifts greater than one word.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/round.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sacos.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sacos.S

### Purpose
`sacos.S` implements the 68040 FPSP `FACOS` transcendental operation. It computes arccosine for a double-extended input at `%a0`, returning the result in `%fp0`, with a separate denormal-input entry.

### Important APIs, Types, And Functions
Exports are `sacos` and `sacosd`. The file defines `PI` and `PIBY2` constants and depends on `t_operr`, `t_frcinx`, and `satan`. The caller supplies the input in FPSP extended format at `%a0`; `%d1` carries the user FPCR mode/precision as used by the surrounding transcendental framework.

### Control Flow
`sacosd` treats denormal input as an inexact arccosine of zero and returns `pi/2` through `t_frcinx`. `sacos` loads `X`, checks `|X|` against 1, and for the normal domain `|X| < 1` computes `z = (1 - X) / (1 + X)`, then calls `satan` on `sqrt(z)` and doubles the arctangent result. For `|X| == 1`, it returns zero for `+1` and `pi` for `-1`; for `|X| > 1`, it branches to `t_operr` for invalid operation.

### State, Persistence, And Dependencies
The routine uses `%fp0` and `%fp1`, temporarily overwrites the input slot at `%a0` before calling `satan`, and may save/restore FPCR state around the helper call. No persistent state is kept. It depends on `satan` accepting its input at `%a0` and on `kernel_ex.S` exception helpers setting FPSR state.

### Integration Points
`tbldo.S` dispatches normal and denormal `FACOS` opcodes to `sacos`/`sacosd`, while infinity and NaN special cases are generally filtered before entry. Results and exception bits flow back through `t_frcinx`/`t_operr` and then `gen_except`.

### Risks
The transformation `(1-X)/(1+X)` is sensitive near `X = -1` because the denominator approaches zero; boundary classification must be exact. The helper call changes FPCR behavior, so failure to restore user exception controls would leak state into later arithmetic. Domain errors for `|X| > 1` must generate invalid operation rather than returning a numeric value.

### Test Signals
Tests should cover `acos(+0)`, `acos(-0)`, `acos(+1)`, `acos(-1)`, values just inside and just outside `[-1,1]`, denormal inputs, and all rounding modes. Compare monotonicity and ulp error against a high-precision oracle, and verify invalid-operation status for out-of-domain inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sacos.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sasin.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sasin.S

### Purpose
`sasin.S` implements the FPSP `FASIN` operation for 68040 unimplemented transcendental emulation. It computes arcsine for a double-extended argument at `%a0` and returns `%fp0`, with a denormal-specific entry.

### Important APIs, Types, And Functions
Exports are `sasin` and `sasind`. It defines `PIBY2` and depends on `t_operr`, `t_frcinx`, `t_extdnrm`, and `satan`. The routine uses `%fp0` through `%fp2` for the transformation and temporarily stores the reduced argument back through `%a0` for the arctangent helper.

### Control Flow
`sasind` returns the denormal input via `t_extdnrm`, reflecting `asin(x) ~= x` with inexact/denormal handling. `sasin` checks `|X|` against 1. For `|X| < 1`, it computes `sqrt((1-X)(1+X))`, divides `X` by that value, stores the quotient as the new helper input, and calls `satan`. For `|X| == 1`, it returns signed `pi/2` and forces inexact. For `|X| > 1`, it branches to `t_operr`.

### State, Persistence, And Dependencies
State is limited to FPU temporaries, the `%a0` operand slot, and FPSR bits managed by exception helpers. It depends on exact extended-format exponent/sign tests and on `satan` for the final approximation.

### Integration Points
`tbldo.S` dispatches FASIN normal and denormal entries here, with invalid infinity cases routed to `t_operr`. Results feed the shared FPSP exception reporting path through `t_frcinx` or `t_extdnrm`.

### Risks
Accuracy near `|X| = 1` depends on the product `(1-X)(1+X)` not losing domain classification. Saving/restoring `%fp2` is required because the shared FPSP prologue preserves only selected registers for callers. Incorrect handling of signed `-1` would produce `+pi/2` instead of `-pi/2`.

### Test Signals
Test `asin(0)`, signed zero, denormal inputs, `+1`, `-1`, near-boundary values, and out-of-domain values. Check odd symmetry, monotonicity, inexact status, invalid-operation status for `|X| > 1`, and ulp accuracy in double-rounded results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sasin.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/satan.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/satan.S

### Purpose
`satan.S` implements the FPSP `FATAN` operation. It computes arctangent for normal inputs and delegates denormal input handling to the shared denormal helper, targeting a monotonic result within the file's documented ulp bounds.

### Important APIs, Types, And Functions
Exports are `satan` and `satand`. The file contains polynomial coefficients `ATANA*`, `ATANB*`, `ATANC*`, constants for `+/-pi/2` and tiny denorm proxies, and a large `ATANTBL` table of precomputed arctangent values. Scratch aliases map `X` and `ATANF` onto `FP_SCR1` and `FP_SCR2`. It depends on `t_frcinx` and `t_extdnrm`.

### Control Flow
`satand` handles denormal inputs through `t_extdnrm`. `satan` first classifies `|X|` into medium, small, big, and huge ranges. Medium inputs use table reduction: choose a nearby `F` from the leading bits of `X`, compute `u = (X-F)/(1+XF)`, approximate `atan(u)` with a polynomial, and add tabulated `atan(F)`. Small inputs use an odd polynomial directly in `X`. Big inputs compute in terms of `-1/X` and add signed `pi/2`; huge inputs return signed `pi/2` plus tiny inexact adjustment. All normal exits route through `t_frcinx`.

### State, Persistence, And Dependencies
The routine uses FPSP scratch float slots and FPU registers for temporary reductions; no persistent state is written. It assumes caller-provided `%a0` points to an extended operand and that exception helpers will record inexact status.

### Integration Points
`satan` is called directly for FATAN from `tbldo.S` and indirectly by `sasin.S` and `sacos.S`. Its range-reduction constants are internal ABI for those higher-level inverse trig functions, which store transformed inputs at `%a0` before calling it.

### Risks
The table index computation and sign/exponent manipulation are the major risk areas. A wrong selected `F` or sign restoration breaks monotonicity and can produce quadrant errors in the big-input path. Huge/tiny cases intentionally force inexact; removing those tiny adjustments would change FPSR behavior while leaving numeric results apparently correct.

### Test Signals
Test small, medium, large, and huge magnitudes, signed zeros, denormal input through `satand`, positive and negative values, and values near 1/16 and 16 branch boundaries. Verify odd symmetry, monotonicity, inexact signaling, and agreement with high-precision atan within the documented tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/satan.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/satanh.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/satanh.S

### Purpose
`satanh.S` implements the FPSP `FATANH` inverse hyperbolic tangent operation. It returns `atanh(X)` in `%fp0` for normal inputs and has a denormal entry that preserves the expected near-zero behavior.

### Important APIs, Types, And Functions
Exports are `satanh` and `satanhd`. It depends on `t_dz`, `t_operr`, `t_frcinx`, `t_extdnrm`, and `slognp1`. The main transformation uses FPU temporaries and stores the `log1p` helper argument through `%a0`.

### Control Flow
`satanhd` uses `t_extdnrm` because `atanh(x) ~= x` for denormal `x`. `satanh` computes `|X|` and branches for boundary cases. For `|X| < 1`, it forms `z = 2X/(1-X)` and calls `slognp1` to compute `log(1+z)`, then halves the result. For `|X| == 1`, it returns divide-by-zero behavior through `t_dz`; for `|X| > 1`, it raises invalid operation via `t_operr`. Normal finite results route through `t_frcinx`.

### State, Persistence, And Dependencies
No persistent state is used. The routine mutates the operand slot at `%a0` for the `slognp1` call and relies on shared FPSR exception helpers for status. It depends on `slognp1` implementing accurate log-one-plus behavior for transformed arguments.

### Integration Points
`tbldo.S` dispatches FATANH normal and denormal cases here. The routine composes with `slogn.S`, `kernel_ex.S`, and `gen_except` for math and exception reporting.

### Risks
Domain boundaries at `-1` and `+1` are critical: equality must produce divide-by-zero, while greater magnitude must produce invalid operation. The formula `2X/(1-X)` magnifies error near `X = 1`, so branch order and exact comparisons matter. Sign handling must be preserved through the log1p call.

### Test Signals
Test denormals, signed zeros, small values, values near `+/-1`, exact `+1` and `-1`, and out-of-domain values. Check odd symmetry, divide-by-zero status at exact endpoints, invalid-operation status outside the domain, and inexact status for normal nonzero results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/satanh.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/scale.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/scale.S

### Purpose
`scale.S` implements the FPSP `FSCALE` operation, scaling a floating-point source by a power of two derived from the destination/source exponent operand according to 68881-compatible semantics. It handles normal results, denormal results, overflow, and underflow.

### Important APIs, Types, And Functions
The export is `sscale`. Constants include `SRC_BNDS`, and the file depends on `t_ovfl2`, `t_unfl`, `round`, and `t_resdnrm`. Important local paths include `src_small`, `src_in`, `src_pos`, `src_neg`, `denorm`, `fix_dnrm`, `fix_unfl`, `sm_dnrm`, `dst_dnrm`, and `src_out`. Scratch flags in `L_SCR1` and `L_SCR2` hold sign and inexact information.

### Control Flow
`sscale` extracts the integer scaling exponent from the source operand, records its sign, and handles exponents too small or too large to affect the destination normally. In-range positive and negative scaling adjusts the destination exponent and checks for normal, denormal, overflow, or underflow outcomes. Denormal paths shift mantissas, round when bits are lost, return signed zero or smallest denorm for directed rounding modes, and call `t_resdnrm` when a reportable denormal result must be exposed. Overflow and underflow branch to `t_ovfl2` or `t_unfl`.

### State, Persistence, And Dependencies
The routine mutates the FPSP temporary/result operand and scratch long fields. It uses FPCR rounding mode and FPSR status through helpers but has no persistent state. It depends on `round.S` for correct inexact rounding and on `kernel_ex.S` helpers for exception state.

### Integration Points
`do_func` dispatches unimplemented FSCALE here. Results return through standard FPSP result storage or exception reporting, depending on whether the helper paths set status and whether traps are enabled.

### Risks
FSCALE has many boundary cases: source exponent too small to matter, source exponent too large, destination becoming denormal, catastrophic underflow, directed rounding from zero to smallest denorm, and sign-preserving zero. Off-by-one exponent thresholds or missing sticky bits will produce incorrect gradual-underflow behavior.

### Test Signals
Tests should scale normal, denormal, zero, large, and tiny operands by positive and negative scale factors. Include values crossing normal/denormal thresholds, catastrophic underflow, overflow, all rounding modes, signed zero results, and directed-rounding cases that choose smallest positive or negative denorm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/scale.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/scosh.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/scosh.S

### Purpose
`scosh.S` implements the FPSP `FCOSH` hyperbolic cosine operation. It computes `cosh(X)` for normal and denormal double-extended inputs and returns the result in `%fp0`.

### Important APIs, Types, And Functions
Exports are `scosh` and `scoshd`. Constants include split log2 values `T1`/`T2` and `TWO16380` for large-result reconstruction. It depends on `t_ovfl`, `t_frcinx`, and `setox`.

### Control Flow
`scoshd` returns approximately `1` for denormal input via `t_frcinx`. `scosh` takes `|X|`, checks magnitude, and for ordinary inputs calls `setox` to compute `exp(|X|)`, then returns `(exp(|X|) + 1/exp(|X|))/2`. For larger but not overflowing inputs it computes a scaled exponential form using split constants to avoid premature overflow. Huge inputs branch to `t_ovfl`.

### State, Persistence, And Dependencies
The routine uses `%fp0`/`%fp1`, the operand slot at `%a0` for `setox`, and no persistent state. It relies on `setox.S` for exponential approximation and on exception helpers for inexact/overflow reporting.

### Integration Points
`tbldo.S` dispatches FCOSH normal and denormal cases here. The routine composes with `setox` and the standard exception generation path.

### Risks
Overflow threshold handling is the main risk. Cosh is always positive and grows quickly, so using the ordinary formula beyond its safe range can overflow intermediate values before the final result should overflow. Denormal and tiny inputs should return near 1 with inexact status, not the input.

### Test Signals
Test denormal inputs, zero, small finite values, moderate values, near-overflow large values, and huge values. Check positive-only result sign, monotonicity in `|X|`, inexact status, and overflow status at the documented threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/scosh.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/setox.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/setox.S

### Purpose
`setox.S` implements `FETOX` (`exp(x)`) and `FETOXM1` (`exp(x)-1`) for the 68040 FPSP. It provides normal and denormal entries and is a shared backend for other hyperbolic functions.

### Important APIs, Types, And Functions
Exports are `setoxd`, `setox`, `setoxm1d`, and `setoxm1`. The file defines polynomial coefficients for exp and expm1 (`EXPA*`, `EM1A*`, `EM1B*`), scaling constants (`L2`, `TWO140`, `TWON140`), overflow/underflow sentinels (`HUGE`, `TINY`), and a 64-entry `EXPTBL` for table-based reconstruction. Scratch aliases include `ADJFLAG`, `SCALE`, `ADJSCALE`, `SC`, and `ONEBYSC`. It depends on `t_extdnrm`, `t_unfl`, and `t_ovfl`; normal exits use `t_frcinx`.

### Control Flow
`setoxd` handles denormal input by returning `1 + x`-like behavior with forced inexact. `setox` classifies input into small, main, and big ranges. The main path computes a table index `N ~= round(x * 64/log2)`, splits it into scale and residual parts, evaluates a polynomial approximation of the residual exponential, and multiplies by the tabulated scale. Large positive/negative values route to overflow or underflow helpers. `setoxm1d` returns denormal input through `t_extdnrm`; `setoxm1` uses specialized small-input and main paths to preserve cancellation-sensitive `exp(x)-1`, with fallback to the exp path for large values.

### State, Persistence, And Dependencies
The routines use FPU registers, `%a0` operand storage, and FPSP scratch fields, but no persistent state. They depend on exact table indexing, FPCR control restoration, and shared exception helpers for final status.

### Integration Points
`tbldo.S` dispatches FETOX and FETOXM1 here. `scosh.S`, `stanh.S`, and other hyperbolic routines call `setox` or `setoxm1` as helper functions. Exception status flows through `kernel_ex.S` and `gen_except`.

### Risks
The table/polynomial reconstruction is numerically delicate: wrong `N`, wrong scale split, or wrong residual sign changes results over broad ranges. `exp(x)-1` needs special small-input handling; replacing it with `exp(x)-1` directly loses precision near zero. Overflow/underflow thresholds must match 68881-compatible behavior and rounding modes.

### Test Signals
Test exp and expm1 for denormals, signed zeros, tiny positive/negative values, moderate values, table-boundary inputs, and near overflow/underflow limits. Compare against high-precision references and verify monotonicity, exact `expm1(0)`, inexact status, underflow for large negative inputs, and overflow for large positive inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/setox.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sgetem.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sgetem.S

### Purpose
`sgetem.S` implements `FGETEXP` and `FGETMAN` for the FPSP. It extracts the unbiased exponent or normalized mantissa from a double-extended operand, including denormal-specific paths.

### Important APIs, Types, And Functions
Exports are `sgetexp`, `sgetexpd`, `sgetman`, and `sgetmand`. It depends on `nrm_set` for denormal exponent recovery. Internal labels `shft`, `cont`, `upper`, and `shft_end` normalize denormal mantissas for `FGETMAN`.

### Control Flow
`sgetexp` reads the exponent word, strips/adjusts the bias, converts the integer exponent to floating-point, and returns it in `%fp0`. `sgetexpd` first normalizes the denormal operand with `nrm_set`, then returns the recovered exponent. `sgetman` forces the exponent field to the canonical mantissa range while preserving sign, returning a significand in `%fp0`. `sgetmand` shifts denormal mantissa bits until the high bit is set before restoring the canonical exponent and sign.

### State, Persistence, And Dependencies
The routine mutates the operand image at `%a0` when normalizing or setting the mantissa exponent, and returns through `%fp0`. It has no persistent state. It depends on the internal extended layout from `fpsp.h` and shared normalization semantics.

### Integration Points
`tbldo.S` dispatches FGETEXP/FGETMAN normal and denormal cases here; infinities are routed elsewhere as invalid operation. Results continue through standard FPSP result storage and exception handling.

### Risks
Denormal exponent recovery is sensitive to the exact number of left shifts. An off-by-one shift gives an exponent and mantissa that are both plausible but wrong. Sign preservation for `FGETMAN` matters because the mantissa keeps the original sign. Special cases must remain filtered consistently by the dispatch table.

### Test Signals
Test normal powers of two, non-power normal values, positive and negative denormals, signed zeros if dispatched, and values near exponent boundaries. Verify exponent bias removal, mantissa range/sign, and consistency with `x = getman(x) * 2**getexp(x)` for finite nonzero inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sgetem.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sint.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sint.S

### Purpose
`sint.S` implements `FINT` and `FINTRZ` integer-rounding operations for the FPSP, plus an internal `sintdo` entry used by binary/decimal conversion. It rounds a double-extended input to an integral floating-point value and returns it in `%fp0`.

### Important APIs, Types, And Functions
Exports are `sint`, `sintd`, `sintrz`, and `sintdo`. It depends on `dnrm_lp`, `nrm_set`, `round`, `t_inx2`, `ld_pone`, `ld_mone`, `ld_pzero`, `ld_mzero`, and `snzrinx`. Scratch `L_SCR1` stores the selected rounding mode.

### Control Flow
`sint` extracts the user's rounding mode; `sintrz` forces round-to-zero; `sintdo` accepts a caller-provided mode. The main path converts the operand to internal extended format, classifies exponent ranges, returns the input unchanged for exponent >= 63, returns signed zero or one for exponent < 0 according to rounding mode, and otherwise denormalizes to expose fractional bits, calls `round`, normalizes, restores IEEE sign/exponent layout, and loads `%fp0`. `sintd` handles denormal inputs using the documented rounding-mode table.

### State, Persistence, And Dependencies
The routine mutates the operand at `%a0`, scratch mode state, and inexact FPSR bits via `t_inx2`. It has no persistent state. It depends on shared rounding/normalization and on load-constant helpers from other FPSP utility files.

### Integration Points
`tbldo.S` dispatches FINT and FINTRZ here, and `bindec.S` uses `sintdo` during packed decimal conversion. Exception status is propagated through `kernel_ex.S` and `gen_except`.

### Risks
The exponent thresholds determine whether fractional bits exist; off-by-one errors around exponent 0 and 63 change large or tiny values. Directed rounding for tiny negative and positive values must return signed zero or signed one exactly as the table states. `sintrz` must not leak the user's rounding mode into the operation.

### Test Signals
Test all rounding modes with values just below and above integers, `+/-0.5`, tiny normals, denormals, large already-integral values, values around `2**63`, signed zeros, and `FINTRZ` under non-zero user rounding modes. Verify inexact status when fractional bits are discarded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sint.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/skeleton.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/skeleton.S

### Purpose
`skeleton.S` is the Linux/m68k system-dependent wrapper layer around the Motorola FPSP package. It defines real exception entry points, FPSP handoff labels, completion paths, and user-memory access helpers used by FPSP routines.

### Important APIs, Types, And Functions
Exports include `dz`, `real_dz`, `inex`, `real_inex`, `ovfl`, `real_ovfl`, `unfl`, `real_unfl`, `snan`, `real_snan`, `operr`, `real_operr`, `bsun`, `real_bsun`, `fline`, `real_fline`, `unsupp`, `real_unsupp`, `real_trace`, `fpsp_fmt_error`, `fpsp_done`, `mem_write`, and `mem_read`. It includes Linux headers `linux/linkage.h`, `asm/entry.h`, `asm/asm-offsets.h`, and FPSP offsets from `fpsp.h`. It references FPSP core handlers such as `fpsp_ovfl`, `fpsp_unfl`, `fpsp_snan`, `fpsp_operr`, `fpsp_bsun`, `fpsp_fline`, `fpsp_unsupp`, plus errata helper `b1238_fix`.

### Control Flow
Real hardware exception entries either clear pending FPU state and call Linux `trap_c` via `SAVE_ALL_INT`/`ret_from_exception`, or jump into an FPSP handler for emulatable conditions. The inexact path contains erratum handling that can redirect to SNAN, overflow, or underflow paths depending on pending E1/E3 state. `fpsp_done` restores or returns from exception depending on whether the frame is kernel or user context. `fpsp_fmt_error` emits an illegal f-line word for malformed FPSP frames. `mem_write` and `mem_read` choose supervisor or user copy routines based on the saved status register and use exception-table fixups for safe copyin/copyout.

### State, Persistence, And Dependencies
This file interacts with real kernel exception state: stack frames, saved registers, current task lookup, and user memory. It does not maintain persistent variables, but it mutates FPU pending exception state with `fsave`/`frestore`, clears E-byte bits, and copies memory through user/supervisor paths. It depends on Linux m68k calling conventions and exception macros.

### Integration Points
It is the bridge between CPU exception vectors and the architecture-neutral parts of the FPSP tree. Core math and exception routines rely on `fpsp_done`, `real_*` labels, `mem_read`, and `mem_write`. Linux trap handling is invoked through `trap_c` and `ret_from_exception`.

### Risks
This file is security- and correctness-sensitive. User memory helpers must respect user/supervisor mode and handle faults via exception tables; mistakes can corrupt kernel memory or oops during emulation. Exception wrapper paths must preserve register/FPU state exactly. Errata redirection in the inexact path can report the wrong exception if E1/E3 bits are mishandled.

### Test Signals
Validation should include user-mode floating-point traps, kernel-mode FPSP exits, memory write/read faults during packed move-out, divide-by-zero and inexact exception delivery, malformed fsave frame handling, and regression tests for errata paths. Kernel exception traces should show clean return through `ret_from_exception` with user registers intact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/skeleton.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/slog2.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/slog2.S

### Purpose
`slog2.S` implements base-10 and base-2 logarithm wrappers for the FPSP. It delegates natural logarithm calculation to `slogn`/`slognd`, applies reciprocal-log constants, and includes an optimized exact path for powers of two in `FLOG2`.

### Important APIs, Types, And Functions
Exports are `slog10d`, `slog10`, `slog2d`, and `slog2`. Constants are `INV_L10` and `INV_L2`. It depends on `t_frcinx`, `t_operr`, `slogn`, and `slognd`. Local labels include `continue` and `invalid`.

### Control Flow
Each entry first rejects negative inputs with `t_operr`, then sets FPCR behavior for the helper calculation. `slog10d`/`slog10` compute natural log and multiply by `1/log(10)`. `slog2d` computes natural log and multiplies by `1/log(2)`. `slog2` additionally detects exact powers of two by examining the significand; for those inputs it returns the unbiased exponent directly as an exact floating value, otherwise it follows the natural-log path.

### State, Persistence, And Dependencies
The routine saves/restores FPCR around helper calls and returns `%fp0`. It has no persistent state. It depends on `slogn.S` for domain handling of zero and positive values, and on exact extended operand representation for power-of-two detection.

### Integration Points
`tbldo.S` dispatches FLOG10 and FLOG2 normal/denormal cases here, though symbol aliases in the table may use wrapper names for shared implementations. Exception flow is handled by `t_operr`, `t_frcinx`, and `gen_except`.

### Risks
Negative input detection must preserve `-0` behavior expected by lower-level log code. Exact power-of-two optimization must only trigger when all fraction bits except the integer bit are clear; otherwise it can skip inexact status and return a wrong integer log. FPCR restoration is necessary so helper default precision does not leak.

### Test Signals
Test positive powers of two, non-powers near powers of two, denormal positives, zero, negative values, and large/small normals. Verify exact integer results for powers of two, invalid operation for negatives, divide-by-zero behavior through `slogn` for zero, and correct scaling for log10/log2 against high-precision references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/slog2.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/slogn.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/slogn.S

### Purpose
`slogn.S` implements natural logarithm (`FLOGN`) and log-one-plus (`FLOGNP1`) for the FPSP. It provides normal and denormal entries and uses table reduction plus polynomial approximation to meet the documented monotonicity and accuracy targets.

### Important APIs, Types, And Functions
Exports are `slognd`, `slogn`, `slognp1d`, and `slognp1`. Constants include range bounds, `LOGOF2`, polynomial coefficients `LOGA*` and `LOGB*`, `TWO`, `LTHOLD`, and a 64-entry `LOGTBL` containing precomputed reciprocal/significand and log values. Scratch aliases include `ADJK`, `X`, `F`, `KLOG2`, and `SAVEU`. Dependencies are `t_extdnrm`, `t_operr`, and `t_dz`; normal exits use `t_frcinx`.

### Control Flow
`slognd` normalizes denormal input and adjusts the effective exponent before using the main log logic. `slogn` rejects negatives, handles zero through divide-by-zero, and for `|X-1| < 1/16` uses a near-one odd polynomial in `u = 2(X-1)/(X+1)`. Otherwise it decomposes `X = 2**k * Y`, chooses a table value `F`, computes `u = (Y-F)/F`, evaluates a polynomial approximation to `log(1+u)`, and reconstructs `k*log(2) + log(F) + poly`. `slognp1` uses a cancellation-aware path for small `X`, otherwise forms `1+X` and uses the same decomposition, with special cases for `X = -1`, `X < -1`, `X = 0`, and tiny values.

### State, Persistence, And Dependencies
The routine mutates FPSP scratch float slots and `%a0` operand storage but does not persist state. It depends on exact exponent/significand decoding, table indexing, and exception helpers. Several paths temporarily adjust `ADJK` to account for denormal normalization or log1p reconstruction.

### Integration Points
`slog2.S` calls `slogn`/`slognd` for base conversions, `satanh.S` calls `slognp1`, and `tbldo.S` dispatches FLOGN/FLOGNP1 here. Results and exceptions feed the shared FPSP reporting machinery.

### Risks
Log near one and log1p near zero are cancellation-sensitive; using the general decomposition for those cases would lose precision. Domain boundary handling is subtle: `log(0)` is divide-by-zero, `log(negative)` is invalid operation, `log1p(-1)` is divide-by-zero, and `log1p(x<-1)` is invalid. Table index or exponent adjustment mistakes shift the result by multiples of `log(2)`.

### Test Signals
Test `log(1)`, values very close to 1, powers of two, denormals, zero, negatives, large/small normals, `log1p(0)`, tiny `log1p` inputs, `log1p(-1)`, and `log1p` just below `-1`. Check monotonicity, domain exception class, inexact status, and ulp accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/slogn.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/smovecr.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/smovecr.S

### Purpose
`smovecr.S` implements the unimplemented `FMOVECR` constant-load instruction. It decodes the constant offset from the instruction, selects a rounding-mode-specific precomputed constant, and returns the rounded value in `%fp0`.

### Important APIs, Types, And Functions
The export is `smovcr`. It depends on `nrm_set`, `round`, and the constant tables exported by `get_op.S`: `PIRN`, `PIRZRM`, `PIRP`, `SMALRN`, `SMALRZRM`, `SMALRP`, `BIGRN`, `BIGRZRM`, and `BIGRP`. Internal labels select `PI_TBL`, `SM_TBL`, `BG_TBL`, `set_finx`, `no_finx`, and `fin_fcr`.

### Control Flow
`smovcr` extracts the 7-bit offset from `CMDREG1B` and the rounding mode from `USER_FPCR`. Offset 0 selects pi. Offsets `0x0b` through `0x0e` select small constants such as log10(2), e, log2(e), and log10(e). Offsets `0x30` through `0x3f` select large constants including ln(2), ln(10), and powers of ten. Unsupported offset ranges return zero. For constants with known inexact encodings, `set_finx` records inexact; for destination precisions below extended, the routine converts to internal format and calls `round`.

### State, Persistence, And Dependencies
The routine reads instruction and FPCR state from the FPSP frame and may set inexact FPSR bits. It returns `%fp0` and has no persistent state. It depends on `get_op.S` table ordering and on the FPCR precision/mode bit layout from `fpsp.h`.

### Integration Points
`tbldo.S` dispatches FMOVECR opcodes to `smovcr`, and `get_op.S` defines the tables it consumes. Final exception reporting follows the standard inexact path.

### Risks
The offset map is architectural. Returning zero for reserved offsets is intentional; accidentally treating a reserved offset as a table index can read unrelated data. Rounding-mode-specific low bits are precomputed, so using RN data for RZ/RM/RP is incorrect. Inexact status differs per constant and offset group and must be preserved.

### Test Signals
Test all architected FMOVECR offsets under RN, RZ, RM, and RP, plus reserved offset ranges that should return zero. Verify extended, single, and double precision outputs, inexact flag behavior, pi low-bit variants, powers-of-ten table entries, and no out-of-range table access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/smovecr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/srem_mod.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/srem_mod.S

### Purpose
`srem_mod.S` implements floating-point `FMOD` and IEEE `FREM` for finite nonzero operands. It computes the remainder of `X` divided by `Y`, returning the correct sign, quotient bits, and remainder value according to the selected operation.

### Important APIs, Types, And Functions
Exports are `smod` and `srem`, which share the `Mod_Rem` body. Scratch aliases define `Mod_Flag`, `SignY`, `SignX`, `SignQ`, `Sc_Flag`, `Y`, and `R`. The only external dependency is `t_avoid_unsupp`, used at finish to avoid denormal unsupported traps during result handling. A `Scale` constant supports denormal scaling.

### Control Flow
The common path saves operand signs, strips signs, records MOD versus REM, normalizes denormal operands if needed, and compares exponents. It initializes a scaled remainder `R`, quotient accumulator `Q`, and loop count from exponent difference. `Mod_Loop` repeatedly compares/subtracts `Y`, shifts `R`, and accumulates quotient bits. After the loop, MOD returns the signed remainder directly, while REM compares `R` with `Y/2`, possibly performs a final subtract, and handles the exact tie case by checking quotient parity. Finish restores signs, quotient bits, and branches through `t_avoid_unsupp`.

### State, Persistence, And Dependencies
All state is held in FPSP scratch slots and data registers. The routine writes the result operand and FPSR quotient byte but keeps no persistent state. It assumes NaNs, infinities, and zero divisors were handled before entry, as stated in the file comments.

### Integration Points
The arithmetic function dispatcher calls `smod` or `srem` for FMOD/FREM normal finite cases. The result then flows through common FPSP storage and exception machinery, with `t_avoid_unsupp` guarding denormal replay behavior.

### Risks
Remainder semantics are branch-sensitive. FMOD and FREM differ at the post-loop step, especially when `R` is exactly `Y/2`, where IEEE remainder chooses the even quotient. Quotient sign and low seven quotient bits must be correct for FPSR. Denormal scaling must not change the mathematical remainder or lose sign information.

### Test Signals
Test positive and negative X/Y combinations, exact multiples, `R < Y/2`, `R > Y/2`, exact half-way ties with even and odd quotients, large exponent differences, denormal operands, and quotient byte/sign behavior. Compare FMOD versus FREM against an m68k/68881 reference or high-precision software model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/srem_mod.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/ssin.S -->
## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/ssin.S

### Purpose
`ssin.S` implements `FSIN`, `FCOS`, and `FSINCOS` for the 68040 FPSP. It performs range reduction, selects sine or cosine polynomial approximations, handles tiny and denormal inputs, and returns one or two FPU results depending on the instruction.

### Important APIs, Types, And Functions
Exports are `ssind`, `scosd`, `ssin`, `scos`, `ssincosd`, and `ssincos`. Constants include range bounds, `2/pi`, inverse `2*pi`, split `2*pi` values, and sine/cosine polynomial coefficients `SINA*` and `COSB*`. Scratch aliases include `INARG`, `X`, `RPRIME`, `SPRIME`, `POSNEG1`, `TWOTO63`, `ENDFLAG`, `N`, and `ADJN`. It depends on `PITBL`, `t_extdnrm`, `sto_cos`, and `t_frcinx`.

### Control Flow
Denormal sine returns the input through `t_extdnrm`; denormal cosine returns one through `t_frcinx`. Normal `ssin` and `scos` set an adjustment value (`ADJN`) to distinguish sine from cosine, classify the magnitude, and for ordinary `|X| < 15*pi` reduce `X` to `N*pi/2 + r` with `|r| <= pi/4`. The quadrant determines sign and whether to evaluate the sine odd polynomial or cosine even polynomial. Very tiny sine returns `X`, tiny cosine returns `1`, and larger inputs go through `REDUCEX`, which computes `X rem 2*pi` using split constants and loops until the reduced argument is in range. `ssincos` computes both polynomials and uses quadrant parity to store sine in `%fp0` and cosine through `sto_cos`/`%fp1`.

### State, Persistence, And Dependencies
The routine uses FPSP scratch operands, FPU registers, and sometimes the operand slot at `%a0`; no persistent state is stored. It depends on external `PITBL` data for high-quality range reduction and on `sto_cos` to place the second result for FSINCOS.

### Integration Points
`tbldo.S` dispatches FSIN, FCOS, and FSINCOS normal and denormal opcodes here. Exception helpers record inexact/denormal status, and the common FPSP completion path stores results or reports exceptions.

### Risks
Argument reduction dominates correctness. Large inputs require split-constant reduction; small mistakes produce wrong quadrants and signs even when polynomial code is correct. FSINCOS has two result registers and sign rules, so it is more integration-sensitive than single-result sine/cosine. Tiny inputs must return exactly `x` or `1` with appropriate status, not reduced polynomial noise.

### Test Signals
Test signed zeros, denormals, tiny magnitudes, quadrant boundaries, multiples of `pi/2`, values near `15*pi`, large finite arguments requiring `REDUCEX`, and FSINCOS destination handling. Verify sine/cosine signs by quadrant, identity consistency, inexact status, and ulp accuracy against a high-precision range-reduction oracle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/ssin.S -->
