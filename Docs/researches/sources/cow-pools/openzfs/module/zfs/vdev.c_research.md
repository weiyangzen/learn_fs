# File Research: sources/cow-pools/openzfs/module/zfs/vdev.c

This file implements core OpenZFS virtual-device (`vdev_t`) management for pools: vdev tree construction and teardown, device open/probe/validate/load, metaslab group setup, DTL tracking and synchronization, state transitions, online/offline/fault/clear operations, statistics, user-visible vdev properties, and module tunables. It is part of subset A through `sources/cow-pools/openzfs`.

Primary exported administrative APIs:
- `vdev_fault()`: marks a leaf vdev faulted, optionally as a persistent external fault, but falls back to degraded if removing it would lose required data.
- `vdev_degrade()`: marks a leaf vdev degraded without preventing normal I/O.
- `vdev_online()`: clears offline/tmpoffline state, reopens the top-level vdev, handles expansion flags, restarts initialization/TRIM work, and may schedule spare detach.
- `vdev_offline()`: safely offlines a leaf vdev, refusing if DTL analysis says it contains required data; log devices are reset before offlining.
- `vdev_clear()`: recursively resets error counters and persistent fault/degraded/read/write failure state, reopens affected vdevs, and clears cached ereports.

Other major public/internal entry points:
- Allocation and tree management: `vdev_alloc_common()`, `vdev_alloc()`, `vdev_free()`, `vdev_add_child()`, `vdev_remove_child()`, `vdev_compact_children()`, `vdev_add_parent()`, `vdev_remove_parent()`, `vdev_split()`.
- Opening and validation: `vdev_open()`, `vdev_close()`, `vdev_reopen()`, `vdev_probe()`, `vdev_validate()`, `vdev_validate_aux()`, `vdev_create()`, `vdev_open_children()`, `vdev_open_children_subset()`.
- Metaslab and sync handling: `vdev_metaslab_group_create()`, `vdev_metaslab_init()`, `vdev_metaslab_fini()`, `vdev_metaslab_set_size()`, `vdev_expand()`, `vdev_sync()`, `vdev_sync_dispatch()`, `vdev_sync_done()`, `vdev_destroy_spacemaps()`.
- DTL/resilver handling: `vdev_dtl_dirty()`, `vdev_dtl_contains()`, `vdev_dtl_empty()`, `vdev_dtl_reassess()`, `vdev_dtl_load()`, `vdev_dtl_required()`, `vdev_resilver_needed()`, `vdev_defer_resilver()`, `vdev_clear_resilver_deferred()`.
- State and accessibility helpers: `vdev_set_state()`, `vdev_propagate_state()`, `vdev_is_dead()`, `vdev_readable()`, `vdev_writeable()`, `vdev_allocatable()`, `vdev_accessible()`, `vdev_is_concrete()`, `vdev_log_state_valid()`.
- Space and I/O accounting: `vdev_stat_update()`, `vdev_space_update()`, `vdev_get_stats_ex()`, `vdev_get_stats()`, `vdev_clear_stats()`, `vdev_scan_stat_init()`, `vdev_deflated_space()`.
- Property plumbing: `vdev_prop_set()`, `vdev_prop_get()`, `vdev_construct_zaps()`, `vdev_create_link_zap()`, `vdev_destroy_unlink_zap()`.
- Address translation: `vdev_default_xlate()`, `vdev_xlate()`, `vdev_xlate_walk()`.

