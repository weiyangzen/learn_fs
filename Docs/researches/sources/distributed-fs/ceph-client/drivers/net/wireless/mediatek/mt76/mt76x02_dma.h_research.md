<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dma.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dma.h

Purpose: shared DMA/FCE descriptor definitions for mt76x02. It defines TXD/RXFCE/MCU message bitfields, DMA ports, RX headroom/ring sizes, and DMA init/disable prototypes.

Important APIs/types/functions: `enum dma_msg_port`, `MT_TXD_INFO_*`, `MT_RX_FCE_INFO_*`, `MT_MCU_MSG_*`, `mt76x02_wait_for_wpdma()`, `mt76x02_dma_init()`, and `mt76x02_dma_disable()`.

Control flow: declarative header with one inline polling helper used before enabling/disabling MAC/DMA. TX/RX and MCU transports compose these fields when preparing descriptors or USB in-band command headers.

State and persistence: no local state. Constants affect persistent hardware queue/FCE register programming during runtime.

Dependencies/integration: includes `mt76x02.h` and core `dma.h`; consumed by MMIO DMA, USB TX preparation, and MCU response parsing.

Risks: bitfield mismatches corrupt transfer lengths, ports, encryption flags, or MCU sequence IDs. Test signals include TX/RX on all queues, MCU request/response sequence matching, USB DMA header padding, and DMA idle polling on reset/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dma.h -->
