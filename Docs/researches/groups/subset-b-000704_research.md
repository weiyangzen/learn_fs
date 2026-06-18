# subset-b-000704 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/ssinh.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/ssinh.S

Purpose: implements the Motorola 68040 FPSP software routine for `fsinh`, with `ssinh` handling finite normalized inputs and `ssinhd` handling denormalized inputs. The routine computes `sinh(X)` in `%fp0` from the extended-precision operand pointed to by `%a0`, preserving the FPSP contract that common exception transfer code handles final inexact/overflow posting.

Important APIs/types/functions: exported labels are `ssinh` and `ssinhd`. `ssinhd` immediately branches to `t_extdnrm`, because denormalized `sinh(x)` is treated as `x` with denormal/inexact handling delegated. `ssinh` calls shared exponential helpers `setoxm1` for the normal range and `setox` for the large-but-not-overflow range, then exits through `t_frcinx` or `t_ovfl`. Constants `T1` and `T2` split `16381*log(2)` into leading/trailing terms for accurate large-argument reduction.

Control flow: `ssinh` loads the input, compacts the sign/exponent/high mantissa into `%d0`, and compares `|X|` against two thresholds. For `|X| <= 16380*log(2)`, it computes `z = expm1(|X|)` and returns `sign(X) * 0.5 * (z + z/(1+z))`. For `16380*log(2) < |X| <= 16480*log(2)`, it subtracts split `16381*log(2)` and computes `sign(X)*2^16380*exp(reduced)`. Beyond that it branches to `t_ovfl`.

State and persistence: no persistent state is owned. The routine uses `%a0` as the operand/scratch pointer, `%a1` to preserve the compacted original sign, `%d1` for the saved user FPCR value, the FPU stack for temporary extended values, and the FPSP scratch frame indirectly through `setox`/`setoxm1`.

Dependencies/integration: depends on `fpsp.h` frame/register offsets and on common FPSP routines `setox`, `setoxm1`, `t_frcinx`, `t_ovfl`, and `t_extdnrm`. It is dispatched by `tbldo.S` for `fsinh` normal and denormal source tags.

Risks: correctness relies on exact threshold constants, split-log constants, and restoring the user's FPCR only for the final operation that should raise user-visible exceptions. The routine stores `%fp0` back through `%a0` before calling exponential helpers; callers must provide a valid FPSP scratch operand area. Boundary values around the two large-argument thresholds are the highest-risk cases.

Test signals: exercise denormal input, signed zero, small finite values, normal positive/negative ranges, values just below and above `16380*log(2)`, values near `16480*log(2)`, overflow sign propagation, and FPCR rounding/inexact behavior through `t_frcinx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/ssinh.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/stan.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/stan.S

Purpose: implements FPSP `ftan`, with `stan` computing tangent for normalized finite operands and `stand` forwarding denormal handling. It provides both the fast table-reduction path for common inputs and a multi-iteration high-magnitude argument reduction path.

Important APIs/types/functions: exported labels are `stan`, `stand`, and the shared `PITBL` table of split `N*pi/2` values for `-32 <= N <= 32`. Local constants include polynomial coefficients `TANP1..TANP3` and `TANQ1..TANQ4`, `TWOBYPI`, `INVTWOPI`, and split `2*pi` constants. Common exits are `t_extdnrm` and `t_frcinx`.

Control flow: `stand` branches to `t_extdnrm`. `stan` loads `%fp0`, forms a compact absolute magnitude, returns `X` for `|X| < 2^-40`, uses `PITBL` when `|X| < 15*pi`, and otherwise enters `REDUCEX`. The fast path converts `X*2/pi` to integer `N`, subtracts split `N*pi/2`, derives the odd/even quadrant bit, and evaluates `tan(r)` as `U/V` for even quadrants or `-V/U` for odd quadrants. The slow path repeatedly reduces large arguments using scaled `2/pi`, scaled split `pi/2`, and a compensated `(R,r)` remainder until the fast polynomial can be used.

State and persistence: no persistent state. Uses FPSP scratch offsets `INARG`, `TWOTO63`, `ENDFLAG`, and `N`; saves `%fp2-%fp5` and `%d2` during slow reduction. `%d1` carries the user FPCR value restored before the final floating operation.

Dependencies/integration: included by the FPSP unimplemented-instruction flow and selected from `tbldo.S` for `ftan`. It depends on `fpsp.h` scratch offsets and exception exits. The polynomial result is left in `%fp0` and final exception status is delegated to `t_frcinx`.

Risks: argument reduction is precision-sensitive, especially the table address calculation, the odd-quadrant bit derived from the rotated integer multiple, and the special pre-reduction for the largest compact exponent. Any corruption of `%fp0/%fp1` as a compensated remainder pair in `REDUCEX` can produce quadrant errors. The slow path has many scratch-register assumptions.

Test signals: cover tiny inputs, denormal inputs, all signs, values around multiples of `pi/2`, near `15*pi`, very large finite operands, odd/even quadrant transitions, FPCR rounding modes, inexact flag propagation, and monotonicity/ULP checks near zeros and vertical asymptotes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/stan.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/stanh.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/stanh.S

Purpose: implements FPSP `ftanh`, with `stanh` for normalized finite inputs and `stanhd` for denormalized inputs. The routine computes `tanh(X)` in `%fp0` while preserving sign and exception behavior expected by 68881/68882-compatible software.

Important APIs/types/functions: exported labels are `stanh` and `stanhd`. It uses scratch aliases `X`, `SGN`, and `V`, range table `BOUNDS1` for `2^-40` and `(5/2)*log(2)`, and calls shared exponential helpers `setoxm1` and `setox`. Common exits are `t_extdnrm` and `t_frcinx`.

Control flow: denormal input jumps to `t_extdnrm`. For `2^-40 < |X| < (5/2)*log(2)`, the routine computes `Y=2|X|`, `Z=expm1(Y)`, and returns `sign(X)*Z/(Z+2)`. For larger inputs below `50*log(2)`, it computes `exp(2|X|)` and returns `sign - sign*2/(exp(Y)+1)`. For huge inputs it returns `sign - sign*epsilon`; for tiny normalized inputs it returns the source value.

State and persistence: no persistent state. It stores a copy of the input in FPSP scratch memory, keeps the sign in `SGN`, and uses `%d1` as the saved FPCR restored before the final visible arithmetic operation.

Dependencies/integration: depends on `fpsp.h`, `setox`, `setoxm1`, `t_frcinx`, and `t_extdnrm`. It is selected by `tbldo.S` for normal and denormal `ftanh` source classes.

Risks: the code manipulates the extended exponent directly to form `2|X|`; malformed scratch state or unexpected source format would be dangerous. Boundary behavior around `2^-40`, `(5/2)*log(2)`, and `50*log(2)` determines whether inexact and saturation behavior match hardware expectations.

Test signals: verify denormal and tiny inputs return `X`, moderate values use the expm1 formula, large positive/negative values approach signed one without premature overflow, threshold equality cases, signed zero behavior, FPCR rounding modes, and inexact/accrued flags via `t_frcinx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/stanh.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sto_res.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sto_res.S

