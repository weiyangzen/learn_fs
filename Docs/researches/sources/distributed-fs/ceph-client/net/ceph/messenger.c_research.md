# Research: sources/distributed-fs/ceph-client/net/ceph/messenger.c

## Purpose

`messenger.c` is the protocol-independent core of the kernel Ceph messenger. It owns connection lifetime, TCP socket callback wiring, the per-connection workqueue engine, generic fault and reconnect behavior, message queueing and acknowledgement handling, message allocation/refcounting, data-payload cursor logic, address parsing/formatting, and messenger instance initialization. The version-specific files `messenger_v1.c` and `messenger_v2.c` plug into this core through `ceph_con_v[12]_try_read()`, `ceph_con_v[12]_try_write()`, revoke, opened, and reset hooks.

The messenger promises ordered reliable delivery over TCP where possible. It tolerates disconnects, CRC/signature failures, and protocol faults by resetting the socket/protocol state, requeueing unacknowledged messages, and retrying with exponential backoff unless the connection is lossy or idle enough to enter standby.

## Important APIs, Types, and Functions

Connection and messenger lifecycle:

- `ceph_msgr_init()`, `ceph_msgr_exit()`, and `ceph_msgr_flush()` create/destroy/flush the global message slab, zero page reference, and `ceph-msgr` workqueue.
- `ceph_messenger_init()`, `ceph_messenger_fini()`, and `ceph_messenger_reset_nonce()` initialize a client messenger instance, manage its network namespace, and update the encoded local address.
- `ceph_con_init()`, `ceph_con_open()`, `ceph_con_close()`, `ceph_con_opened()`, `ceph_con_reset_session()`, and the private `ceph_con_reset_protocol()` manage an individual `struct ceph_connection`.

Socket and workqueue operations:

- `ceph_tcp_connect()` creates a kernel TCP socket, installs callbacks, optionally enables `TCP_NODELAY`, and starts a nonblocking connect.
- `ceph_con_close_socket()` shuts down and releases the socket and clears `CEPH_CON_F_SOCK_CLOSED`.
- `ceph_sock_data_ready()`, `ceph_sock_write_space()`, and `ceph_sock_state_change()` translate socket events into queued connection work.
- `ceph_con_workfn()` is the central worker: handle socket-close and backoff flags, dispatch version-specific read/write loops, and invoke fault handling on errors.

Message and queue operations:

- `ceph_con_send()` consumes a message reference and appends it to `out_queue`.
- `ceph_con_get_out_msg()` moves the next queued message to `out_sent`, assigns sequence numbers, and optionally calls `ops->reencode_message`.
- `ceph_con_discard_sent()` and `ceph_con_discard_requeued()` release messages acknowledged by the peer or already handled before reconnect.
- `ceph_msg_revoke()` and `ceph_msg_revoke_incoming()` remove or skip outgoing/incoming messages, delegating protocol-specific stream repair to v1/v2 hooks.
- `ceph_msg_new2()`, `ceph_msg_new()`, `ceph_msg_get()`, `ceph_msg_put()`, and `ceph_msg_dump()` allocate, retain, release, and debug-dump `struct ceph_msg`.

Data payload cursor APIs:

- `ceph_msg_data_add_pages()`, `ceph_msg_data_add_pagelist()`, `ceph_msg_data_add_bio()`, `ceph_msg_data_add_bvecs()`, and `ceph_msg_data_add_iter()` attach payload segments.
- `ceph_msg_data_cursor_init()`, `ceph_msg_data_next()`, and `ceph_msg_data_advance()` drive page-by-page send/receive over pages, pagelists, bios, bvecs, and iov_iters.
- `ceph_crc32c_page()` maps a page to compute CRC32C.

Address helpers:

- `ceph_pr_addr()`, `ceph_addr_is_blank()`, `ceph_addr_port()`, `ceph_addr_set_port()`, and `ceph_parse_ips()` format and parse Ceph entity addresses, including optional DNS resolver support.

## Control Flow

The connection state model has two layers. `con->state` tracks Ceph protocol states such as `CLOSED`, `PREOPEN`, v1/v2 handshake phases, `OPEN`, and `STANDBY`. `con->sock_state` separately tracks TCP socket state transitions from closed to connecting, connected, closing, and closed using atomic exchange helpers that warn on unexpected transitions.

