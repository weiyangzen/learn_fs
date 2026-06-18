# subset-b-004035 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/slab-depot.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/slab-depot.c

## Purpose
`slab-depot.c` implements the VDO physical-space allocator, slab reference-count store, slab journal, slab summary, scrub/rebuild flow, resize registration, and related statistics. A `slab_depot` owns all slabs and per-physical-zone `block_allocator` instances; each allocator runs on its physical-zone thread and serializes updates for the slabs assigned to that zone.

## Important APIs, Types, And Functions
The exported entry points are the operational surface declared in `slab-depot.h`: `vdo_decode_slab_depot()`, `vdo_free_slab_depot()`, `vdo_record_slab_depot()`, `vdo_load_slab_depot()`, `vdo_prepare_slab_depot_to_allocate()`, `vdo_drain_slab_depot()`, `vdo_resume_slab_depot()`, `vdo_allocate_block()`, `vdo_modify_reference_count()`, `vdo_release_block_reference()`, `vdo_acquire_provisional_reference()`, `vdo_attempt_replay_into_slab()`, `vdo_adjust_reference_count_for_rebuild()`, resize helpers, scrub helpers, and statistics/dump helpers. Internally, the file centers on `struct vdo_slab`, `struct slab_journal`, `struct reference_block`, `struct block_allocator`, and `struct slab_scrubber`.

## Control Flow
Allocation opens the current slab or dequeues the highest-priority slab, scans reference counters for a zero byte, assigns a provisional reference, adjusts free-space accounting, and returns the PBN. Normal reference changes enqueue a `reference_updater` on the slab journal. `add_entries()` preserves recovery-journal order, appends journal entries, locks journal blocks, commits full or draining tail blocks, and then updates counters unless the slab is still unrecovered. Metadata I/O is callback-driven: journal blocks, reference blocks, summary blocks, flushes, and scrub reads all complete back on the allocator thread. Load first reads/combines slab summary data, then loads or reconstructs per-slab state. Preparation for allocation orders slabs by clean/dirty and fullness, queues clean slabs directly, and sends dirty or long-journal slabs to the scrubber. Drain and resume advance through scrubber, slabs, and summary state machines.

## State And Persistence
Persistent state is split across the superblock-encoded slab depot state, slab summary partition, slab journals, and reference-count blocks. Slab summary entries persist tail block offset, dirty/clean state, whether reference counts must be loaded, and a fullness hint. Slab journal entries persist ordered increment/decrement operations and recovery-journal points. Reference blocks persist counters plus per-sector commit points to detect torn writes and skip already-applied journal entries during replay. The code uses flushes before reference-block writes, slab-summary writes, and journal reaping to preserve ordering against lower-layer write reordering. Runtime state includes priority queues, dirty journal lists, dirty reference-block wait queues, journal block locks, admin states, and per-zone counters.

## Dependencies And Integration Points
This file integrates with VDO completion/admin-state machinery, recovery journal locking, physical-zone thread scheduling, `vio` metadata I/O, `dm_kcopyd` for rebuild erasure, priority tables, wait queues, packed on-disk encodings, read-only notification, and VDO statistics. The action manager fans operations across physical zones while preserving per-zone thread ownership.

## Risks
Correctness depends on strict ordering among recovery journal, slab journal, reference blocks, and slab summary updates. Lock underflow, journal full thresholds, torn reference writes, stale slab summary hints, wrong callback thread IDs, or mishandled read-only transitions can cause allocation leaks, lost references, or recovery corruption. The code assumes serialized physical-zone mutation; callers must not mutate slab structures from arbitrary threads. Resize has rollback-sensitive `new_slabs`/`slabs` ownership. Several counters are read with `READ_ONCE()` from other threads, so they are approximate reporting values, not synchronization barriers.

## Test Signals
Useful tests include journal replay idempotence with torn-sector commit points, tail-block partial writes, journal reaping only after flush and lock release, clean load versus dirty scrub load, read-only transition while waiters and VIOs are outstanding, provisional allocation release/confirmation, block-map reference saturation, no-space and priority-table behavior, physical-zone fan-out, grow/abandon/use-new-slabs flows, and statistics aggregation under concurrent allocator activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/slab-depot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/slab-depot.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/slab-depot.h

