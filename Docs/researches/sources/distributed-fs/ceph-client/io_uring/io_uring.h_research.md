<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/io_uring.h -->
# sources/distributed-fs/ceph-client/io_uring/io_uring.h

## Purpose
`io_uring.h` is the core private header for the io_uring subsystem. It declares setup feature/flag masks, internal result codes, shared wait/defer helper types, core entry points exported across io_uring modules, and many inline helpers for CQE allocation, request state, file/resource handling, submit locking, ring wakeups, task reference caching, and ring occupancy.

## Important APIs, Types, and Functions
- `struct io_rings_layout` records shared ring size, SQE area size, and optional SQ array offset.
- `struct io_ctx_config` bundles `io_uring_params`, computed layout, and the user pointer used by setup.
- Flag macros `IORING_FEAT_FLAGS`, `IORING_SETUP_FLAGS`, `IORING_ENTER_FLAGS`, `SQE_VALID_FLAGS`, and `IO_REQ_LINK_FLAGS` define supported UAPI feature/setup/enter/SQE bits and internal link masks.
- Internal completion/issue return values include `IOU_COMPLETE`, `IOU_ISSUE_SKIP_COMPLETE`, `IOU_RETRY`, and `IOU_REQUEUE`.
- `struct io_defer_entry` and `struct io_wait_queue` define drain deferral and CQ wait state, including optional NAPI busy-poll fields.
- Declared core functions include config prep, CQE posting, aux CQEs, file lookup, task-work queueing, iowq queueing, polling issue, SQE submission, IOPOLL reaping, completion flushing, request freeing, task ref management, and restriction cloning.
- Inline helpers include `io_get_rings()`, `io_should_wake()`, `io_lockdep_assert_cq_locked()`, `io_is_compat()`, `io_get_cqe_overflow()`, `io_fill_cqe_req()`, `req_set_fail()`, `io_req_set_res()`, `io_req_set_res32()`, `io_uring_alloc_async_data()`, async data cleanup helpers, `io_put_file()`, submit lock/unlock wrappers, `io_commit_cqring()`, wake helpers, SQ/CQ occupancy helpers, `io_req_complete_defer()`, `io_commit_cqring_flush()`, `io_alloc_req()`, `io_req_queue_tw_complete()`, `io_file_can_poll()`, `io_is_uring_cmd()`, `io_get_time()`, and `io_has_work()`.

## Control Flow
The header is not executable by itself, but its inlines sit on hot paths. Submission code uses `io_alloc_req()` to pull requests from the context free list, `io_ring_submit_lock()`/`unlock()` when async issue arrives without the ring mutex, and `io_file_can_poll()` to cache file poll capability. Completion code uses `io_get_cqe()`/`io_get_cqe_overflow()` to reserve CQE slots, `io_fill_cqe_req()` to copy a request CQE into the ring, `io_commit_cqring()` to publish the tail, and wake/flush helpers to notify waiters, eventfd, poll users, and timeout processing.

`io_should_wake()` is used by waits and NAPI busy polling. It reads the current CQ tail under RCU and wakes when enough events arrived or timeout accounting changed. `io_submit_flush_completions()` is a cheap wrapper that only calls the heavy flush path when deferred completions or CQ flush flags are present.

## State and Persistence Behavior
The header manipulates persistent ring context fields such as `cached_cq_tail`, `cqe_cached`, `cqe_sentinel`, `submit_state.free_list`, `submit_state.compl_reqs`, `submit_state.cq_flush`, `rings_rcu`, `completion_lock`, `uring_lock`, `int_flags`, and `check_cq`. Request state helpers mutate `req->flags`, `req->cqe`, `req->big_cqe`, `req->async_data`, `req->file`, and task cached reference counts. These helpers are deliberately small because they run in hot submission/completion paths.

## Dependencies and Integration Points
This header includes `io_uring_types.h`, eventpoll UAPI, allocation cache, io-wq, internal singly linked list helpers, task-work helpers, opcode definitions, and tracepoints. It is included throughout the io_uring directory, so its ABI-like internal contracts bind `io_uring.c`, opcode handlers, buffer selection, networking, polling, waits, and resource modules.

## Risks and Edge Cases
- The lockdep helper encodes several CQ locking models; callers must satisfy the right model for `DEFER_TASKRUN`, IOPOLL, lockless CQ, or submitter-task completion.
- `io_get_cqe_overflow()` advances cached tail and handles CQE32/mixed CQE slot consumption; misuse can corrupt completion layout.
- `req_set_fail()` changes CQE-skip semantics for linked requests, so handler failure paths should use it consistently.
- Async data allocation must match `io_issue_defs[opcode].async_size`; missing table metadata becomes a warning and likely memory corruption.
- `io_alloc_req()` assumes `uring_lock` protection because requests can be retired before issue functions fully return.

## Test Signals
Compile-time coverage comes from build warnings and lockdep assertions. Runtime tests should stress CQE32/mixed CQE posting, skipped CQEs, async data cleanup, request cache refill/failure, fixed vs normal file put behavior, task ref refill/drop, poll wake behavior, and lockdep with `DEFER_TASKRUN`, IOPOLL, and task-complete rings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/io_uring.h -->
