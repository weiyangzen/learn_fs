# Group Research: group_661_kvdo_sources_block_storage_kvdo_vdo_compression_state_c_sources_bloc_73fe86c183cb

Scope: `Docs/research_subset_a.md`  
Files read completely: 13 source/header files under `sources/block-storage/kvdo/vdo/`.

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/compression-state.c -->
# File Research: sources/block-storage/kvdo/vdo/compression-state.c

## Purpose
Implements the atomic state machine controlling whether a `data_vio` may move through VDO compression, packing, and compressed-write emission.

## Main Concepts
- Compression state is stored in `data_vio->compression.state` as an atomic `uint32_t`.
- Low byte stores `enum vio_compression_status`.
- High bit `MAY_NOT_COMPRESS_MASK` records cancellation or disallowance.
- State transitions use `atomic_cmpxchg()` with explicit memory barriers.

## Key Functions
- `get_vio_compression_state()` reads and unpacks the atomic state.
- `set_vio_compression_state()` performs compare-and-swap transition.
- `advance_status()` moves through `PRE_COMPRESSOR -> COMPRESSING -> PACKING -> POST_PACKER`, or skips to post-packer if canceled.
- `may_compress_data_vio()` rejects compression when there is no allocation, FUA is required, compression is off, no hash lock exists, or a partial discard must complete quickly.
- `may_pack_data_vio()` rejects non-compressible data, disabled compression, or canceled VIOs.
- `may_vio_block_in_packer()` advances to `VIO_PACKING`.
- `may_write_compressed_data_vio()` advances past packer and checks cancellation.
- `set_vio_compression_done()` forces `VIO_POST_PACKER` and marks `may_not_compress`.
- `cancel_vio_compression()` sets `may_not_compress` and reports whether the caller canceled a VIO currently in packer.

## Dependencies
Uses `data-vio.h` helpers for allocation/FUA checks, `vdo_get_compressing()`, and packer/dedupe interactions through the cancellation contract.

## Concurrency Notes
The state is lock-free and may be changed by multiple threads. CAS retry loops are used wherever another thread can advance or cancel the compression path concurrently.

## Research Notes
This file is central to preventing indefinite waits when a VIO is blocked in the packer while another VIO needs its logical/hash lock.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/compression-state.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/compression-state.h -->
# File Research: sources/block-storage/kvdo/vdo/compression-state.h

## Purpose
Declares the compression-path state model and public helpers for `data_vio` compression eligibility, packer blocking, completion, and cancellation.

## Key Types
- `enum vio_compression_status`
  - `VIO_PRE_COMPRESSOR`
  - `VIO_COMPRESSING`
  - `VIO_PACKING`
  - `VIO_POST_PACKER`
- `struct vio_compression_state`
  - `status`
  - `may_not_compress`

## Public API
- `get_vio_compression_state()`
- `may_compress_data_vio()`
- `may_pack_data_vio()`
- `may_vio_block_in_packer()`
- `may_write_compressed_data_vio()`
- `set_vio_compression_done()`
- `cancel_vio_compression()`

## Important Invariant
The order of `enum vio_compression_status` is semantic: `advance_status()` in `compression-state.c` increments the status to move along the compression path.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/compression-state.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/config.c -->
# File Research: sources/block-storage/kvdo/vdo/config.c

## Purpose
Builds, serializes, deserializes, validates, and logs UDS index configuration used by VDO deduplication.

## On-Disk Format
- Magic: `"ALBIC"`
- Supported versions:
  - `"06.02"`: legacy layout without remapped virtual/physical chapter fields.
  - `"08.02"`: includes remapped chapter fields.
- Encoding and decoding use little-endian buffer helpers.

## Key Functions
- `decode_index_config_06_02()` and `decode_index_config_08_02()` parse saved config payloads.
- `read_version()` reads version bytes and dispatches to the correct decoder.
- `are_matching_configurations()` compares saved config against the runtime `struct configuration`.
- `validate_config_contents()` verifies magic, reads saved config, validates it, and imports remapped chapter metadata.
- `encode_index_config_06_02()` and `encode_index_config_08_02()` serialize runtime config.
- `write_config_contents()` writes magic, version, and serialized payload; versions below 4 use `06.02`.
- `compute_memory_sizes()` maps UDS memory configuration and sparse mode to chapter counts and record-page sizing.
- `normalize_zone_count()` defaults to half CPU cores and clamps to `[1, MAX_ZONES]`.
- `normalize_read_threads()` clamps to `[1, MAX_VOLUME_READ_THREADS]` with default 2.
- `make_configuration()` allocates and initializes `struct configuration` and its `geometry`.
- `free_configuration()` frees geometry and configuration.
- `log_uds_configuration()` emits debug configuration fields.