Key dependencies:
- `sys/vdev_impl.h`, `sys/spa.h`, and `sys/spa_impl.h` define the vdev tree, SPA locks, load states, allocation classes, and pool-wide state.
- `sys/metaslab.h`, `sys/metaslab_impl.h`, `sys/space_map.h`, and `sys/space_reftree.h` provide metaslab groups, persistent space maps, and reference-tree logic for DTL recomputation.
- `sys/zio.h`, `sys/abd.h`, and `sys/arc.h` provide physical I/O, probe I/O, error propagation, and accounting integration.
- `sys/dsl_scan.h`, `sys/vdev_rebuild.h`, `sys/vdev_initialize.h`, and `sys/vdev_trim.h` integrate vdev state with scrub, resilver, rebuild, initialize, and TRIM workflows.
- `sys/vdev_raidz.h` and `sys/vdev_draid.h` provide layout-specific parity, resilver, DTL, failure-domain, and sit-out behavior.
- `sys/zap.h`, `sys/dmu.h`, and `sys/dmu_tx.h` persist vdev ZAP properties, DTL objects, metaslab arrays, checkpoint maps, obsolete maps, and sync-time updates.
- `sys/fm/fs/zfs.h` and `sys/zfs_ratelimit.h` support ereports, state-change notifications, and rate-limiting of slow I/O, checksum, deadman, and Direct I/O verification events.

Vdev type model:
- `vdev_ops_table` maps config strings to concrete operation vectors for root, RAIDZ, dRAID, dRAID spare, mirror, replacing, spare, disk, file, missing, hole, and indirect vdevs.
- Most generic behavior is dispatched through `vdev_ops_t`: open/close, init/fini, space-size conversion, min allocation, parity, disk count, logical-to-physical translation, state aggregation, and optional platform events.
- `vdev_is_concrete()` excludes root, hole, missing, and indirect vdevs from normal allocation/state-sync behavior.

Allocation and construction behavior:
- `vdev_alloc()` parses an nvlist config, checks type/features, initializes type-specific private state, restores paths/devid/physical/enclosure/FRU metadata, ashift, creation txg, ZAP object ids, DTL/rebuild/resilver state, persistent offline/fault/degraded/removed flags, allocation bias, and top-level metaslab metadata.
- `vdev_alloc_common()` creates the base `vdev_t`, generates GUIDs when needed, initializes locks, condition variables, dirty lists, DTL range trees, obsolete segment tracking, rate-limit structures, vdev queues, and default error/slow-I/O threshold properties.
- `vdev_add_child()` and `vdev_remove_child()` maintain parent/child links, top-vdev pointers, child arrays, GUID sums, nonrotational aggregation, and the SPA leaf list.
- `vdev_add_parent()` and `vdev_remove_parent()` are used by mirror/replacing/spare tree rewrites. Top-level state transfer preserves metaslab arrays, metaslab groups, checkpoint maps, removal/rebuild/indirect mapping state, dirty-list membership, deflate ratio, log status, and scan queues.

Open/probe/validate/load behavior:
- `vdev_open()` enforces fault/offline state, calls the type-specific open method, validates physical and maximum sizes, handles removed devices, applies fault injection, updates open state, calculates allocatable size, psize/asize/max_asize, logical/physical ashift, expansion eligibility, deflate/min allocation state, and triggers leaf probes and resilver assessment.
- `vdev_probe()` issues read probes to label pad regions and write probes when the pool is writeable. It coalesces concurrent probe requests through `vdev_probe_zio`, updates `vdev_cant_read`/`vdev_cant_write`, posts probe-failure ereports, and may schedule asynchronous vdev faulting.
- `vdev_validate()` recursively validates child labels, reads the best label config for an appropriate txg, checks split-pool state, pool GUID, vdev GUID/top GUID, trusted-config rules, and pool state. Most bad-label cases update vdev state but return success so pool loading can continue with degraded topology unless the pool state itself makes import invalid.
- `vdev_load()` recursively loads children, loads RAIDZ-specific data, restores allocation bias/failfast/autosit/rebuild and property state from ZAPs, creates metaslab groups, initializes metaslabs, opens checkpoint and obsolete space maps, and loads leaf DTLs.
- `vdev_validate_aux()` handles hot spare and L2ARC vdev validation by checking their labels for supported pool version, matching GUID, and sane pool state.

