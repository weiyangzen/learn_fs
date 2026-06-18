# Research: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/pfpsp.S

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000712`: lines 1-8268, `Docs/researches/chunks/subset-b-000712_research.md`
- `subset-b-000713`: lines 8269-14745, `Docs/researches/chunks/subset-b-000713_research.md`

## Chunk Research

### subset-b-000712: lines 1-8268

# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/pfpsp.S lines 1-8268

## Scope And Purpose

This chunk is the opening and central exception-handling portion of Motorola's 68060 Floating Point Software Package (`060FPSP`) assembly source as vendored under the m68k client tree. It provides the exported branch table, operating-system callout stubs, local stack-frame layout constants, major FPSP exception entry points, effective-address and `fmovm` emulation helpers, floating-point classification and rounding primitives, `fmove`-out support, and the beginning of the `fmul` emulation path.

The file is not Ceph client logic; it is low-level m68k architecture support code. Its job is to repair or emulate cases where the MC68060 FPU traps for overflow, underflow, unimplemented data type, unimplemented effective address, operand error, signalling NaN, inexact, divide-by-zero, FPU-disabled/Line-F conditions, and selected unsupported instruction forms. It bridges CPU exception frames, FPU `fsave` state, emulated FP operations, memory access callouts supplied by the embedding OS, and final exits back into OS exception handlers.

This chunk ends at line 8268 in the middle of the enabled-underflow path for `fmul`; the rest of `fmul` and later arithmetic routines are outside this chunk.

## Entry Table And Callout Layer

`_060FPSP_TABLE` is the public branch table for users linking the FPSP. It branches to `_fpsp_snan`, `_fpsp_operr`, `_fpsp_ovfl`, `_fpsp_unfl`, `_fpsp_dz`, `_fpsp_inex`, `_fpsp_fline`, `_fpsp_unsupp`, and `_fpsp_effadd`.

The early `_real_*`, `_fpsp_done`, `_imem_*`, and `_dmem_*` symbols are trampoline stubs. Each saves `d0`, loads a relative offset from the table area, pushes the resolved target address, restores `d0`, and returns with `rtd &0x4`. These are integration points for the OS or surrounding FPSP package:

- `_fpsp_done` exits after the FPSP has fully handled an exception.
- `_real_ovfl`, `_real_unfl`, `_real_inex`, `_real_bsun`, `_real_operr`, `_real_snan`, `_real_dz`, `_real_fline`, `_real_fpu_disabled`, `_real_trap`, `_real_trace`, and `_real_access` transfer to real OS exception handlers.
- `_imem_read`, `_imem_read_word`, `_imem_read_long` fetch instruction bytes/words/longs through callouts.
- `_dmem_read`, `_dmem_read_{byte,word,long}`, `_dmem_write`, and `_dmem_write_{byte,word,long}` access data memory through callouts.

This indirection is central to portability: the FPSP core can `bsr` stable local labels while the actual OS handlers and memory-access routines are supplied through the table.

## Stack Frame, FP State, And Constants

The chunk defines a 192-byte local frame (`LOCAL_SIZE`) rooted at `a6`. It maps CPU exception-frame fields (`EXC_SR`, `EXC_PC`, `EXC_VOFF`, `EXC_EA`), saved address/data registers (`EXC_A*`, `EXC_D*`), saved FP registers (`EXC_FP0` through `EXC_FP2`), scratch extended operands (`FP_SCR0`, `FP_SCR1`), source/destination operands (`FP_SRC`, `FP_DST`), saved user FP control registers (`USER_FPCR`, `USER_FPSR`, `USER_FPIAR`), and small flags such as `STAG`, `DTAG`, `STORE_FLG`, and `SPCOND_FLG`.

Operand tags classify FP inputs as `NORM`, `ZERO`, `INF`, `QNAN`, `DENORM`, `SNAN`, or `UNNORM`. FPSR/FPCR bit and mask definitions model exception precedence and accrued exceptions: BSUN, SNAN, OPERR, OVFL, UNFL, DZ, INEX2, INEX1, and corresponding accrued bits. Precision and rounding constants cover extended, single, double, round-to-nearest, round-to-zero, round-minus, and round-plus modes.

Constants such as `PI`, `PIBY2`, `TWOBYPI`, and logarithm fragments are defined early for use by broader FPSP arithmetic code, though most transcendental routines are not in this chunk.

## Major Exception Entry Points

`_fpsp_ovfl` handles FP overflow exceptions. It saves the busy `fsave` frame and key registers, fetches the faulting instruction from `USER_FPIAR`, distinguishes `fmove`-out from opclass 0/2 operations, repairs skewed source operands, tags source/destination operands, dispatches through `tbl_unsupp` for arithmetic emulation, stores the default result, and then decides whether to exit via `_fpsp_done`, `_real_ovfl`, `_real_inex`, or `_real_trace`. Enabled overflow creates an exceptional operand in the `fsave` frame using `fp1`; disabled overflow with enabled inexact may be redirected to the real inexact handler.

`_fpsp_unfl` mirrors the overflow flow for underflow. It includes a hardware quirk check for the 68060 multiplier producing the smallest normalized number: if emulation shows no real underflow or no inexact, it avoids incorrectly delivering the trap. It handles `fmove`-out underflow, enabled underflow, disabled-underflow plus enabled-inexact, and trace-frame conversion.

`_fpsp_unsupp` is the largest handler in this chunk. It covers unimplemented data types and packed formats for opclass 0/2 and opclass 3 moves. It decodes user/supervisor stack state, repairs DENORM/UNNORM and packed operands, calls `get_packed`, `set_tag_x`, `unnorm_fix`, `load_fpn*`, `tbl_unsupp` arithmetic routines, or `fout`, and resolves enabled exception precedence. It can insert exception state back into the FPU via `frestore`, call real handlers for SNAN/OPERR/OVFL/UNFL/INEX, update `usp`, and rewrite supervisor stack frames for `(a7)+` and `-(a7)` special cases.

`_fpsp_effadd` handles unimplemented effective-address exceptions. It first checks the processor control register for a disabled FPU, because the effective-address exception can arrive before the higher-priority FPU-disabled condition. Normal operation decodes immediate extended/packed operands, dynamic `fmovm.x`, and control-register `fmovm.l`. It reads immediate operands through `_imem_read`, converts packed inputs through `decbin`, emulates arithmetic through `tbl_unsupp`, stores FP results, or dispatches to `fmovm_dynamic`/`fmovm_ctrl`. It creates trace frames on traced instructions, FPU-disabled frames via `iea_disabled`, and access-error frames via `iea_iacc`/`iea_dacc`.

`_fpsp_operr` repairs skewed operands for enabled operand-error traps. For opclass 3 integer move-outs, it also writes the default integer saturation/QNaN-derived result to data registers or memory before calling `_real_operr`, because the 68060 does not perform that store automatically on enabled OPERR.

`_fpsp_snan` similarly repairs skewed operands and, for opclass 3 move-outs, writes the default quieted-SNaN result before calling `_real_snan`. It supports byte/word/long/single/double/extended stores and uses `_calc_ea_fout` plus special stack-frame shifting for supervisor `-(a7)` extended stores.

`_fpsp_inex` emulates inexact operations so the destination FP register or output memory receives the default result before `_real_inex`. It has a special `fmovcr` path through `smovcr`, but in this reduced file `smovcr` is a self-branch stub, so linking this reduced variant with live `fmovcr` inexact handling would hang unless overridden by another module.

`_fpsp_dz` repairs the source operand for divide-by-zero and exits to `_real_dz`.

`_fpsp_fline` is the reduced-package Line-F handler. It distinguishes an FPU-disabled frame (`0x402c`) from other Line-F cases and branches to `_real_fpu_disabled` or `_real_fline`.

## Operand Repair And Effective Address Helpers

`fix_skewed_ops` corrects the 68060's internal representation for opclass 2 single/double inputs that were delivered as skewed zero, denorm, infinity, or NaN. It normalizes denorm mantissas with `norm`, adjusts exponents back to single/double thresholds, clears bogus j-bits, and maps skewed zero/infinity/NaN into the expected extended representation.

`funimp_skew` performs the inverse when an operand must be put back into an `fsave` frame in the same skewed shape hardware would have produced for single or double source operands.

`_dcalc_ea` repairs stacked effective addresses for unimplemented data type and packed opclass 2 paths. It handles `(An)+`, `-(An)`, and immediate `#<data>` specially, using `inc_areg`/`dec_areg` and `SPCOND_FLG`.

