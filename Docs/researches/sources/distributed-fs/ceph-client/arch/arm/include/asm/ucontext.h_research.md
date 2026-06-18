# sources/distributed-fs/ceph-client/arch/arm/include/asm/ucontext.h

## Purpose
Defines ARM signal ucontext linkage by including the UAPI ucontext layout.

## Important APIs, Types, And Functions
Key declarations include struct ucontext {; unsigned long uc_flags;; struct ucontext *uc_link;; struct sigcontext uc_mcontext;; unsigned long uc_regspace[128] __attribute__((__aligned__(8)));; struct iwmmxt_sigframe {. Important macros/constants include _ASMARM_UCONTEXT_H, DUMMY_MAGIC, IWMMXT_MAGIC, IWMMXT_STORAGE_SIZE, VFP_MAGIC, VFP_STORAGE_SIZE. It depends directly on #include <asm/fpstate.h>, #include <asm/user.h>.

## Control Flow
Signal delivery and sigreturn use the UAPI frame shape to save and restore user register/FPU state.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/fpstate.h>, #include <asm/user.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
