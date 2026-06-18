<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/mesh-interface.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/mesh-interface.c

## Purpose
Implements the virtual `batadv` mesh netdevice: rtnetlink creation/destruction, netdev operations, transmit/receive encapsulation policy, VLAN bookkeeping, counters, ethtool statistics, and slave hard-interface attachment.

## APIs, Types, and Functions
Public symbols are `batadv_skb_head_push()`, `batadv_interface_rx()`, `batadv_meshif_vlan_release()`, `batadv_meshif_vlan_get()`, `batadv_meshif_create_vlan()`, `batadv_meshif_is_valid()`, and `batadv_link_ops`. Netdevice operations include `batadv_meshif_init_late()`, `batadv_interface_stats()`, VLAN add/kill callbacks, MAC/MTU changes, `batadv_interface_tx()`, and slave add/delete. Rtnetlink uses `batadv_meshif_init_early()`, `batadv_meshif_validate()`, `batadv_meshif_newlink()`, and `batadv_meshif_destroy_netlink()`. Etthool support is provided by `batadv_get_drvinfo()`, `batadv_get_strings()`, `batadv_get_ethtool_stats()`, and `batadv_get_sset_count()`.

## Control Flow
`batadv_interface_tx()` is the central egress path. It rejects inactive mesh interfaces and batman-in-batman frames, resets the skb control block, extracts VLAN state, lets BLA filter loops, learns local clients into TT, snoops DHCP/ARP for DAT/gateway behavior, drops STP/ECTP, and then chooses between broadcast, gateway unicast, multicast unicast fanout, batman-adv multicast packets, or TT unicast. Broadcast prepends `struct batadv_bcast_packet`, fills version/TTL/originator/sequence, and schedules `batadv_send_bcast_packet()`. Unicast paths call gateway, multicast, or TT send helpers and update per-CPU counters.

`batadv_interface_rx()` removes a parsed batman-adv header, resets conntrack, validates the encapsulated Ethernet frame, rejects nested batman-adv payloads, updates RX counters, lets BLA consume frames, adds temporary global TT entries for learned sources, applies AP isolation marks or drops isolated unicast, and finally injects the skb via `netif_rx()`.

Mesh netdevice creation runs early setup from rtnl link ops, then late `ndo_init` allocates per-CPU counters, initializes tunables and feature state, selects the routing algorithm, and calls `batadv_mesh_init()`. Deletion detaches all lower hard interfaces, destroys the untagged VLAN entry, unregisters the netdevice, calls `batadv_mesh_free()`, and waits for RCU callbacks.

## State and Persistence
Persistent state lives in `struct batadv_priv` attached to the netdevice: mesh state, selected algorithm, primary interface, gateway settings, TT counters, broadcast/fragment sequence numbers, multicast defaults, per-CPU statistic counters, isolation marks, and the `meshif_vlan_list`. VLAN objects are kref-managed and RCU-freed; creation also installs a NOPURGE local TT entry for the mesh MAC on that VID, while destruction explicitly removes it. User-set MTU is persisted in `bat_priv->mtu_set_by_user`.

## Dependencies and Integration
This file sits at the Linux netdevice/rtnetlink boundary and depends on hard-interface management, routing algorithm selection, BLA, DAT, gateway, multicast, send, and TT modules. UAPI dependencies are `batadv_packet.h` and `batman_adv.h`. It integrates with ethtool, VLAN core callbacks, netdevice lower/upper adjacency, lockdep classes for stacked devices, and standard skb helpers.

## Risks
High-risk paths are skb headroom changes and skb reallocations, especially because helper calls may invalidate cached header pointers. TX classification combines BLA, DAT, gateway, TT, multicast, VLAN, AP isolation, and DHCP rules, so ordering regressions can produce loops, duplicate delivery, or dropped discovery traffic. VLAN refcounting mixes lookups under RCU with list mutation under spinlocks. `batadv_meshif_is_valid()` identifies devices by `ndo_start_xmit`, so accidental operation reuse would be significant.

