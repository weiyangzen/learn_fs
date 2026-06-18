# Research: subset-b-004619

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_main.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_main.c

Purpose: implements the PCI/netdev-facing Rocker switch driver core. It discovers the Red Hat Rocker PCI device, maps BAR0, validates MSI-X vector counts, runs register/DMA self-tests, creates device-level command/event DMA rings, probes per-port net_devices, and bridges Linux netdev, switchdev, netevent, and FIB notifier events into a pluggable Rocker "world" implementation. In this tree the only world is OF-DPA, supplied by `rocker_ofdpa_ops`.

Important APIs and functions: `rocker_cmd_exec()` is the exported command submission path used by world code. It reserves a command descriptor under `cmd_ring_lock`, initializes the descriptor cookie as a `rocker_wait`, calls a caller-supplied TLV prepare callback, advances the hardware head, optionally waits for the command interrupt, maps Rocker completion errors to Linux errno, and invokes an optional response parser. `rocker_probe()` and `rocker_remove()` own PCI lifetime. `rocker_port_open()`, `rocker_port_stop()`, and `rocker_port_xmit()` implement net_device behavior. `rocker_port_poll_tx()` and `rocker_port_poll_rx()` are NAPI poll handlers. Switchdev callbacks (`rocker_switchdev_event()`, `rocker_switchdev_blocking_event()`) and notifier handlers (`rocker_router_fib_event()`, `rocker_netdevice_event()`, `rocker_netevent_event()`) route policy changes into world callbacks.

Control flow: module init registers netdevice and netevent notifiers before registering the PCI driver. Probe enables PCI, requests regions, sets a 64-bit coherent DMA mask, ioremaps BAR0, reads `PORT_PHYS_COUNT`, enables exact MSI-X vectors, runs `rocker_basic_hw_test()`, resets hardware, initializes command/event rings, requests command/event IRQs, creates an ordered workqueue, probes all ports, registers FIB and switchdev notifiers, and reads the switch ID. Per-port probe allocates an Ethernet device, discovers/initializes the world mode, fetches the hardware MAC, installs netdev/ethtool ops, adds NAPI contexts, registers the device, and then calls world port init. Open creates TX/RX rings, requests per-port IRQs, calls world port open, enables NAPI, enables the physical port when not proto-down, and starts the queue. Stop reverses those steps.

State and persistence: persistent state is in memory and hardware registers only. `struct rocker` stores PCI resources, MSI-X entries, command/event rings, port array, ordered workqueue, world ops/private data, FIB notifier, and switch ID. `struct rocker_port` stores per-port rings, NAPI state, netdev, physical port number, and world-private state. DMA ring state tracks head/tail, coherent descriptors, per-descriptor buffers/cookies, and TLV sizes. TX/RX packet accounting updates `net_device_stats`; ethtool stats are fetched via command TLVs.

Dependencies and integration: depends on PCI, DMA mapping, MSI-X, NAPI, net_device, ethtool, switchdev, rtnetlink, ARP/neighbour, FIB notifier, and the Rocker hardware/TLV headers. It integrates hardware link and MAC/VLAN learning events into carrier state and OF-DPA learning, and integrates Linux bridge/FDB/VLAN/STP/FIB changes into world callbacks.

Risks: command wait timeout is fixed at `HZ / 10`, so slow hardware/emulation can surface as `-EIO`. Many hardware interactions assume Rocker TLV schemas are well formed. `rocker_change_mtu()` stops a running port and changes `dev->mtu` before command success, so a failed MTU set can leave software state changed. Workqueue callbacks retain references for queued switchdev FDB work, but FIB work relies on held `fib_info`/rules and careful RTNL ordering. Ring lifetime, DMA unmap direction consistency, and nowait command descriptor reuse are core bug surfaces.

Test signals: PCI probe/remove on Rocker emulation, basic register/DMA test success, MSI-X vector count validation, successful netdev registration for every physical port, TX/RX NAPI traffic, ethtool settings/stats commands, link-change event carrier updates, bridge VLAN/FDB/STP operations through switchdev, neighbour update/destroy, and IPv4 route add/delete/abort behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_ofdpa.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_ofdpa.c

