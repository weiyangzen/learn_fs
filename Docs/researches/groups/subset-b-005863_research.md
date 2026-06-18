# Research: subset-b-005863

This grouped report covers the requested Linux networking and IIO headers under `sources/distributed-fs/ceph-client/include/linux`. Each section is source-tree aligned and wrapped for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211.h -->
# `sources/distributed-fs/ceph-client/include/linux/ieee80211.h`

Purpose: central in-kernel IEEE 802.11 definition header for Wi-Fi frame formats, element IDs, action/status/reason codes, cipher/AKM suite constants, and inline frame parsers used by mac80211/cfg80211/drivers. It is a dense protocol contract rather than a storage component.

Important APIs/types/functions: frame-control masks and subtype constants, sequence helpers (`ieee80211_sn_less`, `ieee80211_sn_add`, `IEEE80211_SEQ_TO_SN`), packed protocol structures such as `ieee80211_hdr`, `ieee80211_mgmt`, TIM/channel switch/TPC/TSPEC/RNR elements, robust/public/action helpers, `ieee80211_get_qos_ctl`, `ieee80211_get_tid`, `ieee80211_get_SA`, `ieee80211_get_DA`, `ieee80211_check_tim`, `ieee80211_get_tdls_action`, and element iteration macros.

Control flow and state: all logic is inline, stateless parsing over caller-owned frame buffers and `sk_buff` data. Control flow is mostly bitmask classification, length guarding, address offset selection based on ToDS/FromDS/A4 bits, and bounded IE iteration.

Dependencies/integration: depends on Ethernet definitions, byteorder/unaligned helpers, `sk_buff`, and companion 802.11 capability headers (`ieee80211-ht.h`, `-vht.h`, `-he.h`, `-eht.h`, `-uhr.h`, mesh/S1G/P2P/NAN). Wireless drivers rely on these constants matching the standard and userspace ABI expectations.

Risks: malformed management frames can drive out-of-bounds reads if callers bypass length-checked wrappers; endian mistakes corrupt classification; element iteration requires `for_each_element_completed()` when malformed tails matter; suite and EID values are compatibility-sensitive; sequence-number comparisons require modulo semantics.

Test signals: compile wireless stack with multiple feature combinations; exercise frame parsing with short/truncated action frames, malformed IEs, TIM bitmaps, TDLS encapsulation, robust management frame checks, and SAE/RSN suite constants; use packet-capture based regression tests for beacon/probe/action parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee802154.h -->
# `sources/distributed-fs/ceph-client/include/linux/ieee802154.h`

Purpose: IEEE 802.15.4 MAC constants and inline helpers for low-rate wireless PAN frames, including PSDU bounds, frame-control parsing, security-control values, MAC status codes, filtering levels, and address validation.

Important APIs/types/functions: `IEEE802154_MTU`, header/footer/address lengths, frame type/security/address-mode masks, MAC command IDs, status enum values, `enum ieee802154_filtering_level`, `ieee802154_is_data`, `ieee802154_is_secen`, `ieee802154_is_ackreq`, address-mode helpers, `ieee802154_is_valid_psdu_len`, short/extended address validators, and `ieee802154_random_extended_addr`.

Control flow and state: purely inline parsing and generation helpers. Random extended address generation mutates caller-provided storage by filling 8 bytes, clearing the group bit, and setting locally administered bit.

Dependencies/integration: depends on kernel types and random bytes. It is consumed by 802.15.4 MAC/PHY drivers and softmac code that build or validate frames.

Risks: FC bit layouts differ across 802.15.4 revisions, so mixed use of legacy and newer masks can misparse frames; address validity is endian-sensitive; PSDU length validation must include MHR/MFR; random address generation must be called only when a stable random address is acceptable.

Test signals: unit or packet tests for every frame-control bit, PSDU boundary lengths 4/5/8/9/127/128, broadcast/unspecified short addresses, zero/group extended addresses, and generated-address local/group bit properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee802154.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_arp.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_arp.h`

Purpose: kernel ARP helpers layered over the UAPI ARP header, giving network code a standard way to locate ARP headers, compute ARP header lengths, and decide whether a netdevice transmits a MAC header.

Important APIs/types/functions: `arp_hdr`, `arp_hdr_len`, and `dev_is_mac_header_xmit`. `arp_hdr_len` special-cases FireWire ARP address sizing and otherwise uses two hardware addresses plus two IPv4 addresses.

Control flow and state: stateless inline helpers over `sk_buff` and `net_device`. `dev_is_mac_header_xmit` switches on `dev->type` and treats tunnel/raw/PPP-like devices as L3 transmit devices.

Dependencies/integration: depends on `linux/skbuff.h`, `net_device`, and UAPI `if_arp.h`. Used by ARP, BPF redirect, traffic control mirred, and device transmit paths.

Risks: wrong `dev->type` classification changes whether callers prepend L2 headers; `arp_hdr_len` assumes IPv4 ARP address structure and device `addr_len` validity; FireWire behavior depends on `CONFIG_FIREWIRE_NET`.

Test signals: ARP packet construction on Ethernet and FireWire, BPF redirect to PPP/tunnel/raw devices, and compile coverage with and without FireWire support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_arp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_bridge.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_bridge.h`

Purpose: internal bridge integration API for multicast snooping, VLAN filtering, MST state, FDB lookup/offload cleanup, bridge ioctl hooks, and bridge-port flag/state queries.

Important APIs/types/functions: `struct br_ip`, `struct br_ip_list`, bridge port flag bits (`BR_HAIRPIN_MODE`, `BR_LEARNING`, `BR_PORT_LOCKED`, etc.), `brioctl_set`, `br_ioctl_call`, multicast query/list helpers, VLAN getters (`br_vlan_get_pvid`, `br_vlan_get_info`), MST getters, `br_fdb_find_port`, `br_fdb_clear_offload`, `br_port_flag_is_set`, `br_port_get_stp_state`, and `br_get_ageing_time`.

Control flow and state: the header exposes live bridge state through `net_device` lookups. When relevant configs are disabled it provides stubs returning false, zero, `NULL`, or `-EINVAL`.

Dependencies/integration: depends on netdevice, UAPI bridge definitions, bitops, IPv6 conditionals, and feature configs `CONFIG_BRIDGE`, `CONFIG_BRIDGE_IGMP_SNOOPING`, and `CONFIG_BRIDGE_VLAN_FILTERING`.

Risks: callers must tolerate stubs under disabled configs; RCU-specific getters (`*_rcu`) require correct read-side locking; FDB and VLAN results are bridge-lifetime dependent; port flags are bit ABI shared across bridge, switchdev, and drivers.

