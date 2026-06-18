# Group Research: group_530_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_cb4db0aa2faf

Scope: `Docs/research_subset_a.md`; source tree `sources/os/illumos/illumos-gate` is included in subset A. This group covers ZFS virtual-device support code: indirect vdev mappings, device initialization, labels and uberblocks, mirror/RAID-Z dispatch, queue scheduling, and RAID-Z math backends.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_indirect_mapping.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_indirect_mapping.c

## Purpose
Implements the in-memory and on-disk handling for ZFS indirect vdev mapping objects used after device removal. The mapping translates source offsets on a removed vdev to destination DVAs elsewhere in the pool and optionally tracks obsolete byte counts per mapping entry.

## Main Responsibilities
- Validate mapping handles with `vdev_indirect_mapping_verify()`, including object/dbuf/phys consistency, entry-array presence, max-offset bounds, and obsolete-count object expectations.
- Provide accessors for entry count, max offset, DMU object id, bytes mapped, and logical mapping-array byte size.
- Locate mapping entries by source offset using a custom binary search over sorted mapping entries.
- Allocate, open, close, and free DMU objects containing the mapping and optional obsolete-count arrays.
- Append new mapping entries in syncing context and maintain the in-core entry array.
- Load and update obsolete counts from the obsolete spacemap.

## Key Functions
- `dva_mapping_overlap_compare()` treats entries as half-open ranges `[src, src + asize)`, returning less/equal/greater relative to an offset.
- `vdev_indirect_mapping_entry_for_offset_impl()` performs binary search and optionally returns the next greater mapping entry when an exact overlap is missing.
- `vdev_indirect_mapping_alloc()` creates the main DMU metadata object; when `SPA_FEATURE_OBSOLETE_COUNTS` is enabled it allocates a parallel uint32 counts object and increments the feature refcount.
- `vdev_indirect_mapping_open()` holds the bonus buffer, detects the newer bonus layout by bonus size, and reads all physical entries into memory.
- `vdev_indirect_mapping_add_entries()` consumes a list of `vdev_indirect_mapping_entry_t`, writes entries and obsolete counts in `SPA_OLD_MAXBLOCKSIZE` batches, updates `vimp_bytes_mapped`, `vimp_max_offset`, and `vimp_num_entries`, then rebuilds the in-memory array.
- `vdev_indirect_mapping_increment_obsolete_count()` walks mapping entries covering a logical range and increments per-entry byte counts, asserting counts never exceed entry size.
- `vdev_indirect_mapping_load_obsolete_spacemap()` iterates a spacemap and applies obsolete allocations to the count array.

## Important Behavior And Invariants
- Mapping entries must be appended in nondecreasing source-offset order; `vdev_indirect_mapping_add_entries()` asserts each new `src_offset` is at or beyond the current max offset.
- Fully obsolete entries should not be added; entry obsolete count must be less than mapped size.
- Obsolete counts are optional for old-format mappings. If absent, loading counts returns a zeroed array.
- The size accessor deliberately avoids full verification so stats paths can read a possibly stale entry count without contending with concurrent changes.

## Dependencies
Uses DMU object APIs, DMU bonus buffers, SPA feature flags, `space_map_iterate()`, ZIO buffers, and DVA mapping macros from ZFS vdev headers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_indirect_mapping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_initialize.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_initialize.c

## Purpose
Implements vdev initialization, a best-effort background process that writes a known filler pattern to free regions of a leaf vdev. It persists progress and state in leaf ZAP entries so initialization can be suspended, canceled, completed, or resumed after import.

## Tunables And State
- `zfs_initialize_value` is the 64-bit pattern written to disk, defaulting to `0xdeadbeefdeadbeef`.
- `zfs_initialize_limit` caps outstanding initialization I/Os per leaf vdev.
- `zfs_initialize_chunk_size` controls physical write size, defaulting to 1 MiB.
- Persistent ZAP keys store initialize state, last offset, and action timestamp.

