<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mroute.h -->
# sources/distributed-fs/ceph-client/include/linux/mroute.h

## Purpose
`mroute.h` declares IPv4 multicast routing interfaces and IPv4-specific MFC cache entries built on top of `mroute_base.h`.

## Important APIs, Types, and Functions
It provides `ip_mroute_opt()`, `ip_mroute_setsockopt()`, `ip_mroute_getsockopt()`, `ipmr_ioctl()`, `ipmr_compat_ioctl()`, `ip_mr_init()`, `ipmr_rule_default()`, `ipmr_sk_ioctl()`, `VIFF_STATIC`, `struct mfc_cache_cmp_arg`, `struct mfc_cache`, and `ipmr_get_route()`. Disabled `CONFIG_IP_MROUTE` builds return `-ENOPROTOOPT`, `-ENOIOCTLCMD`, default success for init, and conservative rule behavior.

## Control Flow and State
Socket options and ioctls configure multicast routing tables and VIFs. IPv4 route cache entries embed common `struct mr_mfc` state first, then add IPv4 group/origin keys used by rhashtable comparisons. Route lookup fills `rtmsg` data for userspace queries.

## State and Persistence Behavior
State lives in per-network-namespace multicast route tables, VIFs, and MFC caches declared in the base header. Entries are runtime networking state and are removed on namespace/table teardown.

## Dependencies and Integration Points
It depends on IPv4 address types, PIM definitions, fib rules/notifiers, UAPI mroute constants, sockptr, and `mroute_base.h`. It integrates with raw sockets, routing daemons, netlink route dumps, and multicast forwarding.

## Risks
Disabled stubs must preserve caller expectations. The embedded common struct must remain first for casting. Wrong key comparison breaks multicast forwarding. Userspace ioctl buffers must match UAPI layouts.

## Test Signals
IPv4 multicast routing daemon tests, setsockopt/getsockopt/ioctl coverage, route dump queries, multi-table rules, disabled-config behavior, and forwarding counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mroute.h -->
