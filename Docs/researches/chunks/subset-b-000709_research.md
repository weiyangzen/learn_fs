# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/fpsp.S lines 16685-24785

## Scope

This chunk covers a large, middle-to-late section of the m68k 68060 Floating-Point Software Package assembly source. The range begins in the tail of `fdbcc` conditional-branch emulation, then includes complete handlers and shared helpers for:

- `ftrapcc` and `fscc` floating-point conditional instruction emulation.
- Dynamic `fmovm.x` register-mask moves and their private effective-address calculator.
- Control-register immediate `fmovm.l` loads.
- Effective-address correction for unimplemented FP and opclass-3 move-out paths.
- `_load_fop`, `fout`, and packed/extended/single/double/integer operand conversion paths.
- Integer and FP register-file accessors.
- Denormalization, rounding, normalization, type tagging, underflow and overflow default-result helpers.
- Packed decimal conversion in both directions through `get_packed`, `decbin`, `bindec`, and `binstr`.
- Data-access-fault exits (`facc_in_*`, `facc_out_*`) and `restore` for undoing address-register updates before building an access-error frame.

The assembly is not Ceph-specific at the algorithm level; it is architecture support code carried under the Ceph client source tree for the m68k FPSP. Its behavior is tightly tied to the exception-frame layout, scratch-stack offsets, FPCR/FPSR/FPIAR state, and 68881/68882/68040-compatible floating-point semantics expected by the m68k kernel port.

## Purpose

This code provides software emulation and exception-recovery support for floating-point instructions or operand forms that the 68060 does not execute directly. It consumes decoded exception-frame fields under `%a6`, emulates instruction side effects, updates stacked user FP state, and either returns to the caller for normal exception completion or marks special stack flags so the higher-level FPSP dispatcher can synthesize a trap, BSUN exception, memory access exception, or deferred supervisor-stack write.

The covered routines fall into several functional groups:

- Conditional FP instructions: `fdbcc`, `_ftrapcc`, and `_fscc` interpret FPSR condition codes, distinguish IEEE aware versus non-aware predicates, raise BSUN/AIOP where required, and update counters, destination bytes, or special trap flags.
- Move and operand plumbing: `fmovm_dynamic`, `fmovm_ctrl`, `_dcalc_ea`, `_calc_ea_fout`, `_load_fop`, and `fout` move values between stacked FP registers, integer registers, memory, and internal `FP_SRC`/`FP_DST` work areas.
- Numeric conversion and classification: `set_tag_x`, `set_tag_s`, `set_tag_d`, `unnorm_fix`, `norm`, `_denorm`, `dnrm_lp`, `_round`, `unf_res`, and `ovf_res` classify operands and construct IEEE-compatible rounded, denormalized, underflow, and overflow results.
- Packed decimal support: `get_packed` and `decbin` convert 68881/68882 packed decimal input to extended binary; `bindec` and `binstr` convert extended binary back to packed BCD for `fmove.p`.
- Fault recovery: `facc_in_*`, `facc_out_*`, `facc_finish`, and `restore` convert memory access failures detected during emulation into real m68k access-error frames while undoing any predecrement/postincrement side effects already applied by the emulator.

## Important APIs, Types, And Entry Points

### Conditional Instruction Emulation

`fdbcc_ogt` through `fdbcc_un` are the IEEE-aware tail of `fdbcc` predicate handling. They use the corresponding `fb*` predicate branch to test the loaded FPSR condition-code byte. A true condition returns without changing the counter. A false condition branches to `fdbcc_false`, which extracts the low three opcode bits to identify `Dn`, fetches it through `fetch_dreg`, decrements the low word, stores it back with `store_dreg_l`, and if the result is not `-1`, updates `EXC_PC` to `USER_FPIAR + 4 + L_SCR1` where `L_SCR1` holds the sign-extended displacement. `fdbcc_bsun` sets `SPCOND_FLG` to `fbsun_flg`.