Test signals: build matrix for bridge/snooping/VLAN/MST configs, switchdev offload FDB clear paths, multicast router/querier behavior, VLAN PVID/proto/info lookups under RCU, and STP state fallbacks when bridge is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_eql.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_eql.h`

Purpose: internal structures for the legacy EQL serial-line equalizer/load-balancer driver.

Important APIs/types/functions: `slave_t`, `slave_queue_t`, and `equalizer_t` track member devices, priority/byte accounting, a spinlock-protected slave list, min/max slave counts, and a timer.

Control flow and state: no functions are defined here; state is persistent in the equalizer device private structures and updated by the EQL driver.

Dependencies/integration: depends on timers, spinlocks, netdevice trackers, and UAPI `if_eql.h`.

Risks: legacy code with shared mutable lists and timers; netdevice reference tracking must be balanced; priority and byte counters use `long`, so overflow/sign assumptions matter on old platforms.

Test signals: EQL device add/remove, slave attach/detach, timer-driven balancing, device unregister cleanup, and lockdep coverage around queue list operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_eql.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_ether.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_ether.h`

Purpose: kernel Ethernet header access helpers and MAC formatting declarations layered over UAPI Ethernet constants.

Important APIs/types/functions: `MAC_ADDR_STR_LEN`, `eth_hdr`, `skb_eth_hdr`, `inner_eth_hdr`, `eth_header_parse`, and `sysfs_format_mac`.

Control flow and state: inline pointer casts over the caller-managed `sk_buff` header pointers; no persistent state.

Dependencies/integration: depends on `sk_buff`, UAPI `if_ether.h`, and netdevice parsing/formatting users throughout Ethernet, VLAN, tunneling, sysfs, and drivers.

Risks: helpers assume header pointers have been set and data is pulled enough; `skb_eth_hdr` is TX-path oriented and uses `skb->data`; MAC string length excludes trailing NUL.

Test signals: short skb header tests, TX path callers using `skb_eth_hdr`, inner MAC header tunnel parsing, sysfs MAC formatting buffer sizing, and compile checks for Ethernet UAPI constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_ether.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_fddi.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_fddi.h`

Purpose: ANSI FDDI kernel statistics layout that augments generic netdevice stats with RFC 1512 SMT/MAC/path/port counters and state fields.

Important APIs/types/functions: `struct fddi_statistics`, containing `struct net_device_stats gen` plus station IDs, operation versions, MAC counters, neighbor addresses, frame/error counters, path configuration, and two-port status arrays.

Control flow and state: no functions. The structure is persistent driver/device statistics exported or queried by FDDI code.

Dependencies/integration: depends on netdevice and UAPI `if_fddi.h`; used by FDDI network drivers and ioctl/stat reporting paths.

Risks: fixed-size statistics layout must match legacy consumers; counters are 32-bit and can wrap; old FDDI paths may receive little active testing.

Test signals: FDDI driver build, statistics zero/init/update/export behavior, ioctl ABI size checks, and counter wrap handling where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_fddi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_hsr.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_hsr.h`

Purpose: shared definitions for High-availability Seamless Redundancy and PRP devices, including protocol versions, port roles, HSR tag layout, and optional helper entry points.

Important APIs/types/functions: `enum hsr_version`, `enum hsr_port_type`, packed `struct hsr_tag`, `HSR_HLEN`, `is_hsr_master`, `hsr_get_version`, `hsr_get_port_ndev`, and `hsr_get_port_type`.

Control flow and state: helpers are real only with `CONFIG_HSR`; otherwise stubs return false or `-EINVAL`/`ERR_PTR(-EINVAL)`. Actual state is in HSR netdevices and port mappings outside the header.

Dependencies/integration: depends on kernel types and `struct net_device`; integrated with Ethernet redundancy drivers and consumers checking HSR/PRP topology.

Risks: callers must handle disabled-config stubs; HSR tag fields are packed network order and easy to misalign/mis-endian; port enum ordering is semantically constrained.

Test signals: build with and without HSR, packet tag encode/decode, master/port lookup error handling, and PRP/HSR version detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_hsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_link.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_link.h`

Purpose: kernel-side link metadata supplement for virtual function information, kept separate from the larger UAPI link definitions.

Important APIs/types/functions: `struct ifla_vf_stats` for VF RX/TX packet/byte, multicast/broadcast, and drop counters; `struct ifla_vf_info` for VF MAC, VLAN/QoS, spoof check, link state, min/max TX rate, RSS query enablement, trust, and IB node/port GUIDs.

Control flow and state: no functions. Structures carry snapshot state between netdevice/SR-IOV providers and rtnetlink-style reporting.

Dependencies/integration: used by netdevice VF management and link reporting code; fields mirror netlink attributes.

Risks: ABI/layout drift with UAPI link attributes; partial driver support may leave fields unset; rate and GUID semantics vary by NIC family.

Test signals: SR-IOV VF query through rtnetlink, drivers filling all fields, zero/default behavior for unsupported features, and structure layout compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_link.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_macvlan.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_macvlan.h`

Purpose: internal macvlan device definitions, statistics helpers, link registration hooks, lower-device access, and offload helpers.

Important APIs/types/functions: `struct macvlan_dev`, multicast filter constants, `macvlan_count_rx`, `macvlan_common_setup`, `macvlan_common_newlink`, `macvlan_dellink`, `macvlan_link_register`, `macvlan_dev_real_dev`, `macvlan_accel_priv`, `macvlan_supports_dest_filter`, and `macvlan_release_l2fw_offload`.

Control flow and state: `macvlan_dev` persists per virtual device, linking upper `dev`, lower device, port, accel private data, per-CPU stats, filters, mode, flags, and optional netpoll. `macvlan_count_rx` updates per-CPU VLAN-style counters with `u64_stats_sync`.

Dependencies/integration: depends on netdevice, VLAN stats, rtnetlink/netlink, netpoll, and UAPI macvlan modes. Integrated with macvlan/macvtap link creation and L2 forwarding offload.

Risks: stats require correct per-CPU access and sync; `macvlan_dev_real_dev` BUGs if called when macvlan is unavailable; offload release changes unicast filters on the lower device; mode checks control destination filtering behavior.

Test signals: macvlan create/delete in all modes, RX success/error/multicast stat updates on 32-bit and 64-bit, offload release, disabled-config build behavior, and lower-device unregister handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_macvlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_phonet.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_phonet.h`

Purpose: tiny kernel Phonet interface header exposing header operations in addition to UAPI Phonet definitions.

Important APIs/types/functions: `phonet_header_ops` declaration.

Control flow and state: no inline logic or state; provides an integration symbol for Phonet netdevice setup.

Dependencies/integration: depends on UAPI `if_phonet.h` and `struct header_ops` from networking headers included by users.

Risks: very small surface; build failures mainly come from missing Phonet configuration or incorrect header-ops linkage.

Test signals: Phonet driver compile/link and netdevice setup path using `phonet_header_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_phonet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_pppol2tp.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_pppol2tp.h`

Purpose: PPP over L2TP kernel include wrapper that supplies IPv4/IPv6 address types and UAPI PPPoL2TP socket definitions to the L2TP PPP driver.

Important APIs/types/functions: no new structs or functions beyond including `linux/in.h`, `linux/in6.h`, and UAPI `if_pppol2tp.h`.

Control flow and state: none in this header.

Dependencies/integration: used by `l2tp_ppp.c` and PPPoL2TP socket code that needs both kernel IP types and user-facing sockaddr definitions.

Risks: include-order and ABI compatibility with UAPI structures; functionality lives in PPP/L2TP implementation files.

Test signals: PPPoL2TP socket build, IPv4/IPv6 tunnel setup, and UAPI sockaddr compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_pppol2tp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_pppox.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_pppox.h`

