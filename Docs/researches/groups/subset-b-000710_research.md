# subset-b-000710 Research

Grouped research for Motorola 68060 FPSP/ISP support sources under `sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src`. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/ftest.S -->
# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/ftest.S

## Purpose
`ftest.S` is a self-checking Motorola 68060 FPSP validation harness. It exercises floating-point unimplemented-instruction handling, unsupported FP effective-address/data formats, non-maskable overflow/underflow behavior, and enabled exception cases for SNAN, OPERR, overflow, underflow, divide-by-zero, and inexact. It is not production exception handling code; it is a diagnostic entry table plus test cases that prove the FPSP restores integer registers, floating-point registers, FP control registers, condition codes, and `fpiar` as expected after each emulated or trapped FP operation.

## Important APIs, Types, And Functions
The branch table at `TESTTOP` exposes `_060TESTS_`, `_060TESTS_unimp`, and `_060TESTS_enable`, each followed by a reserved `short 0x0000` slot. `_060TESTS_` runs effective-address, unsupported-format, non-maskable overflow, and non-maskable underflow tests. `_060TESTS_unimp` runs the unimplemented FP instruction group. `_060TESTS_enable` enables specific FPCR exception bits and runs enabled exception tests.

The local stack frame uses fixed negative offsets from `%a6`: `SREGS`, `IREGS`, `IFPREGS`, `SFPREGS`, `IFPCREGS`, `SFPCREGS`, `ICCR`, `SCCR`, `TESTCTR`, and `DATA`. These model initial and saved integer/FP/FPC register images. `DEF_REGS`, `DEF_FPREGS`, and `DEF_FPCREGS` provide deterministic defaults. `chkregs` and `chkfpregs` compare expected versus observed snapshots; `error` returns the current `TESTCTR` in `%d1`; `chk_test` prints `passed` or the failing test number with `failed`.

The test labels are grouped by behavior: `unimp_0` through `unimp_5` cover `fsin`, `ftan`, `fmovcr`, `fscc`, `fdbcc`, and `ftrapcc`; `effadd_0`, `effadd_1`, `fmovml_0` through `fmovml_3`, and `fmovmx_0` through `fmovmx_2` cover immediate packed/extended operands and FP control/register multi-moves; `unsupp_0` through `unsupp_2` cover unnormalized, denormalized, and packed decimal formats. The exception groups are single-case routines with labels such as `ovfl_0_pc`, `snan_0_pc`, and `dz_0_pc`, whose addresses are written into expected `fpiar` slots.

## Control Flow
Each top-level runner links a 384-byte frame, saves general and FP registers, prints a start string through `_print_str`, clears `TESTCTR` for each category, calls the category routine, and delegates pass/fail reporting to `chk_test`. Each individual test repeats the same pattern: seed all registers with defaults, capture the initial register images into `IREGS`/`IFPREGS`/`IFPCREGS`, load operands into `DATA` or FP registers, clear or set condition/FPCR state, execute the instruction under test at a named `_pc` label, snapshot the post-instruction machine state into `SREGS`/`SFPREGS`/`SFPCREGS`, patch the expected image with the exact result and expected FPSR/FPIAR values, then call `chkregs` and `chkfpregs`.

The harness returns `%d0 = 0` on success. On the first mismatch, `chkregs` or `chkfpregs` returns nonzero, `error` copies `TESTCTR` into `%d1`, and the caller prints the failing ordinal. The print stubs do not implement I/O directly: `_print_str` and `_print_num` read callout displacements from `TESTTOP - 0x80` and tail-call via `rtd`, so the embedding environment supplies the actual output hooks.

## State And Persistence
All test state is stack-frame-local except the callout table used by printing. The code intentionally mutates real CPU state while testing, but restores caller-visible general and FP registers at the end of each top-level runner using `movm.l` and `fmovm.x`. No disk, heap, or kernel state is persisted by this file. The observed state that matters is condition code, data/address register contents, FP register triples, FPCR/FPSR/FPIAR, and the test counter.

## Dependencies And Integration Points
The file depends on a 68060-capable assembler dialect with Motorola syntax, FP instructions, `fmovm`, packed/extended FP constants, and `rtd`. It assumes the Motorola 68060 FPSP exception package is installed so the unimplemented and exception-generating instructions return to the next instruction with FPSP-updated state. It integrates with an external test harness through the `TESTTOP` branch table and the two print callouts placed before `TESTTOP` in the linked image.

