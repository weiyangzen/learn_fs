# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/ravb_main.c

## Purpose
This is the primary platform and netdev implementation for the Renesas Ethernet AVB/GbEth driver. It probes device-tree AVB-compatible devices, selects the correct hardware variant table, initializes clocks/reset/MMIO/MDIO/descriptors, manages BE and optional NC queues, drives Tx/Rx through DMA descriptors and NAPI, handles PHY link changes, PTP timestamp routing, ethtool operations, wake-on-LAN, runtime/system PM, and removal.

## Important APIs, Types, And Functions
- Platform/module surface: `ravb_match_table`, `ravb_driver`, `ravb_probe()`, `ravb_remove()`, `ravb_suspend()`, `ravb_resume()`, `ravb_runtime_suspend()`, and `ravb_runtime_resume()`.
- Netdev surface: `ravb_netdev_ops` wires open/stop, transmit, queue select, stats, rx mode, timeout, PHY ioctl, MTU, MAC validation, feature changes, and hwtstamp get/set.
- Hardware variant tables: `ravb_gen2_hw_info`, `ravb_gen3_hw_info`, `ravb_gen4_hw_info`, `ravb_rzv2m_hw_info`, and `gbeth_hw_info` select descriptor sizes, queue counts, checksum support, interrupt layout, gPTP mode, frame limits, WoL, and init callbacks.
- Ring/data path: `ravb_ring_init()`, `ravb_ring_format()`, `ravb_ring_free()`, `ravb_rx_ring_refill()`, `ravb_rx_rcar()`, `ravb_rx_gbeth()`, `ravb_tx_free()`, and `ravb_start_xmit()`.
- Hardware init/stop: `ravb_set_opmode()`, `ravb_set_config_mode()`, `ravb_dmac_init()`, `ravb_dmac_init_rcar()`, `ravb_dmac_init_gbeth()`, `ravb_emac_init_*()`, `ravb_stop_dma()`, `ravb_set_gti()`, and `ravb_compute_gti()`.
- Interrupt/NAPI: `ravb_interrupt()`, `ravb_multi_interrupt()`, `ravb_emac_interrupt()`, `ravb_be_interrupt()`, `ravb_nc_interrupt()`, `ravb_queue_interrupt()`, `ravb_timestamp_interrupt()`, `ravb_error_interrupt()`, and `ravb_poll()`.
- PHY/MDIO/ethtool: `ravb_mdio_init()`, `ravb_phy_init()`, `ravb_adjust_link()`, `ravb_get_ethtool_stats()`, `ravb_set_ringparam()`, `ravb_get_ts_info()`, and WoL helpers.

## Control Flow
Probe requires a device-tree node, obtains reset control and match data, allocates a multiqueue netdev sized for BE-only or BE+NC operation, deasserts reset, requests IRQs according to the selected interrupt topology, gets clocks, enables runtime PM, maps MMIO, parses PHY mode and link properties, computes maximum MTU and descriptor count, computes the gPTP increment when needed, parses internal-delay DT properties, allocates the descriptor base address table, switches hardware to config mode, reads or randomizes the MAC address, registers the MDIO bus, returns hardware to reset mode, adds NAPI contexts, optionally enables software IRQ coalescing for GbEth, registers the netdev, and marks wakeup capable.

Open enables NAPI, resumes runtime PM, enters config mode, applies internal delays, writes the descriptor base table DMA address, initializes DMAC rings, initializes EMAC registers, programs GTI, registers PTP when supported, connects and starts the PHY, and starts all Tx queues. Close stops Tx, masks interrupts, stops/disconnects PHY, unregisters PTP, stops DMA into config mode, drains pending Tx timestamp skbs, cancels timeout work, disables NAPI, frees BE/NC rings and page pools, updates stats, switches to reset mode, and drops runtime PM usage.

Receive processing is variant-specific. R-Car uses extended Rx descriptors with hardware timestamps and a two-queue model; GbEth uses normal descriptors and can assemble multi-descriptor packets into a page-backed skb. Both paths check descriptor ownership/type before reading fields, account MAC errors, sync DMA buffers for CPU, build or extend skbs from page-pool pages, apply checksum status if enabled, feed GRO, mark consumed page slots NULL, and refill descriptors with `DT_FEMPTY`. Transmit maps one or two descriptors per packet depending on alignment requirements, optionally sets a Tx timestamp tag for NC queue packets, uses DMA barriers before descriptor type changes and doorbell writes, advances `cur_tx`, frees completed descriptors, and stops a subqueue if the ring remains full.

Interrupt handling supports both shared summary IRQs and multi-IRQ devices. Summary handlers read `ISS`, dispatch timestamp FIFO processing, queue RX/TX scheduling, E-MAC link/magic-packet events, error accounting, and gPTP interrupts under `priv->lock`. Per-queue handlers schedule only their queue. NAPI clears RX/TX status, receives packets, retires Tx descriptors, wakes subqueues, mirrors overrun/fifo stats, and unmasks interrupts after completion.

## State And Persistence
Runtime state is held in `struct ravb_private`, DMA rings, page pools, descriptor base table, per-queue `net_device_stats`, pending timestamp skb list, PHY state, MDIO bus, clocks, reset control, and hardware registers. Persistent platform configuration comes from device tree properties such as compatible string, MAC address, PHY mode, `renesas,no-ether-link`, link polarity, internal delay properties, MDIO child node, and PHY handle. No runtime settings are stored to disk; ethtool ring size, timestamp mode, WoL flag, and feature flags are in-memory netdev state.

## Dependencies And Integration Points
The driver depends on Linux platform device, OF/MDIO/PHY, PM runtime, reset controller, clocks, DMA mapping, page pool, NAPI, ethtool, hwtstamp, PTP, netdev queueing, and `ravb_ptp.c`. Device-tree compatible entries map hardware generations to the `ravb_hw_info` table. It integrates with phylib for link negotiation, MDIO bitbang for bus access, ethtool for stats/ring/ts/WoL controls, PTP for timestamping, and kernel PM for autosuspend and system suspend/resume.

## Risks And Edge Cases
- `ravb_start_xmit()` calls `skb_checksum_help()` but does not check its return value before continuing, which is worth scrutiny if software checksum completion can fail.
- Descriptor programming relies on strict `dma_wmb()` ordering, especially two-descriptor aligned Tx; reordering can leave DMA seeing a start descriptor without an end descriptor.
- `ravb_stop_dma()` may fail; timeout and close paths intentionally avoid some reinitialization when hardware is still operating.
- `ravb_set_ringparam()` stops and frees rings on a running device; failure during reinit can leave the interface detached or partially stopped.
- PTP init/stop conditions vary between `gptp` and `ccc_gac`; timeout work checks only `info->gptp`, unlike open/close, so Gen3/Gen4 `ccc_gac` behavior deserves regression coverage.
- Runtime PM guards interrupt handlers and stats/feature operations; missed get/put ordering could produce MMIO while clocks are off.
- `ravb_remove()` returns early if runtime resume fails, which can leave device-managed teardown incomplete.

## Test Signals
Test probe on each compatible family, MDIO registration and PHY/fixed-link connection, BE-only GbEth and BE+NC R-Car traffic, Rx/Tx checksum toggles, hardware timestamp Tx on NC queue and Rx filters, PTP clock registration and interrupts, ethtool ring resize while running, MTU changes, WoL suspend/resume, runtime autosuspend clock gating, multi-IRQ and shared-IRQ paths, Tx timeout recovery, descriptor empty/fifo error accounting, and unload after active traffic with no DMA/page-pool leaks.
