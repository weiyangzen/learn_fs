# subset-b-004504 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mv643xx_eth.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mv643xx_eth.c

## Purpose
`mv643xx_eth.c` is the legacy Marvell Discovery/MV643XX/Orion Ethernet MAC driver. It manages the shared controller register block, per-port platform devices, per-port netdevs, RX/TX DMA rings, NAPI interrupt handling, PHY attachment through phylib, ethtool controls, multicast/unicast filtering, interrupt coalescing, optional descriptor SRAM, and platform/Device Tree glue for Orion and Kirkwood systems. The companion `orion-mdio` bus from `mvmdio.c` supplies PHY access for the scan and `phy_connect()` paths.

## Important APIs, Types, and Functions
- `struct mv643xx_eth_shared_private` stores the shared MMIO base, MBUS window protection, clock, checksum limit, coalescing capabilities, and TX bandwidth register layout discovered by `infer_hw_params()`.
- `struct mv643xx_eth_private` is the per-port netdev state: port MMIO base, timers, NAPI instance, interrupt work bits, RX/TX ring sizes, SRAM descriptor ranges, queue arrays, PHY/netdev pointers, clock rate, and timeout work.
- `struct rx_queue` and `struct tx_queue` track circular descriptor rings, DMA addresses, software indices, queued SKBs, DMA mapping types, TSO header memory, and TX accounting.
- Datapath functions include `rxq_process()`, `rxq_refill()`, `skb_tx_csum()`, `txq_submit_skb()`, `txq_submit_tso()`, `txq_submit_frag_skb()`, `mv643xx_eth_xmit()`, `txq_reclaim()`, and `txq_kick()`.
- Interrupt and NAPI flow is implemented by `mv643xx_eth_collect_events()`, `mv643xx_eth_irq()`, `mv643xx_eth_poll()`, and `oom_timer_wrapper()`.
- Link and PHY logic is handled by `mv643xx_eth_adjust_link()`, `phy_scan()`, `phy_init()`, `init_pscr()`, `port_start()`, and `port_reset()`.
- Netdev/ethtool entry points are `mv643xx_eth_open()`, `mv643xx_eth_stop()`, `mv643xx_eth_change_mtu()`, `mv643xx_eth_ioctl()`, `mv643xx_eth_set_features()`, ring/coalesce/stat/WoL/link-ksettings ethtool helpers, and `mv643xx_eth_netdev_ops`.
- Platform glue is split between shared-device setup (`mv643xx_eth_shared_probe()`, `mv643xx_eth_conf_mbus_windows()`, `mv643xx_eth_shared_of_probe()`) and per-port setup (`mv643xx_eth_probe()`, `mv643xx_eth_remove()`, `mv643xx_eth_shutdown()`).

## Control Flow
Module initialization registers two platform drivers: one for the shared controller and one for each Ethernet port. The shared probe maps the controller, enables the optional shared clock, programs MBUS decode windows from `mv_mbus_dram_info()`, creates child port devices from Device Tree if present, reads platform checksum settings, and probes hardware layout bits for RX coalescing and TX bandwidth controls. The port probe allocates an 8-queue-capable netdev, derives the per-port register base at `shared->base + 0x0400 + port_number << 10`, configures Kirkwood RGMII/GMII quirks, establishes the port clock rate, copies platform queue/SRAM/MAC parameters, connects a PHY by DT phandle or by scanning the `orion-mdio-mii` bus, initializes the serial control register, installs NAPI/timers/work, sets feature flags and MTU limits, programs default SDMA and coalescing registers, and registers the netdev.

Opening the netdev clears pending interrupt causes, requests the shared IRQ, recalculates RX SKB size, enables NAPI, initializes and fills all RX rings, initializes all TX rings and TSO header buffers, starts the MIB timer, calls `port_start()`, and unmasks link/RX/TX interrupts. `port_start()` resets and starts the PHY when present, enables the serial port, configures TX rates and queue priorities, applies RX checksum feature state, programs address filters, writes RX current descriptor pointers, and enables RX queues.

The RX path refills descriptors with `netdev_alloc_skb()`, DMA-maps the data area, sets `BUFFER_OWNED_BY_DMA`, and reserves the two dummy hardware header bytes. NAPI polls descriptors until either budget is exhausted or a DMA-owned descriptor is reached, unmaps each buffer, updates netdev stats, validates first/last/error bits, trims dummy bytes and FCS, sets checksum state when `LAYER_4_CHECKSUM_OK` is present, and passes packets to GRO. Allocation failure sets `mp->oom`; a short timer reschedules NAPI for later refilling.

