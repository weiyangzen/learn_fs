# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-dev.c

## Purpose

`xgbe-dev.c` is the low-level hardware programming layer for AMD XGBE. It configures DMA, MTL queues, MAC filtering, VLAN, RSS, flow control, DCB, ECC, MDIO/XPCS access, descriptors, TX/RX enablement, timestamp/MMC counter handling, and device reset. It also publishes the `struct xgbe_hw_if` function table consumed by the netdev driver, PHY code, ethtool paths, DCB, debugfs, and PTP support.

The file translates driver-private state into concrete XGMAC register writes and descriptor bitfields using `xgbe-common.h`.

## Important APIs and Functions

- Hardware feature/config: `xgbe_init()`, `xgbe_exit()`, `xgbe_config_dma_bus()`, `xgbe_config_dma_cache()`, `xgbe_config_mtl_mode()`, `xgbe_config_queue_mapping()`, FIFO sizing, flow-control thresholds, and `xgbe_set_speed()`.
- Descriptor programming: `xgbe_tx_desc_init()`, `xgbe_rx_desc_init()`, `xgbe_tx_desc_reset()`, `xgbe_rx_desc_reset()`, `xgbe_tx_start_xmit()`, `xgbe_dev_xmit()`, and `xgbe_dev_read()`.
- Interrupt control: `xgbe_enable_dma_interrupts()`, MAC/MTL/ECC interrupt setup, and per-channel `xgbe_enable_int()`/`xgbe_disable_int()`.
- RSS/VXLAN: RSS key/table programming through `MAC_RSSAR/RSSDR`, feature-gated RSS enable/disable, VXLAN tunnel ID setup and tunneling enablement.
- Flow control/DCB: TX/RX pause configuration, PFC queue detection, FIFO distribution, DCB ETS traffic class programming, PFC reconfiguration, and netdev TC mapping.
- MAC/VLAN/filtering: MAC address programming, hash/perfect filter setup, promiscuous/all-multicast handling, VLAN hash table, VLAN stripping/filtering, jumbo mode, checksum offload.
- MDIO/XPCS: V1/V2 MMIO windowed XPCS access, V3 SMN-based access, external clause 22/45 MDIO reads/writes with completion wait, and MDIO mode selection.
- MMC/statistics: counter read width handling, interrupt accumulation, freeze/read/unfreeze bulk stats, and counter reset-on-read configuration.
- Lifecycle/export: `xgbe_init_function_ptrs_dev()` fills `struct xgbe_hw_if`; `xgbe_enable_mac_loopback()` and `xgbe_disable_mac_loopback()` support loopback tests.

## Control Flow

Device initialization flushes TX queues, configures DMA bus/cache/PBL/coalescing/buffer sizes/TSO/SPH/RSS, initializes descriptor rings, enables DMA interrupts, configures MTL scheduling/queue mapping/store-forward/thresholds/FIFOs/DCB, configures MAC address/filtering/jumbo/flow-control/speed/checksum/VLAN/MMC, then enables MAC and ECC interrupts. This path is called from `xgbe-drv.c` during start and restart.

TX control flow begins after `xgbe-drv.c` maps skb data. `xgbe_dev_xmit()` optionally emits a context descriptor for changed TSO MSS or VLAN tag, fills normal descriptors with DMA addresses and lengths, sets checksum/TSO/VLAN/PTP/VXLAN bits, accounts packet/byte totals, applies memory barriers, gives the first descriptor to hardware by setting OWN, advances `ring->cur`, and either rings the DMA tail pointer immediately or defers via `xmit_more`.

RX control flow reads the current descriptor, checks OWN, handles timestamp context descriptors, extracts first/last/context flags, split-header length, RSS hash/type, packet length, checksum and tunnel status, VLAN tag, error status, and per-queue accounting. The NAPI layer in `xgbe-drv.c` uses this parsed packet state to assemble skbs and recycle descriptors.

MDIO/XPCS access is selected by `pdata->vdata->xpcs_access`. V1 and V2 use MMIO window selection guarded by `xpcs_lock`; V3 uses AMD SMN reads/writes and updates halfwords within a 32-bit SMN word. External MDIO operations use MAC MDIO command registers and wait on `pdata->mdio_complete`, which is completed by the MAC interrupt path.

## State and Persistence Behavior

Most persistent runtime state is in `struct xgbe_prv_data`: hardware feature flags, queue counts, FIFO sizing limits, DCB policy pointers, PFC queue flags, RSS key/table/options, active VLAN bitmap, flow-control threshold arrays, cached netdev features, VXLAN port, PHY speed, interrupt mode, coalescing settings, and MMC stats. Ring-local persistent state includes cached TSO MSS and VLAN tag context plus coalescing counters. Hardware register state is volatile and reconstructed by `xgbe_init()` after reset, open, and restart.

Counters in `pdata->mmc_stats` accumulate hardware MMC values read on interrupt and stats queries. The code freezes counters for bulk reads and uses reset-on-read mode, making the software structure the long-lived counter accumulator.

## Dependencies and Integration Points

The file depends on kernel PHY/MDIO, PCI/SMN access, clocks, CRC helpers, bit reversal, netdev feature bits, VLAN/RSS/VXLAN concepts, DMA descriptor definitions, and xgbe private interfaces. It integrates with:

- `xgbe-drv.c` through `struct xgbe_hw_if` for open/close, TX/RX, NAPI, feature changes, stats, and restart.
- `xgbe-desc.c` through descriptor init/reset and mapped descriptor metadata.
- `xgbe-dcb.c` through DCB TC/PFC hardware callbacks.
- PTP timestamp helpers such as `xgbe_get_rx_tstamp()` and `xgbe_get_tx_tstamp()`.
- PHY and debugfs paths through MMD/MDIO register access.
- Netdev VLAN, RSS, checksum, GSO/VXLAN, and traffic-class feature APIs.

## Risks and Failure Modes

- Register programming order is critical. DMA/descriptor ownership barriers, tail-pointer writes, MAC/MTL/DMA enable order, and reset polling must remain correct to avoid hangs.
- MDIO completion relies on MAC interrupts. If interrupts are disabled or misrouted, external MDIO reads/writes time out.
- XPCS V3 SMN read-modify-write must preserve the opposite halfword. Bad offset handling can corrupt adjacent PCS registers.
- FIFO and PFC calculations depend on MTU, TC count, queue count, and delay estimates. Wrong thresholds can cause pause storms, loss where lossless is expected, or underutilized RX FIFO.
- RX parsing trusts descriptor status fields but contains length-underflow guards. Any hardware erratum around descriptor fields can surface as drops or checksum misclassification.
- RSS programming is serialized by `rss_mutex`, but callers must still ensure feature changes and device reset do not race in unsupported ways.
- `xgbe_disable_tx()` waits for DMA completion and queue drain; link-down cases are specially handled by returning early in completion wait and later cleanup paths. This reduces shutdown stalls but makes packet accounting and descriptor cleanup behavior important.

## Test Signals

Exercise full open/close/restart, MTU changes, TX/RX under load, TSO/checksum/VLAN/VXLAN offloads, RSS enable/disable and indirection changes, DCB/PFC policy changes, pause negotiation, MDIO access, PTP timestamping, hardware stats, ECC interrupt injection if available, and MAC loopback. Watch for DMA API warnings, descriptor ownership stalls, MDIO timeouts, NAPI budget livelocks, wrong RSS hashes, VLAN filter misses, bad MMC counter deltas, and timeout messages from TX/RX stop paths.
