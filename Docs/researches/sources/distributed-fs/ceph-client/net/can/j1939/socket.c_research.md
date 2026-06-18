# sources/distributed-fs/ceph-client/net/can/j1939/socket.c

## Purpose
This file implements the user-visible SAE J1939 datagram socket protocol. It handles bind/connect, address and PGN filtering, receive delivery, send queueing into J1939 transport sessions, ancillary data, timestamp/error queue reporting, socket options, release, and netdevice event cleanup.

## Important APIs, Types, And Functions
The `proto_ops` table exposes release, bind, connect, getname, poll, setsockopt, getsockopt, sendmsg, recvmsg, and ioctl fallback. `j1939_can_proto` registers this as a `SOCK_DGRAM` PF_CAN protocol.

Important functions include `j1939_sk_bind()`, `j1939_sk_connect()`, `j1939_sk_sendmsg()`, `j1939_sk_send_loop()`, `j1939_sk_recvmsg()`, `j1939_sk_recv()`, `j1939_sk_recv_match()`, `j1939_sk_setsockopt()`, `j1939_sk_errqueue()`, `j1939_sk_queue_activate_next()`, `j1939_sk_netdev_event_netdown()`, and `j1939_sk_netdev_event_unregister()`.

Socket options include `SO_J1939_FILTER`, `SO_J1939_PROMISC`, `SO_J1939_ERRQUEUE`, and `SO_J1939_SEND_PRIO`.

## Control Flow
Initialization clears the protocol-private tail of `struct j1939_sock`, sets default priority and reuse behavior, initializes filters, queues, and wait queue, enables RCU socket free, and installs the J1939 destructor.

Bind validates `sockaddr_can`, requires an ifindex and clean PDU1 PGN, resolves and validates the CAN device, starts or references the per-device `j1939_priv`, records local NAME/source address/PGN receive filter, increments local ECU accounting, and adds the socket to `priv->j1939_socks`. Rebinding to the same interface drops old local references and installs new ones; rebinding to a different interface is rejected.

Connect requires a prior bind to the same interface, validates destination name/address and broadcast permissions, stores peer NAME/address and optional PGN, and marks the socket connected.

Receive delivery walks `priv->j1939_socks`. `j1939_sk_recv_one()` rejects own-origin skbs, applies bound/connected destination-source matching, PGN and filter matching, clones matching skbs, sets message flags such as `MSG_DONTROUTE`, and queues to the socket receive queue. `recvmsg()` returns payload, source sockaddr, destination ancillary data, priority ancillary data, timestamp cmsgs, and message flags.

Send validates bound state, source identity, destination and broadcast permissions, allocates one or more skbs, fills J1939 control metadata, creates or extends a transport session via `j1939_tp_send()` and `j1939_session_skb_queue()`, queues the session on the socket, activates the first non-conflicting session, and schedules transport timers. Release waits for pending skbs, cancels sessions on interruption, removes the socket from the device list, decrements local ECU accounting, stops the netdevice private, frees filters, and drops the socket.

## State And Persistence
Socket state persists for the life of the socket. It includes bind/connect flags, local/remote J1939 addresses, filters, a PGN receive filter, pending skb count, and queued transport sessions. Per-device socket membership is protected by `priv->j1939_socks_lock`; per-socket session queue is protected by `sk_session_queue_lock`.

Error queue state is optional and controlled by `SO_J1939_ERRQUEUE`. When disabled, abort errors are reported through `sk_err` and `sk_error_report()` instead of queued timestamp/error skbs.

## Dependencies And Integration Points
This file depends on `main.c` for netdevice private start/stop and sending, `bus.c` for local ECU accounting, `transport.c` for session creation/activation/cancellation/timers, Linux error queue/timestamping support, CAN J1939 UAPI structures, and datagram socket queue helpers.

Netdevice event callbacks from `main.c` call into this file to report `ENETDOWN`, drop queues, unbind sockets on unregister, and synchronize RCU before clearing private pointers.

## Risks And Edge Cases
The send loop can split large writes into multiple TP-sized skbs and requires later writes that complete an existing incomplete session to match the originally declared total size. Mismatches return `-EIO`.

Release waits for `skb_pending` to reach zero. If interrupted, it cancels active sessions and drops queued sessions, so callers can observe shutdown errors for in-flight sends.

Filtering combines bind destination matching, connected source matching, PGN receive filter, and arbitrary user filters. Broadcast receive requires `SO_BROADCAST` unless promiscuous mode is enabled.

Priority values below 2 require `CAP_NET_ADMIN`. Conversion between socket priority and J1939 priority is inverted (`7 - prio`), which is easy to mishandle in tests.

Netdevice unregister manually detaches bound sockets and nulls `jsk->priv` to avoid a later destructor put. This path is race-prone and depends on socket locks plus `synchronize_rcu()`.

## Test Signals
Tests should cover bind/rebind/release, connect permissions, broadcast send/receive with and without `SO_BROADCAST`, NAME and address-based matching, PGN filters, `SO_J1939_FILTER`, promiscuous mode, send priority permission checks, multi-packet TP queueing, interrupted release, error queue notifications, and netdevice down/unregister while sockets and sessions are active.
