# sources/distributed-fs/ceph-client/drivers/net/ifb.c

## Purpose
`ifb.c` implements the Intermediate Functional Block netdevice. IFB provides a redirect target for tc actions, allowing ingress traffic to be queued and shaped by egress qdisc machinery and allowing per-device qdisc/policy sharing.

## Important APIs, types, and functions
`struct ifb_q_private` is per-TX-queue state with receive/transmit skb queues, tasklet, queue index, and u64 stats. `struct ifb_dev_private` points to the per-queue array. Key functions are `ifb_xmit()`, `ifb_ri_tasklet()`, `ifb_stats64()`, ethtool stats helpers, `ifb_dev_init()`, `ifb_dev_free()`, `ifb_setup()`, and rtnl link registration via `ifb_link_ops`.

## Control flow
Module init registers the rtnl link kind and creates legacy `ifb%d` devices according to `numifbs`. `ifb_xmit()` accepts only redirected packets with a valid ingress interface index, updates RX queue stats, enqueues to the queue-private receive queue, possibly stops the TX queue, and schedules the tasklet. The tasklet moves queued packets to a transmit queue under netdev queue lock, clears redirect/classify/netfilter-egress loop markers, restores the original device from `skb_iif`, updates TX stats, and reinjects via `dev_queue_xmit()` or `netif_receive_skb()`.

## State and persistence
State is volatile per netdevice and per queue: skb queues, tasklet pending flag, stats, drops, and queue stopped state. Configuration persistence is handled externally by rtnetlink userspace, not by this driver.

## Dependencies and integration points
IFB integrates with netdevice core, rtnl link ops, ethtool stats, qdisc/tc redirect actions, netfilter egress skip markers, skb metadata, and network namespaces for original-device lookup.

## Risks and test signals
Risks include queue/tasklet races, redirect loops if skip flags regress, drops when original ifindex disappears, queue wake/stop threshold correctness, stats consistency under 32-bit readers, and behavior with ingress vs egress redirected skbs. Tests should cover `ip link add type ifb`, module legacy creation, tc mirred ingress shaping, multi-queue stats, queue limit backpressure, original device removal, netns isolation, close/open queue transitions, and ethtool stat names/values.