## Purpose
`slab-depot.h` defines the in-memory contracts and public APIs for VDO slab allocation, slab journals, reference-count blocks, slab summary blocks, scrubbers, block allocators, and the top-level slab depot.

## Important APIs, Types, And Functions
Key types include `enum reference_status`, `struct journal_lock`, `struct slab_journal`, `struct reference_block`, `struct search_cursor`, `enum slab_rebuild_status`, `struct vdo_slab`, `struct slab_scrubber`, `struct slab_summary_block`, `struct block_allocator`, `enum slab_depot_load_type`, and `struct slab_depot`. Public functions expose load/decode/free/record, reference-count adjustment, provisional allocation, physical block allocation, recovery replay, grow/use/abandon resize paths, drain/resume, forced tail commits, scrub launch, statistics, and dumps.

## Control Flow
The header documents thread ownership: loads and saves originate on the admin thread, normal allocation/reference updates run on the owning physical-zone thread, and recovery-journal tail-commit requests are scheduled from the recovery journal thread into physical-zone threads. Embedded waiters in journal, reference block, and summary structures are used by asynchronous VIO and wait-queue flows implemented in `slab-depot.c`.

## State And Persistence
The structures mirror persistent VDO metadata. `slab_journal` tracks head/unreapable/tail/commit/summarized sequence numbers, recovery locks, thresholds, packed tail block, and on-disk journal locks. `reference_block` tracks dirty/write state and commit points per sector. `vdo_slab` owns physical extents, journal/refcount origins, free counters, search cursor, and admin/rebuild state. `slab_depot` carries slab geometry, summary partition origin, current and resize slab arrays, zone counts, and allocators.

## Dependencies And Integration Points
The header depends on admin state, completions, data VIOs, on-disk encodings, physical-zone configuration, priority tables, recovery journal, statistics, VIOs, wait queues, Linux atomics/lists, and dm-kcopyd.

## Risks
Many fields are deliberately thread-affine rather than lock-protected; changing call sites without respecting physical-zone ownership risks races. Several comments identify persisted values or unit-test-adjusted capacities, so enum values, packed geometry, and journal entry counts must remain compatible. Resize state has two slab arrays and must be cleaned up carefully.

## Test Signals
Tests should verify exported API behavior across normal, recovery, rebuild, suspend/save, read-only, and resize states; validate field initialization and teardown; and assert that thread-affinity assumptions are preserved by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/slab-depot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/statistics.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/statistics.h

## Purpose
`statistics.h` defines the stable VDO statistics payload reported by the driver. It groups allocator, journal, packer, block-map, dedupe, error, bio, memory, and index counters under `struct vdo_statistics`.

## Important APIs, Types, And Functions
The file is type-only. `STATISTICS_VERSION` is `36`. Important structs include `block_allocator_statistics`, `commit_statistics`, `recovery_journal_statistics`, `packer_statistics`, `slab_journal_statistics`, `slab_summary_statistics`, `ref_counts_statistics`, `block_map_statistics`, `hash_lock_statistics`, `error_statistics`, `bio_stats`, `memory_usage`, `index_statistics`, and `vdo_statistics`.

## Control Flow
There is no executable control flow. Producers throughout the VDO codebase fill subsets of `vdo_statistics`; for this subset, `slab-depot.c` fills allocator, ref-count, slab-journal, slab-summary, and recovery percentage fields.

## State And Persistence
The structs represent runtime/accounting state rather than on-disk metadata, but consumers may treat their layout/version as a user-visible ABI. Counter widths vary between `u32`, `u64`, and VDO block-count typedefs. `mode[15]` and nested bio stats are fixed-size reporting fields.

## Dependencies And Integration Points
The file includes `types.h` for block-count typedefs. It integrates with sysfs/dm statistics collection and VDO component-specific aggregation functions.

## Risks
Changing field order, field type, or `STATISTICS_VERSION` without coordinating readers can break user-space tooling. Mixed thread updates mean consumers should expect approximate snapshots unless producers add synchronization.

## Test Signals
Tests should check version changes when layout changes, complete population of nested counters, overflow behavior for high-volume counters, and compatibility with user-space parsers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/statistics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/status-codes.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/status-codes.c

