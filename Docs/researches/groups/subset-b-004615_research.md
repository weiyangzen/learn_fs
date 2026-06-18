# Research: subset-b-004615

This grouped report covers the requested RMNET, RDC, and Realtek Ethernet driver files. Each section is bounded by the exact reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_handlers.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_handlers.c

Purpose: Implements the RMNET ingress and egress packet handlers that sit between a real lower net_device and virtual RMNET devices. It classifies MAP command/data frames, selects logical endpoints by mux id, bridges frames when configured, and wraps outbound virtual-device traffic in MAP headers.

Important APIs and functions: `rmnet_rx_handler()` is the lower-device RX handler. `rmnet_egress_handler()` is called by virtual netdev TX. `rmnet_map_ingress_handler()` handles Ethernet headroom correction and optional deaggregation. `__rmnet_map_ingress_handler()` processes one MAP frame. `rmnet_map_egress_handler()` builds MAP plus checksum headers and may aggregate TX. `rmnet_deliver_skb()` finalizes skb headers, updates VND RX stats through `rmnet_vnd_rx_fixup()`, and feeds GRO cells.

Control flow: RX linearizes the skb, ignores loopback packets, gets the port with RCU lookup, then dispatches by `rmnet_mode`. VND mode parses MAP, validates mux endpoint, strips MAP/checksum headers, sets `skb->protocol`, trims padding, and delivers to the virtual egress device. Bridge mode pushes an existing MAC header and transmits to `bridge_ep`. TX moves `skb->dev` from virtual to real device, uses the virtual private mux id, invokes MAP egress formatting, records virtual TX stats, and queues to the real device.

State and persistence: Persistent state is in `struct rmnet_port`, endpoint tables, `struct rmnet_priv`, per-cpu VND stats, and aggregation fields owned by `rmnet_map_data.c`. The file mutates skb metadata and drops packets on invalid mux ids, missing endpoints, checksum parse errors, or headroom allocation failure.

Dependencies and integration: Depends on `rmnet_config` for port/endpoint lookup and flags, `rmnet_map` for MAP protocol helpers, `rmnet_vnd` for stats/fixups, Linux RX handler API, GRO cells, SKB helpers, and `dev_queue_xmit()`.

Risks and test signals: Key risks are malformed MAP lengths, MAPv5 next-header expectations, aggregation error returns, and bridge-mode header handling. Tests should exercise mux routing, bad mux drops, command packets with/without command flag enablement, CKSUMV4 and CKSUMV5 paths, deaggregation, aggregation enabled vs disabled, bridge mode, and stat/drop counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_handlers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_handlers.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_handlers.h

Purpose: Declares the two RMNET packet-handler entry points shared between virtual device and configuration code.

Important APIs: `void rmnet_egress_handler(struct sk_buff *skb)` accepts an skb transmitted on an RMNET virtual net_device and rewrites it for the real lower device. `rx_handler_result_t rmnet_rx_handler(struct sk_buff **pskb)` is registered as an RX handler on the real device and consumes or passes ingress frames.

Control flow and integration: This header is included by `rmnet_vnd.c` so VND TX can call the egress path, and by configuration or lower-device setup code that installs the RX handler. It includes `rmnet_config.h` for shared type visibility.

State and persistence: No state is defined here. It exposes functions that operate on SKBs, per-device private state, and RMNET ports maintained elsewhere.

Risks and test signals: API stability matters because these functions are boundary points between RMNET net_device operations and lower-device RX handling. Build coverage should ensure prototypes remain synchronized with implementation, and runtime tests should verify RX handler registration and VND TX call paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_handlers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_map.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_map.h

Purpose: Defines RMNET MAP command metadata and declares MAP data, checksum, deaggregation, command, and uplink aggregation helpers.

