# subset-b-007883 grouped research

This grouped report covers the requested SeaweedFS S3 lifecycle router/scheduler helpers and S3 Tables handler files. Each section is source-tree aligned and bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/router.go -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/router.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/router_test.go -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/router_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/schedule.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/schedule.go

## Purpose
This file provides the lifecycle worker's in-memory pending queue. It orders `Match` values by due time so the dispatcher can poll for ready actions and leave future work in place.

## Important APIs and functions
`Schedule` wraps a `scheduleHeap` with a mutex. `NewSchedule` constructs an empty schedule. `Add` pushes a match. `Len` returns pending count. `NextDue` exposes the earliest due time without popping. `Drain` pops every match whose `DueTime <= now` and returns them in due-time order. `scheduleHeap` implements `heap.Interface` with `Less` ordered by `Match.DueTime.Before`.

## Control flow and state behavior
All public methods take the mutex before reading or mutating the heap, making concurrent producer/consumer use safe at the data-structure level. The queue is ephemeral process memory; pending lifecycle work is not persisted here. Duplicate entries are intentionally allowed, because schedule-time dedup would need extra indexing while dispatcher identity CAS resolves stale duplicates safely.

## Dependencies and integration points
The schedule depends on the standard `container/heap`, `sync`, and `time` packages plus the local `Match` type. It is consumed by the lifecycle dispatch loop, which calls `Drain` on each tick and uses `NextDue`/`Len` for visibility or sleeping decisions.

## Risks and edge cases
Duplicates can grow heap size for hot keys if upstream routing over-emits. The heap ordering is only by due time; equal due times have no stable tie-break. Because state is in-memory, process restarts require bootstrap or event replay to restore pending work.

## Test signals
`schedule_test.go` verifies empty behavior, ordering, inclusive drain boundary, duplicate preservation, no-op drain before any item is due, heap invariants after partial drain and add-after-drain, ascending drain order, and concurrent add/drain race safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/schedule.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/schedule_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/schedule_test.go

## Purpose
This file tests the lifecycle `Schedule` heap contract. It ensures due-time ordering and mutex-protected concurrent access behave as the dispatcher expects.

## Important APIs and helpers
`mkMatch` creates small `Match` values with an `ActionKey`, `DueTime`, and `ObjectKey`. The tests call `NewSchedule`, `Add`, `Len`, `NextDue`, and `Drain` directly.

## Control flow and state behavior under test
The tests cover an empty schedule returning length zero, no next due time, and nil drain output. They insert matches out of order and assert `NextDue` returns the minimum and `Drain` returns due matches in ascending due-time order. Boundary behavior is pinned as inclusive: an item due exactly at `now` drains. Duplicate matches with the same object key and due time are retained and drained separately. Partial drains leave future entries in the heap, and adding a new earlier entry after a drain correctly updates `NextDue`.

## Dependencies and integration points
The tests use the local router package and `s3lifecycle.ActionKey` only to satisfy the `Match` shape. They implicitly validate `container/heap` usage through public schedule operations rather than inspecting internals.

## Risks and gaps
The concurrent test only asserts no deadlock or data race under race-enabled runs; without `go test -race`, it mainly exercises completion. It does not test process restart recovery because `Schedule` has no persistence layer.

## Test signals
The suite is a clear regression guard for dispatcher timing semantics: no early dispatch, no missed remaining minimum after partial drains, no deduplication, and thread-safe add/drain interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/schedule_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/rule.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/rule.go

## Purpose
This file defines the canonical flat lifecycle rule and object-evaluation data structures shared across the lifecycle compiler, router, evaluator, scheduler, and tests.

## Important APIs and types
`Rule` represents XML-derived lifecycle configuration after canonicalization. It includes rule identity/status, prefix, current expiration by days or date, expired delete marker flag, noncurrent expiration days, `NewerNoncurrentVersions`, abort-MPU days, tag filters, and size filters. `ObjectInfo` describes a candidate object or MPU init event: key, modification time, size, current/delete-marker state, version count, successor modification time, optional noncurrent rank, tags, and MPU-init marker. Constants define enabled/disabled statuses, `SmallDelay`, action enum values, and `EvalResult`.

## Control flow and state behavior
The file has no executable control flow and no persistence. Its field semantics drive other packages: zero values generally mean unset, `NoncurrentIndex` is a pointer so rank zero is distinguishable from unknown, and `SuccessorModTime` is the clock for noncurrent retention.

