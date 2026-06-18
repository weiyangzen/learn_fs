# Research: subset-b-004031

Grouped research for VDO encoding, flushing, funnel queue, workqueue, and UDS indexer files. Each section is source-tree aligned for reconciliation into the per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/encodings.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/encodings.h

## Purpose
`encodings.h` is the shared contract for VDO's persistent metadata formats and the inline helpers that translate between native in-memory structures and packed, little-endian, on-disk representations. It covers volume geometry, block-map entries and pages, recovery journal blocks and entries, slab journal/reference-count formats, slab summary entries, layout/superblock component state, and CRC helpers.

## Important APIs, Types, And Functions
- Versioning and component headers: `struct version_number`, `struct packed_version_number`, `struct header`, `struct packed_header`, `vdo_pack_version_number()`, `vdo_unpack_version_number()`, `vdo_pack_header()`, and `vdo_unpack_header()`. Component IDs include `VDO_SUPER_BLOCK`, `VDO_LAYOUT`, `VDO_RECOVERY_JOURNAL`, `VDO_SLAB_DEPOT`, `VDO_BLOCK_MAP`, and `VDO_GEOMETRY_BLOCK`.
- Geometry: `struct volume_geometry`, `struct volume_region`, `struct index_config`, `vdo_initialize_volume_geometry()`, `vdo_encode_volume_geometry()`, `vdo_parse_geometry_block()`, `vdo_get_index_region_start()`, `vdo_get_data_region_start()`, and `vdo_get_index_region_size()`.
- Block map: `struct block_map_entry`, `struct block_map_page`, `vdo_pack_block_map_entry()`, `vdo_unpack_block_map_entry()`, `vdo_is_valid_location()`, `vdo_format_block_map_page()`, `vdo_validate_block_map_page()`, `vdo_compute_block_map_page_count()`, and `vdo_compute_new_forest_pages()`.
- Recovery journal: `struct recovery_journal_entry`, `struct packed_recovery_journal_entry`, v1 compatibility entry structures, `struct recovery_block_header`, `struct packed_journal_header`, `struct packed_journal_sector`, `vdo_pack_recovery_journal_entry()`, `vdo_unpack_recovery_journal_entry()`, `vdo_pack_recovery_block_header()`, `vdo_unpack_recovery_block_header()`, `vdo_is_valid_recovery_journal_sector()`, and `vdo_compute_recovery_journal_block_number()`.
- Slab/refcount metadata: `vdo_refcount_t`, `struct packed_reference_sector`, `struct packed_reference_block`, `struct slab_depot_state_2_0`, `struct slab_journal_entry`, `packed_slab_journal_entry`, `struct packed_slab_journal_block`, `vdo_pack_slab_journal_entry()`, `vdo_unpack_slab_journal_entry()`, `vdo_decode_slab_journal_entry()`, `vdo_get_saved_reference_count_size()`, and `vdo_get_slab_journal_start_block()`.
- Layout and superblock: `struct layout`, `struct partition`, `struct vdo_config`, `struct vdo_component`, `struct vdo_component_states`, `vdo_initialize_layout()`, `vdo_validate_config()`, `vdo_decode_component_states()`, `vdo_validate_component_states()`, `vdo_encode_super_block()`, `vdo_decode_super_block()`, and `vdo_initialize_component_states()`.

## Control Flow And Data Flow
Most helpers are one-step pack/unpack routines. Callers construct native metadata state, invoke a pack helper to produce a packed structure or block, then write it through the VDO I/O path. Reads reverse that path: packed bytes are validated, converted to native values, and then passed to higher-level block map, slab depot, journal, or superblock logic. Journal helpers preserve sequence/entry ordering through `struct journal_point`, with `vdo_advance_journal_point()` and `vdo_before_journal_point()` used by recovery and slab journal code.

Bitfield-heavy structures encode constrained fields into compact records. A block-map entry stores 36 PBN bits plus a 4-bit mapping state in five bytes. Recovery journal entries combine a block-map slot, operation, mapping, and unmapping. Slab journal entries use a 23-bit slab-block offset and a one-bit increment flag, with an alternate payload layout when block-map increments are present.

## State And Persistence Behavior
This file defines persistent VDO compatibility. Packed structures use fixed-width little-endian fields and `__packed` layout so metadata remains machine independent. The declared version constants and encoded-size constants act as hard gates for decoding old formats and laying out superblock component data. Compatibility-sensitive fields such as `volume_geometry_4_0`, recovery journal v1 entries, layout 3.0 structures, and `packed_vdo_component_41_0` preserve older on-disk formats.

Persistent risk centers on exact field sizes. The 36-bit PBN encodings cap physical addressability, `packed_journal_point` assumes the top 16 sequence bits are zero, and many size constants are derived from VDO block/sector sizes. Any change here changes on-disk metadata and must be paired with versioning and upgrade logic.

## Dependencies And Integration Points
The header depends on Linux endian/CRC/UUID/block types plus VDO `constants.h`, `types.h`, and `numeric.h`. Implementations live mainly in `encodings.c`, while callers are spread across `vdo.c`, `dm-vdo-target.c`, `block-map.c`, `slab-depot.c`, and recovery journal code. Index geometry stored inside `struct volume_geometry` connects the VDO metadata area to the UDS indexer.

## Risks
- Bitfields depend on explicit byte-order branches; build coverage must include supported endian assumptions.
- The journal and block-map encodings rely on masked values fitting in narrow fields; missing validation before packing can silently truncate.
- Persistent size constants are cross-component contracts; accidental structure padding or enum-size assumptions would corrupt metadata.
- `vdo_is_valid_location()` treats zero-block mappings specially, so compression-state validation must stay aligned with block-map semantics.

## Test Signals
Useful tests include pack/unpack round trips for every packed structure, block-map entry tests around PBN values near 32-bit and 36-bit boundaries, recovery journal sector validation for v1/v2 metadata, superblock decode/encode compatibility fixtures, and CRC/geometry-block corruption tests. Kernel integration signals are successful VDO creation, load, suspend/resume, recovery replay, and metadata validation on existing volumes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/encodings.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/errors.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/errors.c

## Purpose
`errors.c` implements UDS/VDO error-code stringification, kernel errno translation, and registration of additional error-code blocks. It bridges internal positive UDS status codes with negative Linux errno values expected by kernel callers.

## Important APIs, Types, And Functions
- `message_table[]` provides fixed text for common errno values up to `ERANGE`.
- `error_list[]` defines built-in UDS status names/messages for codes beginning at `UDS_ERROR_CODE_BASE`.
- `struct error_block` describes a registered range, and `registered_errors` stores up to `MAX_ERROR_BLOCKS` ranges.
- `get_error_info()` resolves an error code to an `error_info` and optional block name.
- `uds_string_error()` formats a human-readable message.
- `uds_string_error_name()` formats a stable symbolic name.
- `uds_status_to_errno()` converts UDS status values to negative kernel errno values.
- `uds_register_error_block()` adds non-overlapping custom error-code ranges.