Important APIs and types: `struct rmnet_map_control_command` models MAP command payloads after the MAP header, including command name/type, transaction id, and flow-control fields. `enum rmnet_map_commands` names supported commands, mainly flow enable/disable. Command response constants define ACK, unsupported, and invalid types. Function declarations cover `rmnet_map_deaggregate()`, `rmnet_map_add_map_header()`, `rmnet_map_command()`, downlink and uplink checksum helpers, MAPv5 next-header processing, and TX aggregation lifecycle/configuration.

Control flow and integration: `rmnet_handlers.c` calls the ingress, egress, checksum, deaggregation, and aggregation helpers declared here. `rmnet_map_command.c` consumes the control command structure. `rmnet_map_data.c` implements data-plane helpers and aggregation configuration.

State and persistence: This header defines no global state. It standardizes command layout and helper contracts for state stored in `struct rmnet_port`, `struct rmnet_priv`, and SKBs.

Risks and test signals: Bitfield layout and alignment of `rmnet_map_control_command` are protocol-sensitive. Tests should cover command parsing, mux id routing, checksum offload variants, and padding/header length invariants. Build tests should catch prototype drift across MAP files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_map_command.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_map_command.c

Purpose: Handles MAP command frames, currently focused on modem-driven flow-control enable/disable commands for RMNET virtual devices.

Important APIs and functions: `rmnet_map_command()` is the public command dispatcher. `rmnet_map_do_flow_control()` validates mux id, resolves the endpoint, and calls `rmnet_vnd_do_flow_control()` on the virtual net_device. `rmnet_map_send_ack()` mutates the command type in-place and sends an ACK frame back through the real device's `ndo_start_xmit()`.

Control flow: The ingress handler routes command frames here only when ingress MAP commands are enabled. Command data follows the MAP header. Flow enable and disable commands call the VND queue wake/stop helper. Unsupported commands free the skb and report unsupported. Successful flow-control commands return ACK and reuse the original skb to send an acknowledgement. If CKSUMV4 ingress is enabled, ACK generation trims the downlink checksum trailer before transmit.

State and persistence: The command path changes the target VND TX queue state and mutates the command `cmd_type` for ACK. It does not store command history. It frees SKBs for invalid mux ids, missing endpoints, VND flow-control errors, or unsupported command names.

Dependencies and integration: Depends on endpoint lookup from `rmnet_config`, MAP structures from `rmnet_map.h`, and VND queue control from `rmnet_vnd.c`. ACK transmission directly calls the lower device `ndo_start_xmit()` under `netif_tx_lock()`.

Risks and test signals: Risks include short command frames not explicitly length-checked here, assumptions about skb linearity from the caller, and ACK reuse of the received skb. Tests should cover supported and unsupported command ids, invalid mux ids, endpoint absence, CKSUMV4 trailer trimming, and queue stop/wake effects on the VND.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_map_command.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_map_data.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_map_data.c

Purpose: Implements RMNET MAP data-plane mechanics: MAP header insertion, ingress deaggregation, downlink checksum validation, uplink checksum metadata generation, MAPv5 next-header processing, and uplink TX aggregation.

Important APIs and functions: `rmnet_map_add_map_header()` pushes MAP headers and optional padding. `rmnet_map_deaggregate()` extracts one MAP packet from an aggregate skb. `rmnet_map_checksum_downlink_packet()` validates CKSUMV4 trailers. `rmnet_map_checksum_uplink_packet()` dispatches CKSUMV4 or CKSUMV5 metadata generation. `rmnet_map_process_next_hdr_packet()` handles MAPv5 checksum headers. `rmnet_map_tx_aggregate()`, `rmnet_map_tx_aggregate_init()`, `rmnet_map_update_ul_agg_config()`, and `rmnet_map_tx_aggregate_exit()` manage uplink aggregation.

