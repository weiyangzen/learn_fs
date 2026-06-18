# Research: subset-b-006007

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/openclose.c -->
# sources/distributed-fs/ceph-client/io_uring/openclose.c

Purpose: implements io_uring open, close, fixed-file install, and pipe operations. It translates SQE fields into VFS open/close/pipe actions while respecting fixed-file tables and async-only paths.

Important APIs/types/functions: `struct io_open`, `struct io_close`, `struct io_fixed_install`, and `struct io_pipe` are the per-op command payloads. Entry points include `io_openat_prep()`, `io_openat2_prep()`, `io_openat2()`, `io_close_prep()`, `io_close()`, `io_install_fixed_fd_prep()`, `io_install_fixed_fd()`, `io_pipe_prep()`, and `io_pipe()`. `__io_close_fixed()` is exported to other io_uring resource paths.

Control flow: prep validates unused SQE fields, copies paths or `open_how`, captures rlimits, and marks cleanup or forced async where required. Open uses `build_open_flags()`, optional `LOOKUP_CACHED`/`O_NONBLOCK` for nonblocking issue, VFS `do_file_open()`, then either installs a normal fd or inserts into the fixed file table. Close removes a fixed slot or safely extracts an fd under `files->file_lock`, punting flush-capable files to async. Pipe creates both files, then installs them in normal fd space or adjacent/allocated fixed slots.

State and persistence: state changes are fd table entries, io_uring fixed-file table slots, file references, pipe file objects, and delayed filename storage. No disk state is kept directly, but open/close may trigger filesystem side effects.

Dependencies/integration: integrates with VFS namei/open helpers, file descriptor allocation, pipe creation, fixed-file helpers in `filetable`/`rsrc`, BPF filter population for open, and io_uring completion flags.

Risks/test signals: important risks are cleanup of delayed names on retries, fixed-slot rollback on pipe copy-to-user failure, `O_CLOEXEC` rejection for fixed opens/pipes, and avoiding recursive registration of io_uring fds. Test with normal and fixed open/close, open retry with `RESOLVE_CACHED`, close of flush files, fixed fd install credentials, pipe fixed-slot allocation, and faulted user fd arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/openclose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/openclose.h -->
# sources/distributed-fs/ceph-client/io_uring/openclose.h

Purpose: declares the open/close/pipe/fixed-fd operation interface used by the io_uring opcode dispatch table and resource helpers.

Important APIs/types/functions: prototypes cover `__io_close_fixed()`, prep/issue pairs for `openat`, `openat2`, `close`, `pipe`, and `install_fixed_fd`, plus `io_open_cleanup()` and `io_openat_bpf_populate()`.

Control flow: this header has no runtime control flow; it provides the contract that operation definitions call during SQE prep, issue, and cleanup.

State and persistence: no state is defined here. The visible API implies ownership transfer rules for fixed files and delayed filename cleanup implemented in `openclose.c`.

Dependencies/integration: includes `bpf_filter.h` because open requests can be exposed to io_uring BPF filtering. Other users need `io_ring_ctx`, `io_kiocb`, and `io_uring_sqe` definitions from the wider io_uring type set.

Risks/test signals: header drift would break opcode registration or cleanup hooks. Build coverage is the main signal; behavioral tests live with `openclose.c` and fixed-file resource paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/openclose.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/poll.c -->
# sources/distributed-fs/ceph-client/io_uring/poll.c

Purpose: implements explicit `POLL_ADD`/`POLL_REMOVE` and internal async-poll arming used to retry operations when files are not immediately ready.

Important APIs/types/functions: key local types are `io_poll_update` and `io_poll_table`. Public entry points are `io_poll_add_prep()`, `io_poll_add()`, `io_poll_remove_prep()`, `io_poll_remove()`, `io_poll_cancel()`, `io_poll_remove_all()`, `io_arm_apoll()`, `io_arm_poll_handler()`, and `io_poll_task_func()`. `IO_POLL_CANCEL_FLAG`, `IO_POLL_RETRY_FLAG`, and the ref mask encode ownership and wake races in `req->poll_refs`.

Control flow: prep parses event masks and update flags. Arming initializes wait queue entries, calls `vfs_poll()`, records one or two waitqueues, inserts the request into the cancel hash, and either completes inline or hands ownership to task_work. Wake callbacks match poll masks, handle `POLLFREE`, remove one-shot entries, and queue `io_poll_task_func()`. Task work rechecks current readiness, posts multishot CQEs or reissues the original operation, then tears down waitqueue and cancel-table state. Removal can either cancel a poll or update its user data/events and re-arm it.

State and persistence: poll state lives in request flags, `poll_refs`, waitqueue entries, optional allocated double poll entry, `ctx->cancel_table`, and `req->apoll`. It is transient but highly concurrent with file waitqueue lifetime and task_work execution.

Dependencies/integration: depends on VFS poll callbacks, io_uring task work, cancellation matching, NAPI tracking, provided-buffer multishot read retry, and opcode pollability metadata from `opdef`.

Risks/test signals: risks center on ownership races, double-waitqueue allocation failure, `POLLFREE` lifetime, multishot overflow termination, and cancel/update interactions. Test with one-shot and multishot poll, edge vs level flags, event updates, fd/op/user-data cancellation, two-waitqueue files such as sockets, and poll-free teardown under concurrent close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/poll.h -->
# sources/distributed-fs/ceph-client/io_uring/poll.h

Purpose: defines shared poll data structures and exported poll helper APIs for explicit poll requests and async retry.

Important APIs/types/functions: `IO_POLL_ALLOC_CACHE_MAX` sizes cached async poll objects. `IO_APOLL_OK`, `IO_APOLL_ABORTED`, and `IO_APOLL_READY` describe async-poll arm results. `struct io_poll` stores file, waitqueue head, event mask, retry budget, and wait entry. `struct async_poll` adds optional double poll. `io_poll_multishot_retry()` bumps `poll_refs` for owned multishot retries. Prototypes expose add/remove, cancel, arm, remove-all, and task-work execution.

Control flow: inline control is limited to `io_poll_multishot_retry()`, which assumes the caller owns the poll request and increments `req->poll_refs` so task-work will loop.

State and persistence: state is transient request waitqueue state and retry counters; no persistent storage.

Dependencies/integration: includes `io_uring_types.h` and is consumed by read/write, uring_cmd, task-work, cancel, and opcode dispatch paths.

