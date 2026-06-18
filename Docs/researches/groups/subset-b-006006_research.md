# Research: subset-b-006006 io_uring

Grouped research report for the `sources/distributed-fs/ceph-client/io_uring` subset. Each section preserves its source path in the title and is bounded by reconciliation markers for splitting into source-tree-aligned per-file reports.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/kbuf.c -->
# sources/distributed-fs/ceph-client/io_uring/kbuf.c

## Purpose
`kbuf.c` implements io_uring provided buffers. It supports legacy kernel-managed buffer lists supplied by `IORING_OP_PROVIDE_BUFFERS`, ring-mapped provided buffers registered with `io_register_pbuf_ring()`, incremental buffer consumption, buffer selection for recv/send/write-style operations, buffer recycling/drop, buffer removal, status query, and cleanup at ring teardown.

## Important APIs, Types, and Functions
- `struct io_provide_buf` is the per-request command payload for provide/remove buffer operations.
- `io_kbuf_commit()` commits selected ring buffers after a transfer, advancing `head` or incrementally shortening buffers for `IOBL_INC`.
- `io_buffer_select()` selects one provided buffer from a legacy list or mapped buffer ring.
- `io_buffers_select()` selects one or more buffers for bundle operations, optionally expanding the iovec array.
- `io_buffers_peek()` peeks multiple buffers while the caller holds `uring_lock`, used when selection and later commit must be coordinated.
- `__io_put_kbufs()`, `io_kbuf_recycle_legacy()`, and `io_kbuf_drop_legacy()` return CQE buffer flags, commit ring buffers, or put legacy buffers back/drop them.
- `io_manage_buffers_legacy()` handles `IORING_OP_PROVIDE_BUFFERS` and `IORING_OP_REMOVE_BUFFERS`.
- `io_register_pbuf_ring()`, `io_unregister_pbuf_ring()`, and `io_register_pbuf_status()` manage mapped provided-buffer rings.
- `io_pbuf_get_region()` integrates pbuf ring mmap offsets with `memmap.c`.
- `io_destroy_buffers()` frees all buffer groups during context teardown.

## Control Flow
Legacy provide/remove requests are prepared by `io_provide_buffers_prep()` and `io_remove_buffers_prep()`, validating counts, address ranges, buffer IDs, and reserved SQE fields. `io_manage_buffers_legacy()` locks the ring, looks up the buffer group, creates one if providing to a missing group, rejects operations against mapped ring groups, then adds or removes `struct io_buffer` nodes.

Runtime buffer selection locks the ring with `io_ring_submit_lock()`, looks up `ctx->io_bl_xa[bgid]`, then chooses legacy or ring behavior. Legacy selection pops a `struct io_buffer` from `buf_list`, stores it in `req->kbuf`, sets `REQ_F_BUFFER_SELECTED`, and returns its user pointer. Ring selection reads the userspace ring tail with acquire semantics, reads the buffer at `head`, sets `REQ_F_BUFFER_RING|REQ_F_BUFFERS_COMMIT`, stores `req->buf_index`, and either commits immediately for unlocked/non-pollable cases or returns a `buf_list` for later commit.

Bundle selection uses `io_ring_buffers_peek()` to map multiple ring entries into an iovec array, optionally expanding the vector when data is known to exist. It records `out_len`, truncates to `max_len`, marks partial maps for non-incremental buffers, and sets `REQ_F_BL_EMPTY` when the ring drains. Finalization through `__io_put_kbufs()` returns `IORING_CQE_F_BUFFER` plus the selected bid and may add `IORING_CQE_F_BUF_MORE` for incremental buffers with remaining data.

Registration of pbuf rings copies `io_uring_buf_reg`, validates flags and power-of-two entry count, prevents ambiguous full/empty rings, rejects `min_left` without incremental mode, creates or replaces an empty legacy group, creates an `io_mapped_region` either from kernel pages or user-provided memory, validates SHM color aliasing where needed, initializes mask/flags/head, and publishes the buffer list under `mmap_lock`.

## State and Persistence Behavior
Buffer groups live in `ctx->io_bl_xa` indexed by `bgid`. Legacy groups persist as linked lists of heap `struct io_buffer` nodes and `nbufs`. Ring groups persist as `struct io_buffer_list` with `buf_ring`, `head`, `mask`, flags, `min_left_sub_one`, and an owned `io_mapped_region`. Userspace owns the ring tail and buffer descriptors; the kernel owns `head` and commit behavior. `io_buffer_add_list()` publishes groups under `mmap_lock` because mmap lookup can access the xarray without `uring_lock`.

Requests carry transient state in `req->kbuf`, `req->buf_index`, and flags such as `REQ_F_BUFFER_SELECTED`, `REQ_F_BUFFER_RING`, `REQ_F_BUFFERS_COMMIT`, `REQ_F_BUF_MORE`, `REQ_F_BL_EMPTY`, and `REQ_F_BL_NO_RECYCLE`. Cleanup must drop or recycle legacy buffers and commit or clear ring-buffer state.

## Dependencies and Integration Points
This module depends on `io_uring.h` for request flags and locking, `opdef.h` for opcode dispatch, and `memmap.h` for mapped region allocation/free. `net.c`, `rw.c`, and uring command paths call buffer selection helpers and include returned CQE flags in completions. `memmap.c` calls `io_pbuf_get_region()` for pbuf ring mmap offsets.

## Risks and Edge Cases
- Incremental commit must not consume a zero-length transfer and must avoid infinite loops on invalid zero-length buffer descriptors.
- Ring `head`/userspace `tail` use 16-bit arithmetic; entry counts >= 65536 are rejected to preserve full/empty disambiguation.
- Unlocked io-wq selection commits immediately because another request could otherwise reuse the same ring entry.
- A legacy buffer selected before the group is upgraded or removed is dropped instead of recycled.
- Partial bundle maps can shorten non-incremental buffer lengths visible to userspace, so bundle retry paths must respect `partial_map`.
- Publishing/removing buffer groups must coordinate `uring_lock` with `mmap_lock` to avoid mmap seeing freed regions.

## Test Signals
Tests should cover legacy provide/remove counts and BID overflow, selection from empty groups, recycle after async retry, mapped pbuf registration/unregistration/status, mmap of pbuf regions, incremental buffer consumption including zero/partial transfers, bundle send/recv with vector expansion, CQE buffer flags and `BUF_MORE`, group replacement rules, and teardown with mixed legacy and mapped groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/kbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/kbuf.h -->
# sources/distributed-fs/ceph-client/io_uring/kbuf.h

## Purpose
`kbuf.h` declares the internal data structures and APIs for io_uring provided buffers. It covers legacy buffer lists, mapped buffer rings, incremental consumption, multi-buffer selection arguments, buffer lifecycle helpers, registration hooks, and small inline helpers used by network/rw paths.

## Important APIs, Types, and Functions
- `IOBL_BUF_RING` marks mapped provided-buffer rings; `IOBL_INC` marks incremental buffer consumption.
- `struct io_buffer_list` stores either a legacy `buf_list` or mapped `buf_ring`, buffer count/group id, ring head/mask, flags, incremental threshold, and `io_mapped_region`.
- `struct io_buffer` is the legacy per-buffer node with address, length, buffer id, and group id.
- `struct buf_sel_arg` describes multi-buffer selection input/output: iovec storage, accumulated length, max length, vector count, allocation mode, group id, and partial-map indicator.
- Public helpers include `io_buffer_select()`, `io_buffers_select()`, `io_buffers_peek()`, `io_destroy_buffers()`, prep/issue functions for provide/remove buffers, pbuf registration/status functions, recycle/drop helpers, `__io_put_kbufs()`, `io_kbuf_commit()`, and `io_pbuf_get_region()`.
- Inline helpers include `io_kbuf_recycle_ring()`, `io_do_buffer_select()`, `io_kbuf_recycle()`, `io_put_kbuf()`, and `io_put_kbufs()`.

