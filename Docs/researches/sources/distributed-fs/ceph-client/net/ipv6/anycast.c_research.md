# sources/distributed-fs/ceph-client/net/ipv6/anycast.c

## Purpose
Provides IPv6 anycast address membership support for sockets and network devices. It lets privileged sockets join/drop anycast addresses, maintains per-device anycast lists, installs/removes associated IPv6 routes and solicited-node multicast memberships, exposes lookups for source/address validation, and optionally reports state through `/proc/net/anycast6`.

## Important APIs, Types, and Functions
The global hash table `inet6_acaddr_lst` indexes `struct ifacaddr6` objects by network namespace and anycast address. Socket-facing APIs include `ipv6_sock_ac_join()`, `ipv6_sock_ac_drop()`, `ipv6_sock_ac_close()`, and `__ipv6_sock_ac_close()`. Device APIs include `__ipv6_dev_ac_inc()`, `__ipv6_dev_ac_dec()`, `ipv6_ac_destroy_dev()`, `ipv6_chk_acast_addr()`, and `ipv6_chk_acast_addr_src()`. Procfs support uses `ac6_seq_ops`.

## Control Flow
Joining validates `CAP_NET_ADMIN`, rejects multicast addresses, resolves or chooses a device, checks host/router prefix rules, allocates a socket membership entry, and increments the device anycast object. Device increment either bumps `aca_users` or allocates a route-backed `ifacaddr6`, links it under `idev->lock`, publishes it into the RCU hash, inserts the route, joins solicited-node multicast, and sends RTNL notification. Drop/close paths unlink socket entries and decrement device usage; the last user removes hash membership, leaves solicited multicast, deletes the route, notifies RTNL, and frees via RCU.

## State and Persistence
State is in per-socket `np->ipv6_ac_list`, per-device `idev->ac_list`, the global RCU hash, refcounted `ifacaddr6` objects, and route references (`aca_rt`). It is runtime-only and scoped by network namespace/device lifetime.

## Dependencies and Integration Points
Depends on addrconf, IPv6 route allocation/deletion, netdevice reference tracking, RTNL multicast notifications, procfs seq files, RCU, and namespace hashing. Datagram send control uses `ipv6_chk_acast_addr_src()` to permit anycast source addresses.

## Risks and Test Signals
Risks include device lifetime races, mismatched socket/device refcounts, route insertion/deletion failures, host/router behavior differences, and RCU/hash cleanup leaks. Test signals include privileged/unprivileged join/drop, link-local and global anycast checks, device teardown cleanup, `/proc/net/anycast6` output, RTM_NEWANYCAST/RTM_DELANYCAST notifications, and `ipv6_anycast_cleanup()` empty-hash warnings.
