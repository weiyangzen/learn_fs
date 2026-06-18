# subset-b-006171 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_vlan.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_vlan.c

## Purpose
Implements the Linux bridge VLAN database, including bridge-wide and per-port VLAN membership, PVID/untagged flags, VLAN protocol/default-PVID controls, ingress and egress filtering, VLAN stats, bridge-binding VLAN device carrier updates, rtnetlink VLAN add/delete/dump handlers, switchdev/8021q device-filter programming, and integration with multicast, MST, tunnel, FDB, and forwarding path state.

## Important APIs, Types, And Functions
The main state is `struct net_bridge_vlan_group` with an rhashtable and ordered VLAN list, and `struct net_bridge_vlan` entries that can be bridge master VLANs or port VLANs. Key APIs include `br_vlan_add`, `br_vlan_delete`, `br_vlan_flush`, `nbp_vlan_add`, `nbp_vlan_delete`, `nbp_vlan_flush`, `br_allowed_ingress`, `br_allowed_egress`, `br_should_learn`, `br_handle_vlan`, `br_vlan_filter_toggle`, `br_vlan_set_proto`, `br_vlan_set_default_pvid`, `br_vlan_get_pvid*`, `br_vlan_get_info*`, `br_vlan_notify`, `br_vlan_rtnl_init`, and `br_vlan_rtnl_uninit`.

## Control Flow
VLAN add paths allocate or find a VLAN entry, program hardware through switchdev or software 8021q filters, ensure a master VLAN exists for port VLANs, attach stats and multicast contexts, add local FDB entries, publish the entry through rhashtable/list insertion, commit PVID/untagged flags, and notify consumers. Delete/flush paths remove PVID state, hardware filters, FDB entries, tunnel mappings, multicast contexts, list/hash membership, and references before RCU freeing. Ingress validates tags, assigns PVID for untagged or priority-tagged frames, updates VLAN stats, checks per-VLAN STP/MST state, and drops invalid frames. Egress validates membership/state, optionally strips tags, updates stats, and applies VLAN tunnel metadata. Rtnetlink handlers parse `RTM_NEWVLAN`, `RTM_DELVLAN`, and `RTM_GETVLAN`, support ranges, dump compressed ranges, and dispatch option processing.

## State And Persistence Behavior
All state is in kernel memory under RTNL/RCU: VLAN groups, per-VLAN refcounts, PVID state with memory barriers, per-CPU stats, bridge options, multicast contexts, local FDB rows, switchdev attributes, and upper VLAN-device carrier state. There is no disk persistence; durable configuration is expected from userspace replay. RCU freeing protects readers, and RTNL protects mutation.

## Dependencies And Integration Points
Depends on `br_private.h`, `br_private_tunnel.h`, rhashtable, rtnetlink, switchdev, 8021q `vlan_vid_add/del`, bridge FDB, multicast snooping, MST state, netdevice notifiers, and netlink VLAN DB attributes. It exports bridge VLAN query helpers for other modules such as nft bridge meta, and it calls `br_vlan_process_options` / `br_vlan_rtm_process_global_options` from `br_vlan_options.c` plus tunnel helpers from `br_vlan_tunnel.c`.

## Risks And Test Signals
Risk concentrates in rollback after partial switchdev/filter/FDB failures, master VLAN refcount handling, PVID memory ordering, range notification correctness, default PVID changes across many ports, VLAN protocol migration, RCU lifetime, stats sharing versus per-port stats, and tag handling with forwarding offload or QinQ. Good signals are rtnetlink VLAN add/delete/range dumps, bridge selftests for VLAN filtering and default PVID, switchdev fallback tests, multicast/MST option tests, carrier propagation for bridge-bound VLAN devices, and packet tests for untagged, priority-tagged, protocol-mismatched, ingress-drop, and egress-untag paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_vlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_vlan_options.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_vlan_options.c

## Purpose
Handles user-visible bridge VLAN options for per-entry and global VLAN database netlink operations: VLAN STP state, tunnel mapping, neighbor suppression, per-port multicast limits/router state, global multicast snooping parameters, and MST instance assignment.

## Important APIs, Types, And Functions
Important functions include `br_vlan_opts_eq_range`, `br_vlan_opts_fill`, `br_vlan_opts_nl_size`, `br_vlan_process_options`, `br_vlan_global_opts_can_enter_range`, `br_vlan_global_opts_fill`, and `br_vlan_rtm_process_global_options`. Internal helpers include `br_vlan_modify_state`, `br_vlan_modify_tunnel`, `br_vlan_process_one_opts`, `br_vlan_global_opts_notify`, and `br_vlan_process_global_one_opts`.

## Control Flow
Per-VLAN option processing validates the requested VLAN or range exists, then walks each VLAN and applies requested netlink attributes. State changes are rejected for kernel STP and MST-enabled bridges, tunnel changes require a port VLAN with `BR_VLAN_TUNNEL`, multicast max-groups require active per-port VLAN snooping context, and neighbor suppression is port-only. Changed VLANs are coalesced into notification ranges when flags/options allow. Global processing is bridge-device-only and `RTM_NEWVLAN`-only; it validates ID/range attributes, applies multicast and MST attributes, and emits global option notifications in compatible ranges.

## State And Persistence Behavior
The file mutates existing in-memory `net_bridge_vlan` fields: `state`, PVID state cache, `priv_flags`, tunnel mappings through `br_vlan_tunnel_info`, multicast context fields and timers, multicast router state, and `msti`. It emits rtnetlink notifications but does not persist data outside kernel memory.

## Dependencies And Integration Points
Integrates with the VLAN DB netlink path in `br_vlan.c`, tunnel helpers in `br_vlan_tunnel.c`, multicast bridge code under `CONFIG_BRIDGE_IGMP_SNOOPING`, MST helpers, rtnetlink nested attribute policy validation, and clock/jiffies conversion for multicast timers.

## Risks And Test Signals
Risks include partial range updates before an error, incorrect range coalescing after option changes, invalid direct state mutation while STP/MST owns state, tunnel ID arithmetic across VLAN ranges, and global multicast timer unit conversion. Tests should exercise netlink set/dump round trips for single VLANs and ranges, rejected non-port tunnel/neigh options, missing attributes, MST assignments, multicast snooping toggles, and notification content for option-only changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_vlan_options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_vlan_tunnel.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_vlan_tunnel.c