## Control Flow
Opcode handlers check `io_do_buffer_select()` to determine whether a request still needs buffer selection. After a transfer, handlers call `io_put_kbuf()` or `io_put_kbufs()` to commit buffers and obtain CQE flags. If an operation must retry or poll, `io_kbuf_recycle()` returns selected buffers where legal: ring buffers are cleared from request state, legacy selected buffers are reinserted into the group, and `REQ_F_BL_NO_RECYCLE` prevents unsafe reuse.

## State and Persistence Behavior
The header defines the persistent per-group state in `struct io_buffer_list` and the transient request state used by inline helpers. The `io_mapped_region` embedded in ring buffer lists persists until unregister or context teardown. Inline helpers mutate request flags to prevent double commit/recycle.

## Dependencies and Integration Points
It includes UAPI io_uring definitions and `io_uring_types.h`. It depends on `memmap.h` indirectly through `struct io_mapped_region` in the included type definitions. It is consumed by core completion paths, network send/recv, read/write, and mmap region dispatch.

## Risks and Edge Cases
- `io_put_kbuf()` and `io_put_kbufs()` are no-ops unless a buffer was actually selected, so callers must not rely on them for unrelated CQE flags.
- `io_kbuf_recycle_ring()` only clears flags when a valid list is supplied; null lists mean the buffer was already committed or cannot be recycled.
- `REQ_F_BL_NO_RECYCLE` is critical for bundle paths where buffers were already committed.

## Test Signals
Header-level signals come from builds across buffer-select users. Runtime signals should verify callers consistently call put/recycle helpers exactly once and preserve CQE buffer IDs for both single and multi-buffer selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/kbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/loop.c -->
# sources/distributed-fs/ceph-client/io_uring/loop.c

## Purpose
`loop.c` implements a ring-local loop runner used when `ctx->loop_step` is installed. It lets an io_uring context execute repeated step callbacks from `io_uring_enter()` while waiting for CQ progress, running task work/local work, handling signals, and flushing CQ overflow.

## Important APIs, Types, and Functions
- `io_run_loop()` is the exported entry point used by `io_uring_enter()` when `io_has_loop_ops(ctx)` is true.
- `__io_run_loop()` drives repeated `ctx->loop_step(ctx, &lp)` callbacks until the callback returns `IOU_LOOP_STOP`.
- `io_loop_nr_cqes()` computes how far the current CQ tail is from `lp.cq_wait_idx`.
- `io_loop_wait_start()`, `io_loop_wait_finish()`, and `io_loop_wait()` update `ctx->cq_wait_nr`, set task state, schedule if no local/CQ/check work is pending, and restore state.

## Control Flow
`io_run_loop()` first checks `io_allowed_run_tw(ctx)` to ensure task_work may run, then locks `ctx->uring_lock` and calls `__io_run_loop()`. Each iteration verifies `loop_step` still exists, calls it with an `iou_loop_params` instance, stops on `IOU_LOOP_STOP`, rejects unknown return values, optionally waits until `cq_wait_idx` is reached, runs pending task work outside the mutex, handles signals, runs local io_uring work while locked, and flushes CQ overflow if needed.

## State and Persistence Behavior
The module does not own persistent data beyond fields in `io_ring_ctx`: `loop_step`, `rings->cq.tail`, `cq_wait_nr`, local work queues, and `check_cq`. `struct iou_loop_params` carries the step callback's CQ wait hint for the current iteration only.

## Dependencies and Integration Points
It depends on `io_uring.h` for ring locking, task-work helpers, CQ overflow flushing, and `io_allowed_run_tw()`, plus `wait.h` for `IO_CQ_WAKE_INIT`. The integration point is the early branch in `io_uring_enter()`, which diverts normal submit/wait behavior to `io_run_loop()`.

## Risks and Edge Cases
- `loop_step` can disappear while entering the loop; this returns `-EFAULT`.
- Waiting releases `uring_lock`, so callback state must tolerate concurrent wakeups and ring changes.
- Signal pending returns `-EINTR`.
- Unknown callback return values are treated as `-EINVAL`.
- CQ overflow must be flushed while locked to keep loop wait decisions accurate.

## Test Signals
Tests should install a loop step that continues, stops, waits for CQ tail movement, observes task work, handles signals, and triggers CQ overflow. Negative tests should cover missing `loop_step` and invalid callback return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/loop.h -->
# sources/distributed-fs/ceph-client/io_uring/loop.h

## Purpose
`loop.h` declares the io_uring loop-step interface. It defines the per-step parameters, callback result constants, a helper for detecting configured loop operations, and the `io_run_loop()` entry point.

## Important APIs, Types, and Functions
- `struct iou_loop_params` currently contains `cq_wait_idx`, a hint for the CQE index the loop should wait for.
- `IOU_LOOP_CONTINUE` and `IOU_LOOP_STOP` are valid loop-step return values.
- `io_has_loop_ops(ctx)` checks `ctx->loop_step` with `data_race()` because the enter path only needs a quick branch.
- `io_run_loop()` runs the loop under core locking.

## Control Flow
Callers use `io_has_loop_ops()` to decide whether to divert `io_uring_enter()` to loop mode. The loop implementation calls the configured `ctx->loop_step`, which fills `iou_loop_params` and returns continue or stop.

## State and Persistence Behavior
The header defines only transient step parameters. Persistent state is the function pointer in `io_ring_ctx`.

## Dependencies and Integration Points
It includes `io_uring_types.h` and is included by `io_uring.c` and `loop.c`. Any subsystem assigning `ctx->loop_step` must follow the return-value contract here.

## Risks and Edge Cases
- The unsynchronized helper is intentionally loose; the implementation must recheck the pointer under lock.
- `cq_wait_idx` is only a hint, so loop users must tolerate earlier wakeups.

## Test Signals
Build coverage and loop-mode runtime tests should verify the helper branch, valid stop/continue behavior, and early wake semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/loop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/memmap.c -->
# sources/distributed-fs/ceph-client/io_uring/memmap.c

## Purpose
`memmap.c` owns io_uring mapped memory regions: pinning user-provided pages, allocating kernel-owned pages for rings and auxiliary regions, creating kernel virtual mappings, accounting memory, freeing regions, dispatching mmap offsets to the correct region, and supporting both MMU and NOMMU mappings.

## Important APIs, Types, and Functions
- `io_pin_pages()` pins a page-aligned user range with `FOLL_WRITE|FOLL_LONGTERM`.
- `io_create_region()` validates an `io_uring_region_desc`, accounts pages, either pins user pages or allocates kernel pages, initializes a kernel pointer, and returns a mmap offset for kernel-owned memory.
- `io_free_region()` releases pinned or allocated pages, unmaps vmap mappings, unaccounts memory, and clears the region.
- `io_uring_mmap()` maps ring, SQE, pbuf, parameter, or zcrx regions into userspace.
- `io_uring_get_unmapped_area()` provides cache-aliasing-aware placement for MMU builds and direct pointer return for NOMMU builds.
- `io_uring_nommu_mmap_capabilities()` advertises direct read/write mapping support on NOMMU.
- Internal helpers allocate compound or bulk pages, initialize direct/vmap pointers, resolve mmap offsets, and validate mmap requests.

