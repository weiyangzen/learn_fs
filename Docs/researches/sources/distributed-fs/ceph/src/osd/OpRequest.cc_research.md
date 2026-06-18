# sources/distributed-fs/ceph/src/osd/OpRequest.cc

## Purpose
`OpRequest.cc` implements the tracked wrapper around incoming OSD messages. `OpRequest` owns a `Message` reference, extracts request identity/source metadata, lazily derives operation read/write flags, records major scheduling/execution milestones for `TrackedOp`, exposes formatter dumps, releases heavyweight message resources after unregistering, and filters tracked operations by client address.

## Important APIs and Functions
The constructor initializes `TrackedOp` from the message receive stamp, stores the raw `Message*`, adjusts warning intervals for low-priority work, extracts `reqid` from `MOSDOp`, `MOSDRepOp`, or `MOSDRepOpReply`, and records the source instance. `_dump()` writes the current flag point, optional client info, and the tracked event timeline with per-event duration. `_dump_op_descriptor()` delegates to `Message::print()`. `_unregistered()` clears data/payload, releases throttles, and drops the connection pointer.

`maybe_init_op_info()` lazily populates `OpInfo` from a `MOSDOp` and `OSDMap`, then emits an LTTng tracepoint when tracing is enabled. `mark_flag_point()` and `mark_flag_point_string()` add tracked events, update `last_event_detail`, OR in the reached flag, set the latest flag, and trace the transition. `filter_out()` parses filter strings as `entity_addr_t` values and matches the request source address with exact, nonce-zeroed, and port-zeroed forms.

## Control Flow
Request processing code creates an intrusive `OpRequestRef`, then marks milestones as the request moves through PG queueing, PG entry, delay, start, sub-op wait, and commit-sent phases. The first code path that needs semantic operation flags calls `maybe_init_op_info()`; later accessors in the header read cached `OpInfo`. Administrative tracking calls `_dump()` and `_dump_op_descriptor()` through the `TrackedOp` interface. When the op leaves tracking, `_unregistered()` strips message buffers and connection references to reduce memory pressure and avoid stale connection retention.

## State and Persistence
All state is in memory and tied to the lifetime of the `OpRequest`. Persistent effects come only from the operation that later uses the request, not from `OpRequest` itself. Important state includes the owned message pointer, `reqid`, source instance, accumulated/recent flag points, last event detail, dequeued time, `hitset_inserted`, optional coroutine handles, `osd_parent_span`, map epoch fields, and lazy `OpInfo`.

## Dependencies and Integration Points
The implementation depends on `TrackedOp`, Ceph formatting, message classes (`MOSDOp`, `MOSDRepOp`, `MOSDRepOpReply`), `OSDMap`, operation utility parsing (`OpInfo::set_from_op()`), Ceph config priorities, message throttle/connection APIs, and optional LTTng tracepoints. PG request queues, OSD schedulers, op trackers, tracing, and admin dump paths all consume its state.

## Risks
`maybe_init_op_info()` casts the request to `MOSDOp` and should only be called for client op messages. `last_event_detail` stores a raw `const char*`; the string overload marks an event but does not update `last_event_detail`, so delayed-state reporting relies on callers passing stable C strings to `mark_delayed()`. `filter_out()` returns true when no valid filter addresses parse, which is easy to misread. `_unregistered()` clears connection/data, so later code must not expect payloads or connection state after unregistering.

## Test Signals
Tests should cover construction for each supported message type, lazy `OpInfo` initialization and idempotence, state-string transitions for every mark method, dump output with and without client sources, unregister resource clearing, tracing-neutral builds, and address filtering with full address, nonce-zeroed, port-zeroed, and invalid filters.