Risks/test signals: callers must obey ownership assumptions for `io_poll_multishot_retry()` or corrupt poll reference accounting. Build coverage plus multishot read/command tests exercise this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/poll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/query.c -->
# sources/distributed-fs/ceph-client/io_uring/query.c

Purpose: implements blind and ring registration query support so userspace can discover io_uring opcode, feature, zero-copy receive, and shared-CQ metadata without relying on hard-coded constants.

Important APIs/types/functions: `union io_query_data` bounds all result payloads. `io_query_ops()`, `io_query_zcrx()`, and `io_query_scq()` fill individual result structures. `io_handle_query_entry()` validates/copies a linked query header and result buffer. `io_query()` walks the user-provided linked list.

Control flow: `io_query()` rejects nonzero `nr_args`, zeroes a stack result buffer, then follows `hdr.next_entry` up to `IO_MAX_QUERY_ENTRIES`. Each entry copies the header, clamps the requested size to `IO_MAX_QUERY_SIZE`, validates reserved fields and opcode, copies the input payload, fills the selected result, writes the result data with `copy_struct_to_user()`, writes back the header result/size, and reschedules between entries.

State and persistence: no kernel state is persisted. It only copies capability snapshots to userspace and uses an iteration cap to avoid cycles.

Dependencies/integration: depends on UAPI query structs, io_uring feature/setup/enter/SQE flag constants, `struct io_rings`, `struct io_uring`, and zcrx constants.

Risks/test signals: risks are user pointer faults, linked-list cycles, unsupported op handling, and keeping reported constants current with UAPI additions. Test with undersized/oversized buffers, chained queries, invalid reserved fields, unknown query opcodes, zero-copy query, SCQ query, and signal interruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/query.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/query.h -->
# sources/distributed-fs/ceph-client/io_uring/query.h

Purpose: exposes the single `io_query()` registration handler.

Important APIs/types/functions: `int io_query(void __user *arg, unsigned nr_args)` is the only declaration.

Control flow: none in this header.

State and persistence: no state is declared.

Dependencies/integration: includes `io_uring_types.h` and is used by `register.c` for both `IORING_REGISTER_QUERY` on a ring and the blind fd `-1` query path.

Risks/test signals: compatibility depends on the prototype matching `register.c`. Build coverage and userspace query tests are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/query.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/refs.h -->
# sources/distributed-fs/ceph-client/io_uring/refs.h

Purpose: provides inline request reference-count helpers for `struct io_kiocb` with overflow checks borrowed from page-ref hardening patterns.

Important APIs/types/functions: `req_ref_zero_or_close_to_overflow()` checks ref values near zero/overflow. Helpers include `req_ref_inc_not_zero()`, `req_ref_put_and_test_atomic()`, `req_ref_put_and_test()`, `req_ref_get()`, `req_ref_put()`, `__io_req_set_refcount()`, and `io_req_set_refcount()`.

Control flow: fast paths avoid atomics when `REQ_F_REFCOUNT` is absent, meaning a request with no extra refs is consumed by `req_ref_put_and_test()`. When refcounted, helpers assert the flag and use atomic inc/dec/test operations.

State and persistence: state is `req->refs` and `REQ_F_REFCOUNT` on an in-flight request. It is transient but controls request lifetime.

Dependencies/integration: used by timeout, waitid, poll, and general completion paths that need to keep requests alive across timers, callbacks, or linked operations.

Risks/test signals: misuse causes UAF or leaked requests; overflow warnings catch ref corruption. Test signals are lockdep/KASAN runs under cancellation, linked timeouts, multishot operations, and task exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/refs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/register.c -->
# sources/distributed-fs/ceph-client/io_uring/register.c

Purpose: implements the `io_uring_register()` syscall dispatch and ring configuration/resource registration operations.

Important APIs/types/functions: `io_probe()`, personality register/unregister, restriction parsing, task restrictions, BPF filter registration, ring enable, io-wq affinity/limits, clock registration, ring resize, memory-region registration, blind registration, and `SYSCALL_DEFINE4(io_uring_register)` are central. `io_ring_ctx_rings` stages resize state.

Control flow: syscall normalizes `IORING_REGISTER_USE_REGISTERED_RING`, handles blind `fd == -1` opcodes, resolves the ring file, locks `ctx->uring_lock`, and dispatches through `__io_uring_register()`. Dispatch validates arguments per opcode and calls resource, eventfd, pbuf, NAPI, zcrx, resize, query, restriction, and BPF helpers. Resize allocates new shared ring/SQE regions, copies pending SQ/CQ entries, swaps under mmap and completion locks, RCU-publishes new rings, and frees old regions after synchronization. Enabling disabled rings sets single-issuer state before releasing `R_DISABLED`.

State and persistence: mutates ring context flags, personalities xarray, restrictions, registered files/buffers, eventfd, io-wq settings, SQPOLL state, mapped ring regions, clock source, parameter memory region, and BPF filters. State persists for the lifetime of the ring or current task restrictions.

Dependencies/integration: integrates nearly every io_uring subsystem: resources, SQPOLL, task context, eventfd, kbuf, NAPI, msg_ring, memmap, zcrx, query, cancel, and BPF filter code, plus VFS fd lookup and credentials.

Risks/test signals: risks include restriction bypass, wrong lock ordering during SQPOLL/io-wq updates, resize races with mmap/userspace ring access, registered-ring fd semantics, and partial userspace copy failures. Test with every register opcode, disabled-ring restrictions, blind query/restriction/filter paths, ring resize overflow, registered ring fd lookup, SQPOLL affinity, and BPF filter enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/register.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/register.h -->
# sources/distributed-fs/ceph-client/io_uring/register.h

Purpose: small public registration header for helpers needed outside `register.c`.

Important APIs/types/functions: declares `io_eventfd_unregister()` and `io_unregister_personality()`.

Control flow: no control flow.

State and persistence: no state defined; declarations operate on `io_ring_ctx` eventfd and personality state.

Dependencies/integration: used by registration dispatch and teardown paths that need to remove eventfd notification or credentials personalities.

Risks/test signals: prototype drift would break cleanup and unregister call sites. Build and personality/eventfd registration tests are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/register.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/rsrc.c -->
# sources/distributed-fs/ceph-client/io_uring/rsrc.c

