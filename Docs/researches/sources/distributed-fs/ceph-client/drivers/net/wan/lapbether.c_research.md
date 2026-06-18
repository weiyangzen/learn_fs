# sources/distributed-fs/ceph-client/drivers/net/wan/lapbether.c

## Purpose
`lapbether.c` creates pseudo X.25/LAPB netdevices over Ethernet devices. It registers an `ETH_P_DEC` packet handler, creates `lapb%d` devices when Ethernet devices come up, and uses the kernel LAPB layer to encapsulate X.25-style pseudo-header traffic inside Ethernet frames with a two-byte length prefix.

## Important APIs, Types, And Functions
`struct lapbethdev` links an Ethernet device to its LAPB/X.25 netdevice and holds up-state, receive queue, and NAPI. Important functions are `lapbeth_rcv()`, `lapbeth_data_indication()`, `lapbeth_xmit()`, `lapbeth_data_transmit()`, `lapbeth_connected()`, `lapbeth_disconnected()`, `lapbeth_open()`, `lapbeth_close()`, `lapbeth_new_device()`, `lapbeth_free_device()`, and `lapbeth_device_event()`.

## Control Flow
Module init registers the DEC packet handler and a netdevice notifier. On `NETDEV_UP` for an Ethernet device, `lapbeth_new_device()` allocates a `lapb%d` netdevice, computes required headroom from the underlying Ethernet device, holds the Ethernet device, initializes NAPI and queues, registers the netdevice, and adds it to the RCU list. Incoming DEC frames are cloned if needed, length-checked for the two-byte prefix, mapped to the matching `lapbethdev`, and passed to `lapb_data_received()` while up. Upper transmit expects a one-byte X.25 pseudo-header; data calls `lapb_data_request()`, connect/disconnect call LAPB control APIs. LAPB's data-transmit callback prepends a two-byte length and Ethernet header and queues the frame to the underlying Ethernet device.

## State And Persistence
State is volatile. The global RCU list tracks active mappings. `up` is protected by `up_lock`, RX indications are queued to NAPI, and the Ethernet device reference is held until unregister. Cleanup unregisters notifiers/packet handler and removes all remaining pseudo devices under RTNL.

## Dependencies And Integration Points
The file depends on Ethernet netdevices in `init_net`, packet type hooks, netdevice notifiers, the LAPB module, X.25 type translation, NAPI, RCU list traversal, and `netdev_lock` semantics via `dev_is_ethdev()`.

## Risks
The DEC packet handler accepts broadcast-style encapsulated traffic on any managed Ethernet device in `init_net`, so deployment must account for link-layer exposure. `lapbeth_rcv()` increments underlying Ethernet stats based on the embedded length before trimming. Removal uses RCU list deletion plus netdevice unregister; ordering must preserve the held Ethernet reference. A malformed length can trim beyond pulled data only as allowed by skb helpers; pskb and trim behavior should be regression-tested.

## Test Signals
Test automatic pseudo-device creation/removal on Ethernet up/unregister, prevention of underlying type changes, open/close LAPB registration, connect/disconnect pseudo-header delivery, DEC frame receive with valid/short lengths, NAPI draining, and cleanup with multiple devices.
