# sources/distributed-fs/ceph-client/include/uapi/asm-generic/sembuf.h

Purpose: Defines generic SysV semaphore status structure layout.

Important APIs/types/functions: Exports `struct semid64_ds` containing `ipc64_perm`, operation/change timestamps using either long or split low/high halves, semaphore count, and unused extension fields.

Control flow: `__BITS_PER_LONG` selects 64-bit or split 32-bit timestamp representation.

State/persistence: No runtime state; struct is copied across user/kernel semaphore IPC APIs.

Dependencies/integration: Includes `asm/bitsperlong.h` and `asm/ipcbuf.h`; used by SysV semaphore syscalls.

Risks: Big-endian 32-bit padding is historically odd and documented; changing it breaks compatibility.

Test signals: SysV semaphore IPC tests and struct layout checks on 32-bit/64-bit and endian variants.