`_ftrapcc` is exported. It reads the predicate from `EXC_CMDREG`, copies the stacked FPSR condition-code byte into the real `%fpsr`, and dispatches through `tbl_ftrapcc`. Predicate labels either return, set `USER_FPSR` BSUN/AIOP bits, branch to `ftrapcc_bsun`, or set `SPCOND_FLG` to `ftrapcc_flg` via `ftrapcc_trap`.

`_fscc` is exported and mirrors `_ftrapcc` predicate dispatch through `tbl_fscc`, but produces a byte result in `%d0`: `0x00` for false or `0xff` for true. `fscc_done` writes that byte either to a data register with `store_dreg_b` or to memory with `_dmem_write_byte`. Postincrement and predecrement memory forms are handled by `fscc_mem_inc` and `fscc_mem_dec`, which update the address register only after the byte write succeeds. `fscc_chk_bsun` suppresses the store when BSUN is enabled and sets `SPCOND_FLG` to `fbsun_flg`.

### FMOVM And Effective Address Helpers

`fmovm_dynamic` emulates dynamic-register-list `fmovm.x` forms where a data register supplies an 8-bit FP-register mask. It extracts the source data register from the extension word, fetches the mask with `fetch_dreg`, uses `tbl_fmovm_size` to compute byte count, calculates the effective address with `fmovm_calc_ea`, and then dispatches to move-in or move-out paths. It also handles the special supervisor `fmovm.x Dn,-(a7)` case by returning the size and mask to the caller when `SPCOND_FLG` is `mda7_flg`.

`tbl_fmovm_size` maps every 8-bit FP-register mask to byte count, using 12 bytes per extended FP register. `tbl_fmovm_convert` reverses mask ordering for predecrement stores, because predecrement `fmovm` register ordering is opposite of control and postincrement forms.

`fmovm_calc_ea` is a private effective-address decoder for dynamic `fmovm`. It uses the low six opcode bits to dispatch through `tbl_fea_mode` and supports address indirect, postincrement, predecrement, displacement, indexed, memory-indirect indexed, absolute short/long, PC-relative displacement, and PC-relative indexed modes. It advances `EXC_EXTWPTR` while fetching extension words with `_imem_read_word` or `_imem_read_long`. Data faults in memory-indirect EA calculation branch to `iea_dacc`; instruction-fetch faults branch to `iea_iacc`.

`fmovm_ctrl` emulates immediate `fmovem.l #<data>, {FPCR,FPSR,FPIAR}` forms. It decodes selected control registers from `EXC_EXTWORD`, sequentially reads immediate longwords from instruction memory, advances `EXC_EXTWPTR`, and stores results into `USER_FPCR`, `USER_FPSR`, and/or `USER_FPIAR`.

`_dcalc_ea` fixes the effective address for unimplemented FP and opclass-2 packed operands where the stacked EA is mostly correct but address-register updates or immediate-data handling still need to be applied. It sets `immed_flg` for immediate operands, updates `(An)+` through `inc_areg`, updates `-(An)` through `dec_areg`, and subtracts 8 from the stacked EA for extended/packed predecrement cases.

`_calc_ea_fout` fixes opclass-3 extended and packed move-out destinations. For `(An)+`, it returns the stacked EA and advances `An` by 12. For `-(An)`, it subtracts 8 from the stacked EA, stores that corrected address back, and writes it into the selected address register. `a7` updates set `mia7_flg` or `mda7_flg`.

### Operand Loading And Storing

`_load_fop` loads source and destination operands for unimplemented FP exceptions. It handles opclass `000` register-to-register and opclass `010` memory/data-register-to-FP forms. Dyadic operations load `FP_DST` via `load_fpn2`; source operands are loaded into `FP_SRC`. Tags are stored in `DTAG` and `STAG`.

For integer data-register sources, `opd_long`, `opd_word`, and `opd_byte` fetch with `fetch_dreg`, convert to extended in `%fp0`, store to `FP_SRC`, and set `STAG=ZERO` if the converted value is zero. `opd_sgl` fetches a single-precision value from a data register, classifies it with `set_tag_s`, and routes SNAN and DENORM through manual conversion helpers.

