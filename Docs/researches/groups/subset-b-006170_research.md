# subset-b-006170 bridge research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_netlink.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_netlink.c

## Purpose
`br_netlink.c` is the bridge driver's rtnetlink control plane. It registers the `"bridge"` link kind, validates bridge link attributes, creates/deletes bridge devices, applies bridge-wide and per-port changes, dumps bridge/port state, emits link notifications, and parses `AF_BRIDGE` nested attributes for VLANs, VLAN tunnel mappings, MRP, CFM, and MST state.

## Important APIs, types, and functions
- `br_link_ops` wires bridge setup, validation, `newlink`, `changelink`, `dellink`, bridge attribute sizing/fill, link xstats, and slave port operations into rtnetlink.
- `br_netlink_init()` / `br_netlink_fini()` register/unregister bridge VLAN rtnetlink support, `rtnl_af_ops`, and `rtnl_link_ops`.
- `br_getlink()`, `br_fill_ifinfo()`, `br_info_notify()`, and `br_ifinfo_notify()` build `RTM_NEWLINK` payloads for bridge masters and bridge ports.
- `br_setlink()` and `br_dellink()` process legacy and nested `IFLA_PROTINFO`/`IFLA_AF_SPEC` requests for ports and bridge masters.
- `br_changelink()` applies bridge-wide `IFLA_BR_*` options such as STP timing, STP state/mode, VLAN filtering/protocol/default PVID, group forwarding masks/address, FDB flush/limits, multicast options, netfilter toggles, and boolean option batches.
- `br_setport()` applies `IFLA_BRPORT_*` attributes including state, cost, priority, hairpin, guard/protect, flood/learning flags, VLAN tunnel mode, neighbor suppression, isolation, locked/MAB mode, backup port, EHT host limit, multicast router, and backup nexthop ID.
- `br_process_vlan_info()` and `br_afspec()` handle singleton and ranged VLAN add/delete operations, generate `RTM_NEWVLAN`/`RTM_DELVLAN` notifications, and dispatch optional MRP/CFM/MST/tunnel nested attributes.
- `br_get_size()`, `br_fill_info()`, `br_port_info_size()`, `br_port_fill_attrs()`, `br_get_link_af_size_filtered()`, and link xstats helpers keep netlink dump size accounting aligned with actual `nla_put*()` output.

## Control flow
Bridge creation enters through `br_dev_newlink()`: register the netdevice, optionally adopt a user MAC into the STP bridge ID, then call `br_changelink()` so creation-time attributes are applied through the same path as later changes. A failure after registration calls `br_dev_delete()`.

Per-port updates through `br_setlink()` first parse `IFLA_PROTINFO`; nested modern attributes are validated against `br_port_policy`, then `br_setport()` runs under `br->lock`. A non-nested byte remains supported for old RSTP state changes. `IFLA_AF_SPEC` is then parsed by `br_afspec()` for VLAN, VLAN tunnel, MRP, CFM, and MST subcommands. Any effective change triggers `br_ifinfo_notify(RTM_NEWLINK, ...)`.

Bridge-wide updates through `br_changelink()` are ordered and fail-fast. STP timing calls `br_set_forward_delay()`, `br_set_hello_time()`, `br_set_max_age()`, and `br_set_ageing_time()`. STP mode cannot change while STP is enabled unless the same request turns STP off. VLAN operations are delegated to VLAN helpers, multicast operations to multicast helpers, netfilter toggles to `br_opt_toggle()`, and boolean batches to `br_boolopt_multi_toggle()`.

Dump paths precompute enough space, open nested attributes only when requested, use RCU for VLAN and backup-port reads, and cancel empty `IFLA_AF_SPEC` nests. Link xstats support restart by updating `*prividx` on `-EMSGSIZE`.

## State and persistence
All state is in kernel memory in `struct net_bridge`, `struct net_bridge_port`, VLAN groups, timers, and FDB/multicast tables. Netlink changes do not persist across bridge destruction or reboot. State visibility is via rtnetlink notifications/dumps and xstats. Synchronization uses RTNL, `br->lock`, RCU, `READ_ONCE`/`WRITE_ONCE` for selected fields, and helper-specific locks.

## Dependencies and integration points
This file integrates with rtnetlink, `AF_BRIDGE`, VLAN, MST, MRP, CFM, multicast snooping, bridge netfilter, switchdev, STP, FDB, netdevice core, and uapi bridge attributes. `br_switchdev_set_port_flag()` is called before committing hardware-offloadable port flag changes, so driver rejection rolls back software flags.

## Risks and edge cases
Size accounting must match every emitted attribute; mismatches surface as `-EMSGSIZE` warnings or truncated dumps. Range handling for VLANs and tunnel mappings must reset the pending range after an end marker and reject malformed ranges. MAB requires locked ports with learning enabled and flushes locked FDB entries when disabled. Group forwarding masks reject restricted link-local protocols on bridge masters and MAC pause on ports. Changing STP mode while active is guarded to avoid control-plane ownership ambiguity.

## Test signals
Useful coverage includes `ip link add type bridge` with creation attributes, repeated `ip link set type bridge` changes, port `IFLA_BRPORT_*` toggles, invalid VLAN/tunnel ranges, compressed VLAN dumps, xstats dump restart behavior, STP mode/state transitions, MAB enable/disable FDB flushing, bridge multicast/netfilter option toggles with configs on/off, and switchdev driver rejection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_netlink_tunnel.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_netlink_tunnel.c

## Purpose
`br_netlink_tunnel.c` implements the netlink view and mutation path for per-VLAN tunnel metadata on bridge ports. It lets userspace dump VLAN-to-tunnel-ID mappings and add/delete singleton or range mappings when a port has `BR_VLAN_TUNNEL` enabled.

