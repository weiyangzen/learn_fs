<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dma-types.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/dma-types.h

Purpose: Defines type-safe s390 32-bit and 64-bit DMA address wrappers.

Important APIs/types/functions: `dma32_t`, `dma64_t`, conversion helpers to/from virtual addresses and integers, and add/and helpers. Source-visible declarations include: #define _ASM_S390_DMA_TYPES_H_; typedef u32 __bitwise dma32_t;; typedef u64 __bitwise dma64_t;; static inline dma32_t virt_to_dma32(void *ptr); static inline void *dma32_to_virt(dma32_t addr); static inline dma32_t u32_to_dma32(u32 addr); static inline u32 dma32_to_u32(dma32_t addr); static inline dma32_t dma32_add(dma32_t a, u32 b); static inline dma32_t dma32_and(dma32_t a, u32 b); static inline dma64_t virt_to_dma64(void *ptr).

Control flow: Inline helpers cast physical/virtual addresses into bitwise-distinct DMA types so sparse can catch accidental mixing.

State and persistence behavior: No state; values represent DMA-visible addresses.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/io.h>. Integrated with Integrates CIO/CCW/EADM DMA pools, device drivers, and sparse checking..

Risks: Truncation in 32-bit DMA helpers or bypassing bitwise types can corrupt device address programming.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 103 lines, 2563 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dma-types.h -->