`fetch_from_mem` dispatches memory/immediate source loading by source type. `load_long`, `load_word`, `load_byte`, `load_sgl`, `load_dbl`, `load_ext`, and `load_packed` call `_dcalc_ea`, choose instruction-memory reads for immediate operands when `SPCOND_FLG=immed_flg`, and otherwise use `_dmem_read*` or `_dmem_read`. Faults exit through `facc_in_*` for data faults or `funimp_iacc`/`iea_iacc` for instruction fetch faults. Single and double denormals/SNANs are converted manually to extended representation so the emulator can avoid unwanted hardware exceptions while preserving type information.

`fout` is the shared opclass-3 move-out dispatcher. It decodes the destination format from `EXC_CMDREG` and branches to:

- `fout_byte`, `fout_word`, `fout_long`: convert extended source to integer using the requested rounding mode, merge FPSR exception/accrued bits into `USER_FPSR`, and write to `Dn` or memory.
- `fout_sgl`, `fout_dbl`: convert to single/double, explicitly detect underflow and overflow thresholds, generate default underflow/overflow results, write memory or `Dn` as appropriate, and return EXOP in `%fp1` when an enabled exception requires it.
- `fout_ext`: writes a 12-byte extended value after clearing the reserved 16-bit word and creates an underflow EXOP for denormal outputs when enabled.
- `fout_pack`: fetches static or dynamic k-factor, calls `bindec` to create packed BCD in `FP_SCR0`, normalizes zero packed results when k-factor is zero, handles SNAN by setting `snaniop2_mask`, and writes 12 bytes to memory or through `_mem_write2` for supervisor `-(a7)`.

### Register Accessors

`fetch_dreg` reads data or address registers by index `0..15`. The saved `d0`, `d1`, `a0`, `a1`, `a6`, and `a7` values are read from the exception frame; live `d2..d7` and `a2..a5` are read directly. `store_dreg_l`, `store_dreg_w`, and `store_dreg_b` write only data registers `d0..d7`, preserving upper bytes/words for byte and word stores.

`inc_areg` and `dec_areg` update address registers for postincrement and predecrement modes. They handle `a0`, `a1`, `a6`, and `a7` through stacked locations and `a2..a5` directly. For byte-sized `a7` updates, they adjust by two rather than one and set `mia7_flg` or `mda7_flg` so later fault paths can restore state correctly.

`load_fpn1` and `load_fpn2` copy FP registers into `FP_SRC` and `FP_DST`. FP0/FP1 are taken from stacked saved values; FP2..FP7 are moved from hardware FP registers. `store_fpreg` writes `%fp0` back to the selected FP register, using stack-mediated moves for FP2..FP7 to tolerate DENORM and SNAN values without taking a new exception.

### Numeric Helpers

`_denorm` and `dnrm_lp` denormalize an internal extended operand to a precision-specific threshold. They maintain guard, round, and sticky bits in `%d0{31:29}`. `dnrm_lp` has separate bitfield paths for shifts under 32, between 32 and 63, exactly 64, exactly 65, and greater than 65.

`_round` rounds an internal extended operand according to precision and mode in `%d1`, using existing or extracted guard/round/sticky bits. It supports round-to-nearest-even, round-to-zero, round-minus-infinity, and round-plus-infinity. `ext_grs` derives the proper GRS bits for single and double precision from the extended mantissa and any incoming sticky state.

`norm` left-shifts an extended mantissa until the high mantissa word has its leading bit set, returning the shift count. `unnorm_fix` converts an UNNORM extended operand into NORM, DENORM, or ZERO based on mantissa position and exponent capacity.

`set_tag_x`, `set_tag_d`, and `set_tag_s` classify extended, double, and single operands as `NORM`, `INF`, `QNAN`, `SNAN`, `DENORM`, `UNNORM`, or `ZERO` as applicable. `set_tag_x` also canonicalizes an "unnormalized zero" by clearing the exponent while preserving sign.