## Control Flow And Data Flow
Stringification normalizes negative inputs to positive codes, looks for registered UDS-style ranges, and falls back to the errno message table. Known internal codes are formatted as either `block: message` or symbolic names; reserved but undefined slots are reported as unknown codes inside the block. Unknown system errors are rendered into the caller buffer by `system_string_error()`.

`uds_status_to_errno()` treats zero and negative values as already kernel-compatible. Positive values below 1024 are assumed to be userspace errno numbers and negated. Internal UDS codes are mapped case-by-case: missing/corrupt index to `-ENOENT`, incompatible or unclean saved index to `-EEXIST`, disabled sessions to `-EIO`, and unexpected internal errors to `-EIO` with an informational log.

## State And Persistence Behavior
The module has process-global mutable state in `registered_errors`. It is not persisted to disk. Error text is static and used for diagnostics only. The mappings affect externally visible error behavior for index load/create paths, especially preventing an existing but unsupported index from being mistaken for absent.

## Dependencies And Integration Points
The file uses `logger.h` for fallback mapping logs, `permassert.h` for range validation, and `string-utils.h` for bounded appends. UDS indexer code returns these positive status values; kernel-facing VDO paths call `uds_status_to_errno()` when reporting failures to block/device-mapper layers.

## Risks
- `registered_errors` has no explicit locking. It is safe only if registrations happen during initialization or otherwise serialized.
- `uds_string_error_name()` lacks the explicit `buf == NULL` guard present in `uds_string_error()`.
- Positive values below 1024 are treated as errno values, so accidental internal codes in that range would be translated incorrectly.
- The static errno table is partial; unknown errno values get generic formatting rather than kernel `strerror` behavior.

## Test Signals
Unit-style tests should cover negative errno passthrough, positive errno translation, every special `uds_status_to_errno()` mapping, unknown internal errors and logs, buffer truncation behavior, duplicate block names, overlapping ranges, and registration capacity overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/errors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/errors.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/errors.h

## Purpose
`errors.h` declares the UDS status-code namespace and the public error utility APIs used by the VDO indexer and kernel integration code.

## Important APIs, Types, And Functions
- `VDO_SUCCESS` and `UDS_SUCCESS` define zero success.
- `enum uds_status_codes` reserves the internal positive error block beginning at `UDS_ERROR_CODE_BASE == 1024`, including `UDS_OVERFLOW`, `UDS_INVALID_ARGUMENT`, `UDS_BAD_STATE`, `UDS_DUPLICATE_NAME`, `UDS_QUEUED`, `UDS_UNSUPPORTED_VERSION`, `UDS_CORRUPT_DATA`, `UDS_NO_INDEX`, and `UDS_INDEX_NOT_SAVED_CLEANLY`.
- `VDO_MAX_ERROR_NAME_SIZE` and `VDO_MAX_ERROR_MESSAGE_SIZE` size caller-provided formatting buffers.
- `struct error_info` pairs symbolic names with messages for built-in or registered error ranges.
- Public functions are `uds_string_error()`, `uds_string_error_name()`, `uds_status_to_errno()`, and `uds_register_error_block()`.

## Control Flow And Data Flow
Callers return positive UDS status codes inside the indexer and convert to kernel errno only at external boundaries. The header keeps status values contiguous so `errors.c` can index into `error_info` arrays by subtracting the block base.

## State And Persistence Behavior
The status-code values are ABI-like within this source tree and affect logs, saved error handling, and external failure semantics. They are not persisted directly by this header, but index-load decisions depend on distinguishing absent, corrupt, unclean, and unsupported index states.

## Dependencies And Integration Points
The header uses Linux compiler/types annotations and is included throughout the UDS indexer, assertion helpers, and VDO code paths that need to return or translate internal statuses. Registered blocks allow other modules to extend the error namespace without colliding with the built-in range.

## Risks
- Adding or reordering enum members changes numeric values unless new codes are appended before `UDS_ERROR_CODE_LAST`.
- `UDS_QUEUED` is a non-error status inside the same positive range, so callers must not blindly translate all positive results to failures.
- Registered block range arguments must be consistent with array sizes or unknown slots are exposed at runtime.

## Test Signals
Compile-time and runtime checks should verify stable numeric values, stringification for each enum, and caller handling of `UDS_QUEUED` as an asynchronous state rather than an error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/errors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/flush.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/flush.c

## Purpose
`flush.c` implements the VDO flusher, which batches incoming flush/FUA bios, advances flush generations through logical zones and the packer, waits until affected VIO activity has retired, and finally submits the flush bios to the backing block device.

## Important APIs, Types, And Functions
- `struct flusher` owns the administrative state, generation counters, notifier and pending queues, flush mempool, waiting bio list, locking, and bio-thread rotor.
- Lifecycle APIs are `vdo_make_flusher()`, `vdo_free_flusher()`, and `vdo_get_flusher_thread_id()`.
- Request path APIs are `vdo_launch_flush()`, `flush_vdo()`, `notify_flush()`, `increment_generation()`, `flush_packer_callback()`, `finish_notification()`, `vdo_complete_flushes()`, and `vdo_complete_flush()`.
- Drain/resume APIs are `vdo_drain_flusher()` and `vdo_resume_flusher()`.
- Allocation helpers use a `mempool_t` with `allocate_flush()` and `free_flush()`, creating `struct vdo_flush` completions.

## Control Flow And Data Flow
`vdo_launch_flush()` is called when an empty flush bio arrives or before acknowledging a non-empty FUA bio. It appends the bio to `waiting_flush_bios` under the flusher spinlock and tries to allocate a `vdo_flush` from a nonblocking mempool. If allocation succeeds, all waiting bios are moved into that flush object and enqueued to the packer thread.

On the flusher thread, `flush_vdo()` asserts normal operation, assigns the next `flush_generation`, enqueues the request on `notifiers`, and starts notification if it is first in line. Notification walks logical zones one at a time with `increment_generation()`, calling `vdo_increment_logical_zone_flush_generation()` on each zone thread. After all logical zones are notified, `flush_packer_callback()` increments the packer flush generation and returns to `finish_notification()`.

`finish_notification()` moves the request from `notifiers` to `pending_flushes`, then calls `vdo_complete_flushes()`. Completion scans all logical zones for the minimum `oldest_active_generation`; pending flushes complete only when their generation is older than every active generation. Completed flushes are requeued to a selected bio thread, where `vdo_complete_flush_callback()` accounts bios, retargets them to the backing device, increments `flush_out`, and calls `submit_bio_noacct()`.

## State And Persistence Behavior
The flusher persists no disk metadata itself, but enforces write-ordering and durability semantics across VDO's in-memory pipeline and the backing device. Generation counters (`flush_generation`, `first_unacknowledged_generation`, `notify_generation`) define the ordering contract. `pending_flushes` tracks generations waiting for active logical-zone work to drain. The mempool ensures at least one flush descriptor can be available under memory pressure, and completed descriptors are reused to launch bios that accumulated after allocation failures.

