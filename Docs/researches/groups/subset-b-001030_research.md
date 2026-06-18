# subset-b-001030 research

Grouped research for Android Binder C and Rust Binder support files. Each section preserves the source path and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder.c -->
# sources/distributed-fs/ceph-client/drivers/android/binder.c

## Purpose

This is the main Android Binder IPC kernel driver implementation. It exposes Binder devices through `binder_fops`, backs `/dev/binder`-style misc devices and binderfs devices, implements the userspace Binder protocol commands and returns, translates binder objects and file descriptors between processes, manages per-process Binder address-space buffers through `binder_alloc`, tracks object/reference lifetimes, and publishes debug/diagnostic state through debugfs and binderfs proc log files.

The file is stateful kernel IPC infrastructure rather than a Ceph-specific component. In this source tree it is a vendored Linux driver under the distributed-fs client sources, and it integrates with sibling Android driver files such as `binder_alloc.c`, `binderfs.c`, `binder_internal.h`, `binder_trace.h`, and `binder_netlink.c`.

## Important APIs, types, and functions

The file exports `binder_fops`, `binder_add_device()`, `binder_remove_device()`, the KUnit-visible `binder_vm_fault()`, and the `device_initcall(binder_init)` initializer. Most other functions are static helpers over core internal types declared in `binder_internal.h`: `binder_proc`, `binder_thread`, `binder_node`, `binder_ref`, `binder_transaction`, `binder_buffer`, `binder_work`, `binder_context`, `binder_device`, death/freeze notification objects, and transaction log entries.

Important entry points are:

- `binder_open()`, `binder_release()`, `binder_flush()`, `binder_mmap()`, and `binder_poll()` implement file operations.
- `binder_ioctl()` dispatches user ioctls such as `BINDER_WRITE_READ`, `BINDER_SET_CONTEXT_MGR[_EXT]`, `BINDER_SET_MAX_THREADS`, `BINDER_THREAD_EXIT`, `BINDER_VERSION`, node debug queries, freezer ioctls, one-way spam detection, and extended-error retrieval.
- `binder_thread_write()` consumes `BC_*` commands including refcount changes, transaction submission, buffer free, looper registration, death notification, and freeze notification operations.
- `binder_thread_read()` emits `BR_*` returns, waits for work, applies fd fixups in the recipient context, returns transactions/replies/errors, delivers node ref updates, death/freeze notifications, transaction-complete events, and spawn-looper requests.
- `binder_transaction()` is the central transaction constructor. It resolves the target node/thread/process, allocates the destination buffer, copies and validates the offsets array, translates embedded Binder objects, handles scatter-gather buffers and pointer fixups, optionally attaches security context data, queues the work, and performs detailed failure cleanup.
- `binder_proc_transaction()` queues transactions to a target thread, process todo list, or node async queue and handles frozen-process behavior including `TF_UPDATE_TXN` superseding.
- `binder_translate_binder()`, `binder_translate_handle()`, `binder_translate_fd()`, `binder_translate_fd_array()`, `binder_fixup_parent()`, `binder_validate_ptr()`, and `binder_validate_fixup()` implement object translation and validation.
- `binder_inc_ref_for_node()`, `binder_update_ref_for_handle()`, `binder_get_ref_for_node_olocked()`, `binder_cleanup_ref_olocked()`, `binder_inc_node*()`, and `binder_dec_node*()` manage Binder reference accounting.
- `binder_deferred_release()`, `binder_thread_release()`, `binder_node_release()`, and `binder_release_work()` tear down process, thread, node, and pending work state.

## Control flow

Normal operation begins at `binder_open()`, which allocates a `binder_proc`, initializes locks/lists/stats/allocator state, attaches the process to a `binder_device` context, and registers global process/debug entries. Userspace then mmaps the Binder buffer region through `binder_mmap()`, which rejects writable mappings, marks the VMA `VM_DONTCOPY | VM_MIXEDMAP`, and delegates page management to `binder_alloc_mmap_handler()`.