`unf_res` and `unf_res4` produce default underflow results. They convert to an internal sign/exponent format, denormalize with `_denorm`, round with `_round`, restore normal sign layout, set zero condition codes in the return byte when the result becomes zero, and set accrued underflow when inexact underflow occurred. `unf_res4` is the single-round-precision, extended-denormal variant used by single multiply/divide emulation.

`ovf_res` and `ovf_res2` build default overflow results from sign, rounding precision, and rounding mode. They index `tbl_ovfl_cc` and `tbl_ovfl_result`, returning condition-code bits in `%d0` and a pointer to an extended-format default result in `%a0`.

### Packed Decimal Conversion

`get_packed` computes a 12-byte packed operand address with `_dcalc_ea`, reads it into `FP_SRC`, returns directly for packed INF/NAN encodings, recognizes packed zero, and otherwise calls `decbin` to convert packed decimal to binary extended precision.

`decbin` copies the packed BCD operand into `FP_SCR0`, computes the decimal exponent from sign/exponent nibbles, converts the mantissa digits to a binary FP accumulator, adjusts for leading or trailing decimal zeros when the exponent magnitude is greater than 27, chooses a power-of-ten table based on user rounding mode and operand/exponent signs, scales by `10^exp`, and sets `INEX1/AINEX` in `USER_FPSR` when the final multiply/divide was inexact.

`RTABLE` selects the directed rounding mode used by `decbin` power-table construction. `PTENRN`, `PTENRP`, and `PTENRM` are extended-precision powers of ten rounded to nearest, plus, or minus for exponents `1,2,4,...,4096`.

`bindec` converts extended binary input to 68881/68882 packed decimal. It saves FP/data registers, normalizes denormal inputs when needed, computes an approximate base-10 exponent `ILOG` using `PLOG2`/`PLOG2UP1`, calculates output digit length from the k-factor, calculates decimal scaling with `RBDTBL` and the power-of-ten tables, scales the magnitude, rounds to an integer with `fint`, adjusts `ILOG` and length if the integer has too few or too many digits, converts mantissa and exponent with `binstr`, writes sign bits, and sets OPERR/AIOP on invalid length/exponent cases.

`binstr` converts a 64-bit binary fraction in `%d2:%d3` into BCD digits at `%a0`. It repeatedly multiplies the fraction by 10 using separate multiply-by-8 and multiply-by-2 shift paths, collects the digit from overflow bits, packs two BCD digits per byte, and preserves `%d0..%d7`.

### Access Fault Exit Helpers

`facc_in_b`, `facc_in_w`, `facc_in_l`, `facc_in_d`, and `facc_in_x` handle failed data reads of byte, word, long, double, and extended/packed operands. `facc_out_b`, `facc_out_w`, `facc_out_l`, `facc_out_d`, and `facc_out_x` handle failed writes. Each passes the operand size in `%d0`, calls `restore` to undo postincrement/predecrement address-register effects, sets an FSLW code in `EXC_VOFF`, and falls into `facc_finish`.

`facc_finish` rewrites the current unimplemented-FP exception frame into an access-error frame. It restores user FP and integer registers, unlinks `%a6`, reshuffles stack words for SR/PC/EA/FSLW, sets vector offset `0x4008`, marks supervisor transfer mode in the FSLW when the old SR says supervisor mode, and jumps to `_real_access`.

`restore` decodes the original effective-address mode. For postincrement it subtracts the operand size from the selected address register; for predecrement it negates the size and uses the same table, effectively adding it back. `ri_a7` has special handling for user-mode stack pointer restoration through `%usp` and avoids changing `a7` in cases where the emulator did not update it.

## Control Flow

Conditional instruction emulation follows a common pattern:

