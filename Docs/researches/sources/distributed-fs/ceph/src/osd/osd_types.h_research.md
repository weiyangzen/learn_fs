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
