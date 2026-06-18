# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/router.go

## Purpose
This file implements the event router that turns filer meta-log events and bootstrap-synthesized version events into lifecycle `Match` records for the scheduler/dispatcher. It bridges `reader.Event`, compiled lifecycle `engine.Snapshot` actions, and `s3lifecycle.EvaluateAction`, while carefully classifying versioned-object edge cases that cannot be inferred from a single filer entry.

## Important APIs, types, and functions
`SiblingLister` abstracts the filer lookups needed for versioned keys: survivor counts, specific version lookup, full version listing, and null-version lookup. `Survivors` describes sibling state for expired delete-marker routing. `Match` is the scheduled action payload, carrying `ActionKey`, compiled action, evaluation result, event/due times, bucket/object/version identity, and a CAS witness. `EntryIdentity` mirrors the lifecycle delete RPC identity fields without importing proto types.

`Route` is the main entry point. It short-circuits nil inputs, buckets with no action keys, inactive actions, scan-only actions, and incompatible MPU/non-MPU action shapes. It delegates to `routeBootstrapVersion`, `routePointerTransition`, and `routeSoleSurvivorMarker` for versioned paths. Helpers include `needsFullExpansion`, `successorModTimeFromContainer`, `routePointerTransitionDisplaced`, `routePointerTransitionExpand`, `emitNoncurrentMatches`, `buildObjectInfo`, `mpuInitInfo`, `buildIdentityFromEntry`, `extractTags`, `hasActiveEventDrivenAction`, and delete-marker/path classifiers.

## Control flow and state behavior
Normal current-object events build `ObjectInfo` from `ev.NewEntry`, compute a due time with `s3lifecycle.ComputeDueAt`, evaluate at that due time, and append matches. MPU init directory events are recognized under `.uploads/<upload_id>` using `ExtMultipartObjectKey`; part uploads and malformed init directories are suppressed.

For versioned buckets, `.versions` directory updates route noncurrent retention immediately when the latest pointer changes. Without `NewerNoncurrentVersions`, only the displaced version or bare null entry is looked up. With count-based retention, the router lists all version siblings, includes the bare null version, sorts newest-first by mtime then `CompareVersionIds`, locates the new latest, and emits only rank 0 plus threshold-crossing ranks instead of every expired version. Sole-survivor delete-marker handling lists sibling state and emits `ExpiredObjectDeleteMarker` only when exactly one versioned entry remains, it is a marker, and no bare null version survives. Bootstrap version events already contain logical-key, latest, rank, successor, and version metadata, so the router only builds `ObjectInfo` and applies action gates.

The file does not persist state itself. It depends on snapshot action state, filer extended attributes, and identity CAS to make duplicate or stale scheduled work harmless at dispatch time.

## Dependencies and integration points
The router integrates with `engine.Snapshot`, `reader.Event`, lifecycle rule evaluation, S3 constants such as `ExtLatestVersionIdKey`, `ExtLatestVersionMtimeKey`, `ExtVersionIdKey`, `ExtDeleteMarkerKey`, and filer `Entry` metadata. It assumes the S3 versioning code writes latest pointer metadata on `.versions` directories and optional successor stamps on displaced entries. The dispatcher consumes `Match` and uses `EntryIdentity` to protect deletes against drift.

## Risks and edge cases
The highest-risk logic is version ranking during pointer flips, especially null-version inclusion, stale cached mtime, missing new-version listings, and mixed old/new version IDs. Suppression on missing lister data is deliberate but can delay lifecycle work until bootstrap. `Schedule.Add` permits duplicates, so router over-emission can increase heap pressure even if CAS prevents destructive effects. Reflection is avoided here, but proto-independent `EntryIdentity` must remain encoding-compatible with server-side identity computation.

## Test signals
`router_test.go` covers nil/missing inputs, inactive actions, current expiration scheduling, prefix filtering, delete events, identity hashing, MPU shape gates, version-folder suppression, expired delete markers, bootstrap version handling, pointer transitions, null versions, stale/latest mtime behavior, expansion threshold logic, and suspended-versioning pointer clears.
