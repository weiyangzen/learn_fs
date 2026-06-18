<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/compat.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/compat.h

**Purpose:** Defines MIPS 32-bit compatibility types, data layouts, and compat task detection for 64-bit kernels.

**Important APIs/types/functions:** Provides compat UID/GID typedefs, signal constants, `COMPAT_RLIM_INFINITY`, `COMPAT_UTS_MACHINE`, `struct compat_stat`, `compat_statfs`, IPC structures, compat SysV sem/msg/shm layouts, `compat_stack_t`, and `is_compat_task()`.

**Control flow:** Structure definitions adapt field ordering for endianness in message queues. `is_compat_task()` checks `TIF_32BIT_ADDR`.

**State, dependencies, integration:** Used by compat syscalls, signal altstack, stat/statfs, IPC, and personality handling.

**Risks and test signals:** ABI layout is user-visible and cannot drift. Test 32-bit userspace syscall ABI on 64-bit kernels, big/little endian IPC times, stat/statfs binary layouts, and compat altstack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/compat.h -->
