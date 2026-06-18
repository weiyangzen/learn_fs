# Research: subset-b-001031

Grouped research for the Rust Binder process, node, freeze, mmap-page, range allocator, binderfs, tracepoint, and stats implementation under the Ceph client source mirror.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/freeze.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/freeze.rs

Purpose: implements Binder freeze notification support for the Rust Binder driver. It lets one process register interest in freeze-state changes for a remote binder node, receive `BR_FROZEN_BINDER`, acknowledge notifications with `BC_FREEZE_NOTIFICATION_DONE`, and clear listeners with `BC_CLEAR_FREEZE_NOTIFICATION`.

Important APIs/types/functions: `FreezeCookie` is the ordered key for listener lookup. `FreezeListener` records the watched `Node`, cookie, last reported frozen state, pending/clearing flags, and duplicate listener counts. `FreezeMessage` is a `DeliverToRead` work item that writes freeze or clear-complete replies. `Process::request_freeze_notif`, `freeze_notif_done`, `clear_freeze_notif`, `prepare_freeze_messages`, and `find_freeze_recipients` are the main entry points. `FreezeMessages::send_messages` batches cross-process work delivery.

Control flow: registration reads a `BinderHandleCookie`, validates the handle, reserves an RBTree node and message allocation, adds the listening process to the target node's freeze list, installs or updates the cookie entry, and queues an initial `FreezeMessage`. Message delivery checks duplicate-clear counters first, suppresses duplicate frozen states, marks notifications pending, and emits either `BR_FROZEN_BINDER` with `BinderFrozenStateInfo` or `BR_CLEAR_FREEZE_NOTIFICATION_DONE`. Freeze completion either drains pending duplicates or queues another message when the clear state or frozen state changed while userspace was processing the previous notification.

State and persistence: listener state is held in `ProcessNodeRefs.freeze_listeners`, per-handle cookies live in `NodeRefInfo.freeze`, and target nodes keep an owner-lock-protected `freeze_list` of listening processes. This is volatile per-open Binder fd state, cleaned on process exit by `FreezeListener::on_process_exit` and process release.

Dependencies and integration points: depends on `Process`, `Node`, `Thread`, Binder UAPI structs/constants, kernel `RBTree`, `ListArc`, `UniqueArc`, and the shared `DeliverToRead` queueing model. `process.rs` invokes `prepare_freeze_messages` during `BINDER_FREEZE` transitions and `Node` supplies add/remove/list APIs.

Risks: duplicate cookie handling is subtle because userspace can clear and recreate a listener before acknowledgements arrive. Lock ordering crosses `node_refs` mutex and node owner spinlocks; new code must avoid adding reverse acquisitions. Allocation failures are deliberately pushed before state mutation during registration, but later notification batching can race with listener removal and must tolerate dropped notifications.

Test signals: exercise request, duplicate request, clear, done-before-clear, clear-before-done, process-exit cleanup, and freeze/unfreeze transitions across multiple binder contexts. Debug logs should not show invalid-cookie warnings in valid flows, and userspace should receive at most one state change until it sends the corresponding done command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/freeze.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/node.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/node.rs

Purpose: defines Binder nodes, local references to remote nodes, death notifications, reference-count work delivery, and oneway transaction serialization. A `Node` represents a userspace Binder object owned by one `Process`; `NodeRef` and `NodeRefInfo` model handles held by other processes.

Important APIs/types/functions: `DeliveryState` tracks whether a node or wrapper is scheduled and whether pending work is weak or strong zero-to-one refcount work. `NodeInner` stores strong/weak `CountState`, oneway queues, death listeners, freeze listeners, active inc refs, and reverse ref lists. `Node::new`, `update_refcount_locked`, `incr_refcount_allow_zero2one`, `do_work_locked`, `submit_oneway`, `pending_oneway_finished`, `release`, freeze-list helpers, and debug helpers are central. `NodeRef` owns counted node refs and updates remote counts in `Drop`. `NodeDeath` implements `BR_DEAD_BINDER` and clear-complete delivery.

