# subset-b-007851 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_rdma/rdma.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_rdma/rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_rdma/rdma.h -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_rdma/rdma.h

## Purpose
`rdma.h` is the private shared header for the OrangeFS BMI RDMA implementation. It defines the central connection, work-item, memory-cache, wire-protocol, and device-state data structures used by `rdma.c`, `util.c`, and the RDMA memory-cache implementation. It also declares internal helper APIs and wraps common debugging, assertion, pointer conversion, and compiler-attribute helpers.

## Important APIs, Types, and Definitions
The header sets default eager-buffer sizing with `DEFAULT_EAGER_BUF_NUM` and `DEFAULT_EAGER_BUF_SIZE`. The default is 20 buffers of 16 KiB per connection; the actual eager payload is reduced by the eager header size in `rdma.c`.

`rdma_connection_t` represents one peer connection. It links into the global device connection list, stores the peer BMI method address and `rdma_conn_info`, owns contiguous eager send/receive buffers plus corresponding free lists and `buf_head` arrays, tracks cancellation/refcount/closed state, tracks send and return credits, stores RDMA CM id/QP/MRs, and caches the BMI address registered with the BMI layer.

`struct buf_head` is the per-eager-buffer descriptor. It links into free lists, records an ordinal, owning connection, associated send or receive work item, and the backing buffer pointer. Completions use the buffer-head pointer as a work request id.

`rdma_method_addr_t` is the RDMA-specific `method_data` stored in a BMI method address. It stores hostname, port, current connection pointer, reconnect policy, and a reference count used by `BMI_DROP_ADDR`.

The send state machine is `sq_state_t`: waiting for eager buffer, waiting for eager send completion, waiting for RTS send completion, waiting for CTS, waiting for RDMA data send completion, waiting for RTS_DONE buffer/send completion, waiting for user test, cancelled, and error. The receive state machine is `rq_state_t`, a bitmask covering eager/RTS waiting-for-user-post states, waiting-for-test states, CTS-send and RTS_DONE states, waiting for incoming data, cancelled, and error. `msg_type_t` defines the on-wire message set: eager send, eager unexpected, RTS, CTS, RTS_DONE, CREDIT, and BYE.

When included by `util.c` with `__util_c` defined, the header also instantiates `name_t` arrays mapping send states, receive states, and message types to strings. Other files get only the state enums and function declarations.

`memcache_entry_t` describes one registered or registerable memory range, including list linkage, buffer pointer, length, reference count, and RDMA memory keys (`mrh`, `lkey`, `rkey`). `rdma_buflist_t` wraps a send or receive scatter/gather list, total length, and a parallel array of memory-cache entries.

`struct rdma_work` is the shared outstanding operation record for both sends and receives. It contains BMI type, owning `method_op`, connection, buflist, inline single-buffer storage, current eager buffer head, BMI tag, send/receive state union, unexpected flag, RTS mop id, and actual receive length.

The wire headers are `msg_header_common_t`, `msg_header_eager_t`, `msg_header_rts_t`, `msg_header_cts_t`, and `msg_header_rts_done_t`. Each is paired with `endecode_fields_*` declarations so the normal OrangeFS little-endian field encoder can serialize and deserialize messages. `MSG_HEADER_CTS_BUFLIST_ENTRY_SIZE` documents the per-receive-buffer variable CTS payload layout: address, length, and rkey.

`struct bmi_rdma_wc` normalizes verbs completions into a local form with id, status, byte length, and opcode (`BMI_RDMA_OP_SEND`, `BMI_RDMA_OP_RECV`, `BMI_RDMA_OP_RDMA_WRITE`). `rdma_device_t` owns global method state: listener id/address, connection/send/recv lists, memcache handle, eager sizing, verbs context/CQ/PD/completion channel, NIC capabilities, SG scratch array, and unsignaled-send counters.

The header declares utility functions from `util.c`, memory-cache functions from `mem.c`, the global `rdma_device`, pointer/integer conversion macros, `qlist_upcast`, branch-prediction macros, `debug`, and `bmi_rdma_assert`.

## Control Flow and Integration
`rdma.h` does not execute code, but it defines the control contracts used by the rest of the RDMA method. `rdma.c` moves `struct rdma_work` instances through the `sq_state_t` and `rq_state_t` states while processing BMI posts, RDMA completions, and user tests. It fills and decodes the message headers defined here for every eager, RTS/CTS, credit, and shutdown control message.