1. The caller has already decoded the FP instruction into `EXC_CMDREG`, `EXC_OPWORD`, `FPSR_CC`, and scratch slots.
2. `_ftrapcc` or `_fscc` loads the stacked condition codes into `%fpsr`.
3. A 32-entry predicate table selects the predicate handler.
4. The handler uses an `fb*` instruction to evaluate the predicate with hardware condition-code semantics.
5. Non-aware and signalling predicates check `nan_bit` and set `bsun_mask+aiop_mask` in `USER_FPSR` when required.
6. If BSUN is enabled, the routine sets `SPCOND_FLG=fbsun_flg` and returns without completing normal side effects.
7. Otherwise `_ftrapcc` sets `ftrapcc_flg` for true predicates, while `_fscc` writes the boolean byte result to register or memory.

`fmovm_dynamic` performs more involved control flow. It extracts a dynamic mask, computes byte size and EA before deciding that mask zero is a no-op, and then routes through move-out or move-in. Move-out builds a contiguous stack buffer of selected 12-byte FP register images and uses `_dmem_write`; move-in reads a contiguous memory buffer with `_dmem_read` and then stores selected FP registers. The special supervisor `-(a7)` path returns early because writing to the active supervisor stack could corrupt the exception frame.

Operand loading through `_load_fop` is driven by opclass and operand type:

1. Register-register opclass loads `FP_DST` only for dyadic operations, then `FP_SRC`.
2. Memory/register-source opclass loads destination register when needed, then dispatches by source type.
3. Data-register integer/single sources avoid memory access and use `fetch_dreg`.
4. Memory and immediate sources call `_dcalc_ea` after source size is known, because address-register side effects depend on operand size.
5. Type-specific loaders classify, normalize, or manually convert denormals/SNANs.
6. Any failed data access diverts to `facc_in_*`; failed immediate instruction access diverts to instruction-access recovery.

Move-out through `fout` has separate paths by destination format. Integer outputs use hardware `fmov.{b,w,l}` to perform conversion under the requested FPCR and then store to a data register or memory. Single/double outputs first check exponent thresholds to avoid relying solely on hardware exceptions; underflow and overflow paths compute the architected default result before storing, then decide whether an enabled exception requires an EXOP return. Extended/packed outputs use corrected EA handling and supervisor-stack avoidance logic.

Packed conversion has two multi-stage algorithms:

- `decbin` interprets packed decimal as mantissa digits plus a signed exponent, reduces large exponent magnitude by appending/stripping zeros from the mantissa, builds a rounded power-of-ten factor from the selected table, and scales the mantissa by multiply or divide.
- `bindec` estimates decimal exponent, calculates k-factor-constrained digit length, scales the binary input to a decimal integer, uses `fint` to round under user mode, validates digit length, then converts mantissa and exponent to packed BCD bytes.

Fault handling is late-bound. Many routines optimistically update address registers or stack scratch state while emulating. If a memory helper later signals a fault in `%d1`, the relevant `facc_*` or `fmovm_*_err` path calls `restore` or otherwise fixes special registers before handing the frame to `_real_access`.

## State And Persistence Behavior

There is no filesystem or durable persistence in this chunk. The persistent-looking state is CPU architectural state staged in the exception frame and scratch area:

- `USER_FPCR`, `USER_FPSR`, and `USER_FPIAR` are the stacked user floating-point control/status/instruction-address registers. Many routines temporarily write hardware `%fpcr` and `%fpsr` and then merge exception/accrued bits back into `USER_FPSR`.
- `EXC_PC`, `EXC_EA`, `EXC_OPWORD`, `EXC_EXTWORD`, `EXC_EXTWPTR`, `EXC_CMDREG`, `EXC_SR`, `EXC_VOFF`, `EXC_DREGS`, `EXC_A7`, `EXC_FPREGS`, `EXC_FP0`, and `EXC_FP1` describe the interrupted instruction, saved registers, and exception-frame fields.
- `FP_SRC`, `FP_DST`, `FP_SCR0`, `FP_SCR1`, `FP_SCR2`, `L_SCR1`, `L_SCR2`, and `L_SCR3` are temporary work areas used for operands, converted results, power/exponent intermediates, and saved control words.
- `STAG` and `DTAG` hold operand type tags used by later arithmetic or move-out paths.
- `SPCOND_FLG` communicates special conditions to the caller, including BSUN, ftrapcc trap, immediate operand, supervisor stack postincrement/predecrement, and deferred memory writes.
- Address-register state may live either in the exception frame (`a0`, `a1`, `a6`, `a7`) or in live CPU registers (`a2..a5`). Helpers must update or restore the correct location consistently.

