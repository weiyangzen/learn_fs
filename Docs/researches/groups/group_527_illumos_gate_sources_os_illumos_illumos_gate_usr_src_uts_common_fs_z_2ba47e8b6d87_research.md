# Group Research: group_527_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_2ba47e8b6d87

Read completely under `Docs/research_subset_a.md` scope: 42 illumos ZFS headers, 7,764 total lines.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/metaslab_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/metaslab_impl.h

This private header defines the in-core state for the ZFS metaslab allocator: allocation tracing records, weight encoding, metaslab classes, metaslab groups, individual metaslabs, and the on-disk unflushed-TXG side record.

Core definitions:
- `metaslab_alloc_trace_t` records allocator attempts, selected group/metaslab, request size, weight, DVA, offset, and allocator index; `trace_alloc_type_t` reserves negative offset values for allocator failure reasons.
- Weight macros divide the 64-bit metaslab weight into active bits, space-vs-segment mode, histogram bucket index, and segment count.
- `metaslab_class` groups vdev allocation classes, owns allocator ops, rotor, allocation throttle state, class-wide space/histogram counters, and selected-TXG multilist.
- `metaslab_group` models a top-level vdev allocation domain with primary/secondary active metaslabs, AVL weight tree, allocation eligibility, queue-depth throttle counters, fragmentation/histogram summaries, and disabled-metaslab coordination.
- `metaslab` owns the per-metaslab locks, space map, alloc/free/defer/checkpoint/trim range trees, loaded/flushing/condensing flags, histograms, weights, active allocator state, auxiliary size-sorted btrees, unflushed log-spacemap trees, and sync-length tracking.

Important invariants:
- `ms_lock` serializes allocator/free paths with sync-side state; `ms_sync_lock` coordinates space-map writers and removal readers.
- Loaded and unloaded metaslabs compute weight from different data sources, so `ms_synchist` and `ms_deferhist` preserve exact spacemap histogram entries without range-tree consolidation drift.
- `ms_allocatable_by_size` must mirror `ms_allocatable` segment membership with a different ordering.
- `ms_unflushed_txg` means changes at that TXG and later live in log spacemaps, not the metaslab spacemap.
- Condensing, flushing, loading, disabling, and allocation activation are all explicit state-machine fields; callers must respect their lock and CV protocols.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/metaslab_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/mmp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/mmp.h

This header declares ZFS Multi-Modifier Protection state and tunables. MMP periodically writes heartbeat uberblocks so imports can detect an active pool on another host.

Core definitions:
- Tunables and bounds include `MMP_MIN_INTERVAL`, defaults for interval/import/fail intervals, safety factor, and normalization macros for minimum write/fail intervals.
- `mmp_thread_t` stores thread/CV state, I/O lock, last successful write time, delay estimate, last written uberblock copy, root zio, kstat sequence, skip error, last leaf, leaf-list generation, and sub-second sequence.
- Lifecycle APIs cover `mmp_init()`, `mmp_fini()`, `mmp_thread_start()`, `mmp_thread_stop()`, `mmp_update_uberblock()`, and `mmp_signal_all_threads()`.
- Global tunables are `zfs_multihost_interval`, `zfs_multihost_fail_intervals`, and `zfs_multihost_import_intervals`.

Risk-sensitive invariants:
- Delay, sequence, and last-leaf fields are protected by `mmp_io_lock`; thread management fields are protected by `mmp_thread_lock`.
- MMP writes are based on the last synced uberblock and are meaningful only with the uberblock MMP fields in `uberblock_impl.h`.
- Import safety depends on conservative interval/fail-interval validation and visible heartbeat progress on writable leaf vdevs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/mmp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/multilist.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/multilist.h

This header declares `multilist_t`, a sharded list abstraction used to reduce lock contention while preserving normal list semantics within each sublist.

Core definitions:
- `multilist_node_t` aliases `list_node_t`; callers embed it in listed objects.
- `multilist_sublist_t` contains a per-sublist mutex, illumos `list_t`, and cache-line padding.
- `multilist_t` records the embedded-node offset, sublist count, sublist array, and caller-supplied object-to-sublist index function.
- Whole-list APIs create/destroy, insert/remove, test emptiness, expose sublist count, and choose a random sublist.
- Sublist APIs explicitly lock by index or object, insert/remove/move entries, and traverse head/tail/next/prev.

Risk-sensitive invariants:
- The index function must be stable while an object is inserted if callers use whole-list remove.
- Traversal safety is per-sublist; there is no single global lock for a consistent whole-list snapshot.
- Direct sublist APIs require callers to hold and release the matching sublist lock correctly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/multilist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/range_tree.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/range_tree.h

This header declares ZFS range trees, the non-concurrent extent-set abstraction used by metaslabs, spacemaps, trim, checkpoints, and removal accounting.

Core definitions:
- `RANGE_TREE_HISTOGRAM_SIZE` is 64 buckets.
- `range_seg_type_t` supports compact 32-bit, 64-bit, and gap/fill segment forms.
- `range_tree_t` stores an offset-ordered `zfs_btree_t`, total represented space, segment encoding, start/shift normalization, optional callback ops/arg, optional secondary btree comparator, allowable gap, and size histogram.
- Segment structs include `range_seg32_t`, `range_seg64_t`, and `range_seg_gap_t`; `range_seg_max_t` is the stack-safe maximum representation.
- Inline accessors convert raw stored starts/ends/fill values to logical byte offsets with `rt_start` and `rt_shift`, and enforce alignment and 32-bit limits on mutation.
- `range_tree_ops_t` lets consumers mirror create/destroy/add/remove/vacate events into secondary structures.

Public API surface:
- Lifecycle: create, create implementation, destroy.
- Query: contains/find/find_in, first, min/max/span, space, number of segments, empty check, histogram verification.
- Mutation: add/remove/remove_fill/clear, resize, adjust fill, swap, vacate, walk.
- Delta helpers: `range_tree_remove_xor_add_segment()` and `range_tree_remove_xor_add()`.
- Built-in secondary btree callbacks are exported as `rt_btree_ops`.

