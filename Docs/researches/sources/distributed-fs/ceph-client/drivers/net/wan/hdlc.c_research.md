# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc.c

## Purpose
`hdlc.c` is the generic HDLC core used by WAN hardware drivers and protocol modules. It owns the common `alloc_hdlcdev()`/`register_hdlc_device()` lifecycle, dispatches `ETH_P_HDLC` receive traffic to the currently attached protocol, forwards outbound packets through either protocol-specific `xmit` or the hardware driver, and coordinates carrier-change start/stop callbacks.

## Important APIs, Types, And Functions
The exported API is the file's main contract: `hdlc_start_xmit()`, `hdlc_open()`, `hdlc_close()`, `hdlc_ioctl()`, `alloc_hdlcdev()`, `unregister_hdlc_device()`, `attach_hdlc_protocol()`, `detach_hdlc_protocol()`, `register_hdlc_protocol()`, and `unregister_hdlc_protocol()`. It depends on the public `struct hdlc_device` and `struct hdlc_proto` definitions from `<linux/hdlc.h>`. `hdlc_packet_type` registers the receive hook for `ETH_P_HDLC`, and `hdlc_notifier` observes `NETDEV_CHANGE` events for carrier transitions.

## Control Flow
Module init registers the netdevice notifier and packet handler. Hardware drivers allocate an HDLC netdevice with `alloc_hdlcdev()`, then fill `hdlc->attach` and `hdlc->xmit` before `register_hdlc_device()`. User-space protocol selection is routed through `hdlc_ioctl()`: the currently attached protocol gets first chance, then all registered protocol modules are scanned. On open, the core calls `proto->open()`, records the open state under `state_lock`, and calls `proto->start()` immediately if carrier is already present. Carrier changes also call `proto->start()` or `proto->stop()` while holding the same lock. On close, open state is cleared, an active protocol is stopped, and `proto->close()` is invoked outside the spinlock.

## State And Persistence
State is in memory only: global `first_proto`, per-device `hdlc->proto`, optional `hdlc->state`, carrier/open flags, and a per-device spinlock. No durable persistence exists. `attach_hdlc_protocol()` allocates protocol state and module-pins the protocol owner; `detach_hdlc_protocol()` invokes optional protocol cleanup, drops the module reference, frees state, and resets netdevice properties to raw HDLC defaults.

## Dependencies And Integration Points
The file integrates with rtnetlink, netdevice notifiers, packet taps, `init_net`, protocol modules such as raw/Cisco/FR/PPP/X.25, and hardware drivers such as SCA, wanXL, and IXP4xx HSS. It assumes protocol changes occur with the device administratively down and uses `NETDEV_PRE_TYPE_CHANGE`/`NETDEV_POST_TYPE_CHANGE` around type transitions in protocol modules.

## Risks
`hdlc_rcv()` calls `BUG_ON(!hdlc->proto->netif_rx)`, so a malformed protocol attachment can panic the kernel. Receive handling is restricted to `init_net`; packets on HDLC devices outside the initial namespace are dropped. `detach_hdlc_protocol()` relies on callers respecting device-down constraints; detaching while callbacks are active would be unsafe. `first_proto` is protected by RTNL registration paths, so protocol ioctl scanning must remain under the expected netdevice serialization.

## Test Signals
Useful signals are protocol attach/detach via `sethdlc`, `IF_GET_PROTO` responses, `NETDEV_POST_TYPE_CHANGE` notifications from protocol modules, carrier up/down messages, packet delivery through `hdlc_type_trans()`, and module unload/reload with multiple registered protocol modules. Regression tests should exercise attach failure cleanup, carrier transitions while open and closed, and unregistering a device with an attached protocol.
