# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_main.c

## Purpose

`mvpp2_main.c` is the main Linux network driver implementation for Marvell PPv2 Ethernet controllers, covering PPv2.1, PPv2.2, and PPv2.3 variants. It binds as a `platform_driver`, discovers OF/ACPI-described ports, maps controller resources, initializes global packet-processor hardware, creates one `net_device` per enabled port, and implements the runtime datapath for RX, TX, XDP, hardware timestamping, RSS/flow steering, VLAN filtering, ethtool controls, interrupt/NAPI handling, phylink MAC/PCS operations, and teardown.

The file is hardware-facing: most behavior is expressed as register programming through `mvpp2_write()`, `mvpp2_read()`, per-thread MMIO windows, syscon regmap access, DMA-coherent descriptor rings, and buffer-manager pools. It depends on local parser/classifier/TAI/debugfs modules for TCAM/parser rules, flow steering/RSS, PTP clock conversion, and diagnostics.

## Important APIs, Types, and Functions

- Driver entry points: `mvpp2_probe()`, `mvpp2_remove()`, `mvpp2_driver_init()`, and `mvpp2_driver_exit()` register and unregister the platform driver for OF compatibles `marvell,armada-375-pp2`, `marvell,armada-7k-pp22`, and ACPI ID `MRVL0110`.
- Netdev operations: `mvpp2_open()`, `mvpp2_stop()`, `mvpp2_tx()`, `mvpp2_set_rx_mode()`, `mvpp2_set_mac_address()`, `mvpp2_change_mtu()`, `mvpp2_get_stats64()`, `mvpp2_ioctl()`, VLAN filter callbacks, `mvpp2_set_features()`, `mvpp2_xdp()`, `mvpp2_xdp_xmit()`, and hardware timestamp get/set callbacks are exported through `mvpp2_netdev_ops`.
- Ethtool operations: coalescing, ring sizing, link settings, pause, timestamp info, hardware stats, RSS indirection/context management, ntuple classifier rules, and EEE are exposed through `mvpp2_eth_tool_ops`.
- Phylink and PCS operations: `mvpp2_phylink_ops`, `mvpp2_phylink_gmac_pcs_ops`, and `mvpp2_phylink_xlg_pcs_ops` integrate GMAC/XLG mode selection, PCS state, in-band negotiation, forced link states, flow control, and LPI/EEE.
- Core shared state, declared in `mvpp2.h`, is `struct mvpp2`: MMIO bases, per-thread software windows, clocks, enabled port list/map, TAI handle, TX aggregate queues, BM pools, parser shadows, RSS tables, page pools, flow-control flags, and shared locks.
- Per-port state is `struct mvpp2_port`: port IDs, register bases, queue arrays, netdev, XDP program, per-CPU stats/timers, rings, phylink/PCS/COMPHY, BM pool choices, queue vectors, RSS/flow rules, timestamp queues, and TX flow-control state.
- Queue and buffer types include `struct mvpp2_rx_queue`, `struct mvpp2_tx_queue`, `struct mvpp2_txq_pcpu`, `struct mvpp2_bm_pool`, hardware descriptor unions `struct mvpp2_rx_desc`/`struct mvpp2_tx_desc`, and `struct mvpp2_queue_vector`.
- Low-level helpers abstract hardware-version descriptor layouts and register windows: `mvpp2_txdesc_*()`, `mvpp2_rxdesc_*()`, `mvpp2_thread_*()`, `mvpp2_cpu_to_thread()`, `mvpp2_bm_pool_put()`, and RX/TX descriptor ring index helpers.

## Control Flow

Probe begins in `mvpp2_probe()`. It allocates `struct mvpp2`, determines the matched hardware generation, maps common and generation-specific MMIO regions, optionally maps CM3 SRAM for firmware flow control, finds syscon registers, chooses per-CPU BM pools when possible, establishes software-thread windows, enables clocks or reads ACPI clock frequency, configures DMA masks, builds the active port bitmap from child firmware nodes, detects PPv2.3 via `MVPP2_VER_ID_REG`, initializes locks, and calls `mvpp2_init()`.

`mvpp2_init()` configures MBUS/AXI access, disables hardware PHY polling, allocates aggregate TX queues per thread, initializes RX/TX FIFO sizing, enables TX snooping, initializes BM pools, initializes parser defaults via `mvpp2_prs_default_init()`, and initializes classifier defaults via `mvpp2_cls_init()`. After that, `mvpp2_probe()` probes the TAI/PTP block, calls `mvpp2_port_probe()` for each child port, creates a single-thread stats workqueue, enables global firmware flow control when available, initializes debugfs, and stores driver data.

`mvpp2_port_probe()` allocates a multi-queue Ethernet device, parses port ID, GOP ID, PHY interface, optional COMPHY, IRQ layout, loopback flag, and MAC address source. It initializes queue vectors, stats storage, ring defaults, per-port hardware, BM pool assignment, per-CPU TX completion timers when TX IRQs are absent, feature flags, XDP capabilities, MTU bounds, phylink/PCS if not in old ACPI compatibility mode, then registers the netdev.

