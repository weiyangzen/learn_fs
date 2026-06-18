# sources/distributed-fs/ceph-client/include/uapi/linux/mroute.h

## Purpose
Defines IPv4 multicast routing socket option/ioctl/netlink ABI compatible with historical mrouted/PIMd control planes.

## Important APIs, Types, And Functions
Exports `MRT_*` commands, `SIOCGETVIFCNT`, `SIOCGETSGCNT`, `SIOCGETRPF`, flush flags, `vifctl`, `mfcctl`, `sioc_sg_req`, `sioc_vif_req`, `igmpmsg`, IPMR netlink table/vif/cache-report attributes, and IGMP pseudo-message constants.

## Control Flow
A multicast routing daemon initializes mroute state, adds VIFs and multicast forwarding cache entries, receives cache-miss/control messages, queries counters, and eventually flushes or shuts down routing.

## State, Persistence, And Dependencies
State persists in kernel multicast routing tables, VIF entries, MFC entries, and counters. Depends on sockios, types, and IPv4 address definitions.

## Integration Points
Used by mrouted, PIM daemons, rtnetlink table dumps, and IPv4 multicast forwarding code.

## Risks
Compatibility typedefs (`vifbitmap_t`, `vifi_t`) and `MAXVIFS` are ABI constraints. Interface selection can be by address or ifindex depending on flags. Counter fields are `unsigned long`, creating ABI-width considerations.

## Test Signals
Test daemon init/done, VIF add/delete, MFC add/delete, cache miss messages, counter ioctls, flush flags, PIM register messages, and netlink dump attributes.
