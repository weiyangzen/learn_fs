<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/math_efp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/math_efp.c

## Purpose
This file emulates e500 SPE embedded floating-point instructions to provide IEEE-754 compliant behavior and rounding fixes.

## Important APIs, types, and functions
Public handlers are `do_spe_mathemu(struct pt_regs *regs)` and `speround_handler(struct pt_regs *regs)`. `insn_type` classifies SPE opcodes into operand layouts. `spe_mathemu_init` detects e500 CPU A005 erratum revisions. Important state includes `current->thread.evr`, GPR halves, `SPEFSCR`, `spefscr_last`, and `fpexc_mode`.

## Control flow
`do_spe_mathemu` fetches the instruction, validates EFAPU primary opcode, decodes function/source class, gathers operand halves from EVR/GPR pairs, loads SPEFSCR into soft-fp FPSCR, dispatches SPFP, DPFP, or vector single operations, updates CR fields for compares, writes destination EVR/GPR, updates sticky exception state, and returns `1` when enabled software FP exceptions should trap. Illegal opcodes may reissue on affected e500 erratum CPUs. `speround_handler` adjusts inexact results for round-to-plus-infinity or round-to-minus-infinity modes when hardware handled only nearest/zero.

## State and persistence behavior
It mutates GPRs, EVRs, CR fields, SPEFSCR SPR, per-thread sticky SPEFSCR shadow, and NIP indirectly via caller behavior. It does not write user memory.

## Dependencies and integration points
Integrated with BookE/e500 SPE exception handling, Linux `prctl` FP exception modes, soft-fp single/double macros, PVR detection, and module init.

## Risks and edge cases
Edge cases include vector lane exception aggregation, sign recovery for zero conversion results, NaN invalid handling, sticky bit preservation, e500 A005 reissue behavior, and correct trapping under `PR_FP_EXC_SW_ENABLE`.

## Test signals
Signals include SPE instruction trap handling returning 0/1/-ENOSYS appropriately, correct EVR/GPR result halves, SPEFSCR sticky bits, and rounding-mode behavior for inexact results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/math_efp.c -->
