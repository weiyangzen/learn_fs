<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/restart_syscall.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/restart_syscall.S

### Purpose
`vdso64/restart_syscall.S` reuses the common restart-syscall trampoline for the 64-bit vDSO.

### Important APIs, Types, And Functions
It includes `../vdso32/restart_syscall.S`, compiled with `__VDSO64__` to select 64-bit load width.

### Control Flow
Runtime control is the included trampoline: load saved return pointer and branch through gateway offset `0x100` with `__NR_restart_syscall`.

### State, Persistence, And Dependencies
Consumes the saved return pointer planted by signal restart code. Depends on the shared source and 64-bit vDSO build flags.

### Integration Points
Exported from `vdso64.so` and used by `signal.c` for native restart-block syscalls.

### Risks
Correctness depends on `__VDSO64__` being defined and native stack layout matching `signal.c`.

### Test Signals
Native 64-bit interrupted syscall restart tests should pass through this trampoline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/restart_syscall.S -->