## Important APIs, types, and functions
- `struct vtunnel_info` comes from `br_private_tunnel.h` and carries `tunid`, `vid`, and range flags parsed from netlink.
- `br_parse_vlan_tunnel_info()` validates nested `IFLA_BRIDGE_VLAN_TUNNEL_*` attributes.
- `br_process_vlan_tunnel_info()` consumes singleton or begin/end range requests and calls `br_vlan_tunnel_info()` for each VLAN.
- `br_vlan_tunnel_info()` delegates add/delete to `nbp_vlan_tunnel_info_add()` and `nbp_vlan_tunnel_info_delete()`.
- `br_get_vlan_tunnel_info_size()` and `br_fill_vlan_tunnel_info()` count and emit dump entries, compressing consecutive VLAN/tunnel-ID runs into range begin/end records.
- `vlan_tunid_inrange()` compares consecutive tunnel IDs after converting the stored 64-bit tunnel ID to a 32-bit key.

## Control flow
Dump sizing counts usable VLAN entries with nonzero tunnel IDs under RCU. Dump filling walks the sorted VLAN list, skips inactive/context-only VLANs and entries without `tinfo.tunnel_dst`, groups consecutive VLAN IDs whose tunnel IDs also increment by one, and writes either one nested mapping or range begin/end mappings.

Mutation starts in `br_afspec()` in `br_netlink.c`, which requires a bridge port with `BR_VLAN_TUNNEL`. The parser requires both tunnel ID and VLAN ID, rejects VLAN IDs greater than or equal to `VLAN_VID_MASK`, and records optional range flags. A range begin is cached in `tinfo_last`; a range end must match the pending begin and have equal VLAN and tunnel-ID span. The loop applies each mapping and coalesces notification ranges through `__vlan_tunnel_handle_range()`.

## State and persistence
Mappings live in per-port VLAN group entries as `struct br_tunnel_info` (`tunnel_id` and RCU `metadata_dst`). The file does not allocate the metadata itself; it calls VLAN tunnel helpers. Changes are in-memory and observable through bridge VLAN netlink notifications and future dumps.

## Dependencies and integration points
This file depends on bridge VLAN filtering data structures, `dst_metadata`, rtnetlink nested attribute parsing, `br_vlan_find()`, `br_vlan_can_enter_range()`, and `br_vlan_notify()`. It is enabled only when the port-level `BR_VLAN_TUNNEL` flag is set by netlink/sysfs control paths.

## Risks and edge cases
Range requests are rejected if a new begin appears before an end, an end appears without a begin, or VLAN and tunnel-ID spans differ. Dump sizing checks `tinfo.tunnel_id`, while dump filling checks `tinfo.tunnel_dst`; any inconsistency in lower helpers could skew size estimates. Notification range coalescing depends on the current VLAN entry being found after mutation.

## Test signals
Exercise singleton add/delete, valid ranges with matching VID/VNI spans, malformed ranges, dump compression, disabling `BR_VLAN_TUNNEL` after mappings exist, and operation with inactive/global-context VLAN entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_netlink_tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_nf_core.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_nf_core.c

## Purpose
`br_nf_core.c` provides the fake routing destination used by bridge netfilter. Bridged packets sometimes travel through IPv4 netfilter code that expects route/dst metadata, so the bridge initializes a synthetic `rtable` with enough fields for PMTU/refragmentation and targets such as `REJECT`.

## Important APIs, types, and functions
- `fake_dst_ops` is a minimal `dst_ops` implementation with no-op PMTU/redirect, null metrics copy-on-write/neighbour lookup, and MTU derived from `dst->dev->mtu`.
- `br_netfilter_rtable_init()` initializes `br->fake_rtable` and bridge metric storage.
- `br_nf_core_init()` and `br_nf_core_fini()` register/destroy `fake_dst_ops` accounting through `dst_entries_init()` and `dst_entries_destroy()`.

## Control flow
Module initialization prepares the dst operations. Per-bridge initialization calls `br_netfilter_rtable_init()`, sets an initial reference, points `dst.dev` at the bridge device, initializes metrics from `br->metrics`, stores MTU, sets `DST_NOXFRM | DST_FAKE_RTABLE`, and attaches `fake_dst_ops`.

## State and persistence
State is per-bridge in-memory route/dst metadata and a static global `dst_ops`. No persistent storage exists. The fake route is valid only for the bridge lifetime.

## Dependencies and integration points
The file depends on the route/dst infrastructure and is compiled through `CONFIG_BRIDGE_NETFILTER`. `br_private.h` exposes `br_netfilter_rtable_init()` as a stub when bridge netfilter is disabled.

## Risks and edge cases
The fake route intentionally leaves many operations inert. Future netfilter code that expects additional dst behavior would require extending this file. MTU must track bridge device MTU at initialization and any later updates handled elsewhere.

## Test signals
Bridge netfilter tests should include IPv4/IPv6/ARP netfilter paths, PMTU-sensitive fragmented traffic, bridge MTU changes, and iptables/nftables reject/forwarding cases with `br_netfilter` enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_nf_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_private.h -->
# sources/distributed-fs/ceph-client/net/bridge/br_private.h

## Purpose
`br_private.h` is the central internal contract for the Linux bridge driver. It defines core bridge/port/VLAN/FDB/MDB state, feature option bits, skb control-block layout, inline helpers, subsystem prototypes, and compile-time stubs for optional bridge features.

