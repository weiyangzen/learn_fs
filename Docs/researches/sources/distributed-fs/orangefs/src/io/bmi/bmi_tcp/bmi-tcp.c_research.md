# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/bmi-tcp.c

## Purpose

This file implements the Unix TCP/IP BMI method for OrangeFS. It exports `bmi_tcp_ops`, translating the BMI method interface into nonblocking TCP sockets, BMI message headers, operation queues, completion queues, and socket readiness polling through either `socket-collection.c` or `socket-collection-epoll.c`.

It is the central transport state machine for `bmi_tcp`: initialization and finalization, address lookup, connect/accept, send and receive posting, progress during test calls, unexpected-message delivery, cancellation, address cleanup, socket buffer tuning, optional trusted-network checks, and PINT event instrumentation.

## Important APIs, Types, And Data

- `bmi_tcp_ops` wires BMI callbacks to `BMI_tcp_initialize`, `BMI_tcp_finalize`, `BMI_tcp_set_info`, `BMI_tcp_get_info`, memory helpers, send/recv post functions, test functions, address lookup, list variants, context open/close, cancel, reverse lookup, and address-range query.
- `struct tcp_msg_header` is the 24-byte wire envelope: magic, mode, tag, payload size, and encoded bytes. `BMI_TCP_ENC_HDR` and `BMI_TCP_DEC_HDR` convert the header using BMI byte-swap helpers.
- `struct tcp_op` is the TCP-private extension of `method_op_p`. It stores the header, TCP operation state, and stub list entries for single-buffer operations.
- `enum bmi_tcp_state` distinguishes `BMI_TCP_INPROGRESS`, `BMI_TCP_BUFFERING`, and `BMI_TCP_COMPLETE`.
- Operation lists are indexed by `IND_SEND`, `IND_RECV`, `IND_RECV_INFLIGHT`, `IND_RECV_EAGER_DONE_BUFFERING`, and `IND_COMPLETE_RECV_UNEXP`.
- `completion_array[BMI_MAX_CONTEXTS]` stores completed expected operations by BMI context. Unexpected receives use `IND_COMPLETE_RECV_UNEXP`.
- `tcp_socket_collection_p` is the readiness backend. The selected implementation is controlled by `__PVFS2_USE_EPOLL__`.
- `tcp_method_params` stores method flags, method id, listen address, and a zone/connect-test toggle.
- `forceful_cancel_mode`, `check_unexpected`, `tcp_buffer_size_receive`, and `tcp_buffer_size_send` are runtime knobs set through BMI info options.

## Control Flow

Initialization enters through `BMI_tcp_initialize`. Server mode validates a listen address, calls `tcp_server_init` to create/bind/listen on a nonblocking socket, allocates all operation lists, creates the socket collection with either the listening socket or `-1`, and registers PINT send/receive event types. Finalization deallocates the listen address, cleans operation lists, and finalizes the socket collection.

Address lookup is handled by `BMI_tcp_method_addr_lookup`. It extracts `tcp` address strings, parses host and port, optionally parses a network zone, allocates a BMI method address, and can run a first client connect test to establish the usable zone. Server-accepted addresses are allocated later by `handle_new_connection`.

Send posting starts in `BMI_tcp_post_send`, `BMI_tcp_post_sendunexpected`, or their list variants. These build a TCP header with mode `TCP_MODE_EAGER`, `TCP_MODE_REND`, or `TCP_MODE_UNEXP`, then call `tcp_post_send_generic`. That function encodes the header, preserves per-address send ordering by checking `IND_SEND`, initializes or advances the connection with `tcp_sock_init`, tries an immediate `payload_progress`, and either returns immediate completion or enqueues the remainder through `enqueue_operation`.

Receive posting starts in `BMI_tcp_post_recv` or `BMI_tcp_post_recv_list`, then calls `tcp_post_recv_generic`. It first checks for already buffered eager data in `IND_RECV_EAGER_DONE_BUFFERING`, then for a partially buffered in-flight operation. If a match exists, it copies buffered data into user buffers and may complete immediately. Otherwise it queues a posted receive in `IND_RECV` with an expected mode inferred from size.

Progress is driven by test calls. `BMI_tcp_test`, `BMI_tcp_testsome`, `BMI_tcp_testcontext`, and `BMI_tcp_testunexpected` take `interface_mutex`, call `tcp_do_work` when necessary, then pop completed operations from completion queues or the unexpected queue.

`tcp_do_work` serializes readiness scanning with `sc_test_busy`. It drops the interface mutex around `BMI_socket_collection_testglobal`, then handles each ready address. Error readiness goes to `tcp_do_work_error`; write readiness goes to `tcp_do_work_send`; read readiness goes to `tcp_do_work_recv`. If another thread is already polling, callers either return immediately for zero timeout or timed-wait on `interface_cond`.

`tcp_do_work_send` repeatedly finds the first queued send for an address and calls `work_on_send_op`. Send work ensures a nonblocking connect has completed, calls `payload_progress` with header bytes plus payload iovecs, removes the write bit when complete, and moves the op to the context completion queue.