## Risks
The tests are exact-register-image checks, so they are sensitive to assembler encoding, FPSP revision, CPU/FPU mode, exception-vector setup, and whether the host preserves `fpiar` addresses exactly. The test frame offsets and `movm` masks are tightly coupled; accidental local-frame changes can silently compare the wrong words. Several cases depend on enabled FPCR exception bits and specific FPSR bit patterns, so running on a different 68k-family FPU or under an emulator with incomplete 68060 FPSP behavior can produce false failures. The print callout addressing is also non-obvious and can break if the branch table placement changes.

## Test Signals
The main signal is the printed category result and, on failure, the one-based `TESTCTR` ordinal. More granular debugging comes from the named `_pc` labels and expected image patches immediately after each instruction. Useful coverage signals include: unimplemented FP op return values and `fpiar`, unsupported operand/data-format normalization, FPCR-enabled trap behavior, non-maskable overflow/underflow, dynamic FP register masks, and exact preservation of unrelated integer and FP registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/ftest.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/ilsp.S -->
# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/ilsp.S

## Purpose
`ilsp.S` is the library-facing integer support package for 68060 instructions that need software emulation when used as callable routines rather than as exception handlers. It provides branch-table entry points for signed and unsigned 64-bit divide, signed and unsigned 32x32-to-64 multiply, and `cmp2` byte/word/long comparisons against address or data register values. Unlike `isp.S`, this file does not decode trapped instruction frames; callers pass operands and output pointers on the stack.

## Important APIs, Types, And Functions
The leading branch table exports `_060LSP__idivs64_`, `_060LSP__idivu64_`, `_060LSP__imuls64_`, `_060LSP__imulu64_`, and six `cmp2` routines: `_060LSP__cmp2_Ab_`, `_060LSP__cmp2_Aw_`, `_060LSP__cmp2_Al_`, `_060LSP__cmp2_Db_`, `_060LSP__cmp2_Dw_`, and `_060LSP__cmp2_Dl_`. The 64-bit divide API takes divisor, high dividend, low dividend, and a pointer to a two-longword result area where remainder is stored first and quotient second. The multiply API takes multiplier, multiplicand, and a pointer to a two-longword result area. The `cmp2` API takes `Rn` and a pointer to the lower/upper bound pair.

The divide implementation uses local frame slots `POSNEG`, `NDIVISOR`, `NDIVIDEND`, `DDSECOND`, `DDNORMAL`, `DDQUOTIENT`, and `DIV64_CC`. The multiply routines use `MUL64_CC`; the compare routines use `CMP2_CC`. Internal helpers `ldclassical`, `lddknuth`, and `ldmm2` implement Knuth Algorithm D and 32x32-to-64 multiplication for long division.

## Control Flow
Both divide entry points save `%d2` through `%d7`, preserve incoming condition-code state in `DIV64_CC`, mark signed versus unsigned in `POSNEG`, then share `ldiv64_cont`. The shared path loads the divisor, forces a real divide-by-zero trap with `divu.w &0,%d0` if needed, normalizes signed operands by recording signs and converting to unsigned, handles fast zero and 32-bit divide cases, rejects quotient overflow, and otherwise calls `ldclassical`. Signed division post-processing applies the original dividend sign to the remainder and the XOR of dividend/divisor signs to the quotient, with explicit signed overflow checks for `0x80000000`.

`ldclassical` has a fast path for word-sized divisors and a full Knuth Algorithm D path for long divisors. The full path normalizes the divisor/dividend until the high divisor bit is set, estimates two quotient words, adjusts overestimates by multiplying back with `ldmm2`, subtracts, optionally adds the divisor back, then denormalizes the remainder.

The multiply routines load operands, special-case zero, convert signed inputs to positive values when needed, compute four 16x16 partial products, combine carries into high and low longwords, optionally two's-complement the 64-bit result, set `N` or `Z` while preserving incoming `X`, and store the two-longword result through the caller's pointer. The `cmp2` routines sign-extend bounds and, for data-register variants, the register operand. `l_cmp2_cmp` computes the two comparisons specified by `cmp2`, merges the new `Z`/`N` bits with preserved old `X`/`N`/`V`, writes `%cc`, restores saved registers, and returns.

## State And Persistence
State is entirely transient: stack frames, caller-provided result buffers, condition codes, and scratch registers. The routines save/restore their documented scratch register sets and no FP registers. Divide-by-zero is intentionally persistent only as an architectural exception side effect: the library routine saves unchanged dividend values before forcing the hardware divide-by-zero exception so the OS can observe the fault.

## Dependencies And Integration Points
This code requires 68020+ style instructions used by the Motorola package, including `link.w`, `movm.l`, `tdivu.l`, `divu.w`, `mulu.w`, `addx`, `negx`, and `rtd`-compatible caller environments. It is integrated by the branch table at file top, with a 0x200 alignment gap reserved for future entries. It is standalone relative to `isp.S`; there are no external symbol dependencies beyond the caller and the processor exception environment for the divide-by-zero case.