## Control Flow
Region creation begins with `io_create_region()`. It rejects already initialized regions, nonzero reserved fields, unsupported flags, mismatched user-address flags, missing size, pre-set mmap offset/id, non-page-aligned address/size, oversized page counts, and address overflow. It accounts memory against `ctx->user` if needed, sets `nr_pages`, then either pins user pages via `io_region_pin_pages()` or allocates zeroed pages via `io_region_allocate_pages()`. Finally, `io_region_init_ptr()` uses direct page address when the pages coalesce into one lowmem folio, otherwise vmaps the pages.

Mmap requests enter `io_uring_mmap()` through ring file operations. Under `ctx->mmap_lock`, the code resolves `vma->vm_pgoff` with `io_mmap_get_region()`, validates the region is set and not user-provided, and inserts pages. SQ/CQ ring mappings may map a limited number of pages based on requested VMA size because SQ and CQ share the same backing region. For cache-color-sensitive architectures, `get_unmapped_area` rejects caller-specified addresses and asks the mm layer for an alias-coherent mapping based on the kernel pointer.

NOMMU mapping requires shared mappings with exact region size, pins pages with `get_page()` for the VMA lifetime, and releases those extra references in `io_uring_nommu_vm_close()`.

## State and Persistence Behavior
`struct io_mapped_region` stores `pages`, `nr_pages`, `ptr`, and internal flags for vmap, user-provided pages, and single-ref compound allocation. Regions persist in `io_ring_ctx` (`ring_region`, `sq_region`, `param_region`) or subsidiary structures such as pbuf lists and zcrx contexts. Memory accounting is tied to `ctx->user` and reversed on free.

## Dependencies and Integration Points
This module integrates with `kbuf.c` through pbuf ring mmap offsets, with `rsrc.c` through coalesced buffer/page helpers and memory accounting, with `zcrx` through zero-copy receive regions, and with `io_uring.c` for ring/SQE region creation and file operations. It depends on mm APIs, GUP pinning, page allocation, vmap/vunmap, `vm_insert_pages()`, NOMMU VMA hooks, and architecture SHM coloring.

## Risks and Edge Cases
- Long-term user page pins must be fully released on partial failure; `io_pin_pages()` handles partial GUP by unpinning.
- User-provided regions are deliberately not mmap-able through the ring fd to avoid aliasing rule violations.
- Compound allocations use `IO_REGION_F_SINGLE_REF`, so free paths must release only one page ref in that case.
- `io_region_pin_pages()` currently returns `-EFAULT` without freeing `pages` if a WARN detects an unexpected page count mismatch; this is theoretically unreachable because page count was derived from the same size.
- Mmap offset dispatch shares bit ranges with pbuf/zcrx ids; incorrect shifts/masks map the wrong region.
- Cache aliasing on SHM-colored architectures can break if callers bypass `get_unmapped_area()` semantics.

## Test Signals
Tests should cover setup mmap of SQ/CQ/SQEs, `IORING_SETUP_NO_MMAP` user-provided regions, invalid descriptors/reserved fields/alignment/overflow, pbuf ring mmap offsets, zcrx region offsets when enabled, memory accounting failure, mmap after unregister, NOMMU exact-size/shared rules, and teardown unmapping with active VMAs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/memmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/memmap.h -->
# sources/distributed-fs/ceph-client/io_uring/memmap.h

## Purpose
`memmap.h` declares io_uring memory-region mapping APIs and special mmap offset constants for parameter and zero-copy receive regions. It also provides inline helpers for inspecting and publishing `io_mapped_region` objects.

## Important APIs, Types, and Functions
- `IORING_MAP_OFF_PARAM_REGION`, `IORING_MAP_OFF_ZCRX_REGION`, and `IORING_OFF_ZCRX_SHIFT` define additional mmap offset classes beyond core rings and pbuf rings.
- `io_pin_pages()` pins userspace pages for fixed regions.
- `io_uring_get_unmapped_area()` and `io_uring_mmap()` are file operation hooks.
- `io_free_region()` and `io_create_region()` manage region lifecycle.
- `io_region_get_ptr()`, `io_region_is_set()`, `io_region_publish()`, and `io_region_size()` expose common region operations.

## Control Flow
Callers create a local `io_mapped_region` with `io_create_region()`, access the kernel pointer with `io_region_get_ptr()`, and publish it to a context-visible destination with `io_region_publish()` when mmap lookup may need to see it. `io_region_publish()` takes `ctx->mmap_lock` before copying the region because mmap lookup may run with only that lock rather than `uring_lock`.

## State and Persistence Behavior
The header treats `nr_pages` as the indicator that a region is set and derives byte size from `nr_pages << PAGE_SHIFT`. Publishing copies the entire region struct; after publication, the destination owns the page pointers and mapping state.

## Dependencies and Integration Points
It is consumed by `io_uring.c`, `kbuf.c`, `memmap.c`, and zcrx-related code. It relies on `struct io_ring_ctx`, `struct io_mapped_region`, and UAPI `io_uring_region_desc` definitions from the broader io_uring type headers.

## Risks and Edge Cases
- `io_region_publish()` is a shallow struct copy; callers must avoid freeing the source as an owner after publishing unless ownership is explicitly transferred.
- `io_region_is_set()` only checks `nr_pages`, so partially initialized regions must be cleaned with `io_free_region()`.
- Offset constants must remain disjoint from other mmap classes.

## Test Signals
Build and runtime signals should verify region publication under mmap races, correct size calculations, and mmap offset dispatch for parameter/zcrx/pbuf/ring regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/memmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/mock_file.c -->
# sources/distributed-fs/ceph-client/io_uring/mock_file.c

## Purpose
`mock_file.c` provides a testing-only misc device, `/dev/io_uring_mock`, that exposes `uring_cmd` manager commands to create anonymous mock files and probe supported features. Created mock files implement controlled read/write behavior, optional poll support, optional NOWAIT support, delayed asynchronous completions, fixed size bounds, and a command for copying registered buffers to/from user memory.

## Important APIs, Types, and Functions
- `struct io_mock_file` stores size, artificial read/write delay, pollability, and a waitqueue.
- `struct io_mock_iocb` stores delayed kiocb completion state and an hrtimer.
- `iou_mock_mgr_cmd()` dispatches manager `IORING_MOCK_MGR_CMD_PROBE` and `IORING_MOCK_MGR_CMD_CREATE`.
- `io_create_mock_file()` validates `io_uring_mock_create`, creates an anonymous mock file, configures fops and modes, and publishes an fd back to userspace.
- `io_mock_read_iter()` and `io_mock_write_iter()` implement bounded zero-fill reads and advancing writes, optionally delayed with `io_mock_delay_rw()`.
- `io_mock_cmd()` dispatches per-file mock commands such as `IORING_MOCK_CMD_COPY_REGBUF`.
- `io_cmd_copy_regbuf()` imports fixed registered vectors from an io_uring command and copies between those iterators and a userspace buffer.
- `io_mock_init()`/`io_mock_exit()` register/deregister the misc device.

