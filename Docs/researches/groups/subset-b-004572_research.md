# subset-b-004572 research

Grouped research for LAN966x driver sources. Each section title preserves the source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_port.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_port.c

Purpose: this file owns low-level LAN966x front-port bring-up, shutdown, PCS status/configuration, and per-port QoS classification/rewrite programming. It translates phylink-facing state and driver QoS structs into ordered writes to DEV, ANA, REW, SYS, QSYS, AFI, and CHIP_TOP registers.

Important APIs and functions: `lan966x_port_config_down()` and `lan966x_port_config_up()` wrap the internal link sequencing helpers. `lan966x_port_status_get()` reads PCS sticky/link/aneg registers and decodes Clause 22 state through phylink helpers. `lan966x_port_pcs_set()` programs in-band/out-of-band PCS mode, advertising, reset release, and stores `port->config`. `lan966x_port_qos_set()` fans out to PCP/DSCP trust maps, default priority, PCP/DEI rewrite, and DSCP rewrite helpers. `lan966x_port_init()` disables learning, forces the port down, initializes FDMA netdev state when present, and handles quad-interface PCS reset release.

Control flow: link-down is a strict hardware drain sequence: stop AFI injection, wait for AFI frame count to clear, reset PCS RX, disable MAC RX, disable switch forwarding and dequeueing, disable pause/PFC, delay for worst-case jumbo drain, disable HDX backpressure, force queue aging/flush, wait for egress queues to empty, stop MAC TX and reset clock domains, then clear flushing. Link-up maps Linux speeds to LAN966x speed encodings, updates TAPRIO speed state, configures MAC mode/IFG/HDX seed/CUPHY clock, enables PCS and pause thresholds, programs flow control and tail-drop watermarks, enables MAC RX/TX, sets clock speed, enables QSYS forwarding, and re-enables AFI.

State and persistence: persistent driver state is mainly `port->config`; QoS inputs are applied directly to hardware rather than stored here. Hardware state persists in register tables until reprogrammed or reset. Timeout loops log but do not fail upward, so callers cannot distinguish a fully flushed port from a best-effort shutdown after an AFI or QSYS timeout.

Dependencies and integration: depends on `lan966x_main.h` register accessors/macros, Linux phylink/PHY interface helpers, FDMA setup, TAPRIO speed programming, and generated register definitions. It is called from netdev/phylink lifecycle code outside this file.

Risks: register ordering is critical, especially around draining queues and clock resets. The watermark encoder silently clamps large values. QoS map loops assume array sizes match hardware table width. `lan966x_port_qos_pcp_rewr_set()` derives DEI from PCP count and indexes `REW_PCP_DEI_CFG`; malformed maps could program unexpected rewrite slots if upstream validation is weak. Test signals include link cycling at all supported speeds/interfaces, pause/PFC disabled/enabled behavior, PCS autoneg and forced modes, FDMA netdev initialization, TAPRIO speed updates, and QoS PCP/DSCP classification/rewrite checks with packet captures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ptp.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ptp.c

Purpose: this file implements LAN966x Precision Time Protocol support: PHC registration, TOD get/set/adjust, frequency adjustment, external timestamp/perout pin control, RX/TX hardware timestamping, and VCAP trap rules for PTP traffic.

Important APIs and functions: `lan966x_ptp_init()` registers one PHC per domain, initializes locks and per-port TX timestamp queues, programs nominal TOD increments, and enables PTP domains. `lan966x_ptp_deinit()` purges queued SKBs and unregisters clocks. `lan966x_ptp_hwtstamp_set/get()` manage netdev hardware timestamp configuration and per-port TX/RX commands. `lan966x_ptp_txtstamp_request()` classifies outgoing PTP packets and queues two-step SKBs with a bounded timestamp ID space. `lan966x_ptp_irq_handler()` consumes the two-step timestamp FIFO and completes SKB timestamps. `lan966x_ptp_rxtstamp()` attaches RX hardware timestamps. PHC operations are `lan966x_ptp_gettime64()`, `settime64`, `adjtime`, `adjfine`, `verify`, and `enable`.

