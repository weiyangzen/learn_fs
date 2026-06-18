<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac_lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac_lib.c

## Purpose
Common helper implementation for older DWMAC DMA/MAC blocks: DMA reset, poll demand, IRQ masks, start/stop, interrupt decoding, TX FIFO flush, and generic MAC address and MAC enable helpers.

## Important APIs, Types, And Functions
Exports `dwmac_dma_reset`, DMA poll/start/stop/IRQ helpers, `dwmac_dma_interrupt`, `dwmac_dma_flush_tx_fifo`, `stmmac_set_mac_addr`, `stmmac_set_mac`, and `stmmac_get_mac_addr`. Optional debug helpers decode TX/RX process state when compiled with `DWMAC_DMA_DEBUG`.

## Control Flow
Reset sets software reset and polls until clear. Poll helpers write demand registers. Start/stop toggle `DMA_CONTROL_ST/SR`. Interrupt handling reads channel status, optionally logs debug state, masks by RX/TX direction, updates abnormal and normal stats, returns STMMAC action flags, warns on unexpected PMT/MMC/line-interface bits, and clears low status bits. MAC address helper writes high/low words with AE; enable helper toggles generic RX/TX bits.

## State And Persistence
State is hardware DMA/MAC registers and stats counters. Exported MAC address registers retain programmed values until reconfigured/reset. No disk persistence exists.

## Dependencies And Integration Points
Depends on `common.h`, `dwmac_dma.h`, STMMAC stats/action enums, Linux iopoll, and is reused by DWMAC100 and DWMAC1000 DMA ops.

## Risks
Interrupt handling checks the global `DMA_INTR_ENA` register for RX enable rather than channel-specific enable in one path, which is legacy-layout sensitive. TX FIFO flush busy-waits without timeout. MAC address helper assumes `addr` is valid and sets AE even for high register 0.

## Test Signals
DMA reset timeout, poll demand, start/stop bits, abnormal IRQ cases, per-CPU normal IRQ counters, unexpected optional interrupt warnings, FIFO flush completion, MAC address round-trip, and MAC enable/disable register transitions are the key checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac_lib.c -->
