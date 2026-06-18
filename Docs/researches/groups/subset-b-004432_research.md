# subset-b-004432 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_enet.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_enet.c

## Purpose
This file is the main Linux netdev and PCI client implementation for the HiSilicon HNS3 Ethernet driver. It registers the `hns3` PCI driver and the KNIC `hnae3_client`, allocates and registers `net_device` instances, owns TX/RX descriptor rings, IRQ vectors, NAPI polling, feature negotiation, reset notifications, SR-IOV entry points, PM/PCI error recovery hooks, and the fast-path packet transmit/receive logic. Hardware-specific policy remains behind `struct hnae3_ae_ops`; this file is the generic NIC-side adapter between the Linux networking stack and the HNS3 AE hardware layer.

## Important APIs, Types, and Functions
- PCI/module entry points include `hns3_probe()`, `hns3_remove()`, `hns3_shutdown()`, `hns3_suspend()`, `hns3_resume()`, PCI error handlers, `hns3_init_module()`, and `hns3_exit_module()`.
- Netdev lifecycle callbacks are collected in `hns3_nic_netdev_ops`: open/stop, xmit, timeout, MTU, MAC address, ioctl, feature changes, stats, TC offload, RX mode, VLAN filter, VF configuration, queue selection, and hardware timestamping.
- `hns3_client_init()` and `hns3_client_uninit()` are the HNAE3 client lifecycle hooks that allocate the netdev, initialize MAC/features/rings/vectors/IRQ/PHY/debugfs, register the netdev, and tear all of it down.
- Ring and vector setup is centered on `hns3_get_ring_config()`, `hns3_nic_alloc_vector_data()`, `hns3_nic_init_vector_data()`, `hns3_init_all_ring()`, `hns3_init_ring_hw()`, and the inverse uninit/dealloc paths.
- TX fast path functions include `hns3_nic_net_xmit()`, `hns3_nic_maybe_stop_tx()`, `hns3_fill_skb_desc()`, `hns3_handle_csum_partial()`, `hns3_handle_desc_filling()`, `hns3_handle_tx_bounce()`, `hns3_handle_tx_sgl()`, and `hns3_tx_doorbell()`.
- RX fast path functions include `hns3_clean_rx_ring()`, `hns3_handle_rx_bd()`, `hns3_alloc_skb()`, `hns3_add_frag()`, `hns3_handle_bdinfo()`, `hns3_rx_checksum()`, `hns3_gro_complete()`, `hns3_handle_rx_vlan_tag()`, and `hns3_set_rx_skb_rss_type()`.
- Interrupt and NAPI paths include `hns3_irq_handle()`, `hns3_nic_common_poll()`, vector masking, IRQ enable/disable, dynamic interrupt moderation, and DIM work handlers.
- Reset and reconfiguration entry points include `hns3_reset_notify()`, `hns3_nic_reset_all_ring()`, `hns3_set_channels()`, `hns3_external_lb_prepare()`, and `hns3_external_lb_restore()`.

## Control Flow
Module load registers debugfs, the HNAE3 KNIC client, and then the PCI driver. PCI probe allocates `struct hnae3_ae_dev`, stores it in PCI driver data, and registers it with HNAE3. The AE layer later calls `hns3_client_init()`, which allocates an `alloc_etherdev_mq()` netdev sized to the available TQPs, initializes `struct hns3_nic_priv`, fetches or generates a MAC address, sets feature flags, installs netdev and ethtool ops, allocates ring metadata, allocates IRQ vectors, maps rings to vectors, allocates descriptor memory and RX buffers, initializes CQ period mode, connects PHY, initializes IRQs, starts the hardware client, initializes debugfs/DCB, marks state initialized, and registers the netdev.

Opening the interface first rejects concurrent reset, sets real TX/RX queue counts and TC queue layout, resets all rings through the AE layer, clears the DOWN bit, enables NAPI/IRQs/vector masks/TQPs, starts the AE device, programs priority-to-TC maps, enables AE timer tasks, and configures XPS. Stopping the interface sets DOWN, disables firmware timer work, drops carrier, disables TX queues, disables TQPs/IRQs/NAPI, stops the AE device, clears ring contents when not inside reset, and resets netdev TX queues.

