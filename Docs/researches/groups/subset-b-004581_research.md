# Research: subset-b-004581

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/mana_en.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/mana_en.c

## Purpose
`mana_en.c` is the main Microsoft Azure Network Adapter Ethernet driver implementation. It binds MANA GDMA devices to Linux `net_device` instances, manages vPort creation, TX/RX queue lifecycles, NAPI completion processing, RSS steering, XDP data paths, link-change handling, bandwidth shaping, auxiliary-device exposure, and suspend/resume removal flows.

## Important APIs, Types, And Functions
The file registers `mana_devops`, including `mana_open`, `mana_close`, `mana_start_xmit`, `mana_select_queue`, `mana_get_stats64`, `mana_change_mtu`, `mana_tx_timeout`, `mana_bpf`, and `mana_xdp_xmit`. It exports MANA core helpers for other namespaces through `EXPORT_SYMBOL_NS`, notably `mana_cfg_vport`, `mana_uncfg_vport`, `mana_create_wq_obj`, `mana_destroy_wq_obj`, `mana_disable_vport_rx`, and `mana_get_primary_netdev`. The central state objects are `struct mana_context`, `struct mana_port_context`, `struct mana_tx_qp`, `struct mana_txq`, `struct mana_rxq`, `struct mana_cq`, and GDMA queue/device types from `<net/mana/*>`.

## Control Flow
Probe starts in `mana_probe`, registers the GDMA device, allocates or reuses `mana_context`, creates EQs, queries device config, probes each vPort with `mana_probe_port`, registers netdevices, creates an auxiliary Ethernet device, and starts periodic GF stats work. `mana_open` allocates vPort queues and marks the port up; `mana_close` calls `mana_detach`. Queue allocation flows through `mana_create_vport`, `mana_cfg_vport`, `mana_create_txq`, `mana_add_rx_queues`, RSS initialization, PF filter registration, and XDP channel update. Detach clears `port_is_up`, disables TX, drains pending sends, disables RX steering, fences RQs, destroys RX/TX queue objects, unregisters PF filters and vPorts, and optionally detaches the netdevice.

TX starts in `mana_start_xmit`: it verifies the port is up, prepares headroom, chooses short or long OOB format, handles VLAN tags, GSO and checksum offload metadata, maps the SKB to DMA SGEs, posts a GDMA work request, manages queue stop/wake thresholds, rings the doorbell, and updates per-queue stats. TX completions in `mana_poll_tx_cq` validate CQEs, dequeue pending SKBs, unmap DMA, consume SKBs, advance SQ tail, and wake stopped netdev queues. RX queue creation preposts WQEs with page-pool or preallocated buffers. `mana_poll_rx_cq` drains completions, `mana_process_rx_cqe` refills each buffer before handing the old buffer to `mana_rx_skb`, and `mana_rx_skb` runs XDP, builds SKBs, applies checksum/RSS/VLAN metadata, then passes packets to GRO or XDP TX.

## State And Persistence
Runtime state is entirely kernel memory and hardware state: queue memory, GDMA object handles, debugfs dentries, RSS indirection/hash state, vPort use counts, port speed/shaper handles, XDP attachment, page pools, pending SKB queues, counters, and work items. No filesystem persistence is used except debugfs views. Synchronization relies on RTNL around attach/detach and link work, `vport_mutex` for vPort ownership, queue/NAPI ordering, atomics for pending sends, memory barriers around `port_is_up` and TX queue state, and u64 stat syncp seqlocks.

## Dependencies And Integration Points
The driver integrates with the Linux networking stack, NAPI, ethtool via `mana_ethtool_ops`, XDP helpers from other MANA files, GDMA hardware command APIs, debugfs, auxiliary bus devices for Ethernet/RDMA exposure, PCI FLR on stuck TX drain, net shaper APIs for bandwidth clamps, and PF/VF hardware command protocols. It also shares vPort programming with the RDMA driver, so `mana_cfg_vport` enforces the RAW QP single-user restriction through `vport_use_count`.

