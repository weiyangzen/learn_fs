# Group Research: group_881_linux_sources_os_linux_linux_io_uring_io_uring_c_sources_os_linux_li_0e1b0a004930

Scope: `Docs/research_subset_a.md` (`sources/os/linux/linux`). All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/io_uring.c -->
# File Research: sources/os/linux/linux/io_uring/io_uring.c

## Purpose
Core io_uring implementation: owns ring setup/teardown, SQE submission, request lifecycle, CQE posting, overflow handling, async punt-to-worker behavior, registered ring lookup, syscall entry points, and initialization-time ABI checks.

## Main Responsibilities
- Defines the memory-ordering contract for shared SQ/CQ rings and consistently uses `READ_ONCE`, `WRITE_ONCE`, acquire/release barriers, and cached head/tail state.
- Allocates and initializes `io_ring_ctx`, including cancel hash table, caches, wait queues, timeout lists, xarrays, NAPI state, mapped regions, and request freelist.
- Implements CQE posting paths: direct CQ cache refill, 16/32-byte CQE handling, mixed CQE support, overflow list allocation, overflow flushing, dropped-CQE signaling, eventfd/poll/timeouts flush hooks.
- Drives request submission from `io_uring_enter`: SQE fetch, validation, restrictions, BPF filters, link assembly, drain handling, file assignment, inline issue, async poll, io-wq fallback, and deferred completion flushing.
- Handles linked timeout preparation, linked request failure, request cleanup, task reference caching, request recycling, and batching of deferred completions.
- Handles IOPOLL reap/wait, SQPOLL enter behavior, `GETEVENTS`, registered wait arguments, and registered ring fd lookup.
- Creates rings through `io_uring_setup`: validates setup flags, computes SQ/CQ sizes and mmap offsets, allocates ring/SQE regions, configures SQPOLL/offload/taskrun behavior, copies params back to userspace, installs or registers the anonymous fd.
- Tears down rings via percpu-ref kill, cancellation loops, SQ thread parking, task_work removal from task ctx lists, region/resource cleanup, and delayed exit work.

## Key Entry Points
- `SYSCALL_DEFINE2(io_uring_setup)`
- `SYSCALL_DEFINE6(io_uring_enter)`
- `io_submit_sqes`
- `io_wq_submit_work`
- `io_req_task_submit`
- `io_req_task_complete`
- `io_post_aux_cqe`, `io_add_aux_cqe`, `io_req_post_cqe`, `io_req_post_cqe32`
- `io_prepare_config`
- `io_uring_ctx_get_file`
- `io_uring_init`

## Important Invariants
- SQE fields read from userspace must be consumed with stable single loads after validation.
- CQ posting must preserve ordering; overflowed CQEs block later direct CQEs to avoid completion reordering.
- Inline issue normally holds `uring_lock`; io-wq paths use `IO_URING_F_UNLOCKED` and re-lock where needed.
- `IORING_SETUP_DEFER_TASKRUN` requires single issuer and pushes completions into submitter-task context.
- Mixed SQE/CQE modes require contiguous entries and explicit head/tail accounting.
- Request caches are only refilled/extracted under `uring_lock` because requests can recycle before issue functions fully return.

## Interactions
This file is the hub for `opdef`, `kbuf`, `rsrc`, `poll`, `rw`, `timeout`, `net`, `notif`, `napi`, `memmap`, `msg_ring`, `uring_cmd`, `sqpoll`, `tctx`, and file table registration.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/io_uring.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/io_uring.h -->
# File Research: sources/os/linux/linux/io_uring/io_uring.h

## Purpose
Shared core declarations and inline helpers for io_uring internals.

## Contents
- Defines ring setup feature flags, allowed setup/enter/SQE flags, max SQ/CQ entries, `io_rings_layout`, `io_ctx_config`, wait queue state, and deferred request entries.
- Declares core functions for config prep, CQE posting, request failure/completion, fixed/normal file lookup, task_work queueing, iopoll, io-wq submission, request allocation, and poll wait activation.
- Provides hot inline helpers for CQE acquisition, CQE filling, deferred completion enqueueing, CQ/SQ wakeups, SQ fullness/entry counting, task ref caching, request cache extraction, async data allocation, file release, and submit lock handling.

