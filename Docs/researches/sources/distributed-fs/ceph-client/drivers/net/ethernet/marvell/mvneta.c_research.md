# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvneta.c

## Purpose
`mvneta.c` is the Marvell NETA Ethernet MAC driver for Armada 370, Armada XP, Armada 3700, and Armada AC5 SoCs. It implements a full netdev driver with RX/TX DMA rings, per-CPU or shared interrupt handling, phylink PCS/MAC integration, optional COMPHY and hardware buffer manager support, software page-pool RX, XDP RX/TX/redirect support, ethtool statistics and controls, RSS indirection for the default RX queue, mqprio and per-queue rate limiting, power management, and platform probe/remove.

## Important APIs, Types, and Functions
- `struct mvneta_port` is the primary per-netdev state: MMIO base, queues, phylink/PCS objects, clocks, per-CPU port/stats storage, XDP program, BM pools, SoC flags, RX offset correction, multicast counters, RSS indirection, and MBUS/DRAM metadata.
- `struct mvneta_rx_queue` and `struct mvneta_tx_queue` hold descriptor rings, page pools/XDP RXQ info, buffer cookies, descriptor indices, coalescing settings, TSO header pages, TX buffer ownership types, queue thresholds, and XPS affinity.
- `struct mvneta_pcpu_port`, `struct mvneta_pcpu_stats`, and `struct mvneta_stats` support per-CPU NAPI and lockless stats aggregation through `u64_stats_sync`.
- RX helpers include `mvneta_rx_refill()`, `mvneta_rx_swbm()`, `mvneta_rx_hwbm()`, `mvneta_run_xdp()`, `mvneta_swbm_build_skb()`, `mvneta_rxq_desc_num_update()`, and `mvneta_rxq_drop_pkts()`.
- TX helpers include `mvneta_tx()`, `mvneta_tx_tso()`, `mvneta_tx_frag_process()`, `mvneta_xdp_xmit()`, `mvneta_xdp_submit_frame()`, `mvneta_tx_done_gbe()`, and `mvneta_txq_bufs_free()`.
- Link and PCS logic is exposed through `mvneta_phylink_pcs_ops` and `mvneta_phylink_ops`, including `mvneta_pcs_config()`, `mvneta_mac_prepare()`, `mvneta_mac_config()`, `mvneta_mac_finish()`, `mvneta_mac_link_down()`, and `mvneta_mac_link_up()`.
- Lifecycle entry points include `mvneta_probe()`, `mvneta_open()`, `mvneta_stop()`, `mvneta_remove()`, `mvneta_suspend()`, `mvneta_resume()`, `mvneta_driver_init()`, and `mvneta_driver_exit()`.
- User-facing controls are in `mvneta_netdev_ops` and `mvneta_eth_tool_ops`, covering MTU, MAC address, features, ioctl, XDP, TC mqprio, link settings, coalescing, rings, pause, WoL, EEE, RSS, and stats.

## Control Flow
Driver initialization registers two CPU hotplug multi-states, then registers the platform driver. Probe allocates a multiqueue netdev sized by module parameters, reads `phy-mode`, obtains optional COMPHY, maps MMIO, detects Armada 3700/AC5 quirks, maps IRQ, enables core and bus clocks, configures phylink capabilities and EEE defaults, creates phylink, allocates per-CPU port and stats storage, chooses a MAC address from DT, hardware, or random generation, derives TX checksum limits, programs MBUS windows, optionally attaches to a buffer-manager node and pools, initializes default hardware/queue structures, validates/powers up the port, installs NAPI instances, sets feature flags and MTU range, registers the netdev, and stores drvdata.

Open computes packet size, allocates and initializes RX and TX queues, requests either a normal IRQ for Armada 3700/AC5 or a percpu IRQ for other SoCs, enables per-CPU IRQs and CPU hotplug instances when applicable, connects phylink to the PHY, then starts the device. Start configures the current interface/COMPHY, programs max RX/TX packet sizes, enables the MAC, enables NAPI, unmasks interrupts on each CPU, enables link-change causes, starts and speeds up phylink, starts TX queues, and clears `__MVNETA_DOWN`.

Interrupt handling differs by SoC. Armada 3700 masks `MVNETA_INTR_NEW_MASK` and schedules a single NAPI instance. Other SoCs use percpu IRQs, disable the current CPU's percpu IRQ, and schedule that CPU's NAPI. The poll routine reads RX/TX/misc causes, reports link changes to phylink, reclaims completed TX queues, merges leftover cause bits from the previous poll, services one RX queue selected from cause bits, completes NAPI when under budget, and unmasks either the shared interrupt or percpu IRQ. RX with software buffer management uses page_pool pages, supports multi-descriptor packets/frags, runs XDP before SKB construction, handles XDP redirect/TX/drop/pass, updates descriptor counters in batches, and refills up to 64 descriptors per pass. RX with hardware BM consumes pool buffers, copybreaks small frames, refills BM pools, builds SKBs from larger buffers, and returns buffers to pools on drops.