Runtime protocol activity flows through `BINDER_WRITE_READ`. The write side parses command words sequentially and updates `write_consumed` after each handled command. Transactions call `binder_transaction()`, which distinguishes replies from new calls. Replies pop `thread->transaction_stack` and target the original caller. New calls resolve either a handle-backed target node or handle 0 context manager node, reject self-calls, and run LSM checks. The transaction buffer layout is data, aligned offsets, optional extra scatter-gather buffers, and optional LSM security context. Offsets are copied first, then each object is validated in increasing order before data is copied or fixups are queued.

The read side selects thread-local work before process work, blocks unless nonblocking, and uses `waiting_threads` for process work scheduling. It dequeues `binder_work` records, emits the corresponding `BR_*` protocol item, and for transactions prepares `binder_transaction_data[_secctx]`. For incoming transaction work, fd fixups are applied only after the target thread is running in the target process, so installed descriptors land in the correct file table. Synchronous transactions are pushed on the target thread stack until a reply; one-way transactions are freed after delivery and async serialization is enforced by `node->has_async_transaction` plus `node->async_todo`.

Release is deferred through `binder_defer_work()` and the global `binder_deferred_work` worker. File release removes proc debug entries, then `binder_deferred_release()` marks the proc dead, releases threads, nodes, outgoing refs, todo lists, delivered notifications, Binder allocator state, credentials, task refs, and finally the device ref if needed.

## State and persistence behavior

Persistent driver state is in global lists and per-open objects. Global state includes `binder_devices`, `binder_procs`, `binder_dead_nodes`, `binder_deferred_list`, debugfs dentries, transaction logs, stats, and module parameters (`debug_mask`, `devices`, `stop_on_user_error`). Per process, `binder_proc` holds rbtrees of threads, nodes, and refs, todo lists, delivered death/freeze lists, freeze flags, outstanding transaction count, descriptor bitmap, allocator state, context pointer, credentials, task pointer, debug entries, and thread-pool counters. Per thread, `binder_thread` tracks todo work, waitqueue, looper state, transaction stack, temporary refs, return errors, and extended error.

No durable on-disk persistence is performed. State persists only while Binder devices, open files, mmaps, transactions, and refs exist. Debugfs and binderfs proc files reflect live memory. Transaction logs are in-memory ring buffers of 32 entries each for successful and failed transactions.

## Dependencies and integration points

The driver depends on Linux VFS/miscdevice, mmap/VMA, waitqueue, rbtrees, debugfs, seq_file, poll/epoll, freezer, task_work, pid/user namespaces, credentials, LSM hooks, generic netlink, tracepoints, KUnit visibility, and UAPI definitions in `<uapi/linux/android/binder.h>`. Binder memory mapping and page copying are delegated to `binder_alloc_*` helpers. Device-context creation also integrates with binderfs through `is_binderfs_device()`, `binderfs_create_file()`, `init_binderfs()`, and binderfs superblock metadata. Transaction failure reporting uses `binder_netlink_report()` and `binder_nl_family`. Observability uses `binder_trace.h` tracepoints and debugfs entries named `state`, `state_hashed`, `stats`, `transactions`, `transactions_hashed`, `transaction_log`, and `failed_transaction_log`.

## Risks

The main risks are concurrency and lifetime bugs. The file has a strict lock order: `proc->outer_lock`, then `node->lock`, then `proc->inner_lock`, with dead-node special cases. Violating that order can deadlock. Node, thread, proc, and transaction temporary refs are used to survive lock drops and cross-thread teardown; missed tmprefs can become use-after-free, while missed decrements leak objects. Transaction buffer parsing is security-sensitive because user-provided offsets, object types, parent fixups, fd arrays, and scatter-gather buffers are copied into another process. Incorrect validation can expose stale pointers, untranslated fds, out-of-order parent fixups, or cross-process memory corruption. Deferred fd close and target-context fd installation are also sensitive because Binder can close its own fd while light fd refs exist. Freeze, oneway spam, async serialization, and update-transaction paths introduce edge cases where work may be consumed by another thread while error reporting still needs stable snapshot data.

## Test signals