Purpose: manages registered io_uring resources: fixed files, fixed user buffers, kernel bvec buffers for uring_cmd users, resource updates, buffer cloning, memory accounting, and fixed-buffer import.

Important APIs/types/functions: memory helpers `io_account_mem()`, `io_unaccount_mem()`, `io_validate_user_buf_range()`. Resource helpers `io_rsrc_node_alloc()`, `io_rsrc_data_alloc/free()`, `io_free_rsrc_node()`. Registration/update entry points include `io_sqe_files_register/unregister()`, `io_sqe_buffers_register/unregister()`, `io_register_rsrc()`, `io_register_rsrc_update()`, `io_register_files_update()`, `io_files_update_prep()`, `io_files_update()`, `io_register_clone_buffers()`, and exported `io_buffer_register_bvec()`/`io_buffer_unregister_bvec()`. Import helpers include `io_import_reg_buf()`, `io_import_reg_vec()`, and `io_prep_reg_iovec()`.

Control flow: file registration allocates a table, takes fds with `fget()`, rejects io_uring files, wraps them in resource nodes, and populates allocation bitmaps. Buffer registration validates iov ranges, pins pages, coalesces huge folios when possible, accounts locked/pinned pages, fills bvecs, and stores nodes. Updates replace selected nodes with rollback-by-count semantics. Fixed-buffer import validates ranges and directions, then builds `iov_iter` over bvecs. Clone buffers locks source/destination rings in address order, shares `io_mapped_ubuf` refs, and optionally replaces destination tables.

State and persistence: state is `ctx->file_table`, `ctx->buf_table`, node refs/tags, fixed-file allocation bitmaps, pinned folios, user locked-vm and mm pinned-vm accounting, per-ring caches for nodes/ubufs, and shared buffer refs between cloned rings. Tags are persisted until resource release and produce aux CQEs.

Dependencies/integration: depends on VFS files, page pinning/unpinning, hugetlb/folio APIs, io_uring fixed file table, memmap accounting, uring_cmd block request bvecs, read/write fixed-buffer import, and registration dispatch.

Risks/test signals: risks include memory-accounting imbalance, huge-page double accounting, range overflow, direction misuse, node ref leaks, clone replace corner cases, and handling sparse/tagged entries. Test with sparse file/buffer tables, resource tags, huge-page buffers, fixed read/write vectors, kernel bvec registration, clone across rings with different users rejected, and fault injection during update/registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/rsrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/rsrc.h -->
# sources/distributed-fs/ceph-client/io_uring/rsrc.h

Purpose: defines resource-node and mapped-buffer structures plus inline lookup/ref helpers for registered files and buffers.

Important APIs/types/functions: `IORING_RSRC_FILE`, `IORING_RSRC_BUFFER`, `struct io_rsrc_node`, `struct io_mapped_ubuf`, `struct io_imu_folio_data`, and flags `IO_IMU_DEST`, `IO_IMU_SOURCE`, `IO_REGBUF_F_KBUF`. Inline helpers include `io_rsrc_node_lookup()`, `io_put_rsrc_node()`, `io_reset_rsrc_node()`, `__io_unaccount_mem()`, `io_vec_reset_iovec()`, and `io_alloc_cache_vec_kasan()`. Prototypes expose registration, import, accounting, clone, and vector allocation APIs.

Control flow: inline lookup bounds-checks with nospec indexing. Put/reset require `ctx->uring_lock`, decrement node refs, free on zero, and clear table slots. Vector helpers free/repoint cached iovec storage.

State and persistence: defines the shape of fixed resource state: file pointer or mapped buffer, tag, refs, pinned bvec metadata, accounting, release callback, direction mask, and optional kernel-buffer flag.

Dependencies/integration: consumed by open/close, splice, read/write, uring_cmd, register, and filetable code. It requires io_uring core types, lockdep, folio/page and iov iterator users.

Risks/test signals: wrong locking around `io_put_rsrc_node()` or `io_reset_rsrc_node()` risks UAF. Header tests are indirect through fixed-resource registration, fixed IO, uring_cmd fixed imports, and KASAN/fault-injection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/rsrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/rw.c -->
# sources/distributed-fs/ceph-client/io_uring/rw.c

Purpose: implements io_uring read/write opcodes, including vectored IO, fixed-buffer IO, multishot reads, metadata/protection-information attributes, buffered retry, and IOPOLL completion.

Important APIs/types/functions: `struct io_rw` is the command payload. Prep entry points include `io_prep_read/write()`, `io_prep_readv/writev()`, fixed variants, and `io_read_mshot_prep()`. Issue/completion entry points include `io_read()`, `io_write()`, `io_read_fixed()`, `io_write_fixed()`, `io_read_mshot()`, `io_req_rw_complete()`, `io_rw_fail()`, `io_do_iopoll()`, and `io_rw_cache_free()`.

Control flow: prep allocates `io_async_rw`, imports user or fixed buffers, stores ioprio/rwf flags/position, and sets kiocb completion callbacks. Read/write issue initializes file mode and IOCB flags, applies NOWAIT/IOPOLL rules, verifies ranges, invokes `read_iter`/`write_iter` or legacy loops, then completes inline, queues async completion, returns `-EAGAIN` for io-wq retry, or arms buffered page wait retry. Partial reads restore iter state and may retry with `IOCB_WAITQ`; partial writes update `bytes_done` and reissue. IOPOLL walks `ctx->iopoll_list`, calls file or uring_cmd poll hooks, batches completions, and flushes CQEs.

State and persistence: request state includes `io_async_rw` iter/vector buffers, bytes completed, selected/provided buffers, metadata iter state, current file position, kiocb flags, iopoll timestamps, and cleanup/cache state. Persistent external effects are file reads/writes, file position updates, fsnotify notifications, and write accounting.

Dependencies/integration: depends on VFS iter IO, legacy file ops, fixed-buffer import from `rsrc`, provided-buffer `kbuf`, async poll, io-wq retry, block IOPOLL, fsnotify, ioprio/capability checks, and task_work completion.

Risks/test signals: major risks are iterator lifetime during io-wq completion, partial IO accounting, NOWAIT vs nonblocking semantics, fixed-vector validation, metadata/direct-IO constraints, multishot buffer recycling, and IOPOLL ordering. Test with buffered/direct files, sockets/pollable fds, fixed buffers/vectors, provided buffers, short reads/writes, RWF_NOWAIT, O_NONBLOCK, PI attributes, SQPOLL/IOPOLL/hybrid poll, and fault injection around async data allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/rw.h -->
# sources/distributed-fs/ceph-client/io_uring/rw.h