## Dependencies
Uses buffer helpers, geometry construction, UDS parameters, logger, thread/core count helper, and project allocation wrappers.

## Important Behavior
Sparse indexing multiplies base chapters by 10 and marks 95% as sparse, increasing record capacity. Reduced memory modes subtract one chapter and are represented in version `08.02` via remapped chapter fields.

## Edge Cases
Invalid memory size returns `-EINVAL`. Configuration mismatch logs specific field differences and returns `UDS_NO_INDEX`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/config.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/config.h -->
# File Research: sources/block-storage/kvdo/vdo/config.h

## Purpose
Defines UDS index configuration structures and public configuration lifecycle/serialization APIs.

## Key Constants
- `DEFAULT_VOLUME_INDEX_MEAN_DELTA = 4096`
- `DEFAULT_CACHE_CHAPTERS = 7`
- `DEFAULT_SPARSE_SAMPLE_RATE = 32`
- `MAX_ZONES = 16`

## Key Structures
- `struct configuration`: runtime configuration with device name, size, offset, geometry, nonce, zone/read thread counts, cache chapters, volume index delta, sparse sample rate.
- `struct uds_configuration_8_02`: persisted version including remapped virtual/physical chapter fields.
- `struct uds_configuration_6_02`: legacy persisted version without remapped fields.

## Public API
- `make_configuration()`
- `free_configuration()`
- `validate_config_contents()`
- `write_config_contents()`
- `log_uds_configuration()`

## Research Notes
This header bridges user-facing `uds_parameters`, runtime geometry, and stable on-disk index config.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/config.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/constants.c -->
# File Research: sources/block-storage/kvdo/vdo/constants.c

## Purpose
Defines externally visible VDO size limit constants declared in `constants.h`.

## Constants
- `MAXIMUM_VDO_LOGICAL_BLOCKS`: 4 PB, represented as 1 terablock.
- `MAXIMUM_VDO_PHYSICAL_BLOCKS`: 256 TB, represented as 64 gigablocks.
- `MINIMUM_VDO_SLAB_JOURNAL_BLOCKS`: unit-test minimum of 2.

## Research Notes
This file contains only constant definitions; most compile-time constants live in `constants.h`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/constants.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/constants.h -->
# File Research: sources/block-storage/kvdo/vdo/constants.h

## Purpose
Defines global VDO sizing, layout, queueing, journal, and block constants.

## Key Constants
- Block map:
  - `VDO_BLOCK_MAP_ENTRIES_PER_PAGE = 812`
  - `VDO_BLOCK_MAP_TREE_HEIGHT = 5`
  - `DEFAULT_VDO_BLOCK_MAP_TREE_ROOT_COUNT = 60`
- Bio submission:
  - `DEFAULT_VDO_BIO_SUBMIT_QUEUE_COUNT = 4`
  - `DEFAULT_VDO_BIO_SUBMIT_QUEUE_ROTATE_INTERVAL = 64`
  - `VDO_BIO_ROTATION_INTERVAL_LIMIT = 1024`
- Journals:
  - `DEFAULT_VDO_RECOVERY_JOURNAL_SIZE = 32 * 1024`
  - `DEFAULT_VDO_SLAB_JOURNAL_SIZE = 224`
  - `VDO_RECOVERY_JOURNAL_TAIL_BUFFER_SIZE = 64`
- Limits:
  - `MAX_VDO_LOGICAL_ZONES = 60`
  - `MAX_VDO_PHYSICAL_ZONES = 16`
  - `MAX_VDO_SLAB_BITS = 23`
  - `MAX_VDO_SLABS = 8192`
  - `MAXIMUM_VDO_THREADS = 100`
  - `MAXIMUM_VDO_USER_VIOS = 2048`
