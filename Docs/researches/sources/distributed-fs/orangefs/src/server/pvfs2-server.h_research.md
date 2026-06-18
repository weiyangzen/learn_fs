# sources/distributed-fs/orangefs/src/server/pvfs2-server.h

## Purpose
This header is the central server-side contract for OrangeFS/PVFS2 request handling. It defines initialization flags, reserved Trove metadata keys, permission and scheduler metadata hooks, request-specific scratch structures, and the large `PINT_server_op` state object passed through server state machines.

## Important APIs, Types, and Functions
- `PINT_server_req_permissions` classifies request permission checks: invalid, write, read, none, attribute ownership, and create-directory-entry write/execute checks.
- `Trove_Common_Keys` and `Trove_Special_Keys` are external key tables indexed by the reserved and optional metadata-key enums.
- `PINT_server_status_flag` tracks server subsystem initialization and cleanup responsibility for gossip, config, BMI, Trove, Flow, Job, request scheduler, state machines, precreate pools, security caches, and similar subsystems.
- Request operation scratch structs include creation, lookup, directory reads and mutations, remove, mkdir, getattr/listattr/eattr, I/O, mirroring, immutable-copy creation, tree operations, and performance updates.
- `PINT_server_op` is the main per-request state record. It carries queue links, cancellation/unexpected-message fields, operation type, event timing, scheduler id, generic keyval buffers, target attributes, client address/tag, decoded and encoded request/response objects, message-array state, prelude/scheduler metadata, and the request-specific union.
- `PINT_server_req_params` binds each request type to a string name, permission callback, access-type callback, scheduler policy, object-reference extractor, credential extractor, and the state machine that implements it.
- `PINT_CREATE_SUBORDINATE_SERVER_FRAME` allocates and initializes subordinate server operation frames, choosing local execution or remote msgarray setup based on handle placement and host id.
- Public helpers include request-table lookup functions, access-debug wrappers, keyval buffer ownership helpers, unexpected receive posting, state-machine lifecycle functions, and no-request state-machine entry points.

## Control Flow and State
Incoming server requests are decoded into `PINT_server_op`, then table-driven metadata from `PINT_server_req_table` selects permission checking, access classification, scheduling policy, object reference, credential, and state machine. The `prelude_mask` records prelude work such as permission checks before the operation-specific state machine consumes the relevant union member. Subordinate server frames allow nested/pjump state machines to reuse the same structure while resetting operation-specific state.

## State and Persistence Behavior
This header does not persist data directly, but it defines the handles, filesystem ids, Trove keyvals, object attributes, distribution metadata, mirror state, and encoded responses used by persistent server state machines. The reserved key enums are part of the persistent metadata namespace, so changes to indexes or meanings can affect on-disk Trove compatibility.

## Dependencies and Integration Points
It depends on core OrangeFS subsystems: BMI messaging, Trove storage, job/flow systems, request protocol encoding, state machines, cached configuration, performance counters, events, and mirror/distribution support. The request scheduler integrates through `scheduled_id`, `access_type`, `sched_policy`, and the request parameter table. State machine modules integrate through the declared external `PINT_state_machine_s` symbols.

## Risks and Edge Cases
- `PINT_server_op` is a broad shared mutable structure; state machines must clean only the fields they own and use the correct union member for `op`.
- The subordinate-frame macro has several side effects, allocates memory, and can return from the caller on allocation failure.
- Reserved Trove key enum order is ABI-like for metadata lookup and must stay synchronized with table definitions.
- Scheduler and permission callbacks rely on every request table entry being populated consistently.
- Ownership for capability, keyval buffers, encoded/decoded data, and nested frames is manual.

## Test Signals
No tests are in this header. Coverage is indirect through server state-machine tests and integration tests that exercise request decoding, permission prelude, scheduling, Trove metadata, mirroring, and nested server-to-server operations.
