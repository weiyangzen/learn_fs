# sources/distributed-fs/ceph-client/include/linux/ceph/messenger.h

## Purpose

`messenger.h` defines libceph's in-kernel messaging runtime: connection callbacks, message payload abstractions, message objects, v1/v2 connection state, crypto framing state, ordered send/ack queues, and public connection/message APIs.

## Important APIs, Types, and Functions

Important types include `ceph_connection_operations`, `ceph_messenger`, `ceph_msg_data`, `ceph_msg_data_cursor`, `ceph_msg`, `ceph_connection_v1_info`, `ceph_connection_v2_info`, and `ceph_connection`. Public APIs cover connection flags, socket/session reset, data cursor iteration, CRC, address parsing/printing, messenger init/fini, connection open/close/send/keepalive, message allocation/refcounting/revocation, and data attachment helpers for pages, pagelists, bio, bvecs, and `iov_iter`.

## Control Flow

Connections transition through closed/preopen, v1 banner/connect or v2 banner/hello/auth/session states, then open/standby. Workqueue-driven read/write handlers process frames, allocate incoming messages through callbacks, dispatch messages, maintain ordered out queues and sent-but-unacked lists, and use reconnect sequence state to preserve lossless delivery unless the connection is marked lossy.

## State and Persistence Behavior

State is in `ceph_messenger` global sequence counters and each `ceph_connection`: peer identity/address/features, socket, flags, queues, sequence numbers, active messages, CRCs, keepalive timestamps, delayed work, backoff delay, and protocol-specific v1/v2 scratch state. No disk persistence is owned.

## Dependencies and Integration Points

It depends on networking, crypto, workqueues, block/bvec APIs, page/pagelist buffers, and `ceph/types.h`. It integrates with monitor and OSD clients through callback tables and with `msgr.h` wire headers.

## Risks and Edge Cases

Concurrency is high-risk: queue, refcount, socket, delayed work, and reconnect state must stay consistent. v2 secure mode adds GCM/HMAC nonce and buffer lifetime concerns. Data cursors must not overrun page/bio/bvec/iov boundaries. Lossless reconnection handling must discard only acknowledged or safely requeued messages.

## Test Signals

Run messenger v1/v2 connection tests, forced reconnect and peer reset tests, lossy channel behavior, keepalive expiry, payload cursor tests for every data type, CRC/signature failures, secure-mode crypto tests, and stress tests under socket close races.
