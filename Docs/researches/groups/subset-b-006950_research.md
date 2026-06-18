# Research: subset-b-006950

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_types.h -->
# `sources/distributed-fs/ceph/src/osd/osd_types.h`

## Purpose

`osd_types.h` is the central declaration header for Ceph OSD placement, pool, placement-group, object, log, missing-set, scrub, recovery, and on-disk metadata types. It is intentionally broad: most OSD subsystems include these declarations to exchange state between OSDs, encode persistent PG metadata, format diagnostics, and classify scheduler behavior. The header defines versioned encoders for wire/on-disk structures and many small helper APIs that preserve compatibility across old OSD feature sets.

## Important APIs, Types, And Constants

- OSD compatibility and priority constants: `CEPH_OSD_ONDISK_MAGIC`, `CEPH_OSD_FEATURE_INCOMPAT_*`, pool priority bounds, recovery/backfill/delete priority bands, and `op_queue_type_t`.
- Identity and placement: `osd_reqid_t`, `pg_shard_t`, `object_locator_t`, `request_redirect_t`, `pg_t`, `spg_t`, `coll_t`, `denc_coll_t`, and hash specializations.
- Pool and PG configuration: `pool_snap_info_t`, `pool_opts_t`, `pg_merge_meta_t`, and `pg_pool_t`.
- PG stats and history: `object_stat_sum_t`, `object_stat_collection_t`, scrub enums/status, `pg_stat_t`, `store_statfs_t`, `osd_stat_t`, `pool_stat_t`, `pg_hit_set_info_t`, `pg_hit_set_history_t`, `pg_history_t`, `pg_info_t`, `pg_fast_info_t`, and `PastIntervals`.
- Peering messages and leases: `pg_notify_t`, `pg_query_t`, `pg_lease_t`, and `pg_lease_ack_t`.
- Object modification and logging: `ObjectModDesc`, `ObjectCleanRegions`, `OSDOp`, `pg_log_op_return_item_t`, `pg_log_entry_t`, `pg_log_dup_t`, `pg_log_t`, `pg_missing_item`, `pg_missing_set<TrackChanges>`, `pg_missing_t`, and `pg_missing_tracker_t`.
- List/copy/create responses: `pg_nls_response_t`, `pg_ls_response_t`, `object_copy_cursor_t`, `object_copy_data_t`, `pg_create_t`, and `ObjectExtent`.
- Persistent OSD/object state: `OSDSuperblock`, `SnapSet`, `watch_info_t`, `notify_info_t`, `object_ref_delta_t`, `chunk_info_t`, `object_manifest_t`, `object_info_t`, and object attributes `OI_ATTR`/`SS_ATTR`.
- Recovery and scrub data: `ObjectRecoveryInfo`, `ObjectRecoveryProgress`, `PushReplyOp`, `PullOp`, `PushOp`, `ScrubMap`, `ScrubMapBuilder`, watch/snap list responses, `PromoteCounter`, `pool_pg_num_history_t`, and PG metadata key constants.
- Integration helpers: `prepare_info_keymap()`, `create_pg_collection()`, `init_pg_ondisk()`, `PGLSFilter`, `PGLSPlainFilter`, `missing_map_t`, `get_op_queue_type_name()`, and `get_op_queue_type_by_name()`.

## Control Flow And State Behavior

The header is mostly declarative, but several inline methods encode essential state transitions. PG and pool placement methods (`pg_t::is_split`, `is_merge_source`, `contains`, `pg_pool_t::raw_pg_to_pg`, `raw_pg_to_pps`, `is_pending_merge`) provide the shared placement math used by OSDMap, PG split/merge, peering, and object routing. `pg_pool_t` manages pool flags, tiering fields, quota fields, snap modes, EC behavior, CRUSH stretch-peering rules, and PG count transitions; `dec_pg_num()` records merge metadata while decreasing `pg_num`.

PG lifecycle state flows through `pg_info_t`, `pg_history_t`, `PastIntervals`, and peering messages. `pg_history_t::merge()` monotonically incorporates newer creation, clean, split, full, and scrub epochs, while `PastIntervals::check_new_interval()` and `PriorSet` model when an acting/up-set change creates prior participants that must be probed before a PG can become active. `PriorSet` explicitly treats down but potentially write-capable prior OSDs as blockers, which feeds PG down/incomplete decisions.