## Important APIs, types, and functions
- Core types: `struct net_bridge`, `struct net_bridge_port`, `struct net_bridge_vlan`, `struct net_bridge_vlan_group`, `struct net_bridge_fdb_entry`, `struct net_bridge_mdb_entry`, `struct net_bridge_port_group`, `struct net_bridge_mcast`, and `struct br_input_skb_cb`.
- Identity and STP helpers: `bridge_id`, `mac_addr`, `port_id`, `br_is_root_bridge()`, `br_port_get_rcu()`, `br_port_get_rtnl()`, `br_port_get_check_rcu()`, and `br_port_get_check_rtnl()`.
- VLAN helpers: `br_vlan_should_use()`, `br_vlan_valid_id()`, `br_vlan_valid_range()`, `br_get_pvid()`, `br_vlan_flags()`, `br_vlan_get_state()`, `br_vlan_set_state()`, and `br_vlan_state_allowed()`.
- Multicast helpers: router/querier checks, VLAN multicast-context predicates, source/group mode helpers, and no-op stubs when `CONFIG_BRIDGE_IGMP_SNOOPING` is off.
- Option APIs: `br_opt_get()`, `br_opt_toggle()`, `br_boolopt_toggle()`, `br_boolopt_multi_toggle()`, and `br_boolopt_multi_get()`.
- Subsystem prototypes cover device setup, FDB, forwarding, bridge interface management, input, multicast, VLAN, MST, netfilter, STP, MRP, CFM, netlink, sysfs, switchdev, and ARP/ND proxy suppression.

## Control flow
This header does not run control flow directly, but it shapes all bridge subsystem interactions. Data-plane files use `BR_INPUT_SKB_CB()` for per-packet forwarding metadata. Control-plane files mutate `struct net_bridge` and `struct net_bridge_port` fields declared here. Optional features are hidden behind compile-time stubs so call sites can stay mostly unconditional while unsupported operations return `-EOPNOTSUPP`, no-op, or default values.

## State and persistence
The declared state is in-memory kernel state. `struct net_bridge` owns bridge-wide timers, FDB/MDB tables, VLAN group, multicast context, STP identity/timers, option bits, switchdev hardware-domain state, and optional MRP/CFM lists. `struct net_bridge_port` owns per-port flags, VLAN group, backup port, STP state/timers/statistics, multicast context, sysfs name, netpoll, and switchdev offload metadata. RCU, spinlocks, atomics, seqcounts, refcounts, rhashtables, hlists, rbtrees, timers, delayed work, and per-CPU stats encode lifetime and concurrency expectations.

## Dependencies and integration points
The header ties the bridge to netdevice, rtnetlink, VLAN, route/dst, IPv6 fib, tc skb extensions, rhashtable, netpoll, switchdev, netfilter, sysfs, multicast, MRP, CFM, and UAPI bridge definitions. It is included by nearly every bridge implementation file and is the primary place where optional features present a uniform internal API.

## Risks and edge cases
Because this file defines shared layout and inline locking assumptions, mistakes have broad blast radius. Risks include using VLAN master/context entries as active entries without `br_vlan_should_use()`, reading RCU pointers without the required protection, changing option enum order in ways that break bit semantics, and relying on optional feature stubs without checking `-EOPNOTSUPP` where user-visible behavior matters.

## Test signals
Broad bridge regression coverage should compile multiple config matrices: VLAN filtering on/off, multicast snooping on/off, bridge netfilter on/off, sysfs on/off, switchdev on/off, MRP/CFM on/off, IPv6 on/off, and TC skb extensions on/off. Runtime tests should stress concurrent port/VLAN/FDB/MDB changes, RCU-protected port deletion, netlink dump races, and data-plane forwarding metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_private_cfm.h -->
# sources/distributed-fs/ceph-client/net/bridge/br_private_cfm.h

## Purpose
`br_private_cfm.h` defines the bridge Connectivity Fault Management internal API and state objects. It bridges CFM netlink/UAPI concepts to in-kernel MEP, peer MEP, continuity-check, transmit, receive, and status tracking.

## Important APIs, types, and functions
- Configuration structs include `br_cfm_mep_create`, `br_cfm_mep_config`, `br_cfm_maid`, `br_cfm_cc_config`, and `br_cfm_cc_ccm_tx_info`.
- Status structs include `br_cfm_mep_status` and `br_cfm_cc_peer_status`.
- Runtime structs are `br_cfm_mep` and `br_cfm_peer_mep`, which hold hlist membership, instance IDs, RCU bridge-port pointers, peer lists, delayed work, sequence numbers, status flags, RDI, and RCU teardown.
- Exported APIs create/delete MEPs, set MEP and CC config, add/remove peer MEPs, set RDI, and control CCM transmission.

## Control flow
This header is declarative. Callers such as CFM netlink parsing create or configure MEP instances, then CFM implementation code uses delayed work to transmit CCMs until `ccm_tx_end` and to detect missed peer CCMs. Status is later filled into netlink dumps through CFM helpers declared in `br_private.h`.

## State and persistence
CFM state is in `br->mep_list` when `CONFIG_BRIDGE_CFM` is enabled. Per-MEP state tracks configuration, peer list, residence port, transmit lifetime, sequence counters, and local status. Per-peer state tracks received CCM status and missed-count detection. State is in-memory only and protected by the CFM implementation's locking/RCU rules.

## Dependencies and integration points
The header depends on bridge internals and `<uapi/linux/cfm_bridge.h>`. It integrates with `br_netlink.c` through CFM `AF_BRIDGE` attributes and with bridge port lifetime through RCU `b_port` pointers.

## Risks and edge cases
Delayed work and RCU lifetimes must be cancelled/drained before freeing MEP or peer objects. Sequence-number and defect flags must reflect the latest CCM without racing status dumps. Residence port deletion must clear or retire dependent MEPs.

## Test signals
Test MEP create/delete, invalid instance references, peer add/remove, CCM enable/disable with timeout renewal, RDI toggling, port deletion while CFM exists, and status dumps for unexpected opcode/version/level and peer defect flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_private_cfm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_private_mcast_eht.h -->
# sources/distributed-fs/ceph-client/net/bridge/br_private_mcast_eht.h

## Purpose
`br_private_mcast_eht.h` defines Explicit Host Tracking structures and helpers for multicast snooping. EHT tracks hosts and per-source sets for a bridge port group so IGMPv3/MLDv2 source-filtering state can be managed per listener.

