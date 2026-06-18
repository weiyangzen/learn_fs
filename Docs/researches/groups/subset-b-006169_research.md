# Research: subset-b-006169

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_multicast.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_multicast.c

## Purpose

`br_multicast.c` is the Linux bridge multicast snooping implementation. It tracks multicast database (MDB) entries for L2, IPv4 IGMP, and IPv6 MLD traffic, maintains bridge-level and port/VLAN-level multicast contexts, sends bridge-generated queries, processes reports/leaves/queries, manages multicast-router discovery, and exposes helper APIs used by bridge forwarding, netlink, switchdev, and external bridge consumers. It is the main owner of runtime multicast state: bridge MDB entries, per-port group memberships, source-specific memberships, router-port lists, querier state, timers, GC work, and per-CPU multicast statistics.

## Important APIs, Types, and Functions

Key state types come from `br_private.h`: `struct net_bridge`, `struct net_bridge_mcast`, `struct net_bridge_mcast_port`, `struct net_bridge_mdb_entry`, `struct net_bridge_port_group`, `struct net_bridge_group_src`, and `struct bridge_mcast_stats`. The file also uses EHT helpers from `br_private_mcast_eht.h`.

Hash tables are configured by `br_mdb_rht_params` for MDB entries keyed by `struct br_ip`, and `br_sg_port_rht_params` for source/group/port entries keyed by `struct net_bridge_port_group_sg_key`.

Lookup and forwarding APIs include `br_mdb_ip_get()`, `br_mdb_entry_skb_get()`, `br_multicast_new_group()`, `br_multicast_new_port_group()`, `br_multicast_del_pg()`, `br_multicast_sg_add_exclude_ports()`, and `br_multicast_star_g_handle_mode()`. These maintain `*,G` and `S,G` relationships, including automatic `MDB_PG_FLAGS_STAR_EXCL` port groups for EXCLUDE-mode `*,G` memberships.

IGMP/MLD receive paths are `br_multicast_rcv()`, `br_multicast_ipv4_rcv()`, `br_multicast_ipv6_rcv()`, `br_ip4_multicast_igmp3_report()`, `br_ip6_multicast_mld2_report()`, query handlers, and leave handlers. They parse protocol messages, update MDB state, and set bridge input control flags such as `BR_INPUT_SKB_CB(skb)->igmp` and `mrouters_only`.

Query generation is handled by `br_ip4_multicast_alloc_query()`, `br_ip6_multicast_alloc_query()`, `br_multicast_alloc_query()`, `__br_multicast_send_query()`, `br_multicast_send_query()`, and the bridge/port query timer callbacks. These synthesize IGMPv2/v3 or MLDv1/v2 query skbs with router-alert options, VLAN tags where required, checksums, and source lists for last-member/source-specific retransmission.

Lifecycle and configuration APIs include `br_multicast_init()`, `br_multicast_ctx_init()`, `br_multicast_open()`, `br_multicast_stop()`, `br_multicast_dev_del()`, `br_multicast_add_port()`, `br_multicast_del_port()`, `br_multicast_toggle()`, `br_multicast_toggle_vlan_snooping()`, `br_multicast_toggle_global_vlan()`, `br_multicast_set_router()`, `br_multicast_set_port_router()`, `br_multicast_set_vlan_router()`, `br_multicast_set_querier()`, `br_multicast_set_igmp_version()`, `br_multicast_set_mld_version()`, and query interval setters.

Exported helper APIs are `br_multicast_enabled()`, `br_multicast_router()`, `br_multicast_list_adjacent()`, `br_multicast_has_querier_anywhere()`, `br_multicast_has_querier_adjacent()`, and `br_multicast_has_router_adjacent()`.

## Control Flow

Ingress starts at `br_multicast_rcv()`. It clears multicast input flags, checks global snooping, optionally switches to VLAN multicast contexts, and dispatches by protocol. IPv4 goes through `ip_mc_check_igmp()`: non-IGMP multicast packets may be marked router-only, PIM hello and MRD advertisements mark router ports, parse errors increment stats, and valid IGMP messages update groups or query state. IPv6 follows the analogous MLD path via `ipv6_mc_check_mld()`.

