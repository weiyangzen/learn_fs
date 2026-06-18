<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/airq.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/airq.h

Purpose: Declares adapter interrupt registration and interrupt-vector management for s390 I/O adapters.

Important APIs/types/functions: `airq_struct`, `airq_iv`, `register_adapter_interrupt()`, `unregister_adapter_interrupt()`, allocation/scan/free helpers, bit locks, per-bit data, and pointer tagging helpers. Source-visible declarations include: #define _ASM_S390_AIRQ_H; struct airq_struct {; struct hlist_node list; /* Handler queueing. */; void (*handler)(struct airq_struct *airq, struct tpi_info *tpi_info);; #define AIRQ_PTR_ALLOCATED 0x01; int register_adapter_interrupt(struct airq_struct *airq);; void unregister_adapter_interrupt(struct airq_struct *airq);; struct airq_iv {; unsigned long *vector; /* Adapter interrupt bit vector */; unsigned long *avail; /* Allocation bit mask for the bit vector */.

Control flow: Drivers register an adapter interrupt descriptor with a handler and summary indicator, allocate bits from an interrupt vector, lock or unlock bit ownership, and scan for pending interrupt indicators.

State and persistence behavior: Persistent state is vector memory, allocation and lock bitmaps, optional per-bit data/pointer arrays, and registered adapter interrupt descriptors.

Dependencies and integration points: Direct includes are #include <linux/bit_spinlock.h>, #include <linux/dma-mapping.h>, #include <asm/tpi.h>. Integrated with Integrates with PCI, AP, virtio, and other adapter-interrupt users plus s390 interrupt delivery..

Risks: Bit allocation, guest-pinned vectors, and pointer tagging are concurrency-sensitive; lost unlocks or stale bit metadata can drop interrupts or leak pinned memory.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 110 lines, 3370 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/airq.h -->