`_calc_ea_fout` repairs effective addresses for opclass 3 extended and packed move-outs. It updates address registers for `(An)+`, subtracts 8 from stacked EAs for `-(An)`, and records `mia7_flg`/`mda7_flg` for stack-pointer special cases.

`fmovm_calc_ea` is a full effective-address calculator for dynamic `fmovm`. It supports register indirect, postincrement, predecrement, displacement, indexed, absolute short/long, PC-relative, and memory-indirect modes. It advances `EXC_EXTWPTR` as extension words are consumed and routes instruction/data access failures to `iea_iacc` or `iea_dacc`.

## `fmovm` Emulation

`fmovm_dynamic` emulates dynamic-register-mask `fmovm.x`. It fetches the mask from a data register, uses `tbl_fmovm_size` to determine the byte count, calculates the EA, and then reads or writes 12-byte extended FP registers. Move-out with predecrement converts the mask through `tbl_fmovm_convert`; supervisor `fmovm.x Dn,-(a7)` returns size and mask to the caller so stack-frame rewriting can be done outside the generic routine. Data memory failures call `restore` and build an access-error frame.

`fmovm_ctrl` emulates immediate control-register loads for FPCR, FPSR, and FPIAR combinations. It decodes the extension byte and reads two or three longwords through `_imem_read_long`, storing them into `USER_FPCR`, `USER_FPSR`, and `USER_FPIAR`. Instruction access failure exits through `iea_iacc`.

