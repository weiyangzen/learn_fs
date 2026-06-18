<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/switch_to.h

Purpose: declares the low-level context switch routine `_switch_to(void *last, void *next)` and maps the generic `switch_to(prev, next, last)` macro to it.

Control flow is a simple macro wrapper; actual state save/restore is in `kernel/entry.S`. Persistent state touched by the implementation includes `thread_struct.ra/sp`, kernel stack pointer in `exc_table`, coprocessor enable state, optional user Xtensa registers, stack canary, and PS interrupt state. Dependencies include scheduler calling conventions and ABI-specific `_switch_to`. Integration points are the scheduler, task fork setup, register-window spilling, coprocessor lazy context switching, and stack protector. Risks are type-erased `void *` misuse, ABI register preservation errors, and switch return value assumptions. Test signals include scheduler stress, fork/exec tests, preemption, SMP task migration, and coprocessor state preservation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/switch_to.h -->
