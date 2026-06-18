<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/signal.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/signal.h

## Purpose
Signal-frame FPU UABI helpers for sizing, copying, restoring, and converting 32-bit/FXSR FPU state. The header is 37 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/compat.h>`; `#include <linux/user.h>`; `#include <asm/fpu/types.h>`

Notable constants/macros: `#define _ASM_X86_FPU_SIGNAL_H`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_SIGNAL_H`; `# define user_i387_ia32_struct user_i387_struct`; `# define user32_fxsr_struct user_fxsr_struct`; `extern void convert_from_fxsr(struct user_i387_ia32_struct *env,`; `struct task_struct *tsk);`; `extern void convert_to_fxsr(struct fxregs_state *fxsave,`; `unsigned long`; `unsigned long *buf_fx, unsigned long *size);`; `unsigned long fpu__get_fpstate_size(void);`; `extern bool copy_fpstate_to_sigframe(void __user *buf, void __user *fp, int size, u32 pkru);`; `extern void fpu__clear_user_states(struct fpu *fpu);`; `extern bool fpu__restore_sig(void __user *buf, int ia32_frame);`; `extern void restore_fpregs_from_fpstate(struct fpstate *fpstate, u64 mask);`

## Control Flow
Signal setup computes fpstate size, copies fpstate and PKRU to user sigframes, and restore paths validate user buffers before loading fpstate registers.

## State and Persistence
State is task FPU state serialized into user signal frames and restored after signal return; no filesystem persistence.

## Dependencies and Integration Points
Depends on compat/user structures, fpu/types.h, uaccess, PKRU, xstate masks, and restore_fpregs_from_fpstate().

## Risks
Risks include accepting malformed xstate, compat conversion mistakes, sigframe size mismatches for dynamic features, and PKRU restore ordering.

## Test Signals
Tests should cover native and ia32 signal delivery/return, altstack frames, XSAVE feature combinations, AMX dynamic size, bad user buffers, and PKRU preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/signal.h -->