## Dependencies and integration points
The only direct dependency is `time`. The structures are populated by XML parsing/canonicalization, router event classification, bootstrap version walking, and S3 Tables-independent lifecycle evaluation code. `RuleHash`, `RuleActionKinds`, `ComputeDueAt`, and `EvaluateAction` depend on these fields.

## Risks and edge cases
`FilterSizeGreaterThan` cannot represent an explicit greater-than-zero exclusion differently from unset zero, as noted in the comment. Misinterpreting zero-valued days, dates, rank pointers, or MPU flags can produce immediate or wrong-kind actions. Because this is a shared schema, adding fields requires updating hashing, evaluation, XML canonicalization, and tests.

## Test signals
This file has no direct tests, but its fields are exercised by rule hash tests, router tests, config-load tests, and evaluator/compiler tests elsewhere in the package tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/rule.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/rule_hash.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/rule_hash.go

## Purpose
This file computes stable compact identifiers for lifecycle rules. The hash is used in `ActionKey` state so compiled actions can retain continuity across rule ID renames and status flips while changing when filters or action semantics change.

## Important APIs and functions
`RuleHash` returns the first eight bytes of SHA-256 over a canonical length-prefixed encoding. It includes prefix, sorted tag filters, size filters, expiration days/date/delete-marker flag, noncurrent days, noncurrent keep count, and MPU abort days. It intentionally ignores `Rule.ID` and `Rule.Status`. Helpers `writeBytes`, `writeUvarint`, `writeInt64`, `writeBool`, and `canonicalTime` encode values with field tags and varint length/value framing.

## Control flow and state behavior
The function is nil-safe, returning a zero hash for nil rules. Tag keys are sorted before encoding so map iteration order cannot perturb hashes. `ExpirationDate` is canonicalized to UTC RFC3339Nano; zero time encodes as an empty string. The file has no persistence but influences persisted or long-lived scheduler prior states keyed by rule hash.

## Dependencies and integration points
Dependencies are `crypto/sha256`, `encoding/binary`, `sort`, and `time`. The hash is consumed by engine compile output, scheduler prior-state seeding, router match keys, and any code reconciling rule state across refreshes.

## Risks and edge cases
Only eight bytes of SHA-256 are retained, so theoretical collision risk exists but is small for operational rule counts. Any new semantically relevant `Rule` field must be added to this encoding or stale action state may be reused after a rule change. Conversely, adding non-semantic fields would unnecessarily reset state if included.

## Test signals
`rule_hash_test.go` covers determinism, tag-order invariance, prefix sensitivity, ignored ID/status, different action/filter fields, nil safety, and delimiter/field-boundary collision resistance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/rule_hash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/rule_hash_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/rule_hash_test.go

## Purpose
This file verifies the stability and semantic sensitivity of `RuleHash`, especially around fields that determine lifecycle action identity and bootstrap/event-driven state continuity.

## Important APIs and test cases
Tests call `RuleHash` with constructed `Rule` values. They cover deterministic repeat hashing, tag map order invariance, prefix trailing slash significance, ID/status ignoring, different days/action kinds/filter fields, nil handling, and collision resistance against naive delimiter encodings.

## Control flow and state behavior under test
The tests establish that operational state should survive rule renames and enable/disable flips because those fields are not hashed. They also establish that prefix, tags, size filters, and action parameters must change the hash because they alter the object/action match set. Collision-resistance tests use embedded `=`, newline, and separator-like prefix strings to ensure length-prefix and field-tag encoding isolates fields.

## Dependencies and integration points
The file depends only on the local lifecycle package and Go testing. It protects consumers such as `engine.ActionKey`, scheduler prior-state maps, and router matches from subtle hash instability or accidental state reuse.

## Risks and gaps
The tests do not prove cryptographic collision absence for the truncated eight-byte digest. They also only cover fields currently present in `Rule`; future fields need corresponding test additions.

## Test signals
These tests are strong evidence that the current hash encoding has intentional compatibility semantics and is safe against common delimiter-forgery regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/rule_hash_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/scheduler/configload.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/scheduler/configload.go

## Purpose
This file loads S3 bucket lifecycle configurations from filer bucket entries and converts them into `engine.CompileInput` records for lifecycle snapshot compilation.

