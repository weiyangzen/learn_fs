# sources/distributed-fs/orangefs/src/server/request-scheduler/request-scheduler.c

## Purpose
This file implements the OrangeFS server request scheduler. It serializes or admits requests by object handle to preserve consistency while allowing concurrency for safe classes such as simultaneous I/O, readonly operations, and selected directory-entry operations. It also provides timer completions and server mode changes between normal and admin mode.

## Important APIs, Types, and Functions
- Internal states: `REQ_QUEUED`, `REQ_SCHEDULED`, `REQ_READY_TO_SCHEDULE`, and `REQ_TIMING`.
- `req_sched_list` is one hash bucket entry per handle and owns a per-handle request list.
- `req_sched_element` represents one request, timer, or mode change with list links, caller pointer, generated id, state, handle, access type, mode-change fields, and timer deadline.
- Globals: `req_sched_table`, `ready_queue`, `timer_queue`, `mode_queue`, `sched_count`, and `current_mode`.
- Lifecycle: `PINT_req_sched_initialize`, `PINT_req_sched_finalize`, and `PINT_timer_queue_finalize`.
- Mode APIs: `PINT_req_sched_change_mode`, `PINT_req_sched_get_mode`, `PINT_req_sched_in_admin_mode`, `PINT_req_sched_schedule_mode_change`, and `PINT_req_sched_do_change_mode`.
- Scheduling APIs: `PINT_req_sched_post`, `PINT_req_sched_unpost`, `PINT_req_sched_release`, `PINT_req_sched_post_timer`, `PINT_req_sched_test`, `PINT_req_sched_testsome`, and `PINT_req_sched_testworld`.
- Hash helpers: `hash_handle` and `hash_handle_compare`.

## Control Flow and State
Initialization creates a quickhash table keyed by `PVFS_handle`. Posting a bypass request may return immediately unless it is a modifying non-management request during or near admin mode. Scheduled requests allocate an element, register a generated id, find or create the handle queue, and either schedule immediately or enqueue behind existing work. If the queue contains only already scheduled I/O operations, another I/O may run concurrently. If it contains only already scheduled readonly work, another readonly request may run concurrently. Create/remove dirent requests also bypass each other by being marked readonly for scheduler purposes.

Release removes the completed element from its handle queue, destroys an empty queue, or advances the next request(s) into `ready_queue`. It advances consecutive I/O or readonly requests together. Test APIs move ready elements into scheduled state and return the caller's user pointer. Timer posts insert by deadline and tests complete expired timers. Mode changes are queued separately; normal mode can proceed immediately, while admin mode waits until `sched_count` is zero.

## State and Persistence Behavior
All scheduler state is in memory. It persists no data, but it gates access to persistent filesystem objects by handle. The generated scheduler id maps back to allocated elements through the id generator and must be released, unposted, or timer-completed to avoid leaks and stale ids.

## Dependencies and Integration Points
The implementation depends on quickhash, qlist, the id generator, server op tables/macros from `pvfs2-server.h`, and protocol definitions for `PVFS_server_op`, `PVFS_server_mode`, `PVFS_fs_id`, and `PVFS_handle`. Server state machines post before executing and release when complete. Debugging integrates with `GOSSIP_REQ_SCHED_DEBUG`.

## Risks and Edge Cases
- The scheduler is global and has no explicit locking in this file; callers must serialize access or run it in an event-loop context.
- `fs_id` and `in_user_ptr` release arguments are mostly unused, so future multi-filesystem semantics are not represented in the hash key.
- Concurrent dirent optimization treats create/remove dirent as readonly after scheduling, which is a consistency assumption specific to directory-entry handling.
- Timer test frees timer elements without unregistering ids in this file; correctness depends on id-generator behavior or external expectations.
- `PINT_req_sched_unpost` assumes `id_gen_fast_lookup` succeeds and that the element is not already scheduled.
- `PINT_timer_queue_finalize` frees `user_ptr`, while normal scheduler finalize does not; caller ownership expectations differ by path.

## Test Signals
No local tests are present. Useful coverage should include per-handle serialization, concurrent I/O and readonly admission, mixed modify/read queues, admin-mode blocking of modifying requests, timer ordering, unpost behavior, and release-time promotion of multiple ready elements.