- Block geometry:
  - `VDO_BLOCK_SIZE = 4096`
  - `VDO_SECTORS_PER_BLOCK = VDO_BLOCK_SIZE >> SECTOR_SHIFT`
  - `VDO_SECTOR_SIZE = 512`
  - `VDO_ZERO_BLOCK = 0`

## External Constants
Declares logical/physical maximums and minimum slab journal blocks defined in `constants.c`.

## Research Notes
This file supplies shared assumptions used across pool sizing, hash lock capacity, block map layout, and I/O alignment.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/constants.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/cpu.h -->
# File Research: sources/block-storage/kvdo/vdo/cpu.h

## Purpose
Provides cache-line sizing and prefetch helpers.

## Cache Line Selection
- PPC: 128 bytes.
- s390x: 256 bytes.
- x86_64 and aarch64: 64 bytes.
- Unknown architectures fail compilation.

## Functions
- `prefetch_address(address, for_write)`: wraps `__builtin_prefetch()` only when `for_write` is compile-time constant.
- `prefetch_range(start, size, for_write)`: prefetches all cache lines overlapping a byte range, accounting for address alignment.

## Research Notes
This header is architecture-sensitive and intentionally uses a `#define` for `CACHE_LINE_BYTES` because enum constants are not sufficient for all compile-time uses.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/cpu.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/data-vio-pool.c -->
# File Research: sources/block-storage/kvdo/vdo/data-vio-pool.c

## Purpose
Implements the preallocated `data_vio` pool used to service incoming bios while bounding concurrency and avoiding allocation during normal I/O.

## Core Design
The pool has two resource limiters:
- Main limiter for total active `data_vio` requests.
- Discard limiter for discard permits, preventing discards from starving reads/writes.

Completed VIOs are returned through a funnel queue and processed in batches on the CPU thread.

## Key Structures
- `struct limiter`: tracks limit, busy count, high-water mark, release/wake counts, waiter lists, permitted waiters, and blocked submitter wait queue.
- `struct data_vio_pool`: owns admin state, spinlock, limiters, permitted discard list, available VIO list, funnel queue, processing flag, and flexible array of `data_vios`.

## Key Functions
- `reset_data_vio()` clears reusable state while preserving separately allocated buffers and bio.
- `launch_bio()` classifies bio as read/write/read-modify-write/discard, handles partial-block state, copies full writes into `data_block`, detects zero blocks, computes LBN, and launches the VIO.
- `acquire_permit()` either consumes a limiter slot or queues the bio and blocks the submitter.
- `vdo_launch_bio()` obtains discard permit if needed, obtains data_vio permit, removes an available VIO, and launches it.
- `release_data_vio()` enqueues completed VIOs into the funnel queue and schedules release processing.
- `process_release_callback()` batches returned VIOs, acknowledges bios, transfers discard permits, reassigns VIOs to oldest eligible waiters, wakes blocked submitters, and completes drain if applicable.
- `make_data_vio_pool()` allocates pool and initializes every `data_vio`.
- `free_data_vio_pool()` asserts no busy VIOs/waiters and destroys all pooled VIOs.
- `drain_data_vio_pool()` and `resume_data_vio_pool()` integrate with admin state.
- Getter functions expose active/limit/max counts for discards and requests.

## Concurrency Notes
The fast release path avoids taking the pool lock in releasing threads by using a funnel queue and atomic `processing` flag. Memory barriers pair scheduling and release callback processing.

## Edge Cases
- Discard waiters first need discard permits, then data_vio permits.
- `bio->bi_private` stores arrival time from `jiffies`; comments note this assumes `jiffies` is not effectively only 32 bits.
- `set_data_vio_pool_discard_limit()` rejects limits above total request limit.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/data-vio-pool.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/data-vio-pool.h -->
# File Research: sources/block-storage/kvdo/vdo/data-vio-pool.h

## Purpose
Declares the `data_vio_pool` lifecycle, bio launch, release, drain/resume, diagnostics, and statistics APIs.

## Public API
- Creation/destruction:
  - `make_data_vio_pool()`
  - `free_data_vio_pool()`
- I/O:
  - `vdo_launch_bio()`
  - `release_data_vio()`
- Admin:
  - `drain_data_vio_pool()`
  - `resume_data_vio_pool()`