Object log and missing-set control flow is encoded in `pg_log_t` and `pg_missing_set`. `pg_log_t::rewind_from_head()` detaches divergent entries when a local log is rolled back to an authoritative head and adjusts rollback boundaries. `split_out_child()` partitions log entries for PG split using object hash bits. `pg_missing_set::add_next_event()` advances missing state from ordered log entries, handles divergent missing items, marks deletes, merges clean-region information, and skips unwritten nonprimary EC shards for partial writes. `revise_need()`, `revise_have()`, `got()`, `rm()`, and `split_into()` update both the object map and reverse version map; the tracked variant records changed objects for incremental persistence/debug validation.

Object state flows through `object_info_t`, `object_manifest_t`, `ObjectCleanRegions`, and `SnapSet`. `object_info_t` carries flags for lost, whiteout, dirty, omap, digests, cache pinning, manifest, and redirect reference state; `get_version_for_shard()` allows per-shard EC versions. `object_manifest_t` calculates reference deltas for chunk/redirect manifests during set, modify, and removal. `ObjectCleanRegions` represents clean byte intervals plus omap/new-object state and exposes dirty-region derivation for recovery.

## Persistence And Encoding

Almost every major type declares Ceph encoders through `WRITE_CLASS_ENCODER`, `WRITE_CLASS_ENCODER_FEATURES`, or `WRITE_CLASS_DENC`. Many structures use explicit `ENCODE_START`/`DECODE_START` versions, compatibility branches, feature-dependent encodings, and `generate_test_instances()` for encode/decode coverage. `eversion_t` and `object_stat_sum_t` rely on packed/raw little-endian layouts for efficiency and include comments/static assertions warning about padding and member changes. `pg_fast_info_t` is a fast path for hot PG-info fields and warns that adding unmatched fields requires an incompatible OSD feature bit.

Persistent PG metadata keys are declared near the end: `_infover`, `_info`, `_biginfo`, `_epoch`, and `_fastinfo`, with `pg_latest_struct_v`/`pg_compat_struct_v` set to 10. `prepare_info_keymap()` prepares these PG metadata updates, including fast-info and big-info handling. `OSDSuperblock` persists OSD identity, current epoch, map epoch intervals, mount/clean ranges, compatibility features, and trim lower bounds; its nested `GuardedMap` protects the interval set with a mutex and copies/moves under lock.

Compatibility risks are visible in legacy upgrade paths: `pg_missing_set::decode()` repairs old pool-less `hobject_t` entries, `pg_missing_item` supports multiple missing encodings including Octopus clean regions, and `pg_t` still decodes old `ceph_pg`/preferred fields. Any new persistent member must update encoders, decoders, dump output, equality where present, and `generate_test_instances()`.

## Dependencies And Integration Points

This header depends on Ceph common primitives (`hobject_t`, `ghobject_t`, `interval_set`, `Formatter`, `buffer::list`, mempools, `utime_t`, `CompatSet`, `entity_addr_t`, `entity_name_t`, `SnapContext`, `HitSet`, `ECTypes`, and `pg_features.h`). It forward-declares `OSDMap`, `PGBackend`, `ceph::os::Transaction`, and `CephContext` consumers.

Primary integration points are OSDMap/pool mapping, `PG` and `PeeringState` state machines, PG log persistence, objectstore transactions, scrubber code, EC and replicated backends, recovery messages, monitor stats, RADOS list/copy operations, watch/notify, and op scheduler selection. `op_queue_type_t` names are defined here and consumed by scheduler construction and OSD configuration parsing.

## Risks And Edge Cases

- Serialization compatibility is the largest risk. Field order, struct version, feature gating, padding, and raw-copy assumptions are part of the on-disk/wire contract.
- `object_stat_sum_t::padding_check()` appears to omit several later fields from the static size expression, so changes require careful validation against the implementation in `osd_types.cc`.
- `pg_missing_set` maintains two correlated indexes (`missing` and `rmissing`); bugs in erase/insert ordering can corrupt recovery ordering. The multimap is intentional because distinct objects may share a `need` version during log merge.
- Partial-write EC paths rely on `nonprimary_shards`, `written_shards`, `partial_writes_last_complete`, and `shard_versions`; mistakes can mark unwritten shards missing or complete incorrectly.
- `ObjectCleanRegions` limits interval count through a global atomic maximum; aggressive trimming may reduce recovery precision while preserving bounded memory.
- `PGRecoveryMsg::run()` in a companion file falls through switch cases intentionally or accidentally; latency counters may be incremented for all later message kinds unless fallthrough is intended and documented.
- `OSDSuperblock::GuardedMap` is thread-safe around its interval set, but callers receive copies; stale snapshots can be observed by design.
- Formatter/logging functions can expose large maps or attr contents through `fmt` in related headers; debug paths should avoid excessive output for huge scrub maps or manifests.

