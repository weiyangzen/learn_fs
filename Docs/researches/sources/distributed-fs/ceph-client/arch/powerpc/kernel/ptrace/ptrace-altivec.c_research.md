# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-altivec.c

## Purpose
This file exposes Altivec/VMX register state through the ptrace regset interface.

## Important APIs, Types, And Functions
It exports `vr_active()`, `vr_get()`, and `vr_set()`. The ABI buffer is 34 `vector128` slots: VR0-VR31, VSCR as the 33rd vector, and VRSAVE in the low word of the 34th vector.

## Control Flow
`vr_active()` flushes live Altivec state and returns the regset size only if the task used VMX. `vr_get()` flushes state, verifies `thread_vr_state` layout, writes 33 vectors from `target->thread.vr_state`, then writes a zero-padded vector containing `target->thread.vrsave`. `vr_set()` flushes state, copies incoming VR/VSCR data directly into `vr_state`, then optionally copies the VRSAVE vector and stores only its first word.

## State And Persistence
The persistent task fields are `thread.vr_state` and `thread.vrsave`; flushing reconciles live CPU registers with `thread_struct` before copying.

## Dependencies And Integration Points
It is wired into `native_regsets` and `compat_regsets` as `REGSET_VMX` under `CONFIG_ALTIVEC`, and shares layout macros from `ptrace-decl.h`.

## Risks
The userspace VRSAVE vector layout only uses one word, so endian/layout assumptions matter. Missing flushes would expose stale live vector state. VMX state also interacts with transactional memory checkpointed state in `ptrace-tm.c`.

## Test Signals
Regset get/set tests should verify all 32 VRs, VSCR placement, VRSAVE low-word semantics, active state before and after VMX use, native and compat views, and core dump note size.