Risk-sensitive invariants:
- Range trees are explicitly not internally synchronized; consumers provide external locking.
- All stored offsets and sizes must be aligned to `1 << rt_shift` and be at or above `rt_start`.
- For non-gap segment types, fill must equal segment length; gap trees have different fill semantics.
- Histograms and `rt_space` are allocator-critical and must track every add/remove/split/merge.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/range_tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/refcount.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/refcount.h

This header declares ZFS debug-aware reference counters. In debug builds it tracks owners and reference numbers; in non-debug builds it compiles down to atomic count operations.

Core definitions:
- `FTAG` uses the current function name as a holder tag for function-scoped holds.
- `zfs_refcount_t` in debug builds stores count, mutex, AVL tree of active references, removed-reference list/count, and tracking mode.
- `reference_t` records holder tag, removed marker, reference number, and search/link state.
- Non-debug `zfs_refcount_t` is just a `uint64_t rc_count` with macro implementations.

Public API surface:
- Create/destroy tracked or untracked counters, including destroy with expected count.
- Count/zero queries and add/remove single references.
- `add_few`/`remove_few` adjust many independently removable references.
- `add_many`/`remove_many` add one tracked reference with a larger reference number that must be removed as a unit.
- Transfer counts or transfer ownership tags, and query whether a holder has or lacks a reference.
- Global `zfs_refcount_init()` / `zfs_refcount_fini()` exist only for debug tracking support.

Risk-sensitive invariants:
- Debug `add_many()` and `remove_many()` semantics are not equivalent to repeated single-reference operations.
- Holder tags are correctness aids in debug builds and become largely advisory in non-debug builds.
- Non-debug held checks only prove the count is nonzero, not ownership by a specific holder.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/refcount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/rrwlock.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/rrwlock.h

This header declares ZFS re-entrant reader/writer locks and reader-mostly locks built on top of them.

Core definitions:
- `rrwlock_t` contains a mutex, CV, current writer thread, anonymous-reader refcount, linked-reader refcount, writer-wanted flag, and `track_all` mode.
- `rrw_enter_read_prio()` is the priority read path for readers that may need to bypass waiting writers.
- Held macros wrap `rrw_held()` for read, write, and any-lock checks.
- `rrmlock_t` contains `RRM_NUM_LOCKS` (`17`) `rrwlock_t` shards for scalable read acquisition.

Public API surface:
- `rrw_init()`, `rrw_destroy()`, generic/read/write/prio-read enter, exit, held query, and TSD destructor.
- `rrm_init()`, `rrm_destroy()`, generic/read/write enter, exit, and held query.

Risk-sensitive invariants:
- Tags passed to `rrw_enter()` and `rrw_exit()` must match for tracked reader references.
- `rrwlock_t` allows re-entrant reads but not writer re-entrancy or upgrades.
- `rrmlock_t` pessimizes writers by acquiring all shards; read release must correspond to the thread/shard used at acquire time.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/rrwlock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/sa.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/sa.h

This public header declares the System Attributes (SA) interface used to pack typed object attributes into DMU bonus and spill buffers.

Core definitions:
- `sa_bswap_type_t` enumerates supported byteswap formats: uint arrays of 64/32/16/8 bits and ACLs.
- `sa_attr_type_t` is a 16-bit attribute ID.
- `sa_attr_reg_t` describes an attribute name, fixed length, byteswap class, and assigned ID.
- `sa_data_locator_t` callbacks can locate or synthesize attribute data for update paths.
- `sa_bulk_attr_t` carries attribute descriptors for bulk lookup/update/replace, with private fields filled by SA internals.
- `SA_ADD_BULK_ATTR()` appends a bulk descriptor and increments the caller's index.
- `sa_handle_type_t` selects shared vs private SA handles.

Public API surface:
- Handle acquisition from object or existing dbuf, handle destruction, dbuf hold/release, userdata accessors, lock/unlock helpers.
- Single and bulk lookup/update/remove/size operations.
- Callback-based update, object info/size queries, spill prediction, setup/teardown, replace-all-by-template, SA enablement, cache init/fini, and SA object configuration.
- Kernel-only `sa_lookup_uio()` and `sa_add_projid()` support ZPL-specific paths.

Risk-sensitive invariants:
- Attribute IDs and registered byteswap classes are persistent compatibility surface.
- Transactions must be supplied for mutating operations and must follow DMU transaction rules.
- Bulk descriptors are opaque except through the provided macro and APIs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/sa.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/sa_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/sa_impl.h

This private header defines the in-memory and on-disk implementation details behind System Attributes.

Core definitions:
- `sa_attr_table_t` stores per-attribute ID, registration state, fixed length, byteswap class, and name.
- `ATTR_*` macros encode/decode persistent registry entries containing attr number, byteswap type, and length.
- `TOC_*` macros encode/decode per-layout table-of-contents entries: presence, variable-length index, and offset.
- `SA_LAYOUTS` and `SA_REGISTRY` name the ZAP objects used for persistent metadata.
- `sa_lot_t` is a layout table entry keyed by layout number and by hash, with ordered attributes, variable-size count, total attr count, and cached index tables.
- `sa_idx_tab_t` caches offsets for a layout and variable-length vector, with refcounted sharing across handles.
- `sa_os` stores objset-level SA state: locks, master/registry/layout objects, private attr table, layout AVL trees, update callback, and caller name-to-attr table.
- `sa_hdr_phys_t` is the bonus/spill header with magic, encoded layout number/header size, and optional variable-length array.
- `sa_handle` stores DB user data, handle lock, bonus/spill dbufs, objset, user pointer, and cached index tables.

Important macros and APIs:
- Header macros extract/set layout number, header size, and header layout info.
- Buffer macros select bonus vs spill dbufs, headers, and index tables.
- `SA_LAYOUT_NUM()` maps legacy non-SA or zero-layout cases to layout conventions.
- Internal helpers include `sa_add_impl()`, update callback registration, locked size query, default locator, and attribute-size lookup.

Risk-sensitive invariants:
- `SA_MAGIC`, layout numbers, registry encoding, and header-size encoding are on-disk format.
- Variable-length attributes require matching header-size and layout metadata.
- Index tables are shared with refcounts; handle rebuild/destruction must balance holds.
- Legacy non-SA bonus types map through special layout logic and cannot be treated as normal SA headers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/sa_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/simd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/simd.h