## Main Responsibilities
- Decide when initialization must stop: requested exit, non-writable vdev, detached vdev, or top-level removal.
- Persist state transitions and progress through sync tasks using vdev GUIDs rather than raw `vdev_t *` pointers, because a vdev can be freed before the sync task runs.
- Estimate progress from metaslab free space and the last initialized physical offset.
- Walk free metaslab ranges, translate logical ranges to leaf physical ranges, and write initialized chunks.
- Start, stop, wait for, restart, and recursively stop initialization threads.

## Key Functions
- `vdev_initialize_zap_update_sync()` resolves the vdev by GUID in syncing context and writes `INITIALIZE_LAST_OFFSET`, `INITIALIZE_ACTION_TIME`, and `INITIALIZE_STATE`.
- `vdev_initialize_change_state()` changes in-memory state, schedules the ZAP sync task, logs spa history, and wakes waiters for terminal/non-active states.
- `vdev_initialize_write()` throttles inflight I/O, obtains a txg, schedules a progress ZAP update for the txg, checks stop conditions under locks, records the offset for that txg, and issues `zio_write_phys()`.
- `vdev_initialize_calculate_progress()` sums free metaslab space, with RAID-Z adjustment by child count, and loads the current metaslab only when the saved offset lies inside it.
- `vdev_initialize_range_add()` translates logical free ranges to the leaf vdev, clips already-initialized portions, and adds nonempty physical ranges to the initialize range tree.
- `vdev_initialize_thread()` drives the process: load progress, allocate filler ABD, iterate metaslabs, disable/load each metaslab, collect free ranges, write them, re-enable/unload as appropriate, wait for inflight I/O, then mark complete if not stopped.
- `vdev_initialize_stop_all()` recursively requests a target state for all concrete leaves and waits for their threads before syncing state to disk.
- `vdev_initialize_restart()` reads persisted state and action time; suspended/offline devices only load reporting progress, while active writable devices resume.

## Important Behavior And Invariants
- Initialization is best-effort. Non-availability rolls back the recorded offset for the txg, but other I/O errors only increment `vs_initialize_errors`.
- Sync task data is a copied GUID, freed by the sync callback.
- The initialize thread drops locks around `txg_wait_synced()` to avoid deadlock with online/import paths holding config locks.
- RAID-Z leaves may receive no translated range for a logical free segment; zero-length physical ranges are ignored.

## Dependencies
Uses SPA config locking, ZIO physical writes, DMU transactions and sync tasks, metaslab loading/disabling, range trees, ABD buffers, vdev translation, and leaf/top ZAP metadata.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_initialize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_label.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_label.c

## Purpose
Implements ZFS vdev label handling: label layout addressing, config nvlist generation, label reads/writes, device-in-use checks, initial label creation, boot environment label storage, uberblock loading/syncing, and transactionally consistent config sync.

## Label Model
Each leaf has four labels: two at the beginning and two at the end of the device. Each label contains padding, a packed `vdev_phys_t` nvlist, a boot-environment pad area, and an uberblock ring. Config updates write one label set before the uberblock and the other after it so power loss can be resolved using label and uberblock txgs.

## Main Responsibilities
- Compute physical label offsets and reverse-map offsets to label numbers.
- Generate vdev config nvlists, including identity, topology, metaslab fields, DTL objects, indirect-vdev metadata, ZAP object ids, state flags, aux state, stats, and child arrays.
- Read the best label config from a vdev subject to a maximum txg.
- Detect whether candidate devices are already in active use, spare use, or L2ARC use.
- Initialize labels for new pool devices, replacements, spares, L2ARC devices, removals, and splits.
- Read/write the boot environment area from/to all readable/writable leaf labels.
- Load the best uberblock across the whole vdev tree and read the associated config.
- Sync labels and uberblocks in a crash-consistent sequence.

