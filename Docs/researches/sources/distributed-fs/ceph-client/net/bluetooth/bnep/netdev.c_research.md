# sources/distributed-fs/ceph-client/net/bluetooth/bnep/netdev.c

## Purpose
This file implements the virtual Ethernet net_device operations for BNEP PAN sessions.

## Important APIs, Types, And Functions
`bnep_net_setup()` initializes a BNEP net_device. Netdev operations include open/close, transmit, multicast-list update, MAC-address handling, timeout recovery, and validation. Optional helpers are `bnep_net_mc_filter()`, `bnep_net_proto_filter()`, and `bnep_net_eth_proto()`.

## Control Flow
Opening starts the netdev queue and closing stops it. TX optionally drops packets rejected by multicast or protocol filters, queues accepted skbs on the underlying Bluetooth socket write queue, wakes the BNEP session thread, and stops the netdev queue once `BNEP_TX_QUEUE_LEN` is reached. Multicast-list updates build and queue a BNEP filter control request based on promiscuous/allmulti/broadcast/multicast address state. TX timeout simply wakes the queue.

## State, Persistence, And Dependencies
Per-netdev state is `struct bnep_session` stored in netdev private data. Filter state is shared with `core.c`. The socket write queue buffers outbound Ethernet frames and locally generated control packets until `kbnepd` sends them. There is no persistent storage.

## Integration Points
`core.c` allocates the netdev and calls `bnep_net_setup()`. Linux networking calls these `net_device_ops`. The session thread in `core.c` consumes the sk_write_queue that TX and multicast filter updates populate.

## Risks
TX runs in contexts where L2CAP send is unsafe, so all direct send attempts must stay in the session thread. Queue pressure is managed by skb count, not byte size. Optional filters can silently drop traffic by design; default protocol filter ranges should match BNEP expectations. `bnep_net_set_mac_addr()` returns success without changing the address, so user attempts to set MAC may appear accepted but have no effect.

## Test Signals
Signals include queue stop/wake when write queue reaches threshold and drains, multicast filter control packets on address-list changes, protocol/multicast drops when options are enabled, no direct L2CAP send from hard-xmit context, and normal Ethernet traffic over the PAN netdev.
