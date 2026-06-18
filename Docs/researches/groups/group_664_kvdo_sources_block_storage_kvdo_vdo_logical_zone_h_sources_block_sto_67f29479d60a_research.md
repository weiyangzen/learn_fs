# Group Research: group_664_kvdo_sources_block_storage_kvdo_vdo_logical_zone_h_sources_block_sto_67f29479d60a

Scope verified against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/logical-zone.h -->
# File Research: sources/block-storage/kvdo/vdo/logical-zone.h

## Purpose
Defines the logical-zone layer data structures and exported operations for per-logical-zone VDO write/map coordination.

## Key Structures
- `struct logical_zone`: owns per-zone completion state, LBN operation map, block map zone pointer, flush generation accounting, write VIO list, admin state, allocation selector, and ring-style `next` pointer.
- `struct logical_zones`: container for all logical zones, linked to the parent `vdo` and admin `action_manager`.

## API Surface
Exports construction/destruction, drain/resume, flush generation increment/lock acquire/release, and diagnostic dump functions:
- `vdo_make_logical_zones`
- `vdo_free_logical_zones`
- `vdo_drain_logical_zones`
- `vdo_resume_logical_zones`
- `vdo_increment_logical_zone_flush_generation`
- `vdo_acquire_flush_generation_lock`
- `vdo_release_flush_generation_lock`
- `vdo_dump_logical_zone`

## Integration Notes
The header depends on `admin-state.h`, `int-map.h`, and VDO core types. It separates logical operation tracking by LBN from physical allocation, while retaining an `allocation_selector` used to choose physical zones.

## Concurrency / State
`oldest_active_generation` is mutated only on the logical-zone thread but queried from the flusher thread, so readers must respect the implementation’s cross-thread visibility assumptions.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/logical-zone.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/memory-alloc.c -->
# File Research: sources/block-storage/kvdo/vdo/memory-alloc.c

## Purpose
Implements UDS/VDO memory allocation wrappers, allocation-thread tracking, kmalloc/vmalloc selection, memory usage accounting, and leak reporting.

## Behavior
- Tracks threads allowed to allocate freely through `allocating_threads`.
- Uses `memalloc_noio_save()` for allocation contexts not registered as allocation-allowed.
- Chooses `kmalloc` for allocations up to `PAGE_SIZE` when alignment is below a page; uses `__vmalloc` otherwise.
- Zeroes allocated memory via GFP flags.
- Retries briefly on allocation failure to let reclaim make progress.
- Tracks actual allocated size using `ksize()` for kmalloc and `PAGE_ALIGN(size)` for vmalloc.

## Key Functions
- `uds_allocate_memory`: main checked allocator with error logging and accounting.
- `uds_allocate_memory_nowait`: GFP_NOWAIT zeroed kmalloc path.
- `uds_free_memory`: dispatches to `vfree` or `kfree` and decrements stats.
- `uds_reallocate_memory`: allocate-copy-free realloc wrapper.
- `uds_duplicate_string`: checked string duplication.
- `uds_memory_init` / `uds_memory_exit`: initialize registry/stats and report leaks.
- `get_uds_memory_stats` / `report_uds_memory_usage`: expose current and peak tracked memory.

## Integration Notes
Used broadly through macros in `memory-alloc.h`. Vmalloc accounting uses a linked list of `vmalloc_block_info`, allocated through the same wrapper, so recursive accounting is intentional.

## Risks / Edge Cases
- Vmalloc tracking removal is O(number of vmalloc blocks), acceptable per file comments but relevant for heavy vmalloc churn.
- `uds_reallocate_memory` relies on caller-provided `old_size`; an incorrect old size can truncate or over-copy relative to the original allocation’s logical size.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/memory-alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/memory-alloc.h -->
# File Research: sources/block-storage/kvdo/vdo/memory-alloc.h

## Purpose
Declares the UDS allocation API and provides typed allocation macros used throughout the VDO/UDS code.

## Key API / Macros
- `uds_allocate_memory`, `uds_free_memory`, `uds_reallocate_memory`, `uds_duplicate_string`.
- `UDS_ALLOCATE`: typed zeroed allocation.
- `UDS_ALLOCATE_EXTENDED`: allocates a primary struct plus trailing array storage.
- `UDS_ALLOCATE_IO_ALIGNED`: page-aligned allocation for I/O buffers.
- `uds_allocate_cache_aligned`: cache-line-aligned allocation helper.
- `UDS_FORGET`: NULLs a pointer and returns its previous value for ownership transfer.
- `UDS_FREE`: wrapper around `uds_free_memory`.
- `uds_register_allocating_thread` / `uds_unregister_allocating_thread`.
- `get_uds_memory_stats` / `report_uds_memory_usage`.