## Risks
The high-risk areas are DMA mapping/unmapping symmetry, queue teardown while completions are in flight, the 120 second TX drain path and FLR fallback, RX refill-before-delivery behavior under memory pressure, page-pool ownership for single-buffer versus fragment mode, XDP redirect/TX buffer ownership, PF filter/vPort deregistration on error paths, and the vPort sharing contract with RDMA. Hardware command response validation is critical because stale or mismatched activity IDs return `-EPROTO`. MTU, queue count, ring size, and shaper changes all detach and reattach the port, so rollback paths must preserve old state on failure.

## Test Signals
Useful signals include kernel build coverage with MANA enabled, probe/remove/resume cycles, `ip link set up/down`, MTU changes, ethtool channel/ring/RSS/coalesce changes, XDP attach/detach and redirect/TX tests, traffic with TSO/checksum/VLAN/RSS enabled, TX timeout injection, link event handling, PF mode filter registration, RDMA auxiliary probe/remove, debugfs queue dump sanity, and counter validation through `ip -s link` and ethtool stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/mana_en.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/mana_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/mana_ethtool.c

## Purpose
`mana_ethtool.c` implements ethtool operations for MANA Ethernet devices. It exposes driver, host-controller, PHY, RX queue, and TX queue statistics; RSS key and indirection table access; channel count changes; RX CQE coalescing controls; ring-size controls; and link settings.

## Important APIs, Types, And Functions
The exported object is `const struct ethtool_ops mana_ethtool_ops`. Local descriptor arrays map ethtool stat names to offsets in `struct mana_ethtool_stats`, `struct mana_ethtool_hc_stats`, and `struct mana_ethtool_phy_stats`. Major callbacks include `mana_get_sset_count`, `mana_get_strings`, `mana_get_ethtool_stats`, `mana_get_rxfh`, `mana_set_rxfh`, `mana_get_channels`, `mana_set_channels`, `mana_get_coalesce`, `mana_set_coalesce`, `mana_get_ringparam`, `mana_set_ringparam`, and `mana_get_link_ksettings`.

## Control Flow
Stats collection returns early when the port is down. When up, `mana_get_ethtool_stats` first refreshes PHY stats through `mana_query_phy_stats`, copies global software and hardware counters through descriptor offsets, then reads RX/TX per-queue counters under `u64_stats_fetch_begin/retry`. RSS reads copy the current indirection table and hash key; RSS writes validate Toeplitz-only hashing, clone current state, update requested key/table fields, call `mana_config_rss`, and restore the saved values if hardware programming fails. Channel, ring, and MTU-affecting operations preallocate RX buffers before calling `mana_detach`, mutate the relevant queue count or ring sizes, call `mana_attach`, and roll back software values if attach fails. Coalescing toggles `cqe_coalescing_enable` and reprograms RSS/steering while the port is up.

## State And Persistence
The file does not persist data outside memory. It reads and mutates `mana_port_context` fields such as `num_queues`, `max_queues`, `indir_table`, `hashkey`, `cqe_coalescing_enable`, `cqe_coalescing_timeout_ns`, `rx_queue_size`, and `tx_queue_size`. It also surfaces counters owned by RX/TX queues and MANA hardware-stat snapshots. State changes are applied through `mana_detach`/`mana_attach`, meaning hardware and queue state is rebuilt rather than patched in place for channel and ring changes.

## Dependencies And Integration Points
This file depends on `mana_en.c` for RSS programming, PHY/link queries, queue preallocation, detach, and attach. It integrates with the kernel ethtool core, netlink extended ACK strings for invalid parameters, and MANA hardware command helpers.