State changes are deliberately ordered around memory faults. For example, `fscc_mem_inc` and `fscc_mem_dec` write the result byte before updating the address register. In contrast, `_dcalc_ea` and `fmovm_calc_ea` may update address registers during EA calculation, so access-error paths call `restore` to undo them.

Rounding and exception state is staged carefully. `_round` sets inexact bits in `USER_FPSR`; `fout_sgl`/`fout_dbl` set overflow, underflow, inexact, and accrued bits before deciding whether enabled exceptions require EXOP; `decbin` maps final inexact work from an internal `INEX2` occurrence to `INEX1/AINEX` for packed-input conversion; `bindec` clears FPSR at several stages to prevent intermediate inexact bits from leaking except where explicitly folded into output decisions.

## Dependencies And Integration Points

This chunk depends on local FPSP assembly definitions outside the range:

- Exception-frame and scratch offsets such as `EXC_*`, `USER_*`, `FP_SRC`, `FP_DST`, `FP_SCR*`, `L_SCR*`, `FPSR_*`, `FPCR_ENABLE`, `SPCOND_FLG`, `STAG`, and `DTAG`.
- Constants and masks including `NORM`, `ZERO`, `DENORM`, `UNNORM`, `INF`, `QNAN`, `SNAN`, `bsun_mask`, `aiop_mask`, `snaniop2_mask`, `opaop_mask`, `ovfl_inx_mask`, `ovfinx_mask`, `inx2a_mask`, `inx1a_mask`, precision/mode constants, exponent thresholds, and bias constants.
- Memory and instruction access helpers: `_dmem_read`, `_dmem_read_byte`, `_dmem_read_word`, `_dmem_read_long`, `_dmem_write`, `_dmem_write_byte`, `_dmem_write_word`, `_dmem_write_long`, `_mem_write`, `_mem_write2`, `_imem_read`, `_imem_read_word`, and `_imem_read_long`.
- Higher-level exception exits: `iea_iacc`, `iea_dacc`, `funimp_iacc`, and `_real_access`.
- Arithmetic routines and entry points outside this range that call these helpers, such as unimplemented-instruction dispatch, arithmetic emulation, and special-condition frame fixup.

The exported labels in this range are integration points for the broader FPSP file:

- `_ftrapcc`, `_fscc`, `fmovm_dynamic`, `fmovm_calc_ea`, `fmovm_ctrl`, `_dcalc_ea`, `_calc_ea_fout`, `_load_fop`, `fout`.
- `fetch_dreg`, `store_dreg_l`, `store_dreg_w`, `store_dreg_b`, `inc_areg`, `dec_areg`.
- `load_fpn1`, `load_fpn2`, `store_fpreg`.
- `_denorm`, `dnrm_lp`, `_round`, `norm`, `unnorm_fix`, `set_tag_x`, `set_tag_d`, `set_tag_s`, `unf_res`, `unf_res4`, `ovf_res`, `ovf_res2`.
- `get_packed`, `decbin`, `bindec`, `binstr`, and the `PTENRN`/`PTENRP`/`PTENRM` power tables.

At the kernel integration level, the most important contract is that these routines return with the exception frame in the shape expected by the outer FPSP handler. Normal returns mean emulation completed or staged a result. Special flag returns mean the caller must synthesize BSUN, ftrapcc, memory-write, or access-error behavior.

## Risks And Edge Cases