Purpose: implements the Rocker OF-DPA-like world selected by `rocker_main.c`. It translates Linux switchdev, neighbour, bridge, STP, VLAN, learned-FDB, and IPv4 FIB events into Rocker OF-DPA flow and group table commands while maintaining software shadow tables for installed flows, groups, learned FDB entries, internal VLAN allocations, and neighbour nexthops.

Important APIs and types: `struct rocker_world_ops rocker_ofdpa_ops` exports the implementation to the core. `struct ofdpa` is global per-device world state: flow/group/FDB/internal-VLAN/neighbour hash tables, locks, FDB cleanup timer, cookie/index counters, ageing state, and FIB abort flag. `struct ofdpa_port` is per-port state: associated netdev, pport, bridge/OVS master, internal VLAN, STP state, bridge flags, ageing time, active control rules, and VLAN bitmap. Flow/group programming funnels through `ofdpa_flow_tbl_do()` and `ofdpa_group_tbl_do()`, which build TLV commands via `rocker_cmd_exec()`.

Control flow: device init creates hash tables and starts the FDB cleanup timer. Port init enables hardware learning according to bridge flags, installs an ingress-port table entry, allocates an internal VLAN for untagged traffic, and installs VLAN 0 plus router MAC/control entries. STP changes compute desired control flows, update ACL/termination/bridge defaults, flush learned FDB entries if forwarding is disabled, and add or remove L2 interface groups to represent forwarding state. Bridge join/leave removes VLAN 0, swaps the internal VLAN from per-port to per-bridge or back, reinstalls VLAN 0, and calls switchdev offload/unoffload helpers. FDB learn events install bridging flows and optionally notify the bridge. Neighbour and FIB events create L3 unicast groups and /32 neighbour routes, then program route entries toward resolved nexthops or CPU fallback groups.

State and persistence: all state is volatile shadow state synchronized to hardware. Flow entries are keyed by a CRC32 over a table-specific key and receive monotonically increasing cookies. Group entries are keyed by Rocker group ID. FDB entries track learned/static status and last touched jiffies. Internal VLAN entries are reference-counted by ifindex over a 255-entry reserved range. Neighbour entries are reference-counted, indexed, and retain resolved destination MAC and TTL-check state. Learned FDB ageing uses `ofdpa->ageing_time`/per-port ageing and a timer.

Dependencies and integration: depends on Rocker command/TLV APIs, Linux bridge constants, switchdev notifier semantics, neighbour/ARP APIs, IPv4 FIB structures, nexthop helpers, CRC32, hash tables, and RTNL-context callbacks from the core driver. It programs Rocker OF-DPA table IDs and group encodings defined in Rocker headers.

Risks: shadow tables are often mutated before hardware command success, so failed commands can desynchronize software and device state. `ofdpa_fib4_abort()` iterates the flow table under `flow_tbl_lock` and calls `ofdpa_flow_tbl_del()`, which takes the same lock, a lock recursion/deadlock risk. `ofdpa_fini()` deletes hash nodes but does not free every entry, so memory cleanup relies on device removal scope and may leak. Internal VLAN exhaustion returns VLAN 0 after logging. ECMP, IPv6 routing, nexthop objects, and some VLAN flags/PVID semantics are explicitly unsupported or incomplete. Nowait commands mean errors may be logged only indirectly.

Test signals: bridge join/leave with untagged VLAN remapping, VLAN add/delete, STP state transitions, BR_LEARNING toggles, learned FDB ageing and bridge notifications, static FDB add/delete, ARP resolution and neighbour invalidation, IPv4 route offload and abort paths, OVS master attach, and hardware command error injection for rollback/desync behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_ofdpa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_tlv.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_tlv.c

Purpose: provides the out-of-line Rocker TLV parser and writer used by command, event, TX, and RX descriptor payload handling. It is intentionally narrow: parse an aligned TLV buffer into an indexed table and append one TLV to a descriptor buffer.

Important APIs: `rocker_tlv_parse()` clears a caller-provided table of `maxtype + 1` pointers, walks the TLV stream with `rocker_tlv_for_each()`, and stores TLVs whose type is within `1..maxtype`. `rocker_tlv_put()` checks descriptor tailroom, writes type/length, copies payload bytes, and zero-fills alignment padding.