## Test Signals

Useful validation signals include Ceph encode/decode round-trip tests built from `generate_test_instances()`, PG split/merge tests, OSDMap placement tests, peering/PastIntervals/PriorSet tests, PG log rewind/merge tests, missing-set recovery tests, EC partial-write tests, object-info attr compatibility tests, scrub-map comparison tests, and OSD superblock persistence tests. At runtime, monitor/OSD dump output, scrub error counters, recovery queue metrics, PG state transitions, and assertions in missing/log paths are strong signals for regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_types_fmt.h -->
# `sources/distributed-fs/ceph/src/osd/osd_types_fmt.h`

## Purpose

`osd_types_fmt.h` supplies fmtlib formatters for selected OSD types declared in `osd_types.h`. It centralizes compact, allocation-conscious diagnostic formatting for request IDs, PG IDs, versions, object info/manifests, PG history/info, snap sets, scrub maps, and object stat summaries. It also bridges a few ostream-only types into fmt for fmt version 9 and newer.

## Important APIs And Types

- `fmt::formatter<osd_reqid_t>` renders `entity.inc:tid`.
- `fmt::formatter<pg_shard_t>` renders undefined shards as `?`, no-shard entries as the OSD id, and sharded entries as `osd(shard)`.
- `fmt::formatter<eversion_t>` renders `epoch'version`.
- `fmt::formatter<chunk_info_t>`, `object_manifest_t`, and `object_info_t` expose manifest, chunk, digest, allocation-hint, and per-shard-version details.
- `fmt::formatter<pg_t>` and `spg_t` render pool/seed and optional shard suffix.
- `fmt::formatter<pg_history_t>` and `pg_info_t` mirror the ostream summaries in `osd_types.h`.
- `fmt::formatter<SnapSet>` supports a `D` parse flag for verbose clone/overlap/snap detail.
- `fmt::formatter<ScrubMap::object>` recognizes `OI_ATTR` and `SS_ATTR`, hiding raw object-info bytes and decoding snapset bytes for readable output.
- `fmt::formatter<ScrubMap>` supports a `D` parse flag to include all objects.
- `fmt::formatter<object_stat_sum_t>` prints every stat field as a labeled tuple and backs an inline `operator<<`.
- For fmt >= 9, `pg_missing_set<TrackChanges>`, `pool_opts_t`, and `store_statfs_t` use `fmt::ostream_formatter`.

## Control Flow And State Behavior

The file has no persistent state beyond formatter booleans parsed from format specs. `SnapSet` and `ScrubMap` formatters implement small parse methods that consume a single `D` debug flag and switch between compact and verbose rendering. `ScrubMap::object` iterates attributes and treats object-info and snapset attributes specially, which prevents unreadable binary object-info dumps while still exposing decoded snapset state.

## Persistence Behavior

This header does not encode or persist data. Its behavior affects logs, asserts, debug messages, and operator output only. Because output text is often used in tests and operational debugging, format stability still matters, but it is not a wire/on-disk compatibility contract.

## Dependencies And Integration Points

It includes `common/hobject.h`, `include/types_fmt.h`, `osd/osd_types.h`, and fmt headers for chrono/ranges/std/ostream support. It is consumed by scheduler item formatting, PG/OSD logs, scrub diagnostics, and any code using `fmt::format()` with OSD types. The dependency on `OI_ATTR` and `SS_ATTR` couples scrub-map formatting to object-info/snapset attribute names from `osd_types.h`.

## Risks And Edge Cases

