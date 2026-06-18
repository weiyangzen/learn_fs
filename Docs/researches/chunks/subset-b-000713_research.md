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
