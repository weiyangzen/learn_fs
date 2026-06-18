# sources/distributed-fs/ceph-client/arch/arm/include/asm/signal.h

## Purpose
Provides ARM signal ABI declarations and includes UAPI signal definitions.

## Important APIs, Types, And Functions
Key declarations include typedef unsigned long old_sigset_t; /* at least 32 bits */; typedef struct {; unsigned long sig[_NSIG_WORDS];; void do_rseq_syscall(struct pt_regs *regs);; int do_work_pending(struct pt_regs *regs, unsigned int thread_flags,; int syscall);. Important macros/constants include _ASMARM_SIGNAL_H, _NSIG, _NSIG_BPW, _NSIG_WORDS, __ARCH_UAPI_SA_FLAGS, __ARCH_HAS_SA_RESTORER. It depends directly on #include <uapi/asm/signal.h>, #include <asm/sigcontext.h>.

## Control Flow
Signal delivery and return paths use the architecture stack frame definitions and generic signal constants.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <uapi/asm/signal.h>, #include <asm/sigcontext.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