Purpose: stores FPSP function results into the user-requested floating-point destination register after a software-emulated function completes. `sto_res` stores the primary result from `%fp0`; `sto_cos` stores the cosine half of `fsincos` from `%fp1`.

Important APIs/types/functions: exported labels are `sto_res` and `sto_cos`. They decode destination register fields from `CMDREG1B`: `sto_res` uses bits `{#6:#3}`, while `sto_cos` uses bits `{#13:#3}`. For registers `%fp0-%fp3`, they write the saved user register slots (`USER_FP0`..`USER_FP3`); for `%fp4-%fp7`, they build a dynamic `fmovemx` mask and move directly.

Control flow: each entry extracts the destination register number, branches to explicit `%fp0-%fp3` cases for saved-frame copies, or pushes `%fp0`/`%fp1` and restores it through a computed FPU dynamic mask for higher registers. It returns to the unimplemented-instruction handler, which later restores saved registers and posts exceptions.

State and persistence: no persistence. The only state updated is the FPSP local exception frame's saved `USER_FPn` images or the live higher-numbered FPU destination register.

Dependencies/integration: depends on `fpsp.h` command register and saved-register offsets. Called by `x_unimp.S` after `do_func` unless `STORE_FLG` suppresses result storage. `sto_cos` supports `ssincos`-style dual outputs.

Risks: destination bitfield decoding must match the 68040 command word layout. If `%fp0-%fp3` saved copies are not updated, later exception cleanup would restore stale values and lose the computed result. Dynamic masks for `%fp4-%fp7` depend on the `7 - dest` convention used by `fmovemx`.

Test signals: test all eight destination FP registers for normal monadic results, all `fsincos` cosine destination encodings, preservation of `%d2/%a0` caller assumptions, and restoration paths that reload `%fp0-%fp3` from `USER_FPn`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sto_res.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/stwotox.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/stwotox.S

Purpose: implements FPSP exponential base routines for `ftwotox` (`2**X`) and `ftentox` (`10**X`), including denormal entries. Results are returned in `%fp0` with common FPSP exception exits handling overflow, underflow, and inexact behavior.

Important APIs/types/functions: exported labels are `stwotox`, `stwotoxd`, `stentox`, and `stentoxd`. It defines range constants `BOUNDS1`/`BOUNDS2`, log conversion constants, polynomial coefficients `EXPA1..EXPA5`, `HUGE`, `TINY`, and a 64-entry `EXPTBL` table storing split approximations to `2^(j/64)`.

Control flow: denormal entries return `1+X`. `stwotox` bounds-checks `|X|`, computes `N=round(64X)`, splits `N` into `64(M+M')+J`, fetches `2^(J/64)` from `EXPTBL`, computes reduced `R=(X-N/64)*log(2)`, and jumps to `expr`. `stentox` similarly computes `N=round(X*64*log2(10))`, uses split `log10(2)/64` to reduce, multiplies by `log(10)`, then shares `expr`. `expr` evaluates `exp(R)-1` and reconstructs the scaled result using `FACT1`, `FACT2`, and `ADJFACT`. Large positive inputs branch to `t_ovfl`; large negative inputs branch to `t_unfl`; tiny inputs return `1+X`.

State and persistence: no persistent state. Scratch aliases `N`, `X`, `ADJFACT`, `FACT1`, and `FACT2` hold decomposition state and scaled table values. `%d1` is restored to FPCR immediately before the final multiply that should expose user rounding/exceptions.

Dependencies/integration: depends on `fpsp.h` and common exits `t_unfl`, `t_ovfl`, and `t_frcinx`. `tbldo.S` dispatches `ftwotox` and `ftentox` source classes here. The routines share mathematical structure with other FPSP exponential helpers.

Risks: reconstruction is sensitive to off-by-one errors in `N` splitting, table displacement `J*16`, and exponent adjustments in `FACT1/FACT2/ADJFACT`. The code directly clears the input sign byte before underflow/overflow exits because those handlers expect positive magnitude, so sign handling must be kept in sync with common exception code.

Test signals: cover denormal and tiny inputs, base-2 and base-10 normal ranges, exact integer exponents, threshold values near `16480` and `16480*log2/log10`, large positive overflow, large negative underflow, all rounding modes, and ULP checks across table bucket boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/stwotox.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/tbldo.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/tbldo.S

Purpose: defines the primary monadic FPSP dispatch table `tblpre`. The table maps a combined opcode/source-tag index to the correct software routine or special-case handler for unimplemented floating-point instructions.

Important APIs/types/functions: exported symbol is `tblpre`. Entries point to math routines such as `ssinh`, `stanh`, `stan`, `stwotox`, `stentox`, `scosh`, `sacos`, `ssin`, `scos`, log routines, integer-conversion routines, `ssincos`, and dyadic generic entries such as `pmod`, `prem`, and `pscale`. Special handlers include `szero`, `sinf`, `sone`, `src_nan`, `serror`, `t_operr`, `t_dz2`, `ld_pone`, `ld_pinf`, and `ld_ppi2`.