This header abstracts SIMD/FPU availability and kernel FPU enter/exit handling for ZFS acceleration code.

Core behavior:
- On x86, `kfpu_initialize()`, `kfpu_init()`, and `kfpu_fini()` are no-op/success macros for this platform.
- In the kernel, `kfpu_allowed()` checks the global `zfs_fpu_enabled` tunable and disables FPU use during panic handling.
- Kernel `kfpu_begin()` uses `KFPU_USE_LWP` for system processes with LWPs, otherwise disables preemption and uses `KFPU_NO_STATE`; `kfpu_end()` mirrors that path.
- Kernel feature predicates query `x86_featureset` for SSE, SSE2, SSE3, SSSE3, AVX, AVX2, AVX512F, and AVX512BW.
- User-level feature predicates query `getisax()` and ISA extension bits.
- Non-x86 builds always disallow kernel FPU support and provide no-op enter/exit stubs.

Risk-sensitive invariants:
- FPU sections must be bracketed by begin/end and cannot run while panic handling.
- AVX/AVX512 feature selection depends on both platform support and the caller respecting `kfpu_allowed()`.
- Non-x86 code paths must tolerate SIMD acceleration being unavailable.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/simd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa.h

This major public header defines the Storage Pool Allocator interface, core block-pointer/DVA layout, pool-level constants, config lock classes, async task flags, and a broad set of exported SPA/vdev/property/error/history APIs.

Core on-disk definitions:
- SPA block constants define supported block sizes, ashift range, config block size, DVA bit widths, compression/vdev bit widths, and the 128-byte `blkptr_t`.
- `dva_t` stores two opaque 64-bit DVA words; macros get/set ASIZE, GRID, VDEV, OFFSET, and GANG fields.
- `zio_cksum_salt_t` stores a 256-bit secret checksum/MAC salt.
- `blkptr_t` stores three DVAs, encoded block properties, padding, physical/logical birth TXGs, fill count, and 256-bit checksum.
- Extensive `BP_*` and `BPE_*` macros encode/decode normal, encrypted/authenticated, indirect-MAC, embedded, hole, gang, dedup, byteorder, fill, IV, size, and type/level fields.
- `SNPRINTF_BLKPTR()` formats block pointers for kernel, libzpool, and mdb callers.

SPA API surface:
- Pool lifecycle: open, rewind-open, create, import, tryimport, destroy, checkpoint, export, reset, stats.
- Async requests and task flags include config update, remove/probe/resilver, autoexpand, initialize/TRIM restarts, autotrim, and L2ARC rebuild.
- Vdev operations cover add/attach/detach/remove/initialize/TRIM/path/fru/split.
- Global spare and L2ARC device management APIs.
- Scan/scrub/resilver control and SPA sync entry points.
- Config cache generation/loading/update APIs, namespace lookup/add/remove/iteration, open refcount APIs, config locks, and vdev enter/exit locks.
- Accessors expose pool state, txgs, allocation classes, checkpoint/slop/dspace, features, roots, log state, import progress, event posting, error logging, waiters, and miscellaneous support routines.

Risk-sensitive invariants:
- Block-pointer bit layouts are on-disk format and shared across kernel, userland tools, and debuggers.
- Encrypted block pointers sacrifice the third DVA for salt/IV data and truncate fill to 32 bits.
- Embedded block pointers do not reference disk space and must use embedded-specific size/type macros.
- SPA config locks are divided into `SCL_*` classes; callers must use the correct lock class and rw mode.
- Many APIs are sync-context, config-lock, or transaction-context sensitive even though this header only declares them.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_boot.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_boot.h

This small header declares boot-time SPA support hooks.

Core API surface:
- `spa_get_bootprop()` retrieves a named boot property string.
- `spa_free_bootprop()` releases a returned property value.
- `spa_arch_init()` performs architecture-specific boot SPA initialization.

Risk-sensitive invariants:
- Returned boot property memory must be released through the matching SPA helper.
- This interface is intentionally minimal and depends only on nvpair-facing boot configuration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_boot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_checkpoint.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_checkpoint.h

This header declares pool checkpoint accounting and discard-thread entry points.

Core definitions:
- `spa_checkpoint_info_t` stores checkpoint timestamp and disk space consumed by checkpoint-preserved blocks.

Public API surface:
- User-facing operations: `spa_checkpoint()` and `spa_checkpoint_discard()`.
- Background discard zthr hooks: `spa_checkpoint_discard_thread_check()` and `spa_checkpoint_discard_thread()`.
- Stats export: `spa_checkpoint_get_stats()`.

Risk-sensitive invariants:
- Checkpoint space is pool-level accounting and must align with checkpointed uberblock semantics.
- Discard work is asynchronous through `zthr_t`; check/sync code must coordinate with pool lifecycle.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_checkpoint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_checksum.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_checksum.h

This header defines the generic 256-bit ZFS checksum value and basic checksum macros.

Core definitions:
- `zio_cksum_t` contains four 64-bit words.
- `ZIO_SET_CHECKSUM()` assigns all four words.
- `ZIO_CHECKSUM_EQUAL()` compares checksums by OR-ing word deltas.
- `ZIO_CHECKSUM_IS_ZERO()` tests for an all-zero checksum.
- `ZIO_CHECKSUM_BSWAP()` byte-swaps each checksum word in place.

Risk-sensitive invariants:
- This type is embedded in `blkptr_t` and is part of on-disk metadata.
- Byte swapping must be applied per 64-bit word, not to the structure as arbitrary bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_checksum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_impl.h

This private header defines internal SPA structures: error entries, history records, vdev-removal and indirect-condensing physical records, aux-vdev sets, config locks, taskq state, import config sources, and the full `struct spa`.

