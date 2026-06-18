# Research: subset-b-001032

Grouped research for Android Binder Rust/C driver files and ATA libata configuration/ACard AHCI support under `sources/distributed-fs/ceph-client`. Each section is source-tree aligned for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/thread.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/thread.rs

## Purpose
`thread.rs` implements the Rust Binder `Thread` object: the per-userspace-thread endpoint that handles binder write commands, read-side work delivery, looper state, transaction-stack management, object translation, scatter-gather buffer copying, and reply/error delivery. It is the main bridge between Binder ioctl payloads and higher-level `Process`, `Node`, `Allocation`, and `Transaction` logic.

## Important APIs, Types, And Functions
Key local types are `Thread`, `InnerThread`, `PushWorkRes`, `ThreadError`, `ScatterGatherState`, `ScatterGatherEntry`, `PointerFixupEntry`, `ParentFixupInfo`, and `UnusedBufferSpace`. Important methods include `Thread::new`, `write_read`, `write`, `read`, `transaction`, `transaction_inner`, `reply_inner`, `oneway_transaction_inner`, `copy_transaction_data`, `translate_object`, `apply_sg`, `get_work`, `get_work_local`, `deliver_reply`, `deliver_single_reply`, `unwind_transaction_stack`, `push_work`, `push_work_if_looper`, `poll`, `exit_looper`, and `release`. `InnerThread` owns looper flags, local work queue, current transaction stack head, reusable return/reply error work, and extended error state.

## Control Flow
The main ioctl path calls `write_read`: it copies a `BinderWriteRead` from userspace, drains write commands, optionally drains read work, writes consumed counts back, and clears `looper_need_return`. `write` parses `BC_*` commands, dispatching transactions/replies, reference updates, death/freeze notifications, looper registration, and buffer frees. Transaction commands call `read_transaction_info`, then select sync, reply, or oneway handling. Sync transactions allocate a target buffer, update the caller's transaction stack, queue deferred `BR_TRANSACTION_COMPLETE`, then submit work to a target thread or process. Replies pop the transaction being answered and deliver either a reply transaction or an error to the original sender. `read` chooses between local and process queues, emits an initial `BR_NOOP`, executes `DeliverToRead` work items until the buffer is full or a transaction payload is delivered, and may replace the noop with `BR_SPAWN_LOOPER`.

## State And Persistence
Persistent per-thread state lives in `InnerThread` behind a spinlock: looper flags, dead flag, work list, transaction stack head, reusable error work, and extended error. `Thread` also persists process/task references, wait condition variable, and list links for the process ready-thread list. Transaction payload state is not persisted here after delivery except through `current_transaction` and work queues. Scatter-gather state is transient for one `copy_transaction_data` call. `release` marks the thread dead, unwinds outstanding transaction stacks, and cancels pending local work.

## Dependencies
The file depends on kernel Rust primitives (`Arc`, `SpinLock`, `PollCondVar`, `UserSlice`, `LocalFile`, list support, task/security APIs), Binder UAPI command/return constants, and crate modules for allocation, process, node, transaction, errors, stats, tracing, and return writing. Security hooks include `security::binder_transaction`, `binder_transfer_binder`, and `binder_transfer_file`.

## Integration Points
It integrates with `Process` for thread registration, process-wide work, reference bookkeeping, buffer allocation/free, oneway spam detection, and freeze/death notification state. It integrates with `Transaction` through stack links, submit/delivery, replies, and outstanding transaction accounting. It integrates with allocation code by translating embedded binder objects, file descriptors, FDA arrays, pointer buffers, and optional security context into target-process buffers. Tracing is emitted for commands, waits, read/write completion, transaction send/receive, and fd send events.

## Risks
This is a high-risk Binder boundary: malformed user offsets, scatter-gather parent fixups, fd arrays, and pointer alignment must be rejected before kernel copies or fd installs occur. Transaction-stack races are guarded by rechecking `current_transaction`, but incorrect stack updates can deadlock sync calls or misroute replies. Looper state controls process work dispatch and `BR_SPAWN_LOOPER`; mistakes can starve work or over-request threads. Build coverage remains important because this module sits at the Rust Binder/C UAPI boundary and uses many generated UAPI layouts.

## Test Signals
Useful signals include Binder ioctl tests for all supported `BC_*` commands, sync/oneway/reply transaction loops, nested transaction-stack tests, looper pool registration/exit/poll behavior, `BR_SPAWN_LOOPER` behavior under load, malformed offset/fd-array/scatter-gather fuzzing, SELinux/security context transfer tests, fd-transfer lifetime tests, freeze notification and frozen-target transaction tests, and Rust Binder build coverage that catches duplicated fields or syntax regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/thread.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/trace.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/trace.rs

## Purpose
`trace.rs` is the Rust Binder tracepoint wrapper layer. It declares Rust-callable bindings for Binder tracepoints and exposes small safe wrapper functions that convert Rust Binder state and `Result` values into the C tracepoint ABI.

## Important APIs, Types, And Functions
The `declare_trace!` block declares tracepoints for ioctl entry/exit, read/write completion, wait-for-work decisions, transaction send/receive, fd send/receive, commands, and returns. `raw_transaction` casts a Rust `Transaction` reference to the generated `rust_binder_transaction` handle described by `TRANSACTION_LAYOUT` in `transaction.rs`. `to_errno` converts `kernel::error::Result` into integer errno. Public crate wrappers include `trace_ioctl`, `trace_ioctl_done`, `trace_read_done`, `trace_write_done`, `trace_wait_for_work`, `trace_transaction`, `trace_transaction_received`, `trace_transaction_fd_send`, `trace_transaction_fd_recv`, `trace_command`, and `trace_return`.