Control flow: this file is data-only. The caller, normally `do_func`, uses a 10-bit index where the upper seven bits are opcode and lower three bits are source tag. Normal, zero, infinity, NaN, denormal, and invalid tag cases have separate entries, allowing common special values to bypass general algorithms.

State and persistence: no mutable or persistent state. The table is static read-only dispatch data assembled into the FPSP text/data image.

Dependencies/integration: tightly integrated with `do_func.S`, `get_op.S`, and all function implementations referenced by the table. The table layout is a contract: changing opcode order or source-tag meaning without updating the decoder will dispatch to incorrect routines.

Risks: because this is a positional table, missing or misordered entries cause silent incorrect emulation. Many unsupported opcode/tag combinations intentionally point to `serror`; accidental replacement with a real function would mask illegal instruction conditions. The repeated `fsincos` opcode range must stay consistent with hardware encodings.

Test signals: validate every documented opcode/tag pair against expected target labels, illegal-extension opcodes against `serror`, normal/zero/inf/NaN/denormal dispatch for functions in this subset, and `fsincos` opcode variants across `$30-$37`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/tbldo.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/util.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/util.S

Purpose: provides shared FPSP helper routines for overflow/underflow result selection, instruction decoding, opcode reads, destination-format/rounding-precision lookup, and integer data-register writeback.

Important APIs/types/functions: exported labels are `ovf_r_k`, `ovf_r_x2`, `ovf_r_x3`, `ovf_res`, `get_fline`, `g_rndpr`, `g_opcls`, `g_dfmtou`, `unf_sub`, and `reg_dest`. Static tables `tblovfl` and `tblunf` select results by precision and rounding mode. Result constants encode infinities, largest finite values, zeros, and smallest denormals in internal extended format.

Control flow: overflow helpers choose precision from kernel exception context, opclass, force-precision fields, destination format, or FPCR; `ovf_res` combines precision and rounding mode into a table dispatch and writes the selected internal extended result while preserving sign. `get_fline` reads the interrupted opcode through `mem_read`. `g_rndpr`, `g_opcls`, and `g_dfmtou` decode E1/E3 command words. `unf_sub` mirrors overflow selection for catastrophic underflow. `reg_dest` indexes a table of byte/word/long write handlers for `D0-D7`.

State and persistence: no persistence. It mutates the current FPSP frame: `FPSR_CC`, `USER_FPSR`, `LOCAL_EX/HI/LO`, and saved `USER_D0/USER_D1` where needed. Writes to `D2-D7` go directly to live data registers because only `D0-D1/A0-A1` are saved in the local frame.

Dependencies/integration: depends on `fpsp.h` bit definitions and on `mem_read`. Called by overflow, underflow, store, operand-error, and signaling-NaN handlers. Its decoding helpers are shared by code that must distinguish opclass 3 move-out instructions from register-destination operations.

Risks: table indexes pack precision in bits `{3:2}` and rounding mode in bits `{1:0}`; decoding errors change IEEE-visible results. The E1/E3 split is subtle and hardware-specific. `reg_dest` assumes `L_SCR1` contains correctly aligned data and that only `D0/D1` need saved-frame writes.

Test signals: check overflow result matrices for extended/single/double across RN/RZ/RM/RP and signs, underflow zero/smallest-denorm matrices, `g_rndpr` for FPCR and force-precision cases, `g_dfmtou` destination formats, `get_fline` fault propagation via `mem_read`, and all `reg_dest` register/size combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/util.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_bsun.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_bsun.S

Purpose: implements `fpsp_bsun`, the FPSP entry for branch/set-on-unordered exceptions. It preserves 68881/68882 compatibility by copying the exception PC into the saved user FPIAR before delegating to the real kernel handler.

Important APIs/types/functions: exported label is `fpsp_bsun`. It saves `%d0-%d1/%a0-%a1`, `%fp0-%fp3`, and `%fpcr/%fpsr/%fpiar`, writes `EXC_PC` to `USER_FPIAR`, restores state, `frestore`s the FPU state frame, unlinks, and branches to `real_bsun`.

Control flow: linear handler: allocate local frame, save FPU state and volatile registers, update FPIAR compatibility state, restore everything, then tail-call the OS-level `real_bsun` handler.

State and persistence: no persistence. It mutates only the exception-local saved FPIAR slot before restoring user-visible FPU control registers.

Dependencies/integration: depends on `fpsp.h` frame offsets and the external `real_bsun` kernel entry. The real handler is expected to perform remaining corrective behavior described by the 68040 manual.

Risks: incorrect stack/frame offsets would corrupt the exception frame before transferring to the kernel. Because the code restores FPU state before `real_bsun`, any required FPSP-side state changes must be completed before the branch.

Test signals: trigger BSUN with unordered comparisons, verify FPIAR equals the faulting PC, ensure all saved general/FPU registers are restored, and confirm the OS handler receives the expected integer exception frame.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_bsun.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_fline.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_fline.S

Purpose: handles F-line exceptions that may represent unimplemented floating-point instructions, malformed `fmovecr`, or true illegal F-line instructions. It redirects unimplemented instruction vectors to `fpsp_unimp` and converts one special illegal-frame `fmovecr` case into the unimplemented-instruction path.

Important APIs/types/functions: exported label is `fpsp_fline`. External targets are `real_fline`, `fpsp_unimp`, `uni_2`, `mem_read`, and `fpsp_fmt_error`.

Control flow: before linking a frame, it checks `EXC_VEC-4(%sp)` for the unimplemented vector and branches to `fpsp_unimp` if present. Otherwise it adjusts the stack to account for a shorter frame, saves a local frame, reads the F-line and command word via `mem_read`, and checks for coprocessor id 1 plus `fmovecr` opcode. If matched, it synthesizes an unimplemented fsave frame (`VER_40` or `VER_41`), rewrites SR/PC/vector/EA/CMDREG fields, sets `UFLAG`, restores registers, and branches to `uni_2`. Non-matching instructions restore state and branch to `real_fline`.

