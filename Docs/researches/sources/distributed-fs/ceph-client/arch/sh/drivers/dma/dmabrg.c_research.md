# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dmabrg.c



Source read size: 195 lines, 5287 bytes.



Purpose: SH7760 DMABRG interrupt broker for USB and audio DMA events independent of the traditional SH DMAC.

Important APIs/types/functions: `dmabrg_request_irq()`, `dmabrg_free_irq()`, `dmabrg_irq()`, `dmabrg_enable_irq()`, `dmabrg_disable_irq()`, `dmabrg_handlers`, and DMABRGCR/DMAOR/DMARSRA register programming.

Control flow: init allocates ten handler slots, reserves DMAC channel 0 when possible, enables bridge mode in DMAOR, and requests three hardware IRQ lines. The shared handler reads and acknowledges DMABRGCR, masks disabled events, dispatches USB completion/error first, then iterates audio full/half events and calls registered callbacks.

State and persistence: global handler table, DMABRG enable/status register bits, DMAC channel 0 reservation, and IRQ registrations persist after subsys init.

Dependencies and integration points: integrates SH7760 USB/audio drivers through `asm/dmabrg.h`, raw MMIO, generic IRQs, and optional legacy SH DMA reservation.

Risks and test signals: no locking around handler registration versus interrupt dispatch; calling a NULL handler would fault if an enabled event fires after free; bridge mode blocks DMAC0 use. Test USB/audio DMA interrupts, request/free races, masked events, and DMAC0 reservation conflict.
