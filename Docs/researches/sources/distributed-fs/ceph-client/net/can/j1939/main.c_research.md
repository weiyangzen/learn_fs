# sources/distributed-fs/ceph-client/net/can/j1939/main.c

## Purpose
This file is the J1939 core glue between PF_CAN and the internal J1939 stack. It registers the CAN_J1939 protocol, manages one `j1939_priv` object per CAN netdevice, registers receive filters, parses incoming CAN EFF frames into J1939 metadata, sends J1939 skbs as CAN frames, and reacts to netdevice state changes.

## Important APIs, Types, And Functions
Externally visible internal functions are `j1939_netdev_start()`, `j1939_netdev_stop()`, `j1939_send_one()`, `j1939_priv_get()`, and `j1939_priv_put()`.

Important internal helpers include `j1939_can_recv()`, `j1939_priv_create()`, `j1939_priv_set()`, `j1939_can_rx_register()`, `j1939_can_rx_unregister()`, `j1939_priv_get_by_ndev()`, and `j1939_netdev_notify()`.

The module registers `j1939_can_proto`, implemented in `socket.c`, and a netdevice notifier.

## Control Flow
`j1939_netdev_start()` is called when a socket binds to a CAN device. It looks for an existing `j1939_priv` under `j1939_netdev_lock`, increments the receive refcount if present, or creates a new object, initializes transport and socket lists, installs it into `can_ml_priv`, registers a broad extended-frame receive filter, and returns the referenced private object.

`j1939_can_recv()` receives borrowed CAN skbs from PF_CAN, accepts only Classical CAN, clones the skb, takes a `j1939_priv` reference, pulls the CAN header so the skb payload is just J1939 data bytes, fills `j1939_sk_buff_cb` from the 29-bit CAN ID, normalizes PDU1 PGNs and destination addresses, annotates local source/destination flags from the address table, then runs address-claim receive, transport receive, simple receive, and socket delivery. It releases the private reference and cloned skb afterward.

`j1939_send_one()` performs TX sanity normalization, calls address-claim fixup, pushes a CAN header back onto the skb, pads to an 8-byte CAN frame, constructs the EFF CAN ID from priority, PGN, destination, and source address, then sends with local loopback through `can_send()`.

The netdevice notifier cancels active sessions, reports errors to sockets, and unmaps ECUs on down/unregister. Module init registers the notifier first and then the PF_CAN protocol; exit unregisters both.

## State And Persistence
`j1939_priv` is stored in `can_ml_priv->j1939_priv` for the CAN netdevice. It is protected by `j1939_netdev_lock` for creation/removal and by krefs for receive, socket, ECU, and transient users. The receive filter's lifetime is counted by `rx_kref`; the final unregister path clears the netdevice pointer and unmaps ECUs.

State persists while at least one socket/session/receive user holds references. It is not persisted across module unload or device unregister.

## Dependencies And Integration Points
This file depends on PF_CAN core receive registration and `can_send()`, CAN skb extensions, CAN multi-layer device private state, the J1939 socket protocol from `socket.c`, ECU/address claim from `address-claim.c` and `bus.c`, and transport/simple receive functions from `transport.c`.

## Risks And Edge Cases
The code relies on local loopback for address-claim ordering and transmit completion behavior. Devices or configurations that disturb echo semantics can affect J1939 state.

`j1939_can_recv()` clones and mutates the skb layout; downstream layers expect skb data to start at J1939 payload, while `j1939_send_one()` expects enough headroom to push the CAN header back.

Per-device private creation handles a race where another binder creates `priv` first, but this path must keep netdevice and kref accounting balanced.

Only Classical CAN frames are accepted in this receive path; CAN FD frames are ignored for J1939 here.

## Test Signals
Tests should cover concurrent binds to the same vcan device, bind/release reference balance, receive parsing for PDU1/PDU2 PGNs, transmit CAN ID construction, netdevice down/unregister behavior, and module autoload through `can-proto-CAN_J1939`.