Purpose: generic PPP-over-X kernel socket support for PPPoE/PPTP style transports, including socket private state and protocol registration hooks.

Important APIs/types/functions: `pppoe_hdr`, `struct pppoe_opt`, `struct pptp_opt`, `struct pppox_sock`, `pppox_sk`, `struct pppox_proto`, registration functions, `pppox_unbind_sock`, `pppox_ioctl`, compat ioctl, and socket state enum values.

Control flow and state: PPPoX socket state persists in `struct pppox_sock`, embedding `struct sock` first, a PPP channel, RCU hash linkage, transport-specific union, protocol number, sequence/ack state for PPTP, and PADT work for PPPoE.

Dependencies/integration: depends on netdevice, PPP channel core, workqueues, sockets, and UAPI PPPoX definitions. PPPoE and PPTP modules register `pppox_proto` handlers.

Risks: `struct sock` must remain first for container casting; RCU hash linkage and workqueue teardown must be synchronized; ioctl compatibility matters; PPP channel unbind must avoid use-after-free during disconnect.

Test signals: PPPoE connect/disconnect/PADT handling, PPTP sequence/ack updates, proto register/unregister, ioctl and compat ioctl paths, and socket lifetime under module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_pppox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_rmnet.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_rmnet.h`

Purpose: Qualcomm RMNET MAP header definitions for multiplexed mobile data packets and checksum offload metadata.

Important APIs/types/functions: packed/aligned `struct rmnet_map_header`, downlink checksum trailer, uplink checksum header, MAP v5 checksum header, flag masks for pad length, command, next header, checksum valid/requested, and `RMNET_MAP_HEADER_TYPE_CSUM_OFFLOAD`.

Control flow and state: no functions. The structures describe on-wire per-packet metadata interpreted by RMNET drivers.

Dependencies/integration: depends on kernel integer types, `GENMASK`, `BIT`, and checksum types. Used in RMNET data path encode/decode and checksum offload handling.

Risks: fields are intentionally byte-aligned and network-order; padding, mux ID, and packet length mistakes can corrupt frame parsing; checksum flags differ between uplink/downlink and v5; no helper functions enforce bounds.

Test signals: MAP packet encode/decode with padding, muxed channels, command packets, v5 next-header chains, checksum insertion/validation, and unaligned-access build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_rmnet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_tap.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_tap.h`

Purpose: internal TAP character-device/netdevice bridge definitions, exposing queue/socket accessors, queue limits, TAP device state, and cdev/minor helpers.

Important APIs/types/functions: `tap_get_socket`, `tap_get_ptr_ring`, `MAX_TAP_QUEUES`, `struct tap_dev`, `struct tap_queue`, `tap_handle_frame`, queue deletion/resizing, minor allocation/freeing, and cdev create/destroy.

Control flow and state: `tap_dev` tracks active RCU queue pointers, all queue list entries, queue counts, features, minor, and callbacks for feature/drop accounting. `tap_queue` embeds sock/socket, virtio-net header size, ring, file, flags, queue index, and enabled state.

Dependencies/integration: depends on socket, `skb_array`/`ptr_ring`, char device infrastructure, netdevice RX handlers, and `CONFIG_TAP` stubs.

Risks: multiqueue RCU pointer lifetime, ring resizing under active traffic, disabled-config callers receiving `ERR_PTR(-EINVAL)`, file/socket lifetime coupling, and virtio header size mismatches.

Test signals: TAP open/close, multiqueue attach/detach up to queue limits, queue resize, RX handler delivery, cdev minor allocation cleanup, disabled-config compile, and virtio-net header compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_tap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_team.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_team.h`

Purpose: internal network team device API for port state, mode callbacks, options, per-CPU stats, queue override, netpoll forwarding, and mode registration.

Important APIs/types/functions: `struct team_pcpu_stats`, `struct team_port`, port enabled/txable helpers, `team_netpoll_send_skb`, `struct team_mode_ops`, `struct team_option`, `struct team_mode`, `struct team`, `team_dev_queue_xmit`, tx-port hash/index helpers, first-txable lookup, option register/unregister, mode register/unregister, and `MODULE_ALIAS_TEAM_MODE`.

Control flow and state: persistent team state owns port lists, tx-enabled hash buckets, option lists, selected mode operations, notification delayed work, multicast rejoin work, queue override lists, and mode-private storage. Inline TX path restores queue mapping, changes `skb->dev` to the selected port, and either netpoll-sends or calls `dev_queue_xmit`.

Dependencies/integration: depends on netpoll, qdisc control block, UAPI team options, RCU lists, delayed work, and netdevice LAG semantics.

Risks: RCU and list traversal must match port lifetime; tx index hashing assumes enabled-port count consistency; queue mapping uses qdisc skb CB layout asserted by `BUILD_BUG_ON`; mode callbacks must handle link/user state transitions; delayed work cleanup is critical on teardown.

Test signals: team mode module registration, port add/remove under traffic, failover/load-balance transmit, queue override mapping, netpoll transmit, option setter/getter change notifications, and lockdep/RCU stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_team.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_tun.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_tun.h`

Purpose: internal TUN/TAP access helpers and XDP pointer tagging utilities for the universal TUN driver.

Important APIs/types/functions: `TUN_XDP_FLAG`, `TUN_MSG_UBUF`, `TUN_MSG_PTR`, `struct tun_msg_ctl`, `tun_get_socket`, `tun_get_tx_ring`, `tun_is_xdp_frame`, `tun_xdp_to_ptr`, `tun_ptr_to_xdp`, and `tun_ptr_free`.

Control flow and state: inline helpers encode XDP-frame pointers by setting low bit `TUN_XDP_FLAG`, decode by masking it off, and provide disabled-config stubs returning errors or nulls. Persistent queue state is external to this header.

Dependencies/integration: depends on UAPI TUN and virtio-net headers, optional `CONFIG_TUN`, `struct file`, socket, ptr ring, and XDP frame types.

Risks: pointer tagging assumes XDP frame alignment leaves the low bit clear; callers must distinguish user-buffer vs pointer message types; disabled-config stubs must be handled; `tun_ptr_free` must match the pointer kind.

