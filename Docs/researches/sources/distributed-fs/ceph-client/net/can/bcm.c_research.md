# sources/distributed-fs/ceph-client/net/can/bcm.c

## Purpose
This file implements the PF_CAN Broadcast Manager protocol (`CAN_BCM`). It lets user space configure cyclic CAN/CAN FD transmissions, one-shot sends, receive filters, receive-change notifications, timeout notifications, multiplexed content comparisons, RTR replies, and optional procfs introspection.

## Important APIs, Types, And Functions
`struct bcm_sock` is the protocol socket state: bound ifindex, notifier list entry, RX/TX operation lists, procfs entry name, and dropped-user-message counter. `struct bcm_op` represents one BCM operation with CAN ID, flags, timers, frame arrays, last-frame arrays, counters, current TX frame index, owning socket, and registered RX device.

Core command handlers are `bcm_sendmsg()`, `bcm_tx_setup()`, `bcm_rx_setup()`, `bcm_tx_send()`, `bcm_delete_rx_op()`, `bcm_delete_tx_op()`, and `bcm_read_op()`. Delivery and timer functions include `bcm_can_tx()`, `bcm_tx_timeout_handler()`, `bcm_rx_handler()`, `bcm_rx_timeout_handler()`, `bcm_rx_thr_handler()`, and `bcm_send_to_user()`.

The socket operations table exposes `connect()` as the binding operation, `sendmsg()` for BCM opcodes, `recvmsg()` for notifications/status replies, `poll`, timestamp retrieval, and release.

## Control Flow
Socket initialization sets up RX/TX operation lists and adds the socket to a global notifier list. `bcm_connect()` binds the BCM socket to a CAN interface or ifindex zero ("any"), verifies CAN devices, creates a procfs entry when available, and marks the socket bound.

`bcm_sendmsg()` reads a `struct bcm_msg_head`, validates payload size against Classic CAN or CAN FD frame size, resolves an alternative sendto ifindex when the socket is bound to any, locks the socket, and dispatches by opcode. `TX_SETUP` creates or updates a TX op, copies frame payloads, configures count and timers, optionally announces immediately, and starts cyclic transmission. `RX_SETUP` creates or updates an RX op, allocates comparison and last-frame storage, configures timeout/throttle timers, and registers a CAN receive filter. `TX_SEND` sends exactly one frame without storing an op.

RX callbacks arrive through `can_rx_register()`. `bcm_rx_handler()` filters by frame type and CAN ID, cancels receive timeout, records timestamp and source ifindex, handles RTR auto-reply, computes local/own traffic flags, performs direct or multiplexed content comparison, reports `RX_CHANGED` immediately or through throttle handling, and restarts timeout monitoring.

Release removes the socket from the notifier list, tears down procfs entries, unregisters RX filters, waits for RCU readers, cancels timers, frees operations via RCU, orphans the socket, and drops protocol usage.

## State And Persistence
All BCM state is per socket and per net namespace. Operation configuration persists while the socket is open. Timers hold runtime scheduling state for cyclic TX, RX timeout, and throttled RX notifications. Procfs entries under `/proc/net/can-bcm` are live views only and disappear on socket release, net namespace exit, or device unregister.

TX and RX operation lists are protected primarily by socket locking. Individual cyclic TX fields that can change while timers run are protected by `bcm_tx_lock`. Operation memory is freed with `call_rcu()` because receive callbacks can observe operations after list removal.

## Dependencies And Integration Points
BCM depends on PF_CAN core protocol registration, `can_send()`, `can_rx_register()`, and `can_rx_unregister()`. It uses CAN UAPI types from `linux/can/bcm.h`, CAN skb extensions, high-resolution timers, netdevice notifiers, procfs/seq_file, and per-net operations.

Netdevice notifier integration removes receive registrations and reports `ENODEV` or `ENETDOWN` to affected sockets. Per-net init/exit owns the procfs directory.

## Risks And Edge Cases
The message format is compact and user-controlled; length checks must stay aligned with `CAN_FD_FRAME` and frame count flags. `MAX_NFRAMES` limits most operations to 256 frames, with RX multiplex setup allowing `MAX_NFRAMES + 1` because index zero is the mux mask.

Existing TX/RX operations cannot grow their frame arrays; updates with more frames than originally allocated return `-E2BIG`.

Receive callbacks run asynchronously with socket close and device unregister. Correctness depends on unregistering filters, `synchronize_rcu()`, and RCU-delayed operation free.

Timer callbacks can send frames and queue user notifications. Tests need to cover cancellation paths, especially release during active TX/RX timers and notifier callbacks.

`bcm_notify()` sets socket errors but does not necessarily remove all configured ops on `NETDEV_DOWN`; user space must handle errors and potentially reconfigure after link changes.

## Test Signals
Useful tests include `can-utils` BCM exercises, kernel CAN selftests, and fault-injection around invalid opcodes, invalid frame lengths, timer values beyond `BCM_TIMER_SEC_MAX`, CAN FD/classic mismatches, multiplex filters, RTR reply setup, `RX_CHECK_DLC`, throttle flush behavior, and netdevice unregister while operations are active.