## Arithmetic Support Primitives

`addsub_scaler2`, `scale_to_zero_src`, `scale_to_zero_dst`, and `scale_sqrt` rescale extended operands around exponent zero (`0x3fff`) so later hardware FP operations can be used without causing host FPU overflow/underflow. These routines preserve signs, normalize denormals, and return scale factors for later exponent restoration.

`res_qnan`, `res_snan`, `res_qnan_1op`, `res_snan_1op`, and `res_operr` produce default NaN/operand-error results and update `USER_FPSR` exception/accrued bits. SNaNs are quieted by setting the signalling bit in the mantissa before returning the chosen NaN through `fp0`.

`_denorm` and `dnrm_lp` denormalize extended internal-format operands to the selected precision threshold while maintaining guard, round, and sticky bits. `dnrm_lp` handles shifts of 0-31, 32-63, 64, 65, and greater than 65 separately to preserve sticky-bit correctness.

`_round` implements IEEE-style rounding for extended, single, and double precision under RN/RZ/RM/RP. It calls `ext_grs` to derive precision-specific guard/round/sticky bits, sets inexact status when needed, adds at the correct precision boundary, handles mantissa carry into the exponent, and truncates excess mantissa bits. RN ties are rounded to even.

`norm` left-normalizes an extended mantissa and returns the shift count. `unnorm_fix` converts an unnormalized extended value into `NORM`, `DENORM`, or `ZERO` by shifting mantissa bits and adjusting or clearing exponent fields.

`set_tag_x`, `set_tag_d`, and `set_tag_s` classify extended, double, and single operands into the local tag enum. `set_tag_x` also rewrites an "unnormalized zero" into a real zero.

`unf_res` and `unf_res4` create default underflow results by converting to internal sign/exponent format, denormalizing with `_denorm`, rounding with `_round`, restoring normal sign layout, returning zero condition-code information, and setting accrued underflow when inexact is present. `unf_res4` forces the denormalization/rounding choices needed by `fsglmul`/`fsgldiv`.

`ovf_res` and `ovf_res2` map result sign, rounding precision, and rounding mode to a default overflow value and condition-code byte using `tbl_ovfl_cc` and `tbl_ovfl_result`. The table covers infinities and largest finite values for extended, single, and double modes.

## `fout` And Move-Out Conversion

`fout` is the shared opclass 3 move-out engine. It dispatches by destination format: byte, word, long, single, double, extended, or packed.

For byte/word/long integer outputs, it uses hardware `fmov` conversions with the caller's rounding mode, collects FPSR exception bits, and stores either to a data register through `store_dreg_{b,w,l}` or to memory through `_dmem_write_{byte,word,long}`. Denorm inputs are converted through the smallest single-precision value with the source sign before conversion.

For extended outputs, it writes a 12-byte extended result, fixes EA/address-register side effects through `_calc_ea_fout`, defers supervisor `-(a7)` writes through `_mem_write2`, and flags underflow for denorm extended stores. If underflow/inexact is enabled, it creates an EXOP in `fp1` by normalizing the denorm and rebuilding the exponent.

For single and double outputs, it checks exponent thresholds before using hardware stores. Definite underflow goes through `unf_res` and `dst_sgl`/`dst_dbl`; definite overflow goes through `ovf_res`; boundary cases perform a scaled test conversion to decide whether rounding crosses the overflow threshold. If an enabled OVFL/UNFL/INEX condition needs an exceptional operand, `fout_sd_exc_*` rebuilds and rounds the EXOP into `fp1`.

For packed outputs, `fout_pack` obtains static or dynamic k-factors, calls `bindec` to convert binary extended to packed decimal, clears unused packed fields, normalizes packed zero exponent behavior, writes through `_dmem_write`/`_mem_write2`, and quiets SNaNs while setting SNAN/AIOP status.

`dst_sgl` and `dst_dbl` convert internal extended operands to raw single/double bit layouts without rounding; callers are responsible for prior rounding.

## Beginning Of `fmul` Emulation

The chunk includes the start of `fmul`, `fsmul`, and `fdmul`. `fsmul` and `fdmul` force the rounding precision to single or double, then enter `fmul`. `fmul` stores rounding mode/precision in `L_SCR3`, combines `STAG` and `DTAG`, and fast-paths the common `NORM`/`NORM` case.

For normal operands, it copies source/destination to scratch, scales both exponents to zero with `scale_to_zero_src` and `scale_to_zero_dst`, sums the scale factors, and compares the scale factor against precision-specific overflow/underflow thresholds in `tbl_fmul_ovfl` and `tbl_fmul_unfl`.

