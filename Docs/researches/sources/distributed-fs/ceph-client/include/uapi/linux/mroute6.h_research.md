# sources/distributed-fs/ceph-client/include/uapi/linux/mroute6.h

## Purpose
Defines IPv6 multicast routing UAPI for MIF management, multicast forwarding cache, counters, kernel-to-daemon control messages, and cache-report netlink attributes.

## Important APIs, Types, And Functions
Exports `MRT6_*`, `SIOCGETMIFCNT_IN6`, `SIOCGETSGCNT_IN6`, flush flags, `mifi_t`, `if_set` and macros, `mif6ctl`, `mf6cctl`, `sioc_sg_req6`, `sioc_mif_req6`, `mrt6msg`, and `IP6MRA_CREPORT_*`.

## Control Flow
IPv6 multicast daemons initialize routing, add MIFs, install MFC entries, receive `mrt6msg` notifications on cache misses or whole-packet events, query counters, and flush or close state.

## State, Persistence, And Dependencies
State is kernel IPv6 multicast routing table, interface bitsets, and counters. Depends on const, types, sockios, and IPv6 sockaddr definitions.

## Integration Points
Used by PIM6/mrouted-style daemons, IPv6 raw socket control flows, and netlink cache-report consumers.

## Risks
The `if_set` macros use BSD `bcopy`/`bzero` names for userspace compatibility. `SIOCGETRPF` collides in name with IPv4 header. ABI width for `unsigned long` counters must be respected.

## Test Signals
Validate MIF add/delete, MFC entries, bitset operations, cache miss delivery, raw socket message format, counter ioctls, flush flags, and netlink cache reports.
