# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-vsx.c

## Purpose
This file implements FPR regset access for VSX-capable builds and exposes the lower halves of the first 32 VSX registers.

## Important APIs, Types, And Functions
It exports `fpr_get()`, `fpr_set()`, `vsr_active()`, `vsr_get()`, and `vsr_set()`. It uses `TS_FPR()` and `TS_VSRLOWOFFSET` to address the correct FPR/VSX storage lanes.

## Control Flow
`fpr_get()` and `fpr_set()` flush FP state, copy the 32 FPRs and FPSCR through a temporary 33-u64 buffer, and then update thread state. `vsr_active()` flushes VSX state and reports availability only after VSX use. `vsr_get()` and `vsr_set()` flush TM, FP, Altivec, and VSX state, copy the lower VSX halves from `thread.fp_state.fpr[i][TS_VSRLOWOFFSET]`, and write back after successful copyin.

## State And Persistence
Persistent task state is `thread.fp_state.fpr`, `thread.fp_state.fpscr`, and the `used_vsr` activity flag.

## Dependencies And Integration Points
This file is built under `CONFIG_VSX` and provides both `REGSET_FPR` and `REGSET_VSX` functions referenced from `ptrace-view.c`. It must stay consistent with transactional checkpointed VSX handling in `ptrace-tm.c`.

## Risks
VSX overlays FPR and VMX architectural state, so flushing all related units before VSR access is important. Temporary buffers avoid partial-copy corruption; direct writes without that pattern would be risky. ABI comments clarify that callers need FP and VMX regsets in addition to VSX to reconstruct all VSX state.

## Test Signals
Tests should include FPR/FPSCR round trips on VSX kernels, VSR lower-half get/set, active state before and after VSX use, partial copy offsets, and interaction with VMX/FPR regsets in debugger and coredump output.