## Purpose
Maintains per-port VLAN-to-tunnel metadata mappings for bridge VLAN tunnel mode, allowing ingress tunnel IDs to map to VLAN tags and egress VLAN tags to attach tunnel destination metadata.

## Important APIs, Types, And Functions
Key APIs are `nbp_vlan_tunnel_info_add`, `nbp_vlan_tunnel_info_delete`, `vlan_tunnel_info_del`, `nbp_vlan_tunnel_info_flush`, `vlan_tunnel_init`, `vlan_tunnel_deinit`, `br_handle_ingress_vlan_tunnel`, and `br_handle_egress_vlan_tunnel`. The file uses a tunnel-ID rhashtable keyed by `net_bridge_vlan.tinfo.tunnel_id`.

## Control Flow
Adding a mapping finds the port VLAN, builds `metadata_dst` with a tunnel key, marks it as TX bridge tunnel metadata, stores it under RCU, records the tunnel ID, and inserts the VLAN into the tunnel hash. Deletion removes the hash node and releases destination metadata. Ingress checks for tunnel info on untagged packets, looks up a VLAN by tunnel ID, drops old dst metadata, and pushes an accelerated bridge VLAN tag. Egress clears the hardware VLAN tag, then either constructs backup-nexthop metadata or reuses the VLAN's stored metadata with a safe dst hold.

## State And Persistence Behavior
Mappings live in the VLAN group's in-memory rhashtable and each VLAN's `tinfo` pointer/id fields. Updates require RTNL and use RCU pointer assignment/dereference for packet paths. Metadata references are held/released through dst lifetime rules; no disk persistence exists.

## Dependencies And Integration Points
Depends on `br_private_tunnel.h`, `net/dst_metadata.h`, `net/switchdev.h`, IP tunnel metadata helpers, VLAN tag helpers, bridge input control block fields, and the VLAN add/delete/option paths that call tunnel add/delete/flush.

## Risks And Test Signals
Risks include duplicate tunnel IDs, dst metadata lifetime races, failure rollback after hash insertion errors, handling QinQ by clearing only the accelerated outer tag, and preserving backup nexthop IDs. Useful tests cover netlink tunnel add/delete/range behavior, ingress untagged VXLAN-to-VLAN mapping, egress VLAN-to-tunnel metadata, duplicate mapping rejection, flush on VLAN removal, and QinQ payload preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_vlan_tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/Kconfig -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/Kconfig

## Purpose
Defines build-time configuration for bridge netfilter support: nftables bridge family expressions, native bridge connection tracking, legacy ebtables core, legacy ebtables tables, matches, targets, and logging watchers.

## Important APIs, Types, And Functions
This Kconfig file declares `NF_TABLES_BRIDGE`, `NFT_BRIDGE_META`, `NFT_BRIDGE_REJECT`, `NF_CONNTRACK_BRIDGE`, `BRIDGE_NF_EBTABLES_LEGACY`, `BRIDGE_NF_EBTABLES`, table symbols such as `BRIDGE_EBT_BROUTE`, match symbols such as `BRIDGE_EBT_IP6`, and target/watcher symbols such as `BRIDGE_EBT_DNAT`, `BRIDGE_EBT_LOG`, and `BRIDGE_EBT_NFLOG`.

## Control Flow
Menu visibility is dependency-driven. nft bridge options appear only under `NF_TABLES_BRIDGE`; ebtables tables/matches/targets/watchers appear under `BRIDGE_NF_EBTABLES`; legacy table modules depend on `BRIDGE_NF_EBTABLES_LEGACY`; IPv6 and reject options add their protocol-specific dependencies.

## State And Persistence Behavior
The file has no runtime state. Its selected tristate values persist only through kernel configuration artifacts such as `.config` and determine whether modules are built-in, modules, or absent.

## Dependencies And Integration Points
Coordinates with `net/bridge/netfilter/Makefile`, bridge core, `NETFILTER`, `NETFILTER_XTABLES`, `NETFILTER_XTABLES_LEGACY`, `NF_TABLES`, `NF_CONNTRACK`, `NFT_REJECT`, `NF_REJECT_IPV4`, `NF_REJECT_IPV6`, `IPV6`, and `INET`.

## Risks And Test Signals
Risks are mismatched dependencies that build modules without required protocol helpers, unintentional default enablement, or hiding legacy support needed by old userspace. Signals are `oldconfig`/`allyesconfig`/`allmodconfig` coverage, module link success for each selected symbol, and runtime smoke tests loading nft bridge, conntrack bridge, and ebtables legacy modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/Makefile -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/Makefile

## Purpose
Maps bridge netfilter Kconfig symbols to the object files that implement nftables bridge extensions, bridge conntrack, legacy ebtables core, tables, matches, targets, and watchers.

## Important APIs, Types, And Functions
Important object mappings include `nft_meta_bridge.o`, `nft_reject_bridge.o`, `nf_conntrack_bridge.o`, `ebtables.o`, `ebtable_broute.o`, `ebtable_filter.o`, `ebtable_nat.o`, and the `ebt_*` match/target/watcher modules.

## Control Flow
Kbuild includes each object when the matching `CONFIG_*` symbol is `y` or `m`. The ebtables legacy core is gated by `CONFIG_BRIDGE_NF_EBTABLES_LEGACY`, while individual extensions are gated separately.

## State And Persistence Behavior
No runtime state exists. The file contributes build graph state by selecting compiled objects and module names.

## Dependencies And Integration Points
Integrates directly with `Kconfig` symbols in the same directory and with source files in `net/bridge/netfilter`.

## Risks And Test Signals
Risks are missing object mappings for enabled symbols or stale mappings for removed files. Build tests with representative config combinations and module load tests for each object provide the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_802_3.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_802_3.c

## Purpose
Implements the legacy ebtables `802_3` match for LLC/SNAP 802.3 frame fields, allowing rules to match DSAP/SSAP SAP values and SNAP type.

## Important APIs, Types, And Functions
The module registers `xt_match ebt_802_3_mt_reg`. Core functions are `ebt_802_3_mt`, `ebt_802_3_mt_check`, and the helper `ebt_802_3_hdr`.

## Control Flow
At match time the code reads the MAC-header LLC structure, selects the UI or non-UI type field, applies SAP and type comparisons with ebtables inversion flags, and returns true only if requested conditions pass. Checkentry validates bitmask and inversion mask bounds before rules are accepted.

