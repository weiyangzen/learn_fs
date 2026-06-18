# sources/distributed-fs/ceph/src/mon/MonOpRequest.h

## Purpose

`MonOpRequest.h` defines the tracked operation wrapper used by monitor code to carry a received `Message` through dispatch, service handling, Paxos waits, forwarding, command processing, and callbacks. It extends `TrackedOp` so monitor operations can be observed in slow-op/historic-op dumps with event timings and request descriptors.

It also defines `C_MonOp`, a callback base class that retains a `MonOpRequestRef` and marks completion, retry, or cancellation events before delegating to subclass-specific `_finish()`.

## Important APIs, types, and fields

`MonOpRequest` inherits from `TrackedOp` and is reference-counted through `boost::intrusive_ptr` as `MonOpRequest::Ref` / `MonOpRequestRef`.

Important fields:

- `Message *request`: the underlying monitor message. The destructor releases it with `put()`.
- `RefCountedPtr session`: retained monitor session private data, usually a `MonSession`.
- `ConnectionRef con`: source connection captured from the message.
- `bool forwarded_to_leader`: diagnostic flag set by `mark_forwarded()`.
- `op_type_t op_type`: coarse request classification.
- `utime_t dequeued_time`: declared but not manipulated in this header.

Important methods:

- Event markers: `mark_dispatch()`, `mark_wait_for_quorum()`, `mark_zap()`, `mark_forwarded()`, `mark_svc_event()`, and service-specific helpers for log, OSD map, PG map, MDS map, auth, and Paxos events.
- Request/session access: `get_req<T>()`, `get_req()`, `get_req_type()`, `get_connection()`, `get_session()`, and `set_session()`.
- Source checks: `is_src_mon()`.
- Type setters/getters: `set_type_service()`, `set_type_monitor()`, `set_type_paxos()`, `set_type_election_or_ping()`, `set_type_command()`, `get_op_type()`, and `is_type_*()` helpers.
- Debug output overrides: `_dump()` and `_dump_op_descriptor()`.

`C_MonOp` APIs:

- `finish(int r)` marks `"callback canceled"`, `"callback retry"`, or `"callback finished"` for `-ECANCELED`, `-EAGAIN`, or `0` before calling `_finish(r)`.
- `mark_op_event()` lets subclasses add arbitrary events.
- `_finish(int r)` is pure virtual for concrete callback behavior.

## Control flow

`MonOpRequest` construction is private and intended for `OpTracker` creation. The constructor initializes `TrackedOp` with the message receive timestamp when available or `ceph_clock_now()` otherwise, stores the raw request pointer, captures the connection, and reads the connection private pointer as the monitor session.

During monitor processing, dispatchers and services call event marker methods to append timestamped entries to the underlying `TrackedOp`. `mark_forwarded()` also flips `forwarded_to_leader` for dump output. `set_type_*()` calls classify the operation so monitor diagnostics can distinguish service, monitor, election, Paxos, and command paths.

Dumping opens an `events` array, locks the inherited event list, emits each event and duration to the next event or from initiation to the last event, then emits request info such as sequence, source-is-monitor, source instance, and forwarded flag. `_dump_op_descriptor()` delegates to the underlying message `print()`.

`C_MonOp::finish()` is a callback control-flow hook: it annotates the retained operation based on the completion code and then calls subclass `_finish()`.

## State and persistence behavior

This file does not persist cluster state. Its state is operational telemetry and request lifetime management:

- It keeps the underlying `Message` alive until the wrapper is destroyed.
- It retains the monitor session and connection for authorization, routing, and diagnostics.
- It records an event timeline used by operation tracking, slow-op reporting, historic-op dumps, and admin diagnostics.
- It records whether the request was forwarded to the leader and its high-level type.

Because `MonOpRequest` wraps monitor messages that may trigger Paxos updates, losing or misclassifying the wrapper affects observability and routing decisions but not direct persistence serialization.

## Dependencies

The header depends on `TrackedOp`, `RefCountedObj`, `Context`, `Formatter`, `Session.h`, `Connection.h`, and `Message.h`. It is included widely by monitor services such as `Monitor`, `PaxosService`, `Paxos`, `Elector`, `OSDMonitor`, `MDSMonitor`, `AuthMonitor`, `LogMonitor`, `ConfigMonitor`, `KVMonitor`, `MgrMonitor`, and health/NVMe monitor code.

Integration points:

- `OpTracker` is a friend and constructs instances.
- Monitor dispatch uses `MonOpRequestRef` as the common request handle.
- Paxos wait callbacks commonly derive from or use `C_MonOp`.
- Admin/historic operation dump code consumes `_dump()` and `_dump_op_descriptor()`.

## Risks and edge cases

- The destructor unconditionally calls `request->put()`. The constructor accepts `Message *req` and several methods handle null, but `_dump()`, `_dump_op_descriptor()`, and the destructor assume a non-null request. Creation should not pass null in production.
- `_dump()` uses `request->get_source_inst()` and event timing while holding the event lock for event iteration. Code changes should avoid introducing lock inversions with formatter or message code.
- `is_src_mon()` uses bitwise `get_peer_type() & CEPH_ENTITY_TYPE_MON`, relying on entity type bit conventions.
- Session capture happens at construction from connection private data. If connection private state changes later, the wrapper may retain the earlier session unless `set_session()` is called.
- Event strings are free-form. Inconsistent naming reduces diagnostic value and can break tooling that expects known event labels.
- `op_type_t` is diagnostic but may be used for filtering; new dispatch paths should set it consistently.

## Test signals

Useful tests include:

- Construction through `OpTracker` with messages that have and lack receive stamps, verifying initiated time selection.
- Request lifetime tests that ensure `put()` occurs exactly once when the wrapper is released.
- Event marker tests for dispatch, quorum wait, zap, forwarded, service-specific labels, and `C_MonOp::finish()` status mapping.
- Dump tests validating event duration fields, request source fields, forwarded flag, and op descriptor output.
- Session/connection tests for `get_session()`, `set_session()`, and `is_src_mon()`.
- Type classification tests covering every `set_type_*()` and `is_type_*()` helper.