IGMPv1/v2 and MLDv1 reports create EXCLUDE-mode memberships with timer refresh. IGMPv3/MLDv2 reports iterate group records and implement the include/exclude state machines: `MODE_IS_INCLUDE`, `MODE_IS_EXCLUDE`, `CHANGE_TO_INCLUDE`, `CHANGE_TO_EXCLUDE`, `ALLOW_NEW_SOURCES`, and `BLOCK_OLD_SOURCES`. The handlers add/delete source entries, mod source timers, send group/source-specific queries when needed, change filter mode, notify MDB updates, and call `br_multicast_eht_handle()` for host-aware fast-leave tracking.

Leave processing either deletes a port group immediately when bridge fast-leave is enabled, or sends last-member queries and shortens membership timers. Query processing updates selected querier state for general queries, marks multicast router state, and shortens group/port timers for group-specific queries.

The timer graph is central. MDB entry timers clear host-joined state and delete empty MDB entries. Port-group timers convert EXCLUDE to INCLUDE, delete expired sources, or delete empty groups. Source timers delete INCLUDE sources or mark EXCLUDE sources blocked. Router timers expire local and per-port router state. Own-query timers drive startup and periodic bridge queries. Rexmit timers send last-member group/source queries until counters drain.

## State and Persistence Behavior

State is in memory only; no on-disk persistence exists. MDB and source/group/port lookups persist for the lifetime of the bridge, port, VLAN, or membership timers. Durable user-visible state is emitted through netlink notifications (`br_mdb_notify()`, `br_rtr_notify()`), switchdev attributes (`SWITCHDEV_ATTR_ID_BRIDGE_MC_DISABLED`, `SWITCHDEV_ATTR_ID_BRIDGE_MROUTER`, `SWITCHDEV_ATTR_ID_PORT_MROUTER`), and exported query/router helper APIs.

Concurrency uses `br->multicast_lock` for mutation, RCU lists for readers, rhashtable for MDB and `S,G,port` indexes, and delayed destruction through `br->mcast_gc_list` plus `br->mcast_gc_work`. Timers are stopped with `timer_delete_sync()` or `timer_shutdown_sync()` during teardown; object memory is usually released with `kfree_rcu()`.

VLAN snooping creates separate bridge and port multicast contexts per VLAN. Context choice is deliberately careful because VLAN snooping can be toggled while timers and packets are active. `br_multicast_pg_to_port_ctx()` is explicitly read-only and can return the currently applicable context rather than the historical one.

Statistics are per-CPU `bridge_mcast_stats`, updated with `u64_stats_update_begin/end()` and collected with retry loops in `br_multicast_get_stats()`.

## Dependencies and Integration Points

The file depends on bridge private structures, multicast protocol helpers (`ip_mc_check_igmp()`, `ipv6_mc_check_mld()`), VLAN helpers, netfilter bridge local-out for query transmission, switchdev offload attributes, netlink MDB notifications, RCU/rhashtable/timer/workqueue primitives, IPv4/IPv6 address selection and multicast group APIs, and EHT support in `br_multicast_eht.c`.

Forwarding integration occurs through MDB lookups from packet forwarding (`br_mdb_entry_skb_get()`) and router-only flags on ingress. Netlink integration exposes configuration and reports querier/router/MDB state. Switchdev integration tells hardware drivers when bridge or port multicast-router/disabled state changes.

## Risks and Edge Cases

The highest-risk areas are concurrency and lifetime: timers race with port/VLAN teardown, RCU readers, rhashtable deletion, and GC work. The code relies on consistent `multicast_lock` coverage and delayed frees. VLAN snooping toggles can change which context timers read; comments explicitly acknowledge possible timer inconsistency.

State-machine correctness is subtle for IGMPv3/MLDv2 source filtering, especially `*,G` EXCLUDE propagation to `S,G`, blocked `S,G` entries, permanent user-managed MDB entries, and EHT fast-leave deletion. Query generation can fail silently on MTU, allocation, missing IPv6 source address, or checksum/header guard failures.

Resource limits are enforced by global `br->hash_max`, per-port/per-port-VLAN max group counts, `PG_SRC_ENT_LIMIT`, and EHT host limits. Hitting the bridge hash limit disables multicast snooping through `br_mc_disabled_update()` and `BROPT_MULTICAST_ENABLED`, which is operationally significant.

## Test Signals