Test signals: TUN/TAP open and socket retrieval, TX ring access, XDP frame enqueue/free, pointer tag round-trips, disabled-config builds, and virtio-net header interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_tun.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_tunnel.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_tunnel.h`

Purpose: small internal tunnel helper header that includes IP tunnel UAPI definitions and provides an RCU iteration macro for tunnel hash/list traversal.

Important APIs/types/functions: `for_each_ip_tunnel_rcu(pos, start)`.

Control flow and state: macro follows `pos->next` with `rcu_dereference` until null. The tunnel list/hash state is owned by tunnel drivers.

Dependencies/integration: depends on IPv4/IPv6 headers, UAPI `if_tunnel.h`, `u64_stats_sync`, and RCU conventions.

Risks: caller must hold appropriate RCU read lock or RTNL as documented; `pos` type must have `next`; mutation outside the documented locking model risks races.

Test signals: tunnel lookup/list traversal under concurrent add/delete with RCU, lockdep coverage, and build coverage for IP tunnel drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_tunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_vlan.h -->
# `sources/distributed-fs/ceph-client/include/linux/if_vlan.h`

Purpose: internal VLAN 802.1Q/802.1ad API for header layouts, SKB tag manipulation, device-private VLAN state, hardware acceleration metadata, protocol extraction, feature filtering, and VLAN device management hooks.

Important APIs/types/functions: `struct vlan_hdr`, `struct vlan_ethhdr`, tag masks (`VLAN_PRIO_MASK`, `VLAN_CFI_MASK`, `VLAN_VID_MASK`), `struct vlan_pcpu_stats`, `struct vlan_priority_tci_mapping`, `struct vlan_dev_priv`, VLAN device lookup/metadata functions, `is_vlan_dev`, `vlan_dev_get_egress_qos_mask`, `eth_type_vlan`, tag insertion/removal helpers, hwaccel tag helpers, `vlan_get_tag`, `vlan_get_protocol*`, `skb_protocol`, `skb_vlan_tagged`, `skb_vlan_tagged_multi`, `vlan_features_check`, and `compare_vlan_header`.

Control flow and state: persistent VLAN state is in `vlan_dev_priv` with ingress/egress priority maps, proto/id/flags, lower-device reference, proc entry, per-CPU stats, and optional netpoll. Inline data path code may grow SKB headroom, move MAC header bytes, manipulate `skb->vlan_all/vlan_tci/vlan_proto`, parse nested VLANs up to bounded depth through implementation functions, and mask off unsafe offload features for multi-tagged packets.

Dependencies/integration: depends on netdevice, skbuff, rtnetlink, Ethernet helpers, UAPI VLAN definitions, notifiers, RCU, and `CONFIG_VLAN_8021Q`. It is used by core RX/TX, drivers, offload, bridges, and virtual network devices.

Risks: SKB headroom failures transfer ownership for wrapper helpers that free on error; direct `__vlan_insert_*` helpers do not free; hardware-accelerated vs in-payload tags must be kept consistent; egress QoS map traversal requires RCU; protocol extraction can fail if headers are not pulled; disabled-config stubs can hide missing VLAN support; multi-tag feature masking is security/correctness-sensitive.

Test signals: single and stacked VLAN RX/TX, C-tag and S-tag offload, SKB headroom exhaustion, vlan tag get/remove/insert ownership behavior, egress QoS mapping under RCU, protocol extraction with short/nonlinear SKBs, feature masking for QinQ, and builds with VLAN disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/if_vlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/igmp.h -->
# `sources/distributed-fs/ceph-client/include/linux/igmp.h`

Purpose: internal IPv4 IGMP/multicast membership structures and APIs for socket membership lists, device multicast records, source filters, report/query parsing, and IGMP lifecycle operations.

Important APIs/types/functions: `igmp_hdr`, `igmpv3_report_hdr`, `igmpv3_query_hdr`, `struct ip_sf_socklist`, `struct ip_mc_socklist`, `struct ip_sf_list`, `struct ip_mc_list`, IGMPv3 exponential decode macros, `ip_mc_may_pull`, multicast join/leave/source/filter APIs, device init/up/down/remap APIs, group refcount helpers, and `ip_mc_check_igmp`.

Control flow and state: socket multicast lists are RCU-linked; per-interface multicast records hold source lists, timers, user/ref counts, spinlock, reporter state, retransmission counts, timestamps, and RCU teardown. `ip_mc_may_pull` validates transport length before pulling data into linear SKB memory.

Dependencies/integration: depends on SKB, timers, IP, socket pointer abstraction, refcounting, and UAPI IGMP. Integrated with IPv4 multicast routing, socket options, and netdevice address lifecycle.

Risks: RCU lifetime of socket/source lists, timer teardown during device/socket close, source-filter include/exclude accounting, short packet parsing, and exponential max-response decoding edge cases.

Test signals: IGMPv2/v3 receive, join/leave/SSM, source filter add/drop/query, device up/down/unmap/remap, short/truncated query/report packets, timer cancellation, and RCU/refcount stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/igmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ihex.h -->
# `sources/distributed-fs/ceph-client/include/linux/ihex.h`

Purpose: compact binary Intel HEX firmware record format and helpers for safe iteration and firmware request validation.

Important APIs/types/functions: packed `struct ihex_binrec`, `ihex_binrec_size`, `__ihex_next_binrec`, `ihex_next_binrec`, `ihex_validate_fw`, and `request_ihex_firmware`.

Control flow and state: firmware is treated as a sequence of 4-byte-aligned binary records ending in a zero-length record. Validation walks records and only succeeds when the terminator is exactly at the computed end location. Request helper loads firmware, validates it, logs/release on invalid input, and returns a retained firmware pointer on success.

Dependencies/integration: depends on firmware loader and device logging. Used by drivers that want pre-converted IHEX firmware without parsing text in kernel.

Risks: validation assumes `fw->size >= sizeof(*end)`; malformed lengths can skip past data until loop fails; callers must release firmware after success; addresses/lengths are big-endian; alignment is part of the format.

Test signals: valid multi-record firmware, missing terminator, truncated header/data, unaligned record size padding, zero-length-only image, request failure/release path, and endian conversion checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ihex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/accel/kxcjk_1013.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/accel/kxcjk_1013.h`

Purpose: platform-data contract for the KXCJK-1013 three-axis accelerometer IIO driver.

Important APIs/types/functions: `struct kxcjk_1013_platform_data` with interrupt polarity (`active_high_intr`) and an `iio_mount_matrix` orientation.

Control flow and state: no functions; state is board/platform configuration consumed during driver probe.

Dependencies/integration: depends on IIO core types. Used by board files or platform data paths in addition to firmware-node configuration.

Risks: wrong interrupt polarity prevents data-ready handling; incorrect mount matrix misreports axes; platform data can diverge from device-tree/ACPI paths.

