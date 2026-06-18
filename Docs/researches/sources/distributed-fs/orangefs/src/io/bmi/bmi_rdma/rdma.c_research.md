# sources/distributed-fs/orangefs/src/io/bmi/bmi_rdma/rdma.c

## Purpose
`rdma.c` implements the OrangeFS BMI method named `bmi_rdma`. It adapts the BMI nonblocking send/receive API to RDMA CM and libibverbs, managing method address parsing, client/server connection setup, queue pair creation, eager-buffer flow control, rendezvous transfers for larger messages, memory registration, cancellation, polling, and shutdown. The exported integration point is the `bmi_rdma_ops` method table at the end of the file.

The implementation uses two transfer paths. Small payloads fit in a per-connection eager buffer and are sent with `IBV_WR_SEND`. Larger expected sends use an RTS/CTS protocol: the sender posts `MSG_RTS`, the receiver pins its destination buffers and replies with `MSG_CTS` containing remote addresses, lengths, and rkeys, the sender posts one or more `IBV_WR_RDMA_WRITE` requests, and finally sends `MSG_RTS_DONE` so the receiver can deregister memory and report completion.

## Important APIs, Types, and Functions
The BMI-facing entry points are all static functions installed in `bmi_rdma_ops`: `BMI_rdma_initialize`, `BMI_rdma_finalize`, `BMI_rdma_set_info`, `BMI_rdma_get_info`, `BMI_rdma_memalloc`, `BMI_rdma_memfree`, `BMI_rdma_unexpected_free`, `BMI_rdma_post_send`, `BMI_rdma_post_sendunexpected`, `BMI_rdma_post_send_list`, `BMI_rdma_post_sendunexpected_list`, `BMI_rdma_post_recv`, `BMI_rdma_post_recv_list`, `BMI_rdma_testcontext`, `BMI_rdma_testunexpected`, `BMI_rdma_method_addr_lookup`, `BMI_rdma_open_context`, `BMI_rdma_close_context`, `BMI_rdma_cancel`, and `BMI_rdma_rev_lookup`.

Core internal helpers include `check_cq` and `get_one_completion` for completion queue progress; `msg_header_init`, `post_sr`, `post_sr_rdmaw`, `post_rr`, and `repost_rr` for wire posting and credit return; `encourage_send_waiting_buffer`, `encourage_send_incoming_cts`, `encourage_recv_incoming`, `encourage_rts_done_waiting_buffer`, and `send_cts` for protocol state transitions; `post_send` and `post_recv` for common BMI operation setup; `test_sq` and `test_rq` for completion reporting; `rdma_client_connect`, `rdma_client_event_loop`, `rdma_server_init_listener`, `rdma_server_listener_thread`, and `rdma_server_accept_client_thread` for RDMA CM handling; and `build_rdma_context`, `alloc_connection`, `rdma_new_connection`, `register_memory`, `build_qp_init_attr`, `verify_qp_caps`, `rdma_close_connection`, and `cleanup_rdma_context` for device and connection lifecycle.

Important local state includes the global `rdma_device`, the module method id `bmi_rdma_method_id`, `interface_mutex`, listener-thread globals, and the global listen backlog. The file-local `struct rdma_conn_info` stores an RDMA CM id, peer host, port, and display name for each connection.

## Control Flow
Initialization starts in `BMI_rdma_initialize`. It validates that `listen_addr` matches `BMI_INIT_SERVER`, allocates `rdma_device`, initializes the memory cache callbacks, initializes listener state for servers, initializes global connection/send/receive lists, and sets eager buffer defaults. The RDMA verbs context is not fully built at initialization; `build_rdma_context` is called lazily from the first `rdma_new_connection` using the CM id's device context.

Address lookup parses strings like `rdma://hostname:port/filesystem` via `BMI_rdma_method_addr_lookup`. It strips the scheme with `string_key`, splits hostname and port, reuses an existing connected `remote_map` when possible, or allocates a client-side method address with `reconnect_flag` set. `ensure_connected` uses that flag to call `rdma_client_connect` when a BMI post targets an unconnected client address.

Client connection setup converts the port to a service string, resolves with `rdma_getaddrinfo`, creates an RDMA CM event channel and id, calls `rdma_resolve_addr`, then drives `rdma_client_event_loop`. The client event loop handles address resolution, route resolution, connection creation, `rdma_connect`, established events, address/route failures, and rejected connections. Server setup binds and listens on an RDMA CM id, makes the event fd nonblocking, and starts `rdma_server_listener_thread`. The listener polls for CM events, dispatches connect requests to `rdma_server_accept_client_thread`, and on established events allocates/registers a permanent BMI method address for the client.