The visible normal path performs `fmul.x`, records FPSR status into `USER_FPSR`, restores the scaled exponent, and returns the result in `fp0`. The visible overflow path records overflow/inexact status, creates the default result with `ovf_res` when exceptions are disabled, and creates an EXOP in `fp1` when OVFL/INEX is enabled. The visible underflow path sets UNFL, performs an extended round-to-zero multiply to gather status, uses `unf_res` for disabled exceptions, and starts building the enabled-underflow EXOP. The chunk ends immediately after restoring `d2` while constructing that EXOP.

## State And Persistence Behavior

The code persists no filesystem or heap state. Its state is CPU/FPU state, the current exception frame, the local `a6` stack frame, memory/register side effects required by the trapped instruction, and the OS callout table.

Important state transitions include:

- `fsave`/`frestore` capture and reinsert FPU busy/exception state.
- `fmovm.l %fpcr,%fpsr,%fpiar` saves user FP control/status/instruction-address registers and later restores them.
- `fmovm.x` saves/restores `fp0`/`fp1`, while many emulation routines use `fp0` for default results and `fp1` for exceptional operands.
- `USER_FPSR` is selectively cleared, preserved, ORed with new exception/accrued bits, and sometimes used to synthesize stack/FPU exception state.
- `EXC_PC`, `EXC_VOFF`, `EXC_EA`, and sometimes the real system stack are rewritten to convert one exception frame shape into another, especially trace, access error, FPU disabled, packed/extended supervisor `a7`, and enabled FP exception cases.
- User stack pointer changes are staged in `EXC_A7` and committed with `mov.l %a0,%usp`; supervisor stack-pointer special cases are handled by moving the exception frame itself.

## Dependencies And Integration Points

This chunk depends on m68k/68060-specific instructions and assembler features: `fsave`, `frestore`, `fmovm`, `fmov`, `movec %pcr`, bitfield instructions (`bfextu`, `bfexts`, `bfffo`, `bfins`, `bftst`), `rtd`, and 68k exception-frame layout.

Internal routines referenced but defined outside this exact range include later arithmetic operations and conversion/helpers such as `fadd`, `fsub`, `fdiv`, `fsqrt`, `fcmp`, `ftst`, `fetch_dreg`, `store_dreg_*`, `load_fpn*`, `store_fpreg`, `get_packed`, `decbin`, `bindec`, `restore`, and access-error finalization paths. `tbl_unsupp` indexes many of these routines by FP extension opcode.

The main external integration surface is the callout table behind `_060FPSP_TABLE`. The embedding kernel/OS must provide correct handlers and memory access routines with the expected register protocol, especially the convention that memory callouts signal failure through `d1` and return data in `d0` or buffers.

## Risks And Edge Cases

This code is extremely sensitive to stack-frame layout and register conventions. Offsets such as `EXC_VOFF`, `EXC_EA`, `FP_SRC`, and `USER_FPSR` are shared across many handlers; a wrong constant corrupts exception delivery or user register state.

Exception precedence is subtle. The handlers repeatedly choose the highest enabled exception, but also force INEX delivery when disabled OVFL/UNFL interacts with enabled INEX and an EXOP would otherwise be lost. Changes here can alter IEEE exception semantics.

Supervisor `-(a7)` and `(a7)+` are high-risk paths. Several handlers delay memory writes or move stack frames to avoid overwriting the active exception frame while emulating a store to the supervisor stack.

Memory callouts must be precise. Instruction fetch failure must become an instruction access error; data load/store failure must become a data access error with a correct fault address and FSLW. Incorrect `d1` handling silently follows success paths after failed memory operations.

`smovcr` is a self-loop stub in this reduced source section. Any build using this exact symbol for reachable `fmovcr` inexact emulation would hang unless a full implementation replaces it.

The range ends mid-`fmul` enabled-underflow EXOP construction, so review of multiply behavior must continue in the next chunk before drawing conclusions about full `fmul` correctness.

## Test Signals

There are no direct tests in this assembly file. Useful validation signals would come from m68k/68060 FPSP exception tests or emulator/kernel tests that exercise:

- Overflow/underflow with traps enabled and disabled, including disabled OVFL/UNFL plus enabled INEX.
- Opclass 3 move-outs to integer, single, double, extended, and packed destinations, including memory access failures.
- DENORM, UNNORM, INF, QNAN, SNAN, zero, and skewed single/double source representations.
- Trace frame conversion after emulated operations.
- FPU-disabled priority over unimplemented effective address.
- Dynamic `fmovm.x` with all addressing modes, especially supervisor `-(a7)` and `(a7)+`.
- Instruction and data access-error synthesis from `_imem_*`/`_dmem_*` callout failures.
- Rounding modes and precision-specific guard/round/sticky behavior for `_round`, `_denorm`, `unf_res`, `ovf_res`, and `fout`.
- `fmul` normal, may-overflow, definite-overflow, definite-underflow, and enabled-exception paths, continued into the following chunk.

