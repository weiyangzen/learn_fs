# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/ni/nixge.c

## Purpose

`nixge.c` is a platform Ethernet driver for the National Instruments XGE Management MAC exposed through device tree. It binds to `ni,xge-enet-2.00` and `ni,xge-enet-3.00`, maps AXI DMA and control register windows, allocates a `net_device`, drives TX/RX rings, connects a PHY through OF/PHYLIB, and exposes netdev and ethtool operations.

The driver is not a distributed filesystem component directly; it is part of the Linux network stack underneath the Ceph client tree. Its operational relevance is that Ceph traffic depends on this NIC driver for packet delivery, link state, DMA correctness, interrupt handling, and MTU behavior on systems using NI XGE hardware.

## Important APIs, Types, and Functions

- `struct nixge_priv`: private per-netdev state. It stores `ndev`, `napi`, device pointer, OF PHY node/mode, link/speed/duplex cache, MDIO bus, mapped `ctrl_regs`/`dma_regs`, TX/RX IRQs, TX/RX descriptor rings, TX skb metadata, descriptor cursors, and RX/TX interrupt coalescing counts.
- `struct nixge_hw_dma_bd`: hardware buffer descriptor layout with next pointer, buffer physical address, control/status words, app words, and a software ID offset used here to remember the skb pointer.
- `struct nixge_tx_skb`: software metadata for a TX descriptor mapping, including skb ownership, DMA address, size, and whether the mapping came from a page fragment.
- Descriptor address helpers: `nixge_hw_dma_bd_set_addr`, `nixge_hw_dma_bd_set_phys`, `nixge_hw_dma_bd_set_next`, `nixge_hw_dma_bd_set_offset`, and `nixge_hw_dma_bd_get_addr` hide 32-bit versus 64-bit physical-address fields.
- MMIO helpers: `nixge_dma_write_reg`, `nixge_dma_write_desc_reg`, `nixge_dma_read_reg`, `nixge_ctrl_write_reg`, `nixge_ctrl_read_reg`, plus poll wrappers over `readl_poll_timeout`.
- Ring lifecycle: `nixge_hw_dma_bd_init`, `nixge_hw_dma_bd_release`, `nixge_device_reset`, `__nixge_device_reset`, and `nixge_dma_err_handler`.
- TX path: `nixge_start_xmit`, `nixge_check_tx_bd_space`, `nixge_start_xmit_done`, and `nixge_tx_skb_unmap`.
- RX/NAPI path: `nixge_rx_irq`, `nixge_poll`, and `nixge_recv`.
- Device lifecycle: `nixge_probe`, `nixge_open`, `nixge_stop`, `nixge_remove`, `nixge_of_get_resources`.
- PHY/MDIO: `nixge_mdio_setup`, Clause 22 and Clause 45 read/write helpers, `nixge_handle_link_change`, `of_phy_connect`, fixed-link registration, and `of_get_phy_mode`.
- ethtool/netdev hooks: `nixge_ethtools_get_drvinfo`, `nixge_ethtools_get_coalesce`, `nixge_ethtools_set_coalesce`, `nixge_ethtools_set_phys_id`, `nixge_netdev_ops`, and `nixge_ethtool_ops`.

## Control Flow

Probe starts in `nixge_probe`. It allocates an Ethernet device, attaches `nixge_netdev_ops` and `nixge_ethtool_ops`, sets SG support and MTU bounds, obtains a MAC address from nvmem cell `"address"` or falls back to a random MAC, initializes private state and NAPI, maps resources according to IP version, programs the MAC registers, obtains named TX/RX IRQs, configures default coalescing, optionally registers an OF MDIO bus, resolves PHY mode and `phy-handle` or fixed-link, and registers the netdev.

Open starts with `nixge_device_reset`, which resets both DMA channels and allocates/initializes rings. RX descriptors are prefilled with jumbo-sized skb buffers, mapped for DMA, linked into a circular ring, and handed to the RX DMA channel. TX descriptors are linked and the TX DMA channel is started but only transmits after the TX tail descriptor register is written. Open then connects and starts the PHY, initializes the DMA error tasklet, enables NAPI, requests TX and RX IRQs, and starts the TX queue.

TX begins in `nixge_start_xmit`. It verifies descriptor space for the skb head plus fragments, maps the skb head with SOF, maps each fragment, marks EOF on the final descriptor, stores the skb only in the final descriptor's software slot, writes the TX tail descriptor register, and advances the software tail. TX completion is interrupt driven: `nixge_tx_irq` acknowledges IOC/delay status and calls `nixge_start_xmit_done`, which scans completed descriptors from `tx_bd_ci`, unmaps DMA, frees the skb when present, updates netdev TX stats, clears status, advances the completion cursor, and wakes the queue when work was reclaimed.