Control flow: refcount updates mutate owner-process state under `ProcessInner`; zero-to-one increments may schedule the node or a wrapper so userspace receives `BR_INCREFS`/`BR_ACQUIRE`. `do_work_locked` compares Rust-side counts with userspace-visible `has_count` flags, emits increment or decrement commands, and removes nodes with no remaining weak reachability. Oneway transactions are serialized by `has_oneway_transaction`: the first is delivered, later ones wait in `oneway_todo` until buffer free completion calls `pending_oneway_finished`. Death registration stores `NodeDeath` objects on the target node; node release marks them dead and queues notifications to listeners.

State and persistence: node state is volatile and lock-coupled to its owner process. It persists while the owner has a node mapping or foreign refs/death/freeze listeners exist. `refs` links enable cleanup from both owning and referencing processes; release cancels queued oneway work and wakes death listeners.

Dependencies and integration points: integrates with `process.rs` handle tables, `thread.rs` work delivery, `transaction.rs` oneway transactions, `freeze.rs` listener enumeration, and C trace layout via `NODE_LAYOUT`. It relies heavily on kernel Rust `ListArc`, `LockedBy`, `SpinLock`, `AtomicTracker`, and Binder UAPI return codes.

Risks: refcount sequencing is the highest-risk area; `active_inc_refs` intentionally delays decrements to avoid userspace-visible reordering. Incorrect delivery-state changes can lose critical zero-to-one notifications or deliver them to the wrong thread. Oneway serialization can deadlock or reorder if buffer-free signaling is missed. Unsafe list removals rely on invariants that each object is linked only into its documented owner list.

Test signals: stress strong/weak acquire/release, cross-thread zero-to-one races, manager node refs, process death with active death notifications, oneway ordering, transaction replacement, and freeze listeners. Debug output should show balanced `hs/hw/cs/cw` counts and no refcount underflow or duplicate list warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/node/wrapper.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/node/wrapper.rs

Purpose: provides `CritIncrWrapper`, a small work-item wrapper used when a strong zero-to-one node refcount increment cannot be safely represented by scheduling the `Node` itself. It preserves Binder's requirement that critical acquire notifications reach the thread that caused them.

Important APIs/types/functions: `CritIncrWrapper::new` preallocates uninitialized storage for `DTRWrap<NodeWrapper>`. `CritIncrWrapper::init` pins a `NodeWrapper` around a `DArc<Node>` and returns it as `DLArc<dyn DeliverToRead>`. `NodeWrapper` implements `DeliverToRead` with `do_work`, `cancel`, `should_sync_wakeup`, and `debug_print`.

Control flow: `process.rs` allocates a wrapper after `Node::incr_refcount_allow_zero2one` reports `CouldNotDeliverCriticalIncrement`. On delivery, `NodeWrapper::do_work` locks the node owner process, asserts wrapper/strong-zero2one state, clears the wrapper scheduling flags, and delegates to `Node::do_work_locked` to write the actual Binder return commands.

State and persistence: the wrapper owns only an arc to the target node and exists while queued on a thread or process work list. Persistent scheduling state remains in `NodeInner.delivery_state`; the wrapper is the transport used to disambiguate one pending strong increment from other node work.

Dependencies and integration points: depends on `node.rs` private delivery-state access, `Thread`, `BinderReturnWriter`, `DTRWrap`, `ListArc`, and `UniqueArc`. It is intentionally internal to the `node` module and exported as `CritIncrWrapper`.

Risks: the asserts in `do_work` encode critical invariants; a wrapper queued without `has_pushed_wrapper` and `has_strong_zero2one` indicates corrupted scheduling state. If wrapper allocation fails, the higher-level refcount path returns allocation failure to avoid losing a required acquire notification.

Test signals: force concurrent weak and strong zero-to-one increments so the normal node delivery path is already occupied, then verify a wrapper is used and `BR_ACQUIRE` reaches the initiating thread. Invalid double scheduling should surface as assertion or warning failures in debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/node/wrapper.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/page_range.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/page_range.rs

Purpose: manages a Binder mmap page range whose unused pages can be reclaimed by a kernel shrinker. It backs transaction buffers with lazily allocated pages, maps them into the owning process, and moves freed pages to an LRU for memory pressure reclamation.

Important APIs/types/functions: `Shrinker` wraps a C shrinker pointer and `list_lru`; `register` initializes callbacks. `ShrinkablePageRange` owns the process `Mm`, mmap synchronization mutex, spinlocked `Inner`, and pinned page metadata. `register_with_vma`, `use_range`, `use_page_slow`, `stop_using_range`, `copy_from_user_slice`, `read`, `write`, and `fill_zero` are the main Rust APIs. C callbacks are `rust_shrink_count`, `rust_shrink_scan`, and `rust_shrink_free_page`.