State and persistence: no persistence. It rewrites the exception stack frame and FPSP command fields only for the emulated `fmovecr` conversion path.

Dependencies/integration: depends on `fpsp.h` frame constants, `mem_read` for fault-safe instruction fetch, `fpsp_unimp`/`uni_2` for software emulation, and `real_fline` for true illegal instructions.

Risks: stack-frame conversion is fragile because it manually shifts SR/PC fields and fsave sizes. Version-byte validation only accepts known 040 frame versions. Misidentifying an instruction as `fmovecr` would run the wrong emulation path.

Test signals: unimplemented vector dispatch, true illegal F-line dispatch, `fmovecr` with nonzero EA conversion, both original and revised unimplemented fsave versions, invalid fsave format to `fpsp_fmt_error`, and `mem_read` access faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_fline.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_operr.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_operr.S

Purpose: implements `fpsp_operr`, the operand-error FPSP handler. It corrects 68040 move-out integer conversion behavior, stores the 68881-compatible result when required, posts operand-error/inexact state, or forwards enabled traps to kernel handlers.

Important APIs/types/functions: exported label is `fpsp_operr`. Internal helpers include `operr_long`, `operr_word`, `operr_byte`, `operr_nan`, `store_max`, `operr_store`, `dest_mem`, `check_upper`, `end_operr`, `ck_inex`, and `take_inex`. External dependencies are `mem_write`, `real_operr`, `real_inex`, `get_fline`, `fpsp_done`, and `reg_dest`.

Control flow: the handler saves local state and only performs special correction for TFLAG/opclass-3 move-out operations with byte/word/long destinations. It distinguishes NaN conversions from integer overflow and from the 040's incorrectly signaled largest-negative-integer cases. Corrected or saturated values are written through `operr_store`, which chooses data register or memory by reading the original F-line. Enabled operand-error traps branch to `real_operr`; disabled traps may still chain to `real_inex` if inexact is enabled and reported; otherwise they finish through `fpsp_done`.

State and persistence: no persistence. It mutates `USER_FPSR`, clears incorrect inexact bits for saturated integer overflow, may write user memory/register destinations, and may rewrite `EXC_VEC` for inexact chaining.

Dependencies/integration: relies on `fpsp.h` frame fields `FPTEMP`, `ETEMP`, `STAG`, `CMDREG1B`, `EXC_EA`, and FPSR/FPCR bit definitions. Uses shared `reg_dest` and `mem_write` destination paths, and kernel exception entries for real traps.

Risks: integer conversion edge cases are dense and hardware-specific. The code intentionally writes "garbage-compatible" NaN-derived upper mantissa bits for some disabled cases; simplifying it could break compatibility. `operr_store` depends on correct F-line mode bits and `EXC_EA` validity.

Test signals: byte/word/long move-out NaN conversion, positive/negative integer overflow saturation, largest negative byte/word/long false-operr correction, destination Dn vs memory, enabled vs disabled operand-error traps, combined inexact handling, and FPSR bit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_operr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_ovfl.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_ovfl.S

Purpose: implements `fpsp_ovfl`, the overflow exception handler. It computes and stores the 68881-compatible overflow result for trap-disabled behavior, prepares the exceptional operand for trap-enabled behavior, and chains to inexact when required.

Important APIs/types/functions: exported label is `fpsp_ovfl`. Internal helper `ovf_adj` selects `WBTEMP` or `ETEMP`, normalizes sign into `LOCAL_SGN`, chooses opclass-specific overflow result routines `ovf_r_x2` or `ovf_r_x3`, and calls `store`. External exits are `real_ovfl`, `real_inex`, and `fpsp_done`; `b1238_fix` repairs known E3 frame cases.

Control flow: after saving state, it sets the accrued inexact bit the 040 fails to set, calls `ovf_adj` to store the rounded overflow result, then checks whether overflow traps are enabled. Enabled overflow branches to `real_ovfl` after E3 dirty-bit cleanup. Disabled overflow checks inexact enable and may branch to `real_inex`; otherwise it finishes via `fpsp_done`, using the E3 path to clear dirty bits, call `b1238_fix`, shadow FPSR, and set `sx_mask`.

State and persistence: no persistence. It mutates `FPSR_AEXCEPT`, destination FP register/memory via `store`, `FPR_DIRTY_BITS`, `FPSR_SHADOW`, and `E_BYTE` status bits.

Dependencies/integration: depends on `fpsp.h`, `util.S` overflow selectors, `x_store.S` store conversion, kernel real exception handlers, and `b1238_fix` from the FPSP bug-fix path.

Risks: E1 vs E3 operand selection changes whether `ETEMP` or `WBTEMP` is used. Opclass 3 move-out must preserve condition codes around `ovf_r_x3`. Inexact handling in this file tests only the enable bit for `inex2`, reflecting hardware-specific assumptions.

Test signals: overflow for register and memory destinations, all rounding modes/signs/precisions, opclass 3 condition-code preservation, enabled overflow trap exceptional operand, disabled overflow with and without inexact enabled, E3 dirty-bit cleanup, and bug1238 cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_ovfl.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_snan.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_snan.S

Purpose: implements `fpsp_snan`, the signaling-NaN exception handler. It quiets/stores results for disabled traps, prepares enabled trap frames, handles integer move-out special cases, and preserves inexact chaining semantics.

Important APIs/types/functions: exported label is `fpsp_snan`. Internal helpers include `move_out`, `sto_long`, `sto_word`, `sto_byte`, `wrt_dn`, `not_out`, `dst_nan`, `issrc`, `report_snan`, and `end_snan`. External dependencies are `get_fline`, `mem_write`, `real_snan`, `real_inex`, `fpsp_done`, and `reg_dest`.