The TX path selects the queue from `skb_get_queue_mapping()`, linearizes small unaligned fragments if required by hardware, then builds either normal descriptors or software TSO descriptors. The first descriptor command/status write is deferred until all related descriptors are populated, with memory barriers before handing ownership to hardware and before queue kick. Completion interrupts or extended TX events drive `txq_reclaim()`, which unmaps DMA buffers according to stored mapping type, skips TSO header DMA areas, frees SKBs on interrupt-marked descriptors, accounts TX errors, and wakes stopped netdev queues.

Stop and teardown paths mask interrupts, disable NAPI, stop PHY/carrier, free IRQs, reset the port, snapshot stats, delete timers, deinitialize rings, disconnect PHYs, cancel timeout work, disable clocks, and free the netdev. MTU and ring-size changes stop and reopen the interface if it is running.

## State and Persistence Behavior
Driver state is runtime-only. The hardware keeps live configuration in MMIO registers for MBUS windows, SDMA, serial control, MAC address filters, coalescing, queue pointers, PHY address, and bandwidth shaping; the driver rebuilds these from platform/DT data and netdev settings at probe/open. MIB counters are read-and-accumulate: hardware counters are cleared by dummy reads, and software accumulates values in `struct mib_counters` under `mib_counters_lock`. RX/TX descriptors, SKB arrays, TSO headers, and optional SRAM mappings exist only while the interface is open. There is no filesystem persistence.

## Dependencies and Integration Points
The driver integrates with Linux platform devices, Device Tree helpers, `mv_mbus_dram_info()`, phylib, `orion-mdio` PHY naming, netdev core, NAPI, ethtool, DMA mapping APIs, timers, workqueues, optional netpoll, Linux TSO helpers, and Marvell platform data from `<linux/mv643xx_eth.h>`. Device Tree child-port parsing consumes `reg`, IRQ, MAC address, `phy-handle`, `speed`, `duplex`, `phy-mode`, queue-size, and SRAM properties. Shared-controller and per-port platform devices are coupled by `mv643xx_eth_platform_data->shared`.

## Risks and Edge Cases
- The driver uses 32-bit descriptor DMA pointer fields, so the coherent DMA mask and platform DMA addressing must keep rings and buffers reachable by this MAC.
- RX OOM recovery depends on a timer and NAPI reschedule; sustained allocation failure can keep RX queues underfilled.
- `txq_submit_tso()` has an error path that notes data descriptors may not all be released, making DMA mapping failure during TSO a high-value fault-injection case.
- Queue disable and port reset loops poll hardware without broad timeout protection in some paths, so stuck hardware can hang teardown.
- Ring-size and MTU changes stop and reopen the device; reopen failure after changing in-memory settings leaves the interface down and logs a fatal error.
- Multicast filtering collapses to promiscuous/all-multicast behavior on allocation failure or unsupported unicast filter combinations.
- PHY scan depends on a specific `orion-mdio-mii` bus id and may defer probe when the MDIO bus is not registered yet.
- Optional descriptor SRAM is used only for queue zero when the requested ring fits; mixed SRAM/coherent allocation paths need separate cleanup coverage.

## Test Signals
- Build coverage for OF and non-OF platform-data configurations, big-endian and little-endian descriptor layouts, netpoll, and phylib support.
- Probe/remove tests should cover shared-device creation, DT child-port creation failure, missing IRQ/reg/phy properties, deferred PHY/clock probing, and Kirkwood interface mode quirks.
- Runtime tests should exercise open/stop, IRQ/NAPI RX and TX, OOM RX refill recovery, TX timeout recovery, MTU changes, ethtool ring changes, coalescing changes, checksum toggles, and WoL passthrough.
- Packet tests should include checksum-offloaded IPv4 TCP/UDP, VLAN-tagged checksum cases, TSO, fragmented SKBs, tiny unaligned fragments, multicast filter programming, promiscuous/allmulti modes, and link up/down events.
- Fault injection should target DMA allocation/mapping failures, TSO descriptor construction, IRQ request failure, ring allocation failure, and PHY connection failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mv643xx_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvmdio.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvmdio.c

## Purpose
`mvmdio.c` implements the shared Marvell Orion/NETA MDIO controller driver. It registers a Linux `mii_bus` for classic clause 22 SMI or clause 45 XSMI accesses, serializes PHY register reads and writes through the mdiobus core, optionally waits for completion through the controller error/completion interrupt, manages controller clocks, and supports both Device Tree and ACPI firmware descriptions. The file is explicitly used by Marvell Ethernet MAC drivers such as `mvneta` and `mv643xx_eth`.

