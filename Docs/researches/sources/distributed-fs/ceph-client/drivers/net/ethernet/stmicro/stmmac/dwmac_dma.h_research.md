<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac_dma.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac_dma.h

## Purpose
Defines common pre-DWMAC4 DMA register offsets, channel address helpers, status/control/interrupt masks, AXI mode fields, register dump sizes, and common helper prototypes.

## Important APIs, Types, And Functions
Macros cover `DMA_BUS_MODE`, poll-demand registers, descriptor base registers, `DMA_STATUS` event bits, RX/TX/common masks, `DMA_CONTROL` start/stop/flush bits, interrupt enable masks, missed-frame counter, channel offset helpers, RX watchdog, AXI LPI/OSR/UNDEF fields, current buffer registers, and hardware feature register. Prototypes expose common DMA start/stop/IRQ/reset and poll helpers.

## Control Flow
No runtime control flow except `dma_chan_base_addr`, which maps common register offsets to per-channel offsets.

## State And Persistence
No state is stored. It describes hardware DMA register state used by DWMAC100 and DWMAC1000 code.

## Dependencies And Integration Points
Used by `dwmac_lib.c`, `dwmac100_dma.c`, and `dwmac1000_dma.c`. It integrates older DMA engines with STMMAC's `stmmac_dma_ops`.

## Risks
Interrupt mask definitions are shared across older cores and must be paired with correct channel offsets. Common helper prototypes assume this older register layout, not DWMAC4. Debug state masks are only used when `DWMAC_DMA_DEBUG` is enabled.

## Test Signals
Compile coverage for DWMAC100/1000, DMA reset/poll demand/start/stop, RX/TX IRQ masks, AXI config, RX watchdog, and register dump sizes validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac_dma.h -->
