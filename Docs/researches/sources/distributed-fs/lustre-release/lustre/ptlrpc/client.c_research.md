# Research: sources/distributed-fs/lustre-release/lustre/ptlrpc/client.c

## Purpose
`client.c` implements the client-side PortalRPC core. It allocates and packs requests, manages bulk descriptors, assigns XIDs and bulk match bits, sends requests through imports, drives request-set state transitions, handles replies, timeouts, resends, adaptive timeouts, replay retention/commit cleanup, synchronous waits, and request reference/resource teardown.

## Important APIs, Types, And Functions
Major exported APIs include `ptlrpc_init_client()`, `ptlrpc_uuid_to_connection()`, `ptlrpc_prep_bulk_imp()`, `__ptlrpc_prep_bulk_page()`, `ptlrpc_free_bulk()`, `ptlrpc_at_set_req_timeout()`, `ptlrpc_at_get_net_latency()`, `ptlrpc_at_adj_net_latency()`, request cache/pool APIs, `ptlrpc_request_alloc()`, `ptlrpc_request_alloc_pool()`, `ptlrpc_request_alloc_pack()`, `ptlrpc_prep_set()`, `ptlrpc_set_add_req()`, `ptlrpc_check_set()`, `ptlrpc_set_wait()`, `ptlrpc_req_put()`, `ptlrpc_queue_wait()`, replay helpers, abort helpers, and XID helpers.

Important state lives in `struct ptlrpc_request`, `struct ptlrpc_request_set`, `struct obd_import`, `struct ptlrpc_bulk_desc`, and `struct ptlrpc_request_pool`. The file's static `request_cache` is the slab cache for requests, and `ptlrpc_last_xid` is the node-wide atomic XID counter.

## Control Flow
Request creation begins with `ptlrpc_request_alloc_internal()`, which allocates a request from the slab or optional pool, references the import, reconnects an idle import if needed, initializes a request capsule, and assigns the request format. `ptlrpc_request_pack()` obtains a security context, packs Lustre message buffers, initializes callbacks, portals, timeout, send state, opcode, and XID, and inserts the request into the import's unreplied list sorted by XID.

Bulk setup uses `ptlrpc_new_bulk()` to allocate a descriptor and bio_vec array, then `ptlrpc_prep_bulk_imp()` attaches it to a client request. `__ptlrpc_prep_bulk_page()` splits fragments across LNet MTU and `LNET_MAX_IOV` boundaries, growing `bd_md_count` and `bd_md_max_brw` as needed. `ptlrpc_free_bulk()` releases pool pages, import/export refs, fragment pins, and descriptor memory.

Request sets own caller references. `ptlrpc_set_add_req()` adds ordinary requests to `set_requests`, increments `set_remaining`, and sends immediately for producer sets. `ptlrpc_set_add_new_req()` queues ptlrpcd work on `set_new_requests` and wakes partner threads. `ptlrpc_queue_wait()` is the synchronous wrapper: allocate a set, add one referenced request, wait, destroy the set.

`ptlrpc_check_set()` is the main state machine. It sends NEW requests through `ptlrpc_send_new_req()`, delays requests when import recovery requires it, handles security-context waits, processes network errors/timeouts/resends, unregisters reply and bulk buffers, handles early replies and adaptive timeout updates, calls `after_reply()`, waits for bulk completion, moves to INTERPRET, invokes request interpreters, marks COMPLETE, removes requests from import sending/unreplied lists, decrements set/import counters, and produces more work for flow-controlled sets.

`after_reply()` unwraps and unpacks replies, handles truncated replies by resizing and resending when allowed, retries `-EINPROGRESS` unless disabled, records service statistics and adaptive timeout observations, validates reply type/status, triggers reconnect handling for recoverable errors, stores transnos, retains replayable requests, invokes commit callbacks for already committed requests, updates peer committed transno, and frees committed replay entries.

Timeout and resend logic is split across `ptlrpc_expire_one_request()`, `ptlrpc_expired_set()`, `ptlrpc_resend_req()`, and the resend branches in `ptlrpc_check_set()`. Expiration marks requests timed out, unregisters network buffers, optionally fails imports, and respects no-resend/recovery restrictions. Resends refresh security contexts, unregister old bulk, assign new match bits when appropriate, and call `ptl_send_rpc()` again.

Replay flow uses `ptlrpc_retain_replayable_request()` to keep transno-sorted replay requests, `ptlrpc_free_committed()` to prune replay and committed lists based on server committed transno/generation, and `ptlrpc_replay_req()` to reset a retained request for `LUSTRE_IMP_REPLAY` and queue it to ptlrpcd with `ptlrpc_replay_interpret()`.

## State And Persistence
The file manages volatile protocol state, but it is central to Lustre recovery semantics. Replay lists preserve enough request data in memory to replay committed-but-not-yet-confirmed operations after reconnect. XIDs are initialized from time or randomness and monotonically advanced in `PTLRPC_BULK_OPS_COUNT` increments so bulk match bits do not collide. Request phases (`NEW`, `RPC`, `BULK`, unregister phases, `INTERPRET`, `COMPLETE`) are the core lifecycle state.

Request buffers, reply buffers, security contexts, imports, bulk descriptors, request-set membership, unreplied/replay list entries, and pool ownership are all released in `__ptlrpc_free_req()` when the reference count reaches zero. Early reply buffers for large open RPCs can be freed before final request release to reduce memory pressure.

## Dependencies And Integration Points
`client.c` depends on LNet, Lustre import recovery, request capsules/layouts, SPTLRPC security, LDLM pool updates, lprocfs statistics, adaptive timeout helpers, ptlrpcd, and lower-level network send/unregister callbacks defined elsewhere. Higher layers such as OSC, MDC, MGC, LDLM, and batch code use these APIs for all client RPCs.

## Risks
This file is concurrency-sensitive. Request phase transitions depend on callback ordering from LNet and ptlrpcd. Returning a request to a pool before reply/bulk unlink completes can corrupt later users, which is why unregister phases are explicit. Replay list pruning must balance lock hold time against memory growth. XID/match-bit handling must remain collision-free across multi-bulk resends and old-server compatibility. Error paths in `ptlrpc_request_bufs_pack()` and request allocation must balance import references, security contexts, and pool ownership.

## Test Signals
Important tests include request allocation and pool fallback, bulk fragmentation at MTU and IOV boundaries, adaptive timeout/early reply behavior, import states NEW/CLOSED/INVALID/RECOVERY, no-resend vs resend timeouts, `-EINPROGRESS` retry, reply truncation resize, bulk failure after successful reply, replay retention and committed pruning, synchronous `ptlrpc_queue_wait()`, interruptible sets, flow-controlled producer sets, security context refresh waits, and fail hooks for long reply/bulk/request unlink and rounded XIDs.
