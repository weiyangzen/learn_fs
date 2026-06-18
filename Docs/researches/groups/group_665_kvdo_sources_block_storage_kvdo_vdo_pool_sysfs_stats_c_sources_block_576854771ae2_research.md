# Group Research: group_665_kvdo_sources_block_storage_kvdo_vdo_pool_sysfs_stats_c_sources_block_576854771ae2

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/pool-sysfs-stats.c -->
# File Research: sources/block-storage/kvdo/vdo/pool-sysfs-stats.c

Read completely: 2065 lines.

This file exposes VDO runtime statistics under the pool `statistics` sysfs directory. It defines `struct pool_stats_attribute`, a read-only sysfs show path, `vdo_pool_stats_sysfs_ops`, and the exported `vdo_pool_stats_attrs[]` table consumed by the pool sysfs setup.

Every attribute read takes `vdo->stats_mutex`, refreshes `vdo->stats_buffer` with `vdo_fetch_statistics()`, calls the attribute-specific printer, and unlocks. The file is mostly a generated-style projection from `struct vdo_statistics` fields to one sysfs file per counter, using `sprintf()` with numeric or string formatting.

Statistics covered include capacity and block usage, recovery counters and mode, packer counters, allocator counters, recovery journal events, slab journal events, slab summary and refcount writes, block map cache/page counters, hash/dedupe lock counters, error counters, instance/VIO counts, dedupe timeout and flush counters, logical block size, memory usage, UDS index counters, and many bio counters split by operation class and stage. Bio groups include incoming, partial incoming, outgoing, metadata, journal, page cache, completed variants, acknowledged variants, partial acknowledged, and in-progress.

Dependencies: Linux kobject/sysfs conventions, `vdo_fetch_statistics()`, `struct vdo_statistics`, `vdo->stats_directory`, `vdo->stats_mutex`, `logger.h`, `dedupe.h`, `statistics.h`, and `pool-sysfs.h`.

Security/reliability notes: attributes are read-only and serialized around a single stats buffer. The implementation assumes all printed values fit sysfs buffers and uses legacy `sprintf()` rather than bounded helpers. The file has no mutation path; correctness depends on `vdo_fetch_statistics()` producing a coherent snapshot while protected by `stats_mutex`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/pool-sysfs-stats.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/pool-sysfs.c -->
# File Research: sources/block-storage/kvdo/vdo/pool-sysfs.c

Read completely: 215 lines.

This file defines the main VDO pool sysfs kobject type and top-level pool attributes. It implements generic `show` and `store` dispatch through `struct pool_attribute`, resolves the enclosing `struct vdo` from `vdo_directory`, and exports `vdo_directory_type`.

Exposed top-level attributes are `compressing`, `discards_active`, `discards_limit`, `discards_maximum`, `instance`, `requests_active`, `requests_limit`, and `requests_maximum`. `discards_limit` is writable; its store path parses an unsigned integer, rejects overly long or invalid input, requires a value of at least 1, and delegates to `set_data_vio_pool_discard_limit()`.

The kobject release callback frees the enclosing `struct vdo` via `UDS_FREE(container_of(directory, struct vdo, vdo_directory))`. The attribute group is installed through `ATTRIBUTE_GROUPS(pool)` and assigned to `vdo_directory_type.default_groups`.

Dependencies: Linux sysfs/kobject APIs, VDO compression state, `data-vio-pool` limit/activity accessors, `dedupe.h`, `vdo.h`, and VDO memory allocation wrappers.

Security/reliability notes: writable parsing for `discards_limit` is narrow and rejects invalid values, but uses `sscanf()` and a fixed length heuristic rather than kernel numeric helpers. The release callback ties sysfs kobject lifetime directly to the `struct vdo` allocation.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/pool-sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/pool-sysfs.h -->
# File Research: sources/block-storage/kvdo/vdo/pool-sysfs.h

Read completely: 19 lines.

This header declares the sysfs integration objects for VDO pool exposure: `vdo_directory_type`, `vdo_pool_stats_sysfs_ops`, and `vdo_pool_stats_attrs[]`.

