# Group Research: group_882_linux_sources_os_linux_linux_io_uring_openclose_c_sources_os_linux_l_df3769087c3d

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/linux/linux`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/openclose.c -->
# File Research: sources/os/linux/linux/io_uring/openclose.c

Implements io_uring open, close, fixed-fd install, and pipe operations.

Key responsibilities:
- Handles `IORING_OP_OPENAT` and `IORING_OP_OPENAT2`, including `open_how` parsing, delayed pathname capture, `O_LARGEFILE`, `RESOLVE_CACHED`, and normal vs fixed-file installation.
- Handles `IORING_OP_CLOSE` for normal task fds and fixed-file slots.
- Implements `IORING_OP_FIXED_FD_INSTALL`, receiving a fixed file into the task fd table.
- Implements pipe creation into normal fd pairs or fixed-file table slots.

Important behavior:
- Open requests force async for `O_TRUNC`, `O_CREAT`, and `__O_TMPFILE`.
- Fixed opens reject `O_CLOEXEC` because fixed slots are not process fds.
- Normal close rejects io_uring files to avoid recursive ring lifetime problems.
- Fixed pipe mode installs both pipe ends under `ctx->uring_lock` and rolls back installed slots on userspace copy failure.

Concurrency:
- Fixed-file mutations use `io_ring_submit_lock()`.
- Normal fd close validates and removes under `files->file_lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/openclose.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/openclose.h -->
# File Research: sources/os/linux/linux/io_uring/openclose.h

Header for io_uring open, close, pipe, and fixed-fd install operations.

Exports:
- Open prep/issue/cleanup entry points for openat and openat2.
- `io_openat_bpf_populate()` for BPF-visible open fields.
- Fixed close helper `__io_close_fixed()`.
- Normal close, pipe, and fixed-fd install entry points.

Important invariant:
- `__io_close_fixed()` takes a zero-based fixed-file slot offset, while SQE `file_index` is generally one-based except special allocation cases.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/openclose.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/poll.c -->
# File Research: sources/os/linux/linux/io_uring/poll.c

Implements io_uring poll and async-poll retry machinery.

Key responsibilities:
- Arms poll waitqueue entries through `vfs_poll()`.
- Implements `IORING_OP_POLL_ADD`, `IORING_OP_POLL_REMOVE`, poll update, cancellation, and teardown.
- Provides async-poll support for other opcodes that need readiness before retry.
- Supports multishot poll and multishot read retry integration.

Core data flow:
- `__io_arm_poll_handler()` initializes poll state, calls `vfs_poll()`, attaches waitqueue entries, inserts into `ctx->cancel_table`, and decides inline vs armed completion.
- `io_poll_wake()` filters readiness masks, handles `POLLFREE`, optionally removes oneshot wait entries, and schedules task_work.
- `io_poll_check_events()` rechecks readiness, posts multishot CQEs, reissues operations, or completes/cancels.
- `io_poll_remove()` disarms an existing poll request and optionally updates events or user data before rearming.

Concurrency:
- `req->poll_refs` combines ownership refs with cancel/retry flags.
- Waitqueue removal is RCU protected to tolerate `wake_up_pollfree()`.
- Cancel-table changes are serialized under `ctx->uring_lock`.

Important invariants:
- Error and hangup bits are always included via `IO_POLL_UNMASK`.
- `EPOLLONESHOT` is added unless multishot or level-trigger behavior is requested.
- Single and double waitqueue entries are tracked with `REQ_F_SINGLE_POLL` and `REQ_F_DOUBLE_POLL`.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/poll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/poll.h -->
# File Research: sources/os/linux/linux/io_uring/poll.h

Header for io_uring poll state and poll entry points.

Defines:
- `struct io_poll`, the waitqueue entry and event mask state.
- `struct async_poll`, wrapping primary and optional secondary poll entries.
- Async-poll result codes: ok, aborted, ready.
- Poll add/remove prep and issue functions.
- Async poll arming, cancellation, teardown, and task_work callback entry points.

