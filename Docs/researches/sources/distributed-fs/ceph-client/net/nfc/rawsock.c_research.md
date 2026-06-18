# sources/distributed-fs/ceph-client/net/nfc/rawsock.c

## Purpose

This file implements the AF_NFC raw socket protocol. It supports connected `SOCK_SEQPACKET` sockets for exchanging data with an activated NFC target and privileged `SOCK_RAW` sockets for passively receiving raw NFC traffic copies with metadata headers.

## Important APIs, Types, and Functions

The protocol is registered by `rawsock_init()` through `nfc_proto_register()` with `rawsock_nfc_proto`. The main socket operations are `rawsock_create()`, `rawsock_connect()`, `rawsock_release()`, `rawsock_sendmsg()`, and `rawsock_recvmsg()`. Monitor delivery is exported as `nfc_send_to_raw_sock()`.

`rawsock_tx_work()` asynchronously dequeues outgoing skbs and calls `nfc_data_exchange()`. `rawsock_data_exchange_complete()` adds the one-byte NFC header to replies, queues them to the socket receive queue, and schedules the next transmit if more data is queued. `rawsock_destruct()` deactivates the target and drops the NFC device reference for established sockets.

## Control Flow

`rawsock_create()` accepts only `SOCK_SEQPACKET` and `SOCK_RAW`. Raw sockets require `CAP_NET_RAW`, use receive-only ops, and are linked into `raw_sk_list`; seqpacket sockets initialize transmit work. `rawsock_connect()` validates the NFC sockaddr, gets the target device, checks target index against the current target range, activates the target for the requested protocol, stores the device and target index, and moves the socket to connected state.

`sendmsg()` allocates an NFC send skb, copies user payload, appends it to `sk_write_queue`, and schedules TX work if idle. Completion queues the response and continues the TX queue. Release unlinks raw sockets and, for connected sockets, sets send shutdown, cancels TX work, purges queued writes, orphans the socket, and drops the socket reference.

## State and Persistence

Per-socket state is embedded in `struct nfc_rawsock`: `dev`, `target_idx`, `tx_work`, and `tx_work_scheduled`. Raw monitor sockets are tracked in a global hlist with rwlock. There is no durable persistence; target activation persists only while the socket remains established.

## Dependencies and Integration Points

The file depends on AF_NFC protocol registration, NFC core target activation/data exchange/deactivation, socket and skb datagram helpers, kcov remote coverage, and Linux capability checks. `nfc_send_to_raw_sock()` is called by lower NFC paths to fan out observed traffic to raw monitors.

## Risks and Edge Cases

Release/work ordering is safety-critical because TX work uses the NFC device pointer. The code sets `SEND_SHUTDOWN`, cancels work synchronously, and purges the write queue before orphaning to avoid use-after-free. `rawsock_tx_work()` assumes `skb_dequeue()` returns a valid skb when scheduled. Raw monitor fanout clones one prepared skb per socket; allocation failures silently skip recipients.

## Test Signals

Tests should cover capability enforcement, invalid sockaddr/target ranges, connect while connected, send before connect, queued multi-message exchange, data-exchange error propagation, release during active exchange, raw monitor fanout header fields, and receive truncation behavior.