## Control Flow
Callers invoke wrappers at event sites in Binder ioctl, thread, and transaction code. The wrappers do no filtering or buffering; they immediately call the underlying tracepoint in an `unsafe` block. Transaction trace wrappers optionally pass a target task pointer or null and rely on the event consumer to decode fields through the transaction layout exported from Rust.

## State And Persistence
The file owns no persistent state. It observes transaction objects only for the duration of a tracepoint call and writes event records into the kernel tracing infrastructure when enabled. Errnos are computed per call and not retained.

## Dependencies
It depends on `kernel::tracepoint::declare_trace`, kernel C FFI types, `task_struct`, `Task`, and the generated `rust_binder_transaction` layout. Correctness depends on `transaction.rs` exporting offsets that match what C tracepoint code expects.

## Integration Points
The wrappers are used by Rust Binder thread and transaction code. They integrate with the C trace definitions in `binder_trace.h` and with ftrace/perf tooling that consumes Binder trace events. Transaction tracing is ABI-sensitive because it crosses Rust/C object-layout boundaries.

## Risks
The main risk is layout drift: if `TRANSACTION_LAYOUT` and the tracepoint-side interpretation disagree, tracing can read wrong fields or unsafe addresses. Pointer casts are intentionally narrow but still rely on the transaction object being alive for the tracepoint call. Missing trace wrappers for newer C events would leave observability gaps, while tracepoint ABI mismatches can break builds.

## Test Signals
Build with Rust Binder tracing enabled, run Binder transaction traffic while enabling `binder:*` ftrace events, verify ioctl/read/write errno values, check transaction IDs/codes/flags against debugfs or Binder logs, and validate fd send/receive trace offsets during fd transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/trace.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/transaction.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/transaction.rs

## Purpose
`transaction.rs` implements the Rust Binder `Transaction` work item and `TransactionInfo` metadata. It owns copied target-process allocations until userspace receives them, manages outstanding transaction accounting, selects target delivery queues, supports oneway transaction replacement, prepares translated file descriptors, and emits reply/error behavior on cancellation or delivery failure.

## Important APIs, Types, And Functions
`TransactionInfo` stores from/to pids and tids, code, flags, source data/offset pointers, sizes, target handle, reply errno/code, spam and reply flags. `Transaction` stores debug ID, target node, caller stack parent, sender thread, target process, allocation, outstanding flag, code/flags/sizes, sender euid, optional security-context offset, and start time. Key methods are `new`, `new_reply`, `submit`, `can_replace`, `is_stacked_on`, `clone_next`, `find_target_thread`, `find_from`, `set_outstanding`, `drop_outstanding_txn`, `prepare_file_list`, and `debug_print_inner`. The `DeliverToRead` implementation provides `do_work`, `cancel`, `should_sync_wakeup`, and `debug_print`.

## Control Flow
Constructors call `Thread::copy_transaction_data` to create an allocation in the target process, then annotate allocation metadata for target node, oneway node, clear-on-drop, or security context. `submit` locks the target process, marks the transaction outstanding, handles frozen-process behavior, routes oneway transactions through the target node async queue, or sends sync work to a thread found in the existing transaction stack or to the process queue. `do_work` prepares translated fd lists, fills `binder_transaction_data` or `binder_transaction_data_secctx`, writes the return code and payload to userspace, commits fds, keeps the allocation alive for userspace free, clears outstanding accounting, traces receipt, and updates the recipient thread's current transaction for sync calls.

## State And Persistence
The transaction persists as a refcounted work item until delivered, canceled, or dropped. Its allocation is protected by a spinlock and is taken exactly once for fd translation and userspace handoff; after `keep_alive`, userspace owns the buffer lifetime through Binder free-buffer commands. `is_outstanding` is an atomic guard ensuring target-process outstanding counts are decremented once. `from_parent` preserves transaction-stack ancestry for nested sync calls.

## Dependencies
The file depends on allocation and fd translation types, Binder flags/return constants, `Node` and `NodeRef`, `Process`, `Thread`, Binder security credentials, seq_file debugging, kernel atomics/time/task uid APIs, and the crate tracing layer. It also exports `TRANSACTION_LAYOUT` with field offsets for C/Rust trace integration.

## Integration Points
`Thread` creates and delivers transactions; `Process` queues work and tracks outstanding transactions; `Node` owns oneway queues and update-transaction replacement; allocation code translates fds and tracks buffer cleanup; tracing observes send/receive latency and metadata. Frozen process handling sets `sync_recv` or `async_recv` and returns Binder frozen errors.

## Risks
Error paths are subtle: delivery failures must send `BR_FAILED_REPLY` or `BR_DEAD_REPLY` without leaking allocations or double-dropping outstanding counts. Oneway replacement requires exact matching on sender pid, code, flags, and target node to avoid dropping semantically distinct work. File descriptor preparation happens just before userspace delivery; failures intentionally notify the sender and skip target delivery. The Rust/C transaction trace layout must stay synchronized with this struct.

