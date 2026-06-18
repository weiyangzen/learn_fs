<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/restart_syscall.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/restart_syscall.S

### Purpose
`restart_syscall.S` provides the vDSO trampoline used to restart interrupted syscalls.

### Important APIs, Types, And Functions
It exports `__kernel_restart_syscall`, compiled as either `__VDSO32__` or `__VDSO64__` through build flags.

### Control Flow
The trampoline loads the saved original return pointer from the user stack with 32-bit or 64-bit width, branches to the fixed gateway syscall entry at `0x100(%sr2,%r0)`, and loads `__NR_restart_syscall` into `%r20` in the delay slot.

### State, Persistence, And Dependencies
It consumes the saved return address planted by `insert_restart_trampoline()` in `signal.c`. Dependencies include syscall gateway fixed offset, stack layout, and generated syscall numbers.

### Integration Points
Used by both 32-bit and 64-bit vDSO builds and by signal restart handling.

### Risks
Stack layout must match signal.c for native and compat cases. The gateway offset is ABI-fixed.

### Test Signals
Interrupted syscalls returning `ERESTART_RESTARTBLOCK` should resume through this trampoline on both 32-bit and 64-bit tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/restart_syscall.S -->