TX begins in `hns3_nic_net_xmit()`: short frames are padded, descriptor budget is calculated including GSO and fraglist constraints, the queue may be stopped if there are not enough descriptors, VLAN/checksum/TSO metadata is encoded into the first descriptor, and payload buffers are mapped either directly, through a TX spare bounce buffer, or via a TX spare scatterlist table. The final descriptor is marked FE, optional TX timestamping is requested, BQL is updated, and a doorbell is sent either as TX push, memory doorbell, or tail-register write. TX completion happens during NAPI via `hns3_clean_tx_ring()`, which reclaims descriptors whose VLD bit was cleared by hardware, unmaps/free buffers, updates BQL and stats, advances `next_to_clean` with release ordering, reclaims TX spare space, and wakes stopped queues when space returns.

RX polling allocates or reuses RX buffers in batches, consumes valid descriptors, creates an SKB with a small copied head, attaches page fragments or frag_list SKBs for larger packets, handles page-pool and page-frag reuse, reads packet metadata from the final descriptor, applies timestamp/VLAN/RSS/checksum/GRO information, updates stats, records the RX queue, and passes packets to GRO. On exit, any cleaned RX descriptors are refilled and the hardware head register is updated.

Reset control flows are split into DOWN, UNINIT, INIT, and UP notifications from the AE layer. DOWN stops the netdev and sets RESETTING. UNINIT disables IRQs, clears rings, frees vectors/rings, and clears initialized state. INIT reconstructs ring/vector/IRQ/client state and preserves CQ modes. UP clears RESETTING and reopens the netdev if it was running. Channel changes and TX spare buffer tunables use this same staged teardown/rebuild model.

## State and Persistence
Persistent runtime state lives in `struct hns3_nic_priv`: AE handle, netdev/device pointers, ring array, vector array, vector count, max non-TSO descriptor limit, TX timeout count, state bitset, CQ period modes, interrupt coalescing defaults, copybreak values, and minimum TX spare constraints. Per-ring state lives in `struct hns3_enet_ring`: descriptor memory, descriptor control blocks, ring indices, TQP pointer, queue index, stats with `u64_stats_sync`, page pool, RX assembly scratch state, and TX spare state. Per-vector state includes NAPI, IRQ information, IRQ mask address, TX/RX ring groups, coalescing state, DIM state, affinity mask, and event counters.

Hardware-persistent state includes descriptor base addresses and lengths, TQP enable bits, interrupt moderation registers, TX/RX ring head/tail registers, MAC/VLAN/RSS/FD/TC/FEC state managed through AE ops, and PCI/SR-IOV configuration. Module parameters `debug`, `tx_sgl`, and `page_pool_enabled` persist for the module lifetime and change logging, TX mapping strategy, and RX page-pool use.

Concurrency state is protected mostly by netdev serialization, NAPI context, queue stop/wake ordering, and explicit memory barriers. `ring_space()` pairs an acquire load of `next_to_clean` with release stores in TX completion; TX doorbell stores `last_to_use` with release ordering so completion does not reclaim descriptors before valid bits are visible. Ring stats use `u64_stats_sync` for lockless 64-bit accounting.

## Dependencies and Integration Points
The file depends on the HNS3 common contract in `hnae3.h`, HNS3 local definitions in `hns3_enet.h`, ethtool setup from `hns3_ethtool.c`, and tracepoints from `hns3_trace.h`. It integrates with PCI, SR-IOV, PCI AER/FLR recovery, PM, Linux netdev ops, BQL, NAPI/GRO, DMA mapping, page_pool, DIM interrupt moderation, RFS/aRFS when configured, TC mqprio and flower offload, VLAN filtering, PHY, timestamping, debugfs, and DCB when enabled. Hardware-specific work is delegated to AE ops such as `start`, `stop`, `reset_queue`, `map_ring_to_vector`, `set_mtu`, `set_mac_addr`, `set_vlan_filter`, `enable_fd`, `add_cls_flower`, `get_status`, and reset event helpers.

## Risks and Edge Cases
The TX descriptor path is sensitive to descriptor accounting, GSO limits, fraglist recursion, and hardware restrictions on continuous descriptors relative to MSS. Incorrect `next_to_use`, `last_to_use`, or memory barrier handling could lead to stale descriptors being reclaimed or hardware seeing incomplete descriptors. TX spare buffer handling has separate producer/consumer indices and special reclaim paths for bounce and SGL descriptors, so rollback and reclaim errors can leak DMA mappings or corrupt buffer reuse.