Control flow: after saving state, disabled SNAN traps call `move_out` and then check for enabled inexact. Enabled traps distinguish move-out instructions from non-move-out instructions; move-out gets corrected storage before reporting. Reporting paths expand the unimplemented frame into a busy frame, shadow FPSR, set `sx_mask`, restore state, and branch to `real_snan` or `fpsp_done`. For byte/word/long move-out, it writes the upper ETEMP mantissa with the quiet bit set either to memory or a Dn register.

State and persistence: no persistence. It writes user destinations for move-out integer formats, updates FPSR condition code negative bit based on source/destination NaN sign, rewrites the fsave frame to busy format, and may rewrite `EXC_VEC` for inexact.

Dependencies/integration: depends on `fpsp.h` frame layouts, `mem_write`, `reg_dest`, and real kernel exception handlers. It shares destination-register decoding style with `x_operr.S`.

Risks: frame expansion depends on version-specific sizes (`VER_40` vs revised frame), and incorrect counts would corrupt the exception stack. SNAN priority between destination and source NaNs is explicitly encoded; changing it affects IEEE exception reporting. Integer destination writes use `EXC_EA == 0` as the data-register indicator.

Test signals: disabled and enabled SNAN traps, move-out to byte/word/long Dn and memory, quiet-bit setting in stored mantissa, source-vs-destination NaN priority, negative condition code setting, inexact chaining, and busy-frame construction for both frame versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_snan.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_store.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_store.S

Purpose: provides the shared `store` routine used by overflow and underflow handlers to write an internal extended-format operand to the actual user destination, whether FP register, Dn register for single move-out, or user memory in extended/single/double format.

Important APIs/types/functions: exported labels are `store`, `dest_ext`, `dest_dbl`, and `dest_sgl`. Static `fpreg_mask` converts FP register numbers to dynamic `fmovemx` masks. It calls `mem_write`, `get_fline`, `g_opcls`, `g_dfmtou`, and `reg_dest`.

Control flow: `store` first checks E3; E3 destinations are always FP registers from `CMDREG3B`. E1 non-opclass-3 also stores to an FP register from `CMDREG1B`. Opclass 3 move-out gets destination format through `g_dfmtou`: extended writes 12 bytes, double converts exponent/mantissa into 8-byte IEEE double, and single converts into 4-byte IEEE single. Single destination with null `EXC_EA` is written to Dn through `reg_dest`.

State and persistence: no persistence. It mutates the destination register or user memory, and mirrors `%fp0-%fp3` writes into `USER_FP0..USER_FP3` because exception handlers later restore those registers from the local frame. It may temporarily reinsert the sign bit into `LOCAL_EX`.

Dependencies/integration: depends on internal extended-format layout from `fpsp.h`, safe user memory write support from `mem_write`, and decoder helpers in `util.S`. Called by `x_ovfl.S` and `x_unfl.S`.

Risks: comments state no rounding is attempted during extended-to-single/double conversion; callers must round beforehand. Destination conversion assumes normal/inf encodings and direct bit extraction; denormal bias corrections are handled by underflow before calling `store`. Incorrect saved `%fp0-%fp3` mirroring would lose results on handler exit.

Test signals: E3 FP register stores for all registers, E1 register stores, opclass 3 memory stores for extended/double/single, single Dn destination, positive/negative infinity conversion, sign preservation, and `%fp0-%fp3` saved-frame synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_store.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_unfl.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_unfl.S

Purpose: implements `fpsp_unfl`, the underflow exception handler. It denormalizes, rounds, and stores intermediate results for 68881/68882-compatible trap-disabled behavior, while preparing enabled underflow and inexact trap paths.

Important APIs/types/functions: exported label is `fpsp_unfl`. Internal helper `unf_res` performs precision selection, operand selection, `denorm`, `round`, store dispatch, condition-code updates, and accrued-underflow updates. External dependencies are `denorm`, `round`, `store`, `g_rndpr`, `g_opcls`, `g_dfmtou`, `real_unfl`, `real_inex`, `fpsp_done`, and `b1238_fix`.

Control flow: the handler saves state and calls `unf_res`. If underflow traps are enabled, it performs E3 cleanup and branches to `real_unfl`. If disabled, it checks enabled/reported inexact and may branch to `real_inex`. Otherwise it finishes through `fpsp_done`, with E3 dirty-bit clearing and bug1238 repair where needed. `unf_res` chooses `WBTEMP` for E3 and `FPTEMP` for E1, handles `fsgldiv/fsglmul` precision quirks, denormalizes, rounds with FPCR mode, adjusts single/double denormal exponent bias for opclass 3 memory stores, calls `store`, and sets zero/negative condition codes for FP-register stores.

State and persistence: no persistence. It mutates the result operand, destination, FPSR condition/accrued bits, `FPR_DIRTY_BITS`, `FPSR_SHADOW`, and E-byte state. It relies on stack-passed precision/mode data between `denorm` and `round`.

Dependencies/integration: tightly coupled to `round.S`, `x_store.S`, `util.S`, and `fpsp.h`. Kernel-level exits are `real_unfl`, `real_inex`, and `fpsp_done`.

Risks: comments warn that `%d0` guard/round/sticky bits and `%a0` must not be corrupted between `denorm` and `round`. Bias adjustment for single/double memory denormals is easy to break. Inexact/accrued-underflow handling depends on `FPSR_EXCEPT` bits set by rounding.

Test signals: underflow to FP register and memory, extended/single/double destinations, fsglmul/fsgldiv precision overrides, exact vs inexact underflow, enabled underflow traps, enabled inexact chaining, signed zero/smallest denormal results, and E3 dirty-bit repair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_unfl.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_unimp.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_unimp.S

Purpose: implements `fpsp_unimp`, the 68040 FPSP handler for unimplemented floating-point instructions. It decodes operands, runs the software function dispatcher, stores results, and posts any generated exceptions.

Important APIs/types/functions: exported labels are `fpsp_unimp` and `uni_2`. It calls `get_op`, `do_func`, `sto_res`, `gen_except`, and `fpsp_fmt_error`.