## Dependencies And Integration Points
The implementation integrates with `admin-state`, `completion`, `io-submitter`, `logical-zone`, `slab-depot`, `vdo`, and the Linux bio/mempool APIs. It uses VDO completion queues for thread handoff, the packer thread as its home thread, logical-zone generation tracking for barriers, and bio threads for final lower-device submission.

## Risks
- Correctness depends on all flusher state transitions running on the packer/flusher thread except the spinlock-protected waiting-bio list.
- Allocation failure is intentionally deferred by keeping bios on `waiting_flush_bios`; regressions in `release_flush()` could strand them.
- Completion ordering assumes `oldest_active_generation` is read consistently enough with `READ_ONCE()` and that logical zones update it correctly.
- Drain completion requires both `pending_flushes` and `waiting_flush_bios` to be empty; missed relaunches can hang suspend.
- `select_bio_queue()` depends on a valid nonzero bio thread count and sane `bio_rotation_interval`.

## Test Signals
Integration tests should stress concurrent flush and FUA bios, forced `GFP_NOWAIT` allocation failure, suspend/drain while flushes are pending, multiple logical zones with long-running VIOs, bio-thread rotation, and read-only transition during `flush_vdo()`. Useful runtime signals are no stuck drain, monotonic generation logs, and correct lower-device flush count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/flush.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/flush.h

## Purpose
`flush.h` exposes the VDO flush barrier API and defines `struct vdo_flush`, the completion-backed request object used internally by the flusher.

## Important APIs, Types, And Functions
- `struct vdo_flush` contains a `vdo_completion`, a `bio_list` of covered bios, a `vdo_waiter` link for flusher queues, and a `flush_generation`.
- `struct flusher` is opaque outside `flush.c`.
- Public operations include `vdo_make_flusher()`, `vdo_free_flusher()`, `vdo_get_flusher_thread_id()`, `vdo_complete_flushes()`, `vdo_dump_flusher()`, `vdo_launch_flush()`, `vdo_drain_flusher()`, and `vdo_resume_flusher()`.

## Control Flow And Data Flow
External VDO code creates a flusher during VDO setup, calls `vdo_launch_flush()` for block-layer flush semantics, calls `vdo_complete_flushes()` when logical-zone activity advances enough to acknowledge pending flushes, and uses drain/resume during administrative suspend/resume.

## State And Persistence Behavior
The header exposes only transient flush state. The generation value on `struct vdo_flush` is the logical persistence-order barrier: bios attached to a request are not submitted to the lower device until all relevant in-flight VDO work older than that generation is done.

## Dependencies And Integration Points
The header depends on `funnel-workqueue.h`, `types.h`, `vio.h`, and `wait-queue.h`. It is consumed by VDO core, logical zone, and administrative state code that must coordinate with flush barriers.

## Risks
- `struct vdo_flush` embeds queue linkage and must not be queued on multiple wait queues at once.
- Callers must respect the flusher thread returned by `vdo_get_flusher_thread_id()` for operations that assert thread affinity.
- `vdo_complete_flushes()` must be invoked after logical-zone generation progress or flush bios can remain pending.

## Test Signals
Compile coverage should catch type and completion integration. Runtime tests should verify that suspend/drain users call the API from the correct thread and that `vdo_dump_flusher()` reports expected queue states under pending flushes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/flush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-queue.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-queue.c

## Purpose
`funnel-queue.c` implements the non-inline portions of VDO's multi-producer, single-consumer funnel queue. It provides allocation, teardown, polling, and idle/empty checks for a queue whose enqueue operation is inlined in the header.

## Important APIs, Types, And Functions
- `vdo_make_funnel_queue()` allocates and initializes the queue with a permanent stub node.
- `vdo_free_funnel_queue()` releases the queue object.
- `get_oldest()` is the core consumer-side algorithm for finding a retrievable non-stub entry while handling producer races.
- `vdo_funnel_queue_poll()` removes and returns the oldest available entry for the single consumer.
- `vdo_is_funnel_queue_empty()` reports no retrievable entries.
- `vdo_is_funnel_queue_idle()` reports neither retrievable entries nor in-progress producer enqueue state.

## Control Flow And Data Flow
The queue starts with `newest` and `oldest` pointing to a stub entry. Producers atomically swap `newest` and then link the previous node's `next` pointer. The consumer reads `oldest->next`; if the stub has a successor it advances past the stub. If the candidate entry has no successor, the consumer may reinsert the stub to preserve non-null invariants and force a future successor before dequeueing.

`vdo_funnel_queue_poll()` calls `get_oldest()`, advances `queue->oldest`, issues a read barrier so the caller sees producer-initialized entry contents, prefetches the next oldest entry, clears the removed link, and returns it. Only the consumer mutates `oldest`, so no consumer-side lock is used.

## State And Persistence Behavior
The queue is entirely transient memory state. Its key invariant is that `newest` and `oldest` are never NULL. The stub is a persistent in-memory sentinel that is sometimes reinserted to handle the race where a producer has swapped `newest` but not yet linked the previous node.

## Dependencies And Integration Points
The implementation uses VDO memory allocation, assertion helpers, `READ_ONCE`/`WRITE_ONCE`, `xchg()` from the inline put helper, `smp_rmb()`, and CPU prefetch helpers. It underpins `funnel-workqueue.c` and `indexer/funnel-requestqueue.c`.

## Risks
- The queue is safe only for one consumer; multiple consumers corrupt ordering and ownership.
- A preempted producer between `xchg()` and `previous->next = entry` temporarily hides later enqueued work.
- `vdo_is_funnel_queue_empty()` may return empty during an enqueue transition even though the queue is not idle; callers must choose the correct predicate.
- Entry lifetime is caller-owned; freeing before poll returns the entry would be unsafe.

## Test Signals
Concurrency tests should run many producers with one consumer, include forced preemption around enqueue, verify FIFO order among completed link chains, and distinguish empty versus idle behavior. Sanitizer or debug builds should assert that dequeued entries have `next == NULL` after poll.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-queue.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-queue.h

## Purpose
`funnel-queue.h` declares the VDO multi-producer, single-consumer queue and inlines the producer enqueue operation for low overhead.

## Important APIs, Types, And Functions
- `struct funnel_queue_entry` is the embedded link field required in every queued object.
- `struct funnel_queue` contains producer-owned `newest`, consumer-owned cache-line-separated `oldest`, and the `stub` sentinel.
- `vdo_funnel_queue_put()` initializes `entry->next`, atomically exchanges it into `queue->newest`, and links it from the previous newest entry.
- Non-inline APIs are `vdo_make_funnel_queue()`, `vdo_free_funnel_queue()`, `vdo_funnel_queue_poll()`, `vdo_is_funnel_queue_empty()`, and `vdo_is_funnel_queue_idle()`.

