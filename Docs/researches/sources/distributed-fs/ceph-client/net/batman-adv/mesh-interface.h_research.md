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