Core definitions:
- `spa_error_entry_t` stores error bookmarks, object names, and AVL linkage.
- `spa_history_phys_t` tracks persistent history log offsets and lost-record count.
- `spa_removing_phys_t` is persistent pool-removal progress: state, removing/previous indirect vdev IDs, start/end time, bytes to copy, and bytes copied/freed.
- `spa_condensing_indirect_phys_t` persists an in-progress indirect-vdev mapping condense operation.
- `spa_aux_vdev` caches spare/L2ARC config, active vdevs, pending additions, and sync state.
- `spa_config_lock_t` combines mutex, writer pointer, wanted count, CV, and debug refcount.
- `spa_taskqs_t`, `zio_taskq_type_t`, `spa_proc_state_t`, `spa_avz_action_t`, and `spa_config_source_t` define internal scheduling, per-pool process, all-vdev-ZAP, and import-source state.

`struct spa` responsibilities:
- Namespace/config/load state, taskqs, DSL pool, allocation classes, txg/vdev dirty lists, root vdev, ashift bounds, GUIDs, config dirtiness, allocator locks/trees.
- Aux devices, labels/features, MOS objects, checksum salt/templates, uberblocks, scrub/resilver, async tasks, missing-vdev import policy.
- Vdev removal, indirect condensing, checkpoints, log spacemap tracking, error logs, history, properties, pool I/O roots, suspension, claiming, log state, DDT, dedup defaults, feature objects/cache, deadman, all-vdev-ZAP, autotrim, keystore, kstats, MMP, leaf list, and waiters.
- `spa_refcount` and `spa_config_lock[]` are intentionally last for MDB layout compatibility.

Risk-sensitive invariants:
- Many fields are protected by different locks named in comments; callers must follow the matching lock domain.
- Persistent physical structs must remain byteswappable and format-compatible.
- Import/load, sync, removal, checkpoint, log-spacemap, MMP, and suspend state all coexist in one SPA object, so state transitions must avoid cross-subsystem races.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_log_spacemap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_log_spacemap.h

This header declares pool-wide log spacemap state and helpers for batching metaslab allocation/free deltas before flushing them back to individual metaslab spacemaps.

Core definitions:
- `DIV_ROUND_UP` local helper is defined if absent.
- `log_summary_entry_t` tracks a start TXG, remaining metaslabs to flush, block count, and list linkage.
- `spa_unflushed_stats_t` tracks memory used by unflushed trees plus block-limit and block-count heuristics.
- `spa_log_sm_t` records a log spacemap object, its TXG, block count, metaslabs flushed in that TXG, and AVL linkage by TXG.

Public API surface:
- Load/generate/flush/close log spacemaps, clean old logs, compute/set block limits, query block and memory usage.
- Decrement/increment metaslab counts for log spacemap and log summary accounting.
- Add flushed metaslabs to summaries, decrement summary block counts, and query flush-all requests.
- Tunable `zfs_keep_log_spacemaps_at_export`.

Risk-sensitive invariants:
- Log spacemaps introduce unflushed allocator deltas; metaslab load/sync/flush code must not double-apply or lose them.
- Summary counts determine when old log spacemap records can be cleaned.
- Memory and block heuristics affect when accumulated unflushed state is forced back to metaslab spacemaps.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_log_spacemap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/space_map.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/space_map.h

This header defines ZFS space maps: on-disk append logs of allocated/free ranges plus in-core handles for loading, writing, truncating, and histogram maintenance.

Core definitions:
- `space_map_phys_t` contains legacy object field, object length, allocated-space count, padding, and 32-bucket histogram.
- `space_map_t` records the logical region start/size, unit shift, objset/object/blocksize, dbuf, and physical bonus pointer.
- `maptype_t` distinguishes `SM_ALLOC` and `SM_FREE`.
- `space_map_entry_t` is the decoded entry form: type, optional vdev ID, offset, and run length in `sm_shift` units.
- Encoding macros define debug entries, single-word entries, and two-word entries, including offset/run/vdev/type limits.

Public API surface:
- Entry classification helpers for debug/single/double word entries.
- Load full or length-limited spacemaps into range trees, iterate entries, and incrementally destroy.
- Histogram verify/clear/add helpers.
- Accessors for object, allocated space, length, entry count, and block count.
- Write range-tree deltas, estimate optimal size, truncate, allocate/free objects, open/close handles.

Risk-sensitive invariants:
- Space maps are not internally concurrent; callers provide synchronization.
- Two-word entries must not straddle block boundaries; padding uses debug entries.
- `smp_histogram` is allocator-visible and may include log-spacemap unflushed changes for metaslab spacemaps.
- Offsets and runs are encoded in `sm_shift` units and must respect single/two-word maximums.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/space_map.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/space_reftree.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/space_reftree.h

This header declares a small AVL-backed reference-counted space-range helper.

Core definitions:
- `space_ref_t` stores an AVL node, range boundary offset, and signed reference-count delta.

Public API surface:
- Create/destroy a reftree AVL.
- Add a segment with a signed refcount over `[start, end)`.
- Add every segment from a `range_tree_t` with a signed refcount.
- Generate a range tree containing ranges whose accumulated reference count reaches a caller-specified minimum.

Risk-sensitive invariants:
- The structure appears to model sweep-line reference deltas at offsets, so start/end ordering and signed counts must balance.
- Generated maps depend on the caller choosing the correct `minref` threshold.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/space_reftree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/txg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/txg.h

This header declares transaction group constants, handles, per-TXG object lists, and synchronization APIs.

Core definitions:
- `TXG_CONCURRENT_STATES` is 3 for open/quiescing/syncing.
- `TXG_SIZE` is 4, `TXG_MASK` indexes circular arrays, `TXG_INITIAL` is the first txg, and `TXG_DEFER_SIZE` is 2.
- `txg_handle_t` records the per-CPU hold object and assigned txg.
- `txg_node_t` embeds per-TXG next pointers and membership flags in dirty objects.
- `txg_list_t` stores a lock, embedded-node offset, owning SPA, and per-TXG heads.

Public API surface:
- Init/fini and sync-thread start/stop.
- Hold open txg, release to quiesce/sync, register commit callbacks, delay or kick sync.
- Wait for synced/open txgs, including signal-aware wait, stalled/sync-waiting queries, and verification.
- Per-TXG list create/destroy, empty checks, add/head/tail/remove/remove-this/member/head/next.