## Risks
Key risks are mismatches between stat string count and data fill order, insufficient rollback after RSS or attach failures, queue/ring changes while traffic is active, and stale PHY stats if hardware commands fail silently. `mana_set_ringparam` rounds requested counts to powers of two, so user-visible behavior should be tested. `mana_set_channels` trusts the requested combined count after preallocation and depends on ethtool core validation for min/max bounds.

## Test Signals
Run `ethtool -S`, `ethtool -x/-X`, `ethtool -l/-L`, `ethtool -c/-C`, `ethtool -g/-G`, and `ethtool -k` while traffic is flowing and while the port is down. Regression tests should verify RSS rollback on invalid table entries, coalescing frame limits, ring min validation, stat count stability, and successful detach/attach recovery after channel or ring changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/mana_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/shm_channel.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/shm_channel.c

## Purpose
`shm_channel.c` implements the MANA shared-memory channel used by a VF to ask the PF or hardware to establish and destroy the hardware communication channel. It packs queue physical frame addresses and protocol control fields into a 256-bit MMIO shared-memory aperture.

## Important APIs, Types, And Functions
The file defines `union smc_proto_hdr`, a 32-bit hardware protocol header containing message type, version, direction, status, VF reset request, and owner bits. Public entry points are `mana_smc_init`, `mana_smc_setup_hwc`, and `mana_smc_teardown_hwc`. Internal helpers are `mana_smc_poll_register` and `mana_smc_read_response`.

## Control Flow
`mana_smc_init` stores the device and shared-memory base pointer. `mana_smc_setup_hwc` waits until the VF owns the shared memory, validates page alignment for EQ/CQ/RQ/SQ addresses and a 16-bit MSI-X vector, packs the low 48 bits plus high 4 bits of each page frame into the aperture, writes the EQ vector, writes an establish-HWC protocol header in the final dword, then waits for and validates the PF response. `mana_smc_teardown_hwc` similarly waits for ownership, writes a destroy-HWC header into the final dword, and waits for completion so hardware invalidates state before software frees backing memory.

## State And Persistence
The only driver state is `struct shm_channel` with `dev` and `base`. Persistent state lives in device-owned shared memory and hardware ownership bits. Reset handling accepts `0xffffffff` as the shared-memory reset state when `reset_vf` is true.

## Dependencies And Integration Points
The file uses MMIO `readl`/`writel`, `usleep_range`, MANA page-frame macros, and the shared HWC setup protocol defined by MANA hardware. It is called during GDMA/HWC bring-up and teardown before or after queue memory lifetimes.

## Risks
Risks include incorrect address packing, unaligned queue addresses, endian or aliasing assumptions when writing 48-bit fields through `u64 *`, timeouts if ownership does not return, and freeing queue memory before destroy acknowledgment. The reset path must tolerate all-ones reads without treating them as malformed protocol headers.

## Test Signals
Tests should exercise normal HWC setup/teardown, reset requested setup/teardown, invalid unaligned addresses, invalid MSI-X vector values, PF timeout injection, malformed response header fields, nonzero response status, and teardown ordering under device reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/shm_channel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/Kconfig

## Purpose
This Kconfig file defines the MOXA ART Ethernet vendor menu and the `ARM_MOXART_ETHER` driver option for the internal Ethernet controller on MOXA ART SoCs.

## Important APIs, Types, And Functions
It declares `NET_VENDOR_MOXART` as a boolean vendor gate, defaulting to `y` only when its dependencies are met, and `ARM_MOXART_ETHER` as a tristate driver option. The driver option depends on `ARM && ARCH_MOXART` and selects `NET_CORE`.

## Control Flow
Kconfig evaluation first exposes the vendor menu when building for ARM MOXART. If enabled, the `ARM_MOXART_ETHER` prompt becomes available and determines whether `moxart_ether.o` can be built into the kernel, built as a module, or omitted.

## State And Persistence
The persistent output is the kernel `.config` symbol selection. No runtime state exists in this file.

