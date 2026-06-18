<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/sigreturn.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/sigreturn.S

### Purpose
`sigreturn.S` implements the LoongArch vDSO `__vdso_rt_sigreturn` signal trampoline.

### Important APIs, Types, And Functions
The exported signal function is `__vdso_rt_sigreturn`, declared with `SYM_SIGFUNC_START/END`.

### Control Flow
The routine loads `__NR_rt_sigreturn` into syscall register `a7` and executes `syscall 0`.

### State, Persistence, And Dependencies
It has no persistent local state. Dependencies include LoongArch syscall ABI, UAPI syscall numbers, and signal-frame expectations.

### Integration Points
The vDSO linker exports this symbol and `vdso.lds.S` also aliases `VDSO_sigreturn` for kernel offset generation. Userspace signal return uses this trampoline.

### Risks
Wrong syscall number/register breaks signal return for every userspace process on this ABI.

### Test Signals
Run signal delivery/return tests, `strace` signal paths, and vDSO symbol inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/sigreturn.S -->