Control flow: RX timestamp filters add or remove VCAP IS2 trap rules for L2 PTP and UDP/IPv4/IPv6 event/general PTP ports. Existing trap rules are modified by clearing or setting ingress-port mask bits so multiple ports share one rule ID. TX classification uses `ptp_classify_raw()` and `ptp_parse_header()` to choose no-op, one-step, or two-step rewrite operations and IFH PDU type. Two-step TX queues SKBs under a global ID budget, and the IRQ handler matches hardware-returned IDs back to queued SKBs before reporting `skb_tstamp_tx()`.

State and persistence: software state includes `lan966x->phc[]`, `ptp_clock_lock`, `ptp_ts_id_lock`, `ptp_lock`, `ptp_skbs`, per-port `tx_skbs`, `ts_id`, `ptp_tx_cmd`, and `ptp_rx_cmd`. Hardware state includes PTP domain counters, TOD access pin registers, waveform registers, pin interrupt masks, and VCAP PTP trap rules. `phc->hwtstamp_config` stores the last timestamping configuration.

Dependencies and integration: integrates with Linux PTP clock framework, skb timestamp APIs, ptp packet classifiers, netdev hwtstamp configuration, LAN966x IFH rewrite metadata, and the shared VCAP API. TAPRIO depends on `lan966x_ptp_gettime64()` and `lan966x_ptp_get_period_ps()`.

Risks: shared physical pins across PHCs require strict `verify()` enforcement; TOD access uses a common access pin protected by `ptp_clock_lock`. Trap-rule mask logic must stay consistent with `num_phys_ports` and VCAP mask semantics. TX timestamp accounting has a 512-ID limit and timeout cleanup; missed IRQs or ID mismatches can leak timestamp requests until aged. Large time adjustments fall back to read-modify-set and are not exact. Test signals include `phc2sys`/`testptp` get/set/adj tests, one-step and two-step TX timestamping, RX filters for L2/IPv4/IPv6 PTP, VCAP trap add/remove across multiple ports, extts/perout pin conflicts across PHCs, and IRQ-path stress with more than 512 pending timestamp attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_regs.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_regs.h

Purpose: this autogenerated header is the LAN966x register-address and bitfield vocabulary used by the driver. It maps named hardware targets and registers to the tuple format consumed by the LAN966x register accessors and provides `SET`/`GET` helpers for individual fields.

Important APIs and types: `enum lan966x_target` assigns hardware target IDs for AFI, ANA, CHIP_TOP, CPU, DEV, FDMA, GCB, ORG, PTP, QS, QSYS, REW, SYS, VCAP, and `NUM_TARGETS`. Register macros such as `DEV_CLOCK_CFG(t)`, `ANA_PGID(g)`, `QSYS_TAS_CFG_CTRL`, `PTP_DOM_CFG`, `REW_PORT_CFG(r)`, and `VCAP_UPDATE_CTRL(t)` expand through `__REG(...)` into address metadata. Field helpers follow a consistent pattern: a mask macro, `_SET(x)` using `FIELD_PREP`, and `_GET(x)` using `FIELD_GET`.

Control flow: there is no runtime control flow in this header. Its control effect is indirect: C files compose bitfield values with these macros and pass register tuples to `lan_rd`, `lan_wr`, and `lan_rmw`. The header therefore defines which hardware blocks are reachable and how values are packed for reads and writes.

State and persistence: no software state is stored. The header describes persistent hardware state in register blocks for switching, MAC/PCS, QoS/scheduling, PTP, FDMA, rewriting, and VCAP caches/constants. Because it is generated from hardware descriptions, source provenance and consistency with silicon revision are part of the state contract.

Dependencies and integration: includes Linux `bitfield.h`, `types.h`, and `bug.h`. It is pulled by LAN966x implementation files through `lan966x_main.h` and underpins most register programming in port, PTP, switchdev, QoS, TAPRIO, FDMA, VCAP, and debug paths.

