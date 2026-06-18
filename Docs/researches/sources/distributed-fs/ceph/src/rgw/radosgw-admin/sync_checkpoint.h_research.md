# sources/distributed-fs/ceph/src/rgw/radosgw-admin/sync_checkpoint.h

## Purpose
Declares the admin-facing bucket sync checkpoint API for waiting on bucket replication catch-up.

## Important APIs, Types, and Functions
- Forward declares `DoutPrefixProvider`, `rgw::sal::RadosStore`, `RGWBucketInfo`, and `RGWBucketSyncPolicyHandler`.
- Exposes `rgw_bucket_sync_checkpoint(...)` with source-zone/source-bucket filters, retry delay, and timeout deadline.

## Control Flow
This header has no control flow. It establishes the contract consumed by `radosgw-admin` command code and implemented in `sync_checkpoint.cc`.

## State and Persistence
No state is stored here. The signature makes persistence dependencies explicit through the RADOS store, bucket info, and sync policy inputs.

## Dependencies and Integration Points
Includes `common/ceph_time.h` for deadline/delay types and `rgw_basic_types.h` for `rgw_zone_id`/`rgw_bucket`. It is a narrow integration point between admin commands and bucket sync internals.

## Risks and Edge Cases
The API exposes an absolute timeout rather than a duration; callers must compute it consistently with the monotonic coarse clock. Optional filters must be interpreted by the implementation without silently skipping all intended sources.

## Test Signals
Compile/link coverage should confirm only the minimal forward declarations are needed. Admin tests should verify caller-provided filters and timeout values reach the implementation.
