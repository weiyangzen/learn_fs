# sources/distributed-fs/ceph-client/include/linux/usb/usbnet.h

## Purpose
This header defines the shared USB networking core contract used by many USB Ethernet, RNDIS, CDC, WLAN, WWAN, and vendor minidrivers.

## Important APIs, types, and functions
Key types are `usbnet`, `driver_info`, `cdc_state`, `skb_state`, and `skb_data`. APIs include probe/suspend/resume/disconnect, control command helpers, CDC bind/status helpers, netdev operations, RX/TX queue control, power management, link settings, status URB control, and `usbnet_set_skb_tx_stats()`. Flags describe framing, naming, ARP, multi-packet, runtime PM, and link interrupt behavior.

## Control flow, state, and persistence
Minidrivers provide `driver_info` callbacks for bind, reset, stop, power, status, link reset, RX/TX fixups, recovery, indication, and multicast filtering. The core owns URBs, skb queues, work items, status interrupt URB, MII state, link state, and event bits. State is runtime network/USB state; no persistent storage is defined.

## Dependencies and integration points
It depends on USB, netdevice, skbuff, MII, workqueue, mutex, spinlock, and CDC descriptors. It integrates the USB driver model with netdev/ethtool, runtime PM, CDC Ethernet/RNDIS-like protocols, and minidriver framing.

## Risks and test signals
Risks include queue/work races during unplug, malformed framing in fixups, runtime PM misuse, multi-packet accounting errors, and deadlocks around interrupt/status URBs. Tests should cover probe/bind failure cleanup, suspend/resume, RX pause/resume, TX timeout, CDC descriptors, link changes, and unplug while work is pending.