## Important Invariants
- `io_get_cqe_overflow` centralizes CQE slot advancement and knows about `IORING_SETUP_CQE32` and mixed 32-byte CQEs.
- `io_fill_cqe_req` copies normal and big CQE payloads and clears `req->big_cqe` after use.
- `io_lockdep_assert_cq_locked` encodes completion-context locking rules for normal, IOPOLL, and task-complete rings.
- `io_commit_cqring` publishes CQ tail with release ordering.

## Role
This header is the fast-path contract for most io_uring source files; changes here affect request lifetime, completion ordering, and shared-ring synchronization.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/io_uring.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/kbuf.c -->
# File Research: sources/os/linux/linux/io_uring/kbuf.c

## Purpose
Implements io_uring provided-buffer management for legacy kernel-owned lists and userspace-visible buffer rings.

## Main Responsibilities
- Selects buffers for read/recv/send-style operations, returning either a single user pointer or a vector list.
- Supports classic `PROVIDE_BUFFERS`/`REMOVE_BUFFERS` linked-list buffers.
- Supports registered provided-buffer rings, including kernel-allocated mmap regions and user-provided pinned regions via `io_create_region`.
- Handles incremental buffer consumption (`IOU_PBUF_RING_INC`) by advancing buffer address/length until minimum-left rules require consuming the entry.
- Commits or recycles selected buffers depending on issue context, polling state, and operation type.
- Reports CQE buffer IDs and `IORING_CQE_F_BUF_MORE` when partially consumed buffers remain.
- Destroys all buffer groups during ring teardown.

## Key Entry Points
- `io_buffer_select`
- `io_buffers_select`
- `io_buffers_peek`
- `io_kbuf_commit`
- `io_put_kbuf`, via `__io_put_kbufs`
- `io_provide_buffers_prep`
- `io_remove_buffers_prep`
- `io_manage_buffers_legacy`
- `io_register_pbuf_ring`
- `io_unregister_pbuf_ring`
- `io_register_pbuf_status`
- `io_pbuf_get_region`

## Important Invariants
- Buffer group lookup is under `uring_lock`; mmap-visible group publication/removal is under `mmap_lock`.
- Legacy buffers are removed from a list and pinned to the request until recycled or dropped.
- Ring buffers are consumed by advancing `bl->head`; callers must commit selected buffers exactly once unless explicitly recycled.
- Multiple-buffer peek may allocate/replace iovec arrays and marks cleanup with `REQ_F_NEED_CLEANUP`.

## Interactions
Used heavily by network receive/send bundle paths, read paths, uring commands, mmap region lookup, and teardown cleanup.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/kbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/kbuf.h -->
# File Research: sources/os/linux/linux/io_uring/kbuf.h

## Purpose
Declares provided-buffer data structures and helper APIs.

## Contents
- `io_buffer_list`: represents either a legacy buffer list or a mapped buffer ring; stores buffer group id, ring head/mask, flags, incremental-consumption threshold, and mapped region.
- `io_buffer`: legacy buffer descriptor with address, length, bid, and bgid.
- `buf_sel_arg`: multi-buffer selection arguments for vector expansion and partial mapping.
- Declares buffer selection, peek, register/unregister/status, legacy management, destroy, recycle, commit, and mmap-region lookup functions.
- Provides inline helpers for recycling ring or legacy buffers and for emitting CQE buffer flags.

## Important Invariants
- `io_do_buffer_select` prevents selecting twice for the same request.
- `io_kbuf_recycle` refuses recycling when `REQ_F_BL_NO_RECYCLE` is set.
- `io_put_kbuf`/`io_put_kbufs` are no-ops unless the request actually selected a legacy or ring buffer.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/kbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/loop.c -->
# File Research: sources/os/linux/linux/io_uring/loop.c

## Purpose
Implements a ring-owned loop execution mode driven by a `ctx->loop_step` callback.

