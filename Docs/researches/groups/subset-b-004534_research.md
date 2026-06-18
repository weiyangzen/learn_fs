# Research: subset-b-004534

This grouped report covers the mlx5 Ethernet TC conntrack, tunnel, TIR, trap, TX/RX helper, and XDP files requested for subset-b-004534. Each section is delimited with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_ct.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_ct.c

Purpose: implements mlx5 TC connection tracking offload. It translates flower CT matches/actions and nf_flow_table established-flow callbacks into mlx5 flow tables, CT/NAT tables, modify-header actions, register mappings, counters, and restore support for packets that miss back to software.

Important APIs and types: `struct mlx5_tc_ct_priv` owns CT global tables, tuple/zone rhashtables, mapping contexts, post-action table, FS provider ops, debugfs stats, and an ordered workqueue. `struct mlx5_ct_ft` represents one CT zone and nf_flowtable callback registration. `struct mlx5_ct_entry` represents one offloaded connection keyed by nf flow cookie and by original or NAT tuple. Public entry points are `mlx5_tc_ct_init`, `mlx5_tc_ct_clean`, `mlx5_tc_ct_match_add`, `mlx5_tc_ct_match_del`, `mlx5_tc_ct_parse_action`, `mlx5_tc_ct_flow_offload`, `mlx5_tc_ct_delete_flow`, `mlx5e_tc_ct_restore_flow`, `mlx5_tc_ct_add_no_trk_match`, and `mlx5e_tc_ct_is_valid_flow_rule`.

Control flow: init validates post-action and eswitch capabilities, creates zone/label mappings, CT and CT NAT global tables, NAT miss rule, tuple/zone hashes, workqueue, provider-specific CT flow-steering state, and debugfs counters. TC parsing records CT action, zone, nf flowtable, miss cookie, mark and labels mapping in `mlx5_ct_attr`. Flow offload registers a per-zone nf_flow_table callback, maps the action miss cookie, programs register writes, then jumps either directly to CT/CT-NAT or to per-zone pre-CT tables for nonzero chains. nf_flow_table callbacks add, update, delete, or query stats for individual established entries. Entry add builds tuple and NAT tuple, inserts hashes under `ht_lock`, allocates shared or per-entry counters, creates rules in CT and/or CT NAT, and marks the entry valid. Restore decodes the zone id, dissects the skb tuple, looks up the entry, and calls `tcf_ct_flow_table_restore_skb`.

State and persistence: state is in kernel memory and hardware flow tables only. Zone and label mappings are reference counted; CT entries are rhashtable/refcount objects. Deletion can be deferred through the ordered workqueue when references drop outside a safe context. Debugfs exposes `offloaded` and `rx_dropped`.

Dependencies and integration points: netfilter conntrack and nf_flow_table, TC flower dissectors/actions, mlx5 flow steering chains, modify-header cache, mapping API, post-action table, CT FS provider implementations for DMFS/HMFS/SMFS, eswitch representors, counters, and debugfs. Register contracts come from `tc_ct.h` and are consumed by the broader TC parser and restore path.

Risks and test signals: high-risk areas are tuple hash consistency during update/delete, NAT modify-header ordering, shared-counter refcounts, zone/label mapping lifetime, unsupported CT states or dissectors, and restore drops when zone or tuple lookup fails. Useful tests include CT clear and CT commit rules, NAT and non-NAT flows, IPv4/IPv6 TCP/UDP/GRE tuples, flow stats, flow replacement with changed restore cookie, zone teardown while entries exist, module builds with each steering mode, and packet restore after hardware miss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_ct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_ct.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_ct.h

Purpose: declares the mlx5 TC conntrack offload interface and the metadata-register layout used to carry CT zone, state, mark, labels, flow-table id, and restore-zone information through mlx5 hardware pipelines.

Important APIs and types: `struct mlx5_ct_attr` is embedded in flow attributes and records zone, CT action bits, nf_flowtable pointer, labels mapping id, action-miss mapping, miss cookie, offload state, and zone flow-table pointer. Macros `zone_to_reg_ct`, `ctstate_to_reg_ct`, `mark_to_reg_ct`, `labels_to_reg_ct`, `fteid_to_reg_ct`, `zone_restore_to_reg_ct`, and `nic_zone_restore_to_reg_ct` define precise metadata fields. `MLX5_CT_ZONE_BITS` and `MLX5_CT_ZONE_MASK` expose the usable zone width. The header exports init/cleanup, match add/delete, action parsing, flow offload/delete, restore, no-track match setup, and validation helpers.