Important invariant:
- `io_poll_multishot_retry()` is only valid when the caller owns the multishot poll request or is running in multishot issue context.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/poll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/query.c -->
# File Research: sources/os/linux/linux/io_uring/query.c

Implements `IORING_REGISTER_QUERY`.

Key responsibilities:
- Supports query records for opcode/register/flag availability, zero-copy receive capability, and shared completion queue layout.
- Traverses a user-provided linked list of `io_uring_query_hdr` records.
- Copies bounded result payloads back to userspace and writes per-entry `hdr.result`.

Important behavior:
- `nr_args` must be zero.
- Reserved fields and preexisting `result` must be zero.
- Unknown query opcodes return `-EOPNOTSUPP` in the entry result.
- Traversal is capped by `IO_MAX_QUERY_ENTRIES` to avoid cycles.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/query.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/query.h -->
# File Research: sources/os/linux/linux/io_uring/query.h

Small header for io_uring query registration.

Exports:
- `io_query(void __user *arg, unsigned nr_args)`.

Role:
- Provides the registration dispatcher with the query helper used both for ring-bound and blind query registration.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/query.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/refs.h -->
# File Research: sources/os/linux/linux/io_uring/refs.h

Inline helpers for `io_kiocb` request reference counting.

Key responsibilities:
- Provides guarded increment/decrement helpers for requests with `REQ_F_REFCOUNT`.
- Detects zero or near-overflow refcount states using the same style as mm page ref checks.
- Initializes request refcount state with `io_req_set_refcount()`.

Important invariants:
- Most helpers warn if called on a request without `REQ_F_REFCOUNT`.
- `req_ref_put_and_test()` fast-paths unrefcounted requests as immediately releasable.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/refs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/register.c -->
# File Research: sources/os/linux/linux/io_uring/register.c

Implements the `io_uring_register()` syscall dispatcher and many ring registration operations.

Key responsibilities:
- Dispatches buffer/file registration, updates, eventfd, probe, personalities, restrictions, ring enabling, provided buffers, NAPI, clocks, clone buffers, zero-copy receive, ring resize, memory regions, query, BPF filters, and ring-fd registration.
- Supports blind registration operations that do not require a ring fd.
- Enforces register restrictions when rings have registered policy.
- Handles registered-ring lookup via `IORING_REGISTER_USE_REGISTERED_RING`.

Notable registration flows:
- `io_probe()` reports supported opcodes.
- Personality registration stores current credentials in an xarray.
- Restrictions can be ring-scoped or task-scoped and require disabled rings or appropriate privilege/no-new-privs.
- IOWQ affinity and worker limits may need SQPOLL-specific lock ordering.
- Ring resizing allocates new ring/SQE regions, copies pending SQ/CQ entries, swaps under mmap and completion locks, and RCU-synchronizes old ring pointers.
- Memory-region registration can publish a parameter/wait-argument region.

Concurrency and locking:
- Main registration runs under `ctx->uring_lock`.
- SQPOLL worker-limit updates temporarily drop/reacquire locks to respect `sqd->lock -> ctx->uring_lock` ordering.
- Ring resize coordinates `mmap_lock`, `completion_lock`, SQPOLL park/unpark, and RCU.

Important risks:
- `submitter_task` restrictions reject registration from other tasks.
- Resize fails with `-EOVERFLOW` if pending SQ/CQ entries do not fit.
- BPF filter registration publishes filter pointers only after successful install.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/register.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/register.h -->
# File Research: sources/os/linux/linux/io_uring/register.h

Small registration header.

Exports:
- `io_eventfd_unregister()`.
- `io_unregister_personality()`.

Role:
- Shares unregister helpers needed outside the main registration dispatcher.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/register.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/rsrc.c -->
# File Research: sources/os/linux/linux/io_uring/rsrc.c