Risk-sensitive invariants:
- TXG arrays are circular and must use the proper txg index.
- Objects may be members of different per-TXG lists simultaneously only through the explicit `txg_node_t` membership fields.
- Hold/release ordering drives quiesce/sync progress and must be balanced by transaction users.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/txg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/txg_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/txg_impl.h

This private header defines the implementation state for transaction group progression.

Core definitions:
- `tx_cpu` is per-CPU state with `tc_open_lock`, `tc_lock`, per-TXG CVs, per-TXG hold counts, per-TXG callback lists, and padding.
- `tx_state_t` stores the per-pool TXG state machine: per-CPU array, sync lock, open/quiescing/quiesced/syncing/synced txg IDs, open timestamp, waiting txg values, CVs, exit flags, sync/quiesce threads, and commit-callback taskq.

Important concurrency model:
- Frequent hold-count updates are fanned out by CPU to avoid a single hot lock.
- `tx_open_txg` is protected by every CPU's `tc_open_lock`, not by `tx_sync_lock`.
- Quiescing must acquire all `tc_open_lock`s before moving the open txg forward.

Risk-sensitive invariants:
- `tc_count[txg]` must reach zero on all CPUs before a txg is quiesced.
- Sync/quiesce CVs and waiting fields drive user waits and sync-thread progress.
- Commit callbacks are stored per TXG and dispatched after the corresponding sync boundary.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/txg_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/uberblock.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/uberblock.h

This public header forward-declares uberblocks and exposes verification/update helpers.

Core API surface:
- `uberblock_t` is an opaque typedef for `struct uberblock`.
- `uberblock_verify()` validates an uberblock.
- `uberblock_update()` updates an uberblock for a root vdev, target TXG, and MMP delay.

Risk-sensitive invariants:
- Actual layout is private to `uberblock_impl.h` but is persistent pool metadata.
- Update must coordinate with root vdev state and MMP heartbeat semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/uberblock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/uberblock_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/uberblock_impl.h

This private header defines the on-disk uberblock layout and MMP field encoding.

Core definitions:
- `UBERBLOCK_MAGIC`, `UBERBLOCK_SHIFT`, and `MMP_MAGIC` identify uberblocks and MMP heartbeat data.
- MMP valid-bit macros and getters/setters encode write interval, sequence, and fail intervals into `ub_mmp_config`.
- `struct uberblock` stores magic, SPA version, synced txg, vdev guid sum, timestamp, MOS root block pointer, writing software version, MMP magic/delay/config, and checkpoint TXG.

Risk-sensitive invariants:
- `ub_magic` and `ub_version` must remain the first two fields so version/magic can be read before compatibility is known.
- `ub_mmp_delay == 0` with valid MMP magic means MMP is off.
- `ub_checkpoint_txg` marks checkpointed uberblocks and determines claim behavior when rewinding to a checkpoint.
- MMP config bit widths cap interval and sequence/fail values; setters mask values into the persistent layout.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/uberblock_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/unique.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/unique.h

This header declares a small unique-value allocator used by ZFS code needing non-colliding 56-bit identifiers.

Core definitions:
- `UNIQUE_BITS` is 56 significant bits per unique value.

Public API surface:
- `unique_init()` / `unique_fini()` initialize and tear down global state.
- `unique_create()` returns a new candidate value that is not made collision-reserved until insertion.
- `unique_insert()` returns a unique value equal to the requested value if possible.
- `unique_remove()` releases a value from future uniqueness checks.

Risk-sensitive invariants:
- Creation and insertion are distinct; callers that need reservation must insert.
- Values outside the significant-bit model should not be assumed preserved.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/unique.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev.h

This public header declares the virtual-device interface: lifecycle, DTLs, state, metaslabs, stats, labels, queue/cache, and config generation.

Core definitions:
- `vdev_dtl_type_t` enumerates missing, partial, scrub, outage, and count DTLs.
- Global `zfs_nocacheflush` controls cache flush behavior.
- `vdev_config_flag_t` marks spare, L2ARC, removing, MOS, and missing config generation modes.
- `vdev_labeltype_t` describes label initialization reasons: create, replace, spare, remove, L2ARC, and split.

Public API surface:
- Vdev debug, open/validate/create/reopen/close/probe, path copy, zvol-use detection, concrete/bootable checks, lookup/count helpers.
- DTL dirty/contains/empty/need-resilver/reassess/required/resilver-needed APIs.
- ZAP link management, spacemap destruction, obsolete marking, replacement progress, vdev hold/release.
- Metaslab init/fini/size/expand/split/deadman/xlate APIs.
- Stats update/get/clear/scan init/propagate/set-state/children-offline helpers.
- Space accounting, deflation, psize-to-asize, fault/degrade/online/offline/clear, liveness/readable/writeable/allocatable/accessibility checks.
- Cache and queue init/fini/read/write/purge/IO/priority helpers.
- Config/state dirty/clean/sync, deferred resilver, config generation, label offsets/config/uberblock load/bootenv read/write/label init.

Risk-sensitive invariants:
- DTLs are central to resilver safety and replication accounting.
- Label routines operate on persistent disk labels and bootenv data.
- Vdev state changes must coordinate with SPA config/state locks and dirty lists.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_file.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_file.h

This header defines file-backed vdev type-specific state.

Core definition:
- `vdev_file_t` contains the backing file `vnode_t *vf_vnode`.

Risk-sensitive invariants:
- File vdev operations must manage vnode lifetime outside this struct.
- The header intentionally contains no public operations; it is type-specific data consumed by vdev file code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_impl.h

This private header defines vdev operations, queues, caches, indirect state, the full `struct vdev`, persistent label layout, and internal vdev helper APIs.

Core definitions:
- `vdev_ops_t` contains type operations for open/close/asize/io start/done/state change/resilver need/hold/release/remap/xlate/dumpio plus type name and leaf flag.
- `vdev_cache_entry_t`, `vdev_cache_t`, `vdev_queue_class_t`, and `vdev_queue_t` define physical cache and queue scheduling state.
- `vdev_alloc_bias_t` distinguishes none, log, special, and dedup allocation classes.
- `vdev_indirect_config_t` records MOS object IDs for indirect mapping and birth arrays plus previous indirect vdev ID.
- `struct vdev` contains common identity/topology/state/stat fields, top-level metaslab fields, checkpoint/initialize/TRIM state, indirect/removal/obsolete fields, scan queue, leaf DTL/device/path/state/cache/queue/probe/MMP fields, and DTrace-sensitive final mutexes.
- Label constants define 256 KiB vdev labels, boot area offsets/sizes, uberblock ring layout, MMP slots, and boot envblock format.