## Test Signals
Useful signals include creating/deleting `batadv` rtnl devices with and without algorithm attributes, enslaving/detaching hard interfaces, MTU boundary tests against lower-interface limits, MAC-address change TT updates, VLAN add/kill for VID 0 and tagged VIDs, TX of unicast/broadcast/multicast/DHCP/ARP/STP/ECTP frames, RX nested batman-frame drops, AP-isolation mark/drop behavior, ethtool counter names/counts, and RCU/refcount leak checks on device teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/mesh-interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/mesh-interface.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/mesh-interface.h

## Purpose
Declares the mesh-interface API used by batman-adv subsystems to manipulate the virtual mesh netdevice, skb header space, local RX injection, and per-mesh VLAN records.

## APIs, Types, and Functions
Exports `batadv_skb_head_push()`, `batadv_interface_rx()`, `batadv_meshif_is_valid()`, `batadv_link_ops`, `batadv_meshif_create_vlan()`, `batadv_meshif_vlan_release()`, `batadv_meshif_vlan_get()`, and inline `batadv_meshif_vlan_put()`. The inline helper handles NULL safely and releases objects through `kref_put()`.

## Control Flow
The header has no standalone runtime flow. Callers request VLAN objects with `batadv_meshif_vlan_get()`, hold the returned reference while reading or updating VLAN-local state, and release it with `batadv_meshif_vlan_put()`. Rtnetlink registration code consumes `batadv_link_ops`, and data paths use `batadv_skb_head_push()` before adding batman-adv headers and `batadv_interface_rx()` to hand decapsulated Ethernet frames to the local stack.

## State and Persistence
The header defines no storage. It exposes kref-managed `struct batadv_meshif_vlan` lifetime and the singleton rtnl link ops object implemented in `mesh-interface.c`.

## Dependencies and Integration
Depends on `main.h`, `linux/kref.h`, `linux/netdevice.h`, `linux/skbuff.h`, and kernel integer types. It is included by netlink, send/receive, VLAN, and mesh setup code that need the virtual-interface boundary.

## Risks
The main risk is reference discipline: every successful VLAN get must be paired with put, and release callbacks must not be invoked directly except through kref paths. Since the header exposes `batadv_link_ops`, rtnl users depend on its ABI shape and kind string from the C file.