Control flow: callers include the TC parser and flow lifecycle code. Match parsing fills a `mlx5_flow_spec` using the register macros and records label mappings in `mlx5_ct_attr`. Action parsing stores the CT action contract. Flow offload uses the populated `mlx5_ct_attr` to install CT pipeline jumps, and delete reverses it. Restore uses the zone restore metadata from RX completion paths.

State and persistence: this header owns no runtime state, but its register mappings are persistent ABI-like contracts inside the driver. Any change to bit widths or offsets must remain consistent with `tc_ct.c`, mapping definitions, post-action handling, and hardware match/set capabilities.

Dependencies and integration points: depends on TC action definitions, mlx5 flow steering structures, and `en.h`. It hides implementation details behind `struct mlx5_tc_ct_priv` and `struct mlx5_ct_ft`. When `CONFIG_MLX5_TC_CT` is disabled, inline stubs either no-op, reject CT features with extack messages, or fail restore for nonzero zone ids.

Risks and test signals: register collisions are the main risk, especially the C5 low-byte reservation for packet color and different restore-zone placement for NIC mode. Test signals include build coverage with CT enabled and disabled, extack behavior when disabled, and hardware flow dumps verifying that CT zone/state/mark/label fields land in the expected registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_ct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_priv.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_priv.h

Purpose: provides private TC offload structures and helper declarations shared by mlx5 Ethernet TC implementation files. For this subset it is the central contract tying conntrack, tunnel encap/decap, hairpin, slow path, post actions, and flow flags together.

Important APIs and types: `enum MLX5E_TC_FLOW_FLAG_*` extends exported TC flags with driver-private lifecycle flags such as `OFFLOADED`, `SLOW`, `NOT_READY`, `DELETED`, `TUN_RX`, and `FAILED`. `struct mlx5e_tc_flow_parse_attr` carries parsed tunnel info per destination, MPLS info, filter device, flow spec, pedit state, modify-header actions, mirred ifindexes, and action parse state. `struct mlx5e_tc_flow` is the private flow object with hardware rule handles, encap/decap attachments, route attachments, hairpin/peer lists, original device, temporary list node, refcount, completions, attributes, and chain mapping. It also declares rule offload/unoffload, post-action, slow-path, namespace, counter, internal-port, flow-meter, and match-header helper APIs.

Control flow: parser code fills `parse_attr`; action-specific files attach encap, decap, CT, hairpin, or post-action resources to `mlx5e_tc_flow`; offload functions install the hardware rules and set flags; delete paths detach resources and use completions/refcounts to serialize teardown. The inline flag helpers wrap bit operations with memory barriers so data fields are visible before flags are observed by concurrent paths.

State and persistence: runtime state lives in `mlx5e_tc_flow` objects and their linked resources. The temporary flow list and `tmp_entry_index` are intentionally reused during neighbor and route updates. `init_done` and `del_hw_done` completions are important persistence points for concurrent update workers.

Dependencies and integration points: depends on public `en_tc.h`, action parser state, mlx5 flow specs and attrs, eswitch flow attributes, tunnel encap entries, route entries, decap entries, hairpin entries, counters, internal ports, and flow meters. Many files in this subset depend on this header to avoid exposing these internals publicly.

Risks and test signals: incorrect flag ordering or list ownership can cause use-after-free or stale hardware rules. Tunnel updates rely on array-indexed `encaps` and `encap_routes` matching destination indexes. Test signals include KCSAN/KASAN under concurrent TC add/delete and route/neigh updates, multi-destination encap, slow-path transition tests, and compile coverage for optional features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun.c

Purpose: implements generic tunnel support for mlx5 TC offload. It identifies supported tunnel netdevs, performs IPv4/IPv6 route and neighbor lookup, builds outer Ethernet/IP/tunnel headers for packet reformat objects, parses outer tunnel match keys into mlx5 flow specs, and resolves decap route information.

Important APIs and types: `struct mlx5e_tc_tun_route_attr` stores route device, output device, flowi4/flowi6 lookup keys, neighbor, and TTL. Public functions include `mlx5e_get_tc_tun`, `mlx5e_tc_tun_init_encap_attr`, `mlx5e_tc_tun_create_header_ipv4`, `mlx5e_tc_tun_update_header_ipv4`, IPv6 equivalents when enabled, `mlx5e_tc_tun_route_lookup`, `mlx5e_tc_tun_device_to_offload`, `mlx5e_tc_tun_parse`, and `mlx5e_tc_tun_parse_udp_ports`.