Risks: generated definitions must match the exact LAN966x hardware revision; stale offsets or widths cause silent hardware misprogramming. Callers rely on field widths for validation, but many values are only checked locally in the functional files. Some writes combine several fields, so an incorrect mask can overwrite unrelated hardware state. Test signals are primarily compile coverage, register read/write smoke tests on target hardware, functional validation of every block that uses the macros, and generated-header diff review against upstream hardware descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_switchdev.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_switchdev.c

Purpose: this file connects LAN966x ports to Linux switchdev and netdevice notifier events. It handles bridge/LAG join and leave, bridge port flags, STP learning/forwarding state, VLAN and MDB object offload, FDB event forwarding, multicast snooping, and notifier registration.

Important APIs and functions: `lan966x_register_notifier_blocks()` and `lan966x_unregister_notifier_blocks()` register netdevice, switchdev, and blocking switchdev notifiers. `lan966x_port_changeupper()` and `lan966x_port_prechangeupper()` process bridge/LAG upper changes. `lan966x_port_stp_state_set()` updates learning and source PGID forwarding masks. `lan966x_update_fwd_mask()` writes per-source PGIDs including CPU forwarding and LAG exclusion. Attribute/object handlers dispatch bridge flags, ageing, VLAN filtering, multicast disabled state, VLAN add/del, and MDB add/del.

Control flow: netdevice events first distinguish LAN966x ports from foreign devices. For foreign bridge/LAG upper changes, the code validates that a bridge does not mix LAN966x with foreign ports and does not combine multiple LAN966x switch instances. LAN966x port upper changes offload bridge ports through `switchdev_bridge_port_offload()` or delegate LAG operations. Switchdev events use kernel helper dispatchers to target LAN966x devices and call FDB, attribute, and object handlers. Blocking notifier paths handle potentially sleeping VLAN/MDB operations.

State and persistence: software state includes `lan966x->bridge`, `bridge_mask`, `bridge_fwd_mask`, per-port `learn_ena`, `mcast_ena`, and `bond` references. Hardware state includes ANA PGIDs for multicast/unicast/broadcast flooding, source PGIDs, CPU forward config for IGMP/MLD/IPMC control copies, ANA learning enable, VLAN awareness, host VLAN rewrites, MAC ageing, and MDB/FDB/VLAN tables via helper modules.

Dependencies and integration: integrates with Linux bridge/switchdev notifiers, FDB/MDB/VLAN helper code elsewhere in the LAN966x driver, LAG support, and netlink extack diagnostics. It depends on generated ANA register macros for flooding and learning state.

Risks: bridge admission policy is intentionally strict; bugs can either reject valid topologies or allow unsupported foreign/multi-switch bridges. FWD mask handling must coordinate with LAG masks to avoid loops or blackholes. Multicast snooping toggles clear/restore MDB entries and rewrite IP multicast PGIDs, so order matters. Test signals include bridge join/leave, VLAN filtering toggles, STP state transitions, FDB learning and flush on unoffload, multicast snooping on/off with MDB restore, LAG inside bridges, and rejection of foreign or multi-switch bridge topologies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_switchdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_taprio.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_taprio.c

Purpose: this file offloads TAPRIO time-aware shaper schedules to the LAN966x TAS hardware. It validates tc-taprio schedules, manages per-port hardware lists, allocates global gate-control-list entries, computes safe base times from the PHC, and initializes/deinitializes TAS state.

Important APIs and functions: `lan966x_taprio_add()` validates and installs a schedule. `lan966x_taprio_del()` shuts schedules down. `lan966x_taprio_speed_set()` updates the TAS profile link-speed field used for guard band calculations. `lan966x_taprio_init()` configures TAS state-machine revisit delay, list count, always-guard-band mode, and per-port profile numbers. `lan966x_taprio_deinit()` tears schedules down for all ports.

