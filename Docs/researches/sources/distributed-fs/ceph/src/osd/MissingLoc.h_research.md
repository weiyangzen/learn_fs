# sources/distributed-fs/ceph/src/osd/MissingLoc.h

## Purpose

`MissingLoc.h` declares and partly implements the placement-group recovery location index used by OSD peering and recovery. It tracks which objects need recovery, which shards are known possible sources for those objects, and aggregate counts of source availability split between shards in the current up set and other shards. The class gives peering code fast answers for unfound-object detection, readability, recoverability, recovery prioritization, and source cleanup.

## Important APIs, Types, and Functions

`MappingInfo` abstracts PG mapping facts needed by this index: current up set, whether the PG is erasure-coded, and PG size. `loc_count_t` counts known locations as `up` and `other`, orders counts for map keys, and asserts non-negative values when streamed. `missing_by_count_t` maps each EC `shard_id_t` or replicated `NO_SHARD` to a histogram of `loc_count_t` buckets.

The main state maps are `needs_recovery_map`, `missing_loc`, `missing_loc_sources`, and `missing_by_count`. Helpers `_get_count()`, `pgs_by_shard_id()`, `_inc_count()`, and `_dec_count()` maintain the aggregate count index. Public APIs include `needs_recovery()`, `is_deleted()`, `is_unfound()`, `readable_with_acting()`, `num_unfound()`, `have_unfound()`, `clear()`, `add_location()`, `remove_location()`, `clear_location()`, `add_active_missing()`, `add_missing()`, `revise_need()`, `add_source_info()`, `add_batch_sources_info()`, `check_recovery_sources()`, `remove_stray_recovery_sources()`, `recovered()`, `rebuild()`, and accessors for locations and maps.

## Control Flow and Data Flow

Missing data enters from the acting PG's `pg_missing_t` via `add_active_missing()` or explicit `add_missing()`. Source data enters from peer `pg_info_t` and `pg_missing_t` via `add_source_info()`, from proven batches via `add_batch_sources_info()`, or from direct location mutation. `is_unfound()` and `have_unfound()` combine `needs_recovery_map`, delete status, known locations, and the recoverable predicate. `readable_with_acting()` further intersects known locations with a caller-provided acting set and applies the readable predicate.

`rebuild()` is the densest inline flow. It first removes old state for one object, discovers the missing item from local missing data or peer missing maps for the recovery target set, returns if the object is no longer missing, records deletes without locations, and otherwise rebuilds source locations from self and peer maps using version, backfill, and peer-missing tests before recomputing counts.

## State and Persistence Behavior

`MissingLoc` is in-memory state derived from persistent PG metadata and current OSD map membership. `needs_recovery_map` records object-to-needed-version state, including delete markers. `missing_loc` records possible source shards only for non-delete objects when known. `missing_loc_sources` summarizes the source shards currently referenced. `missing_by_count` is a secondary index that must always match `missing_loc`; for EC PGs it contains an entry for every shard id, including empty sets for completely missing shards, while replicated PGs use `NO_SHARD`.

## Dependencies and Integration Points

The header depends on `OSDMap`, heartbeat handles, Ceph context/logging, `osd_types`, `pg_missing_t`, `pg_info_t`, `pg_shard_t`, `hobject_t`, `spg_t`, `DoutPrefixProvider`, and backend predicates `IsPGReadablePredicate` and `IsPGRecoverablePredicate`. `PeeringState` inherits `MappingInfo` and owns `MissingLoc`; `PG` exposes missing-by-count diagnostics; `PrimaryLogPG` consults readability during read processing; EC and replicated backends provide the predicates that define enough shards for read or recovery.

## Risks and Edge Cases

The class relies on callers to set readable and recoverable predicates before methods dereference them. EC count handling deliberately creates empty per-shard buckets, so tests must account for shards with zero locations. `add_active_missing()` asserts if the same object is added with a conflicting needed version, making inconsistent peering input fatal. `rebuild()` asserts local `last_backfill` is max and local `last_update` covers the needed version; it is intended for a specific peering state. Deletes are treated as recovery needs but not unfound source needs. Direct map accessors expose internal state as const references, so callers must not assume persistence beyond the current peering epoch.

## Test Signals

Tests should validate replicated and EC `missing_by_count` histograms, including completely missing EC shards, direct add/remove/clear location mutations, conflicting `add_active_missing()` input, delete handling, unfound counts, and predicate-driven recoverability. `rebuild()` needs cases where the item is local missing, peer missing, recovered, deleted, present on self, present on peers, blocked by peer `last_update`, blocked by `last_backfill`, and blocked by peer missing maps. OSD map changes should be tested through the `.cc` cleanup methods.