## Purpose
`status-codes.c` registers VDO-specific status codes with the shared UDS error framework and maps internal VDO/UDS/system errors to kernel errno return values.

## Important APIs, Types, And Functions
`vdo_status_list[]` provides names and messages for each `enum vdo_status_codes` value. `vdo_register_status_codes()` validates list length with `BUILD_BUG_ON()` and registers the block. `vdo_status_to_errno()` normalizes successful, negative errno, small positive errno, and VDO/UDS status codes.

## Control Flow
Registration is a simple one-shot call into `uds_register_error_block()`. Error mapping returns existing non-positive values unchanged, maps positive values below 1024 to negative errno, maps `VDO_BAD_CONFIGURATION` to `-EINVAL`, `VDO_NO_SPACE` to `-ENOSPC`, `VDO_READ_ONLY` to `-EIO`, and logs any other internal status before returning `-EIO`.

## State And Persistence
No persistent state is written. The status-code numeric range is ABI-like because error names, messages, and mappings are consumed across VDO and UDS components.

## Dependencies And Integration Points
The file depends on `errors.h`, `logger.h`, `permassert.h`, and `thread-utils.h`. It integrates with UDS error registration and the kernel-facing paths that must return negative errno values.

## Risks
If the enum and `vdo_status_list[]` diverge, registration would describe the wrong errors; the compile-time size assertion mitigates this. Unknown errors are intentionally collapsed to `-EIO`, so losing a specific mapping can reduce diagnosability or alter user-visible behavior.

## Test Signals
Tests should verify registration size, all status-to-string entries, direct errno passthrough, positive errno negation, specific VDO mappings, and default logging-to-`-EIO` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/status-codes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/status-codes.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/status-codes.h

## Purpose
`status-codes.h` reserves the VDO status-code block after the UDS block and declares all VDO-specific internal statuses plus registration and errno-conversion helpers.

## Important APIs, Types, And Functions
`enum vdo_status_codes` defines `VDO_STATUS_CODE_BASE`, specific failures such as `VDO_REF_COUNT_INVALID`, `VDO_NO_SPACE`, `VDO_READ_ONLY`, `VDO_CORRUPT_JOURNAL`, `VDO_JOURNAL_OVERFLOW`, and `VDO_INVALID_ADMIN_STATE`, then `VDO_STATUS_CODE_LAST` and `VDO_STATUS_CODE_BLOCK_END`. It declares `vdo_status_list[]`, `vdo_register_status_codes()`, and `vdo_status_to_errno()`.

## Control Flow
The header has no runtime control flow but establishes the numeric sequence used by `status-codes.c` and call sites throughout VDO.

## State And Persistence
These values are not directly on-disk records, but they are cross-component error contracts. Numeric stability matters for logging, registration, diagnostics, and any user-space code that decodes internal statuses.

## Dependencies And Integration Points
The header includes `errors.h` for the UDS error-block constants and `struct error_info`. Many VDO components include this header to return or test VDO-specific error results.

## Risks
Inserting, deleting, or reordering enum members changes numeric codes unless carefully coordinated. The block-size relationship with UDS errors must remain valid, and every enum value before `VDO_STATUS_CODE_LAST` needs a matching entry in `vdo_status_list[]`.

## Test Signals
Tests should assert numeric block boundaries, enum/list count parity, errno conversion for important statuses, and compilation of downstream modules that switch on these codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/status-codes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/string-utils.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/string-utils.c

## Purpose
`string-utils.c` implements a bounded append helper for constructing strings in caller-owned buffers.

## Important APIs, Types, And Functions
`vdo_append_to_buffer(char *buffer, char *buf_end, const char *fmt, ...)` wraps `vsnprintf()`, appends formatted output at the current buffer cursor, and returns the next write cursor. It is annotated as printf-like in the header.

## Control Flow
The function starts a variadic argument list, calls `vsnprintf()` with the remaining buffer length, clamps the returned cursor to `buf_end` on truncation, otherwise advances by the number of bytes written, then ends the variadic list.

## State And Persistence
No global or persistent state exists. The only state is the caller's buffer and cursor. Truncated output is detected by comparing the formatted length against available space.