Test signals: probe with platform data, interrupt polarity validation, orientation matrix sysfs output, and sample axis mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/accel/kxcjk_1013.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/adc-helpers.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/adc-helpers.h`

Purpose: helper API for ADC drivers that describe channels via firmware properties.

Important APIs/types/functions: `iio_adc_device_num_channels` counts named child nodes called `channel`; `devm_iio_adc_device_alloc_chaninfo_se` allocates channel specs from a template with single-ended channel semantics and a max channel ID.

Control flow and state: inline channel count delegates to property/fwnode child counting; allocation is devm-managed and persists until device release.

Dependencies/integration: depends on firmware property APIs and IIO channel specs. Used by ADC drivers parsing DT/ACPI child channels.

Risks: only children named exactly `channel` are counted; channel IDs must be bounded by `max_chan_id`; template fields must be safe to clone.

Test signals: firmware nodes with zero/one/multiple channel children, invalid channel IDs, devm cleanup on probe failure, and generated channel spec contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/adc-helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/adc/ad_sigma_delta.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/adc/ad_sigma_delta.h`

Purpose: common support interface for Analog Devices sigma-delta ADC drivers, covering register communication, channel/mode selection, calibration, triggered buffers, SPI offload, and sample post-processing.

Important APIs/types/functions: `enum ad_sigma_delta_mode`, `struct ad_sd_calib_data`, `struct ad_sigma_delta_info` callback table, `struct ad_sigma_delta` core state, inline callback wrappers, `ad_sd_set_comm`, register read/write, reset, single conversion, calibration helpers, init, devm buffer/trigger setup, and trigger validation.

Control flow and state: persistent `ad_sigma_delta` state stores SPI device, trigger, completion, IRQ lock/disabled flag, bus/chip-select state, communication byte, active slots/current slot, ready GPIO/IRQ, status-append state, slot mapping, SPI messages/transfers, DMA-aligned buffers, and optional SPI offload trigger. Inline wrappers call device-specific callbacks when present and otherwise no-op.

Dependencies/integration: depends on IIO core, SPI, triggers, completions, GPIO, and optional SPI offload. Individual ADC drivers fill `ad_sigma_delta_info` and call init/setup helpers.

Risks: IRQ enable/disable state is lock-protected and race-sensitive; DMA buffer alignment is required; optional callbacks must preserve core state such as `status_appended`; SPI offload support requires channel scan-type compatibility; calibration and mode switching must not run concurrently with buffered capture.

Test signals: register read/write/reset, single conversions, triggered buffer capture, IRQ completion timeouts, calibration sequences, callback absent/present paths, SPI offload path, and DMA alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/adc/ad_sigma_delta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/adc/qcom-adc5-gen3-common.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/adc/qcom-adc5-gen3-common.h`

Purpose: shared Qualcomm PMIC ADC5 Gen3 register definitions, channel property structs, thermal-monitor auxiliary wrapper, and common helpers for main and auxiliary ADC/TM drivers.

Important APIs/types/functions: register offsets/status bits, virtual SID/channel packing (`ADC5_GEN3_V_CHAN`), PMIC channel IDs, `enum adc5_cal_method`, `enum adc5_time_select`, `struct adc5_sdam_data`, `struct adc5_device_data`, `struct adc5_channel_common_prop`, `struct tm5_aux_dev_wrapper`, SDAM read/write, handshake polling, digital parameter update, status clear, shared mutex lock/unlock, scaled reading/therm conversion, and TM notifier registration.

Control flow and state: ADC state spans regmap plus one or more SDAM bases/IRQs. Channel properties persist parsed channel configuration: channel, calibration, decimation, SID, label, prescale, settle time, averaging, and scale function. Helpers coordinate register access, conversion request/status clearing, and scaled conversion.

Dependencies/integration: depends on auxiliary bus, bitfield helpers, device/regmap, and `qcom-vadc-common.h`. Integrated with Qualcomm PMIC ADC and thermal monitor drivers.

Risks: wrong SDAM index/base corrupts register access; virtual channel packing must preserve SID/channel fields; handshake/status polling can hang without timeout discipline in implementation; calibration/scale enums must match hardware; shared mutex must protect cross-auxiliary access.

Test signals: SDAM read/write boundaries, conversion request/status clear, multiple SDAMs, SID/channel packing, calibration mode update, thermal code conversion, threshold IRQ/notifier delivery, and probe cleanup of auxiliary devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/adc/qcom-adc5-gen3-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/adc/qcom-vadc-common.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/adc/qcom-vadc-common.h`

Purpose: common Qualcomm VADC/ADC5 scaling constants, calibration structures, scale-function enum, data descriptors, and firmware-property conversion helpers.

Important APIs/types/functions: ADC code/range/decimation/settle/average constants, `enum vadc_calibration`, `struct vadc_linear_graph`, `enum vadc_scale_fn_type`, `struct adc5_data`, `qcom_vadc_scale`, `struct qcom_adc5_scale_type`, `qcom_adc5_hw_scale`, TM temperature/voltage conversion helpers, and DT parser helpers for prescale, settle time, average samples, and decimation.

Control flow and state: no persistent state in the header. Runtime code uses calibration graphs and ADC data descriptors to convert raw codes into microvolts or millidegrees and map firmware values into hardware selector indices.

Dependencies/integration: depends on math and types, IIO descriptors referenced indirectly, and Qualcomm ADC/TM drivers.

Risks: physical-unit conversions are sensitive to signed 32/64-bit arithmetic, prescale ratios, absolute vs ratiometric calibration, and lookup-table scale function selection; enum comments contain duplicated PMIC therm wording, so callers must use exact enum names.

Test signals: known-code-to-voltage/temperature vectors for every scale function, DT parser invalid values, min/max ADC codes, prescale ratio mapping, PMIC5/PMIC7 thermistor paths, and overflow checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/adc/qcom-vadc-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/adc/stm32-dfsdm-adc.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/adc/stm32-dfsdm-adc.h`

Purpose: callback registration API for STM32 DFSDM ADC audio-buffer integration.

Important APIs/types/functions: `stm32_dfsdm_get_buff_cb` registers a buffer callback with private data; `stm32_dfsdm_release_buff_cb` releases it.

Control flow and state: callback state is managed by the STM32 DFSDM driver outside this header and persists against an `iio_dev` until released.

Dependencies/integration: depends on IIO core. Used by STM32 audio/ADC glue that consumes DFSDM samples through callback buffers.

Risks: callback lifetime and private data ownership must outlive streaming; callback context may be constrained by IIO buffer/IRQ rules; release must be balanced.

Test signals: register/release callback, streaming sample delivery, double register/release error paths, probe/remove ordering, and callback under buffer stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/adc/stm32-dfsdm-adc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/afe/rescale.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/afe/rescale.h`

Purpose: IIO analog front-end rescale helper interface for channels whose scale/offset are transformed by resistor dividers, amplifiers, or similar front-end circuitry.

Important APIs/types/functions: `struct rescale_cfg`, `struct rescale`, `rescale_process_scale`, and `rescale_process_offset`.

Control flow and state: `struct rescale` persists source channel, derived channel spec, optional ext-info, processed/raw flag, numerator/denominator gain, and offset. Processing functions transform source scale/offset outputs into rescaled values.

