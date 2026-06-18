# sources/distributed-fs/ceph-client/include/uapi/asm-generic/shmbuf.h

Purpose: Defines generic SysV shared-memory status and system-info structures.

Important APIs/types/functions: Exports `struct shmid64_ds` with `ipc64_perm`, segment size, attach/detach/change timestamps with 32-bit split fields when needed, creator/last-op pids, attach count, and unused fields; exports `struct shminfo64` with shmmax, shmmin, shmmni, shmseg, shmall, and unused fields.

Control flow: `__BITS_PER_LONG` selects timestamp layout. The header includes generic IPC and POSIX type definitions.

State/persistence: No runtime state; structures define shared-memory syscall ABI.

Dependencies/integration: Includes `asm/bitsperlong.h`, `asm/ipcbuf.h`, and `asm/posix_types.h`; used by SysV shared-memory syscalls and libc.

Risks: Timestamp and padding layout are ABI-sensitive, especially for 32-bit and big-endian user space.

Test signals: SysV shared-memory tests and ABI layout validation for `shmid64_ds` and `shminfo64`.
