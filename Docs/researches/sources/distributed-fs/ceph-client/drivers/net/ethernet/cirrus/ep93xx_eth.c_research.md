<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/ep93xx_eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/ep93xx_eth.c

## Purpose

`ep93xx_eth.c` is the platform Ethernet driver for the Cirrus EP93xx on-chip MAC. It implements a NAPI netdev with fixed-size DMA descriptor/status rings, simple MDIO access through MAC registers, ethtool MII controls, and OF probing through `cirrus,ep9301-eth`.

## Important APIs, Types, and Functions

Hardware layout is modeled by `struct ep93xx_rdesc`, `ep93xx_rstat`, `ep93xx_tdesc`, `ep93xx_tstat`, and aggregate coherent `struct ep93xx_descs`. `struct ep93xx_priv` owns the mapped register base, IRQ, descriptor DMA block, per-entry RX/TX bounce buffers, RX/TX ring pointers, NAPI object, `mii_if_info`, and MDIO divisor.

Important functions include `ep93xx_mdio_read`, `ep93xx_mdio_write`, `ep93xx_rx`, `ep93xx_poll`, `ep93xx_xmit`, `ep93xx_tx_complete`, `ep93xx_irq`, `ep93xx_alloc_buffers`, `ep93xx_free_buffers`, `ep93xx_start_hw`, `ep93xx_stop_hw`, `ep93xx_open`, `ep93xx_close`, `ep93xx_ioctl`, ethtool link helpers, `ep93xx_eth_probe`, and `ep93xx_eth_remove`.

## Control Flow

Probe maps the MMIO resource, resolves `phy-handle` and its `reg` property, allocates a netdev, reads the hardware MAC from `REG_INDAD0..5` or generates a random one, wires NAPI/netdev/ethtool ops, requests the memory region, initializes generic MII callbacks, and registers the device.

Open allocates a coherent descriptor/status block plus per-entry kmalloc buffers mapped with streaming DMA, enables NAPI, resets and starts hardware, initializes software ring pointers and locks, requests the shared IRQ, unmasks global interrupt delivery, and starts the queue. Hardware start programs RX/TX descriptor and status queue base/current/length registers, enables bus mastering, enqueues all RX descriptors/status entries, writes the station MAC, sets max frame length, and enables RX/TX.

RX NAPI scans status entries until budget or until `RFP` bits are absent. It validates EOF/EOB/index, accounts hardware errors, strips FCS when indicated, syncs the reusable RX buffer for CPU access, copies into a fresh SKB, syncs the buffer back for device use, and calls `napi_gro_receive`. After polling, it returns consumed RX descriptors/status entries to hardware. TX copies SKB data into pre-mapped per-entry TX buffers, enqueues one descriptor, tracks `tx_pending`, stops the queue when all eight entries are outstanding, and completion reclaims status entries and wakes the queue.

## State and Persistence Behavior

State is volatile and rebuilt on each open. Descriptor memory and RX/TX buffers are allocated on open and freed on close/remove. The driver uses copy-based RX/TX rather than owning SKBs in descriptors, so persistent per-packet state is limited to ring indices and mapped buffers. Link state is exposed through generic MII helpers, not phylib.

## Dependencies and Integration Points

Dependencies include platform resources, OF `phy-handle`, DMA mapping, NAPI/GRO, generic MII/ethtool helpers, and raw MMIO accessors. The netdev advertises SG and hardware checksum features, but the implementation still copies packet data into fixed buffers.

## Risks and Edge Cases

Probe has a leak risk pattern: if `of_parse_phandle` or PHY ID parsing fails after `ioremap`, the early return does not pass through `ep93xx_eth_remove`. TX ring size is only eight entries, so queue stop/wake and `tx_pending` accounting are important. RX allocation failure drops a packet but still advances the ring. Hardware reset/start polling uses short 10 ms windows. The driver requests the memory region after ioremap, which is unusual and makes failure paths sensitive.

## Test Signals

Signals include OF probe with valid and missing `phy-handle`, open/close/remove leak checks, MDIO read/write timeout logs, RX/TX traffic, TX queue full/wake behavior, NAPI interrupt masking/unmasking, RX error bits, random MAC fallback, MTU-sized packet handling up to `MAX_PKT_SIZE`, and ethtool MII operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/ep93xx_eth.c -->