Purpose: declares read/write operation APIs and defines async read/write request state shared with completion, retry, and resource-import paths.

Important APIs/types/functions: `struct io_meta_state` stores protection-information iterator state. `struct io_async_rw` contains cached iovec storage, `bytes_done`, data iterator/state, fast iovec, buffer group, and a union of buffered-IO `wait_page_queue` or direct-IO metadata fields. Prototypes cover all read/write prep and issue variants, multishot read, cleanup, failure fixup, completion, and cache free.

Control flow: no complex header flow; the struct layout uses `struct_group(clear, ...)` so allocation paths can clear retry-sensitive state consistently.

State and persistence: all state is per-request transient async IO state. It may retain allocated iovec arrays across cache reuse until cleanup or KASAN-forced free.

Dependencies/integration: includes `io_uring_types.h` and `pagemap.h`; used by `rw.c`, task-work indirect calls, and opdef cleanup hooks.

Risks/test signals: the union means buffered waitqueue and metadata cannot coexist; `rw.c` enforces that metadata is direct IO only. Compile layout checks plus read/write metadata and buffered retry tests cover this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/rw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/slist.h -->
# sources/distributed-fs/ceph-client/io_uring/slist.h

Purpose: provides minimal singly-linked list helpers for io_uring work queues.

Important APIs/types/functions: macros and inlines include `__wq_list_for_each`, `wq_list_for_each`, `wq_list_empty()`, `INIT_WQ_LIST()`, `wq_list_add_after()`, `wq_list_add_tail()`, `wq_list_cut()`, `wq_stack_add_head()`, `wq_list_del()`, `wq_stack_extract()`, and `wq_next_work()`.

Control flow: helpers maintain `first` and `last` pointers for queue lists, plus stack-style operations using `node->next`. `wq_list_empty()` uses `READ_ONCE()` for concurrent visibility.

State and persistence: manipulates in-memory `io_wq_work_node`/`io_wq_work_list` links only. No persistence.

Dependencies/integration: depends on `io_uring_types.h` work-node definitions and is used by io-wq/completion batching code.

Risks/test signals: misuse can corrupt queue ordering or leave `last` stale. Tests are indirect through io-wq scheduling, cancellation, and completion batching under KASAN/lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/slist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/splice.c -->
# sources/distributed-fs/ceph-client/io_uring/splice.c

Purpose: implements io_uring `splice` and `tee` operations, including fixed-file input support.

Important APIs/types/functions: `struct io_splice` stores output file, input/output offsets, length, input fd, flags, and optional fixed-resource node. Entry points are `io_tee_prep()`, `io_tee()`, `io_splice_prep()`, `io_splice()`, and `io_splice_cleanup()`.

Control flow: prep validates splice flags, records `splice_fd_in`, stores offsets, and forces async. Issue gets the input file either through normal fd lookup or fixed-file table lookup under the submit lock, calls `do_tee()` or `do_splice()` with offsets or NULL for current position, releases normal fd refs, and completes. Cleanup drops a held fixed resource node.

State and persistence: transient state is the input file reference/resource-node reference and offsets. External effects are pipe/file data movement and file offset updates when offsets are `-1`.

Dependencies/integration: depends on VFS splice helpers, fixed-file resources, io_uring file lookup, and cleanup hooks.

Risks/test signals: risks are fixed resource ref leaks, unsupported flag acceptance, input/output offset semantics, and treating short splice/tee as failure. Test with pipes/files, fixed input fd, zero length, invalid flags, faulted/closed input fds, and cleanup after cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/splice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/splice.h -->
# sources/distributed-fs/ceph-client/io_uring/splice.h

Purpose: declares io_uring splice and tee prep/issue/cleanup hooks.

Important APIs/types/functions: prototypes are `io_tee_prep()`, `io_tee()`, `io_splice_cleanup()`, `io_splice_prep()`, and `io_splice()`.

Control flow: none.

State and persistence: no state is defined; the cleanup prototype signals that splice may hold a fixed-resource reference.

Dependencies/integration: used by opdef dispatch and cleanup handling for splice/tee opcodes.

Risks/test signals: build integration and fixed-file splice tests cover the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/splice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/sqpoll.c -->
# sources/distributed-fs/ceph-client/io_uring/sqpoll.c

Purpose: implements submission-queue polling, where a kernel thread watches one or more rings and submits SQEs on behalf of userspace.

Important APIs/types/functions: `io_sq_data` is defined in the header. Public functions include `io_sq_offload_create()`, `io_sq_thread_finish()`, `io_sq_thread_stop()`, `io_sq_thread_park()`, `io_sq_thread_unpark()`, `io_put_sq_data()`, `io_sqpoll_wait_sq()`, `io_sqpoll_wq_cpu_affinity()`, and `io_sq_cpu_usec()`. Internal `io_sq_thread()` is the kernel-thread loop.

Control flow: setup validates attach/fd/capability/security, creates or attaches `io_sq_data`, records credentials and idle timeout, optionally validates CPU affinity, creates an io thread, allocates that thread's io_uring task context, and wakes it. The thread loops over attached contexts, caps submit count when sharing, overrides credentials, polls IOPOLL completions, submits SQEs unless refs are dying or ring disabled, runs task_work with a retry cap, does NAPI busy polling, then sleeps with `IORING_SQ_NEED_WAKEUP` set when idle. Park/stop coordinate via state bits, waitqueues, completions, and `park_pending`.

State and persistence: state persists while rings use SQPOLL: shared `io_sq_data`, thread pointer, ctx list, refcount, park/stop bits, CPU, task pid/tgid, idle timeout, work-time accounting, and captured submitter creds in each ctx.

Dependencies/integration: integrates with security hooks, cpusets, io thread creation, io-wq task contexts, SQ ring submit, IOPOLL, NAPI, cancellation, audit, registered attach fd, and ring teardown.

Risks/test signals: risks include park/unpark ref races, attaching to a dying thread, credential override errors, affinity validation, fairness across multiple rings, and wakeup flag ordering. Test SQPOLL creation/teardown, attach WQ, CPU affinity, disabled rings, shared rings, IOPOLL under SQPOLL, cancellation on exit, and fdinfo work-time accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/sqpoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/sqpoll.h -->
# sources/distributed-fs/ceph-client/io_uring/sqpoll.h