## Dependencies And Integration Points
It includes `string-utils.h`, which brings kernel string/kernel helpers. Callers can repeatedly chain the returned pointer while preserving a fixed buffer end.

## Risks
Correctness depends on callers passing a valid `[buffer, buf_end]` range. If `buffer > buf_end`, the subtraction passed to `vsnprintf()` is invalid. Truncation is silent except for cursor clamping, so callers that need complete strings must check the returned pointer.

## Test Signals
Tests should cover exact fit, truncation, empty remaining space, multiple chained appends, and printf format checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/string-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/string-utils.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/string-utils.h

## Purpose
`string-utils.h` declares small string helpers used by VDO code.

## Important APIs, Types, And Functions
`vdo_bool_to_string(bool value)` returns `"true"` or `"false"` for diagnostic output. `vdo_append_to_buffer()` appends formatted text into a bounded buffer and carries a `__printf(3, 4)` attribute for compile-time format checking.

## Control Flow
The inline boolean helper is a direct ternary. The append helper is implemented in `string-utils.c`.

## State And Persistence
No state is retained. The helpers are pure except for writes into caller-provided buffers.

## Dependencies And Integration Points
The header includes Linux kernel and string headers. `slab-depot.c` uses `vdo_bool_to_string()` in diagnostic dumps.

## Risks
The string literals are stable and safe. The append declaration relies on callers respecting buffer bounds and format/argument types.

## Test Signals
Tests should compile format-checked calls, verify boolean rendering, and exercise append truncation behavior through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/string-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-device.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-device.c

## Purpose
`thread-device.c` provides a process-thread-local registry mapping the current kernel thread to a VDO device id pointer.

## Important APIs, Types, And Functions
It owns a static `struct thread_registry device_id_thread_registry`. `vdo_register_thread_device_id()` registers the current thread with a supplied `unsigned int *`. `vdo_unregister_thread_device_id()` removes the current thread. `vdo_get_thread_device_id()` returns the registered id or `-1`. `vdo_initialize_thread_device_registry()` initializes the registry.

## Control Flow
Each public wrapper delegates to the generic thread registry in `thread-registry.c`. Lookup returns a typed integer by dereferencing the stored pointer when present.

## State And Persistence
State is in the static registry only and is not persistent. The registered id pointer must outlive the thread registration.

## Dependencies And Integration Points
The file integrates generic `thread-registry` with VDO device identity, likely for logging, allocation tracking, or per-device context lookup from code that only knows `current`.

## Risks
Forgetting to unregister leaves stale task-to-pointer mappings. Registering a pointer with too short a lifetime can cause lookup use-after-free. Lookup returns `-1`, so callers must handle "not registered".

## Test Signals
Tests should cover initialization, register/lookup/unregister on the same thread, duplicate registration behavior inherited from `thread-registry`, and unregistered lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-device.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-device.h

## Purpose
`thread-device.h` declares the VDO device-id thread registry wrappers.

## Important APIs, Types, And Functions
The header exposes `vdo_register_thread_device_id()`, `vdo_unregister_thread_device_id()`, `vdo_get_thread_device_id()`, and `vdo_initialize_thread_device_registry()`. It reuses `struct registered_thread` from `thread-registry.h`.

## Control Flow
No runtime flow is defined here; call sites register a `registered_thread` storage object for the current thread, query the id while registered, then unregister before thread exit or context teardown.

## State And Persistence
The header declares access to volatile runtime registration state only. It does not own storage.

## Dependencies And Integration Points
It includes `thread-registry.h`, tying this device-id layer to the generic task-pointer registry.

## Risks
The API requires caller-owned `registered_thread` and id storage. Mismanaged lifetime or missing unregister can leave invalid registry entries.

## Test Signals
Compile-time tests should ensure callers include this header without needing generic internals beyond `struct registered_thread`; runtime tests should check the lifecycle documented by the API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-registry.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-registry.c

## Purpose
`thread-registry.c` implements a small RCU-protected registry that associates the current `task_struct` with an arbitrary pointer.

