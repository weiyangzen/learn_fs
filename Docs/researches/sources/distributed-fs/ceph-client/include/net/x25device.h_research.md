# sources/distributed-fs/ceph-client/include/net/x25device.h

## Purpose

`x25device.h` provides the link-layer type translation helper for X.25 netdevices. It prepares an incoming SKB as an X.25 host packet.

## Important APIs, types, and functions

The only helper is `x25_type_trans(struct sk_buff *skb, struct net_device *dev)`. It sets `skb->dev`, resets the MAC header, marks the packet as `PACKET_HOST`, and returns `ETH_P_X25`.

## Control flow

Device receive code calls `x25_type_trans()` before handing the skb to the network stack so the packet is classified as X.25 and associated with the receiving device.

## State and persistence behavior

The helper mutates transient SKB metadata only. It owns no persistent state.

## Dependencies and integration points

It depends on Ethernet, packet, X.25 if definitions, SKB, and netdevice types. It integrates with X.25 netdevice drivers and packet receive classification.

## Risks and test signals

Risks are small but include stale MAC header offsets, wrong packet type for non-host frames, or missing device assignment. Tests should verify receive classification, skb metadata after translation, and delivery to X.25 protocol handlers.
