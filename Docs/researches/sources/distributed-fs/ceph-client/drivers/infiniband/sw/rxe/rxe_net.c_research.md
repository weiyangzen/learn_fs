# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_net.c

## Purpose

`rxe_net.c` is the RoCEv2 UDP/IP transport layer for RXE. It creates per-network-namespace UDP tunnel sockets, builds IPv4/IPv6 + UDP headers around RXE packets, routes them over the backing netdev, handles local loopback, receives UDP-encapsulated packets, and translates netdev events into RXE device/port actions.

## Important APIs, Types, and Functions

Key entry points are `rxe_prepare()`, `rxe_xmit_packet()`, `rxe_init_packet()`, `rxe_udp_encap_recv()`, `rxe_net_init()`, `rxe_net_add()`, `rxe_net_del()`, `rxe_net_exit()`, and `rxe_register_notifier()`. Route helpers, socket setup/release helpers, and header builders isolate kernel networking details.

## Control Flow

Requester/responder code allocates an skb with `rxe_init_packet()`, fills RXE headers, calls `rxe_prepare()` to resolve routes and prepend UDP/IP headers, then calls `rxe_xmit_packet()`. Transmit validates QP readiness, generates ICRC, and either sends through `ip_local_out()`/`ip6_local_out()` or loops back by reshaping the skb and calling `rxe_rcv()`. Receive starts in the UDP tunnel callback, locates the RXE device, linearizes the skb, records packet metadata, strips UDP, and dispatches to RXE receive validation.

## State and Persistence Behavior

Persistent state includes per-netns tunnel sockets, per-QP send sockets, route cache cookies, skb/QP/socket references, inflight skb counters, and port/device counters. Tunnel socket references are shared across RXE devices in a namespace and released when devices or namespaces go away.

## Dependencies and Integration Points

The file integrates Linux UDP tunnel, routing, IPv4/IPv6 output, VLAN, netdev notifier, RDMA GID/netdev APIs, RXE namespace storage, RXE packet helpers, and RDMA device registration. It sits between RXE protocol engines and the Linux network stack.

## Risks and Edge Cases

High-risk areas are route-cache refresh, netdev lifetime, loopback header surgery, VLAN real-device lookup, socket reference accounting, IPv6-disabled builds, and netdev unregister while QPs or tunnel sockets still exist. The code also intentionally reclassifies socket lockdep classes.

## Test Signals

Test RXE add/delete, IPv4/IPv6 traffic, VLAN devices, loopback sends, net namespace deletion, MTU/link/unregister notifications, route invalidation, module unload after traffic, and inflight skb backpressure under many QPs.
