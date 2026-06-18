# sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/sni_ave.c

## Purpose
`sni_ave.c` is the full Linux netdev driver for the Socionext UniPhier AVE Ethernet MAC. It owns MAC reset/configuration, embedded descriptor memory, MDIO bus operations, NAPI RX/TX processing, PHY link adjustment, packet filtering, ethtool pause/WOL controls, suspend/resume, and SoC-specific pin-mode programming for multiple UniPhier variants. It is not an STMMAC glue layer; it implements a standalone `platform_driver` named `ave`.

## Important APIs, Types, And Functions
- Register and bit definitions cover AVE general, interrupt, MAC, descriptor-control, packet-filter, 32-bit and 64-bit descriptor memory, RMII bridge, and UniPhier syscon pinmode registers.
- `struct ave_private` is the driver state: MMIO base, IRQ, clocks/resets, PHY mode/device, MDIO bus, syscon regmap, WOL options, NAPI handles, RX/TX descriptor rings, pause settings, and `ave_soc_data`.
- `struct ave_desc_info` tracks each ring's descriptor-memory base, descriptor count, producer/consumer indices, and skb sidecar array. `struct ave_desc` stores skb and DMA mapping metadata.
- `ave_desc_read*()`, `ave_desc_write*()`, and `ave_desc_write_addr()` abstract 32-bit versus 64-bit hardware descriptor formats.
- `ave_mdiobus_read()` and `ave_mdiobus_write()` implement MDIO transactions with `readl_poll_timeout()` on `AVE_MDIOSR_STS`.
- `ave_open()`, `ave_stop()`, `ave_start_xmit()`, `ave_rx_receive()`, `ave_tx_complete()`, `ave_irq_handler()`, and NAPI poll functions form the datapath.
- `ave_pfsel_*()` and `ave_set_rx_mode()` implement unicast, broadcast, multicast, allmulti, and promiscuous filtering using AVE packet-filter entries.
- `ave_init()` and `ave_uninit()` are `ndo_init`/`ndo_uninit`; they enable clocks/resets, program syscon pinmode, reset hardware, register MDIO, attach the PHY, configure WOL defaults, and detach on cleanup.
- `ave_probe()` parses DT resources, allocates `net_device`, sets feature flags (`NETIF_F_IP_CSUM`, `NETIF_F_RXCSUM`), selects descriptor format and DMA mask, registers NAPI and the netdev, and logs hardware ID/version.
- `ave_suspend()` and `ave_resume()` preserve PHY WOL state and re-open the device when it was running.
- SoC match data (`ave_pro4_data`, `ave_pxs2_data`, `ave_ld11_data`, `ave_ld20_data`, `ave_pxs3_data`, `ave_nx1_data`) selects 32/64-bit descriptors, clocks/resets, and pinmode validation functions.

## Control Flow
Probe obtains `phy-mode`, IRQ, MMIO, optional MAC address, clocks/resets, syscon phandle, and MDIO bus, then registers the netdev. `ndo_init` enables the hardware clock/reset domain, writes pinmux bits through the syscon regmap, globally resets the MAC/PHY, registers the child `mdio` bus, and connects the PHY with `ave_phy_adjust_link()` as the callback. `ndo_open` requests the shared IRQ, allocates RX/TX sidecar arrays, initializes descriptor memory, pre-maps RX buffers, starts descriptors, initializes packet filters and MAC address registers, configures RX/TX MAC controls, enables interval IRQs, enables NAPI, starts PHY autonegotiation, and starts the queue.

TX maps the skb data into the current TX descriptor, pads short frames, sets `OWN`, first/last, length, checksum-disable, and interrupt bits, then advances `tx.proc_idx`. Completion is interrupt-driven through `AVE_GI_TX`; the TX NAPI poll calls `ave_tx_complete()`, which walks descriptors from `done_idx`, stops at hardware-owned entries, unmaps DMA, consumes skbs, updates u64 stats, and wakes the queue when buffers were freed.

RX uses pre-filled descriptors with mapped skb buffers. The RX interval interrupt schedules NAPI, which calls `ave_rx_receive()`. That path checks hardware ownership and status, unmaps the buffer, builds an skb, marks checksum as unnecessary when hardware reports a valid checksum, submits via `netif_receive_skb()`, advances indices, and refills freed RX descriptors. RX FIFO overflow calls `ave_rxfifo_reset()`, temporarily disables RX, suspends descriptors, drains packets, resets FIFO, clears status, and resumes RX.

Link changes update RGMII or RMII speed registers, duplex, and pause flow-control bits. Packet filter setup disables or enables exact-match filters for unicast/broadcast/multicast and can fall back to multicast prefix filters for IPv4/IPv6 all-multicast behavior.

## State And Persistence
Persistent state is in `ave_private`, descriptor sidecar arrays allocated during open, and hardware registers. RX/TX counters are software-maintained using `u64_stats_sync`; errors, drops, FIFO errors, and collisions are updated in IRQ/NAPI paths. `wolopts` is saved across suspend and restored during resume. MAC address persists in `ndev->dev_addr` and is rewritten to hardware on open or address change. No on-disk state exists.

## Dependencies And Integration Points
The driver integrates with platform DT (`compatible`, `phy-mode`, `mdio` child, `socionext,syscon-phy-mode`), phylib, of_mdio, syscon/regmap, clk/reset frameworks, DMA mapping, NAPI, ethtool, and PM sleep hooks. SoC-specific pinmode functions validate the requested PHY interface and syscon argument. It exposes a conventional Ethernet `net_device` and registers an MDIO bus named `uniphier-mdio`.

## Risks
- Descriptor ownership semantics differ for RX and TX and must remain correct; bad transitions can leak buffers or hand incomplete descriptors to hardware.
- `ave_start_xmit()` supports only the linear skb buffer, so scatter-gather is not enabled; enabling SG without implementation would be unsafe.
- RX descriptor preparation relies on 2-byte headroom and alignment assumptions.
- Error paths in `ave_open()` after partial RX descriptor preparation do not free already allocated descriptor sidecars in the shown failure path before IRQ cleanup; allocation failures during RX setup should be carefully tested.
- Syscon pinmode programming is SoC-specific and invalid DT arguments return probe/init errors.
- Suspend/resume assumes PHY state is available and `ave_global_reset()` can run before reopening the interface.

## Test Signals
Useful checks include DT probe for all compatible strings, MDIO child registration and PHY attach, `ip link set up/down`, RX/TX traffic including checksum offload, multicast/allmulti/promisc transitions, MTU maximum enforcement, link speed and duplex changes across RMII/RGMII, ethtool pause/WOL operations, suspend/resume with and without WOL, and induced RX FIFO overflow or TX completion stress. Kernel warning signals include descriptor stop/suspend timeouts, MDIO poll timeouts, invalid pinmode errors, and netdev stats consistency.
