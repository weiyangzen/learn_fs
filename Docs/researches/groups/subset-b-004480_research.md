# subset-b-004480 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tc_lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tc_lib.c

Purpose: implements Linux TC flower offload for the Intel ice driver. It translates kernel flow dissector keys and TC actions into ice advanced switch rules, covering legacy PF ADQ filters, switchdev representor forwarding, tunnel matching, drop/mirror/redirect behavior, and LLDP exception handling.

Important APIs and functions: `ice_add_cls_flower()` and `ice_del_cls_flower()` are the public add/delete entry points used by the netdev TC offload path. `ice_parse_cls_flower()` parses supported dissector keys into `struct ice_tc_flower_fltr`; `ice_parse_tc_flower_actions()` maps classid, queue mapping, drop, redirect, and mirror actions; `ice_add_switch_fltr()` dispatches to `ice_eswitch_add_tc_fltr()` in switchdev mode or `ice_add_tc_flower_adv_fltr()` in legacy mode. `ice_tc_fill_rules()` and `ice_tc_fill_tunnel_outer()` construct `struct ice_adv_lkup_elem` arrays, while `ice_tc_count_lkups()` keeps allocation and fill counts consistent. `ice_replay_tc_fltrs()` reprograms saved rules after reset.

Control flow: add starts with reset, LLDP firmware-agent, feature, and duplicate-cookie checks. The parser rejects unsupported dissector keys, validates tunnel-device context, fills outer and inner header keys/masks, flips representor ingress/egress direction, then parses actions. Rule programming allocates lookup elements, injects metadata lookups for direction/VLAN/tunnel/src VSI, fills hardware protocol entries, sets switch action priority/source/VSI handle, calls `ice_add_adv_rule()`, and stores recipe/rule IDs for later deletion.

State and persistence: successful filters live in `pf->tc_flower_fltr_list` keyed by cookie and retain source/destination VSI pointers, rule IDs, direction, flags, tunnel type, and parsed masks. ADQ bookkeeping updates destination `num_chnl_fltr` and `pf->num_dmac_chnl_fltrs`. LLDP helper paths persist VF LLDP state in `vsi->vf->lldp_*`. Replay uses the in-memory filter list after reset rather than reparsing netlink rules.

Dependencies and integration: depends on kernel flow dissector, TC actions, netlink extack, tunnel netdev helpers, representor/eswitch helpers, VLAN/DVM state, ice switch recipe APIs (`ice_add_adv_rule`, `ice_rem_adv_rule_by_id`), ADQ queue mapping, and LLDP/VF state. It consumes types from `ice_tc_lib.h`, `ice_type.h`, `ice_protocol_type.h`, `ice_fltr.h`, and `ice_lib.h`.

Risks: lookup count and fill logic must remain exactly synchronized or rule programming fails. Tunnel support is intentionally partial, with encap source L4 and several VXLAN/Geneve port cases rejected. IPv6 parsing rejects loopback and all-any masks. Rule replay ignores return values, so reset recovery failures may be silent. The LLDP special cases are fragile because PF drop rules and VF pass/drop rules interact across the same filter list.

Test signals: exercise TC flower add/delete for MAC, VLAN/CVLAN, IPv4/IPv6, ToS/TTL, TCP/UDP ports, PPPoE, L2TPv3, VXLAN/Geneve/GRETAP/GTP/PFCP, ADQ classid, queue mapping, drop, redirect, mirror, switchdev representor ingress/egress, duplicate cookies, unsupported masks, reset replay, and LLDP firmware-agent modes. Hardware counters, extack messages, `tc filter show`, and traffic steering/drop behavior are the primary observability points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tc_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tc_lib.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tc_lib.h

Purpose: declares the TC flower offload contract used by the ice driver. It defines the bit flags, parsed header containers, action representation, filter lifetime object, and exported helper prototypes consumed by the TC implementation and other driver modules.

Important APIs and types: `ICE_TC_FLWR_FIELD_*` flags describe every supported match dimension, including L2/L3/L4, tunnel key ID, encap addresses and ports, GTP/PFCP options, VLAN priority/TPID, PPPoE, and L2TPv3. `struct ice_tc_flower_action` stores either hardware traffic class or queue forwarding target plus `enum ice_sw_fwd_act_type`. `struct ice_tc_flower_lyr_2_4_hdrs` contains key and mask storage for MAC, VLAN, CVLAN, PPPoE, L2TPv3, IP, and ports. `struct ice_tc_flower_fltr` is the persistent filter node linked into the PF list. Exported functions include add/delete, replay, queue-to-VSI lookup, tunnel support checks, and LLDP pass/drop helpers.