## Dependencies And Integration Points
The file integrates with the top-level Ethernet vendor Kconfig hierarchy and the local Makefile, where `CONFIG_ARM_MOXART_ETHER` controls object inclusion. It is tightly scoped to ARM MOXART platforms.

## Risks
The main risk is configuration visibility: non-MOXART builds cannot select this driver. Selecting `NET_CORE` is conservative but the driver also depends on platform, DMA, interrupt, and OF support through normal kernel infrastructure.

## Test Signals
Validate with `oldconfig` or `menuconfig` on an `ARCH_MOXART` ARM configuration, then confirm that `CONFIG_ARM_MOXART_ETHER=m/y` causes `moxart_ether.o` to build and that non-MOXART configs do not expose the prompt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/Makefile

## Purpose
The Makefile wires the MOXART Ethernet driver object into the kernel build.

## Important APIs, Types, And Functions
It contains one build rule: `obj-$(CONFIG_ARM_MOXART_ETHER) += moxart_ether.o`.

## Control Flow
When Kconfig sets `CONFIG_ARM_MOXART_ETHER` to `y`, the object is built into the kernel. When set to `m`, it is built as a module. When unset, no object from this directory is compiled.

## State And Persistence
The file has no runtime state. Its persistent effect is the build graph generated by Kbuild.

## Dependencies And Integration Points
It depends on the symbol declared in the sibling Kconfig and on Kbuild conventions. The compiled object contains the platform driver and module metadata from `moxart_ether.c`.

## Risks
The rule is simple. The main risk is symbol drift if Kconfig renames the driver or if additional source files are added without updating the object list.

## Test Signals
Run a kernel build with `CONFIG_ARM_MOXART_ETHER=y` and `m` and confirm `drivers/net/ethernet/moxa/moxart_ether.o` or `.ko` is produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/moxart_ether.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/moxart_ether.c

## Purpose
`moxart_ether.c` is a platform Ethernet driver for the MOXA ART internal MAC, documented as RTL8201CP based hardware. It provides netdev open/stop/transmit/multicast/MAC-address operations, fixed RX/TX descriptor rings, interrupt handling, and Device Tree probing.

## Important APIs, Types, And Functions
The driver uses `struct moxart_mac_priv_t` from `moxart_ether.h` for private state. Key functions are `moxart_mac_probe`, `moxart_remove`, `moxart_mac_open`, `moxart_mac_stop`, `moxart_rx_poll`, `moxart_mac_start_xmit`, `moxart_tx_finished`, `moxart_mac_interrupt`, `moxart_mac_set_rx_mode`, and `moxart_set_mac_address`. The netdev ops are collected in `moxart_netdev_ops`, and the platform driver matches `moxa,moxart-mac`.

## Control Flow
Probe allocates an Ethernet device, maps the first MMIO resource, parses IRQ 0, obtains or randomizes the MAC address, allocates coherent descriptor rings and separate RX/TX buffer areas, requests the interrupt, adds NAPI, and registers the netdev. Open enables NAPI, resets the MAC, writes the MAC address, initializes TX and RX descriptor rings, enables interrupts/DMA/MAC units, and starts the TX queue. RX interrupt masks RX completion and schedules NAPI. `moxart_rx_poll` walks RX descriptors until the budget or DMA-owned descriptor, validates error bits, syncs the DMA buffer for CPU, copies the packet into a newly allocated SKB, sends it to GRO, updates stats, then returns descriptor ownership to DMA. TX maps the outgoing SKB data, fills the current descriptor, pads short frames, syncs for device, sets first/last/end bits, gives ownership to DMA, kicks poll demand, advances the ring head, and updates the watchdog timestamp. TX completion unmaps all descriptors from tail to head, updates stats, consumes SKBs, and wakes the queue if enough space returns.

## State And Persistence
State is held in descriptor memory, DMA mappings, per-ring indices, SKB pointers, software copies of register values, NAPI state, and netdev stats. Nothing persists across unload except platform firmware configuration. RX buffers are permanently allocated for the device lifetime and remapped on open, while TX maps each SKB on demand and unmaps on completion.

