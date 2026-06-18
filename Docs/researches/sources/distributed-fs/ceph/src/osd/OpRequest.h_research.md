# sources/distributed-fs/ceph/src/osd/OpRequest.h

## Purpose
`OpRequest.h` declares the OSD's tracked operation wrapper. It bridges raw `Message` ownership, `TrackedOp` observability, operation semantic flags from `OpInfo`, request state milestones, source/request identity, coroutine handles, and map epoch gating used by PG and OSD scheduling code.

## Important APIs, Types, and Members
`OpRequest` derives from `TrackedOp` and is reference-counted through `boost::intrusive_ptr` as `OpRequestRef`. Public accessors expose `OpInfo` properties such as read/write/cache capability, read/write caps, promote/cache-skip behavior, return-vector allowance, EC direct/sync read flags, class info, and RMW ordering. `maybe_init_op_info(const OSDMap&)` is the lazy initializer.

Message APIs include templated `get_req<T>()`, `get_req()`, `get_nonconst_req()`, `get_source()`, `has_feature()`, and `get_reqid()`. State tracking APIs include `state_flag()`, `_get_state_string()`, static `get_state_string()`, `mark_queued_for_pg()`, `mark_reached_pg()`, `mark_delayed()`, `mark_started()`, `mark_sub_op_sent()`, and `mark_commit_sent()`. Map handling fields include `check_send_map`, `sent_epoch`, and `min_epoch`; other public state includes `hitset_inserted`, `osd_parent_span`, optional `CoroHandles`, and dequeued-time accessors.

Private state includes the owned raw `Message*`, `osd_reqid_t`, source instance, reached/latest flag bits, last event detail, dequeued time, and six milestone bit constants. Protected overrides implement dump descriptor, unregister cleanup, and filtering.

## Control Flow
The class takes over a single message reference at construction and releases it in the destructor with `request->put()`. Callers generally pass `OpRequestRef` through OSD and PG queues, marking milestones as the op advances. `TrackedOp` uses `_get_state_string()` and `_dump()` to report blocked/slow requests. Code that needs permissions or op semantics first calls `maybe_init_op_info()` and then uses the many thin accessors to avoid reparsing the request.

## State and Persistence
The wrapper is runtime-only. It owns a message reference and transient tracking fields but does not persist anything itself. The map epoch fields are important control state: `sent_epoch` tracks the client's map epoch, while `min_epoch` gates when the op can be handled. `hit_flag_points` records every reached milestone; `latest_flag_point` drives the current displayed state.

## Dependencies and Integration Points
The header depends on OSD op utilities/types, `TrackedOp`, tracing types, and coroutine handles. It forward-uses `OSDMap` in the initializer signature. Integration points include `OpTracker`, OSD scheduler items, PG wait queues, capability checks through `OpInfo`, LTTng tracepoints in the implementation, and Crimson-specific connection feature handling.

## Risks
The destructor unconditionally calls `request->put()`, so construction requires a non-null message reference. Many accessors assume `op_info` has been initialized; the header exposes `op_info_needs_init()` to help call sites avoid stale zero flags. `has_feature()` aborts under Crimson because Crimson keeps connection state separately. The public mutable fields simplify call-site integration but make invariants around map epochs and hitset insertion dependent on convention.

## Test Signals
Useful tests include intrusive reference lifetime, state transition strings, delayed detail behavior, lazy op-info requirement checks, map-wait field handling, connection feature behavior in non-Crimson builds, and tracked-op filter/dump integration. Request scheduling tests should verify milestones remain ordered and meaningful in slow-op diagnostics.