The RX path must preserve buffer ownership precisely. Page-pool and non-page-pool buffers have different lifetime rules, and the driver conditionally reuses, copies, drains, or returns pages. Multi-fragment packets can require frag_list SKBs after `MAX_SKB_FRAGS`, and failure before FE leaves partial packet state in `ring->skb`. GRO completion rewrites checksum and GSO metadata and only supports IPv4/IPv6 TCP. VLAN reporting depends on hardware generation and port-base VLAN state.

Reset and reconfiguration are high risk because they tear down IRQs, NAPI, ring memory, CPU rmap, vectors, and AE client state while preserving netdev registration and user-visible settings. The code has explicit guards for RESETTING/DOWN/INITED but relies on callers using the HNAE3 notification order. Channel changes and TX spare size changes attempt rollback; failed rollback would leave the device unusable.

Hardware version and capability gates are pervasive: TX push, advanced RX descriptor layout, hardware TX checksum, CQ period mode, GRE offload, page-pool behavior, FEC/WOL/etc. are not uniformly available. The older-tunnel UDP checksum workaround and V2 port-base VLAN limitations are examples where missing a generation check can produce bad packets or RAS errors.

## Test Signals
High-value tests include PCI probe/remove/shutdown on PF and VF IDs, module unload with active netdevs, open/stop cycles, TX/RX traffic at multiple MTUs, TSO/GSO/GRO, UDP tunnel and GRE offloads across device generations, SCTP checksum, VLAN insert/strip/filter with port-base VLAN modes, multi-frag and frag_list SKBs, TX timeout reset recovery, SR-IOV enable/disable with assigned VF behavior, VF MAC/VLAN/rate/spoof/trust operations, TC mqprio/flower offload, RFS/aRFS flow steering, hardware timestamp get/set and packet timestamps, channel changes with rollback, suspend/resume, PCI AER/FLR recovery, NAPI budget behavior, queue stop/wake under pressure, page-pool disabled/enabled RX runs, and ethtool selftest external loopback preparation/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_enet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_enet.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_enet.h

## Purpose
This header is the shared NIC-side contract for the HNS3 Ethernet driver. It defines NIC state bits, register offsets, descriptor layouts, packet type enums, ring/vector/private data structures, ring helpers, interrupt coalescing structures, hardware error/reset mapping types, and exported function prototypes used between the main netdev implementation, ethtool support, debug/DCB modules, and tracepoints.

## Important APIs, Types, and Functions
- `enum hns3_nic_state` defines private state bits for testing, resetting, initialized/down/disabled/removing states, service flags, hardware TX checksum, advanced RX descriptor layout, and TX push.
- Register macros define RX/TX ring base address, descriptor count/length, head/tail, free descriptor count, packet record, error, TQP enable, RX/TX enable, vector GL/RL/QL offsets, CQ period mode registers, and hardware buffer-size encodings.
- Descriptor bit macros define TX fields for L3/L4 types, checksum, VLAN, TSO, header lengths, outer tunnel metadata, FE/VLD/timestamp bits, MSS, and hardware checksum mode; RX fields define parsed packet metadata, error bits, GRO fields, timestamp bits, VLAN strip indicators, and packet type.
- `struct hns3_desc` is the packed hardware descriptor union for TX, RX, checksum, and timestamp views.
- `struct hns3_desc_cb` tracks driver-side ownership for each descriptor: DMA address, CPU buffer, private pointer, page offset or sent bytes, length, reuse/refill flags, descriptor type, and pagecnt bias.
- `struct ring_stats`, `struct hns3_tx_spare`, `struct hns3_enet_ring`, `struct hns3_enet_ring_group`, `struct hns3_enet_tqp_vector`, and `struct hns3_nic_priv` define the main runtime data model.
- Inline helpers and macros include `ring_space()`, register read/write wrappers, reset-state check, `ring_to_*` conversions, page sizing, ring iteration, AE op accessors, GL/RL unit conversion, and stats update helpers.
- Prototypes expose ethtool setup, channel changes, ring init/reset/cleanup, TX/RX fast paths, coalescing setters, promisc update requests, reset notifications, debug/DCB hooks, trace helper `hns3_shinfo_pack()`, and external loopback helpers.