## Dependencies And Integration Points
The driver integrates with platform devices, Device Tree address and IRQ parsing, DMA mapping, NAPI/GRO, Kbuild module registration, and the generic Ethernet netdev stack. Register definitions, descriptor bit fields, ring sizes, and private state come from `moxart_ether.h`.

## Risks
The TX ring cleanup drains all descriptors from tail to head on any TX completion interrupt without checking per-descriptor DMA ownership, which assumes interrupts only arrive after all queued descriptors have completed. RX copies packets rather than building SKBs around DMA buffers, which is simple but costs memory bandwidth. Multicast hash registers are only ORed when addresses are added and are not cleared before recomputing a new list, so stale multicast bits can remain. TX padding writes beyond `skb->len` without explicitly expanding tailroom, relying on the original SKB headroom/tailroom. Error paths after partial RX DMA mapping in ring setup log mapping failures but continue. Probe uses `irq_of_parse_and_map` and later `devm_request_irq`, with manual `devm_free_irq` in remove.

## Test Signals
Test probe/remove, random and firmware MAC address paths, open/stop cycles, ping and bulk TX/RX traffic, NAPI budget behavior, multicast filter changes, queue stop/wake under TX pressure, RX error descriptors, DMA mapping failure injection, and module unload. Hardware tests should inspect interrupt mask/status and descriptor ownership transitions under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/moxart_ether.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/moxart_ether.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/moxart_ether.h

## Purpose
`moxart_ether.h` defines the MOXA ART Ethernet register map, descriptor layouts, bit masks, ring sizes, buffer sizing limits, and private driver state used by `moxart_ether.c`.

## Important APIs, Types, And Functions
The header has no functions. It defines TX/RX descriptor offsets and flags such as `TX_DESC0_DMA_OWN`, `TX_DESC1_LTS`, `RX_DESC0_DMA_OWN`, and RX error bits; ring constants such as `TX_DESC_NUM`, `RX_DESC_NUM`, `TX_NEXT`, `RX_NEXT`, `TX_WAKE_THRESHOLD`; MMIO register offsets from interrupt status through counters; MAC/PHY/flow-control/test-mode bit fields; and `struct moxart_mac_priv_t`.

## Control Flow
The macros shape runtime control in the C file. Ring wrap macros implement power-of-two descriptor cycling. Descriptor ownership bits coordinate DMA versus CPU ownership. Register bit masks drive reset, interrupt masking, MAC enable, DMA enable, RX filtering, multicast hashing, and PHY access.

## State And Persistence
`struct moxart_mac_priv_t` contains all persistent in-memory state for a device instance: platform device, MMIO base, cached MAC control and interrupt-mask registers, NAPI, netdev pointer, coherent RX/TX descriptor bases and DMA addresses, RX/TX buffer arrays and mappings, ring head/tail indices, TX lock, TX lengths, and pending TX SKBs.

## Dependencies And Integration Points
The header is consumed by the MOXART platform driver and assumes Linux kernel types such as `struct platform_device`, `struct napi_struct`, `struct net_device`, `dma_addr_t`, `spinlock_t`, and `struct sk_buff`. Register definitions are specific to the MOXART MAC block.

## Risks
The header encodes fixed 64-entry rings and 1600-byte buffers, so jumbo frames are unsupported. Compile-time checks reject buffers that exceed the descriptor size mask. There is a likely typo in `tx_buf[RX_DESC_NUM]`, which happens to be harmless only because RX and TX descriptor counts are both 64. Any hardware revision with different register layout, descriptor format, or buffer-size limits would require coordinated changes.

## Test Signals
Compile coverage should catch buffer-size mask violations. Runtime tests should validate ring wrap at 64 descriptors, descriptor `END` handling, RX/TX buffer size limits, register writes for promiscuous and multicast modes, and DMA ownership transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/moxart_ether.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/Kconfig