## Control Flow And Data Flow
Producers call `vdo_funnel_queue_put()` with the address of an embedded `funnel_queue_entry`. The full barrier behavior of `xchg()` orders all caller data initialization before publication. Consumers call `vdo_funnel_queue_poll()` and recover the containing object with `container_of()` or equivalent, assuming every queued type uses the same link offset for a given queue.

## State And Persistence Behavior
The queue has no persistence. Its concurrency state is encoded in two pointers and the stub node. Cache-line alignment separates producer and consumer hot fields to reduce false sharing.

## Dependencies And Integration Points
The header uses Linux atomic/cache primitives and is included by VDO workqueue and UDS request queue implementations. It intentionally exposes internals only to make `vdo_funnel_queue_put()` inline.

## Risks
- The API cannot enforce single-consumer use.
- All entries in a queue must have the embedded link at the same offset if callers use a shared cast pattern.
- Producers must not modify or free entries after enqueue until ownership returns through the consumer.
- The enqueue operation can temporarily leave the linked-list view incomplete; consumers must tolerate NULL polls.

## Test Signals
Tests should verify memory-order visibility of payload fields, correct behavior with queue stub reinsertion, and no ABA sensitivity when entries are freed after poll and later reallocated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-workqueue.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-workqueue.c

## Purpose
`funnel-workqueue.c` builds VDO kernel worker queues on top of funnel queues. It supports single-thread simple queues and multi-thread round-robin queues, completion priority selection, kthread lifecycle, idle wakeup optimization, debugging dumps, and current-workqueue introspection.

## Important APIs, Types, And Functions
- `struct vdo_work_queue` is the common external representation with name, owner thread, type, and mode.
- `struct simple_work_queue` owns priority funnel queues, private context, wait queue, idle flag, and worker kthread.
- `struct round_robin_work_queue` owns an array of simple service queues.
- Core processing: `poll_for_completion()`, `enqueue_work_queue_completion()`, `wait_for_next_completion()`, `process_completion()`, `service_work_queue()`, and `work_queue_runner()`.
- Lifecycle APIs: `vdo_make_work_queue()`, `vdo_finish_work_queue()`, `vdo_free_work_queue()`.
- Debug/introspection APIs: `vdo_dump_work_queue()`, `vdo_dump_completion_to_buffer()`, `vdo_get_current_work_queue()`, `vdo_get_work_queue_owner()`, `vdo_get_work_queue_private_data()`, and `vdo_work_queue_type_is()`.
- Submission API: `vdo_enqueue_work_queue()`.

## Control Flow And Data Flow
Creation either builds one simple queue or a round-robin wrapper with multiple simple queues. Each simple queue creates priority-specific funnel queues, starts a kthread, and waits until the worker has entered VDO code. The worker runs optional start hooks, repeatedly polls for completions from highest priority to lowest, sleeps when no work is visible, runs completions with `vdo_run_completion()`, and exits after `kthread_should_stop()` once pending work is drained.

Submission resolves a round-robin queue to one subordinate simple queue using a per-CPU rotor, sets a default priority if needed, marks `completion->my_queue`, puts the completion on the priority funnel queue, and uses the `idle` atomic flag plus barriers/CMPXCHG to avoid excessive wakeups while still waking a possibly sleeping worker.

## State And Persistence Behavior
All state is volatile worker scheduling state. Completion ownership is tracked through `completion->my_queue`; processing clears it before callback execution. Queue lifecycle is explicit: `vdo_finish_work_queue()` stops threads, and `vdo_free_work_queue()` then frees queues, names, and subordinate structures.

## Dependencies And Integration Points
The file depends on Linux kthread, waitqueue, completion, percpu, atomic, cache, and task-state APIs plus VDO `completion.h`, `funnel-queue.h`, logging, memory allocation, numeric, assertions, strings, and status codes. It is the generic executor for VDO completions across packer, logical-zone, bio, and other VDO thread domains.

## Risks
- Priority ordering is best-effort; a race can cause lower-priority work to be processed before newly visible high-priority work.
- No completions should be enqueued after `vdo_finish_work_queue()`; the code documents this as a caller contract.
- Wakeup minimization relies on subtle barriers around `idle` and funnel queue visibility.
- `get_current_thread_work_queue()` intentionally returns NULL in interrupt context to avoid nested completion processing assumptions.
- Round-robin distribution uses a per-CPU rotor shared across queues, so it is approximate rather than strict.

## Test Signals
Tests should cover single and multi-thread queues, start/finish hook invocation, priority fallback, invalid priority clamping, enqueue and stop races, current-queue introspection from worker and non-worker contexts, and dump formatting for NULL callbacks. Runtime signals are no stuck kthreads on teardown and no completion left with stale `my_queue`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-workqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-workqueue.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-workqueue.h

## Purpose
`funnel-workqueue.h` declares the public VDO workqueue API and the workqueue type descriptor used by completion scheduling code.

## Important APIs, Types, And Functions
- `MAX_VDO_WORK_QUEUE_NAME_LEN` ties queue names to Linux `TASK_COMM_LEN`.
- `struct vdo_work_queue_type` defines optional `start` and `finish` hooks plus `max_priority` and `default_priority`.
- Opaque types include `struct vdo_completion`, `struct vdo_thread`, and `struct vdo_work_queue`.
- Public APIs create, enqueue, finish, free, dump, inspect current queue/private data/owner, and compare queue type.

## Control Flow And Data Flow
Callers define a queue type, create a queue with one or more worker threads, enqueue initialized `vdo_completion` objects, and finish/free the queue during teardown. The default priority is applied when a completion uses `VDO_WORK_Q_DEFAULT_PRIORITY`.

## State And Persistence Behavior
The header exposes no persistent state. It defines the contracts for transient completion execution and thread-private context attached to worker queues.

## Dependencies And Integration Points
It depends on Linux scheduling constants and VDO `types.h`. It is consumed by VDO completion infrastructure and modules that create named execution domains.

## Risks
- Queue type priority bounds must not exceed the implementation's `VDO_WORK_Q_MAX_PRIORITY`.
- Caller-provided private contexts must outlive the worker thread that uses them.
- The API does not by itself prevent enqueue-after-finish; lifecycle ordering is external.

## Test Signals
Compile-time coverage should confirm all completion users include this interface cleanly. Runtime tests should validate that type matching, owner lookup, and private-data lookup behave correctly from worker and non-worker contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-workqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/chapter-index.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/chapter-index.c

## Purpose
`chapter-index.c` manages UDS chapter indexes. An open chapter index is mutable and tracks record names as they are added to the currently written chapter; closed chapter index pages are immutable delta-index pages used for lookup and rebuild validation.