## Control Flow
This header has no standalone executable flow, but it strongly shapes the control flow in `hns3_enet.c` and `hns3_ethtool.c`. TX setup fills `struct hns3_desc` using the TX bitfield macros, records buffer ownership in `struct hns3_desc_cb`, advances indices in `struct hns3_enet_ring`, and checks capacity through `ring_space()`. RX setup uses the same descriptor and control-block pair to map pages, reuse fragments, parse packet metadata, and refill hardware descriptors. Vector control flows iterate `struct hns3_enet_ring_group` through `hns3_for_each_ring()`, and reset/open/close paths rely on `struct hns3_nic_priv` state bits to gate operations.

## State and Persistence
The header declares all major in-memory persistent state for a netdev instance. `struct hns3_nic_priv` persists for the `net_device` lifetime. Ring descriptors and descriptor callbacks persist across open state until ring teardown or reset uninit. Ring indices, pending buffers, TX spare indices, RX SKB assembly scratch state, and coalescing/DIM counters are mutable runtime state. The register constants describe hardware state that persists in device registers until reset or driver reprogramming.

The descriptor control block `type` flags are critical persistence metadata because they determine whether cleanup uses skb freeing, page unmapping, page-pool return, TX spare reclaim, or scatterlist unmap. `ring_stats` is shared with ethtool and netdev stats, while `u64_stats_sync` provides a stable read protocol.

## Dependencies and Integration Points
The header includes Linux DIM, VLAN, page_pool type definitions, barriers, and `hnae3.h`. It is consumed by the main enet file, ethtool file, trace header, debug code, and optional DCB support. It integrates directly with kernel types such as `net_device`, `sk_buff`, `napi_struct`, `ethtool_channels`, `page_pool`, `dim`, `pci_dev`, and DMA addresses. Hardware capability and reset types come from HNAE3, so this header is tightly coupled to the AE layer ABI.

## Risks and Edge Cases
The packed descriptor layout must match hardware exactly; changing alignment, field order, or endian types would corrupt DMA descriptors. Several macros encode fields by shifts and masks rather than typed bitfield helpers, so callers must pass values within hardware ranges. `ring_space()` assumes exactly one unused descriptor and relies on release/acquire pairing with completion, making memory ordering part of the ABI. `struct hns3_enet_ring` uses unions for TX and RX-only fields; using the wrong half for a ring type would corrupt unrelated state.

RX page sizing depends on PAGE_SIZE and `buf_size`, with higher-order pages only for small page kernels and larger RX buffers. Descriptor counts must stay aligned to `HNS3_RING_BD_MULTIPLE` and within min/max pending limits. Feature state bits must stay synchronized with actual AE capabilities; advertising TX push, advanced RX layout, or hardware TX checksum without matching hardware support would misprogram descriptors.

## Test Signals
Compile-time layout and type checks are important because this file underpins tracepoints, ethtool, and the main driver. Runtime signals include correct descriptor DMA programming, stable TX/RX under ring wrap, accurate ethtool queue stats, correct feature advertisement, successful coalescing register programming, reset/open/close state transitions, page reuse behavior for 2K and 4K RX buffers, TX push on capable devices, and absence of DMA mapping leaks during ring teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_enet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_ethtool.c

## Purpose
This file implements the ethtool interface for HNS3 netdevs. It exposes driver/firmware info, per-queue and hardware statistics, selftests, ring parameters, pause settings, link settings, RSS and flow director controls, resets, channels, interrupt coalescing, register dumps, LED identify, message level, FEC, module EEPROM, private flags, timestamp info, tunables, link extended state, and Wake-on-LAN. It supports separate PF and VF operation tables, with PFs receiving the full physical-port feature set and VFs receiving the virtualized subset.

