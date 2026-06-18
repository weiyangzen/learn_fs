<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/sys_parisc32.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/sys_parisc32.c

### Purpose
`sys_parisc32.c` contains the 32-on-64 syscall fallback for unimplemented compat syscalls.

### Important APIs, Types, And Functions
`sys32_unimplemented()` logs the current command, pid, and syscall number from `r20`, then returns `-ENOSYS`.

### Control Flow
The function is entered through compat syscall table holes and immediately reports the missing syscall before failing.

### State, Persistence, And Dependencies
No state is persisted. It depends on `current`, printk, and syscall table dispatch convention passing the syscall number as the final argument.

### Integration Points
Used by generated or hand-wired compat syscall tables for unsupported entries.

### Risks
Repeated unsupported calls can spam logs. The function assumes PA-RISC argument register ordering.

### Test Signals
Invoke an intentionally unimplemented compat syscall and confirm `-ENOSYS` plus a single understandable kernel log line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/sys_parisc32.c -->