Internal API surface:
- Allocate/free vdevs, manipulate parent/child topology, load/sync DTL and vdev state, dirty vdev components.
- Export ops structures for root, mirror, replacing, raidz, disk, file, missing, hole, spare, and indirect vdevs.
- Default size/xlate helpers and metaslab/vdev cache tunables.
- Indirect-vdev obsolete sync/condense helpers.
- Boot-from-ZFS disk label helper APIs.

Risk-sensitive invariants:
- `struct vdev` spans top-level, non-leaf, and leaf state; many fields are meaningful only for specific vdev kinds.
- Label geometry and uberblock offsets are persistent disk format.
- Indirect mapping pointers are protected by `vdev_indirect_rwlock`; obsolete segments have separate locking.
- Final DTrace-sensitive mutex fields must remain at the end for userland/kernel CTF compatibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_indirect_births.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_indirect_births.h

This header declares the birth-time side table for indirect vdev mappings created during device removal.

Core definitions:
- `vdev_indirect_birth_entry_phys_t` stores a source offset boundary and physical birth TXG.
- `vdev_indirect_birth_phys_t` stores the number of birth entries.
- `vdev_indirect_births_t` stores object ID, in-memory sorted entry array, objset, dbuf, and bonus pointer.

Public API surface:
- Open/close/is-open, allocate/free object, count/object accessors.
- Add an entry for an offset and TXG.
- Query physical birth for a range and get the last entry TXG.

Risk-sensitive invariants:
- Entries are sorted by increasing physical birth and offset; lookup semantics depend on "everything up to but not including offset" boundaries.
- Birth TXGs determine whether remapped data is old enough for a given block pointer or rewind context.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_indirect_births.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_indirect_mapping.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_indirect_mapping.h

This header declares indirect vdev mapping objects, used to translate offsets from removed vdevs to replacement DVAs.

Core definitions:
- `vdev_indirect_mapping_entry_phys_t` stores encoded source offset/mark in `vimep_src` and destination DVA in `vimep_dst`.
- `DVA_MAPPING_GET_SRC_OFFSET()` and `DVA_MAPPING_SET_SRC_OFFSET()` encode/decode source offsets in SPA minimum-block units.
- `vdev_indirect_mapping_entry_t` wraps a physical entry with obsolete-count and list linkage for pending updates.
- `vdev_indirect_mapping_phys_t` stores max offset, bytes mapped, entry count, and obsolete-counts object.
- `vdev_indirect_mapping_t` stores object ID, whether counts exist, sorted in-memory entry array, objset, dbuf, and bonus pointer.

Public API surface:
- Open/close, allocate/free mapping object.
- Query entry count, max offset, object ID, bytes mapped, and mapping size.
- Add pending mapping entries from a list.
- Find mapping entry for an offset or the next mapping entry at/after an offset.
- Load, populate, increment, and free obsolete-count arrays from obsolete spacemaps.

Risk-sensitive invariants:
- Mapping entries are sorted by source offset and DVA ASIZE limits individual mapped ranges.
- Obsolete counts are used during indirect-vdev condense and must remain aligned with mapping entries.
- The high source-offset mark bit is reserved for garbage collection tooling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_indirect_mapping.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_initialize.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_initialize.h

This header declares vdev initialization control APIs. Initialization writes across allocatable space so later reads avoid exposure to stale media state.

Public API surface:
- `vdev_initialize()` starts initialization for a vdev.
- `vdev_initialize_stop()` stops one vdev toward a target state and records it in a caller list.
- `vdev_initialize_stop_all()` applies a target state to a subtree.
- `vdev_initialize_stop_wait()` waits for stop completion for a SPA/list.
- `vdev_initialize_restart()` restarts initialization.

Risk-sensitive invariants:
- The actual progress fields and thread/CV state live in `struct vdev`.
- Stop/restart operations must coordinate with spa async tasks and vdev lifecycle.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_initialize.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_raidz.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_raidz.h

This public header declares RAID-Z map and math-selection interfaces.

Public API surface:
- `vdev_raidz_map_alloc()` and `vdev_raidz_map_free()` allocate/free a `raidz_map` for a zio and geometry.
- `vdev_raidz_generate_parity()` generates parity columns.
- `vdev_raidz_reconstruct()` reconstructs missing data/parity targets.
- Math subsystem lifecycle and dispatch: `vdev_raidz_math_init()`, `vdev_raidz_math_fini()`, `vdev_raidz_math_get_ops()`, `vdev_raidz_math_generate()`, `vdev_raidz_math_reconstruct()`, and `vdev_raidz_impl_set()`.

Risk-sensitive invariants:
- The public interface is intentionally opaque; detailed map geometry and implementation operations are in `vdev_raidz_impl.h`.
- Userland builds define a dummy `kernel_param` for shared code compatibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_raidz.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_raidz_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_raidz_impl.h

This private header defines RAID-Z parity/reconstruction operation tables, map/column structures, implementation wrappers, kstats, and Galois-field helpers.

Core definitions:
- Parity code indexes `CODE_P`, `CODE_Q`, `CODE_R`; parity widths `PARITY_P`, `PARITY_PQ`, `PARITY_PQR`; reconstruction targets `TARGET_X/Y/Z`.
- `raidz_math_gen_op` and `raidz_rec_op` enumerate parity generation and reconstruction methods.
- `raidz_impl_ops_t` contains init/fini, generation function array, reconstruction function array, support predicate, and implementation name.
- `raidz_col_t` stores child index, offset, size, ABD, known-good copy, error, tried, and skipped state.
- `raidz_map_t` stores column counts, size/asize, missing counts, first data column, skip/padding information, ABD copy, report/freed/injected flags, selected ops, and flexible column array.
- Implementation symbols include scalar and x86 SSE2/SSSE3/AVX2 ops when built for x86.
- Wrapper macros generate implementation-specific dispatch functions and ops-array initializers.
- `raidz_impl_kstat_t` reports generation/reconstruction speeds.
- `raidz_mul_info_t` indexes multiplication constants needed by reconstruction formulas.

