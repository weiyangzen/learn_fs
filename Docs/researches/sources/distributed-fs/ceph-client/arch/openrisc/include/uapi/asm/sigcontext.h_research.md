<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/sigcontext.h

## Purpose
Defines the user ABI signal machine context for OpenRISC.

## Important APIs, Types, And Functions
`struct sigcontext` embeds `struct user_regs_struct regs` first, followed by a union holding `fpcsr` or legacy `oldmask`.

## Control Flow
`kernel/signal.c` writes this structure when building an RT signal frame and restores it in `rt_sigreturn`.

## State And Persistence
The structure persists on the user stack while a signal handler runs and determines restored user register/FPU state.

## Dependencies And Integration Points
Includes `asm/ptrace.h`; paired with generic `ucontext` and OpenRISC signal frame setup.

## Risks
Field order is ABI-sensitive, especially `regs` being first. Bad restoration could let userspace set privileged SR bits, so kernel masks supervisor mode.

## Test Signals
Signal handler return tests, alternate signal stack tests, FPU status preservation, and libc `ucontext_t` compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/sigcontext.h -->
