<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mdb.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_mdb.c

Purpose: implements rtnetlink dump, notification, add, delete, flush, and get support for the bridge multicast database (MDB) and multicast router ports. It bridges user-visible `RTM_*MDB` messages to internal multicast snooping state, including host joins, per-port group membership, router-port timers, VLAN multicast snooping contexts, source-specific multicast, protocol tags, and switchdev notification.

Important APIs, types, and functions:

- Dump/fill APIs: `br_mdb_dump()`, `br_mdb_fill_info()`, `br_rports_size()`, `br_rports_fill_info()`, `__mdb_fill_info()`, and `__mdb_fill_srcs()`.
- Notification APIs: `br_mdb_notify()`, `br_mdb_flag_change_notify()`, and `br_rtr_notify()`.
- Mutation APIs: `br_mdb_add()`, `br_mdb_del()`, `br_mdb_del_bulk()`, and helpers for `(*,G)`, `(S,G)`, source-list replacement, and host joins.
- Query API: `br_mdb_get()`.
- Key internal structures include `struct net_bridge_mdb_entry`, `struct net_bridge_port_group`, `struct net_bridge_group_src`, `struct br_ip`, `struct br_mdb_config`, and `struct br_mdb_flush_desc`.

Core control flow:

- Router-port dump walks bridge or VLAN multicast contexts and emits per-port router attributes: ifindex, timer, router type, IPv4/IPv6 timers, and optional VID.
- MDB dump emits `RTM_GETMDB` replies with nested `MDBA_MDB`/`MDBA_MDB_ENTRY`/`MDBA_MDB_ENTRY_INFO` attributes. It handles host-joined entries, port groups, timers, flags, source address, routing protocol, source lists, and group mode depending on IGMP/MLD version.
- `br_mdb_add()` initializes a `br_mdb_config` from netlink attributes, validates bridge running state and multicast enablement, resolves the target port if not a host join, rejects invalid IP/L2/source combinations, expands VID 0 across VLAN memberships when VLAN filtering is enabled, and calls `__br_mdb_add()` under `multicast_lock`.
- `br_mdb_add_group()` chooses the correct bridge or VLAN multicast context, creates or finds the MDB group, handles bridge-host joins, and dispatches to `br_mdb_add_group_star_g()` for `(*,G)` or `br_mdb_add_group_sg()` for `(S,G)`.
- Source-specific multicast support creates source entries and also installs corresponding `(S,G)` forwarding entries. `(*,G)` EXCLUDE groups update related `(S,G)` entries so replication remains correct. Replacement marks existing sources for deletion, adds the requested set, then removes old marked sources.
- `br_mdb_del()` builds the same config, optionally expands across VLANs, and removes either a host join or a matching port group under `multicast_lock`.
- `br_mdb_del_bulk()` builds a flush descriptor from ifindex, VID, state and optional state mask, and `RTPROT`; it scans all MDB entries and removes matching host joins and port groups.
- `br_mdb_get()` parses a group, locks multicast state while sizing and filling the reply, and unicasts an `RTM_NEWMDB`-formatted response.

State and persistence behavior:

- MDB state is runtime multicast snooping state held in `br->mdb_list`, each MDB entry's host flag/timer, RCU-linked port groups, per-port source lists, router-port lists, and optional VLAN multicast contexts.
- `br->multicast_lock` serializes MDB mutation and size-then-fill get replies. RCU protects dump and packet-path readers, with lockdep annotations for multicast lock cases.
- Temporary entries use timers based on multicast membership intervals or group membership intervals. Permanent entries delete timers. Host leave can restart the group timer when no ports remain.
- Notifications to `RTNLGRP_MDB` and switchdev are the external observation path; switchdev notification can be suppressed for flag-only notifications.

Dependencies and integration points:

- Depends heavily on multicast core helpers in other bridge files: `br_multicast_new_group()`, `br_multicast_new_port_group()`, `br_multicast_del_pg()`, `br_multicast_host_join()`, `br_multicast_host_leave()`, `br_multicast_star_g_handle_mode()`, source-list helpers, router-port helpers, and multicast context selection.
- `br_forward.c` consumes MDB port groups for multicast replication. `br_input.c` resolves MDB entries on multicast ingress.
- Netlink policies validate MDB entry attributes, source attributes, group modes, state masks, and protocol tags. Switchdev receives MDB add/delete notifications for hardware programming.
- VLAN snooping integration requires a configured VID and enabled VLAN multicast context when `BROPT_MCAST_VLAN_SNOOPING_ENABLED` is set.

Risks and edge cases:

- Source-specific multicast is the most complex area. Failing to maintain the derived `(S,G)` forwarding entries for `(*,G)` source lists or EXCLUDE mode can produce multicast leaks or drops.
- Size-then-fill netlink replies must hold the multicast lock where entries can change; dumps tolerate RCU iteration but need correct continuation indexes.
- VID 0 expansion mutates `cfg.entry->vid` and `cfg.group.vid` while iterating VLANs. Errors can leave a partial set of VLAN entries.
- L2 MDB entries are only allowed as permanent entries; IP host joins cannot carry flags or source-specific groups.
- VLAN multicast snooping rejects non-VID entries and disabled VLAN contexts; callers must surface these extack messages cleanly.

Test signals:

- Test `bridge mdb add/del/show/get/flush` for IPv4, IPv6, and L2 groups; host joins and port joins; permanent and temporary entries; VLAN-specific and VID 0 expansion.
- Cover IGMPv3/MLDv2 source lists, INCLUDE/EXCLUDE mode, source replacement, duplicate sources, empty INCLUDE rejection, and invalid multicast source addresses.
- Verify router-port dumps and notifications for IPv4, IPv6, VLAN contexts, and timer values.
- Validate bulk flush by port, bridge host entry, VID, permanent state mask, and `RTPROT`.
- Observe `RTNLGRP_MDB` events and switchdev MDB notifications, and test packet replication through `br_multicast_flood()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mdb.c -->