## Safety Notes
`uds_do_allocation` checks multiplication overflow and intentionally forces an impossible allocation size on overflow so callers get an out-of-memory style failure. `UDS_ALLOCATE_EXTENDED` uses `STATIC_ASSERT` to enforce compatible alignment between the header type and trailing element type.

## Integration Notes
This header is the central memory management interface. It pulls in compiler helpers, CPU cache-line size, assertions, type definitions, page size, and thread registry support.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/memory-alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/messageStats.c -->
# File Research: sources/block-storage/kvdo/vdo/messageStats.c

## Purpose
Serializes a fetched `struct vdo_statistics` snapshot into a text buffer.

## Structure
The file is a hierarchy of writer helpers:
- Primitive writers: `write_uint64_t`, `write_uint32_t`, `write_block_count_t`, `write_string`, `write_bool`, `write_uint8_t`.
- Nested statistics writers for allocator, commits, recovery journal, packer, slab journal, slab summary, ref counts, block map, hash lock, errors, bios, memory usage, index, and full VDO stats.
- Public entry point: `vdo_write_stats`.

## Output Model
Writers emit a brace-delimited, field-name text representation such as `field : value`. Each helper takes `char **buf` and `unsigned int *maxlen`, writes with `scnprintf`, advances the buffer pointer, decrements remaining length, and returns `VDO_UNEXPECTED_EOF` on truncation/error.

## Data Coverage
`write_vdo_statistics` serializes core capacity, logical/physical block counts, recovery state, mode, packer stats, allocator stats, journal stats, block-map stats, dedupe/hash-lock stats, error stats, VIO counts, flush counts, logical block size, many bio counters, memory usage, and UDS index stats.

## Integration Notes
`vdo_write_stats` allocates a temporary `struct vdo_statistics`, calls `vdo_fetch_statistics`, serializes it, then frees it. This file depends on `statistics.h`, `thread-device.h`, `vdo.h`, and the allocation wrappers.

## Risk Note
The truncation pattern compares `count` after decrementing `*maxlen`; that can report `VDO_UNEXPECTED_EOF` when a write consumes more than half of the remaining buffer, even if `scnprintf` did not truncate. If this file is behaviorally important, that check deserves review against intended kernel `scnprintf` semantics.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/messageStats.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/messageStats.h -->
# File Research: sources/block-storage/kvdo/vdo/messageStats.h

## Purpose
Declares the public stats serialization entry point.

## API
- `int vdo_write_stats(struct vdo *vdo, char *buf, unsigned int maxlen);`

## Integration Notes
Includes `types.h` for the opaque VDO type definitions. The implementation lives in `messageStats.c`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/messageStats.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/murmurhash3.c -->
# File Research: sources/block-storage/kvdo/vdo/murmurhash3.c

## Purpose
Kernel implementation of MurmurHash3 x64 128-bit hashing, adapted for VDO/UDS use and exported as a symbol.

## Key Functions
- `murmurhash3_128`: computes a 128-bit hash from key bytes, length, and seed.
- `rotl64`, `getblock64`, `putblock64`, `fmix64`: internal helpers for rotation, endian-aware block access, and final avalanche mixing.

## Behavior
Processes 16-byte blocks into two 64-bit hash lanes, handles remaining tail bytes through fallthrough switch cases, finalizes with length mixing and `fmix64`, then writes two 64-bit output words in endian-correct form.

## Integration Notes
Includes `<linux/murmurhash3.h>` and exports `murmurhash3_128` with `EXPORT_SYMBOL`. Endianness is resolved at compile time for little- and big-endian systems.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/murmurhash3.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/num-utils.h -->
# File Research: sources/block-storage/kvdo/vdo/num-utils.h

## Purpose
Small utility umbrella header for numeric helpers.

## Contents
Includes:
- `numeric.h`
- `types.h`
- `<linux/log2.h>`
- `<linux/math.h>`

## Integration Notes
Marked as a candidate for an eventual utility library. It provides no declarations itself; it centralizes commonly needed numeric includes.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/num-utils.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/numeric.h -->
# File Research: sources/block-storage/kvdo/vdo/numeric.h

