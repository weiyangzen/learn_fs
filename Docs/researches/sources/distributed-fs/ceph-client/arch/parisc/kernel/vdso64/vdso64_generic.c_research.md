<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64_generic.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64_generic.c

### Purpose
`vdso64_generic.c` provides native 64-bit vDSO time symbols as syscall fallbacks.

### Important APIs, Types, And Functions
It defines `__vdso_gettimeofday()` and `__vdso_clock_gettime()`, both implemented with `syscall2()`.

### Control Flow
Each exported function casts pointer arguments to `long`, invokes the corresponding syscall number, and returns the result.

### State, Persistence, And Dependencies
No state is persisted. Dependencies include PA-RISC vDSO syscall helpers, syscall numbers, and kernel time structure ABI declarations.

### Integration Points
Exported from `vdso64.so` for libc resolver use; execution still enters the kernel gateway.

### Risks
These are syscall wrappers rather than true data-page time fast paths. ABI type mismatch would surface in libc time calls.

### Test Signals
Compare vDSO gettimeofday/clock_gettime results and errno behavior with direct syscalls on native 64-bit tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64_generic.c -->