Control flow role: this header does not implement the parser, but its fields determine how `ice_tc_lib.c` moves from flow dissector input to hardware lookup elements. `ice_is_chnl_fltr()` classifies ADQ channel filters after the implementation has resolved destination VSI or traffic class. `ice_is_forward_action()` centralizes the action categories that need destination validation.

State and persistence: `struct ice_tc_flower_fltr` is the main persistence unit. It stores netlink cookie, rule and recipe IDs returned by firmware, destination VSI handle and pointer, source VSI, direction, parsed outer/inner headers, tenant ID, GTP/PFCP metadata, tunnel type, flags, action, and extack pointer. The extack pointer is transient and is reset during replay.

Dependencies and integration: pulls in Linux bit helpers and PFCP metadata plus driver-specific `struct ice_vsi`, `struct ice_pf`, `struct ice_netdev_priv`, switch forwarding action enums, and ADQ constants from other ice headers. Kernel networking consumers reach these functions through TC setup hooks.

Risks: the field-bit namespace is nearly full at bit 30; adding fields requires compatible count/fill/parser changes in the C file. Header aliases for IPv4/IPv6 fields use macros inside `struct ice_tc_l3_hdr`, so careless names can obscure actual storage. `ice_is_chnl_fltr()` depends on `dest_vsi` being populated before it is called for queue actions.

Test signals: compile coverage should catch missing prototypes and struct drift, but behavioral tests need to verify that each flag has parser, lookup-count, and lookup-fill support. ADQ tests should confirm `ice_is_chnl_fltr()` for class and queue modes, and tunnel tests should validate PFCP/GTP metadata layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tc_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_trace.h

Purpose: defines the ice driver's tracepoint namespace and trace events for RX/TX datapath, DIM tuning, TX timestamps, eswitch bridge events, and switch rule statistics. It lets production kernels observe fast-path and eswitch behavior with ftrace/perf without adding ad hoc logging.

Important APIs and types: `TRACE_SYSTEM ice` establishes the subsystem. `ice_trace(name, args...)` and `ice_trace_enabled(name)` wrap `trace_ice_*` symbols so driver code can call tracepoints through a common macro. Event classes include `ice_rx_dim_template`, `ice_tx_dim_template`, `ice_tx_template`, `ice_rx_template`, `ice_rx_indicate_template`, `ice_xmit_template`, `ice_tx_tstamp_template`, `ice_esw_br_fdb_template`, `ice_esw_br_vlan_template`, `ice_esw_br_port_template`, and `ice_switch_stats_template`.

Control flow role: this file is included by C files that emit trace events, especially `ice_txrx.c` for `clean_tx_irq`, `clean_rx_irq`, `xmit_frame_ring`, and timestamp request/completion points. Each `DECLARE_EVENT_CLASS` defines the recorded fields and `TP_printk` format, and `DEFINE_EVENT` creates concrete tracepoints.

State and persistence: tracepoints do not own persistent driver state. They snapshot pointers, queue indices, netdev names, DIM fields, bridge FDB/VLAN data, switch recipe/rule counts, and timestamp indices at event time. Runtime enablement is controlled by the kernel tracing subsystem.

Dependencies and integration: depends on Linux `tracepoint.h`, `trace/define_trace.h`, ice ring types, DIM structures, and eswitch bridge types from `ice_eswitch_br.h`. The `TRACE_INCLUDE_FILE` override points back to the driver-local header path because this is built as a module rather than under the global trace include tree.

Risks: tracepoint field expressions dereference ring/netdev and eswitch bridge objects, so callers must only emit events while those objects are live. Format or field changes affect scripts consuming trace output. Pointer-valued fields are useful for correlation but not stable identifiers across lifetimes.

Test signals: build with tracing enabled, confirm generated `trace_ice_*` symbols, enable events under `/sys/kernel/tracing/events/ice/`, run TX/RX, DIM, timestamp, and eswitch bridge scenarios, and verify trace output includes expected netdev names, queue indices, bridge data, and switch rule counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tspll.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tspll.c

Purpose: programs and validates the Clock Generation Unit TSPLL used by PTP and SyncE-capable Intel ice devices. It handles E82x style MACs and E825-C style MACs with different register layouts, lock-status registers, and recovered-clock controls.