## Purpose
Provides inline little-endian encode/decode helpers for unaligned numeric fields.

## Key Helpers
- 64-bit signed/unsigned: `decode_int64_le`, `encode_int64_le`, `decode_uint64_le`, `encode_uint64_le`.
- 32-bit signed/unsigned: `decode_int32_le`, `encode_int32_le`, `decode_uint32_le`, `encode_uint32_le`.
- 16-bit unsigned: `decode_uint16_le`, `encode_uint16_le`.

## Behavior
Each decoder reads from `buffer + *offset`, stores the decoded value, and advances `*offset` by the type size. Each encoder writes to `data + *offset` and advances likewise.

## Integration Notes
Uses Linux unaligned little-endian primitives from `<asm/unaligned.h>`. Declares `numeric_compile_time_assertions()` as a compile-time type-size assertion hook.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/numeric.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/open-chapter.c -->
# File Research: sources/block-storage/kvdo/vdo/open-chapter.c

## Purpose
Implements the in-memory “open chapter” of the UDS index, where newest chunk records are staged before being closed into indexed chapter pages.

## Core Model
Each index zone has an `open_chapter_zone`:
- Records are stored 1-based in insertion order.
- A hash table maps chunk names to record numbers.
- Record number 0 means empty slot.
- Deleted records are marked with a flag, not physically removed.
- Hash slots are sized as a power of two above capacity times load ratio.

## Key Operations
- `make_open_chapter`: validates geometry, sizes hash slots, allocates zone and cache-aligned records.
- `reset_open_chapter`: clears records and slots.
- `probe_chapter_slots`: name lookup with quadratic probing.
- `search_open_chapter`: returns metadata if a live record exists.
- `put_open_chapter`: updates existing metadata or appends a new record.
- `remove_from_open_chapter`: marks matching record deleted.
- `close_open_chapter`: builds a delta chapter index and writes chapter contents.
- `save_open_chapters` / `load_open_chapters`: versioned persistence of open-chapter records.
- `compute_saved_open_chapter_size`: computes saved representation size.

## Close / Save Behavior
When closing, records from zones are interleaved to preserve temporal locality. Deleted or unused records are replaced with a valid fill record so record pages contain valid records. Live records are inserted into the open chapter index by page number.

## Persistence
Saved data starts with magic `ALBOC`, version `02.00`, a little-endian record count, then live `uds_chunk_record` entries. Load redistributes records by current zone mapping and can discard overflow in zones that become too full.

## Integration Notes
Depends on geometry, volume writing, open chapter index, volume index zone selection, buffered readers/writers, and numeric unaligned helpers.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/open-chapter.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/open-chapter.h -->
# File Research: sources/block-storage/kvdo/vdo/open-chapter.h

## Purpose
Declares the open-chapter structures and operations for UDS index staging.

## Key Definitions
- `OPEN_CHAPTER_RECORD_NUMBER_BITS = 23`.
- `OPEN_CHAPTER_MAX_RECORD_NUMBER`.
- `struct open_chapter_zone_slot`: packed bitfield containing record number and deleted flag.
- `struct open_chapter_zone`: per-zone capacity, size, deleted count, records array, slot count, and flexible slot table.

## API Surface
Construction, reset, lookup, insertion, deletion, free, close, save/load, and saved-size computation are declared.

## Integration Notes
Includes chapter index, geometry, index, and volume headers. The record array is 1-based by contract, matching the implementation’s use of zero as “empty slot.”
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/open-chapter.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/packed-recovery-journal-block.h -->
# File Research: sources/block-storage/kvdo/vdo/packed-recovery-journal-block.h

## Purpose
Defines in-memory and packed on-disk layouts for VDO recovery journal blocks and sectors.

## Key Structures
- `struct recovery_block_header`: native CPU representation.
- `struct packed_journal_header`: packed little-endian on-disk header.
- `struct packed_journal_sector`: per-sector check/recovery bytes, entry count, and flexible packed entries.

## Constants
- `RECOVERY_JOURNAL_ENTRIES_PER_BLOCK = 311`.
- `RECOVERY_JOURNAL_ENTRIES_PER_SECTOR`: derived from sector size and entry size.
- `RECOVERY_JOURNAL_ENTRIES_PER_LAST_SECTOR`: remainder for the last sector.