Control flow: Downlink CKSUMV4 validates IPv4 header checksum, rejects fragments, supports TCP/UDP, handles optional IPv4 UDP checksum zero, and compares trailer checksum to pseudo-header complement. IPv6 validation is compiled behind `CONFIG_IPV6` and rejects extension-header cases by only looking at `nexthdr`. Uplink CKSUMV4 pushes a UL checksum header for CHECKSUM_PARTIAL packets and complements transport checksum fields; otherwise it zeros the metadata and counts software checksum. MAPv5 pushes or consumes a next header and uses a validity bit to set `CHECKSUM_UNNECESSARY`. Aggregation either sends immediately, copies a first skb into a larger aggregate buffer, appends later skbs via frag_list, and flushes on count, byte, or timer thresholds.

State and persistence: Stats are updated in `rmnet_priv->stats`. Aggregation state persists in `struct rmnet_port`: `skbagg_head`, tail, count, state, time stamps, hrtimer, work item, spinlock, and `egress_agg_params`. Exit cancels timer/work and frees a pending aggregate.

Dependencies and integration: Uses SKB DMA/linearization-independent helpers, checksum helpers from IPv4/IPv6 stacks, hrtimers/workqueues, `rmnet_vnd_tx_fixup_len()` through the egress caller, and port configuration from ethtool coalescing.

Risks and test signals: High-risk areas are packet length/padding math, MAPv5 invalid next-header behavior, IPv6 extension-header limitations, aggregation ownership of SKBs, timer/work races, and linearization failure handling. Tests should include IPv4/IPv6 TCP/UDP checksum pass/fail, fragments, unsupported protocols, aggregate boundary sizes, sparse traffic bypass, timer flush, count flush, and teardown with pending aggregate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_map_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_private.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_private.h

Purpose: Holds small private RMNET constants shared by RMNET implementation files.

Important definitions: `RMNET_MAX_PACKET_SIZE`, `RMNET_DFLT_PACKET_SIZE`, `RMNET_NEEDED_HEADROOM`, and `RMNET_TX_QUEUE_LEN` define virtual device sizing defaults. `RMNET_EPMODE_VND` and `RMNET_EPMODE_BRIDGE` select whether ingress frames are delivered to a virtual RMNET device or forwarded directly to a bridge endpoint.

Control flow and integration: The mode constants are consumed by `rmnet_handlers.c`. MTU, headroom, and queue length constants are consumed by `rmnet_vnd.c` during device setup and MTU validation.

State and persistence: No runtime state is stored here. The constants shape persistent net_device configuration once VND devices are created.

Risks and test signals: Changes affect device MTU bounds, headroom guarantees for MAP/checksum headers, and handler mode dispatch. Build tests plus create/change-MTU/link tests should verify constants remain compatible with MAP header growth and real-device MTU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_vnd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_vnd.c

Purpose: Implements RMNET virtual network device behavior: TX entry, RX/TX statistics, MTU rules, ethtool stats and TX aggregation coalescing, net_device setup, link creation/deletion, flow control, and MTU synchronization with the real device.

Important APIs and functions: Public functions include `rmnet_vnd_setup()`, `rmnet_vnd_newlink()`, `rmnet_vnd_dellink()`, `rmnet_vnd_do_flow_control()`, `rmnet_vnd_rx_fixup()`, `rmnet_vnd_tx_fixup_len()`, `rmnet_vnd_validate_real_dev_mtu()`, and `rmnet_vnd_update_dev_mtu()`. Netdev ops cover `ndo_start_xmit`, `ndo_change_mtu`, `ndo_get_iflink`, bridge slave add/del, init/uninit, and stats64. Ettool ops expose checksum counters and TX aggregation coalescing.

Control flow: Device setup creates a raw-IP net_device with no header ops, random hardware/permanent addresses, fixed headroom, and lltx. Init allocates per-cpu stats and GRO cells; uninit frees them. TX calls `rmnet_egress_handler()` when a real device is attached, otherwise drops. Newlink validates mux uniqueness, enables checksum/SG features, sets private real_dev and mux id, derives MTU from real MTU minus MAP headroom, registers the netdev, and stores the endpoint. Dellink clears endpoint state. Flow control stops or wakes the VND TX queue.