Dependencies/integration: depends on IIO core and IIO consumer channels. Used by AFE rescale drivers and variants selected by `rescale_cfg`.

Risks: rational numerator/denominator and offset arithmetic can overflow or lose precision; `chan_processed` changes interpretation of source data; ext-info allocation/lifetime must match device lifetime.

Test signals: scale/offset conversion vectors for divider/amplifier cases, negative offsets, large numerator/denominator, processed vs raw source channels, and IIO value type propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/afe/rescale.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/backend.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/backend.h`

Purpose: frontend/backend abstraction for IIO converter stacks, allowing frontend devices to configure data format, source, sampling, buffers, test patterns, interface timing, filters, debugfs, and backend capabilities.

Important APIs/types/functions: data type/source/sample-trigger/interface/filter enums, capability bits, `IIO_BACKEND_EX_INFO`, `struct iio_backend_data_fmt`, `struct iio_backend_ops`, `struct iio_backend_info`, wrapper APIs for channel enable/disable, backend enable/disable, data format/source, sampling frequency, test pattern, status, I/O delay, buffer request, filter, interface alignment, lanes, DDR, stream, transfer address, ext-info, raw read, channel spec extension, capability checks, priv lookup, devm get/register, and debugfs helpers.

Control flow and state: frontends obtain a backend by firmware/device lookup, check capabilities, then call wrappers that dispatch to backend ops. Persistent backend state and private data live in the implementation registered through `devm_iio_backend_register`.

Dependencies/integration: depends on IIO core, firmware nodes, device-managed resources, and optional debugfs. Common in split ADC/DAC designs where digital backend and analog frontend are separate devices.

Risks: capability bits must match implemented ops; optional ops need clear error returns; enable/disable and stream/DDRadjustment ordering is hardware-sensitive; ext-info private values are uintptr_t; debugfs exposure must not bypass locking.

Test signals: frontend probe with named/fwnode backend, missing op/capability errors, full enable/configure/stream/disable sequence, buffer request/free, channel spec extension, ext-info read/write, debugfs status/reg access, and devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/backend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/buffer-dma.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/buffer-dma.h`

Purpose: reusable IIO DMA buffer queue framework for block-based DMA capture/output, file I/O, and DMABUF attachment/enqueue handling.

Important APIs/types/functions: `enum iio_block_state`, `struct iio_dma_buffer_block`, `struct iio_dma_buffer_queue_fileio`, `struct iio_dma_buffer_queue`, `struct iio_dma_buffer_ops`, block done/list abort, enable/disable/read/write/usage/update, bytes-per-datum/length setters, init/exit/release, DMABUF attach/detach/enqueue, queue lock/unlock, and DMA device getter.

Control flow and state: queue state embeds `struct iio_buffer`, device, ops, mutex for configuration/file I/O, spinlock for list changes in atomic context, incoming list, active flag, DMABUF count, and file-I/O double-buffer state. Blocks move through queued, active, done, and dead states with kref-managed lifetime and optional fences/sg tables.

Dependencies/integration: depends on IIO buffer internals, DMA/DMABUF/fence/sg types, mutex/spinlock/list/kref/atomic. DMA-capable IIO drivers supply submit/abort callbacks.

Risks: block state transitions cross mutex/spinlock contexts; fileio and DMABUF modes must not race; cyclic transfers and fences require correct completion signaling; DMA addresses and sg tables must match device DMA constraints; abort must drain active lists.

Test signals: enable/disable while queued, read/write fileio, block completion ordering, abort paths, DMABUF attach/enqueue/detach with fences, cyclic mode, length/BPD changes, and lockdep under IRQ completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/buffer-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/buffer-dmaengine.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/buffer-dmaengine.h`

Purpose: convenience API for wiring IIO buffers to DMAengine channels.

Important APIs/types/functions: `iio_dmaengine_buffer_teardown`, `iio_dmaengine_buffer_setup_ext`, `iio_dmaengine_buffer_setup`, `devm_iio_dmaengine_buffer_setup_ext`, `devm_iio_dmaengine_buffer_setup_with_handle`, and `devm_iio_dmaengine_buffer_setup`.

Control flow and state: setup functions allocate/attach DMAengine-backed IIO buffers for input or output direction; devm variants bind teardown to device lifetime.

Dependencies/integration: depends on IIO buffer API, DMAengine channel handles, and device-managed resources.

Risks: wrong buffer direction breaks capture/output semantics; channel name/handle resolution failures must unwind; teardown must not race active DMA.

Test signals: named-channel setup, handle-based setup, IN and OUT directions, devm cleanup on probe failure/remove, and active stream teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/buffer-dmaengine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/buffer.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/buffer.h`

Purpose: public in-kernel IIO buffer API for pushing/popping scans, timestamp injection, scan-mask validation, and buffer attachment.

Important APIs/types/functions: `enum iio_buffer_direction`, `iio_push_to_buffers`, `iio_pop_from_buffer`, deprecated `iio_push_to_buffers_with_timestamp`, `iio_push_to_buffers_with_ts`, unaligned timestamp variant, `iio_validate_scan_mask_onehot`, and `iio_device_attach_buffer`.

Control flow and state: timestamp helpers check whether the IIO device scan includes a timestamp and write it to the final aligned slot before pushing. The safer `_with_ts` helper validates supplied storage length against `indio_dev->scan_bytes`.

Dependencies/integration: depends on IIO core, sysfs, device logging, and buffer implementations. Used by sensor drivers and triggered handlers.

Risks: undersized stack/sample buffers can corrupt memory if deprecated helper is used directly; timestamp offset assumes scan layout ending with `s64`; push/pop context requirements depend on buffer implementation.