## Inline Helpers
- `vdo_get_journal_block_sector`: computes a sector pointer from the packed header and 1-based sector number.
- `vdo_pack_recovery_block_header`: CPU-to-little-endian conversion.
- `vdo_unpack_recovery_block_header`: little-endian-to-CPU conversion.

## Integration Notes
Includes numeric helpers, constants, recovery journal entry definitions, and VDO types. The packed structures are ABI/on-disk format sensitive.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/packed-recovery-journal-block.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/packed-reference-block.h -->
# File Research: sources/block-storage/kvdo/vdo/packed-reference-block.h

## Purpose
Defines the on-disk packed layout for reference count blocks.

## Key Definitions
- `typedef uint8_t vdo_refcount_t`.
- Special values:
  - `EMPTY_REFERENCE_COUNT = 0`
  - `MAXIMUM_REFERENCE_COUNT = 254`
  - `PROVISIONAL_REFERENCE_COUNT = 255`

## Layout
- `COUNTS_PER_SECTOR`: sector capacity after `packed_journal_point`.
- `COUNTS_PER_BLOCK`: sector count times VDO sectors per block.
- `struct packed_reference_sector`: journal commit point plus refcount array.
- `struct packed_reference_block`: array of packed sectors.

## Integration Notes
Used by block reference management and PBN lock logic. The provisional value is referenced by write/allocation paths to reserve references before they become durable.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/packed-reference-block.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/packer.c -->
# File Research: sources/block-storage/kvdo/vdo/packer.c

## Purpose
Implements the compressed block packer, which batches multiple compressed `data_vio` fragments into a single compressed block write.

## Core Model
- Maintains multiple `packer_bin` instances sorted by ascending `free_space`.
- Each bin holds pending compressed VIO fragments.
- First-best-fit bin selection is used.
- A special canceled bin holds canceled VIOs waiting for rendezvous with canceling VIOs.

## Key Flow
- `vdo_attempt_packing`: validates packer-thread context, increments in-packer stats, checks admin state/flush generation, selects a bin, transitions VIO to packing, and enqueues it.
- `add_data_vio_to_packer_bin`: inserts VIO, updates free space, writes bin if full, restores sort order.
- `write_bin`: picks an agent VIO, packs client fragments into the agent’s compressed block, aborts if only one fragment, prepares and submits compressed write otherwise.
- `finish_compressed_write`: releases clients first, shares the compressed write PBN lock, then releases the agent.
- `handle_compressed_write_error`: moves to allocated-zone thread if needed, updates error stats, releases clients/agent back to the normal write path.

## Administrative Operations
- `vdo_flush_packer`: writes all non-empty bins.
- `vdo_increment_packer_flush_generation`: increments generation and flushes older VIOs.
- `vdo_drain_packer`: starts drain and prevents new packer entries.
- `vdo_resume_packer`: resumes after suspension.
- `vdo_dump_packer`: logs state and non-empty bins.

## Statistics
`vdo_get_packer_statistics` returns READ_ONCE copies of fragment/block counters. Writes use `WRITE_ONCE`.

## Integration Notes
Integrates with compression state, allocation, compressed block layout, VIO I/O submit, read-only notifier, admin state, and PBN locks.

## Risks / Invariants
Correctness depends on packer-thread serialization and the cancellation rendezvous rules documented around VDO-2809/VDO-2826. A VIO in `VIO_PACKING` must be placed in a bin before another packer-thread request can observe it.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/packer.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/packer.h -->
# File Research: sources/block-storage/kvdo/vdo/packer.h

## Purpose
Declares compressed block packer structures and APIs.

## Key Structures
- `struct packer_bin`: list node, slot count, free space, flexible `incoming` VIO array.
- `struct packer`: callback thread id, bin count, usable compressed block size, max slots, sorted bin list, canceled bin, flush generation, admin state, and packer statistics.

## API Surface
Construction/destruction, compressibility test, stats snapshot, packing attempt, flush, lock-holder removal, flush generation increment, drain/resume, and dump functions.

## Integration Notes
The header documents packer batching semantics in detail: the first uncanceled VIO becomes the write agent, other fragments are packed into its block, and the agent shares its PBN lock with the clients after successful write.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/packer.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/page-cache.c -->
# File Research: sources/block-storage/kvdo/vdo/page-cache.c

## Purpose
Implements UDS volume page cache management, queued reads, LRU victim selection, and safe invalidation around concurrent zone searches.