## Important APIs, types, and functions
- `BR_MCAST_DEFAULT_EHT_HOSTS_LIMIT` sets the default host-count cap.
- `union net_bridge_eht_addr` stores IPv4 or optional IPv6 addresses.
- `net_bridge_group_eht_host` tracks one host's set entries, filter mode, entry count, and parent port group.
- `net_bridge_group_eht_set_entry` connects one host to one per-source set and carries a timer plus multicast GC hook.
- `net_bridge_group_eht_set` represents a source set with an rb-tree of host entries, timer, parent group, bridge pointer, and GC hook.
- `br_multicast_eht_clean_sets()`, `br_multicast_eht_handle()`, and `br_multicast_eht_set_hosts_limit()` are the main implementation entry points when snooping is enabled.

## Control flow
The multicast implementation calls `br_multicast_eht_handle()` when processing source-filter capable reports. Host/set rbtrees are updated, timers drive expiry, and GC hooks handle deferred destruction. Inline helpers decide whether fast-leave can delete a port group after the last tracked host, enforce host limits, and increment/decrement per-port host counters.

## State and persistence
EHT state lives under each `net_bridge_port_group` in `eht_set_tree` and `eht_host_tree`, with per-port counts in `multicast_eht_hosts_cnt` and limits in `multicast_eht_hosts_limit`. It is in-memory multicast snooping state only.

## Dependencies and integration points
The header depends on bridge multicast structures from `br_private.h`, rbtrees, timers, and optional IPv6. It is consumed by multicast code and exposed through port netlink/sysfs attributes for EHT host limits/counts.

## Risks and edge cases
Host-limit enforcement must avoid counter leaks on partial allocation failures. Fast-leave deletion depends on the host tree being truly empty. Timer/GC teardown must avoid use-after-free while multicast reports and port-group deletion race.

## Test signals
Use IGMPv3/MLDv2 include/exclude report sequences from multiple hosts, host-limit exhaustion, fast-leave behavior, timer expiry, IPv4/IPv6 builds, and port group deletion with active EHT entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_private_mcast_eht.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_private_mrp.h -->
# sources/distributed-fs/ceph-client/net/bridge/br_private_mrp.h

## Purpose
`br_private_mrp.h` defines bridge Media Redundancy Protocol state, software/hardware offload APIs, and on-wire MRP PDU header formats. MRP provides ring and interconnect redundancy distinct from STP.

## Important APIs, types, and functions
- `struct br_mrp` stores one MRP instance with primary/secondary/interconnect ports, ring/interconnect IDs, priorities, roles, states, transition counters, delayed test work, miss counters, monitoring flags, sequence IDs, and RCU destruction.
- `enum br_mrp_hw_support` expresses no support, software-assisted support, or full hardware support.
- Bridge MRP APIs include add/delete, port state/role changes, ring/interconnect state/role changes, and test start calls.
- Switchdev APIs let hardware add/delete MRP instances, set roles/states, and send ring/interconnect tests.
- PDU structs model TLV, common, ring-test, interconnect-test, OUI, and manufacture-data suboption headers.

## Control flow
MRP configuration comes through MRP netlink parsing declared in `br_private.h` and calls the APIs declared here. Runtime test delayed work sends/monitors MRP frames, updates miss counters, and changes ring/interconnect open state. Switchdev return values determine whether software continues protocol processing, assists hardware, or lets hardware own the protocol completely.

## State and persistence
MRP instances live in `br->mrp_list` under `CONFIG_BRIDGE_MRP`. Port pointers are RCU-protected; timers/delayed work drive transient test state. State is in-memory and disappears with the bridge or instance.

## Dependencies and integration points
The header depends on bridge internals and `<uapi/linux/mrp_bridge.h>`. It integrates with netlink `IFLA_BRIDGE_MRP`, switchdev offload, bridge port deletion, and STP exclusion: `br_stp_set_enabled()` rejects STP if MRP is already enabled.

## Risks and edge cases
MRP and STP control the same forwarding state and must not both own a bridge. Offload fallback must avoid duplicate software/hardware frame handling. Delayed work needs careful cancellation on instance deletion and port removal. Packed PDU structs must remain wire-compatible.

## Test signals
Test add/delete of rings and interconnects, role/state changes, test monitoring timeout/miss thresholds, switchdev support levels, port deletion, STP enable rejection while MRP exists, and PDU encode/decode interop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_private_mrp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_private_stp.h -->
# sources/distributed-fs/ceph-client/net/bridge/br_private_stp.h

## Purpose
`br_private_stp.h` declares the internal Spanning Tree Protocol contract: BPDU constants, timer/path-cost limits, the in-kernel config BPDU representation, and STP state-machine/transmit APIs shared across STP implementation files.

## Important APIs, types, and functions
- `BPDU_TYPE_CONFIG` and `BPDU_TYPE_TCN` define supported BPDU kinds.
- Timer bounds encode IEEE 802.1D ranges for hello time, forward delay, and max age; path-cost bounds protect port configuration.
- `struct br_config_bpdu` carries topology flags, root/bridge IDs, root path cost, port ID, and STP timers in jiffies.
- `br_is_designated_port()` tests whether a port's designated bridge/port match the local bridge.
- Prototypes cover root transition, BPDU generation/reception, configuration update, port state selection, topology-change handling, and BPDU send helpers.

## Control flow
The header links `br_stp.c` state-machine logic, `br_stp_bpdu.c` packet encoding/decoding, and `br_stp_timer.c` timer callbacks. Callers hold `br->lock` for most STP state-machine functions, as documented in comments and enforced by implementation patterns.

## State and persistence
No state is stored in the header itself. It defines constants and structs used to mutate `struct net_bridge` and `struct net_bridge_port` STP fields declared in `br_private.h`.

## Dependencies and integration points
It depends on bridge ID and port types from `br_private.h` and is included by STP implementation, netlink/sysfs setters, and bridge initialization paths.

