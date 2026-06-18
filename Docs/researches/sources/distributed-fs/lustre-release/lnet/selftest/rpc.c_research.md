# sources/distributed-fs/lustre-release/lnet/selftest/rpc.c

## Purpose
Implements the SRPC transport layer for LNet Selftest: LNet lazy portals, passive request buffers, active reply/bulk RDMA, service registration, per-CPT state, client/server RPC state machines, counters, timers, aborts, shutdown, and LNet event handling.

## Important APIs And Functions
Service APIs include `srpc_add_service()`, `srpc_remove_service()`, `srpc_shutdown_service()`, `srpc_finish_service()`, and `srpc_abort_service()`. Buffer APIs include `srpc_service_add_buffers()`, `srpc_service_remove_buffers()`, and `srpc_add_buffer()`. Client APIs include `srpc_create_client_rpc()`, `srpc_post_rpc()`, `srpc_abort_rpc()`, and `srpc_send_rpc()`. Server and transport helpers include `srpc_handle_rpc()`, `srpc_send_reply()`, `srpc_lnet_ev_handler()`, `srpc_alloc_bulk()`, `srpc_init_bulk()`, `srpc_free_bulk()`, `srpc_startup()`, and `srpc_shutdown()`.

## Control Flow
Startup initializes LNet NI, lazy request portals, matchbits, and the selftest timer. Services allocate per-CPT state, preallocated server RPC descriptors, and request buffers posted as passive PUT MDs. Incoming LNet request events validate buffers and schedule server RPC workitems. Server work handles request dispatch, optional active bulk RDMA, optional `sv_bulk_ready`, and active PUT reply. Client work posts passive reply/bulk buffers, sends request, waits for request/reply/bulk events, and completes through caller callbacks. The LNet event handler records event status, updates counters, and reschedules owning workitems.

## State And Persistence
All state is volatile in `srpc_data` and service CPT structures. Counters are atomic. Matchbits are monotonic for the module lifetime. Client RPC timers use `stt_timer`. No persistence exists.

## Dependencies And Integration Points
Provides the base transport for framework, console, and tests. Depends on LNet APIs, workqueues from `module.c`, libcfs CPT/allocation helpers, spinlocks, atomics, lists, and `timer.c`.

## Risks
Asynchronous event ordering is subtle; completions depend on correct `ev_fired` updates. Shutdown requires services to be removed before `srpc_shutdown()` asserts an empty registry. Lazy buffer growth can fail under memory pressure. Reposting test buffers before replying creates lifetime sensitivity. Active RDMA failures rely on unlink events for completion.

## Test Signals
Service lifecycle, buffer growth/removal, client timeout/abort, malformed request drops, version mismatch, bulk counters, blocked buffers when no RPC descriptor is free, and shutdown with active RPCs.