## Important APIs, Types, and Functions
- `struct orion_mdio_dev` holds mapped registers, up to four clocks, optional completion IRQ, and the wait queue used when interrupt-driven completion is available.
- `enum orion_mdio_bus_type` selects classic `BUS_TYPE_SMI` or extended `BUS_TYPE_XSMI`.
- `struct orion_mdio_ops` abstracts the bus-type-specific busy/done test used by `orion_mdio_wait_ready()`.
- Clause 22 accessors are `orion_mdio_smi_read()` and `orion_mdio_smi_write()`, with completion status from `orion_mdio_smi_is_done()`.
- Clause 45 accessors are `orion_mdio_xsmi_read_c45()` and `orion_mdio_xsmi_write_c45()`, with completion status from `orion_mdio_xsmi_is_done()`.
- `orion_mdio_xsmi_set_mdc_freq()` reads the optional `clock-frequency` property and `mg_core_clk` to program XSMI MDC clock division.
- `orion_mdio_err_irq()` handles `MVMDIO_ERR_INT_SMI_DONE`, clears the interrupt cause, and wakes waiters.
- `orion_mdio_probe()` allocates and registers the mdiobus; `orion_mdio_remove()` unregisters it and disables clocks.

## Control Flow
Probe reads the firmware match data to determine SMI versus XSMI, obtains the first memory resource, allocates a devm `mii_bus` with private `orion_mdio_dev` storage, installs either clause 22 or clause 45 callbacks, maps the controller registers, and initializes the wait queue. For OF devices it acquires up to four indexed clocks, handles `-EPROBE_DEFER`, warns if more clocks exist than the static array supports, and configures XSMI MDC frequency when requested. For non-OF devices it gets one optional unnamed clock.

The optional IRQ path calls `platform_get_irq_optional()`. If the IRQ exists but the MMIO resource is too small to cover the interrupt mask register, the driver disables IRQ use and falls back to polling. Otherwise it requests a shared IRQ and enables the SMI-done interrupt mask. Finally, ACPI-described devices register through `acpi_mdiobus_register()`, while other devices register through `of_mdiobus_register()`.

Each read or write first calls `orion_mdio_wait_ready()` to ensure the controller is idle. With no completion IRQ, that helper uses `read_poll_timeout_atomic()` with a 2 microsecond poll interval and a 1 millisecond timeout. With an IRQ, it waits on `smi_busy_wait` for at least two jiffies. SMI reads then write the PHY address, register number, and read command, wait again, verify `MVMDIO_SMI_READ_VALID`, and return the low 16 bits. SMI writes post address/register/data with the write operation bit pattern. XSMI reads additionally write the clause 45 register address to `MVMDIO_XSMI_ADDR_REG`, issue the management read command with PHY and device address, wait, verify read-valid, and return 16 bits. XSMI writes similarly program address and management write data.

Remove disables the interrupt mask if used, unregisters the mdiobus, disables/unprepares clocks, and drops clock references.

## State and Persistence Behavior
The driver owns only runtime state: mapped MMIO, clock handles, wait queue, and mdiobus registration. MDIO transaction state lives in hardware busy/read-valid bits and is not persisted. Clock-frequency programming changes the live XSMI configuration register but is reconstructed on probe. There is no disk persistence or long-lived software cache of PHY register values.

## Dependencies and Integration Points
This file depends on platform devices, firmware match data, OF and ACPI MDIO registration helpers, phylib mdiobus callbacks, Linux clock APIs, interrupt APIs, wait queues, MMIO accessors, and polling helpers. OF compatibles are `marvell,orion-mdio` for SMI and `marvell,xmdio` for XSMI; ACPI IDs are `MRVL0100` and `MRVL0101`. MAC drivers consume the registered bus through phylib/phylink and PHY nodes rather than calling this file directly.

## Risks and Edge Cases
- The code manually unwinds clocks acquired with `of_clk_get()` and `clk_get_optional()`; deferred probes and partial clock arrays need cleanup coverage.
- `orion_mdio_wait_ready()` uses atomic polling when no IRQ is present, so long hardware stalls become timeout errors and can delay PHY operations.
- XSMI MDC frequency setup only works with OF and `mg_core_clk`; missing or failed clock lookup logs an error and leaves the default divider.
- If the interrupt resource exists but the MMIO resource is too short for the interrupt registers, interrupt completion is silently disabled after an error message.
- Read-valid failure returns `-ENODEV`, which can be interpreted by PHY discovery as an absent device.
- The interrupt handler writes the bitwise complement of the done bit to the cause register, matching this controller's clear semantics; wrong semantics on a variant would be destructive.

## Test Signals
- Probe tests should cover SMI and XSMI compatibles, ACPI IDs, no IRQ polling mode, IRQ completion mode, short MMIO resources, missing memory resource, and clock defer/unwind.
- MDIO transaction tests should cover valid reads/writes, busy timeout, read-valid failure, clause 45 device/register addressing, and concurrent PHY accesses through mdiobus locking.
- Device Tree tests should include multiple clocks, more than four clocks, `clock-frequency`, missing `mg_core_clk`, and child PHY discovery.
- Integration tests with `mvneta` and `mv643xx_eth` should verify PHY attach, link negotiation, WoL propagation, and remove ordering where MACs detach before the MDIO bus disappears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvmdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvneta.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvneta.c -->