## Important APIs, Types, And Functions
- `uds_make_open_chapter_index()` allocates an `open_chapter_index` and initializes a single-zone mutable `delta_index`.
- `uds_free_open_chapter_index()` tears down the delta index and wrapper.
- `uds_empty_open_chapter_index()` resets the mutable index for a new virtual chapter number.
- `uds_put_open_chapter_index_record()` inserts a record name mapped to a record page number.
- `uds_pack_open_chapter_index_page()` packs a range of delta lists into one immutable chapter-index page, removing entries if a page would overflow.
- `uds_initialize_chapter_index_page()` wraps a page buffer as an immutable `delta_index_page`.
- `uds_validate_chapter_index_page()` walks all entries in a loaded page and verifies page-number payloads.
- `uds_search_chapter_index_page()` maps a record name to a possible record page or `NO_CHAPTER_INDEX_ENTRY`.

## Control Flow And Data Flow
Insertion hashes the record name with `hash-utils.h` into a chapter delta list and address. It searches the mutable delta index for the address and detects full-name collision entries. If the same full name already appears as a collision, it returns a bad-state signal. Otherwise it stores the record page payload, passing the full name only when a collision entry is needed.

Packing repeatedly calls `uds_pack_delta_index_page()`. If the first not-yet-packed list cannot fit, or the caller is packing the last page and remaining lists do not fit, the code logs stats and removes whole non-empty delta lists until the page fits. This sacrifices some chapter-index precision to keep the persistent page bounded; later record-page verification still prevents false metadata reads from becoming matches.

Search initializes an immutable page delta index, computes the sub-list number from the page's `lowest_list_number`, searches by address and full name, and returns the payload if found.

## State And Persistence Behavior
Open chapter state is memory-resident until packed. Packed pages persist nonce, virtual chapter number, list range, and delta-list bitstreams through the delta-index page format. Page validation treats corrupt random data and implausible record page payloads as `UDS_CORRUPT_DATA`, but avoids logging expected unwritten-volume cases as hard errors.

## Dependencies And Integration Points
This module depends on `delta-index`, `geometry`, `hash-utils`, `indexer`, errors, logging, memory allocation, and assertions. It is used by `open-chapter.c`, `volume.c`, sparse cache paths, and index writer/rebuild code.

## Risks
- Overflow handling removes entries, reducing lookup selectivity and potentially increasing record-page scans or misses.
- Correctness depends on hash partitioning matching `index_geometry` values used when the chapter was written.
- Duplicate-name detection differs between normal and rebuild-style collision replay paths.
- Immutable page validation must keep payload bounds aligned with `record_pages_per_chapter`.

## Test Signals
Tests should insert dense collision-heavy records, pack across multiple pages, force last-page overflow, validate corrupt page buffers, search absent/present/collision names, and ensure page payloads equal or exceed `record_pages_per_chapter` are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/chapter-index.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/chapter-index.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/chapter-index.h

## Purpose
`chapter-index.h` defines the open chapter index structure and declares APIs for building, packing, validating, and searching UDS chapter indexes.

## Important APIs, Types, And Functions
- `NO_CHAPTER_INDEX_ENTRY` is `U16_MAX`, used when no index entry points to a candidate record page.
- `struct open_chapter_index` holds geometry, mutable `delta_index`, current virtual chapter number, volume nonce, and memory footprint.
- Public APIs mirror the lifecycle: make, free, empty for new chapter, put record, pack page, initialize immutable page, validate page, and search page.

## Control Flow And Data Flow
Callers maintain one open index while accumulating chapter records. When a chapter closes, they pack pages in list order. Readers initialize a `delta_index_page` from raw page data and search it for a name to narrow candidate record-page reads.

## State And Persistence Behavior
Open chapter state is volatile. Packed page state is persistent through `delta-index` immutable page encoding and includes the nonce/list range needed to validate pages during read or rebuild.

## Dependencies And Integration Points
The header depends on `delta-index.h` and `geometry.h`. It is part of the UDS volume/index writer and lookup path.

## Risks
- The sentinel value must stay outside valid record-page numbers.
- `memory_size` is informational but useful for resource accounting; callers should not assume it is only the requested memory.
- The APIs rely on consistent geometry across creation, packing, and search.

## Test Signals
Compile and integration tests should verify closed-chapter lookup after writing records, sparse/dense geometry compatibility, and behavior when no entry is found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/chapter-index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/config.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/config.c

## Purpose
`config.c` creates UDS index configurations, serializes/deserializes saved configuration metadata, validates user configuration against saved index geometry, and normalizes concurrency parameters.

## Important APIs, Types, And Functions
- Constants include magic `"ALBIC"`, versions `"06.02"` and `"08.02"`, default/max read threads, and buffer lengths.
- `uds_validate_config_contents()` reads saved config data, decodes versioned fields, handles remapping fields for 8.02, and compares to the supplied configuration.
- `uds_write_config_contents()` writes magic, version, base configuration fields, and optional remapping fields.
- `compute_memory_sizes()` maps memory-size presets and sparse mode to `chapters_per_volume`, `record_pages_per_chapter`, and `sparse_chapters_per_volume`.
- `normalize_zone_count()` and `normalize_read_threads()` clamp concurrency knobs.
- `uds_make_configuration()` allocates `struct uds_configuration`, builds index geometry, and fills derived defaults and user parameters.
- `uds_free_configuration()` and `uds_log_configuration()` handle teardown and diagnostics.

## Control Flow And Data Flow
Configuration creation starts from `uds_parameters`, computes chapter/page counts from memory size and sparse flag, allocates geometry with `uds_make_index_geometry()`, normalizes zones/readers, and records nonce, block device, offset, and size. Saved configuration validation reads magic and version, decodes the common 6.02 payload, optionally reads 8.02 remap fields into the user geometry, then compares saved and requested values field-by-field.

Writing selects the older 6.02 format for superblock versions below 4 to preserve compatibility, otherwise writes 8.02 and includes reduced-index remapping metadata.

## State And Persistence Behavior
Saved config content is persistent index metadata. It protects against opening an index with incompatible geometry, cache, sampling, mean-delta, page-size, or nonce. Version 8.02 adds fields for LVM conversion/reduced geometry remapping. Sparse configurations multiply chapter count and persistent storage footprint while preserving memory footprint.

## Dependencies And Integration Points
The file depends on logging, allocation, numeric helpers, string utilities, thread utilities, buffered readers/writers, geometry, and indexer parameter types. It is called from index layout load/save paths and index-session creation.

## Risks
- Version handling must remain compatible with older metadata; writing 8.02 to old superblock versions would break downgrade/compatibility expectations.
- `compute_memory_sizes()` has many preset branches; invalid enum values return `-EINVAL` while most UDS code expects positive UDS statuses.
- Sparse mode multiplies chapters by ten and sets 95 percent sparse chapters; geometry and storage sizing must account for this.
- Validation writes remapping fields into `user_config->geometry` before full match confirmation.