## Important APIs, Types, and Functions
- Per-queue stat descriptors `hns3_txq_stats[]` and `hns3_rxq_stats[]` map ethtool strings to offsets inside `struct hns3_enet_ring.stats`.
- Selftest helpers include `hns3_self_test()`, `hns3_selftest_prepare()`, `hns3_selftest_restore()`, `hns3_lp_setup()`, `hns3_lp_run_test()`, loopback packet construction and RX validation, plus external loopback prepare/restore integration with `hns3_enet.c`.
- Stats and strings are handled by `hns3_get_sset_count()`, `hns3_get_strings()`, `hns3_get_stats_tqps()`, and `hns3_get_stats()`, combining software per-queue stats with AE-provided MAC/misc stats.
- Link and media settings flow through `hns3_get_link_ksettings()`, `hns3_set_link_ksettings()`, `hns3_nway_reset()`, pause helpers, FEC conversion helpers, module EEPROM access, and link extended-state mapping.
- RSS and flow director operations include `hns3_get_rss_key_size()`, `hns3_get_rss_indir_size()`, `hns3_get_rss()`, `hns3_set_rss()`, `hns3_get_rxfh_fields()`, `hns3_set_rxfh_fields()`, `hns3_get_rxnfc()`, and `hns3_set_rxnfc()`.
- Reset and reconfiguration controls include `hns3_set_reset()`, `hns3_set_ringparam()`, `hns3_set_channels()` from the enet file, and TX spare buffer reset/rebuild through `hns3_set_tx_spare_buf_size()`.
- Coalescing controls include validation of GL, RL, QL, and CQE mode parameters and programming each queue vector via exported HNS3 coalescing setters.
- `hns3_ethtool_ops`, `hns3vf_ethtool_ops`, and `hns3_ethtool_set_ops()` install the correct operation table based on `HNAE3_SUPPORT_VF`.

## Control Flow
During netdev initialization, `hns3_ethtool_set_ops()` selects PF or VF ethtool ops. Ettool statistics requests first validate reset state, ask the AE layer to update hardware stats, append per-TQP software stats by reading ring stat offsets, then let the AE layer append MAC and miscellaneous counters. String counts are computed from per-queue counts plus AE-provided string sets.

Offline selftest initializes all result slots as unexecuted, rejects reset or non-offline requests, optionally performs external loopback first, then stops the netdev, disables VLAN filtering if active, halts autoneg, sets TESTING, runs supported loopback modes, clears loopback, restores autoneg/VLAN filtering, and reopens the netdev if it was running. Loopback traffic is generated by building one ARP-like SKB, transmitting through `hns3_nic_net_xmit()`, sleeping for RX completion, polling RX rings with a validation callback, and clearing TX descriptors.

Ring parameter changes validate descriptor bounds, RX buffer length, reset state, and TX push support. If depth or RX buffer size changes, the function backs up current rings, stops the netdev if running, updates descriptor counts and RX buffer sizes, reallocates all rings, and either frees the old backup or restores old ring structs on failure before reopening. TX push alone can be toggled without full ring reallocation.

Coalescing changes validate support and ranges, round legacy GL/RL units where needed, store global private coalescing settings, then iterate all queues and update the TX/RX vector coalescing state and hardware registers. CQE/EQE period mode is then reinitialized. Channel changes are delegated to `hns3_set_channels()` in the enet file, which performs reset-style teardown and rebuild.

Link setting operations select behavior based on media type, PHY presence, hardware generation, and PHY-IMP support. Copper ports may use PHY ethtool helpers; newer MAC-only hardware can set autoneg and fixed speed/duplex/lanes through AE ops after validation. FEC, module EEPROM, WOL, LED identify, pause, register dump, RSS, flow director, and resets are all thin wrappers that capability-check and dispatch to AE ops.

## State and Persistence
This file reads and mutates state owned by `struct hns3_nic_priv`, `struct hnae3_handle`, AE device capabilities/specs, and rings. Persistent user-visible settings include message level, private flags, coalescing configuration, CQ period mode, ring descriptor counts, RX buffer length, TX push bit, copybreak values, TX spare buffer size, RSS key/indirection/hash function, flow director rules, FEC settings, pause settings, WOL settings, and link settings when accepted by hardware. Selftest temporarily changes netdev running state, VLAN filtering, autoneg halt, loopback mode, TESTING/DOWN state bits, and ring contents.

Ring parameter and TX spare buffer changes are persistence-sensitive because they rebuild descriptor memory and may need rollback. Private flag updates toggle bits in `handle->priv_flags` and invoke handlers such as limited promiscuous mode update. Stats are not persisted separately; they are sampled from rings and AE hardware on request.