Important APIs and functions: `ice_tspll_init()` is the exported initialization entry point. It reads firmware function capabilities, validates `time_ref` and `clk_src`, disables sticky lock bits, programs TSPLL, and retries with TCXO/default frequency on failure. `ice_tspll_cfg_pps_out_e825c()` controls 1PPS output amplitude/enable. `ice_tspll_bypass_mux_active_e825c()`, `ice_tspll_cfg_bypass_mux_e825c()`, and `ice_tspll_cfg_synce_ethdiv_e825c()` manage E825-C SyncE bypass mux and divider state. Static helpers provide frequency/source names, default frequency, parameter checking, per-MAC TSPLL programming, sticky-bit programming, and link-speed-to-divider mapping.

Control flow: initialization exits early for unsupported MACs. For supported MACs, firmware capability values are checked against valid ranges and MAC/source restrictions. E82x programming disables PLL, writes R9/R19/R22/R24 using table-driven divisors, reenables PLL, waits, and checks `ICE_CGU_RO_BWM_LF_TRUE_LOCK`. E825-C programming disables PLL and time sync, enables the selected input receiver, writes fixed E825 divisors and source selection, clears R24, reenables PLL, waits, and checks `ICE_CGU_RO_LOCK_TRUE_LOCK`.

State and persistence: state is hardware register state in the CGU, not heap state. The code persists selected clock source, frequency, divisors, enable bits, lock-status mode, 1PPS output, bypass mux source, and SyncE dividers in device registers. `hw->func_caps.ts_func_info`, `hw->mac_type`, `hw->ptp.ports_per_phy`, and current link speed guide programming.

Dependencies and integration: uses `ice_read_cgu_reg()` and `ice_write_cgu_reg()` from PTP hardware support, CGU register/mask definitions, `ice_hw_to_dev()` logging, firmware capabilities from `ice_type.h`, and link speed constants from AQ definitions. SyncE calls are documented as running under `pf->dplls.lock`.

Risks: incorrect frequency/source combinations can fail PLL lock or produce invalid PTP timing. Register sequences are MAC-specific and order-sensitive. E825-C mux selection uses `port_num + ICE_CGU_BYPASS_MUX_OFFSET_E825C`, so invalid port numbering would select the wrong recovered clock. Link speeds without a divider mapping return `-EOPNOTSUPP`.

Test signals: test on E82x/E825-C hardware with firmware-provided TIME_REF and TCXO configs, confirm lock success and fallback behavior, verify warnings on invalid capability values, check 1PPS output, recovered clock mux active reporting, divider programming across supported link speeds, and PTP/SyncE stability after reset or link changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tspll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tspll.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tspll.h

Purpose: declares TSPLL parameter structures, E825-C CGU constants, and exported TSPLL/SyncE helper prototypes used by the ice PTP and DPLL integration code.

Important APIs and types: `struct ice_tspll_params_e82x` stores the E82x table-driven reference pre-divider, post-PLL divider, feedback divider, and fractional divider. Constants name CGU recovered-clock mux selections (`ICE_CGU_NET_REF_CLK0`, `ICE_CGU_REF_CLK_BYP0`, `ICE_CGU_REF_CLK_BYP1`) and fixed E825 TSPLL programming values. Exported functions initialize TSPLL, configure E825-C 1PPS output, query/configure bypass mux activity, and set SyncE ETH divider values.

Control flow role: the header is consumed by `ice_tspll.c` and callers that need TSPLL initialization or SyncE output programming. It does not enforce locking itself, but the implementation documents bypass mux and divider configuration as protected by the PF DPLL lock.

State and persistence: no direct state is stored here. The constants and struct shape define how `ice_tspll.c` writes hardware CGU registers and how selected frequencies map to register fields.

Dependencies and integration: depends on `struct ice_hw`, `enum ice_synce_clk`, and TSPLL frequency/source definitions from `ice_type.h` and related PTP headers included by C files. It is part of the PTP/SyncE hardware support boundary rather than the network datapath.

Risks: constants are hardware contract values; changing them breaks register programming. The E82x parameter struct must stay synchronized with the frequency table and CGU field widths. Callers must pass valid output enums and hold required locks for DPLL-related paths.

Test signals: compile coverage for all users, TSPLL init on supported and unsupported MAC types, DPLL/SyncE tests for both outputs, and hardware validation that generated 1PPS/recovered-clock outputs match selected link speed and source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tspll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx.c

Purpose: implements the main transmit and receive datapath for the ice driver. It allocates and frees descriptor rings, services NAPI TX/RX completion, maps SKBs and XDP frames to hardware descriptors, handles checksum/TSO/VLAN/timestamp offloads, programs Flow Director dummy packets, and manages interrupt moderation.