Useful signals include Android Binder IPC integration tests, libbinder transaction/reply/oneway/fd-transfer tests, binderfs device creation tests, LSM/SELinux binder permission tests, process death and death-notification tests, freeze/thaw tests for `BR_FROZEN_REPLY` and `BR_TRANSACTION_PENDING_FROZEN`, one-way spam detection tests, debugfs transaction-log inspection, lockdep, KASAN/KCSAN, syzkaller-style malformed offsets/object/fd-array fuzzing, and the local KUnit coverage under `drivers/android/tests` for allocator and Binder fault behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/Makefile -->
# sources/distributed-fs/ceph-client/drivers/android/binder/Makefile

## Purpose

This Makefile builds the Rust Binder driver objects when `CONFIG_ANDROID_BINDER_IPC_RUST` is enabled. It is the build glue for the Rust implementation living under `drivers/android/binder/`, not for the legacy C `binder.c` driver.

## Important APIs, types, and functions

The file has no functions or types. Its build-facing API is:

- `ccflags-y += -I$(src)` so generated or local C trace/event headers can be found.
- `obj-$(CONFIG_ANDROID_BINDER_IPC_RUST) += rust_binder.o` to conditionally build the Rust Binder aggregate object.
- `rust_binder-y := rust_binder_main.o rust_binderfs.o rust_binder_events.o` to compose the aggregate from the Rust module object plus C shims for binderfs and events.

## Control flow

There is no runtime control flow. Kbuild reads this file during kernel build evaluation. If the Rust Binder config option is disabled, none of the listed objects are linked. If enabled, Kbuild links `rust_binder.o` from the three component objects.

## State and persistence behavior

The file persists no runtime state. It controls object inclusion in the kernel build output. The important state is the build-time configuration value of `CONFIG_ANDROID_BINDER_IPC_RUST` and the source directory include path.

## Dependencies and integration points

This Makefile depends on the kernel Kbuild object syntax and the surrounding Android driver Kconfig. It integrates Rust Binder code with C helper files `rust_binderfs.c` and `rust_binder_events.c`, plus local trace/event headers reachable through `-I$(src)`.

## Risks

The risk is build composition drift. Adding a Rust Binder source without updating this file can compile locally only under partial configs or fail at link time. Removing `-I$(src)` can break trace-event includes. Misnaming component objects can silently disable the Rust Binder implementation for enabled configs.

## Test signals

Build with `CONFIG_ANDROID_BINDER_IPC_RUST=y` or `m`, build with it disabled, and run a clean incremental rebuild after touching trace/event headers. Link-time presence of `rust_binder.o` and absence of unresolved Rust Binder/binderfs/event symbols are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/allocation.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/allocation.rs

## Purpose

This Rust file models a Binder transaction buffer allocation while the kernel owns or inspects it. It provides bounds-checked read/write/copy helpers over the target process page range, carries cleanup metadata for translated Binder objects and file descriptors, performs fd reservation/installation handoff, releases Binder object refs when the allocation is dropped, and parses serialized Binder object unions safely enough for the Rust Binder transaction path.

## Important APIs, types, and functions

Core types are:

- `AllocationInfo`: optional metadata attached to an allocation, including the offsets range, target node, one-way serialization node, clear-on-free flag, and `FileList`.
- `Allocation`: the live allocation handle. It stores offset, size, user pointer, owning `Arc<Process>`, optional info, drop policy, and debug id.
- `NewAllocation`: transparent wrapper for a newly allocated buffer. Its destructor marks failed transactions unless `success()` is called to extract the allocation.
- `AllocationView<'a>`: bounded view over the data area before offsets; reads/writes/copies through it fail if they exceed `limit`.
- `BinderObject`: C-layout union over UAPI Binder object variants, plus `BinderObjectRef` for typed matching.
- `TranslatedFds`, `Reservation`, `FileList`, `FileEntry`, and `FdsCloseOnFree`: fd translation bookkeeping.