Control flow: each port owns two list slots, allowing pending/admin/operating transitions. `lan966x_taprio_find_list()` prefers replacing a pending list, then an admin list, while tracking the currently operating list as obsolete target. `lan966x_taprio_check()` rejects unsupported cycle extensions, too many GCL entries, invalid intervals, unsupported commands, total interval overflow, and cycle times shorter than interval sum. `lan966x_taprio_gcl_free_get()` scans all non-admin lists to mark globally used GCL entries. `lan966x_taprio_gcl_setup()` links free entries into a circular list. `lan966x_taprio_new_base_time()` uses the PTP clock to move base time safely into the future before programming TAS start registers.

State and persistence: state is mostly in QSYS TAS registers: list state, selected list/GCL entry, list base, GCL command/time/next pointer, base time, cycle time, obsolete list, profile link speed, and gate state. No durable software copy of the schedule is kept here. Shutdown restores all queues open if an operating list is stopped with gates closed.

Dependencies and integration: integrates with tc TAPRIO offload via `lan966x_tc.c`, PTP PHC time for scheduling, port link-up speed updates, and generated QSYS TAS register macros.

Risks: list-state reads are selected by writing `QSYS_TAS_CFG_CTRL_LIST_NUM`, so concurrent TAS operations would need serialization by higher-level context. GCL allocation is global and depends on accurately walking circular lists. Time arithmetic mixes `ktime_t`, u32 cycle times, and current PHC time; bad base-time calculation can miss the hardware activation window. Test signals include valid/invalid schedule replacement, pending-to-operating transitions, deletion while gates are closed, GCL exhaustion across ports, link speed changes, base times in past/near future/far future, and packet gating observations with PTP-synchronized traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_taprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tbf.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tbf.c

Purpose: this file offloads tc Token Bucket Filter shaping to LAN966x hierarchical scheduler elements. It supports both root/port shaping and per-queue shaping depending on the qdisc parent handle.

Important APIs and functions: `lan966x_tbf_add()` validates the parent, maps it to a scheduler element, converts Linux rate and burst parameters to hardware units, enables frame-mode shaping, and programs committed information rate/burst registers. `lan966x_tbf_del()` resolves the same scheduler element, disables shaping mode, and clears CIR/burst.

Control flow: a root qdisc maps to `SE_IDX_PORT + chip_port`; a class/queue parent maps to `SE_IDX_QUEUE + chip_port * NUM_PRIO_QUEUES + queue`. Non-root queue indices are extracted with `TC_H_MIN(parent) - 1` and rejected when outside `NUM_PRIO_QUEUES`. Rate bytes/s are converted to kbps-like units through bytes-to-bits and a hardware 100 kbps unit, rounded up and clamped away from zero. Burst is converted to 4 KiB units, rounded up and clamped away from zero. Field-width checks reject values too large for QSYS fields.

State and persistence: no software state is persisted. Hardware state lives in `QSYS_SE_CFG(se_idx)` and `QSYS_CIR_CFG(se_idx)` until destroyed or overwritten. Delete returns success after clearing the hardware state even if the previous configuration is unknown.

Dependencies and integration: called from `lan966x_tc_setup_qdisc_tbf()` in `lan966x_tc.c`; depends on scheduler index constants and QSYS register macros from `lan966x_main.h`/`lan966x_regs.h`.

Risks: parent-handle interpretation must match tc queue numbering. Hardware unit conversion can materially differ from requested rates, especially at low rates where values round up to one unit. Only CIR/CBS are programmed; unsupported TBF semantics are not represented here. Test signals include root and per-queue TBF add/delete, rejection of invalid queue parents and oversized rates/bursts, observed egress throughput around rounding boundaries, and interaction with CBS/ETS/TAPRIO scheduler state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tbf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tc.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tc.c

Purpose: this file is the LAN966x traffic-control entry point. It dispatches qdisc offloads and classifier block callbacks to specialized modules for mqprio, taprio, tbf, cbs, ets, matchall, and flower handling.

Important APIs and functions: `lan966x_tc_setup()` is the netdev `ndo_setup_tc`-style dispatcher. It recognizes `TC_SETUP_QDISC_MQPRIO`, `TAPRIO`, `TBF`, `CBS`, `ETS`, and `TC_SETUP_BLOCK`. `lan966x_tc_setup_block()` binds clsact ingress/egress callbacks using `flow_block_cb_setup_simple()`. `lan966x_tc_block_cb_ingress()` and `_egress()` route classifier setup to `lan966x_tc_matchall()` or `lan966x_tc_flower()`.

