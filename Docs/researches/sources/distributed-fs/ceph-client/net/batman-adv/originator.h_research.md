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