## State And Persistence Behavior
No per-rule mutable state is kept beyond userspace-provided `struct ebt_802_3_info`. Runtime state is limited to module registration with xtables.

## Dependencies And Integration Points
Depends on `x_tables`, bridge ebtables headers, skbuff MAC header access, and UAPI `ebt_802_3.h`. It is loaded by ebtables/xtables rule validation when the `802_3` match is referenced.

## Risks And Test Signals
Risks include assuming an 802.3/LLC header is present and subtle UI versus non-UI type interpretation. Tests should verify SAP, type, inversion, malformed/truncated frames, and rejection of invalid masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_802_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_among.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_among.c

## Purpose
Implements the legacy ebtables `among` match, which checks source and/or destination MAC addresses against compact wormhash tables and can optionally bind MAC matches to IPv4 addresses from IP or ARP payloads.

## Important APIs, Types, And Functions
Important routines are `ebt_among_mt`, `ebt_among_mt_check`, `ebt_mac_wormhash_contains`, `ebt_mac_wormhash_check_integrity`, `get_ip_src`, `get_ip_dst`, `poolsize_invalid`, `wormhash_offset_invalid`, and `wormhash_sizes_valid`. The module registers an `xt_match` named `among`, with variable runtime match size.

## Control Flow
Validation checks that embedded source/destination wormhash offsets are aligned, ordered, within the match blob, correctly sized after `EBT_ALIGN`, non-overflowing, and internally monotonic. Runtime matching extracts source/destination MACs and optional IP addresses from IPv4 or ARP payloads, then performs bucketed tuple searches. Positive and negated source/destination membership tests are applied independently.

## State And Persistence Behavior
All match data is immutable per-rule data supplied by userspace and stored inside the ebtables rule blob. No counters or persistent state are maintained by this module.

## Dependencies And Integration Points
Depends on ebtables among UAPI layout, `x_tables`, Ethernet/IP/ARP header helpers, and the ebtables compat path, which has special handling for `matchsize == -1` because this match embeds variable-sized data.

## Risks And Test Signals
Risks are malformed variable-length blobs, offset arithmetic overflows, ARP/IP header truncation, and compat-size translation. Tests should include empty, source-only, destination-only, both-hash, MAC-only, MAC/IP, negated, malformed offset, bad poolsize, non-monotonic table, fragmented/truncated IP/ARP, and 32-bit compat rule loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_among.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_arp.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_arp.c

## Purpose
Implements the legacy ebtables `arp` match for ARP/RARP header fields, IPv4 sender/target protocol addresses, Ethernet sender/target hardware addresses, and gratuitous ARP detection.

## Important APIs, Types, And Functions
The module centers on `ebt_arp_mt`, `ebt_arp_mt_check`, and `xt_match ebt_arp_mt_reg`, using `struct ebt_arp_info` from UAPI.

## Control Flow
The matcher safely reads the ARP header and requested payload fields with `skb_header_pointer`, validates protocol/hardware lengths before address matching, applies masks to IP and MAC fields, and honors ebtables inversion flags. Checkentry requires ARP or RARP ethproto without inverted protocol match and rejects unknown bitmask or inversion bits.

## State And Persistence Behavior
No mutable state is stored. Per-rule match criteria live in ebtables rule memory.

## Dependencies And Integration Points
Depends on ARP/Ethernet headers, ebtables core validation, masked Ethernet comparison helpers, and xtables registration. It is typically used with rules whose base ethproto is ARP/RARP.

## Risks And Test Signals
Risks include offset mistakes for variable ARP hardware/protocol lengths and matching incomplete packets. Useful tests cover each field, masks, inversion, gratuitous ARP, RARP, invalid ethproto rejection, and truncated ARP frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_arp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_arpreply.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_arpreply.c

## Purpose
Implements the legacy ebtables `arpreply` target, which sends synthetic ARP replies from bridge prerouting nat rules and returns a configured ebtables verdict.

## Important APIs, Types, And Functions
Core functions are `ebt_arpreply_tg`, `ebt_arpreply_tg_check`, and `xt_target ebt_arpreply_tg_reg`. It uses `arp_send` and `struct ebt_arpreply_info`.

## Control Flow
Runtime target evaluation validates the skb contains an Ethernet/IPv4 ARP request, extracts sender MAC, sender IP, and target IP, sends an ARP reply on the incoming device using the configured MAC address, and returns the configured target verdict. Checkentry restricts use to ARP ethproto, the nat table's bridge prerouting hook, non-invalid verdicts, and forbids `RETURN` from base chains.

## State And Persistence Behavior
No durable state exists. The target emits packets as side effects and uses immutable rule parameters.

## Dependencies And Integration Points
Depends on ARP helpers, bridge netfilter hook context, ebtables target validation, xtables registration, and the legacy nat table.

## Risks And Test Signals
Risks include replying to malformed ARP, using the wrong device/IP tuple, and rule verdict interactions after a reply is emitted. Tests should cover valid ARP request reply generation, non-request continuation, malformed header drop, invalid target rejection, and base-chain return rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_arpreply.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_dnat.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_dnat.c

## Purpose
Implements the legacy ebtables `dnat` target for destination MAC address rewriting in bridge nat and broute hooks.

## Important APIs, Types, And Functions
Key functions are `ebt_dnat_tg`, `ebt_dnat_tg_check`, and `xt_target ebt_dnat_tg_reg`, using `struct ebt_nat_info`.

## Control Flow
The target ensures the Ethernet header is writable, copies the configured MAC to `h_dest`, updates `skb->pkt_type` for broadcast, multicast, host, or otherhost semantics depending on hook and destination device, and returns the configured verdict. Checkentry validates allowed table/hook combinations (`nat` prerouting/local-out or `broute` brouting), target validity, and base-chain `RETURN` rules.

## State And Persistence Behavior
State mutation is limited to the current skb Ethernet destination and packet type. Rule data is immutable and there is no persistence.

## Dependencies And Integration Points
Depends on bridge private helpers for bridge-port lookup, netfilter bridge hook numbers, ebtables nat UAPI, and xtables target registration.

