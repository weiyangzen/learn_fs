# sources/distributed-fs/seaweedfs/weed/s3api/s3api_internal_lifecycle.go

## Purpose
Implements the internal lifecycle delete executor called by lifecycle workers. It re-fetches live object state, verifies an expected identity witness, enforces object-lock protections, dispatches expiration/noncurrent/delete-marker/abort-MPU actions, and classifies results into worker outcomes.

## Important APIs, Types, And Functions
`LifecycleDelete` is the gRPC-facing entry point for `s3_lifecycle_pb.LifecycleDeleteRequest`. `lifecycleDispatch` handles expiration, noncurrent, newer-noncurrent, expired-delete-marker, and defensive unknown action paths. `lifecycleAbortMPU` validates and removes multipart upload init directories. `checkSoleSurvivorMarker` prevents unsafe expired-delete-marker deletion if the marker is not the sole/latest surviving version or if a null version exists. `isCurrentLatestVersion`, `computeEntryIdentity`, `identityMatches`, `entryUsesMetadataOnlyDelete`, `recordMetadataOnlyIf`, `done`, `noopResolved`, `blocked`, and `retryLater` are supporting helpers.

## Control Flow
`LifecycleDelete` rejects empty requests as `BLOCKED`, routes `ABORT_MPU` before object fetch, then fetches the object/version. Not-found variants become `NOOP_RESOLVED`; other fetch errors become `RETRY_LATER`. If the live entry identity differs from `ExpectedIdentity`, the request is stale and becomes `NOOP_RESOLVED`. Object lock is enforced without bypass. Expiration of current versions branches on bucket versioning: enabled creates a delete marker, suspended best-effort deletes the null version then creates a delete marker, and unversioned deletes the regular object. Noncurrent and expired-marker actions require `VersionId`, guard against deleting the current latest version, optionally re-check sole-survivor marker state, then delete the specific version. Metadata-only TTL-stamped entries increment a Prometheus counter instead of forcing per-chunk delete accounting.

## State And Persistence
The executor mutates filer state by creating delete markers, deleting unversioned objects, deleting specific version files, and recursively removing `.uploads/<upload_id>` directories. It reads versioning state, `.versions/` directory metadata, `ExtLatestVersionIdKey`, object-lock extended attributes, object chunks, object attributes, and extended metadata. It updates only metrics locally.

## Dependencies And Integration Points
It depends on `filer_pb`, `s3_lifecycle_pb`, S3 versioning constants, lifecycle hashing, object-lock enforcement, versioned object helpers, delete marker helpers, filer listing, `rm`, `exists`, and stats collection. It is the server side of the lifecycle worker contract: worker retries and budgets depend on the returned outcome and reason strings.

## Risks And Test Signals
Key risks are stale event deletion, current-version deletion from a noncurrent action, path traversal during abort-MPU, object-lock bypass, delete-marker races while `.versions/` latest-pointer metadata is being updated, and metadata-only counter drift. Tests should verify outcome classification, malformed MPU path blocking, identity CAS fields, latest-pointer guards, sole-survivor marker checks, object-lock skips, and metadata-only metrics.
