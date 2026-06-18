# sources/distributed-fs/ceph/src/osd/osd_types.cc

## Purpose

`osd_types.cc` implements most of Ceph OSD's shared value types: placement-group identifiers, pool metadata, OSD and PG statistics, persisted PG info/history, past interval compression, log entries, object metadata, recovery payloads, scrub maps, request/op formatting, and helpers for initializing PG metadata on disk. It backs declarations in `osd_types.h` and is used by OSDMap placement, peering, PGLog, recovery backends, scrub code, admin formatting, and objectstore transactions.

The file is not one large algorithm. Its main role is to define stable serialization, formatter output, printable forms, compatibility upgrades, and small domain operations for the data that moves between monitors, OSDs, clients, and local objectstore metadata. Because many of these objects are persisted or sent over the wire, `encode`/`decode` version handling is the dominant correctness concern.

## Important APIs, Types, And Functions

- Flag/string helpers: `ceph_osd_flag_name`, `ceph_osd_flag_string`, `ceph_osd_op_flag_name`, `ceph_osd_op_flag_string`, `ceph_osd_alloc_hint_flag_string`, `pg_state_string`, and `pg_string_state` convert bitmasks to stable admin-visible text and parse selected PG state names back to state bits.
- Identity and placement types: `pg_shard_t`, `osd_reqid_t`, `object_locator_t`, `request_redirect_t`, `pg_t`, `spg_t`, and `coll_t` encode shard identities, request ids, object locators, redirected objects, PG names, shard PG names, and objectstore collection names.
- OSD and pool reporting types: `objectstore_perf_stat_t`, `osd_stat_t`, `store_statfs_t`, `object_stat_sum_t`, `object_stat_collection_t`, `pool_stat_t`, and `pg_stat_t` serialize and dump usage, latency, heartbeat, scrub, snaptrim, repair, placement, and object accounting.
- Pool configuration: `pool_snap_info_t`, `pool_opts_t`, and `pg_pool_t` implement pool snapshots, typed pool options, pool placement/hash/mask helpers, tier/cache/hit-set fields, PG autoscale fields, stretch-pool peering constraints, erasure-code shard metadata, and long-lived pool encoding compatibility.
- Durable PG metadata: `pg_history_t`, `pg_info_t`, `pg_notify_t`, `pg_query_t`, `pg_lease_t`, `pg_lease_ack_t`, and `PastIntervals` carry PG epoch history, authoritative per-PG info, peering notifications/queries, read leases, and compact witness sets for prior intervals.
- PG log and rollback metadata: `ObjectModDesc`, `ObjectCleanRegions`, `pg_log_entry_t`, `pg_log_dup_t`, and `pg_log_t` describe object mutations, rollback cleanliness, log entries, duplicate request tracking, log filtering, partial log copying, and checksum-protected log-entry storage.
- Object copy, snapshots, watchers, and manifests: `object_copy_cursor_t`, `object_copy_data_t`, `pg_create_t`, `pg_hit_set_info_t`, `pg_hit_set_history_t`, `OSDSuperblock`, `SnapSet`, `watch_info_t`, `chunk_info_t`, `object_manifest_t`, and `object_info_t` implement persisted object-side metadata and copy/recovery transfer state.
- Recovery and scrub payloads: `ObjectRecoveryProgress`, `ObjectRecoveryInfo`, `PushReplyOp`, `PullOp`, `PushOp`, `ScrubMap`, `ScrubMap::object`, and `ScrubMapBuilder` define recovery messages, queue cost estimates, scrub object summaries, and incremental scrub-map merging.
- Storage and op helpers: `OSDOp` stream formatting, `OSDOp::split_osd_op_vector_out_data`, `OSDOp::merge_osd_op_vector_out_data`, `prepare_info_keymap`, `create_pg_collection`, `init_pg_ondisk`, `PGLSPlainFilter`, `get_op_queue_type_name`, and `get_op_queue_type_by_name`.