## Behavior
- Runs loop steps under `uring_lock` until the callback returns `IOU_LOOP_STOP`.
- Uses `iou_loop_params.cq_wait_idx` as a completion-tail wait hint.
- Sleeps interruptibly when the loop wants future CQEs and no local work/CQ overflow is pending.
- Drops `uring_lock` around `schedule()` and task_work execution, then reacquires it.
- Runs local work and flushes CQ overflow while looping.
- Returns `-EEXIST` if task_work is not allowed in the current context, `-EINTR` on pending signal, `-EINVAL` for invalid callback return, and `-EFAULT` if no loop callback exists.

## Key Entry Point
- `io_run_loop`

## Interactions
Called from `io_uring_enter` when `io_has_loop_ops(ctx)` is true.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/loop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/loop.h -->
# File Research: sources/os/linux/linux/io_uring/loop.h

## Purpose
Small interface for io_uring loop mode.

## Contents
- Defines `struct iou_loop_params` with `cq_wait_idx`.
- Defines loop callback return values `IOU_LOOP_CONTINUE` and `IOU_LOOP_STOP`.
- Provides `io_has_loop_ops`, which checks `ctx->loop_step`.
- Declares `io_run_loop`.

## Role
Allows the core enter path to delegate execution to a specialized per-ring loop while keeping the callback opaque to the core.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/loop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/memmap.c -->
# File Research: sources/os/linux/linux/io_uring/memmap.c

## Purpose
Shared mapped-memory region management for io_uring rings, SQEs, provided-buffer rings, parameter regions, and zero-copy receive regions.

## Main Responsibilities
- Pins user-provided pages with long-term writable pins.
- Allocates kernel-owned page arrays using compound allocation when possible, falling back to bulk page allocation.
- Accounts mapped pages against `ctx->user` and unaccounts on free.
- Builds kernel virtual access using direct `page_address` for single lowmem folios or `vmap` otherwise.
- Validates `io_uring_region_desc` fields, size alignment, flags, address/size overflow, and reserved bytes.
- Resolves mmap offsets to the correct `io_mapped_region`: ring, SQE, provided-buffer ring, param region, or zcrx region.
- Implements `mmap`, `get_unmapped_area`, and NOMMU mapping behavior.

## Key Entry Points
- `io_pin_pages`
- `io_create_region`
- `io_free_region`
- `io_uring_mmap`
- `io_uring_get_unmapped_area`
- `io_uring_nommu_mmap_capabilities`

## Important Invariants
- User-provided regions cannot be mmaped back through the io_uring fd.
- Region lookup and validation are protected by `mmap_lock`.
- Kernel-owned regions set `reg->mmap_offset`; user-backed regions pin supplied pages instead.
- Cache-aliasing architectures may require colored mappings through `get_unmapped_area`.

## Interactions
Used by ring setup, buffer-ring registration, zero-copy receive registration, and context teardown.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/memmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/memmap.h -->
# File Research: sources/os/linux/linux/io_uring/memmap.h

## Purpose
Declares io_uring mapped-region APIs and offset constants.

## Contents
- Defines private mmap offsets for parameter and zero-copy receive regions plus zcrx id shift.
- Declares page pinning, region creation/freeing, mmap, and unmapped-area functions.
- Provides inline helpers to get region pointer, test whether a region is set, publish a region under `mmap_lock`, and compute region byte size.