Purpose: defines SQPOLL shared thread state and public SQPOLL control APIs.

Important APIs/types/functions: `struct io_sq_data` stores refs, `park_pending`, lock, context list, RCU thread pointer, waitqueue, idle timeout, CPU, task identifiers, work time, state bits, and exit completion. `sqpoll_task_locked()` safely dereferences the thread under `sqd->lock`.

Control flow: inline `sqpoll_task_locked()` uses `rcu_dereference_protected()` with lockdep validation.

State and persistence: header defines per-SQPOLL-thread lifetime state shared by one or more rings.

Dependencies/integration: used by setup, register io-wq affinity handling, teardown, and fdinfo/reporting paths.

Risks/test signals: callers must hold `sqd->lock` for the inline dereference. Lockdep and SQPOLL affinity/teardown tests cover misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/sqpoll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/statx.c -->
# sources/distributed-fs/ceph-client/io_uring/statx.c

Purpose: implements io_uring `statx` using delayed pathname resolution and forced async execution.

Important APIs/types/functions: `struct io_statx` stores dfd, mask, flags, delayed filename, and userspace statx buffer. Entry points are `io_statx_prep()`, `io_statx()`, and `io_statx_cleanup()`.

Control flow: prep validates unused SQE fields and rejects fixed-file mode, copies dfd/mask/path/buffer/flags, calls `delayed_getname_uflags()`, marks cleanup, and forces async. Issue completes the delayed filename and calls `do_statx()`. Cleanup dismisses the delayed filename if the request is canceled before issue.

State and persistence: only delayed filename request state is held. External state is a userspace statx result copy and filesystem metadata lookup effects.

Dependencies/integration: depends on VFS `do_statx()`, delayed filename helpers from fs internals, and io_uring cleanup flags.

Risks/test signals: risks include path cleanup on failure, invalid fixed-file use, user buffer faults, and lookup flag propagation. Test regular path, empty path/AT flags, invalid flags, cancellation before issue, and faulted statx buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/statx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/statx.h -->
# sources/distributed-fs/ceph-client/io_uring/statx.h

Purpose: declares statx prep, issue, and cleanup hooks.

Important APIs/types/functions: `io_statx_prep()`, `io_statx()`, and `io_statx_cleanup()`.

Control flow: none.

State and persistence: none in the header; cleanup declaration reflects delayed filename ownership.

Dependencies/integration: consumed by io_uring opcode dispatch and cleanup tables.

Risks/test signals: build coverage and statx cancellation tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/statx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/sync.c -->
# sources/distributed-fs/ceph-client/io_uring/sync.c

Purpose: implements file synchronization and space allocation opcodes: `sync_file_range`, `fsync`, and `fallocate`.

Important APIs/types/functions: `struct io_sync` stores file, offset, length, flags, and fallocate mode. Entry points are `io_sfr_prep()`, `io_sync_file_range()`, `io_fsync_prep()`, `io_fsync()`, `io_fallocate_prep()`, and `io_fallocate()`.

Control flow: prep validates unused SQE fields, stores offsets/length/flags, validates fsync datasync flags and nonnegative fsync offset, and forces async. Issue asserts blocking context, calls `sync_file_range()`, `vfs_fsync_range()`, or `vfs_fallocate()`, and posts the result. Fallocate emits modify notification on success.

State and persistence: request state is transient, but operations persist filesystem sync/allocation effects and may update filesystem metadata.

Dependencies/integration: depends on VFS sync/allocation helpers, fsnotify for fallocate, and io_uring async issue semantics.

Risks/test signals: risks are overflow in `off + len` end handling, invalid flag acceptance, and blocking operations accidentally issued nonblocking. Test datasync/full fsync, `len == 0` end-to-LLONG_MAX behavior, sync range flags, fallocate modes, negative offsets, and nonblocking warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/sync.h -->
# sources/distributed-fs/ceph-client/io_uring/sync.h

Purpose: declares sync-related io_uring operation hooks.

Important APIs/types/functions: prototypes cover `io_sfr_prep()`, `io_sync_file_range()`, `io_fsync_prep()`, `io_fsync()`, `io_fallocate_prep()`, and `io_fallocate()`.

Control flow: none.

State and persistence: none.

Dependencies/integration: consumed by opcode dispatch for sync, fsync, and fallocate.

Risks/test signals: compile integration and filesystem operation tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/tctx.c -->
# sources/distributed-fs/ceph-client/io_uring/tctx.c

Purpose: manages per-task io_uring context, io-wq offload creation, task-to-ring mappings, registered ring fds, task restrictions, and fork cleanup/clone behavior.

Important APIs/types/functions: `io_uring_alloc_task_context()`, `__io_uring_free()`, `__io_uring_add_tctx_node()`, `__io_uring_add_tctx_node_from_submit()`, `io_uring_del_tctx_node()`, `io_uring_clean_tctx()`, `io_uring_unreg_ringfd()`, `io_ringfd_register()`, `io_ringfd_unregister()`, and `__io_uring_fork()`.

Control flow: allocation creates `io_uring_task`, inflight counter, io-wq with a per-ring hash map, waitqueue, task llist, and task_work callback. Adding a context ensures single-issuer rules, applies io-wq worker limits, installs a node in the task xarray and ring tctx list, and caches `last` for fast submit. Cleanup removes all nodes, exits io-wq, drops registered ring files, and frees task restrictions. Ring-fd registration ensures a task context, validates io_uring fds, fills requested or free slots, and copies assigned offsets back to userspace.

State and persistence: per-task state includes `current->io_uring`, xarray of ring nodes, io-wq, inflight counters, task_work list, registered ring fd references, `last` ring shortcut, and `io_uring_restrict` filters. It persists for task lifetime.

Dependencies/integration: integrates with io-wq, xarray, ring tctx lists, BPF/restriction clone, registered-ring syscall fast paths, fork handling, and cancellation.

Risks/test signals: risks include xarray/list mismatch, io-wq lifetime races, registered ring fd leaks, single-issuer violations, and fork restriction clone failure. Test multi-ring tasks, ring close/task exit, registered ring fd register/unregister, io-wq limits propagation, fork with restrictions, and fault injection in node allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/tctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/tctx.h -->
# sources/distributed-fs/ceph-client/io_uring/tctx.h