## Risks
The APIs are assembly calling-convention sensitive: stack offsets must match exactly, result pointers must be valid and aligned enough for longword stores, and callers must tolerate condition-code changes. Divide and multiply both preserve only selected condition-code bits by design; code that expects exact hardware instruction side effects beyond those bits can diverge. The signed divide overflow boundaries are subtle, especially quotient `0x80000000`. The final result store order intentionally handles equal quotient/remainder or high/low destination cases; changing it can break compatibility. The forced divide-by-zero trap may not point at the original caller instruction, as the header explicitly warns.

## Test Signals
Strong tests compare quotient/remainder and condition codes for zero dividend, zero divisor, 32-bit fast path, long Knuth path, unsigned overflow, signed positive/negative combinations, and signed minimum-value boundaries. Multiply tests should cover zero, high-bit unsigned results, negative signed results, carry propagation across partial products, and equal-result-register semantics via the result buffer order. `cmp2` tests should check byte/word/long bounds, data versus address register sign extension, in-range equal-bound cases, and preservation of old `X`/`V` bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/ilsp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/isp.S -->
# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/isp.S

## Purpose
`isp.S` is the exception-frame-oriented 68060 Integer Software Package. It is the first handler for the Unimplemented Integer Instruction exception and emulates integer instructions removed or special-cased on the 68060: 64-bit `mul{s,u}.l`, 64-bit `div{s,u}.l`, `movep`, `chk2`, `cmp2`, `cas`, and `cas2`. It also supplies branch-table stubs for OS callouts and memory access helpers, converts successful emulation back into an `rte` path through `_isp_done`, and converts secondary faults into trace, CHK, divide-by-zero, or access-error exception frames.

## Important APIs, Types, And Functions
`_060ISP_TABLE` starts with branch entries for `_isp_unimp`, `_isp_cas`, `_isp_cas2`, `_isp_cas_finish`, `_isp_cas2_finish`, `_isp_cas_inrange`, `_isp_cas_terminate`, and `_isp_cas_restart`. The table also stores callout offsets consumed by stubs: `_real_chk`, `_real_divbyzero`, `_real_trace`, `_real_access`, `_isp_done`, `_real_cas`, `_real_cas2`, `_real_lock_page`, `_real_unlock_page`, and instruction/data memory access functions such as `_imem_read_word`, `_dmem_read_long`, and `_dmem_write_byte`. Each stub loads an offset from `_060ISP_TABLE - 0x80`, pushes the computed target address, restores `%d0`, and returns with `rtd`.

The local exception workspace is defined by `LOCAL_SIZE` and offsets such as `EXC_OPWORD`, `EXC_EXTWORD`, `EXC_EXTWPTR`, `EXC_CC`, `SPCOND_FLG`, `EXC_DREGS`, `EXC_AREGS`, and `EXC_TEMP`. Special-condition bits track `(a7)+`, `-(a7)`, CHK traps, divide-by-zero, address-register restore, and immediate operands. Core exported or internal routines include `_isp_unimp`, `_calc_ea`, `_moveperipheral`, `_chk2_cmp2`, `_div64`, `_mul64`, `_compandset`, `_compandset2`, `_isp_cas_finish`, `_isp_cas2_finish`, `_isp_cas_restart`, `_isp_cas_terminate`, `_isp_cas_inrange`, `_isp_cas`, and `_isp_cas2`.

## Control Flow
`_isp_unimp` builds a 96-byte frame, saves all user-visible data registers and address registers through `a6`, reconstructs `a7` from USP or the supervisor stack, snapshots SR/PC, fetches the first instruction longword through `_imem_read_long`, then decodes the opcode. Group 1 dispatches to `_mul64` or `_div64`; group 2 dispatches to `_moveperipheral`, `_chk2_cmp2`, `_compandset`, or `_compandset2`. After emulation, `uieh_done` restores condition codes and user registers, updates USP for user mode, advances the stacked PC to `EXC_EXTWPTR`, and exits through `_isp_done`. Trace mode is handled by building a format-2 trace frame and jumping to `_real_trace`.

Secondary exception control flow is explicit. `_div64` sets `idbyz_flg` instead of taking the trap immediately; `_isp_unimp` later builds a divide-by-zero frame and jumps to `_real_divbyzero`, with special paths for supervisor `(a7)+` stack movement. `_chk2_cmp2` sets `ichk_flg` when `chk2` is out of bounds; the top-level handler builds a CHK frame and jumps to `_real_chk`. Instruction access failures enter `isp_iacc`; data access failures enter `isp_dacc`; both create 68060 access-error frames with FSLW values and jump to `_real_access`.