Implements io_uring registered resources: fixed files, fixed buffers, resource updates, buffer cloning, and fixed-buffer import.

Key responsibilities:
- Accounts pinned memory against `RLIMIT_MEMLOCK`, user locked pages, and optional mm pinned counters.
- Registers/unregisters fixed file tables and fixed buffer tables.
- Updates fixed file/buffer slots, including sparse registration and allocated fixed-file slot mode.
- Pins user buffers, coalesces huge folios into fewer bvecs when safe, and builds `io_mapped_ubuf`.
- Imports registered buffers as `iov_iter` instances for fixed read/write and uring_cmd users.
- Supports kernel bvec buffer registration for uring_cmd/block users.
- Clones registered buffer mappings between rings sharing the same accounting context.

Important behavior:
- Fixed file registration rejects io_uring files.
- Resource tags generate auxiliary CQEs when tagged resources are freed.
- Buffer registration allows zero-length/null entries as sparse removals but rejects tags on empty slots.
- Fixed range validation ensures requested IO lies within the registered buffer and below `MAX_RW_COUNT`.
- Kernel bvec buffers carry direction flags and custom release callbacks.

Concurrency:
- Resource table mutation runs under `ctx->uring_lock`.
- Buffer node lookup increments per-node refs while holding the ring lock.
- Cloning two rings locks them in address order to avoid deadlock.

Important risks:
- Huge-page accounting avoids double-counting compound pages already represented in the current or existing buffer table.
- Cloned buffers share `io_mapped_ubuf` refs and require matching user/mm accounting owners.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/rsrc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/rsrc.h -->
# File Research: sources/os/linux/linux/io_uring/rsrc.h

Header for io_uring fixed resource management.

Defines:
- Resource types for files and buffers.
- `struct io_rsrc_node`, holding a tag plus fixed file pointer or mapped buffer.
- `struct io_mapped_ubuf`, representing pinned user or kernel bvec buffers.
- Folio coalescing metadata for large registered buffers.

Exports:
- Resource cache init/free, node allocation/free, table allocation/free.
- Fixed buffer import helpers for single buffers and fixed iovec vectors.
- File/buffer registration, update, unregister, and clone-buffer APIs.
- Memory accounting helpers and vector allocation helpers.

Important invariants:
- `io_put_rsrc_node()` and `io_reset_rsrc_node()` require `ctx->uring_lock`.
- `io_rsrc_node_lookup()` uses nospec masking for valid indices.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/rsrc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/rw.c -->
# File Research: sources/os/linux/linux/io_uring/rw.c

Implements io_uring read, write, vectored read/write, fixed-buffer read/write, multishot read, and IOPOLL completion.

Key responsibilities:
- Prepares `kiocb` state, ioprio, offsets, rw flags, optional PI metadata, and buffer imports.
- Imports normal user buffers, vectored buffers, selected provided buffers, and fixed registered buffers.
- Handles normal read/write issue, fallback legacy `->read`/`->write`, partial IO, retry, completion, and cleanup.
- Supports multishot reads with provided buffers.
- Implements IOPOLL and hybrid IOPOLL polling/completion.

Important behavior:
- Nonblocking issue sets `IOCB_NOWAIT` only when file/poll capability supports it.
- Buffered read retry can arm page-unlock waitqueue callbacks for async task_work retry.
- Partial reads/writes can accumulate `bytes_done` and reissue in blocking context when appropriate.
- PI metadata is limited to direct IO on files with `FMODE_HAS_METADATA`.
- Multishot read requires provided buffers and a pollable file.

Concurrency and lifetime:
- Async RW state is cached in `ctx->rw_cache` but cleanup is delayed for io-wq/refcounted paths to avoid UAF with filesystems that inspect iter state after queueing.
- IOPOLL completion uses release/acquire ordering on `req->iopoll_completed`.
- Selected buffers are returned/recycled with CQE flags on completion.

