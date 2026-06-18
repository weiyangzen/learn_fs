# sources/distributed-fs/ceph-client/arch/s390/kernel/perf_regs.c

Purpose: implements s390 perf register sampling support for general registers, selected floating-point registers, PSW mask, and program counter.

Important APIs/functions: `perf_reg_value()` returns one requested register from `pt_regs` or the current task FPU save area. `perf_reg_validate()` rejects empty masks and masks containing bits outside `PERF_REG_S390_MAX`. `perf_reg_abi()` reports `PERF_SAMPLE_REGS_ABI_64`. `perf_get_regs_user()` points perf at the task's user interrupt regs and saves user FPU state when needed.

Control flow: register reads branch by perf register index. GPR indices map directly to `regs->gprs[]`; FP indices are available only for user-mode samples and are read from `current->thread.ufpu.vxrs`; mask and PC map to `regs->psw`. User-reg collection intentionally uses `task_pt_regs(current)` from the first interruption, leaving nested interrupt handling to perf core.

State and persistence: the file does not own persistent state. It may refresh the current task's saved FPU registers before perf copies sampled registers.

Dependencies and integration points: depends on `linux/perf_event.h`, `linux/perf_regs.h`, `asm/ptrace.h`, and `asm/fpu.h`. It is called by generic perf when users request `PERF_SAMPLE_REGS_USER` or related register masks.

Risks: FP register reads are current-task specific and return zero for kernel-mode contexts. Register index assumptions must track `enum perf_event_s390_regs`. Failing to save user FPU state before sampling would expose stale vector/FPU content.

Test signals: `perf record --user-regs` on s390 should return GPR/FP/PC/mask data for user samples, invalid masks should return `-EINVAL`, kernel samples should not expose FP values, and ABI should report 64-bit.
