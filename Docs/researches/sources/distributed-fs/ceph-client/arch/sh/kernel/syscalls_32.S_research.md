# sources/distributed-fs/ceph-client/arch/sh/kernel/syscalls_32.S

Purpose: emits the 32-bit SH syscall dispatch table.

Important APIs and control flow: `__SYSCALL(nr, entry)` expands to a `.long entry`; `sys_call_table` includes generated `<asm/syscall_table.h>` in `.data`, so table contents are generated from `syscall.tbl`.

State, dependencies, and risks: persistent state is the linker-visible `sys_call_table` consumed by `entry-common.S`. Dependencies include generated syscall table header, syscall symbols, and `NR_syscalls`. Risks are table/header mismatch, missing syscall symbol references, and data-section placement assumptions. Test signals are boot syscall dispatch, invalid syscall returning `-ENOSYS`, and kbuild regeneration.