Control flow: `mlx5e_get_tc_tun` dispatches netdev kind to VXLAN, GENEVE, GRE, or MPLS-over-UDP tunnel ops. Route lookup resolves the kernel route, validates unicast routing and eswitch/uplink constraints, selects route and output devices, holds the route device, and grabs a neighbor reference. Header creation computes total encap size, checks hardware maximum, attaches the encap entry to representor neighbor tracking before testing neighbor validity, copies the neighbor MAC, writes Ethernet and IP headers, delegates tunnel-protocol header generation to tunnel ops, and allocates a packet reformat object only when the neighbor is valid. Update paths rebuild existing headers after route or neighbor changes. Decap route lookup swaps source/destination addresses to find the reverse route and records VF tunnel vport or OVS internal-port state. Parse code writes outer UDP/IP/tunnel matches and rejects unsupported fragments or TTL matching without capability.

State and persistence: this file creates per-encap `encap_header`, `encap_size`, `pkt_reformat`, `out_dev`, `route_dev_ifindex`, destination MAC, and validity flags. Neighbor and route references are released through cleanup helpers. No persistent storage exists outside runtime kernel objects and hardware packet reformat handles.

Dependencies and integration points: Linux routing, neighbors, VXLAN/GRE/GENEVE/BareUDP helpers, mlx5 eswitch representors, LAG multipath, internal-port offload, tunnel-specific ops from `tc_tun_*.c`, and encap lifecycle code in `tc_tun_encap.c`.

Risks and test signals: route-device validation, LAG/OVS/uplink cases, max encap size, neighbor invalidation, IPv6-disabled builds, and unsupported outer-key masks are key risks. Test with VXLAN/GENEVE/GRE/MPLSoUDP encap and decap, unresolved neighbor then neighbor resolution, route replacement, VLAN route device, LAG multipath, TTL match rejection, and tunnel fragment handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun.h

Purpose: declares the generic tunnel-offload abstraction used by mlx5 TC. It lets protocol-specific VXLAN, GENEVE, GRE, and MPLS-over-UDP files plug capability checks, header generation, match parsing, and encap key comparison into the common route/header machinery.

Important APIs and types: tunnel type enum defines `UNKNOWN`, `VXLAN`, `GENEVE`, `GRETAP`, and `MPLSOUDP`. `struct mlx5e_encap_key` pairs an `ip_tunnel_key` with tunnel ops for hash/equality. `struct mlx5e_tc_tunnel` contains tunnel type, match level, and callbacks for `can_offload`, `calc_hlen`, `init_encap_attr`, `generate_ip_tun_hdr`, `parse_udp_ports`, `parse_tunnel`, `encap_info_equal`, and optional `get_remote_ifindex`. The header exports the four protocol ops objects and common functions for tunnel selection, encap attr init, IPv4/IPv6 header create/update, route lookup, device offload checks, parsing, UDP port parsing, and equality helpers.

Control flow: TC action parsing stores tunnel info in parse attributes, then encap attach calls `mlx5e_get_tc_tun` and `mlx5e_tc_tun_init_encap_attr`. Header construction calls the selected tunnel's length and header-generation callbacks. Decap parsing calls UDP-port and protocol-specific parsing callbacks, then common outer IP parsing. Equality callbacks are used by encap hash-table reuse.

State and persistence: no runtime state is owned here. The callback table is effectively a static vtable and must remain consistent with each protocol implementation and common encap code.

Dependencies and integration points: available under `CONFIG_MLX5_ESWITCH`; depends on netdevice, mlx5 flow steering, TC classifier, netlink extack, mlx5 `en.h`, and representor declarations. IPv6 helpers are stubbed to `-EOPNOTSUPP` when IPv6 support is unavailable.

Risks and test signals: adding a tunnel type requires filling all callbacks that common code assumes are present. Misreported `match_level` or equality behavior can cause under-matching or encap reuse bugs. Test with eswitch disabled/enabled builds, IPv6 disabled builds, protocol-specific offload gating, and hash reuse for tunnels with and without options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_encap.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_encap.c

Purpose: owns the mlx5 TC tunnel encap/decap object caches and route-revalidation machinery. It attaches flows to shared encap or decap packet-reformat objects, tracks route entries for VF tunnel and decap routing, reacts to FIB notifications, and moves flows between fast hardware rules and slow path while routes or neighbors are invalid.

