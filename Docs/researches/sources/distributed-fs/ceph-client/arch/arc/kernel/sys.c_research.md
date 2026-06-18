# sources/distributed-fs/ceph-client/arch/arc/kernel/sys.c

Purpose: defines the ARC syscall dispatch table.

Important APIs/functions: `sys_call_table[NR_syscalls]` is initialized to `sys_ni_syscall` for every slot, then populated by including `asm/syscall_table_32.h`. Local defines map `sys_clone`, `sys_clone3`, and `sys_mmap2` to ARC wrapper or pgoff implementations.

Control flow: there is no runtime control flow in this file beyond table lookup performed by the syscall entry path elsewhere. The preprocessor expands syscall table macros into designated initializers.

State and persistence: the syscall table is static kernel data. It persists for the kernel lifetime and controls every userspace syscall dispatch on this architecture.

Dependencies and integration: depends on Linux syscall headers, ARC syscall wrappers, `NR_syscalls`, and generated or maintained `asm/syscall_table_32.h`. Integrates directly with low-level ARC syscall entry code.

Risks: wrong macro aliases route syscalls to the wrong ABI wrapper. Missing table entries fall back to `sys_ni_syscall`, which is safe but visible as unimplemented syscall behavior. ABI drift between syscall numbers and `asm/syscall_table_32.h` is the main compatibility risk.

Test signals: syscall ABI selftests, clone/clone3 process creation tests, `mmap2` tests, and audit/strace checks that expected syscall numbers dispatch correctly.
