# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_callbacks.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_callbacks.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_callbacks.c

### Purpose
System-call callback table for SPU code. It lets SPU contexts request a restricted subset of 64-bit PowerPC syscalls through the PPE kernel.

### Important APIs, Types, And Functions
Defines `spu_syscall_table[]` from `asm/syscall_table_spu.h` and exports `spu_sys_callback(struct spu_syscall_block *s)`. The callback validates the syscall number, logs debug details, and invokes the selected syscall function with up to six arguments from the SPU syscall block.

### Control Flow
SPU support code calls `spu_sys_callback()` when an SPU issues a syscall request. Invalid syscall numbers return `-ENOSYS`; valid entries dispatch directly through the table.

### State, Persistence, And Dependencies
State is the static syscall table only. No durable persistence. Dependencies include syscall function prototypes, SPU syscall block layout, and the generated SPU syscall table.

### Integration Points
Used by spufs/SPU runtime to implement the allowed syscall ABI for SPU programs.

### Risks
This is ABI-sensitive and security-sensitive: table contents decide what SPU programs can invoke. Missing NULL checks would be dangerous if the table contains holes.

### Test Signals
Run SPU syscall tests for valid calls, disabled calls, out-of-range numbers, argument passing, and debug symbol formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_callbacks.c -->