Dependencies: Linux `struct kobj_type`, `struct sysfs_ops`, and `struct attribute`.

Research notes: this header is the narrow linkage point between the main pool sysfs directory and the separate statistics attribute implementation.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/pool-sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/priority-table.c -->
# File Research: sources/block-storage/kvdo/vdo/priority-table.c

Read completely: 240 lines.

This file implements a bounded-height priority queue for small integer priorities. The table stores one circular Linux list per priority bucket and a 64-bit `search_vector` indicating which buckets are non-empty. The highest-priority non-empty bucket is found with `ilog2(search_vector)`, so enqueue, dequeue, remove, reset, and empty checks are O(1) for priorities 0 through 63.

`make_priority_table()` allocates a flexible-array table with `max_priority + 1` buckets and initializes each list head. `priority_table_enqueue()` moves an embedded `list_head` to the selected bucket tail and sets the bucket bit. `priority_table_dequeue()` removes the oldest entry from the highest priority bucket and clears the bit if the bucket becomes empty. `priority_table_remove()` removes an arbitrary entry and clears the corresponding bucket bit when it removed the last item.

Dependencies: Linux lists, `ilog2`, VDO/UDS allocation and status codes, and assertion helpers.

Security/reliability notes: the implementation asserts but does not hard-fail invalid enqueue priorities in production paths. `priority_table_remove()` cannot prove that an entry belongs to the supplied table; misuse with an entry from another list can corrupt the table state.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/priority-table.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/priority-table.h -->
# File Research: sources/block-storage/kvdo/vdo/priority-table.h

Read completely: 53 lines.

This header documents and declares the bounded integer-priority queue API. It exposes the opaque `struct priority_table` and operations to allocate, free, reset, enqueue, dequeue, remove arbitrary entries, and test for emptiness.

The header emphasizes that queued objects provide their own embedded `struct list_head`, that priorities are small non-negative integers, and that changing an entry's priority is a remove plus enqueue operation.

Dependencies: Linux list API and `__must_check`.

Security/reliability notes: ownership of queued entries remains with callers; freeing/resetting the table does not free entries.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/priority-table.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/radix-sort.c -->
# File Research: sources/block-storage/kvdo/vdo/radix-sort.c

Read completely: 392 lines.

This file implements an unstable in-place American Flag radix sort for fixed-length byte-string keys. It sorts an array of key pointers, not key contents, using an 8-bit radix and insertion sort for small piles.

`make_radix_sorter()` preallocates reusable heap state: histogram bins, pile pointers, insertion-sort task storage, and a bounded task stack sized from the maximum count. `radix_sort()` validates zero-length and small-count cases, rejects counts larger than the preallocated capacity, and then processes sorting tasks iteratively. `measure_bins()` builds a 256-bin histogram for the current byte offset, `push_bins()` sets pile boundaries and schedules follow-up tasks, and the main loop cycles keys into their piles in place. Small piles are handled with insertion sort using `memcmp()` from the active offset.

Dependencies: UDS memory allocation, `memcmp`/`memset`, compiler inline macros, `UDS_SUCCESS`, and `UDS_INVALID_ARGUMENT`.

Security/reliability notes: the sorter relies on the invariant that histogram fields are cleared as each task is consumed; error paths explicitly clear bins before returning. The public API requires all key pointers to reference at least `length` bytes. Sorting is unstable by design.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/radix-sort.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/radix-sort.h -->
# File Research: sources/block-storage/kvdo/vdo/radix-sort.h

Read completely: 55 lines.

This header declares the reusable radix sorter API. `make_radix_sorter()` reserves heap storage for up to a maximum key count, `free_radix_sorter()` releases it, and `radix_sort()` sorts fixed-length key pointers in place without further allocation.

The header documents that heap usage is logarithmically proportional to the maximum key count and that sorting is unstable.

Dependencies: local `compiler.h` for `__must_check`.

Security/reliability notes: callers must size the sorter for the largest count they will pass and must provide valid fixed-length byte arrays for every key.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/radix-sort.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/random.c -->
# File Research: sources/block-storage/kvdo/vdo/random.c

