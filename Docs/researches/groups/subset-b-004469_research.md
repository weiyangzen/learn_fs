# Research: subset-b-004469

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ethtool.c

### Purpose

`ice_ethtool.c` is the primary ethtool integration layer for the Intel ICE Ethernet driver. It binds Linux `struct ethtool_ops` callbacks to ICE PF, safe-mode, and port-representor behavior, exposing driver metadata, register and EEPROM reads, self tests, statistics, link settings, FEC, pause, RSS, channel counts, ring sizing, interrupt coalescing, Wake-on-LAN, module EEPROM data, timestamping information, reset requests, and Flow Director classifier rule operations.

The file is intentionally broad because ethtool is the user-facing control and observability surface for a netdev. Most functions translate ethtool structures into ICE PF/VSI/hardware state, then call lower-level ICE admin queue, flow, filter, RSS, PTP, DCB, or queue-management helpers.

### Important APIs, Types, and Functions

The file defines local mapping structures such as `struct ice_stats`, `struct ice_priv_flag`, and uses `struct ice_port_topology` plus register-dump types from `ice_ethtool.h`. `ice_gstrings_vsi_stats`, `ice_gstrings_pf_stats`, `ice_gstrings_test`, and `ice_gstrings_priv_flags` define userspace-visible string tables. The stability of `ice_get_sset_count()`, `__ice_get_strings()`, and `__ice_get_ethtool_stats()` matters because ethtool statistics are a multi-call ABI where string count, order, and values must remain synchronized.

Driver identity and low-level access are provided through `ice_get_drvinfo()`, `ice_get_regs_len()`, `ice_get_regs()`, `ice_get_extended_regs()`, `ice_get_eeprom_len()`, and `ice_get_eeprom()`. Extended register dumping maps logical ports to PCS/SerDes topology and reads SerDes equalization through admin queue calls.

Diagnostics are implemented by `ice_self_test()` and helpers `ice_link_test()`, `ice_eeprom_test()`, `ice_reg_test()`, `ice_intr_test()`, and `ice_loopback_test()`. Offline diagnostics stop the netdev if needed, set `ICE_TESTING`, reject active VFs, create a temporary loopback VSI, program MAC loopback, send test frames, validate receive descriptors, and restore the device.

Link and PHY management is centered around `ice_get_link_ksettings()` and `ice_set_link_ksettings()`. Helper layers map ICE PHY type bits to ethtool link modes (`ice_phy_type_to_ethtool()`), convert requested speed advertisements to admin queue speed masks (`ice_ksettings_find_adv_link_speed()`, `ice_speed_to_aq_link()`), validate autonegotiation (`ice_setup_autoneg()`), and save requested PHY state in `pi->phy`. FEC is exposed with `ice_get_fecparam()`, `ice_set_fecparam()`, `ice_set_fec_cfg()`, and FEC counter callbacks.

Queue and traffic steering management includes `ice_get_ringparam()`, `ice_set_ringparam()`, `ice_get_channels()`, `ice_set_channels()`, `ice_get_rxfh()`, `ice_set_rxfh()`, `ice_get_rxfh_fields()`, `ice_set_rxfh_fields()`, `ice_get_rxnfc()`, and `ice_set_rxnfc()`. The RX NFC functions integrate with `ice_ethtool_fdir.c` through `ice_add_fdir_ethtool()`, `ice_del_fdir_ethtool()`, `ice_get_ethtool_fdir_entry()`, and `ice_get_fdir_fltr_ids()`.

Interrupt coalescing is exposed by `ice_get_coalesce()`, `ice_set_coalesce()`, and the per-queue variants. These read and update `ice_ring_container` ITR mode/settings and queue-vector INTRL values. Timestamping and PTP observability is provided by `ice_get_ts_info()` and `ice_get_ts_stats()`.

The exported setup functions are `ice_adv_lnk_speed_maps_init()`, `ice_set_ethtool_safe_mode_ops()`, `ice_set_ethtool_repr_ops()`, and `ice_set_ethtool_ops()`.

### Control Flow and Integration

The final registration point is one of three ethtool ops tables. `ice_ethtool_ops` is the full PF/netdev table. `ice_ethtool_safe_mode_ops` exposes a reduced set when package download or advanced features are unavailable. `ice_ethtool_repr_ops` exposes driver info, link, stats, and VF reset for port representors.

