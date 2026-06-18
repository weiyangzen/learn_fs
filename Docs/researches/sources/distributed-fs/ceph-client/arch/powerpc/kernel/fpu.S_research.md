# sources/distributed-fs/ceph-client/arch/powerpc/kernel/fpu.S

## Purpose

`fpu.S` implements low-level floating-point register save, restore, and lazy-load support shared by PowerPC kernel entry code. It was split out from head code so chips using different `head-*.S` files can share the same FPU state operations. The file handles plain FP registers and, when `CONFIG_VSX` and CPU features allow, the corresponding VSX register state.

## Important APIs, entry points, and macros

Exported routines are `load_fp_state` and `store_fp_state`. Entry code also calls `_GLOBAL(load_up_fpu)` for lazy user FPU enablement, and C/assembly code calls `_GLOBAL(save_fpu)` to save a task's FPU state. `load_fp_state` and `load_up_fpu` are marked NOKPROBE where required because restore paths must not be instrumented.

Macros `REST_1FPVSR`, `REST_32FPVSRS`, and `SAVE_32FPVSRS` select either FPR or VSR operations. With VSX enabled, feature-fixup sections branch around FPR-only operations when `CPU_FTR_VSX` is present and use `REST_VSR`, `REST_32VSRS`, or `SAVE_32VSRS`; otherwise they use `REST_FPR`, `REST_32FPRS`, and `SAVE_32FPRS`.

## Control flow

`load_fp_state(r3)` assumes FP is already enabled in MSR, restores FPSCR from `FPSTATE_FPSCR(r3)`, then restores all FP or VSR registers from the supplied state area. `store_fp_state(r3)` saves all registers, reads FPSCR with `mffs`, stores it, restores register 0 from memory to undo the scratch use, and returns.

`load_up_fpu` is entered from FP-unavailable exceptions. It reads MSR, sets `MSR_FP`, sets `MSR_RI` on Book3S 64 to allow recovery while accessing current state, and conditionally sets `MSR_VSX`. It updates the saved return MSR in the exception frame to enable FP after return, ORs in the task `THREAD_FPEXC_MODE`, marks `THREAD_LOAD_FP`, restores the task FP state, and returns through the exception return path. The 32-bit and 64-bit paths differ in where current thread and saved MSR live.

`save_fpu(tsk)` computes the task thread pointer, chooses either `THREAD_FPSAVEAREA` or `THREAD_FPSTATE`, saves all registers and FPSCR, restores register 0, and returns with FPU usable by the kernel.

## State and persistence behavior

Persistent state lives in `thread_struct` fields such as `THREAD_FPSTATE`, `THREAD_FPSAVEAREA`, `THREAD_FPEXC_MODE`, `THREAD_LOAD_FP`, and `PT_REGS`. On 64-bit, `PACACURRENT`, saved `_MSR`, and `PACASRR_VALID` are involved in exception return consistency. Hardware state includes MSR FP/VSX bits, FPSCR, and the FP/VSR register file.

## Dependencies and integration points

The file depends on register offsets from `asm-offsets.h`, `ptrace` frame layout, thread and PACA conventions, CPU feature fixup infrastructure, `ppc_asm` register-save macros, and exception handlers in `exceptions-64e.S`, `exceptions-64s.S`, and 32-bit exception code. It integrates with lazy FPU management, restore-math paths, task switching, transactional memory/facility exception paths indirectly, and exported users that need explicit FP state save/restore.

## Risks and invariants

Callers must enable FP before using `load_fp_state` or `store_fp_state`. Register 0 is used as FPSCR scratch and must be restored to avoid corrupting task state. `load_up_fpu` is constrained by exception-return clobber rules, especially on 32-bit where only selected registers are safe. Book3S 64 sets RI because HPT can fault on current access; removing that risks unrecoverable faults. VSX feature patching must match state layout or VSR/FPR halves can be corrupted.

## Test signals

Signals include user floating-point programs after context switches, lazy FP unavailable faults, VSX-enabled workloads, kernel warnings for illegal kernel FP use, suspend/resume or signal restore paths that call FP save/restore, and stress tests with preemption and SMP. Build coverage should include PPC32, PPC64 Book3S, VSX and non-VSX CPUs, and configurations without `CONFIG_VSX`.
