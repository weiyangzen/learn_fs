<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000.h

## Purpose
Register map and bit definitions for the DWMAC1000 GMAC generation, including MAC, PCS, EEE, PMT, filtering, DMA bus/control, flow-control thresholds, debug, extended hash, and PTP auxiliary timestamp registers.

## Important APIs, Types, And Functions
Defines `GMAC_*` offsets, PMT `enum power_event`, inter-frame gap, DMA bus mode and operation-mode bits, threshold enums (`ttc_control`, `rtc_control`, `rfa`, `rfd`), hash/address helpers, PTP auxiliary snapshot bits, and declares `dwmac1000_dma_ops`.

## Control Flow
No executable flow exists. The constants drive `dwmac1000_core.c` and `dwmac1000_dma.c` register operations for init, filters, EEE, PMT, PCS, DMA operation mode, feature discovery, and PTP.

## State And Persistence
The header stores no state. It defines hardware state layout for memory-mapped registers that persist until reset or reprogramming.

## Dependencies And Integration Points
Includes `linux/phy.h` and `common.h`; integrates with generic STMMAC core, PCS, PTP, DMA, and ethtool diagnostics by providing exact register encodings.

## Risks
Threshold encodings and FIFO flow-control masks are hardware-specific and easy to misuse. Address helper behavior changes after register 15. PTP auxiliary snapshot bits are tied to GMAC3 timestamp layout and should not be applied to incompatible cores.

## Test Signals
Build coverage, DWMAC1000 register dump sanity, PCS interrupt behavior, EEE timers, PMT wake, RX/TX flow-control threshold behavior, feature-register decode, and PTP external timestamp tests exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000.h -->