## Purpose
This Kconfig file defines Microsemi Ethernet switch support, including the shared Ocelot switch library and the platform Ocelot switch driver.

## Important APIs, Types, And Functions
It declares `NET_VENDOR_MICROSEMI`, `MSCC_OCELOT_SWITCH_LIB`, and `MSCC_OCELOT_SWITCH`. The library is a tristate selected by consumers and selects `NET_DEVLINK`, `REGMAP_MMIO`, `PACKING`, and `PHYLINK`, while depending on optional PTP clock support. The platform switch driver depends on switchdev, bridge compatibility, IOMEM, OF, and PTP optional support, and selects the library plus `GENERIC_PHY`.

## Control Flow
The vendor option gates Microsemi device prompts. `MSCC_OCELOT_SWITCH_LIB` can be selected by switchdev or DSA drivers as common hardware support. `MSCC_OCELOT_SWITCH` exposes the VSC7514 Ocelot SoC switch driver and pulls in the common library.

## State And Persistence
The only persistent state is kernel configuration. There is no runtime state in this file.

## Dependencies And Integration Points
The symbols feed the sibling Makefile, which builds `mscc_ocelot_switch_lib.o` and `mscc_ocelot.o`. The dependency list documents that the full driver expects switchdev, bridge, OF, regmap MMIO, phylink, devlink, generic PHY, and optional PTP.

## Risks
Because `MSCC_OCELOT_SWITCH_LIB` is non-prompted and selected, its dependencies must remain satisfiable for all consumers. Bridge dependency handling allows builds with `BRIDGE=n`, but bridge-enabled runtime features depend on switchdev/bridge integration.

## Test Signals
Build matrix coverage should include `MSCC_OCELOT_SWITCH_LIB=m/y`, `MSCC_OCELOT_SWITCH=m/y`, PTP enabled/disabled, bridge enabled/disabled where legal, and DSA consumers that select the library without the platform driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/Makefile

## Purpose
This Makefile defines the object composition for the Microsemi Ocelot switch library and the platform Ocelot switch driver.

## Important APIs, Types, And Functions
`obj-$(CONFIG_MSCC_OCELOT_SWITCH_LIB)` builds `mscc_ocelot_switch_lib.o` from common modules including `ocelot.o`, devlink, flower, IO, MAC Merge, policing, PTP, stats, VCAP, and register definitions. `ocelot_mrp.o` is conditionally included when `CONFIG_BRIDGE_MRP` is set. `obj-$(CONFIG_MSCC_OCELOT_SWITCH)` builds `mscc_ocelot.o` from FDMA, netdev, and VSC7514 platform pieces.

## Control Flow
Kbuild links common library objects whenever the library symbol is enabled, then links the platform driver objects when the platform symbol is enabled. Conditional object inclusion keeps MRP support tied to bridge MRP availability.

## State And Persistence
The file has no runtime state. Its persistent effect is the module or built-in object graph for the configured kernel.

## Dependencies And Integration Points
It mirrors the Kconfig split between shared Ocelot hardware library and platform switchdev driver. `ocelot.c` is the core library file for many exported switch operations.

## Risks
Object list drift is the main risk. Adding new exported library functionality without updating `mscc_ocelot_switch_lib-y`, or adding platform-specific code without updating `mscc_ocelot-y`, would produce link or feature gaps.

## Test Signals
Build with the library only, with the platform driver, and with `CONFIG_BRIDGE_MRP` toggled. Confirm expected objects are linked into either built-in archives or modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot.c

## Purpose
`ocelot.c` is the core Microsemi Ocelot switch library. It programs MAC and VLAN tables, VCAP filters, phylink MAC state, CPU injection/extraction queues, PTP RX timestamps, FDB/MDB entries, bridge forwarding domains, DSA tag_8021q CPU port assignments, LAG offload, QoS, mirroring, frame preemption hooks, port initialization, switch reset, and global switch initialization.

