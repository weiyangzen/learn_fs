<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100.h

## Purpose
Register and bit definitions for the older DWMAC100 10/100 MAC and DMA block. It is consumed by DWMAC100 core and DMA implementation files.

## Important APIs, Types, And Functions
Defines MAC CSR offsets (`MAC_CONTROL`, address/hash/MII/flow/VLAN registers), control bits for duplex, port select, loopback, filtering, and flow-control pause time. Defines DMA bus-mode PBL mask, transmit threshold enum values, stop-on-empty/operate-on-second-frame bits, missed-frame counter masks, and declares `dwmac100_dma_ops`.

## Control Flow
The header has no runtime control flow; it controls how the C files interpret memory-mapped registers and construct values for init, filtering, flow control, and diagnostics.

## State And Persistence
No state is stored in the header. Its macros describe persistent hardware state written into MAC/DMA registers during device operation.

## Dependencies And Integration Points
Includes `linux/phy.h` and `common.h`; used by `dwmac100_core.c` and `dwmac100_dma.c`. It bridges generic STMMAC ops to the DWMAC100 register layout.

## Risks
Bit definitions directly encode hardware ABI. Mistakes affect register programming globally. The missed-frame counter masks and comments contain legacy naming/typos, so diagnostics should be verified against the databook.

## Test Signals
Compile coverage of DWMAC100, ethtool register dumps, flow-control register values, multicast filter modes, TX threshold selection, and missed-frame counter increments validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100.h -->
