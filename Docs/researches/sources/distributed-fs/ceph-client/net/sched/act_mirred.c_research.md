# sources/distributed-fs/ceph-client/net/sched/act_mirred.c

## Purpose

`act_mirred.c` implements the tc `mirred` action: packet mirror or redirect to another netdevice or to all ports in a tc block. It supports egress and ingress targets and maps software actions to hardware offload `FLOW_ACTION_*` entries.

## Important APIs, types, and functions

The main action ops object is `act_mirred_ops`. `tcf_mirred_init()` parses `TCA_MIRRED_PARMS` and optional `TCA_MIRRED_BLOCKID`, validates egress/ingress mirror/redirect modes, allocates or replaces the action in the per-net IDR, and stores either an RCU-protected target `net_device` or a block id. `tcf_mirred_act()` is the hot path. `tcf_mirred_to_dev()` handles cloning, loop checks, MAC/network header positioning, netfilter conntrack reset, `skb_iif` updates, and forwarding through `dev_queue_xmit()`, `netif_rx()`, or `netif_receive_skb()`. `tcf_blockcast_*()` fan out to block ports. `mirred_device_event()` clears target devices on unregister. `tcf_mirred_offload_act_setup()` maps modes to redirect/mirror flow actions.

## Control flow

Configuration starts with IDR lookup/create, control-action validation, then either `dev_get_by_index()` plus `netdev_tracker_alloc()` or block-id storage. Runtime first updates lastuse and byte stats, checks the per-CPU mirred recursion limit, handles block fanout if configured, otherwise dereferences the target device. Redirects may consume the original skb when called from ingress and the return action permits reinsertion; mirrors clone instead. Header positioning is adjusted because ingress actions expect network-header data while some egress devices expect MAC-header data.

## State and persistence

Each action persists `tcfm_dev`, `tcfm_blockid`, `tcfm_eaction`, `tcfm_mac_header_xmit`, tc common counters, and list membership in the global `mirred_list`. Device lifetime is protected by RCU plus explicit netdev tracking and a notifier that nulls devices on `NETDEV_UNREGISTER`. Recursion state lives in `softnet_data.xmit` or `current->net_xmit` on PREEMPT_RT.

## Dependencies and integration points

It integrates with tc action IDR/per-net registration, tc blocks, netdevice lifecycle notifiers, qdisc transmit/receive helpers, conntrack reset, flow offload, and classifier control actions including goto chains.

## Risks and edge cases

High-risk areas are redirect loops, recursive mirred nesting, stale device references during unregister, block fanout excluding the source ifindex, and correct skb ownership when redirecting without clone. Header push/pull mistakes can corrupt packets or confuse target devices. Down devices, carrier loss, and missing block ports increment overlimit stats rather than always changing the configured control action.

## Test signals

Use tc selftests with egress/ingress mirror and redirect between veth pairs, including same-device loop attempts, blockcast fanout, target device unregister, down target devices, and hardware offload dumps. Packet counters, overlimit/drop qstats, `skb_iif`, conntrack clearing, and observed packet delivery on ingress versus egress are important signals.