Control flow: callers provide a descriptor data buffer and expected max type. Parse does no schema validation beyond the iterator's size checks and type bounds. Put calculates aligned total size from `rocker_tlv_total_size()`, appends at `rocker_tlv_start()`, advances `desc_info->tlv_size`, and returns `-EMSGSIZE` if the descriptor cannot hold the new attribute.

State and persistence: it only mutates the caller's descriptor TLV size and output parse table. No global state exists.

Dependencies and integration: depends on `rocker_tlv.h`, `rocker_hw.h`, `rocker.h`, string helpers, and errno. It is the common serialization path for Rocker command preparation and event/RX/TX parsing.

Risks: duplicate attribute types overwrite earlier entries in the parse table. Payload type, endian, and length validation are entirely caller-owned. `rocker_tlv_put()` assumes `data` is valid for nonzero `attrlen`, and zero-length nesting uses `NULL` safely only because memcpy length is zero.

Test signals: malformed length/alignment parsing, duplicate TLV type behavior, descriptor full path returning `-EMSGSIZE`, nested TLV construction, and all Rocker command/event schemas that depend on correct parse indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_tlv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_tlv.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_tlv.h

Purpose: defines the Rocker TLV wire layout helpers, alignment rules, typed accessors, parse wrappers, append wrappers, and nested attribute helpers used throughout the Rocker driver.

Important APIs: alignment is fixed at 8 bytes via `ROCKER_TLV_ALIGNTO`; `ROCKER_TLV_HDRLEN` is the aligned `struct rocker_tlv` size. Iteration uses `rocker_tlv_ok()`, `rocker_tlv_next()`, `rocker_tlv_for_each()`, and `rocker_tlv_for_each_nested()`. Accessors include `rocker_tlv_type()`, `rocker_tlv_data()`, `rocker_tlv_len()`, and typed getters for u8/u16/be16/u32/u64. Writers include `rocker_tlv_put_u8/u16/be16/u32/be32/u64()`, `rocker_tlv_nest_start()`, `rocker_tlv_nest_end()`, and `rocker_tlv_nest_cancel()`.

Control flow: command builders append fields by repeatedly calling typed put helpers. Nested commands reserve an empty TLV, append children, then patch the parent length at nest end. Cancel resets `desc_info->tlv_size` to the nested TLV start.

State and persistence: this header owns no state. It manipulates caller-owned descriptor buffers and relies on descriptor `data_size`, `tlv_size`, and `desc->tlv_size` for bounds and parsing.

Dependencies and integration: directly includes Rocker hardware and core structures, so it is tightly coupled to descriptor layout. It underpins Rocker command prep, command response parsing, event parsing, and TX/RX fragment descriptors.

Risks: typed getters cast directly from unaligned-looking payload addresses, relying on the 8-byte-aligned TLV header/data layout. There is no endian conversion for host-order getters. Nest length patching assumes no concurrent mutation of the descriptor. `rocker_tlv_parse_desc()` trusts `desc_info->desc->tlv_size`, so corrupted hardware writeback can affect parsing until iterator bounds stop it.

Test signals: compile coverage on architectures with strict alignment, nested cancel/end behavior, parsing of zero-length and padded attributes, and command builders that fill descriptors near capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_tlv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/Kconfig

Purpose: declares the Samsung Ethernet vendor menu and the SXGBE Ethernet driver option.

Important symbols: `NET_VENDOR_SAMSUNG` is a boolean vendor gate defaulting to `y`; choosing `n` hides Samsung-specific Ethernet options without directly changing built objects. `SXGBE_ETH` is a tristate for the Samsung 10G/2.5G/1G SXGBE Ethernet driver. It depends on `HAS_IOMEM`, `HAS_DMA`, and `PTP_1588_CLOCK_OPTIONAL`, and selects `PHYLIB` and `CRC32`.

Control flow: Kconfig visibility flows from the vendor gate. When `SXGBE_ETH=y` or `m`, the Makefiles include the SXGBE directory and build `samsung-sxgbe`.

State and persistence: only build configuration state in `.config`; no runtime state.

Dependencies and integration: integrates the SXGBE driver into the kernel networking configuration hierarchy under Samsung Ethernet devices and ensures PHY and CRC helpers are selected.

Risks: optional PTP dependency means timestamp support must still be guarded at runtime. Default vendor `y` increases prompt visibility. Missing platform dependencies are deferred to probe/device tree rather than this Kconfig.

