# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/router_test.go

## Purpose
This test file is the behavioral specification for the lifecycle router. It creates compiled snapshots, synthetic filer events, and fake sibling listers to pin routing semantics for current objects, MPU cleanup, versioned objects, delete markers, bootstrap backfill, and pointer-transition races.

## Important APIs, types, and helpers
`compileWith`, `compileWithVersioned`, and `activatedPrior` build active `engine.Snapshot` instances around lifecycle rules. `eventCreate`, `mpuInitEvent`, `markerEvent`, `versionsContainerEvent`, and `versionsContainerEventStaleMtime` construct event shapes matching production storage layouts. `recordingLister` implements `SiblingLister` and records calls to assert when filer I/O is, or is not, performed. `bootstrapVersionEntry`, `markerLoneEntry`, `displacedVersionEntry`, `contains`, and `indexOf` support versioned test cases.

## Control flow and state behavior under test
The first tests verify baseline routing: nil snapshots, foreign buckets, inactive actions, current object expiration, future scheduling, prefix filters, hard deletes, missing attributes, and identity capture including head file ID and extended attribute hash. MPU tests verify that only init directories under `.uploads/<id>` route `AbortIncompleteMultipartUpload`, that destination-key prefix matching is used, and that MPU init events cannot accidentally route noncurrent actions while regular objects cannot route abort actions.

Versioned tests assert that version-file events are skipped without sibling context, current bare-key events still route expiration, non-versioned buckets do not treat `.versions` suffixes specially, and expired delete marker handling requires a sole marker and no null version. Bootstrap tests assert logical-key routing, empty `VersionID` for latest expiration, successor-clock use for noncurrent retention, `NewerNoncurrentVersions` rank suppression, and no MPU routing for version entries.

Pointer-transition tests cover one-lookup displaced routing, unchanged pointers, empty old pointers, null-version displacement, full expansion with null siblings, missing displaced entries, skipping lookup when no noncurrent rule exists, threshold crossing under `NewerNoncurrentVersions`, missing new latest suppression, unversioned bucket suppression, missing cached latest mtime, stale directory mtime avoidance, and suspended-versioning clears using null mtime.

## Dependencies and integration points
The tests depend on `filer_pb.Entry` metadata shapes, `s3_constants` extended keys, `reader.BootstrapVersion`, and engine compile/prior-state behavior. They make strong assertions about the contract between S3 versioning storage layout and router classification.

## Risks and gaps
The suite is broad but still mostly unit-level. It does not exercise actual filer RPC pagination or dispatcher CAS RPC behavior; those are represented by fake listers and match shape assertions. Time-sensitive assertions use broad day-scale comparisons rather than exact monotonic clock behavior.

## Test signals
This file itself is the primary test signal for `router.go`; it documents many regressions in comments, especially cursor-freeze risks from wrong action kind/version ID combinations and heap-pressure risks from over-emitting pointer-transition matches.