Purpose: declares per-task io_uring context helpers and defines the ring-to-task node structure.

Important APIs/types/functions: `struct io_tctx_node` links a task and ring through the ring's `tctx_list` and the task xarray. Prototypes cover task context allocation, node add/delete/clean, registered ring fd register/unregister, and `io_uring_unreg_ringfd()`. Inline `io_uring_add_tctx_node()` fast-paths when `current->io_uring->last == ctx`.

Control flow: inline fast path returns immediately for repeated submissions to the same ring; otherwise it calls the full submit-time add path.

State and persistence: defines link state between task and ring plus the cached last-ring behavior.

Dependencies/integration: used by submit, register, SQPOLL, task exit, and cancellation paths.

Risks/test signals: stale `last` or missed node install would break cancellation/accounting. Multi-ring submit and task-exit tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/tctx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/timeout.c -->
# sources/distributed-fs/ceph-client/io_uring/timeout.c

Purpose: implements timeout requests, linked timeouts, timeout cancellation/update, multishot timeouts, CQ-event-count timeouts, and timeout cleanup during cancellation.

Important APIs/types/functions: `struct io_timeout` and `struct io_timeout_rem` hold command state. Entry points include `io_timeout_prep()`, `io_link_timeout_prep()`, `io_timeout()`, `io_timeout_remove_prep()`, `io_timeout_remove()`, `io_timeout_cancel()`, `io_flush_timeouts()`, `io_kill_timeouts()`, `io_queue_linked_timeout()`, and `io_disarm_next()`.

Control flow: prep validates flags, parses timespec or immediate nanoseconds, handles absolute time namespaces, allocates `io_timeout_data`, and initializes hrtimer callbacks. Normal timeouts are inserted into `ctx->timeout_list`, sorted by CQ target sequence when `off` is nonzero, then hrtimer expiration queues task_work. Completion posts `-ETIME`, re-arms multishot timeouts if repeats remain and CQE posting succeeds, or completes the request. Linked timeouts arm after their head request and cancel the linked request on expiration. Remove requests either cancel a timeout by user_data or update normal/linked timeout hrtimers.

State and persistence: state lives in timeout and linked-timeout lists, hrtimers, `ctx->cq_timeouts`, `cq_last_tm_flush`, request refs, linked request chains, and timeout flags/time/mode. It is transient but controls completion ordering and cancellation.

Dependencies/integration: depends on hrtimers, time namespaces, completion locks, timeout locks, cancel matching, request refs, linked SQE chains, task_work, and CQ tail accounting.

Risks/test signals: risks are timer/cancel races, linked-chain ref handling, sequence wrap comparisons, multishot CQ overflow termination, absolute clock conversion, and lock ordering. Test relative/absolute clocks, CQ-count timeouts, multishot repeats, remove/update normal and linked timeouts, request cancellation, task exit kill, linked timeout racing with head completion, and time namespace behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/timeout.h -->
# sources/distributed-fs/ceph-client/io_uring/timeout.h

Purpose: defines timeout async data and declares timeout operation/cancellation helpers.

Important APIs/types/functions: `struct io_timeout_data` stores request pointer, hrtimer, target time, hrtimer mode, and flags. Prototypes expose timeout flush, cancel, kill, linked queue/disarm, prep, issue, remove prep, and remove issue.

Control flow: none in the header.

State and persistence: defines per-timeout hrtimer state used while requests are pending.

Dependencies/integration: consumed by linked request completion, cancellation, ring teardown, and opcode dispatch.

Risks/test signals: correct declaration is crucial for timer lifetime and cancellation. Timeout unit/integration tests and lockdep runs cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/timeout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/truncate.c -->
# sources/distributed-fs/ceph-client/io_uring/truncate.c

Purpose: implements io_uring `ftruncate` against the request file.

Important APIs/types/functions: `struct io_ftrunc` stores the file and desired length. Entry points are `io_ftruncate_prep()` and `io_ftruncate()`.

Control flow: prep rejects all unsupported SQE fields, reads the length from `sqe->off`, and forces async. Issue asserts blocking context, calls `do_ftruncate(req->file, len, 0)`, and completes.

State and persistence: request state is transient; successful execution persists file size changes and filesystem metadata updates.

Dependencies/integration: depends on VFS `do_ftruncate()` and io_uring async issue/completion.

Risks/test signals: risks are invalid field validation, negative/large length behavior delegated to VFS, and accidental nonblocking issue. Test successful truncate/extend, permission errors, sealed files, invalid SQE fields, and async-only execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/truncate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/truncate.h -->
# sources/distributed-fs/ceph-client/io_uring/truncate.h

Purpose: declares ftruncate prep and issue hooks.

Important APIs/types/functions: `io_ftruncate_prep()` and `io_ftruncate()`.

Control flow: none.

State and persistence: none.

Dependencies/integration: used by opcode dispatch.

Risks/test signals: build integration and ftruncate opcode tests cover this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/truncate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/tw.c -->
# sources/distributed-fs/ceph-client/io_uring/tw.c

Purpose: implements io_uring task_work routing, local deferred task_work for `DEFER_TASKRUN`, fallback workqueue execution, and bounded local task_work runs.

Important APIs/types/functions: `io_fallback_req_func()`, `io_handle_tw_list()`, `tctx_task_work_run()`, `tctx_task_work()`, `io_req_local_work_add()`, `io_req_normal_work_add()`, `io_req_task_work_add_remote()`, `io_move_task_work_from_local()`, `io_run_local_work_locked()`, and `io_run_local_work()`.

Control flow: normal mode queues request task_work to the submitting task's `task_list` and uses kernel task_work notification, except SQPOLL runs it itself. Deferred mode pushes requests to the ring local llist, marks `IORING_SQ_TASKRUN`, signals eventfd if needed, and wakes the submitter based on `cq_wait_nr` and lazy-wake counts. Runners group work by ctx, hold `uring_lock`, take ctx refs, compute cancellation state, invoke request callbacks through indirect-call optimized paths, flush completions, and reschedule if needed. Fallback moves abandoned task_work to delayed work when task_work cannot be queued or task exits.

State and persistence: transient state includes task llists, ring local/retry/fallback llists, `IORING_SQ_TASKRUN`, `cq_wait_nr`, request `nr_tw`, ctx refs, and delayed fallback work. It persists only while completions/retries are pending.