Test signals: timestamp-enabled and disabled scans, undersized storage returning `-ENOSPC`, unaligned data path, one-hot scan mask validation, attached-buffer lifecycle, and triggered-buffer sample alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/buffer_impl.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/buffer_impl.h`

Purpose: internal IIO buffer implementation contract defining buffer access callbacks, core buffer state, update operations, refcounting, and DMABUF signaling when `CONFIG_IIO_BUFFER` is enabled.

Important APIs/types/functions: `INDIO_BUFFER_FLAG_FIXED_WATERMARK`, `struct iio_buffer_access_funcs`, `struct iio_buffer`, `iio_update_buffers`, `iio_buffer_init`, `iio_buffer_get`, `iio_buffer_put`, and `iio_buffer_signal_dmabuf_done`.

Control flow and state: `struct iio_buffer` persists length, flags, bytes-per-datum, direction, access ops, scan mask, demux list/bounce buffer, poll queue, watermark, sysfs attribute groups/lists, attached/current buffer list nodes, kref, and DMABUF list protected by mutex. `iio_update_buffers` tears down and rebuilds active buffering when inserting/removing buffers.

Dependencies/integration: depends on sysfs, kref, IIO public buffer API, UAPI buffer definitions, and optional DMABUF/DMA types. With buffers disabled, get/put stubs no-op.

Risks: implementation callbacks have strict context rules, especially `store_to`; enable/disable calls must balance; demux and scan masks must match channel layout; refcount release must free all resources; DMABUF queue locking must be respected.

Test signals: custom buffer implementation callback coverage, attach/update/detach active buffers, watermark behavior, poll/read/write, refcount release, DMABUF attach/enqueue/done, and builds with `CONFIG_IIO_BUFFER=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/buffer_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/common/cros_ec_sensors_core.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/common/cros_ec_sensors_core.h`

Purpose: shared ChromeOS EC sensor-hub IIO core state and helper APIs for motion sensors exposed through EC host commands or LPC.

Important APIs/types/functions: axis enum, sample size constants, `cros_ec_sensors_capture_t`, `struct cros_ec_sensors_core_state`, read functions for LPC/command paths, core init/register, trigger capture, push data, host command sender, read/read_avail/write helpers, PM ops, and ext-info arrays.

Control flow and state: persistent state owns EC pointer, command mutex, command message/param/response buffers, motion sensor type, range/calibration/sign state, aligned sample buffer, selected read function, FIFO size, and frequency table. Read/write paths send EC host commands under lock; triggered capture pushes calibrated samples and timestamp.

Dependencies/integration: depends on IIO, IRQ return types, ChromeOS EC command/proto/sensorhub platform data, and platform devices.

Risks: EC command serialization via `cmd_lock` is mandatory; range changes must be re-applied on resume; sample buffer has fixed sizing and timestamp alignment assumptions; FIFO frequency tables must match EC firmware.

Test signals: LPC and command read paths, triggered capture/push data, range/calibration read/write, available frequency reporting, suspend/resume PM ops, FIFO event handling, and EC command failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/common/cros_ec_sensors_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/common/inv_sensors_timestamp.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/common/inv_sensors_timestamp.h`

Purpose: timestamp estimation state machine for Invensense sensors, compensating for chip clock period, jitter, interrupts, ODR changes, and FIFO batching.

Important APIs/types/functions: `struct inv_sensors_timestamp_chip`, interval and accumulator structs, `struct inv_sensors_timestamp`, init, ODR update, interrupt update, `inv_sensors_timestamp_pop`, ODR apply, and reset.

Control flow and state: persistent timestamp state tracks chip period bounds, interrupt interval, last sample timestamp, current/new multipliers, measured period, and an accumulator of chip-period measurements. Interrupt handler updates intervals based on sample count; `pop` advances by current period per sample; ODR apply handles pending ODR changes.

Dependencies/integration: uses fixed-width integer types and is consumed by Invensense IIO drivers with FIFO and interrupt streams.

Risks: timestamp drift if jitter bounds or initial period are wrong; ODR changes during FIFO batches require careful `fifo_no` handling; reset clears interval/timestamp but not chip config; 64-bit timestamp arithmetic must avoid underflow/overflow.

Test signals: regular interrupt sample cadence, jittered interrupts, FIFO batches, ODR changes mid-stream, reset behavior, and long-duration drift checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/common/inv_sensors_timestamp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/common/ssp_sensors.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/common/ssp_sensors.h`

Purpose: Samsung Sensor Platform common IIO definitions for sensor type IDs, sample sizes, per-sensor data callbacks, and enable/delay control.

Important APIs/types/functions: sample-size constants, `enum ssp_sensor_type`, `struct ssp_sensor_data`, `ssp_register_consumer`, `ssp_enable_sensor`, `ssp_disable_sensor`, `ssp_get_sensor_delay`, and `ssp_change_delay`.

Control flow and state: sensor consumer state stores a process-data callback, sensor type, and buffer pointer. Runtime SSP state lives in `struct ssp_data` outside the header; functions enable/disable sensors and configure polling/report delay.

Dependencies/integration: depends on IIO core and SSP hub driver internals.

Risks: fixed sample sizes must match firmware protocol; callback timestamp context must be safe; delay changes must synchronize with enabled sensors; enum values are protocol identifiers.

Test signals: register each sensor consumer type, enable/disable, delay read/change, sample buffer length validation, and callback data parsing for accelerometer/gyro/HRM variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/common/ssp_sensors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/common/st_sensors.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/common/st_sensors.h`

Purpose: common STMicroelectronics IIO sensor support for accelerometer, gyroscope, magnetometer, and pressure drivers, including channel macros, register setting descriptors, runtime state, trigger/buffer helpers, power/ODR/fullscale controls, and probe helpers.

Important APIs/types/functions: device-name constants, buffer/channel macros, sampling/scale sysfs attribute macros, ODR/power/axis/fullscale/SIM/BDU/DAS/DRDY descriptors, `struct st_sensor_settings`, `struct st_sensor_data`, optional trigger handler/allocation/validation, sensor init, enable, axis enable, power, debugfs register access, ODR, data-ready IRQ, fullscale, raw read, settings lookup, ID verification, sysfs avail emitters, device-name probe, and common probe functions per sensor class.

Control flow and state: persistent `st_sensor_data` owns trigger, mount matrix, selected settings, current fullscale, regmap, enable state, ODR, data channel count, interrupt pin/open-drain/IRQ mode flags, hardware timestamp, ODR mutex, and aligned buffer data. Common helpers program registers through regmap and coordinate trigger/buffer operation.

Dependencies/integration: depends on I2C/SPI, IRQ, IIO core/trigger, bitops, regulator, regmap, and platform data. Bus-specific headers call into this core after configuring transport.

Risks: per-chip settings tables must match register maps and WAI IDs; ODR/fullscale changes need locking; data-ready IRQ polarity/open-drain and pin selection must match hardware; buffer data alignment and boot-time discarded samples are easy to mishandle.

Test signals: common probe for each sensor class, WAI verification, ODR/fullscale sysfs read/write, trigger allocation/validation, data-ready IRQ enable/disable, buffered capture with timestamp, suspend/power regulator behavior, and I2C/SPI transport parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/common/st_sensors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/common/st_sensors_i2c.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/common/st_sensors_i2c.h`

Purpose: I2C transport configuration entry point for ST common IIO sensor drivers.

Important APIs/types/functions: `st_sensors_i2c_configure(struct iio_dev *, struct i2c_client *)`.

Control flow and state: implementation configures the `iio_dev` transport/regmap and device identity for an I2C-backed ST sensor.

Dependencies/integration: depends on I2C and `st_sensors.h`; used by ST accelerometer/gyro/magnetometer/pressure I2C drivers before common probe logic.

Risks: I2C regmap address width, multi-read behavior, and client device data must align with common settings; probe unwind must handle partial configuration.

Test signals: I2C probe/configure for supported chips, register read/write through common debugfs path, multi-byte sample reads, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/common/st_sensors_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/common/st_sensors_spi.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/common/st_sensors_spi.h`

Purpose: SPI transport configuration entry point for ST common IIO sensor drivers.