Test signals: `allyesconfig`, `allmodconfig`, and minimal configs with `NET_VENDOR_SAMSUNG=n`; module build name `samsung-sxgbe`; dependency checks for I/O memory, DMA, PHYLIB, CRC32, and optional PTP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/Makefile

Purpose: top-level Samsung Ethernet build glue.

Important rule: `obj-$(CONFIG_SXGBE_ETH) += sxgbe/` descends into the SXGBE driver directory when the config is built-in or modular.

Control flow: Kbuild expands the directory object according to `CONFIG_SXGBE_ETH`; the subdirectory Makefile assembles the concrete module objects.

State and persistence: no runtime state; only Kbuild object selection.

Dependencies and integration: tied to `drivers/net/ethernet/samsung/Kconfig` and the subdirectory `sxgbe/Makefile`.

Risks: none beyond ensuring config and directory names stay aligned. If additional Samsung drivers are added, this file is the inclusion point.

Test signals: built-in and module builds of `CONFIG_SXGBE_ETH`, and no descent when the option is unset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/Makefile

Purpose: defines the object composition for the Samsung SXGBE Ethernet driver.

Important rules: `obj-$(CONFIG_SXGBE_ETH) += samsung-sxgbe.o` creates the final built-in object or module. `samsung-sxgbe-objs` aggregates platform probe, main netdev logic, descriptor ops, DMA ops, MAC core ops, MTL ops, MDIO ops, ethtool ops, and any conditional `samsung-sxgbe-y` additions.

Control flow: Kbuild links the listed objects into one driver image when enabled.

State and persistence: no runtime state; controls link composition and module contents.

Dependencies and integration: depends on source files in the same directory (`sxgbe_platform.o`, `sxgbe_main.o`, `sxgbe_desc.o`, `sxgbe_dma.o`, `sxgbe_core.o`, `sxgbe_mtl.o`, `sxgbe_mdio.o`, `sxgbe_ethtool.o`).

Risks: object order can matter for initcall/link symbol resolution in drivers. Conditional `samsung-sxgbe-y` is available but not populated here, so feature expansion must be kept coherent.

Test signals: module link includes all operation providers; missing-object failures catch filename drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_common.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_common.h

Purpose: central shared contract for the Samsung SXGBE driver. It defines driver constants, hardware capability flags, statistics layout, operation tables, queue state, private device state, and cross-file prototypes.

Important APIs and types: `struct sxgbe_extra_stats` is the ethtool-visible extended counter set updated by descriptor and DMA paths. `struct sxgbe_core_ops`, `struct sxgbe_ops`, `struct sxgbe_dma_ops`, `struct sxgbe_desc_ops`, and `struct sxgbe_mtl_ops` form the hardware abstraction tables. `struct sxgbe_tx_queue` and `struct sxgbe_rx_queue` hold descriptor rings, DMA addresses, skb arrays, queue indices, IRQs, and coalescing state. `struct sxgbe_hw_features` stores decoded hardware capabilities. `struct sxgbe_priv_data` is the main netdev private state and holds queues, sizes, NAPI, mapped registers, hardware ops, PHY/MDIO state, pause/EEE/PTP fields, clock, capabilities, stats, and platform data.

Control flow: platform/main probe code fills `sxgbe_priv_data`, obtains ops via `sxgbe_get_core_ops()`, `sxgbe_get_desc_ops()`, `sxgbe_get_dma_ops()`, and `sxgbe_get_mtl_ops()`, allocates rings according to queue constants, then netdev, DMA, ethtool, MDIO, and PM code share this structure.

State and persistence: all runtime state is in `sxgbe_priv_data` and nested queue/stat structures. It is volatile and tied to net_device lifetime. Persistent externally visible state includes ethtool stats, link settings delegated to PHY, coalesce settings, EEE state, and hardware feature reporting.

Dependencies and integration: relies on Linux net_device, PHY, MII, PTP, clock, timer, and platform data types. It bridges the split source files into one driver by declaring all exported helpers.

Risks: many constants hard-code queue counts, FIFO sizes, register dump sizes, and MTU limits. `NETIF_F_HW_VLAN_ALL` is locally defined and may collide with kernel feature naming over time. Stats use `unsigned long` but ethtool extraction handles only u64 vs u32, so width assumptions matter. Hardware descriptor bitfield layout in related headers is compiler/endianness sensitive.