## Test Signals
Test sync calls, replies, oneway calls, update transactions, frozen targets, dead-thread reply unwinding, fd transfer success/failure, `TF_CLEAR_BUF`, `FLAT_BINDER_FLAG_TXN_SECURITY_CTX`, oneway spam reporting, debugfs transaction output, outstanding transaction counts during freeze waits, and tracepoint transaction metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/transaction.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder_alloc.c -->
# sources/distributed-fs/ceph-client/drivers/android/binder_alloc.c

## Purpose
`binder_alloc.c` implements the classic C Binder per-process transaction buffer allocator. It manages the mmapped Binder buffer address space, best-fit buffer allocation, free-buffer coalescing, page installation into the target userspace VMA, LRU-based page reclamation, buffer zeroing, async-space accounting, oneway spam detection, debug output, and copy helpers for Binder payload data.

## Important APIs, Types, And Functions
Public functions include `binder_alloc_init`, `binder_alloc_shrinker_init`, `binder_alloc_shrinker_exit`, `binder_alloc_mmap_handler`, `binder_alloc_new_buf`, `binder_alloc_prepare_to_free`, `binder_alloc_free_buf`, `binder_alloc_deferred_release`, `binder_alloc_vma_close`, `binder_alloc_get_allocated_count`, `binder_alloc_print_allocated`, `binder_alloc_print_pages`, `binder_alloc_copy_user_to_buffer`, `binder_alloc_copy_to_buffer`, `binder_alloc_copy_from_buffer`, and the shrinker callback `binder_alloc_free_page`. Important internals include free/allocated rb-tree insertion, page install helpers, `sanitized_size`, `check_buffer`, async spam debugging, and LRU add/delete helpers.

## Control Flow
`binder_alloc_mmap_handler` validates a single mapping, caps it at 4 MiB, allocates the page array and initial free buffer, initializes async space to half the buffer, and marks the allocator mapped with release semantics. `binder_alloc_new_buf` validates mapping and size, preallocates a split buffer node, selects a best-fit free buffer under `alloc->mutex`, updates rb trees and async accounting, then installs missing pages into the remote mm. `binder_alloc_free_buf` optionally clears sensitive buffers, then coalesces adjacent free buffers and returns fully unused pages to the LRU. The shrinker walks the global `binder_freelist`, isolates pages, clears `alloc->pages`, zaps user mappings, and frees pages under careful mm/VMA/allocator locking.

## State And Persistence
Persistent state lives in `struct binder_alloc`: mm reference, mmap base, buffer list, free and allocated rb trees, free async byte count, installed page array, global or test LRU, buffer size, high watermark, mapped flag, and spam-detection flag. `struct binder_buffer` records each allocation's user address, sizes, flags, transaction/node pointers, and pid attribution. Pages persist until reclaimed by the shrinker or deferred release.

## Dependencies
The allocator depends on Linux mm APIs (`vm_insert_page`, `get_user_pages_remote`, VMA locking, `zap_vma_range`), rb trees, list LRU, shrinkers, highmem copy helpers, uaccess, module parameters, and `binder_trace.h`. KUnit-only exports are guarded through `VISIBLE_IF_KUNIT` and `EXPORT_SYMBOL_IF_KUNIT`.

## Integration Points
Binder process open/mmap initializes this allocator; transaction creation calls `binder_alloc_new_buf`; user `BC_FREE_BUFFER` flows call prepare/free; transaction delivery and object translation use copy helpers; debugfs/binderfs use print functions; memory pressure invokes the shrinker. The Rust Binder allocation wrapper likely maps onto the same concepts or symbols in this tree.

## Risks
This file is concurrency and lifetime sensitive. Page installation races are handled with release/acquire stores and `-EBUSY` lookup, while VMA close races are handled through `mapped`. Buffer coalescing must account for pages shared by adjacent buffers or pages can be reclaimed while still active. `check_buffer` is the boundary against invalid kernel copies. Shrinker lock ordering and VMA lifetime are the highest runtime-risk areas, and build coverage should catch API drift in mm, shrinker, and KUnit-export helpers.

## Test Signals
Run `binder_alloc` KUnit, especially exhaustive allocation/free/page-LRU cases; test mmap single-use behavior, invalid size overflow, async allocation exhaustion and spam detection, `TF_CLEAR_BUF` zeroing, shrinker reclaim under memory pressure, VMA close races, fd/object payload copy bounds, and debugfs page/buffer accounting. Build checks should catch the duplicate-source anomalies noted above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder_alloc.h -->
# sources/distributed-fs/ceph-client/drivers/android/binder_alloc.h

## Purpose
`binder_alloc.h` declares the Binder allocator data model and public C API. It is the contract between the Binder core and `binder_alloc.c` for transaction buffer allocation, mmap initialization, freeing, copying, debug reporting, shrinker setup, and KUnit-only introspection.

## Important APIs, Types, And Functions
`struct binder_buffer` describes one transaction buffer with list/rb-tree membership, free/clear/user-free/async/spam flags, debug ID, transaction/node pointers, sizes, user address, and pid. `struct binder_shrinker_mdata` stores per-page LRU metadata and the owning allocator/page index. `struct binder_alloc` stores allocator-wide mutex, mm, VMA start, buffer lists and rb trees, free async space, page array, LRU, buffer size, pid, pages high watermark, mapped flag, and spam state. Public prototypes cover allocation/free, mmap, deferred release, vma close, shrinker lifecycle, debug printing, allocated count, user/kernel copy helpers, and `binder_alloc_get_free_async_space`.