Important APIs/types/functions: `st_sensors_spi_configure(struct iio_dev *, struct spi_device *)`.

Control flow and state: implementation configures SPI-specific regmap/read flags and binds transport state to the shared ST sensor core.

Dependencies/integration: depends on SPI and `st_sensors.h`; used by ST sensor SPI drivers.

Risks: SPI read/write and multi-read bits vary by chip; mode/word size must match hardware; bus setup must be complete before common probe accesses registers.

Test signals: SPI probe/configure, WAI register read, buffered multi-byte sample reads, debugfs reg access, and compare behavior against I2C variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/common/st_sensors_spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/configfs.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/configfs.h`

Purpose: exposes the IIO configfs subsystem symbol to IIO components that create or manage configfs objects.

Important APIs/types/functions: `extern struct configfs_subsystem iio_configfs_subsys`.

Control flow and state: no functions; state is owned by the configfs subsystem implementation.

Dependencies/integration: depends on configfs declarations being available to including users. Used by IIO configfs registration paths.

Risks: initialization order and symbol availability; consumers must not manipulate subsystem internals without configfs locking rules.

Test signals: IIO configfs mount/listing, subsystem registration/unregistration, and build/link with configfs-enabled IIO features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/configfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/consumer.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/consumer.h`

Purpose: in-kernel IIO consumer interface for acquiring channels, callback buffers, reading/writing raw/processed/channel attributes, converting raw values, and querying extended info.

Important APIs/types/functions: `struct iio_channel`, channel get/release/devm/get-all/fwnode variants, callback buffer get/start/stop/watermark/release and underlying channel/device accessors, raw/average/processed reads, processed scaling, attribute read/write, raw write, min/max/available reads, channel type/offset/scale, `iio_multiply_value`, `iio_convert_raw_to_processed`, ext-info count/read/write, and label read.

Control flow and state: consumers acquire channel descriptors from mapping or firmware lookup, use direct read/write APIs or callback buffers, and release explicitly or through devm. Callback buffers register a callback that must be safe in any context and can stream channels from one provider device.

Dependencies/integration: depends on IIO types and provider channel specs, device/fwnode mapping, and IIO buffer infrastructure. Used by power, thermal, hwmon, regulator, and sensor consumers.

Risks: channel acquisition can return `ERR_PTR`; callback buffers cannot mux multiple provider devices; raw-to-processed conversions depend on offset/scale value types and can lose precision; callback context may not sleep; devm and manual release must not mix incorrectly.

Test signals: mapping-based and fwnode channel lookup, get-all sentinel termination, devm cleanup, raw/processed/scale/offset reads, write paths, available range/list returns, callback buffer streaming/watermark, ext-info and label reads, and absent provider errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/consumer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/dac/ad5421.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/dac/ad5421.h`

Purpose: platform data for AD5421 current-output DAC configuration.

Important APIs/types/functions: `enum ad5421_current_range` and `struct ad5421_platform_data` with `external_vref` and selected current range.

Control flow and state: no functions; platform configuration is consumed at probe to set reference source and current output range.

Dependencies/integration: used by the AD5421 IIO DAC driver and board/platform data paths.

Risks: wrong current range can drive incorrect loop current; external reference flag must match hardware wiring.

Test signals: probe with each range, external/internal reference selection, scale reporting, and output current calibration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/dac/ad5421.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/dac/ad5504.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/dac/ad5504.h`

Purpose: platform data for the AD5504 SPI DAC reference voltage.

Important APIs/types/functions: `struct ad5504_platform_data` with `vref_mv`.

Control flow and state: no functions; probe-time configuration only.

Dependencies/integration: used by the AD5504 IIO DAC driver.

Risks: wrong reference voltage produces incorrect scale and output voltage.

Test signals: scale calculation from `vref_mv`, SPI write/readback paths where supported, and probe with missing/default platform data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/dac/ad5504.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/dac/ad5791.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/dac/ad5791.h`

Purpose: platform data for AD5791 SPI DAC supply reference and output amplifier mode.

Important APIs/types/functions: `struct ad5791_platform_data` with positive/negative reference millivolts and `use_rbuf_gain2`.

Control flow and state: no functions; probe-time configuration informs scale and amplifier setup.

Dependencies/integration: used by the AD5791 IIO DAC driver.

Risks: misspelled comment aside, wrong reference values or gain-of-two setting misreports/sets output voltage; signed bipolar range handling depends on both references.

Test signals: positive/negative reference scale vectors, gain2 mode, output code-to-voltage conversion, and SPI command tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/dac/ad5791.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/dac/max517.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/dac/max517.h`

Purpose: platform data for MAX517-family DAC reference voltages.

Important APIs/types/functions: `struct max517_platform_data` with an eight-entry `vref_mv` array.

Control flow and state: no functions; per-channel reference values configure scale at probe/runtime.

Dependencies/integration: used by the MAX517 IIO DAC driver.

Risks: array size assumes up to eight DAC channels; unset entries can lead to zero or default scale depending on driver policy.

Test signals: per-channel scale from `vref_mv`, devices with fewer channels, default/missing platform data, and I2C output writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/dac/max517.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/dac/mcp4725.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/dac/mcp4725.h`

Purpose: platform data for MCP4725/MCP4726 DAC reference selection and buffering.

Important APIs/types/functions: `struct mcp4725_platform_data` with `use_vref` and `vref_buffered`.

Control flow and state: no functions; settings are consumed during probe to configure reference source and optional Vref buffering where hardware supports it.

Dependencies/integration: used by the MCP4725 IIO DAC driver and complements devicetree binding semantics.

Risks: Vref options apply only to MCP4726-class hardware; missing regulator when `use_vref` is set should fail cleanly; buffered reference changes output impedance/accuracy.

Test signals: MCP4725 vs MCP4726 probe, external reference regulator handling, buffered/unbuffered setting, scale reporting, and EEPROM/output write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/dac/mcp4725.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/driver.h -->
# `sources/distributed-fs/ceph-client/include/linux/iio/driver.h`

Purpose: provider-side in-kernel IIO mapping registration API that connects IIO channels to named in-kernel consumers.

Important APIs/types/functions: `iio_map_array_register`, `iio_map_array_unregister`, and `devm_iio_map_array_register`.

Control flow and state: providers register arrays of `iio_map` entries against an `iio_dev`; consumers later resolve channels through the mapping. Devm variant registers an automatic unregister callback tied to the provider device lifetime.

Dependencies/integration: depends on IIO provider devices, `struct iio_map`, and device-managed resource cleanup.

Risks: map arrays must remain valid for the registration lifetime; unregister must match successful register; duplicate or stale consumer names break channel lookup; devm cleanup order matters during provider removal.

Test signals: provider register/unregister, consumer `iio_channel_get` resolution, duplicate/missing map behavior, devm cleanup on probe failure/remove, and use-after-free checks for map storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/driver.h -->
