<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_dma.c

## Purpose
Implements DWMAC4 DMA operations: system bus/AXI setup, per-channel init, descriptor base programming including 64-bit high halves, MTL RX/TX operation modes, feature discovery, TSO, queue mode, buffer size, split-header, and time-based scheduling enable.

## Important APIs, Types, And Functions
Exports `dwmac4_dma_ops` and `dwmac410_dma_ops`. Key functions include `dwmac4_dma_init`, `dwmac4_dma_init_channel`, `dwmac410_dma_init_channel`, `dwmac4_dma_init_rx_chan/tx_chan`, `dwmac4_dma_rx_chan_op_mode`, `dwmac4_dma_tx_chan_op_mode`, `dwmac4_get_hw_feature`, `dwmac4_enable_tso`, `dwmac4_enable_sph`, and `dwmac4_enable_tbs`.

## Control Flow
STMMAC calls common reset, global DMA init, per-channel init, RX/TX descriptor-base setup, then MTL operation mode setup. RX mode selects store-and-forward or thresholds, sets queue FIFO size, disables TCP error forwarding, and enables flow control if FIFO and queue type allow. TX mode selects SF/threshold, queue enable mode, and FIFO size. Feature discovery reads four GMAC hardware feature registers and populates capabilities for checksum, timestamps, queues, FIFO sizes, TSO, SPH, FPE, EST, FRP, TBS, and address width.

## State And Persistence
State is DMA and MTL channel registers, descriptor base high/low registers, FIFO/threshold config, capability fields, and offload enable bits. No disk state exists.

## Dependencies And Integration Points
Depends on DWMAC4 headers/lib helpers, STMMAC DMA config, AXI config, platform `dwmac4_addrs`, and DWMAC4/5 feature consumers in the core.

## Risks
Flow-control threshold constants are tuned by FIFO size and may overflow at 4 KiB. Feature decode converts encoded FIFO/address widths and must match hardware. `DMA_CHANNEL_NB_MAX` register dumps only one channel despite hardware supporting more. Enabling TBS verifies EDSE but only DWMAC410 ops expose it.

## Test Signals
DMA init for fixed/mixed/AAL/EAME/DCHE/MSI modes, 64-bit descriptor base writes, RX/TX SF and threshold modes, AVB vs DCB queue enable, feature register decode, TSO toggling, SPH enable and buffer size, TBS enable failure path, and multi-queue traffic are primary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_dma.c -->