## Control Flow
The header has only inline helpers and declarations. `page_to_lru` converts a page's private metadata to its LRU node. `binder_alloc_get_free_async_space` locks the allocator mutex and returns the async-space counter. Callers follow the lifecycle: `binder_alloc_init`, `binder_alloc_mmap_handler`, repeated `binder_alloc_new_buf` and free/copy operations, `binder_alloc_vma_close`, then `binder_alloc_deferred_release`.

## State And Persistence
The header defines the persistent allocator state held per Binder process and per buffer. `mapped` is specifically documented as a lifetime gate: each Binder instance gets a single mapping. The page array and LRU metadata persist until deferred release or shrinker reclaim.

## Dependencies
It includes Linux rb-tree, list, mm, rtmutex, vmalloc, slab, list_lru, and Binder UAPI headers. It forward-declares `struct binder_transaction` and exposes KUnit-only helpers when `CONFIG_KUNIT` is enabled.

## Integration Points
`binder_internal.h` embeds `struct binder_alloc` in `struct binder_proc`; Binder transaction code uses `struct binder_buffer`; binderfs/debugfs reporting can call print helpers; KUnit tests include this header directly to verify internal allocation behavior.

## Risks
Because this header exposes struct layouts, any field change is cross-module ABI inside the kernel driver. Bitfield flags in `binder_buffer` control security-sensitive free and zeroing behavior. The inline async-space accessor assumes the mutex is sufficient and should not be used in interrupt contexts. `page_to_lru` trusts `page_private` to contain valid Binder shrinker metadata.

## Test Signals
Compile all Binder objects and KUnit tests after layout changes, run allocator KUnit, verify debugfs output still compiles, test async-space queries under allocation/free churn, and use sparse/lockdep to catch misuse of exposed structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder_alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder_internal.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder_netlink.c -->
# sources/distributed-fs/ceph-client/drivers/android/binder_netlink.c

## Purpose
`binder_netlink.c` is the generated generic-netlink family definition for Binder netlink reporting. It declares Binder's multicast report group and registers the family metadata consumed by generic netlink.

## Important APIs, Types, And Functions
The file defines an empty `binder_nl_ops` split-ops table, `binder_nl_mcgrps` with `BINDER_NLGRP_REPORT` named `"report"`, and the exported `struct genl_family binder_nl_family` marked `__ro_after_init`. Family fields include name, version, net namespace support, parallel ops, module owner, split ops, and multicast groups.

## Control Flow
There are no handlers in the ops table, so this file does not process requests. Runtime use is family registration by Binder/netlink init code elsewhere and multicast publication by Binder reporting code through the family/group.

## State And Persistence
The family descriptor persists after init as read-only metadata. The multicast group definition is static. No dynamic per-socket or per-message state is owned here.

## Dependencies
The file depends on Linux generic netlink headers, `binder_netlink.h`, and the UAPI-generated Binder netlink constants from `uapi/linux/android/binder_netlink.h`. It is generated from `Documentation/netlink/specs/binder.yaml`.

## Integration Points
Binder transaction-report features and trace/report paths can use this family to notify userspace subscribers. `binderfs.c` exposes a `transaction_report` feature flag, and `binder_trace.h` has a `binder_netlink_report` trace event for related observability.

## Risks
Generated files should not be manually edited because YAML regeneration can overwrite changes. An empty ops table is correct for multicast-only reporting, but consumers expecting request/reply commands would find none. Family name/version drift with UAPI headers would break userspace discovery.

## Test Signals
Build with Binder netlink enabled, verify generic-netlink family discovery, subscribe to the `report` multicast group, trigger Binder report events, and compare generated C/header content against the YAML spec regeneration output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder_netlink.h -->
# sources/distributed-fs/ceph-client/drivers/android/binder_netlink.h

## Purpose
`binder_netlink.h` is the generated kernel-side header for Binder generic netlink support. It exposes the multicast group enum and the Binder generic-netlink family object.

## Important APIs, Types, And Functions
The header includes netlink and generic-netlink kernel headers plus the Binder netlink UAPI header. It defines enum value `BINDER_NLGRP_REPORT` and declares `extern struct genl_family binder_nl_family`.

## Control Flow
The header has no executable flow. Binder netlink implementation and registration code include it to reference the family and report group.

## State And Persistence
No state is stored here. The declared family is defined in `binder_netlink.c` and persists after registration.

## Dependencies
It depends on generated UAPI definitions from `uapi/linux/android/binder_netlink.h` and on generic netlink infrastructure. The comment states it is generated from `Documentation/netlink/specs/binder.yaml`.

## Integration Points
Consumers use this header to register or send messages through Binder's generic-netlink family and report multicast group. It is part of the kernel/userspace reporting ABI.

## Risks
Manual edits can diverge from the YAML spec and UAPI header. Adding or renumbering groups is ABI-relevant for userspace subscribers. If included without generic-netlink support, configuration dependencies must ensure the required types are available.

## Test Signals
Regenerate from the YAML spec and diff, build Binder netlink users, inspect generic-netlink family/group IDs at runtime, and run userspace subscription tests for Binder reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder_trace.h -->
# sources/distributed-fs/ceph-client/drivers/android/binder_trace.h

