<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/test_emulate_step.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/test_emulate_step.c

## Purpose
This late-init self-test validates the instruction analysis and emulation infrastructure implemented in `sstep.c`.

## Important APIs, types, and functions
It uses `emulate_step`, `analyse_instr`, `emulate_update_regs`, `patch_instruction_site`, and the assembly helper `exec_instr`. Test helpers include `init_pt_regs`, `run_tests_load_store`, `run_tests_compute`, `emulate_compute_instr`, and `execute_compute_instr`. `struct compute_test` describes mnemonic-specific subtests, feature gates, ignored registers, ignored CR/XER flags, and negative tests.

## Control flow
Load/store tests initialize registers and memory, emulate one instruction, and print PASS/SKIP/FAIL. They cover ordinary, prefixed, atomic, FP, Altivec, VSX, and Power10 paired vector forms depending on config and CPU features. Compute tests emulate a table of arithmetic/prefixed cases, patch the same instruction into `exec_instr`, execute it for real, and compare GPRs, LR, XER, and CR unless flags request an ignore.

## State and persistence behavior
The file creates temporary `pt_regs`, stack data, FP/vector unions, and a patched NOP site in `exec_instr`. It logs results only and does not persist state beyond the patched instruction site used during testing.

## Dependencies and integration points
It depends on PPC raw opcode macros, CPU feature detection, `asm/sstep.h`, `asm/text-patching.h`, prefixed instruction wrappers, and `test_emulate_step_exec_instr.S`.

## Risks and edge cases
The test is feature-sensitive and prints SKIP for unsupported ISA/config combinations. Some operations have hardware-defined undefined results, so individual GPR/CR/XER fields can be ignored. The `pstd` success condition uses `stepped == 1 || regs.gpr[5] == a`, which is weaker than the surrounding tests.

## Test signals
Boot logs from `Running instruction emulation self-tests ...` followed by PASS/SKIP/FAIL lines are the primary signal. Compute mismatches include exact expected and actual register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/test_emulate_step.c -->