## Test Signals
Tests should cover all supported memory-size presets, sparse and reduced modes, invalid memory sizes, zone/read-thread clamping, 6.02 and 8.02 read/write round trips, nonce mismatch, page-size mismatch, remapped geometry persistence, and compatibility behavior for superblock version below 4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/config.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/config.h

## Purpose
`config.h` declares the UDS index configuration object and its versioned on-disk representations.

## Important APIs, Types, And Functions
- Defaults include `DEFAULT_VOLUME_INDEX_MEAN_DELTA`, `DEFAULT_CACHE_CHAPTERS`, `DEFAULT_SPARSE_SAMPLE_RATE`, and `MAX_ZONES`.
- `struct uds_configuration` holds the target block device, index size/offset, geometry, nonce, zone/read-thread counts, cache size, volume-index mean delta, and sparse sample rate.
- `struct uds_configuration_8_02` is the current persisted format with remapped virtual/physical chapter fields.
- `struct uds_configuration_6_02` is the older persisted format without remapping fields.
- Public APIs are `uds_make_configuration()`, `uds_free_configuration()`, `uds_validate_config_contents()`, `uds_write_config_contents()`, and `uds_log_configuration()`.

## Control Flow And Data Flow
The in-memory configuration combines user parameters and derived geometry. Save/load code uses the packed structures as size/layout references while actual encoding/decoding is performed through explicit little-endian helpers in `config.c`.

## State And Persistence Behavior
The packed structs are persistent metadata formats. The in-memory `uds_configuration` is used at runtime to size caches, choose concurrency, and verify that the index on disk belongs to the same nonce and geometry.

## Dependencies And Integration Points
The header includes `geometry.h`, `indexer.h`, and `io-factory.h`. It connects session parameters to index layout, volume index, and buffered metadata I/O.

## Risks
- On-disk structs are packed and version-sensitive; new fields require a new version strategy.
- `size_t`/`off_t` in runtime config are host-sized and must not be directly persisted.
- `MAX_ZONES` is used by other structures such as delta-index load arrays, so increasing it has wider memory/layout impact.

## Test Signals
Tests should verify structure sizes for packed versions, correct defaults in created configurations, and load/save compatibility with both 6.02 and 8.02 metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/delta-index.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/delta-index.c

## Purpose
`delta-index.c` implements the compact UDS delta-index key/value store. It stores sorted addresses in delta lists using variable-length Huffman-coded deltas plus fixed-size payloads, supports collision entries containing full record names, provides mutable in-memory indexes and immutable packed page indexes, and saves/restores mutable indexes by zone.

## Important APIs, Types, And Functions
- Initialization and teardown: `uds_initialize_delta_index()`, `uds_initialize_delta_index_page()`, `uds_uninitialize_delta_index()`, and `uds_reset_delta_index()`.
- Page packing/loading: `uds_pack_delta_index_page()`, `verify_delta_index_page()`, immutable header helpers, and `struct delta_page_header`.
- Save/restore: `uds_start_restoring_delta_index()`, `uds_finish_restoring_delta_index()`, `uds_check_guard_delta_lists()`, `uds_start_saving_delta_index()`, `uds_finish_saving_delta_index()`, `uds_write_guard_delta_list()`, and `uds_compute_delta_index_save_bytes()`.
- Iteration/search: `uds_start_delta_index_search()`, `uds_next_delta_index_entry()`, `uds_remember_delta_index_offset()`, `uds_get_delta_index_entry()`, and `uds_log_delta_index_entry()`.
- Entry operations: `uds_get_delta_entry_collision()`, `uds_get_delta_entry_value()`, `uds_set_delta_entry_value()`, `uds_put_delta_index_entry()`, and `uds_remove_delta_index_entry()`.
- Sizing/stats: `uds_get_delta_index_stats()`, `uds_compute_delta_index_size()`, and `uds_get_delta_index_page_count()`.
- Internal bit utilities include `get_field()`, `set_field()`, `get_big_field()`, `set_big_field()`, `move_bits()`, `insert_bits()`, `delete_bits()`, and delta encode/decode helpers.

## Control Flow And Data Flow
A mutable index is divided into zones, each with a contiguous bit-memory allocation, `delta_list` descriptors, and temporary rebalance offsets. `uds_reset_delta_index()` spaces each list through the zone memory and installs head/tail guard lists; the tail guard is filled with ones so corrupted streams are less likely to run past allocated memory while decoding.

Search begins with `uds_start_delta_index_search()`, which selects the zone/list, optionally starts from a saved offset, and initializes a `delta_index_entry` iterator. `uds_next_delta_index_entry()` advances by the previous entry size, decodes payload/delta bits, updates the running key, detects collision entries as zero deltas after list start, and bounds-checks against list size. `uds_get_delta_index_entry()` walks until the target key or insertion point, remembers the offset, and if a key match exists scans following collision entries comparing full names.

Insertion handles three cases: collision entry after an existing same-key entry, append at end, or insertion before a following entry that requires rewriting the following delta. `insert_bits()` grows a list by shifting nearby bits into free space or rebalancing the whole zone when local gaps are insufficient. Removal similarly deletes bits and, for non-collision entries followed by another entry, merges deltas into the following entry.

Immutable pages are packed from a mutable index by writing a `delta_page_header`, a 19-bit-per-list offset table, list bitstreams, and guard bytes. Immutable page initialization verifies nonce, list-count capacity, offset monotonicity, page bounds, and guard bytes. It supports old big-endian page headers as a fallback.

Save/restore writes per-zone `DI-00002` headers, list sizes, list data descriptors, and guard records. Restore first validates headers and list coverage, resets the target index, assigns list sizes to destination zones, rebalances memory, then reads data blobs and moves their bits to the correct destination zone.

## State And Persistence Behavior
Mutable delta indexes are in-memory structures used by the volume index and open chapter indexes. Immutable delta-index pages are persistent chapter-index pages. Save/restore records are persistent volume-index state. Persistent formats include magic, zone identity, list ranges, record/collision counts, list sizes, bit offsets, byte counts, tags, and list data. Stats track records, collisions, discards, overflow count, rebalance count, and rebalance time.

The encoding is very space-sensitive: payload bits are fixed per index, delta bits are variable-length based on `mean_delta`, collision entries append `UDS_RECORD_NAME_SIZE` bytes, and list size is a `u16` bit count. Rebalancing preserves bit offsets and guard lists while distributing free space.

## Dependencies And Integration Points
The file depends on Linux bit/log2/unaligned primitives plus VDO CPU prefetch, error codes, logging, allocation, numeric helpers, assertions, string utilities, time utilities, config, indexer, and buffered I/O. It is used directly by chapter indexes and volume indexes; geometry sizing calls `uds_get_delta_index_page_count()`.

## Risks
- Bit-level movement and overlapping copies are fragile; off-by-one errors corrupt indexes silently.
- `u16` list sizes cap a single delta list at 65535 bits; overflow handling is required by callers.
- Decode of corrupt streams can run until guard bits; guard setup and page verification are critical.
- Saved offset acceleration must be invalidated after insert/delete before the saved point.
- Collision handling requires full-name comparison; callers passing NULL names for searches that may collide would get only key-level behavior.
- Save/restore distributes lists by zone and assumes headers cover exactly all lists in order.