## Purpose
`binder_trace.h` defines the Binder ftrace event surface for ioctl, read/write completion, waits, transactions, object/ref translation, fd transfer, buffer allocation/release, allocator page activity, commands/returns, and netlink reports.

## Important APIs, Types, And Functions
The file declares `TRACE_SYSTEM binder`, forward-declares Binder structs, and defines many `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT` entries. Major groups are `binder_ioctl`, function return events, `binder_wait_for_work`, transaction latency/free and send/receive events, node/ref translation events, fd send/recv events, buffer lifecycle events, page LRU/map/unmap events, `binder_command`, `binder_return`, and `binder_netlink_report`.

## Control Flow
The header expands into tracepoint definitions through `<trace/define_trace.h>`. Runtime Binder code calls `trace_binder_*` functions generated from this file. When tracing is disabled, event overhead is minimal; when enabled, fast-assign blocks read Binder struct fields and publish formatted event data.

## State And Persistence
Trace events do not own Binder state. They snapshot selected fields into the tracing ring buffer. Event definitions are compile-time ABI for tracing tools and persist as kernel tracepoint names and field layouts.

## Dependencies
It depends on Linux tracepoint infrastructure, Binder UAPI command/return string arrays, and stable field names in `struct binder_buffer`, `binder_alloc`, `binder_node`, `binder_ref_data`, `binder_proc`, `binder_thread`, and `binder_transaction`.

## Integration Points
`binder_alloc.c` emits page and buffer events. C Binder core and Rust Binder wrappers emit ioctl, command, return, wait, transaction, and fd events. Observability tools under ftrace/perf/tracefs consume the event schema.

## Risks
Tracepoint fast-assign code dereferences Binder structs, so layout changes must update event definitions. Rust Binder has a separate transaction representation and uses generated layout metadata; mismatches are risky. Trace fields are user-visible diagnostic ABI in practice, so renaming/removing events can break tooling. Netlink report trace fields assume C `binder_transaction` members such as `to_proc` and `to_thread`.

## Test Signals
Compile with tracing enabled, list `binder:*` events in tracefs, enable transaction/buffer/page events during Binder IPC stress, verify event field values against Binder debug logs, run allocator KUnit with page tracepoints enabled, and test Rust Binder trace wrapper build compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binderfs.c -->
# sources/distributed-fs/ceph-client/drivers/android/binderfs.c

## Purpose
`binderfs.c` implements the Binder filesystem. It provides mount-time Binder device namespaces, a `binder-control` device for dynamic Binder device creation, feature files, optional Binder log files, mount options, minor allocation, and filesystem registration.

## Important APIs, Types, And Functions
Important functions include `init_binderfs`, `binderfs_init_fs_context`, `binderfs_fill_super`, `binderfs_binder_ctl_create`, `binder_ctl_ioctl`, `binderfs_binder_device_create`, `binderfs_evict_inode`, `binderfs_create_file`, `binderfs_create_dir`, `init_binder_features`, `init_binder_logs`, `binderfs_show_options`, `binderfs_fs_context_parse_param`, `binderfs_fs_context_reconfigure`, `binderfs_rename`, `binderfs_unlink`, and `binderfs_kill_super`. Static state includes `binderfs_dev`, `binderfs_minors_mutex`, `binderfs_minors`, mount parameter tables, and feature booleans.

## Control Flow
`init_binderfs` validates default device names, allocates a character-device major, and registers the filesystem. Mounting allocates fs context options, parses `max` and `stats=global`, then `binderfs_fill_super` sets superblock flags, creates root inode, creates `binder-control`, creates default devices from `binder_devices_param`, creates feature files, and optionally creates binder log files. Userspace calls `BINDER_CTL_ADD` on `binder-control` to copy in a `binderfs_device`, allocate a global minor, create a character-device inode/dentry, attach a `binder_device`, copy major/minor back, and add it to Binder's global device list. Eviction frees minors and device state.

## State And Persistence
Per-mount state lives in `struct binderfs_info`: ipc namespace, control dentry, root uid/gid, mount options, device count, and proc log directory. Global minor allocation persists in the IDA. Each device stores `struct binder_device` in inode private data. Feature files expose static booleans. Mount options persist for the superblock, and stats mode cannot be changed on remount.

## Dependencies
The file depends on VFS/simplefs helpers, fs parser, IDA, ipc/user namespaces, char device registration, Binder UAPI, and `binder_internal.h`. It calls `binder_add_device`, `binder_remove_device`, and uses `binder_fops` from Binder core.

## Integration Points
Android userspace mounts binderfs to get Binder device nodes. Binder core opens device nodes created here and uses their `binder_context`. Binder debugfs entries can be mirrored under `binder_logs` when global stats are requested. Feature files advertise support for oneway spam detection, extended errors, freeze notifications, and transaction reports.

## Risks
Minor accounting and device_count must stay balanced across create, ioctl copy failure, dentry creation failure, and inode eviction. User namespace mounting depends on careful device-node restrictions. Default device-name parsing must reject names longer than `BINDERFS_MAX_NAME`. Feature-file creation and inode eviction deserve build, mount, and lockdep coverage because small mistakes there can hide advertised features or leak minors.