State and persistence: `struct rmnet_priv` stores real device, mux id, per-cpu stats, GRO cells, and checksum stat counters. `struct rmnet_port` stores endpoints and aggregation parameters. Endpoint creation increments `nr_rmnet_devs`, deletion decrements it.

Dependencies and integration: Integrates with rtnetlink link ops, RMNET config endpoint lookup, MAP aggregation config, Linux ethtool coalescing, GRO cells, per-cpu u64 stats, and bridge operations from config code.

Risks and test signals: Risks include MTU/headroom miscalculation, per-cpu stat lifetime, coalescing values that permit zero-byte aggregation size, feature toggles vs checksum path assumptions, and endpoint cleanup ordering. Tests should create/delete VND links, duplicate mux ids, transmit without real_dev, flow-control queue state, ethtool stats/coalescing, MTU shrink propagation, and GRO receive stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_vnd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_vnd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_vnd.h

Purpose: Declares the virtual RMNET net_device API used by handlers, MAP command processing, and configuration code.

Important APIs: Creation and deletion are exposed through `rmnet_vnd_newlink()` and `rmnet_vnd_dellink()`. Data path helpers include RX/TX stat fixups and flow control. Device lifecycle/configuration helpers include `rmnet_vnd_setup()`, `rmnet_vnd_validate_real_dev_mtu()`, and `rmnet_vnd_update_dev_mtu()`.

Control flow and integration: `rmnet_map_command.c` uses `rmnet_vnd_do_flow_control()`. `rmnet_handlers.c` uses RX/TX fixups. RMNET rtnetlink/config code calls setup and link lifecycle helpers.

State and persistence: The header declares functions that mutate endpoint tables, virtual net_device private fields, queue state, and per-cpu stats, but defines no state itself.

Risks and test signals: Prototype drift can break boundaries between config and data path. Compile coverage should include RMNET as module/built-in, and runtime tests should verify callers observe correct endpoint and MTU behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_vnd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rdc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/rdc/Kconfig

Purpose: Defines kernel configuration entries for RDC Ethernet drivers.

Important entries: `NET_VENDOR_RDC` is a vendor menu gate, defaulting to yes and depending on PCI. `R6040` is a tristate driver option for RDC R6040 Fast Ethernet MACs, depends on PCI, and selects CRC32, MII, and PHYLIB.

Control flow and integration: The Kconfig symbol `CONFIG_R6040` controls compilation in the sibling Makefile. Dependency selection ensures the r6040 driver has CRC hashing, legacy MII helpers, and PHY library support available.

State and persistence: No runtime state. Configuration persists in the kernel build config and determines whether `r6040.o` is built in, modular, or omitted.

Risks and test signals: Risks are missing dependencies if driver code gains new subsystem use, or accidental visibility without PCI. Test signals include allmodconfig/build coverage and verifying `CONFIG_R6040=m` produces module `r6040`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rdc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rdc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/rdc/Makefile

Purpose: Connects RDC Kconfig symbols to build outputs.

Important rule: `obj-$(CONFIG_R6040) += r6040.o` builds the RDC R6040 driver when its config is enabled.

Control flow and integration: The parent networking Makefile descends into this vendor directory; this Makefile contributes `r6040.o` according to `CONFIG_R6040`.

State and persistence: No runtime state. Build output depends on the config value.

Risks and test signals: The main risk is stale object naming if the source file is renamed or split. Build tests with `CONFIG_R6040=y` and `m` validate the mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rdc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rdc/r6040.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/rdc/r6040.c

Purpose: Implements a PCI NAPI Fast Ethernet driver for RDC R6040 MACs, including descriptor-ring DMA, interrupt handling, PHYLIB integration, multicast filtering, ethtool link settings, and PCI probe/remove.