Important APIs and functions: exported entry points include `ice_start_xmit()`, `ice_select_queue()`, `ice_napi_poll()`, `ice_setup_tx_ring()`, `ice_setup_rx_ring()`, `ice_free_tx_ring()`, `ice_free_rx_ring()`, `ice_alloc_rx_bufs()`, `ice_clean_ctrl_tx_irq()`, `ice_clean_ctrl_rx_irq()`, `ice_xdp_xmit()`, and `ice_prgm_fdir_fltr()`. Major internal paths are `ice_clean_tx_irq()`, `ice_clean_rx_irq()`, `ice_tx_map()`, `ice_tx_csum()`, `ice_tso()`, `ice_tstamp()`, and descriptor-count/linearization helpers.

Control flow: TX starts at `ice_start_xmit()`, pads too-short frames, selects the ring from `skb->queue_mapping`, computes descriptor needs, optionally linearizes, prepares VLAN/TSO/checksum/eswitch/PTP context descriptors, DMA maps skb data/frags, writes descriptors, sets `next_to_watch`, updates BQL, and rings the tail. RX NAPI checks DD bits, processes header-split and payload buffers through libeth XDP buffers, runs XDP, builds SKBs for passed packets, fills checksum/hash/PTP/protocol metadata via `ice_txrx_lib.c`, submits GRO, refills descriptors, finalizes XDP TX/redirect, updates stats, and handles writeback-on-ITR if work remains.

State and persistence: ring state is held in `next_to_use`, `next_to_clean`, descriptor memory, `tx_buf`/RX fill queue entries, page-pool pointers, XDP program pointers, timestamp rings, BQL accounting, per-ring stats, and q_vector DIM samples. Hardware-visible persistence is descriptor DMA memory and tail register updates. Time-based TX optionally writes a separate timestamp descriptor ring.

Dependencies and integration: integrates with netdev NDOs, NAPI, DMA mapping, page pools/libeth, XDP and AF_XDP paths, PTP timestamp allocation, DCB DSCP queue selection, eswitch target selection, Flow Director control VSI, tracepoints from `ice_trace.h`, and register helpers for GLINT interrupt control.

Risks: this is hot-path, memory-order-sensitive code. Barriers before tail writes and descriptor reads are critical. DMA error unwinding must not leak mappings. TX timestamp rings are RCU-freed and require pointer/flag ordering. XDP locking differs depending on `ice_xdp_locking_key`. Descriptor-count mistakes can cause queue stalls or hardware max-buffer violations. RX refill failures intentionally force another poll pass.

Test signals: stress TCP/UDP, TSO/GSO, fragmented SKBs, VLAN offload, DCB DSCP mapping, PTP TX/RX timestamps, XDP PASS/DROP/TX/REDIRECT, AF_XDP zero-copy, Flow Director programming, busy-poll, multi-ring q_vectors, DIM changes, queue stop/wake, DMA mapping failures, MTU extremes, reset cleanup, and link-down TX behavior. Observe ethtool stats, BQL behavior, tracepoints, packet counters, and skb checksum correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx.h

Purpose: defines the ice TX/RX datapath ABI used across the driver. It contains descriptor sizing constants, TX flag bits, XDP result bits, buffer ownership types, offload parameter storage, ring stats, ring state enums, interrupt moderation helpers, ring structures, iterators, and public datapath prototypes.

Important APIs and types: `enum ice_tx_buf_type` defines cleanup ownership for SKB, dummy Flow Director buffers, XDP_TX, XDP_XMIT, XSK, and fragments. `struct ice_tx_buf` stores descriptor watch/RS index, buffer pointer, byte/segment accounting, flags, VLAN ID, and DMA mapping. `struct ice_tx_offload_params` carries context/data descriptor fields while building TX. `struct ice_rx_ring`, `struct ice_tx_ring`, and `struct ice_tstamp_ring` are the core queue structures. `struct ice_ring_container` groups rings per q_vector and holds DIM/ITR state.

Control flow role: macros such as `ICE_DESC_UNUSED()`, `DESC_NEEDED`, and `ICE_GLINT_DYN_CTL_WB_ON_ITR()` directly guide queue stop/wake, refill, and interrupt writeback behavior in `ice_txrx.c`. `ice_for_each_rx_ring` and `ice_for_each_tx_ring` drive NAPI loops. Prototypes expose setup, cleanup, NAPI, xmit, queue selection, Flow Director, and timestamp cleanup to the wider driver.