`rdma_new_connection` allocates connection state, builds the global RDMA context if needed, registers eager send/receive buffers, creates a reliable connected QP through `rdma_create_qp`, verifies capabilities, and posts one receive work request for every eager receive buffer. `alloc_connection` places the connection on `rdma_device->connection`, initializes free buffer lists, and gives the peer all but one initial send credit.

BMI sends flow through `post_send`. The function locks `interface_mutex`, ensures connectivity, allocates an `rdma_work` send item and a BMI `method_op`, constructs a single-buffer or list `rdma_buflist_t`, validates the caller's total length, rejects oversize unexpected sends, queues the work on `rdma_device->sendq`, registers the op id with `id_gen_fast_register`, and calls `encourage_send_waiting_buffer`. If an eager send buffer and send credit are available, that helper emits either `MSG_EAGER_SEND`/`MSG_EAGER_SENDUNEXPECTED` plus payload or `MSG_RTS` plus length and mop id, registers the sender buffer list for large sends, and moves the send state forward.

BMI receives flow through `post_recv`. It locks, ensures connectivity, polls the CQ once, then either matches an already-arrived eager/RTS receive waiting for a user post or allocates a new receive work item in `RQ_WAITING_INCOMING`. It builds the destination buflist, validates the expected total length, registers a method op, handles already-arrived eager data by copying out and reposting the eager receive buffer, handles already-arrived RTS data by registering destination memory and sending CTS, and pre-registers large posted buffers that might later receive an RTS.

Progress is driven by `BMI_rdma_testcontext` and `BMI_rdma_testunexpected`. `BMI_rdma_testcontext` locks, repeatedly calls `check_cq`, walks all send and receive queues, and calls `test_sq`/`test_rq` to either reap matching-context completions or advance operations blocked on buffer availability. If there is no activity and the caller allows blocking, it drops the lock and polls the CQ/async fds through `rdma_block_for_activity`. `BMI_rdma_testunexpected` similarly checks the CQ and scans for `RQ_EAGER_WAITING_USER_TESTUNEXPECTED`, copying the unexpected payload into a freshly allocated BMI buffer and reposting the eager receive buffer.

`check_cq` is the core protocol dispatcher. It polls one completion at a time. Receive completions decode the common header, add returned credits, and route CTS messages to the send state machine or other messages to the receive state machine. RDMA write completions deregister sender memory, move the send to `SQ_WAITING_RTS_DONE_BUFFER`, and try to emit `MSG_RTS_DONE`. Send completions return eager send buffers and update send/receive work states for eager, RTS, CTS, and RTS_DONE sends. Error completions mark operations or connections and can call `rdma_close_connection` once reference counts permit.

Shutdown in `BMI_rdma_finalize` sends `MSG_BYE` to active connections, calls `rdma_disconnect`, polls until per-connection `refcnt` is zero, closes every connection, shuts down the server listener thread and listen id when present, shuts down the memory cache, destroys CQ/channel/PD state, frees `rdma_device`, and clears the global pointer.

## State and Persistence Behavior
The file maintains in-memory runtime state only; there is no on-disk persistence. The main persistent-for-process object is `rdma_device_t`, which owns the connection list, outstanding send and receive queues, memory cache handle, eager-buffer sizing, RDMA verbs context, CQ, PD, completion channel, SG scratch array, and unsignaled-send counters.

Each `rdma_connection_t` owns eager send/receive memory, registered MRs for those eager regions, buffer-head arrays, free lists, credit counters, CM id, QP, BMI address, cancellation/closed flags, and a reference count. `refcnt` is incremented when send/receive/RDMA write work requests are posted and decremented on completions; `rdma_close_connection` only frees resources when it reaches zero.

Outstanding BMI operations are represented as `struct rdma_work` items on `sendq` or `recvq`. They hold type, method op pointer, connection, buflist metadata, optional local eager buffer head, BMI tag, protocol state, unexpected flag, RTS mop id, and actual receive length. BMI op ids are registered in the id generator and removed when `test_sq`/`test_rq` reaps an operation or cancellation completion.

Flow control is credit based. Each connection starts with `eager_buf_num - 1` send credits, and received messages carry returned credits through `msg_header_common_t.credit`. `repost_rr` increments `return_credit` and may emit an explicit `MSG_CREDIT` when credits accumulate. Holding an unexpected or unmatched eager buffer delays reposting and therefore withholds credit until the user consumes or posts a matching receive.

Memory registration state is split between eager per-connection MRs and the shared memcache. Large send and receive buflists are registered before RDMA write access, then deregistered on RDMA write completion, RTS_DONE receipt, cancellation, or eager-shortfall paths. `mem_register` stores MR handle, lkey, and rkey in `memcache_entry_t.memkeys`.