Useful tests include bridge multicast selftests covering IGMPv2/v3 and MLDv1/v2 joins, leaves, query election, last-member retransmission, fast leave, VLAN snooping, multicast-to-unicast, permanent MDB entries, and multicast router port state. Runtime signals include `bridge mdb show`, `bridge -d link`, multicast stats, switchdev notifications, tracepoint `trace_br_mdb_full`, and packet captures showing generated IGMP/MLD queries with correct VLAN tags, router-alert options, checksums, and source lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_multicast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_multicast_eht.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_multicast_eht.c

## Purpose

`br_multicast_eht.c` implements Explicit Host Tracking for bridge multicast fast leave. It augments a `net_bridge_port_group` with per-host and per-source trees so the bridge can tell which hosts on a shared port still need a source/group membership. When the last tracked host for a source disappears, it can delete the corresponding `S,G` source entry and, in some cases, delete the port group quickly.

## Important APIs, Types, and Functions

The public functions are `br_multicast_eht_clean_sets()`, `br_multicast_eht_handle()`, and `br_multicast_eht_set_hosts_limit()`. Inline helpers and data structures are declared in `br_private_mcast_eht.h`: `struct net_bridge_group_eht_host`, `struct net_bridge_group_eht_set_entry`, `struct net_bridge_group_eht_set`, `union net_bridge_eht_addr`, `br_multicast_eht_should_del_pg()`, and host count helpers.

Each port group owns two red-black trees: `pg->eht_host_tree`, keyed by host address, and `pg->eht_set_tree`, keyed by source address. Each EHT source set owns an `entry_tree` keyed by host address. Hosts also keep an hlist of their set entries so a host can be removed across all sources.

Core lookup/create/delete functions are `br_multicast_eht_host_lookup()`, `br_multicast_eht_set_lookup()`, `br_multicast_eht_set_entry_lookup()`, `__eht_lookup_create_host()`, `__eht_lookup_create_set()`, `__eht_lookup_create_set_entry()`, `br_multicast_del_eht_set_entry()`, `br_multicast_del_eht_host()`, and `br_multicast_del_eht_set()`.

Protocol update functions are `br_multicast_eht_allow()`, `br_multicast_eht_block()`, `br_multicast_eht_inc()`, `br_multicast_eht_exc()`, `__eht_ip4_handle()`, and `__eht_ip6_handle()`.

## Control Flow

`br_multicast_eht_handle()` is called from the IGMPv3/MLDv2 source-filter state-machine in `br_multicast.c`. EHT is enabled only when the bridge port has `BR_MULTICAST_FAST_LEAVE`; otherwise the function exits with no change.

On a report, the host address is copied into `union net_bridge_eht_addr` and the message type dispatches to IPv4 or IPv6 handlers. ALLOW adds source entries when the host is in INCLUDE mode and deletes entries when it is in EXCLUDE mode. BLOCK does the inverse. INCLUDE and EXCLUDE reports use `__eht_inc_exc()` to optionally flush a host's previous entries when the host changes mode or when a to-report transition requires replacement.

Creation links three objects: an EHT set for the source, an EHT host for the listener address and filter mode, and a set entry connecting both. Set and entry timers are refreshed to group membership interval (`br_multicast_gmi()`). Deletion removes the set entry from both the per-source RB tree and host hlist, destroys the host if it has no remaining entries, and destroys the set when its entry tree is empty.

Timers `br_multicast_eht_set_entry_expired()` and `br_multicast_eht_set_expired()` run under `br->multicast_lock` and delete stale entries/sets. `br_multicast_eht_clean_sets()` removes all EHT sets for a port group when the group itself is deleted.

## State and Persistence Behavior

EHT state is transient in-memory state rooted in the port group. It is deleted when port-group membership is deleted, source membership expires, host entries time out, or bridge/port cleanup runs. Memory reclamation uses the multicast GC list and `system_long_wq`, matching `br_multicast.c` object lifetime patterns.

Host count state lives in `net_bridge_port.multicast_eht_hosts_cnt` and `multicast_eht_hosts_limit`. `br_multicast_eht_set_hosts_limit()` updates the limit under `multicast_lock`; new hosts are refused when the count reaches the limit. The auto-created zero-source entry used for EXCLUDE host mode is intentionally not counted against per-host source entry limits.