## Important APIs and functions
`BucketLifecycleConfigurationXMLKey` names the extended attribute containing lifecycle XML. `ParseError` records per-bucket parse failures without aborting the whole load. `LoadCompileInputs` lists bucket entries under a buckets path, parses non-empty lifecycle XML via `lifecycle_xml.ParseCanonical`, and returns compile inputs plus parse errors. `IsBucketVersioned` interprets the bucket versioning extended attribute as versioned when it is `Enabled` or `Suspended`, case/space normalized. `AllActivePriorStates` creates event-driven bootstrap-complete prior states for every action kind in every rule.

## Control flow and state behavior
`LoadCompileInputs` paginates through bucket entries with a 1024 entry page size and `startFrom` continuation. It skips non-directories, buckets with missing or empty lifecycle XML, malformed configs after recording `ParseError`, and configs that parse to zero rules. Transport/listing errors abort the entire load. No data is persisted here; compile inputs are regenerated from filer metadata.

## Dependencies and integration points
The file depends on `filer_pb.SeaweedList`, bucket entry extended attributes, S3 lifecycle XML canonicalization, S3 constants for versioning, and the engine compile API. It is part of scheduler refresh, feeding `engine.New().Compile` elsewhere. `AllActivePriorStates` is a temporary or out-of-band scheduler behavior that treats all loaded actions as ready for event-driven dispatch.

## Risks and edge cases
Malformed XML is intentionally non-fatal but can disable lifecycle for that bucket until corrected. Pagination correctness is important at cluster scale; a bad `startFrom` loop could skip buckets. `AllActivePriorStates` bypasses incremental bootstrap completeness and may schedule immediately for all rules, so production callers must understand the current bootstrap model.

## Test signals
`configload_test.go` covers versioning value parsing, prior-state seeding, empty/missing configs, file skipping, valid XML, malformed XML parse errors, and pagination beyond one page.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/scheduler/configload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/scheduler/configload_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/scheduler/configload_test.go

## Purpose
This file tests scheduler lifecycle config loading from filer bucket metadata. It verifies bucket versioning classification, prior-state seeding, and bucket directory pagination/skip/error semantics.

## Important APIs and helpers
The tests use `bucketEntry`, `dirEntry`, `fileEntry`, and `fakeFilerClient` from `testhelpers_test.go`. `minimalLifecycleXML` provides a valid one-rule XML config. Tests call `IsBucketVersioned`, `AllActivePriorStates`, and `LoadCompileInputs`.

## Control flow and state behavior under test
Versioning tests assert that missing attributes are false, `Enabled` and `Suspended` are accepted case-insensitively with whitespace, and unrelated values are rejected. Prior-state tests verify empty inputs produce empty maps and that every action kind receives a `BootstrapComplete=true`, `ModeEventDriven` state keyed by bucket and rule hash. Loader tests assert empty directories, stray files, buckets without XML, and buckets with empty XML are skipped. Valid config becomes one compile input, versioning propagates, malformed XML becomes a parse error while good buckets still load, and 1030 buckets force multi-page listing without skip/duplication.

## Dependencies and integration points
The tests use `filer_pb`, S3 constants, lifecycle rules, engine action keys, and testify assertions. They exercise the fake stream implementation enough to model `SeaweedList` pagination.

## Risks and gaps
The tests do not connect to a real filer or validate all XML variants; parser details are delegated to `lifecycle_xml` tests. They do not test cancellation except through helper stream support.

## Test signals
The suite provides good regression coverage for scheduler refresh correctness, especially the risk of silently missing buckets after the first page or conflating prior states between buckets with identical rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/scheduler/configload_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/scheduler/testhelpers_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/scheduler/testhelpers_test.go

## Purpose
This file provides an in-memory fake filer client and streaming list response used by scheduler config-load tests.

## Important APIs and types
`fakeListStream` implements `grpc.ServerStreamingClient[filer_pb.ListEntriesResponse]` with `Recv`, metadata methods, `Context`, `SendMsg`, and `RecvMsg`. `fakeFilerClient` embeds `filer_pb.SeaweedFilerClient` and implements `LookupDirectoryEntry` plus `ListEntries`. Helper constructors `dirEntry` and `fileEntry` build test entries.

