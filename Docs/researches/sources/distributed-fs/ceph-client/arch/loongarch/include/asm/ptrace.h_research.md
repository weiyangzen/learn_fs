<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/ptrace.h

Purpose: supplies the kernel-internal LoongArch register frame definition and helpers for exception, syscall, and ptrace paths.
Important APIs and types: defines `struct pt_regs`, `user_mode`, `regs_return_value`, `instruction_pointer`, `profile_pc`, `current_pt_regs`, syscall argument accessors, and register classification macros. It includes CSR fields such as ERA, BADVADDR, CRMD, PRMD, EUEN, ECFG, and ESTAT.
Control flow: assembly entry code saves registers into `pt_regs`; C exception, signal, ptrace, KGDB, ftrace, and syscall code consume and mutate the frame. Helpers distinguish user versus kernel mode and expose the syscall return value in the ABI register.
State and persistence: `pt_regs` is the transient but critical trap-frame state stored on the kernel stack while handling exceptions, interrupts, syscalls, and signal delivery.
Dependencies and integration: aligned with UAPI ptrace register numbering, `asm/asm-offsets.h`, `stackframe.h`, syscall code, signal frame setup, and debugger paths.
Risks and test signals: changing ordering or semantics breaks assembly offsets, coredumps, ptrace, seccomp, and signal restore. Signals include `ptrace` selftests, syscall tracing, signal tests, KGDB, and unwinder coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/ptrace.h -->