## Key Functions
- `vdev_label_offset()` maps label number plus offset inside `vdev_label_t` to device offset, placing labels 0/1 at start and 2/3 at end.
- `vdev_config_generate_stats()` packs standard and extended vdev stats including queue active/pending counts, latency histograms, I/O size histograms, and slow I/O count.
- `vdev_config_generate()` recursively builds a vdev nvlist. It handles top-level fields, indirect mapping/birth objects, MOS-only ZAP fields, deferred resilver marker, removable-device indirect-size estimates, leaf state flags, and nested children.
- `vdev_top_config_generate()` records root child count and hole array for top-level namespace holes.
- `vdev_label_read_config()` reads all labels, unpacks nvlists, and selects the newest label whose txg does not exceed the requested txg; if no config is found, retries with `ZIO_FLAG_TRYHARD`.
- `vdev_inuse()` reads labels and checks pool/device GUIDs, pool state, txg/create-txg, spare registry, L2ARC registry, and read-only imported pools.
- `vdev_label_init()` recurses through children, rejects dead/in-use leaves, adjusts GUIDs for shared spares/L2ARC, creates the initial txg-0 config label or special spare/L2ARC label, zeros the bootenv pad, writes an uberblock template with txg 0, and writes all four labels.
- `vdev_label_read_bootenv()` gathers the first checksum-valid bootenv block from all leaves and interprets raw GRUB env data, nvlist data, empty nvlist data, or FreeBSD bootonce strings.
- `vdev_label_write_bootenv()` validates packed size, recursively writes leaves, encodes raw or nvlist bootenv payloads, and succeeds if any disk writes all labels successfully.
- `vdev_uberblock_load()` scans all uberblock rings on all readable leaves, picks the best uberblock by txg, timestamp, then MMP sequence, and reads a matching label config from the same vdev.
- `vdev_uberblock_sync_list()` writes uberblocks to all supplied vdev trees, flushes write caches, and requires at least one successful write to a known-visible vdev.
- `vdev_label_sync_list()` writes even or odd labels for all dirty vdevs, tracks at least one good write per normal top-level vdev, ignores errors for log/cache/aux devices, and flushes.
- `vdev_config_sync()` is the high-level sync order: flush txg data, write even labels, write uberblocks, update MMP data if enabled, then write odd labels, retrying once with `TRYHARD` on failures.

## Important Behavior And Invariants
- Label selection must not use a config newer than the selected uberblock unless extreme rewind explicitly retries without txg restrictions.
- New devices are pre-labeled with txg 0 so failed creates do not leave active-looking pool labels.
- Config nvlists can fail to pack if too large; initialization maps `EFAULT` from `nvlist_pack()` to `ENAMETOOLONG`.
- `vdev_config_sync()` is designed to be idempotent after partial failure.
- Multihost MMP reserves some uberblock slots from normal txg cycling.

## Dependencies
Uses nvlist/fnvlist APIs, ZIO physical I/O, ABD buffers, SPA config and dirty lists, uberblock comparison/update, MMP helpers, vdev stats, DTL/space maps, scan/removal/checkpoint stats, ZAP metadata, and bootenv constants.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_label.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_mirror.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_mirror.c

## Purpose
Implements mirror-like vdev operations for `mirror`, `replacing`, and `spare` vdevs. It opens/closes children, selects read children based on availability, DTL freshness, load, and locality, fans writes out to all children, retries reads, and repairs stale or damaged replicas.

## Main Structures
- `mirror_child_t` tracks child vdev, offset, last error, calculated load, whether tried/skipped, and whether an error was speculative.
- `mirror_map_t` owns per-I/O child records plus an array of preferred child indexes, and flags for root DVA reads and replacing/spare resilvering.
- Mirror kstats count load-selection outcomes for rotating/non-rotating devices and preferred-child selection.