Control flow: `register_with_vma` validates the mm, allocates `PageInfo` entries, records VMA address, and tags the VMA with Binder-specific `vm_ops` and private data. `use_range` removes existing pages from LRU or allocates through `use_page_slow`, which takes `mm_lock`, inserts a zeroed highmem page into the VMA, then stores it under the spinlock. `stop_using_range` puts fully unused pages on the LRU. The shrinker walks the LRU, trylocks locks in shrinker-safe order, isolates a page, removes it from the array, drops the LRU lock, zaps the user mapping, and drops the page.

State and persistence: page state is an array of `PageInfo` values with three states: free, available-on-LRU, and used. The array is installed once per mmap and destroyed with the process. Pages persist while allocated but may be reclaimed whenever marked available.

Dependencies and integration points: used by `Process::create_mapping`, `buffer_alloc`, and `buffer_raw_free`. Depends on kernel Rust MM/VMA wrappers, `Page`, list LRU C APIs, Binder module-global `BINDER_SHRINKER`, and `AssertSync` for static `vm_operations_struct`.

Risks: lock ordering is explicit and fragile: mmap lock, spinlock, then LRU spinlock, while shrinker paths use trylocks to avoid inversion. `iterate` uses raw page pointers after dropping the spinlock and is safe only when callers guarantee pages are in use. VMA identity checks are essential to avoid mapping or zapping the wrong address range.

Test signals: mmap size validation, concurrent transactions allocating the same page, buffer free followed by shrinker reclaim, mm teardown races, and copy/read/write across page boundaries. Failures should not produce "Page is null" warnings or stale user mappings after shrinker eviction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/page_range.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/process.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/process.rs

Purpose: implements the Binder per-open-file process object. It owns process-local threads, nodes, handle tables, mmap buffer allocator, pending work queues, deferred release/flush work, freeze state, Binder stats, and binderfs proc-log file lifetime.

Important APIs/types/functions: `ProcessInner` is the spinlock-protected core state. `ProcessNodeRefs` maps handles to `NodeRefInfo`, node global ids to handles, and freeze cookies to listeners. `Process::open`, `release`, `flush`, `ioctl`, `mmap`, and `poll` are file-operation entry points. Important internal methods include `get_current_thread`, `push_work`, `get_node`, `insert_or_update_handle`, `update_ref`, `buffer_alloc`, `buffer_get`, `buffer_raw_free`, death/freeze notification methods, `ioctl_freeze`, and `deferred_release`.

Control flow: `open` creates and registers a `Process` in its `Context`; `rust_binder_open` stores its foreign arc in `file.private_data`. Ioctl dispatch splits write-only and read/write commands, obtains the calling `Thread`, and routes Binder commands, version/debug queries, freeze operations, and max-thread settings. Buffer allocation reserves an address range under `RangeAllocator`, then ensures pages exist in `ShrinkablePageRange`. Release is deferred to a workqueue: it marks the process dead, removes manager/context state, drops binderfs log files, releases threads and owned nodes, clears death/freeze listeners, cancels pending work, and drains allocated buffers.

State and persistence: all state is per Binder fd, not per Linux task globally. It persists from open until deferred release completes. `is_frozen`, `sync_recv`, `async_recv`, and `outstanding_txns` govern freeze behavior and wake waiters. `mapping` persists after mmap and is capped to 4 MiB.

Dependencies and integration points: ties together `Context`, `Thread`, `Node`, `TransactionInfo`, `Allocation`, `ShrinkablePageRange`, `RangeAllocator`, `BinderStats`, binderfs proc files, kernel file/mm/poll/uaccess APIs, workqueues, and Binder UAPI constants.

Risks: cleanup spans several lock domains and must avoid dropping transactions or nodes under locks that their destructors can reacquire. `WithNodes` temporarily moves the node tree out and detects illegal mutation on drop. Freeze waits depend on `outstanding_txns` and thread transaction stacks; missed decrements can keep freeze stuck. Handle id allocation must keep `IdPool`, `by_handle`, and `by_node` synchronized.