## Important APIs, Types, And Functions
The file exports many library APIs used by Ocelot platform and DSA drivers: MAC table operations (`ocelot_mact_learn`, `ocelot_mact_forget`, `ocelot_mact_lookup`, `ocelot_mact_flush`, `ocelot_fdb_*`), VLAN operations (`ocelot_port_vlan_filtering`, `ocelot_vlan_prepare`, `ocelot_vlan_add`, `ocelot_vlan_del`), phylink helpers (`ocelot_phylink_mac_config`, `ocelot_phylink_mac_link_down`, `ocelot_phylink_mac_link_up`), CPU queue helpers (`ocelot_xtr_poll_frame`, `ocelot_can_inject`, `ocelot_port_inject_frame`, `ocelot_drain_cpu_queue`), bridge/LAG/MDB helpers, mirror helpers, QoS DSCP/default-priority helpers, `ocelot_init_port`, `ocelot_reset`, `ocelot_init`, and `ocelot_deinit`. Important local structures include `struct ocelot_mact_entry`, `struct ocelot_pgid`, and `struct ocelot_multicast`.

## Control Flow
Initialization starts with optional hardware reset, lock and workqueue setup, stats initialization, list setup, feature detection, MAC table initialization, VLAN table initialization, VCAP initialization, CPU port setup, optional PSFP and MAC Merge initialization, counter clearing, VLAN ethertype setup, aggregation hash configuration, ageing configuration, flooding PGID setup, source PGID isolation, multicast PGID defaults, CPU queue routing, and injection/extraction group setup. Per-port initialization configures MAC IFG/HDX, max frame length and watermarks, VLAN tag awareness, pause frame source, flood/drop behavior, default VLAN TPID, learning state, receive enable, logical port ID, and VCAP lookups.

MAC table operations serialize through `mact_lock`, select MAC/VID in hardware registers, issue learn/forget/read/age commands, and poll for idle completion. VLAN operations maintain an in-memory list of `ocelot_bridge_vlan` entries while programming `ANA_TABLES_VLANACCESS`; PVID and egress tag decisions update VLAN classification and rewrite registers. The VLAN reclassification path installs or updates VCAP IS1 rules to make Linux bridge 802.1Q behavior match hardware that otherwise treats 802.1Q and 802.1ad similarly. CPU extraction parses the extraction frame header, allocates an SKB, reads frame words including FCS handling, applies optional PTP timestamp, sets offload forwarding marks, and returns the packet. Injection writes SOF, IFH, payload, padding, EOF/valid-byte metadata, dummy CRC, timestamps, and stats.

Bridge and LAG flows are protected by `fwd_domain_lock`. They compute PGID source masks, reserved VLANs for VLAN-unaware bridges, DSA CPU-port assignment masks, LAG logical IDs, aggregation PGIDs, multicast PGID allocation, and FDB migration when LAG IDs change. Phylink link-down disables RX, updates cut-through forwarding, disables core port forwarding, flushes queues, and may reset MAC clocks; link-up configures speed/duplex/pause, enables MAC RX/TX, updates frame preemption state, and re-enables forwarding.

## State And Persistence
State is maintained in `struct ocelot`: hardware register maps, regfields, port pointers, locks, ordered workqueue, stats, packet-buffer limits, VCAP blocks, multicast and PGID lists, VLAN list, LAG FDB list, mirror state, CPU/NPI configuration, and per-port bridge/LAG/VLAN/STP/QoS state. No filesystem persistence exists. Hardware tables and registers are authoritative at runtime, while linked lists mirror enough state to recompute masks and migrate entries.

## Dependencies And Integration Points
The file depends on regmap, phylink, switchdev/bridge semantics, DSA Ocelot tagging, PTP helpers, VCAP implementation, qsys/sys/ana/dev register definitions, devlink/stats modules, frame preemption and MAC Merge helpers, and hardware-specific `ocelot->ops` callbacks. It exports symbols for the platform switch driver and DSA-family users.