At minimum, an integration harness should compare final FP register/memory contents, FPSR exception/accrued bits, FPIAR/PC values, stack-frame vector offsets, and restored integer/address registers against known 68040/68881-compatible behavior promised by the FPSP comments.

### subset-b-000713: lines 8269-14745

# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/pfpsp.S lines 8269-14745

## Scope

This chunk covers the latter half of Motorola's 68060 floating-point software package source `pfpsp.S`. It begins in the middle of the `fmul` underflow path, then contains most of the primary floating-point emulation routines for move, divide, negate, test, integer conversion, absolute value, compare, single-precision multiply/divide, add, subtract, square root, register-file helpers, packed-decimal conversion helpers, and access-error recovery.

The file is original Motorola 68060 support code included under `arch/m68k/ifpsp060/src`. `README-SRC` states that these sources do not assemble out of the box with GNU assembler and are included for GPL compliance; the Linux/m68k build uses precompiled `.sa` files generated from Motorola sources. Research should therefore treat this chunk as authoritative source documentation for FPSP behavior and ABI contracts, not as routinely built kernel code.

The range is chunk-bounded. The first visible lines continue `fmul` logic started earlier, and the final lines end with the access-error restore helper. Whole-file conclusions should be reconciled with adjacent `pfpsp.S` chunks.

## Purpose

The chunk implements software emulation for floating-point operations that the 68060 does not directly support, while preserving 68881/68882-visible behavior around IEEE-style special operands, rounding precision, exception flags, condition codes, and exception operands (`EXOP`). The emulators generally accept unpacked extended-precision operands in the FPSP exception frame, use hardware FPU instructions on scaled temporary operands when possible, then repair exponents and status so the result matches the architected instruction.

The main responsibilities visible here are:

- complete the `fmul` special-case support for non-normal operands, zeros, infinities, NaNs, and underflow boundaries;
- implement `fin`, `fsin`, and `fdin` for `fmove` into the FP register file with extended, single, or double result precision;
- implement `fdiv`, `fsdiv`, and `fddiv` with operand scaling, overflow/underflow detection, default result selection, and divide special cases;
- implement unary operations `fneg`, `fsneg`, `fdneg`, `ftst`, `fint`, `fintrz`, `fabs`, `fsabs`, `fdabs`, and `fsqrt` variants;
- implement binary operations `fcmp`, `fsglmul`, `fsgldiv`, `fadd`/`fsadd`/`fdadd`, and `fsub`/`fssub`/`fdsub`;
- provide data/address/FP register dispatch helpers used by instruction decode and effective-address handling;
- convert packed BCD operands to binary extended precision (`get_packed`, `decbin`) and binary extended precision to packed BCD (`bindec`, `binstr`);
- translate failed data-memory reads/writes into a real access-error frame and undo address-register side effects.

## Important APIs And Entry Points

The exported instruction emulation labels in this chunk are assembly-level entry points, not C APIs. Their calling convention is the FPSP internal convention: `%a6` points at the FPSP exception frame and scratch area, `%a0` and `%a1` usually point at source and destination extended operands, `%d0` carries rounding precision/mode or operation-specific metadata, and results are returned in `%fp0`, with `%fp1` holding `EXOP` when a trapped exception needs one.

Important arithmetic and conversion entry points include:

- `fin`, `fsin`, `fdin`: emulate `fmove`, forcing single or double precision for `fsin`/`fdin` by editing the rounding-precision bits in `%d0`, then handling normal, denormal, zero, infinity, QNaN, and SNaN input.
- `fdiv`, `fsdiv`, `fddiv`: emulate divide by scaling source and destination exponents to avoid intermediate hardware exceptions, executing `fdiv.x`, and post-checking precision-specific overflow/underflow thresholds.
- `fneg`, `fsneg`, `fdneg`: emulate sign negation, including denormal normalization for enabled underflow exceptions and precision-dependent overflow/underflow paths for single/double destination precision.
- `ftst`: tests one operand and writes FPSR condition-code state for norm, denorm, zero, infinity, and NaN cases without returning a numeric result beyond the normal FPU test behavior.
- `fint`, `fintrz`: convert to integer in current rounding mode or forced round-to-zero mode; they special-case denorms as signed zero and use NaN helpers for signaling/quiet NaNs.
- `fabs`, `fsabs`, `fdabs`: clear operand sign while preserving the same exception/result machinery as `fneg`/`fin`.
- `fcmp`: compare source and destination and set condition codes, with explicit handling for NaN condition-code quirks and denorm ordering against normals.
- `fsglmul` and `fsgldiv`: single-precision multiply/divide operations that always use the `fsgl*` hardware instruction form, but still return an extended internal result and use `unf_res4` for single-op underflow defaults.
- `fadd`, `fsadd`, `fdadd`, `fsub`, `fssub`, `fdsub`: add/subtract with shared scaling via `addsub_scaler2`, precision-specific exponent tables, signed-zero rules, infinity invalid-operation checks, and NaN dispatch.
- `fsqrt`, `fssqrt`, `fdsqrt`: square root with negative operand invalid-operation handling, denormal scaling through `scale_sqrt`, and precision-dependent exception handling.
- `get_packed`, `decbin`, `bindec`, `binstr`: packed decimal load and conversion support for 68881/68882 packed BCD formats.

