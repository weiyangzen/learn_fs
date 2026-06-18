# sources/distributed-fs/ceph-client/net/tipc/bearer.c

## Purpose
This file implements TIPC bearer management. A bearer is the generic transport binding between TIPC and a media implementation such as Ethernet, InfiniBand, or UDP.

## Important APIs, Types, And Functions
The file maintains `media_info_array`, bearer lookup helpers, media lookup/printing, bearer name validation, enable/disable/reset paths, L2 media attach/detach/send/receive, device notifier handling, bearer transmit helpers, loopback tracing, and netlink dump/get/enable/disable/add/set APIs for bearers and media. Important functions include `tipc_enable_bearer()`, `bearer_disable()`, `tipc_enable_l2_media()`, `tipc_l2_send_msg()`, `tipc_bearer_xmit_skb()`, `tipc_bearer_xmit()`, `tipc_bearer_bc_xmit()`, `tipc_l2_rcv_msg()`, `tipc_l2_device_event()`, and the `tipc_nl_*` handlers.

## Control Flow
Netlink enable validates `media:interface` names, priority limits, duplicate names, maximum bearer count, and per-priority constraints. It allocates a bearer, lets media-specific code initialize it, creates discovery and monitoring state, marks it up, publishes it via RCU, and sends initial discovery. Disable clears up state, deletes links, disables media, deletes discovery/monitoring, removes the RCU pointer, and drops the reference. L2 media attaches a packet handler to a netdevice and stores the bearer in `dev->tipc_ptr`. Transmit paths look up the bearer under RCU, optionally encrypt, and invoke the media send callback. Device events reset, disable, or update the bearer on carrier, MTU, address, unregister, and rename changes.

## State And Persistence
Per-net bearer pointers live in `tipc_net.bearer_list`. Each bearer stores media pointer, MTU, addresses, discovery pointer, priority/window/tolerance/domain, up bit, packet handler, and refcount. State is in memory and controlled by RTNL plus RCU.

## Dependencies And Integration Points
Dependencies include TIPC core, link, discovery, monitor, broadcast, netlink, UDP media, tracepoints, optional crypto, netdevice notifier APIs, packet handlers, and generic netlink policies. It integrates with node/link creation, broadcast destination counts, and user-space `tipc` commands.

## Risks And Test Signals
Risks include RCU/refcount lifetime bugs, stale `dev->tipc_ptr`, MTU changes below TIPC minimum, media callback failures, discovery skb cleanup on partial enable, encryption skb consumption, and netlink validation gaps. The source snapshot has duplicated comment tokens in the transmit area in earlier reads, so a build should verify this copy. Test signals include enabling/disabling Ethernet and UDP bearers, link reset on carrier/MTU/address events, netlink dump/get/set/add paths, packet receive filtering, crypto-enabled transmit, loopback packet tracing, and namespace teardown with active bearers.