## Dependencies and Integration Points

This file depends on `br_multicast.c` for group/source state, timers, and deletion functions. It calls `br_multicast_find_group_src()` and `br_multicast_del_group_src()` to remove bridge `S,G` source state when no EHT set remains for a source. Netlink integration is indirect: `br_netlink.c` exposes and sets EHT host limits and reports host counters. EHT behavior is also tied to the bridge port `BR_MULTICAST_FAST_LEAVE` flag.

## Risks and Edge Cases

The RB-tree and hlist relationships must stay consistent; deleting a set entry touches the source tree, the host list, host counters, GC list, and potentially parent host/set destruction. A bug in zero-address handling could incorrectly count or drop EXCLUDE-mode tracking. The helper `__eht_del_set_entries()` appears to copy source bytes into `src_ip` directly, so its correctness depends on the `struct br_ip` layout and should be reviewed carefully if that structure changes.

The EHT limit protects memory growth, but hitting it silently prevents new EHT host creation and can reduce fast-leave precision. Timer expiration and report processing both mutate the same trees under `multicast_lock`; missing lock coverage would be severe.

## Test Signals

Good tests use multiple hosts behind one bridge port with fast leave enabled, exercising IGMPv3 and MLDv2 INCLUDE/EXCLUDE transitions, ALLOW/BLOCK messages, host mode changes, zero-source EXCLUDE tracking, source expiration, and host-limit rejection. Observable signals are `bridge -d link` EHT counters, MDB/source entry changes after last host leaves, packet captures showing reduced query/leave behavior, and memory lifetime checks under KASAN/KCSAN/lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_multicast_eht.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_netfilter_hooks.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_netfilter_hooks.c

## Purpose

`br_netfilter_hooks.c` implements the bridge netfilter compatibility layer that lets bridged IPv4, IPv6, ARP, VLAN-tagged, and PPPoE-encapsulated traffic traverse iptables/ip6tables/arptables/nftables hooks. It temporarily presents bridged frames as L3 packets to IPv4/IPv6/ARP netfilter, remembers bridge metadata in `nf_bridge_info`, then restores L2 encapsulation and resumes bridge forwarding or delivery.

## Important APIs, Types, and Functions

Per-net namespace state is `struct brnf_net`, containing hook enablement and sysctl knobs: `call_iptables`, `call_ip6tables`, `call_arptables`, `filter_vlan_tagged`, `filter_pppoe_tagged`, and `pass_vlan_indev`.

Header classification helpers are `IS_IP()`, `IS_IPV6()`, `IS_ARP()`, `vlan_proto()`, `is_vlan_ip()`, `is_vlan_ipv6()`, `is_vlan_arp()`, `pppoe_proto()`, `is_pppoe_ip()`, and `is_pppoe_ipv6()`. Encapsulation helpers are `nf_bridge_encap_header_len()`, `nf_bridge_pull_encap_header()`, `nf_bridge_pull_encap_header_rcsum()`, `nf_bridge_update_protocol()`, and `setup_pre_routing()`.

Main hook callbacks are `br_nf_pre_routing()`, `br_nf_forward()`, `br_nf_post_routing()`, optional conntrack `br_nf_local_in()`, and `ip_sabotage_in()`. Finish callbacks include `br_nf_pre_routing_finish()`, `br_nf_pre_routing_finish_bridge()`, `br_nf_forward_finish()`, and `br_nf_dev_queue_xmit()`.

Registration objects are `br_nf_ops`, `br_ops`, `brnf_notifier`, and `brnf_net_ops`. `br_nf_hook_thresh()` is exported internally to resume bridge hooks after the bridge-netfilter priority point.

## Control Flow

Bridge `NF_BR_PRE_ROUTING` calls `br_nf_pre_routing()`. It pulls VLAN/PPPoE encapsulation if configured, checks the per-net and per-bridge call flags, validates IPv4 headers with `br_validate_ipv4()` or dispatches IPv6 to `br_nf_pre_routing_ipv6()`, allocates `nf_bridge_info`, records original destination, and calls the L3 PRE_ROUTING hook. The finish function detects DNAT by comparing the current destination with the saved one. If routing says the new destination is still reachable through the bridge, it restores bridge encapsulation and resumes bridge PRE_ROUTING via `br_nf_pre_routing_finish_bridge()`. Otherwise it converts the packet for local/routed handling by changing destination MAC and `PACKET_HOST` state.