Register and state helper entry points include:

- `fetch_dreg`, `store_dreg_l`, `store_dreg_w`, `store_dreg_b`: dispatch through jump tables to read or update data/address register values as represented in the exception frame and live registers.
- `inc_areg`, `dec_areg`: apply effective-address postincrement/predecrement updates, including special one-byte alignment behavior for `%a7` and flags that support later rollback.
- `load_fpn1`, `load_fpn2`: copy an FP register into `FP_SRC` or `FP_DST`; `%fp0` and `%fp1` are read from stacked exception-frame slots, while `%fp2` through `%fp7` are read from live FPU registers using `fmovm.x`.
- `store_fpreg`: store `%fp0` into the selected FP register, preserving denorm/SNaN bit patterns by stack-copying for live FP registers.
- `facc_in_b/w/l/d/x` and `facc_out_b/w/l/d/x`: access-fault exits for failed data reads and writes of different operand sizes.
- `restore`, `rest_inc`, `rest_dec`: undo predecrement/postincrement address-register updates before converting an emulation frame into an access-error frame.

Core internal helpers referenced but implemented outside this chunk include `scale_to_zero_src`, `scale_to_zero_dst`, `scale_sqrt`, `addsub_scaler2`, `norm`, `ovf_res`, `unf_res`, `unf_res4`, `res_qnan`, `res_snan`, `res_qnan_1op`, `res_snan_1op`, `res_operr`, `_dcalc_ea`, `_dmem_read`, and `_real_access`.

## Control Flow

Most arithmetic routines follow a common pattern:

1. Save rounding precision/mode in `L_SCR3(%a6)`.
2. Inspect `STAG(%a6)` and, for two-operand operations, `DTAG(%a6)` to build an operand-type index.
3. If operands are normal or denormal, copy them into `FP_SCR0` and `FP_SCR1`, scale exponents to a safe range, and execute a hardware FPU operation such as `fdiv.x`, `fadd.x`, `fsqrt.x`, `fsglmul.x`, or `fsgldiv.x`.
4. Clear `%fpsr` before the operation, set `%fpcr` from the saved user rounding state, then clear `%fpcr` after execution to avoid leaking control-state changes.
5. Merge hardware status into `USER_FPSR(%a6)`, usually preserving `INEX2` and condition-code bits.
6. Compare the repaired exponent with precision-specific overflow/underflow boundaries.
7. If no exception is architecturally required, write the repaired exponent/sign back into the extended result and return it in `%fp0`.
8. If overflow or underflow is required, update exception/accrued bits, test `FPCR_ENABLE(%a6)`, optionally prepare an enabled-exception `EXOP` in `%fp1`, then call `ovf_res`, `unf_res`, or `unf_res4` for the default disabled-exception result.

Special operands are handled through dense jump tables keyed by operand tags. Tables such as `tbl_fmul_op`, `tbl_fdiv_op`, `tbl_fsglmul_op`, `tbl_fsgldiv_op`, `tbl_fadd_op`, and `tbl_fsub_op` encode all combinations of `NORM`, `ZERO`, `INF`, `QNAN`, `DENORM`, and `SNAN`. Their branches implement IEEE/6888x cases such as zero times infinity as `OPERR`, signaling NaNs through `res_snan`, quiet NaNs through `res_qnan`, infinity sign propagation, and signed-zero selection.

The underflow boundary checks are deliberately conservative. For results exactly at the minimum normalized boundary, routines often re-execute the operation with round-to-zero (`rz_mode`) to decide whether the pre-rounded result was truly tiny or merely rounded to the boundary. Add/subtract additionally inspect the mantissa for `0x8000000000000000` and `INEX2` before doing the RZ retry.

`fcmp` differs from arithmetic routines because it only sets condition codes. It uses hardware compare for ordinary values, suppresses the negative condition-code bit after NaN helper calls, and rewrites denorm operands as tiny normals when hardware comparison is safe. For same-sign norm/denorm comparisons where hardware ordering would not match the intended denorm relationship, it sets or clears the negative bit manually.

`get_packed` computes/fixes the effective address with `_dcalc_ea`, reads 12 bytes with `_dmem_read`, exits through `facc_in_x` on failure, returns immediately for packed INF/NaN/zero encodings, and otherwise calls `decbin` to convert BCD to binary extended precision.