## Risks And Test Signals
Risks include writable-header failures, packet-type misclassification, and incorrect table/hook admission. Tests should cover unicast to bridge MAC, otherhost, multicast, broadcast, broute, local-out, invalid hooks, and malformed/cloned skb writability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_dnat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_ip.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_ip.c

## Purpose
Implements the legacy ebtables `ip` match for IPv4 TOS, source/destination addresses, L4 protocol, TCP/UDP-like port ranges, ICMP type/code ranges, and IGMP type ranges.

## Important APIs, Types, And Functions
The module provides `ebt_ip_mt`, `ebt_ip_mt_check`, `xt_match ebt_ip_mt_reg`, and a local `union pkthdr` for minimal L4 field reads.

## Control Flow
At runtime it safely reads the IPv4 header, checks requested L3 fields, then if protocol-dependent fields are requested it rejects non-initial fragments and reads a small L4 header at `ihl * 4` to evaluate port or ICMP/IGMP ranges. Checkentry requires ethproto IPv4, validates masks, enforces valid protocol dependencies for ports/ICMP/IGMP, and checks range ordering.

## State And Persistence Behavior
No mutable state exists. Match criteria are stored in each rule's `struct ebt_ip_info`.

## Dependencies And Integration Points
Depends on IP protocol constants, `skb_header_pointer`, ebtables rule metadata, and xtables match registration. It complements the bridge ethproto basic match in `ebtables.c`.

## Risks And Test Signals
Risks include fragmented packet behavior, short IHL/payload reads, protocol/range validation, and inversion semantics. Tests should cover each field, all supported transport protocols, non-first fragments, invalid protocol dependencies, reversed ranges, and truncated IPv4/L4 headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_ip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_ip6.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_ip6.c

## Purpose
Implements the legacy ebtables `ip6` match for IPv6 traffic class, masked source/destination addresses, next header protocol, TCP/UDP-like port ranges, and ICMPv6 type/code ranges.

## Important APIs, Types, And Functions
Important routines are `ebt_ip6_mt`, `ebt_ip6_mt_check`, and `xt_match ebt_ip6_mt_reg`, using `struct ebt_ip6_info` and `ipv6_skip_exthdr`.

## Control Flow
The match reads the IPv6 header, evaluates traffic class and masked addresses, then follows extension headers to locate the effective next header and L4 offset. If L4 fields are requested, it reads a compact port/ICMP header and applies range and inversion checks. Checkentry enforces IPv6 ethproto, mask bounds, transport-protocol requirements, ICMPv6 requirements, and range ordering.

## State And Persistence Behavior
The module keeps no runtime mutable state beyond registration. Per-rule criteria are immutable.

## Dependencies And Integration Points
Depends on IPv6 header helpers, dsfield helpers, ebtables UAPI, and xtables. It is built only when bridge ebtables and IPv6 support are enabled.

## Risks And Test Signals
Risks include extension-header skip failures, fragmented IPv6 behavior, truncated L4 reads, and invalid protocol/range combinations. Tests should cover extension headers, ports, ICMPv6, masked addresses, traffic class, inversions, bad ranges, and invalid ethproto rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_ip6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_limit.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_limit.c

## Purpose
Implements the legacy ebtables `limit` match, a token-bucket rate limiter for controlling how often a rule can match.

## Important APIs, Types, And Functions
Important code includes `ebt_limit_mt`, `ebt_limit_mt_check`, `user2credits`, global `limit_lock`, and `xt_match ebt_limit_mt_reg`. It uses `struct ebt_limit_info` and compat sizing for 32-bit userspace.

## Control Flow
Rule validation converts userspace average and burst into internal credits, detects overflow, initializes `prev`, `credit`, `credit_cap`, and `cost`. Runtime matching locks globally, refills credits based on elapsed jiffies, caps them, consumes a cost if available, and returns match/no-match.

## State And Persistence Behavior
This match mutates per-rule rate-limit state embedded in the rule blob. The state is memory-only and resets when rules are loaded/replaced. The global spinlock serializes all limit matches.

## Dependencies And Integration Points
Depends on jiffies, spinlocks, ebtables UAPI, xtables registration, and compat layout support. It follows the classic iptables limit-match model.

## Risks And Test Signals
Risks include arithmetic overflow, global lock contention, HZ-dependent conversion, and per-rule state reset on table replacement. Tests should validate burst/average behavior, overflow rejection, compat load, replacement reset, and concurrent packet paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_limit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_log.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_log.c

## Purpose
Implements the legacy ebtables `log` watcher/target, preserving classic ebtables syslog formatting while optionally delegating to the netfilter logging backend.

## Important APIs, Types, And Functions
Key functions are `ebt_log_tg`, `ebt_log_tg_check`, `ebt_log_packet`, `print_ports`, and `xt_target ebt_log_tg_reg`. Local helper structs describe minimal TCP/UDP and ARP payload fields.

## Control Flow
Validation checks log bitmask and loglevel, and NUL-terminates the prefix. Runtime constructs `nf_loginfo`, then either calls `nf_log_packet` when `EBT_LOG_NFLOG` is requested or prints classic bridge log output under a spinlock. The classic path prints MAC fields and optionally decodes IPv4, IPv6, ARP/RARP, and transport ports using safe skb header reads.

## State And Persistence Behavior
No per-rule mutable state exists. Runtime side effects are logs to syslog/netfilter logging; non-init network namespaces are suppressed unless `sysctl_nf_log_all_netns` permits logging.

## Dependencies And Integration Points
Depends on `nf_log`, IPv4/IPv6/ARP helpers, bridge ebtables log UAPI, xtables, and optional `CONFIG_BRIDGE_EBT_IP6` for IPv6 decoding.

## Risks And Test Signals
Risks include log format regressions, namespace logging policy, incomplete header reads, rate/volume effects, and lock-held printing. Tests should verify prefix truncation, loglevel rejection, IP/IPv6/ARP decode, NFLOG delegation, namespace behavior, and malformed packet logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_mark.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_mark.c

## Purpose
Implements the legacy ebtables `mark` target for setting, ORing, ANDing, or XORing `skb->mark`, returning a verdict encoded in the same target field.

## Important APIs, Types, And Functions
Important functions are `ebt_mark_tg`, `ebt_mark_tg_check`, compat conversion helpers, and `xt_target ebt_mark_tg_reg`, using `struct ebt_mark_t_info`.