The endecode declarations integrate with `pvfs2-encode-stubs.h` and require `rdma.c` to define `__PINT_REQPROTO_ENCODE_FUNCS_C` before including protocol headers so encoder definitions are available. The named-state arrays are intentionally emitted only in `util.c` to avoid multiple definitions while still keeping enum-to-string data close to the enum declarations.

The memory-cache declarations are consumed by both the BMI method and the cache implementation. `rdma.c` supplies registration callbacks that fill `memcache_entry_t.memkeys`; `mem.c` is expected to manage allocation, caching, registration reference counts, preregistration, deregistration, and cache flushing.

## State and Persistence Behavior
All types represent process-local volatile state. Nothing in this header implies durable persistence. The strongest ownership relationships are: `rdma_device_t` owns global lists and verbs resources; each `rdma_connection_t` owns per-peer eager memory and queue-pair resources; each `struct rdma_work` owns one outstanding BMI operation's protocol state; `memcache_entry_t` owns or references one registered memory range.

The receive state enum is a bitmask, not a simple sequential enum. Code can set multiple receive bits simultaneously, for example waiting for RTS_DONE, CTS send completion, and user test. The send state enum is a single-state progression. This difference is central to interpreting state checks in `rdma.c`.

## Dependencies
The header depends on OrangeFS BMI types, quicklist, gossip logging, debug definitions, encode stubs, PVFS types, and RDMA CM. It also assumes libibverbs types through RDMA CM and through users that include verbs before or after the header. The debug macro depends on `GOSSIP_BMI_DEBUG_IB`.

## Risks and Edge Cases
The include guard and helper macros use double-underscore identifiers such as `__rdma_h`, `__hidden`, and `__unused`, which are reserved by C implementations. Existing project style may tolerate this, but it is not portable C hygiene.

The state-name arrays are `static` definitions conditional on `__util_c`; this works for one translation unit but is brittle if another source defines `__util_c` accidentally. `entry` is also a generic macro name, though it is undefined after use.

`ptr_from_int64` and `int64_from_ptr` cast through `unsigned long`. Comments acknowledge truncation behavior on 32-bit architectures. The code assumes work request ids and stored MR handles can round-trip through this representation; 32-bit support should be treated cautiously.

The CTS wire layout exposes raw remote addresses and rkeys. The header documents the layout but not any authentication or bounds protection. Correctness depends on RDMA RC connection trust and higher-level configuration.

`bmi_rdma_assert` logs through `error` but does not abort. In debug builds, failed assertions may leave execution continuing in a corrupt state.

## Test Signals
Compile tests should include `rdma.h` in more than one translation unit to catch accidental multiple-definition or macro exposure problems. State-name tests can verify every enum value maps to a non-unknown string in `util.c`. Protocol encoding tests should round-trip every wire header and verify CTS variable payload offsets match `MSG_HEADER_CTS_BUFLIST_ENTRY_SIZE`.

