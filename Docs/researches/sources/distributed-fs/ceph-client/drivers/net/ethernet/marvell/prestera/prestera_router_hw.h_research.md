# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_router_hw.h

## Purpose
This header defines the Prestera router hardware object model and exports the router-hardware API used by the rest of the Prestera driver. It captures software keys, hardware IDs, reference relationships, route actions, and public lifecycle functions for virtual routers, RIFs, nexthop neighbors, nexthop groups, and FIB nodes.

## Important APIs, types, and functions
`struct prestera_vr` maps a kernel FIB table ID to a hardware VR ID and carries a `refcount_t`. `struct prestera_rif_entry` binds a Prestera interface key, VR pointer, MAC address, hardware RIF ID, and router-list node. `struct prestera_ip_addr` is a versioned IPv4/IPv6 union with `PRESTERA_IP_ADDR_PLEN()`. `struct prestera_nh_neigh_key` identifies a neighbor by IP address and RIF-cookie domain. `struct prestera_neigh_info` is the hardware-facing resolved-neighbor payload. `struct prestera_nh_neigh` links a neighbor to dependent nexthop groups. `struct prestera_nexthop_group` holds up to four neighbor keys and per-neighbor linkage. `struct prestera_fib_key`, `struct prestera_fib_info`, and `struct prestera_fib_node` describe route lookup keys and actions.

The exported functions cover object find/get/create/destroy/update operations plus `prestera_router_hw_init()` and `prestera_router_hw_fini()`.

## Control flow
The header shows the intended ownership graph: FIB nodes and RIF entries reference VRs; UC FIB nodes reference nexthop groups; nexthop groups reference nexthop neighbors through `prestera_nh_neigh_head`; neighbor updates can fan out to groups.

## State and persistence behavior
All structures are runtime-only kernel objects. Hardware persistence is represented by fields such as `hw_vr_id`, `hw_id`, and `grp_id`; these IDs are valid only while the driver has successfully programmed the corresponding ASIC resources. The key structs are value keys for list or hash lookup and must be fully canonicalized before use.

## Dependencies and integration points
The header depends on common Prestera definitions such as `struct prestera_switch` and `struct prestera_iface`, Linux list and refcount types, Ethernet address constants, and IP address types. It is the public boundary between router control-plane code and `prestera_router_hw.c`.

## Risks and edge cases
The header advertises IPv6 representation, but the C file's LPM programming path is IPv4-only. `prestera_nh_neigh_key.rif` is a raw cookie pointer; stale or nonunique cookies can collapse or split ARP/ND domains incorrectly. The fixed `PRESTERA_NHGR_SIZE_MAX` of four constrains ECMP width and must match hardware and higher-level assumptions.

## Test signals
Tests should validate key equality/canonicalization, table-ID VR sharing, max-width nexthop group keys, empty neighbor-key termination, IPv6 rejection or support behavior in callers, and ABI consistency between exported prototypes and users.
