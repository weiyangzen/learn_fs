<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/io_uring.c -->
# sources/distributed-fs/ceph-client/io_uring/io_uring.c

## Purpose
`io_uring.c` is the core io_uring implementation: it creates ring contexts, validates setup parameters, maps SQ/CQ storage, submits SQEs, dispatches opcode handlers through `opdef.c`, posts CQEs, manages request lifetime, and tears rings down. It owns the system call entry points `io_uring_setup` and `io_uring_enter`, the anonymous file operations for ring fds, request caching, CQ overflow handling, async fallback to io-wq, links/drains, and several cross-cutting policy gates such as sysctl/LSM permission checks and restricted rings.

## Important APIs, Types, and Functions
- `io_prepare_config()` validates setup flags, rounds SQ/CQ sizes, computes `io_rings_layout`, and fills `io_uring_params` offsets/features.
- `io_uring_create()` allocates `io_ring_ctx`, creates shared memory regions, initializes SQPOLL/offload state, copies params back to user space, installs or registers the ring fd, and attaches the current task context.
- `io_submit_sqes()` reads the userspace SQ tail, allocates `io_kiocb` objects, fetches SQEs with `io_get_sqe()`, calls `io_submit_sqe()`, flushes completions, and commits the SQ head.
- `io_init_req()` converts one SQE into an `io_kiocb`: opcode validation, SQE128/mixed handling, common flag checks, buffer-select setup, drain setup, restriction checks, ioprio/iopoll capability checks, optional file fd capture, block plug start, personality credentials, and opcode-specific prep.
- `io_issue_sqe()` and `__io_issue_sqe()` assign files, apply saved credentials and linked timeout arming, call the opcode issue function, audit where required, and translate `IOU_COMPLETE`/`IOU_ISSUE_SKIP_COMPLETE`.
- `io_queue_sqe()`, `io_queue_async()`, `io_queue_iowq()`, and `io_wq_submit_work()` implement nonblocking first issue, async poll arming, and io-wq fallback/retry.
- `io_req_complete_defer()`, `__io_submit_flush_completions()`, `io_req_complete_post()`, `io_post_aux_cqe()`, and `io_add_aux_cqe()` are the completion posting paths.
- `io_cqe_cache_refill()`, `io_cqe_overflow()`, and `__io_cqring_overflow_flush()` manage CQ space, mixed/32-byte CQE alignment, overflow side lists, and dropped CQE signaling.
- `io_ring_ctx_wait_and_kill()`, `io_ring_exit_work()`, and `io_ring_ctx_free()` cancel in-flight work, wait for references/task contexts, unregister resources, free mmap regions, release caches, and destroy state.
- `io_uring_ctx_get_file()` resolves normal or registered ring fds and verifies `io_uring_fops`.

## Control Flow
Setup starts in `SYSCALL_DEFINE2(io_uring_setup)`, which checks `io_uring_allowed()` and calls `io_uring_setup()`. User params are copied, reserved fields are checked, and `io_uring_create()` drives config validation, context allocation, ring memory allocation through `io_allocate_scq_urings()`, SQPOLL creation, feature reporting, ring fd creation, task context registration, and final fd publication. The fd is deliberately installed last to avoid exposing a partially initialized context.

Submission starts in `SYSCALL_DEFINE6(io_uring_enter)`. The ring file is resolved, disabled rings are rejected, optional loop operations can take over, SQPOLL rings are woken or waited on, and non-SQPOLL submissions lock `ctx->uring_lock` and call `io_submit_sqes()`. `io_submit_sqes()` batches request allocation and SQE reads, then `io_submit_sqe()` performs prep, optional BPF filter evaluation, link-chain assembly, fallback queuing for forced async/fail/drain cases, or inline issue. Inline issue uses nonblocking flags and deferred completions; errors route to async poll or io-wq depending on retryability and file poll support.

Completion is split by execution context. Inline and task-work paths append requests to `ctx->submit_state.compl_reqs`, then `__io_submit_flush_completions()` posts all CQEs under the right CQ locking mode and returns requests to the cache. io-wq completions may post directly with `io_req_complete_post()` unless lockless CQ/task-owner rules force task_work deferral. Auxiliary CQEs for multishot operations use `io_post_aux_cqe()` or `io_add_aux_cqe()` and must preserve ordering with deferred completions. CQ ring tail updates use release semantics and wake waiters/eventfd/timeouts as needed.

Wait/completion retrieval through `io_uring_enter(...GETEVENTS...)` either uses `io_iopoll_check()` for syscall-driven IOPOLL rings or `io_cqring_wait()` for ordinary rings, after validating extended wait arguments. IOPOLL actively reaps `ctx->iopoll_list` and periodically runs task work to avoid deadlocks with workqueues trying to acquire `uring_lock`.