## Control Flow

### Placement And Naming

`object_locator_t` preserves the client/object placement hints used by `OSDMap::object_locator_to_pg`. It enforces the invariant that an explicit hash and key are not both set. `pg_pool_t::hash_key`, `raw_hash_to_pg`, `raw_pg_to_pg`, `raw_pg_to_pps`, and `get_random_pg_position` turn names, namespaces, and raw hashes into stable PG ids and CRUSH placement seeds. `pg_t` supports string parsing/printing, ancestor calculation, split/merge detection, parent lookup, and hobject range boundaries for a PG.

`coll_t` maps a PG or meta collection to objectstore collection names. Current PG collections are encoded structurally when possible, while temporary PG collection names use string encoding because old structural versions cannot express them. `create_pg_collection` and `init_pg_ondisk` use `coll_t` with `ceph::os::Transaction` to create/touch PG collections, set expected-object hints, mark Crimson PG metadata with a log allocation hint, and write the current PG info structure version under `infover_key`.

### Pool State

`pg_pool_t` is the largest type in the file. It dumps all user- and monitor-visible pool settings, converts acting vectors to shard sets, recalculates PG masks, checks pending merges, manages pool-managed and self-managed snaps, hashes object keys, and applies PG-number changes. Encoding branches heavily on feature bits and significant release gates: very old `ceph_pg_pool`-compatible layouts, pre-OSDENC layouts, pre-OSD_POOLRESEND layouts, and modern versions up to struct version 33. Decode fills defaults for absent fields, repairs legacy snap-mode flags, reconstructs old merge metadata, recalculates masks, and rebuilds hit-set grade tables.

Stretch-pool support is enforced by `stretch_set_can_peer`, which inspects CRUSH ancestors for the requested acting set and requires enough distinct barrier buckets plus an optional mandatory member. This feeds peering decisions through `PastIntervals::check_new_interval` and PeeringState code.

### Peering History And Prior Intervals

`pg_history_t` tracks epoch boundaries and scrub history. Decode supplies best-effort interval defaults for old encodings and preserves a `prior_readable_until_ub` bound for lease/readability behavior.

`pg_info_t` combines shard PG id, log bounds, stats, history, purged snaps, hit-set history, backfill marker, and partial-write completion maps. `pg_notify_t` and `pg_query_t` wrap this information for peer exchange.

`PastIntervals` stores interval history through an `interval_rep` implementation named `pi_compact_rep`. The compact representation retains all participants and only the minimal set of maybe-read-write acting sets needed to answer two peering questions: which OSDs may hold unfound objects, and which subsets must be contacted to guarantee a witness of completed writes. New intervals are detected from acting/up changes, primary changes, pool size/min_size changes, PG split/merge state, sortbitwise/recovery-deletes flags, stretch CRUSH parameters, and EC optimization toggles.

`PastIntervals::check_new_interval` constructs a `pg_interval_t` when the map changes. It checks whether the old acting set could have gone active using min_size, stretch constraints, the caller-supplied recoverability predicate, and primary `up_from`/`up_thru` coverage. It then records whether the interval maybe went read-write. `PriorSet::affected_by_map` tells peering when a new OSDMap changes prior-set liveness, lost-at state, or destroyed OSD status.

### Stats And Admin Output

The stat types follow a common pattern: `dump` emits formatter fields for admin/monitor surfaces, `encode` writes versioned storage/wire state, `decode` accepts older versions and fills compatibility defaults, and `generate_test_instances` supplies encode/decode corpus values. `osd_stat_t` reports store stats, snap trim state, heartbeat peers, op queue histograms, performance latencies, OSD alerts, repaired shards, per-pool OSD counts, and front/back heartbeat ping times. `pg_stat_t` reports PG state, epoch timestamps, log sizes, scrub scheduling text, placement sets, blocked OSDs, purged snaps, and invalid-stat flags.