## Control flow and state behavior
`fakeListStream.Recv` returns context cancellation errors, then streams prebuilt responses until `io.EOF`. `fakeFilerClient.ListEntries` records listed directories, increments an atomic count, filters by `StartFromFileName` and `InclusiveStartFrom`, sorts names stably, applies `Limit`, and wraps entries as list responses. `LookupDirectoryEntry` searches the configured tree and returns `filer_pb.ErrNotFound` on misses. State is protected by a mutex for tree/listed access and an atomic counter for listing count.

## Dependencies and integration points
The helpers depend on `filer_pb`, `grpc`, and `metadata`. They model enough of the Seaweed filer API for `filer_pb.SeaweedList` and direct lookup calls used by config loading.

## Risks and edge cases
This fake assumes entries are all available in memory and sorted lexicographically by name. It does not model streaming backpressure, server errors other than context cancellation, permissions, or concurrent mutation during pagination. Tests depending on it should not overgeneralize to real filer behavior.

## Test signals
The helper is indirectly validated by `configload_test.go`, especially pagination and continuation token behavior around page boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/scheduler/testhelpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/shard.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/shard.go

## Purpose
This file maps lifecycle events into a fixed shard space for per-shard readers and cursors. Stable sharding lets workers divide the bucket/key keyspace and advance independent read tasks.

## Important APIs and functions
`ShardCount` is fixed at 16. `ShardID(bucket, key string) int` hashes `bucket + "/" + key` with SHA-256 and returns the top four bits of the first digest byte. `shardHashPool` is a `sync.Pool` of SHA-256 hashers to reduce allocations in the hot path.

## Control flow and state behavior
`ShardID` gets a hasher from the pool, resets it, writes bucket, separator, and key bytes, computes the digest into a stack buffer, returns the hasher to the pool, and maps to `[0, ShardCount)`. No persistent state is stored; stability comes from deterministic hashing and the constant shard count.

## Dependencies and integration points
The file depends on `crypto/sha256`, `hash`, and `sync`. It integrates with lifecycle reader task partitioning and any cursor storage keyed by shard.

## Risks and edge cases
Changing `ShardCount`, the separator, or the hash algorithm would remap all keys and could invalidate cursor ownership assumptions. Pooling hashers requires every call to reset before use, which this implementation does. Distribution is statistical; small key sets may be imbalanced.

## Test signals
`shard_test.go` checks range safety, determinism, and a basic distribution signal across different bucket names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/shard.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/shard_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/shard_test.go

## Purpose
This file tests the `ShardID` keyspace partition helper used by lifecycle readers.

## Important APIs and test cases
The tests call `ShardID` and compare results to `ShardCount`. Cases include empty strings, ordinary bucket/key pairs, nested object keys, Unicode strings, and empty object keys.

## Control flow and state behavior under test
`TestShardIDInRange` ensures all sampled inputs map into `[0, ShardCount)`. `TestShardIDDeterministic` calls the same bucket/key twice and requires identical output. `TestShardIDDistinctFromBucket` hashes one key across sixteen bucket names and expects at least four distinct shards as a coarse distribution check.

## Dependencies and integration points
The tests live in the lifecycle package and do not mock anything. They protect code that assigns reader tasks and shard cursors.

## Risks and gaps
The distribution test is intentionally statistical and small; it would not catch all skew patterns. It also does not pin exact shard IDs, which is good for implementation flexibility but means accidental remapping could pass unless range/distribution stayed plausible.

## Test signals
The tests confirm the minimum stable-contract properties: bounded output, deterministic mapping, and bucket name participation in the hash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/shard_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/tags.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/tags.go

## Purpose
This file defines the lifecycle package's object-tag extended-attribute prefix constant.

## Important APIs and state
`tagPrefix` is the string `X-Amz-Tagging-`. It is package-private, so it is intended for internal lifecycle code that reads or writes S3 object tag metadata from filer entry extended attributes.

## Control flow and persistence behavior
There is no control flow. Persistence behavior is implicit: object tags are represented as extended attributes whose keys use this prefix plus the tag key.

## Dependencies and integration points
The file has no imports. It aligns with S3 metadata constants and router tag extraction, which similarly reads extended attributes named with the S3 object tagging prefix.

## Risks and edge cases
Because the constant is private and this file is only three lines, drift is possible if other packages use a separate constant such as `s3_constants.AmzObjectTagging`. A future cleanup should avoid duplicate tag-prefix definitions or ensure all prefixes remain identical.

## Test signals
There are no direct tests for this file. Tag behavior is indirectly tested where lifecycle filtering and router `extractTags` are exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/tags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/version_time.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/version_time.go

