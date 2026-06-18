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