Galois-field helpers:
- Extern aligned pow/log tables map GF(2^8) exponent/log values.
- Inline `vdev_raidz_exp2()`, `gf_mul()`, `gf_div()`, `gf_inv()`, `gf_exp2()`, and `gf_exp4()` implement field arithmetic.

Risk-sensitive invariants:
- Reconstruction math assumes nonzero divisors where asserted and wraps exponents modulo 255.
- SIMD implementation selection must use `is_supported()` before dispatch.
- `raidz_map_t` is variable-sized with one trailing column and must be allocated by the RAID-Z map allocator.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_raidz_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_removal.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_removal.h

This header declares active vdev removal and indirect-vdev condensing state.

Core definitions:
- `spa_vdev_removal_t` stores removing vdev ID, per-TXG max offset to sync, removal thread, current metaslab allocated segments, lock/CV/exit flag, per-TXG new mapping lists, per-TXG frees intersecting in-flight mappings, per-TXG bytes done, and leaf-ZAP unlink list.
- `spa_condensing_indirect_t` stores per-TXG new mapping entries and the new mapping object during condense.

Public API surface:
- Initialize/restart removal and initialize/finalize/start/suspend indirect condensing.
- Start/cancel/suspend vdev removal, free ranges from the removing vdev, get removal stats, sync removal state, and destroy removal state.
- Tunables `vdev_removal_max_span` and `zfs_remove_max_segment`.

Risk-sensitive invariants:
- New mapping lists and free-range trees are per-TXG because removal updates are synced transactionally.
- Frees racing with copied mappings must be accounted so the removal does not preserve dead data.
- Condensing replaces indirect mapping state and must coordinate with readers via vdev indirect locks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_removal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_trim.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_trim.h

This header declares manual TRIM and autotrim control APIs for vdevs.

Core API surface:
- Tunable `zfs_trim_metaslab_skip` controls metaslab skipping behavior.
- `vdev_trim()` starts TRIM for a vdev with rate, partial, and secure flags.
- Stop/stop-all/stop-wait/restart helpers manage manual TRIM state.
- `vdev_autotrim()`, `vdev_autotrim_stop_all()`, `vdev_autotrim_stop_wait()`, and `vdev_autotrim_restart()` manage background autotrim.

Risk-sensitive invariants:
- Manual TRIM and autotrim have separate thread/lock/CV state in `struct vdev`.
- Secure and partial TRIM flags change device commands and accounting semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_trim.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zap.h

This public header declares the ZFS Attribute Processor, a DMU-backed name/value object store used for directories, metadata maps, feature state, and many pool/filesystem tables.

Core model:
- ZAP objects store zero-terminated string names up to `ZAP_MAXNAMELEN` and integer-array values up to `ZAP_MAXVALUELEN`, with element sizes of 1, 2, 4, or 8 bytes.
- `matchtype_t` controls normalized/case-sensitive matching.
- `zap_flags_t` selects 64-bit hashes, uint64-array binary keys, and pre-hashed keys.

Public API surface:
- Create APIs support normal, normalized, flag-controlled, linked, claimed, and custom dnode-size ZAP objects.
- Lookup APIs support strings, normalized string lookup, uint64-array keys, dnode-based lookup, prefetch, containment, and write-count estimation.
- Mutation APIs add, update, length-query, remove, count, value-search, join, join-key, join-increment, int-key helpers, and increment helpers.
- Cursor APIs initialize/finalize, retrieve, advance, serialize, and resume serialized positions.
- `zap_attribute_t` reports integer length, normalization conflicts, count, first integer, and name.
- `zap_stats_t` exposes internal pointer table, block, leaf, entry, salt, and histogram statistics for diagnostic users.

Risk-sensitive invariants:
- ZAP routines are thread-safe at the object level, but a DMU transaction must not be operated on concurrently.
- Integer-size conversion never sign-extends and may return overflow for too-small buffers.
- Serialized cursor cookies are persistent and reserve low bits for type differentiation.
- Normalization conflict handling matters for case-insensitive or Unicode-normalized datasets.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zap_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zap_impl.h

This private header defines microzap/fatzap physical layouts and internal ZAP locking, naming, hashing, and fatzap operations.

Core definitions:
- `ZAP_MAGIC`, block type constants, microzap entry/name/block limits, and `ZAP_NEED_CD`.
- `mzap_ent_phys_t` stores a microzap value, collision differentiator, padding, and fixed-size name; `mzap_phys_t` stores microzap header and variable chunk array.
- `mzap_ent_t` is the in-memory AVL entry for microzap chunks.
- `zap_phys_t` is the fatzap header with magic, pointer table metadata, free block, leaf/entry counts, salt, normalization flags, and ZAP flags.
- `zap_t` stores dbuf user data, objset/object/dbuf, rwlock, micro/fat mode, normalization flags, salt, and mode-specific state.
- Inline `zap_f_phys()` and `zap_m_phys()` return typed physical pointers from the dbuf.
- `zap_name_t` stores original and normalized key forms, hash, match type, normalization flags, and stack normalization buffer.

Internal API surface:
- Match names, lock/unlock directories, evict dbuf user data, allocate/free normalized names, query hash bits/max collision differentiator/flags.
- Fatzap byteswap, count, lookup/prefetch/add/update/length/remove/cursor/stat operations, leaf release, add-with-collision-differentiator, and micro-to-fat upgrade.

Risk-sensitive invariants:
- Comments explicitly require `zap_byteswap()` updates if `zap_phys_t` changes.
- Embedded pointer-table layout depends on fatzap block shift and begins halfway through the block.
- Locking mode parameters in `zap_lockdir()` control writer/reader and add-specific behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zap_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zap_leaf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zap_leaf.h

This private header defines fatzap leaf-block layout, chunk format, entry handles, and leaf manipulation APIs.