RX completion is NAPI driven. `nixge_rx_irq` acknowledges RX IOC/delay status, disables RX completion/delay interrupts, and schedules NAPI. `nixge_poll` calls `nixge_recv`, which scans completed RX descriptors, unmaps the old buffer, trims length to the jumbo maximum, builds an skb, marks checksum as `CHECKSUM_NONE`, passes it to GRO, allocates and maps a replacement skb, resets descriptor state, advances `rx_bd_ci`, and finally updates the RX tail descriptor register. If NAPI finishes under budget, it either reschedules if new RX status is already pending or re-enables RX interrupts.

DMA error IRQ handling disables both TX and RX DMA interrupt sources and schedules `nixge_dma_err_handler`. The tasklet resets both DMA channels, unmaps and clears all TX descriptors, clears RX statuses, resets software cursors, reprograms coalescing/delay/IRQ bits, restarts RX and TX descriptor channels, and re-arms the tail pointers.

Stop shuts down the queue and NAPI, disconnects the PHY, clears DMA run/stop bits, kills the tasklet, frees both IRQs, and releases descriptor rings and skb buffers. Remove unregisters the netdev, deregisters fixed-link if needed, drops the PHY node, unregisters MDIO, and frees the netdev.

## State and Persistence Behavior

Most state is volatile kernel runtime state in `struct nixge_priv`: descriptor memory, skb DMA mappings, IRQ numbers, link cache, coalescing counts, and OF/MDIO handles. Descriptor rings are coherent DMA allocations and are recreated on open/reset and released on stop or probe failure. RX skb pointers are persisted in descriptor software offset fields, which is convenient but fragile because it relies on pointer-size-safe casting through DMA descriptor fields.

The MAC address can persist in hardware registers during driver lifetime. At probe, it is sourced from nvmem when available and valid, otherwise generated randomly. `nixge_net_set_mac_address` updates both `dev_addr` and hardware registers. Coalescing settings are stored in private fields and applied during ring initialization; the setter refuses changes while the interface is running. There is no suspend/resume implementation in this file.

## Dependencies and Integration Points

- Linux platform driver and OF matching via `module_platform_driver`, `of_device_id`, `platform_get_irq_byname`, `devm_platform_get_and_ioremap_resource`, and named resource lookup for v3.
- netdev core through `alloc_etherdev`, `register_netdev`, NAPI, `ndo_open`, `ndo_stop`, `ndo_start_xmit`, `ndo_change_mtu`, `ndo_set_mac_address`, and `ndo_validate_addr`.
- PHYLIB and OF MDIO through `of_phy_connect`, fixed-link helpers, `of_mdiobus_register`, `devm_mdiobus_alloc`, and ethtool PHY ksettings delegates.
- DMA API through coherent descriptor allocations and streaming skb maps/unmaps.
- ethtool for driver info, coalescing, link settings, and physical LED identification.
- nvmem consumer API for MAC address retrieval.

## Risks and Edge Cases

- RX allocation failure in `nixge_recv` returns early after consuming a completed descriptor without replacing it, leaving throughput dependent on later completions and tail updates.
- RX DMA mapping failure logs an error but continues to install the failed mapping into the descriptor, with a `FIXME` comment. This is a correctness risk under DMA pressure.
- `nixge_hw_dma_bd_release` unmaps every RX descriptor if `rx_bd_v` exists, regardless of whether mapping succeeded for each descriptor, so partial initialization failures rely on zeroed coherent memory and may attempt to unmap address zero.
- TX descriptor space check uses the descriptor at `tx_bd_tail + num_frag`; this accounts for head plus fragments indirectly, but ring-full behavior is subtle and can return `NETDEV_TX_OK` after stopping the queue without consuming the skb.
- MTU changes are rejected while running, reducing live reconfiguration risk but requiring operational downtime for jumbo changes.
- The DMA error tasklet reuses existing RX skb mappings and does not allocate new RX buffers; it assumes RX descriptors still own valid buffers after reset.
- The driver has no hardware checksum offload, VLAN acceleration, or advanced stats; all RX packets are marked `CHECKSUM_NONE`.

## Test Signals

- Build coverage through kernel compilation with NI XGE enabled and both 32-bit and 64-bit physical-address configurations.
- Device-tree probe tests for both compatible strings, including v2 single-resource mapping and v3 named `"dma"`/`"ctrl"` resources.
- Runtime smoke tests: interface open/close, DHCP/static IP, ping, sustained TCP/UDP traffic, and `ethtool -i`.
- TX/RX ring stress with fragmented skbs, jumbo MTU up to 9000, queue stop/wake behavior, and DMA mapping error injection if available.
- PHY tests: fixed-link and external MDIO PHY, link up/down transitions, autonegotiated speed/duplex reporting, and ethtool link ksettings.
- Interrupt tests: separate TX/RX IRQ request failure paths, NAPI budget exhaustion, RX interrupt re-enable, and DMA error interrupt recovery.
- ethtool tests for coalescing only while down and LED identify state transitions.
