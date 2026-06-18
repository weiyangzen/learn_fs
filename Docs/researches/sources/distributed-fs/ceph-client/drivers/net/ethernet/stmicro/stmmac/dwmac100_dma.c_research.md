<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100_dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100_dma.c

## Purpose
Implements DMA operations for the DWMAC100 controller: bus/PBL setup, descriptor base programming, TX threshold selection, register dump, and missed-frame diagnostics.

## Important APIs, Types, And Functions
Exports `dwmac100_dma_ops`. Key functions are `dwmac100_dma_init`, `dwmac100_dma_init_rx/tx`, `dwmac100_dma_operation_mode_tx`, `dwmac100_dump_dma_regs`, and `dwmac100_dma_diagnostic_fr`.

## Control Flow
STMMAC resets through common `dwmac_dma_reset`, calls init to write bus mode and default interrupt mask, writes RX/TX descriptor base registers, configures TX threshold based on requested mode, and uses common helpers for DMA start/stop/IRQ/poll demand. Diagnostics reads the missed-frame counter and accumulates overflow and missed counters.

## State And Persistence
State is DMA registers and `stmmac_extra_stats` counters. Descriptor bases are written as low 32-bit DMA addresses. No durable persistence exists.

## Dependencies And Integration Points
Depends on `dwmac100.h`, `dwmac_dma.h`, common DMA helper functions, and STMMAC DMA op dispatch.

## Risks
No RX operation mode callback is supplied. TX threshold configuration ORs bits without clearing previous threshold bits, so repeated mode changes may preserve stale threshold bits. Descriptor addressing is 32-bit. Missed-frame counter interpretation must match hardware.

## Test Signals
PBL programming, descriptor base writes, TX threshold changes from ethtool/module settings, missed-frame counter increments, common DMA interrupt handling, and register dump layout are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100_dma.c -->