## Dependencies and Integration Points
The file depends on `hns3_enet.h`, `hns3_ethtool.h`, HNAE3 AE ops, Linux ethtool netlink/kernel parameter structs, PHY helpers, SFP identifiers, string helpers, VLAN feature bits, flow director ethtool commands, DIM CQE mode semantics, and netdev open/stop callbacks. It directly invokes exported enet functions for TX, RX ring cleaning, ring reset/init/fini, coalescing register writes, reset notifications, channel changes, external loopback, and promiscuous update requests.

## Risks and Edge Cases
Many operations must reject reset-in-progress or uninitialized rings; missing these checks can race against ring teardown. Selftest directly stops/reopens the netdev and manipulates VLAN filtering/autoneg/loopback, so failure paths must restore hardware state. The loopback test uses queue 0 and one packet, which is useful for smoke testing but limited as a coverage signal.

Ring resizing backs up full ring structs with embedded pointers and then overwrites live ring structs during rollback. This is fragile if ownership rules change in `struct hns3_enet_ring`, especially for page pools, pending SKBs, TX spare buffers, and descriptor callbacks. Coalescing values are hardware-generation dependent; older GL units must be rounded to multiples of 2 and RL to multiples of 4, while QL/CQE require capability checks. Link setting accepts different paths for PHY, PHY-IMP, and MAC-only devices and intentionally rejects some speed/duplex combinations.

Private flags are indexed up to `HNAE3_PFLAG_MAX`; descriptors and supported bits must stay aligned. Module EEPROM type detection relies on the first bytes of the EEPROM and returns errors for unknown module IDs. RSS hash function support differs by device generation. Reset requests from ethtool are mapped differently for PF and VF, and IMP reset is unsupported on older hardware.

## Test Signals
Useful tests include `ethtool -S` string/count/data alignment, `ethtool -t offline` for each supported loopback mode including restore after failure, PF/VF ethtool op differences, ring depth and RX buffer length changes while down and running, TX push toggle, channel changes with RSS configured, coalescing range validation and register effects, CQE mode toggling, RSS key/indir/hash changes including unsupported hash functions on older devices, flow director add/delete/list, ethtool reset flags for PF/VF, pause and FEC get/set, module EEPROM identification for SFP/QSFP variants, WOL get/set, link extended-state mapping when carrier is down, tunable changes with rollback, and reset-state rejection for all mutating operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_ethtool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_ethtool.h

## Purpose
This small header defines ethtool-local helper structures shared by the HNS3 ethtool implementation. It keeps statistic descriptors, SFP identification bytes, private flag descriptors, link extended-state mappings, and ring-parameter snapshots separate from the much larger NIC runtime header.

## Important APIs, Types, and Functions
- `struct hns3_stats` pairs an ethtool stat string with an offset into a runtime object, used for per-ring TX/RX stat extraction.
- `struct hns3_sfp_type` models the first EEPROM bytes used to classify SFP/QSFP module type and extended type.
- `struct hns3_pflag_desc` maps a private flag name to a handler invoked when that ethtool private flag changes.
- `struct hns3_ethtool_link_ext_state_mapping` maps an HNS3 link diagnosis status code to ethtool link extended state and substate values.
- `struct hns3_ring_param` stores TX descriptor count, RX descriptor count, and RX buffer length for ring resize comparison and rollback.

## Control Flow
There is no executable control flow. `hns3_ethtool.c` instantiates arrays of these structures and uses them to drive ethtool string generation, stats lookup, private flag dispatch, module EEPROM type detection, link diagnosis translation, and ring parameter change/rollback logic.

## State and Persistence
The structures are transient or static metadata. `hns3_stats`, `hns3_pflag_desc`, and link extended-state mappings are compile-time tables. `hns3_sfp_type` is a short stack object populated from module EEPROM reads. `hns3_ring_param` is stack state used during ring configuration changes and does not persist after the ethtool operation returns.

## Dependencies and Integration Points
The header depends on Linux ethtool and netdevice types. It is intentionally narrow and included by `hns3_ethtool.c`; its structures refer to `ETH_GSTRING_LEN`, `struct net_device`, and ethtool link extended-state enums. It complements `hns3_enet.h`, which provides the actual ring and private state these descriptors address.

