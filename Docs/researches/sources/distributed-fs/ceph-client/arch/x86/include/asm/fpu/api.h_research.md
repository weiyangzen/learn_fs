<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/api.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/api.h

## Purpose
Public in-kernel FPU API for kernel FPU sections, fpregs locking/loading, boot/resume init, exception handling, xfeature queries, KVM guest fpstate, and xstate prctl. The header is 180 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/bottom_half.h>`; `#include <asm/fpu/types.h>`

Notable constants/macros: `#define _ASM_X86_FPU_API_H`; `#define KFPU_387 _BITUL(0) /* 387 state will be initialized */`; `#define KFPU_MXCSR _BITUL(1) /* MXCSR will be initialized */`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_API_H`; `#define KFPU_387 _BITUL(0) /* 387 state will be initialized */`; `#define KFPU_MXCSR _BITUL(1) /* MXCSR will be initialized */`; `extern void kernel_fpu_begin_mask(unsigned int kfpu_mask);`; `extern void kernel_fpu_end(void);`; `extern bool irq_fpu_usable(void);`; `extern void fpregs_mark_activate(void);`; `static inline void kernel_fpu_begin(void)`; `static inline void fpregs_lock(void)`; `static inline void fpregs_unlock(void)`; `void fpregs_lock_and_load(void);`; `extern void fpregs_assert_state_consistent(void);`; `static inline void fpregs_assert_state_consistent(void) { }`; `extern void switch_fpu_return(void);`; `extern int cpu_has_xfeatures(u64 xfeatures_mask, const char **feature_name);`; `extern int fpu__exception_code(struct fpu *fpu, int trap_nr);`; `extern void fpu_sync_fpstate(struct fpu *fpu);`; `extern void fpu_reset_from_exception_fixup(void);`; `extern void fpu__init_cpu(void);`; `extern void fpu__init_system(void);`; `extern void fpu__init_check_bugs(void);`; `extern void fpu__resume_cpu(void);`; `extern void fpstate_init_soft(struct swregs_state *soft);`; `static inline void fpstate_init_soft(struct swregs_state *soft) {}`

## Control Flow
kernel_fpu_begin() selects 64-bit MXCSR-only default or 32-bit 387+MXCSR, fpregs_lock() disables BH or preemption for RT, and KVM helpers swap guest/task fpstates around vCPU entry/exit.

## State and Persistence
State touched through per-CPU kernel_fpu_allowed and fpu_fpregs_owner_ctx plus task fpu/fpstate buffers, guest fpstate allocation, XFD, and confidential-guest flags.

## Dependencies and Integration Points
Depends on bottom-half/preempt semantics, fpu/types.h, xstate helpers, KVM, signal/prctl, CPU hotplug, and exception fixups.

## Risks
Risks include using FPU in invalid IRQ/NMI contexts, missing fpregs_lock discipline, RT preemption assumptions, guest XFD desynchronization, and leaked dynamic fpstate.

## Test Signals
Tests should cover kernel_fpu_begin/end nesting rules, irq_fpu_usable contexts, CPU hotplug/resume, ptrace/signal state sync, KVM guest fpstate swap, AMX/XFD prctl behavior, and debug consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/api.h -->