Most callbacks begin by resolving `netdev_priv(netdev)` or `ice_netdev_to_pf(netdev)` into an `ice_vsi`, `ice_pf`, and `ice_hw`. They then validate the VSI type, feature flags, reset state, media type, or queue availability before touching hardware. Configuration callbacks generally serialize with `ICE_CFG_BUSY`, netdev carrier state, queue-down/up flows, or explicit device locks.

Link setting control is a multi-step flow: get PHY caps, compute supported/advertised modes, reject unsupported advertisement bits, check autoneg, read current link status, convert advertisement to ICE PHY types, intersect with media or lenient-mode NVM masks, optionally mark carrier down, call `ice_aq_set_phy_cfg()`, then persist `curr_user_speed_req` and `req_speeds`. FEC, pause, and N-way reset follow the same design pattern: map ethtool semantics to the current ICE PHY/admin queue representation and persist requested state only after accepted hardware calls.

Ring resizing is cautious. It validates descriptor counts and AF_XDP state, allocates replacement Tx/Rx/XDP rings while the old netdev remains live, then brings the VSI down and swaps rings. If the netdev is down, it only updates stored descriptor counts for the next open. Channel changes reject safe mode, ADQ, active Flow Director filters, invalid TC counts, and active RDMA clients before calling `ice_vsi_recfg_qs()` and updating RSS LUT sizing.

Flow Director enters through `ice_set_rxnfc()` and `ice_get_rxnfc()`. Insert and delete commands are delegated to `ice_ethtool_fdir.c`; count/list/read commands use `hw->fdir_active_fltr`, `ice_get_fdir_cnt_all()`, and the Flow Director in-memory list.

### State and Persistence Behavior

The file mutates several long-lived driver fields. `pf->msg_enable` and, without dynamic debug, `pf->hw.debug_mask` hold message-level settings. `pf->flags` stores private flags such as FW LLDP agent, VF true promiscuous support, VF VLAN pruning, and link-down-on-close; `ice_set_priv_flags()` computes changed bits and may trigger LLDP/DCB reconfiguration.

PHY user state persists in `pi->phy.curr_user_phy_cfg`, `pi->phy.curr_user_fec_req`, `pi->phy.curr_user_speed_req`, and `pi->phy.link_info.req_speeds`. Flow control persists in `pi->fc.req_mode`. Queue/ring configuration persists in `vsi->num_tx_desc`, `vsi->num_rx_desc`, ring `count` fields, `vsi->hsplit`, `vsi->rss_size`, `vsi->rss_lut_user`, `vsi->rss_hkey_user`, and `vsi->rss_hfunc`. Coalescing persists in q-vector/ring-container ITR and INTRL fields. WoL persists in `pf->wol_ena` and the device wakeup setting.

Statistics are not written to disk but are long-lived counters in PF/VSI/ring/PTP structures. EEPROM and module reads acquire hardware resources and copy bytes to ethtool buffers without modifying NVM.

### Dependencies and Integration Points

This file depends heavily on `ice.h`, `ice_ethtool.h`, `ice_flow.h`, `ice_fltr.h`, `ice_lib.h`, `ice_dcb_lib.h`, Linux ethtool/netdev APIs, DCBNL, libeth RX buffer types, PCI device naming, admin queue calls, register accessors `rd32()`/`wr32()`, queue setup/teardown helpers, RSS helpers, Flow Director helpers, PTP state, RDMA auxiliary device state, and representor operations.

Externally visible integration points are ethtool commands such as driver info, stats, tests, link settings, pause/FEC, RSS, ntuple classifier, module EEPROM, ring/channel/coalesce configuration, reset, and timestamping. In-driver integration is strongest with Flow Director, DCB/LLDP, queue reconfiguration, PTP, safe mode, ADQ, XDP/AF_XDP, and VF representors.

### Risks and Edge Cases

The main ABI risk is changing statistic string counts or ordering without matching value output. Hardware access risk is concentrated in register tests, NVM access, module EEPROM reads, and admin queue PHY changes. Offline tests can disrupt traffic, so active VFs are rejected and the netdev is reopened on exit.

Concurrency risks include `ICE_CFG_BUSY` timeout handling, reset-in-progress interaction, queue reconfiguration while AF_XDP/ADQ/RDMA/Flow Director are active, and representor readiness. Link-mode handling has media-specific edge cases, especially lenient mode, link override TLVs, 1000M copper/optical mapping, and FEC/autoneg semantics. Ring resizing must avoid leaking partially allocated rings and must preserve timestamps, tails, XDP ring identity, and head split state.

### Test Signals

