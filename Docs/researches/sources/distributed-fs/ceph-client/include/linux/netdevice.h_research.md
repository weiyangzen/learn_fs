# sources/distributed-fs/ceph-client/include/linux/netdevice.h

## Purpose
`netdevice.h` is the central Linux networking device contract. It defines `struct net_device`, its driver callback table, queue/NAPI state, hardware address lists, packet type registration, device notifier data, statistics helpers, feature negotiation helpers, transmit/receive entry points, and link-state helpers. It is not Ceph-specific; in this tree it supplies the kernel networking ABI surface used by Ceph-client-adjacent code and dependencies.

## Important APIs, Types, and Functions
The key type is `struct net_device`, which aggregates identity, namespace membership, feature masks, MTU/header limits, per-queue arrays, RX/TX state, protocol private pointers, XDP and netfilter hook pointers, statistics, lifecycle state, refcount tracking, sysfs/device metadata, and optional offload subsystems. `struct net_device_ops` is the driver-facing operations table with callbacks for open/stop, transmit, queue selection, MTU/MAC changes, VLAN, SR-IOV, bridge/FDB/MDB, XDP, timestamping, tunnel, and offload behavior.

Other important types include `struct napi_struct`, `struct gro_node`, `struct netdev_queue`, `struct netdev_hw_addr_list`, `struct packet_type`, `struct packet_offload`, `struct softnet_data`, and notifier payload structs. Important helpers include `dev_queue_xmit()`, `dev_direct_xmit()`, `netdev_start_xmit()`, NAPI add/schedule/complete/delete wrappers, TX queue stop/start/wake helpers, BQL helpers, `netdev_priv()`, namespace helpers, refcount helpers, feature/GSO/GRO helpers, and device type predicates.

## Control Flow
The header describes core RX/TX flow. TX callers enter through `dev_queue_xmit()` or `dev_direct_xmit()`, select a queue, lock according to `lltx`, set `netdev_xmit.more`, call `ndo_start_xmit`, update queue timestamps, and account BQL/DQL state if accepted. Queue state helpers manipulate driver XOFF, stack XOFF, and frozen bits. RX flow is represented through NAPI scheduling, GRO delivery, receive entry points, and RX handlers that can consume, redirect, force exact delivery, or pass skbs.

Lifecycle flow is allocation, registration, open/close, notifier emission, namespace movement, unregister queuing, and `free_netdev`. Link-state helpers set bits in `dev->state` and trigger linkwatch. Address-list flows synchronize unicast, multicast, and device addresses to hardware callbacks.

## State and Persistence
All state is in-memory kernel state. Registered devices persist for their lifecycle in per-net namespace lists and indexes, but no durable storage is defined. The header documents locking expectations: hot-path fields are cacheline grouped; many writers require RTNL; selected fields use `dev->lock`; address lists use `addr_list_lock`; RCU protects NAPI deletion, protocol pointers, and netfilter hook pointers; per-CPU stats use u64 seqcount helpers.

## Dependencies and Integration Points
Dependencies include kernel atomic/refcount/RCU/list/rbtree/percpu/timer/workqueue primitives, skb, qdisc, net namespace, rtnetlink/uapi netdevice types, XDP/BPF, ethtool, DCB, VLAN, DSA, XFRM, TLS, MACsec, UDP tunnel offload, page pools, and netfilter ingress/egress. Integration points include driver `ndo_*` tables, protocol handlers, packet offloads, netdevice notifier chains, upper/lower device graph helpers, rtnetlink/sysfs/ethtool, checksum/GSO/GRO, and XDP/AF_XDP.

## Risks
Primary risks are synchronization and ownership errors: drivers returning `NETDEV_TX_BUSY` without stopping queues, mismatched BQL byte accounting, premature RCU frees, lockless MTU/feature access without `READ_ONCE`/locking, memory-barrier mistakes around queue stop/completion, refcount tracker leaks, and incorrect skb ownership on transmit/forward/drop paths. `struct net_device` is config- and version-sensitive, so layout assumptions are fragile.

## Test Signals
Compile across relevant configs, bring devices up/down, exercise multi-queue TX/RX, NAPI scheduling/deletion with lockdep and RCU debugging, forwarding with GSO/GRO, BQL watchdog and queue-stall paths, notifier sequencing, namespace moves, address-list sync/unsync, XDP attach/detach, and runtime warnings from debug/refcount tooling.
