<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/test_emulate_step_exec_instr.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/test_emulate_step_exec_instr.S

## Purpose
This assembly helper executes one dynamically patched instruction against a supplied `pt_regs` image so C self-tests can compare real hardware behavior with software emulation.

## Important APIs, types, and functions
It exposes `_GLOBAL(exec_instr)` and a `patch_site` named `patch__exec_instr`. It uses register save/restore macros, `INT_FRAME_SIZE`, `GPR*`, `_LINK`, `_CCR`, and `_XER` offsets from `asm-offsets.h`.

## Control flow
The routine builds a stack frame, saves nonvolatile state, loads LR/CR/XER/GPRs from the input `pt_regs`, runs the patched instruction at an aligned site, then saves resulting registers back. An exception table maps faults at the test instruction to a `-EFAULT` return.

## State and persistence behavior
It mutates the caller-supplied `pt_regs` structure with post-execution state and preserves caller nonvolatile registers. The instruction slot is patched externally by the C test.

## Dependencies and integration points
It is tightly coupled to `test_emulate_step.c`, PowerPC code patching, exception tables, and the kernel `pt_regs` layout.

## Risks and edge cases
The helper intentionally does not restore stack pointer and thread pointer from the test image, so instructions modifying those would not be meaningfully tested. Fault behavior is collapsed to `-EFAULT`.

## Test signals
`execute_compute_instr` returns zero when this helper runs successfully; mismatches are reported by the C comparison loop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/test_emulate_step_exec_instr.S -->