## Key Functions
- `vdev_mirror_load()` computes a load score from vdev queue depth and last issued offset. It applies different sequential/seek penalties for rotating and non-rotating media; root DVA selection treats all copies equally.
- `vdev_mirror_map_init()` builds a map either from a block pointer's DVAs for root/ditto reads (`io_vd == NULL`) or from the mirror/replacing/spare children. Sequential scrub reads can limit initial work to one sorted DVA until retry.
- `vdev_mirror_open()` opens all children, computes the mirror size as the minimum child size and max ashift, and fails only if all children fail.
- `vdev_mirror_child_select()` skips unreadable children and DTL-missing children, gathers lowest-load candidates, randomizes among ties, and falls back to untried stale children only when no clean choice exists.
- `vdev_mirror_io_start()` sends scrub reads with checksummable data to every child unless the replacing vdev is resilvering; normal reads go to one selected child; writes go to all children.
- `vdev_mirror_io_done()` accepts partial writes if at least one copy succeeded for normal mirrors, retries reads on additional children when no good copy exists, sets worst error when exhausted, and issues repair writes when a good copy exists and repair is warranted.
- `vdev_mirror_state_change()` sets parent state to offline/no replicas, degraded, or healthy based on child fault/degraded counts.
- `vdev_mirror_dumpio()` performs dump I/O on children, stopping after the first successful read but attempting all children for writes.

## Important Behavior And Invariants
- Replacing/spare vdevs suppress scrub reads to resilvering children because the new device may not yet contain the block.
- A mirror read can repair children not tried when scrub/resilver/indirect-vdev/DTL conditions imply they may be stale.
- Partial writes are intentionally treated as success in some cases, with comments noting future write reallocation policy could be stricter.
- For untrusted pool configs, invalid DVAs are filtered before root mirror map creation; if none remain, the parent zio is failed with `ENXIO`.

## Registered Ops
`vdev_mirror_ops`, `vdev_replacing_ops`, and `vdev_spare_ops` share open/close/asize/io/state/dump handlers, differ only by type string.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_mirror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_missing.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_missing.c

## Purpose
Defines placeholder vdev operations for `missing` and `hole` vdev types. A missing vdev is used during import to represent a known-absent device while still allowing the rest of the pool configuration to be parsed and opened.

## Main Behavior
- `vdev_missing_open()` pretends to succeed with zero physical size, max size, and ashift. This avoids the root vdev being marked `VDEV_AUX_NO_REPLICAS`; the pool should later fail the GUID-sum check with `VDEV_AUX_BAD_GUID_SUM`.
- `vdev_missing_close()` is a no-op.
- `vdev_missing_io_start()` fails any I/O with `ENOTSUP` and executes the zio completion path.
- `vdev_missing_io_done()` is a no-op.

## Registered Ops
- `vdev_missing_ops` uses type `VDEV_TYPE_MISSING`.
- `vdev_hole_ops` uses type `VDEV_TYPE_HOLE`.
- Both are leaf vdevs with default asize and no remap/xlate/dump handlers.

## Important Behavior And Invariants
The GUID for a missing vdev is always zero, so the root configuration's GUID sum will not match. This file intentionally supports import-time diagnosis rather than operational I/O.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_missing.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_queue.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_queue.c

## Purpose
Implements the per-leaf ZFS vdev I/O scheduler. It classifies queued I/O by priority, enforces per-class and aggregate concurrency limits, adjusts async-write concurrency based on dirty data, orders queued I/O by timestamp or LBA, aggregates adjacent I/Os, and issues more work as active I/Os complete.

## Queue Classes And Tunables
The queueable priorities include sync read/write, async read/write, scrub, removal, initializing, and trim. Tunables define min/max active counts per class, aggregate max active count, async-write dirty-data thresholds, aggregation size/gap limits, allocator queue-depth threshold, and optional TRIM aggregation.

## Main Data Structures
- Each `vdev_queue_t` has a mutex, active offset tree, per-type offset trees for reads/writes/TRIMs, and per-priority class trees.
- Sync read/write and TRIM class trees are timestamp ordered for latency consistency.
- Async, scrub, removal, and initializing class trees are LBA ordered.

