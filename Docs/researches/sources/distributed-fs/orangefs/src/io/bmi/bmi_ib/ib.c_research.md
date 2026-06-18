# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/ib.c

## Purpose
`ib.c` is the provider-neutral core of OrangeFS/PVFS2's BMI InfiniBand method. It exposes the `bmi_ib_ops` method table to BMI, owns global method state, manages TCP-assisted connection setup, and drives the send/receive state machines used by both OpenIB and VAPI backends. It implements eager messages for small payloads and a rendezvous RTS/CTS/RDMA-write protocol for large payloads.

## Important APIs, Types, and Functions
The public integration point is `const struct bmi_method_ops bmi_ib_ops`, whose entries map BMI operations to static functions such as `BMI_ib_initialize`, `BMI_ib_finalize`, `BMI_ib_post_send`, `BMI_ib_post_recv`, `BMI_ib_test`, `BMI_ib_testsome`, `BMI_ib_testcontext`, `BMI_ib_testunexpected`, `BMI_ib_cancel`, and `BMI_ib_method_addr_lookup`.

Provider operations are accessed through `ib_device->func` macros such as `new_connection`, `post_sr`, `post_sr_rdmaw`, `check_cq`, `mem_register`, and `check_async_events`. This keeps common BMI behavior in this file while delegating verbs/VAPI-specific work to `openib.c` or `vapi.c`.

Core helpers include `ib_check_cq`, `encourage_send_waiting_buffer`, `encourage_send_incoming_cts`, `encourage_recv_incoming`, `send_cts`, `encourage_rts_done_waiting_buffer`, `post_send`, `post_recv`, `test_sq`, `test_rq`, `ib_new_connection`, `ib_close_connection`, `ib_tcp_client_connect`, `ib_tcp_server_init_listen_socket`, `ib_tcp_server_accept_thread`, and `ib_block_for_activity`.

## Control Flow
Initialization allocates the global `ib_device`, chooses OpenIB first and VAPI second at compile/runtime depending on macros, initializes the memory cache, and optionally starts a TCP listen socket plus accept thread for server mode. Client-side connections are established lazily by `ensure_connected` when a send or receive is posted.

Posting a send allocates an `ib_work` send queue item and `method_op`, validates the buffer list total, assigns an id through `id_gen_fast_register`, queues it on `ib_device->sendq`, and calls `encourage_send_waiting_buffer`. If the payload fits `eager_buf_payload`, the code encodes `MSG_EAGER_SEND` or `MSG_EAGER_SENDUNEXPECTED`, copies data into an eager send buffer, and posts a provider SEND. Larger sends encode `MSG_RTS`, optionally early-register user buffers, then wait for `MSG_CTS`; after CTS, the provider posts one or more RDMA writes and this file sends `MSG_RTS_DONE`.

Posting a receive either matches an already-arrived eager/RTS receive item or allocates a waiting receive queue item. Eager data is copied from the held eager receive buffer into the user's buflist. RTS data triggers `send_cts`, which registers the receive buflist and sends remote addresses, lengths, and rkeys to the sender. Completion testing polls the CQ, advances all eligible state machines, and reaps completed items only when the matching BMI context or op id asks for them.

Unexpected traffic is handled by `BMI_ib_testunexpected`, which finds `RQ_EAGER_WAITING_USER_TESTUNEXPECTED`, copies the data into a newly allocated buffer returned to BMI, reposts the eager receive buffer, and removes the internal receive item.

## State and Persistence Behavior
The file maintains process-local state only: `ib_device`, send/receive queues, connection list, memory cache pointer, TCP listen state, and accept thread flags. Per-connection state includes eager send/receive buffer pools, credits, refcounts, and `remote_map` links. There is no durable persistence. Operation lifetime is guarded by BMI op ids and `ib_connection_t.refcnt`; connection close is deferred until all queue entries referencing the connection are reaped.

The credit protocol uses `send_credit` to bound posted sends to peer receive buffers and `return_credit` to piggyback replenishment on outgoing message headers. `post_rr` increments returned credit and can send an explicit `MSG_CREDIT` when credits accumulate.

## Dependencies and Integration Points
This file depends on BMI method support, BMI method callbacks, the id generator, quicklists, PVFS locks, pthreads, TCP sockets, `pint-hint.h`, bytefield encode/decode stubs, and provider vtables defined in `ib.h`. It registers accepted server-side addresses through `bmi_method_addr_reg_callback` and parses BMI addresses of the form `ib://hostname:port/filesystem`.

It integrates tightly with `mem.c` for registration caching, `util.c` for logging/list/copy helpers, and `openib.c`/`vapi.c` for QP, CQ, memory registration, and provider-specific event handling.

## Risks and Edge Cases
The implementation is highly stateful and uses a single global mutex around most BMI entry points; provider callback threads and accept threads make lock ordering important. Many `error()` calls only log and do not abort, so callers may continue after serious invariants fail unless the local code returns immediately. Cancellation drains the QP and marks in-flight operations cancelled, but correctness depends on matching all memory registration states for early registration and RDMA completion. `BMI_ib_test` assumes `id_gen_fast_lookup` succeeds and does not visibly guard against invalid ids. Address lookup increments `ref_count`, while `BMI_DROP_ADDR` frees only when the count reaches zero; remote maps attached to live connections are intentionally retained for process lifetime.

The TCP handshake is used only for connection bootstrap; peer identity and network byte order parsing must remain consistent with both provider backends. `ib_block_for_activity` polls provider CQ and async fds but no longer polls the TCP listen socket directly because accept is handled by a separate thread.

## Test Signals
Useful tests would exercise eager expected send/recv, eager unexpected send/testunexpected, large RTS/CTS/RDMA transfers with single and list buffers, cancellation during each send/recv state, connection close by `MSG_BYE`, credit exhaustion/refill, failed TCP connect, invalid BMI address parsing, server accept/finalize thread shutdown, and both OpenIB and VAPI provider selection paths. Runtime validation should inspect debug logs for state transitions and verify no memory registrations remain after finalize.
