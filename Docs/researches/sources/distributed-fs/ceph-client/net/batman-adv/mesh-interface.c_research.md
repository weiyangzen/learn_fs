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