- Diagnostics/statistics:
  - `dump_data_vio_pool()`
  - active/limit/max getters for discards and requests
  - `set_data_vio_pool_discard_limit()`

## Research Notes
The header exposes only pool-level operations; internal limiter and queue details stay private in `data-vio-pool.c`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/data-vio-pool.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/data-vio.c -->
# File Research: sources/block-storage/kvdo/vdo/data-vio.c

## Purpose
Implements `data_vio` allocation, initialization, launch, logical lock handling, completion, allocation lock handling, bio acknowledgement, compression/decompression, and block utility functions.

## Key Functions
- `allocate_data_vio_components()` allocates `data_block`, `compression.block`, `scratch_block`, and creates the backing bio.
- `initialize_data_vio()` and `destroy_data_vio()` manage per-VIO allocated components.
- `launch_data_vio()` resets per-request state, initializes the LBN lock, sets mapping state based on write/discard type, and starts logical lock acquisition.
- `attempt_logical_block_lock()` serializes requests by logical block using the logical zone’s `lbn_operations` map.
- `vdo_release_logical_block_lock()` releases or transfers an LBN lock to the next waiter.
- `data_vio_allocate_data_block()` selects an allocation zone and launches allocation callback.
- `release_data_vio_allocation_lock()` releases PBN allocation lock and optionally resets allocation.
- `acknowledge_data_vio()` completes the original user bio and updates stats.
- `compress_data_vio()` performs LZ4 compression into `compression.block->data`, with `VDO_BLOCK_SIZE + 1` as uncompressible sentinel.
- `uncompress_data_vio()` extracts a compressed fragment and uses LZ4 safe decompression.
- `is_zero_block()` checks a block by 64-bit words.

## Logical Lock Behavior
A request outside configured logical range fails with `VDO_OUT_OF_RANGE`. If a read arrives behind a writing lock holder that already has an allocation, the read can be satisfied directly from the lock holder’s `data_block`; otherwise it queues and may cancel the holder’s compression to avoid packer blocking.

## Completion Flow
- `complete_data_vio()` chooses read or write cleanup after recording errors.
- `finish_data_vio()` sets completion result then calls `complete_data_vio()`.
- `get_data_vio_operation_name()` maps async operation enum values to diagnostic strings.

## Dependencies
Interacts with logical zones, physical zones, block map, allocation selector, packer, dedupe, journals, bio helpers, and VDO completion infrastructure.

## Research Notes
This file is the operational center for user data requests. `data-vio.h` carries much of the thread-routing inline machinery used by this implementation.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/data-vio.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/data-vio.h -->
# File Research: sources/block-storage/kvdo/vdo/data-vio.h

## Purpose
Defines `struct data_vio`, its substructures, async operation identifiers, conversion helpers, thread-affinity assertions, callback launch helpers, and public data_vio operations.

## Key Types
- `enum async_operation_number`: diagnostic state for the last async operation.
- `struct lbn_lock`: LBN, locked flag, waiter queue, logical zone.
- `struct tree_lock`: block-map tree traversal state and page lock waiters.
- `struct compression_state`: atomic compression status, compressed size, packer slot/bin, batch link, packer lock holder, compressed block.
- `struct allocation`: allocation zone, PBN, PBN lock, write lock type, first allocation zone, clean-slab wait flag.
- `struct data_vio`: full per-request state for VDO data I/O.

## Important `data_vio` Fields
- Embedded `struct vio`.
- Waiter link for internal wait queues.
- Logical lock, tree lock, mapped/new mapped locations.
- Chunk hash, duplicate advice/location, hash zone/lock.
- Recovery journal and flush generation state.
- User bio, partial block offset, discard remainder.
- Dedupe context pointer.
- Persistent pooled buffers: compression state, `data_block`, `scratch_block`, pool entry.

## Inline Helpers
- Type conversions: `vio_as_data_vio()`, `data_vio_as_vio()`, `as_data_vio()`, `data_vio_as_completion()`.
- Operation checks: read/write/read-modify-write/trim/FUA.
- Allocation helpers: `get_data_vio_allocation()`, `data_vio_has_allocation()`.
- Wait queue helpers: `enqueue_data_vio()`, waiter conversions.
- VDO/thread accessors: `vdo_from_data_vio()`, `get_thread_config_from_data_vio()`.

