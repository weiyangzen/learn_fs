# sources/distributed-fs/ceph-client/include/uapi/linux/ipv6_route.h

## Purpose
`ipv6_route.h` defines IPv6 route flags, route-message layout, route notifications, and route-priority constants.

## Important APIs, Types, and Functions
Route flags include default, on-link, addrconf, prefix route, anycast, non-nexthop, expires, routeinfo, cache, flow, policy, per-CPU, and local. `RTF_PREF(pref)` encodes route preference in high bits. `struct in6_rtmsg` carries destination/source/gateway addresses, type, prefix lengths, metric, info, flags, and interface index. Notification constants include new/delete device and route events.

## Control Flow
Route tools and compatibility APIs pass `in6_rtmsg` to add, remove, or inspect IPv6 routes. The kernel stores routes and emits notifications when route or device state changes.

## State and Persistence
Routes persist in kernel fib state until deleted, expired, or namespace teardown. Some flags are read-only from userspace and reflect kernel-derived route state.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<linux/in6.h>`. Integration points include IPv6 FIB, route sockets/ioctls, rtnetlink compatibility, router advertisements, and policy routing.

## Risks and Test Signals
Tests should check user-settable versus read-only flags, preference-bit packing, ifindex validation, prefix-length validation, expiration behavior, and compatibility of `in6_rtmsg` layout.