`decbin` converts a normal packed decimal operand by decoding exponent digits, decoding mantissa digits into `%fp0`, adjusting appended or stripped zeros for large exponents, building a power-of-ten scale factor from `PTENRN`, `PTENRM`, or `PTENRP`, then multiplying or dividing by that scale. It maps final `INEX2` from the conversion multiply/divide into `INEX1/AINEX` in `USER_FPSR`.

`bindec` converts binary extended input into packed BCD through a multi-stage pipeline documented as A1 through A16: normalize denorms, compute an approximate decimal exponent `ILOG`, compute output digit length from the k-factor, build decimal scale, round the scaled value to an integer, adjust if the digit count is off by one, convert mantissa and exponent digits with `binstr`, write sign bits, and restore saved registers.

`facc_*` handlers are terminal exits. They call `restore` with the operand byte count, write an FSLW value into `EXC_VOFF(%a6)`, restore user-visible registers/control registers, reshape the stack into a 68060 access-error frame, set the supervisor transfer-mode bit when appropriate, and branch to `_real_access`.

## State And Persistence Behavior

The persistent state is the FPSP exception frame and scratch space rooted at `%a6`. This chunk reads and writes:

- operand tags `STAG(%a6)` and `DTAG(%a6)`;
- source/destination operands `SRC`, `DST`, `FP_SRC`, `FP_DST`, and scratch extended operands `FP_SCR0`, `FP_SCR1`;
- user floating-point state `USER_FPCR`, `USER_FPSR`, and `USER_FPIAR`;
- condition-code and exception subfields such as `FPSR_CC(%a6)`, `FPSR_EXCEPT(%a6)`, and `FPCR_ENABLE(%a6)`;
- stacked general and floating-point registers under `EXC_DREGS`, `EXC_A7`, `EXC_FPREGS`, `EXC_FP0`, and `EXC_FP1`;
- exception-frame fields such as `EXC_PC`, `EXC_SR`, `EXC_VOFF`, and `EXC_OPWORD`;
- conversion scratch values `L_SCR1`, `L_SCR2`, `L_SCR3`, `BINDEC_FLG`, and `SPCOND_FLG`.

The arithmetic routines carefully treat `%fpcr` and `%fpsr` as transient hardware work registers. They set `%fpcr` for the exact operation being emulated, clear `%fpsr` before hardware operations when they need clean status, merge selected status bits into `USER_FPSR`, and usually clear `%fpcr` afterward. Some conversion paths also clear `%fpsr` before return to avoid leaving internal inexact/accrued state behind.

Overflow and underflow behavior persists in `USER_FPSR`. Overflow paths OR in `ovfl_inx_mask`, which represents overflow plus accrued overflow/inexact state. Underflow paths set `unfl_bit` in `FPSR_EXCEPT` and may set inexact based on hardware status. Disabled exceptions return default results in `%fp0`; enabled exceptions additionally place a correctly biased exception operand in `%fp1`.

Register helper routines persist emulated data/address register modifications either in stacked frame slots (`EXC_DREGS`, `EXC_A7`, saved `%a6`) or live registers (`%d2`-`%d7`, `%a2`-`%a5`) depending on where the original architectural register is held during FPSP execution. `%a7` updates have special stack-alignment behavior for byte increments/decrements and set side-condition flags for later rollback.

Packed conversion state is scratch-only except for its final results and exception bits. `decbin` returns the converted binary value in `%fp0` and then `get_packed` stores it into `FP_SRC`. `bindec` writes the final packed decimal string into `FP_SCR0(%a6)` and may set `OPERR/AIOP` in `USER_FPSR` when requested precision or exponent representation exceeds packed decimal limits.

Access-error exits are intentionally persistent and non-returning. They undo address-register side effects, restore user-visible machine state, overwrite the current exception-frame layout with an access-error frame, and transfer control to the OS access-error handler through `_real_access`.

## Dependencies And Integration Points

This chunk depends on Motorola 68060 FPSP frame layout macros and constants, including operand offsets (`SRC_EX`, `SRC_HI`, `SRC_LO`, `DST_EX`, `FP_SCR0_EX`, etc.), operand tags (`NORM`, `ZERO`, `INF`, `QNAN`, `DENORM`, `SNAN`), rounding constants (`s_mode`, `d_mode`, `rz_mode`, `rm_mode`, `rp_mode`), FPSR/FPCR bit masks (`neg_bmask`, `z_bmask`, `inf_bmask`, `unfl_bit`, `inex2_bit`, `opaop_mask`, `ovfl_inx_mask`, `inx1a_mask`), and exception-frame offsets.

The arithmetic routines integrate with earlier/later FPSP code through shared helpers:

- scaling helpers normalize exponent ranges before hardware operations;
- result helpers create architected overflow, underflow, NaN, SNaN, and invalid-operation results;
- effective-address and memory-callout helpers fetch packed operands and report data access failures;
- OS branch-table stubs such as `_real_access` ultimately hand off terminal exceptions to the operating system.

