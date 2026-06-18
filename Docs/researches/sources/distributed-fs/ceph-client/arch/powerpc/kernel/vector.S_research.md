# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vector.S

## Purpose
Provides low-level PowerPC VMX/Altivec and VSX save/restore helpers plus FP-backed scalar implementations used by vector instruction emulation.

## Important APIs, Types, And Functions
Exports `load_vr_state`, `store_vr_state`, `load_up_altivec`, `save_altivec`, optional `load_up_vsx`, and vector arithmetic helpers `vaddfp`, `vsubfp`, `vmaddfp`, `vnmsubfp`, `vrefp`, and `vrsqrtefp`. Internal `fpenable` and `fpdisable` enable FP, save/restore FPSCR and scratch FP registers, and frame temporary state.

## Control Flow
Save/restore helpers move 32 vector registers and VSCR between hardware and thread memory. `load_up_altivec` enables MSR_VEC, sets VRSAVE if zero, marks thread state as loaded/used, restores saved vector state, and arranges return MSR bits. `load_up_vsx` ensures FP and vector facilities are loaded, marks VSX used, and returns through interrupt exit. Emulation helpers enable FP, loop over four single-precision lanes, compute results, store them into vector buffers, and restore FP/MSR state.

## State And Persistence
Mutates hardware vector/FP registers, MSR facility bits, VRSAVE, PACA interrupt-valid state, and per-task thread flags/register save areas. No durable storage is touched.

## Dependencies And Integration Points
Used by context switch, facility-unavailable handlers, and `vecemu.c`. Depends on `asm-offsets`, PACA/current layout, thread_struct offsets, MSR bits, FP/VMX instructions, and 32/64-bit ABI constraints.

## Risks And Edge Cases
This is register-state-critical assembly. 32-bit `load_up_altivec` can use only registers restored by fast exception return. VSX code is intentionally unavailable for 32-bit kernels. PACA SRR validity changes and RI-bit handling are important on Book3S. FP helper routines must preserve caller state and avoid preemption hazards.

## Test Signals
Context-switch tests with FP/Altivec/VSX users, signal save/restore tests, AltiVec emulation tests, kprobe exclusion checks, and stress tests with preemption/SMP should cover the behavior.
