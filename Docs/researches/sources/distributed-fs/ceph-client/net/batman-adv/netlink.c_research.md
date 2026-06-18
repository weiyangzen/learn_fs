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