## Risks and Edge Cases
Offsets in `struct hns3_stats` are only safe if they are built with `offsetof()` against the actual target structure and read as the expected width. Private flag descriptors must stay ordered with `HNAE3_PFLAG_MAX` and supported flag bits. Link extended-state mappings must use ethtool states/substates compatible with the running kernel API. `hns3_ring_param` snapshots only a subset of ring settings, so future ring-rebuild-sensitive fields may need to be added if ring configuration expands.

## Test Signals
Compile coverage catches API drift in ethtool types. Runtime signals include correct `ethtool -S` names and values, private flag name exposure and handler invocation, link extended-state output for known diagnosis codes, successful module type detection, and ring resize rollback preserving TX/RX descriptor counts and RX buffer length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_trace.h

## Purpose
This header defines HNS3 tracepoints for debugging packet layout, descriptor programming, and RX descriptor consumption. It is included by `hns3_enet.c` with `CREATE_TRACE_POINTS`, making this file the trace event contract for TX descriptor, RX descriptor, TSO, GRO, and over-max-descriptor diagnostics.

## Important APIs, Types, and Functions
- `TRACE_SYSTEM hns3` names the tracepoint subsystem.
- `DESC_NR` computes how many 32-bit words are present in `struct hns3_desc` for descriptor array printing.
- `DECLARE_EVENT_CLASS(hns3_skb_template)` captures SKB head length, total length, fragment count, checksum state, header length, GSO size/segs/type, fraglist flag, and all fragment sizes through `hns3_shinfo_pack()`.
- `DEFINE_EVENT()` instantiates `hns3_over_max_bd`, `hns3_gro`, and `hns3_tso` from the shared SKB template.
- `TRACE_EVENT(hns3_tx_desc)` records queue index, software NTU/NTC, descriptor DMA base, netdev name, and the selected TX descriptor image.
- `TRACE_EVENT(hns3_rx_desc)` records queue index, software NTU/NTC, descriptor DMA base, RX buffer DMA address, netdev name, and the current RX descriptor image.

## Control Flow
The header itself only declares tracepoint metadata. Runtime events are emitted from the enet fast paths: TX descriptor fill/FE marking calls `trace_hns3_tx_desc()`, RX allocation and fragment handling call `trace_hns3_rx_desc()`, TSO setup calls `trace_hns3_tso()`, hardware GRO completion calls `trace_hns3_gro()`, and descriptor-limit handling calls `trace_hns3_over_max_bd()`. When tracing is disabled, these calls compile into low-overhead tracepoint checks; when enabled, the trace subsystem evaluates the fast-assign blocks and formats data through `TP_printk`.

## State and Persistence
Tracepoints persist as kernel instrumentation definitions while the module is loaded. Event records are transient in ftrace/perf buffers. They snapshot selected SKB fields and descriptor contents at the call site; they do not own driver state or change packet/descriptors. The header relies on `ring->tqp->handle->kinfo.netdev->name`, ring indices, descriptor DMA base, and descriptor callback DMA addresses being valid during trace emission.

## Dependencies and Integration Points
This file depends on Linux tracepoint infrastructure and on HNS3 types declared before inclusion, especially `struct hns3_desc`, `struct hns3_enet_ring`, and helper `hns3_shinfo_pack()`. It ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE hns3_trace`, and `<trace/define_trace.h>`, which is the standard pattern for tracepoint generation. It integrates with userspace tracing through ftrace, tracefs, perf, and any tooling that subscribes to `hns3:*` events.

## Risks and Edge Cases
Trace fast-assign blocks dereference live SKB and ring state, so trace calls must only occur while those objects are valid. The SKB template uses TCP header helpers to compute header length and chooses inner headers for encapsulated packets; unusual non-TCP GSO packets may still be represented through these helper assumptions. Descriptor dumping copies the whole descriptor as a 32-bit array, which is useful but hardware-version-sensitive and may require decoder updates as descriptor formats evolve. Because this header defines tracepoints, it must be included with `CREATE_TRACE_POINTS` exactly once in the driver build.

## Test Signals
Compile tests verify tracepoint generation and include ordering. Runtime checks include enabling `hns3:hns3_tx_desc`, `hns3:hns3_rx_desc`, `hns3:hns3_tso`, `hns3:hns3_gro`, and `hns3:hns3_over_max_bd` in tracefs, generating matching TX/RX/TSO/GRO traffic, confirming descriptor words and ring indices match driver state, and ensuring tracing does not crash during reset, close, or heavy traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_trace.h -->