Test signals: compile with PTP enabled/disabled, probe feature decoding, queue allocation for max TX/RX queues, ethtool stats string/count consistency, EEE state transitions, RX checksum and VLAN feature toggles, and PM suspend/resume declarations under `CONFIG_PM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_core.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_core.c

Purpose: implements SXGBE MAC core operations: core initialization, MAC address programming, TX/RX enable, version/feature reads, speed selection, EEE LPI controls, RX checksum offload, RX queue enable/disable, and MAC interrupt status handling.

Important APIs: `sxgbe_get_core_ops()` returns a static `struct sxgbe_core_ops`. Key callbacks include `core_init`, `host_irq_status`, `set_umac_addr`, `get_umac_addr`, `enable_rx`, `enable_tx`, `get_controller_version`, `get_hw_feature`, `set_speed`, `set_eee_mode`, `reset_eee_mode`, `set_eee_timer`, `set_eee_pls`, `enable_rx_csum`, `disable_rx_csum`, `enable_rxqueue`, and `disable_rxqueue`.

Control flow: `sxgbe_core_init()` sets TX jabber disable and RX jumbo/ACS bits. IRQ status reads `SXGBE_CORE_INT_STATUS_REG` and, for LPI interrupts, reads `SXGBE_CORE_LPI_CTRL_STATUS` to derive entry/exit status flags. MAC address setters split a six-byte address into high/low registers. Enable functions read-modify-write TX/RX config bits. EEE functions set LPI enable/automate bits, PLS, and timers. Feature/version accessors read register offsets.

State and persistence: state is primarily hardware register state under `ioaddr`. No private static mutable state exists.

Dependencies and integration: depends on `sxgbe_reg.h` register offsets/bit masks, Linux MMIO helpers, netdevice/PHY includes, and the operation table consumed by main/probe paths.

Risks: several callbacks are placeholders (`dump_regs`, `pmt`). RX queue enable/disable masks shift by queue number but write unshifted enable/disable values, which should be validated against register layout. Speed setting directly shifts a caller-supplied value. LPI status read clears hardware bits, so callers must account for destructive reads.

Test signals: register write/read traces during probe, MAC address set/get round trips, TX/RX enable toggles, EEE enable/disable/timer/PLS behavior, LPI interrupt counters, feature register decoding, and queue enable across all supported RX queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_desc.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_desc.c

Purpose: provides the SXGBE descriptor operation implementation for normal TX/RX descriptors and TX/RX context descriptors. It prepares descriptors for DMA ownership, packet lengths, checksums, TSO, VLAN tags, timestamps, and decodes RX writeback status into driver statistics and checksum status.

Important APIs: `sxgbe_get_desc_ops()` returns `desc_ops`. TX callbacks initialize, prepare, set owner, close, release, check last segment, read length, set timestamp, and manipulate TX context descriptor MSS/VLAN/timestamp fields. RX callbacks initialize descriptors, set/get owner, enable interrupt-on-completion, get frame length and first/last status, parse RX writeback status, parse RX context status, test timestamp validity, and return timestamp value.

Control flow: transmit setup fills bitfields in `tdes23.tx_rd_des23`; close marks last descriptor and interrupt-on-completion; ownership is handed to hardware by setting `own_bit`. Receive initialization sets ownership to hardware and optional interrupt mode. RX writeback first treats `err_summary` and `err_l2_type` as either L2 error or packet type, updates extended stats, adjusts checksum to `CHECKSUM_NONE` for IP header/payload checksum errors, then records L3/L4 packet type and filter counters. RX context status updates PTP/timestamp counters and timestamp retrieval combines low/high words.

State and persistence: functions mutate descriptor memory passed by queue code and update `struct sxgbe_extra_stats`; no global mutable state.

Dependencies and integration: depends on descriptor layouts in `sxgbe_desc.h`, stats and constants in `sxgbe_common.h`, DMA definitions, net checksum constants, and queue management in main driver code.

Risks: descriptor layouts are C bitfields matching hardware, making compiler packing and endian assumptions critical. `sxgbe_release_tx_desc()` zeroes the whole descriptor, so caller must restore buffer address before reuse. RX status logs invalid types with `pr_err`, which can be noisy on corrupted descriptors. Some status counters have naming inconsistencies (`dvan_ocvlan_icvlan_pkt` vs `dvlan...`) mirrored in ethtool.

Test signals: TX descriptor contents for linear, fragmented, TSO, VLAN, and timestamped packets; ownership transitions; RX error decoding for every `RX_*` status; checksum status on IP errors; PTP context descriptor timestamps; and ethtool stat increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_desc.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_desc.h

Purpose: declares SXGBE DMA descriptor data structures and the descriptor operation table consumed by the main TX/RX paths.

Important APIs and types: `SXGBE_DESC_SIZE_BYTES` is 16. `enum tdes_csum_insertion` defines checksum insertion modes. `struct sxgbe_tx_norm_desc`, `struct sxgbe_rx_norm_desc`, `struct sxgbe_tx_ctxt_desc`, and `struct sxgbe_rx_ctxt_desc` map hardware normal/context descriptor formats. `struct sxgbe_desc_ops` declares all descriptor callbacks implemented in `sxgbe_desc.c`. `sxgbe_get_desc_ops()` returns the provider.

Control flow: queue code allocates rings of these descriptors, fills read-format fields before setting owner bits, and later decodes writeback-format fields after hardware clears ownership. Context descriptors carry TSO, VLAN, and timestamp metadata.

State and persistence: descriptor rings are DMA-visible memory owned by queue structures. Header fields persist only for ring lifetime and are reused per packet.

Dependencies and integration: forward-declares `sxgbe_extra_stats` and integrates with common private queue state, DMA programming, and netdev transmit/receive paths.

Risks: the structs use implementation-defined C bitfield layout for hardware ABI. `u64 buf2_addr:62` and unions spanning read/write formats require exact compiler behavior and correct endian target assumptions. Changes to descriptor size or fields must match hardware and ring-tail programming in DMA code.

Test signals: `sizeof`/layout validation against hardware documentation, descriptor ring DMA tests on target endian/architecture, TX/RX ownership transitions, context descriptor timestamp and TSO behavior, and sparse/compiler warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_dma.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_dma.c

Purpose: implements SXGBE DMA operation callbacks for system bus setup, per-channel descriptor ring programming, TX/RX start/stop, per-channel IRQ enable/disable, DMA interrupt status decoding, RX interrupt watchdog programming, and TSO enablement.

Important APIs: `sxgbe_get_dma_ops()` returns `sxgbe_dma_ops`. `sxgbe_dma_init()` programs AXI undefined burst and burst length map. `sxgbe_dma_channel_init()` writes per-channel control, PBL, TX/RX descriptor base addresses, tail pointers, ring lengths, and interrupt mask. `sxgbe_tx_dma_int_status()` and `sxgbe_rx_dma_int_status()` translate DMA status bits into `enum dma_irq_status` flags and extended stats.

Control flow: probe/open code initializes bus mode, then calls channel init for each active DMA channel. TX and RX start/stop iterate channel counts or target one queue. Interrupt handlers call status helpers, which read the channel status register, classify normal vs abnormal summary, update counters, build action bits such as `handle_tx`, `handle_rx`, `tx_hard_error`, `rx_hard_error`, `tx_bump_tc`, and `rx_bump_tc`, then clear served bits by writing back a mask.

State and persistence: persistent state is hardware DMA registers plus `sxgbe_extra_stats` counters. The file itself has no global mutable state.

Dependencies and integration: depends on `sxgbe_reg.h` for register offsets and bit masks, `sxgbe_desc.h` for descriptor size, `sxgbe_common.h` for stats and return flags, and Linux MMIO/delay/network includes.

Risks: `sxgbe_dma_channel_init()` computes an RX tail pointer but writes it to `SXGBE_DMA_CHA_RXDESC_LADD_REG(cha_num)` rather than a distinct RX tail pointer register, which looks like a functional bug or naming mismatch requiring hardware validation. It assumes upper 32 bits are constant for tail pointers. Status handling uses `if normal else if abnormal`, so simultaneous normal and abnormal bits process only the normal branch. Clearing FBE subcause bits must match hardware write-one-clear semantics.

Test signals: DMA ring base/tail/ring length register programming, TX/RX traffic on all channels, interrupt status paths for normal and abnormal bits, bus error subcause counters, RX watchdog conversion from ethtool coalesce settings, TSO enable per channel, and hardware register traces around RX tail programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_dma.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_dma.h

Purpose: declares the SXGBE DMA operation table and DMA configuration constants used by the main driver and implemented by `sxgbe_dma.c`.

Important APIs: constants include burst-map/PBL shifts and `DEFAULT_DMA_PBL`. `struct sxgbe_dma_ops` contains callbacks for DMA init, channel init, TX/RX start/stop, queue start/stop, IRQ enable/disable, TX/RX interrupt status, RX watchdog programming, and TSO enable. `sxgbe_get_dma_ops()` returns the implementation.

Control flow: probe/open code gets this ops table and calls it to configure DMA hardware, service interrupts, and apply ethtool coalescing or TSO changes.

State and persistence: no state in the header; it defines function-pointer contracts operating on MMIO registers and stats passed by callers.

Dependencies and integration: forward-declares `sxgbe_extra_stats` and uses `dma_addr_t`, `u32`, and `u8` kernel types. It is included by DMA implementation, descriptor implementation, ethtool, and main paths that need DMA ops.

Risks: the `cha_init` parameter name has a typo (`t_rzie`) that does not affect ABI but can confuse users. The closing include guard comment says `__SXGBE_CORE_H__`, inconsistent with the actual guard. Contract changes must stay synchronized with `sxgbe_dma.c` and `struct sxgbe_ops`.

Test signals: compile-time function pointer type matching, probe calling every required op, and warnings from header guard or prototype drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_ethtool.c

Purpose: exposes SXGBE driver state and controls through ethtool: driver info, message level, extended stats, channel counts, RX interrupt coalescing, RSS hash field selection, register dump, EEE, and PHY link settings.

Important APIs: `sxgbe_set_ethtool_ops()` assigns a static `ethtool_ops`. `sxgbe_gstrings_stats[]` maps `sxgbe_extra_stats` fields to ethtool string names and offsets. `sxgbe_get_eee()`/`sxgbe_set_eee()` bridge MAC EEE state with PHY EEE helpers. `sxgbe_get_coalesce()`/`sxgbe_set_coalesce()` convert RX watchdog ticks to/from usecs using the SXGBE clock. `sxgbe_get_rxfh_fields()`/`sxgbe_set_rxfh_fields()` report and configure RSS hash field support. `sxgbe_get_regs()` copies MAC, MTL, and DMA register ranges into a fixed register dump buffer.

Control flow: ethtool requests read `sxgbe_priv_data` via `netdev_priv()`. Stats optionally refresh EEE wake error count from PHY and then copy fields by offset. Coalesce rejects zero or out-of-range RX usecs and requires `priv->use_riwt` before programming DMA watchdog. RSS setters validate flow type and requested fields before OR-ing control bits into `SXGBE_CORE_RSS_CTL_REG`. EEE set disables MAC EEE or re-runs `sxgbe_eee_init()` before updating `tx_lpi_timer` and calling PHY set.

State and persistence: modifies `priv->msg_enable`, `priv->eee_enabled`, `priv->tx_lpi_timer`, `priv->rx_riwt`, hardware RSS and watchdog registers, and PHY EEE settings. Stats expose volatile counters.

Dependencies and integration: depends on netdevice ethtool APIs, PHY ethtool helpers, clocks, PTP headers, DMA ops, core register definitions, and `sxgbe_common.h` private state.

Risks: stats extraction treats non-u64 fields as u32 even though the struct uses `unsigned long`, which can truncate on 64-bit if `sizeof(unsigned long) != sizeof(u32)` and not equal u64 in assumptions. RSS setter ORs new mode bits with existing register contents and does not clear old flow-type bits. Register dump uses a fixed `REG_SPACE_SIZE` and `BUG_ON` if ranges exceed it. EEE set changes `priv->eee_enabled` before PHY set, so PHY failure may leave partial state.

Test signals: `ethtool -S`, stats string/count matching, EEE enable/disable with PHY support absent/present, coalesce boundary values and clock rate zero, RSS hash field validation per flow type, register dump length and contents, and PHY link ksettings passthrough.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_ethtool.c -->