## Test Signals
Mount binderfs in initial and non-initial user namespaces, use `BINDER_CTL_ADD`, verify max-device limits and minor reserve behavior, rename/unlink normal devices while protecting `binder-control`, read feature files, mount with and without `stats=global`, exercise default device creation from `binder_devices_param`, unmount under open devices, and run build/lockdep checks for the duplicate-lock anomaly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binderfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/dbitmap.h -->
# sources/distributed-fs/ceph-client/drivers/android/dbitmap.h

## Purpose
`dbitmap.h` provides a small dynamically sized bitmap library used by Binder to allocate the smallest available descriptor ID efficiently while allowing growth and shrink decisions to be made outside locks.

## Important APIs, Types, And Functions
`struct dbitmap` stores `nbits` and `map`. Inline APIs are `dbitmap_enabled`, `dbitmap_free`, `dbitmap_shrink_nbits`, `dbitmap_replace`, `dbitmap_shrink`, `dbitmap_grow_nbits`, `dbitmap_grow`, `dbitmap_acquire_next_zero_bit`, `dbitmap_clear_bit`, and `dbitmap_init`. `NBITS_MIN` is one unsigned long worth of bits.

## Control Flow
Users initialize with `dbitmap_init`, acquire descriptor IDs with `dbitmap_acquire_next_zero_bit`, clear IDs with `dbitmap_clear_bit`, and periodically ask whether grow or shrink is needed. Grow/shrink helpers revalidate the requested size because callers may allocate replacement memory after dropping locks. If growth remains needed but allocation failed, `dbitmap_grow` disables the dynamic bitmap so Binder can fall back to a slower descriptor lookup path.

## State And Persistence
The bitmap persists as heap memory referenced by `map`. `nbits == 0` means disabled. Set bits represent allocated IDs. Shrink can reduce the allocation when the highest set bit is in the first quarter, or to `NBITS_MIN` when no bits are set.

## Dependencies
The header depends on Linux bitmap helpers and kernel allocation/free APIs. It intentionally provides no internal locking; Binder protects it with `proc->outer_lock` according to the file comment and `binder_proc` documentation.

## Integration Points
`binder_internal.h` embeds `struct dbitmap dmap` in `struct binder_proc` for reference descriptor management. Binder reference creation/removal code can use it to find free handle IDs faster than rb-tree scans.

## Risks
Callers must hold the right lock around all bitmap state access. Revalidation protects against stale out-of-lock allocation decisions, but callers must pass the exact nbits returned by `dbitmap_*_nbits`. Disabling on grow allocation failure changes performance behavior and requires fallback code to remain correct.

## Test Signals
Unit tests should cover init/free, acquire until `-ENOSPC`, clear/reacquire lowest IDs, grow with stale and valid nbits, grow allocation failure disabling, shrink thresholds, all-clear shrink to minimum, and concurrent-pattern tests under the Binder outer lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/dbitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/tests/Makefile -->
# sources/distributed-fs/ceph-client/drivers/android/tests/Makefile

## Purpose
This Makefile wires the Android Binder allocator KUnit test object into the kernel build.

## Important APIs, Types, And Functions
The only build rule is `obj-$(CONFIG_ANDROID_BINDER_ALLOC_KUNIT_TEST) += binder_alloc_kunit.o`. There are no functions or runtime types.

## Control Flow
Kbuild includes `binder_alloc_kunit.o` only when `CONFIG_ANDROID_BINDER_ALLOC_KUNIT_TEST` is enabled. Otherwise the tests are absent from the build.

## State And Persistence
No runtime state exists. The file controls build graph membership.

## Dependencies
It depends on Kbuild, the config symbol `ANDROID_BINDER_ALLOC_KUNIT_TEST`, and the adjacent `binder_alloc_kunit.c` source.

## Integration Points
The rule integrates Binder allocator tests with the kernel KUnit build and module/test discovery. It is the entry point for building the exhaustive allocator page-LRU tests.

## Risks
If the config symbol changes or the object name drifts, allocator tests silently stop building. The Makefile does not list additional objects, so all required test imports must come from exported Binder symbols and normal kernel links.

## Test Signals
Enable `CONFIG_ANDROID_BINDER_ALLOC_KUNIT_TEST`, run the KUnit suite named `binder_alloc`, and verify `binder_alloc_kunit.o` appears in the build output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/tests/binder_alloc_kunit.c -->
# sources/distributed-fs/ceph-client/drivers/android/tests/binder_alloc_kunit.c

## Purpose
`binder_alloc_kunit.c` is a KUnit suite for Binder allocator page allocation, LRU, free, and reclaim behavior. It exhaustively generates buffer alignment and free-order cases to verify that pages shared across adjacent buffers are placed on or removed from the LRU correctly.

## Important APIs, Types, And Functions
Important definitions include `BINDER_MMAP_SIZE`, `BUFFER_NUM`, `BUFFER_MIN_SIZE`, `TOTAL_EXHAUSTIVE_CASES`, `enum buf_end_align_type`, `struct binder_alloc_test_case_info`, and `struct binder_alloc_test`. Helpers include stringification functions, `check_buffer_pages_allocated`, allocation/free/reclaim helpers, `binder_alloc_test_alloc_free`, `permute_frees`, `gen_buf_sizes`, and `gen_buf_offsets`. Test cases are `binder_alloc_test_init_freelist`, `binder_alloc_test_mmap`, and slow `binder_alloc_exhaustive_test`. Fixture functions are `binder_alloc_test_init` and `binder_alloc_test_exit`.