Useful test signals include `ethtool -i`, `ethtool -S`, `ethtool --show-priv-flags`, private flag toggles for LLDP/VF settings, online and offline `ethtool -t`, `ethtool -k/-K` only as adjacent checks, `ethtool -s` link speed/autoneg cases, `ethtool --show-fec/--set-fec`, pause changes with and without PFC, ring size changes while up/down and with AF_XDP attached, channel changes with ADQ/FDir/RDMA constraints, RSS key/LUT/symmetric hash changes, `ethtool -n/-N` classifier paths, module EEPROM reads, reset flags, and PTP timestamp info when PTP is ready.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ethtool.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ethtool.h

### Purpose

`ice_ethtool.h` provides local ethtool support definitions for the ICE driver. It is not a broad public API header; it primarily defines helper data structures and lookup tables used by `ice_ethtool.c` to translate ICE hardware PHY type bits into Linux ethtool link mode bits and to format extended register/SerDes equalization dump data.

### Important APIs, Types, and Data

`struct ice_phy_type_to_ethtool` maps an ICE admin queue link speed bitmask (`aq_link_speed`) to an ethtool link mode bit (`link_mode`). The `ICE_PHY_TYPE()` macro builds entries from ICE admin queue speed names and ethtool mode names.

`phy_type_low_lkup[]` and `phy_type_high_lkup[]` are static const lookup tables indexed by ICE PHY type bit positions. The low table covers PHY type low bits from 100M through 100G variants. The high table covers newer 100G and 200G variants. `ice_ethtool.c` iterates these arrays in `ice_phy_type_to_ethtool()` and sets supported/advertised bits when the corresponding PHY type masks are present.

`struct ice_serdes_equalization_to_ethtool` is a packed driver-side presentation structure for many SerDes equalization parameters. It contains RX equalization values such as pre/post taps, CTLE gain/bandwidth, and DFE values, plus TX equalization values such as pre, post, and attenuation. `struct ice_regdump_to_ethtool` groups up to four of these per port because a multilane port can have up to four SerDes lanes.

`struct ice_port_topology` holds the derived physical topology for a logical port: PCS port, primary SerDes lane, SerDes lane count, and PCS quad select. It is filled in `ice_get_port_topology()` and then used for extended register dump and FEC counter lookup.

### Control Flow and Integration

The header's PHY lookup tables are consumed at runtime by the ethtool link settings path. `ice_phy_type_to_ethtool()` receives PHY type low/high masks from current media, NVM, or link override state. It then walks `phy_type_low_lkup[]` and `phy_type_high_lkup[]`, setting ethtool supported and advertising bits according to the tables.

The equalization and topology structures are used in the register dump path. `ice_get_regs_len()` includes `sizeof(struct ice_regdump_to_ethtool)`, `ice_get_extended_regs()` derives `struct ice_port_topology`, and `ice_get_tx_rx_equa()` fills each `struct ice_serdes_equalization_to_ethtool` entry with values returned by firmware admin queue calls.

### State and Persistence Behavior

This header itself owns no mutable runtime state. Its lookup arrays are static const data compiled into the driver. The data they help populate is transient ethtool output or driver stack/local structures. The only persistence concern is ABI-like: changing the layout of `struct ice_regdump_to_ethtool` changes what `ice_get_regs()` copies into the ethtool register dump buffer, and changing link mode table entries changes userspace-visible supported/advertised link modes.

### Dependencies and Integration Points

The header assumes ICE admin queue speed macros such as `ICE_AQ_LINK_SPEED_*`, PHY type bit ordering from ICE admin queue headers, and Linux ethtool link mode bit names. It is included by `ice_ethtool.c` and is tightly coupled to the ICE firmware's definition of PHY type low/high bit positions.

### Risks and Edge Cases

The highest risk is incorrect table indexing. Each array index must correspond to the hardware PHY type bit documented in ICE admin queue headers. A shifted or stale entry would advertise the wrong cable/media capability to userspace and could allow invalid speed selections. The high table also only defines currently supported high bits; future PHY types require explicit additions.

The register dump structs are used as raw ethtool data. Field layout changes should be treated cautiously because userspace tooling may decode this binary region by driver version.

### Test Signals

Test through `ethtool <dev>` and `ethtool --show-fec`/link settings on ports with varied media: SFP, QSFP, BASE-T, backplane, direct attach, 25G/50G/100G/200G capable modules, link up and link down. Register dump tests should verify `ethtool -d` length and decode stability, especially on one-lane, two-lane, and four-lane ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ethtool_fdir.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ethtool_fdir.c

### Purpose

