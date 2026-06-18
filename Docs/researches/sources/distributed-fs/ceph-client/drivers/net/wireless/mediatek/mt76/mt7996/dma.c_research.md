# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/dma.c

## Purpose
This file implements MT7996/MT7992/MT7990 DMA queue mapping, WFDMA setup, interrupt enablement, WED/NPU/HWRRO queue integration, RRO initialization/start, reset, and cleanup.

## Important APIs, Types, And Functions
Key exports are `mt7996_init_tx_queues()`, `mt7996_dma_prefetch()`, `mt7996_dma_start()`, `mt7996_dma_rro_init()`, `mt7996_dma_rro_start()`, `mt7996_dma_init()`, `mt7996_dma_reset()`, and `mt7996_dma_cleanup()`. Internal helpers include queue config macros in `mt7996_dma_config()`, TX NAPI `mt7996_poll_tx()`, prefetch base calculation, `mt7996_dma_disable()`, and `mt7996_dma_enable()`.

## Control Flow
DMA config maps logical mt76 TX/RX/MCU queues to hardware ring IDs, WFDMA instances, and interrupt bits based on chip, WA support, HIF2, HWRRO, and NPU. Init attaches mt76 DMA, disables/reset WFDMA, allocates TX/MCU/FWDL rings, allocates event/data/txfree/RRO/MSDU-page RX rings with WED/NPU flags when active, initializes queues/NAPI, initializes NPU queues, and enables DMA. Enable resets ring pointers, disables delayed interrupts, programs prefetch, busy/extension config, pause thresholds, HIF2 band routing/outstanding settings, RX interrupt redirection, and starts WFDMA/interrupts. RRO init allocates either v3.1 RXDMAD-C or older IND/MSDU-page rings. Reset disables DMA, cleans TX/RX/MCU queues, handles WFSYS reset and WED/NPU reset, resets ring memory and RX buffers with special WED RRO exceptions, then reenables DMA.

## State And Persistence
Persistent state includes `q_wfdma_mask`, `q_int_mask[]`, `q_id[]`, mt76 queue objects and flags, WED/NPU queue associations, HIF2 pointer/speed/width-derived tuning, irqmask, RRO mode, WED RRO EMI pointers, and WFDMA/host-config registers. Reset recreates hardware ring state while preserving driver queue objects.

## Dependencies And Integration Points
It integrates mt76 DMA and connac queue helpers, MediaTek WED offload, optional NPU support, MT7996 register macros, chip/band validity helpers, RRO page-map helpers, IRQ enable/disable, PCI HIF2 topology, and firmware WA capabilities.

## Risks
The combinatorial queue matrix is the largest risk: chip type, band count, WA, HIF2, WED RX, HWRRO mode, and NPU all change ring IDs, sizes, flags, interrupts, and base offsets. Reset paths must skip or reset WED RRO queues exactly as expected by hardware. HIF2 routing and outstanding tuning depend on PCIe link speed/width. Incorrect irq masks can leave TX-free or RX rings unserviced.

## Test Signals
Boot on MT7996/MT7992/MT7990, one/two PCIe HIFs, WED on/off, NPU on/off, HWRRO v3/v3.1, tri-band traffic, TX-free handling, RRO reorder traffic, firmware/SER reset, DMA cleanup, and queue/interrupt counters validate this file.