- Verbose scrub-map formatting can emit one line per object and each object's attributes; this is useful for debugging but risky in hot paths or large PGs.
- `ScrubMap::object` converts attribute buffers to strings; binary or very large attributes can be expensive or unreadable, although `OI_ATTR` is explicitly suppressed.
- `object_stat_sum_t` formatter must be kept in sync with fields in `object_stat_sum_t`; omitted fields reduce diagnostics and can break expectations in tests.
- `SnapSet` verbose formatting assumes maps contain clone metadata and prints `??` when related entries are missing, which is useful but may hide structural corruption unless tests assert it.
- The fmt version guards mean formatting support can differ across dependency versions.

## Test Signals

Compile coverage is the primary signal because these are template specializations. Unit tests or log-format tests that call `fmt::format()` on each specialized type, including `{:D}` for `SnapSet` and `ScrubMap`, are useful. Runtime scrub logs, PG-info logs, and scheduler-item logs provide integration signals that formatting compiles and does not recurse or dump raw binary unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_types_fmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/pg_features.h -->
# `sources/distributed-fs/ceph/src/osd/pg_features.h`

## Purpose

`pg_features.h` defines the feature-vector mechanism for capabilities supported by OSDs after a placement group becomes active. It mirrors the broad Ceph feature-bit style in a much smaller PG-local namespace and currently defines the `PCT` feature used by both Crimson and classic OSDs.

## Important APIs And Types

- `using pg_feature_vec_t = uint64_t` is the bit-vector type.
- `PG_FEATURE_INCARNATION_1` is the incarnation mask value used by feature definitions.
- `DEFINE_PG_FEATURE(bit, incarnation, name)` creates `PG_FEATURE_<name>` and `PG_FEATUREMASK_<name>`.
- `PG_HAVE_FEATURE(x, name)` tests whether a vector includes both the feature bit and the required incarnation mask.
- `PG_FEATURE_PCT`, `PG_FEATUREMASK_PCT`, `PG_FEATURE_NONE`, `PG_FEATURE_CRIMSON_ALL`, and `PG_FEATURE_CLASSIC_ALL` are the currently exported constants.

## Control Flow And State Behavior

There is no runtime control flow beyond macro expansion. `PG_HAVE_FEATURE()` performs a masked equality check, so a caller must pass a feature vector that includes the proper incarnation bit in addition to the feature bit. The all-feature constants currently map both Crimson and classic OSDs to `PG_FEATURE_PCT`.

## Persistence Behavior

The feature vector is embedded by users such as `pg_notify_t` in `osd_types.h`, so it participates in peering/wire state through those types, but this header itself has no encoder. Adding a feature changes negotiation semantics and must be coordinated with encode/decode versions and OSD feature compatibility wherever the vector is transmitted.

## Dependencies And Integration Points

The file intentionally has no includes. It is included by `osd_types.h` and is consumed by peering notification paths that need to know which active-PG behaviors are available. `PG_FEATURE_CRIMSON_ALL` and `PG_FEATURE_CLASSIC_ALL` connect classic and Crimson OSD implementations to the same feature mask.

## Risks And Edge Cases

- Feature-bit allocation is global within this 64-bit vector; duplicate bits would silently alias capabilities.
- `PG_HAVE_FEATURE()` requires the incarnation mask, so passing only `PG_FEATURE_PCT` without incarnation bits would fail the check.
- Adding a new incarnation or feature requires careful compatibility planning for mixed-version PGs.

## Test Signals

Compile-time tests can assert bit values and masks. Peering tests should cover mixed feature vectors and `pg_notify_t` propagation. Any new PG feature should include compatibility tests with old peers that lack the bit or required incarnation mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/pg_features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/recovery_types.h -->
# `sources/distributed-fs/ceph/src/osd/recovery_types.h`

## Purpose

`recovery_types.h` defines backfill interval containers used by OSD recovery. A backfill interval represents objects in `[begin, end)` observed at a specific scan version. The header separates primary and replica representations because primaries may track multiple shard/version pairs per object for optimized erasure-coded pools, while replicas track a single version per object.

## Important APIs And Types

- `template <typename T> class BackfillInterval` stores `eversion_t version`, `hobject_t begin`, `hobject_t end`, and `T objects`.
- Common helpers include `clear_objects()`, `reset(start)`, `empty()`, `extends_to_end()`, `trim_to(soid)`, `trim()`, abstract `clear()`, abstract `pop_front()`, and abstract `dump()`.
- `PrimaryBackfillInterval` uses `std::multimap<hobject_t, std::pair<shard_id_t, eversion_t>>`.
- `ReplicaBackfillInterval` uses `std::map<hobject_t, eversion_t>`.
- `operator<<` prints the interval bounds and object count/map.
- For fmt >= 9, both concrete interval types use `fmt::ostream_formatter`.