Test signals: Binder ioctl compatibility tests, open/release races, thread pool registration, manager election, mmap and buffer lifecycle, death/freeze notification sequences, process exit while transactions are pending, and debugfs/binderfs proc output. Runtime warnings for handle bitmap mismatch, outstanding underflow, duplicate ready-thread registration, or failed buffer free are strong bug signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/process.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/range_alloc/array.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/range_alloc/array.rs

Purpose: provides the small-allocation-count implementation of Binder mmap range allocation. It tracks only allocated or reserved ranges in a sorted array and is used until the descriptor count reaches `TREE_THRESHOLD`.

Important APIs/types/functions: `ArrayRangeAllocator<T>` stores sorted `Range<T>` descriptors, total size, and remaining async/oneway space. `FindEmptyRes` records insertion index and offset. Main methods are `new`, `is_full`, `reserve_new`, `reservation_abort`, `reservation_commit`, `reserve_existing`, `take_for_each`, `debug_print`, and `low_oneway_space`. `EmptyArrayAlloc` preallocates the descriptor vector.

Control flow: `reserve_new` checks async-space quota for oneway transactions, searches for a gap by appending after the last range or scanning preceding gaps, inserts a reserved descriptor within capacity, and reports oneway spam suspicion when free async space is low and the caller owns many buffers. `reservation_commit` changes a reserved descriptor into allocated and stores optional metadata. `reserve_existing` changes allocated back to reserved while returning size, debug id, and metadata. `reservation_abort` removes a still-reserved descriptor and computes which interior or boundary pages are no longer covered by neighboring ranges.

State and persistence: state is in the process `RangeAllocator` inside `ProcessInner.mapping`. Descriptors are volatile transaction-buffer state. `free_oneway_space` starts at half the mmap size and is decremented only for oneway reservations.

Dependencies and integration points: used by `range_alloc/mod.rs`, which supplies preallocation and switches to the tree allocator when full. It relies on `DescriptorState`, `FreedRange`, `Range`, `Pid`, page constants, `KVec`, and seq-file debugging.

Risks: linear scans are intentional for small counts but depend on sorted insertion. Page-free calculations around unaligned boundaries must remain synchronized with `ShrinkablePageRange::stop_using_range`; off-by-one errors could mark a page reclaimable while another allocation still overlaps it. `insert_within_capacity(...).unwrap()` is safe only because callers preallocate exactly the threshold capacity.

Test signals: allocate/free gaps at beginning, middle, and end; unaligned buffers sharing pages; transition from reserved to allocated and back; oneway quota exhaustion; spam detection after many same-pid async buffers; and migration to tree when `is_full` becomes true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/range_alloc/array.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/range_alloc/mod.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/range_alloc/mod.rs

Purpose: defines the common Binder transaction-buffer range allocator API and switches between empty, small-array, and RBTree-backed implementations. It also carries descriptor state and metadata for reserved versus allocated buffers.

Important APIs/types/functions: `DescriptorState<T>` is either `Reserved(Reservation)` or `Allocated(Allocation<T>)`. `Reservation` stores debug id, oneway flag, and sender pid; `Allocation<T>` stores committed metadata. `FreedRange` describes page indices that became fully free. `RangeAllocator<T>` exposes `new`, `reserve_new`, `reservation_abort`, `reservation_commit`, `reserve_existing`, `take_for_each`, `free_oneway_space`, `count_buffers`, and `debug_print`. `ReserveNewArgs`, `ReserveNew`, `ReserveNewSuccess`, and `ReserveNewNeedAlloc` implement lock-friendly preallocation.

Control flow: a new allocator starts as `Empty(size)`. First reservation asks the caller to allocate an `EmptyArrayAlloc`, then becomes `Array`. When the array is full, `reserve_new` asks for `FromArrayAllocs` and a tree reservation, converts the sorted array into `TreeRangeAllocator`, and retries. Tree reservations require the caller to provide `ReserveNewTreeAlloc` before the lock is held. Abort, commit, reserve-existing, and shutdown dispatch to the active implementation; an empty tree collapses back to `Empty`.

State and persistence: the allocator is stored per process mapping and tracks live Binder transaction buffers until committed/freeable or aborted. It persists only for the lifetime of the Binder mmap. Optional `T` metadata is stored in allocated descriptors and returned to callers when a userspace buffer is reused/freed.