`object_stat_sum_t` is optimized for little-endian current-version decode by copying the struct payload directly; older versions and non-little-endian builds decode field by field. Its `add`, `sub`, and equality operators aggregate all object, byte, scrub, recovery, cache-tier, omap, manifest, and repair counters.

### Logs, Rollback, And Missing Data

`ObjectModDesc` is a buffer-backed sequence of rollback-relevant mutation descriptors. `visit` decodes each embedded operation and dispatches to a visitor for append, setattr, delete, create, snap update, try-delete, rollback extents, and EC omap changes. Decode rebuilds and reassigns the internal buffer to the OSD PG log mempool to avoid pinning larger buffers.

`ObjectCleanRegions` tracks intervals that remain clean, whether omap is clean, and whether the object already existed. It can merge cleanliness from multiple sources by intersecting clean regions, mark data/omap/object dirtiness, derive dirty regions, and trim retained clean intervals to a bounded count.

`pg_log_entry_t` encodes object log operations, request ids, versions, snaps, rollback descriptors, duplicate request returns, clean regions, operation returns, return codes, and written shards. `encode_with_checksum` wraps the normal encoding with CRC32C. Decode handles old `sobject_t`/pool/hash formats, old `LOST_REVERT` prior-version semantics, absent rollback descriptions, absent clean-region data, and older return-code placement. `pg_log_dup_t` tracks duplicate request results under `dup_` keys.

`pg_log_t::filter_log` rejects log entries that do not belong to an imported PG under the current OSDMap, except hit-set namespace objects. `copy_after` and `copy_up_to` build partial logs from another log while preserving head/tail and copying duplicate request records through `_handle_dups`.

### Object Metadata And Manifests

`SnapSet` persists clone ids, clone overlaps, clone sizes, and per-clone snap vectors. `from_snap_set` reconstructs OSD snap metadata from a librados snap set, with legacy mode omitting `clone_snaps`. `watch_info_t` persists watch cookies, timeouts, and watcher addresses.

`object_manifest_t` supports redirect and chunked objects. Its reference-delta helpers compute which chunk object references to increment or decrement when a manifest is set, modified, or removed. The algorithms compare adjacent clone manifests so shared chunk references are not over-counted and so removing a middle clone adjusts references only when the neighboring clones' chunks require it.

`object_info_t` is the durable per-object metadata record: `hobject_t`, version/prior version, last request, size, mtime/local mtime, truncate state, flags, user version, watcher maps, data/omap digests, allocation hints, optional manifest, and shard versions. Decode upgrades old watcher keys, legacy object locators, tmap defaults, digest defaults, and manifest/shard-version additions.

### Recovery, Copy, And Scrub

`object_copy_cursor_t` and `object_copy_data_t` encode object copy progress and payloads used by copy-from/recovery flows. Decode converts old omap map encodings into the newer encoded `omap_data` buffer and adds request ids, truncate fields, and request return codes when present.

`ObjectRecoveryProgress` records data and omap recovery progress. `ObjectRecoveryInfo` carries the target object, version, size, object info, snapset, copy subset, clone subset, existence flag, and omap-key count. `PushReplyOp`, `PullOp`, and `PushOp` are recovery message payloads; their `cost` methods integrate with the OSD op queue. `PushReplyOp` costs 1 under mClock because it unblocks continued recovery, `PullOp` estimates remaining data capped at `osd_recovery_max_chunk`, and `PushOp` costs included data plus omap payload lengths and per-object cost.

`ScrubMap::merge_incr` applies an incremental scrub map by requiring `valid_through == incr_since`, replacing positive object records, and removing objects with negative records. `ScrubMap` decode upgrades old hobject pool ids. `ScrubMap::object` records size, negative entries, attrs, data/omap digests, stat/read/EC errors, large-omap markers, and object omap byte/key counts. Older scrub encodings collapse EC mismatch/read errors into a compatibility read-error field, which decode expands conservatively.