`ice_ethtool_fdir.c` is the ethtool ntuple/classifier translation and orchestration layer for ICE Flow Director sideband filters. It converts `struct ethtool_rxnfc` and `struct ethtool_rx_flow_spec` requests into `struct ice_fdir_fltr` objects, validates ethtool masks against hardware-supported extraction profiles, programs or removes Flow Director flow profiles, writes filter add/delete training packets, maintains the in-memory filter list, and exposes filter read/list operations back to ethtool.

This file sits between `ice_ethtool.c` and lower-level Flow Director helpers in `ice_fdir.c` and `ice_flow.c`. Its main exported functions are `ice_get_ethtool_fdir_entry()`, `ice_get_fdir_fltr_ids()`, `ice_fdir_rem_adq_chnl()`, `ice_fdir_release_flows()`, `ice_fdir_replay_flows()`, `ice_fdir_num_avail_fltr()`, `ice_fdir_replay_fltrs()`, `ice_fdir_create_dflt_rules()`, `ice_fdir_del_all_fltrs()`, `ice_vsi_manage_fdir()`, `ice_del_fdir_ethtool()`, and `ice_add_fdir_ethtool()`.

### Important APIs, Types, and Functions

Flow type translation is handled by `ice_fltr_to_ethtool_flow()` and `ice_ethtool_flow_to_fltr()`. These map common ethtool flow types such as `TCP_V4_FLOW`, `UDP_V6_FLOW`, `IPV4_USER_FLOW`, `IPV6_USER_FLOW`, and `ETHER_FLOW` to ICE `enum ice_fltr_ptype` values. Unsupported types become `ICE_FLTR_PTYPE_NONF_NONE` or ethtool flow `0`.

Filter retrieval uses `ice_get_ethtool_fdir_entry()` to fill an ethtool flow spec from an existing `ice_fdir_fltr` selected by location. `ice_get_fdir_fltr_ids()` walks `hw->fdir_list_head` under `hw->fdir_fltr_lock` and returns active filter IDs.

Hardware profile management uses `struct ice_fd_hw_prof` entries stored in `hw->fdir_prof[flow]`. `ice_fdir_alloc_flow_prof()` allocates the table, `ice_fdir_set_hw_fltr_rule()` creates ICE flow profiles and entries for main VSI, control VSI, and ADQ channel VSIs, `ice_fdir_rem_flow()` releases a flow profile, and `ice_fdir_replay_flows()` rebuilds hardware flow profiles after reset. `ice_fdir_rem_adq_chnl()` removes ADQ channel VSI entries from existing profiles.

Input-set validation is split by protocol. `ice_set_fdir_ip4_seg()`, `ice_set_fdir_ip4_usr_seg()`, `ice_set_fdir_ip6_seg()`, `ice_set_fdir_ip6_usr_seg()`, `ice_set_ether_flow_seg()`, and `ice_set_fdir_vlan_seg()` build `struct ice_flow_seg_info` masks. They accept only full masks or zero masks for supported fields, reject empty rules, and return `-EOPNOTSUPP` for partially masked or unsupported fields such as TOS/TC/protocol in several paths. `ice_parse_rx_flow_user_data()` handles `FLOW_EXT` user-defined 16-bit flex-word filters and validates the encoded offset/mask.

Filter write operations go through `ice_fdir_write_fltr()` and `ice_fdir_write_all_fltr()`. These allocate raw packet buffers, call `ice_fdir_get_prgm_desc()` and `ice_fdir_get_gen_prgm_pkt()` from `ice_fdir.c`, submit the packet to the control VSI via `ice_prgm_fdir_fltr()`, and repeat for fragment templates when supported. `ice_fdir_write_all_fltr()` writes both non-tunnel and tunnel variants when a tunnel port is open.

`ice_add_fdir_ethtool()` and `ice_del_fdir_ethtool()` are the ethtool entry points called from `ice_ethtool.c`. They enforce feature enablement, reset/flush constraints, capacity limits, duplicate detection, profile compatibility, list updates, and hardware programming.

### Control Flow

Adding a filter starts in `ice_add_fdir_ethtool()`. The function validates VSI and `ICE_FLAG_FD_ENA`, rejects reset state, parses optional user-defined flex data, rejects `FLOW_MAC_EXT`, configures the extraction sequence through `ice_cfg_fdir_xtrct_seq()`, checks the requested location against total Flow Director capacity, checks remaining guaranteed/shared filter availability, allocates `struct ice_fdir_fltr`, converts the ethtool flow spec into ICE filter data with `ice_set_fdir_input_set()`, then takes `hw->fdir_fltr_lock`.

