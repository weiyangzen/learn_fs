# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/msi_bitmap.h

Purpose: defines a bitmap allocator for PowerPC hardware MSI interrupt numbers.

Important APIs/types/functions: `struct msi_bitmap` contains an OF node, bitmap pointer, spinlock, IRQ count, and ownership flag. APIs allocate/free hardware IRQ ranges, reserve individual hwirqs, reserve device-tree-described hwirqs, allocate/init the bitmap, and free it.

Control flow: MSI controller setup initializes the bitmap, reserves unavailable or firmware-described interrupts, then drivers allocate/free contiguous hwirq ranges for MSI vectors under lock.

State and persistence: bitmap bits persist as allocation state for the controller lifetime. `bitmap_from_slab` records whether the bitmap memory should be freed.

Dependencies and integration points: depends on OF and PowerPC IRQ types; used by MPIC and other MSI-capable interrupt controllers.

Risks: allocation/free range errors can double-allocate MSI vectors or leak them. Device-tree reservations must be applied before drivers allocate vectors.

Test signals: MSI allocation/free stress, multi-vector allocation, device-tree reservation tests, lockdep under concurrent MSI users, and MPIC MSI interrupt delivery.
