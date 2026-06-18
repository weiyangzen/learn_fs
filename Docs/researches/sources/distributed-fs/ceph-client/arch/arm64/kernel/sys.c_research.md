## sources/distributed-fs/ceph-client/arch/arm64/kernel/sys.c

### Purpose
`sys.c` implements ARM64-native syscall glue that needs architecture-specific behavior and builds the AArch64 syscall dispatch table.

### Important APIs, Types, And Functions
It defines `sys_mmap`, `sys_arm64_personality`, `__arm64_sys_ni_syscall`, the `__arm64_*` syscall wrappers generated from `asm/syscall_table_64.h`, and `sys_call_table`.

### Control Flow
The mmap syscall rejects byte offsets that are not page-aligned, then delegates to `ksys_mmap_pgoff`. The personality syscall rejects `PER_LINUX32` if the system cannot run 32-bit EL0, then delegates to `ksys_personality`. The table is initialized to `__arm64_sys_ni_syscall` and then populated by the syscall table include.

### State, Persistence, And Dependencies
No durable state is owned here. The file reads CPU capability state for 32-bit EL0 support and affects process personality and VM mappings via generic syscall helpers.

### Integration Points
It is reached from `syscall.c`'s EL0 SVC path and integrates with generic fs/mm/personality syscalls, generated syscall metadata, and CPU feature detection.

### Risks
ABI mistakes in offset validation or table generation affect all userspace. The 32-bit personality guard must match actual compat support to avoid unusable process modes.

### Test Signals
Run native syscall ABI tests, mmap offset alignment tests, personality tests with and without `CONFIG_COMPAT` or 32-bit EL0 support, and syscall table coverage for unimplemented entries.
