# sources/distributed-fs/orangefs/src/server/request-scheduler/request-scheduler.h

## Purpose
This header declares the OrangeFS server request scheduler interface and its access/scheduling policy enums. It is the public API used by server request processing to post, test, unpost, and release scheduled work.

## Important APIs, Types, and Functions
- `req_sched_id` aliases `PVFS_id_gen_t`; `req_sched_error_code` aliases `int`.
- `PINT_server_req_access_type` distinguishes readonly versus modifying requests.
- `PINT_server_sched_policy` distinguishes bypassed requests from scheduled requests.
- Lifecycle: `PINT_req_sched_initialize`, `PINT_req_sched_finalize`, `PINT_timer_queue_finalize`.
- Submission and control: `PINT_req_sched_post`, `PINT_req_sched_post_timer`, `PINT_req_sched_change_mode`, `PINT_req_sched_get_mode`, `PINT_req_sched_unpost`, and `PINT_req_sched_release`.
- Completion polling: `PINT_req_sched_test`, `PINT_req_sched_testsome`, and `PINT_req_sched_testworld`.

## Control Flow and State
Callers initialize the scheduler, post requests with operation, filesystem id, handle, access type, and policy, then either proceed immediately or poll for readiness using the returned id. Completed requests are released to unblock later work. Timers use the same polling model. Mode changes also return scheduler ids and become ready once conditions allow.

## State and Persistence Behavior
The header exposes only in-memory scheduling state. It affects ordering of persistent object mutations but does not define durable storage.

## Dependencies and Integration Points
It includes `pvfs2-req-proto.h` for protocol types and is included by server state-machine code that needs scheduler admission. `pvfs2-server.h` uses the access type and scheduler policy enums in request-table metadata.

## Risks and Edge Cases
The interface requires callers to pair scheduled ids with releases or unposts. `out_id` is zero for bypassed operations, and callers must handle that specially. The API does not expose locking or ownership semantics for `user_ptr`; those are implementation- and caller-dependent.

## Test Signals
Tests should compile both header and implementation users and exercise post/test/release, timer completion, bypass id handling, and mode changes.
