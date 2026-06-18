<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fsgsbase.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fsgsbase.h

## Purpose
64-bit FS/GS base helpers for task state and CPU register/MSR access with optional FSGSBASE instruction use. The header is 85 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/msr.h>`; `#include <asm/cpufeature.h>`

Notable constants/macros: `#define _ASM_FSGSBASE_H`

Notable declarations and inline helpers: `#define _ASM_FSGSBASE_H`; `extern unsigned long x86_fsbase_read_task(struct task_struct *task);`; `extern unsigned long x86_gsbase_read_task(struct task_struct *task);`; `extern void x86_fsbase_write_task(struct task_struct *task, unsigned long fsbase);`; `extern void x86_gsbase_write_task(struct task_struct *task, unsigned long gsbase);`; `static __always_inline unsigned long rdfsbase(void)`; `unsigned long fsbase;`; `static __always_inline unsigned long rdgsbase(void)`; `unsigned long gsbase;`; `static __always_inline void wrfsbase(unsigned long fsbase)`; `static __always_inline void wrgsbase(unsigned long gsbase)`; `static inline unsigned long x86_fsbase_read_cpu(void)`; `static inline void x86_fsbase_write_cpu(unsigned long fsbase)`; `extern unsigned long x86_gsbase_read_cpu_inactive(void);`; `extern void x86_gsbase_write_cpu_inactive(unsigned long gsbase);`; `extern unsigned long x86_fsgsbase_read_task(struct task_struct *task,`; `unsigned short selector);`

## Control Flow
Inline CPU helpers choose RDFSBASE/WRFSBASE when supported or MSR_FS_BASE fallback; GS inactive base is delegated to external helpers because swapgs state matters.

## State and Persistence
State is task thread FS/GS base and CPU FS/GS base registers/MSRs; changes persist across context switch state management.

## Dependencies and Integration Points
Depends on cpufeature checks, MSR access, task_struct thread state, and ptrace/arch_prctl paths.

## Risks
Risks include using instruction helpers without feature checks, confusing active/inactive GS base, and races when reading running tasks.

## Test Signals
Tests should cover arch_prctl, ptrace stopped tasks, context switches, FSGSBASE-enabled and MSR-only CPUs, and swapgs-sensitive kernel GS paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fsgsbase.h -->
