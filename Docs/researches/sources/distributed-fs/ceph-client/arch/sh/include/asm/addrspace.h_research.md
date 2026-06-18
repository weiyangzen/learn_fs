# sources/distributed-fs/ceph-client/arch/sh/include/asm/addrspace.h



Source read size: 63 lines, 1896 bytes.



Purpose: SH privileged segment address helper.

Important APIs/types/functions: `PXSEG`, `P1SEGADDR`, `P2SEGADDR`, `P3SEGADDR`, `P4SEGADDR`, `IS_29BIT`, `P3_ADDR_MAX`.

Control flow: macros translate physical/virtual addresses for segmented SH CPUs or BUG outside 29-bit mode.

State and persistence: no storage; address interpretation affects all MMIO/cache paths.

Dependencies and integration points: MMU, cache, boot, DMA, and PCI code.

Risks and test signals: wrong segment conversion corrupts memory or MMIO. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