## Control Flow
At runtime the high action bits select set/or/and/xor against `skb->mark`, and the low verdict bits are returned as the ebtables verdict. Validation checks base-chain return rules, target validity, and allowed mark actions. Compat helpers translate `unsigned long` mark layout for 32-bit userspace.

## State And Persistence Behavior
The target mutates only the current skb mark. Rule parameters are immutable and there is no persistent storage.

## Dependencies And Integration Points
Depends on ebtables mark-target UAPI, xtables target registration, and ebtables verdict encoding. Its output can be consumed by `ebt_mark_m.c`, tc, routing, or later netfilter logic.

## Risks And Test Signals
Risks include mixed action/verdict bit handling, compat width conversion, and invalid target acceptance. Tests should cover all four actions, verdict preservation, base-chain return rejection, and 32-bit compat rule round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_mark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_mark_m.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_mark_m.c

## Purpose
Implements the legacy ebtables `mark_m` match for comparing `skb->mark` against a value/mask or checking whether any masked bits are set.

## Important APIs, Types, And Functions
Core items are `ebt_mark_mt`, `ebt_mark_mt_check`, compat conversion helpers, and `xt_match ebt_mark_mt_reg`, using `struct ebt_mark_m_info`.

## Control Flow
Runtime matching either tests any masked bit with `EBT_MARK_OR` or checks exact `(mark & mask) == mark`, then applies the invert flag. Checkentry rejects unknown mode bits, simultaneous OR/AND modes, and empty mode masks.

## State And Persistence Behavior
The match reads `skb->mark` only. Per-rule match data is immutable and no state is persisted.

## Dependencies And Integration Points
Depends on ebtables mark-match UAPI and xtables registration. It commonly consumes marks written by `ebt_mark.c` or other netfilter/classifier paths.

## Risks And Test Signals
Risks include confusing OR/AND semantics, invert handling, and compat width conversion for marks/masks. Tests should cover exact, OR, invert, invalid bitmasks, empty mode, simultaneous modes, and 32-bit compat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_mark_m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_nflog.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_nflog.c

## Purpose
Implements the legacy ebtables `nflog` watcher/target, sending bridge packets to the netfilter logging API with NFLOG/ULOG-style group, length, threshold, and prefix parameters.

## Important APIs, Types, And Functions
Important functions are `ebt_nflog_tg`, `ebt_nflog_tg_check`, and `xt_target ebt_nflog_tg_reg`, using `struct ebt_nflog_info`.

## Control Flow
Validation rejects unknown flags and NUL-terminates the prefix. Runtime fills `nf_loginfo` with ULOG parameters, calls `nf_log_packet` for `PF_BRIDGE`, and returns `EBT_CONTINUE` so logging is side-effect-only.

## State And Persistence Behavior
No mutable module state exists. Side effects are logging messages passed to configured netfilter log backends.

## Dependencies And Integration Points
Depends on `nf_log`, bridge ebtables NFLOG UAPI, and xtables target registration. Backend behavior depends on configured nfnetlink log or other logging providers.

## Risks And Test Signals
Risks include invalid flag acceptance, prefix termination, and backend availability. Tests should verify log emission to the right group, length/threshold handling, prefix truncation, and unknown flag rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_nflog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_pkttype.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_pkttype.c

## Purpose
Implements the legacy ebtables `pkttype` match for the skb packet type, such as host, broadcast, multicast, or otherhost.

## Important APIs, Types, And Functions
Core functions are `ebt_pkttype_mt`, `ebt_pkttype_mt_check`, and `xt_match ebt_pkttype_mt_reg`, using `struct ebt_pkttype_info`.

## Control Flow
Runtime matching compares `skb->pkt_type` to the configured value and XORs with the invert flag. Validation only constrains invert to 0 or 1 and intentionally allows any packet-type value.

## State And Persistence Behavior
No mutable state is kept. The match reads packet metadata only.

## Dependencies And Integration Points
Depends on skbuff packet type metadata, ebtables UAPI, and xtables registration. Packet type may be affected by bridge input, DNAT, redirect, or driver classification paths.

## Risks And Test Signals
Risks are minimal but include unexpected pkt_type rewrites before match evaluation. Tests should cover host, broadcast, multicast, otherhost, inversion, and invalid invert values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_pkttype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_redirect.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_redirect.c

## Purpose
Implements the legacy ebtables `redirect` target, rewriting destination MAC addresses so frames are delivered locally to either the bridge device or incoming port.

## Important APIs, Types, And Functions
Important functions are `ebt_redirect_tg`, `ebt_redirect_tg_check`, and `xt_target ebt_redirect_tg_reg`, using `struct ebt_redirect_info`.

## Control Flow
Runtime ensures the Ethernet header is writable, writes the destination MAC to the bridge device address in nat prerouting or to the incoming device address in brouting, sets `skb->pkt_type` to `PACKET_HOST`, and returns the configured verdict. Validation restricts use to nat prerouting or broute brouting hooks, validates verdicts, and forbids base-chain `RETURN`.

## State And Persistence Behavior
Only the current skb destination MAC and packet type are mutated. There is no stored state beyond rule data.

## Dependencies And Integration Points
Depends on bridge-port lookup under RCU, ebtables redirect UAPI, netfilter bridge hooks, and xtables registration. It interacts with broute and nat table traversal.

## Risks And Test Signals
Risks include wrong local MAC selection, writable-header failure, and table/hook validation gaps. Tests should cover nat prerouting redirect, brouting redirect, invalid hooks/tables, base-chain return rejection, and cloned/truncated skb behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_redirect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_snat.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_snat.c

## Purpose
Implements the legacy ebtables `snat` target for source MAC rewriting in bridge nat postrouting, with optional ARP sender hardware address rewriting.

## Important APIs, Types, And Functions
Core functions are `ebt_snat_tg`, `ebt_snat_tg_check`, and `xt_target ebt_snat_tg_reg`, using `struct ebt_nat_info` and the `NAT_ARP_BIT` verdict flag.

## Control Flow
Runtime ensures the Ethernet header is writable, copies the configured MAC into `h_source`, optionally updates the ARP sender hardware address for ARP frames, and returns the encoded verdict. Validation checks base-chain `RETURN`, ebtables target validity, and that only expected NAT_ARP bits accompany the verdict.

## State And Persistence Behavior
The target mutates the current skb Ethernet source and optionally ARP payload. No module-level or durable state exists.

