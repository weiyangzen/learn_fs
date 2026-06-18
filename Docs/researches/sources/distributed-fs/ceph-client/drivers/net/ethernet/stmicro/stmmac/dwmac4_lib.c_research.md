<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_lib.c

## Purpose
Provides common DWMAC4 DMA/MAC helper functions used by the DWMAC4/4.10 DMA ops: reset, tail pointers, ring lengths, DMA start/stop, IRQ enable/disable, interrupt decoding, DWMAC4 MAC address programming, and MAC RX/TX enable.

## Important APIs, Types, And Functions
Exports helper functions declared in `dwmac4_dma.h`: `dwmac4_dma_reset`, `dwmac4_set_rx_tail_ptr`, `dwmac4_set_tx_tail_ptr`, `dwmac4_dma_start_tx/rx`, `dwmac4_dma_stop_tx/rx`, ring length setters, IRQ enable/disable, `dwmac4_dma_interrupt`, `stmmac_dwmac4_set_mac_addr`, and `stmmac_dwmac4_set_mac`.

## Control Flow
Reset sets software reset and polls up to 1 s. Start TX/RX sets DMA channel bits and also enables MAC TE/RE in `GMAC_CONFIG`; stop only clears DMA channel bits. Interrupt handling reads channel status/enables, masks by RX or TX direction, updates abnormal/normal stats, returns STMMAC action flags, and clears enabled pending bits.

## State And Persistence
State is hardware register bits, per-CPU IRQ stats, and `stmmac_extra_stats`. MAC address writes set the AE bit and default DMA channel selection for address filters. No durable persistence exists.

## Dependencies And Integration Points
Depends on DWMAC4 DMA and MAC headers, common status enums, STMMAC stats, and platform address overrides. Used by DWMAC4 DMA ops tables.

## Risks
Start enables MAC RX/TX globally but stop only stops DMA, so caller sequencing matters. Interrupt clear writes `intr_status & intr_en`, unlike older common DMA code. MAC address helper assumes non-null address and channel 0 destination selection. Reset timeout is longer than older DMA.

## Test Signals
Reset timeout behavior, start/stop register bits, IRQ counters/action returns for RX/TX/fatal/RBU/RPS/RWT/TBU/ERI, tail/ring writes, MAC address filter programming, and MAC enable/disable transitions are key checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_lib.c -->