Important APIs and types: `struct r6040_descriptor` describes 32-byte hardware descriptors. `struct r6040_private` stores PCI device, IO base, RX/TX rings and DMA addresses, descriptor cursors, NAPI object, PHY bus, link state, and lock. Netdev ops include open, stop, start_xmit, get_stats, set_rx_mode, ioctl, tx_timeout, and optional poll_controller. PCI entry points are `r6040_init_one()` and `r6040_remove_one()`.

Control flow: Probe enables PCI, configures 32-bit DMA masks, maps BAR0, initializes PHY status-change hardware if needed, reads or randomizes MAC address, allocates a netdev and MII bus, registers the bus, connects first PHY, and registers the netdev. Open requests IRQ, allocates coherent RX/TX descriptor rings, allocates RX SKBs, initializes MAC registers, starts PHY/NAPI/queue. Interrupts mask MAC IRQs, record RX errors, and schedule NAPI. Poll completes TX descriptors then receives packets until budget, re-enabling interrupts on completion. TX pads short packets, maps skb data into the next descriptor, marks MAC ownership, triggers transmit, and stops queue when descriptors run out. Close stops PHY/NAPI/queue, resets MAC, frees buffers, IRQ, and rings.

State and persistence: Runtime state is in descriptor rings, skb pointers, DMA mappings, `tx_free_desc`, MAC control shadow `mcr0`, and PHY link/duplex shadows. Hardware counters are folded into `dev->stats`.

Dependencies and integration: Uses PCI, coherent/single DMA APIs, NAPI, PHYLIB/MDIO bus, MII ethtool helpers, CRC32 multicast hashing, and net_device core.

Risks and test signals: Risks include DMA mapping error checks missing in RX/TX allocation paths, descriptor ownership races, reset loop semantics, multicast register programming, and resource unwind correctness. Tests should cover probe failure unwinds, open/close cycles, TX timeout recovery, RX error accounting, NAPI budget behavior, PHY link changes, multicast modes, and suspend-free remove path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rdc/r6040.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/8139cp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/8139cp.c

Purpose: Implements the Realtek RTL-8139C+ PCI Fast Ethernet driver using C+ descriptor rings, NAPI RX, scatter/gather TX, checksum/VLAN/TSO features, WOL, EEPROM access, ethtool operations, and PCI power management.

Important APIs and types: `struct cp_desc` is the C+ RX/TX descriptor. `struct cp_private` stores MMIO registers, locks, NAPI, rings, skb arrays, descriptor indices, C+ command shadow, MII state, WOL flag, and stats. Data path functions include `cp_rx_poll()`, `cp_interrupt()`, `cp_tx()`, and `cp_start_xmit()`. Lifecycle functions include `cp_init_one()`, `cp_open()`, `cp_close()`, `cp_remove_one()`, suspend/resume, ring allocation/refill/cleanup, and hardware reset/start/stop.

Control flow: Probe rejects non-C+ old revisions, allocates netdev, enables PCI/MWI, maps MMIO BAR1, chooses 64-bit or 32-bit DMA, reads MAC from EEPROM, enables netdev features, registers NAPI and netdev. Open allocates coherent ring memory, enables NAPI, initializes hardware, requests IRQ, enables interrupts, checks media, and starts queue. RX interrupt masks RX and schedules NAPI; NAPI consumes descriptors, replaces SKBs, handles checksum/VLAN status, submits GRO packets, and re-arms interrupts. TX maps linear or fragmented skb segments, fills descriptors with ownership bits and optional TSO/checksum/VLAN flags, updates queue accounting, and rings `TxPoll`; completion unmaps descriptors, frees SKBs on `LastFrag`, updates stats, and wakes queue. Close disables NAPI/queue/hardware, frees IRQ and rings.

State and persistence: Persistent runtime state includes descriptor ownership, RX/TX cursors, skb arrays, DMA addresses, `cp->cpcmd`, `rx_config`, WOL enabled flag, MII state, and software stats. EEPROM read/write routines persist board data when invoked by ethtool with the magic value.