## Risks and edge cases
Timer limits are user-visible through netlink/sysfs and must match validation in setters. The designated-port test assumes bridge IDs are 8-byte comparable. Callers must respect bridge-lock requirements to avoid inconsistent root/port selection.

## Test signals
Compile and runtime STP tests should cover timer validation boundaries, designated-port detection, config and TCN BPDU handling, and state changes with STP disabled, kernel STP, and user STP modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_private_stp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_private_tunnel.h -->
# sources/distributed-fs/ceph-client/net/bridge/br_private_tunnel.h

## Purpose
`br_private_tunnel.h` declares the bridge VLAN tunnel internal API. It connects netlink parsing/dumping to VLAN tunnel storage and data-plane ingress/egress handling.

## Important APIs, types, and functions
- `struct vtunnel_info` is the parsed netlink representation of a tunnel mapping.
- Netlink helpers: `br_parse_vlan_tunnel_info()`, `br_process_vlan_tunnel_info()`, `br_get_vlan_tunnel_info_size()`, `br_fill_vlan_tunnel_info()`, `vlan_tunid_inrange()`, and `br_vlan_tunnel_info()`.
- VLAN tunnel storage/data-plane helpers under `CONFIG_BRIDGE_VLAN_FILTERING`: `vlan_tunnel_init()`, `vlan_tunnel_deinit()`, `nbp_vlan_tunnel_info_add()`, `nbp_vlan_tunnel_info_delete()`, `nbp_vlan_tunnel_info_flush()`, `vlan_tunnel_info_del()`, `br_handle_ingress_vlan_tunnel()`, and `br_handle_egress_vlan_tunnel()`.
- When VLAN filtering is disabled, most helpers become no-ops returning success or `0`.

## Control flow
Netlink code parses requested mappings and delegates add/delete to VLAN tunnel helpers. Data-plane ingress/egress helpers attach or consume tunnel metadata when VLAN tunnel mode is active. Initialization/deinitialization hooks prepare per-VLAN-group tunnel hashes.

## State and persistence
Tunnel state is stored in `struct net_bridge_vlan_group::tunnel_hash` and each VLAN's `struct br_tunnel_info`. It is in-memory only and tied to bridge port/VLAN lifetime.

## Dependencies and integration points
The header depends on bridge VLAN filtering and tunnel metadata support. It integrates with `br_netlink.c`, `br_netlink_tunnel.c`, VLAN implementation files, and encapsulation devices such as VXLAN that use metadata destinations.

## Risks and edge cases
The no-op stubs under disabled VLAN filtering can hide configuration paths unless callers validate feature availability. Data-plane helpers must preserve skb metadata lifetime and correctly map between ingress tunnel IDs and VLAN IDs. Flush paths must remove tunnel metadata when the port flag is disabled.

## Test signals
Test VLAN tunnel mapping add/delete, port flag toggles, ingress metadata-to-VLAN mapping, egress VLAN-to-metadata mapping, range dumps, VLAN filtering disabled configs, and port/VLAN teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_private_tunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_stp.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_stp.c

## Purpose
`br_stp.c` implements the core in-kernel IEEE 802.1D STP state machine. It selects root/designated ports, records received configuration, transitions ports between blocking/listening/learning/forwarding, handles topology-change propagation, and validates bridge STP timing and ageing-time configuration.

## Important APIs, types, and functions
- `br_set_state()` changes a port state, updates MST instance 0 when enabled, offloads STP state through switchdev, logs transitions, and updates STP xstats for kernel STP.
- `br_root_selection()`, `br_designated_port_selection()`, `br_configuration_update()`, and `br_port_state_selection()` are the core selection pipeline.
- `br_received_config_bpdu()` and `br_received_tcn_bpdu()` are BPDU receive entry points from `br_stp_bpdu.c`.
- `br_transmit_config()`, `br_transmit_tcn()`, and `br_config_bpdu_generation()` create outbound STP traffic through BPDU helpers.
- `br_topology_change_detection()` and `__br_set_topology_change()` manage topology-change flags and ageing-time reduction/restoration.
- `br_set_hello_time()`, `br_set_max_age()`, `br_set_forward_delay()`, `br_set_ageing_time()`, `__set_ageing_time()`, and `br_get_ageing_time()` implement user-facing timer configuration.

## Control flow
When topology or configuration changes, `br_configuration_update()` chooses the root port and designated ports, then `br_port_state_selection()` moves the selected ports forward or blocks them. Root selection compares designated root, total path cost, designated bridge, designated port, and local port ID. Root-blocked ports that would become root ports are held in listening and notified.

Received config BPDUs increment xstats, compare against current port information, record superior information, recompute bridge state, stop hello timers if the bridge lost root status, inherit root timing from the root port, generate updated config BPDUs, and process topology-change acknowledgements. TCN BPDUs on designated ports trigger topology-change detection and acknowledgement.

Port forwarding transition depends on STP mode: no STP or zero delay goes directly to forwarding; kernel STP enters listening; user STP enters learning. Topology changes reduce ageing time to twice forward delay during the change window and later restore configured bridge ageing time.

## State and persistence
STP state lives in `struct net_bridge` and `struct net_bridge_port`: root/designated IDs, root path cost, timers, topology flags, per-port designated info, states, pending flags, and xstats. It is volatile kernel state. Timers in `br_stp_timer.c` drive asynchronous progress.

## Dependencies and integration points
The file integrates with switchdev STP state/ageing-time offload, MST state, multicast port enable/disable, FDB ageing, rtnetlink notifications, carrier state, and BPDU send/receive helpers. User-facing control comes through netlink and sysfs setters.

## Risks and edge cases
Most functions require `br->lock`; missing locking would corrupt root/port selection. MRP-aware ports are excluded from STP state changes. Switchdev offload failures are logged but not always fatal. Ageing-time offload failure during topology change leaves software/hardware ageing mismatched. Root-block behavior intentionally prevents a superior port from taking over.