Important methods include `Allocation::copy_into()`, `read()`, `write()`, `fill_zero()`, `keep_alive()`, `set_info_*()`, `info_add_fd_reserve()`, `info_add_fd()`, `translate_fds()`, `looper_need_return_on_free()`, `Drop::drop()`, `AllocationView::transfer_binder_object()`, `AllocationView::cleanup_object()`, `BinderObject::read_from()`, `read_from_inner()`, `as_ref()`, `size()`, and `TranslatedFds::commit()`.

## Control flow

Allocation use starts with `Allocation::new()` after the process allocator has reserved a range and marked pages in use. Transaction-building code copies user data into the allocation, records the offsets range and target/oneway node, collects fds needing translation, and may mark the allocation for zeroing on free. `translate_fds()` reserves new target-process fds with `O_CLOEXEC`, writes those fd numbers into the allocation, traces the receive side, and returns `TranslatedFds`. The caller later calls `commit()` to install files into reserved descriptors and obtain the close-on-free list.

`keep_alive()` transfers a successfully delivered allocation back to the owning `Process` as a freeable buffer and disables automatic free on `Drop`. If the allocation drops normally, cleanup runs: one-way node completion is signaled, target node metadata is cleared, each object in the offsets array is cleaned up through `AllocationView::cleanup_object()`, close-on-free fds are scheduled through `DeferredFdCloser` when running in the owning process group leader, sensitive data is zeroed when requested, and `Process::buffer_raw_free()` frees the raw buffer.

`BinderObject::read_from()` reads only the object size implied by the header while avoiding advancing the caller's `UserSliceReader` until the object type is validated. This prevents extra bytes from becoming a time-of-check/time-of-use surface.

## State and persistence behavior

State lives in the allocation object and in the owning `Process` allocator/page range. The `free_on_drop` flag selects RAII cleanup versus handoff to userspace-freeable state. `AllocationInfo` is intentionally optional, allowing buffers without embedded objects or fd work. File descriptor state is split: reservations are kernel-owned until `TranslatedFds::commit()`, and close-on-free descriptors are retained in `FdsCloseOnFree` for later buffer cleanup. No disk persistence exists.

## Dependencies and integration points

The file depends on Rust-for-Linux kernel APIs for `Arc`, `ARef<File>`, fd reservations, `UserSliceReader`, UAPI Binder structs, transmute traits, allocation vectors, and error codes. It integrates with `Process` page copying and buffer lifecycle methods, `Node`/`NodeRef` reference updates, `DeferredFdCloser` for delayed fd close, `defs.rs` constants/wrappers, and `trace::trace_transaction_fd_recv()`.

## Risks

The largest risks are incorrect bounds checks, mismatched object cleanup, and fd lifetime mistakes. `size_check()` must catch integer overflow and out-of-range access before unsafe page operations. `AllocationView` must keep object parsing inside the intended data region, while direct `alloc` access is reserved for intentional full-allocation operations. Drop cleanup must mirror translation: binder objects increment user refs and handles during delivery, so cleanup must decrement the correct node/ref variant. Deferred close is best effort; allocation failure while creating closers can leave later fds to userspace behavior. `NewAllocation::success()` uses `transmute`, so its transparent layout invariant is critical.

## Test signals

Good coverage includes Rust Binder transaction tests with binder/handle translation in same-process-owner and cross-process cases, fd and fd-array transfer tests, failed transaction cleanup, `TF_CLEAR_BUF` zeroing checks, one-way ordering checks through `pending_oneway_finished()`, invalid object type/offset fuzzing, close-on-free behavior when freeing buffers, and KASAN/KCSAN or Rust Miri-style review of unsafe page access assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/allocation.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/context.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/context.rs

## Purpose

This Rust file manages Binder contexts. A Binder context corresponds to one Binder device namespace such as `/dev/binder` or `/dev/hwbinder`, owns the context-manager node for that namespace, and tracks all `Process` instances registered in the context. It also exposes snapshot helpers for debug and control paths that need to iterate contexts or processes.

## Important APIs, types, and functions

Key types are:

- `CONTEXTS`: global `Mutex<ContextList>` initialized by the module initializer.
- `ContextList`: vector of all active `Arc<Context>` values.
- `Manager`: mutex-protected context-manager state: optional manager `NodeRef`, allowed manager uid, and all registered processes.
- `Context`: pinned struct containing the manager mutex and context name.

Important functions are `get_all_contexts()`, `Context::new()`, `deregister()`, `register_process()`, `deregister_process()`, `set_manager_node()`, `unset_manager_node()`, `get_manager_node()`, `for_each_proc()`, `get_all_procs()`, and `get_procs_with_pid()`.

## Control flow

`Context::new()` copies the supplied C string name into a `CString`, initializes an empty `Manager`, wraps the context in an `Arc`, and appends it to the global context list. A `Process` registers through `register_process()` only if its `proc.ctx` matches the `Context` receiving the call. Deregistration removes the process from `all_procs` and opportunistically shrinks vector capacity when utilization drops below one quarter.

`set_manager_node()` serializes under the manager mutex, rejects duplicate context-manager setup, calls the Binder LSM context-manager hook, enforces that repeated manager setup uses the same effective uid, then stores the manager node and uid. `get_manager_node()` returns a cloned `NodeRef` with requested strong/weak semantics or maps missing manager state to a dead Binder error. Iteration and snapshot helpers lock the manager, clone `Arc<Process>` handles into temporary vectors where needed, and release the lock before callers own the snapshots.

## State and persistence behavior

Context state is process-memory state only. `CONTEXTS` is the global registry of live contexts. Each `Context` persists while held by an `Arc`, typically through devices and processes. The manager uid survives `unset_manager_node()` because it is kept in `Manager::uid`, enforcing the C Binder behavior that a context manager may not be replaced by a different effective uid after first setup.

## Dependencies and integration points

The file depends on Rust-for-Linux synchronization, allocation vectors, strings, `Arc`, `Kuid`, and security hooks. It integrates with `Process` ownership (`proc.ctx`), `NodeRef` cloning/refcount behavior, and `BinderError` for dead context-manager replies. The global list supports module-wide debug or binderfs-style enumeration.

## Risks

The main risks are stale process entries, context-manager replacement bugs, and lock-scope mistakes. `register_process()` and `deregister_process()` check context identity; ignoring those checks would corrupt another context's process list. The manager mutex protects both context-manager node and process vector, so callbacks passed to `for_each_proc()` must not assume they can mutate context membership. Capacity shrinking is intentionally conservative; aggressive shrink could cause allocation churn under frequent open/close.

## Test signals

Tests should cover creating multiple named contexts, process register/deregister identity checks, duplicate context-manager rejection, manager uid enforcement, missing-manager `BR_DEAD_REPLY` behavior through `BinderError::new_dead()`, `get_procs_with_pid()` matching across duplicate opens, and deregistering a context so `get_all_contexts()` no longer returns it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/context.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/deferred_close.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/deferred_close.rs

## Purpose

This Rust file implements Binder-specific deferred file-descriptor closing. It schedules `task_work` so a file whose descriptor was closed during Binder ioctl handling keeps an extra file reference until the current task returns to userspace. This mirrors the C Binder pattern that avoids use-after-free hazards when Binder closes a descriptor that might be held by an active `fdget()` light reference.

## Important APIs, types, and functions

The public helper is `DeferredFdCloser`. It owns a heap-allocated `DeferredFdCloserInner`, which is C-layout and contains a `callback_head` plus a raw `struct file *`. `DeferredFdCloser::new()` allocates the inner object. `DeferredFdCloser::close_fd()` schedules task work, removes the fd from the current file table, calls `filp_close()`, and transfers the final file ref to the task-work callback. `DeferredFdCloser::do_close_fd()` is the unsafe extern callback that reconstructs the `KBox`, calls `fput()` if needed, and frees the allocation. `DeferredFdCloseError` reports `TaskWorkUnavailable` or `BadFd` and maps to `ESRCH` or `EBADF`.

## Control flow