## Control Flow
The fixture creates a private `binder_alloc`, initializes a test `list_lru`, attaches an mm, opens an anonymous inode with an mmap handler, and maps 128 KiB of Binder transaction memory. The exhaustive test generates five-buffer end alignments, tests front-page and back-page sharing arrangements, permutes all free orders, allocates buffers, frees them, verifies expected LRU pages, reallocates from LRU, verifies the LRU drains, frees again, then walks the LRU through `binder_alloc_free_page` until all pages are reclaimed.

## State And Persistence
Per-test state holds allocator state, test LRU, backing file, and mmap address. The allocator's page array, rb trees, and LRU are mutated heavily during each generated case and cleaned up in the fixture exit. The test attaches an mm so allocator mmap and shrinker paths can operate like normal Binder usage.

## Dependencies
The test depends on KUnit, anon inodes, file/mm helpers, seq_buf, `binder_alloc.h`, `binder_internal.h`, and KUnit-exported Binder symbols such as `__binder_alloc_init`, `binder_alloc_buffer_size`, `binder_alloc_new_buf`, `binder_alloc_free_buf`, `binder_alloc_free_page`, and `binder_vm_fault`.

## Integration Points
The Makefile includes this object under `CONFIG_ANDROID_BINDER_ALLOC_KUNIT_TEST`. It directly exercises `binder_alloc.c` internals and is the strongest regression signal for the allocator's page sharing and shrinker logic.

## Risks
The exhaustive suite is intentionally slow: 3125 alignment combinations times two placement modes times 120 free orders. The test focuses on page/LRU behavior and does not cover all allocator security properties, async spam accounting, or user copy bounds. It also depends on KUnit-exported internal symbols, so namespace/export drift can break the suite even when allocator runtime code still builds.

## Test Signals
Run the `binder_alloc` KUnit suite, confirm `TOTAL_EXHAUSTIVE_CASES` runs, zero failures, no leaked LRU items at exit, no installed pages after reclaim, successful mmap initialization, and clean build with `MODULE_IMPORT_NS("EXPORTED_FOR_KUNIT_TESTING")`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/tests/binder_alloc_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ata/Kconfig

## Purpose
`drivers/ata/Kconfig` defines the kernel configuration menu for libata, SATA, PATA, AHCI, SFF, platform, DMA, ACPI, and legacy ATA drivers. It controls which ATA subsystems and host drivers can be built and which dependencies/selects are applied.

## Important APIs, Types, And Functions
This is Kconfig, not C. Key symbols include `ATA`, `SATA_HOST`, `ATA_SFF`, `ATA_BMDMA`, `PATA_TIMINGS`, `ATA_VERBOSE_ERROR`, `ATA_FORCE`, `ATA_ACPI`, `SATA_ZPODD`, `SATA_PMP`, AHCI host drivers such as `SATA_AHCI`, `SATA_ACARD_AHCI`, and many platform/SFF/PATA driver symbols. `SATA_ACARD_AHCI` is the symbol that builds `acard-ahci.o`.

## Control Flow
Kconfig control flow gates symbols under `if ATA`, `if HAS_DMA`, `if ATA_SFF`, and `if ATA_BMDMA`. Selecting `ATA` pulls in SCSI and GLOB. Driver symbols express dependencies such as PCI, OF, architecture, DMA, or `COMPILE_TEST`, and many select `SATA_HOST`, `PATA_TIMINGS`, or helper subsystems.

## State And Persistence
The persistent output is the kernel `.config`. Those config choices control built-in versus module behavior and which Makefile `obj-*` entries are active.

## Dependencies
Kconfig depends on global kernel symbols such as `HAS_IOMEM`, `BLOCK`, `SCSI`, `HAS_DMA`, `PCI`, `ACPI`, `PM`, architecture symbols, `OF`, `DMADEVICES`, `HAS_IOPORT`, and many SoC-specific symbols.

## Integration Points
`drivers/ata/Makefile` consumes these config symbols to build libata and individual drivers. Users, distro configs, and defconfigs select options here to enable storage hardware. The ACard AHCI driver is enabled by `CONFIG_SATA_ACARD_AHCI`, depends on PCI, and selects `SATA_HOST`.

## Risks
Dependency mistakes can expose drivers on unsupported architectures or hide valid hardware. Overbroad `select` usage can force helper subsystems without their dependencies. Because `ATA` selects SCSI, disabling ATA can remove disk access on systems depending on libata. Experimental or legacy drivers need careful dependency gating around IO port, DMA, and architecture assumptions.

## Test Signals
Run `make olddefconfig`/`allnoconfig`/`allyesconfig`/`randconfig`, verify no unmet dependency warnings, build representative AHCI/PATA configs, confirm `CONFIG_SATA_ACARD_AHCI=m/y` builds `acard-ahci.o`, and boot-test storage discovery on supported hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ata/Makefile

## Purpose
`drivers/ata/Makefile` maps ATA Kconfig symbols to built objects and defines the composed `libata.o` object. It is the build graph for libata core, SATA/AHCI, SFF, PATA, platform, fallback, and legacy ATA drivers.