Important risks:
- Legacy looped read/write rejects kernel registered bvec buffers.
- NOWAIT `-EOPNOTSUPP` is normalized to `-EAGAIN` for retry.
- Short writes on regular/block files are traced and retried carefully after ending write accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/rw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/rw.h -->
# File Research: sources/os/linux/linux/io_uring/rw.h

Header for io_uring read/write operation state.

Defines:
- `struct io_meta_state` for PI metadata iterator restoration.
- `struct io_async_rw`, holding cached iovec storage, bytes done, main iterator state, buffer group, and a union of buffered-IO waitqueue or direct-IO metadata state.

Exports:
- Prep/issue functions for read, write, readv, writev, fixed read/write, fixed readv/writev.
- Cleanup, failure, task_work completion, multishot read, and RW cache free helpers.

Important invariant:
- The union means buffered-IO waitqueue retry state and PI metadata state are mutually exclusive.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/rw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/slist.h -->
# File Research: sources/os/linux/linux/io_uring/slist.h

Internal singly linked list helpers for io_uring work queues.

Key responsibilities:
- Provides iteration macros for `io_wq_work_list`.
- Provides empty/init checks.
- Adds nodes after a position or at tail.
- Cuts/deletes nodes while maintaining `first` and `last`.
- Supports stack-style head insertion and extraction.
- Provides `wq_next_work()` to recover the containing `io_wq_work`.

Important invariant:
- Tail maintenance is explicit; callers must pass the correct previous node for cuts/deletes.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/slist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/splice.c -->
# File Research: sources/os/linux/linux/io_uring/splice.c

Implements io_uring splice and tee operations.

Key responsibilities:
- Prepares splice/tee SQEs, validates splice flags, captures input fd and offsets, and forces async execution.
- Supports normal input fds and fixed input fds via `SPLICE_F_FD_IN_FIXED`.
- Issues `do_splice()` and `do_tee()` with io_uring completion semantics.
- Cleans up fixed input resource node refs.

Important behavior:
- Fixed input fd lookup increments resource node refs under `ctx->uring_lock`.
- Both operations warn if issued in nonblocking context because they are forced async.
- Completion marks failure when the returned byte count differs from requested length.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/splice.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/splice.h -->
# File Research: sources/os/linux/linux/io_uring/splice.h

Header for io_uring splice and tee operations.

Exports:
- Tee prep and issue functions.
- Splice prep, issue, and cleanup functions.

Role:
- Shares splice operation entry points with the opcode dispatch table.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/splice.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/sqpoll.c -->
# File Research: sources/os/linux/linux/io_uring/sqpoll.c

Implements SQPOLL submission-side polling and the SQPOLL kernel thread.

Key responsibilities:
- Creates, attaches, parks, unparks, stops, and frees `io_sq_data`.
- Runs a kernel thread that polls SQ rings, submits SQEs, performs IOPOLL, runs task_work, and optionally performs NAPI busy polling.
- Supports sharing SQPOLL worker state with `IORING_SETUP_ATTACH_WQ`.
- Supports SQ thread CPU affinity and IOWQ affinity updates.

Important behavior:
- Shared SQPOLL rings cap per-ring submissions for fairness.
- Worker executes with ring submitter credentials when needed.
- `IORING_SQ_NEED_WAKEUP` is set before sleeping and cleared after wake.
- SQPOLL creation validates security policy and CPU affinity/cpuset constraints.
- Attached SQPOLL workers require matching thread group id.

Concurrency:
- `sqd->lock` serializes thread pointer, ctx list, park/unpark, and stop state.
- Park uses `park_pending` plus state bits to avoid races with nested park requests.
- Shutdown cancels generic io_uring work and marks rings as needing wakeup.

