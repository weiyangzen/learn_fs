# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_enet.c

## Purpose

`hns_enet.c` is the HNS net_device driver. It bridges Linux networking APIs to the HNAE/DSAF hardware abstraction, manages platform probe/remove, queue/ring and IRQ/NAPI lifecycle, TX descriptor submission, RX buffer recycling and GRO delivery, link and PHY handling, reset/service work, MTU and feature changes, multicast/unicast filtering, statistics, and v1/v2 hardware differences.

## Important APIs, Types, And Functions

Externally visible functions are `hns_nic_net_xmit_hw`, `hns_nic_init_phy`, `hns_nic_net_reset`, and `hns_nic_net_reinit`; the module registers `hns_nic_dev_driver`. The file defines descriptor fill variants for v1 and v2/TSO, TX stop logic, RX descriptor parsing, checksum marking, page reuse, ring polling, adaptive interrupt coalescing, IRQ handler, PHY link adjustment, IRQ affinity setup, open/stop/up/down flows, loopback/MTU cleanup helpers, feature filtering, address-list syncing, stats64, queue selection, service timer/work, AE notifier integration, and platform probe/remove.

## Control Flow

Probe allocates a multiqueue Ethernet device, reads OF/ACPI configuration and the AE handle reference, maps old/new port-id properties, initializes a MAC address, sets netdev/ethtool ops and feature flags, sets DMA mask, initializes service timer/work and state bits, then tries to acquire an HNAE handle. If the handle is not ready, a notifier retries later. Handle acquisition initializes PHY, ring data, version-specific descriptor ops, and registers the netdev.

Open sets real queue counts and calls `hns_nic_net_up`. Up requests IRQs for each TX/RX ring, enables NAPI and IRQs, programs the MAC address, starts AE hardware, starts PHY, clears DOWN state, and arms the service timer. Down stops timer, queues, carrier, PHY, AE hardware, disables rings/NAPI/IRQs, and reclaims TX buffers.

TX maps the skb head and fragments, fills descriptors, updates queue accounting/stats, commits descriptors with `wmb`, and submits to hardware. Mapping failure unwinds descriptors and DMA maps. RX NAPI reads fetched descriptor count, builds skbs from copied head plus page frags, validates buffer count and descriptor flags, marks checksum unnecessary when hardware protocol/error bits allow, delivers via GRO, and replenishes RX buffers. TX NAPI reclaims completed descriptors and wakes queues when ring space recovers.

Service work handles reset requests, XGMII link polling, LED updates, and stats updates. TX timeout sets a reset-request bit and schedules service work. MTU change may stop/reopen the device and, for v2 crossing the 2048-buffer threshold, reinitializes descriptors, clears fetched RX packets through a serdes-loopback drain helper, and resets page offsets before applying the new MTU.

## State And Persistence

`struct hns_nic_priv` holds the device fwnode, HNS version, port id, PHY mode, LED state, netdev/device pointers, HNAE handle, version-specific ops, ring-data array, cached link state, TX timeout counter, state bits, service timer, work item, and notifier. Ring state lives in `hnae_ring` descriptor arrays, DMA mappings, producer/consumer indexes, per-ring stats, and NAPI objects. Hardware state is reestablished during open/reset.

## Dependencies And Integration Points

The driver depends on the Linux netdev, NAPI, IRQ, DMA, PHY, OF/ACPI, VLAN, checksum, and platform-driver APIs. It integrates heavily with `hnae` handles and AE ops for start/stop, queue transmit, ring IRQ toggles, MAC/link/MTU/RSS/coalesce operations, LED/status/stats, and handle registration. `hns_ethtool_set_ops` attaches user-facing diagnostics.

## Risks And Test Signals

Major risks are DMA unwind correctness, descriptor count validation, ring index wraparound, queue stop/wake memory ordering, adaptive coalescing races across rings, reset/reinit state-bit deadlocks, MTU transitions while packets are fetched, PHY/link adjustments during traffic, and notifier/remove ordering. Test signals include probe/remove under OF and ACPI, sustained TX/RX with checksum/GSO/GRO, queue recovery after `NETDEV_TX_BUSY`, NAPI completion without interrupt loss, TX timeout reset recovery, MTU changes across 2048-byte RX buffer threshold, multicast/promisc/UC filtering, stats64 consistency, and no DMA mapping leak warnings.
