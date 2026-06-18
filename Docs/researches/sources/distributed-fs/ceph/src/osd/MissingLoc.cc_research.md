# sources/distributed-fs/ceph/src/osd/MissingLoc.cc

## Purpose

`MissingLoc.cc` implements the out-of-line recovery-source maintenance methods for `MissingLoc`. `MissingLoc` is used during OSD peering and recovery to track objects that need recovery, which shards may contain usable copies, and how that source knowledge changes as peers go down or become stray. This file contains the heavier scans over missing objects and source sets, with logging and thread-pool heartbeat resets for long loops.

## Important APIs, Types, and Functions

`readable_with_acting()` checks whether an object can be read from the current acting set. It returns true for objects not needing recovery, false for deletes or no known locations, intersects known locations with `acting`, and asks the configured readable predicate if that shard subset suffices.

`add_batch_sources_info()` marks a set of sources as usable for every non-delete missing object, updating both `missing_loc` and `missing_loc_sources`. `add_source_info()` evaluates a single peer's `pg_info_t` and `pg_missing_t` against every needed object, adding the peer only when its `last_update` is new enough, the object is before `last_backfill`, and the peer is not also missing that object. `check_recovery_sources()` removes sources whose OSDs are now down according to the OSD map. `remove_stray_recovery_sources()` removes one stray shard from all source structures.

## Control Flow and Data Flow

The add-source flow scans `needs_recovery_map`. For each non-delete item it validates whether the source plausibly has the needed version: source `last_update >= need`, object order before `last_backfill`, and not present in the peer's missing set. If valid, it creates or updates `missing_loc[object]`, temporarily decrements the count index before mutation, inserts the source, and increments the count index afterward. The batch form skips the per-object pg-info tests and applies the same source set to every non-delete missing object.

The removal flows are inverse scans. Down or stray shards are removed from `missing_loc_sources`, then each object's source set is filtered. Objects with no remaining sources are erased from `missing_loc`; otherwise their `missing_by_count` bucket is recomputed. Long loops periodically reset `HBHandle` timeouts based on `osd_loop_before_reset_tphandle`, and `add_source_info()` suppresses verbose per-object logging after about 0.5 seconds.

## State and Persistence Behavior

This file mutates in-memory peering and recovery state only. It does not encode or persist `MissingLoc`; durable truth comes from PG logs, `pg_missing_t`, `pg_info_t`, and OSD maps. The key invariant is that `missing_by_count` remains synchronized with `missing_loc`: mutations call `_dec_count()` before changing a non-empty set and `_inc_count()` after the final set is known. `missing_loc_sources` is a deduplicated index of all shards currently believed to be recovery sources.

## Dependencies and Integration Points

The implementation depends on `MissingLoc.h`, `OSDMapRef`, `pg_info_t`, `pg_missing_t`, `pg_missing_item`, `HBHandle`, Ceph logging macros, `CephContext`, and backend-provided readable/recoverable predicates. It is owned by `PeeringState`, surfaced in `PG` diagnostics through missing-by-count output, and used by `PrimaryLogPG` read paths to decide whether degraded or recovering objects are readable with the acting set.

## Risks and Edge Cases

The correctness risk is stale or overbroad source knowledge. `add_batch_sources_info()` assumes all listed sources can serve all non-delete missing objects, so it must be used only when that condition is externally proven. `add_source_info()` has a known uncertainty around `last_backfill` comments: an object past `last_backfill` is treated as missing on the peer. Missing deletes are deliberately not source-tracked. Any mutation that skips `_dec_count()` or `_inc_count()` corrupts recovery prioritization statistics. Logging suppression prevents log floods but can obscure individual object decisions in large PGs.

## Test Signals

Tests should exercise source addition for peers with too-old `last_update`, objects past `last_backfill`, peers that also list the object missing, deletes, and successful source discovery. Recovery-source removal tests should verify down OSDs and stray shards disappear from both `missing_loc_sources` and per-object locations, with empty objects removed. Invariants should assert that the sum of `missing_by_count` buckets matches `missing_loc` after every add/remove path. Readability tests should cover replicated and EC predicates with acting-set intersections.