## State And Persistence Behavior

Nearly every type in this file is either persisted locally, sent over cluster/client protocols, or shown in admin output. State is stored in `ceph::buffer::list` with Ceph's `ENCODE_START`, `DECODE_START`, `*_LEGACY_COMPAT_LEN`, and feature-gated overloads. Important persistence surfaces include:

- OSD superblock state: `OSDSuperblock` stores cluster and OSD FSIDs, OSD id, current epoch, weight, compatibility features, clean-through epoch, mounted epoch, purged-snap scrub state, cluster OSDMap trim lower bound, and guarded map epoch ranges. Decode upgrades legacy magic/compat and map range fields.
- PG collection metadata: `prepare_info_keymap` writes `epoch_key`, `fastinfo_key`, `info_key`, and `biginfo_key` values for PG state. It attempts `pg_fast_info_t` when only fast-applicable info changed, removes stale fast info when updates go backward, stores purged snaps separately from `pg_info_t`, and writes `PastIntervals` plus purged snaps when big info is dirty.
- Pool and PG metadata: `pg_pool_t`, `pg_info_t`, `pg_history_t`, `PastIntervals`, and `pg_stat_t` carry epoch, interval, scrub, autoscale, merge, snap, and placement state across monitor/OSD boundaries.
- Object metadata and logs: `object_info_t`, `SnapSet`, `pg_log_entry_t`, `pg_log_t`, `ObjectModDesc`, and `ObjectCleanRegions` capture object versions, mutations, duplicate request handling, rollback state, watchers, manifests, and per-object recovery/scrub state.

Decode paths commonly preserve cluster upgrade behavior by reading obsolete fields and discarding them, supplying defaults, or translating old representations. Examples include old OSD stat kilobyte fields to `store_statfs_t`, old pool snap flags, old `pg_pool_t` merge fields, old `hobject_t` pool ids, old watcher maps, old object copy omap maps, old scrub-map read-error flags, and removed `request_redirect_t` instruction payloads.

## Dependencies And Integration Points

- `osd_types.h` declares the types implemented here; `osd_types_fmt.h` and stream operators provide formatting integration.
- `OSDMap` consumes `pg_pool_t`, `object_locator_t`, `pg_t`, `spg_t`, and `PastIntervals` helpers for object placement, map interval detection, stretch-pool checks, and log filtering.
- Peering code uses `pg_info_t`, `pg_history_t`, `pg_notify_t`, `pg_query_t`, `PastIntervals`, `pg_lease_t`, `pg_stat_t`, `pg_log_t`, `pg_log_entry_t`, and `prepare_info_keymap` for state exchange and persistence.
- PGLog and PrimaryLogPG paths depend on `ObjectModDesc`, `ObjectCleanRegions`, `pg_log_entry_t`, `pg_log_dup_t`, `object_info_t`, `SnapSet`, and object copy/recovery structures.
- Recovery backends use `ObjectRecoveryInfo`, `ObjectRecoveryProgress`, `PullOp`, `PushOp`, and `PushReplyOp`, including queue-cost calculations keyed by `CephContext` config.
- Scrub code uses `ScrubMap`, `ScrubMap::object`, and `ScrubMapBuilder` for shallow/deep scrub state and incremental scrub-map exchange.
- Objectstore integration is through `ceph::os::Transaction` in `create_pg_collection` and `init_pg_ondisk`, plus collection names from `coll_t`.
- CRUSH integration appears in `pg_pool_t::raw_pg_to_pps`, `get_random_pg_position`, and `stretch_set_can_peer` through `CrushWrapper`, CRUSH hashes, and CRUSH bucket types.
- Formatter/JSON output uses `ceph::Formatter`, `JSONFormatter`, and stream operators for monitor/admin commands and debug output.

## Risks And Edge Cases