Important risks:
- Attaching to a dying SQPOLL thread returns `-ENXIO`.
- Thread task context allocation failure after thread creation is handled through normal stop/finish cleanup.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/sqpoll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/sqpoll.h -->
# File Research: sources/os/linux/linux/io_uring/sqpoll.h

Header for SQPOLL state and helpers.

Defines:
- `struct io_sq_data`, including refs, park state, context list, thread pointer, waitqueue, idle timeout, CPU/pid metadata, work time, state bits, and exit completion.

Exports:
- SQ offload creation, finish/stop, park/unpark, ref put, SQ wait, CPU affinity, CPU time accounting.
- `sqpoll_task_locked()` RCU-protected accessor requiring `sqd->lock`.

Important invariant:
- Access to `sqd->thread` is protected by `sqd->lock` for the inline accessor.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/sqpoll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/statx.c -->
# File Research: sources/os/linux/linux/io_uring/statx.c

Implements io_uring `statx`.

Key responsibilities:
- Prepares `statx` SQEs, captures dirfd, mask, flags, output buffer, and delayed pathname.
- Rejects fixed-file mode.
- Forces async execution.
- Issues `do_statx()` and completes the request.
- Cleans up delayed filename state.

Important behavior:
- `delayed_getname_uflags()` is used so pathname capture respects statx flags.
- Nonblocking issue is not expected because requests are forced async.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/statx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/statx.h -->
# File Research: sources/os/linux/linux/io_uring/statx.h

Header for io_uring statx support.

Exports:
- `io_statx_prep()`.
- `io_statx()`.
- `io_statx_cleanup()`.

Role:
- Connects statx opcode dispatch to prep, issue, and cleanup.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/statx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/sync.c -->
# File Research: sources/os/linux/linux/io_uring/sync.c

Implements io_uring sync and allocation operations.

Key responsibilities:
- Handles `sync_file_range`, `fsync`, and `fallocate`.
- Validates SQE fields and stores offset/length/flags/mode in `struct io_sync`.
- Forces async execution for all operations.
- Issues `sync_file_range()`, `vfs_fsync_range()`, and `vfs_fallocate()`.

Important behavior:
- `fsync` accepts only `IORING_FSYNC_DATASYNC` and rejects negative offsets.
- `fallocate` emits `fsnotify_modify()` on success.
- All issue paths warn if somehow invoked in nonblocking context.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/sync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/sync.h -->
# File Research: sources/os/linux/linux/io_uring/sync.h

Header for io_uring sync-related operations.

Exports:
- Prep/issue functions for `sync_file_range`.
- Prep/issue functions for `fsync`.
- Prep/issue functions for `fallocate`.

Role:
- Provides opcode dispatch entry points for blocking filesystem synchronization/allocation operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/sync.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/tctx.c -->
# File Research: sources/os/linux/linux/io_uring/tctx.c

Implements per-task io_uring context management and registered ring-fd support.

Key responsibilities:
- Allocates and frees `io_uring_task` contexts.
- Creates per-task io-wq offload state and shared hash maps.
- Installs/removes task-to-ring nodes in task xarray and ring task lists.
- Cleans task context on exit.
- Registers/unregisters io_uring ring fds in per-task registered ring slots.
- Clones task restrictions across fork.

Important behavior:
- New task contexts inherit ring IOWQ limits if already set.
- `SINGLE_ISSUER` rings reject submitter changes.
- io-wq keepalive is reactivated on new io_uring usage and set to idle-exit when the task no longer has ring nodes.
- Registered ring fds must refer to io_uring files and can be installed at a requested slot or first free slot.

Concurrency:
- `ctx->tctx_lock` protects each ring’s task-context list.
- The task xarray maps ring context pointer values to `io_tctx_node`.
- Ring-fd registration temporarily drops `ctx->uring_lock` to ensure task context setup.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/tctx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/tctx.h -->
# File Research: sources/os/linux/linux/io_uring/tctx.h

Header for per-task io_uring context support.

Defines:
- `struct io_tctx_node`, linking a task and ring context.