`_calc_ea` decodes all memory effective-address modes used by the emulated instructions through a 64-entry mode table. It handles `(An)`, `(An)+`, `-(An)`, displacement, indexed, memory-indirect, absolute, PC-relative, and immediate modes. It updates `EXC_EXTWPTR` as extension words/longs are consumed, records register restore data for predecrement/postincrement modes, and routes instruction/data access failures to the appropriate frame builder.

`_moveperipheral` implements `movep.w`/`movep.l` by reading or writing only byte lanes separated by two bytes, preserving peripheral semantics rather than using wider memory accesses. `_chk2_cmp2` calculates an EA, fetches byte/word/long bound pairs, sign-extends operands as needed, computes the architectural condition codes, and optionally marks a CHK trap. `_div64` and `_mul64` mirror the library algorithms in `ilsp.S` but operate on the saved exception register file and memory/immediate operands; both update `EXC_CC` and saved data registers rather than returning direct values.

CAS/CAS2 handling is split into setup, locked core, finish, restart, and terminate phases. `_compandset` and `_compandset2` calculate addresses, extract compare/update operands, call `_real_lock_page` for one or two pages, and branch to `_real_cas` or `_real_cas2`. The in-file default `_isp_cas` and `_isp_cas2` cores mask interrupts, set SFC/DFC to user or supervisor data space, preload ATC entries with `plpaw`/`plpar`, push cache lines with `cpushl`, assert bus lock/end-lock through `%buscr`, use `movs` accesses, and handle aligned and misaligned word/long cases with separate 16-byte-aligned instruction sequences. Finish routines recompute comparison condition codes, update compare registers on failed compare, unlock pages, and return. Restart restores SFC/DFC and reruns setup; terminate converts an emulation fault into an access-error frame.

## State And Persistence
The persistent architectural state is the emulated instruction's effect on the saved register file, condition codes, memory, USP/system stack, and exception stack frame. Intermediate state lives in `EXC_TEMP`, `SPCOND_FLG`, saved address-register restore slots, and CAS/CAS2 saved address and compare-register slots. CAS/CAS2 also temporarily changes SR interrupt mask, SFC, DFC, BUSCR, cache/ATC residency, and page-lock state; finish and error paths must restore or release those resources. The file performs no filesystem or heap persistence.

## Dependencies And Integration Points
`isp.S` depends on OS-supplied callouts for memory access, final exception completion, real exception vectors, CAS/CAS2 page locking, and optional external CAS core replacement. The memory helper contract is central: helpers return data in `%d0` and a failure indicator/FSLW in `%d1`; failures are converted to access-error frames. The handler assumes 68060 supervisor features including USP access, SFC/DFC, BUSCR, `plpaw`, `plpar`, `cpushl`, and `movs`. `_isp_cas_inrange` lets an OS access-error handler determine whether a fault PC lies inside the package CAS core between `_CASLO` and `_CASHI`.

## Risks
The largest risks are exception-frame layout and callout contract drift. A wrong offset in `EXC_*`, `_off_*`, or the branch table can corrupt user registers or jump to the wrong OS hook. Effective-address updates are side-effectful; on access failure, `isp_restore` must undo predecrement/postincrement mutations or the architectural fault state is wrong. Supervisor `(a7)+` paths are special because the emulated instruction can shift the active exception frame. Immediate operands must be read with instruction memory helpers, not data memory helpers.

CAS/CAS2 code is highly timing and hardware sensitive. It assumes pages are resident after `_real_lock_page`, assumes SFC and DFC were equal when saved, masks only interrupt levels 0-6, manipulates `%buscr` directly, and relies on aligned writes to assert `LOCKE*` correctly. Misaligned write sequences are duplicated and fragile. Access-error termination shifts stack frames manually and removes a subroutine return address; small changes can break recovery. The in-range helper's comparisons should be validated carefully because it is used by fault recovery logic.

## Test Signals
Test signals include instruction-decode coverage for every emulated opcode family; EA coverage for register, memory, immediate, PC-relative, indexed, memory-indirect, `(An)+`, `-(An)`, and `a7` special cases; exact condition-code checks for multiply, divide, `cmp2`, `chk2`, and CAS; access-error frame FSLW/address validation for instruction and data faults; trace/CHK/divide-by-zero frame conversion; and CAS/CAS2 update/no-update behavior under aligned and misaligned word/long addresses. OS integration tests should exercise callout failures, page-lock failure on first and second CAS2 operands, restart/terminate paths, and `_isp_cas_inrange` results for PCs inside and outside `_CASLO`/`_CASHI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/isp.S -->