## Risks
Risk concentrates around hardware table polling timeouts, lock ordering between MAC table, forwarding-domain, injection, and extraction locks, VLAN semantics around reserved VID 4000-4095, VCAP rule lifetime when VLAN state or QoS defaults change, PGID exhaustion for generic multicast masks, LAG FDB migration after logical ID changes, cut-through forwarding updates around link and bridge-domain changes, and CPU extraction robustness when hardware returns abort/pruned/escape words. Initialization has many hardware ordering assumptions; partial init failures must deinitialize stats/workqueues without leaving programmed tables assumed by later code.

## Test Signals
Important tests include switch initialization and reset timeout injection, per-port phylink up/down at 10/100/1000/2500 speeds with pause, VLAN-aware and VLAN-unaware bridge joins/leaves, reserved VID rejection, PVID changes with 802.1ad ingress reclassification, FDB add/delete/dump/flush, MDB add/delete with IPv4/IPv6 and generic multicast masks, STP state transitions, DSA tag_8021q CPU assignment, LAG join/leave/change with FDB migration, CPU injection/extraction traffic, PTP RX timestamp validation, mirroring, DSCP priority add/delete, mqprio, MTU changes, and deinit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot.h

## Purpose
`ocelot.h` is the private header for the Microsemi Ocelot switch driver library. It gathers required kernel and SoC register headers, defines local constants, declares per-port private structures for the platform netdev side, and exposes core library function prototypes used across Ocelot modules.

## Important APIs, Types, And Functions
The header defines constants such as `OCELOT_STANDALONE_PVID`, `OCELOT_BUFFER_CELL_SZ`, `OCELOT_STATS_CHECK_DELAY`, `OCELOT_PTP_QUEUE_SZ`, and `OCELOT_JUMBO_MTU`. It defines `struct ocelot_port_tc`, `struct ocelot_port_private`, `struct ocelot_pgid`, and `struct ocelot_multicast`. It provides the inline helper `ocelot_reg_to_target_addr`, and declares APIs for bridge lookup, MAC table learn/forget, netdev-port translation, port probe/release, devlink port setup, traps, mirroring, stats, MAC Merge, and frame preemption updates.

## Control Flow
The header does not execute control flow directly, but it defines the contracts that split Ocelot logic across core, netdev, devlink, stats, VCAP, PTP, MM, and platform files. `ocelot_reg_to_target_addr` maps a logical register enum to a hardware target and offset using `ocelot->map`.

## State And Persistence
The declared structures describe in-memory state. `ocelot_port_private` embeds the shared `struct ocelot_port`, its `net_device`, phylink objects, and traffic-control offload bookkeeping. `ocelot_pgid` and `ocelot_multicast` are list entries used by `ocelot.c` to mirror multicast destination masks and hardware MAC-table entries. No persistent storage is involved.

## Dependencies And Integration Points
The header includes Linux networking, phylink, platform, regmap, timestamping, and SoC Ocelot register headers. It is included by multiple Ocelot implementation files and forms the internal ABI between the core library and platform/feature modules.

## Risks
Because this is an internal ABI, changing structure fields or function prototypes affects several objects in `mscc_ocelot_switch_lib.o` and `mscc_ocelot.o`. The `ocelot_pgid` design reflects limited hardware multicast destination entries, so misuse can cause PGID leaks or exhaustion. `ocelot_port_private` combines netdev and core state, so lifetime ordering with port release and phylink teardown matters.

## Test Signals
Build coverage across all Ocelot objects is the primary signal for this header. Runtime signals include multicast PGID refcounting, per-port phylink setup/teardown, devlink port init/teardown, stats init/deinit, MAC Merge initialization, and successful netdev-to-port translation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot.h -->