Under the lock, it rejects duplicates with `ice_fdir_is_dup_fltr()`, copies flex filter details, sets descriptor status/counter/reporting fields, updates or inserts the software list entry through `ice_fdir_update_list_entry()`, and writes all hardware variants. If hardware programming fails after list insertion, it rolls back counters, per-channel sideband counts, and the list node before freeing the input.

Deleting a filter starts in `ice_del_fdir_ethtool()`. It validates Flow Director enablement and reset/flush state, locks `hw->fdir_fltr_lock`, then calls `ice_fdir_update_list_entry()` with `input == NULL`. That removes hardware filter programming, decrements counters, updates ADQ per-queue filter count, deletes the list node, frees it, and if the deleted filter was the last one for the flow type, removes or restores the corresponding hardware profile.

Profile configuration flows from ethtool masks to `ice_flow_seg_info` and then to `ice_flow_add_prof()`/`ice_flow_add_entry()`. A key invariant is that all filters for a given flow type on a port must share the same input set. If a new request asks for a different input set while filters exist, the request fails. If no filters exist, the old profile can be removed and replaced unless aRFS is using the perfect flow.

Default rules are created by `ice_fdir_create_dflt_rules()` for IPv4 TCP/UDP and IPv6 TCP/UDP. `ice_vsi_manage_fdir()` enables these defaults when turning Flow Director on and deletes all filters/profiles when disabling.

### State and Persistence Behavior

The core persistent runtime state is in `hw->fdir_prof`, `hw->fdir_list_head`, `hw->fdir_fltr_lock`, `hw->fdir_active_fltr`, `hw->fdir_fltr_cnt[]`, `hw->fdir_perfect_fltr`, PF flag `ICE_FLAG_FD_ENA`, PF state bit `ICE_FD_FLUSH_REQ`, VSI guaranteed filter allocation `vsi->num_gfltr`, and ADQ channel per-ring sideband filter counters.

Filter list entries are allocated with devm memory and sorted by `fltr_id`. They persist across ordinary operations and are replayed after reset by `ice_fdir_replay_fltrs()`. Hardware flow profile entries and filter entries are not permanent across reset, so `ice_fdir_release_flows()`, `ice_fdir_replay_flows()`, and `ice_fdir_replay_fltrs()` rebuild them from driver state.

Counter persistence is split between software counters (`hw->fdir_active_fltr`, `hw->fdir_fltr_cnt[]`) and hardware usage counters read from `VSIQF_FD_CNT` and `GLQF_FD_CNT` in `ice_fdir_num_avail_fltr()`. E810 and E830 use different field definitions.

### Dependencies and Integration Points

This file depends on `ice.h`, `ice_lib.h`, `ice_fdir.h`, `ice_flow.h`, Linux ethtool flow-spec structures, netdev VLAN helpers, tunnel-port state, ADQ channel structures, and ICE flow profile APIs. It calls `ice_fdir_get_prgm_desc()`, `ice_fdir_get_gen_prgm_pkt()`, `ice_fdir_has_frag()`, `ice_fdir_find_fltr_by_idx()`, `ice_fdir_list_add_fltr()`, `ice_fdir_update_cntrs()`, and `ice_fdir_is_dup_fltr()` from `ice_fdir.c`.

It integrates with `ice_ethtool.c` through RX NFC callbacks and with reset/replay paths elsewhere in the driver. It also coordinates with ADQ (`ice_is_adq_active()`, channel VSI lists), aRFS (`ice_is_arfs_using_perfect_flow()`), control VSI programming (`ice_get_ctrl_vsi()`), main VSI selection, and tunnel configuration.

### Risks and Edge Cases

Input-set compatibility is the main correctness risk. Flow Director hardware profiles are shared per flow type, so accepting incompatible masks while active filters exist would break existing matches. Partial mask handling is intentionally restrictive; relaxing it requires matching hardware extraction support.

Concurrency risks center on `hw->fdir_fltr_lock`, reset state, and flush state. Add/delete must not race reset replay or filter flush. Rollback paths are important because a software list entry may be inserted before hardware programming fails.

Capacity accounting is subtle because a single logical ethtool filter may need both tunnel and non-tunnel hardware filters. ADQ remapping changes the destination VSI and relative queue index, so tests must cover filters targeting channel queues. Duplicate detection is delegated to `ice_fdir.c` and does not compare every advanced flow type equally; newly added flow types need duplicate comparison support.

### Test Signals