## Purpose
This file compares SeaweedFS S3 version IDs by recency, duplicating version ID timestamp logic inside `s3lifecycle` to avoid an import cycle with `s3api`.

## Important APIs and functions
`CompareVersionIds(a, b string) int` returns negative when `a` is newer, positive when `b` is newer, and zero when equal. `"null"` sorts last. `isNewFormatVersionId` classifies 16-character hex timestamp prefixes greater than `versionIdFormatThreshold` as new inverted-timestamp format. `getVersionTimestamp` extracts comparable timestamps, inverting new-format prefixes with max int64 minus parsed value and returning raw old-format values otherwise.

## Control flow and state behavior
Comparison first handles equality and nulls. When both IDs share the same format, new-format IDs sort lexicographically smaller as newer, while old-format IDs sort lexicographically larger as newer. Mixed-format IDs compare derived timestamps. Malformed or short IDs are treated as old/malformed with timestamp zero where needed. There is no persistence.

## Dependencies and integration points
The only dependency is `strconv`. The router uses this comparator as a tiebreaker when version entries share mtime resolution during pointer-transition expansion and bootstrap-like ranking.

## Risks and edge cases
The logic must remain in sync with `s3api_version_id.go`; drift can invert lifecycle retention ranks. Malformed IDs compare as old-format/timestamp zero, which is safe from panics but may produce arbitrary ordering. The threshold boundary is strict greater-than.

## Test signals
`version_time_test.go` covers equality, null sorting, both new-format and old-format ordering, mixed-format timestamp comparisons, equal mixed timestamps, malformed/short IDs, threshold boundaries, and timestamp extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/version_time.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/version_time_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/version_time_test.go

## Purpose
This file tests version ID recency comparison used by lifecycle version ranking.

## Important APIs and helpers
Tests call `CompareVersionIds`, `isNewFormatVersionId`, and `getVersionTimestamp`. Constants define representative new-format and old-format 16-character hex prefixes. `uintToHex16` builds padded hex strings for synthesized equal-timestamp mixed-format cases.

## Control flow and state behavior under test
The suite asserts equality returns zero, `"null"` sorts older than real version IDs, smaller new-format prefixes are newer because timestamps are inverted, larger old-format prefixes are newer because timestamps are raw, and mixed old/new formats compare derived timestamps. It constructs a mixed-format equal timestamp pair and verifies comparison returns zero. It also pins rejection of too-short, null, and non-hex IDs, strict threshold behavior, zero timestamp on malformed inputs, raw old-format extraction, inverted new-format extraction, and ignored trailing suffixes after the first 16 hex characters.

## Dependencies and integration points
The tests use testify assertions and protect router ranking logic in `router.go`.

## Risks and gaps
These are unit tests against the duplicated lifecycle implementation. They do not automatically compare against the source implementation in `s3api_version_id.go`, so future drift between packages could still occur unless both suites are updated.

## Test signals
The suite is comprehensive for documented branches and directly guards lifecycle retention ordering for same-second version mtimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/version_time_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/filer_ops.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/filer_ops.go

## Purpose
This file centralizes low-level filer operations used by the S3 Tables handler to create/delete directories and manipulate extended attributes that hold table bucket, namespace, table, policy, metadata, and tag state.

## Important APIs and functions
`ErrAttributeNotFound` distinguishes missing extended attributes from missing entries or transport errors. Methods on `S3TablesHandler` include `createDirectory`, `ensureDirectory`, `deleteEntryIfExists`, `setExtendedAttribute`, `getExtendedAttribute`, `deleteExtendedAttribute`, `deleteDirectory`, and `entryExists`.

## Control flow and state behavior
`createDirectory` splits a path, builds a directory `Entry` with current mtime/crtime and mode `0755 | os.ModeDir`, and calls `filer_pb.CreateEntry`. `ensureDirectory` looks up a path and creates it only on `filer_pb.ErrNotFound`. Extended attribute setters and deleters perform lookup, mutate the entry's `Extended` map, and call `filer_pb.UpdateEntry`. `getExtendedAttribute` wraps missing attributes with `ErrAttributeNotFound`. Recursive deletion uses `DeleteEntry` with data deletion and ignored recursive errors. `entryExists` is a simple lookup boolean.