`tcp_do_work_recv` accepts server connections, resumes in-flight receives, peeks for a complete header, enforces a short-header timeout, validates the magic number, and dispatches by mode. Unexpected messages allocate a temporary buffer and go to `IND_RECV_INFLIGHT` until complete, then to `IND_COMPLETE_RECV_UNEXP`. Expected eager or rendezvous messages match `IND_RECV` if possible; unmatched eager payloads are buffered, while unmatched rendezvous messages stay in buffering state until a receive post arrives.

`payload_progress` builds up to `BMI_TCP_IOV_COUNT + 1` iovecs using the static `stat_io_vector`, optionally prepends remaining header bytes on sends, calls `BMI_sockio_nbvector`, and updates list index, current segment offset, and header completion counters.

## State And Persistence Behavior

All transport state is process-local memory: operation lists, address objects, socket fds, context completion queues, and global method parameters. There is no durable persistence. Socket failures are persisted only in the lifetime of `struct tcp_addr` through `addr_error`, `dont_reconnect`, `not_connected`, `zero_read_limit`, and `short_header_timer`.

The method relies on BMI-layer ownership for method addresses. `tcp_forget_addr` removes a live fd from the socket collection, shuts it down, moves matching operations into error completion queues with `tcp_cleanse_addr`, records the error on the address, and either deallocates or asks the BMI control layer to forget it later. Server-accepted connections set `dont_reconnect` because they cannot be recreated by hostname/port.

Send ordering is serialized per address through `IND_SEND`. Receive ordering is maintained through matched posted receives, in-flight receives, and buffered eager queues. Unexpected messages are persisted in memory until `BMI_tcp_testunexpected` frees their method op and the caller later frees the payload with `BMI_tcp_unexpected_free`.

## Dependencies And Integration Points

This file depends on OrangeFS BMI support (`bmi-method-support.h`, callbacks, address allocation, op ids), operation lists (`op-list.h`), socket utilities (`sockio.h`), TCP address metadata (`bmi-tcp-addressing.h`), byte swapping, gossip logging, locks/condition variables, PINT hints, and PINT events. It integrates with build-time socket collection selection through `__PVFS2_USE_EPOLL__`.

Runtime integration with the BMI layer happens through method registration (`bmi_tcp_ops`), address registration/forget/drop callbacks, context ids, BMI error codes, and method info options such as `BMI_TCP_BUFFER_SEND_SIZE`, `BMI_TCP_BUFFER_RECEIVE_SIZE`, `BMI_DROP_ADDR`, `BMI_FORCEFUL_CANCEL_MODE`, `BMI_TCP_CHECK_UNEXPECTED`, and trusted-connection configuration.

Optional `USE_TRUSTED` code reads server configuration, converts trusted networks/netmasks, binds client sockets to privileged local ports, and filters accepted server connections by peer network and source port.

## Risks And Edge Cases

- `BMI_tcp_method_addr_lookup` allocates `zone_len + 1` bytes but writes `zone[zone_len + 1] = '\0'`, which is one byte past the allocation. This is under `BMI_TCP_ZONE`.
- The first call to `bmi_set_sock_buffers(tcp_addr_data->socket)` in `tcp_sock_init` occurs before a new socket is created, so it can query/set fd `-1` during the no-socket path.
- In `tcp_post_send_generic`, the `#if PINT_EVENT_ENABLED` block accumulates `total_size`, but `total_size` is not a parameter or local in that function. If that preprocessor symbol is enabled without another macro side effect, this is a compile-time risk.
- `stat_io_vector` is static global state. The file comments rely on BMI serialization; misuse outside the `interface_mutex` discipline would corrupt vector progress.
- `BMI_tcp_test` assumes `id_gen_fast_lookup(id)` returns a valid operation and asserts. Invalid ids can crash in debug/assert builds.
- Unmatched eager messages allocate full payload buffers up to the eager limit. A peer can pressure memory by delivering many unmatched eager messages.
- Partial headers are handled by peeking until the full header is available and closing after `BMI_TCP_HEADER_WAIT_SECONDS`. Slow peers or scheduler stalls can become disconnects.
- Some socket collection paths assert on allocation failures instead of returning graceful BMI errors.
- Cancellation after any header/payload progress closes the socket and can error unrelated operations sharing the address.

## Test Signals

Useful tests should cover immediate and queued sends, send-list/recv-list iovec progress across buffer boundaries, eager receive posted before data, eager data buffered before receive post, rendezvous data before and after receive post, unexpected send/test/free, invalid magic/header timeout, remote close/error readiness, cancellation before and after progress, reconnect after client address failure, server accept and reverse lookup, context-specific completions, and both poll and epoll socket-collection builds. Trusted-mode builds should test accepted/rejected networks and source ports. Build coverage should include `PINT_EVENT_ENABLED`, `BMI_TCP_ZONE`, `USE_TRUSTED`, server, and client configurations.