Control flow: `fpsp_unimp` links a local frame and creates an fsave state frame, then enters `uni_2`. `uni_2` saves volatile data/address and FP registers, validates the fsave version as a 4x 68040 frame, clears transient FPSR exception/condition bits and FPCR user exceptions for internal computation, clears `UFLG_TMP`, calls `get_op`, clears `STORE_FLG`, calls `do_func`, captures any new FPU exception state with `fsave`, stores `%fp0` through `sto_res` unless `STORE_FLG` says not to, and branches to `gen_except`.

State and persistence: no persistence. It mutates the FPSP local frame, saved FPSR/FPCR, `UFLG_TMP`, `STORE_FLG`, operand scratch fields populated by `get_op`, and destination FP register state via `sto_res`.

Dependencies/integration: central integration point for `get_op.S`, `do_func.S`, `tbldo.S`, `sto_res.S`, and `gen_except.S`. `x_fline.S` can branch directly into `uni_2` after synthesizing an unimplemented frame for `fmovecr`.

Risks: fsave frame validation is the only guard before deep FPSP emulation. Clearing FPSR/FPCR bits is intentional; failing to restore/post via `gen_except` would lose user-visible exceptions. `STORE_FLG` must be honored for functions that store through specialized paths.

Test signals: unimplemented monadic functions, dyadic functions, invalid fsave version to format error, `STORE_FLG` suppression, result storage to all FP destinations, generated overflow/underflow/inexact propagation, and `x_fline` `uni_2` entry compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_unimp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_unsupp.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_unsupp.S

Purpose: implements `fpsp_unsupp`, the FPSP handler for unsupported data type exceptions such as packed formats, denormalized numbers, and unnormalized numbers. It normalizes/unpacks operands, restores the operation into the 040 where possible, and posts generated exceptions.

Important APIs/types/functions: exported label is `fpsp_unsupp`. It calls `get_op`, `res_func`, `gen_except`, and `fpsp_fmt_error`.

Control flow: the handler links a local frame, performs `fsave`, saves volatile and FP state, stores the fsave version in `VER_TMP`, validates a 4x 68040 frame, clears live FPSR/FPCR, preserves or clears selected saved FPSR fields depending on whether the instruction is `fmove out`, sets `UFLG_TMP`, calls `get_op`, calls `res_func` to repair the stack frame or perform packed move-out storage, pushes an idle-format word with the saved version, and branches to `gen_except`.

State and persistence: no persistence. It mutates saved FPSR state, `UFLG_TMP`, the fsave frame, and operand/result scratch built by `get_op`/`res_func`.

Dependencies/integration: depends on `fpsp.h` frame layouts and on the operand decoder/result restorer pair. `gen_except` owns final exception posting and return.

Risks: unsupported-data handling is frame-format sensitive. The special FPSR preservation for `fmove out` keeps condition codes and SNAN/accrued state, while other operations clear condition and exception bytes; mixing those paths would change user-visible status. `res_func` must correctly decide whether to restart hardware or complete a packed store in software.

Test signals: packed input/output, denormal and unnormalized operands, `fmove out` vs non-`fmove out` FPSR preservation, invalid fsave frame, `UFLG_TMP` behavior in `get_op`, and final `gen_except` posting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_unsupp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/hp300/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/hp300/Makefile

Purpose: declares the HP300 platform objects built into the m68k kernel subtree.

Important APIs/types/functions: `obj-y := config.o time.o reboot.o` includes HP300 machine setup, timer/clocksource code, and reset stub in the built-in object list.

Control flow: build-system only. Kbuild descends into the directory and links the listed objects when HP300 support is selected by the surrounding architecture configuration.

State and persistence: no runtime state or persistence.

Dependencies/integration: integrates with Linux Kbuild and the HP300 source files in the same directory. Any source added to HP300 machine support must be reflected here to participate in the build.

Risks: omitting an object would produce missing machine hooks or link failures; adding the wrong object could pull platform code into incompatible builds.