## Dependencies and integration points
The file depends on `filer_pb` helpers/RPCs and `splitPath` from `utils.go`. Higher-level handlers use these methods to persist metadata under `s3_constants.DefaultBucketsPath` and table object bucket paths.

## Risks and edge cases
Extended-attribute updates are read-modify-write without compare-and-swap, so concurrent tag/policy/metadata mutations can overwrite each other. `deleteEntryIfExists` relies on `DoRemove` behavior despite the name saying it ignores missing errors. Recursive deletion with ignored recursive errors may hide partial cleanup details. Directory creation does not ensure parent directories unless callers do so.

## Test signals
No direct tests in this subset target these helpers, but S3 Tables handler tests elsewhere exercise them through bucket/namespace/table/policy/tag flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/filer_ops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler.go

## Purpose
This file defines the S3 Tables API handler core: constants, handler configuration, operation dispatch, principal extraction, request/response helpers, ARN generation, and tag-reading utility.

## Important APIs and types
Constants define table storage root, default account/region, extended-attribute keys, and a 10 MB request body limit. `S3TablesHandler` stores region, account ID, default-allow flag, trusted flag, and optional IAM authorizer. Setters configure region/account/default allow/trusted mode. `FilerClient` abstracts access to a Seaweed filer client. `HandleRequest` dispatches by `X-Amz-Target` operation suffix to bucket, namespace, table, policy, and tag handlers. Principal helpers include `getAccountID`, `normalizePrincipalID`, and `getIdentityActions`. HTTP helpers include `readRequestBody`, `writeJSON`, and `writeError`. ARN helpers generate bucket/table ARNs. `isAuthError`, `readTags`, and `mapKeys` support downstream handlers.

## Control flow and state behavior
`HandleRequest` requires `X-Amz-Target`, strips any namespace prefix before the last dot, switches to the correct handler, and logs returned errors. `getAccountID` uses reflection to avoid import cycles: it prefers OIDC `sub`, then `preferred_username`, then non-admin account IDs, identity-name context, `x-amz-account-id`, and finally handler default. Admin account IDs are kept only if identity actions include admin permission. Request bodies are bounded with `io.LimitReader` before JSON decode. Responses use AWS JSON content type.

## Dependencies and integration points
This file depends on `s3_constants` context helpers, `filer_pb`, HTTP, JSON, reflection, and permission/IAM helpers in the same package. It is the entry point called by the S3 API server for S3 Tables control-plane operations.

## Risks and edge cases
Principal extraction uses reflection over identity shapes, so field renames or type changes can silently break ownership. `normalizePrincipalID` collapses ARNs to suffixes and warns this is unsafe for future multi-account support. `defaultAllowFor` and IAM/legacy permission interplay live outside this file but are invoked by handlers dispatched here. `HandleRequest` logs errors after handlers may already have written responses.

## Test signals
`handler_identity_test.go` covers the most fragile identity-principal extraction and default-allow decisions. Other S3 Tables tests cover operation-specific flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_bucket_create.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_bucket_create.go

## Purpose
This file implements `CreateTableBucket`, including request validation, authorization, collision checks with existing S3 buckets, metadata persistence, optional tag persistence, and ARN response generation.

## Important APIs and functions
`handleCreateTableBucket` reads `CreateTableBucketRequest`, validates bucket name, derives the principal, chooses IAM or legacy authorization, checks table/object bucket conflicts, creates directory state, writes `ExtendedKeyTableBucket`, `ExtendedKeyMetadata`, and optional `ExtendedKeyTags`, and returns `CreateTableBucketResponse`.

## Control flow and state behavior
The handler validates JSON and name before authorization. IAM mode uses `shouldUseIAM`, identity policy names, and `authorizeIAMAction`; if IAM denies but zero-config default allow applies without explicit identity actions/policies, it falls back to legacy checks. Legacy permission checks use `CheckPermissionWithContext` against the handler/account owner. The existence check first asks the filer for configured bucket root and then looks up the requested name, distinguishing table bucket entries from ordinary S3 bucket entries. Creation ensures the root path exists, creates the bucket directory, marks it as a table bucket, stores JSON metadata with owner principal and creation time, and stores request tags if present.

## Dependencies and integration points
The file integrates with validation/path helpers (`validateBucketName`, `GetTableBucketPath`), filer ops, S3 constants for bucket root, IAM and legacy permission code, and metadata types from `utils.go`.