## Test Signals
High-value tests include randomized insert/search/delete against a reference map, collision-heavy keys with full-name checks, list overflow and rebalance stress, save/restore round trips with multiple zones, immutable page pack/load/search round trips, corrupted magic/header/list-size/page-guard tests, endian fallback fixtures, and stats consistency after insertions/removals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/delta-index.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/delta-index.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/delta-index.h

## Purpose
`delta-index.h` declares the UDS delta-index data structures and APIs for mutable volume/open-chapter indexes, immutable chapter-index pages, iteration, mutation, persistence, sizing, and statistics.

## Important APIs, Types, And Functions
- `struct delta_list` records bit start, bit size, and saved iterator position for one sorted list.
- `struct delta_zone` owns list memory, descriptors, save writer, coding constants, counters, list range, and tag.
- `struct delta_list_save_info` is the packed descriptor for one saved non-empty list.
- `struct delta_index` groups zones and records global list/zone sizing, load counts, mutability, and tag.
- `struct delta_index_page` embeds a one-zone immutable delta index over a page buffer.
- `struct delta_index_entry` is both iterator, found entry, and insertion/removal handle.
- `struct delta_index_stats` aggregates memory/rebalance/record/collision/discard/overflow/list counts.
- APIs cover initialize, page initialize, reset, pack, save/restore, guard lists, search/iterate, get/set payload, put/remove entries, stats, sizing, and logging.

## Control Flow And Data Flow
Callers create a mutable index with a zone/list/memory/coding configuration. They search a list to obtain a `delta_index_entry`, then use that entry as a mutation handle. Immutable pages expose the same search interface but reject mutation through `assert_mutable_entry()` in the implementation.

## State And Persistence Behavior
The header distinguishes mutable and immutable state via `delta_index.mutable` and by whether entry handles point to real `delta_list` descriptors or a temporary page-derived descriptor. Save-info structs and page descriptors are persistent-format contracts. Runtime counters are used for diagnostics and sizing feedback.

## Dependencies And Integration Points
The header depends on cache alignment, numeric/time helpers, config, and I/O factory types. It is included by chapter-index, volume-index, geometry, and other indexer modules.

## Risks
- Consumers must respect the private/public split in `struct delta_index_entry`; private fields are only stable across delta-index API calls.
- Mutating through an entry from an immutable page is invalid and returns bad-state errors.
- `MAX_ZONES` from configuration constrains `load_lists`.
- Tags must match between saved list data and the delta index being restored.

## Test Signals
API-level tests should verify mutable versus immutable operation handling, stats aggregation across zones, save-info packing assumptions, and iterator behavior at start, found, collision, insertion-point, and end-of-list states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/delta-index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/funnel-requestqueue.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/funnel-requestqueue.c

## Purpose
`funnel-requestqueue.c` implements a UDS request queue using funnel queues and a worker thread. It batches request processing with adaptive wait times, prioritizes retry requests over new requests as a hint, and supports dormant sleep/wakeup behavior for idle periods.

## Important APIs, Types, And Functions
- `struct uds_request_queue` contains wait queue, processor callback, main and retry funnel queues, worker thread handle, lifecycle flags, and dormant atomic flag.
- `poll_queues()` checks retry queue before main queue.
- `are_queues_idle()` combines funnel idle checks.
- `dequeue_request()` returns a request, shutdown signal, or sleep indication.
- `wait_for_request()` sleeps either indefinitely in dormant mode or with an hrtimer timeout.
- `request_queue_worker()` processes requests, adapts batching wait time, exits on shutdown, and drains remaining requests.
- Public APIs are `uds_make_request_queue()`, `uds_request_queue_enqueue()`, and `uds_request_queue_finish()`.

## Control Flow And Data Flow
Queue creation allocates the structure, initializes two funnel queues, sets `running`, and creates a named worker thread. Enqueue chooses `retry_queue` if `request->requeued` is set, otherwise `main_queue`, then wakes the worker if the queue is dormant or the request is `unbatched`.

The worker waits for a request, processes it through the caller-supplied `processor`, and tracks batch size. If the previous wait produced too small a batch, it increases the wait time up to `MAXIMUM_WAIT_TIME`, then enters dormant mode. If batches grow too large, it decreases the wait time down to `MINIMUM_WAIT_TIME`. On finish, `running` is cleared with a write barrier, the worker wakes and joins, then remaining queued requests are drained before freeing queue structures.

## State And Persistence Behavior
The queue is transient runtime state. It preserves request objects owned by callers and returns ownership to the processor callback. The `running`, `started`, and `dormant` flags govern worker lifecycle and sleep mode, not persisted state.

## Dependencies And Integration Points
It uses the generic VDO funnel queue plus Linux waitqueue/atomic primitives, UDS thread utilities, logging, and memory allocation. It is created by index session/index code for callback, index, and triage request processing.

## Risks
- Retry-first ordering is not guaranteed because funnel queues can be in transition states.
- Dormant wakeup correctness relies on memory barriers in funnel enqueue and waitqueue sleep preparation.
- `uds_request_queue_finish()` processes remaining requests after shutdown; processors must tolerate finish-time callbacks.
- `wait_event_interruptible*` return values/signals are ignored, which is acceptable only if loop predicates remain authoritative.

## Test Signals
Tests should cover batching adaptation, dormant entry and wakeup, unbatched immediate wakeup, retry queue preference, finish while requests are pending, enqueue/finish races, and processor invocation count/order under concurrent producers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/funnel-requestqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/funnel-requestqueue.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/funnel-requestqueue.h

## Purpose
`funnel-requestqueue.h` declares the UDS request queue abstraction used to serialize and batch index requests on a worker thread.

## Important APIs, Types, And Functions
- `struct uds_request_queue` is opaque.
- `uds_request_queue_processor_fn` is the callback type invoked for each `struct uds_request`.
- `uds_make_request_queue()` creates a named queue with a processor.
- `uds_request_queue_enqueue()` submits a request.
- `uds_request_queue_finish()` stops the worker, drains remaining work, and frees resources.

## Control Flow And Data Flow
Callers allocate/own `struct uds_request` objects containing the queue link and flags such as `requeued` and `unbatched`. Enqueue transfers the request to the worker queue; the processor callback handles it later on the queue thread.

## State And Persistence Behavior
The interface exposes no persistent metadata. It coordinates transient index-session request state and shutdown.

## Dependencies And Integration Points
The header depends on `indexer.h` for `struct uds_request`. It is used by index-session and index code to build serialized request-processing lanes.

## Risks
- Request objects must remain valid from enqueue until processor callback.
- Finish drains pending work, so callers must not free request state prematurely during shutdown.
- The API does not expose cancellation; shutdown semantics are drain-and-process.