## Key Functions
- `vdev_queue_init()` creates AVL trees and sets FIFO-vs-offset comparators for each priority.
- `vdev_queue_io_add()` and `vdev_queue_io_remove()` maintain queued class/type trees and SPA waitq kstats.
- `vdev_queue_pending_add()` and `vdev_queue_pending_remove()` maintain active counts/tree and SPA runq/kstat I/O accounting.
- `vdev_queue_max_async_writes()` linearly interpolates allowed async writes between min/max active based on `dp_dirty_total`, using max when sync tasks are pending.
- `vdev_queue_class_to_issue()` first finds a nonempty class below its minimum active count; if none, finds one below its maximum; it also respects `zfs_vdev_max_active`.
- `vdev_queue_aggregate()` expands around a candidate I/O through same-type, same inherited flags, sufficiently adjacent I/Os. Reads can bridge read gaps; writes can include optional I/Os and optionally stretch through optional gaps to improve device-level aggregation.
- `vdev_queue_io_to_issue()` selects the next priority, chooses the I/O after the last issued offset for LBA queues or oldest timestamp for FIFO queues, aggregates when possible, drops NODATA optional I/Os, and marks issued I/O active.
- `vdev_queue_io()` normalizes priority based on I/O type, adds `DONT_CACHE` and `DONT_QUEUE`, queues the zio, and may return an immediately issuable zio or start an aggregate.
- `vdev_queue_io_done()` removes completed active I/O, records latency, then issues as many newly eligible I/Os as possible.
- `vdev_queue_change_io_priority()` reprioritizes queued or not-yet-queued I/Os but not active I/Os.

## Important Behavior And Invariants
- Aggregated reads copy data from the aggregate ABD back into each parent on completion; writes copy each child write payload into the aggregate ABD before dispatch.
- Optional/NODATA I/Os are used to preserve write continuity and are completed without physical dispatch when selected alone.
- `vdev_queue_length()` and `vdev_queue_last_offset()` are intentionally lock-free approximations for load calculations.
- Priority is sanitized so child I/Os inherited from parents still land in a valid class for their read/write/TRIM type.

## Dependencies
Uses AVL trees, SPA I/O kstats, ZIO child/aggregate helpers, ABD copy/zero helpers, dirty-data state from the DSL pool, and queue state embedded in `vdev_t`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_queue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz.c

## Purpose
Implements RAID-Z vdev mapping, parity generation, reconstruction, read/write dispatch, checksum/parity verification, repair, dump I/O, resilver decisions, translation, and vdev ops registration. It supports single, double, and triple parity using GF(2^8) Reed-Solomon style coding.

## RAID-Z Layout And Math
- Parity columns are P, Q, and R. P is XOR parity; Q uses powers of 2; R uses powers of 4.
- `vdev_raidz_map_alloc()` maps a logical zio into columns, sizes, device indexes, offsets, parity/data counts, skipped sectors, and ABD slices.
- Short columns are treated as zero-filled during parity generation and reconstruction.
- A historical single-parity parity rotation based on bit 20 of logical offset is preserved as an on-disk format requirement.

## Main Structures
- `raidz_map_t` holds accessed columns, skipped columns, parity count, missing data/parity counts, ABD copy for reports, error-injection flag, ops pointer, and variable `raidz_col_t` array.
- `raidz_col_t` records child index, child offset, size, ABD, generated-good-data ABD, and I/O state/error flags.

## Key Mapping And Lifetime Functions
- `vdev_raidz_map_alloc()` calculates sector quotient/remainder, big columns, accessed/skipped columns, total asize, per-column child offsets, ABDs for parity and data, optional skip padding, and selected math ops.
- `vdev_raidz_map_free()` releases parity ABDs, data ABD references, generated data, and any checksum-copy ABD.
- `vdev_raidz_vsd_ops` wires map lifetime and checksum reporting into zio VSD handling.
- Checksum reporting keeps a copy of read data so later ereport finalization can compare bad disk data to the reconstructed good data.

## Parity Generation
- Scalar fallback functions generate P, PQ, or PQR parity using ABD iteration and 64-bit GF multiply helpers.
- `vdev_raidz_generate_parity()` first tries the selected RAID-Z math backend via `vdev_raidz_math_generate()` and falls back to original scalar implementations when the backend returns `RAIDZ_ORIGINAL_IMPL`.