## Risks and edge cases
The check-then-create sequence is not atomic; concurrent creates can race between lookup and `CreateEntry`. Metadata and marker attributes are written as separate updates, so partial creation can leave a directory without all attributes if later writes fail. Owner selection under legacy default allow may differ from request principal. Collision checks depend on `IsTableBucketEntry` marker correctness.

## Test signals
No test file in this subset targets creation directly. Adjacent S3 Tables tests and permission tests should cover validation/authorization, but this path would benefit from race/partial-failure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_bucket_create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_bucket_get_list_delete.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_bucket_get_list_delete.go

## Purpose
This file implements table-bucket read, list, and delete operations.

## Important APIs and functions
`handleGetTableBucket` fetches metadata and optional bucket policy, authorizes `GetTableBucket`, and returns bucket details. `handleListTableBuckets` paginates table buckets under the tables root, applies prefix and per-bucket visibility filtering, and returns summaries plus continuation token. `handleDeleteTableBucket` validates input, loads metadata/policy, authorizes delete, checks emptiness, and removes both the table object entry and bucket directory.

## Control flow and state behavior
Get parses `tableBucketARN`, derives bucket name, reads `ExtendedKeyMetadata`, optionally reads `ExtendedKeyPolicy`, then authorizes using bucket ARN and metadata owner. List defaults `MaxBuckets` to 100, caps it at 1000, lists from the continuation token with inclusive handling on first page, skips hidden/non-directory/non-table entries, filters prefix, unmarshals metadata, loads policy if present, and filters invisible buckets instead of failing. Delete reads metadata/policy and checks authorization inside one filer-client block, then lists children with limit 10 and treats any non-hidden child as non-empty. Deletion separately removes the table-object bucket path and the table bucket directory, returning failure only if both operations fail.

## Dependencies and integration points
The handlers depend on ARN parsing, path helpers, metadata marker checks, filer list/delete RPCs, permission checks, and extended-attribute metadata/policy format.

## Risks and edge cases
List pagination can return a continuation token after collecting `maxBuckets`, but filtering means the underlying scan may traverse more entries than returned. Delete emptiness ignores hidden entries only; metadata-only or stray entries can block deletion. Delete cleanup can succeed partially, logging one failed removal while returning success. Authorization-denied get/delete responses differ: get returns forbidden while some namespace flows hide resources with not found.

## Test signals
No direct tests in this subset cover these handlers. Behavior should be verified by S3 Tables integration tests, especially list pagination/filtering and delete partial cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_bucket_get_list_delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_identity_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_identity_test.go

## Purpose
This file tests identity-to-principal extraction and default-allow behavior for S3 Tables authorization.

## Important APIs and helpers
`testIdentityAccount` and `testIdentity` mirror the production identity shape accessed by reflection in `getAccountID`. Tests use `httptest.NewRequest`, `s3_constants.SetIdentityInContext`, and `SetIdentityNameInContext`. They call `NewS3TablesHandler`, `getAccountID`, `SetDefaultAllow`, and `defaultAllowFor`.

## Control flow and state behavior under test
The tests assert claim precedence: `sub` beats `preferred_username`, claims beat the default handler account, whitespace claims are ignored, and `sub` is used when username is missing. Fallback behavior covers no identity, identity-name ARN session suffix extraction, ARN colon segment extraction, `x-amz-account-id` header fallback, and direct `Account.Id`. Admin-account safeguards are pinned: a non-admin identity with the shared admin account falls back to identity name, while an identity with admin action keeps the admin account. Default allow applies only to unauthenticated or anonymous requests, not authenticated non-admin identities.

## Dependencies and integration points
The tests depend on S3 constants for context keys, admin/anonymous IDs, and admin action strings. They protect handler authorization ownership fields used by every S3 Tables operation.

## Risks and gaps
The tests mirror reflection field names; they will catch some drift but not all production identity variants. They do not test IAM policy-name extraction or multi-account ARN collisions noted in `normalizePrincipalID`.

## Test signals
The suite is focused and important because incorrect principal derivation can orphan table buckets, overgrant admin ownership, or make default allow apply to authenticated users unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_identity_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_namespace.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_namespace.go

## Purpose
This file implements namespace create/get/list/delete operations within S3 table buckets.