Important APIs and types: private `struct mlx5e_route_key`, `struct mlx5e_route_entry`, and `struct mlx5e_tc_tun_encap` implement a route table keyed by endpoint IP and protected by `route_lock`. Public functions include `mlx5e_tc_set_attr_rx_tun`, `mlx5e_tc_encap_flows_add`, `mlx5e_tc_encap_flows_del`, `mlx5e_take_all_encap_flows`, `mlx5e_get_next_init_encap`, `mlx5e_tc_update_neigh_used_value`, `mlx5e_encap_put`, `mlx5e_detach_encap`, `mlx5e_detach_decap`, equality helpers, `mlx5e_encap_take`, `mlx5e_dup_tun_info`, `mlx5e_attach_encap`, `mlx5e_attach_decap`, encap dest set/unset, decap route attach/detach, and tunnel encap init/cleanup.

Control flow: encap attach looks up or creates a shared `mlx5e_encap_entry` under the eswitch encap lock, duplicates tunnel info, initializes protocol attributes, inserts into the encap hash, creates IPv4/IPv6 headers, completes resource readiness, attaches route tracking for VF tunnel cases, sets internal-port actions if possible, links the flow, and marks the destination valid or slow. Decap attach similarly deduplicates by L2 header and allocates an L3-tunnel-to-L2 packet reformat. Neighbor update helpers take referenced flows and either reoffload slow-path flows when encap becomes valid or move valid flows to slow path when encap is lost. FIB callbacks allocate work, look up route entries, invalidate route state, and worker context updates encap and decap flows under RTNL plus eswitch locks.

State and persistence: state lives in eswitch encap/decap hash tables, route hash table, refcounts, RCU frees, flow attachment lists, route lists, `route_tbl_last_update`, encap validity/no-route flags, completion results, and hardware packet reformat handles. Cleanup unregisters the FIB notifier and flushes pending work.

Dependencies and integration points: Linux FIB notifier and nexthop APIs, `tc_tun.c` route/header functions, representor neighbor tracking, eswitch offload locks, internal-port actions, VF tunnel metadata rewrite, flow post-actions, slow-path helpers, and tracepoints.

Risks and test signals: concurrency among TC delete, neighbor updates, and FIB work is the major risk. Other risks are duplicate encap actions, stale route updates missed during creation, wrong VF source-port rewrite, packet reformat lifetime, and route invalidation leaving flows falsely offloaded. Test with shared encap reuse, multi-destination mirroring rejection for VF tunnels, route replace/delete, concurrent flow delete during update, neighbor used refresh, decap route reoffload, and FIB notifier cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_encap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_encap.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_encap.h

Purpose: declares the public tunnel encap/decap lifecycle API used by mlx5 TC flow parsing and offload paths. It hides the shared object caches, route table, FIB notifier, and neighbor update internals implemented in `tc_tun_encap.c`.

Important APIs and types: exports attach/detach functions for encap destinations and decap reformat objects, route attach/detach for decap flows, bulk destination set/unset helpers, `mlx5e_dup_tun_info`, RX tunnel attribute extraction, and `mlx5e_tc_tun_init`/`mlx5e_tc_tun_cleanup`. It includes `tc_priv.h` so callers operate on private flow and flow-attribute structures.

Control flow: TC flow setup calls `mlx5e_tc_tun_encap_dests_set` after parse attributes contain tunnel info and mirred ifindexes; teardown calls the matching unset path. L3-to-L2 decap setup uses `mlx5e_attach_decap`; RX tunnel route tracking uses `mlx5e_tc_set_attr_rx_tun` and `mlx5e_attach_decap_route`. Driver open/close paths create or destroy the tunnel encap manager through init/cleanup.

State and persistence: no state is defined here directly. It defines ownership boundaries: attach functions take references and add flow list links, detach functions drop them, and init/cleanup own notifier lifetime.

Dependencies and integration points: depends on private TC flow structures and through them on eswitch flow attrs, encap entries, decap entries, and route entries. The API is primarily consumed by `en_tc.c` and related TC action code.

Risks and test signals: because this is a lifecycle boundary, callers must pair every successful attach with detach and must not free parse tunnel info before unset. Test signals are leak-free TC add/delete cycles, failure unwind after partial multi-destination attach, decap attach failure, and cleanup with live or recently completed FIB work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_encap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_geneve.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_geneve.c

Purpose: provides the `mlx5e_tc_tunnel` implementation for GENEVE. It gates offload on flex-parser support, builds GENEVE UDP headers including VNI and options, parses GENEVE decap match keys, and compares encap keys including options.

Important APIs and types: static helpers include capability check, header length calculation, UDP destination-port validation, encap attr init, tunnel-id-to-VNI conversion, header generation, VNI parsing, option parsing, OAM/protocol parsing, and option-aware equality. The exported object is `geneve_tunnel` with `MLX5E_TC_TUNNEL_TYPE_GENEVE` and L4 match level.