Test signals: HP300 kernel configuration builds, link includes `config.o`, `time.o`, and `reboot.o`, and machine boot reaches `config_hp300` and `hp300_sched_init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/hp300/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/hp300/config.c -->
# sources/distributed-fs/ceph-client/arch/m68k/hp300/config.c

Purpose: provides HP300-specific m68k machine initialization. It parses bootinfo, identifies the HP9000 model, installs machine callback hooks, configures RTC access, exposes LED state, and initializes serial console setup.

Important APIs/types/functions: exported globals are `hp300_model`, `hp300_uart_scode`, and `hp300_ledstate` (`EXPORT_SYMBOL`). Key functions are `hp300_parse_bootinfo`, `hp300_get_model`, `hp300_hwclk`, and `config_hp300`. Static RTC helpers `hp300_rtc_read` and `hp300_rtc_write` access BCD clock registers via fixed IO addresses.

Control flow: bootinfo parsing stores model and UART select code. `config_hp300` assigns `mach_sched_init`, `mach_init_IRQ`, `mach_get_model`, `mach_hwclk`, `mach_reset`, and optional heartbeat callbacks, validates the model range excluding HP_350, appends a string suffix to `HP9000/`, prints the detected model, and calls `hp300_setup_serial_console`. RTC read/write helpers busy-wait on command/status bits with interrupts disabled; `hp300_hwclk` converts between `struct rtc_time` and split BCD registers, including year rollover handling.

State and persistence: runtime state includes model ID/name, UART select code, and LED state. Persistent hardware state is the RTC, read and written through `hp300_hwclk`; the code writes 24-hour mode on hour updates.

Dependencies/integration: uses Linux init/module/console/RTC headers, m68k bootinfo records, machine-dependency callback globals from `machdep.h`, HP300 hardware IDs, fixed HP300 RTC IO addresses, `hp300_sched_init` from `time.c`, and `hp300_reset` from `reboot.S`.

Risks: RTC helpers spin indefinitely if hardware status never changes, and they disable interrupts while polling. Model-name array indexing uses `hp300_model-HP_320` after range checks; new enum values must preserve table layout. Unknown models panic during boot.

Test signals: bootinfo parse for model/UART/address/unknown tags, supported and unsupported model detection, serial console setup with UART scode, RTC read/write BCD conversion including years `00-69`, heartbeat callback assignment under `CONFIG_HEARTBEAT`, and interrupt restoration after RTC polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/hp300/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/hp300/reboot.S -->
# sources/distributed-fs/ceph-client/arch/m68k/hp300/reboot.S

Purpose: provides the HP300 `hp300_reset` symbol used as the machine reset callback.

Important APIs/types/functions: exported assembly symbol is `hp300_reset`.

Control flow: currently an infinite self-jump (`jmp hp300_reset`). Comments state a real reboot would need to undo early MMU/cache setup and jump back to PROM, but this implementation is explicitly marked non-working.

State and persistence: no state is updated; reset requests spin forever.

Dependencies/integration: `config.c` assigns `mach_reset = hp300_reset`, so architecture reset paths enter this stub.

Risks: any attempt to reboot an HP300 kernel using this callback will hang instead of resetting hardware. Watchdog or external reset is required if available.

Test signals: link symbol resolution, reset path reaches `hp300_reset`, and platform documentation/known-failure tests should treat reboot as unsupported or hanging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/hp300/reboot.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/hp300/time.c -->
# sources/distributed-fs/ceph-client/arch/m68k/hp300/time.c

Purpose: implements HP300 timer interrupt and clocksource support for m68k. It programs the platform timer, handles periodic ticks, maintains a monotonic tick count, and registers a continuous clocksource.

Important APIs/types/functions: key functions are `hp300_sched_init`, interrupt handler `hp300_tick`, and clocksource read callback `hp300_read_clk`. Static state includes `hp300_clk`, `clk_total`, and `clk_offset`. Hardware constants describe timer registers under `CLOCKBASE`.

Control flow: `hp300_sched_init` resets the clock chip, writes `INTVAL`, requests `IRQ_AUTO_6` as `"timer tick"`, enables timer interrupts, and registers the clocksource at 250 kHz. `hp300_tick` acknowledges status, reads the timer latch with `movpw`, adds `INTVAL` to `clk_total`, clears `clk_offset`, calls `legacy_timer_tick(1)`, drives heartbeat, restores interrupts, and turns off network/SCSI LEDs. `hp300_read_clk` atomically reads MSB/LSB/MSB until stable, accounts for a pending timer interrupt by setting `clk_offset`, and returns total elapsed timer ticks.

State and persistence: runtime-only state is `clk_total` plus `clk_offset`, protected by disabling local interrupts. Hardware timer registers persist only as programmed device state during boot.

Dependencies/integration: depends on Linux clocksource, IRQ, legacy m68k timer hooks, `timer_heartbeat`, `blinken_leds`, `in_8/out_8`, and HP300 auto-vector IRQ 6. `config.c` installs `hp300_sched_init` into `mach_sched_init`.

Risks: timekeeping depends on stable multi-byte timer reads and pending-interrupt detection; races can produce jitter if `clk_offset` is wrong. `request_irq` failure only logs an error, but the clocksource is still registered. Inline `movpw` and fixed addresses are HP300-specific.

Test signals: boot timer initialization, IRQ delivery at `HZ`, clocksource monotonicity across counter rollover and pending interrupts, LED clearing side effect, behavior when `request_irq` fails, and calibration at `HP300_TIMER_CLOCK_FREQ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/hp300/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/hp300/time.h -->
# sources/distributed-fs/ceph-client/arch/m68k/hp300/time.h

Purpose: declares the HP300 scheduler/timer initialization entry point for other HP300 machine code.

Important APIs/types/functions: declares `extern void hp300_sched_init(void);`.

Control flow: no executable logic.

State and persistence: no state.

Dependencies/integration: included by `config.c` to assign `mach_sched_init` and by `time.c` for local consistency.

Risks: if the declaration diverges from `time.c`, the machine callback assignment can break at compile or link time.

