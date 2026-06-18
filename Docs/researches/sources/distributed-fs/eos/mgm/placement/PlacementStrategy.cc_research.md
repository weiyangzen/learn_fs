<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/PlacementStrategy.cc -->
# sources/distributed-fs/eos/mgm/placement/PlacementStrategy.cc

Source read size: 131 lines, 5218 bytes.

## Purpose

Implements shared geolocation-aware helper logic for placement strategies.

## Important APIs, Types, and Functions

Defines `PlacementStrategy::calculateMaxGeoOverlap` and `PlacementStrategy::placeWithGeoFilter`. These operate on `ClusterData::disk_tags`, current `PlacementResult`, and a pre-sorted candidate list.

## Control Flow

`calculateMaxGeoOverlap` rejects non-disk or missing topology candidates, compares the candidate geotag hash vector with every already selected disk, and returns the maximum common prefix depth. `placeWithGeoFilter` walks sorted candidates, skips non-disk and duplicate entries, computes overlap, and skips overlapping candidates only when there are more than twice as many remaining candidates as needed. It fills result ids until the requested replica count or returns `ENOSPC`.

## State and Persistence Behavior

No state is stored. The functions are pure with respect to cluster input and result output.

## Dependencies and Integration Points

Used by placement strategies that want topology spreading after candidate ranking. Depends on `PlacementStrategy.hh` and geotag vectors populated by `StorageHandler::addGeoTag`.

## Risks and Edge Cases

If a candidate id is beyond `disk_tags`, overlap is treated as `max`, which encourages skipping when possible. Candidates without tags get zero overlap. The buffer factor heuristic is intentionally approximate and may still place replicas in the same topology when capacity is tight.

## Test Signals

Unit-test overlap depth for shared site/room/rack prefixes, missing tags, invalid ids, duplicate candidates, insufficient candidates, and cases where the skip heuristic should or should not preserve enough candidates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/PlacementStrategy.cc -->