Control flow: encap init selects VXLAN-style L2-to-VXLAN reformat because hardware inserts a software-provided tunnel header at the same point. Header generation writes UDP destination, GENEVE version, option length, OAM and critical bits, VNI, protocol type `ETH_P_TEB`, and optional TLV bytes. Decap parse first requires valid UDP destination port, then forces OAM off and optionally protocol type, parses VNI when requested and supported, and parses a single GENEVE option into mlx5 misc/misc3 fields after creating a firmware TLV option object.

State and persistence: this file owns no long-lived state, but `mlx5_geneve_tlv_option_add` creates hardware/parser state for option matching. Encap equality inspects option bytes stored adjacent to `ip_tunnel_info`.

Dependencies and integration points: Linux GENEVE definitions, mlx5 geneve library, common tunnel parse/header code, hardware capability fields for GENEVE VNI, OAM, protocol type, option length, TLV option data, and TLV existence.

Risks and test signals: limitations include default GENEVE port only, one option match, unsupported zero option-data matches, unsupported option lengths, and dependency on flex parser capabilities. Test with default/nondefault port, VNI match, no options, one valid option, excessive option length, critical/OAM flags, and capability-negative hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_geneve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_gre.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_gre.c

Purpose: provides GRE/GRETAP tunnel offload operations for mlx5 TC. It supports NVGRE-style encapsulation/decapsulation for Ethernet payloads and optional GRE key matching.

Important APIs and types: helpers check `nvgre_encap_decap` capability, calculate GRE header length from tunnel flags, initialize encap attributes with `MLX5_REFORMAT_TYPE_L2_TO_NVGRE`, generate GRE headers, and parse GRE protocol/key matches. The exported `gre_tunnel` uses tunnel type `GRETAP`, L3 match level, no UDP parser, generic encap equality, and protocol-specific parse/header callbacks.

Control flow: header generation sets outer IP protocol to GRE, rejects checksum and sequence flags because hardware does not calculate them, writes `ETH_P_TEB`, converts tunnel flags to GRE flags, and appends key when requested. Decap parsing forces outer IP protocol GRE, matches GRE protocol `ETH_P_TEB`, and copies optional encap keyid masks/values into misc GRE key fields.

State and persistence: no persistent state is stored here. Encap key identity comes from the common generic equality helper and the shared encap table in `tc_tun_encap.c`.

Dependencies and integration points: Linux GRE helpers, common tunnel abstraction, mlx5 eswitch capability checks, flow dissector encap keyid, and mlx5 misc match fields.

Risks and test signals: GRE checksum/sequence flags are unsupported for encap; callers must receive `-EOPNOTSUPP`. Key matching depends on exact keyid masks and mlx5 misc fields. Test with keyed and unkeyed GRETAP, checksum/sequence rejection, protocol match, capability-negative hardware, IPv4/IPv6 outer routes through common code, and encap reuse for identical GRE keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_gre.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_mplsoudp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_mplsoudp.c

Purpose: implements MPLS-over-UDP, via BareUDP, tunnel operations for mlx5 TC. It builds UDP plus MPLS shim encapsulation and parses MPLS-over-UDP decap keys when hardware can match them.

Important APIs and types: static ops cover capability check for `reformat_l3_tunnel_to_l2`, header length calculation, encap attr init with `MLX5_REFORMAT_TYPE_L2_TO_L3_TUNNEL`, IP tunnel header generation, UDP port parsing, and MPLS tunnel parsing. The exported object is `mplsoudp_tunnel` with L4 match level and generic encap equality.

Control flow: header generation sets outer IP protocol to UDP, writes tunnel destination port, and encodes MPLS label, TTL, traffic class, and BOS from parsed MPLS info. Decap parsing first requires stateless MPLS-over-UDP or CW MPLS UDP flex parser support, rejects encap keyid, and if MPLS key exists supports matching only the first label stack entry. It maps first LSE label, EXP/TC, BOS, and TTL masks/values into misc2 fields and enables misc2 matching.

State and persistence: no local persistent state. It relies on parse attributes to carry MPLS info for encap and common encap caching for object lifetime.

Dependencies and integration points: Linux BareUDP and MPLS helpers, common tunnel UDP parsing, mlx5 Ethernet and generic capabilities, flow dissector MPLS keys, and misc2 hardware match fields.

Risks and test signals: limitations include no encap keyid matching, first-LSE-only matching, and capability-dependent parser support. Test with simple MPLS-over-UDP encap, first-label decap match, multiple LSE rejection, keyid rejection, TTL/TC/BOS masks, and capability-negative hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_mplsoudp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_vxlan.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_vxlan.c