Callers allocate a closer before attempting the close. `close_fd()` rejects kernel threads because task work cannot run for them. It then converts the box to a raw pointer, initializes the embedded `callback_head`, and calls `task_work_add(current, ..., TWA_RESUME)` before touching the fd table. If scheduling fails, ownership returns to a `KBox` and the allocation is dropped.

After task work is scheduled, `file_close_fd(fd)` removes the descriptor and returns a file pointer if the fd was valid. Invalid fds leave the task work queued with a null file pointer, and the callback later frees the allocation. Valid fds get an extra `get_file()` ref, `filp_close()` consumes the close path's ref, and the extra ref is stored in the inner object so `do_close_fd()` releases it on return to userspace.

## State and persistence behavior

The only persistent state is the scheduled task-work allocation and the optional file ref it owns. It is bound to the current task and is expected to execute before userspace resumes. The helper is single-use: `close_fd(self, fd)` consumes the closer and either schedules ownership into task work or drops it on scheduling failure.

## Dependencies and integration points

The file depends on Rust-for-Linux allocation, raw kernel bindings for `callback_head`, task flags, `init_task_work`, `task_work_add`, `file_close_fd`, `get_file`, `filp_close`, and `fput`. It is used by allocation cleanup for Binder buffers with close-on-free fds. The comments cite the historical C Binder fix for avoiding `ksys_close()` during active `fdget()`.

## Risks

This code is unsafe-boundary heavy. The raw pointer must always refer to the first field of `DeferredFdCloserInner` so the callback cast is valid. The file pointer invariant must hold: a non-null pointer owns exactly one ref that `do_close_fd()` may release. Scheduling task work before closing avoids a half-closed fd on task-work failure, but a bad fd still queues a no-op callback; callers must tolerate `BadFd`. Calling from a kthread returns `TaskWorkUnavailable`, so higher-level cleanup must not assume closure always succeeds.

## Test signals

Useful tests include valid fd deferred close from a normal task, invalid fd returning `EBADF`, kthread context returning `ESRCH`, stress where Binder frees buffers while holding descriptors obtained through fd lookup, leak checks proving task-work allocations are freed, and KASAN tests around concurrent close/return-to-userspace paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/deferred_close.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/defs.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/defs.rs

## Purpose

This Rust file centralizes Rust Binder access to Binder UAPI constants and C-layout UAPI structs. It strips long generated UAPI prefixes into local `pub(crate)` constants, re-exports Binder object type constants, and wraps UAPI structs in transparent `MaybeUninit` newtypes that preserve padding bytes while implementing `FromBytes` and `AsBytes` for safe byte copying.

## Important APIs, types, and functions

The `pub_no_prefix!` macro creates local constants for Binder return protocol values (`BR_TRANSACTION`, `BR_REPLY`, `BR_DEAD_REPLY`, `BR_FROZEN_REPLY`, `BR_TRANSACTION_PENDING_FROZEN`, and others), command protocol values (`BC_TRANSACTION`, `BC_REPLY`, refcount commands, looper commands, death/freeze commands), flat binder flags, and transaction flags.

The `decl_wrapper!` macro defines transparent wrappers for UAPI structs including `BinderNodeDebugInfo`, `BinderNodeInfoForRef`, `FlatBinderObject`, `BinderFdObject`, `BinderFdArrayObject`, `BinderObjectHeader`, `BinderBufferObject`, `BinderTransactionData`, `BinderTransactionDataSecctx`, `BinderTransactionDataSg`, `BinderWriteRead`, `BinderVersion`, freezer structs, `BinderHandleCookie`, and `ExtendedError`.

Helper methods are `BinderVersion::current()`, `BinderTransactionData::with_buffers_size()`, `BinderTransactionDataSecctx::tr_data()`, and `ExtendedError::new()`.

## Control flow

Runtime control flow is minimal. Wrapper defaults zero all bytes including padding. `Deref` and `DerefMut` expose the initialized inner UAPI struct while retaining `MaybeUninit` storage to avoid accidentally fabricating or dropping padding during byte-level copies. `BinderTransactionData::with_buffers_size()` constructs the scatter-gather variant around an existing transaction payload. `BinderTransactionDataSecctx::tr_data()` transmutes the embedded UAPI transaction field into the Rust wrapper view.