## Control Flow And State Behavior

`BackfillInterval::reset()` clears the interval and sets both bounds to the requested start. `trim()` advances `begin` to the first object key or to `end` when empty. `trim_to()` first normalizes `begin`, then repeatedly drops entries whose object key is `<= soid`. The concrete `pop_front()` behavior differs: primary intervals erase all entries for the first object key because multiple shards may be represented for the same object, while replica intervals erase only the first map entry.

Primary intervals model optimized EC partial-write behavior: an object may have a `NO_SHARD` baseline version plus shard-specific overrides. Replica intervals model one shard's object versions. Both `dump()` methods emit formatter objects containing begin/end and per-object entries.

## Persistence Behavior

This header does not define `WRITE_CLASS_ENCODER` encoders for the interval classes; they are transient recovery/backfill scan containers. The object and version element types are persistent elsewhere, but these classes are used as in-memory progress/state during recovery work.

## Dependencies And Integration Points

The file includes `<map>` and `osd_types.h`, relying on `hobject_t`, `eversion_t`, `shard_id_t`, `ceph_assert`, `Formatter`, and stream support. It is integrated with OSD backfill/recovery code that scans object ranges, trims already-processed entries, and ships or compares interval contents between primary and replicas.

## Risks And Edge Cases

- `pop_front()` asserts that the interval is non-empty; callers must guard empty intervals.
- Primary `pop_front()` erases all entries for the first object key. This is correct for per-object advancement but would be wrong for code expecting shard-by-shard advancement.
- `trim_to()` removes `<= soid`, not just `< soid`; callers must pass the last completed object, not the next object to retain.
- `extends_to_end()` relies on `end.is_max()`, so scan code must set `end` consistently for terminal intervals.
- Since the containers are maps, ordering follows `hobject_t` comparison and must match objectstore scan ordering.

## Test Signals

Backfill tests should cover empty/unpopulated intervals, terminal intervals, `trim_to()` boundary behavior, primary intervals with multiple entries for one object, replica single-entry trimming, and dump/stream formatting. EC optimized-pool tests are important because shard-specific primary interval entries are the unusual case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/recovery_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scheduler/OpScheduler.cc -->
# `sources/distributed-fs/ceph/src/osd/scheduler/OpScheduler.cc`

## Purpose

`OpScheduler.cc` implements the OSD op scheduler factory and stream output for the scheduler abstraction declared in `OpScheduler.h`. It selects either the legacy weighted priority queue adapter or the mClock scheduler based on configuration and objectstore type.

## Important APIs And Functions

- `make_scheduler(CephContext *cct, int whoami, uint32_t num_shards, int shard_id, bool is_rotational, std::string_view osd_objectstore, op_queue_type_t osd_scheduler, unsigned op_queue_cut_off)` returns an `OpSchedulerRef`.
- `operator<<(std::ostream&, const OpScheduler&)` delegates to `OpScheduler::print()`.

## Control Flow And State Behavior

The factory has three branches. If the configured scheduler is `WeightedPriorityQueue` or the objectstore is `filestore`, it constructs `ClassedOpQueueScheduler<WeightedPriorityQueue<OpSchedulerItem, client>>`. The filestore branch forces WPQ because mClock is not supported for filestore. The WPQ adapter receives the priority cutoff plus `osd_op_pq_max_tokens_per_priority` and `osd_op_pq_min_cost` from `cct->_conf`.

If the configured scheduler is `mClockScheduler`, the factory constructs `mClockScheduler` with OSD identity, shard count/id, rotational flag, and cutoff. Any other queue type aborts via `ceph_abort_msg("Invalid choice of wq")`.

## Persistence Behavior

The file has no persistence logic. It consumes runtime OSD configuration and returns an in-memory scheduler object. Scheduler type names are declared in `osd_types.h`/implemented in `osd_types.cc`, and OSD configuration parsing feeds the `op_queue_type_t` value.

## Dependencies And Integration Points

It includes `OpScheduler.h`, `common/WeightedPriorityQueue.h`, and `osd/scheduler/mClockScheduler.h`. The factory is called by `OSDShard` construction in OSD startup/reconfiguration paths. It integrates with config values on `CephContext`, objectstore type detection, and the `OpSchedulerItem` work item type.