## Important APIs, Types, And Functions
`vdo_initialize_thread_registry()` initializes list and spinlock. `vdo_register_thread()` adds the current task and pointer, replacing and warning on an existing current-task entry. `vdo_unregister_thread()` removes the current task and warns if not found. `vdo_lookup_thread()` performs an RCU read-side search and returns the associated pointer or `NULL`.

## Control Flow
Mutations take `registry->lock`, walk the list, delete existing entries with `list_del_rcu()`, add new entries with `list_add_tail_rcu()`, and call `synchronize_rcu()` before reinitializing removed links. Lookup runs under `rcu_read_lock()` and uses `list_for_each_entry_rcu()`.

## State And Persistence
All state is runtime-only: a list of `registered_thread` nodes keyed by `current`. The registry does not allocate nodes; callers own node and pointer lifetime.

## Dependencies And Integration Points
The implementation uses Linux RCU lists, spinlocks, `current`, and VDO assertion logging. It underpins higher-level registries such as thread-device and allocation-thread tracking.

## Risks
Calling logging or complex code while holding the spinlock is intentionally avoided. Caller-owned storage makes lifetime discipline critical. Duplicate registration is tolerated by replacement but logged as an assertion failure, which can hide a lifecycle bug if ignored.

## Test Signals
Tests should cover concurrent lookup during register/unregister, duplicate registration, unregister missing entry, pointer retrieval, and RCU grace-period behavior before node reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-registry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-registry.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-registry.h

## Purpose
`thread-registry.h` defines the generic current-thread-to-pointer registry interface.

## Important APIs, Types, And Functions
`struct thread_registry` contains the RCU list head and spinlock. `struct registered_thread` contains the list link, stored pointer, and `task_struct *`. The header declares initialize, register, unregister, and lookup functions.

## Control Flow
The intended lifecycle is initialize registry, register a caller-owned `registered_thread` for the current task, use lookups from code running on that task, and unregister before the task or pointed-to data disappears.

## State And Persistence
Registry state is volatile kernel memory. Nothing is persisted or encoded.

## Dependencies And Integration Points
It includes Linux list and spinlock definitions and is included by specialized registries such as `thread-device.h`.

## Risks
Because nodes are caller-owned, the header contract requires stable storage until after unregister and RCU grace handling in the implementation. It also keys only by `current`, so it is unsuitable for looking up arbitrary tasks.

## Test Signals
Tests should verify structure initialization, include dependencies, lifecycle pairing, and integration with wrappers that store typed pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-registry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-utils.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-utils.c

## Purpose
`thread-utils.c` provides VDO kernel-thread creation and joining helpers with naming, allocation tracking registration, and a completion-based join path.

## Important APIs, Types, And Functions
Private `struct thread` stores the function, data, hlist link, task pointer, and done completion. `vdo_initialize_threads_mutex()` initializes global thread list locking. `vdo_create_thread()` allocates a wrapper and starts `kthread_run()`. `vdo_join_threads()` waits for completion, removes the wrapper from the global list, and frees it. `thread_starter()` is the kthread entry trampoline.

## Control Flow
Creation allocates a wrapper, derives a thread name using colon-prefix inheritance from `current->comm` when appropriate, starts the kthread, and returns the wrapper. The starter records `current`, links the wrapper under a mutex, registers the thread as an allocating thread, calls the supplied function, unregisters, completes `thread_done`, and exits. Join waits interruptibly, sleeping briefly on interruptions, then unlinks and frees.

## State And Persistence
Global state is `thread_list` plus `thread_mutex`. Per-thread state is transient and freed by join. No persistent metadata is written.

## Dependencies And Integration Points
The file depends on Linux kthreads, completions, mutexes, delays, current task state, VDO memory allocation, logging, and allocation-thread registration from the broader VDO/UDS infrastructure.

## Risks
Every successful create needs a join to free the wrapper. The global `thread_list` is maintained but not exposed here, so future users must preserve mutex discipline. Name-prefix logic depends on colon conventions. If `kthread_run()` fails, the function returns raw `PTR_ERR()` rather than a VDO status.

## Test Signals
Tests should cover create failure, naming with and without colon prefixes, function invocation with data, allocating-thread registration lifecycle, interrupted join waiting, and memory cleanup after join.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-utils.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-utils.h

