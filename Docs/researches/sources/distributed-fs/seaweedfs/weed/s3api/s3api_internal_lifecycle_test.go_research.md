# sources/distributed-fs/seaweedfs/weed/s3api/s3api_internal_lifecycle_test.go

## Purpose
Unit tests lifecycle delete helper invariants that do not require a live filer. Coverage focuses on identity witnesses, extended-metadata hashing, defensive blocked outcomes, abort-MPU path validation, metadata-only detection, and Prometheus metric increments.

## Important APIs, Types, And Functions
Tests directly call `computeEntryIdentity`, `s3lifecycle.HashExtended`, `identityMatches`, `LifecycleDelete`, `lifecycleDispatch`, `entryUsesMetadataOnlyDelete`, `recordMetadataOnlyIf`, and local `contains`. They use `filer_pb.Entry`, `FuseAttributes`, `FileChunk`, `s3_lifecycle_pb.EntryIdentity`, `LifecycleDeleteRequest`, and `testutil.ToFloat64` for metrics.

## Control Flow
Identity tests construct entries with mtimes, sizes, chunks, and extended metadata and assert exact fields and comparison behavior. Hash tests ensure map order does not affect hashes, delimiter-like payloads do not collide, and nil/empty maps produce empty hashes. Lifecycle dispatch tests assert empty requests, malformed MPU paths, routed-after-fetch `ABORT_MPU`, unknown action kinds, and missing version ids all produce `BLOCKED` without gRPC errors. Metadata-only tests check nil safety, `TtlSec > 0`, negative TTL rejection, counter increments for enabled calls, no-op when disabled, nil request safety, and empty rule-hash labeling.

## State And Persistence
No filer state is persisted. The only shared state touched is the global `S3LifecycleMetadataOnlyCounter`; tests isolate series by unique bucket labels to avoid cross-test interference.

## Dependencies And Integration Points
These tests tie lifecycle executor behavior to `s3lifecycle.HashExtended`, Prometheus stats, lifecycle protobuf outcomes, and filer entry attribute semantics. They are guardrails for worker-facing classification rather than integration tests of actual deletes.

## Risks And Test Signals
Strong signals include CAS field completeness, hash stability, safe nil handling, path traversal rejection, and metadata-only metric behavior. Missing coverage includes real versioning state, filer errors, object-lock enforcement, successful delete marker creation, and sole-survivor marker races.