Dependencies/integration: integrates with task_work, io-wq workers, SQPOLL, eventfd, wait logic, poll and rw completion callbacks, local-work wait wakeups, and ring teardown.

Risks/test signals: risks are lost wakeups, running task_work on the wrong task, fallback ref leaks, cancellation during ring teardown, and starvation when capping local work. Test deferred taskrun waits, SQPOLL task_work, eventfd wakeups, task exit fallback, linked requests disabling lazy wake, and stress with many completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/tw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/tw.h -->
# sources/distributed-fs/ceph-client/io_uring/tw.h

Purpose: declares task-work helpers and inline routing logic for normal vs deferred io_uring task_work.

Important APIs/types/functions: `IO_LOCAL_TW_DEFAULT_MAX`, `io_should_terminate_tw()`, task-work add/run/fallback prototypes, `__io_req_task_work_add()`, `io_req_task_work_add()`, `io_run_task_work()`, `io_local_work_pending()`, `io_task_work_pending()`, `io_tw_lock()`, `io_allowed_defer_tw_run()`, and `io_allowed_run_tw()`.

Control flow: inline routing sends requests to local ring work when `IORING_SETUP_DEFER_TASKRUN` is set, otherwise to task work. `io_run_task_work()` clears notify signals, handles PF_IO_WORKER resume/task lists, and runs generic task_work. Permission helpers enforce that deferred work is run by the submitter task.

State and persistence: manipulates current task notify state and observes ring local-work lists; no state is declared beyond constants.

Dependencies/integration: includes scheduler, percpu refcount, and io_uring types; used throughout completion, poll, timeout, wait, and command paths.

Risks/test signals: incorrect inline routing causes missed completions or wrong-task execution. Tests with `DEFER_TASKRUN`, io-wq workers, and task exit cover this.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/tw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/uring_cmd.c -->
# sources/distributed-fs/ceph-client/io_uring/uring_cmd.c

Purpose: implements the generic passthrough `uring_cmd` opcode used by drivers, including fixed-buffer import, cancellation, IOPOLL, multishot command support, and CQE32 completion.

Important APIs/types/functions: `io_uring_cmd_prep()`, `io_uring_cmd()`, `io_uring_cmd_sqe_copy()`, `io_uring_cmd_cleanup()`, `__io_uring_cmd_done()`, `io_uring_cmd_mark_cancelable()`, `io_uring_try_cancel_uring_cmd()`, `io_uring_cmd_import_fixed()`, `io_uring_cmd_import_fixed_vec()`, `io_uring_cmd_issue_blocking()`, `io_cmd_poll_multishot()`, `io_uring_cmd_buffer_select()`, `io_uring_mshot_cmd_post_cqe()`, and `io_uring_cmd_post_mshot_cqe32()`.

Control flow: prep validates command flags, fixed/multishot combinations, buffer selection requirements, command opcode, and allocates async command state. Issue checks file support and security, derives issue flags for SQE128/CQE32/compat/IOPOLL, calls the driver `file->f_op->uring_cmd()`, and interprets queued, reissue, multishot, and immediate completion returns. Driver completion removes cancelable state, sets result and optional CQE32 extra fields, recycles async state, and either marks IOPOLL completed, defers completion, or queues task_work.

State and persistence: state includes per-request command flags, copied SQE storage, async vector cache, cancelable hlist membership, fixed buffer node refs through import, IOPOLL flags, and multishot provided-buffer state. Driver side effects depend on the consuming file operation.

Dependencies/integration: integrates with driver `uring_cmd` and `uring_cmd_iopoll` file ops, LSM `security_uring_cmd`, fixed buffers from `rsrc`, provided buffers, poll, task_work, cancellation, CQE32/mixed CQE support, and io-wq blocking escalation.

Risks/test signals: risks include driver completion races with cancellation, unsupported IOPOLL cancellation, SQE lifetime if drivers need copied SQE, fixed-buffer range validation, and multishot buffer/CQE overflow behavior. Test with NVMe/driver passthrough, fixed and fixed-vector imports, cancelable commands, IOPOLL commands, CQE32 output, multishot poll commands, and security denial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/uring_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/uring_cmd.h -->
# sources/distributed-fs/ceph-client/io_uring/uring_cmd.h

Purpose: declares internal uring_cmd helpers and defines cached async command state.

Important APIs/types/functions: `struct io_async_cmd` stores an `iou_vec` and two SQE-sized slots for copied 128-byte SQEs. Prototypes cover command prep/issue, SQE copy, cleanup, cancel scanning, multishot CQE32 posting, cache free, and poll multishot arming.

Control flow: none in the header.

State and persistence: per-command async vector/copy state is defined here and freed through `io_cmd_cache_free()`.

Dependencies/integration: includes `linux/io_uring/cmd.h` and io_uring types; consumed by command opcode dispatch and driver-facing helper code.

Risks/test signals: struct sizing must handle SQE128 safely. Tests with `IORING_SETUP_SQE128`, fixed vector command imports, and command cleanup validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/uring_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/wait.c -->
# sources/distributed-fs/ceph-client/io_uring/wait.c

Purpose: implements `io_uring_enter()` completion waiting, including task_work flushing, timeouts, minimum wait time, signal masks, NAPI busy polling, and deferred-taskrun wakeups.

Important APIs/types/functions: `io_cqring_wait()`, `io_run_task_work_sig()`, `io_wake_function()`, hrtimer callbacks for normal and minimum timeout wakeups, and scheduling helpers around `struct io_wait_queue`/`struct ext_arg`.

Control flow: wait first runs local and normal task_work, flushes CQ overflow if needed, and returns immediately if enough CQEs are visible. Otherwise it prepares an exclusive waitqueue entry or deferred-taskrun wait count, applies optional signal mask, runs NAPI busy loop, and loops scheduling until enough events, work, signal, timeout, overflow/drop, or wake condition occurs. Timeout setup uses an on-stack hrtimer; a min-timeout can switch to a normal timeout only if no events/work arrived during the minimum interval.

State and persistence: transient wait state includes CQ target tail, CQ tail at min-wait start, timeout/min-timeout values, timeout hit flag, saved signal mask, current `in_iowait`, and `ctx->cq_wait_nr`. No persistent ring data is changed except wait counters and possible CQ overflow flushing.