Read completely: 19 lines.

This file provides `random_in_range()` and `random_compile_time_assertions()`. `random_in_range()` returns `lo + random() % (hi - lo + 1)`. The compile-time assertion verifies that `RAND_MAX + 1` is a power of two, matching the masking approach in the header implementation of `random()`.

Dependencies: `random.h` and `permassert.h`.

Security/reliability notes: `random_in_range()` has modulo bias unless the range evenly divides `RAND_MAX + 1`, and it assumes `hi >= lo`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/random.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/random.h -->
# File Research: sources/block-storage/kvdo/vdo/random.h

Read completely: 55 lines.

This header wraps Linux kernel randomness for the VDO/UDS code. It declares `random_in_range()` and `random_compile_time_assertions()`, defines `fill_randomly()` as a direct `get_random_bytes()` wrapper, defines `RAND_MAX` as `2147483647`, and implements `random()` by filling a `long` and masking it with `RAND_MAX`.

Dependencies: Linux `get_random_bytes()`, local compiler/type definitions.

Security/reliability notes: the API mimics C library `random()`/`RAND_MAX` naming inside kernel code. The masked `random()` only returns 31 random bits even when `long` is wider.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/random.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/read-only-notifier.c -->
# File Research: sources/block-storage/kvdo/vdo/read-only-notifier.c

Read completely: 563 lines.

This file implements VDO-wide read-only mode notification across base threads. The notifier records the first unrecoverable error, propagates per-thread `is_read_only` state, calls registered thread-local listeners, and supports admin-thread barriers that temporarily disallow read-only entry while shutdown or superblock updates need to avoid races.

The core state machine uses atomics with states `MAY_NOTIFY`, `NOTIFYING`, `MAY_NOT_NOTIFY`, and `NOTIFIED`, plus `read_only_error`. `vdo_enter_read_only_mode()` marks the calling thread read-only, records the first error with compare-exchange, and starts notification if notifications are allowed. `make_thread_read_only()` walks all configured threads, skips the dedupe thread, marks each thread read-only, and invokes registered listeners sequentially on the target thread. Completion returns to the admin thread through `finish_entering_read_only_mode()`.

`vdo_wait_until_not_entering_read_only_mode()` is an admin-thread barrier that waits for in-progress notifications and switches the state to disallow new ones. `vdo_allow_read_only_mode_entry()` re-enables notification and starts a pending notification if an error arrived while notification was disallowed. `vdo_register_read_only_listener()` registers listener callbacks per thread and rejects dedupe-thread listeners.

Dependencies: VDO completion framework, thread configuration, callback thread IDs, atomic operations and memory barriers, logger, allocation wrappers, and `struct vdo`.

Security/reliability notes: correctness depends on admin-thread-only calls for wait/allow paths and on per-thread access discipline for `thread_data`. The code deliberately has non-simultaneous read-only visibility across threads. Listener registration is singly linked and not synchronized; it is intended for setup-time use.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/read-only-notifier.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/read-only-notifier.h -->
# File Research: sources/block-storage/kvdo/vdo/read-only-notifier.h

Read completely: 58 lines.

This header declares the read-only notifier API and documents its purpose: propagating unrecoverable VDO errors to base threads, persisting read-only state through the superblock path, and allowing shutdown code to wait until notifications are complete.

It defines the `vdo_read_only_notification` callback signature and declares creation, destruction, wait/disallow, allow, enter-read-only, state query, and listener registration functions.

Dependencies: VDO completion types, thread configuration, `struct vdo`, and `thread_id_t` through included headers.

Research notes: the API separates `vdo_is_read_only()` for thread-local state from `vdo_is_or_will_be_read_only()` for checking whether read-only entry has begun globally.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/read-only-notifier.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/read-only-rebuild.c -->
# File Research: sources/block-storage/kvdo/vdo/read-only-rebuild.c

Read completely: 495 lines.