## Test signals
STP tests should simulate superior/inferior config BPDUs, TCN handling, root loss/regain, root-block ports, timer boundary validation, zero forward delay, kernel/user/no-STP modes, MST enabled state mirroring, switchdev offload errors, and ageing-time changes on topology events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_stp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_stp_bpdu.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_stp_bpdu.c

## Purpose
`br_stp_bpdu.c` encodes, transmits, receives, validates, and decodes STP BPDUs over LLC on bridge ports. It is the packet I/O layer for the STP state machine in `br_stp.c`.

## Important APIs, types, and functions
- `br_send_config_bpdu()` serializes a 35-byte configuration BPDU from `struct br_config_bpdu`.
- `br_send_tcn_bpdu()` serializes a 4-byte topology-change notification BPDU.
- `br_stp_rcv()` is registered through LLC/STP handling and dispatches inbound BPDUs.
- `br_set_ticks()` and `br_get_ticks()` convert between kernel jiffies and STP's 1/256-second units.
- `br_send_bpdu()` allocates an skb, builds LLC and MAC headers, and sends through `NF_HOOK(NFPROTO_BRIDGE, NF_BR_LOCAL_OUT, ...)`.

## Control flow
Transmit helpers return immediately unless the bridge is in kernel STP mode. They build fixed-format BPDU byte arrays, set control priority, address frames to the bridge group address, pass through bridge local-out netfilter, and update per-port STP xstats.

Receive first verifies the protocol ID/version bytes, resolves the bridge port under RCU, takes `br->lock`, and drops unless kernel STP is active, the bridge is up, the port is enabled, and the destination MAC matches `br->group_addr`. BPDU guard disables the port on receipt. Config BPDUs require enough payload, are decoded field-by-field, and are rejected if `message_age > max_age`; valid config and TCN BPDUs are passed to `br_received_config_bpdu()` or `br_received_tcn_bpdu()`.

## State and persistence
The file mutates per-port xstats and, via STP callbacks, bridge/port STP state. It consumes and frees inbound skbs and allocates transient outbound skbs. No persistent storage exists.

## Dependencies and integration points
It depends on LLC, netfilter bridge local-out hooks, netdevice transmit, skb helpers, unaligned endian access, `br_private_stp.h`, and the bridge group MAC address. It is a direct integration point between data-plane packet reception and the STP control-plane state machine.

## Risks and edge cases
Malformed short packets must be dropped without out-of-bounds reads. BPDU guard intentionally disables a port, so false positives have connectivity impact. Tick conversion rounds up inbound values and may affect boundary behavior. The receive path assumes RCU read-side protection from the caller as documented.

## Test signals
Inject valid config/TCN BPDUs, short frames, wrong protocol/version, wrong destination MAC, `message_age > max_age`, BPDU guard cases, netfilter local-out hooks, and xstats increments for transmit/receive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_stp_bpdu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_stp_if.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_stp_if.c

## Purpose
`br_stp_if.c` connects the STP state machine to bridge and port lifecycle/configuration. It initializes ports, enables/disables STP on bridges and ports, coordinates optional userspace STP helper startup, recalculates bridge IDs, and applies bridge/port priority and path-cost changes.

## Important APIs, types, and functions
- `br_init_port()` initializes port ID, designated info, blocking state, pending flags, and offloaded ageing time.
- `br_stp_enable_bridge()` / `br_stp_disable_bridge()` start/stop bridge-level STP timers/work and enable/disable all ports.
- `br_stp_enable_port()` / `br_stp_disable_port()` transition individual ports and clean timers/FDB/multicast state.
- `br_stp_set_enabled()` owns STP enable/disable requests and rejects STP when MRP is active.
- `br_stp_start()` and `br_stp_stop()` choose user STP or kernel STP and call `/sbin/bridge-stp` in auto mode for `init_net`.
- `br_stp_change_bridge_id()`, `br_stp_recalculate_bridge_id()`, `br_stp_set_bridge_priority()`, `br_stp_set_port_priority()`, and `br_stp_set_path_cost()` update identifiers and recompute state.

## Control flow
Enabling a bridge takes `br->lock`, starts the hello timer for kernel STP, schedules FDB GC, generates config BPDUs, and enables running/up ports. `br_stp_set_enabled()` starts from no-STP by trying the userspace helper in auto mode; success or explicit user mode sets `BR_USER_STP`, otherwise kernel STP starts timers and runs port selection.

Disabling a port designates it locally, sets disabled state, notifies netlink, deletes its STP timers, flushes FDB entries if no backup port is configured, disables multicast, recomputes root/designated state, and if the bridge becomes root, calls `br_become_root_bridge()`.

Bridge ID changes update the FDB local MAC, netdevice hardware address, any port designated/root IDs that referenced the old address, then recompute STP state. Automatic bridge ID recalculation picks the lowest member port MAC unless the user set a bridge MAC.

## State and persistence
All state is in bridge/port STP fields, timers, FDB, multicast context, and `stp_helper_active`. The userspace helper execution is transient; no file-backed persistence is maintained by this code.

## Dependencies and integration points
The file integrates with RTNL callers, `call_usermodehelper()`, switchdev ageing-time offload through `__set_ageing_time()`, FDB address/flush helpers, multicast port enable/disable, MRP exclusion, rtnetlink notifications, and netdevice address assignment.

## Risks and edge cases
Userspace helper startup is only attempted in `init_net` auto mode; failure falls back to kernel STP except explicit user mode. Port priority is limited by `BR_PORT_BITS`, so high bits are dropped into the port ID layout. Disabling a port with a backup port avoids FDB flush. Locking spans state-machine recomputation and helper-active changes must not race lifecycle.

## Test signals
Test STP enable/disable with helper present/missing/failing, explicit user mode, MRP conflict, port up/down enable paths, bridge MAC auto recalculation, user-set MAC preservation, port priority/path cost bounds, and FDB flush behavior with/without backup ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_stp_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_stp_timer.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_stp_timer.c