## Thread Routing
Provides assertion and callback launch helpers for:
- Hash zone
- Logical zone
- Allocated zone
- Duplicate zone
- Mapped zone
- New mapped zone
- Journal thread
- Packer thread
- Dedupe thread
- CPU thread
- Bio zone
- Bio ack queue

## Public Operations
Declares lifecycle, launch/completion, mapping updates, logical lock release, allocation, acknowledgement, compression/decompression, I/O preparation, and zero-block detection.

## Research Notes
This header encodes VDO’s asynchronous execution model. Most subsystem transitions are expressed by setting a completion callback to the owning thread and invoking it.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/data-vio.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/dedupe.c -->
# File Research: sources/block-storage/kvdo/vdo/dedupe.c

## Purpose
Implements VDO’s deduplication coordination layer: hash zones, hash locks, UDS index query/update plumbing, duplicate verification, lock rollover, dedupe timeout handling, sysfs status, and administrative drain/resume.

## Module Model
The file’s design comment describes two coupled systems:
- Hash locks coordinate concurrent writes with identical hashes and allow them to dedupe together.
- UDS index queries are asynchronous and may time out, allowing writes to continue without dedupe.

## Key State Machines
### Hash Lock States
- `INITIALIZING`
- `QUERYING`
- `WRITING`
- `UPDATING`
- `LOCKING`
- `VERIFYING`
- `DEDUPING`
- `UNLOCKING`
- `BYPASSING`
- `DESTROYING`

A hash lock usually has one agent VIO except in `DEDUPING`, where all holders dedupe in parallel against a verified duplicate PBN lock.

### Dedupe Context States
- `IDLE`
- `PENDING`
- `TIMED_OUT`
- `COMPLETE`
- `TIMED_OUT_COMPLETE`

These manage UDS requests that may complete after VDO has already timed them out.

### Index States
- `IS_CLOSED`
- `IS_CHANGING`
- `IS_OPENED`

User-visible names include `closed`, `opening`, `online`, `offline`, `closing`, `error`, and `suspended`.

## Key Structures
- `struct hash_lock`: hash key, duplicate ring, reference counts, state, UDS update flag, verification flags, duplicate location/lock, agent, waiter queue.
- `struct dedupe_context`: UDS request wrapper, zone, requestor VIO, submission time, atomic state.
- `struct hash_zone`: per-zone hash lock map, lock pool, statistics, context lists, timer, completion, active query count.
- `struct hash_zones`: global manager, kobject, UDS parameters/session, ratelimit state, timeout counters, index/admin state, zone array.

## Hash Lock Flow
- `vdo_acquire_hash_lock()` obtains or shares a lock for a chunk name, after detecting possible hash collisions by comparing actual data.
- `vdo_enter_hash_lock()` dispatches based on lock state: starts query, waits, bypasses, dedupes, or reports invalid state.
- `start_querying()` posts or queries UDS using the agent.
- `finish_querying()` either starts locking/verifying returned advice or writes new data.
- `start_locking()` and `lock_duplicate_pbn()` acquire a read lock on candidate duplicate PBN advice.
- `start_verifying()` reads candidate data, decompresses if needed, and compares blocks.
- `finish_verifying()` marks advice valid/stale, claims reference increments, and transitions to dedupe or write.
- `start_writing()` sends an agent through compression/write path when no usable duplicate exists.
- `finish_writing()` makes the written location the verified duplicate and either dedupes waiters, updates UDS, unlocks, or exits.
- `start_deduping()` launches agent/waiters to dedupe in parallel against a verified duplicate lock.
- `finish_deduping()` releases individual holders or advances cleanup/update when the last holder remains.
- `start_updating()` updates UDS advice; `finish_updating()` cleans up after update.
- `start_unlocking()` and `finish_unlocking()` release duplicate PBN read locks and decide whether to re-lock, write, or destroy.
- `start_bypassing()` aborts dedupe for a lock and resumes ordinary compression/write path.

## Rollover Behavior
If a duplicate PBN lock has no remaining reference increments, `fork_hash_lock()` replaces the old lock in the hash map with a new lock. Remaining waiters move to the new lock, and the new agent writes a fresh copy. Only one lock updates UDS advice.