## Control Flow
Users with `CAP_SYS_ADMIN` open the misc device and issue a manager uring command. Probe requires an all-zero `io_uring_mock_probe` input and returns feature bits. Create copies `io_uring_mock_create`, validates flags/reserved fields, caps file size at 1 GiB and delay at 1 second, allocates `io_mock_file`, picks poll or non-poll fops, creates an anonymous inode file, sets read/write/seek modes plus optional `FMODE_NOWAIT`, copies the output fd into the user struct, then publishes the fd.

Read/write operations check `ki_pos + len <= size`. Reads zero the destination iterator immediately; writes advance the source iterator immediately for no-delay mode. With `rw_delay_ns`, both create an hrtimer-backed `io_mock_iocb`, return `-EIOCBQUEUED`, and later call `ki_complete()` with the requested length.

The registered-buffer copy command imports fixed vectors with `io_uring_cmd_import_fixed_vec()` and then loops through the iterator in page-sized chunks, copying from iter to user or user to iter depending on `IORING_MOCK_COPY_FROM`.

## State and Persistence Behavior
The misc device is module-global. Each created anonymous file owns an `io_mock_file` until release. Delayed operations allocate one `io_mock_iocb` per queued IO and free it on hrtimer completion. The module deliberately taints the kernel with `TAINT_TEST` when creating mock files.

## Dependencies and Integration Points
This module integrates with the io_uring command path, registered buffer import, anonymous inodes, miscdevice framework, hrtimers, iterators, poll, and module init/exit. It is a test helper rather than part of production ring operation.

## Risks and Edge Cases
- Delayed IO uses hrtimer completion state; cancellation semantics depend on the broader kiocb/io_uring machinery and the file does not explicitly cancel timers on release.
- Copying registered buffers through a temporary page loop must handle short copies and user faults; current return is bytes copied or `-EFAULT` when zero bytes copied.
- Poll fops always report readable/writable and do not model readiness transitions, so tests must understand it is synthetic.
- Manager commands require `CAP_SYS_ADMIN` but created files can exercise edge cases that normal files may not expose.

## Test Signals
Tests should cover manager permission checks, probe, create validation, NOWAIT flag behavior, pollable vs non-pollable fops, size-bound read/write errors, delayed `-EIOCBQUEUED` completion, registered buffer copy in both directions, and release cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/mock_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/msg_ring.c -->
# sources/distributed-fs/ceph-client/io_uring/msg_ring.c

## Purpose
`msg_ring.c` implements `IORING_OP_MSG_RING`, allowing one io_uring instance to post data CQEs into another ring or transfer a registered file into another ring's fixed-file table. It also implements the synchronous data-message helper used outside normal request context.

## Important APIs, Types, and Functions
- `struct io_msg` is the per-request command payload: target/source files, remote task_work, user data, len, command, source fd, destination fd or CQE flags, and message flags.
- `io_msg_ring_prep()` validates SQE fields and fills `io_msg`.
- `io_msg_ring()` dispatches `IORING_MSG_DATA` and `IORING_MSG_SEND_FD` after verifying the target file is an io_uring fd.
- `io_uring_sync_msg_ring()` sends a data CQE synchronously to a target ring fd.
- `io_msg_ring_cleanup()` drops a held source file for SEND_FD failures/cancellations.
- `__io_msg_ring_data()` posts a data CQE directly, through target task_work, or under IOPOLL target locking.
- `io_msg_send_fd()` grabs a source fixed file and installs it into the target fixed-file table, possibly via target submitter task_work.

## Control Flow
Prep rejects `buf_index` and `personality`, reads user data from `sqe->off`, message length, command, source fixed fd, destination fixed slot, and msg-ring flags. Data messages reject source fd and unsupported flags, reject disabled target rings, and then choose a posting mode. Rings with `IO_RING_F_TASK_COMPLETE` require remote task_work, so `io_msg_data_remote()` allocates a fresh request from `req_cachep`, initializes it as a NOP-like aux completion, bumps the target context ref, and queues remote task_work. Other rings use `io_post_aux_cqe()` directly, with external locking for IOPOLL rings.

SEND_FD rejects nonzero len and same source/target context. It grabs the source fixed file from the source ring's file table if not already held, marks `REQ_F_NEED_CLEANUP`, rejects disabled target rings, and either queues target submitter task_work for task-complete rings or installs immediately. `io_msg_install_complete()` locks the target context, calls `__io_fixed_fd_install()`, clears cleanup ownership on success, and optionally posts a target CQE unless `IORING_MSG_RING_CQE_SKIP` is set.

## State and Persistence Behavior
Data messages create transient CQEs in the target ring. Remote data completion temporarily allocates an `io_kiocb` and frees it with `kfree_rcu()` after the aux CQE is added. SEND_FD holds `msg->src_file` across retries/remote task_work and clears it only after successful install; cleanup fputs it on failure. The target ring's fixed-file table persists the installed file reference.

## Dependencies and Integration Points
This module depends on core CQE posting, task_work, request cache, fixed-file resource lookup/install, ring fd verification, and target context locking. It integrates with `opdef.c` as `IORING_OP_MSG_RING`, with cleanup registered in `io_cold_defs`, and with core ring fd resolution through `io_is_uring_fops()`.

## Risks and Edge Cases
- Lock ordering between source and target rings avoids deadlock by trylocking the target when the source lock is already held; `-EAGAIN` punts to io-wq.
- Target rings with `IORING_SETUP_R_DISABLED` are rejected before submitter-task access.
- If target CQE posting fails after SEND_FD install, the file is already visible in the target table and the sender receives `-EOVERFLOW`.
- Remote task_work can fail with `-EOWNERDEAD` if the target submitter task is exiting.
- SEND_FD cannot target the same ring and fixed destination slot rules are enforced by the fixed-file table.

## Test Signals
Tests should cover data CQE posting to normal, IOPOLL, and task-complete rings; CQE flag passing; disabled target rejection; synchronous msg ring data; SEND_FD installation, CQE skip, source cleanup on failure, same-ring rejection, target overflow, and trylock `-EAGAIN` retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/msg_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/msg_ring.h -->
# sources/distributed-fs/ceph-client/io_uring/msg_ring.h

## Purpose
`msg_ring.h` declares the msg-ring operation interface used by the opcode table and synchronous callers.

## Important APIs, Types, and Functions
- `io_uring_sync_msg_ring()` sends a data message directly from a prepared SQE-like structure.
- `io_msg_ring_prep()` prepares an async `IORING_OP_MSG_RING` request.
- `io_msg_ring()` issues the prepared request.
- `io_msg_ring_cleanup()` releases held resources such as source files for SEND_FD.

## Control Flow
The core request path calls prep, then issue, then cleanup through `io_cold_defs` if `REQ_F_NEED_CLEANUP` remains. Synchronous callers bypass request allocation and call `io_uring_sync_msg_ring()` for data-only messages.

## State and Persistence Behavior
The header does not define persistent state; `msg_ring.c` stores transient payload in the request command area.

## Dependencies and Integration Points
It depends on `struct io_kiocb`, `struct io_uring_sqe`, and issue flags from core io_uring types. It is consumed by `io_uring.c`, `opdef.c`, and any sync msg-ring caller.

## Risks and Edge Cases
The cleanup declaration is essential because SEND_FD can hold a source file across async retry. Missing cleanup table registration would leak file refs.

## Test Signals
Build linkage plus runtime msg-ring data and SEND_FD tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/msg_ring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/napi.c -->
# sources/distributed-fs/ceph-client/io_uring/napi.c