## Purpose
`br_stp_timer.c` owns bridge and port STP timers. It periodically sends hello BPDUs, expires received root information, progresses forward-delay state transitions, retransmits TCNs, clears topology-change state, handles config BPDU hold-down, and exposes timer values for user APIs.

## Important APIs, types, and functions
- `br_stp_timer_init()` initializes bridge timers: hello, TCN, and topology-change.
- `br_stp_port_timer_init()` initializes per-port message-age, forward-delay, and hold timers.
- `br_timer_value()` returns pending time in `USER_HZ` clock ticks for netlink/sysfs.
- Timer callbacks include `br_hello_timer_expired()`, `br_message_age_timer_expired()`, `br_forward_delay_timer_expired()`, `br_tcn_timer_expired()`, `br_topology_change_timer_expired()`, and `br_hold_timer_expired()`.

## Control flow
The hello timer emits config BPDUs while the bridge is up and reschedules only for kernel STP. The message-age timer means a neighbor's superior BPDU information expired; the port becomes designated, configuration is recomputed, and the bridge may become root. The forward-delay timer moves listening to learning, then learning to forwarding, optionally triggering topology-change detection and carrier on. The TCN timer retransmits TCNs while non-root and up. The topology-change timer clears topology-change flags and restores ageing time through `__br_set_topology_change()`. The hold timer sends a pending config BPDU after the hold interval.

## State and persistence
Timer state is in `struct timer_list` fields on `struct net_bridge` and `struct net_bridge_port`. Timers mutate in-memory STP fields under `br->lock` and emit rtnetlink notifications.

## Dependencies and integration points
The callbacks call STP state-machine functions from `br_stp.c`, notification functions from `br_netlink.c`, netdevice carrier helpers, and bridge logging. They rely on bridge/port lifetime management to cancel timers before freeing objects.

## Risks and edge cases
Callbacks use plain `spin_lock()` because they run in timer context. Message-age and forward-delay callbacks recheck disabled state after locking. `br_ifinfo_notify()` is called with an RCU read-side section in the forward-delay path. Failure to delete timers during port/bridge teardown would risk use-after-free.

## Test signals
Use timer-driven STP simulations for hello reschedule, neighbor loss, listening-to-learning-to-forwarding, TCN retransmission, topology-change expiry, hold-timer pending config, and teardown while timers are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_stp_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_switchdev.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_switchdev.c

## Purpose
`br_switchdev.c` integrates the bridge with switchdev hardware offload. It tracks hardware domains, marks frames to avoid duplicate software forwarding, offloads bridge port flags, notifies/replays FDB/VLAN/MDB objects to drivers, and manages offload/unoffload lifecycle for bridge ports.

## Important APIs, types, and functions
- TX forwarding offload helpers: `br_switchdev_frame_uses_tx_fwd_offload()`, `br_switchdev_frame_set_offload_fwd_mark()`, `nbp_switchdev_frame_mark_tx_fwd_offload()`, `nbp_switchdev_frame_mark_tx_fwd_to_hwdom()`, `nbp_switchdev_frame_mark()`, and `nbp_switchdev_allowed_egress()`.
- `br_switchdev_set_port_flag()` pre-validates and applies hardware-offloadable bridge port flags.
- FDB APIs: `br_switchdev_fdb_notify()` and replay helpers populate `switchdev_notifier_fdb_info`.
- VLAN APIs: `br_switchdev_port_vlan_add()`, `br_switchdev_port_vlan_no_foreign_add()`, `br_switchdev_port_vlan_del()`, and replay helpers.
- MDB APIs under multicast snooping: `br_switchdev_mdb_notify()` and replay helpers for host and port MDB objects with completion callbacks.
- Lifecycle APIs: `br_switchdev_port_offload()`, `br_switchdev_port_unoffload()`, and `br_switchdev_port_replay()`.

## Control flow
When a driver offloads a bridge port, `br_switchdev_port_offload()` obtains the physical parent ID, assigns or reuses a hardware domain, optionally enables TX forwarding offload static key, then replays VLAN, MDB, and FDB objects. Failure unwinds the offload accounting. Unoffload replays deletions, processes deferred switchdev work, then decrements offload counters and releases hardware-domain/static-key state.

Data-plane marking records the source hardware domain from ingress ports and tracks destination domains already handled by hardware. Egress is suppressed if the skb was already forwarded to that hardware domain or if an offload forward mark indicates hardware already replicated within the source domain.

FDB notifications skip locked entries and user-added dynamic non-static entries that drivers cannot interpret. VLAN replay walks bridge and port VLAN groups, skips context-only VLANs, and replays MSTI attributes after VLAN adds. MDB replay snapshots objects while holding `multicast_lock`, then calls notifiers outside the lock.

## State and persistence
Switchdev state is per-port `hwdom`, `offload_count`, `ppid`, flags, bridge `busy_hwdoms`, and a static key for TX forwarding offload. Hardware state is external and synchronized by switchdev notifications; software stores only volatile accounting.

## Dependencies and integration points
The file depends on switchdev notifier/object APIs, netdevice parent IDs, bridge FDB/VLAN/MDB/multicast structures, skb bridge control block fields, and rtnetlink locking for replay. It is called by bridge FDB/VLAN/MDB code, bridge port flag setters, and driver offload callbacks.

## Risks and edge cases
Hardware-domain exhaustion returns `-EBUSY`. A single bridge port cannot be offloaded by different physical switch IDs, but repeated offload calls from the same switch are reference-counted. Deferred MDB events can duplicate replay unless `switchdev_port_obj_act_is_deferred()` is checked. Locked FDB entries and unsupported dynamic user entries are intentionally not offloaded. Offload/unoffload ordering must keep hardware and software synchronized.