Dependencies and integration: Uses PCI, DMA, NAPI/GRO, MII helpers, ethtool, VLAN accel, netdev feature negotiation, firmware-independent EEPROM bit banging, and SIMPLE_DEV_PM_OPS.

Risks and test signals: Risks include multi-fragment DMA unwind correctness, descriptor barriers, TSO MSS limit handling, RX refill mapping failures, EEPROM write safety, PM resume with depleted RX ring, and hardware reset timeouts. Tests should cover probe rejection vs `8139too`, open/close, RX checksum/VLAN, fragmented TX, TSO feature check, WOL ethtool, EEPROM get/set, MTU changes while up, TX timeout recovery, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/8139cp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/8139too.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/8139too.c

Purpose: Implements the legacy Realtek RTL-8129/8130/8139 PCI Fast Ethernet driver using a contiguous RX DMA ring, four TX bounce buffers, NAPI receive processing, MII/media management, optional Twister tuning, WOL, ethtool, and PCI PM.

Important APIs and types: `struct rtl8139_private` stores MMIO/PIO mapping, PCI device, NAPI, RX ring, TX buffers, DMA addresses, indices, MII state, chip id, locks, stats, delayed work, and Twister state. Key functions include `rtl8139_init_one()`, `rtl8139_init_board()`, `rtl8139_open()`, `rtl8139_hw_start()`, `rtl8139_start_xmit()`, `rtl8139_interrupt()`, `rtl8139_poll()`, `rtl8139_rx()`, `rtl8139_tx_interrupt()`, `rtl8139_close()`, and suspend/resume.

Control flow: Probe rejects enhanced 8139C+ revisions so `8139cp` can bind them, handles a quirk that forces PIO on OQO Model 2, maps IO or MMIO, identifies chipset revision, configures wake/low-power bits, reads MAC from EEPROM, registers netdev/NAPI, configures MII options, and optionally halts chip clock. Open requests IRQ, allocates coherent RX and TX bounce buffers, enables NAPI, initializes rings and hardware, starts queue, and starts delayed media/Twister work when needed. TX copies and checksums each skb into one of four bounce buffers, writes `TxStatus` to trigger DMA, and stops queue when all descriptors are outstanding. Interrupts acknowledge non-RX causes, schedule NAPI for RX, process abnormal events, and reap TX completions. RX reads packet status/length from the ring, handles FIFO-copy-in-progress, validates size/status, optionally accepts errored packets under RXALL, copies payload into a new skb, updates stats, advances `RxBufPtr`, and acks RX sources.

State and persistence: Runtime state includes `cur_rx`, `cur_tx`, `dirty_tx`, RX/TX coherent buffers, media/Twister delayed-work state, MII force/full-duplex settings, and hardware register shadows. WOL configuration persists in device config registers across suspend states. Stats use `u64_stats_sync` for packet/byte counters plus legacy `dev->stats`.

Dependencies and integration: Uses PCI resource mapping, DMA coherent buffers, NAPI, generic MII helpers, ethtool, CRC multicast hash filtering, delayed work under RTNL, and optional Kconfig branches for PIO, 8129 external MII, old RX reset, and Twister tuning.

Risks and test signals: Risks include RX ring wrap/corruption recovery, copied TX buffer lifetime, delayed-work and close/remove ordering, PIO vs MMIO differences, undocumented Twister tuning, WOL bit semantics, and lock ordering across timeout recovery. Tests should cover old vs C+ probe split, MMIO and PIO mapping, RX ring wrap, RXALL/RXFCS, TX timeout delayed reset, multicast modes, WOL, suspend/resume, external MII when enabled, and close/remove with scheduled work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/8139too.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/Kconfig

Purpose: Defines configuration options for Realtek Ethernet drivers in this vendor directory.

