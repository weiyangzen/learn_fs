# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_versioning_self_heal_test.go

## Purpose

This test file validates versioning self-heal selector behavior.

## Important APIs, Types, and Functions

Tests exercise `selectLatestVersion` and `versionIdFromEntry` with helpers `newVersionEntry` and `newUntaggedVersionFile`.

## Control Flow

Cases cover mixed old/new formats, newest delete marker promotion, content winning when newer, only delete markers, empty/untagged entries, attribute-first ids, filename fallback, mixed tagged/untagged entries, and untagged delete markers.

## State and Persistence Behavior

All state is synthetic in-memory `filer_pb.Entry` slices modeling `.versions` children.

## Dependencies and Integration Points

The tests depend on version id helpers and S3 extended keys. They protect stale pointer heal/recovery and post-delete latest selection paths.

## Risks and Edge Cases

The key risk is resurrecting deleted objects by selecting older content over a newer delete marker, or ignoring valid `v_<id>` files without version-id metadata.

## Test Signals

The unit tests strongly cover selector semantics; pointer persistence needs integration coverage.