## Purpose
`napi.c` implements optional io_uring integration with network RX busy polling when `CONFIG_NET_RX_BUSY_POLL` is enabled. It tracks NAPI IDs statically or dynamically per ring, registers/unregisters busy-poll configuration, removes stale dynamic IDs, and drives busy-poll loops during blocking CQ waits or SQPOLL polling.

## Important APIs, Types, and Functions
- `struct io_napi_entry` stores one NAPI id, list/hash nodes, timeout, and RCU head.
- `io_napi_init()` initializes per-ring NAPI state from `sysctl_net_busy_poll`.
- `io_napi_free()` removes and RCU-frees tracked entries.
- `io_register_napi()` handles register/static-add/static-del UAPI operations and returns the previous config to userspace.
- `io_unregister_napi()` disables tracking and optionally returns previous timeout/prefer settings.
- `__io_napi_add_id()` and `__io_napi_del_id()` manage tracked ids.
- `__io_napi_busy_loop()` runs busy polling during blocking wait.
- `io_napi_sqpoll_busy_poll()` runs busy polling from SQPOLL context.

## Control Flow
Dynamic tracking is fed by `io_napi_add(req)` in `napi.h`, which reads the socket's `sk_napi_id` for requests when the ring is in dynamic mode. `__io_napi_add_id()` rejects invalid ids, checks the hash under RCU, refreshes timeout for existing entries, allocates a new entry, then under `napi_lock` verifies tracking mode has not changed and inserts into both hash and list.

Registration copies an `io_uring_napi` struct from userspace, validates padding, first copies the current config back to userspace, then either changes tracking mode/config, adds a static id, or deletes a static id. Registering a new mode disables tracking, frees existing entries, caps busy-poll timeout at 10 msec, updates prefer-busy-poll, and enables the selected mode.

Busy polling checks wait conditions through `io_napi_busy_loop_should_end()`: pending signals, enough CQEs, ring work, or timeout. Static mode loops all ids and never reports stale. Dynamic mode also detects expired entries and removes them after the RCU loop. Blocking waits skip SQPOLL rings, clamp busy-poll duration to the CQ wait timeout, and then call the blocking busy loop. SQPOLL busy poll runs only when a nonzero timeout and nonempty list are present.

## State and Persistence Behavior
Per-ring state includes `napi_list`, `napi_ht`, `napi_lock`, `napi_track_mode`, `napi_busy_poll_dt`, and `napi_prefer_busy_poll`. Dynamic entries expire after `NAPI_TIMEOUT` jiffies unless refreshed. Entry removal uses RCU list/hash deletion and `kfree_rcu()`, so readers can busy-loop under RCU without holding `napi_lock`.

## Dependencies and Integration Points
The module depends on net busy-poll APIs (`napi_busy_loop_rcu`, `busy_loop_current_time`, `BUSY_POLL_BUDGET`), socket NAPI IDs, RCU, spinlocks, and io_uring wait/task state. It is initialized/freed from ring context allocation/free and used by wait paths and SQPOLL loops. `napi.h` provides no-op stubs when busy poll is disabled.

## Risks and Edge Cases
- Tracking mode can change while adding ids; `__io_napi_add_id()` rechecks under lock and returns `-EINVAL` if mode changed.
- Dynamic stale removal iterates with assumptions about RCU list deletion not resetting next pointers before grace period.
- Busy loops must terminate on signals and CQ/work readiness to avoid starving user tasks.
- IOPOLL rings reject NAPI registration.
- Static add/del operations require current mode to be static and use `op_param` as the NAPI id.

## Test Signals
Tests should cover register/unregister, current-config copyback, dynamic id learning from sockets, duplicate id refresh, stale dynamic removal, static add/delete validation, invalid padding/mode/id, busy-poll timeout clamping, blocking wait wake conditions, SQPOLL busy-poll path, and builds with `CONFIG_NET_RX_BUSY_POLL` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/napi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/napi.h -->
# sources/distributed-fs/ceph-client/io_uring/napi.h

## Purpose
`napi.h` declares and conditionally stubs io_uring NAPI busy-poll integration. It lets networking-enabled builds track NAPI IDs and lets non-busy-poll builds compile with no-op behavior and `-EOPNOTSUPP` registration.

## Important APIs, Types, and Functions
- Enabled declarations: `io_napi_init()`, `io_napi_free()`, `io_register_napi()`, `io_unregister_napi()`, `__io_napi_add_id()`, `__io_napi_busy_loop()`, and `io_napi_sqpoll_busy_poll()`.
- `io_napi(ctx)` checks whether the ring has any tracked NAPI entries.
- `io_napi_busy_loop(ctx, iowq)` runs busy polling only when entries exist.
- `io_napi_add(req)` dynamically tracks a request socket's NAPI id when the ring mode is dynamic.
- Disabled stubs no-op init/free/add/busy-loop, return false or 0 where appropriate, and return `-EOPNOTSUPP` for register/unregister.

## Control Flow
Networking request paths can call `io_napi_add(req)` after socket activity; it quickly exits unless `ctx->napi_track_mode` is dynamic, then calls `sock_from_file()` and `__io_napi_add_id()`. Wait paths call `io_napi_busy_loop()`, which avoids the heavier implementation when no ids are present.

## State and Persistence Behavior
The header only manipulates per-ring fields owned by `napi.c`: tracking mode and NAPI list state. Dynamic add is opportunistic and ignores sockets without a valid `sk`.

## Dependencies and Integration Points
It includes kernel io_uring and net busy-poll headers. It is used by ring allocation/free, wait paths, SQPOLL, and network opcode handlers. Conditional compilation isolates callers from `CONFIG_NET_RX_BUSY_POLL`.

## Risks and Edge Cases
- `io_napi_add()` uses `READ_ONCE` on tracking mode and socket `sk_napi_id`; races are tolerated by the implementation rechecking under lock.
- Disabled builds must return `-EOPNOTSUPP` rather than silently accepting registration.

## Test Signals
Build both enabled and disabled configs. Runtime tests should verify dynamic tracking only occurs in dynamic mode and registration fails with `-EOPNOTSUPP` when busy poll support is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/napi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/net.c -->
# sources/distributed-fs/ceph-client/io_uring/net.c

## Purpose
`net.c` implements io_uring network opcodes: shutdown, send/sendmsg, recv/recvmsg, multishot and bundled send/recv, zero-copy send notifications, zero-copy receive handoff, accept, socket creation, connect, bind, listen, BPF socket filter population, and network async-data cleanup. It is the main bridge between io_uring request semantics and socket APIs.

## Important APIs, Types, and Functions
- Per-op command payloads include `io_shutdown`, `io_accept`, `io_socket`, `io_connect`, `io_bind`, `io_listen`, `io_sr_msg`, and `io_recvzc`.
- Prep/issue pairs include `io_shutdown_prep()`/`io_shutdown()`, `io_sendmsg_prep()`/`io_sendmsg()`/`io_send()`, `io_recvmsg_prep()`/`io_recvmsg()`/`io_recv()`, `io_recvzc_prep()`/`io_recvzc()`, `io_send_zc_prep()`/`io_sendmsg_zc()`, `io_accept_prep()`/`io_accept()`, `io_socket_prep()`/`io_socket()`, `io_connect_prep()`/`io_connect()`, `io_bind_prep()`/`io_bind()`, and `io_listen_prep()`/`io_listen()`.
- `io_msg_alloc_async()`, `io_net_import_vec()`, `io_msg_copy_hdr()`, and compat helpers import and cache msghdr/iovec state.
- `io_recv_finish()` and `io_send_finish()` centralize CQE flags, buffer commitment, multishot retry, bundle continuation, and final result setting.
- `io_send_zc_cleanup()`, `io_sendrecv_fail()`, and `io_netmsg_cache_free()` handle cleanup/failure for async network data and zero-copy notifications.
- `io_socket_bpf_populate()` fills BPF filter context for socket operations.