Important entries: `NET_VENDOR_REALTEK` gates the vendor menu and depends on PCI. `8139CP` enables RTL-8139C+ support and selects CRC32/MII. `8139TOO` enables older RTL-8129/8130/8139 support and selects CRC32/MII. Associated booleans configure PIO, Twister tuning, older 8129/8130 support, and old RX reset behavior. `R8169` enables RTL8169/8168/8101/8125 and selects firmware loading, CRC32, PHYLIB, and REALTEK_PHY. `R8169_LEDS` gates optional LED class support. `RTASE` enables automotive switch PCIe support with CRC32 and PAGE_POOL.

Control flow and integration: Symbols drive object selection in the Makefile and compile-time branches inside `8139too.c` and `r8169_leds.c`. Dependency expressions prevent unsupported combinations such as built-in R8169 with modular LED class.

State and persistence: No runtime state. Kernel `.config` persists these choices and changes compiled code shape.

Risks and test signals: Risks include incorrect defaults, missing selects when source dependencies change, and option combinations that leave unresolved symbols. Test signals include randconfig/allmodconfig builds, `8139TOO_PIO` and `8139TOO_8129` variant builds, and R8169 LED modularity combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/Makefile

Purpose: Maps Realtek Kconfig symbols to driver objects and r8169 composite object parts.

Important rules: `8139cp.o` and `8139too.o` build from their respective config symbols. `r8169-y` always includes `r8169_main.o`, `r8169_firmware.o`, and `r8169_phy_config.o`; `r8169-$(CONFIG_R8169_LEDS)` conditionally adds LED support. `obj-$(CONFIG_R8169)` builds the composite `r8169.o`. `obj-$(CONFIG_RTASE)` descends into `rtase/`.

Control flow and integration: This file lets Kbuild combine multi-object r8169 pieces while keeping optional LED support controlled by config.

State and persistence: No runtime state. Build output reflects selected Kconfig symbols.

Risks and test signals: Risks are missing object pieces after source refactors or optional object linkage mismatches. Build tests should cover each driver as built-in/module and R8169 with and without LED support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169.h

Purpose: Provides shared declarations for the Realtek r8169 family driver pieces, including MAC version identifiers, firmware/PHY hooks, and optional LED-control hooks.

Important APIs and types: `enum mac_version` enumerates supported RTL_GIGA_MAC_VER values and records removed/merged versions in comments. Forward declarations cover `struct rtl8169_private` and `struct r8169_led_classdev`. Functions include firmware application, PHY/efuse helpers, hardware PHY configuration, LED naming, LED mode get/set helpers, LED initialization for RTL8168/RTL8125, and LED removal.

Control flow and integration: `r8169_main.c` and PHY config code use the version enum to select hardware programming. `r8169_firmware.c` and `r8169_phy_config.c` share private hooks through this header. `r8169_leds.c` implements LED class helpers declared here, and the Makefile includes it only under `CONFIG_R8169_LEDS`.

State and persistence: No state is defined here, but the enum and prototypes shape how `rtl8169_private` hardware state is interpreted by other compilation units.

Risks and test signals: Version enum ordering is ABI-internal but behavior-critical. Risks include mismatched version dispatch, missing stubs when LED config changes, and prototype drift. Test signals include r8169 builds with LED enabled/disabled and runtime coverage across representative MAC versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_firmware.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_firmware.c

Purpose: Loads, validates, and executes Realtek r8169 PHY firmware scripts encoded as 32-bit opcodes.

Important APIs and functions: `rtl_fw_request_firmware()` requests firmware by name and validates format and opcode ranges. `rtl_fw_write_firmware()` interprets opcodes against PHY or MAC MCU read/write callbacks. `rtl_fw_release_firmware()` releases the firmware. Internal validators are `rtl_fw_format_ok()` and `rtl_fw_data_ok()`.