Dependencies and integration points: consumed by `Process::buffer_alloc`, `buffer_get`, `buffer_raw_free`, `buffer_make_freeable`, and release cleanup. It depends on `array.rs`, `tree.rs`, `PAGE_SIZE`, `Pid`, and seq-file output.

Risks: the preallocation handshake must be followed exactly so no GFP allocations are needed while the process spinlock is held. Incorrect state transitions can leak metadata, double-free ranges, or free pages too early. The array-to-tree threshold is part of performance behavior and should be changed only with allocator tests.

Test signals: cover first allocation from empty, repeated `NeedAlloc` retry paths, array-to-tree conversion at eight descriptors, commit/reserve-existing/abort state errors, allocator collapse to empty, shutdown `take_for_each`, and preservation of `AllocationInfo` metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/range_alloc/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/range_alloc/tree.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/range_alloc/tree.rs

Purpose: implements the scalable RBTree-backed Binder mmap range allocator used after the small array fills. It stores both allocated descriptors and free descriptors, plus a second tree keyed by free-range size for best-fit allocation.

Important APIs/types/functions: `TreeRangeAllocator<T>` owns `tree: RBTree<offset, Descriptor<T>>`, `free_tree: RBTree<(size, offset), ()>`, total size, and `free_oneway_space`. `Descriptor<T>` carries offset, size, and optional `DescriptorState` plus a reserved free-tree node. `ReserveNewTreeAlloc` and `FromArrayAllocs` preallocate RBTree nodes. Main methods are `from_array`, `reserve_new`, `reservation_abort`, `reservation_commit`, `reserve_existing`, `take_for_each`, `is_empty`, and `low_oneway_space`.

Control flow: `from_array` drains sorted array descriptors, emits free descriptors for gaps, inserts allocated descriptors, and records every free range by `(size, offset)`. `reserve_new` finds the smallest free range at least as large as requested, removes it from `free_tree`, turns the front of that descriptor into a reserved allocation, and inserts a remainder descriptor when needed. `reservation_abort` validates that the descriptor is reserved, changes it to free, merges adjacent free descriptors, updates `free_tree`, and computes newly free page indices. Commit and reserve-existing change descriptor state without moving ranges.

State and persistence: tree state mirrors process mmap buffer reservations and allocations. Free descriptors are persistent allocator state and are merged to avoid adjacent free ranges. Oneway free space is maintained independently from geometric free space.

Dependencies and integration points: selected by `range_alloc/mod.rs` when descriptor count grows. It depends on kernel `RBTree`, preallocated node reservations, page constants, `DescriptorState`, `FreedRange`, `Range`, and seq-file debugging.

Risks: dual-tree consistency is critical; every free range in `tree` must have exactly one matching key in `free_tree`. Merging during abort must remove stale free keys before mutating sizes. Descriptor state uses `try_change_state` to restore state on errors; bypassing it could lose allocations. Best-fit relies on tuple ordering, so changing `FreeKey` semantics affects fragmentation.

Test signals: allocate exact-fit and split-fit ranges, free with previous/next/both-side merging, unaligned page-boundary freed-range expansion, `free_tree` lookup after many operations, oneway quota and spam checks, array migration preserving descriptors, and collapse to empty after all buffers are aborted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/range_alloc/tree.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder.h -->
# sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder.h

Purpose: declares the public C-facing ABI used between Rust Binder, binderfs C code, and tracepoint C code. It exposes binderfs helper functions, opaque Rust object handles, layout descriptors, and inline field accessors for tracing.

Important APIs/types/functions: declarations include `init_rust_binderfs`, `rust_binderfs_create_proc_file`, and `rust_binderfs_remove_file`. Opaque typedefs are `rust_binder_transaction`, `rust_binder_process`, and `rust_binder_node`. `rb_process_layout`, `rb_transaction_layout`, `rb_node_layout`, and `rust_binder_layout` describe offsets exported by Rust as `RUST_BINDER_LAYOUT`. Inline helpers read transaction debug id, code, flags, target node, target process, process task, node debug id, and node userspace pointer.

Control flow: there is no runtime control flow beyond inline pointer arithmetic. C tracepoints receive opaque Rust pointers, add exported offsets, and dereference fields for trace payload formatting.

State and persistence: the header owns no state. It depends on `RUST_BINDER_LAYOUT` matching the in-memory Rust structs for the loaded module instance.

