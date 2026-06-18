# sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb.h

Purpose: provides the shared internal contract for the Kvaser USB driver, covering common device/netdev state, protocol-operation callbacks, device configuration, capabilities, quirks, and helper declarations used by the core plus Leaf and Hydra subdrivers.

Important APIs/types/functions: `struct kvaser_usb` stores the USB device/interface, endpoint descriptors, RX anchors/buffers, per-channel netdev private pointers, driver info, card metadata, firmware/hardware identifiers, max outstanding TX count, and card-specific data. `struct kvaser_usb_net_priv` embeds `can_priv`, `devlink_port`, error counters, channel state, completions, TX anchor, cached busparams, and variable-length TX contexts. `struct kvaser_usb_dev_ops` is the subdriver vtable for mode changes, bit timing, busparams readback, endpoint setup, card/channel init, firmware/card/capability discovery, LED control, chip start/stop/reset/flush, bulk RX decode, and skb-to-command translation. Other central types are `kvaser_usb_driver_info`, `kvaser_usb_dev_cfg`, `kvaser_usb_busparams`, and `kvaser_usb_tx_urb_context`.

Control flow: the core selects a `kvaser_usb_driver_info` from the USB ID table, then drives the selected `kvaser_usb_dev_ops` through probe, open, close, bit timing, TX, and RX paths. Subdrivers use the exported helpers for synchronous/asynchronous USB commands, overflow error injection, TX URB unlinking, devlink port registration, and timestamp conversion.

State and persistence behavior: the header defines only in-memory kernel state. `completion` objects synchronize command replies; spinlocks protect TX contexts, Hydra transaction IDs, and partial RX buffers; anchors own URB lifetimes. No persistent state is represented.

Dependencies/integration points: includes Linux USB, netdev/devlink, SocketCAN, completion, ktime, math64, spinlock, and type headers. It is the integration seam between `kvaser_usb_core.c`, `kvaser_usb_devlink.c`, `kvaser_usb_leaf.c`, and `kvaser_usb_hydra.c`.

Risks: the vtable makes callback contracts critical: subdrivers must complete expected completions, provide matching frame encoders/decoders, and maintain busparam caches. `max_tx_urbs` doubles as the free-context sentinel, so inconsistent values can corrupt TX flow control. Timestamp conversion depends on each device config reporting the correct `timestamp_freq`.

Test signals: compile coverage across all four Kvaser objects catches signature drift. Runtime tests should exercise every ops callback for Leaf/Usbcan and Hydra families, including TX echo, command timeouts, devlink metadata, and timestamp conversion.