## State and persistence behavior

There is no mutable global state. Constants are compile-time aliases and wrappers are per-value byte containers. The key persistence behavior is preserving UAPI padding bytes during read/write of structures crossing the userspace ABI, which matters for exact ABI compatibility and avoiding uninitialized-byte exposure.

## Dependencies and integration points

The file depends on `kernel::uapi`, Binder UAPI generated bindings, `MaybeUninit`, `Deref`, `DerefMut`, and Rust-for-Linux `AsBytes`/`FromBytes`. Other Rust Binder modules import this file for protocol constants, object types, transaction wrappers, version reporting, and extended-error construction.

## Risks

The risks are ABI drift and invalid wrapper assumptions. `decl_wrapper!` marks each wrapper as `FromBytes` and `AsBytes`; this is only sound for C UAPI structs whose initialized byte patterns are acceptable and whose padding is intentionally preserved. If a UAPI struct gains stricter validity constraints, the unsafe impl assumptions need review. Prefix-stripped constants must stay in sync with generated `uapi` names. `tr_data()` relies on transparent layout compatibility between the UAPI field and wrapper.

## Test signals

Build failures against changed UAPI names are an immediate signal. Runtime tests should verify `BINDER_VERSION`, `BINDER_WRITE_READ`, SG transaction wrapping, security-context transaction wrapping, extended-error reporting, and byte-for-byte ABI size/alignment checks against the C Binder structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/defs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/error.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/error.rs

## Purpose

This Rust file defines the Rust Binder error type used for failures that are returned through the Binder protocol in `BINDER_WRITE_READ`, rather than directly as ioctl `errno`. It distinguishes protocol-level reply commands such as dead, frozen, pending-frozen, and failed replies, while optionally retaining the underlying kernel `Error` for extended-error reporting and debugging.

## Important APIs, types, and functions

The main alias is `BinderResult<T = ()> = Result<T, BinderError>`. `BinderError` stores `reply: u32` and `source: Option<Error>`. Constructors are `new_dead()`, `new_frozen()`, and `new_frozen_oneway()`. `is_dead()` recognizes `BR_DEAD_REPLY`. Conversion impls map `kernel::Error`, `BadFdError`, and `AllocError` into `BR_FAILED_REPLY` with an appropriate source (`ENOMEM` for allocation failure). A custom `Debug` impl formats known Binder reply values by name and includes the source error for failed replies.

## Control flow

Code that detects a Binder-level failure constructs or converts into `BinderError`. Callers can return it through `BinderResult`, then higher layers translate `reply` into a `BR_*` item for userspace and can store `source` in extended-error state. Direct dead/frozen constructors have no source errno because the protocol reply is the meaningful result. Generic kernel errors become `BR_FAILED_REPLY`.

## State and persistence behavior

`BinderError` is an owned value with no global state. Its `source` field preserves errno context across Rust call layers until the Binder protocol response and extended error can be produced. No long-term persistence exists.

## Dependencies and integration points

The file depends on `defs.rs` for Binder `BR_*` constants, Rust-for-Linux `Error`, `BadFdError`, allocation errors, and kernel formatting. It integrates with context-manager lookup, transaction delivery, fd handling, allocation failures, and debug logging in the Rust Binder implementation.

## Risks

The main risk is returning the wrong channel of failure. Some failures must be delivered as Binder replies (`BR_DEAD_REPLY`, `BR_FROZEN_REPLY`, `BR_TRANSACTION_PENDING_FROZEN`) rather than ioctl errno; converting them to plain `Error` would break userspace protocol expectations. Conversely, low-level copy or ioctl validation errors may still need direct errno in callers outside this type. Missing source errors reduce extended-error diagnostics.

## Test signals

Tests should cover dead context manager mapping to `BR_DEAD_REPLY`, frozen sync and one-way paths, allocation failure mapping to `BR_FAILED_REPLY` plus `ENOMEM`, bad fd conversion, `is_dead()`, and debug formatting for known and unknown reply values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/error.rs -->