Opening a port runs `mvpp2_open()`: parser rules are programmed for broadcast, local MAC, Marvell header tags, and default flow; RX and TX rings are allocated and programmed; IRQs are requested; phylink or link/PTP IRQ setup is performed; interrupts are unmasked across CPUs; `mvpp2_start_dev()` enables NAPI, interrupts, MAC/GOP mode, phylink/ACPI link startup, and TX queues; periodic hardware-stat collection is scheduled.

The RX path starts at `mvpp2_isr()`, which disables the queue vector interrupt and schedules NAPI. `mvpp2_poll()` reads per-thread cause registers, handles misc errors and TX completions, then dispatches RX queue bits to `mvpp2_rx()`. `mvpp2_rx()` consumes descriptors, syncs DMA, rejects buffer-header/error descriptors, optionally runs an XDP program, refills BM pools, builds an SKB from the received buffer, applies RX timestamp and checksum state, submits GRO, updates per-CPU stats, flushes XDP redirects, and finally updates hardware RX queue counters.

The TX path enters through `mvpp2_tx()`. It chooses the queue from SKB mapping and current software thread, optionally serializes when a hardware thread is shared by multiple CPUs, reserves aggregate and physical TX descriptors, handles GSO through `mvpp2_tx_tso()`, otherwise maps the linear head and fragments, sets checksum and PTP descriptor fields, tracks DMA/SKB ownership in per-CPU queue buffers, updates descriptor counters, kicks the aggregate TXQ, stops the netdev subqueue at high watermark, updates stats, and either relies on TX IRQs or uses an hrtimer to poll completions. Completion flows through `mvpp2_tx_done()` and `mvpp2_txq_done()`, which read-and-clear hardware sent counters, unmap DMA, free SKBs or XDP frames, and wake stopped queues.

Stopping a port runs `mvpp2_stop()`: `mvpp2_stop_dev()` marks the port down, masks interrupts, disables NAPI, stops phylink, powers off COMPHY, then the caller masks per-thread causes, disconnects PHY, frees link/queue IRQs, cancels hrtimers, cleans RX/TX queues, cancels stats work, and asserts MAC/PCS reset.

## State and Persistence Behavior

The driver has no disk persistence. Durable state lives in hardware registers, DMA rings, BM pools, firmware SRAM, local kernel allocations, and netdev/phylink state while the module is loaded.

Global controller state includes MMIO mappings, clocks, port list/map, hardware generation, software-thread count, shared locks, aggregate TX queues, BM pool descriptors, optional page pools, parser shadow tables, RSS tables, TAI/PTP state, and a stats workqueue. Per-port state includes ring sizes, RX/TX queues, queue vectors, current MTU-derived packet size, pool choices, stats, phylink/PCS state, COMPHY power state, XDP program pointer, timestamp configuration, and flow steering rules.

BM pools are central. Shared-pool mode uses logical short/long/jumbo pools; per-CPU mode creates short and long page pools per RX queue. MTU changes can force a global stop/rebuild/switch between per-CPU and shared buffers: jumbo MTUs cannot use per-CPU pools, while all-low-MTU configurations switch back to per-CPU pools. XDP requires per-CPU pools and enough TX queues for per-CPU XDP_TX.

Statistics are split between software per-CPU counters and hardware MIB/counter registers. Hardware counters are periodically folded into 64-bit `port->ethtool_stats` because several registers are 32-bit and can overflow quickly. `mvpp2_get_stats64()` aggregates per-CPU software counters using `u64_stats_sync`.

Firmware flow-control state is written through CM3 SRAM registers under `mss_spinlock`. Per-port TX pause, RXQ thresholds, BM pool thresholds, and PPv2.3 RX FIFO flow-control enables are coordinated with firmware update-command bits.

## Dependencies and Integration Points

- Linux netdev core: `alloc_etherdev_mqs()`, `register_netdev()`, `net_device_ops`, NAPI, XPS, carrier and TX queue control, GRO, VLAN filtering, rtnl stats, and ethtool.
- DMA and memory management: coherent descriptor allocation, streaming DMA map/sync/unmap, `page_pool`, SKB fragment allocation, per-CPU allocations, and XDP memory model registration.
- XDP/BPF: `bpf_prog_run_xdp()`, XDP redirect/flush, XDP_TX, `ndo_xdp_xmit`, and page-pool recycling. XDP support is gated by MTU, per-CPU pools, and queue count.
- Phylink/PHY/COMPHY: phylink MAC and PCS callbacks, MDIO ioctl forwarding, fixed/in-band/PHY-managed link modes, generic PHY lane configuration, and EEE/LPI.
- Local mvpp2 modules: parser functions from `mvpp2_prs.*`, classifier/RSS/RFS functions from `mvpp2_cls.*`, TAI/PTP support from `mvpp2_tai.*`, and debugfs from `mvpp2_debugfs.c`.
- Firmware/firmware-node interfaces: OF/ACPI child nodes, `port-id`, `gop-port-id`, `phy-mode`, IRQ names, optional `marvell,system-controller`, `marvell,loopback`, MAC address sources, NVMEM MAC cells, and old ACPI compatibility mode.
- Hardware resources: packet processor MMIO, LMS or IFACE regions, CM3 SRAM for flow control, system-controller regmap, clocks, MBUS DRAM windows, AXI attributes, FIFO partitions, BM pools, parser/classifier tables, PTP queues, and interrupt lines.