Core definitions:
- `ZAP_LEAF_MAGIC`, 24-byte chunks, chunk-count/hash-table macros, low-water threshold, and hash-table sizing macros define leaf geometry.
- `zap_leaf_phys_t` stores a two-chunk header with block type, prefix, magic, free count, entry count, prefix length, freelist, and flags, followed by hash table and chunks.
- `zap_leaf_chunk_t` is a union of entry chunks, array chunks, and free chunks.
- `zap_leaf_t` stores dbuf user data, leaf rwlock, block ID, block-size shift, and dbuf.
- Inline `zap_leaf_phys()` returns the physical leaf data.
- `zap_entry_handle_t` exposes entry integer count/hash/collision-differentiator/integer size and stores private chunk/leaf references.

Internal API surface:
- Lookup exact name or closest hash/collision differentiator.
- Read value, read name, update value, remove entry, create entry.
- Detect normalization conflicts.
- Initialize, byteswap, split, and collect leaf stats.

Risk-sensitive invariants:
- Comments require `zap_leaf_byteswap()` updates if `zap_leaf_phys_t` changes.
- Chunk chains store names and values across fixed 24-byte chunks; `CHAIN_END` semantics are implementation-critical.
- Split and low-water behavior influence fatzap pointer-table growth and lookup distribution.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zap_leaf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp.h

This header declares ZFS Channel Program infrastructure, which evaluates Lua programs against pool/dataset state with resource limits and optional sync-task execution.

Core definitions:
- `ZCP_RUN_INFO_KEY` names the Lua registry/run-info key.
- Global limits `zfs_lua_max_instrlimit` and `zfs_lua_max_memlimit`.
- `zcp_cleanup_handler_t` stores cleanup function, argument, and list node for fatal-error cleanup.
- `zcp_alloc_arg_t` tracks Lua allocator must-succeed mode, remaining allocation budget, and limit.
- `zcp_run_info_t` stores DSL pool, estimated sync-task space used, invoking credentials, DMU transaction, instruction counters/limit, timeout/cancel/sync flags, cleanup handler list, Lua state, allocator args, output nvlist, and result errno.
- `zcp_arg_t` and `zcp_lib_info_t` describe positional/keyword argument specifications for Lua-exposed library functions.

Public API surface:
- Argument error helper, `zcp_eval()`, list library loader, sync-task library loader.
- Run-info lookup, cleanup registration/deregistration, cleanup execution.
- Argument parsing, nvlist-to-Lua conversion, dataset hold error reporting, and dataset hold helper.

Risk-sensitive invariants:
- Channel programs run with explicit instruction and memory limits; timeout/cancel state is part of run info.
- Sync channel programs must use original caller credentials for permission checks, not the synctask thread's current credentials.
- Cleanup handlers protect resources when Lua raises fatal errors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_change_key.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_change_key.h

This header declares channel-program synctask helpers for changing dataset encryption keys.

Public API surface:
- `zcp_synctask_change_key_cleanup()` releases task-specific state.
- `zcp_synctask_change_key_check()` validates the change-key operation in synctask check context.
- `zcp_synctask_change_key_sync()` applies the operation in sync context.
- `zcp_synctask_change_key_create_params()` builds `dsl_crypto_params_t` from key bytes and key format.

Risk-sensitive invariants:
- Key material and crypto params require explicit cleanup discipline.
- Check and sync phases must agree on validated state and operate under DMU transaction rules.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_change_key.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_global.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_global.h

This header declares loading of global symbols into a ZFS channel-program Lua state.

Core API surface:
- `zcp_load_globals(lua_State *)` installs supported globals.

Risk-sensitive invariants:
- The function mutates the Lua environment used by channel programs.
- Exported globals are part of the scripting compatibility and safety surface.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_global.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_iter.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_iter.h

This header declares loading of channel-program list/iteration functions.

Core API surface:
- `zcp_load_list_funcs(lua_State *)` installs list/iterator-facing Lua functions.

Risk-sensitive invariants:
- Iterator functions expose filesystem/pool traversal to Lua and must follow channel-program limits enforced by `zcp.h`.
- The header uses the guard name `_SYS_ZCP_LIST_H`, matching the list-function naming rather than the file basename.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_iter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_prop.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_prop.h

This header declares channel-program property getter support and dataset-property validation.

Public API surface:
- `zcp_load_get_lib(lua_State *)` loads property-get functions into a Lua state.
- `prop_valid_for_ds(dsl_dataset_t *, zfs_prop_t)` checks whether a ZFS property is valid for a specific dataset.

Risk-sensitive invariants:
- Property validity is dataset-dependent and must be checked before exposing or using property operations in scripts.
- The header assumes the including context provides the relevant DSL dataset and ZFS property type definitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_prop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_set.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_set.h

This header declares channel-program property-setting synctask support.

Core definitions:
- `zcp_set_prop_arg_t` stores Lua state, dataset name, property name, and property value string for a set-property synctask.

Public API surface:
- `zcp_set_prop_check()` validates a property set in synctask check context.
- `zcp_set_prop_sync()` applies the property set in sync context.

Risk-sensitive invariants:
- Check and sync phases must share stable argument state and obey DMU transaction context.
- Dataset/property/value strings are passed by pointer and must remain valid for the synctask lifetime.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_set.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfeature.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfeature.h

This header declares SPA feature-flag management over the MOS feature ZAP objects.

Core definitions:
- `VALID_FEATURE_FID()` validates feature IDs against `SPA_FEATURES`.
- `VALID_FEATURE_OR_NONE()` also permits `SPA_FEATURE_NONE`.

Public API surface:
- Create feature ZAP objects, enable a feature, increment/decrement feature refcounts, query enabled/active/enabled-TXG/refcount state, and check feature compatibility for import/read-write use.
- Lower-level `feature_get_refcount()`, disk refcount retrieval, `feature_enable_sync()`, and `feature_sync()` are exported for `zhack` and `zdb`, not normal callers.

Risk-sensitive invariants:
- Feature enablement and refcounts are persistent compatibility gates for pool import and write support.
- Normal callers should use SPA feature APIs rather than low-level feature sync helpers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfeature.h -->