## Purpose
`thread-utils.h` declares VDO thread lifecycle helpers.

## Important APIs, Types, And Functions
It forward-declares `struct thread` and exposes `vdo_initialize_threads_mutex()`, `vdo_create_thread()`, and `vdo_join_threads()`. `vdo_create_thread()` takes a `void (*)(void *)` function, data pointer, name, and output wrapper pointer.

## Control Flow
The header defines the lifecycle contract: initialize the mutex, create a named thread, and later join it using the returned wrapper.

## State And Persistence
There is no persistent state. Runtime state is owned by the implementation's wrapper and global list.

## Dependencies And Integration Points
The header includes Linux atomic definitions and is included by code that needs to spawn VDO-managed kernel threads.

## Risks
The opaque `struct thread` prevents direct caller cleanup, so callers must use `vdo_join_threads()` exactly once after a successful create. Return values can be VDO allocation errors or kernel `PTR_ERR()` values.

## Test Signals
Compile and runtime tests should validate lifecycle pairing, error propagation, and caller inability to depend on wrapper internals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/time-utils.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/time-utils.h

## Purpose
`time-utils.h` provides tiny kernel time helpers used by VDO/UDS code.

## Important APIs, Types, And Functions
`ktime_to_seconds(ktime_t reltime)` converts nanoseconds to seconds by dividing by `NSEC_PER_SEC`. `current_time_ns(clockid_t clock)` returns monotonic nanoseconds for `CLOCK_MONOTONIC`, otherwise realtime nanoseconds. `current_time_us()` returns realtime microseconds.

## Control Flow
All helpers are static inline and branch only on the requested clock id in `current_time_ns()`.

## State And Persistence
No state is stored. Values reflect the current kernel monotonic or real clock at call time.

## Dependencies And Integration Points
The header includes kernel `ktime`, `time`, and type headers. It can be included wherever low-overhead timestamp conversion is needed.

## Risks
`ktime_to_seconds()` assumes the input is a nanosecond value despite the `ktime_t` type. `current_time_ns()` treats any non-`CLOCK_MONOTONIC` clock as realtime, so callers needing other clock semantics must not use it as a general clock dispatcher.

## Test Signals
Tests should cover monotonic versus realtime branch selection, microsecond conversion, and expected truncation on division.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/time-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/types.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/types.h

## Purpose
`types.h` defines common VDO scalar typedefs, persisted enums, configuration structures, completion types, async action callback types, priorities, and the base `vio` wrapper used for block I/O.

## Important APIs, Types, And Functions
Important typedefs include block counts, logical/physical block numbers, sequence numbers, slab counts, thread IDs, and zone counts. Persisted enums include `vdo_state`, `journal_operation`, `partition_id`, `vdo_metadata_type`, and block mapping state. Important structs include `block_map_slot`, `data_location`, `slab_config`, `thread_count_config`, `device_config`, `vdo_completion`, and `vio`. Inline helpers classify VDO states requiring recovery or read-only rebuild.

## Control Flow
The only executable logic is in inline state predicates. The rest of the file establishes shared type contracts used by completion scheduling, metadata layout, device configuration, and I/O submission.

## State And Persistence
Several enums are explicitly persisted on storage, so numeric values must be preserved. `slab_config` and `thread_count_config` are packed and participate in equality or on-disk/parsed configuration comparisons. `vdo_completion` and `vio` are runtime structures that carry async callback, result, owning VDO, priority, queue link, bio, data buffer, and I/O sizing state.

## Dependencies And Integration Points
The file includes Linux bio/block/device-mapper/list/type headers and `funnel-queue.h`. It is foundational for most VDO modules, including slab depot, recovery journal, block map, VIO pools, and admin completion code.

## Risks
Changing persisted enum values, packed struct layout, or completion priority values can break compatibility or scheduling assumptions. `vdo_completion` is shared across async code, so callback thread IDs, completion type assertions, and queue links must be maintained consistently. `vio` embeds a bio pointer and merge list, making ownership and completion ordering important.

## Test Signals
Tests should verify persisted numeric values, packed sizes/layout where relevant, state predicate behavior, completion type assertions in users, VIO priority routing, and configuration equality/serialization compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/types.h -->
