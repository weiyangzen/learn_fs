# sources/distributed-fs/ceph-client/drivers/android/binder_internal.h

## Purpose
`binder_internal.h` is the central internal C header for the Binder driver. It defines Binder device, binderfs, debugfs, statistics, work, node, reference, process, thread, fd-fixup, transaction, and generic object structures shared across Binder C implementation files.

## Important APIs, Types, And Functions
Important structs include `binder_context`, `binder_device`, `binderfs_mount_opts`, `binderfs_info`, `binder_debugfs_entry`, `binder_stats`, `binder_work`, `binder_error`, `binder_node`, `binder_ref_death`, `binder_ref_freeze`, `binder_ref_data`, `binder_ref`, `binder_proc`, `binder_thread`, `binder_txn_fd_fixup`, `binder_transaction`, and `binder_object`. It declares `binder_fops`, `binder_devices_param`, binderfs helpers, debugfs iteration macro, `binder_add_device`, `binder_remove_device`, and KUnit `binder_vm_fault`.

## Control Flow
The header is declarative. Runtime flow is encoded by struct relationships: devices point to contexts; processes own threads, nodes, references, work lists, allocator state, freeze wait state, and debug entries; threads own todo lists and transaction stacks; transactions link sender, target process/thread, parent transactions, buffer, fd fixups, security context, and lock-protected endpoint pointers.

## State And Persistence
Most Binder C persistent state is described here. `binder_proc` is per opened Binder file/process and persists until deferred release. `binder_thread` persists while a task participates in Binder. Nodes and refs model exported objects and remote handles. Binderfs mount state persists per superblock. Statistics persist as atomics until object teardown. Lock-order comments document `outer_lock`, node lock, and `inner_lock` nesting.

## Dependencies
It includes filesystem, list, miscdevice, mutex, refcount, uid/gid, Binder UAPI, `binder_alloc.h`, and `dbitmap.h`. Binderfs declarations are conditional on `CONFIG_ANDROID_BINDERFS`; KUnit VM fault exposure is conditional on `CONFIG_KUNIT`.

## Integration Points
Almost every C Binder file includes this header. `binderfs.c` consumes device and mount structs, allocator code is embedded through `binder_proc`, tracepoints in `binder_trace.h` read `binder_transaction`, `binder_node`, and `binder_ref_data`, and debugfs code iterates `binder_debugfs_entries`.

## Risks
This is a shared layout and locking contract. Misdocumented or changed lock ordering can create deadlocks. Struct field drift can break tracepoints and any Rust/C layout bridge. Source review shows duplicated comments in some areas; comments are less risky than code, but stale lock annotations can mislead maintainers. The C `binder_transaction` layout differs from the Rust `Transaction` object, so any bridge must use explicit layout metadata instead of assuming identity.

## Test Signals
Full Binder build coverage, sparse/lockdep for lock ordering, debugfs and binderfs mount tests, Binder object/ref lifecycle tests, freeze/death notification tests, tracepoint build tests, and KUnit coverage for allocator and VM fault helpers are relevant signals.