This file coordinates rebuilding VDO metadata to clear read-only mode or support upgrade rebuilds. It loads the recovery journal, extracts valid journal increment entries, replays them into the block map, rebuilds reference counts from the resulting block map, drains the slab depot to save rebuilt state, and reinitializes the recovery journal.

`struct read_only_rebuild_completion` owns the rebuild completion, a subtask completion, loaded journal bytes, extracted numbered block mappings, head/tail sequence numbers, and rebuilt usage counts. `vdo_launch_rebuild()` logs the rebuild type, increments read-only recovery statistics when appropriate, allocates the completion object, and starts by loading the slab depot. The subtask then loads the recovery journal from logical zone 0.

`apply_journal_entries()` finds valid journal head/tail blocks, extracts valid increment entries, enables block-map page-cache rebuild mode to suppress expected errors, and calls `vdo_recover_block_map()`. `extract_journal_entries()` scans exact journal blocks from head to tail, validates block headers and sectors, clamps claimed entry counts, and appends only valid increment operations. After block-map recovery, `vdo_rebuild_reference_counts()` rebuilds refcounts and records logical/block-map usage counts. `finish_rebuild()` updates recovery journal state with the new tail and usage counts.

Dependencies: recovery journal loading/scanning, packed journal sector layout, block map recovery, reference-count rebuild, slab depot load/drain, VDO completion framework, page-cache rebuild mode, and VDO component states.

Security/reliability notes: damaged entries are ignored during read-only recovery, but invalid allocation or structural errors abort the rebuild. The loaded journal buffer and extracted entry array are freed in all normal completion paths. The rebuild assumes logical zone 0 context for journal loading and replay.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/read-only-rebuild.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/read-only-rebuild.h -->
# File Research: sources/block-storage/kvdo/vdo/read-only-rebuild.h

Read completely: 14 lines.

This header declares the single read-only rebuild entry point, `vdo_launch_rebuild(struct vdo *vdo, struct vdo_completion *parent)`.

Dependencies: VDO completion and `struct vdo`.

Research notes: implementation details are intentionally private to `read-only-rebuild.c`; callers only launch the asynchronous rebuild and wait on the supplied completion.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/read-only-rebuild.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/record-page.c -->
# File Research: sources/block-storage/kvdo/vdo/record-page.c

Read completely: 113 lines.

This file encodes and searches UDS record pages. `encode_record_page()` builds an array of pointers to chapter records, sorts the pointers by chunk name using the volume's radix sorter, and copies records into the output page in heap-ordered binary search tree layout. `encode_tree()` performs the in-order traversal that converts the sorted array into tree order.

`search_record_page()` treats a record page as an array of `struct uds_chunk_record`, compares the requested chunk name against records starting at heap index 0, and walks left or right with child indexes `2N + 1` and `2N + 2`. When found, it optionally copies the record metadata to the caller.

Dependencies: `volume->geometry`, `volume->record_pointers`, `volume->radix_sorter`, `radix_sort()`, UDS chunk record/name/data definitions, `memcmp`, `memcpy`, and static assertions on record layout.

Security/reliability notes: encoding assumes `volume->record_pointers` is sized for `records_per_page` and that chunk name is at offset 0 in `struct uds_chunk_record`. Search trusts geometry/page consistency.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/record-page.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/record-page.h -->
# File Research: sources/block-storage/kvdo/vdo/record-page.h

Read completely: 42 lines.

This header declares record-page encoding and lookup helpers for UDS volume chapters. `encode_record_page()` converts a record array into on-disk page layout, and `search_record_page()` finds chunk metadata by name in an encoded page.

Dependencies: `common.h`, `volume.h`, UDS chunk record/name/data types, and volume geometry.

Research notes: the public contract makes record pages an encoded searchable structure rather than a raw sorted array.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/record-page.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal-block.c -->
# File Research: sources/block-storage/kvdo/vdo/recovery-journal-block.c

Read completely: 396 lines.

This file manages one in-memory recovery journal block and its on-disk packed representation. It allocates the block buffer and metadata VIO, initializes block headers/sectors, queues data VIOs waiting for journal entries, packs queued entries into sectors, and submits the journal block write.