Dependencies and integration points: included by `rust_binder_events.c`, `rust_binder_events.h`, and binderfs glue. It includes Binder UAPI headers for `binder_uintptr_t` and binderfs types. Rust defines the corresponding layout static in `rust_binder_main.rs` from `TRANSACTION_LAYOUT`, `PROCESS_LAYOUT`, and `NODE_LAYOUT`.

Risks: this is an unsafe ABI contract. Any Rust struct layout, wrapper offset, or arc offset change must update the exported layout constants or C tracepoints will read invalid memory. Inline arithmetic on `void *` relies on compiler extensions used in the kernel. Nullable target-node handling is explicit but other pointers are assumed valid.

Test signals: build with bindgen and tracepoints enabled, boot/load the module, emit transaction trace events, and verify trace output fields match Rust debug output. Layout-sensitive changes should be checked with compile-time offset tests or targeted runtime trace smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_events.c -->
# sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_events.c

Purpose: defines string tables and instantiates Rust Binder tracepoints. It supplies human-readable Binder command and return names used by both trace formatting and Rust stats output.

Important APIs/types/functions: `binder_command_strings[]` lists `BC_*` command names from `BC_TRANSACTION` through `BC_REPLY_SG`. `binder_return_strings[]` lists `BR_*` return names through `BR_TRANSACTION_PENDING_FROZEN`. The file defines `CREATE_TRACE_POINTS` and `CREATE_RUST_TRACE_POINTS` before including `rust_binder_events.h`.

Control flow: no dynamic control flow is present. During compilation, the tracepoint macros in the header expand into tracepoint definitions. At runtime, trace and stats code indexes the arrays by `_IOC_NR(cmd)` after bounds checks on the caller side.

State and persistence: the arrays are global const string tables for the module lifetime. They must stay aligned with Binder UAPI numeric command ranges and `stats.rs` count constants.

Dependencies and integration points: includes `rust_binder.h`, which provides opaque Rust pointer layout helpers for the trace header. `stats.rs` imports these arrays through `extern "C"` and converts C strings to Rust `&str` for binder log output.

Risks: missing newer Binder commands or returns means trace output may show `unknown` and stats arrays may not cover the full range. The Rust stats code assumes all pointers within its computed bounds are non-null ASCII C strings, so array/order drift can become unsafe.

Test signals: compile tracepoints, run Binder operations that emit common commands and returns, inspect trace output names, and compare nonzero `binder_logs/stats` counters with expected command names. Adding a UAPI constant should include a stats/trace string-table review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_events.h -->
# sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_events.h

Purpose: declares the Rust Binder tracepoint set for ioctl, read/write completion, waiting, transactions, fd transfer, command, and return events.

Important APIs/types/functions: trace events include `binder_ioctl`, `binder_ioctl_done`, `binder_read_done`, `binder_write_done`, `binder_wait_for_work`, `binder_transaction`, `binder_transaction_received`, `binder_transaction_fd_send`, `binder_transaction_fd_recv`, `binder_command`, and `binder_return`. `binder_function_return_class` is reused for function-return-style events, and `DEFINE_RBINDER_FUNCTION_RETURN_EVENT` instantiates named variants.

Control flow: tracepoint fast-assign blocks copy scalar fields into trace entries. `binder_transaction` uses the inline helpers from `rust_binder.h` to read Rust transaction, node, and process fields and records destination pid/thread, reply flag, code, and flags. `binder_command` and `binder_return` format names through the string tables when `_IOC_NR` is in range.

State and persistence: no driver state is stored here; trace events are passive observation hooks. They depend on live Rust Binder object pointers being valid for the duration of trace emission.

Dependencies and integration points: included by `rust_binder_events.c` for tracepoint creation and by trace wrappers in Rust through generated bindings or C trace symbols. The include path is set to `../drivers/android/binder`, matching kernel trace include conventions.

Risks: tracepoint field extraction crosses the Rust/C layout boundary, so stale offsets can corrupt trace data or fault. Tracepoints must avoid expensive or sleeping operations. String table bounds protect formatting, but table alignment with UAPI remains necessary for useful names.

Test signals: enable each tracepoint under ftrace/perf while issuing Binder ioctls, transactions, replies, fd sends/receives, and blocking reads. Verify transaction ids correlate with Rust debug ids and no trace event dereferences null target nodes except the guarded nullable path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_internal.h -->
# sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_internal.h

