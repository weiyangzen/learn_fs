<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/entry.S

Purpose: implements LoongArch syscall entry and fork return assembly paths.
Important APIs and types: defines `handle_syscall`, `ret_from_fork_asm`, and `ret_from_kernel_thread_asm`, using `SAVE_STATIC`, `RESTORE_*`, `STACKLEAK_ERASE`, and unwind hints.
Control flow: `handle_syscall` switches from user to kernel stack using per-CPU saved stack, saves user registers and CSRs into `pt_regs`, enables KGDB watch handling if configured, sets thread pointer state, calls `do_syscall`, erases stack-leak region, and restores state back to user. Fork return paths call C helpers and restore saved frames.
State and persistence: builds transient syscall `pt_regs` on the kernel stack and updates saved return state.
Dependencies and integration: depends on `stackframe.h`, `thread_info.h`, `asm-offsets.h`, `ptrace.h`, `do_syscall`, stackleak, KGDB, and scheduler fork code.
Risks and test signals: register save/restore mistakes break all syscalls and fork. Signals include syscall ABI tests, fork/clone, strace/seccomp, signal restart, and stack unwinding through syscall frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/entry.S -->
