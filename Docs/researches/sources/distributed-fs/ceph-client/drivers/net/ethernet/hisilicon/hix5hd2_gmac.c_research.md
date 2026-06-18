
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hix5hd2_gmac.c

## Purpose

This file implements the Hisilicon HIX5HD2/GMAC platform Ethernet driver. It supports GMAC v1/v2 variants, RGMII/MII link programming, hardware MDIO bus registration, four DMA descriptor queues, optional scatter-gather TX descriptors for TSO-capable hardware, NAPI RX/TX completion, clock/reset handling, and platform netdev registration.

## Important APIs, Types, and Functions

- `struct hix5hd2_priv` holds queue descriptors, SG descriptor ring, MMIO bases, SKB arrays, PHY/MDIO state, hardware capabilities, clocks/resets, NAPI, and timeout work.
- `hix5hd2_dev_probe()` and `hix5hd2_dev_remove()` implement platform lifecycle.
- `hix5hd2_net_open()` and `hix5hd2_net_close()` enable clocks, connect/start PHY, initialize hardware, refill RX, enable port/IRQs, and tear down active DMA.
- `hix5hd2_net_xmit()` submits TX descriptors and optional SG descriptors.
- `hix5hd2_poll()`, `hix5hd2_rx()`, and `hix5hd2_xmit_reclaim()` implement NAPI RX/TX processing.
- `hix5hd2_mdio_read()` and `hix5hd2_mdio_write()` implement the embedded MDIO bus.
- `hix5hd2_config_port()` programs RGMII/MII speed/duplex and mode-change registers.

## Control Flow

Probe allocates a netdev, maps MAC/control resources, gets and temporarily enables clocks, resets MAC/PHY, registers an MDIO bus using the device node, reads PHY mode and `phy-handle`, requests the IRQ, obtains or randomizes MAC address, installs ops/features, allocates four coherent descriptor rings and optional SG descriptors, registers NAPI and netdev, then disables clocks until open.

Open enables clocks, connects the PHY, starts PHY, initializes hardware registers and descriptor queue addresses/depths, fills RX free queue, starts queue/NAPI, enables descriptor read/write, enables port TX/RX, and enables interrupts. Interrupts disable IRQs and schedule NAPI. NAPI reclaims completed TX request descriptors, consumes RX back-queue descriptors, refills RX free queue, and reenables IRQs when below budget.

TX uses the hardware TX buffer queue write pointer as the software slot. It refuses to enqueue if `tx_skb[pos]` is still occupied, maps either a linear SKB or SG descriptor table, writes descriptor command/address, memory-barriers descriptor visibility, advances the write pointer, and updates stats/BQL. Timeout work restarts the netdev by close/open.

## State and Persistence

Persistent runtime state includes four coherent descriptor rings, optional SG descriptor ring, RX/TX SKB arrays and DMA mappings, PHY node/MDIO bus, hardware capability flags, link speed/duplex, clocks/resets, and NAPI. Hardware queue pointers and port/register state persist while clocks are enabled.

## Dependencies and Integration Points

The driver depends on platform/OF/property APIs, OF MDIO/PHY, clocks, reset controls, NAPI, DMA API, netdev BQL/stats, and PHY ethtool helpers. Compatible strings map to `GEMAC_V1` or `GEMAC_V2`, with v2 enabling SG feature exposure.

## Risks and Edge Cases

`hix5hd2_fill_sg_desc()` does not unwind already mapped fragments if a later frag map fails, so mapping-failure injection can expose leaks. `hix5hd2_free_dma_desc_rings()` unmaps TX through `tx_rq` descriptors and does not distinguish SG descriptors, which is risky for in-flight SG SKBs on close. The source has duplicated descriptor setup comments and a duplicate `hix5hd2_set_rx_fq()` call, likely harmless. MDIO read treats `MDIO_R_VALID` as an error condition, matching local naming but worth hardware validation. Queue-full handling relies on `tx_skb[pos]` occupancy.

## Test Signals

Signals include probe for all compatible strings, MDIO bus registration and PHY connection, RGMII/MII link mode changes, open/close clock sequencing, RX/TX traffic, SG-fragment TX on v2 hardware, queue-full stop/wake, TX timeout restart, MDIO timeout behavior, and DMA mapping failure tests for linear and SG paths.