## Reconstruction
- Optimized scalar special cases handle one missing data column via P or Q and two missing data columns via P+Q.
- `vdev_raidz_reconstruct()` classifies targeted and errored columns into bad parity and bad data, asks the math backend for reconstruction, tries optimized scalar paths, then falls back to general matrix reconstruction.
- General reconstruction builds selected Vandermonde/identity rows, removes failed rows, inverts the needed matrix rows using Gauss-Jordan elimination in GF(2^8), and reconstructs missing data columns.
- Nonlinear/scatter ABDs are converted to temporary linear ABDs for the matrix path, then copied back.
- `vdev_raidz_combrec()` attempts combinatorial reconstruction over possible bad columns after all columns have been read but checksum still fails, identifying silent corruption candidates.

## I/O Flow
- `vdev_raidz_open()` validates parity count and child count, opens children, computes aggregate size and max size from the minimum child sizes, and fails if open errors exceed parity.
- `vdev_raidz_io_start()` allocates the map. Writes generate parity, issue children for all accessed data/parity columns, and issue optional NODATA writes for skipped sectors to improve aggregation. Reads issue data-column reads by default and include parity reads when scrub/resilver or missing data requires it.
- `vdev_raidz_io_done()` accepts writes if failures do not exceed parity. Reads proceed through phases: verify checksum with available data, reconstruct known data failures, read all columns if needed, attempt combinatorial reconstruction, then either mark checksum verified or fail with `ECKSUM`/worst I/O error.
- On successful reads with unexpected errors or resilver flags, bad/stale columns are repaired with async write child I/Os and `IO_REPAIR`, optionally `SELF_HEAL`.
- `raidz_parity_verify()` regenerates parity and compares it with parity columns that were actually read, posting checksum errors for parity mismatches unless parity checksums are disabled with `ZIO_CHECKSUM_NOPARITY`.

## Dump I/O
`vdev_raidz_dumpio()` handles dump devices specially under `_KERNEL`: it maps a full 128 KiB logical block but reads/writes only the requested data-column portions and deliberately avoids parity for dump performance and simplicity.

## Resilver, State, And Translation
- `vdev_raidz_state_change()` faults the vdev when faulted children exceed parity, degrades it for any degraded/faulted child otherwise, and marks healthy with no child issues.
- `vdev_raidz_need_resilver()` returns true for full-width stripes or if any touched child has a nonempty partial DTL.
- `vdev_raidz_xlate()` translates a logical parent range to a child range by row/column math for leaf-level physical work such as initialization.

## Registered Ops
`vdev_raidz_ops` provides open/close/asize/io_start/io_done/state_change/need_resilver/xlate/dumpio and marks RAID-Z as a non-leaf vdev type.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math.c

## Purpose
Coordinates RAID-Z parity math implementations. It registers compiled backends, selects a backend at runtime, benchmarks supported implementations in kernel builds, exposes generation/reconstruction dispatch, and supports user selection by implementation name.

## Implementations
- `vdev_raidz_original_impl` is an opaque placeholder for the original scalar code in `vdev_raidz.c`; its NULL methods tell callers to use the original implementation.
- `vdev_raidz_scalar_impl` is always present when supported.
- On amd64, SSE2, SSSE3, and AVX2 implementations are included.
- `vdev_raidz_fastest_impl` is populated with the fastest method per generation/reconstruction function.

## Selection State
- `zfs_vdev_raidz_impl` is the active selector. Values include `fastest`, `cycle`, `original`, `scalar`, or an index into supported implementations.
- `user_sel_impl` records a user preference set before math initialization.
- `raidz_supp_impl[]` stores supported implementations after probing.
- `raidz_math_initialized` gates selectors that require benchmark/probe completion.

