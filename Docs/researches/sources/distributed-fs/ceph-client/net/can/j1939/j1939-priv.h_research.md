# sources/distributed-fs/ceph-client/net/can/j1939/j1939-priv.h

## Purpose
This private header defines the internal SAE J1939 protocol data model and cross-file function contracts. It ties together socket handling, CAN receive/transmit glue, address claiming, ECU bus state, and transport protocol sessions.

## Important APIs, Types, And Functions
Key types include `struct j1939_ecu`, `struct j1939_priv`, `struct j1939_addr`, `struct j1939_sk_buff_cb`, `struct j1939_session`, and `struct j1939_sock`.

`struct j1939_priv` is the per-CAN-device protocol object. It owns the ECU list, address-entry table, netdevice pointer, active transport session list, max packet size, socket list, receive-side refcount, and timestamp key counter.

`struct j1939_sk_buff_cb` is stored in `skb->cb` and carries J1939 address metadata, message flags, transport offset, timestamp key, local source/destination flags, and priority.

`struct j1939_session` describes simple/TP/ETP transfer state, packet counters, timers, queued skbs, socket association, session state, and identifying address tuple.

`struct j1939_sock` embeds `struct sock`, bind/connect state, filters, PGN receive filter, wait queue, pending skb count, and queued sessions.

The header declares internal APIs for ECU mapping, address claim, socket receive/error queues, transport send/receive/session management, netdevice start/stop, and notifier reactions.

## Control Flow
Files in this module share state through this header. `main.c` creates `j1939_priv` and converts CAN frames to/from `j1939_sk_buff_cb`; `address-claim.c` resolves NAME/address state; `bus.c` owns ECU objects; `socket.c` owns user-visible sockets and session queues; `transport.c` implements the session machinery declared here.

Inline helpers classify addresses and PDU1 PGNs and provide `j1939_skb_to_cb()` with a build-time size check against `skb->cb`.

## State And Persistence
The header defines in-memory state only. Lifetimes are controlled by krefs, socket references, RCU-deferred socket destruction, hrtimers, list ownership, and netdevice references in the implementation files.

## Dependencies And Integration Points
It depends on public J1939 CAN UAPI (`linux/can/j1939.h`) and networking socket internals. It is included by all J1939 implementation units and is the internal ABI between them.

## Risks And Edge Cases
Because this header defines `skb->cb` layout, any size growth in `struct j1939_sk_buff_cb` can break receive/transmit paths; the build-time assertion in `j1939_skb_to_cb()` is the guard.

The session struct has multiple lock domains: active session list lock, socket session queue lock, and timer-owned TX fields. Changes need careful lock-order review.

`struct j1939_sock` embeds `struct sock` as the first member; `j1939_sk_init()` relies on this to memset the protocol-private tail only.

## Test Signals
Build coverage catches many header contract breaks. Runtime signals should come from J1939 socket tests covering bind/connect, filters, transport sessions, session cancellation, error queue reporting, and netdevice teardown.