Use `ethtool -N` to add and delete TCP/UDP/SCTP IPv4 and IPv6 rules, user IPv4/IPv6 rules, ether rules, VLAN-qualified ether rules, drop rules, and flex-word rules. Verify `ethtool -n` single-rule and list output, duplicate rejection, partial mask rejection, max-location and capacity errors, tunnel-port open/closed behavior, ADQ queue remapping, reset replay, Flow Director disable cleanup, and per-channel sideband filter counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ethtool_fdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fdir.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fdir.c

### Purpose

`ice_fdir.c` provides the low-level Flow Director data-plane construction helpers for the ICE driver. It defines static no-op/training packet templates for supported filter protocol types, builds Flow Director programming descriptors, allocates Flow Director hardware resources, generates raw packets from `struct ice_fdir_fltr` match data, maintains the sorted software filter list, updates Flow Director counters, and detects duplicate filters.

This file is lower level than `ice_ethtool_fdir.c`: it does not parse ethtool flow specs. Instead, it consumes already-normalized `struct ice_fdir_fltr` objects and turns them into descriptor plus packet data suitable for `ice_prgm_fdir_fltr()`.

### Important APIs, Types, and Functions

The large static packet-template section defines raw Ethernet/IP/L4/tunnel packet byte arrays for many ICE filter packet types: non-fragmented Ethernet, IPv4 TCP/UDP/SCTP/other, IPv6 TCP/UDP/SCTP/other, GTP-U inner IPv4 variants, L2TPv3, ESP, AH, NAT-T ESP, PFCP node/session, non-IP L2, and tunnel templates. `ice_fdir_pkt[]` maps each `enum ice_fltr_ptype` to its non-tunnel and tunnel template and length.

Descriptor programming starts with `ice_set_dflt_val_fd_desc()`, which fills default descriptor context values such as completion queue/reporting, Flow Director space, counter enablement, eviction, destination behavior, flex metadata, descriptor type, profile priority, swap behavior, and FDID metadata. `ice_set_fd_desc_val()` packs the context into `struct ice_fltr_desc` qwords with `FIELD_PREP()`. `ice_fdir_get_prgm_desc()` applies per-filter add/delete command, drop/direct destination, queue, VSI, counter, FDID, priority, and completion report before packing.

Resource helpers `ice_alloc_fd_res_cntr()`, `ice_free_fd_res_cntr()`, `ice_alloc_fd_guar_item()`, `ice_alloc_fd_shrd_item()`, and `ice_get_fdir_cnt_all()` wrap ICE admin queue resource allocation for Flow Director counters and guaranteed/shared filter entries.

Packet synthesis uses insertion helpers `ice_pkt_insert_ipv6_addr()`, `ice_pkt_insert_u6_qfi()`, `ice_pkt_insert_u8()`, `ice_pkt_insert_u8_tc()`, `ice_pkt_insert_u16()`, `ice_pkt_insert_u32()`, and `ice_pkt_insert_mac_addr()`. The main function `ice_fdir_get_gen_prgm_pkt()` selects the correct base template, optionally switches IPv4/IPv6 "other" flows to TCP/UDP/SCTP templates based on protocol, optionally fills tunnel destination port and inner packet offset, then writes filter fields into the packet. It reverses source and destination because user input is from RX perspective while hardware programming expects TX perspective.

List and duplicate helpers include `ice_fdir_find_fltr_by_idx()`, `ice_fdir_list_add_fltr()`, `ice_fdir_update_cntrs()`, `ice_fdir_has_frag()`, `ice_fdir_is_dup_fltr()`, and local comparison helpers. The list is ordered by `fltr_id`, which makes location lookup and ordered listing deterministic.

### Control Flow

The normal add/delete path is orchestrated by `ice_ethtool_fdir.c`, which calls `ice_fdir_get_prgm_desc()` and `ice_fdir_get_gen_prgm_pkt()` through `ice_fdir_write_fltr()`. Descriptor construction and packet construction are independent: the descriptor tells hardware what to do with a matched packet and the synthetic packet tells hardware what exact key to program.

`ice_fdir_get_gen_prgm_pkt()` first resolves the effective flow type. For `ICE_FLTR_PTYPE_NONF_IPV4_OTHER` or IPv6 other, it inspects `input->ip.v4.proto` or `input->ip.v6.proto` and may use TCP, UDP, or SCTP templates. It then finds the template in `ice_fdir_pkt[]`. For tunnel programming, it requires an open tunnel port, copies the tunnel template, writes the outer UDP destination tunnel port, and points `loc` to the inner packet offset. For non-tunnel programming, it copies the base template and points `loc` to the packet start.