## Control Flow
Send prep allocates `io_async_msghdr`, reads length/flags/message flags, records buffer group for buffer-select requests, handles bundle mode, marks NOWAIT on `MSG_DONTWAIT`, sets compat CMSG flags, then imports either a raw buffer, a fixed registered buffer, a vector, or a userspace msghdr. Send issue checks socket type, honors `POLL_FIRST`, applies nonblocking flags, optionally selects provided buffers, calls `sock_sendmsg()` or `__sys_sendmsg_sock()`, handles `MSG_WAITALL` short sends by accumulating `done_io` and returning retry, commits selected buffers, posts bundle CQEs with `IORING_CQE_F_MORE`, recycles async msg data, and completes.

Recv prep mirrors send but validates recv-specific flags, requires buffer selection for multishot, rejects `MSG_WAITALL` for multishot, supports per-shot and total byte limits for `IORING_OP_RECV`, and imports destination buffers or msghdrs. Recv issue selects provided buffers when needed, prepares multishot recvmsg output headers, calls `sock_recvmsg()` or `__sys_recvmsg_sock()`, handles partial `MSG_WAITALL`, converts `-ERESTARTSYS`, recycles buffers on no data/retry, and delegates to `io_recv_finish()`. Finish computes `SOCK_NONEMPTY`, buffer CQE flags, bundle accumulation, multishot CQE posting, fairness-limited immediate retries, and `IOU_REQUEUE` when a multishot loop exceeds `MULTISHOT_MAX_RETRY`.

Zero-copy send prep allocates a notification request with `io_alloc_notif()`, chooses notification user_data, rejects CQE skip, sets `MSG_ZEROCOPY`, imports normal or fixed buffers, configures `sg_from_iter`, and accounts memory for non-fixed iterators. Issue verifies socket zero-copy support, imports fixed buffers lazily if needed, assigns the notification ubuf, sends, flushes notification immediately unless running unlocked in io-wq, sets the request result with `IORING_CQE_F_MORE`, and relies on notification completion for the final notification CQE.

Accept/socket operations optionally install files into fixed-file tables. Accept supports multishot, poll-first, don't-wait, normal fd allocation, fixed slot allocation, and `SOCK_NONEMPTY` CQE flags. Socket creation supports normal or fixed-file install and BPF context population. Connect stores sockaddr in async data, tracks in-progress state, retries `-EINPROGRESS`/`-EAGAIN`/first `-ECONNABORTED` under nonblocking issue, and reads `sock_error()` for completion after poll. Bind/listen are straightforward wrappers around kernel socket helpers after prep-time address/backlog validation.

## State and Persistence Behavior
Network requests persist mutable state across retries in the request command area: `done_io`, message flags, selected buffer group, multishot counters/limits, current buffer pointer/length, control pointer, notification request, connect progress flags, and fixed-file slot/nofile limits. `req->async_data` stores `io_async_msghdr` and can be recycled into `ctx->netmsg_cache` when issue occurs under the ring lock. Cached vectors may be retained up to `IO_VEC_CACHE_SOFT_CAP`; larger vectors are freed.

Provided buffers interact with request flags `REQ_F_BUFFER_SELECT`, `REQ_F_BUFFER_RING`, `REQ_F_BUFFERS_COMMIT`, `REQ_F_BL_EMPTY`, `REQ_F_BL_NO_RECYCLE`, `REQ_F_APOLL_MULTISHOT`, and `REQ_F_MULTISHOT`. Zero-copy send creates a secondary notification request whose completion state persists until skb ubuf references drain.

## Dependencies and Integration Points
This module depends on core io_uring request/completion APIs, `kbuf` buffer selection, registered resources/fixed buffers, filetable fixed fd install, allocation cache, zero-copy notification support from `notif.c`, zcrx receive support, compat msghdr helpers, socket syscalls/helpers, skb zero-copy APIs, BPF filter context types, and opdef registration. It is compiled behind `CONFIG_NET` entries in `opdef.c`; `net.h` provides stubs for non-NET builds where needed.

## Risks and Edge Cases
- Multishot and bundle paths are stateful and must avoid monopolizing CPU; `MULTISHOT_MAX_RETRY` forces requeue after repeated immediate completions.
- Buffer-selected sends/receives must commit or recycle buffers on every retry/error path to avoid leaks or double use.
- `MSG_WAITALL` partial transfers accumulate `done_io`; final failures may complete with partial byte counts instead of errors.
- Recvmsg multishot writes a header plus sockaddr/control payload into the selected buffer; size calculation and copy-to-user faults must stop the multishot safely.
- Zero-copy send has two CQE streams: the send result and notification CQE. Cleanup must flush the notification on cancellation/failure and preserve `IORING_CQE_F_MORE`.
- Fixed-buffer zero-copy import is deferred until issue for some paths and uses the notification request for resource ownership.
- Accept/socket fixed-file installs must handle failure after file allocation without leaking fds/files.
- Connect has protocol-specific in-progress behavior and must interpret `-EBADFD`/`-EISCONN` through `sock_error()`.

## Test Signals
Tests should cover send/sendmsg/recv/recvmsg raw and vectored forms, compat msghdrs, fixed buffers, buffer selection, bundles, multishot receive limits, `POLL_FIRST`, NOWAIT and `MSG_DONTWAIT`, `MSG_WAITALL` partials, CQE `SOCK_NONEMPTY`/`MORE`/buffer flags, zero-copy send notification success/copy fallback/accounting, zcrx multishot receive, accept multishot normal/fixed fds, socket fixed install, connect retry and socket error completion, bind/listen validation, cleanup on cancellation, and non-CONFIG_NET fallback via opcode support checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/net.h -->
# sources/distributed-fs/ceph-client/io_uring/net.h

## Purpose
`net.h` declares io_uring networking request helpers and the async msghdr cache object. It conditionally exposes full networking APIs when `CONFIG_NET` is enabled and provides minimal no-op stubs for non-network builds.

## Important APIs, Types, and Functions
- `struct io_async_msghdr` stores cached vector state and the clearable msghdr-related fields: name length, fast iovec, control/payload lengths, user address, kernel `msghdr`, and sockaddr storage.
- Declared prep/issue/cleanup APIs cover shutdown, sendmsg/send, recvmsg/recv, send/recv failure, accept, socket, connect, zero-copy send, bind, listen, socket BPF population, and network message cache free.
- Non-CONFIG_NET stubs make `io_netmsg_cache_free()` and `io_socket_bpf_populate()` no-ops.

## Control Flow
The opcode table uses these declarations to wire network opcodes to prep and issue functions. Core request cleanup calls `io_sendmsg_recvmsg_cleanup()` or `io_send_zc_cleanup()` through `io_cold_defs`. Allocation caches call `io_netmsg_cache_free()` when freeing cached async msghdr objects.

## State and Persistence Behavior
`io_async_msghdr` is stored in `req->async_data` and may be recycled in the ring's `netmsg_cache`. The `struct_group(clear, ...)` layout allows the allocation cache to clear only per-use fields while retaining reusable vector allocations.