## Test Signals
Tests should verify queue creation failure handling, callback invocation after enqueue, requeued/unbatched behavior through the implementation, and safe finish with empty and non-empty queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/funnel-requestqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/geometry.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/geometry.c

## Purpose
`geometry.c` computes and manages `index_geometry`, the derived layout model for a UDS index volume. It maps memory/page/chapter parameters into record capacity, delta-index sizing, persistent volume size, sparse/dense chapter behavior, and reduced-index physical remapping.

## Important APIs, Types, And Functions
- `uds_make_index_geometry()` allocates geometry and computes all derived fields.
- `uds_copy_index_geometry()` clones an existing geometry through the same constructor.
- `uds_free_index_geometry()` releases geometry.
- `uds_map_to_physical_chapter()` maps a virtual chapter number to a physical chapter, including reduced-index remap handling.
- `uds_has_sparse_chapters()` determines whether the active window extends into sparse chapters.
- `uds_is_chapter_sparse()` checks whether one virtual chapter should be treated as sparse.
- `uds_chapters_to_expire()` returns how many chapters to expire after opening a new chapter, with special reduced-index behavior.

## Control Flow And Data Flow
Geometry construction stores direct parameters, derives dense chapter count, records per page/chapter/volume, chapter delta-list coding parameters, index pages per chapter using `uds_get_delta_index_page_count()`, pages per chapter/volume, and bytes per volume including header pages. Hashing and chapter-index code then use these derived bit counts to split record names into list/address/payload fields.

Virtual-to-physical mapping is simple modulo for normal geometry. Reduced geometry handles an eliminated physical chapter 0 by remapping one virtual chapter to a replacement physical chapter and adjusting nearby virtual chapters to avoid the removed slot. Expiration logic normally expires one old chapter after the volume is full, but may expire two or zero around the remapped chapter to keep physical space consistent.

## State And Persistence Behavior
Geometry is runtime state derived from persistent configuration. `remapped_virtual` and `remapped_physical` are persisted by config version 8.02. The derived values control persistent index layout, so a mismatch between saved and requested geometry makes an index unusable.

## Dependencies And Integration Points
The file depends on errors, logging, memory allocation, assertions, delta-index sizing, and indexer constants. It feeds config creation, volume mapping, sparse cache, chapter-index packing/search, and index layout size checks.

## Risks
- Arithmetic uses a mix of `u32`, `u64`, and `size_t`; large sparse configurations need overflow scrutiny.
- `uds_is_reduced_index_geometry()` infers reduced geometry from odd `chapters_per_volume`, so constructors must preserve that convention.
- Remap mapping is nontrivial and off-by-one errors can read/write the wrong physical chapter.
- Delta-list bit calculations must remain aligned with `hash-utils.h`.

## Test Signals
Tests should cover every memory-size geometry produced by config, dense and sparse active windows, reduced-index mapping before/at/after remapped virtual chapters, expiration counts around remap boundaries, and computed page/byte sizes against known fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/geometry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/geometry.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/geometry.h

## Purpose
`geometry.h` defines `struct index_geometry`, layout constants, and helper predicates for UDS index-volume geometry.

## Important APIs, Types, And Functions
- `struct index_geometry` contains direct parameters such as page size, record pages per chapter, total/sparse chapters, remap fields, and derived fields such as pages/records per chapter/volume, delta-list counts, address bits, payload bits, and dense chapter count.
- Constants define record size, default page size, record pages per chapter, chapters per volume, sparse defaults, chapter mean delta bits, default delta-list bit counts, and header pages.
- APIs include make/copy/free, virtual-to-physical chapter mapping, reduced/sparse predicates, sparse-window checks, chapter sparse check, and chapters-to-expire.

## Control Flow And Data Flow
The geometry object is created from configuration and then passed by pointer to index components. Hash utilities use `chapter_delta_list_bits` and `chapter_address_bits`; chapter-index code uses `record_pages_per_chapter`, `delta_lists_per_chapter`, `chapter_mean_delta`, and `chapter_payload_bits`; volume code uses chapter mapping and sparse predicates.

## State And Persistence Behavior
Runtime geometry mirrors persisted configuration. Direct fields and remap fields are saved by config metadata; derived fields must be recomputed consistently after load rather than stored independently.

## Dependencies And Integration Points
The header includes `indexer.h` for record name/data sizes and basic UDS types. It is included broadly by config, chapter-index, hash-utils, volume, sparse-cache, and index layout code.

## Risks
- Changing constants changes index format and capacity.
- Derived fields are assumed internally consistent; callers should not mutate direct fields after construction.
- `records_per_volume` is `u64`, but many page/list fields are `u32`; boundary sizes need testing.

## Test Signals
Tests should verify derived values for default, small, sparse, and reduced geometries, and ensure helper predicates match persisted config semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/geometry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/hash-utils.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/hash-utils.h

## Purpose
`hash-utils.h` provides inline helpers that partition a 16-byte UDS record name into fields used by the volume index, chapter index, and sparse sampling logic.

## Important APIs, Types, And Functions
- Byte layout constants divide the name into volume-index bytes `[0..7]`, chapter-index bytes `[8..13]`, and sampling bytes `[14..15]`.
- `uds_extract_chapter_index_bytes()` reads six bytes as a 48-bit big-endian value.
- `uds_extract_volume_index_bytes()` reads eight big-endian bytes for volume-index addressing.
- `uds_extract_sampling_bytes()` reads two big-endian bytes for sampling.
- `uds_hash_to_chapter_delta_list()` computes the chapter delta-list number from high address bits.
- `uds_hash_to_chapter_delta_address()` computes the chapter-list address from low address bits.
- `uds_name_to_hash_slot()` maps chapter-index bytes modulo a caller-provided slot count.

## Control Flow And Data Flow
Record names are treated as already-hashed names. Callers extract deterministic slices for different index structures. Chapter-index insertion/search uses geometry-derived `chapter_address_bits` and `chapter_delta_list_bits` so each name maps to one list and one address within that list.

## State And Persistence Behavior
The header has no mutable state. Its byte partitioning is a persistent compatibility contract because it determines how record names are placed in saved volume and chapter indexes.

## Dependencies And Integration Points
It depends on unaligned numeric access, `geometry.h`, and `indexer.h`. It is used by chapter-index, volume-index, sparse-cache, and other index lookup paths.

## Risks
- Any change to byte offsets/counts breaks lookup compatibility with existing indexes.
- Big-endian extraction is intentional even though many on-disk structures are little-endian; changing it would remap every record name.
- Geometry bit counts must keep masks within valid shift widths.
- `uds_name_to_hash_slot()` assumes `slot_count` is nonzero.

## Test Signals
Tests should use fixed 16-byte names to verify extracted volume/chapter/sample values, list/address mapping for several geometries, modulo slot mapping, and sparse-sampling decisions in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/hash-utils.h -->