## UDS Index Handling
- Advice encoding uses version `2`, mapping state, and little-endian 64-bit PBN.
- `decode_uds_advice()` validates UDS result, rejects unmapped/zero/invalid PBN advice, and resolves the physical zone.
- `prepare_uds_request()` fills UDS request metadata for `UDS_POST` and `UDS_UPDATE`.
- `query_index()` acquires a dedupe context, starts timeout tracking, and launches `uds_start_chunk_operation()`.
- `finish_index_operation()` handles completion before or after timeout.
- `acquire_context()` reuses available contexts or recycles timed-out contexts that later completed.

## Timeout Handling
- Default timeout interval: 5000 ms.
- Default minimum timer interval: 100 ms.
- `start_expiration_timer()` arms per-zone timer.
- `timeout_index_operations_callback()` scans pending contexts, moves expired ones to timed-out list, clears requestor context, and resumes VIO processing without dedupe.
- Timeout reports are ratelimited and included in statistics.

## Admin and Lifecycle
- `vdo_make_hash_zones()` allocates zones, initializes UDS index session, creates hash-zone threads, lock pools, context pools, and action manager.
- `vdo_free_hash_zones()` frees maps, lock arrays, action manager, UDS session, ratelimit state, and kobject or raw allocation depending on admin state.
- `vdo_drain_hash_zones()` suspends UDS index then drains all zones.
- `vdo_resume_hash_zones()` resumes index and zones unless read-only.
- `vdo_start_dedupe_index()` opens/enables index, optionally creating it.
- `vdo_message_dedupe_index()` handles `index-close`, `index-create`, `index-disable`, and `index-enable`.
- `vdo_add_dedupe_index_sysfs()` creates the `dedupe/status` sysfs node.

## Statistics and Diagnostics
- Tracks valid/stale advice, concurrent data matches, hash collisions, current queries, UDS index stats, and dedupe advice timeouts.
- `vdo_dump_hash_zones()` logs UDS index state and active hash locks.
- `vdo_select_hash_zone()` maps the first byte of chunk name to a zone using multiply/shift scaling.

## Concurrency Notes
Hash lock transitions are confined to the owning hash-zone thread. Dedupe context and timer state use atomic compare-and-swap because UDS callbacks, timers, and zone completions can race.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/dedupe.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/dedupe.h -->
# File Research: sources/block-storage/kvdo/vdo/dedupe.h

## Purpose
Declares public dedupe/hash-zone APIs and tunables used by VDO write, compression, statistics, sysfs, and admin paths.

## Forward Declarations
- `struct hash_lock`
- `struct hash_zone`
- `struct hash_zones`

## Public API Groups
### Hash Lock Operations
- `vdo_get_duplicate_lock()`
- `vdo_acquire_hash_lock()`
- `vdo_enter_hash_lock()`
- `vdo_continue_hash_lock()`
- `vdo_continue_hash_lock_on_error()`
- `vdo_release_hash_lock()`
- `vdo_share_compressed_write_lock()`

### Hash Zone Lifecycle/Admin
- `vdo_make_hash_zones()`
- `vdo_free_hash_zones()`
- `vdo_get_hash_zone_thread_id()`
- `vdo_drain_hash_zones()`
- `vdo_resume_hash_zones()`
- `vdo_finish_dedupe_index()`

### Statistics/Selection/Diagnostics
- `vdo_get_dedupe_statistics()`
- `vdo_select_hash_zone()`
- `vdo_dump_hash_zones()`
- `vdo_get_dedupe_index_state_name()`
- `vdo_get_dedupe_index_timeout_count()`

### Sysfs and Messages
- `vdo_message_dedupe_index()`
- `vdo_add_dedupe_index_sysfs()`
- `vdo_start_dedupe_index()`

### Tunables
- `vdo_dedupe_index_timeout_interval`
- `vdo_dedupe_index_min_timer_interval`
- `vdo_set_dedupe_index_timeout_interval()`
- `vdo_set_dedupe_index_min_timer_interval()`

## Research Notes
Most declarations are implemented in `dedupe.c`. The timeout-count accessor is declared here but is not implemented in the paired `dedupe.c` file read for this group.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/dedupe.h -->