State and persistence: the ring structures cache hardware descriptor DMA addresses, tail MMIO pointers, queue indices, register indices, backreferences to VSI/q_vector/netdev, XDP and XSK resources, page-pool/fill-queue state, per-ring stats, and channel/scheduler identifiers. Ring stats use `u64_stats_sync` so readers can safely sample 64-bit counters.

Dependencies and integration: includes libeth types and `ice_type.h`, and references netdev, BPF/XDP, page pool, PTP, channel, q_vector, and VSI types defined elsewhere. The layout uses cacheline grouping macros because these structures are touched in high-frequency NAPI and transmit paths.

Risks: structure layout and flag semantics are performance and correctness sensitive. Changing descriptor constants can break hardware limits. Ring fields have implicit concurrency expectations between NAPI, xmit, teardown, XDP, and stats readers. The timestamp ring pointer is RCU-managed and must be paired with ordering in the implementation.

Test signals: build all datapath users, run traffic with varying ring sizes, XDP/XSK enablement, TX timestamp enable/disable, queue stop/wake, interrupt moderation settings, stats reads under load, and teardown/reset while traffic is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx_lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx_lib.c

Purpose: provides shared RX/TX helper logic used by the ice datapath, especially RX descriptor-to-skb metadata conversion and XDP TX handling. It keeps smaller common operations out of the main `ice_txrx.c` NAPI loop.

Important APIs and functions: exported functions are `ice_release_rx_desc()`, `ice_process_skb_fields()`, `ice_receive_skb()`, `__ice_xmit_xdp_ring()`, and `ice_finalize_xdp_rx()`. The file also exports `ice_xdp_md_ops` for XDP metadata hints. Internal helpers decode RX hash and packet type, set checksum state including GCS, apply RX hardware timestamps, clean XDP TX completions, return XDP frames in bulk, and expose XDP metadata for timestamp/hash/VLAN.

Control flow: RX refill calls `ice_release_rx_desc()` to update `next_to_use` and write the tail only on 8-descriptor boundaries. Packet delivery calls `ice_process_skb_fields()` to set RSS hash, representor target/protocol in multidev mode, checksum state, and PTP timestamp; then `ice_receive_skb()` applies VLAN acceleration and calls GRO. XDP TX calls `__ice_xmit_xdp_ring()` to reserve descriptors, optionally clean completions, DMA-map frame-based data or sync page-pool data, write descriptors, and update `next_to_use`. Batches finish in `ice_finalize_xdp_rx()`, which flushes redirects and sets RS/tail for XDP TX.

State and persistence: updates RX `next_to_use`, TX XDP `next_to_use`, `next_to_clean`, `xdp_tx_active`, descriptor RS index, per-ring stats, SKB metadata, and packet context fields. XDP metadata callbacks read the saved descriptor pointer in `libeth_xdp_buff` and RX ring packet context.

Dependencies and integration: relies on libeth/libie packet type parsing, page-pool DMA addresses, XDP core APIs, GRO/VLAN helpers, PTP timestamp helpers, representor/eswitch helpers, and descriptor definitions from ice LAN headers. It is called from `ice_txrx.c` but also forms the XDP metadata operations contract with BPF.

Risks: RX checksum decisions must match hardware descriptor semantics, especially tunneled packets, IPv6 extension flags, GCS, and NAT/outer UDP errors. XDP frame cleanup must distinguish page-pool-backed XDP_TX from externally supplied XDP_XMIT frames. `ice_release_rx_desc()` intentionally masks lower tail bits; changing that can increase MMIO writes or confuse hardware. XDP metadata returns `-ENODATA` for absent hints and must not report stale packet context.

Test signals: validate RX checksum offload on IPv4, IPv6, tunnels, GCS-enabled rings, and checksum errors; RSS hash propagation; VLAN stripped-tag delivery; representor RX stats/protocol; RX and XDP hardware timestamp hints; XDP_TX and `ndo_xdp_xmit` with fragments; redirect flushes; and tail update cadence under refill pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx_lib.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx_lib.h

Purpose: declares inline descriptor helpers and shared RX/XDP helper prototypes for the ice datapath. It is included by `ice_txrx.c` and `ice_txrx_lib.c`.