## Risks and Edge Cases

- Descriptor accounting is delicate. RX/TX rings, per-thread aggregate TXQs, per-CPU reserved descriptors, and hardware counters must stay synchronized; mistakes cause queue stalls, leaks, double frees, or descriptor overruns.
- Some cleanup paths in queue allocation can return after partial allocation failures; callers rely on later cleanup/deinit paths and devm/percpu unwinding. Changes in `mvpp2_txq_init()` or setup rollback need careful review for partially initialized per-thread buffers and TSO header DMA.
- Shared hardware-thread locking is conditional on `priv->lock_map`. Any new BM refill or TX code that uses per-thread registers must preserve `get_cpu()`/`put_cpu()` or migration-disabled assumptions and lock when a thread can be used by more than one CPU.
- DMA address handling differs between PPv2.1 and PPv2.2/2.3 descriptors, and BM pool high-address registers restrict coherent memory. Changes must preserve 32-bit coherent mask assumptions and high-address release/allocation register programming.
- XDP and page_pool behavior is coupled to per-CPU BM pools and DMA direction. Adding/removing XDP can force BM pool rebuilds so page-pool DMA direction becomes bidirectional when needed.
- MTU changes can stop and restart ports and can reconfigure all ports' BM pools. Jumbo MTU, checksum-offload limitations on non-port-0 jumbo, and low-MTU pool switching are cross-port behaviors.
- Flow control depends on CM3 firmware. `mvpp2_enable_global_fc()` disables `global_tx_fc` if firmware does not acknowledge; code paths must tolerate SRAM absence, old DT/ACPI layouts, and unsupported firmware revisions.
- Link/MAC behavior differs across PPv2.1, PPv2.2, PPv2.3, GMAC, XLG, RGMII, SGMII, 802.3z, 5G/10GBASE-R, XAUI/RXAUI, OF phylink, and old ACPI link-IRQ mode. Mode reconfiguration touches resets, COMPHY, GOP syscon, PCS, MAC, interrupts, and max frame size.
- PTP TX timestamp queues hold SKB references indexed by hardware queue entry IDs. Queue wrap or missed PTP IRQ handling can drop old references; descriptor PTP bits must be cleared on non-PTP descriptors.
- Hardware stats are cumulative-folded; direct comparison with software stats is intentionally unreliable because hardware and software count at different processing points.

## Test Signals

- Build signals: compile this driver with relevant kernel configs for OF and ACPI, phylink, XDP, page_pool, PTP hardware timestamping, debugfs, and Marvell PPv2 support. Watch for generation-specific dead code warnings and API signature drift in ethtool/netdev/phylink callbacks.
- Probe/remove signals: platform device binds, expected clocks/resources map, no enabled-port error, ports register with expected MAC sources, debugfs initializes, and unload removes netdevs, BM pools, aggregate queues, clocks, workqueue, and debugfs without leaks or warnings.
- Link signals: phylink reports link up/down correctly for RGMII, SGMII, 1000BASE-X, 2500BASE-X, 5G/10GBASE-R, and old ACPI mode where applicable; carrier and TX queues follow link state; COMPHY power cycling does not break mode changes.
- Datapath signals: RX/TX traffic passes with small packets, jumbo frames, VLAN filtering, multicast/promiscuous modes, checksum offload, TSO, fragmented SKBs, concurrent multi-queue traffic, and queue stop/wake under load.
- Interrupt/NAPI signals: per-queue and shared IRQ modes work; TX completion via IRQ and hrtimer fallback both drain descriptors; NAPI completes and re-enables interrupts without stuck pending causes.
- XDP signals: attach/detach programs, XDP_PASS, XDP_DROP, XDP_TX, XDP_REDIRECT, and `ndo_xdp_xmit` succeed only under supported MTU/per-CPU-pool/TXQ conditions; page_pool recycling and DMA direction switching remain correct.
- MTU/BM signals: changing MTU while running stops/restarts safely, switches per-CPU/shared buffers when required, refills pools, and preserves flow control and checksum features.
- PTP signals: hardware timestamp get/set reports PHC index, RX timestamps appear when enabled, TX PTP packets receive timestamps from both queues, and non-PTP TX descriptors do not inherit stale PTP bits.
- Ethtool signals: coalescing and ring changes program hardware and recover on allocation failure; stats strings/counts match data layout; RSS contexts, indir tables, ntuple rules, pause, EEE, and link-ksettings return expected support or `-EOPNOTSUPP`.
