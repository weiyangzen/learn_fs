# sources/distributed-fs/ceph-client/drivers/net/mhi_net.c

## Purpose
This file implements a raw-IP network driver over MHI channels. It creates a point-to-point `net_device` for modem data channels, queues SKBs to the MHI uplink and downlink rings, refills RX buffers asynchronously, classifies received packets as IPv4, IPv6, or MAP, and maintains per-device 64-bit network statistics.

## Important APIs, Types, and Functions
`struct mhi_net_dev` is the private netdev state: it stores the `mhi_device`, netdev, RX aggregation pointers, delayed refill work, stats, RX queue size, optional MRU, and message flag field. `struct mhi_net_stats` uses `u64_stats_t` and syncp fields for lockless stats reads. Netdev operations are `mhi_ndo_open()`, `mhi_ndo_stop()`, `mhi_ndo_xmit()`, and `mhi_ndo_get_stats64()`. MHI callbacks are `mhi_net_dl_callback()` and `mhi_net_ul_callback()`. Lifecycle functions are `mhi_net_probe()`, `mhi_net_newlink()`, `mhi_net_dellink()`, and `mhi_net_remove()`.

## Control Flow
Probe allocates a raw-IP netdev using the matched channel-specific name, attaches it to the MHI device, and calls `mhi_net_newlink()`. Newlink initializes private state, starts MHI transfer channels with `mhi_prepare_for_transfer()`, records RX queue depth, and registers the netdev. Opening the netdev schedules immediate RX refill, marks carrier on because link state is managed out of band, and starts TX queues. TX queues the skb to MHI with `mhi_queue_skb()` and stops the queue if the MHI TX ring becomes full. TX completion frees the skb, updates stats, and wakes the netdev queue if descriptors are available. RX completion handles MHI errors, aggregates `-EOVERFLOW` fragments through `frag_list`, classifies successful frames by first nibble, accounts bytes/packets, hands packets to `__netif_rx()`, and schedules refill when descriptors fall below half full.

## State and Persistence
The driver maintains only runtime state. Aggregated RX fragments are held in `skbagg_head` and `skbagg_tail` until the final successful transfer completes; stale aggregation is freed during dellink. RX refill work persists while the netdev is open and is canceled on stop. Stats are kept in private memory and exposed through `ndo_get_stats64()`. MHI transfer preparation persists between newlink and dellink.

## Dependencies and Integration Points
The file depends on MHI core APIs, Linux netdev core, SKB allocation/classification, raw-IP ARP type definitions, and u64 stats helpers. It binds to MHI channels `IP_HW0` and `IP_SW0`, using predictable names `mhi_hwip%d` and `mhi_swip%d`. Higher-level modem control such as QMI establishes carrier semantics outside this driver.

## Risks and Edge Cases
RX aggregation assumes `-EOVERFLOW` fragments will be followed by a successful final fragment; repeated errors can hold memory until teardown. RX classification reads `skb->data[0]` after `skb_put()` without an explicit zero-length guard, relying on MHI transfers to provide data. `mhi_net_newlink()` calls `mhi_prepare_for_transfer()` before `register_netdev()` but does not unprepare transfers if netdev registration fails. Refill work can reschedule itself when starved, so stop/remove correctness depends on `cancel_delayed_work_sync()` and transfer teardown ordering. MHI queue full handling relies on callbacks to wake queues.

## Test Signals
Useful tests include probe/remove for both channel names, open/stop cycles, TX ring full and wake behavior, RX refill starvation, normal IPv4/IPv6/MAP receive classification, fragmented receive aggregation, and MHI error statuses `-EOVERFLOW`, `-ENOTCONN`, and unknown errors. Stats should reflect packets, bytes, errors, and drops accurately under concurrent traffic.