## Dependencies And Integration Points
Depends on ARP helpers, ebtables nat UAPI, bridge postrouting hook registration via the nat table, and xtables target registration.

## Risks And Test Signals
Risks include inconsistent Ethernet/ARP source rewriting, failure on non-writable skbs, and target-bit encoding mistakes. Tests should cover ARP and non-ARP frames, NAT_ARP_BIT behavior, invalid verdicts, base-chain return rejection, and postrouting hook constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_snat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_stp.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_stp.c

## Purpose
Implements the legacy ebtables `stp` match for Spanning Tree Protocol BPDUs, including BPDU type and configuration BPDU fields such as root/sender priority, MAC addresses, costs, port, and timers.

## Important APIs, Types, And Functions
Important items are `struct stp_header`, `struct stp_config_pdu`, `ebt_filter_config`, `ebt_stp_mt`, `ebt_stp_mt_check`, and `xt_match ebt_stp_mt_reg`.

## Control Flow
Runtime first validates the LLC STP header prefix, applies type matching, and if the BPDU is a configuration BPDU and config fields are requested, safely reads the config PDU and checks each configured range/masked field with inversion support. Checkentry requires at least one valid bit, validates inversion masks, and for non-nft-compat rules requires the rule's destination MAC match to target the STP multicast address.

## State And Persistence Behavior
No mutable state exists. Match criteria are immutable per rule.

## Dependencies And Integration Points
Depends on bridge ebtables UAPI, Ethernet STP multicast address constants, masked Ethernet comparison, and xtables registration. It is part of legacy bridge filtering, not the bridge STP implementation itself.

## Risks And Test Signals
Risks include accepting non-STP frames, endian/range errors for packed PDU fields, and nft compatibility differences in destination-MAC validation. Tests should cover all config fields, type-only matching, masked root/sender addresses, malformed/truncated BPDUs, required destination MAC checks, and inversion semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_stp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_vlan.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_vlan.c

## Purpose
Implements the legacy ebtables `vlan` match for 802.1Q VLAN ID, priority, and encapsulated protocol fields.

## Important APIs, Types, And Functions
Core code includes `ebt_vlan_mt`, `ebt_vlan_mt_check`, `xt_match ebt_vlan_mt_reg`, and macros `GET_BITMASK` / `EXIT_ON_MISMATCH`, using `struct ebt_vlan_info`.

## Control Flow
Runtime reads either the skb accelerated VLAN tag or an inline `struct vlan_hdr`, extracts TCI, VLAN ID, priority, and encapsulated protocol, then applies requested comparisons with inversion. Validation requires outer ethproto 802.1Q, validates bitmask/inversion masks, handles VID 0 priority-tag rules, drops priority matching when a nonzero VID is requested, validates priority range, and rejects encapsulated length values below Ethernet minimum.

## State And Persistence Behavior
No mutable state exists. Match criteria are per-rule constants.

## Dependencies And Integration Points
Depends on VLAN header helpers, accelerated VLAN tag metadata, ebtables UAPI, xtables registration, and bridge ethproto matching in ebtables core.

## Risks And Test Signals
Risks include differing behavior between hardware-accelerated and inline tags, VID 0 priority semantics, and encapsulated proto/length validation. Tests should cover accelerated tags, inline VLAN headers, VID, priority, encapsulated protocol, inversions, invalid masks, priority with nonzero VID, and short frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_vlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtable_broute.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtable_broute.c

## Purpose
Defines the legacy ebtables `broute` table, which runs before normal bridge input processing to decide whether a frame should be bridged or routed.

## Important APIs, Types, And Functions
Important items are `initial_chain`, `initial_table`, `broute_table`, `ebt_broute`, `ebt_ops_broute`, `broute_table_init`, per-net exit hooks, and module init/exit.

## Control Flow
The module registers a template table and per-net operations. When a namespace needs the table, `ebt_register_table` installs a single `BROUTING` chain at `NF_BR_PRE_ROUTING` with first priority. Runtime calls `ebt_do_table`; a legacy ebtables `DROP` verdict is remapped to `NF_ACCEPT` plus `BR_INPUT_SKB_CB(skb)->br_netfilter_broute = 1` to signal routing, and packet type is restored when bridge input previously marked a frame as host for the bridge MAC.

## State And Persistence Behavior
State is per-network-namespace ebtables table registration and mutable table contents managed by ebtables core. The runtime side effect is the skb bridge control block broute flag.

## Dependencies And Integration Points
Depends on bridge input code, `br_private.h`, ebtables core APIs, netfilter bridge hooks, pernet operations, and the legacy broute userspace table semantics.

## Risks And Test Signals
Risks include the inverted DROP-means-route compatibility rule, packet-type restoration, forwarding-state gating, and namespace teardown ordering. Tests should cover ACCEPT bridge path, DROP route path, non-forwarding ports, host packet-type restoration, table replacement, and per-net module teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtable_broute.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtable_filter.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtable_filter.c

## Purpose
Defines the legacy ebtables `filter` table for bridge local input, forwarding, and local output filtering.

## Important APIs, Types, And Functions
Important declarations are `FILTER_VALID_HOOKS`, `initial_chains`, `initial_table`, `frame_filter`, `ebt_ops_filter`, `frame_filter_table_init`, and pernet init/exit wrappers.

## Control Flow
Module init registers pernet operations and a lazy template. Table initialization creates default ACCEPT `INPUT`, `FORWARD`, and `OUTPUT` base chains and registers `ebt_do_table` hooks at the bridge filter priorities. Pre-exit unregisters hooks before final table cleanup.

## State And Persistence Behavior
Per-network-namespace ebtables table state is held by ebtables core and can be replaced by userspace. This file itself only owns the static initial table template and registration lifetime.

## Dependencies And Integration Points
Depends on ebtables core registration, bridge netfilter hook constants, xtables modules referenced by loaded rules, and pernet namespace lifecycle.

## Risks And Test Signals
Risks include hook priority regressions, lazy template registration failures, and namespace cleanup leaks. Tests should cover default ACCEPT behavior, rules at all three hooks, table replacement, module autoload, and netns create/destroy with active rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtable_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtable_nat.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtable_nat.c

## Purpose
Defines the legacy ebtables `nat` table for bridge destination/source MAC translation at prerouting, local output, and postrouting.

