# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpnet.c

## Purpose
`xpnet.c` implements the XPNET virtual Ethernet device layered on XPC. It presents `xp0` as an Ethernet-like interface where MAC destination bytes identify SGI UV partition IDs and packets are transferred either embedded in an XPC message or by remote DMA-style copy from a cacheline-aligned buffer.

## Important APIs, Types, and Functions
`struct xpnet_message` is the XPC payload describing version, magic, embedded bytes, source physical address, size, and cacheline lead/tail ignore counts. `struct xpnet_pending_msg` tracks an skb and outstanding asynchronous XPC notifications. Network callbacks are `xpnet_dev_open()`, `xpnet_dev_stop()`, `xpnet_dev_hard_start_xmit()`, and `xpnet_dev_tx_timeout()`. XPC integration flows through `xpnet_connection_activity()`, `xpnet_receive()`, `xpnet_send()`, and `xpnet_send_completed()`. Module setup/teardown is `xpnet_init()` and `xpnet_exit()`.

## Control Flow
Module init runs only on UV systems, allocates the broadcast partition bitmap and Ethernet netdev, sets a locally administered MAC containing `xp_partition_id`, disables multicast, and registers the device. Opening the interface calls `xpc_connect()` on `XPC_NET_CHANNEL`. XPC connection events add/remove partition IDs from the broadcast bitmap and update carrier state. Transmit builds an `xpnet_message`, chooses broadcast or a single destination from MAC bytes, increments the pending count for each `xpc_send_notify()`, and frees the skb after all completion callbacks run. Receive validates version/magic, allocates an aligned skb, either copies embedded payload bytes or calls `xp_remote_memcpy()`, then submits the skb with `netif_rx()` and ACKs through `xpc_received()`.

## State and Persistence
The persistent runtime state is the registered `net_device`, its stats, carrier state, the broadcast bitmap protected by `xpnet_broadcast_lock`, and per-transmit pending-message counters. No durable state exists; partition connectivity is rebuilt from XPC events after interface open.

## Dependencies and Integration Points
The driver depends on XPC/XPNET constants from `xp.h`, Linux networking core, Ethernet address helpers, UV detection, remote physical address helpers, and XPC notify/receive callbacks. It integrates directly with `xpc_connect()`, `xpc_send_notify()`, `xpc_received()`, and the network stack `net_device_ops`.

## Risks and Edge Cases
The receive path can leak or strand an skb if `xp_remote_memcpy()` fails after `skb_put()`, as the source comment notes it cannot simply free the skb. IPv6 multicast destination byte `0x33` is dropped outright, and Ethernet multicast is disabled. Transmit stats are incremented even when no destination partition accepts a unicast/broadcast send. Cacheline alignment fields are critical: incorrect lead/tail values would expose extra bytes or truncate data.

## Test Signals
Exercise interface open/close, XPC connection/disconnection carrier changes, partition-ID MAC addressing, broadcast delivery to multiple connected partitions, embedded small packets, large remote-copy packets, completion callback skb lifetime, remote copy failure handling, MTU bounds, and packet stats under no-destination traffic.