Exports:
- Task context allocation, node add/delete, cleanup.
- Registered ring-fd unregister/register helpers.
- Fast inline `io_uring_add_tctx_node()` using `tctx->last` cache.

Important invariant:
- The `last` ring cache avoids repeated xarray/list work when the current task keeps submitting to the same ring.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/tctx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/timeout.c -->
# File Research: sources/os/linux/linux/io_uring/timeout.c

Implements io_uring timeout, linked timeout, timeout remove/update, and timeout cancellation.

Key responsibilities:
- Parses relative/absolute/immediate timeout values with monotonic, boottime, or realtime clocks.
- Arms normal timeouts, sequence-based completion-count timeouts, linked timeouts, and multishot timeouts.
- Flushes completion-count timeouts as CQEs advance.
- Removes or updates existing normal/linked timeouts.
- Cancels timeouts by user data or task/ring teardown.
- Disarms linked timeout chains and fails dependent links when needed.

Important behavior:
- Multishot timeouts rearm and post `IORING_CQE_F_MORE` until repeats are exhausted or CQE posting fails.
- Linked timeout expiry tries to cancel the previous linked request and completes with `-ETIME` semantics.
- `IORING_TIMEOUT_ETIME_SUCCESS` suppresses request failure marking on timeout.
- Absolute times are translated through time namespaces.

Concurrency:
- Timeout lists and hrtimers are protected by `ctx->timeout_lock`.
- Some linked timeout operations also require `completion_lock`.
- Request references protect linked heads during timer expiry races.

Important risks:
- `hrtimer_try_to_cancel() == -1` means another path owns completion.
- Completion-count timeout sequence math handles wraparound by comparing differences from the last flush sequence.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/timeout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/timeout.h -->
# File Research: sources/os/linux/linux/io_uring/timeout.h

Header for io_uring timeout support.

Defines:
- `struct io_timeout_data`, holding the owning request, hrtimer, time, mode, and flags.

Exports:
- Timeout flush, cancellation, teardown, linked timeout queue/disarm.
- Prep/issue functions for timeout, linked timeout, timeout remove/update.

Role:
- Shares timeout control APIs with completion, cancellation, and opcode dispatch code.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/timeout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/truncate.c -->
# File Research: sources/os/linux/linux/io_uring/truncate.c

Implements io_uring `ftruncate`.

Key responsibilities:
- Validates SQE fields for ftruncate.
- Captures target length from `sqe->off`.
- Forces async execution.
- Issues `do_ftruncate()` against the request file and completes with its return value.

Important behavior:
- Rejects unrelated SQE fields including rw flags, addr, len, buf index, splice fd, and addr3.
- Warns if issued in nonblocking context because it is forced async.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/truncate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/truncate.h -->
# File Research: sources/os/linux/linux/io_uring/truncate.h

Header for io_uring ftruncate support.

Exports:
- `io_ftruncate_prep()`.
- `io_ftruncate()`.

Role:
- Connects ftruncate opcode dispatch to prep and issue handlers.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/truncate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/tw.c -->
# File Research: sources/os/linux/linux/io_uring/tw.c

Implements io_uring task_work and local task_work execution.

Key responsibilities:
- Runs fallback task_work from delayed work when normal task_work cannot be queued.
- Processes per-task task_work lists grouped by ring context.
- Supports deferred task-run local work lists for `IORING_SETUP_DEFER_TASKRUN`.
- Marks shared SQ flags for `IORING_SQ_TASKRUN`.
- Wakes submitter tasks based on completion wait thresholds.
- Moves local work to fallback lists during exit/slow paths.
- Runs bounded local work loops with retry lists.

Important behavior:
- Task_work processing locks each ring, gets `ctx->refs`, computes termination state, invokes request callbacks, and flushes completions.
- Local work uses `work_llist` and `retry_llist` to cap work and preserve remaining entries.
- Lazy wake can be disabled for linked requests or forced wake conditions.
- Fallback work holds refs per context and schedules `fallback_work`.

