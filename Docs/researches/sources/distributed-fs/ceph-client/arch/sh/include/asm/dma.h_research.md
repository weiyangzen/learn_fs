# sources/distributed-fs/ceph-client/arch/sh/include/asm/dma.h



Source read size: 133 lines, 3161 bytes.



Purpose: legacy SH DMA API contract.

Important APIs/types/functions: `struct dma_ops`, `struct dma_channel`, `struct dma_info`, mode/flag enums, `dma_xfer`, `dma_read/write`, channel lookup, wait/configure/register APIs, sysfs hooks.

Control flow: clients request/configure/start/wait on virtual channels provided by DMAC drivers.

State and persistence: per-channel state, busy flags, waitqueues, device objects.

Dependencies and integration points: legacy SH DMA drivers and consumers.

Risks and test signals: API is legacy and conflicts with DMAengine; channel lifetime matters. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
