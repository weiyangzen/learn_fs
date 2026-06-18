<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/PlacementStrategy.hh -->
# sources/distributed-fs/eos/mgm/placement/PlacementStrategy.hh

Source read size: 387 lines, 12482 bytes.

## Purpose

Declares the common placement strategy interface, placement/access argument structures, result structure, strategy enum/string mapping, validation helpers, and deterministic hash ranking primitives.

## Important APIs, Types, and Functions

Important items are `PlacementResult`, `PlacementStrategyT`, `PlacementArguments`, `AccessArguments`, abstract `PlacementStrategy::placeFiles` and `access`, `validateArgs`, `validDiskPlct`, `calculateMaxGeoOverlap`, `placeWithGeoFilter`, `hashFid`, and `RankedItem`.

## Control Flow

Concrete strategies call `validateArgs` before selecting. `validDiskPlct` rejects non-disk ids, excluded filesystems, offline disks, and disks below the requested config status. Strategy string conversion maps unknown strings to `kGeoScheduler`. `hashFid` hashes fid/fsid/salt in little-endian order for cross-platform deterministic ranking.

## State and Persistence Behavior

The header defines data passed through scheduler calls; no persistence is owned. `PlacementResult` contains a fixed array of 32 ids, return code, replica count, and optional error text.

## Dependencies and Integration Points

Consumed by all placement strategies, `FlatScheduler`, and `FSScheduler`. Depends on cluster data, `RRSeed`, xxhash, and EOS status enums.

## Risks and Edge Cases

`PlacementResult::contains` searches up to `n_replicas`, not the number already filled, so default zeros can matter if used before all slots are set. The result array caps placements at 32 replicas. `validateArgs` compares bucket vector size to replica count, not the selected bucket's item count only. Unknown strategy strings silently become geoscheduler.

## Test Signals

Test enum/string round trips, unknown strategy defaulting, validation errors, exclude/status filtering, result validity for positive/negative ids, hash determinism across endian platforms, and max-replica boundary behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/PlacementStrategy.hh -->