Purpose: provides internal C declarations and structs used by `rust_binderfs.c` to interact with Rust Binder contexts and exported seq-file/file-operation hooks.

Important APIs/types/functions: defines `RUST_BINDERFS_SUPER_MAGIC`, opaque `rust_binder_context`, `struct binder_device`, show callbacks `rust_binder_stats_show`, `rust_binder_state_show`, `rust_binder_transactions_show`, and `rust_binder_proc_show`, exported `rust_binder_fops`, context lifecycle functions `rust_binder_new_context` and `rust_binder_remove_context`, `binderfs_mount_opts`, and `binderfs_info`.

Control flow: the header is declarative. binderfs code stores `binder_device` in inode private data, calls Rust to create/remove contexts, assigns `rust_binder_fops` to Binder character device inodes, and passes seq-file calls back into Rust.

State and persistence: `binder_device` owns a Binder minor and a Rust context reference, except for binder-control where `ctx` is null. `binderfs_info` persists per superblock and tracks namespace, root uid/gid, mount options, device count, control dentry, and proc log directory.

Dependencies and integration points: includes Linux seq-file and Android Binder UAPI headers. It is intentionally not part of the bindgen input for exports from binderfs to Rust; those are declared in `rust_binder.h`/Rust extern blocks.

Risks: ownership comments are part of the ABI contract. Forgetting to call `rust_binder_remove_context` during inode eviction leaks Rust contexts; freeing `binder_device` while Rust file operations still access it would be unsafe. Mount option structs must stay consistent with parser/fill-super code.

Test signals: mount/unmount binderfs repeatedly, create and unlink binder devices, open/close Binder files, and read global/proc log files. Leak checks should show balanced context creation/removal and minor allocation/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_main.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_main.rs

Purpose: is the Rust Binder module root. It declares submodules, registers the Binder shrinker and binderfs filesystem, exposes C file operations and debug show callbacks, and defines the common `DeliverToRead` work-item abstraction.

Important APIs/types/functions: `BinderModule::init` initializes global contexts, registers `BINDER_SHRINKER`, and calls C `init_rust_binderfs`. `RUST_BINDER_LAYOUT` exports Rust struct offsets to C. `BinderReturnWriter` writes BR commands/payloads and updates stats. `DeliverToRead`, `DTRWrap`, `DArc`, and `DLArc` are the dynamic work queue foundation. `DeliverCode` emits simple return codes. Exported callbacks include `rust_binder_new_context`, `rust_binder_remove_context`, `rust_binder_open`, `release`, `ioctl`, `mmap`, `poll`, `flush`, and seq-file show functions. `BinderfsProcFile` owns per-pid binderfs log dentries.

Control flow: module initialization prepares global infrastructure. binderfs creates contexts through `rust_binder_new_context`; opening a Binder device creates a `Process`, optionally creates a per-pid proc log file, and stores the process arc in `file.private_data`. C file operations borrow or consume that arc and delegate to `Process`. Seq-file callbacks enumerate contexts and processes to print stats, state, transactions, or one pid.

State and persistence: global state includes the context registry, debug-id counter, shrinker, file operations table, and exported layout. Per-file state is owned by `Process`; per-pid binderfs proc files are removed by `BinderfsProcFile::drop`.

Dependencies and integration points: ties Rust modules to C binderfs (`rust_binderfs.c`), trace/stats, kernel module macros, file/mm/poll/uaccess wrappers, and Android Binder UAPI. `rust_binder_fops` is the C-visible vtable assigned to binderfs Binder device inodes.

Risks: all `unsafe extern "C"` callbacks assume binderfs passed valid pointers and correct private data. Foreign arc ownership must match open/release exactly. The module init path lacks a shown exit/unregister path in this file, so unload semantics depend on kernel module infrastructure elsewhere. Layout exports must track struct changes.

Test signals: module load, binderfs mount, device open/close, ioctl/mmap/poll/flush smoke tests, stats/state/proc/transactions file reads, trace/stats counter increments, and repeated process log creation with duplicate pids returning `EEXIST` as non-fatal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/rust_binderfs.c -->
# sources/distributed-fs/ceph-client/drivers/android/binder/rust_binderfs.c