- Predicate emulation is table-driven and duplicated across `ftrapcc` and `fscc`; a wrong table index or reversed IEEE aware/non-aware predicate would silently change NaN and BSUN behavior.
- BSUN handling depends on both setting `USER_FPSR` bits and checking `FPCR_ENABLE`. A path that stores an `fscc` result before recognizing enabled BSUN would violate architectural side effects; the current code avoids this through `fscc_chk_bsun`.
- Address-register updates are fragile because some registers are stacked and others are live. `a7` is especially sensitive: byte increments/decrements are word-aligned, user `usp` restoration differs from supervisor mode, and supervisor `-(a7)` move-out is deferred to avoid corrupting the frame.
- `fmovm_calc_ea` supports complex 68020-style memory-indirect modes. Instruction-pointer advancement, base/index suppression, word/long displacement sign extension, and data-fault address reporting are all high-risk areas.
- Several paths intentionally use real FPU instructions while exceptions are blocked or FPSR is cleared. Any missed FPCR/FPSR restore can leak rounding mode or status into later emulation.
- Single/double DENORM and SNAN loading is manually reconstructed into extended format. Bitfield offsets for signs, quiet/signalling bits, and mantissas are correctness-critical.
- `_round` and `_denorm` rely on GRS bits in the top three bits of `%d0` and scratch aliases `GRS=L_SCR2`, `FTEMP_LO2=L_SCR1`. Callers must not expect those scratch words to survive.
- `fout_pack` comments acknowledge that `bindec` can scramble `FP_SRC` for denormal inputs. That coupling is a maintenance risk if later code assumes `FP_SRC` remains intact after packed conversion.
- `bindec` contains an apparent infinite self-branch at `sc_mul_err`. It is likely a historical "should not happen" trap, but if reached for a denormal scaling edge case it would hang the emulator.
- Packed decimal conversion uses directed rounding tables and special exponent-length checks. Off-by-one errors in `LEN`, `ILOG`, or the `10^LEN` comparisons can produce non-68881-compatible decimal strings.
- Access-error frame construction in `facc_finish` manually rewrites stack words after `unlk %a6`; any exception-frame layout mismatch with the surrounding kernel ABI would corrupt trap delivery.

## Test Signals

Useful validation should focus on architectural side effects rather than only numeric outputs:

- For all 32 `ftrapcc` and `fscc` predicates, test FPSR condition-code combinations including ordered, unordered, zero, negative, equal, and NaN. Verify true/false result, `SPCOND_FLG`, BSUN/AIOP bits, and suppression of `fscc` stores when BSUN is enabled.
- For `fdbcc`, verify counter decrement, loop branch PC calculation from `USER_FPIAR + 4 + displacement`, and no decrement when the predicate is true.
- For `fscc`, test Dn destination, ordinary memory destination, `(An)+`, `-(An)`, failed byte write, and `a7` byte-size alignment behavior.
- For `fmovm_dynamic`, test zero masks, full masks, sparse masks, predecrement mask reversal, move-in and move-out ordering, access faults during `_dmem_read`/`_dmem_write`, and supervisor `fmovm.x Dn,-(a7)` special return.
- For `fmovm_calc_ea`, test address indirect, displacement, indexed, PC-relative, absolute short/long, memory-indirect pre/postindexed, suppressed base/index, word and long displacements, and instruction/data access fault exits.
- For `_load_fop`, test register, immediate, and memory sources for byte/word/long/single/double/extended/packed. Include zero, normal, denormal, unnormal, infinities, QNAN, and SNAN values.
- For `fout`, test integer conversion rounding modes, single/double underflow and overflow thresholds, enabled versus disabled UNFL/OVFL/INEX exceptions, EXOP return in `%fp1`, extended denormal move-out underflow, packed static and dynamic k-factors, and memory-write faults.
- For `_round`, `_denorm`, `unf_res`, and `ovf_res`, compare against known 68881/68882 or FPSP vectors for RN/RZ/RM/RP and single/double/extended precision.
- For packed conversions, round-trip representative `fmove.p` values: zero with exponent, positive/negative mantissa and exponent, long digit strings, k-factor > 17, k-factor <= 0, denormal inputs, large exponents requiring `PTEN*` tables, and INF/NAN encodings.
- For `facc_finish` and `restore`, inject failures after predecrement/postincrement updates and verify final access-error frame PC, EA, FSLW size/direction bits, supervisor transfer bit, and restored address-register values.
