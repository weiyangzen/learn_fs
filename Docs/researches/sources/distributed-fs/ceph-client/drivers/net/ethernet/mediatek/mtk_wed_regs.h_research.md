# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_regs.h

## Purpose
This header is the MediaTek WED register and descriptor contract. It defines WED, WPDMA, WDMA, RRO/RROQM/RTQM, RX buffer manager, AMSDU, PCIe mirror, interrupt, DMA, reset, MIB, and descriptor bitfields used by the WED implementation.

## Important APIs and Types
- `struct mtk_wdma_desc` defines the packed four-word WDMA descriptor layout.
- `MTK_WED_RESET`, `MTK_WED_CTRL`, `MTK_WED_GLO_CFG`, and related bitfields describe major WED engine reset/enable/busy controls.
- `MTK_WED_RING_TX()`, `MTK_WED_RING_RX()`, `MTK_WDMA_RING_TX()`, and similar macros compute ring register offsets.
- WPDMA/WDMA interrupt, prefetch, reset-index, coherent MIB, and DMA global configuration macros are used by setup, teardown, and diagnostics.
- RRO and AMSDU definitions expose v3 receive reorder and aggregation hardware programming surfaces.

## Control Flow
The header has no runtime control flow. It shapes control flow in users by providing register addresses, masks, and field encodings that decide how drivers poll busy bits, reset engines, program rings, and read counters.

## State and Persistence
All state represented here is hardware state. Driver code persists values in device registers, DMA descriptors, and hardware counters using these offsets and masks.

## Dependencies and Integration Points
It assumes kernel bit helpers such as `BIT()` and `GENMASK()`. It is included by WED core, WO MCU, and WO queue code. The macros align the Ethernet DMA path with Wi-Fi offload DMA, PCIe interrupt routing, RX reorder offload, and hardware MIB/statistics paths.

## Risks and Test Signals
Risks are register drift between WED hardware versions, duplicated definitions such as `MTK_WED_PCIE_CFG_BASE`, field-width mistakes, and accidental use of v2/v3-only bits on older chips. Good validation signals are register programming traces during WED bring-up, DMA ring traffic, reset recovery, interrupt routing, MIB reads, and compile coverage across supported MediaTek SoCs.