Control flow: mqprio sets `mqprio->qopt.hw = TC_MQPRIO_HW_OFFLOAD_TCS` and adds or deletes hardware TCs based on `num_tc`. TAPRIO, TBF, and ETS switch over command enums and call add/delete helpers; CBS uses its enable flag. Block setup only supports clsact ingress and egress binder types; ingress also records `port->tc.ingress_shared_block = f->block_shared`. Unsupported qdisc, block binder, and classifier setup types return `-EOPNOTSUPP`.

State and persistence: this file stores little state directly beyond the ingress shared-block flag and the global `lan966x_tc_block_cb_list` callback registry. Hardware state persists in the modules it dispatches to. Classifier state is primarily maintained by flow block infrastructure and VCAP/filter helper modules.

Dependencies and integration: integrates with Linux `pkt_cls`, `pkt_sched`, flow block infrastructure, netdev private `lan966x_port`, and driver-local modules for shaping/scheduling and VCAP classifiers. It is the central adapter between kernel tc APIs and LAN966x offload implementations.

Risks: command dispatch must track kernel tc enum evolution. Shared block handling is only explicitly recorded for ingress, so code depending on this flag must not assume egress symmetry. Errors from leaf modules propagate directly to tc. Test signals include exercising each supported qdisc command, binding/unbinding clsact ingress and egress blocks, unsupported binder rejection, shared block behavior, and classifier replace/destroy/stats through both flower and matchall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tc_flower.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tc_flower.c

Purpose: this file translates tc flower filters into LAN966x VCAP rules. It parses supported flow dissector keys, validates action sequences and chain transitions, selects VCAP action sets, installs rules, deletes rules by cookie, and reports hardware counters.

Important APIs and functions: `lan966x_tc_flower()` dispatches replace/destroy/stats. `lan966x_tc_flower_add()` allocates a VCAP rule for the tc chain, parses dissectors, adds chain-link target keys/actions, maps tc actions, validates the rule, and commits it. `lan966x_tc_flower_use_dissectors()` iterates the handler table for Ethernet, IPv4/IPv6, control/fragment, ports, basic proto, VLAN/CVLAN, TCP, ARP, and IP keys. `lan966x_tc_flower_action_check()` enforces action uniqueness, hardware stats support, legal goto placement, and trap/pass conflicts.

Control flow: basic parsing records L3/L4 protocol and emits VCAP keys differently for IS1, IS2, and ES0. IS1 has special handling for ETYPE length/SNAP/IP4 indicators and TCP/UDP hints; IS2 supports additional known ethertypes. VLAN keys use IS1-specific `VID0/PCP0` fields or classified VLAN fields in other VCAPs. Control keys map fragment flags to `L3_FRAGMENT` and `L3_FRAG_OFS_GT0`. Actions support trap only in IS2, goto chain links from IS1 to IS2 via PAG or IS1 to ES0 via ISDX, and VLAN pop only in ES0 by forcing untagged output.

State and persistence: software state is VCAP rule metadata: cookie, priority, chain index, selected actionset, keys, actions, counters, and generated rule ID. Persistent hardware state resides in the VCAP tables through the shared VCAP API. Stats are read by cookie and reported as immediate hardware packet counts.

Dependencies and integration: depends on Linux flow dissector/action APIs, VCAP API/client helpers, `vcap_tc` common flower parsers, LAN966x VCAP chain layout, and driver constants such as `LAN966X_PMM_REPLACE`.

Risks: unsupported combinations must fail early with extack; otherwise rules can validate against the wrong keyset or actionset. Chain-link semantics are narrow and currently only support IS1-to-IS2 and IS1-to-ES0. Deletion loops over all rules with the same cookie, so cookie uniqueness assumptions matter. Test signals include flower matches for MAC/IP/TCP/UDP/VLAN/ARP/fragment keys, invalid ethertype/key combinations per VCAP, action duplicate and trap/pass rejection, goto chain validation, ES0 VLAN pop, stats reads, and deletion of multiple rules sharing a cookie.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tc_flower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tc_matchall.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tc_matchall.c