The source-tree integration point is the Linux/m68k `arch/m68k/ifpsp060` package. The adjacent `README-SRC` explains that the source accompanies the precompiled Motorola `.sa` files used by the kernel. Any behavioral research should therefore connect this source to the binary support package and exception-entry table, not expect normal in-tree assembly of `src/pfpsp.S`.

The packed conversion tables `PTENRN`, `PTENRP`, and `PTENRM` are integration points for decimal conversion accuracy. They provide extended-precision powers of ten rounded to nearest, plus, or minus; `RTABLE` and `RBDTBL` choose which table and rounding mode to use based on signs and user rounding mode.

## Risks And Edge Cases

The largest risk is silent divergence from 68881/68882-visible behavior. Many branches exist solely to preserve exact legacy details: infinity j-bit priority, signed-zero result signs under directed rounding, NaN condition-code suppression in `fcmp`, denorm comparison ordering, and enabled-exception `EXOP` rebiasing by `0x6000`.

Exception-state handling is delicate. Routines mix hardware `%fpsr` snapshots with manual ORs into `USER_FPSR`; clearing `%fpcr` or `%fpsr` at the wrong time would change accrued exception state or leak internal rounding modes into subsequent emulation. Enabled underflow/overflow paths also recompute results in extended precision without disturbing previously captured inexact state.

Boundary underflow detection is easy to get wrong. The code distinguishes definite underflow, definite normal, and "may underflow" cases by re-running operations with RZ or inspecting mantissas and `INEX2`. Removing those retries would misclassify operands that round to the smallest normal value.

The operand-tag jump tables assume stable tag values and table widths. A wrong tag encoding or table index would branch into unrelated special-case code. Several table entries intentionally point back to the table label for unused combinations; executing one would be a serious decode/tag bug.

`bindec` contains an apparent self-loop at `sc_mul_err`, used when denormal scaled multiplication still underflows in a path the code treats as impossible or unrecoverable. If reachable, it would hang the emulator. This is a high-value test/review target for extreme denormal plus k-factor cases.

Packed decimal conversion is numerically fragile. It depends on exact powers of ten up to specified limits, directed rounding table selection, one-bit inexact compensation before `fint`, and fixed packed-decimal digit layout. Small changes can produce off-by-one decimal digits, wrong exponent signs, or incorrect `OPERR` on length overflow.

Access-error frame creation is architecture-sensitive. The `facc_*` paths manually move stack words, write FSLW/vector fields, and adjust transfer-mode bits. Incorrect size codes, `%a7` rollback, or supervisor/user detection would misreport memory faults to the OS or corrupt the interrupted context.

The source is not directly assembled in the normal build according to `README-SRC`. Tests that only build the kernel from precompiled `.sa` files will not catch source edits in this file; validation must compare behavior/source generation against the assembled support package if source changes are contemplated.

## Test Signals

Build-level signals are limited because `src/pfpsp.S` is not expected to assemble with GNU assembler in this tree. A practical source-alignment check is that the precompiled Motorola `.sa` package and any generated listings still correspond to these labels, tables, and branch targets.

Behavioral floating-point tests should exercise:

- normal, denormal, zero, infinity, QNaN, and SNaN operands for each visible instruction family;
- all rounding modes and extended/single/double precision selections;
- overflow disabled and enabled paths, including `EXOP` contents in `%fp1`;
- underflow disabled and enabled paths, including boundary cases that round to the smallest normal value;
- signed-zero rules for add/subtract, multiply/divide, square root, negate, and absolute value;
- invalid operations such as zero times infinity, zero divided by zero, infinity divided by infinity, adding opposite-signed infinities, subtracting same-signed infinities, and square root of negative nonzero values;
- `fcmp` condition codes for NaNs, denorm-vs-normal pairs of same and opposite signs, zeros, and infinities.

Packed decimal tests should cover packed INF/NaN/zero fast paths in `get_packed`, normal decimal-to-binary conversion across positive and negative exponents, table selection under RN/RZ/RM/RP, final `INEX1/AINEX` reporting, `bindec` k-factor positive/zero/negative cases, LEN clamping to 17, exponent digit overflow to `OPERR`, denormal input handling, and extreme values around `ILOG = -4933`.

Register-helper tests should cover every dispatch-table index for `fetch_dreg`, `store_dreg_l/w/b`, `inc_areg`, `dec_areg`, `load_fpn1`, `load_fpn2`, and `store_fpreg`, with special attention to `%a0`, `%a1`, `%a6`, `%a7`, `%fp0`, and `%fp1` because those use stacked exception-frame storage instead of only live registers.

Access-fault integration tests should inject read/write failures for byte, word, long, double, and extended operands; verify that `restore` undoes predecrement/postincrement effective-address updates; verify `%usp` handling for user-mode `%a7`; and check the final access-error frame fields handed to `_real_access`.