## Dependencies and Integration Points
It includes kernel net/uio/io_uring type headers and UAPI BPF filter context. It is consumed by `io_uring.c`, `opdef.c`, and network-related opcode handlers. Conditional compilation aligns with opdef's `CONFIG_NET` support decisions.

## Risks and Edge Cases
- The clear-group boundary must match cache initialization in `io_ring_ctx_alloc()`; otherwise stale msghdr state can leak across requests.
- Non-NET builds must not leave dangling references to unavailable issue functions.

## Test Signals
Build tests with `CONFIG_NET=y` and `CONFIG_NET=n` validate declarations/stubs. Runtime tests should verify async msghdr cache reuse does not preserve stale sockaddr/control/iovec state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/nop.c -->
# sources/distributed-fs/ceph-client/io_uring/nop.c

## Purpose
`nop.c` implements `IORING_OP_NOP` and `IORING_OP_NOP128`. Besides a basic no-op completion, it supports test/control flags for injected results, file lookup, fixed-file lookup, fixed-buffer lookup, task-work completion, and 32-byte CQE payloads.

## Important APIs, Types, and Functions
- `struct io_nop` stores result, optional fd, flags, and extra CQE32 payload words.
- `io_nop_prep()` validates `nop_flags`, reads injected result, optional fd, fixed buffer index, and CQE32 extra fields.
- `io_nop()` performs optional file/fixed-buffer lookup, marks failure on negative result, sets normal or 32-byte CQE result, and optionally completes through task_work.

## Control Flow
Prep accepts only `NOP_FLAGS`. If `IORING_NOP_INJECT_RESULT` is set, `sqe->len` becomes the completion result; otherwise result is zero. `IORING_NOP_FILE` records an fd and `IORING_NOP_FIXED_FILE` controls fixed vs normal lookup. `IORING_NOP_FIXED_BUFFER` stores `buf_index`. `IORING_NOP_CQE32` requires a ring configured for CQE32 or mixed CQE and stores extra fields from `off` and `addr`.

Issue optionally resolves a file, optionally finds a fixed buffer resource, marks failure on errors, writes `req->cqe`, and either returns `IOU_COMPLETE` or queues `io_req_task_complete` and returns `IOU_ISSUE_SKIP_COMPLETE` for task-work testing.

## State and Persistence Behavior
State is request-local. A normal file lookup sets `req->file` and follows core cleanup. Fixed file lookup sets `REQ_F_FIXED_FILE`. Fixed buffer lookup attaches resource state through the resource subsystem. CQE32 extras are stored in `req->big_cqe` through `io_req_set_res32()`.

## Dependencies and Integration Points
This module depends on core request helpers and registered resource lookup. `opdef.c` wires it to both NOP opcodes, with `NOP128` marked as requiring a 128-byte SQE in mixed/128 modes.

## Risks and Edge Cases
- CQE32 NOP must reject rings without CQE32/mixed CQE support.
- Injected negative results must call `req_set_fail()` to interact correctly with links and CQE-skip semantics.
- Task-work completion returns skip-complete so the core does not post a duplicate CQE.

## Test Signals
Tests should cover plain NOP, injected positive/negative results, linked NOP failure, normal/fixed file lookup, fixed buffer lookup failure, task-work completion, CQE32 extra data, and NOP128 submission in SQE128/mixed modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/nop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/nop.h -->
# sources/distributed-fs/ceph-client/io_uring/nop.h

## Purpose
`nop.h` declares the prep and issue functions for NOP-style io_uring operations.

## Important APIs, Types, and Functions
- `io_nop_prep()` validates and prepares NOP SQEs.
- `io_nop()` issues the prepared no-op request.

## Control Flow
The opcode table calls these functions for `IORING_OP_NOP` and `IORING_OP_NOP128`.

## State and Persistence Behavior
The header itself stores no state; request-local state is defined in `nop.c`.

## Dependencies and Integration Points
It depends on core `io_kiocb` and SQE types from io_uring headers and is consumed by `opdef.c`.

## Risks and Edge Cases
The header's minimal contract means all capability distinctions, including NOP128 and CQE32 support, must remain in `opdef.c` and `nop.c`.

## Test Signals
Build coverage plus NOP/NOP128 runtime tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/nop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/notif.c -->
# sources/distributed-fs/ceph-client/io_uring/notif.c

## Purpose
`notif.c` implements io_uring zero-copy send notification requests. It creates notification `io_kiocb`s, exposes `ubuf_info_ops` for skb zero-copy completion/linking, aggregates linked notifications, accounts/unaccounts pinned memory, and completes notification CQEs through task_work when skb references drain.

## Important APIs, Types, and Functions
- `io_alloc_notif()` allocates and initializes a notification request with NOP opcode and `ubuf_info`.
- `io_tx_ubuf_complete()` is the skb zero-copy completion callback.
- `io_link_skb()` links compatible io_uring notification ubufs on the same skb.
- `io_notif_tw_complete()` finishes one or a linked list of notifications under `uring_lock`.
- Static `io_ubuf_ops` provides `.complete` and `.link_skb` to networking.

## Control Flow
Zero-copy send prep calls `io_alloc_notif()` under `uring_lock`. The function pulls a request from the normal request cache, initializes core fields, consumes a task reference, clears resource nodes, initializes `io_notif_data`, configures ubuf flags/ops, and sets refcount to one.

When the networking stack completes skb zero-copy, `io_tx_ubuf_complete()` updates report fields for zero-copy used/copied status, decrements the ubuf refcount, and returns until it reaches zero. If the notification is linked to a head, it recursively completes the head. Otherwise it queues task_work on the notification request, lazily waking only when no `next` notifications are linked. `io_notif_tw_complete()` walks the linked notification chain, sets `IORING_NOTIF_USAGE_ZC_COPIED` when reporting requires it, unaccounts pages, and delegates each notification to normal request completion.

`io_link_skb()` either attaches a fresh io_uring ubuf to an skb or links another notification into an existing io_uring notification chain if contexts/task contexts match and the chain is not already merged.

## State and Persistence Behavior
Notification state lives in `struct io_notif_data` embedded in a request command area: file pointer, ubuf info, linked-list pointers, page accounting, report flags, and zero-copy used/copied booleans. The ubuf refcount controls lifetime. Linked notifications share a head ubuf reference and complete in a single task_work chain.

## Dependencies and Integration Points
This module integrates with `net.c` zero-copy send paths, skb zero-copy APIs, io_uring request allocation/completion/task_work, resource memory accounting, and notification helpers declared in `notif.h`.

## Risks and Edge Cases
- Notification completion can be linked recursively; context and task context mismatches are rejected to keep task_work completion valid.
- Memory accounting must be unaccounted exactly once when notification completes.
- Reported `ZC_COPIED` status depends on both success and whether the stack actually used zero-copy.
- Cleanup paths must flush notifications when sends fail or are canceled before skb completion.