## Risks And Edge Cases

- Filestore always forces WPQ even when mClock is configured, so tests and operational expectations must account for objectstore override.
- `op_queue_type_t::PrioritizedQueue` exists in `osd_types.h`, but this factory does not handle it; selecting it reaches `ceph_abort_msg`.
- The WPQ branch passes `cct` to `ClassedOpQueueScheduler` even though the adapter currently does not store it; constructor signature compatibility hides that unused parameter.
- Factory behavior depends on exact string comparison with `"filestore"`.

## Test Signals

Scheduler factory tests should assert WPQ selection for explicit WPQ, WPQ selection for filestore even with mClock requested, mClock selection for mClock on supported stores, and abort behavior for unsupported queue types. OSD startup logs and `operator<<` output provide integration signals for selected scheduler type and parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scheduler/OpScheduler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scheduler/OpScheduler.h -->
# `sources/distributed-fs/ceph/src/osd/scheduler/OpScheduler.h`

## Purpose

`OpScheduler.h` declares the scheduler abstraction used by OSD shards to order `OpSchedulerItem` work and provides an adapter from Ceph's classed `OpQueue` implementations to that abstraction. It is the interface boundary between OSD worker queues and concrete scheduling policies such as weighted priority queue and mClock.

## Important APIs And Types

- `using client = uint64_t` is the queue owner/client key type.
- `using WorkItem = std::variant<std::monostate, OpSchedulerItem, double>` is the dequeue result type, allowing no item, a real op item, or scheduler-specific delay/cost feedback.
- `class OpScheduler` declares `enqueue()`, `enqueue_front()`, `empty()`, `dequeue()`, `dump()`, `print()`, `get_type()`, optional `get_cost_per_io()`, and a virtual destructor.
- `OpSchedulerRef` is `std::unique_ptr<OpScheduler>`.
- `make_scheduler()` is the factory implemented in `OpScheduler.cc`.
- `template <typename T> class ClassedOpQueueScheduler final` adapts an `OpQueue<OpSchedulerItem, client>`-like type.

## Control Flow And State Behavior

`ClassedOpQueueScheduler` stores a priority cutoff and the concrete queue. `enqueue()` and `enqueue_front()` read priority, cost, and owner from `OpSchedulerItem`. Items with `priority >= cutoff` enter the strict queue (`enqueue_strict` or `enqueue_strict_front`) and bypass cost accounting; lower-priority items enter the classed queue with owner, priority, and cost. `dequeue()`, `empty()`, `dump()`, `print()`, and `get_type()` delegate to the underlying queue.

`OpScheduler::get_cost_per_io()` asserts by default, indicating it is only valid for schedulers that override it, such as mClock. Calling it on WPQ-style implementations is a programming error.

## Persistence Behavior

No persistent state is stored here. Scheduler queues are in-memory runtime state. The only durable coupling is indirect: `get_type()` returns `op_queue_type_t` from `osd_types.h`, and OSD configuration/state may report that type.

## Dependencies And Integration Points

The header includes `CephContext`, `OpQueue`, `MonClient`, `OpSchedulerItem`, and `ceph_assert`. Concrete integrations include `WeightedPriorityQueue` through the adapter and `mClockScheduler` through the factory. OSDShard uses this interface to enqueue client ops, peering events, scrub events, recovery, and deletes while worker threads consume `WorkItem` results.

## Risks And Edge Cases

- The cutoff comparison is `>=`, so a priority exactly equal to `op_queue_cut_off` becomes strict/immediate.
- Strict queueing ignores cost; misconfigured priorities can starve lower classes.
- `WorkItem` includes `double`, so consumers must handle scheduler delay/control results and not assume every dequeue returns an op.
- The adapter assumes `T` implements a specific `OpQueue` surface: strict/front enqueue APIs, classed enqueue APIs, `dequeue`, `dump`, `print`, and `get_type`.
- `get_cost_per_io()` default asserts; generic code must branch by scheduler type or virtual capability before calling it.

## Test Signals

