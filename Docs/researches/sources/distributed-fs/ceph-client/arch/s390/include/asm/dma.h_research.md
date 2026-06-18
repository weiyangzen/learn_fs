<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dma.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/dma.h

Purpose: Provides minimal s390 DMA address constants.

Important APIs/types/functions: `MAX_DMA_ADDRESS` as the 2 GiB virtual boundary. Source-visible declarations include: #define _ASM_S390_DMA_H; #define MAX_DMA_ADDRESS __va(0x80000000).

Control flow: Generic DMA code includes the architecture limit for low DMA allocations.

State and persistence behavior: No state.

Dependencies and integration points: Direct includes are #include <linux/io.h>. Integrated with Integrates DMA mapping and legacy low-memory allocation assumptions..

Risks: The boundary must match devices or subsystems requiring below-2G DMA memory.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 14 lines, 359 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dma.h -->