TX maps the linear SKB head, optional fragments, or software TSO-generated headers/data into descriptors. It records ownership type in `struct mvneta_tx_buf`, batches hardware doorbells with `netdev_xmit_more()` and `txq->pending`, applies queue stop thresholds, timestamps SKBs, and updates per-CPU stats. XDP TX and ndo_xdp_xmit share descriptor submission logic but differ in DMA mapping ownership. TX completion reads sent-descriptor counters, decrements hardware accounting, unmaps/free SKBs or XDP frames in bulk, resets netdev TX queue accounting, and wakes queues below threshold.

Stop marks the device down, stops phylink, disables NAPI and CPU hotplug hooks, masks interrupts, stops RX/TX DMA with timeout loops, disables the MAC, clears interrupt causes, resets TX/RX DMA, disconnects PHY, frees IRQs, and releases queues. MTU, ring, RSS, and XDP program changes stop/reinitialize relevant runtime resources when necessary. Suspend detaches the device, stops the live datapath, drops RX packets, deinitializes TX hardware queues, and disables clocks; resume reenables clocks, restores MBUS/BM/default hardware state, reinitializes queue hardware if running, reinstalls CPU hotplug hooks, restarts the device, and restores RX filters.

## State and Persistence Behavior
All software state is runtime state tied to the platform device or open netdev. Hardware configuration is held in NETA MMIO registers for descriptor bases, queue sizes, CPU queue maps, MAC/PCS/autoneg, filters, coalescing, MBUS windows, BM windows, rate limiting, VLAN priority mapping, LPI/EEE, and interrupt masks. Per-CPU packet counters and software ethtool counters accumulate in memory; hardware MIB counters are read and accumulated into `pp->ethtool_stats`. Page-pool state and RX buffers exist while queues are initialized. XDP program state is a live `bpf_prog` pointer replaced by `xchg()`. BM pool ownership is tracked in BM pool port maps and released on remove or BM fallback. There is no disk persistence.

## Dependencies and Integration Points
The driver depends on the netdev core, NAPI, phylink, phylib MDIO attachment, platform/OF APIs, clock APIs, IRQ/percpu IRQ APIs, CPU hotplug, COMPHY generic PHY APIs, mvebu MBUS helpers, Marvell NETA BM helpers from `mvneta_bm.h`, page_pool, XDP/BPF helpers, Linux TSO helpers, TC mqprio offload APIs, ethtool, DMA mapping, and PM sleep hooks. It consumes Device Tree properties such as compatible strings, `phy-mode`, MAC address, IRQ, clocks, optional `buffer-manager`, `bm,pool-long`, `bm,pool-short`, and `tx-csum-limit`. It integrates with `mvmdio.c` indirectly through phylink PHY connection.

## Risks and Edge Cases
- `rxq_number`, `txq_number`, and `rxq_def` are module parameters used broadly for allocation, CPU maps, queues, and bit masks; invalid combinations can stress assumptions even though hardware only supports eight queues.
- Per-CPU interrupt routing and CPU hotplug election are complex and intentionally bypassed on Armada 3700 because its per-CPU interrupt path is broken.
- Software BM and hardware BM have very different buffer ownership rules; XDP is rejected with hardware BM, and MTU updates can fall back from BM to software BM on pool refill failure.
- Multi-fragment RX and XDP require careful page_pool lifetime handling; incomplete descriptor chains or missing LAST descriptors are dropped and must return all pages.
- TX descriptor rollback paths for TSO/fragments and XDP DMA mapping failures must keep `next_desc_to_proc`, put indices, DMA mappings, and buffer ownership consistent.
- `mvneta_txq_sw_init()` can allocate descriptors then fail allocating `buf` or TSO headers; cleanup paths must free partially allocated resources.
- Link mode changes force link down around interface/in-band changes; COMPHY power transitions and PCS register programming are sensitive to phylink mode.
- Suspend/resume rebuilds hardware state while preserving software queue allocations; BM reinitialization failure on resume can switch the port to software BM.
- RSS indirection table size is one entry, so ethtool RSS controls only the default RX queue rather than full hash distribution.
- Rate limiting accepts only max rates that are exact multiples of the hardware resolution and rejects min-rate requests.

## Test Signals
- Build and boot tests for Armada 370, Armada XP, Armada 3700, and AC5 compatibles, with and without COMPHY, BM, PM sleep, XDP, page_pool stats, and TC mqprio.
- Probe/remove tests should inject failures in IRQ mapping, clock enable, phylink create, per-CPU allocation, BM pool setup, netdev registration, and queue allocation.
- Datapath tests should cover software BM RX, hardware BM RX, small-frame copybreak, jumbo/multi-descriptor RX, checksum offloads for IPv4/IPv6, TSO, fragmented SKBs, XDP PASS/DROP/TX/REDIRECT/ndo_xmit, and TX completion batching.
- Link tests should cover RGMII, SGMII, QSGMII, 1000BASE-X, 2500BASE-X, in-band and fixed/PHY modes, EEE LPI timer limits, pause negotiation, WoL, and COMPHY mode switching.
- Control tests should exercise MTU changes with and without XDP frags, ringparam changes, coalescing updates, RSS default queue change, MAC filter/promiscuous/allmulti updates, mqprio VLAN priority mapping, and per-queue rate limiting.
- PM and CPU hotplug tests should suspend/resume while running, offline/online elected CPUs under traffic, and verify interrupts/NAPI/queues recover without lost carrier or stuck queues.