Focused tests should verify cutoff behavior, `enqueue_front()` ordering, strict vs non-strict queue selection, `dump()`/`print()` delegation, `get_type()` propagation, and safe handling of all `WorkItem` alternatives. Integration signals include OSD op latency under mixed priorities and scheduler dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scheduler/OpScheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scheduler/OpSchedulerItem.cc -->
# `sources/distributed-fs/ceph/src/osd/scheduler/OpSchedulerItem.cc`

## Purpose

`OpSchedulerItem.cc` implements the `run()` methods for concrete scheduler queueable items declared in `OpSchedulerItem.h`. Each method is a small dispatch adapter from a queued work item to the correct `OSD` or `PG` method, with PG lock release where ownership conventions require it.

## Important APIs And Functions

- Client and peering dispatch: `PGOpItem::run()` and `PGPeeringItem::run()`.
- Snap trim and scrub dispatch: `PGSnapTrim::run()`, `PGScrub::run()`, scrub-reschedule/update/unblock/digest/replmap item runs, and replica scrub item runs.
- Replica scrub message dispatch: `PGScrubReplicaPushes`, `PGScrubScrubFinished`, `PGScrubGetNextChunk`, `PGScrubChunkIsBusy`, and `PGScrubChunkIsFree`.
- Recovery dispatch: `PGRecovery::run()`, `PGRecoveryContext::run()`, `PGDelete::run()`, and `PGRecoveryMsg::run()`.

## Control Flow And State Behavior

Most methods call a single target method and then `pg->unlock()`. `PGOpItem` passes the held `PGRef`, `OpRequestRef`, and thread-pool handle to `OSD::dequeue_op()`. `PGPeeringItem` sends a peering event to `OSD::dequeue_peering_evt()` and does not unlock in this method, implying the callee owns or manages that path's lock convention. Snap trim and scrub items call the corresponding `PG` methods with `epoch_queued` and sometimes `activation_index`, then unlock.

Recovery items also update latency counters. `PGRecovery::run()` increments `l_osd_recovery_queue_lat` based on `time_queued`, calls `OSD::do_recovery()` with reserved pushes and priority, then unlocks. `PGRecoveryContext::run()` increments `l_osd_recovery_context_queue_lat`, completes a captured context, then unlocks. `PGDelete::run()` calls `OSD::dequeue_delete()` and does not unlock locally, matching that callee's ownership convention.

`PGRecoveryMsg::run()` computes queue latency, switches on the message type, increments recovery-message latency counters, then dispatches the request through `OSD::dequeue_op()` and unlocks. The switch cases have no `break` statements, so a push message increments all subsequent counters, a push-reply increments all later counters, and so on. That fallthrough is a key behavior to verify against intended metrics semantics.

## Persistence Behavior

This file has no direct persistence logic. It mutates OSD/PG runtime state by invoking operations that may later write PG logs, object data, recovery metadata, or scrub state. The queued epochs (`epoch_queued`) guard against stale work in the target PG methods rather than being persisted here.

## Dependencies And Integration Points

It includes `OpSchedulerItem.h`, `OSD.h`, and `osd_tracer.h`. It is tightly integrated with `OSD`, `OSDShard`, `PG`, scrubber methods, peering events, recovery reservations, `ThreadPool::TPHandle`, OSD perf counters, and message type constants such as `MSG_OSD_PG_PUSH`, `MSG_OSD_PG_PULL`, and `MSG_OSD_PG_SCAN`.

## Risks And Edge Cases

- Lock ownership is subtle. Most run methods unlock the PG, but peering and delete paths do not; changing target methods requires rechecking lock contracts.
- The missing `break` statements in `PGRecoveryMsg::run()` may be intentional cumulative accounting or a counter bug. Tests should lock down expected counter increments.
- `PGRecoveryContext::run()` calls `c.release()->complete(handle)`; ownership must be valid and non-null when queued.
- Many scrub methods ignore `osd` or `sdata`, which is fine for method signature uniformity but can hide stale queue context issues.
- Work may be queued for an old epoch; each PG method must validate `epoch_queued`.

## Test Signals

Scheduler item tests can use fake OSD/PG objects to verify each run method calls the correct target and unlocks exactly when expected. Integration signals include OSD perf counters for recovery queue latency, scrub state-machine progress, absence of PG lock leaks/deadlocks, and recovery-message dispatch behavior. Counter tests should specifically cover the switch fallthrough behavior in `PGRecoveryMsg::run()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scheduler/OpSchedulerItem.cc -->