The switch over flow type writes fields at fixed offsets defined in `ice_fdir.h`. IPv4/IPv6 address and port fields are reversed relative to RX input, ToS/TTL or TC/hop-limit are inserted where supported, destination MACs are inserted for several flows, GTP-U TEID and QFI fields are inserted, L2TPv3 session IDs and IPsec SPI fields are inserted, PFCP ports are inserted, and optional flex-word data is written at `input->flex_offset`. IPv4 "other" may generate an additional fragment packet through `ice_fdir_has_frag()`.

The software list path is simple but important. `ice_fdir_list_add_fltr()` inserts by ascending `fltr_id`; `ice_fdir_find_fltr_by_idx()` stops once it passes the requested ID; `ice_fdir_update_cntrs()` increments or decrements total and per-flow counters. `ice_fdir_is_dup_fltr()` walks same-flow entries and compares relevant key fields, with a special case allowing same filter ID with a different queue to be treated as an update rather than a duplicate.

### State and Persistence Behavior

This file manipulates in-memory driver state, not persistent storage. `hw->fdir_list_head` stores active software filter definitions. `hw->fdir_active_fltr` and `hw->fdir_fltr_cnt[]` track total and per-flow active filters. Hardware resource counters are allocated/freed through admin queue resource helpers. The packet template arrays are immutable static data.

The generated programming packets and descriptors are transient per hardware programming operation. The software list is the durable driver copy used for ethtool reporting and replay by higher layers after reset. Incorrect list or counter updates can therefore cause both observability and replay errors.

### Dependencies and Integration Points

The file includes `ice_common.h` and relies on definitions from `ice_fdir.h`, ICE admin queue resource APIs, ICE flow/filter descriptor field macros, ICE register/resource definitions, Linux Ethernet helpers, and net byte-order types. Its exported functions are consumed by `ice_ethtool_fdir.c` and other Flow Director setup/replay paths.

It integrates directly with hardware programming semantics: descriptor bit layout, packet offsets, fixed tunnel offset `ICE_FDIR_TUN_PKT_OFF`, open tunnel port discovery, and ICE flow packet type enums. Any change in hardware parser expectations must be reflected in both templates and offsets.

### Risks and Edge Cases

The largest risk is offset/template mismatch. The fixed offsets in `ice_fdir.h` must match the byte arrays in this file. A wrong packet length, protocol byte, or offset would silently program filters that do not match traffic. The source/destination reversal is required by hardware perspective and is easy to break when adding a new flow.

Tunnel programming depends on an open tunnel port and uses a fixed inner offset. Unsupported tunnel templates return errors or skip tunnel writes at higher layers. Fragment support is currently only reported for IPv4 other flows, so new fragmented flow support needs explicit updates.

Duplicate detection is incomplete for newer specialty flows such as GTP-U, L2TPv3, ESP/AH, NAT-T ESP, PFCP, and non-IP L2 unless their compared fields are added. This can allow semantically duplicate filters or reject too little, depending on higher-level constraints.

### Test Signals

Low-level validation should exercise add/delete for each packet template family, then verify hardware match behavior with real packets where possible. Useful tests include IPv4/IPv6 TCP/UDP/SCTP source/destination reversal, IPv4 other fragment programming, tunnel and non-tunnel programming, GTP-U TEID/QFI insertion, L2TPv3 session ID, IPsec SPI flows, PFCP node/session, non-IP L2 ethertype, flex-word offsets, sorted rule locations, duplicate detection, counter increments/decrements, and reset replay from the software list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fdir.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fdir.h

### Purpose

`ice_fdir.h` defines the shared Flow Director data structures, packet offsets, descriptor context types, and function prototypes used by ICE Flow Director implementation files. It is the contract between ethtool Flow Director translation, raw packet/descriptor construction, and the rest of the ICE driver.

### Important APIs, Types, and Constants

Packet offset macros define where `ice_fdir.c` inserts match data into synthetic programming packets. They cover Ethernet ethertype/VLAN offsets, IPv4/IPv6 source and destination addresses, TCP/UDP/SCTP ports, IPv4 protocol/TOS/TTL, IPv6 next-header/traffic-class/hop-limit, GTP-U TEID/QFI, L2TPv3 session ID, ESP/AH SPI, and NAT-T ESP SPI. `ICE_FDIR_TUN_PKT_OFF` marks the inner packet offset for tunnel templates, and `ICE_FDIR_MAX_RAW_PKT_SIZE` bounds raw programming packet buffers.