Purpose: this file handles tc `matchall` classifier offload for whole-port actions. It supports one action per filter and delegates policing, mirroring, and goto-chain actions to LAN966x helper modules.

Important APIs and functions: `lan966x_tc_matchall()` dispatches replace, destroy, and stats commands. `lan966x_tc_matchall_add()` enforces exactly one action and maps `FLOW_ACTION_POLICE`, `FLOW_ACTION_MIRRED`, and `FLOW_ACTION_GOTO`. `lan966x_tc_matchall_del()` chooses the delete helper by comparing the filter cookie with per-port police and mirror IDs. `lan966x_tc_matchall_stats()` reports police or mirror stats and rejects unsupported goto stats.

Control flow: replace validates `flow_offload_has_one_action()`, then calls `lan966x_police_port_add()`, `lan966x_mirror_port_add()`, or `lan966x_goto_port_add()` with ingress/egress context and extack. Destroy checks whether the cookie belongs to the active police ID, ingress mirror ID, or egress mirror ID, otherwise treats it as a goto rule. Stats follow the same cookie matching but only police and mirror expose stats.

State and persistence: this file does not store state itself. It relies on `port->tc.police_id`, `port->tc.ingress_mirror_id`, and `port->tc.egress_mirror_id` maintained by delegated helpers. Hardware state is in policing/mirroring/goto programming outside this file.

Dependencies and integration: called by `lan966x_tc.c` classifier block callbacks; integrates with driver policing, mirroring, and VCAP goto helpers. Uses kernel flow action structures and netlink extack for diagnostics.

Risks: one-action-only policy rejects valid Linux matchall filters that combine actions. Cookie-based delete routing can misroute if helper state is stale or cookies collide. Stats for goto actions are unsupported, so users may see errors for stats requests after a goto offload. Test signals include add/delete/stats for police and mirror on ingress/egress, add/delete for goto, duplicate-action rejection, unsupported action rejection, and stale-cookie destroy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tc_matchall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_ag_api.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_ag_api.c

Purpose: this autogenerated file describes the LAN966x VCAP capabilities consumed by the generic VCAP API. It defines key fields, key field sets, action fields, action field sets, typegroups, printable names, and the exported `lan966x_vcaps[]` and `lan966x_vcap_stats` descriptors.

Important APIs and data: the exported `lan966x_vcaps[]` has three VCAP instances: IS1 (`rows = 192`, `sw_count = 4`, `sw_width = 96`, `act_width = 123`), IS2 (`rows = 64`, `sw_count = 4`, `sw_width = 96`, `act_width = 31`), and ES0 (`rows = 256`, `sw_count = 1`, `sw_width = 96`, `act_width = 65`). IS1 keysets include normal, IPv4/IPv6 5-tuples, 7-tuple, double VID, RT, and DMAC/VID. IS2 keysets include MAC etype/LLC/SNAP, ARP, IPv4 TCP/UDP/other, IPv6 std/TCP/UDP/other, OAM, and SMAC/SIP variants. ES0 exposes VID. Action sets include IS1 S1 classification actions, IS2 base/smac-sip actions, and ES0 VID rewrite actions.

Control flow: there is no executable algorithm beyond static descriptor initialization. Runtime VCAP code indexes these arrays to validate rule fields, pack keys/actions into the correct widths, select typegroup bits, print diagnostics, and expose statistics. The name arrays give stable string labels for debugfs and errors.

State and persistence: no mutable software state exists here. The data is a compiled hardware contract. It controls persistent hardware rule layout indirectly by telling the VCAP API how many rows exist, how wide streams/actions/counters are, what typegroups identify each superword width, and where each key/action field sits.

Dependencies and integration: includes VCAP API types through the header path. `lan966x_tc_flower.c`, PTP trap setup, VCAP debugfs, and lower VCAP programming code depend on these descriptors to validate and encode rules. The companion header exports the arrays.