Metaslab and allocation-class behavior:
- `vdev_metaslab_group_create()` assigns top-level vdevs to the normal, log, special, or dedup metaslab class based on log status and allocation bias, and creates embedded-log metaslab groups for non-log normal/special vdevs.
- `vdev_metaslab_init()` allocates/expands the metaslab pointer array, initializes new metaslabs from the MOS metaslab array when loading, recalculates existing weights, selects one emptiest metaslab for embedded slog use when enough metaslabs exist, and activates groups unless the vdev is non-allocating.
- `vdev_metaslab_set_size()` chooses metaslab size/count with defaults targeting roughly 200 metaslabs, minimum 16 metaslabs, 512 MiB lower size, 16 GiB upper size, and a practical 131,072 metaslab count cap.
- `vdev_update_nonallocating_space()` accounts normal-class non-allocating vdev dspace in `spa_nonallocating_dspace`.
- `vdev_expand()` initializes additional metaslabs after device growth when expansion is possible and not handled by active RAIDZ expansion.

DTL and resilver model:
- The file documents four dirty time log maps: `DTL_MISSING`, `DTL_PARTIAL`, `DTL_SCRUB`, and `DTL_OUTAGE`.
- Leaf vdevs persist only `DTL_MISSING` to disk. Interior vdev DTLs are recomputed from children with reference trees.
- `vdev_dtl_dirty()` adds txg ranges to a DTL range tree under the vdev DTL lock.
- `vdev_dtl_reassess_impl()` is the central recomputation path. For leaves, it may excise successfully scrubbed/resilvered/rebuilt DTL ranges, folds scrub DTL state, recomputes outage ranges based on readability, resets rebuild/resilver txg markers, and dirties top-level DTL state for sync. For interior vdevs, it unions child DTLs with thresholds derived from mirror, RAIDZ, dRAID parity, and dRAID failure-domain rules.
- `vdev_dtl_required()` temporarily marks a vdev unreadable and recomputes outage DTLs to decide whether offlining/detaching/removing/faulting would lose data.
- `vdev_resilver_needed()` walks leaves to find the minimum and maximum missing txg range requiring repair.
- `vdev_stat_update()` adds DTL entries on failed writes in the correct transactional context, including scrub repair, ZIL claim, and dRAID rebuild cases.

Sync-time persistence:
- `vdev_dirty()` records dirty metaslabs or leaf DTLs in per-top-level txg lists and adds the vdev to `spa_vdev_txg_list`.
- `vdev_sync()` syncs obsolete segments, creates the metaslab array object when needed, syncs dirty metaslabs, syncs leaf DTL space maps, removes metadata for empty removed log vdevs, and queues the vdev for clean-phase processing.
- `vdev_dtl_sync()` creates/truncates/writes the DTL space map for a leaf, frees it when the vdev is detached or being removed, and dirties the top-level config when the DTL object changes.
- `vdev_sync_dispatch()` and `vdev_sync_done()` run metaslab clean-phase work on the SPA sync taskq and reassess metaslab groups afterward.
- `vdev_destroy_spacemaps()` frees all metaslab space map objects and the metaslab array object for a vdev, including unflushed metaslab metadata.

State transitions and safety:
- `vdev_set_state()` centralizes state changes, auxiliary status, close-on-dead behavior, removed-device preservation, not-present import behavior, ereport posting, leaf state-change notification, and parent propagation.
- `vdev_propagate_state()` recomputes parent health from children, treating unreadable/unwriteable children as faulted except that top-level log failure degrades the root; corrupt-data aux state is propagated specially to the root.
- `vdev_fault()` and `vdev_offline()` both rely on `vdev_dtl_required()` to avoid actions that would make required data unavailable.
- `vdev_online()` reopens the top-level vdev, handles explicit or automatic expansion, restarts initialize/TRIM work when applicable, and emits online events.
- `vdev_remove_wanted()` probes a leaf to confirm it is gone before scheduling asynchronous user-requested removal.
- `vdev_clear()` resets persistent health state and may request resilver-done processing so completed spares can be detached.

