# sources/distributed-fs/ceph-client/net/phonet/pn_netlink.c

## Purpose
`pn_netlink.c` implements the rtnetlink control plane for Phonet addresses and routes. It handles RTM_NEWADDR/DELADDR/GETADDR and RTM_NEWROUTE/DELROUTE/GETROUTE for `PF_PHONET`, and emits multicast notifications when addresses or routes change.

## Important APIs, types, and functions
Address handling uses `addr_doit()`, `getaddr_dumpit()`, `fill_addr()`, `phonet_address_notify()`, and `ifa_phonet_policy`. Route handling uses `route_doit()`, `route_dumpit()`, `fill_route()`, `rtm_phonet_notify()`, and `rtm_phonet_policy`. `phonet_rtnl_msg_handlers[]` declares the rtnetlink handlers, and `phonet_netlink_register()` registers them with `rtnl_register_many()`.

## Control flow and state
Address add/delete requests require both `CAP_NET_ADMIN` and `CAP_SYS_ADMIN`, parse `IFA_LOCAL`, require the low two address bits to be zero, resolve the target device by ifindex under RCU, call `phonet_address_add()` or `phonet_address_del()`, and notify `RTNLGRP_PHONET_IFADDR` on success. Dumps walk each Phonet device and each set address bit using callback cursors for device and address position.

Route add/delete requests require the same capabilities, parse `RTA_DST` and `RTA_OIF`, require main-table unicast routes and aligned 6-bit destination addresses, resolve the output device, and call `phonet_route_add()` or `phonet_route_del()`. Successful delete waits for RCU and drops the route-held device reference. Dumps iterate all 64 route slots and emit route messages for populated entries.

## State and persistence behavior
This file does not own persistent state; it mutates address and route state in `pn_dev.c` and emits live netlink notifications. Dump cursors are stored in `netlink_callback->args` only for the duration of a dump.

## Dependencies and integration points
It integrates with rtnetlink, Phonet device/route helpers, netlink capability checks, netlink multicast groups `RTNLGRP_PHONET_IFADDR` and `RTNLGRP_PHONET_ROUTE`, and per-net socket namespace resolution through `sock_net(skb->sk)`.

## Risks and edge cases
Risks include capability policy regressions, address alignment validation, route delete reference handling, dump cursor correctness, and netlink message sizing. Because handlers use `RTNL_FLAG_DOIT_UNLOCKED`/`DUMP_UNLOCKED`, underlying helpers must provide their own locking and RCU protection.

## Test signals
Use `ip`/rtnetlink tests or custom netlink clients to add/delete/dump Phonet addresses and routes, verify notifications, reject unaligned addresses, reject wrong table/type, enforce capabilities, exercise partial dumps with small skb buffers, and run concurrent route/device unregister stress.