## Important APIs, Types, And Functions
There are no runtime APIs. Important build entries include `obj-$(CONFIG_ATA) += libata.o`, `obj-$(CONFIG_SATA_AHCI) += ahci.o libahci.o`, `obj-$(CONFIG_SATA_ACARD_AHCI) += acard-ahci.o libahci.o`, many platform AHCI entries with `libahci_platform.o`, numerous SFF/PATA driver objects, and `libata-y` composition from `libata-core.o`, `libata-scsi.o`, `libata-eh.o`, `libata-transport.o`, and `libata-trace.o`. Conditional `libata-*` entries add SATA, SFF, PMP, ACPI, ZPODD, and PATA timing support.

## Control Flow
Kbuild expands active `obj-*` lines based on `.config`. Some drivers share helper objects, so enabling multiple AHCI drivers can include `libahci.o` through multiple entries as Kbuild resolves composite objects. `libata.o` is built from its core list plus conditional helper objects.

## State And Persistence
No runtime state exists. Build outputs persist as built-in objects or modules according to config choices.

## Dependencies
The Makefile depends on config symbols defined in `Kconfig`, Kbuild object semantics, and source files in the same directory and `pata_parport/` subdirectory.

## Integration Points
The file is consumed by the kernel build when entering `drivers/ata`. It directly links `acard-ahci.c` to `CONFIG_SATA_ACARD_AHCI` and `libahci.o`, tying the ACard variant to shared AHCI support.

## Risks
Object/config drift can cause a driver to be selectable but not built, or built without required helper objects. Ordering comments for generic fallback and legacy drivers matter because driver probe order can affect hardware binding. Shared helper objects must remain compatible with all drivers that include them.

## Test Signals
Build with focused configs for `CONFIG_ATA`, `CONFIG_SATA_ACARD_AHCI`, platform AHCI, SFF PATA, and fallback drivers; inspect `modules.order` or built-in object lists; run `make W=1 drivers/ata/`; and test module load/probe order for fallback drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/acard-ahci.c -->
# sources/distributed-fs/ceph-client/drivers/ata/acard-ahci.c

## Purpose
`acard-ahci.c` is a libata low-level PCI driver for the ACard/ARTOP ATP8620 AHCI SATA variant. It reuses the common AHCI implementation but overrides command preparation, result taskfile extraction, and port start behavior for ACard-specific FIS and scatter-gather quirks.

## Important APIs, Types, And Functions
Important definitions include `DRV_NAME`, `DRV_VERSION`, `ACARD_AHCI_RX_FIS_SZ`, `AHCI_PCI_BAR`, `board_acard_ahci`, and `struct acard_sg`. Driver objects include `acard_ahci_sht`, `acard_ops`, `acard_ahci_port_info`, `acard_ahci_pci_tbl`, and `acard_ahci_pci_driver`. Key functions are `acard_ahci_qc_prep`, `acard_ahci_qc_fill_rtf`, `acard_ahci_port_start`, `acard_ahci_init_one`, suspend/resume handlers under `CONFIG_PM_SLEEP`, `acard_ahci_pci_print_info`, and `acard_ahci_fill_sg`.

## Control Flow
PCI probe enables the device, requests regions, allocates AHCI private data, optionally enables MSI, maps BAR 5, saves initial AHCI config, sets NCQ/PMP flags based on capabilities, allocates an ATA host, marks disabled ports dummy, configures DMA mask, resets and initializes the controller, prints controller info, sets bus master, and activates the host. Command prep builds the command table FIS, copies ATAPI CDBs, fills the ACard SG table for DMA, sets AHCI command slot flags, and returns `AC_ERR_OK`. Result taskfile handling uses PIO Setup FIS for successful PIO data-in commands and D2H Reg FIS otherwise. Port start allocates coherent DMA memory with an ACard 128-byte received-FIS stride and resumes the port.

## State And Persistence
Persistent driver state is stored in `ahci_host_priv` for the host and `ahci_port_priv` for each port. Coherent DMA memory stores command slots, received FIS area, and command tables. PCI driver registration persists for module lifetime. The SG table is per command.

## Dependencies
The driver depends on PCI, DMA mapping, libata, SCSI host templates, AHCI shared helpers from `ahci.h`/`libahci.o`, optional power management, and the `CONFIG_SATA_ACARD_AHCI` Kconfig/Makefile entries.

## Integration Points
It inherits most operations from `ahci_ops` and overrides only the ACard-specific pieces. It binds to `PCI_VDEVICE(ARTOP, 0x000d)`, exports module PCI IDs, and participates in libata scanning, error handling, power management, and SCSI presentation.

## Risks
ACard SG entries require an end-of-table bit and maximum 64 KiB segment size; if the DMA mapping layer supplies larger segments without splitting, hardware may misinterpret descriptors. The driver disables NCQ through `AHCI_HFLAG_NO_NCQ`, so enabling NCQ accidentally could expose unsupported behavior. FIS stride differs from standard AHCI, especially with FBS. Suspend/resume must disable interrupts before D3 and reinitialize controller state correctly.

## Test Signals
Build with `CONFIG_SATA_ACARD_AHCI`, confirm module PCI alias for ARTOP 0x000d, probe on ATP8620 hardware, run SATA disk discovery and I/O stress, test ATAPI and PIO data-in result taskfile paths, verify DMA across multi-segment SG lists, suspend/resume cycles, PMP/FBS behavior where supported, and libata error handling after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/acard-ahci.c -->
