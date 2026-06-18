<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ClusterDataTypes.hh -->
# sources/distributed-fs/eos/mgm/placement/ClusterDataTypes.hh

Source read size: 440 lines, 13005 bytes.

## Purpose

Defines compact placement data structures used by the new EOS MGM filesystem scheduler: disks, hierarchical buckets, cluster snapshots, geotag hash storage, and formatted diagnostics.

## Important APIs, Types, and Functions

Important types are `fsid_t`, `item_id_t`, `epoch_id_t`, `Disk`, `Bucket`, `ClusterData`, and `StdBucketType`. Helpers include `getActiveStatus`, `GroupIDtoBucketID`, `BucketIDtoGroupID`, `BucketTypeToStr`, `FormatItemList`, `ClusterData::setDiskStatus`, `setDiskWeight`, `getDisksAsString`, `getBucketsAsString`, and `isValidBucketId`.

## Control Flow

There is no scheduler control loop here; methods perform atomic field updates and diagnostic table generation. `getActiveStatus` maps an online filesystem that is not booted to offline. Group ids are represented as negative bucket ids. `ClusterData` indexes disks by `fsid - 1` and buckets by `-bucket_id`.

## State and Persistence Behavior

`ClusterData` is an in-memory snapshot. Disk config/active status, weight, and percent used are atomics to allow live updates without rebuilding the full snapshot. Geotag hashes and string maps are diagnostic/topology state within the snapshot.

## Dependencies and Integration Points

Depends on `common::FileSystem` status enums, table formatter classes, atomics, vectors, and unordered maps. It is consumed by `ClusterMap`, `FlatScheduler`, and placement strategies.

## Risks and Edge Cases

Indexing assumes positive disk ids start at 1 and negative bucket ids fit the bucket vector. `setDiskStatus` checks `id > disks.size()` but not `id == 0`, so id 0 would index before the vector. The `Disk` size static assertion is ABI/performance-sensitive. `isValidBucketId` returns true for valid bucket ids; callers must not invert its meaning.

## Test Signals

Cover group/bucket id round trips, active status mapping with boot states, atomic status/weight updates, table formatting color thresholds, geotag display, invalid id handling including id 0, and `sizeof(Disk) == 8` compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ClusterDataTypes.hh -->