Important APIs and helpers: `ice_test_staterr()` tests little-endian RX descriptor status/error bits. `ice_is_non_eop()` identifies multi-buffer packets and increments `rx_non_eop_descs`. `ice_build_ctob()` builds the transmit data descriptor command/offset/buffer-size/tag quadword. `ice_build_tstamp_desc()` builds a TX time scheduling descriptor. `ice_get_vlan_tci()` extracts a stripped VLAN tag from L2TAG1 or L2TAG2. `ice_xdp_ring_update_tail()` writes the XDP TX tail with a barrier. `ice_set_rs_bit()` sets Report Status on the last produced XDP descriptor and returns its index.

Control flow role: these helpers sit directly in hot paths. TX descriptor construction and XDP RS/tail updates depend on them for correct bit packing and ordering. RX processing uses `ice_is_non_eop()` to defer skb construction until end-of-packet and uses `ice_get_vlan_tci()` before GRO delivery.

State and persistence: inline helpers update descriptor memory, ring statistics, and MMIO tail registers. They do not allocate resources, but the ordering effects are persistent from hardware's perspective because descriptor writes become visible before tail updates.

Dependencies and integration: includes `ice.h` for descriptor and ring definitions, hardware bit masks, and stats helpers. Prototypes expose the C helpers for RX descriptor release, skb metadata processing, skb receive, XDP TX submission, and XDP batch finalization.

Risks: endian and bit-shift mistakes here corrupt hardware descriptors. `ice_set_rs_bit()` assumes `next_to_use` is already advanced and wraps correctly. `ice_get_vlan_tci()` assumes only one stripped tag is supported by the OS/PF configuration. Barriers before tail writes are required on weakly ordered architectures.

Test signals: compile for endian correctness, TX descriptor inspection on real hardware, XDP_TX completion with RS wraparound, VLAN tag extraction for L2TAG1/L2TAG2, multi-buffer RX packets, and refill tail-write behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_type.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_type.h

Purpose: defines core hardware-facing types, constants, capabilities, persistent state containers, and enums used throughout the ice driver. It is the central model of device, function, port, scheduler, DCB, PTP, NVM, switch, mailbox, and forwarding state.

Important APIs and types: top-level `struct ice_hw` holds MMIO base, backpointer, port info, MAC type, PCI IDs, scheduler topology, VSI contexts, bus/flash/capability data, control queues, firmware/API versions, package metadata, tunnel/DVM/filter/RSS state, mailbox snapshot, PTP hardware, and CGU metadata. `struct ice_port_info` owns link, MAC, PHY, flow control, scheduler tree, QoS, and per-port locks. Capability structs include `ice_hw_common_caps`, `ice_hw_func_caps`, and `ice_hw_dev_caps`. Other major types cover link status, PHY info, Flow Director profiles, TSPLL and clock source enums, NVM/OROM/netlist banks, TX scheduler nodes, DCBX config, switch recipe state, mailbox malicious-VF detection, and stats.

Control flow role: this header does not implement algorithms, but nearly every driver subsystem branches on these enums and fields. Examples include MAC-type dispatch for TSPLL, VSI-type dispatch in datapath and TC, DCB mode selection for queue priority, reset source handling, switch forwarding action selection, and capability checks for queues, MSI-X, RSS, PTP, RDMA, SR-IOV, NVM updates, and DVM.

State and persistence: many structures mirror persistent device or firmware state: flash bank locations and versions, active package metadata, scheduler tree TEIDs and bandwidth profiles, link/PHY requested modes, DCB desired/local/remote configs, PTP function ownership, switch recipe counts, Flow Director profiles/filter counts, RSS lists, mailbox snapshots, and hardware statistics. Some fields are protected by mutexes such as scheduler, tunnel, filter profile, Flow Director, and RSS locks.

Dependencies and integration: includes generated hardware definitions, device IDs, OS abstraction, control queue, LAN descriptor definitions, flex/parser types, protocol types, sideband queue commands, VLAN mode, fwlog, wait queues, and DSCP definitions. It is consumed by almost all C files in the driver.

Risks: because this is a shared contract header, field changes have broad ABI-like impact inside the driver. Bit definitions must match firmware/hardware registers. Lock ownership is documented by field grouping rather than enforced by types. Capability or enum mismatches can lead to unsupported hardware paths, wrong queue counts, incorrect TSPLL programming, or invalid switch actions.

Test signals: broad compile coverage, probe on multiple MAC types, firmware/API compatibility checks, NVM bank/version reads, DCB/DSCP configuration, scheduler and devlink-rate operations, SR-IOV/VF mailbox stress, Flow Director/RSS/filter programming, PTP/TSPLL initialization, reset flows, and ethtool stats validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_type.h -->