## Important APIs, Types, And Functions
Important declarations are `NAT_VALID_HOOKS`, `initial_chains`, `initial_table`, `frame_nat`, `ebt_ops_nat`, `frame_nat_table_init`, and module/pernet lifecycle functions.

## Control Flow
The module registers a lazy ebtables table template. On namespace table initialization, default ACCEPT `PREROUTING`, `OUTPUT`, and `POSTROUTING` chains are installed with `ebt_do_table` hooks at bridge NAT priorities: destination NAT for bridged prerouting/local-output and source NAT for postrouting.

## State And Persistence Behavior
Runtime table contents are per-net ebtables state managed by the core. The file contributes static initial chains and hook registration lifetime only.

## Dependencies And Integration Points
Depends on ebtables core, bridge netfilter hook ordering, and target modules such as `ebt_dnat`, `ebt_snat`, `ebt_redirect`, and `ebt_arpreply`.

## Risks And Test Signals
Risks include hook priority/order regressions relative to bridge forwarding, invalid teardown ordering, and interaction with MAC rewrite targets. Tests should cover each hook, MAC DNAT/SNAT/redirect/arpreply behavior, table replacement, module autoload, and netns teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtable_nat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtables.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtables.c

## Purpose
Implements the legacy ebtables core: bridge-family rule evaluation, table registration/lazy templates, sockopt get/set ABI, userspace table replacement validation, counters, match/watcher/target module loading, per-net table lifetime, and 32-bit compat translation.

## Important APIs, Types, And Functions
Exported APIs include `ebt_do_table`, `ebt_register_table`, `ebt_unregister_table_pre_exit`, `ebt_unregister_table`, `ebt_register_template`, and `ebt_unregister_template`. Important internals include `struct ebt_pernet`, `struct ebt_template`, `ebt_basic_match`, `ebt_check_match`, `ebt_check_watcher`, `ebt_verify_pointers`, `ebt_check_entry_size_and_hooks`, `check_chainloops`, `translate_table`, `do_replace`, `do_replace_finish`, `update_counters`, `copy_everything_to_user`, compat conversion helpers, and sockopt handlers.

## Control Flow
Packet evaluation locks the active table, selects the base chain for the bridge hook, evaluates basic Ethernet/device/logical bridge matches, then extension matches, watchers, and targets. Standard verdicts accept/drop/return/continue or jump to user-defined chains through a per-CPU chain stack. Userspace replacement copies a table blob, verifies hook pointers and entry sizes, detects chain loops, resolves and validates match/watcher/target modules, swaps the active table under lock, snapshots counters, and cleans old modules/resources. Get paths copy active or initial tables back to userspace with extension names restored. Compat paths resize 32-bit entries and embedded match/watcher/target data before reuse of normal validation.

## State And Persistence Behavior
Per-net state is a live table list and dead-table list. Each table has rwlock-protected active `ebt_table_info`, vmalloced entries, per-CPU counters, optional per-CPU chain stacks, module references, and nf hook ops. State is memory-only and controlled through legacy sockopts requiring `CAP_NET_ADMIN`. Counters are accumulated per CPU and copied/updated atomically under write locks.

## Dependencies And Integration Points
Depends on x_tables, netfilter bridge hooks, nf sockopts, pernet generic storage, module autoloading, audit logging, usercopy, vmalloc, bridge private logical in/out device lookup, and all legacy ebtables table/match/target modules. It provides the common runtime for `ebtable_*` table files and `ebt_*` extensions.

## Risks And Test Signals
Highest risks are user-supplied blob validation, pointer/offset arithmetic, chain-loop detection, compat resizing, module refcount cleanup on partial failure, counter size overflow, concurrent table replacement versus packet evaluation, and namespace teardown. Strong signals include syzkaller/usercopy fuzzing, KASAN/KCSAN runs, 32-bit compat ebtables tests, table replace/get/counter round trips, loop/jump validation tests, module autoload/unload tests, per-net namespace teardown, and packet traversal tests for base chains and user-defined chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/nf_conntrack_bridge.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/nf_conntrack_bridge.c

## Purpose
Provides native bridge-family IPv4/IPv6 connection tracking, including bridge prerouting defragmentation/tracking, local-in clone handling, postrouting confirmation, and refragmentation after conntrack processing.

## Important APIs, Types, And Functions
Key functions include `nf_ct_bridge_pre`, `nf_ct_bridge_in`, `nf_ct_bridge_post`, `nf_ct_br_defrag4`, `nf_ct_br_defrag6`, `nf_br_ip_fragment`, `nf_ct_bridge_refrag`, `nf_ct_bridge_frag_save`, `nf_ct_bridge_frag_restore`, and `nf_ct_bridge_refrag_post`. Registration uses `nf_ct_bridge_info` with three `nf_hook_ops`.

## Control Flow
Prerouting skips already-tracked or untracked packets, trims and validates IPv4/IPv6 payloads, defragments fragments while preserving bridge skb control block state, then invokes `nf_conntrack_in` using IPv4 or IPv6 protocol family. Local-in clears unconfirmed conntrack from non-host clones so inet prerouting can track again. Postrouting confirms conntrack and, when `frag_max_size` indicates defragmentation happened, saves L2/VLAN data, fragments IPv4 or IPv6 output, restores the bridge L2/VLAN header per fragment, and queues through bridge transmit.

## State And Persistence Behavior
State lives in skb conntrack pointers, bridge skb control block fields, defrag queues, and conntrack tables owned by nf_conntrack. The module registers bridge hooks globally through `nf_ct_bridge_register`; no disk persistence exists.

## Dependencies And Integration Points
Depends on nf_conntrack core/helper APIs, IPv4/IPv6 defrag and fragmentation helpers, bridge output `br_dev_queue_push_xmit`, VLAN tag helpers, skb control block layout from `br_private.h`, and module alias `nf_conntrack-AF_BRIDGE`.

## Risks And Test Signals
Risks include skb control block save/restore mistakes, fragment geometry loss, VLAN tag/header restoration, confirmed clone handling for multicast/broadcast, IPv6 defrag optionality, and silent blackhole behavior on fragmentation failure. Tests should cover fragmented IPv4/IPv6 bridge traffic, VLAN-tagged fragments, multicast clones, untracked non-IP traffic, postrouting refragmentation MTU behavior, conntrack zone behavior, and netns/module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/nf_conntrack_bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/nft_meta_bridge.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/nft_meta_bridge.c

