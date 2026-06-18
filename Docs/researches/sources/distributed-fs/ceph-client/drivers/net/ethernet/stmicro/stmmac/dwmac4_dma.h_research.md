<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_dma.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_dma.h

## Purpose
Defines DWMAC4 DMA register offsets, channel address helpers, interrupt masks, control bits, TBS control, ring-length/tail-pointer/current-pointer registers, status masks, and prototypes for lib helpers.

## Important APIs, Types, And Functions
The `dma_chanx_base_addr` helper supports default and platform-specific `dwmac4_addrs`. Macros define global bus mode, system bus mode, AXI LPI/OSR, channel TX/RX control, descriptor base high/low, ring length, interrupt enable/status masks, RX watchdog, and current descriptors/buffers. It declares `dwmac4_dma_reset`, IRQ enable/disable, start/stop, interrupt, ring length, and tail pointer helpers.

## Control Flow
No runtime flow except address calculation. The macros drive all DWMAC4 DMA/lib register access.

## State And Persistence
No stored state. It describes DMA channel register state that persists in hardware.

## Dependencies And Integration Points
Used by `dwmac4_dma.c` and `dwmac4_lib.c`; depends on `struct dwmac4_addrs` from common STMMAC definitions.

## Risks
Interrupt summary bit definitions differ between 4.00 and 4.10; the header carries separate masks that must be paired with the correct ops table. Channel address remapping must be consistent across DMA and MTL users. `DMA_CHANNEL_NB_MAX` is set to 1 for dumps, not actual max capability.

## Test Signals
Compile coverage, register dump offsets, interrupt handling on 4.00 vs 4.10, ring length/tail pointer writes, 64-bit base address registers, and TBS register writes validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_dma.h -->
