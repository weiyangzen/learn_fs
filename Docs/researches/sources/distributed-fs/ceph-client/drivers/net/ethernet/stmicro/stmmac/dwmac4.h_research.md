<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4.h

## Purpose
Defines the DWMAC4/5 MAC and MTL register map, bit fields, helper address calculators, interrupt bits, feature bits, queue routing, filtering, EEE, CBS, debug, and L3/L4 filter constants.

## Important APIs, Types, And Functions
Important macros include `GMAC_CONFIG`, queue control registers, address/hash helpers, `GMAC_HW_FEATURE*` fields, `MTL_CHAN_*` helpers, ETS/CBS register helpers, interrupt masks, `GMAC_CORE_INIT`, and PCS status masks. It declares `dwmac4_dma_ops` and `dwmac410_dma_ops`.

## Control Flow
No runtime flow exists in the header, but inline helpers choose default or platform-provided register strides from `struct dwmac4_addrs`, affecting all DWMAC4 core/DMA register accesses.

## State And Persistence
No state is stored. The constants describe persistent hardware registers and allow platform-specific address remapping via `dwmac4_addrs`.

## Dependencies And Integration Points
Includes `common.h`; used by DWMAC4 core, DMA, lib, descriptors, DWMAC5, and platform glue such as Visconti. It is central to queue, MTL, feature, and offload support.

## Risks
Address helper changes can affect every queue/channel register access. `DMA_CHANNEL_NB_MAX` in the DMA header is separate, so register dump coverage may not reflect all hardware channels. Feature-bit interpretation must stay synchronized with Synopsys databooks.

## Test Signals
Builds across DWMAC4/5 users, feature decode, multi-queue routing, CBS, VLAN fail queueing, L3/L4 filters, EEE, PCS status, and ethtool register dumps indirectly validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4.h -->