## Test Signals
Compile coverage should verify declarations match C definitions under all config combinations. Runtime checks should include VLAN lookup/create/release paths, netlink creation using `batadv_link_ops`, and NULL-safe `batadv_meshif_vlan_put()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/mesh-interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/multicast.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/multicast.c

## Purpose
Implements multicast optimization policy for batman-adv. It discovers local and bridged multicast listeners, advertises multicast capability and interest via TVLV and TT, chooses the best forwarding mode for outgoing multicast frames, sends unicast fanout when selected, tracks remote originator multicast flags, and exposes multicast state through netlink.

## APIs, Types, and Functions
Public entry points are `batadv_mcast_forw_mode()`, `batadv_mcast_forw_send()`, `batadv_mcast_init()`, `batadv_mcast_mesh_info_put()`, `batadv_mcast_flags_dump()`, `batadv_mcast_free()`, and `batadv_mcast_purge_orig()`. Important internal groups include MLA worker helpers (`batadv_mcast_mla_flags_get()`, `batadv_mcast_mla_meshif_get*()`, `batadv_mcast_mla_bridge_get()`, `batadv_mcast_mla_tt_retract()`, `batadv_mcast_mla_tt_add()`), packet eligibility helpers (`batadv_mcast_forw_mode_check*()`), unicast fanout helpers for TT/want-all/router lists, and TVLV handlers (`batadv_mcast_tvlv_ogm_handler()`, `batadv_mcast_tvlv_flags_get()`).

## Control Flow
`batadv_mcast_init()` registers multicast TVLV handlers and starts a delayed worker every `BATADV_MCAST_WORK_PERIOD`. The worker computes local flags from bridge presence, bridge queriers, multicast router presence, lower-interface MTUs, and multicast packet-type capability. It then collects IPv4/IPv6 listener MACs from the mesh/upper bridge and bridge snooping tables, filters entries made redundant by want-all flags or router presence, updates the local TT multicast listener announcements, and refreshes the multicast TVLV container.

On egress, `batadv_mcast_forw_mode()` first rejects disabled optimization, IGMP/MLD reports, unsupported protocols, invalid IPv6 scopes, and allocation failures. It counts TT listeners plus remote originators that want all IPv4/IPv6, all unsnoopable traffic, or routable traffic through multicast routers. No recipients yields `BATADV_FORW_NONE`; unsnoopable recipients force broadcast; otherwise it selects batman-adv multicast packets when all nodes support the packet type and the packet fits in the IPv6 minimum MTU, falls back to unicast fanout if the recipient count is within `multicast_fanout`, and broadcasts beyond that.

`batadv_mcast_forw_send()` implements the unicast-fanout mode by copying the skb for TT listeners, want-all lists, and router lists. Each copy goes to `batadv_send_skb_unicast()` unless BLA identifies the destination originator as a shared backbone gateway. The original skb is consumed or freed depending on success. Incoming multicast TVLVs update per-originator capability bits, mcast flags, global counters, and RCU want-all lists under `orig->mcast_handler_lock`.

## State and Persistence
Per-mesh state is in `bat_priv->mcast`: local MLA list, current `mla_flags`, delayed work, want-all/want-router originator lists, counters for each list, counter of nodes without multicast packet capability, `mla_lock`, and `want_lists_lock`. Per-originator state includes `orig->mcast_flags`, capability bits, and hlist nodes for each multicast interest list. Local listener announcements persist as TT entries until the next worker reconciliation or `batadv_mcast_free()`.

## Dependencies and Integration
Depends on Linux bridge multicast snooping APIs, IPv4/IPv6 multicast and router state, netdevice upper/lower relations, TVLV container/handler infrastructure, TT local/global tables, BLA, generic netlink, originator hash dumps, and send helpers. `multicast_forw.c` supplies batman-adv multicast packet encapsulation and tracker TVLV processing.

## Risks
Multicast correctness depends on subtle combinations of IGMP/MLD snooping, bridge querier shadowing, router flags, and local-vs-bridged listener discovery. Counter/list updates must stay paired or forwarding mode decisions will under- or over-deliver. Unsupported or absent multicast TVLVs intentionally map to broad want-all behavior for compatibility, increasing traffic. skb parser helpers can reallocate or linearize data, so cached headers must be refreshed. Allocation failures in listener collection can skip updates and leave previous TT/TVLV state active until the next worker run.

## Test Signals
Strong tests include multicast disabled/force-flood mode, IPv4 and IPv6 listener joins/leaves on mesh and bridge, bridge querier present/absent/shadowing cases, multicast router presence, link-local unsnoopable traffic, routable multicast with and without router receivers, fanout threshold changes, BLA gateway suppression, TVLV absent/present/malformed values, netlink multicast flag dumps, worker cancellation on teardown, and packet capture proving broadcast, unicast fanout, and batman-adv multicast packet modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/multicast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/multicast.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/multicast.h

## Purpose
Declares the multicast optimization interface and config-gated fallback behavior for builds without `CONFIG_BATMAN_ADV_MCAST`.

## APIs, Types, and Functions
Defines `enum batadv_forw_mode` with `BATADV_FORW_BCAST`, `BATADV_FORW_UCASTS`, `BATADV_FORW_MCAST`, and `BATADV_FORW_NONE`. When multicast is enabled it declares forwarding decision/send functions, lifecycle functions, netlink dump helpers, purge hooks, multicast tracker TVLV handling, packet header length calculation, header push, and multicast send. When disabled it provides inline stubs that force broadcast decisions, drop multicast send attempts, return no mesh info, and report unsupported dumps.

## Control Flow
Enabled builds route mesh TX through `batadv_mcast_forw_mode()` and then either `batadv_mcast_forw_send()` or `batadv_mcast_forw_mcsend()`. Disabled builds compile the same callers but make multicast optimization a no-op: mode selection returns broadcast, explicit send helpers free the skb and return drop, and lifecycle hooks do nothing.

## State and Persistence
The header owns no storage. It controls whether per-mesh multicast state and per-originator multicast list membership from the C files are reachable in a given build.

## Dependencies and Integration
Depends on `main.h`, netlink callback types, skb types, and integer types. It is included by `mesh-interface.c`, multicast implementation files, originator purge/free paths, and netlink mesh-info reporting.

## Risks
Stub semantics must match caller ownership expectations. In particular, disabled-build send stubs consume/free skbs, while `batadv_mcast_forw_mode()` forces broadcast so normal paths should rarely call them. Adding new multicast APIs requires matching stubs or non-mcast builds will fail.

## Test Signals
Build both `CONFIG_BATMAN_ADV_MCAST=y` and disabled configurations. Runtime disabled-build checks should show mesh operation still broadcasts multicast traffic, netlink multicast flag dumps return `-EOPNOTSUPP`, and no multicast worker or TVLV state is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/multicast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/multicast_forw.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/multicast_forw.c

## Purpose
Implements the batman-adv multicast packet forwarding format. It constructs multicast packets with a tracker TVLV listing destination originators, forwards incoming or locally generated packets per next-hop neighbor, removes destinations already assigned to other copies, and shrinks tracker headers to avoid redundant retransmission.

## APIs, Types, and Functions
Public symbols are `batadv_mcast_forw_tracker_tvlv_handler()`, `batadv_mcast_forw_packet_hdrlen()`, `batadv_mcast_forw_push()`, and `batadv_mcast_forw_mcsend()`. Important internal helpers push padding, destination MACs, TT recipients, want-all recipients, router recipients, tracker TVLV headers, and the outer `struct batadv_mcast_packet`. Forwarding helpers include `batadv_mcast_forw_packet()`, `batadv_mcast_forw_scrub_dests()`, `batadv_mcast_forw_shrink_tracker()`, and the shrink/pack/header-update routines.

## Control Flow
Local encapsulation starts in `batadv_mcast_forw_push()`: it expands skb headroom to fit an IPv6-minimum-MTU multicast packet, remembers the transport header, pushes destination originator MACs from TT and want lists, adjusts two-byte TVLV padding depending on the actual destination count, pushes the multicast tracker TVLV header, and finally pushes the batman-adv multicast packet header. `batadv_mcast_forw_mcsend()` then calls the common forwarding engine with `local_xmit=true`.

`batadv_mcast_forw_packet()` validates the tracker TVLV length, marks the checksum invalid, iterates destination originator addresses, drops zero/multicast invalid entries, records local receive when the destination is one of this node's MACs, resolves each remaining originator to its next-hop neighbor, copies the skb for that neighbor, scrubs the copy so it only contains destinations reachable through that next hop, scrubs the original to prevent duplicate sends, shrinks the copy's tracker TVLV, and sends it via `batadv_send_unicast_skb()`. It returns `NET_RX_SUCCESS` only if the local mesh interface should also receive the decapsulated payload.

## State and Persistence
This file mostly mutates transient skbs. Persistent state is read from TT global entries, multicast want lists in `bat_priv->mcast`, originator routing state, BLA gateway state, and per-mesh counters. It updates multicast TX, local TX, forwarding, and byte counters. No long-lived objects are allocated here besides skb copies.

## Dependencies and Integration
Depends on packet UAPI structures from `batadv_packet.h`, multicast policy from `multicast.c`, originator route lookup, TT global tables, BLA filtering, send helpers, skb headroom/linearization helpers, and Ethernet/VLAN/IP constants. Incoming multicast packets reach this file through the TVLV handler registered by `multicast.c`.

## Risks
The tracker TVLV is variable-length and alignment-sensitive; wrong padding or header-length updates can corrupt the packet. The code assumes the tracker TVLV is linearized and that `skb_network_header()` points at `struct batadv_tvlv_mcast_tracker`. Destination counts can diverge from earlier estimates because BLA suppression and concurrent list changes remove entries. Failure paths must preserve skb ownership and avoid leaving partially pushed headers on success callers. Next-hop grouping by neighbor is routing-state sensitive and may drop stale or unresolved originators.

## Test Signals
Tests should cover header length for odd/even destination counts, padding add/remove after actual destination count changes, U16 destination-count bounds, malformed tracker lengths, zero and multicast destination entries, local receive plus forwarding in the same packet, multiple destinations behind one next hop, destinations behind different next hops, route-missing drops, BLA gateway suppression, MTU/headroom expansion failure, and packet capture confirming shrunk tracker TVLVs on forwarded copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/multicast_forw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/netlink.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/netlink.c

## Purpose
Implements the batman-adv generic netlink family. It defines attribute policy, command dispatch, object lookup and lifetime handling, mesh/hard-interface/VLAN get-set operations, dump command routing, multicast notifications, and throughput-meter control/result messages.

## APIs, Types, and Functions
Public symbols are `batadv_netlink_family`, `batadv_netlink_get_meshif()`, `batadv_netlink_get_hardif()`, `batadv_netlink_tpmeter_notify()`, `batadv_netlink_register()`, and `batadv_netlink_unregister()`. Internal command handlers include mesh fill/get/set/notify helpers, hard-interface fill/get/set/dump/notify helpers, VLAN fill/get/set/notify helpers, throughput-meter start/cancel/result helpers, object lookup helpers, and `batadv_pre_doit()`/`batadv_post_doit()`.

## Control Flow
Incoming doit commands pass through `batadv_pre_doit()`, which validates internal flag combinations, resolves and pins the requested mesh interface, hard interface, or mesh VLAN from netlink attributes, and stores pointers in `info->user_ptr`. Command handlers then read or mutate atomic mesh settings, gateway state, BLA/DAT status, fragmentation MTU recalculation, multicast force-flood/fanout, hard-interface hop penalty and BATMAN_V settings, VLAN AP isolation, or throughput-meter sessions. `batadv_post_doit()` releases all pinned objects.

Dump commands are registered in `batadv_netlink_ops` and delegated to subsystem dump functions for algorithms, TT, originators, hard-if neighbors, gateways, BLA, DAT, and multicast flags. Mesh/hardif/VLAN changes build config messages and multicast them on `BATADV_NL_MCAST_GROUP_CONFIG`; throughput-meter completion multicasts on `BATADV_NL_MCAST_GROUP_TPMETER`.

## State and Persistence
The file owns the global `struct genl_family` definition and multicast group table. Configuration mutations persist in `struct batadv_priv`, `struct batadv_hard_iface`, or `struct batadv_meshif_vlan` atomics/fields for the lifetime of those objects. Netlink messages are transient skbs. References to mesh netdevices, hard interfaces, and VLANs are explicitly acquired and released around command handling.

## Dependencies and Integration
Depends on generic netlink, network namespaces, rtnl locking for lower-device dumps, UAPI `batman_adv.h`, and most batman-adv subsystems: algorithms, BLA, DAT, gateways, hard interfaces, mesh interface validation, multicast, originator, throughput meter, and TT. It is the main control-plane bridge to userspace tools such as `batctl`.

## Risks
Attribute validation is intentionally non-strict for compatibility, so handlers must defend against missing attributes and invalid ranges. Some setters silently ignore out-of-range values rather than returning errors. Object lifetime is split between netdevice refs, batman hardif krefs, and mesh VLAN krefs; pre/post flag mismatches can leak or use wrong `user_ptr` slots. Config notifications allocate GFP_KERNEL skbs and may fail after state has already changed. Dump consistency depends on generation counters in subsystem hashes.

## Test Signals
Netlink tests should cover get/set mesh fields, gateway mode and selection-class bounds, fragmentation MTU update, BLA/DAT status updates, multicast force-flood/fanout, origin interval clamping, hardif and VLAN get/set, invalid mesh/hardif/VLAN ifindexes, unprivileged allowed getters versus admin-only setters, dump callbacks with and without optional hardif attributes, throughput-meter start/cancel/notify cookies, and multicast group notifications in non-initial network namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/netlink.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/netlink.h

## Purpose
Declares the batman-adv generic netlink integration points used by module setup, subsystem dump callbacks, and throughput-meter reporting.

## APIs, Types, and Functions
Exports `batadv_netlink_register()`, `batadv_netlink_unregister()`, `batadv_netlink_get_meshif()`, `batadv_netlink_get_hardif()`, `batadv_netlink_tpmeter_notify()`, and `batadv_netlink_family`.

## Control Flow
The header itself has no executable flow. Module init registers the family; exit unregisters it. Dump callbacks use the callback-based mesh/hardif lookup helpers to resolve request attributes and must release returned references. Throughput-meter code calls `batadv_netlink_tpmeter_notify()` when sessions finish.

## State and Persistence
No storage is defined here except the external family object implemented in `netlink.c`. Returned mesh and hardif objects carry increased references whose lifetime must be handled by callers.

## Dependencies and Integration
Depends on `main.h`, netlink callback types, and integer types. It is included by multicast, originator, throughput-meter, and other dump-capable subsystems that need the family object for `genlmsg_put()` or lookup helpers.

## Risks
The lookup helpers encode ownership contracts that are easy to misuse: successful mesh lookups require `dev_put()`, and successful hardif lookups require `batadv_hardif_put()`. The exported family object couples all subsystem dumps to the command IDs and policy in `netlink.c`.

## Test Signals
Compile coverage should verify all subsystem dumps include the header cleanly. Runtime signals include correct reference release in dump paths, successful family registration/unregistration, and throughput-meter notifications delivered with the exported family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/originator.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/originator.c

## Purpose
Owns originator and neighbor state for batman-adv routing. It allocates the originator hash table, creates and looks up originator, neighbor, hard-interface-neighbor, VLAN, and per-interface info objects, exposes route/neighbor lookup helpers, purges stale topology state, and delegates originator/neighbor netlink dumps to the selected routing algorithm.

## APIs, Types, and Functions
Public entry points include `batadv_orig_hash_find()`, `batadv_compare_orig()`, `batadv_orig_node_vlan_get/new/release()`, `batadv_originator_init/free()`, `batadv_hardif_neigh_get()`, `batadv_neigh_node_get_or_create()`, `batadv_neigh_ifinfo_get/new/release()`, `batadv_orig_ifinfo_get/new/release()`, `batadv_orig_router_get()`, `batadv_orig_to_router()`, `batadv_hardif_neigh_dump()`, `batadv_orig_node_new/release()`, `batadv_purge_orig_ref()`, and `batadv_orig_dump()`.

## Control Flow
`batadv_originator_init()` creates a 1024-bucket hash table, assigns lockdep classing, and starts the periodic purge worker. New originator-related objects follow a get-or-create pattern: first look up under RCU without expensive locking, then lock the relevant list, recheck, allocate with `GFP_ATOMIC`, initialize krefs/list nodes/locks/timestamps, take references to hard interfaces or hardif-neighbor objects, and add to RCU hlist.

Routing lookup starts from `batadv_orig_hash_find()` by originator MAC, then `batadv_orig_to_router()` calls the algorithm's router selection through `batadv_find_router()`. `batadv_orig_router_get()` directly reads an `orig_ifinfo->router` RCU pointer for a specific outgoing interface. Netlink originator and neighbor dumps validate mesh and primary interface state, optionally resolve a hardif filter, then call `algo_ops->orig.dump` or `algo_ops->neigh.dump`.

The purge worker calls `batadv_purge_orig_ref()` periodically. It scans the hash table under bucket locks, removes originators timed out for twice the purge timeout, deletes gateway and TT global state for them, purges fragment queues, removes stale neighbor/per-interface info for down or removed hard interfaces, recomputes best neighbors for default and active outgoing interfaces, updates routes, and finally triggers gateway election.

## State and Persistence
Persistent state is the RCU-protected `bat_priv->orig_hash` and each `struct batadv_orig_node` subtree: neighbor list, VLAN list, orig-ifinfo list, TT buffer, broadcast sequence state, fragment queues, multicast flags/list nodes, last-seen timestamps, route candidates, and per-algorithm private state initialized through algorithm hooks. Objects are kref-managed and mostly RCU-freed. The delayed purge work persists until `batadv_originator_free()` cancels it and tears down all buckets.

## Dependencies and Integration
Depends on hash helpers, routing algorithm ops, hard-interface lifetime, routing updates, gateways, TT, DAT, fragmentation, multicast purge hooks, netlink lookup helpers, workqueues, RCU, krefs, and jiffies timeout helpers. It is a central integration point for BATMAN_IV/BATMAN_V algorithm-specific metrics while keeping generic object lifetime and purge behavior common.

## Risks
This file has dense lifetime rules: hash buckets, nested hlists, RCU readers, krefs, hardif refs, and delayed free callbacks all interact. Purge removes objects while algorithms may be reading route state, so route pointers and last bonding candidates must be cleared with matching puts. Timeout thresholds influence route stability and stale forwarding. `batadv_orig_hash_find()` uses `batadv_compare_eth(orig_node, data)`, relying on the originator MAC being the first field in `struct batadv_orig_node`. Multicast purge runs from the RCU free callback, so it must tolerate originator teardown ordering.

## Test Signals
Coverage should include creating originators, duplicate get-or-create races, VLAN VID validation, neighbor creation on multiple hard interfaces, ifinfo creation for default and concrete outgoing interfaces, route lookup before/after router updates, originator and neighbor netlink dumps with and without hardif filters, purging stale neighbors due to timeout and interface status, full originator timeout cleanup including TT/gateway deletion, fragment purge, gateway election after purge, and RCU/kref leak detection on mesh teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/originator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/originator.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/originator.h

## Purpose
Declares originator, neighbor, hard-interface-neighbor, VLAN, and per-interface info APIs plus small hash/refcount helpers used across batman-adv routing, forwarding, purge, and netlink code.

## APIs, Types, and Functions
Exports lifecycle and lookup functions for originator hash initialization/free/purge, originator nodes, hardif neighbors, neighbor nodes, neighbor ifinfo, originator ifinfo, originator VLANs, route lookup, and netlink dumps. Inline helpers include `batadv_choose_orig()` using `jhash()` over `ETH_ALEN`, and NULL-safe kref put wrappers for originator VLANs, neighbor ifinfo, hardif neighbors, neighbor nodes, originator ifinfo, and originator nodes.

## Control Flow
The header does not execute code beyond inlines. Callers hash originator MACs with `batadv_choose_orig()`, acquire objects with get/new helpers, use returned references while traversing route or neighbor state, and release them with the matching inline put helper. Dump code calls `batadv_orig_dump()` or `batadv_hardif_neigh_dump()` through netlink command registration.

## State and Persistence
No storage is owned by the header. It exposes lifetime contracts for kref-managed objects stored in the originator hash and nested RCU lists. The hash function defines bucket placement for persistent `bat_priv->orig_hash` entries.

## Dependencies and Integration
Depends on `main.h`, compiler attributes, Ethernet constants, `jhash`, kref, netlink, skb, and integer types. Included by multicast forwarding, routing algorithms, TT/gateway code, and originator netlink dump paths.

## Risks
The inlines hide reference ownership; missed puts or extra puts can leak or prematurely free RCU-managed topology objects. Hash behavior must remain stable with the compare function and table size. Callers must distinguish `BATADV_IF_DEFAULT` from real hard interfaces when using ifinfo helpers because release paths only drop hardif refs for concrete interfaces.

## Test Signals
Compile coverage should exercise all config combinations that include routing algorithms and multicast. Runtime checks should pair each get/new helper with put helpers, verify originator hash lookup by MAC, validate netlink dump entry points, and use refcount/RCU debug options to catch lifetime mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/originator.h -->