Bridge `NF_BR_FORWARD` calls `br_nf_forward()`. IP and IPv6 packets are unshared, decapsulated, validated, given physical out-device metadata, and passed through L3 FORWARD. ARP packets optionally go through ARP FORWARD. `br_nf_forward_finish()` restores encapsulation, original protocol, `PACKET_OTHERHOST` state, and resumes bridge forwarding hooks before `br_forward_finish()`.

Bridge `NF_BR_POST_ROUTING` calls `br_nf_post_routing()`. Packets that still carry `nf_bridge_info->physoutdev` are decapsulated and sent through L3 POST_ROUTING. `br_nf_dev_queue_xmit()` restores protocol and encapsulation, handles packet type restoration, frees bridge netfilter skb extension on normal transmit, and fragments IPv4/IPv6 packets when defragmentation plus MTU constraints require it.

`ip_sabotage_in()` prevents locally destined bridge packets from being handed to IPv4/IPv6 PRE_ROUTING a second time. `br_nf_dev_xmit()` handles the slow bridged-DNAT path where neighbour output rewrote the MAC header and the original bridge source header must be restored before bridge forwarding continues.

## State and Persistence Behavior

Per-packet state lives in the skb extension `SKB_EXT_BRIDGE_NF` as `struct nf_bridge_info`. It records original encapsulation protocol, physical in/out devices, original IPv4/IPv6 destination, fragmentation limits, packet type, DNAT bridge path state, neighbour header bytes, and the `in_prerouting`/`sabotage_in_done` flags.

Per-CPU state `brnf_frag_data_storage` stores temporary MAC/encapsulation data while IPv4 or IPv6 fragmentation is rebuilding L2 headers. It is protected with `local_lock_nested_bh()`.

Per-net persistent state is registered through `brnf_net_ops`; sysctl state exists under `net/bridge` when `CONFIG_SYSCTL` is enabled. Bridge netfilter hooks are registered lazily on `NETDEV_REGISTER` for bridge master devices and unregistered on namespace exit.

## Dependencies and Integration Points

The file integrates bridge hooks (`NFPROTO_BRIDGE`) with IPv4, IPv6, ARP, conntrack, dst/neighbour routing, VLAN, PPPoE, sysctl, net namespace generic storage, and bridge forwarding (`br_handle_frame_finish()`, `br_forward_finish()`, `br_dev_queue_push_xmit()`). It calls IPv6-specific code in `br_netfilter_ipv6.c` for IPv6 validation and PRE_ROUTING handling. It also publishes `nf_br_ops.br_dev_xmit_hook` so bridge device transmit can delegate bridged-DNAT completion.

## Risks and Edge Cases

The main risk is preserving skb invariants while repeatedly pulling and pushing L2 encapsulation. Bugs can corrupt header offsets, checksums, protocol values, packet type, VLAN tags, or physical device metadata. DNAT routing decisions are subtle because packets may remain bridged or become routed after L3 netfilter changes destination addresses.

Fragmentation is explicitly imperfect: comments note that original fragment boundaries are not preserved when refragmenting. Conntrack handling for multicast/broadcast clone races is delicate and depends on confirmed/unconfirmed skb reference assumptions. Sysctl defaults enable bridge calls to iptables, ip6tables, and arptables, which can surprise deployments and affect forwarding performance.

## Test Signals

Tests should cover IPv4, IPv6, ARP, VLAN-tagged, and PPPoE bridge traffic with bridge-nf sysctls both enabled and disabled; DNAT to same bridge, DNAT to routed device, REDIRECT, local delivery, broadcast/multicast conntrack confirmation, MTU fragmentation, and IPv6-disabled handling. Observable signals include netfilter rule hits in bridge and L3 families, tcpdump header preservation across hooks, conntrack table behavior for multicast clones, sysctl values under `net/bridge`, and drop reasons for malformed packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_netfilter_hooks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_netfilter_ipv6.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_netfilter_ipv6.c

## Purpose

`br_netfilter_ipv6.c` contains the IPv6-specific bridge netfilter PRE_ROUTING path. It validates IPv6 packets received by the bridge, sends them through IPv6 PRE_ROUTING, detects DNAT, restores bridge encapsulation, and decides whether the packet should continue bridged or be converted for routed/local handling.