Risks: because this is generated metadata, correctness depends on generator input matching the silicon and the shared VCAP enum definitions. A single offset/width/typegroup mismatch can make valid tc/PTP rules match the wrong packets or program wrong actions. Descriptor size arrays must stay aligned with enum indices. Test signals include VCAP rule validation for every supported key/action set, debugfs dump readability, tc flower and PTP trap behavior across IS1/IS2/ES0, counter reads, and comparison against upstream generated LAN966x VCAP descriptions after regeneration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_ag_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_ag_api.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_ag_api.h

Purpose: this small generated/public header exposes LAN966x VCAP capability descriptors to the rest of the driver.

Important APIs and types: it includes `vcap_api.h` and declares `extern const struct vcap_info lan966x_vcaps[];` and `extern const struct vcap_statistics lan966x_vcap_stats;`. The include guard is `__LAN966X_VCAP_AG_API_H__`.

Control flow: no control flow. Its role is linkage: implementation files include it to reference the generated VCAP descriptor arrays defined in `lan966x_vcap_ag_api.c`.

State and persistence: no local state. The declared objects are immutable descriptor tables compiled into the driver. They define how VCAP hardware state is interpreted and programmed by consumers.

Dependencies and integration: consumed by VCAP debugfs and any initialization path that needs LAN966x VCAP descriptors. It depends on the shared VCAP API type definitions. The header is intentionally narrow, keeping generated table internals private to the `.c` file.

Risks: declarations must stay type-compatible with the generated `.c` definitions and shared VCAP API. If the VCAP API changes these structures, this header and implementation must regenerate together. Test signals are compile/link coverage, VCAP initialization, and debugfs/statistics consumers resolving both exported arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_ag_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_debugfs.c

Purpose: this file provides per-port VCAP debug output. It reads current hardware parser/key-selection state for IS1, IS2, and ES0 and prints human-readable status through the VCAP debug output callback.

Important APIs and functions: `lan966x_vcap_port_info()` is the exported entry point. It finds the `lan966x_port`, retrieves the VCAP descriptor name from `vctrl->vcaps[admin->vtype]`, and dispatches to type-specific printers. `lan966x_vcap_is1_port_keys()` prints IS1 enable state and lookup key-selection modes for other, IPv4, IPv6, and RT traffic. `lan966x_vcap_is2_port_keys()` prints IS2 enable state and lookup modes for SNAP, OAM, ARP, IPv4 other, IPv4 TCP/UDP, and IPv6. `lan966x_vcap_es0_port_keys()` prints ES0 enable state from rewrite port config.

Control flow: each printer reads the relevant ANA or REW register for the port, decodes fields with generated register helpers, and emits labels such as normal, 7tuple, dbl_vid, dmac_vid, mac_llc, mac_snap, ip4_other, ipv6_std, or mac_etype. IS1 loops over `admin->lookups` and reads `ANA_VCAP_S1_CFG(port, lookup)` for each lookup. IS2 reads `ANA_VCAP_S2_CFG(port)` and interprets per-lookup disable bits or IPv6 key selection bits. Unknown VCAP types print `no info`.

State and persistence: the file does not mutate state. It observes persistent hardware parser configuration and the in-memory VCAP control/admin descriptors. Output is transient debugfs text.

Dependencies and integration: depends on `lan966x_vcap_ag_api.h`, VCAP API/client types, netdev private port mapping, generated ANA/REW register macros, and whatever debugfs plumbing calls `lan966x_vcap_port_info()`.

Risks: debug output can become misleading if field decoding does not match hardware bit layouts. The IS2 IPv6 switch masks with `(0x3 << l)` and compares with selection constants, so constant encoding must align with lookup bit positions. Since it is read-only, operational risk is low, but diagnostics quality matters for tc/PTP VCAP debugging. Test signals include debugfs dumps with IS1/IS2/ES0 enabled and disabled, multiple lookup configurations, known parser mode changes from tc/VCAP setup, and comparison of printed labels with raw register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_debugfs.c -->
