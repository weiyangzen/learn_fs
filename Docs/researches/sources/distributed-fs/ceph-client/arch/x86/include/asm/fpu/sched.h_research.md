<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/sched.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/sched.h

## Purpose
Scheduler-facing FPU hooks for saving, dropping, cloning, flushing, and switching task FPU ownership. The header is 55 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/sched.h>`; `#include <asm/cpufeature.h>`; `#include <asm/fpu/types.h>`; `#include <asm/trace/fpu.h>`

Notable constants/macros: `#define _ASM_X86_FPU_SCHED_H`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_SCHED_H`; `extern void save_fpregs_to_fpstate(struct fpu *fpu);`; `extern void fpu__drop(struct task_struct *tsk);`; `extern int fpu_clone(struct task_struct *dst, u64 clone_flags, bool minimal,`; `unsigned long shstk_addr);`; `extern void fpu_flush_thread(void);`; `static inline void switch_fpu(struct task_struct *old, int cpu)`; `struct fpu *old_fpu = x86_task_fpu(old);`

## Control Flow
switch_fpu() saves old task registers only when TIF_NEED_FPU_LOAD is clear, records AVX512 timestamp when relevant, and marks next task for lazy restore on return to userspace.

## State and Persistence
Persistent state is task->thread.fpu, last_cpu, fpstate contents, TIF_NEED_FPU_LOAD, and optional AVX512 timing metadata.

## Dependencies and Integration Points
Integrates with scheduler context switches, trace_fpu hooks, cpufeature bits, clone/exec/thread flush paths, and lazy FPU restore return path.

## Risks
Risks include stale register ownership, missed saves before kernel FPU use, timestamp skew, clone/minimal-copy bugs, and feature-dependent lazy restore regressions.

## Test Signals
Tests should exercise context switches under FP/SSE/AVX/AVX512 load, clone/exec, ptrace after switch, preemption around kernel FPU, and debug FPU consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/sched.h -->
