# Research: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/fpsp.S

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000707`: lines 1-7886, `Docs/researches/chunks/subset-b-000707_research.md`
- `subset-b-000708`: lines 7887-16684, `Docs/researches/chunks/subset-b-000708_research.md`
- `subset-b-000709`: lines 16685-24785, `Docs/researches/chunks/subset-b-000709_research.md`

## Chunk Research

### subset-b-000707: lines 1-7886

# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/fpsp.S lines 1-7886

## Scope And Purpose

This chunk is the first 7,886 lines of Motorola's M68060 Floating-Point Software Package source, vendored under the Ceph client m68k architecture tree. Despite the repository path, the code is not distributed-filesystem logic. It is privileged 68060 FPSP assembly that provides operating-system entry points, exception dispatch stubs, stack-frame layout definitions, floating-point exception handlers, unimplemented-instruction emulation, and the first group of transcendental math kernels.

The top of the file identifies the Motorola 68060 Software Package Production Release P1.00 from October 10, 1994. The chunk begins with the branch/callout table that an operating system links against and then defines the common stack-local ABI used by the FPSP handlers. It covers the complete implementations of the overflow, underflow, unimplemented-data-type, unimplemented-effective-address, operand-error, signalling-NaN, inexact, divide-by-zero, line-F, and unimplemented-instruction handlers. It also includes the dispatch table for transcendental emulation and complete or near-complete kernels for sine, cosine, sine/cosine, tangent, arctangent, arcsine, arccosine, exponential, exponential-minus-one, getexp/getman, and hyperbolic cosine. The chunk ends inside the `ssinh` large-input path, so conclusions about `ssinh` and later routines must be reconciled with the next chunk.

## Important APIs, Types, And Entry Points

The external ABI begins at `_060FPSP_TABLE`. The initial table contains branch slots for FPSP exception entry points such as `_fpsp_snan`, `_fpsp_operr`, `_fpsp_ovfl`, `_fpsp_unfl`, `_fpsp_dz`, `_fpsp_inex`, `_fpsp_fline`, `_fpsp_unsupp`, and `_fpsp_effadd`. Immediately after that are global callout stubs for OS handlers and memory services: `_fpsp_done`, `_real_ovfl`, `_real_unfl`, `_real_inex`, `_real_bsun`, `_real_operr`, `_real_snan`, `_real_dz`, `_real_fline`, `_real_fpu_disabled`, `_real_trap`, `_real_trace`, `_real_access`, `_imem_read`, `_dmem_read`, `_dmem_write`, `_imem_read_word`, `_imem_read_long`, `_dmem_read_byte`, `_dmem_read_word`, `_dmem_read_long`, `_dmem_write_byte`, `_dmem_write_word`, and `_dmem_write_long`. Each stub saves `d0`, loads a PC-relative offset from `_060FPSP_TABLE-0x80`, pushes the computed target address, restores `d0`, and returns through `rtd &0x4`; this is the indirection layer between FPSP code and OS-provided services.

The core stack-local data layout is defined by `set` constants. `LOCAL_SIZE` is 192 bytes, with negative offsets from `%a6` used for saved data/address registers, saved `fp0`/`fp1`, source and destination extended-precision operands, scratch extended values, saved `fpcr`/`fpsr`/`fpiar`, the current operation word and extension word, source/destination type tags, and special-condition flags. Operand tags include `NORM`, `ZERO`, `INF`, `QNAN`, `DENORM`, `SNAN`, and `UNNORM`. FPSR/FPCR bits and masks are defined for condition codes, enabled exceptions, accrued exceptions, overflow/underflow/inexact combinations, rounding modes, vector offsets, and special addressing cases such as `(a7)+`, `-(a7)`, `fmovm`, and immediate operands.

Major handler entry points in this chunk are:

- `_fpsp_ovfl` and `_fpsp_unfl`: repair source operands from fsave frames, emulate the faulting instruction to produce default and exceptional results, store default results when exceptions are disabled, and route enabled overflow/underflow/inexact/trace cases.
- `_fpsp_unsupp`: handles unimplemented data types, including denormal, unnormal, and packed formats for opclass 0/2/3 instructions.
- `_fpsp_effadd`: handles unimplemented effective-address forms, including extended/packed immediate operands, dynamic `fmovm.x`, `fmovm.l` control-register moves, FPU-disabled priority conversion, and access-error frame creation.
- `_fpsp_operr`, `_fpsp_snan`, `_fpsp_inex`, and `_fpsp_dz`: enabled-exception front ends that repair fsave operands and, for move-out cases, synthesize missing default stores to data registers or memory before calling the OS handler.
- `_fpsp_fline`: classifies line-F frames into unimplemented FP instruction, FPU-disabled, or true line-F cases, including the 68060 `fmovecr` nonzero-effective-address quirk.
- `_fpsp_unimp`: emulates unimplemented FPgen transcendental instructions plus `ftrapcc`, `fdbcc`, and `fscc`.

Important internal helpers in this chunk include `fix_skewed_ops`, `funimp_skew`, `_mem_write2`, and the exception-status tables `tbl_except`, `tbl_fu_out`, `tbl_except_p`, `tbl_iea_except`, and `tbl_funimp_except`. `tbl_trans` is the dispatch table used by `_fpsp_unimp` for transcendental operations. It indexes by operation plus source operand tag and maps to routines such as `ssinh`, `slognp1`, `setoxm1`, `stanh`, `satan`, `sasin`, `ssin`, `stan`, `setox`, `stwotox`, `stentox`, `slogn`, `slog10`, `slog2`, `scosh`, `sacos`, `scos`, `sgetexp`, `sgetman`, and special-case handlers like `src_zero`, `src_qnan`, `src_snan`, `t_operr`, and `t_dz2` that are defined outside or later in the full file.

## Control Flow

The exception handlers share a common prologue pattern: create the 192-byte local frame, `fsave` any busy FPU state when applicable, save `d0`/`d1`/`a0`/`a1`, save `fpcr`/`fpsr`/`fpiar`, save `fp0`/`fp1`, fetch the faulting instruction from `FPIAR` or the stacked PC through `_imem_read_long`, then decode the operation word and extension word. The handler clears the active hardware `fpcr`/`fpsr` while emulating, uses memory operands stored in `FP_SRC` and `FP_DST`, and restores user-visible state before branching to an OS callout or `_fpsp_done`.

For overflow and underflow, control first distinguishes ordinary FPgen operations from `fmove out` operations. Ordinary cases call `fix_skewed_ops`, tag source and possibly destination operands, emulate through `tbl_unsupp`, then store a default result with `store_fpreg`. Enabled exception bits decide whether to insert an exceptional fsave frame and branch to `_real_ovfl`, `_real_unfl`, or `_real_inex`; disabled cases restore state and exit through `_fpsp_done`. Underflow includes an explicit 68060 multiplier hardware workaround for the smallest normalized product, where the hardware may report underflow even if emulation does not.

The unimplemented-data handler splits into denormal/unnormal opclass 0/2, opclass 3 move-out, packed input, and packed output paths. It uses `fix_skewed_ops`, `set_tag_x`, `unnorm_fix`, `get_packed`, `load_fpn1`, `load_fpn2`, `store_fpreg`, and `fout` to emulate the operation. It then applies Motorola's exception precedence ordering with `bfffo` over enabled-and-set FPSR bits. If an enabled FP exception must be reintroduced, it writes the corresponding `0xe00x` fsave status into `FP_SRC` and uses `frestore`; otherwise it writes the default result and exits. Special supervisor-stack cases shift the exception frame to account for `-(a7)` and `(a7)+` addressing.

The unimplemented-effective-address handler first checks PCR bit 1 because FPU-disabled has priority over unimplemented effective address. If the FPU is disabled, it calculates the faulting instruction length and rewrites the current 4-word frame into an 8-word FPU-disabled frame before calling `_real_fpu_disabled`. Otherwise it either reads extended/packed immediate data via `_imem_read`, converts packed decimal with `decbin`, emulates through `tbl_unsupp`, or dispatches to `fmovm_dynamic`/`fmovm_ctrl`. Instruction-fetch and data-access failures are converted into access-error stack frames with fault-status longwords and routed to `_real_access`.

The unimplemented-instruction handler is the central emulation path for transcendental instructions. It saves the user/supervisor stack pointer context, fetches the instruction, clears active FP state, and separates type-0 general instructions from type-1 condition-code instructions. General instructions use `_load_fop`, combine the instruction extension with `STAG`, dispatch through `tbl_trans`, then either store `fp0` into the destination FP register or reinsert enabled exceptions into the FPU state. Type-1 instructions call `_ftrapcc`, `_fdbcc`, or `_fscc`; these can convert the current frame into trap, BSUN, trace, or access-error frames.

The math-kernel control flow is table-driven from `tbl_trans` and routine-local. Trigonometric kernels use compact integer comparisons of the extended input's exponent and high fraction to choose tiny, normal, or large-argument paths. Normal sine/cosine/tangent use table-based reduction by `N*pi/2` for `|x| < 15*pi`; large arguments use iterative reduction by scaled `pi/2` pieces. Polynomial or rational approximations compute the final result and then deliberately restore the user's rounding mode only for the final operation, so FPSR exception signaling is attributed to the last relevant FP instruction. Exponential kernels similarly split tiny, normal, near-overflow, and definite overflow/underflow ranges, use `EEXPTBL` values for `2^(j/64)`, and reconstruct scale factors in extended precision.

## State And Persistence Behavior

This source has no persistent storage in the filesystem or Ceph sense. Its state is CPU architectural state: the supervisor stack exception frame, the user stack pointer, `fpcr`, `fpsr`, `fpiar`, the FPU fsave frame, data/address registers, and the FP register file. The code treats the exception stack frame as mutable state and often rewrites frame format/vector-offset words, current/next PC fields, effective addresses, and fault-status fields before tail-calling the OS handler.

The local frame under `%a6` is the transient state hub. `FP_SRC`, `FP_DST`, `FP_SCR0`, and `FP_SCR1` carry 12-byte extended values; `STAG` and `DTAG` carry operand classifications; `SPCOND_FLG` carries addressing-mode side effects that determine whether supervisor stack frames must be shifted; `USER_FPCR`, `USER_FPSR`, and `USER_FPIAR` preserve user-visible control state while emulation runs with active FP control registers cleared.

State restoration order is important. The code generally restores FP registers and control registers before `frestore` of a synthetic exception frame because later floating-point moves could otherwise disturb exception state. Some trace paths deliberately use a temporary `fsave`/`frestore` sequence around moving `fpiar` to avoid triggering an unwanted exception after an exception has already been reinserted.

Constant tables are read-only runtime data embedded in the assembly stream. This chunk defines constants for logarithms, pi, `2/pi`, polynomial coefficients, `PITBL`, `ATANTBL`, and `EEXPTBL`. The numerical algorithms depend on exact bit patterns, including split high/low constants chosen for cancellation and final rounding behavior.

## Dependencies And Integration Points

The file integrates with an m68k operating system port by requiring the OS to install `_060FPSP_TABLE` branch-table offsets and implement the callout routines behind `_real_*`, `_imem_*`, and `_dmem_*`. The FPSP does not directly know how to safely access user instruction or data memory; it asks OS callouts to read or write memory and expects failure information in registers, then converts failures into access-error exception frames.

This chunk depends heavily on 68060/68k privileged and floating-point instructions: `fsave`, `frestore`, `fmovm`, `fmov`, `fadd`, `fsub`, `fmul`, `fdiv`, `fsqrt`, `ftest`, `fb*` branches, `movc %pcr`, `%usp`, `rtd`, `link/unlk`, `movm`, bit-field instructions such as `bfextu` and `bfffo`, and stack-frame formats specific to the 68060 exception model. It assumes Motorola assembler syntax, including `set`, `global`, `short`, `long`, `space`, and `swbeg`.

Many helper routines and special-case targets referenced here are defined elsewhere in the full `fpsp.S` beyond this chunk or in adjacent FPSP source sections: `tbl_unsupp`, `fout`, `load_fpn1`, `load_fpn2`, `store_fpreg`, `store_dreg_b/w/l`, `_load_fop`, `_calc_ea_fout`, `fmovm_dynamic`, `fmovm_ctrl`, `fmovm_calc_ea`, `decbin`, `get_packed`, `norm`, `dnrm_lp`, `t_catch`, `t_inx2`, `t_pinx2`, `t_minx2`, `t_extdnrm`, `t_ovfl`, `t_ovfl2`, `t_unfl2`, and many `tbl_trans` targets. Merge-time research should connect these later definitions to the entry points described here.

The visible source-tree integration is the Linux/m68k-style `arch/m68k/ifpsp060` package. Neighboring files such as `fskeleton.S`, `os.S`, `fpsp.doc`, `fpsp.sa`, and `src/README-SRC` likely describe or wrap how an OS links the branch table and callouts, but this work item only required the `fpsp.S` chunk.

## Risks And Edge Cases

The highest risk is exception-frame correctness. Many paths rewrite stack frames in-place, change vector offsets, shift frames up or down for `-(a7)` and `(a7)+`, and update `%usp` only for user-mode cases. Small offset mistakes would corrupt return-from-exception behavior or write FP results over exception metadata.

The OS callout ABI is another critical risk. The stubs compute targets from offsets stored relative to `_060FPSP_TABLE-0x80`; if the OS table layout, relocation model, or assembler interpretation changes, every memory and exception callout can branch to the wrong code. Memory callouts must also preserve the expected register protocol, especially `d1` as a success/failure signal after reads/writes.

Skewed operand handling is subtle. `fix_skewed_ops` repairs single/double source operands that the 68060 presents in an unusual extended format for denormal, zero, infinity, and NaN cases. `funimp_skew` sometimes intentionally re-skews operands before reinserting an enabled exception. These transformations are precision- and format-specific; changing them risks reporting the wrong exceptional operand to user handlers.

Exception precedence is deliberately encoded in tables and `bfffo` scans of the enabled exception byte. Overflow plus enabled inexact and underflow plus enabled inexact get special routing because the inexact handler needs the exceptional operand that would otherwise be lost. Reordering these checks would produce architecturally visible differences.

Math kernels rely on exact constants, final-operation exception behavior, and reduced-argument bounds. The code often restores the user's FPCR immediately before the final operation to generate the intended rounded result and exception flags. Seemingly harmless instruction scheduling or constant changes can alter inexact, overflow, underflow, or monotonicity behavior.

This chunk ends in the middle of `ssinh` after saving a reduced large-input value on the stack. The `ssinh` large-input completion, `ssinhd`, and later hyperbolic/logarithmic/special-case routines are outside the line range, so this chunk should not be treated as a complete function-level report for all transcendental behavior.

## Test Signals

Assembly/build tests should confirm that the Motorola syntax still assembles for the intended m68k toolchain and that all global symbols and local labels referenced in lines 1-7886 resolve when the full `fpsp.S` file is assembled. Useful static checks include verifying `_060FPSP_TABLE` branch slot order, callout offset constants, `LOCAL_SIZE`-relative offsets, and exception-status tables against the documented 68060 stack-frame formats.

Exception-level tests need an emulator or real 68060-capable environment. They should exercise disabled and enabled overflow, underflow, inexact, operand-error, signalling-NaN, divide-by-zero, unimplemented data type, unimplemented effective address, FPU-disabled, line-F, and trace cases. The observable signals are the final stack-frame format/vector offset, updated next/current PC, fsave exception status word, FPCR/FPSR/FPIAR preservation, default result storage, and selected `_real_*` callout target.

Memory access tests should force `_imem_read`, `_dmem_read`, and `_dmem_write` failures and verify that handlers create access-error frames with the expected effective address, FSLW, supervisor/user transfer-mode bit, and target `_real_access`. Supervisor stack edge cases should cover `fmove.x` and packed moves using `-(a7)` and `(a7)+`, plus dynamic `fmovm.x` predecrement/postincrement.

Numerical tests should compare `ssin`, `scos`, `ssincos`, `stan`, `satan`, `sasin`, `sacos`, `setox`, `setoxm1`, `sgetexp`, `sgetman`, and `scosh` against a high-precision oracle across normal, tiny, denormal, boundary, huge, NaN, infinity, and invalid-domain inputs. Important boundary samples are `2^-40`, `15*pi`, `1/16`, `16`, `1`, `1/4`, `2^-65`, `70*log(2)`, `16380*log(2)`, `16480*log(2)`, and values near the maximum extended exponent. Tests should assert not only numeric results but also FPSR condition codes and exception bits.

Chunk-boundary validation should record that `subset-b-000707` documents only lines 1-7886 and ends mid-routine. The later merge lane should combine this with the subsequent chunk before producing final per-file conclusions about `ssinh`, shared `t_*` exception helpers, and routines referenced by `tbl_trans` but not defined here.

### subset-b-000708: lines 7887-16684

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

### subset-b-000709: lines 16685-24785

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