Concurrency:
- Local work enqueue uses `try_cmpxchg()` on the llist head and pairs with wait-state barriers.
- RCU is used when marking taskrun during possible ring resizing.
- `ctx->uring_lock` protects local work migration from races with retry lists.

Important risks:
- Work may be completed under cancellation state if task/ring is exiting.
- Deferred task-run is allowed only for the submitter task.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/tw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/tw.h -->
# File Research: sources/os/linux/linux/io_uring/tw.h

Header and inline helpers for io_uring task_work.

Defines:
- Default local task_work batch size.
- `io_should_terminate_tw()` conditions for terminating work: exiting task, fallback kthread, or dying ring refs.

Exports:
- Normal/local/remote task_work add functions.
- Task_work execution helpers for task context and local ring work.
- Fallback task_work functions.
- Pending-work checks and permission checks for deferred task-run.

Important behavior:
- `__io_req_task_work_add()` chooses local work for `IORING_SETUP_DEFER_TASKRUN`, otherwise normal task_work.
- `io_run_task_work()` handles notify-signal clearing, io-worker resume work, per-task io_uring task work, and generic `task_work_run()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/tw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/uring_cmd.c -->
# File Research: sources/os/linux/linux/io_uring/uring_cmd.c

Implements io_uring command passthrough support for file operations exposing `uring_cmd`.

Key responsibilities:
- Prepares uring_cmd SQEs, validates command flags, supports fixed buffers and multishot commands.
- Copies SQEs for async lifetime when needed.
- Issues commands through `file->f_op->uring_cmd`.
- Supports command cancellation, task-context completion, deferred completion, IOPOLL completion, fixed-buffer import, fixed-vector import, blocking requeue, and multishot poll/CQE helpers.

Important behavior:
- Multishot command use must match provided-buffer selection.
- Fixed command mode rejects multishot command flag.
- IOPOLL command completion uses `iopoll_completed`; cancelable tracking is disabled for IOPOLL because hash node storage overlaps.
- CQE32/mixed CQE support sets extra result fields and flags when requested.
- Security hook `security_uring_cmd()` gates command issue.

Concurrency:
- Cancelable commands are tracked in `ctx->cancelable_uring_cmd` under `ctx->uring_lock`.
- `__io_uring_cmd_done()` removes cancelable state before completing.
- Deferred completion requires locked context and rejects unlocked misuse.

Important risks:
- Drivers remain responsible for cancellation races after receiving `IO_URING_F_CANCEL`.
- Multishot completion helper must use the buffer selection returned in the same submission context.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/uring_cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/uring_cmd.h -->
# File Research: sources/os/linux/linux/io_uring/uring_cmd.h

Header for io_uring command passthrough.

Defines:
- `struct io_async_cmd`, containing reusable vector storage and space for copied 64-byte or 128-byte SQEs.

Exports:
- Command prep/issue/SQE-copy/cleanup.
- Command cancellation scan.
- CQE32 multishot posting helper.
- Command async cache free.
- Multishot poll arming helper.

Role:
- Shares uring_cmd operation hooks with dispatch, cancellation, and driver-facing helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/uring_cmd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/wait.c -->
# File Research: sources/os/linux/linux/io_uring/wait.c

Implements waiting for io_uring completion queue events.

Key responsibilities:
- Waits until the CQ ring has at least `min_events`, or until timeout/signal/error.
- Runs local and normal task_work while waiting.
- Handles CQ overflow flush and dropped CQ detection.
- Supports absolute/relative timeout and minimum wait time.
- Supports temporary signal mask replacement.
- Integrates NAPI busy polling and iowait accounting.

Important behavior:
- `io_wake_function()` wakes only when enough CQEs/work are visible.
- Min-timeout first waits for a minimum duration, then switches to normal timeout if no events/work arrived.
- `IORING_SETUP_DEFER_TASKRUN` uses `ctx->cq_wait_nr` instead of a normal waitqueue entry.
- Return is zero if CQ head/tail indicates an event is now available, even if the schedule path observed a timeout.

Concurrency:
- Shared ring head/tail reads use ordering helpers and RCU-protected ring pointer access.
- `cq_wait_nr` uses sentinel values from `wait.h` to avoid accidental wake matches.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/wait.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/wait.h -->
# File Research: sources/os/linux/linux/io_uring/wait.h

Header for io_uring CQ wait support.

Defines:
- `IO_CQ_WAKE_INIT`, sentinel for no CQ waiters.
- `IO_CQ_WAKE_FORCE`, forced wake marker.
- `struct ext_arg`, carrying wait timeout, signal mask, minimum time, and iowait mode.

Exports:
- `io_cqring_wait()`.
- `io_run_task_work_sig()`.
- CQ overflow flush helpers.
- Inline CQ event counters for kernel-cached and userspace-visible head/tail values.

Important invariant:
- `io_cqring_events()` performs a read memory barrier before using cached CQ tail against userspace head.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/wait.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/waitid.c -->
# File Research: sources/os/linux/linux/io_uring/waitid.c

Implements async io_uring support for `waitid`.

Key responsibilities:
- Prepares waitid requests and async wait state.
- Registers a child-exit waitqueue callback.
- Calls `__do_wait()` inline and from task_work.
- Copies `siginfo` results to normal or compat userspace layouts.
- Supports cancellation by user data/task/ring teardown.

Important behavior:
- `kernel_waitid_prepare()` builds wait options from SQE fields.
- `-ERESTARTSYS` means the request remains armed on the child waitqueue.
- Wake callback claims ownership through `refs`, removes the waitqueue entry, and schedules task_work.
- Cancellation sets a high cancel bit and completes with `-ECANCELED` only if it wins ownership.
- Positive wait return is translated to success with `SIGCHLD` siginfo.

Concurrency:
- `refs` combines cancellation flag and ownership count.
- Waitqueue head pointer is release/acquire protected so removal and callback do not race with freed state.
- `ctx->waitid_list` is used for cancellation lookup under ring locking.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/waitid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/waitid.h -->
# File Research: sources/os/linux/linux/io_uring/waitid.h

Header for async io_uring waitid.

Defines:
- `struct io_waitid_async`, containing the request pointer and kernel `wait_opts`.

Exports:
- Waitid prep and issue functions.
- Waitid cancellation and remove-all helpers.

Role:
- Exposes waitid operation state to opcode dispatch and cancellation code.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/waitid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/xattr.c -->
# File Research: sources/os/linux/linux/io_uring/xattr.c

Implements io_uring extended attribute operations.

Key responsibilities:
- Prepares and issues `getxattr`, `fgetxattr`, `setxattr`, and `fsetxattr`.
- Imports xattr names and setxattr values into kernel-owned storage.
- Captures delayed pathnames for path-based operations.
- Forces async execution and cleans allocated xattr/path resources.

Important behavior:
- Path-based operations reject fixed-file mode.
- `getxattr` rejects nonzero xattr flags.
- `setxattr_copy()` imports name/value and validates set flags through VFS helpers.
- Completion clears `REQ_F_NEED_CLEANUP`, frees resources, and sets request result.
- Issue paths warn if invoked nonblocking.

Resource lifetime:
- Cleanup frees delayed filename, kernel xattr name, and kernel xattr value.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/xattr.h -->
# File Research: sources/os/linux/linux/io_uring/xattr.h

Header for io_uring xattr support.

Exports:
- Cleanup helper.
- Prep/issue functions for fsetxattr, setxattr, fgetxattr, and getxattr.

Role:
- Connects xattr opcode dispatch to prep, issue, and cleanup paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/xattr.h -->