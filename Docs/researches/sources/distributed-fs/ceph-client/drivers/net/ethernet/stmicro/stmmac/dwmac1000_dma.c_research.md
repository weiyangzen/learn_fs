<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000_dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000_dma.c

## Purpose
Implements DMA operations for DWMAC1000, including AXI bus programming, channel initialization, RX/TX descriptor base setup, operation modes, register dumps, hardware feature decode, and RX watchdog.

## Important APIs, Types, And Functions
Exports `dwmac1000_dma_ops`. Key functions are `dwmac1000_dma_axi`, `dwmac1000_dma_init_channel`, `dwmac1000_dma_init_rx/tx`, `dwmac1000_dma_operation_mode_rx/tx`, `dwmac1000_configure_fc`, `dwmac1000_get_hw_feature`, and `dwmac1000_rx_watchdog`.

## Control Flow
STMMAC calls reset via common `dwmac_dma_reset`, initializes bus/channel bits, writes descriptor base addresses, configures AXI limits/burst settings, selects store-and-forward or threshold modes, and enables common DMA helpers for IRQ/start/stop. RX mode also enables embedded flow control when RX FIFO is at least 4 KiB. Feature discovery reads `DMA_HW_FEATURE` and populates `dma_features`, returning `-EOPNOTSUPP` for old zero-valued registers.

## State And Persistence
State is DMA channel registers, AXI bus mode, descriptor base addresses, interrupt masks, RX watchdog, and decoded `dma_features`. No persistent storage exists.

## Dependencies And Integration Points
Depends on `dwmac1000.h`, common `dwmac_dma.h` helpers, STMMAC DMA config, AXI config, and the common interrupt/start/stop paths in `dwmac_lib.c`.

## Risks
AXI UNDEF semantics are inverted/read-only, so platform AXI values must be valid. Flow-control thresholds are simplified to full-minus-1K/full-minus-2K. Feature decode assumes databook bit positions. Only low 32 bits of descriptor base are written, so DMA addressing support is limited here.

## Test Signals
DMA init register values for PBL/RPBL/ATDS/AAL, AXI burst/OSR settings, RX/TX SF vs threshold modes, FIFO-size flow-control behavior, hardware feature decode on old/new IP, RX watchdog writes, and normal/abnormal IRQ handling through common code are useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000_dma.c -->