## Core Structures Used
Uses `page_cache` from the header:
- `index` maps physical pages to cache entries or queued-read entries.
- `cache` stores `cached_page` records.
- `read_queue` stores coalesced pending reads.
- `search_pending_counters` protect zone-thread searches from concurrent invalidation.

## Key Operations
- `make_page_cache` / `free_page_cache`: allocate and destroy cache, index, read queue, counters, and page buffers.
- `invalidate_page_cache`: clears all index entries and releases page data.
- `invalidate_page_cache_for_chapter`: invalidates all pages in a chapter.
- `get_page_from_cache`: returns a cached page if present.
- `enqueue_read`: queues/coalesces a physical page read and links requests.
- `reserve_read_queue_entry` / `release_read_queue_entry`: read-thread queue reservation lifecycle.
- `select_victim_in_cache`: chooses least-recent non-pending page and marks it pending.
- `put_page_in_cache`: installs completed read into cache.
- `cancel_page_in_cache`: cancels pending read and invalidates mapping.
- `get_page_cache_size`: reports delta-index page footprint.

## Concurrency
Zone threads use pending-search counters around page searches. Read threads holding the read mutex invalidate mappings only after `wait_for_pending_searches` observes active searches finish. Memory barriers pair:
- `begin_pending_search` with `wait_for_pending_searches`
- `put_page_in_cache` with `get_page_and_index`
- `end_pending_search` with readers observing counter updates

## Queue Model
The high bit of `index[physical_page]` marks queued reads. The remaining bits store either a cache index or read-queue index. `read_queue_first`, `read_queue_last_read`, and `read_queue_last` let multiple read threads reserve entries while preserving queue reuse ordering.

## Integration Notes
Works with geometry, volume pages, delta index pages, record pages, UDS threads, and buffered request structures.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/page-cache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/page-cache.h -->
# File Research: sources/block-storage/kvdo/vdo/page-cache.h

## Purpose
Declares page cache data structures, queue helpers, cache operations, and pending-search counter helpers for UDS volume pages.

## Key Structures
- `struct request_list`: first/last request chain.
- `struct cached_page`: pending flag, physical page id, last-used clock, volume page data, and delta index page.
- `struct queued_read`: invalid/reserved flags, physical page, and waiting requests.
- `struct search_pending_counter`: cache-line-aligned atomic64 counter.
- `struct page_cache`: geometry, zone count, index/cache sizing, index array, cache array, counters, read queue, queue cursors, and clock.

## Constants
- `VOLUME_CACHE_MAX_ENTRIES = UINT16_MAX >> 1`
- `VOLUME_CACHE_QUEUED_FLAG = 1 << 15`
- `VOLUME_CACHE_MAX_QUEUED_READS = 4096`

## Inline Counter Semantics
`invalidate_counter_t` stores physical page in low 32 bits and a sequence counter in high bits. Odd/even counter state indicates search pending. `begin_pending_search` and `end_pending_search` update counters with memory barriers.

## API Surface
Declares cache allocation/free, invalidation, lookup, queue operations, victim selection, completion/cancel of reads, and cache size query.

## Integration Notes
The header exposes some functions explicitly for unit tests, especially `assert_page_in_cache`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/page-cache.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/pbn-lock-pool.c -->
# File Research: sources/block-storage/kvdo/vdo/pbn-lock-pool.c

## Purpose
Implements a fixed-capacity pool of reusable PBN lock objects.

## Core Model
Uses `idle_pbn_lock` union to overlay `struct list_head` while idle and `struct pbn_lock` while borrowed. This avoids adding free-list fields to live lock objects.

## Key Functions
- `vdo_make_pbn_lock_pool`: allocates pool plus flexible lock storage, initializes all locks as idle.
- `vdo_free_pbn_lock_pool`: asserts all locks are returned before freeing.
- `vdo_borrow_pbn_lock_from_pool`: removes an idle lock, zeroes list memory, initializes as requested type.
- `vdo_return_pbn_lock_to_pool`: zeroes lock memory and appends it to idle list.

## Integration Notes
Used by physical zones to avoid allocating locks dynamically during I/O. Failure to borrow returns `VDO_LOCK_ERROR`.

## Invariants
`borrowed <= capacity`; freeing with outstanding locks logs an assertion failure. Returned lock must be the last live reference.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/pbn-lock-pool.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/pbn-lock-pool.h -->
# File Research: sources/block-storage/kvdo/vdo/pbn-lock-pool.h