## Dependencies and Integration Points
This file depends on OrangeFS BMI support (`bmi-method-support.h`, `bmi-method-callback.h`, `bmi-types.h` through `rdma.h`), id generation (`id-generator.h`), byte-order helpers (`bmi-byteswap.h` and generated encode/decode stubs), generic locks and threads, gossip logging, PVFS error mapping/status formatting, and `string_key`/internal utility helpers.

The external networking dependencies are RDMA CM (`rdma/rdma_cma.h` through `rdma.h`) and libibverbs (`infiniband/verbs.h`). The implementation uses RDMA CM for address resolution, route resolution, connect/listen/accept/disconnect, CM ids and event channels. It uses verbs for PD allocation, CQ and completion channel creation, QP creation through RDMA CM, memory registration, posting send/recv/RDMA-write work requests, polling CQ, async events, and resource destruction.

The memory cache interface is implemented in another file (`mem.c`) and called through `memcache_init`, `memcache_memalloc`, `memcache_memfree`, `memcache_register`, `memcache_preregister`, `memcache_deregister`, `memcache_cache_flush`, and `memcache_shutdown`. `rdma.c` supplies the verbs-backed `mem_register` and `mem_deregister` callbacks.

`util.c` supplies logging, allocation, queue deletion, state-name helpers, and scatter/gather copy helpers. `rdma.h` defines shared state types, wire headers, states, and debug/assertion macros.

## Risks and Edge Cases
Several error paths report errors but do not fully unwind partial allocations. For example, `post_send` can jump to `out` after allocating `sq` for a total-length mismatch without freeing it, and `post_recv` can similarly leave a partially initialized receive item/method op on error. Connection setup failures also rely heavily on `rdma_close_connection` handling partially initialized fields.

The locking model is broad but mixed with threads. Most BMI operations use `interface_mutex`, and the server accept thread holds it around `rdma_new_connection` and `rdma_accept`, while the listener thread handles established events and modifies connection method addresses. This reduces races but may expose ordering issues around CTS arriving before sender state changes; comments in the code explicitly call out such concerns.

The cancellation path assumes `id_gen_fast_lookup(id)` succeeds and immediately dereferences `mop->method_data`; invalid or already-reaped ids could crash. It also closes the entire connection for many in-flight cancel cases, which is simple but has a large blast radius for other operations sharing that connection.

There is a likely id-generator bug in `test_rq`: when completing a receive with `rq->mop`, it calls `id_gen_fast_unregister(rq->mop->user_ptr)` instead of `rq->mop->op_id`. The cancellation and error paths use `op_id`, so this completion path may leak or corrupt id-generator state depending on `user_ptr`.

`post_sr` always sets `IBV_SEND_SIGNALED` while maintaining `num_unsignaled_sends`; comments suggest the intended unsignaled-send design is not actually implemented. This is safer for completion-driven buffer recycling but makes the unsignaled counter misleading and may alter CQ pressure/performance expectations.

Wire validation is limited. CTS size is checked against the expected variable-length encoding, and buffer sizes are checked before copies, but rkeys and remote addresses are trusted after CTS decode. Comments question rkey security. Malformed or hostile peers could stress error paths.

`error`, `warning`, and related helpers in `util.c` use `vsprintf` into fixed-size buffers, so long format expansions from this file can overflow local logging buffers. Several fatal server setup failures call `exit(1)` instead of returning an error through BMI initialization.

`BMI_rdma_initialize` calls `rdma_server_init_listener` before initializing `rdma_device->connection`, `sendq`, `recvq`, and eager sizes. The listener thread can in principle accept a connection and call `rdma_new_connection` before those fields are initialized, depending on scheduling. Moving list/eager initialization before listener startup would reduce that race.

`rdma_close_connection` behaves differently for client/server CM event channels and can block on client CM events while holding the interface mutex in finalize paths. If the expected disconnect event is not delivered, shutdown behavior can stall.

## Test Signals
Useful static test signals include successful compilation with RDMA CM/libibverbs headers, warning-free builds around pointer/integer conversions, and unit/static checks for id-generator unregistering in `test_rq`. A focused code audit should verify every `id_gen_fast_register` has the correct unregister path.

Functional tests should cover client connect, server accept, small expected eager send/recv, small unexpected send/testunexpected/unexpected_free, large expected RTS/CTS/RDMA-write/RTS_DONE transfer, list sends/receives with multiple SG entries, sends that are smaller than a large posted receive, and receive-before-send plus send-before-receive ordering.

Reliability tests should exercise connection refusal, address resolution failure, route retry, disconnect/BYE handling, cancellation of completed and in-flight sends/receives, memory registration ENOMEM with cache flush retry, credit exhaustion/recovery, and finalize with outstanding requests. RDMA hardware or software RDMA integration testing is needed because most behavior depends on real CQ/CM event ordering.