Purpose: provides VXLAN tunnel operations for mlx5 TC, including registered-port validation, VXLAN header generation, VNI and GBP option parsing, and option-aware encap equality.

Important APIs and types: helpers check `vxlan_encap_decap`, calculate VXLAN header length, validate UDP destination port against the mlx5 VXLAN port registry, initialize encap attr as `MLX5_REFORMAT_TYPE_L2_TO_VXLAN`, generate VXLAN headers, parse GBP options, parse VNI, compare options, and fetch VXLAN remote ifindex. The exported `vxlan_tunnel` has L4 match level and the common UDP parser wrapper.

Control flow: encap init rejects unregistered destination ports. Header generation rejects malformed VXLAN option lengths, writes UDP destination, sets VNI flag, converts tunnel id to VNI field, and optionally builds GBP metadata. Decap parsing requires an encap keyid for VNI work; with GBP options it validates option type, length, mask, and custom tunnel-header capability, then writes GBP and shifted VNI into misc5 fields. Without options it requires `outer_vxlan_vni` support and writes VNI to misc fields. The remote-ifindex callback returns the VXLAN default destination ifindex for route lookup.

State and persistence: no local long-lived state. Port registration is held by the mlx5 VXLAN subsystem, and encap object sharing is handled by common encap code.

Dependencies and integration points: Linux VXLAN and IP tunnel helpers, mlx5 VXLAN library, common tunnel code, hardware capability fields for VXLAN VNI and custom tunnel headers, and flow dissector encap key/options.

Risks and test signals: risks include stale port registration, GBP mask validation, mixing symbolic and custom tunnel fields, and remote-ifindex routing behavior. Test registered and unregistered ports, VNI match with and without GBP, invalid GBP length/mask/type, VXLAN GBP encap, remote-ifindex route lookup, and hardware without VNI/custom header support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_vxlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tir.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tir.c

Purpose: implements a builder and lifecycle wrapper for mlx5 Transport Interface Receive objects. TIRs route received packets to direct RQs or indirect RQTs and carry RSS, packet merge/LRO, self-loopback blocking, and TLS receive settings.

Important APIs and types: private `struct mlx5e_tir_builder` stores a create/modify command buffer and a `modify` flag. Public builder functions allocate/free/clear, build inline direct-RQ dispatch, build indirect RQT dispatch, configure packet merge, RSS, direct mode, self loopback blocking, and TLS. Lifecycle functions are `mlx5e_tir_init`, `mlx5e_tir_destroy`, and `mlx5e_tir_modify`.

Control flow: callers allocate a builder for create or modify, fill the relevant TIRC context through helper functions, then create or modify a hardware TIR. Builders select the correct `create_tir_in.ctx` or `modify_tir_in.ctx` layout. Create-only helpers warn if used with a modify builder. Modify-capable helpers set the appropriate modify bitmask. `mlx5e_tir_init` creates the TIR and optionally registers it in the transport-domain TIR list under a mutex; destroy removes it if registered and destroys the hardware object.

State and persistence: the hardware TIR number persists in `struct mlx5e_tir`. Optional list registration persists until destroy. Builder state is temporary command input memory.

Dependencies and integration points: mlx5 transport object commands, Ethernet params for packet merge constants, RSS hash definitions, transport-domain hardware object list, and callers such as normal RX channels and trap queues.

Risks and test signals: incorrect create-vs-modify use, missing modify bitmasks, RSS key length mismatches, and list registration races are key risks. Test create/destroy for direct and RQT TIRs, modify RSS/packet merge/self-loopback, TLS TIR creation, trap direct-RQ TIR creation, and lockdep around registered TIR list deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tir.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tir.h

Purpose: declares the mlx5e TIR builder API, RSS parameter structures, and TIR object wrapper used by RX setup paths.

Important APIs and types: `struct mlx5e_rss_params_hash` carries hash function, Toeplitz key, and symmetric hash flag. `struct mlx5e_rss_params_traffic_type` carries L3/L4 protocol selectors and selected hash fields. `struct mlx5e_tir` stores the core device, TIR number, and optional list node. Builder and lifecycle functions match the implementation in `tir.c`, and `mlx5e_tir_get_tirn` exposes the hardware TIR number.

Control flow: RX resource setup builds command input through a `mlx5e_tir_builder`, creates a `mlx5e_tir`, uses the TIR number in flow steering destinations or trap rules, and later modifies or destroys it. The header keeps builder internals opaque so callers cannot accidentally depend on firmware command layouts.

