<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32_generic.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32_generic.c

### Purpose
`vdso32_generic.c` provides 32-bit vDSO time symbols as syscall fallbacks.

### Important APIs, Types, And Functions
It defines `__vdso_gettimeofday()`, `__vdso_clock_gettime()`, and `__vdso_clock_gettime64()`, each using `syscall2()`.

### Control Flow
Each function directly invokes the matching syscall number with casted pointer arguments and returns the syscall result.

### State, Persistence, And Dependencies
No state is persisted. Dependencies include PA-RISC vDSO syscall helpers, UAPI syscall numbers, and time structure forward declarations.

### Integration Points
Exported from `vdso32.so` through the linker script for libc fast-path lookup, though these implementations still trap to the kernel.

### Risks
These are not true userspace time reads, so performance is syscall-bound. Type declarations must match the 32-bit ABI, especially `clock_gettime64`.

### Test Signals
Call all vDSO time symbols from 32-bit userspace and compare return values/errors with direct syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32_generic.c -->
