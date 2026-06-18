<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_on_meta_event_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_on_meta_event_test.go

## Purpose
Tests bucket event handling for a rename into the bucket root.

## Important APIs and Types
Defines `bucketTrackingStore`, a minimal `FilerStore` plus `BucketAware` implementation recording created/deleted bucket names. `TestOnBucketEventsRenameIntoBucketsRootCreatesBucket` calls `onBucketEvents`.

## Control Flow and State
The test creates a filer with `DirBucketsPath` `/buckets`, sends a rename-like metadata response with old directory `/tmp` and `NewParentPath` `/buckets`, and asserts one bucket creation and no deletion.

## Persistence Behavior
No persistence. The tracking store records events in slices.

## Dependencies and Integration Points
Uses `NewFilerStoreWrapper`, `filer_pb.SubscribeMetadataResponse`, and package bucket event code. It validates wrapper forwarding of bucket callbacks to bucket-aware stores.

## Risks
The test models event shape manually; it does not assert `filer_pb.IsRename` construction from a real rename path. Other create/delete/rename-out cases are not tested.

## Test Signals
Useful regression for renamed directories becoming buckets when moved into the S3 bucket root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_on_meta_event_test.go -->