## Purpose
Adds bridge-family nftables `meta` expression support for bridge-specific keys, while delegating generic meta keys to the common nft meta implementation.

## Important APIs, Types, And Functions
Important functions are `nft_meta_bridge_get_eval`, `nft_meta_bridge_get_init`, `nft_meta_bridge_set_eval`, `nft_meta_bridge_set_init`, `nft_meta_bridge_set_validate`, `nft_meta_bridge_select_ops`, and helper `nft_meta_get_bridge`. The expression type is `nft_meta_bridge_type`.

## Control Flow
Get expressions return bridge input/output interface names, input PVID, bridge VLAN protocol, and bridge hardware address when the packet device is a bridge port and required VLAN state is enabled; otherwise they break rule evaluation. Set expressions currently support bridge broute by writing `BR_INPUT_SKB_CB(skb)->br_netfilter_broute`. Init selects get or set ops based on destination/source register attributes, and validation restricts broute and input hardware address keys to prerouting.

## State And Persistence Behavior
Get paths read device, bridge, and VLAN state under packet context. Set path mutates only the skb bridge control block. Nft expression configuration is stored in nftables rulesets, not by this module directly.

## Dependencies And Integration Points
Depends on nftables core/meta helpers, bridge private APIs, `br_vlan_enabled`, `br_vlan_get_pvid_rcu`, `br_vlan_get_proto`, bridge port/master relationships, and NF_BR hook validation.

## Risks And Test Signals
Risks include missing bridge-device checks, invalid register lengths, hook validation gaps, and broute flag semantics. Tests should cover all bridge meta keys, absent/non-bridge devices, VLAN disabled behavior, broute set in prerouting, invalid get/set attribute combinations, and generic meta fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/nft_meta_bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/nft_reject_bridge.c -->
# sources/distributed-fs/ceph-client/net/bridge/netfilter/nft_reject_bridge.c

## Purpose
Implements the nftables bridge-family `reject` expression, generating IPv4/IPv6 TCP resets or ICMP unreachable replies at bridge prerouting/local-in while ultimately dropping the original packet.

## Important APIs, Types, And Functions
Important functions are `nft_reject_bridge_eval`, `nft_reject_bridge_validate`, `nft_reject_br_push_etherhdr`, `nft_reject_br_send_v4_tcp_reset`, `nft_reject_br_send_v4_unreach`, `nft_reject_br_send_v6_tcp_reset`, and `nft_reject_br_send_v6_unreach`. The expression uses common `nft_reject_init`/`dump` helpers.

## Control Flow
Evaluation ignores broadcast/multicast destinations, then dispatches on Ethernet protocol and reject type. It asks IPv4/IPv6 reject helpers to build the L3 response, pushes a reversed Ethernet header and VLAN tag from the original skb, forwards the generated skb through the ingress bridge port, and sets the original verdict to `NF_DROP`. Validation allows only bridge prerouting and local-in chains.

## State And Persistence Behavior
No persistent state is kept. The expression emits response packets as side effects and drops the triggering skb.

## Dependencies And Integration Points
Depends on nftables core, common reject helpers, IPv4/IPv6 reject code, bridge forwarding `br_forward`, bridge-port lookup, VLAN accelerated tag helpers, and NF_BR hook validation.

## Risks And Test Signals
Risks include using the wrong egress device for bridge-generated replies, missing VLAN preservation, emitting rejects for multicast/broadcast, and hook validation errors. Tests should cover IPv4/IPv6 TCP reset, ICMP/ICMPv6 unreachable, ICMPx mapping, VLAN-tagged packets, broadcast/multicast no-reply drop, unsupported ethproto drop, and invalid hook rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/netfilter/nft_reject_bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/Kconfig -->
# sources/distributed-fs/ceph-client/net/can/Kconfig

## Purpose
Defines the kernel configuration menu for the Controller Area Network protocol family and core CAN socket protocols.

## Important APIs, Types, And Functions
The file declares `CAN`, `CAN_RAW`, `CAN_BCM`, `CAN_GW`, sources `net/can/j1939/Kconfig`, and declares `CAN_ISOTP`. `CAN` selects `SKB_EXTENSIONS`.

## Control Flow
When `CAN` is enabled, users can select raw CAN sockets, Broadcast Manager sockets, CAN gateway/router support, J1939 options from the sourced Kconfig, and ISO-TP segmented transport support. Several protocol options default to `y` when CAN is enabled.

## State And Persistence Behavior
No runtime state exists. Selected symbols persist in kernel configuration and drive built-in/module/absent protocol availability.

## Dependencies And Integration Points
Integrates with `net/can/Makefile`, PF_CAN core code, socket protocols, J1939 subdirectory configuration, and networking documentation referenced by help text.

## Risks And Test Signals
Risks include default-enabling protocols unexpectedly, missing dependencies for protocol modules, or breaking sourced J1939 config visibility. Signals include Kconfig linting, `oldconfig`, `allmodconfig`, protocol module builds, and runtime socket creation tests for CAN_RAW, CAN_BCM, CAN_GW, J1939, and CAN_ISOTP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/Makefile -->
# sources/distributed-fs/ceph-client/net/can/Makefile

## Purpose
Maps CAN Kconfig symbols to PF_CAN core and protocol object builds.

## Important APIs, Types, And Functions
Important Kbuild targets are `can.o` from `af_can.o` plus optional `proc.o`, `can-raw.o` from `raw.o`, `can-bcm.o` from `bcm.o`, `can-gw.o` from `gw.o`, the `j1939/` subdirectory, and `can-isotp.o` from `isotp.o`.

## Control Flow
Kbuild includes each object or subdirectory when the corresponding `CONFIG_CAN*` symbol is enabled. `can-$(CONFIG_PROC_FS)` conditionally adds procfs support to the core `can.o` composite.

## State And Persistence Behavior
No runtime state exists in the Makefile. It defines build graph composition and module names.

## Dependencies And Integration Points
Integrates with `net/can/Kconfig`, PF_CAN core sources, protocol implementation files, and Kbuild's composite object syntax.

## Risks And Test Signals
Risks include stale object names, missing protocol mappings, or incorrect procfs conditional inclusion. Build tests across CAN as built-in/module and protocol combinations, plus module load smoke tests, are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/Makefile -->