Teardown begins at `io_uring_release()`. `io_ring_ctx_wait_and_kill()` kills the percpu ref, unregisters personalities, flushes fallback work, and queues `io_ring_exit_work()` on the bounded exit workqueue. Exit work cancels requests, reaps overflow/iopoll, handles SQPOLL io-wq cancellation, drains request caches, removes task context nodes through task_work, synchronizes deferred taskrun RCU usage, and finally frees all ring resources.

## State and Persistence Behavior
Persistent state is per-ring in `struct io_ring_ctx`: setup flags, `int_flags`, SQ/CQ entry counts, shared rings/SQEs, xarrays for personalities/buffer lists/zcrx contexts, registered file/buffer resources, request caches, cancel hash table, task context list, CQ overflow list, deferred/drain lists, iopoll list, timeout lists, eventfd state, BPF filters, NAPI state, and mmap regions. State persists for the lifetime of the anonymous ring file and is released asynchronously after last fd close and all in-flight references complete.

Request state lives in cached `struct io_kiocb` objects from `req_cachep`. Requests carry opcode-specific data, file/resource nodes, flags, task context, optional async data, link pointers, CQE data, credentials, buffer selection state, and io-wq/task_work linkage. Clean state is enforced by `io_clean_op()`, `io_req_put_rsrc_nodes()`, `io_put_file()`, and request poisoning under KASAN before cache reuse/free.

Userspace-visible state is the SQ/CQ shared memory. The file carefully pairs `READ_ONCE`/`WRITE_ONCE` and acquire/release barriers with userspace ring head/tail updates. CQ overflow state is persisted in `ctx->cq_overflow_list` and signaled through `IORING_SQ_CQ_OVERFLOW`; if overflow entries cannot be allocated, `cq_overflow` and `IO_CHECK_CQ_DROPPED_BIT` record loss until userspace observes `-EBADR`.

## Dependencies and Integration Points
This file integrates almost every io_uring subsystem: `opdef` dispatch, registered files and buffers, resources, cancel, net, notifications, waitid/futex, NAPI, uring_cmd, msg_ring, mmap/zcrx, BPF filters, timeout, poll, rw, alloc caches, eventfd, wait, loop, and SQPOLL. Kernel dependencies include anon inodes, task_work, percpu refs, RCU, spinlocks/mutexes, slab caches, sysctl, LSM hooks, audit hooks, block plugs, wait queues, and fds.

The opcode table in `opdef.c` is the central integration contract: `io_init_req()` and `io_issue_sqe()` rely on `needs_file`, `iopoll`, `buffer_select`, `plug`, async data size, prep, issue, cleanup, fail, and SQE-copy metadata. `memmap.c` supplies `io_uring_mmap()`/region creation for ring memory. `kbuf.c` supplies provided-buffer cleanup and buffer-select CQ flags. `net.c` and `notif.c` provide network async data cleanup and zero-copy notification integration. `loop.c` can replace the normal enter path when `ctx->loop_step` is configured.

## Risks and Edge Cases
- Ring memory ordering is correctness-critical; missed `READ_ONCE`, `WRITE_ONCE`, or release/acquire pairing can corrupt SQE/CQE visibility.
- CQ overflow handling must preserve ordering; posting normal CQEs while overflow entries exist is intentionally blocked.
- Mixed SQE128/CQE32 support has boundary and wrap constraints; off-by-one errors can consume the wrong SQE or misalign 32-byte CQEs.
- `DEFER_TASKRUN`, IOPOLL, lockless CQ, SQPOLL, and io-wq paths have different locking/owner-task rules; direct CQ posting in the wrong context can race with submitter-only completion assumptions.
- Link/drain behavior defers whole chains and must fail hardlinks/soft links consistently when prep fails.
- Async fallback requires stable copied SQE data for opcodes with userspace pointers; failure to copy before io-wq/poll retry can observe userspace mutation.
- Teardown waits up to `IO_URING_EXIT_WAIT_MAX`; stuck task_work, frozen tasks, or refs held by nested ring fd usage can prolong cleanup.
- Fixed io_uring files are disallowed, and normal ring fd references are tracked as in-flight to make cancellation find them.

## Test Signals
Useful tests exercise setup flag matrices, invalid reserved fields, SQ/CQ sizing/clamping, `REGISTERED_FD_ONLY` with `NO_MMAP`, SQE128/CQE32 and mixed modes, CQ overflow and dropped CQE behavior, linked and hardlinked chains with prep failure, drains, NOWAIT fallback, async poll retry, io-wq retry, IOPOLL reaping, SQPOLL wake/wait, `DEFER_TASKRUN`, registered ring fd enter, restrictions/BPF filters, personality credentials, eventfd wakeups, mmap offsets, and close-with-inflight cancellation. Kernel selftests under io_uring plus syzkaller-style overflow/cancellation tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/io_uring.c -->