Purpose: implements the C binderfs filesystem glue for Rust Binder. It registers the binderfs file system, allocates Binder device nodes, manages minors, creates feature and log files, and bridges Binder device file operations to Rust via `rust_binder_fops`.

Important APIs/types/functions: globals include `binderfs_dev`, `binderfs_minors_mutex`, and `binderfs_minors`. `binderfs_binder_device_create`, `binder_ctl_ioctl`, `binderfs_evict_inode`, mount-option parsers, `binderfs_binder_ctl_create`, `rust_binderfs_create_proc_file`, `rust_binderfs_remove_file`, `init_binder_features`, `init_binder_logs`, `binderfs_fill_super`, `binderfs_init_fs_context`, `binderfs_kill_super`, and `init_rust_binderfs` are central. Feature files expose oneway spam detection, extended error, and freeze notification support.

Control flow: `init_rust_binderfs` validates configured default device names, allocates a char-device major, and registers the filesystem. Mount setup allocates `binderfs_info`, creates the root inode, binder-control device, default configured Binder devices, feature files, and optional global logs. `BINDER_CTL_ADD` copies a device request from userspace and calls `binderfs_binder_device_create`, which reserves a minor, creates a Rust context, allocates a char inode using `rust_binder_fops`, copies major/minor back to userspace, and attaches a persistent dentry. Eviction frees minors and removes Rust contexts.

State and persistence: per-mount `binderfs_info` tracks namespace, mount limits, device count, control dentry, and log directories. Per-device `binder_device` owns its minor and Rust context. Global IDA state tracks minor allocation across mounts.

Dependencies and integration points: includes Linux VFS, fs_context, IDA, ipc namespace, uaccess, and Android binderfs UAPI headers. Calls Rust exports declared in `rust_binder_internal.h` and exposes helper functions declared in `rust_binder.h`.

Risks: minor/device_count accounting must unwind correctly on every error path. `binderfs_binder_ctl_create` appears to allocate a minor but its error path frees only `device` and `inode`, so changes should audit minor cleanup on dentry allocation failure. User namespace behavior depends on controlled device creation and clearing `SB_I_NODEV`. Proc log file names are pid-based and can collide for multiple binder fds in one process.

Test signals: mount with `max` and `stats=global`, remount option validation, default device creation, `BINDER_CTL_ADD`, add failure unwinding, unlink/rename protections for binder-control, per-pid proc log creation/removal, feature file reads, global log reads, unmount cleanup, and minor exhaustion across namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/rust_binderfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/stats.rs -->
# sources/distributed-fs/ceph-client/drivers/android/binder/stats.rs

Purpose: tracks Binder command (`BC_*`) and return (`BR_*`) counters for global and per-process binder logs.

Important APIs/types/functions: `BC_COUNT` and `BR_COUNT` size arrays from the highest supported UAPI command/return numbers. `GLOBAL_STATS` is a static `BinderStats`. `BinderStats` stores relaxed atomic arrays and provides `new`, `inc_bc`, `inc_br`, and `debug_print`. The internal `strings` module imports C `binder_command_strings` and `binder_return_strings` and converts indexed C strings to Rust `&str`.

Control flow: Binder command handling calls `inc_bc`; return writing through `BinderReturnWriter::write_code` calls `inc_br` for both global and process stats. `debug_print` iterates counters and prints only nonzero entries with names resolved from the C arrays.

State and persistence: counters are in-memory atomics for the module/process lifetime. Global stats persist while the module is loaded; per-process stats live inside each `Process`.

Dependencies and integration points: depends on Binder UAPI constants from `defs`, kernel `_IOC_NR`, seq-file output, and the string tables in `rust_binder_events.c`. `rust_binder_main.rs` includes global and per-process stats in binderfs log output.

Risks: relaxed atomics are appropriate for approximate counters but not for synchronization. The C string conversion is unsafe and assumes every in-range table entry is a valid nul-terminated ASCII string; table length/order must match `BC_COUNT` and `BR_COUNT`. Commands beyond the current max are silently ignored.

Test signals: issue representative Binder commands and returns, read `binder_logs/stats`, and verify nonzero named counters for global and process sections. Add-UAPI tests should fail or be reviewed when new `BC_*`/`BR_*` constants exceed the configured counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/binder/stats.rs -->