## Test Signals
Tests should cover successful zero-copy notification CQEs, copied fallback reporting, linked skb notifications, memory accounting/unaccounting, cancellation cleanup via flush, io-wq cleanup ordering, and context mismatch rejection in `link_skb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/notif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/notif.h -->
# sources/distributed-fs/ceph-client/io_uring/notif.h

## Purpose
`notif.h` declares io_uring zero-copy notification data structures and helpers used by network send paths.

## Important APIs, Types, and Functions
- `IO_NOTIF_UBUF_FLAGS` defines skb ubuf flags for managed zero-copy fragments and orphan behavior.
- `IO_NOTIF_SPLICE_BATCH` defines a batching constant for notification-related splice behavior.
- `struct io_notif_data` stores file, ubuf info, linked notification pointers, accounted pages, and zero-copy report state.
- `io_alloc_notif()` allocates notification requests.
- `io_tx_ubuf_complete()` is the ubuf completion callback.
- `io_notif_to_data()` converts a notification request to its embedded data.
- `io_notif_flush()` forces completion of a notification under `uring_lock`.
- `io_notif_account_mem()` accounts pages against the ring user for non-fixed zero-copy send buffers.

## Control Flow
Zero-copy send prep allocates a notification and optionally calls `io_notif_account_mem()` for the send length. Send issue attaches `io_notif_to_data(notif)->uarg` to the socket message. Cleanup or successful in-ring issue calls `io_notif_flush()` when immediate flushing is required.

## State and Persistence Behavior
`account_pages` accumulates page-accounting charge until completion. `zc_report`, `zc_used`, and `zc_copied` determine notification result flags. `next` and `head` implement linked notification chains.

## Dependencies and Integration Points
It includes net/uio/socket headers and `rsrc.h` for memory accounting. It is used by `net.c` and implemented by `notif.c`.

## Risks and Edge Cases
- `io_notif_account_mem()` estimates pages as `(len >> PAGE_SHIFT) + 2`; callers must pass the same notification that will later unaccount.
- `io_notif_flush()` assumes `uring_lock` is held and invokes the same completion callback path used by networking.

## Test Signals
Tests should verify memory accounting failure paths, flush behavior, report flag propagation, and linked notification completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/notif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/opdef.c -->
# sources/distributed-fs/ceph-client/io_uring/opdef.c

## Purpose
`opdef.c` is the central opcode definition table for io_uring. It maps every `IORING_OP_*` opcode to hot issue metadata (`io_issue_defs`) and cold metadata (`io_cold_defs`), including required file behavior, polling support, buffer selection, async data size, BPF filter context size/population, prep/issue handlers, cleanup hooks, failure hooks, opcode names, and SQE copy hooks.

## Important APIs, Types, and Functions
- `io_issue_defs[]` is indexed by opcode and consumed by core submission/issue paths.
- `io_cold_defs[]` is indexed by opcode and consumed by cleanup, failure, tracing/name lookup, and SQE-copy paths.
- `io_no_issue()` is a sentinel issue function for opcodes such as linked timeout that should never be directly issued.
- `io_eopnotsupp_prep()` is used for conditionally unsupported opcodes when kernel config disables their subsystem.
- `io_uring_get_opcode()` returns the opcode name or `"INVALID"`.
- `io_uring_op_supported()` reports whether an opcode has real support in this build.
- `io_uring_optable_init()` validates table sizes and mandatory prep/issue/name entries at boot.

## Control Flow
Core request initialization reads `io_issue_defs[opcode]` to validate ioprio, IOPOLL compatibility, buffer-select support, SQE128/mixed SQE requirements, file requirements, block plug hints, async data sizes, and BPF filter payload size. It then calls the opcode prep function. Issue calls `def->issue()`, and async fallback uses metadata such as pollin/pollout, hash/unbound workqueue flags, and async size.

Cleanup and failure paths use `io_cold_defs[opcode]`: `cleanup` frees opcode-specific request state, `fail` adjusts opcode-specific failure state such as partial IO or zero-copy notification flags, `sqe_copy` snapshots SQE data before async retry, and `name` supports fdinfo/tracing/debug. `io_uring_optable_init()` runs during io_uring init before request cache creation.

## State and Persistence Behavior
The tables are static const global state. They encode persistent behavioral policy for every opcode in the build. Conditional entries use `io_eopnotsupp_prep` when `CONFIG_NET`, `CONFIG_EPOLL`, or `CONFIG_FUTEX` support is absent, allowing `io_uring_op_supported()` and prep-time validation to reject unsupported operations cleanly.

## Dependencies and Integration Points
This file includes nearly every opcode module header: xattr, nop, fs, splice, sync, advise, open/close, uring_cmd, epoll, statx, net, msg_ring, timeout, poll, cancel, rw, waitid, futex, truncate, zcrx, plus core refs/tctx/sqpoll/fdinfo/kbuf/rsrc. It is the dispatch glue between `io_uring.c` and all opcode implementations.

## Risks and Edge Cases
- Table order must exactly match `IORING_OP_*` numeric values and `IORING_OP_LAST`; mismatches are caught by boot-time build/BUG checks but can be severe.
- Missing cleanup/fail/sqe_copy hooks cause leaks or wrong retry behavior for opcodes with allocated state or userspace pointers.
- Incorrect `needs_file`, `iopoll`, `buffer_select`, `pollin/pollout`, or async size metadata changes core behavior before the handler runs.
- Conditional support must use `io_eopnotsupp_prep`; a null prep or issue pointer is a boot BUG.
- SQE128-only opcodes (`NOP128`, `URING_CMD128`) require `is_128` metadata so the core consumes the correct SQE footprint.

## Test Signals
Build-time `io_uring_optable_init()` checks are primary. Runtime tests should verify `io_uring_op_supported()` under different kernel configs, every opcode's prep/issue dispatch, cleanup/fail hooks for cancellation, buffer-select capability enforcement, IOPOLL rejection for unsupported ops, SQE128/mixed behavior, BPF filter payload population, and opcode names in diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/opdef.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/opdef.h -->
# sources/distributed-fs/ceph-client/io_uring/opdef.h

## Purpose
`opdef.h` declares the opcode metadata structures and global tables that bind core io_uring submission to individual opcode handlers.

## Important APIs, Types, and Functions
- `struct io_issue_def` contains hot-path metadata: file requirement, block plug hint, ioprio/iopoll support, buffer selection support, workqueue hashing/unbound hints, poll direction/exclusive flags, audit skipping, vectored flag, 128-byte SQE flag, async data size, BPF filter payload size, issue/prep callbacks, and BPF populate callback.
- `struct io_cold_def` contains colder metadata: opcode name, SQE copy hook, cleanup hook, and fail hook.
- `io_issue_defs[]` and `io_cold_defs[]` are extern arrays indexed by opcode.
- `io_uring_op_supported()` reports build-time opcode availability.
- `io_uring_optable_init()` performs boot-time validation.

## Control Flow
The core initializes requests using `io_issue_defs[opcode].prep`, later issues through `.issue`, and consults metadata before either step. Cleanup and failure paths consult `io_cold_defs[opcode]`. BPF filtering uses `filter_pdu_size` and `filter_populate`.

## State and Persistence Behavior
The header defines static metadata contracts; actual state lives in the arrays in `opdef.c`. The tables are immutable after initialization.

## Dependencies and Integration Points
It forward-declares `struct io_uring_bpf_ctx` and relies on core `struct io_kiocb` and SQE types. It is included by `io_uring.h`, opcode handlers, and dispatch code.

## Risks and Edge Cases
- Bitfield metadata is compact and hot-path-sensitive; adding a new opcode capability requires updating both the struct and all relevant core consumers.
- Async data sizes must match the handler's expected `req->async_data` layout.
- `is_128` must be set for opcodes that consume 128-byte SQEs.

## Test Signals
Compile-time and boot-time table validation plus broad opcode selftests validate this header contract. New opcodes should add tests for metadata-driven rejection and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/opdef.h -->