`vdo_initialize_recovery_block()` clears the block buffer, fills a packed header with metadata type, nonce, recovery count, sequence number, check byte, and usage counters, sets the on-disk circular block number, and initializes sector 1 as the active sector. Sector 0 is the header; subsequent sectors hold packed entries with per-sector check/recovery bytes.

`vdo_enqueue_recovery_block_entry()` queues a data VIO for the next commit, increments entry counts, and updates journal started counters. `add_queued_recovery_entries()` drains entry waiters, builds `struct recovery_journal_entry` values from each data VIO operation and tree-lock slot, packs them into the active sector, tracks FUA requirements for data increments, moves VIOs to commit waiters, and advances sectors when full. `vdo_commit_recovery_block()` validates commit readiness, translates the journal partition block to PBN, updates header heads and entry count, sets write flags including preflush/sync and optional FUA, and submits the metadata VIO.

Dependencies: data VIOs, tree locks, packed recovery journal format, metadata VIO submission, partition translation, wait queues, recovery journal state, and read-only notifier checks.

Security/reliability notes: commit is refused when the journal is read-only, already committing, or has no queued entries. The write path always uses a flush because journal ordering protects data references and previous mappings. If queuing to commit waiters fails, the affected data VIO is continued with the error.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal-block.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal-block.h -->
# File Research: sources/block-storage/kvdo/vdo/recovery-journal-block.h

Read completely: 128 lines.

This header defines `struct recovery_journal_block`, the in-memory state for a recovery journal tail block. Fields include list and write-waiter nodes, owning journal, packed block buffer, active sector pointer, metadata VIO, sequence/block numbers, commit flags, entry counters, and wait queues for entries and commit completion.

It provides inline helpers to recover a block from its list entry and test whether a block is dirty, empty, or full. Public functions cover allocation, free, initialization, entry enqueue, block commit, dumping, and commit-readiness checks.

Dependencies: packed recovery journal block format, `struct recovery_journal`, VIO/data VIO forward declarations through included headers, Linux bio callback type, wait queues, and VDO types.

Security/reliability notes: `vdo_is_recovery_block_full(NULL)` returns true, letting callers treat absent active blocks as needing advancement.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal-block.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal-entry.h -->
# File Research: sources/block-storage/kvdo/vdo/recovery-journal-entry.h

Read completely: 110 lines.

This header defines the logical and packed recovery journal entry formats. A logical entry records the block-map slot being changed, the target data location mapping, and the journal operation. The packed on-disk entry uses bitfields for operation, slot, and the high nibble of the block-map-page PBN, a little-endian low 32-bit PBN word, and a packed block-map entry.

`vdo_pack_recovery_journal_entry()` converts a logical entry into the compact on-disk layout. `vdo_unpack_recovery_journal_entry()` reconstructs the operation, block-map slot, block-map page PBN, and data location.

Dependencies: block-map entries, journal operation enum, journal point/types, endian conversion helpers, and packed layout assumptions.

Security/reliability notes: the format stores a 36-bit block-map page PBN and a 10-bit slot. Correctness depends on callers validating bounds before trusting unpacked entries.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal-entry.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal-format.c -->
# File Research: sources/block-storage/kvdo/vdo/recovery-journal-format.c

Read completely: 164 lines.

This file encodes and decodes the recovery journal component state stored in the VDO superblock. It defines `VDO_RECOVERY_JOURNAL_HEADER_7_0` with component id `VDO_RECOVERY_JOURNAL`, version 7.0, and payload size `sizeof(struct recovery_journal_state_7_0)`.

`vdo_get_recovery_journal_encoded_size()` returns header plus payload size. The encode path writes the component header and three little-endian 64-bit values: journal start sequence, logical blocks used, and block-map data blocks. The decode path validates the header and reads the same fields back, asserting the decoded payload size matches the header. `vdo_get_journal_operation_name()` maps journal operation enum values to diagnostic strings.

Dependencies: VDO buffer encoding helpers, component header validation, status codes, recovery journal format definitions, and packed journal operation enum.