Opening starts in `ceph_con_open()`, which sets peer identity/address and queues work. `ceph_con_workfn()` runs under `con->mutex`. If the connection is `PREOPEN`, the version-specific write path initiates the TCP connect and handshake. Each work iteration tries reads first, then writes, using msgr2 selection from `ceph_msgr2(from_msgr(con->msgr))`. A negative read/write result marks a fault unless it is `-EAGAIN`, which loops because the callback path may have dropped the mutex and state changed.

Socket callbacks are intentionally small. Data readiness and write-space events call `queue_con()` if the messenger is not stopping and data or write capacity is relevant. TCP close/close-wait marks the socket closing, sets `CEPH_CON_F_SOCK_CLOSED`, and queues work. The worker later converts the asynchronous socket flag into a controlled fault under `con->mutex`.

Outgoing message flow is `ceph_con_send()` -> `out_queue` -> `ceph_con_get_out_msg()` -> version-specific serialization -> `out_sent` until acknowledged. Assigning the message sequence happens only the first time a message leaves `out_queue`, so requeued messages retain their original sequence. Incoming flow is version-specific parsing -> `ceph_con_in_msg_alloc()` -> `ceph_con_process_message()`. Allocation temporarily drops `con->mutex` while invoking `ops->alloc_msg()`, then rechecks that the connection is still open.

Fault handling resets protocol state, closes the socket, drops current in/out messages, and calls the selected protocol reset hook. Lossy connections close permanently. Non-lossy connections splice `out_sent` back to `out_queue`; if no outbound work or keepalive remains, the connection enters `STANDBY`, otherwise it returns to `PREOPEN`, increases `delay` up to `MAX_DELAY_INTERVAL`, sets `CEPH_CON_F_BACKOFF`, and queues later work. `con_fault_finish()` runs outside the connection mutex and notifies `ops->fault()`.

## State and Persistence Behavior

All state is in memory. Global module state includes the message slab cache, workqueue pointer, zero page reference, and a small rotating address-format buffer. Per-messenger state includes global sequence, local entity address and name, stopping flag, and network namespace. Per-connection state includes flags, peer identity/address, socket pointer/state, current protocol state, backoff delay, message queues, sequence counters, current input/output messages, bounce page, and protocol-specific v1/v2 substructures.

Message lifetime is reference counted with `kref`. A message may hold a connection reference through `msg_con_set()`, a middle buffer, and one or more data items. When a pooled message reaches zero references, `ceph_msg_release()` returns it to its pool via `ceph_msgpool_put()`; otherwise it frees the front buffer, data array, and slab object.

## Dependencies and Integration Points

This file integrates with Linux kernel sockets, workqueues, namespaces, DNS resolver, TCP helpers, bio/iov APIs, CRC32C, and Ceph protocol headers. It depends on connection operation callbacks supplied by monitor, OSD, MDS, or other clients: `get`, `put`, `alloc_msg`, `dispatch`, `fault`, `peer_reset`, `reencode_message`, and authentication/signature hooks used by protocol versions. It exports the generic APIs consumed by the monitor client (`mon_client.c`), OSD client, CephFS, and RBD.

## Risks and Edge Cases

The highest-risk areas are concurrency and partial I/O. `con->mutex` protects most connection state, but socket callbacks set flags asynchronously and message allocation/dispatch temporarily drops the mutex. State is rechecked after those drops, and refcounting through `ops->get()` prevents queued work from racing teardown. Cursor code has many `BUG_ON()` invariants; callers must attach valid data items matching declared lengths before sending or receiving payloads. Revoke paths depend on v1/v2 stream repair to preserve framing after a partially sent or received message is abandoned. Fault handling must not lose unacknowledged messages, must avoid resending acked messages, and must put idle connections into standby without starving future keepalives or sends.

Address parsing accepts IPv4, bracketed IPv6, optional ports, and optional DNS names. It sets addresses to `LEGACY` initially because msgr mode may be parsed later; callers adjust type later. DNS resolver availability changes behavior under `CONFIG_CEPH_LIB_USE_DNS_RESOLVER`.

## Test Signals

Important tests include connection open/close under concurrent socket callbacks, reconnect with out_sent requeue and acknowledgement discard, lossy connection fault closure, standby wakeup by send/keepalive, partial message send/receive revocation, incoming allocation races where connection closes while `alloc_msg` runs, data cursor traversal across pages/pagelists/bios/bvecs/iov_iters, CRC over highmem pages, DNS/IP parsing including malformed ports and bracketed IPv6, and module init/exit leak checks. Runtime lockdep, KASAN, refcount warnings, and fault-injection around socket I/O and memory allocation are strong signals for this file.
