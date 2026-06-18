<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cache.h

Purpose: Defines s390 cache-line constants and read-mostly placement.

Important APIs/types/functions: `L1_CACHE_BYTES`, `L1_CACHE_SHIFT`, `NET_SKB_PAD`, and `__read_mostly` section annotation. Source-visible declarations include: #define __ARCH_S390_CACHE_H; #define L1_CACHE_BYTES 256; #define L1_CACHE_SHIFT 8; #define NET_SKB_PAD 32; #define __read_mostly __section(".data..read_mostly").

Control flow: Generic code uses these constants for alignment, padding, and section placement.

State and persistence behavior: No runtime state beyond linker section placement of annotated objects.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates networking skb allocation, percpu/cache alignment, and linker script sections..

Risks: Changing line size or padding affects performance and potentially DMA/network headroom assumptions.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 19 lines, 389 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cache.h -->
