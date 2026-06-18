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
