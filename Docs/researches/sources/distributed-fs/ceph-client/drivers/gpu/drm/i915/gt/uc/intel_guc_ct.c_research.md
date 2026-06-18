## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ct.c

Purpose: implements GuC Command Transport (CT), the shared-buffer transport replacing many MMIO command paths. It allocates H2G and G2H circular buffers, registers them with GuC, sends synchronous and nonblocking HXG messages, receives GuC events/responses, dispatches events to subsystem handlers, and reports dead CT conditions in debug builds.

Important APIs, types, and functions:
- Internal `ct_request` tracks synchronous request fence, status, and optional response buffer. `ct_incoming_msg` stores copied G2H messages for response/event processing.
- Lifecycle: `intel_guc_ct_init_early()`, `intel_guc_ct_init()`, `intel_guc_ct_enable()`, `intel_guc_ct_disable()`, and `intel_guc_ct_fini()`.
- Send path: `intel_guc_ct_send()` chooses `ct_send()` or `ct_send_nb()`. `ct_write()` encodes the CT header, HXG header, action data, fence, updates local/firmware tails, and notifies GuC.
- Flow control: `h2g_has_room()`, `g2h_has_room()`, G2H credit reserve/release helpers, `has_room_nb()`, and `ct_deadlocked()`.
- Receive path: `intel_guc_ct_event_handler()`, `ct_receive_tasklet_func()`, `ct_read()`, `ct_handle_msg()`, `ct_handle_hxg()`, `ct_handle_response()`, and `ct_handle_event()`.
- Event dispatch: `ct_process_request()` calls GuC submission, deregistration, context reset, state capture, engine failure, log flush, crash, and TLB invalidation handlers.
- Diagnostics: `intel_guc_ct_print_info()` and debug-only `ct_dead_ct_worker_func()` with `CT_DEAD()` reasons.

Control flow:
- Early init initializes locks, pending/incoming lists, work items, tasklet, and waitqueue.
- Full init allocates one GuC-mapped blob containing send/receive descriptors and buffers. Send is 4 KiB, receive is 16 KiB, and receive reserves one quarter for unexpected G2H traffic.
- Enable resets descriptors, registers receive then send buffer addresses/sizes via self-config KLVs, sends CTB enable over MMIO, and marks CT enabled.
- Synchronous sends reserve maximal G2H response space, insert a stack `ct_request` into the pending list, write the H2G message, notify GuC, wait for matching response by fence, handle retry responses, copy payload/status, then unlink and release credits.
- Nonblocking sends use `MAKE_SEND_FLAGS()`-style credit sizing, reserve expected G2H space, write with `FAST_REQUEST` type, notify GuC, and return without a pending request.
- Interrupt/event handling reads one G2H CTB message at a time under the receive lock. Responses update pending `ct_request`s. Events either release reserved credits and queue a work item, or process TLB invalidation completion immediately to unblock other flows.

State and persistence:
- `ct->vma` persists the descriptor/buffer blob until fini. Local `head`, `tail`, and `space` shadow firmware descriptor state.
- `ct->requests.pending` holds stack-backed synchronous requests while blocked. `ct->requests.incoming` holds heap-allocated G2H events waiting for workqueue processing.
- `ct->enabled`, per-buffer `broken`, and `stall_time` gate operations and deadlock detection. Debug builds keep lost-and-found fence/action records and dead-CT reporting state.

Dependencies and integration points:
- Uses GuC ABI headers for CTB/HXG bitfields and action ids, `intel_guc_send_mmio()` for CTB enable/disable, GuC self-config KLV helpers for buffer registration, and `intel_guc_notify()` for doorbell/interrupt notification.
- Dispatches to GuC submission, scheduling, deregistration, context reset, error capture, engine failure, log, crash, and TLB invalidation code.
- Uses Linux tasklets, workqueues, spinlocks, atomics, wait helpers, and circular-buffer macros.

Risks:
- CT is concurrency-sensitive: descriptor head/tail corruption, missed barriers, wrong G2H credit accounting, or processing events in the wrong context can deadlock GuC communication.
- Synchronous request objects are stack allocated; response handling must only reference them while linked and the caller is waiting.
- `ct_deadlocked()` has a probable typo assigning both `send` and `recv` descriptor pointers from `ct->ctbs.send.desc`, which can misreport receive descriptor status.
- Event dispatch failures mark CT dead in debug builds and can force broad error capture.

Test signals:
- Unit/selftest CT send paths for synchronous, retry, response payload, nonblocking, no-room, and disabled cases.
- Fault injection on `intel_guc_ct_init()` allocation and corrupted descriptor status/head/tail.
- Stress GuC submission with high G2H traffic, TLB invalidations, log flushes, and state capture notifications.
- Verify `intel_guc_ct_print_info()` and dead-CT klog capture under debug configs.
