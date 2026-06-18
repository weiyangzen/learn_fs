# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm63xx_enet.h

## Purpose
Defines constants and private state for the BCM63xx Ethernet MAC/switch driver. It centralizes default ring sizes, DMA burst limits, MTU limits, MIB counter indexes for MAC and switch blocks, the software MIB accumulator, and `struct bcm_enet_priv`.

## Important APIs, Types, and Functions
The header has no functions. Important constants are `BCMENET_DEF_RX_DESC`, `BCMENET_DEF_TX_DESC`, `BCMENET_DMA_MAXBURST`, `BCMENETSW_DMA_MAXBURST`, `BCMENET_TX_FIFO_TRESH`, and `BCMENET_MAX_MTU`. It enumerates MAC MIB indexes (`ETH_MIB_*`) and switch MIB indexes (`ETHSW_MIB_*`). `struct bcm_enet_mib_counters` stores accumulated or sampled statistics for both MAC and switch paths. `struct bcm_enet_priv` is the main driver-private object for both `bcm63xx_enet` and `bcm63xx_enetsw`.

## Control Flow
There is no direct runtime control flow. The layout of `struct bcm_enet_priv` drives the C file's lifecycle: probe initializes platform/clock/PHY/DMA fields, open allocates and programs ring fields, NAPI mutates RX/TX indices and counts, ethtool reads/writes ring/pause/link fields, timers use `rx_timeout` and `swphy_poll`, and remove/stop free resources based on pointers and flags stored here.

## State and Persistence
The private state covers MMIO base, IRQs, coherent descriptor DMA addresses and sizes, RX/TX descriptor rings, ring counters and cursor indices, RX buffer sizing and fragment pointers, timers, locks, PHY/MII state, forced link and pause settings, MIB counters, workqueue/mutex protection for stats, MAC/PHY clocks, device references, hardware MTU, switch-vs-MAC mode, switch port map/link cache, DMA channel masks, SRAM capability, channel width, and descriptor shift. The MIB register constants describe persistent hardware counters that are read and folded into software counters.

## Dependencies and Integration Points
Includes kernel types plus MII, mutex, PHY, and platform-device APIs, and BCM63xx-specific `bcm63xx_regs.h`, `bcm63xx_io.h`, and `bcm63xx_iudma.h`. It also depends on platform data types such as `struct bcm63xx_enetsw_port` and `ENETSW_MAX_PORT` from BCM63xx headers. It is consumed by `bcm63xx_enet.c` only, but it defines the shared contract between the MAC and switch halves of that file.

## Risks and Test Signals
Risks are structural: incorrect field types or MIB indexes can corrupt stats or descriptor control; wrong defaults can break low-memory devices; mismatched `dma_desc_shift` assumptions can set wrong wrap/SOP/EOP bits; and switch port array sizing must match platform data. Test signals are all BCM63xx build variants, MAC and switch probe/open/stop, ethtool stats/ring output, MIB counter rollover tests, RX/TX descriptor wrap tests, MTU boundary checks, and switch port polling with all valid `ENETSW_MAX_PORT` entries.
