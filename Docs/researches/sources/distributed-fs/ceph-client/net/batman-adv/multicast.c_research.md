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