Dependencies/integration: depends on task_work, local deferred task_work, CQ ring memory ordering, time namespaces, hrtimers, NAPI, signal masks, overflow flush helpers, and waitqueue wake logic.

Risks/test signals: risks include lost wakeups, timeout vs task_work ordering, deferred taskrun wait counts, CQ overflow/drop handling, and signal mask restoration. Test `min_complete`, relative/absolute waits, min-time waits, signal interruption, deferred taskrun, NAPI busy poll, CQ overflow flush, and empty/nonempty CQ races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/wait.h -->
# sources/distributed-fs/ceph-client/io_uring/wait.h

Purpose: declares completion-wait helpers and CQ event counting utilities.

Important APIs/types/functions: `IO_CQ_WAKE_INIT` and `IO_CQ_WAKE_FORCE` encode waiter thresholds. `struct ext_arg` stores wait timeout, signal mask, minimum wait time, and iowait flag. Prototypes include `io_cqring_wait()`, `io_run_task_work_sig()`, `io_cqring_do_overflow_flush()`, and `io_cqring_overflow_flush_locked()`. Inlines count kernel/user-visible CQ events with required memory ordering.

Control flow: `io_cqring_events()` issues `smp_rmb()` before reading cached events to match CQ ring ordering rules.

State and persistence: no owned state; observes `ctx->cached_cq_tail` and shared ring CQ head/tail.

Dependencies/integration: used by enter/wait paths, task-work wakeup code, and overflow handling.

Risks/test signals: memory-ordering regressions can expose stale CQEs. Litmus-style CQ visibility tests and enter wait stress are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/wait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/waitid.c -->
# sources/distributed-fs/ceph-client/io_uring/waitid.c

Purpose: provides async io_uring support for `waitid`, allowing child-state waits to arm a waitqueue and complete through task_work.

Important APIs/types/functions: `struct io_waitid` stores wait parameters, refs/cancel flag, waitqueue head, user siginfo pointer, and result info. `struct io_waitid_async` is declared in the header. Entry points are `io_waitid_prep()`, `io_waitid()`, `io_waitid_cancel()`, and `io_waitid_remove_all()`.

Control flow: prep allocates async wait options and captures `which`, pid, options, and siginfo pointer. Issue prepares kernel wait options, sets an initial ref, adds the request to `ctx->waitid_list`, arms `current->signal->wait_chldexit`, and calls `__do_wait()`. If it returns `-ERESTARTSYS`, the request remains armed until the wait callback queues task_work or cancellation completes it. Task_work retries `__do_wait()`, handles spurious wakeups by rearming, copies siginfo in native or compat layout, removes waitqueue/list state, drops pid refs, and completes.

State and persistence: transient state includes child waitqueue entry, wait options pid ref, cancel/ref bits, waitid cancel hlist entry, and copied `waitid_info`. Userspace siginfo is updated on completion.

Dependencies/integration: depends on kernel wait/exit internals, compat siginfo layout, io_uring cancellation helpers, task_work, ring submit lock, and request async data lifetime.

Risks/test signals: risks are cancellation/wakeup ref races, waitqueue removal under concurrent child exit, compat siginfo copy faults, pid ref leaks, and task-specific cancellation. Test immediate child reap, async child exit, cancellation by user_data/task exit, compat mode, null siginfo, spurious wake/rearm, and faulted siginfo pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/waitid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/waitid.h -->
# sources/distributed-fs/ceph-client/io_uring/waitid.h

Purpose: declares waitid operation and cancellation helpers plus async wait option state.

Important APIs/types/functions: `struct io_waitid_async` stores the owning request and `struct wait_opts`. Prototypes cover prep, issue, cancel, and remove-all.

Control flow: none in the header.

State and persistence: defines per-request async wait state that owns wait options and pid refs until completion/free.

Dependencies/integration: includes `../kernel/exit.h` for `wait_opts`; used by waitid implementation and cancel paths.

Risks/test signals: changes to kernel wait internals can affect this header. Build and waitid cancellation tests are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/waitid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/xattr.c -->
# sources/distributed-fs/ceph-client/io_uring/xattr.c

Purpose: implements async get/set extended attribute operations for path-based and file-based xattr io_uring opcodes.

Important APIs/types/functions: `struct io_xattr` stores file, `kernel_xattr_ctx`, and optional delayed filename. Entry points are `io_fgetxattr_prep()`, `io_getxattr_prep()`, `io_fgetxattr()`, `io_getxattr()`, `io_fsetxattr_prep()`, `io_setxattr_prep()`, `io_fsetxattr()`, `io_setxattr()`, and `io_xattr_cleanup()`.

Control flow: get prep initializes delayed filename state, imports the xattr name into kernel memory, stores userspace value buffer/size, rejects flags, and forces async. Path get additionally rejects fixed-file mode and delays pathname lookup. Set prep imports name and copies value through `setxattr_copy()`, with path and file variants mirroring get behavior. Issue calls file or filename xattr helpers, then `io_xattr_finish()` clears cleanup, frees name/value/path resources, and posts the result.

State and persistence: transient state includes imported xattr name, optional copied value, delayed path, and userspace value pointer. Successful set operations persist filesystem xattr changes; get operations copy values to userspace.

Dependencies/integration: depends on VFS xattr helpers, delayed filename helpers, `kernel_xattr_ctx`, io_uring cleanup flags, and async issue semantics.

Risks/test signals: risks are cleanup leaks on prep failure/cancel, fixed-file rejection for path variants, flag validation differences between get/set, user buffer faults, and path lookup semantics. Test file/path get/set, remove via zero size where supported, invalid flags, faulted name/value/path pointers, cancellation before issue, and permission/security xattr failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/xattr.h -->
# sources/distributed-fs/ceph-client/io_uring/xattr.h

Purpose: declares xattr prep, issue, and cleanup hooks for io_uring opcode dispatch.

Important APIs/types/functions: `io_xattr_cleanup()`, prep/issue pairs for `fsetxattr`, `setxattr`, `fgetxattr`, and `getxattr`.

Control flow: none.

State and persistence: no state defined; cleanup declaration indicates requests may own imported names/values and delayed paths.

Dependencies/integration: consumed by opdef dispatch and cleanup paths.

Risks/test signals: compile coverage and xattr cancellation/fault tests validate the API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/xattr.h -->