Static analysis should focus on pointer/work-request-id casts, reserved macro names, and bitmask use of `rq_state_t`. Integration tests need to confirm the constants and state definitions match the behavior expected by `rdma.c` and `mem.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_rdma/rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_rdma/util.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_rdma/util.c

## Purpose
`util.c` provides small support routines for the BMI RDMA method. It centralizes RDMA-specific logging helpers, checked allocation, quicklist pop helpers, enum-to-string lookup for debugging, and copying between contiguous buffers and `rdma_buflist_t` scatter/gather lists.

## Important APIs and Functions
`error`, `error_errno`, and `error_xerrno` format an error message and send it to `gossip_err`; the latter two append `strerror(errno)` or `strerror(errnum)`. `warning` is the analogous warning logger and is annotated with GCC printf-format checking.

`bmi_rdma_malloc` rejects zero-length allocations, calls `malloc`, logs on allocation failure, and returns the allocated pointer or `NULL`.

`qlist_del_head` removes and returns the first list node, logging an error on an empty list. `qlist_try_del_head` performs the same removal but returns `0` silently when the list is empty. Both return a raw `void *` pointer to the removed `qlist_head`, which callers cast or use via `qlist_upcast`.

`sq_state_name`, `rq_state_name`, and `msg_type_name` translate RDMA send states, receive states, and message types into static string names. They use the `name_t` arrays emitted by `rdma.h` when `__util_c` is defined before including it.

`memcpy_to_buflist` copies from a contiguous source buffer into a receive buflist, stopping once either the buflist is exhausted or the requested length has been copied. `memcpy_from_buflist` copies all entries from a send buflist into a contiguous destination buffer.

## Control Flow
The logging helpers are leaf functions used throughout `rdma.c` and likely other RDMA method files. They build a temporary stack string with varargs formatting and immediately log it.

The list helpers are used in resource-management paths such as eager-buffer allocation. `get_eager_buf` in `rdma.c` uses `qlist_try_del_head` to avoid logging when no send buffer is currently available, while harder invariants can use `qlist_del_head`.

The state-name helpers call a private `name_lookup` loop that scans until a sentinel `{0, 0}` entry. Unknown values return `"(unknown)"`. The lookup is exact, so composite receive-state bitmasks only resolve when a composite value happens to equal a named single flag; this matters because `rq_state_t` is intentionally bitwise.

The buflist copy helpers are used for eager protocol payloads. Eager sends gather user buffers into one registered eager send buffer before posting `IBV_WR_SEND`; eager receives scatter data out of an eager receive buffer into user receive buffers.

## State and Persistence Behavior
`util.c` has no durable state. Its only static state comes indirectly from the `sq_state_names`, `rq_state_names`, and `msg_type_names` arrays instantiated through `rdma.h`. All other functions operate on caller-owned buffers, lists, or stack temporaries.

The buflist copy helpers do not allocate, register, or retain memory. They assume the caller has already validated sizes and buffer directions. `memcpy_to_buflist` intentionally permits a shorter copy than the total receive buflist capacity, which supports receives smaller than posted buffers.

## Dependencies and Integration Points
The file includes standard C headers, defines `__util_c`, then includes `rdma.h` and `pvfs2-internal.h`. Defining `__util_c` causes the private state/message name tables in `rdma.h` to be instantiated here. It depends on OrangeFS gossip logging, quicklist layout, RDMA state enums, `rdma_buflist_t`, and BMI size types.

`rdma.c` relies on this file for `error*`, `warning`, allocation, state/message names in debug output, quicklist removal, and eager payload copies. The header exposes these functions as internal, not public BMI APIs.

## Risks and Edge Cases
The logging helpers use `vsprintf` into a fixed 2048-byte stack buffer. Long formatted messages can overflow the buffer. Replacing these calls with `vsnprintf` would reduce risk without changing callers.

`error` and `bmi_rdma_assert` style failures do not abort execution; they log and return. Callers that treat `error` as fatal may continue after broken invariants. Some code comments show previous `exit(1)` or backtrace behavior was intentionally disabled.

`bmi_rdma_malloc` logs failure but does not terminate. Several callers immediately dereference returned pointers, so allocation failure handling is inconsistent.

`qlist_del_head` returns `NULL` after logging an empty-list invariant violation, but callers must check. `qlist_try_del_head` returns integer `0` rather than `NULL`, equivalent in C but less idiomatic.

`rq_state_name` is not well suited for receive states that combine flags such as `RQ_RTS_WAITING_RTS_DONE | RQ_RTS_WAITING_CTS_SEND_COMPLETION | RQ_RTS_WAITING_USER_TEST`; it will report `"(unknown)"` for many valid composite states.

`memcpy_from_buflist` copies the entire buflist with no destination length parameter. Correctness depends on callers ensuring the contiguous destination has enough space. `memcpy_to_buflist` limits by `len` but does not report if bytes remain after all receive entries are filled.

## Test Signals
Unit tests can exercise empty and non-empty quicklist pop behavior, state/message name lookups including unknown values, and scatter/gather copies across one, multiple, partial, and zero-length remaining entries. Fuzz or boundary tests should check long log format strings after converting to bounded formatting. Static analysis should flag the unbounded `vsprintf` calls and destination-size-free `memcpy_from_buflist`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_rdma/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/bmi-tcp-addressing.h -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/bmi-tcp-addressing.h

## Purpose
`bmi-tcp-addressing.h` defines TCP-specific address state for the OrangeFS BMI TCP method. It is a private method header that records how a BMI method address maps to a TCP socket, peer host/port metadata, socket-collection bookkeeping, reconnect policy, partial-read tracking, and optional trusted-connection rules.

## Important APIs, Types, and Definitions
`BMI_TCP_ZERO_READ_LIMIT` is the maximum number of sequential zero-byte reads tolerated before treating a TCP connection as dead. `BMI_TCP_HEADER_WAIT_SECONDS` caps how long the TCP method waits for the rest of a partial BMI header after detecting part of it.

`BMI_TCP_PEER_IP` and `BMI_TCP_PEER_HOSTNAME` identify the interpretation of the `peer` field in `struct tcp_addr`.

When `USE_TRUSTED` is enabled, `struct tcp_allowed_connection_s` describes policy for accepted peers. It can enforce a port range, enforce network membership, store a count of allowed networks, and hold arrays of network and netmask `struct in_addr` values.

`struct tcp_addr` is the main TCP per-address record. It stores the owning generic BMI method address (`map`), BMI address id, address-level error code, hostname and zone strings, port, socket fd, server-port marker, pending write reference count, not-connected flag, socket collection link/index, sequential zero-read count, partial-header timer, reconnect suppression flag, peer string, and peer type.

The header aliases `bmi_tcp_errno_to_pvfs` to the shared `bmi_errno_to_pvfs` mapper, and declares `tcp_forget_addr` and `alloc_tcp_method_addr`.

## Control Flow and Integration
This header contains declarations and state layout rather than executable code. The TCP BMI implementation fills `struct tcp_addr` as addresses are parsed, connections are accepted or initiated, sockets are added to socket collections, reads/writes are posted, failures occur, and reconnect decisions are made.

`tcp_forget_addr` is the cleanup/invalidation entry point: callers pass a generic method address, a deallocation flag, and an error code. Based on the fields here, that function is expected to close or detach sockets, update address error state, remove socket collection links, and optionally free address storage. `alloc_tcp_method_addr` creates a generic BMI method address with enough TCP-specific private data to hold `struct tcp_addr`.

The zero-read and short-header constants are consumed by receive-side logic. `zero_read_limit` tracks repeated EOF-like reads that may signal dead peers. `short_header_timer` supports bounded waits for a complete BMI protocol header after a partial header arrives.

## State and Persistence Behavior
All state is process-local and tied to live TCP method addresses. `struct tcp_addr` persists as long as the generic BMI method address remains live. It can outlive a specific socket across reconnect attempts unless `dont_reconnect` is set or cleanup deallocates it.

`write_ref_count` tracks pending sends to avoid freeing or reconnecting address state while writes are active. `not_connected`, `addr_error`, and `dont_reconnect` together describe connection health and future reconnect behavior. `sc_link` and `sc_index` persist the address's membership in a socket collection.

No fields are written to disk by this header; persistence here means lifetime within the OrangeFS process and BMI address registry.

## Dependencies and Integration Points
The header depends on BMI core types through `bmi-types.h`, IPv4 address structures from `<netinet/in.h>`, and quicklist linkage through the `struct qlist_head` member made available by included BMI/common headers in the TCP implementation build context.

It integrates with the BMI TCP method's socket collection, method-address allocation, address-forget cleanup, reconnect logic, trusted-connection filtering, and BMI error mapping. It is separate from the RDMA files in this work item but plays a similar role for TCP private method address state.

## Risks and Edge Cases
The header is IPv4-centric: trusted network policy uses `struct in_addr`, and `struct tcp_addr` stores host/port as strings plus integer port without visible IPv6-specific fields. IPv6 support, if present elsewhere, would require additional handling.

The ownership of string fields (`hostname`, `zone`, and `peer`) is not documented here. Cleanup correctness depends on `tcp_forget_addr` and allocation/parsing code following consistent ownership rules.

`write_ref_count`, reconnect flags, socket collection indices, and socket fd state can become inconsistent if error paths do not update them together. The header exposes mutable fields directly, so invariants are distributed across implementation files.

`zero_read_limit` and `short_header_timer` are per-address counters/timers; tests should ensure they are reset on successful reads/reconnects and not inherited incorrectly across new sockets.

`USE_TRUSTED` policy stores arrays by pointer without lengths beyond `network_count`, so allocation and cleanup must keep those arrays synchronized. Port policy uses a two-element `ports` array whose ordering and inclusivity are not documented in the header.

## Test Signals
TCP method tests should cover address allocation and cleanup, hostname/zone/peer ownership, active write references during cleanup, server-port addresses, reconnect and `dont_reconnect` behavior, repeated zero-byte reads crossing `BMI_TCP_ZERO_READ_LIMIT`, partial-header timeout handling, socket collection add/remove bookkeeping, and trusted network/port filtering when `USE_TRUSTED` is enabled.

Static checks should verify every `struct tcp_addr` field is initialized in `alloc_tcp_method_addr` or address parsing paths, and that `tcp_forget_addr` clears socket collection links and frees owned strings consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/bmi-tcp-addressing.h -->