State and persistence: `struct mlx5e_tir` is the persistent runtime object. Builder state is opaque and temporary. The list node is meaningful only when init was called with registration enabled.

Dependencies and integration points: depends on Linux kernel types and forward-declared mlx5 core and packet merge types. Used by channel setup, RSS configuration, TLS RX, self-loopback controls, and trap queue creation.

Risks and test signals: callers must not use a destroyed TIR number or modify with a create-style builder. Test signals include compile coverage for all builder declarations, RSS reconfiguration, trap use of `mlx5e_tir_get_tirn`, and cleanup paths that destroy registered and unregistered TIRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/trap.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/trap.c

Purpose: implements devlink trap receive support for mlx5e. It opens a dedicated RQ/CQ/NAPI queue and direct TIR, programs trap steering rules for selected generic traps, and tears the queue down when traps return to drop action.

Important APIs and types: internal helpers include `mlx5e_trap_napi_poll`, trap RQ init/open/close, direct RQ TIR creation, parameter build, trap open/close/activate/deactivate, action trap/drop handlers, and per-trap apply logic. Public functions are `mlx5e_close_trap`, `mlx5e_deactivate_trap`, `mlx5e_handle_trap_event`, and `mlx5e_apply_traps`.

Control flow: opening a trap allocates `struct mlx5e_trap` on the CPU-local node, builds cyclic RQ params, adds NAPI, opens CQ/RQ, creates an inline direct TIR pointing at the trap RQ, enables NAPI and activates the RQ. Trap action handling lazily opens the queue, then installs VLAN or DMAC trap rules with the trap TIR number. Drop action removes the matching trap rule and deletes the queue when no active devlink traps remain. Runtime NAPI polling polls RX CQ, reposts WQEs, completes NAPI when idle, and arms CQ.

State and persistence: `priv->en_trap` points to the active trap context. The trap owns RQ, TIR, NAPI, params, CQ/RQ params, stats pointer, DMA device, netdev, and mkey. Devlink stores configured trap actions; this file applies them when the interface is open.

Dependencies and integration points: TX/RX helpers, RX params, TIR builder, mlx5e flow-steering trap rule helpers, devlink trap APIs, NAPI, RQ/CQ open/close, and netdev locking.

Risks and test signals: failures during lazy queue open must unwind NAPI/RQ/TIR correctly. Trap events while interface is down intentionally do nothing and rely on later open. Test trap-to-drop transitions, two active traps sharing one queue, unknown trap id/action rejection, interface down/up action replay, NAPI polling under trapped traffic, and resource cleanup after partial open failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/trap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/trap.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/trap.h

Purpose: declares the trap queue context and public trap-control hooks for mlx5e devlink trap support.

Important APIs and types: `struct mlx5e_trap` contains datapath fields (`mlx5e_rq`, `mlx5e_tir`, NAPI, DMA device, netdev, mkey, stats pointer) and control fields (`priv`, core device, channel state bitmap, params, RQ params). Public functions close and deactivate a trap, handle a devlink trap event, and apply configured traps on interface state changes.

Control flow: interface open or devlink action changes call into `trap.c` through this API. The trap context is opened lazily when a trap action is requested and closed when active traps are removed. Consumers use the public functions rather than manipulating the queue directly.

State and persistence: `struct mlx5e_trap` persists while `priv->en_trap` is set. It is not a normal traffic channel but shares receive queue and TIR infrastructure.

Dependencies and integration points: includes the main Ethernet private header and devlink definitions. Depends on `tir.h` transitively through `en.h` types and on RX queue structures.

Risks and test signals: the structure mixes datapath and control fields, so lifetime must be serialized by netdev lock and interface state. Test compile coverage, open/close idempotence through public hooks, and trap handling when no trap context exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/trap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/txrx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/txrx.h

Purpose: collects core inline helpers, constants, WQE bookkeeping structures, and function declarations for mlx5e TX/RX datapaths. It is a shared low-level contract for normal TX, RX, ICO SQ, XDP SQ, trap RX, checksum/SWP, and CQ handling.

Important APIs and types: defines maximum TX WQE sizes and stop-room calculations, KSM UMR sizing, RX error CQE macro, `mlx5e_xmit_data`, `mlx5e_xmit_data_frags`, TX WQE info, ICO SQ WQE info, skb FIFO helpers, DMA FIFO helpers, SW parser spec, CQ arm, error CQE dump, RQ WQ accessors, and posting helpers. Declares polling and cleanup functions for CQ/RQ/TX/ICO. Inline WQE helpers include `mlx5e_txqsq_get_next_pi`, `mlx5e_icosq_get_next_pi`, `mlx5e_notify_hw`, `mlx5e_post_nop`, and stop-room helpers.