## Test signals
Test offload/unoffload of simple ports and bond/team ports, mismatched parent IDs, hardware-domain reuse/exhaustion, TX forwarding offload duplicate suppression, port flag rejection, FDB/VLAN/MDB replay on late driver join, multicast offload completion success/failure, and unoffload deletion ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_switchdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_sysfs_br.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_sysfs_br.c

## Purpose
`br_sysfs_br.c` exposes legacy bridge master attributes in sysfs. It lets privileged users read and update bridge STP, FDB, multicast, netfilter, VLAN, and group-address settings, and creates the bridge sysfs group, FDB binary file, and `brif` directory.

## Important APIs, types, and functions
- `store_bridge_parm()` is the common numeric store path: CAP_NET_ADMIN check, parse, `rtnl_trylock()`, call a setter, notify netdevice state change, and log extack messages.
- Attribute pairs expose `forward_delay`, `hello_time`, `max_age`, `ageing_time`, `stp_state`, `group_fwd_mask`, `priority`, IDs/root state, timers, `group_addr`, `flush`, `no_linklocal_learn`, multicast settings, bridge netfilter toggles, and VLAN filtering settings.
- `brforward_read()` exports the FDB as binary `struct __fdb_entry` records through `SYSFS_BRIDGE_FDB`.
- `br_sysfs_addbr()` and `br_sysfs_delbr()` create/remove the bridge attribute group, FDB binary attribute, and port-link directory.

## Control flow
Read attributes directly format fields from `struct net_bridge`, often converting jiffies to clock ticks or using `br_timer_value()`. Numeric writes pass through `store_bridge_parm()` and the same core setters used by netlink where possible. `group_addr_store()` is custom because it parses a MAC address and validates link-local group-address restrictions before updating under `br->lock`. `flush` writes call `br_fdb_flush()` for non-static entries.

Creation first creates the `"bridge"` attribute group on the netdevice kobject, then the FDB binary file, then the `brif` kobject. Failure unwinds earlier sysfs additions.

## State and persistence
Sysfs writes mutate in-memory bridge state. Sysfs files are views over live kernel state and are recreated with the device; they are not persistent configuration. The `ifobj` kobject pointer is stored in `struct net_bridge`.

## Dependencies and integration points
The file depends on sysfs, netdevice kobjects, RTNL, namespace CAP_NET_ADMIN checks, STP, multicast snooping, VLAN filtering, bridge netfilter, FDB helpers, and bridge option toggles. The source warns that new bridge options should use netlink rather than new sysfs files.

## Risks and edge cases
`rtnl_trylock()` can return `restart_syscall()`, so userspace must retry. Some sysfs setters directly mutate fields and are legacy surfaces parallel to netlink. Group address and forwarding mask validation protect reserved link-local protocols. FDB binary reads require record-aligned offsets. Sysfs creation failure must unwind cleanly.

## Test signals
Test CAP_NET_ADMIN enforcement, invalid numeric/MAC inputs, RTNL contention retry behavior, every writable attribute versus equivalent netlink behavior, FDB binary alignment, sysfs add/remove failure injection, and builds with multicast/netfilter/VLAN options disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_sysfs_br.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_sysfs_if.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_sysfs_if.c

## Purpose
`br_sysfs_if.c` exposes legacy per-bridge-port sysfs attributes under each port's `brport` kobject and maintains symlinks from the bridge's `brif` directory. It provides read/write access to STP state, timers, path cost, priority, port flags, group forwarding mask, backup port, and multicast router settings.

## Important APIs, types, and functions
- `struct brport_attribute` wraps sysfs attributes with numeric or raw store callbacks.
- Macros `BRPORT_ATTR`, `BRPORT_ATTR_RAW`, and `BRPORT_ATTR_FLAG` define port attributes and flag toggles.
- `store_flag()` validates hardware-offloadable flag changes through `br_switchdev_set_port_flag()` before committing `p->flags` and calling `br_port_flags_change()`.
- `brport_show()` and `brport_store()` implement `sysfs_ops`.
- `br_sysfs_addif()` creates the `bridge` link, all `brport` files, and the bridge `brif/<ifname>` symlink.
- `br_sysfs_renameif()` renames the `brif` symlink when a port device is renamed.

## Control flow
Reads call the attribute-specific show callback and format live `struct net_bridge_port` fields. Writes require CAP_NET_ADMIN and RTNL. Raw stores, such as `backup_port`, copy the user buffer and call the callback under `br->lock`; numeric stores parse `unsigned long` and call the setter under `br->lock`. Successful writes emit `br_ifinfo_notify(RTM_NEWLINK, NULL, p)`.

Port attributes include STP path cost/priority and designated/root state, timers, flush, hairpin, BPDU guard, root block, learning, flooding controls, proxy ARP, multicast flags, neighbor suppression, isolation, group forwarding mask, backup port, and multicast router when snooping is enabled.

## State and persistence
The file mutates per-port in-memory fields such as `flags`, `path_cost`, `priority`, `group_fwd_mask`, backup port pointer, multicast router mode, and FDB contents. `p->sysfs_name` stores the current symlink name for rename tracking. No persistent configuration is written.

## Dependencies and integration points
It depends on sysfs/kobject support, RTNL, namespace CAP_NET_ADMIN, switchdev port-flag validation/offload, STP setters, FDB flush, backup-port management, multicast snooping, and bridge netlink notifications.

## Risks and edge cases
Some file creation errors in `br_sysfs_addif()` return immediately after partial creation; caller teardown must remove the kobject/files. Raw backup-port input strips a newline and resolves the device by name in the port namespace. Switchdev rejection must prevent software flag drift from hardware. `simple_strtoul()` accepts partial numeric input, matching legacy sysfs behavior.

## Test signals
Test all flag toggles with and without switchdev support, path-cost/priority bounds, backup-port set/clear/unknown device, FDB flush, multicast router writes, symlink creation and rename rollback, CAP_NET_ADMIN failures, and netlink notification emission after successful writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_sysfs_if.c -->