## Purpose
Declares the opaque PBN lock pool API.

## API
- `vdo_make_pbn_lock_pool`
- `vdo_free_pbn_lock_pool`
- `vdo_borrow_pbn_lock_from_pool`
- `vdo_return_pbn_lock_to_pool`

## Integration Notes
Includes `pbn-lock.h` and VDO types. The pool owns lock storage; callers borrow initialized locks and must return them to the same pool.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/pbn-lock-pool.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/pbn-lock.c -->
# File Research: sources/block-storage/kvdo/vdo/pbn-lock.c

## Purpose
Implements PBN lock typing, read/write downgrade, reference increment claiming, and provisional reference release.

## Key Concepts
`LOCK_IMPLEMENTATIONS` maps each `pbn_lock_type` to its type, name, and provisional-reference release reason:
- read lock: candidate duplicate
- write lock: newly allocated
- block-map write lock: block map write

## Key Functions
- `vdo_initialize_pbn_lock`: clears holder count and sets type.
- `vdo_is_pbn_read_lock`: type check.
- `vdo_downgrade_pbn_write_lock`: converts write lock to read lock and sets increment limit.
- `vdo_claim_pbn_lock_increment`: atomically claims a read-lock reference-count increment.
- `vdo_assign_pbn_lock_provisional_reference`
- `vdo_unassign_pbn_lock_provisional_reference`
- `vdo_release_pbn_lock_provisional_reference`

## Concurrency
`vdo_claim_pbn_lock_increment` uses `atomic_add_return` because multiple hash-zone threads may deduplicate against a single compressed-block PBN lock.

## Integration Notes
References `MAXIMUM_REFERENCE_COUNT` from `packed-reference-block.h` and calls `vdo_release_block_reference` through the block allocator when releasing provisional references.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/pbn-lock.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/pbn-lock.h -->
# File Research: sources/block-storage/kvdo/vdo/pbn-lock.h

## Purpose
Defines PBN lock types, lock state, and lock operations.

## Key Definitions
- `enum pbn_lock_type`: read, data write, block-map write.
- `struct pbn_lock`: implementation pointer, holder count, compressed fragment lock count, provisional-reference flag, read-lock increment limit, and atomic claimed-increment count.

## API Surface
Initialization, read-lock check, write-to-read downgrade, increment claim, provisional-reference assign/unassign/release.

## Integration Notes
PBN locks are used by physical zones, dedupe, compressed writes, and block reference accounting. The inline `vdo_pbn_lock_has_provisional_reference` safely handles NULL locks.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/pbn-lock.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/permassert.c -->
# File Research: sources/block-storage/kvdo/vdo/permassert.c

## Purpose
Implements assertion-failure logging for UDS assertion macros.

## Key Function
- `uds_assertion_failed`: logs an embedded error message containing the formatted assertion message, expression string, file, and line, then logs a backtrace and returns the supplied error code.

## Integration Notes
Despite header comments mentioning process abort behavior, this implementation only logs and returns `code`; no local exit/abort path is present in this file.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/permassert.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/permassert.h -->
# File Research: sources/block-storage/kvdo/vdo/permassert.h

## Purpose
Defines UDS assertion macros and compile-time assertion helpers.

## Key Macros
- `ASSERT_WITH_ERROR_CODE`: checked assertion returning caller-specified error.
- `ASSERT`: checked assertion returning `UDS_ASSERTION_FAILED`.
- `ASSERT_LOG_ONLY`: logs failure without requiring caller to use an error code.
- `ASSERT_FALSE`: convenience wrapper for impossible paths.
- `STATIC_ASSERT`, `STATIC_ASSERT_SIZEOF`: compile-time checks.
- `uds_must_use`: wraps integral expressions with `__must_check`.

## API
- `set_exit_on_assertion_failure`
- `uds_assertion_failed`

## Integration Notes
All assertion macros route through `__UDS_ASSERT`, which includes module name, file, line, and formatted message. The macro design enforces checked handling for assertion-return values where used.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/permassert.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/physical-zone.c -->
# File Research: sources/block-storage/kvdo/vdo/physical-zone.c

## Purpose
Implements physical zone construction, per-PBN lock tracking, block allocation, allocation retry across zones, and lock release.