Control flow: TX and ICO callers reserve cyclic WQ space, fill NOPs at page boundaries so WQEs do not wrap, write WQE control/data segments, push DMA bookkeeping, and notify hardware through ordered doorbell writes. CQ pollers consume completions and use WQE info to free descriptors. RX callers use WQ accessors and reset helpers for cyclic or linked-list striding RQs. SW parser helpers set checksum/parser offsets and adjust partial checksums for GSO encapsulation.

State and persistence: state is held in queue doorbell counters (`pc`, `cc`), WQE info arrays, DMA FIFOs, skb FIFOs, CQ work queues, and per-queue stats. The header itself owns no global state but defines invariants for queue memory and DMA ownership.

Dependencies and integration points: mlx5 WQ/CQ primitives, netdev/skbuff, page-pool netmem, TCP/UDP checksum helpers, TLS conditionals, RX/TX implementation files, XDP code, trap code, and params helpers.

Risks and test signals: off-by-one stop room, WQE page-boundary wrapping, missing memory barriers before doorbell, DMA unmap type mismatches, and incorrect SWP offsets are high-risk. Test signals include heavy TX with max fragments and IPsec inline size, MPWQE, ICO UMR posting, CQ error injection, striding and cyclic RQ resets, GSO checksum with tunnels, and sparse/lockdep builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xdp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xdp.c

Purpose: implements mlx5e XDP RX actions, XDP TX/redirect transmit queues, AF_XDP TX metadata integration, XDP metadata callbacks, completion cleanup, and XDP-specific transmit mode selection.

Important APIs and types: public functions include `mlx5e_xdp_max_mtu`, `mlx5e_xdp_handle`, `mlx5e_xdp_mpwqe_complete`, `mlx5e_xmit_xdp_frame_check_mpwqe`, `mlx5e_xmit_xdp_frame_mpwqe`, `mlx5e_xmit_xdp_frame_check`, `mlx5e_xmit_xdp_frame`, `mlx5e_poll_xdpsq_cq`, `mlx5e_free_xdpsq_descs`, `mlx5e_xdp_xmit`, `mlx5e_xdp_rx_poll_complete`, and `mlx5e_set_xmit_fp`. Metadata ops are `mlx5e_xdp_metadata_ops` for RX timestamp/hash/VLAN and `mlx5e_xsk_tx_metadata_ops` for AF_XDP TX timestamp/checksum.

Control flow: RX XDP runs the BPF program and handles `PASS`, `TX`, `REDIRECT`, `DROP`, and abort paths. XDP_TX converts buffers to frames, handles XSK zero-copy special ownership, maps or syncs DMA, sends through either MPWQE or regular WQE, and records completion ownership in the XDP info FIFO. MPWQE mode batches single-buffer packets into enhanced multi-packet WQEs and falls back to regular WQEs for multi-frag packets. Regular mode builds inline and DMA data segments, including fragment segments. Completion polling walks CQEs to WQE info entries, pops FIFO records, unmaps DMA or recycles page-pool pages, completes AF_XDP frames and metadata, updates CQ DB, then advances SQ consumer counter. `mlx5e_xdp_xmit` handles ndo_xdp_xmit redirects from other devices and rings the doorbell on flush.

State and persistence: per-XDPSQ state includes producer/consumer counters, MPWQE session, WQE info array, XDP info FIFO, doorbell control segment, XSK pool, stats, and selected indirect-call function pointers. RQ flags record pending XDP transmit and redirect flush. DMA/page ownership is persisted in FIFO records until completion.

Dependencies and integration points: BPF/XDP core, AF_XDP sockets and metadata, page_pool, mlx5 CQ/WQ helpers from `txrx.h`, hardware timestamp conversion, RSS CQE bits, RX queue context, netdev XDP feature gating, and channel count to select per-CPU SQ.

Risks and test signals: high-risk areas are DMA unmap/recycle ownership across regular page-pool, XSK, and redirected frames; MPWQE fallback for fragments; SQ full handling; missing redirect flush; metadata timestamp mode; and completion counter ordering. Test XDP_PASS/TX/DROP/REDIRECT, AF_XDP zero-copy TX with checksum/timestamp metadata, multi-buffer XDP frames, MTU boundary, SQ full, MPWQE on/off, ndo_xdp_xmit from multiple CPUs, RX hash/VLAN metadata, and teardown freeing outstanding descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xdp.c -->