Control flow: Format validation supports a headered format with zero magic, checksum over the whole file, version string, start offset, and opcode count, plus a raw opcode format used when magic is nonzero. Data validation scans all opcodes, verifies branch/skip targets remain in range, validates MDIO selector values, and rejects unknown opcodes. Execution maintains `predata`, `count`, active read/write callback pair, and an instruction index. Opcodes read, OR/AND previous data, branch backward, switch MDIO target, clear read count, write literal or previous values, conditionally skip, unconditionally skip, and delay in milliseconds.

State and persistence: Firmware data remains in `rtl_fw->fw`, parsed action pointer/size, and version string until release. Execution writes hardware registers through callbacks but does not persist interpreter state after completion.

Dependencies and integration: Uses Linux firmware loader, endian helpers, device logging, and callbacks supplied by r8169 main/PHY code. It is built into the composite r8169 object.

Risks and test signals: Risks include malformed firmware bounds, checksum/header interpretation, backward branch loops, hardware callback side effects, and version string truncation. Tests should cover missing firmware warnings, headered/raw valid firmware, invalid opcodes, out-of-range skip/branch, MDIO selector validation, and interpreter callback sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_firmware.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_firmware.h

Purpose: Declares the r8169 firmware interpreter data structures and public firmware lifecycle/execution functions.

Important APIs and types: `rtl_fw_write_t` and `rtl_fw_read_t` abstract register access callbacks. `RTL_VER_SIZE` bounds firmware version strings. `struct rtl_fw` stores PHY and MAC MCU callbacks, firmware pointer/name/device, parsed version, and `rtl_fw_phy_action` opcode pointer/size.

Control flow and integration: r8169 hardware setup fills `struct rtl_fw`, calls request, optionally writes firmware, then releases it. The function-pointer design lets the interpreter switch between PHY and MAC MCU register spaces.

State and persistence: Holds firmware object lifetime state and parsed action metadata. Hardware writes caused by execution persist in device registers.

Risks and test signals: Risks include uninitialized callbacks, lifetime misuse after release, and version buffer assumptions. Compile tests validate declarations, while runtime tests should exercise request/write/release order and failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_leds.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_leds.c

Purpose: Provides optional LED class integration for Realtek r8169-family NIC LEDs using the kernel netdev LED trigger.

Important APIs and types: `struct r8169_led_classdev` wraps `struct led_classdev`, net_device pointer, and LED index. Public functions initialize RTL8168 or RTL8125 LED arrays and remove them. Hardware-control callbacks implement trigger validation, set, get, and device lookup for both RTL8168 and RTL8125 families.

Control flow: Initialization allocates an array with a sentinel, fills each LED classdev with a generated name from `r8169_get_led_name()`, sets `hw_control_trigger` to `netdev`, retains LED state at shutdown, installs callbacks, and registers with the net_device parent. Validation rejects half/full-duplex trigger flags and requires RX/TX activity flags to be both set or both clear. Set callbacks translate netdev trigger flags to chip-specific LED mode bits. Get callbacks read current hardware mode and translate bits back to trigger flags; RTL8168 also disables unsupported OPTION2 mode if observed. Removal iterates until the sentinel `ndev` is null, unregisters LEDs, and frees memory.

State and persistence: LED state is represented by chip LED mode registers accessed through r8169 main callbacks. Allocated LED classdev arrays persist while the net_device is alive. `LED_RETAIN_AT_SHUTDOWN` asks LED core to preserve state.

Dependencies and integration: Depends on `CONFIG_R8169_LEDS`, LED class, netdev LED trigger constants, and r8169 hardware helper callbacks for mode read/write.

Risks and test signals: Risks include ignored registration failures leaving partially registered arrays, stack-allocated LED name buffers assigned to `led_cdev->name`, unsupported trigger combinations, and family-specific bit mismatches. Tests should cover init/remove, trigger set/get for each supported speed/activity combination, unsupported duplex flags, OPTION2 clearing, partial registration failures, and R8169 builds without LED support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_leds.c -->
