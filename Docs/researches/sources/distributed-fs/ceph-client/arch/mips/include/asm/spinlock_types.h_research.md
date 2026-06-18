<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/spinlock_types.h

Purpose: Exposes generic queued spinlock and queued read-write lock type definitions for MIPS.

Important APIs/types/functions: Includes `asm-generic/qspinlock_types.h` and `asm-generic/qrwlock_types.h`.

Control flow: No control flow; this provides type declarations used by locking headers and structures.

State and persistence: Lock state is stored in generic lock structures defined by the included headers.

Dependencies and integration points: Integrated by MIPS locking and generic kernel synchronization code.

Risks: Type include order must remain compatible with `spinlock.h` and generic locking. ABI/layout changes affect every embedded spinlock/rwlock.

Test signals: Kernel build and lockdep/locking selftests provide coverage.

Source read size: 8 lines, 188 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/spinlock_types.h -->
