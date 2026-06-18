# sources/distributed-fs/ceph-client/arch/sh/include/asm/dma-register.h



Source read size: 50 lines, 1708 bytes.



Purpose: common SH DMAC register offsets and CHCR/DMAOR bit definitions.

Important APIs/types/functions: SAR/DAR/TCR/CHCR/DMAOR offsets, DMAOR flags, request/address increment modes, CHCR enable/end/interrupt bits.

Control flow: no flow; controller code combines bitfields and writes MMIO.

State and persistence: hardware register state.

Dependencies and integration points: legacy DMA and dmaengine SH drivers.

Risks and test signals: bitfield errors break DMA direction/size/interrupts. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