## Construction
`vdo_make_physical_zones` allocates a flexible `physical_zones` container and initializes each zone with:
- `int_map` for PBN operations.
- fixed PBN lock pool sized at `2 * MAXIMUM_VDO_USER_VIOS`.
- zone number and thread id.
- zone-specific block allocator.
- next-zone ring pointer.
- default callback thread creation.

## Locking
- `vdo_get_physical_zone_pbn_lock`: lookup existing lock by PBN.
- `vdo_attempt_physical_zone_pbn_lock`: borrows a new lock first, attempts `int_map_put`, returns existing lock if already present, otherwise installs new lock.

## Allocation Flow
- `allocate_and_lock_block`: allocates a block, locks it, verifies it was not spuriously already held, increments holder count, assigns provisional reference.
- `vdo_allocate_block_in_zone`: returns true if allocation succeeds; otherwise tries retry/continuation handling.
- `continue_allocating`: if all zones are exhausted, optionally waits on slab scrubber; otherwise dispatches completion to next physical-zone thread.
- `retry_allocation`: restarts after clean slab wait.

## Release
`vdo_release_physical_zone_pbn_lock` decrements holder count, removes lock from map when last holder exits, releases any provisional reference, and returns lock to pool.

## Integration Notes
Connects block allocator, slab depot/scrubber, data VIO completion dispatch, int maps, PBN lock pools, and VDO thread config.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/physical-zone.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/physical-zone.h -->
# File Research: sources/block-storage/kvdo/vdo/physical-zone.h

## Purpose
Declares physical-zone structures and operations.

## Key Structures
- `struct physical_zone`: zone number, callback thread id, PBN operation map, PBN lock pool, block allocator, and next-zone pointer.
- `struct physical_zones`: flexible array container.

## API Surface
Construction/destruction, lock lookup/acquire/release, zone allocation, and diagnostic dump functions.

## Integration Notes
Physical zones are the per-thread/per-allocator partition for physical block operations. The `next` pointer supports ring traversal during allocation retries.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/physical-zone.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/pointer-map.c -->
# File Research: sources/block-storage/kvdo/vdo/pointer-map.c

## Purpose
Implements a generic pointer-key to pointer-value hash map using Hopscotch hashing without the algorithm’s concurrency features.

## Data Model
- `struct bucket`: packed `first_hop`, `next_hop`, key, and value.
- `struct pointer_map`: size, capacity, bucket count, bucket array, comparator, and hasher.
- Neighborhood size is 255; hop offsets are biased by one so zero means NULL.

## Key Operations
- `make_pointer_map`: allocates map and bucket array sized by requested capacity/load.
- `free_pointer_map`: frees map storage but not keys/values.
- `pointer_map_size`
- `pointer_map_get`
- `pointer_map_put`
- `pointer_map_remove`

## Hashing / Placement
`select_bucket` scales a 32-bit hash into `[0, capacity)` with `(hash * capacity) >> 32`, avoiding modulo division. Entries that hash to a bucket must live within that bucket’s 255-entry neighborhood.

## Collision Resolution
- `find_empty_bucket` linearly probes for a vacancy.
- `move_empty_bucket` relocates entries from enclosing neighborhoods to move a hole closer.
- `find_or_make_vacancy` repeats relocation until the hole is within the target neighborhood.
- If this fails, `resize_buckets` grows capacity by 1.5x and rehashes all entries.

## Update / Removal
`pointer_map_put` rejects NULL values. Existing mappings can be returned and optionally updated. Removal clears the bucket and splices it out of the hop list.

## Integration Notes
The map does not own keys or values. The header explicitly assumes keys are either part of values, unmanaged, or safe to forget when replaced.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/pointer-map.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/pointer-map.h -->
# File Research: sources/block-storage/kvdo/vdo/pointer-map.h

## Purpose
Declares the opaque pointer map interface and key callback contracts.

## Callback Contracts
- `pointer_key_comparator`: determines equality of key referents.
- `pointer_key_hasher`: returns a stable, uniformly distributed 32-bit hash for a key while stored.

## API Surface
- `make_pointer_map`
- `free_pointer_map`
- `pointer_map_size`
- `pointer_map_get`
- `pointer_map_put`
- `pointer_map_remove`

## Ownership Model
The map retains key/value pointer values but does not own the referenced memory. NULL values are unsupported. NULL keys are allowed only if the caller’s comparator and hasher support them.

## Integration Notes
Designed for constant-time lookup/update/remove in common cases, with occasional expensive resize on insertion.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/pointer-map.h -->