# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_dma.c

## Purpose
This file implements shared PCIe/MMIO WFDMA interrupt, NAPI, enable/disable/reset, prefetch, and WFSYS reset handling for MT792x devices.

## Important APIs, Types, And Functions
Exports include `mt792x_irq_handler()`, `mt792x_irq_tasklet()`, `mt792x_rx_poll_complete()`, `mt792x_dma_enable()`, `mt792x_wpdma_reset()`, `mt792x_wpdma_reinit_cond()`, `mt792x_dma_disable()`, `mt792x_dma_cleanup()`, `mt792x_poll_tx()`, `mt792x_poll_rx()`, and `mt792x_wfsys_reset()`. Internal helpers include chip-specific `mt792x_dma_prefetch()` and `mt792x_dma_reset()`.

## Control Flow
The hard IRQ disables host interrupts and schedules a tasklet if initialized. The tasklet reads and acks WFDMA interrupt status, traces it, masks active RX/MCU rings, handles MCU software wake interrupts, disables those sources while NAPI runs, then schedules TX/RX NAPI instances. RX poll completion re-enables the matching interrupt source. DMA enable programs prefetch windows, resets ring pointers, disables delayed interrupts, sets WFDMA global configuration bits, applies MT7925-specific priority settings, marks the dummy reinit bit, and enables TX/RX/MCU interrupts. Reset disables DMA, resets all TX/MCU/RX queues, checks TX status, reenables DMA, and resets RX queues. Poll paths require a PM reference and schedule wake work if the device is asleep.

## State And Persistence
State spans WFDMA registers, mt76 irqmask, NAPI enabled/scheduled state, queue head/tail/ring memory, PM wake counters, `MT_WFDMA_NEED_REINIT`, and WFSYS reset bits. WFSYS reset persists by toggling hardware reset and waiting for init done.

## Dependencies And Integration Points
It integrates mt76 DMA queues, Linux NAPI/tasklets/IRQ, connac PM, MT792x register maps, tracepoints, and bus reset flows in PCI/MT7925 code.

## Risks
Interrupt masking must pair with NAPI completion or rings can stall. PM references in poll functions must not be taken while firmware-owned. DMA busy polling can timeout during suspend/reset. Chip-specific prefetch values and MT7925 priority bits must match hardware ring allocation. WFSYS reset addresses differ for connac2 vs later chips.

## Test Signals
Sustained RX/TX, MCU event traffic, interrupt storm protection, PM sleep/wake while traffic arrives, WPDMA reinit after low power, forced reset, DMA timeout injection, and tracepoint IRQ visibility validate this file.