Security/reliability notes: decode validates component identity/version/size before accepting state. Operation names include an unknown fallback for diagnostics.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal-format.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal-format.h -->
# File Research: sources/block-storage/kvdo/vdo/recovery-journal-format.h

Read completely: 82 lines.

This header defines the superblock-encoded recovery journal state: `journal_start`, `logical_blocks_used`, and `block_map_data_blocks`. It declares the versioned component header, encode/decode helpers, encoded-size helper, and journal operation name helper.

It also provides inline validation for packed journal sectors by comparing sector check byte and recovery count against the unpacked block header, and inline circular journal block-number computation using `sequence_number & (journal_size - 1)`.

Dependencies: buffer/header APIs, packed recovery journal block definitions, and VDO numeric types.

Security/reliability notes: the block-number helper assumes the journal size is a power of two.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal-format.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal.c -->
# File Research: sources/block-storage/kvdo/vdo/recovery-journal.c

Read completely: 1539 lines.

This file implements the VDO recovery journal state machine. The journal is a circular on-disk log of block-map and reference-count changes not yet stably reflected in the block map or slab journals. It manages in-memory tail blocks, queues data VIOs needing journal entries, writes journal blocks with ordering flushes, tracks lock counts that prevent premature reaping, advances block-map and slab-journal heads, handles drain/resume, and transitions to read-only on unrecoverable errors.

Construction in `vdo_decode_recovery_journal()` allocates the journal, initializes lists and wait queues, records nonce/recovery count/size/state, creates tail buffers with `vdo_make_recovery_block()`, creates the lock counter, creates a flush VIO, registers a read-only listener, and makes the journal thread. `vdo_open_recovery_journal()` links the slab depot and block map and enters normal operation. `vdo_record_recovery_journal()` records either the saved tail or the earliest active head depending on admin state.

Entry assignment is split between decrement and increment queues. `vdo_add_recovery_journal_entry()` enqueues data VIOs, advances the append point, and calls `assign_entries()`. Decrements are assigned first so reserved space is protected for cleanup entries. `prepare_to_assign_entry()` checks available journal space, advances to a free tail block when needed, rejects disk-full cases, and initializes lock counts for newly used blocks. `assign_entry()` updates logical-block or block-map usage counters, maintains pending decrement counts, records each VIO's journal point, enqueues the VIO into the active block, and schedules full blocks for writing.

Write policy is handled by `write_blocks()`: if writes are pending it waits; otherwise it writes all queued full blocks and, if needed to ensure progress, writes a non-full active block. Completion updates committed counters, releases VIO waiters in order, schedules rewrites for blocks that accumulated more entries while committing, recycles fully committed blocks, and checks drain completion. Write or flush errors record metadata I/O errors and enter read-only mode.

Reaping uses a lock counter with separate logical and physical zone references. `reap_recovery_journal()` advances candidate block-map and slab-journal heads only up to acknowledged writes and only across unlocked blocks, then submits a flush before committing the new heads. `finish_reaping()` updates official heads, restores available entry space, checks slab-journal commit thresholds, and resumes entry assignment. The journal asks the slab depot to commit old slab journal tail blocks when the active length exceeds two thirds of journal size.

Drain/resume paths use `admin_state`. `vdo_drain_recovery_journal()` starts draining for suspend/save, and completion waits for no reaping, no block waiters, no entry waiters, and a suspended lock counter. Saving recycles a clean active block. `vdo_resume_recovery_journal()` resumes only from quiescent state, rejects read-only mode, reinitializes state after saved drains, resumes the lock counter, and reaps if notifications were missed.

Dependencies: recovery journal block management, packed journal formats, lock counters, wait queues, VDO admin states, data VIOs, metadata VIO submission/flushes, block map era advancement, slab depot/slab journal commit hooks, read-only notifier, thread IDs, and statistics structures.

Security/reliability notes: the implementation is strongly thread-affine to the journal thread and asserts that affinity on mutating paths. Journal overflow at sequence numbers `>= 1 << 48`, allocation/queueing failures, no-space-for-decrement conditions, metadata write failures, and flush failures force read-only mode. Correct recovery depends on ordered flush semantics, accurate lock-counter releases from block-map/slab-journal users, and power-of-two journal sizing.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal.h -->
# File Research: sources/block-storage/kvdo/vdo/recovery-journal.h

