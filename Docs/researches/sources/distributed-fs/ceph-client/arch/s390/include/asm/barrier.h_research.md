<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/barrier.h

Purpose: Defines s390 memory barriers, acquire/release helpers, and nospec masking.

Important APIs/types/functions: `bcr_serialize()`, `__mb`, `__dma_mb`, `__smp_*`, `__smp_store_release`, `__smp_load_acquire`, and `array_index_mask_nospec()`. Source-visible declarations include: #define __ASM_BARRIER_H; #define __ASM_BCR_SERIALIZE "bcr 14,0"; #define __ASM_BCR_SERIALIZE "bcr 15,0"; static __always_inline void bcr_serialize(void); #define __mb() bcr_serialize(); #define __rmb() barrier(); #define __wmb() barrier(); #define __dma_rmb() __mb(); #define __dma_wmb() __mb(); #define __smp_mb() __mb().

Control flow: Full barriers emit the serializing `bcr` sequence while read/write barriers rely on compiler barriers where the s390 memory model permits it; nospec masks protect array indices.

State and persistence behavior: No state; it enforces ordering around shared memory and MMIO/DMA.

Dependencies and integration points: Direct includes are #include <asm/march.h>, #include <asm-generic/barrier.h>. Integrated with Integrates the Linux memory model, atomics, DMA, user-copy/speculation mitigations, and lockless code..

Risks: Over-weak barriers break lockless algorithms and device ordering; over-strong barriers hurt performance but are safer.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 84 lines, 1976 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/barrier.h -->