## Important APIs and functions
`handleCreateNamespace`, `handleGetNamespace`, `handleListNamespaces`, and `handleDeleteNamespace` parse requests, validate namespace arrays, use bucket and namespace paths, read/write metadata, consult bucket policies/tags, enforce permissions, and write AWS JSON responses. Namespace metadata is stored in `ExtendedKeyMetadata`.

## Control flow and state behavior
Create validates ARN and namespace, loads bucket metadata and policy/tags, and has a compatibility branch that reconstructs missing bucket metadata for existing table-bucket entries. It authorizes `CreateNamespace`, checks namespace absence by looking for metadata, creates the namespace directory, and writes metadata with bucket owner as owner. Get loads namespace metadata and bucket policy/tags, authorizes `GetNamespace`, and returns not found on access denial to hide resource existence. List validates bucket, loads bucket metadata/policy/tags, authorizes `ListNamespaces`, then paginates bucket children, skipping hidden/non-directory entries, applying prefix, requiring metadata, and matching owner. Delete loads namespace metadata plus bucket policy/tags, authorizes, checks emptiness by listing children and treating metadata-bearing directories or files as children, then recursively deletes the namespace directory.

## Dependencies and integration points
The file depends on path/validation helpers, filer list/extended-attribute methods, bucket policy checks via `CheckPermissionWithContext`, bucket tags via `readTags`, and metadata structs from `utils.go`.

## Risks and edge cases
There are verbose log calls at create time, including an error-level "called" log that may be noisy. Namespace existence checks conflate missing metadata with missing entries except for the create compatibility branch. Create is not atomic across directory creation and metadata write. List pagination uses `maxNamespaces*2` without an explicit cap like bucket listing. Delete emptiness intentionally ignores empty directories without metadata, which may surprise callers if stray directories contain hidden state.

## Test signals
No direct namespace tests are included in this subset. Coverage should come from broader S3 Tables operation tests; important missing areas are metadata reconstruction, permission-hiding behavior, and delete emptiness semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_namespace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_policy.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_policy.go

## Purpose
This file implements table-bucket policies, table policies, and resource tag operations for S3 Tables resources.

## Important APIs and functions
`extractResourceOwnerAndBucket` derives owner and bucket name from stored metadata and resource path. Bucket policy handlers are `handlePutTableBucketPolicy`, `handleGetTableBucketPolicy`, and `handleDeleteTableBucketPolicy`. Table policy handlers are `handlePutTablePolicy`, `handleGetTablePolicy`, and `handleDeleteTablePolicy`. Tag handlers are `handleTagResource`, `handleListTagsForResource`, and `handleUntagResource`. `resolveResourcePath` maps bucket/table ARNs to filer paths and the tag extended attribute key.

## Control flow and state behavior
Policy put handlers validate required ARN/name/policy fields, parse bucket/table identity, load metadata, authorize against owner and existing bucket policy where applicable, then store policy bytes under `ExtendedKeyPolicy`. Get handlers load metadata and policy, distinguish missing resource from missing policy, authorize, and return policy text. Delete handlers load metadata and current bucket policy, authorize, and remove `ExtendedKeyPolicy`, treating missing policy as non-fatal in delete paths.

Tagging resolves the resource ARN, reads metadata for owner and bucket, optionally reads bucket policy and bucket tags for context, reads existing resource tags, authorizes with request tag keys/resource tags, merges or deletes tags in-memory, and writes the updated JSON map under `ExtendedKeyTags`. Listing tags returns an empty map when the tag attribute is absent.

## Dependencies and integration points
The file depends on ARN parsing, path helpers, metadata structs, filer extended-attribute helpers, `CheckPermissionWithContext`, `PolicyContext`, and resource tag/policy request types. It shares authorization context with bucket and namespace handlers.

## Risks and edge cases
Policy JSON is accepted as an opaque string here; validation is likely delegated to permission evaluation or omitted. Tag updates are read-modify-write without CAS, so concurrent tag changes can be lost. `extractResourceOwnerAndBucket` derives bucket name from path component position, coupling it to `GetTableBucketPath`/`GetTablePath`. Permission for table policies uses bucket policy but not table policy itself before overwrite/delete. Deleting absent policy returns success, which is idempotent but may hide client mistakes.

## Test signals
No direct tests in this subset cover policy/tag handlers. Permission tests elsewhere likely exercise `CheckPermissionWithContext`; handler-level tests should verify missing-policy status codes, tag merge/delete concurrency expectations, and ARN resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_policy.go -->