## Important APIs, Types, and Functions

The exported functions are `br_validate_ipv6()` and `br_nf_pre_routing_ipv6()`, declared for the main hook file through `include/net/netfilter/br_netfilter.h` when IPv6 support is enabled.

`br_validate_ipv6()` checks pullability, IPv6 version, hop-by-hop extension length through `nf_ip6_check_hbh_len()`, payload length versus skb length, checksum-safe trimming, and clears `IP6CB(skb)`.

`br_nf_pre_routing_finish_ipv6()` mirrors the IPv4 finish path in `br_netfilter_hooks.c`. It compares destination addresses with `br_nf_ipv6_daddr_was_changed()`, reroutes on DNAT with `ip6_route_input()`, handles bridge-parent routes, restores original bridge protocol, pushes encapsulation, and resumes bridge hooks.

`br_nf_pre_routing_ipv6()` validates the skb, allocates `nf_bridge_info`, calls `setup_pre_routing()`, stores the original IPv6 destination, sets protocol and transport-header offsets, invokes `NF_HOOK(NFPROTO_IPV6, NF_INET_PRE_ROUTING, ...)`, and returns `NF_STOLEN`.

## Control Flow

The main bridge pre-routing hook dispatches IPv6 frames here after optional VLAN/PPPoE decapsulation and call-ip6tables checks. `br_nf_pre_routing_ipv6()` first validates the skb. If validation or metadata allocation fails, it returns a bridge netfilter drop verdict with a reason. Otherwise, `setup_pre_routing()` records the physical ingress device and changes `skb->dev` to the logical bridge or bridge VLAN device. IPv6 PRE_ROUTING then runs.

When the IPv6 PRE_ROUTING hook finishes, `br_nf_pre_routing_finish_ipv6()` stores fragment size state, restores `PACKET_OTHERHOST` if needed, clears `in_prerouting`, and checks for DNAT. If the destination changed, it drops the old dst, runs `ip6_route_input()`, and either continues bridged when the route output device is still the bridge device, or rewrites the Ethernet destination to the bridge device address and marks the skb as `PACKET_HOST` for routed/local processing. If the destination did not change, it uses the bridge parent rtable. Both non-drop paths restore the physical bridge input device, update the original protocol, push encapsulation, and resume bridge PRE_ROUTING.

## State and Persistence Behavior

This file owns no persistent global state. Per-packet state is stored in `nf_bridge_info`, especially `ipv6_daddr`, `frag_max_size`, `pkt_otherhost`, and `in_prerouting`. IPv6 control block state is cleared during validation and `IP6CB(skb)->frag_max_size` is copied back into bridge netfilter metadata after IPv6 hooks run.

## Dependencies and Integration Points

The implementation depends on IPv6 core helpers (`ipv6_hdr()`, `ipv6_payload_len()`, `ip6_route_input()`), IPv6 stats, netfilter bridge metadata helpers (`nf_bridge_alloc()`, `nf_bridge_info_get()`, `nf_bridge_update_protocol()`, `nf_bridge_push_encap_header()`), `setup_pre_routing()` and `br_nf_hook_thresh()` from `br_netfilter_hooks.c`, and bridge forwarding completion through `br_handle_frame_finish()` or `br_nf_pre_routing_finish_bridge()`.

## Risks and Edge Cases

IPv6 validation must keep skb length, extension header length, checksum state, and `IP6CB` state consistent before the packet enters IPv6 netfilter. DNAT handling depends on route output device comparison; wrong device restoration can turn a bridged packet into a routed one or vice versa. The file shares header offset and encapsulation assumptions with the main hook file, so VLAN/PPPoE changes there directly affect this path.

## Test Signals

Useful tests include IPv6 bridge forwarding with `bridge-nf-call-ip6tables` enabled and disabled, IPv6 DNAT to another host on the same bridge, DNAT to routed/local destinations, VLAN and PPPoE IPv6 frames, malformed payload length and hop-by-hop headers, IPv6-disabled behavior in the caller, and packet captures verifying that Ethernet headers and skb devices are restored correctly after IPv6 PRE_ROUTING.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_netfilter_ipv6.c -->