`ICE_FDIR_MAX_FLTRS` defines a 16384 filter upper bound, while `ICE_FDIR_NO_QUEUE_IDX` represents no queue target. `ICE_FDIR_IPV4_PKT_FLAG_MF` is the IPv4 "more fragments" bit used for fragment template generation.

`enum ice_fltr_prgm_desc_dest` defines descriptor destination behavior: drop, direct to queue index, direct to queue group, or direct to other. `enum ice_fltr_prgm_desc_fd_status` defines whether the descriptor reports no status or FD ID status.

`struct ice_fd_fltr_desc_ctx` is an unpacked software representation of the hardware Flow Director programming descriptor fields. `ice_fdir_get_prgm_desc()` fills this and packs it into `struct ice_fltr_desc`.

`struct ice_rx_flow_userdef` holds parsed ethtool `FLOW_EXT` user-defined flex filter data: flex word, offset, and enabled flag. `struct ice_fdir_v4`, `struct ice_fdir_v6`, `struct ice_fdir_udp_gtp`, `struct ice_fdir_l2tpv3`, and `struct ice_fdir_extra` hold protocol-specific match data and masks. `struct ice_fdir_fltr` is the central software filter object: list node, flow type, Ethernet/IP/tunnel/extra data and masks, flex fields, queue/destination controls, counter data, filter ID, priority, and completion reporting.

`struct ice_fdir_base_pkt` maps a flow type to raw non-tunnel and tunnel packet templates. The prototypes export resource allocation, descriptor generation, packet generation, capacity, duplicate detection, fragment support, list lookup, counter updates, and list insertion.

### Control Flow and Integration

The header is included by `ice_ethtool_fdir.c` and used indirectly by `ice_fdir.c`. Ettool parsing fills `struct ice_fdir_fltr` and `struct ice_rx_flow_userdef`; low-level programming reads the same filter object to generate descriptors and packets. The fixed packet offset macros are the bridge between high-level protocol fields and byte-level packet templates.

Resource helpers (`ice_alloc_fd_res_cntr()`, `ice_free_fd_res_cntr()`, `ice_alloc_fd_guar_item()`, `ice_alloc_fd_shrd_item()`) integrate with ICE admin queue resource counters. Programming helpers (`ice_fdir_get_prgm_desc()`, `ice_fdir_get_gen_prgm_pkt()`) integrate with control VSI transmit programming. List helpers (`ice_fdir_find_fltr_by_idx()`, `ice_fdir_list_add_fltr()`, `ice_fdir_is_dup_fltr()`, `ice_fdir_update_cntrs()`) integrate with ethtool rule add/delete/list/replay behavior.

### State and Persistence Behavior

The header does not allocate state itself, but it defines the shape of persistent runtime Flow Director state. `struct ice_fdir_fltr` instances are stored in `hw->fdir_list_head`, survive across normal ethtool operations, and are used for reset replay. Counter fields and destination fields in the structure determine hardware programming, ethtool reporting, and per-flow accounting.

The packet offset constants are compile-time persistent assumptions. They must remain aligned with the packet byte templates in `ice_fdir.c`; otherwise the driver will persist and replay filters with wrong keys.

### Dependencies and Integration Points

This header depends on Linux networking types (`struct ethhdr`, `ETH_ALEN`, byte-order integer types, `struct list_head`) and ICE-internal enums/types such as `enum ice_fltr_ptype`, `struct ice_hw`, `struct ice_vsi`, and `struct ice_fltr_desc`. It is part of the ICE Flow Director API surface used by ethtool, reset replay, ADQ interaction, and hardware programming.

### Risks and Edge Cases

Adding new flow types requires coordinated updates in several places: packet offsets and data structures here, packet templates and insertion logic in `ice_fdir.c`, ethtool mask parsing and profile setup in `ice_ethtool_fdir.c`, duplicate comparison, and reporting back to ethtool. A mismatch in any layer can create filters that program successfully but do not match traffic.

Bitfield layout in `struct ice_fdir_udp_gtp` is compiler and endian sensitive if used directly as wire layout; current code mostly uses explicit fields such as TEID and QFI insertion. Descriptor context fields must match hardware descriptor masks and shifts used by `ice_fdir.c`.

### Test Signals

Build coverage should catch missing prototypes and type drift. Runtime tests should focus on every macro offset family: Ethernet/VLAN, IPv4/IPv6 L3 fields, L4 ports, GTP-U, L2TPv3, ESP/AH/NAT-T ESP, PFCP, flex-word insertion, drop/direct destination modes, queue-group fields, counter enablement, duplicate/list behavior, and reset replay of stored `struct ice_fdir_fltr` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fdir.h -->