Test signals: build coverage that includes both `config.c` and `time.c`, and link resolution for `hp300_sched_init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/hp300/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/Makefile

Purpose: declares the 68060 integer and floating-point support package wrapper objects for the m68k kernel build.

Important APIs/types/functions: `obj-y := fskeleton.o iskeleton.o os.o` builds the FPSP wrapper, ISP wrapper, and shared operating-system call-outs.

Control flow: build-system only. Kbuild links these objects when the 68060 support package directory is selected.

State and persistence: no runtime state.

Dependencies/integration: integrates Linux Kbuild with `fskeleton.S`, `iskeleton.S`, and `os.S`; those include generated/converted Motorola package sources (`fpsp.sa`, `isp.sa`) at assembly time.

Risks: missing any of the three objects breaks call-out table references or package entry symbols. Object ordering can matter if included package labels rely on local wrapper symbols.

Test signals: 68060 m68k build, resolution of `_060_fpsp_*`, `_060_isp_*`, and `_060_[id]mem_*` symbols, and successful assembly of included `.sa` package files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/fskeleton.S -->
# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/fskeleton.S

Purpose: adapts the Motorola 68060 Floating-Point Software Package to Linux/m68k. It defines OS call-outs, public FPSP entry stubs, a 128-byte call-out table, and includes the converted `fpsp.sa` package body.

Important APIs/types/functions: exported call-outs include `_060_fpsp_done`, `_060_real_ovfl`, `_060_real_unfl`, `_060_real_operr`, `_060_real_snan`, `_060_real_dz`, `_060_real_inex`, `_060_real_bsun`, `_060_real_fline`, `_060_real_fpu_disabled`, and `_060_real_trap`. Exported entry stubs include `_060_fpsp_snan`, `_060_fpsp_operr`, `_060_fpsp_ovfl`, `_060_fpsp_unfl`, `_060_fpsp_dz`, `_060_fpsp_inex`, `_060_fpsp_fline`, `_060_fpsp_unsupp`, and `_060_fpsp_effadd`.

Control flow: normal FPSP completion branches to `_060_isp_done`. Real enabled FP exceptions mostly `fsave`, write `0x6000` into the state frame, `frestore`, and branch to the generic `trap` handler. BSUN clears the NaN bit in FPSR before trapping. FPU-disabled call-out clears the PCR FPU-disabled bit, copies the causing instruction PC into the current PC slot, and returns with `rte`. Entry stubs branch to fixed offsets after `_FP_CALL_TOP+0x80`. `_FP_CALL_TOP` contains relative offsets to call-outs and memory access routines, then `fpsp.sa` is included.

State and persistence: no persistent state. Runtime state is the exception stack/FPU state frame, FPSR/PCR, and the static call-out table consumed by the package.

Dependencies/integration: includes `<linux/linkage.h>` and `fpsp.sa`; references `_060_isp_done`, `trap`, `_060_real_trace`, `_060_real_access`, and memory call-outs implemented in `os.S`.

Risks: the call-out section must remain exactly 128 bytes as required by the Motorola package. Fixed branch offsets are ABI with `fpsp.sa`; adding entries or changing order breaks package calls. The sample real exception handlers are generic trap bridges rather than rich Linux signal-specific implementations.

Test signals: assemble/link with `fpsp.sa`, invoke each `_060_fpsp_*` vector, verify call-out table size/order, enabled FP exceptions reach `trap`, FPU-disabled path re-enables PCR and resumes, and BSUN clears FPSR NaN before handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/fskeleton.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/iskeleton.S -->
# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/iskeleton.S

Purpose: adapts the Motorola 68060 Integer Software Package to Linux/m68k. It defines OS call-outs, entry stubs for unimplemented integer/CAS emulation, the ISP call-out table, and includes `isp.sa`.

Important APIs/types/functions: exported labels include `_060_isp_done`, `_060_real_chk`, `_060_real_divbyzero`, `_060_real_cas`, `_060_real_cas2`, `_060_real_lock_page`, `_060_real_unlock_page`, `_060_isp_unimp`, `_060_isp_cas`, `_060_isp_cas2`, `_060_isp_cas_finish`, `_060_isp_cas2_finish`, `_060_isp_cas_inrange`, `_060_isp_cas_terminate`, and `_060_isp_cas_restart`.

Control flow: `_060_isp_done` returns directly with `rte` for supervisor-mode frames, but for user-mode frames it saves an interrupt frame, gets current task, and jumps to `ret_from_exception` so Linux can deliver signals/reschedule. CHK and divide-by-zero exits branch to `trap`. CAS/CAS2 call-outs re-enter the package through offsets. `_060_real_lock_page` sets SFC/DFC based on user/supervisor mode, uses 68060 `plpaw` to prefetch/lock one or two pages, records access failures through exception-table fixups, restores function codes, and returns a fault-status long in `%d0`. `_060_real_unlock_page` currently returns success without action.

State and persistence: no persistent state. Runtime state includes exception stack frames, SFC/DFC control registers, prefetch/fault status in `%d0`, and the static `_I_CALL_TOP` table.

Dependencies/integration: includes Linux m68k entry macros and asm offsets, references `trap`, `ret_from_exception`, `_060_real_trace`, `_060_real_access`, and memory call-outs from `os.S`. Includes `isp.sa` at the end.

Risks: user/supervisor return split in `_060_isp_done` is critical for signal and reschedule handling. `plpaw` fixups must return correctly encoded FSLW values or package access-error synthesis fails. The call-out table has the same fixed 128-byte ABI risk as the FPSP wrapper.

Test signals: unimplemented integer emulation returning to user and supervisor contexts, CHK/divide-by-zero trap paths, CAS/CAS2 emulation, page-lock success and fault fixups for word/long operands crossing pages, SFC/DFC restoration, and call-out table size/order validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/iskeleton.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/os.S -->
# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/os.S

Purpose: implements operating-system memory and exception call-outs shared by the 68060 FPSP and ISP packages. It provides data/instruction memory reads and writes for user or supervisor contexts, plus real trace/access exception exits.

Important APIs/types/functions: exported labels include `_060_dmem_write`, `_060_imem_read`, `_060_dmem_read`, `_060_dmem_read_byte`, `_060_dmem_read_word`, `_060_dmem_read_long`, `_060_imem_read_word`, `_060_imem_read_long`, `_060_dmem_write_byte`, `_060_dmem_write_word`, `_060_dmem_write_long`, `_060_real_trace`, and `_060_real_access`.

Control flow: generic read/write loops test bit 5 of the saved SR at `0x4(%a6)` to choose supervisor `move` instructions or user-space `movs` instructions. Known-size byte/word/long helpers clear success status in `%d1`, perform a single supervisor or user access, and return data in `%d0` for reads. Write helpers similarly store from `%d0`. `_060_real_trace` branches to `trap`; `_060_real_access` branches to `buserr`. Exception-table entries map faults in user `movs` access labels to a `.fixup` routine that returns `%d1 = -1`.

State and persistence: no persistence. Runtime state is limited to copied bytes/words/longs, `%d1` status, and exception-table recovery for access faults.

Dependencies/integration: used by call-out tables in `fskeleton.S` and `iskeleton.S`. Depends on Linux/m68k exception table and `.fixup` mechanisms, `trap`, `buserr`, and 68060 `movs` address-space instructions.

Risks: generic byte loops decrement `%d0` before `dbra`; zero-length calls would underflow and copy too much, so callers must pass positive byte counts. Known-size helpers rely on exception table coverage for every user-access label. Supervisor-mode paths do raw kernel memory moves and will not recover through user access fixups.

Test signals: user and supervisor reads/writes for byte/word/long and arbitrary byte counts, invalid user addresses returning `%d1=-1`, instruction vs data read call-outs, trace and access exception exits, and integration with FPSP/ISP package memory callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/os.S -->