- Encoding changes are high risk. New fields must choose correct struct versions, feature gates, significant feature dependencies, compatibility defaults, and old-field masking. Divergent monitor/OSD encodings can cause map scrub noise, decode failures, or incorrect persisted state.
- Several decode paths accept legacy encodings by inference. Mistakes around old pool snap modes, old `hobject_t` pool ids, old `LOST_REVERT` ordering, watcher maps, or scrub read-error compatibility can silently produce wrong metadata.
- `object_locator_t` asserts that key and explicit hash are mutually exclusive. Callers constructing locators must preserve this or risk aborts.
- `pg_t` split/merge helpers assume correct PG counts and bit math. Bad `pg_num`, `pg_num_pending`, or mask recalculation can misclassify split/merge source/target PGs and disrupt peering/upmap cleanup.
- `coll_t::decode` throws if a v3 string cannot parse. Corrupt collection names or incompatible temp naming can break metadata reads.
- `object_stat_sum_t` current little-endian fast decode copies the whole struct layout. Field additions, padding, or ABI assumptions must remain aligned with the versioned layout.
- `PastIntervals::check_new_interval` is correctness-critical. Under-recording maybe-read-write intervals can lose witnesses for completed writes; over-recording can keep PGs down waiting for unnecessary or lost OSDs.
- `ObjectModDesc::visit` aborts on malformed operation codes or encoding exceptions. Corrupted log rollback descriptors are treated as fatal.
- Manifest reference-delta calculations are subtle around adjacent clones and equal chunks. Incorrect equality or dirty-region inputs can leak or prematurely drop chunk references.
- `prepare_info_keymap` mutates `last_written_info` and temporarily swaps `info.purged_snaps` out before encoding `info_key`; future edits must preserve restoration on all paths.
- Recovery op `cost` behavior differs between mClock and legacy weighted queues. Scheduler config changes can alter throttling and recovery fairness.
- `init_pg_ondisk` divides `expected_num_objects` by `pg_num`; callers must supply valid pool metadata with nonzero PG count.

## Test Signals

- Many types expose `generate_test_instances()` for Ceph's encode/decode corpus tests: request ids, locators, redirects, OSD stats, PG ids, collections, pool snaps/options/pools, object and pool stats, PG stats/history/info/notify/query, intervals, leases, log entries, copy data, hit-set history, superblocks, snapsets, watchers, chunks, manifests, recovery ops, scrub maps, and others.
- Serialization tests should round-trip current and legacy versions for `pg_pool_t`, `osd_stat_t`, `pg_stat_t`, `pg_info_t`, `PastIntervals`, `pg_log_entry_t`, `object_info_t`, `ScrubMap`, and `OSDSuperblock`, including feature-mask-dependent encodings.
- Placement tests should cover `pg_t` split/merge/ancestor/range behavior, `pg_pool_t` hash and mask helpers, namespace hashing, `raw_pg_to_pps`, random PG positions, and stretch-pool `stretch_set_can_peer`.
- Peering tests should exercise `PastIntervals::is_new_interval`, `check_new_interval`, `PriorSet::affected_by_map`, old/new acting/up changes, min_size changes, PG split/merge transitions, lost/down OSD changes, and stretch CRUSH bucket constraints.
- Persistence tests should verify `prepare_info_keymap` fast-info success/failure, stale fastinfo removal, biginfo writes, purged-snap separation, and `init_pg_ondisk` metadata keys/hints.
- Log tests should verify `pg_log_entry_t` checksum failures, rollback descriptor visiting, clean-region defaults for old logs, duplicate request copy limits, and `pg_log_t::filter_log` rejection of temp or wrong-PG entries.
- Manifest tests should cover reference deltas for setting, modifying, and removing chunked manifests with and without adjacent clone matches.
- Recovery and scrub tests should validate recovery op cost estimates, object recovery encode/decode with old pool ids, `ScrubMap::merge_incr` negative entries, and scrub object compatibility for read and EC mismatch errors.