Read completely: 313 lines.

This header documents the recovery journal design and defines `struct recovery_journal`. The long design comment explains the circular on-disk log, the `head`/`tail`/active interval, the in-memory tail block rings, the write/commit flow for VIO waiters, and the lock-counter scheme that prevents journal blocks from being reaped while referenced by active VIOs, dirty block-map pages, or slab-journal replay needs.

`struct recovery_journal` contains thread and component pointers, increment/decrement waiter queues, available-space accounting, pending decrement tracking, read-only notifier, admin state, partition pointer, block-map and slab-journal heads, last acknowledged write, tail/append/commit points, nonce/recovery count, entry capacity, free/active block lists, pending write queue, reap heads and block numbers, flush VIO, on-disk size, logical/block-map usage counters, pending write count, slab-journal commit threshold, statistics, and lock counter.

The header provides inline helpers for circular block-number mapping, check-byte computation, and increment-operation classification. It declares lifecycle, state recording, post-recovery/rebuild initialization, open, entry add, lock-reference acquire/release, drain/resume, stats, and dump APIs.

Dependencies: admin state, completion, flush/journal point/lock counter types, read-only notifier, recovery journal format, VDO layout/types, wait queues, and statistics.

Security/reliability notes: comments identify the invariants the implementation relies on: monotonic sequence numbers, reserved circular-log space, per-entry and per-page lock references, and thread-affine journal mutation.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-journal.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-utils.c -->
# File Research: sources/block-storage/kvdo/vdo/recovery-utils.c

Read completely: 283 lines.

This file provides recovery-time utilities for loading and scanning the recovery journal. `vdo_load_recovery_journal()` allocates a full journal-sized buffer, creates enough multi-block metadata VIOs to read the journal partition in chunks of at most `MAX_BLOCKS_PER_VIO`, submits reads, and completes the parent when all reads finish. `journal_loader` owns the parent completion, original callback thread, VIO array, and completion counts.

`vdo_find_recovery_journal_head_and_tail()` scans every journal block read from disk, unpacks each header, checks that it is congruent with its circular offset, nonce, recovery count, and metadata type, then finds the highest valid sequence number plus maximum block-map and slab-journal head values. It returns false if no valid entries newer than the current journal tail are found.

`vdo_validate_recovery_journal_entry()` checks unpacked entries against VDO bounds: block-map page PBN, slot range, valid mapped location, physical data block membership, and special restrictions for block-map increment entries, which cannot be compressed or point at the zero block.

Dependencies: metadata VIO allocation/submission, partition layout offsets, packed recovery journal block headers, recovery journal entry unpacking, slab depot physical-block checks, VDO config bounds, completion framework, and metadata I/O error recording.

Security/reliability notes: a loader allocation failure after the journal data buffer is allocated finishes the parent without freeing that buffer in this function; ownership expectations around `journal_data_ptr` matter on that path. Scan logic ignores stale/unformatted/misplaced blocks and only trusts headers matching nonce and recovery count.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-utils.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-utils.h -->
# File Research: sources/block-storage/kvdo/vdo/recovery-utils.h

Read completely: 90 lines.

This header declares recovery utility helpers and provides inline accessors/validators for loaded journal data. `vdo_get_recovery_journal_block_header()` maps a sequence number to the corresponding block offset in a loaded journal buffer. `vdo_is_valid_recovery_journal_block()` validates metadata type, nonce, and recovery count. `vdo_is_exact_recovery_journal_block()` additionally requires an exact sequence number match.

Public declarations cover asynchronous journal loading, head/tail discovery, and recovery journal entry validation.

Dependencies: constants, packed recovery journal block headers, recovery journal entries, recovery journal state, and VDO types.

Security/reliability notes: buffer indexing uses the journal's circular block-number helper, so callers must pass a buffer sized for the full journal and a journal with valid power-of-two sizing.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/recovery-utils.h -->