Statistics and accounting:
- `vdev_stat_update()` records successful leaf I/O operations, bytes, queue histograms, disk latency histograms, aggregate/individual request histograms, scan processed bytes, rebuild processed bytes, and self-healed bytes.
- It suppresses gang leaders, bypass I/O, speculative failures, retryable failfast-style errors, and root-level no-propagate intent-log errors.
- `vdev_get_stats_ex()` copies current stats, computes elapsed timestamp, reports real/physical/expandable size, ashift values, initialize/TRIM progress, resilver-deferred state, top-level fragmentation, and noalloc state.
- `vdev_get_stats_ex_impl()` aggregates child stats upward, excluding dRAID virtual spare I/O to avoid double counting.
- `vdev_space_update()` updates top-level vdev and root pool allocated/space/dspace counters using the top-level deflate ratio.

Property behavior:
- Vdev properties are stored in root/top/leaf ZAPs when available; `vdev_prop_get_objid()` selects the applicable object.
- `vdev_prop_set()` validates requested property changes, handles special live operations for `path`, `allocating`, `failfast`, `sit_out`, `autosit`, checksum/slow-I/O thresholds, scheduler, and allocation bias, then persists values through a sync task.
- `vdev_props_set_sync()` writes property updates to ZAPs and logs history. User properties are string-only and empty string removes the property.
- `vdev_prop_get()` returns read-only computed properties such as name, capacity, state, GUID, sizes, ashift, free/allocated space, parity, dRAID failure-domain/group, paths, children, errors, operations/bytes, removing/RAIDZ-expanding/sit-out/TRIM support, plus local/default-source numeric and text properties.
- Allocation-bias changes are restricted to top-level non-log vdevs with the allocation-classes feature, and converting the last normal vdev is disallowed.

Range translation:
- `vdev_xlate()` walks from a leaf toward the top vdev and unwinds through parent-specific `vdev_op_xlate()` functions to convert logical ranges to physical ranges.
- `vdev_xlate_walk()` repeatedly translates remaining ranges and skips empty physical ranges, which matters for RAIDZ/dRAID layouts where a logical range may not map to the selected leaf.

Filesystem relevance:
- This is one of the central files for ZFS pool integrity. It decides when a physical device can participate in reads, writes, allocation, resilver, removal, import, and export.
- It connects on-disk pool metadata, vdev labels, metaslab allocation state, DTL repair history, and administrative commands into one coherent vdev lifecycle.
- Safety checks here prevent offlining or faulting a device when it contains the only readable copy of data, reject mismatched labels, track txg ranges needing repair, and preserve compatibility-sensitive ashift/metaslab behavior.
- The code also exposes user-facing observability and control surfaces through vdev stats, properties, ZED notifications, FMA ereports, and tunables.

Notable implementation details:
- Embedded slog allocation reserves the emptiest metaslab from normal/special vdevs when enough metaslabs exist, providing a fallback log allocation class after dedicated slog devices.
- Zvol-backed vdev trees are opened/validated/loaded serially in several paths to avoid namespace-lock deadlocks.
- Import/open validation is deliberately tolerant in many failure cases: bad devices are marked in state, while loading may continue with degraded topology.
- Top-level vdev replacement/detach code preserves GUIDs and, when autoexpand is disabled, asize, to avoid import confusion and unexpected mirror expansion.
- DTL recomputation for RAIDZ/dRAID uses parity thresholds; dRAID failure-domain logic can skip repeated failures within a domain until thresholds are exceeded.
- Direct I/O write verification is enabled by default on non-FreeBSD platforms through `zfs_vdev_direct_write_verify`.
- Module parameters expose metaslab sizing, event rate limits, scan error ignoring, validation skipping, cache-flush disabling, embedded slog threshold, min/max auto ashift, and RAIDZ implementation selection.
