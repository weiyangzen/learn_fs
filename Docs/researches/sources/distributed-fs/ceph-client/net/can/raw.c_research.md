# sources/distributed-fs/ceph-client/net/can/raw.c

## Purpose
Implements the PF_CAN raw socket protocol (`CAN_RAW`). It lets users bind raw sockets to a CAN interface or all interfaces, configure CAN ID and error filters, opt into CAN FD and CAN XL frames, control loopback and own-message reception, send frames, and receive matched CAN datagrams.

## Important APIs, Types, and Functions
The central type is `struct raw_sock`, which embeds `struct sock` and stores bound device state, filter arrays, error masks, CAN FD/XL enable flags, CAN XL VCID options, loopback settings, notifier linkage, and per-CPU duplicate-suppression state (`struct uniqframe`). Key functions are `raw_init()`, `raw_release()`, `raw_bind()`, `raw_setsockopt()`, `raw_getsockopt()`, `raw_sendmsg()`, `raw_recvmsg()`, `raw_rcv()`, `raw_enable_filters()`, `raw_disable_filters()`, `raw_enable_errfilter()`, `raw_notify()`, and `raw_notifier()`. Protocol registration is through `raw_can_proto`, `raw_proto`, and `raw_ops`.

## Control Flow
Socket creation initializes one default catch-all filter stored in `dfilter`, allocates per-CPU duplicate tracking, and links the socket into `raw_notifier_list`. Binding validates `sockaddr_can`, resolves an optional CAN netdevice, registers current filters against either the device or all devices, then unregisters old filters and updates held device references. `setsockopt()` replaces filters and error masks with register-new-then-unregister-old ordering for bound sockets; other options mutate local flags.

Receive callbacks are invoked by the CAN core for each matching filter. `raw_rcv()` drops unwanted looped-back frames, disallowed FD/XL frames, and CAN XL frames failing VCID policy. It suppresses duplicate deliveries from multiple matching filters, or with `CAN_RAW_JOIN_FILTERS` waits until all filters matched. Accepted frames are cloned, annotated with `sockaddr_can` and message flags in `skb->cb`, and queued to the socket. `sendmsg()` obtains the target device, rejects read-only devices, copies user frame bytes into an skb, validates CAN/FD/XL size and device capability, applies CAN XL VCID transmit policy, handles control messages, and calls `can_send()`.

## State and Persistence
All state is socket-local except the global notifier list and the transient `raw_busy_notifier` reentrancy guard. `ro->dev` is refcounted with a `netdevice_tracker` while bound. `ro->filter` either points at inline `dfilter`, a dynamically allocated filter array, or NULL when zero filters are configured. No state is persisted beyond socket lifetime.

## Dependencies and Integration Points
Depends on the CAN core receive registry (`can_rx_register()`/`can_rx_unregister()`), CAN skb extensions, CAN frame validators, netdevice notifier API, socket layer datagram queues, control message parsing, and CAN capability bits (`CAN_CAP_CC`, `CAN_CAP_FD`, `CAN_CAP_XL`, `CAN_CAP_RO`). It registers as protocol `CAN_RAW` / `can-proto-1`.

## Risks
Filter replacement is sensitive to lock ordering (`rtnl_lock()` plus socket lock) and to cleanup on partial registration failure. The notifier loop intentionally drops the spinlock while notifying sockets and uses `raw_busy_notifier` to avoid freeing a socket being notified. Per-CPU duplicate suppression relies on skb pointer and hash stability across callback invocations. CAN XL VCID policy has deny-by-default behavior for tagged RX frames unless a filter is enabled, which can surprise callers. Send path must keep frame-size validation aligned with CAN core helpers.

## Test Signals
Cover default receive-all binding, zero filters receiving nothing, multi-filter duplicate suppression, join-filter behavior, error mask registration, device unregister/down notifications, bind-to-all versus bind-to-device, CAN FD opt-in, CAN XL opt-in and VCID RX/TX options, read-only send rejection, capability-based frame-size rejection, own-message flags (`MSG_CONFIRM`/`MSG_DONTROUTE`), and module register/unregister cleanup.
