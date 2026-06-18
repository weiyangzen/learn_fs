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