## Important Invariant
`io_region_publish` copies a prepared region into a mmap-visible destination while holding `ctx->mmap_lock`, allowing mmap lookup without also holding `uring_lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/memmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/mock_file.c -->
# File Research: sources/os/linux/linux/io_uring/mock_file.c

## Purpose
Testing-only miscdevice that creates mock files for exercising io_uring edge cases.

## Main Responsibilities
- Registers `/dev/io_uring_mock` with an `uring_cmd` manager interface.
- Supports manager commands for probing features and creating mock anonymous files; requires `CAP_SYS_ADMIN` and taints the kernel as test code.
- Mock files support read/write iterators, llseek, optional poll support, optional `FMODE_NOWAIT`, bounded size, and optional delayed async completion through hrtimer.
- Provides an uring command that copies between registered fixed buffers and a userspace buffer for testing fixed-buffer import/copy behavior.

## Key Entry Points
- `iou_mock_mgr_cmd`
- `io_create_mock_file`
- `io_probe_mock`
- `io_mock_cmd`
- `io_mock_read_iter`
- `io_mock_write_iter`

## Important Invariants
- Mock file size is capped at `SZ_1G`; delay is capped at one second.
- Delayed IO returns `-EIOCBQUEUED` and completes through `ki_complete`.
- Pollable and non-pollable mock files use distinct `file_operations`.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/mock_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/msg_ring.c -->
# File Research: sources/os/linux/linux/io_uring/msg_ring.c

## Purpose
Implements `IORING_OP_MSG_RING`, allowing one io_uring instance to post CQEs or send fixed files to another ring.

## Main Responsibilities
- Parses MSG_RING SQEs into `io_msg`.
- Sends data CQEs to a target ring, optionally passing CQE flags.
- Sends a source fixed file from the current ring into a destination fixed-file slot in another ring.
- Handles target rings requiring task-complete semantics by queueing remote task_work to the submitter task.
- Avoids ABBA deadlocks by trylocking target context when source context is already locked; returns `-EAGAIN` so the request can be punted.
- Provides synchronous data-only helper for non-request contexts.

## Key Entry Points
- `io_msg_ring_prep`
- `io_msg_ring`
- `io_msg_ring_cleanup`
- `io_uring_sync_msg_ring`

## Important Invariants
- Target must be an io_uring file.
- SEND_FD cannot target the same ring and cannot send data length.
- Disabled target rings return `-EBADFD`.
- If file installation succeeds but target CQE posting overflows, sender sees `-EOVERFLOW` and must arrange later notification if needed.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/msg_ring.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/msg_ring.h -->
# File Research: sources/os/linux/linux/io_uring/msg_ring.h

## Purpose
Declares MSG_RING interfaces.

## Contents
- Synchronous data helper: `io_uring_sync_msg_ring`
- Request prep and issue functions: `io_msg_ring_prep`, `io_msg_ring`
- Cleanup hook: `io_msg_ring_cleanup`

## Role
Used by opcode definitions and by callers that need data-only ring-to-ring notification without a full io_uring request.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/msg_ring.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/napi.c -->
# File Research: sources/os/linux/linux/io_uring/napi.c

## Purpose
Implements optional NAPI busy-poll integration for io_uring when `CONFIG_NET_RX_BUSY_POLL` is enabled.

## Main Responsibilities
- Tracks NAPI ids in both a hash table and RCU list.
- Supports dynamic tracking from sockets and static add/delete by userspace.
- Removes stale dynamic entries after timeout.
- Registers/unregisters NAPI settings through `io_uring_napi`, returning previous settings to userspace.
- Executes busy-poll loops during blocking CQ waits and SQPOLL idle paths.
- Honors busy-poll timeout, prefer-busy-poll setting, signals, available CQEs, and pending io_uring work as loop termination conditions.

## Key Entry Points
- `io_napi_init`
- `io_napi_free`
- `io_register_napi`
- `io_unregister_napi`
- `__io_napi_add_id`
- `__io_napi_busy_loop`
- `io_napi_sqpoll_busy_poll`

## Important Invariants
- NAPI tracking mode transitions are serialized with `napi_lock`.
- Registering resets tracking to inactive, frees old entries, configures settings, then publishes the new mode.
- Busy-poll timeout is capped to 10 ms on registration.
- IOPOLL rings reject NAPI registration.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/napi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/napi.h -->
# File Research: sources/os/linux/linux/io_uring/napi.h

## Purpose
Provides the NAPI integration interface and no-op fallbacks.

## Contents
- Under `CONFIG_NET_RX_BUSY_POLL`, declares init/free/register/unregister/add/busy-loop/SQPOLL functions.
- Inline `io_napi_add` records a socket’s `sk_napi_id` for dynamic tracking when enabled.
- Inline `io_napi_busy_loop` skips work when the tracked list is empty.
- Without busy-poll support, all operations become no-op or `-EOPNOTSUPP`.

## Role
Allows network and wait paths to call NAPI helpers without scattering configuration guards throughout the core.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/napi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/net.c -->
# File Research: sources/os/linux/linux/io_uring/net.c

## Purpose
Implements io_uring network opcodes: send/recv/sendmsg/recvmsg, zero-copy send, zero-copy receive hook, accept, socket, connect, shutdown, bind, and listen.

## Main Responsibilities
- Parses SQEs into per-op command structs and validates unsupported fields/flags.
- Imports msghdrs, compat msghdrs, iovecs, fixed buffers, and provided buffers.
- Supports single-shot, multishot, and bundle send/recv behavior.
- Handles `MSG_WAITALL`, partial transfers, retry-on-`EAGAIN`, poll-first, nowait, socket-nonempty CQE flags, and fairness caps for multishot loops.
- Implements recvmsg multishot header layout (`io_uring_recvmsg_out` plus sockaddr/control space).
- Supports send zero-copy with notification CQEs, memory accounting, `ubuf_info`, fixed-buffer skb fragment filling, usage reporting, and cleanup on failure.
- Hooks zero-copy receive through zcrx contexts.
- Implements fixed-file installation variants for `accept` and `socket`.
- Handles connect in-progress state and socket error extraction after poll readiness.
- Forces async bind for filesystem-backed UNIX socket paths to avoid lockdep issues around mount write semaphores.

## Key Entry Points
- Prep: `io_sendmsg_prep`, `io_recvmsg_prep`, `io_send_zc_prep`, `io_recvzc_prep`, `io_accept_prep`, `io_socket_prep`, `io_connect_prep`, `io_shutdown_prep`, `io_bind_prep`, `io_listen_prep`
- Issue: `io_sendmsg`, `io_send`, `io_recvmsg`, `io_recv`, `io_sendmsg_zc`, `io_recvzc`, `io_accept`, `io_socket`, `io_connect`, `io_shutdown`, `io_bind`, `io_listen`
- Cleanup/failure: `io_sendmsg_recvmsg_cleanup`, `io_send_zc_cleanup`, `io_sendrecv_fail`, `io_netmsg_cache_free`

## Important Invariants
- Network async data is cached in `ctx->netmsg_cache`; embedded iovec allocations must be freed or recycled carefully.
- Multishot recv requires provided buffers and cannot use `MSG_WAITALL`.
- Bundle sends/receives commit multiple provided buffers and compute CQE buffer count from residual iterator state.
- Zero-copy send always produces a notification CQE and currently rejects `IOSQE_CQE_SKIP_SUCCESS`.
- Fixed-buffer zero-copy import is delayed until issue time when `REQ_F_IMPORT_BUFFER` is set.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/net.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/net.h -->
# File Research: sources/os/linux/linux/io_uring/net.h

## Purpose
Declares network opcode interfaces and async message state.

## Contents
- `io_async_msghdr`: cached vector state plus a clearable group containing fast iovec, sockaddr storage, msghdr, control/payload lengths, and user address.
- Declares all network prep/issue/cleanup/failure functions.
- Declares socket BPF population and network async-cache free hook.
- Provides `CONFIG_NET` fallbacks for builds without networking.

## Role
Connects `opdef.c`, core async-data allocation, BPF filtering, and network opcode implementations.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/net.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/nop.c -->
# File Research: sources/os/linux/linux/io_uring/nop.c

## Purpose
Implements NOP and NOP128 test/control opcodes.

## Behavior
- Supports injected result values, normal or fixed file lookup, fixed-buffer lookup, forced task_work completion, and 32-byte CQEs.
- Validates NOP-specific flags and CQE32 availability.
- Optional file lookup exercises normal fd and fixed-file paths.
- Optional fixed-buffer lookup exercises registered buffer resource lookup.
- Optional `IORING_NOP_TW` queues completion through task_work and returns `IOU_ISSUE_SKIP_COMPLETE`.
- `IORING_NOP_CQE32` emits extra CQE payload from SQE fields.

## Key Entry Points
- `io_nop_prep`
- `io_nop`

## Role
Useful for feature validation, ABI testing, resource lookup testing, and completion-path testing without actual IO.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/nop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/nop.h -->
# File Research: sources/os/linux/linux/io_uring/nop.h

## Purpose
Declares NOP opcode hooks.

## Contents
- `io_nop_prep`
- `io_nop`

## Role
Used by `opdef.c` for `IORING_OP_NOP` and `IORING_OP_NOP128`.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/nop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/notif.c -->
# File Research: sources/os/linux/linux/io_uring/notif.c

## Purpose
Implements notification requests used by io_uring zero-copy send.

## Main Responsibilities
- Allocates notification `io_kiocb` objects from the normal request cache.
- Initializes `ubuf_info` with io_uring-specific ops.
- Completes notifications from skb zerocopy callbacks once all refs drop.
- Tracks whether zero-copy was used or copied when usage reporting is requested.
- Unaccounts memory charged for notification-backed zerocopy buffers.
- Supports linking multiple io_uring notifications onto one skb when they share context/task constraints.

## Key Entry Points
- `io_alloc_notif`
- `io_tx_ubuf_complete`

## Important Invariants
- Notification completion is delivered through io_uring task_work.
- Linked notifications must complete in the same task_work context; mixed ctx/tctx links are rejected.
- `io_notif_tw_complete` may walk a linked notification chain and completes each request.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/notif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/notif.h -->
# File Research: sources/os/linux/linux/io_uring/notif.h

## Purpose
Defines notification state and inline helpers for zero-copy send.

## Contents
- `io_notif_data`: stores file placeholder, `ubuf_info`, linked-notification pointers, page-accounting count, and usage-reporting booleans.
- Declares notification allocation and skb completion.
- Defines `io_notif_to_data`.
- Defines `io_notif_flush`, which completes the notification as successful.
- Defines `io_notif_account_mem`, charging approximate pages to the ring user.

## Role
Used by network zero-copy send paths to produce notification CQEs and manage zerocopy memory accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/notif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/opdef.c -->
# File Research: sources/os/linux/linux/io_uring/opdef.c

## Purpose
Central opcode definition table for io_uring.

## Main Responsibilities
- Maps every `IORING_OP_*` opcode to issue-time metadata: file requirement, polling direction, iopoll support, buffer selection support, regular-file hashing, unbound worker policy, vectored status, 128-byte SQE status, async-data size, BPF filter payload size, prep function, issue function, and filter population hook.
- Maps every opcode to cold metadata: printable name, SQE copy hook, cleanup hook, and fail hook.
- Provides unsupported-op prep fallback for config-disabled features.
- Validates opcode table completeness at init.

## Key Functions
- `io_uring_get_opcode`
- `io_uring_op_supported`
- `io_uring_optable_init`

## Important Details
- Network opcodes are conditionally wired to real handlers only under `CONFIG_NET`.
- Epoll and futex opcodes similarly depend on their config guards.
- Read/write opcodes declare async data and cleanup/fail hooks.
- `URING_CMD` and `URING_CMD128` include SQE-copy and cleanup hooks.
- `NOP128` and `URING_CMD128` are marked `is_128`.
- `MSG_RING`, provided buffers, fixed fd install, zcrx recv, bind/listen, pipe, and newer fixed-vector operations are represented in the same uniform tables.

## Role
This file is the dispatch contract consumed by core submission, validation, cleanup, audit, worker selection, BPF filtering, and failure handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/opdef.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/opdef.h -->
# File Research: sources/os/linux/linux/io_uring/opdef.h

## Purpose
Declares opcode metadata structures and table accessors.

## Contents
- `struct io_issue_def`: hot-path issue metadata and function pointers.
- `struct io_cold_def`: opcode name plus less-frequent SQE copy, cleanup, and fail hooks.
- Extern declarations for `io_issue_defs` and `io_cold_defs`.
- Declares `io_uring_op_supported` and `io_uring_optable_init`.

## Role
Used by core submission to validate SQEs, decide file/poll/worker behavior, allocate async state, issue requests, and clean up failed or completed operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/opdef.h -->