## Key Functions
- `vdev_raidz_math_get_ops()` returns scalar ops if FPU/SIMD is not allowed in the current context. Otherwise it returns fastest, cycles through supported impls, original, scalar, or an indexed supported implementation.
- `vdev_raidz_math_generate()` selects P, PQ, or PQR generation function from `rm_ops`; NULL means use original implementation.
- `vdev_raidz_math_reconstruct()` chooses a reconstruction function based on parity level, which parity columns are valid, and the number of bad data columns. Unsupported cases return `RAIDZ_ORIGINAL_IMPL`.
- `benchmark_raidz()` probes each implementation, calls optional init hooks, stores supported ops, and either benchmarks each method in kernel or picks the last supported implementation in user space to avoid zdb/zhack/zinject/ztest overhead.
- `benchmark_raidz_impl()` measures per-disk throughput for each method and records the best implementation for each function slot.
- `vdev_raidz_math_init()` benchmarks/probes and atomically applies the user selector.
- `vdev_raidz_impl_set()` sanitizes a requested name, accepts mandatory options (`cycle`, `fastest`, `original`, `scalar`) or initialized supported implementation names, then updates the active or pending selector.

## Important Behavior And Invariants
- SIMD backends are only used when `kfpu_allowed()` permits FPU use; otherwise scalar is selected regardless of the configured implementation.
- The fastest implementation is per-method, not necessarily a single backend for every parity operation.
- In user space, benchmarking is skipped deliberately; this changes selection behavior for libzpool consumers.
- Linux-only module parameter glue is present under `defined(_KERNEL) && defined(__linux__)`, but the illumos port comments note OpenZFS-style free-form kstats are omitted here.

## Dependencies
Uses RAID-Z implementation ops, ABD-backed synthetic zios/maps for benchmarks, SIMD/FPU availability helpers, GF method names, and kernel parameter support where available.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_avx2.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_avx2.c

## Purpose
Provides the amd64 AVX2 RAID-Z math backend. It defines vector-register helper macros for GF(2^8) operations, includes the generic RAID-Z math template, generates AVX2 parity/reconstruction methods, and registers support probing.

## Main Components
- amd64-only implementation guarded by `#if defined(__amd64)`.
- Inline assembly macros for YMM loads, stores, XOR, copy, zero, multiply-by-2, multiply-by-4, and table-based multiplication.
- FPU scope macros `raidz_math_begin()` and `raidz_math_end()` wrap `kfpu_begin()`, `vzeroupper`, and `kfpu_end()`.
- Stride/register mapping macros define how the shared `vdev_raidz_math_impl.h` template emits AVX2 variants for generation, syndrome, and reconstruction functions.
- `DEFINE_GEN_METHODS(avx2)` and `DEFINE_REC_METHODS(avx2)` instantiate method arrays.

## Key Operations
- `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, and `STORE` operate on 32-byte YMM lanes, typically in two- or four-register groups.
- `MUL2_SETUP()` prepares constants for GF multiply-by-2; `MUL2` and `MUL4` apply field multiplication with AVX2 byte operations.
- `MUL(c, ...)` uses lookup tables from `gf_clmul_mod_lt` and byte shuffles to multiply by arbitrary GF constants.
- `raidz_will_avx2_work()` requires FPU use to be allowed and CPU AVX plus AVX2 availability.

## Registered Ops
`vdev_raidz_avx2_impl` has generated `.gen` and `.rec` method arrays, no init/fini hooks, support callback `raidz_will_avx2_work`, and name `avx2`.

## 32-bit Stub
For `__i386`, the file exposes a stub `vdev_raidz_avx2_impl` with NULL method pointers and name `avx2`, satisfying user-level fakekernel dependencies without providing AVX2 operations.

## Important Behavior And Invariants
- Assembly paths assume aligned 32-byte vector operations through the template and ABD/method setup.
- `vzeroupper` is issued before leaving the AVX2 math scope to avoid AVX/SSE transition penalties and preserve kernel FPU hygiene.
- Unsupported contexts must be filtered by the math dispatcher or support predicate; direct use requires FPU/SIMD safety.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_avx2.c -->