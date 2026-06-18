# subset-b-008192 research

Work item `subset-b-008192` covers MinIO erasure server pool orchestration, pool decommissioning, pool rebalancing, generated msgp persistence codecs, and their focused tests. Each section below preserves the source path and is intended to be split into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-decom.go -->
# sources/object-store/minio/cmd/erasure-server-pool-decom.go

## Purpose
This file implements erasure server pool decommissioning. It owns the persistent `pool.bin` state model, APIs for starting/canceling/failing/completing pool decommission, background migration of all bucket and metadata objects away from a suspended pool, status reporting, resume after restart, and trace/audit emission. It is tightly coupled to `erasureServerPools` in `erasure-server-pool.go` and reuses the same data movement safeguards used by rebalance.

## Important APIs, Types, and Functions
`PoolDecommissionInfo` is the persisted and admin-visible decommission progress structure. It records start/current/total size, terminal flags, queued and completed buckets, current bucket/object resume markers, and item/byte success/failure counters.

`PoolStatus` stores per-pool identity, command-line string, last update, and optional `PoolDecommissionInfo`. `poolMeta` wraps all `PoolStatus` entries, has the msgp generation marker, and persists to `pool.bin`.

Key `poolMeta` methods include `returnResumablePools`, `Decommission`, `DecommissionComplete`, `DecommissionFailed`, `DecommissionCancel`, `QueueBuckets`, `PendingBuckets`, `TrackCurrentBucketObject`, `CountItem`, `validate`, `load`, `save`, and `updateAfter`. These methods are the durable state machine for decommission.

Key `erasureServerPools` methods include `Init`, `IsDecommissionRunning`, `StartDecommission`, `Decommission`, `doDecommissionInRoutine`, `decommissionInBackground`, `decommissionPool`, `decommissionObject`, `checkAfterDecom`, `Status`, `ReloadPoolMeta`, `DecommissionCancel`, `DecommissionFailed`, and `CompleteDecommission`.

## Control Flow
Startup calls `Init`, which first loads rebalance metadata and starts rebalance if needed, then loads `pool.bin` from the first server pool, validates it against current command-line pools, writes a fresh merged `poolMeta` when pool membership changed, and resumes any non-terminal decommission after a 3 minute stabilization delay on the pool leader.

Starting decommission calls `StartDecommission`, which gathers all user buckets plus `.minio.sys/config` and `.minio.sys/buckets` metadata prefixes, heals metadata buckets, creates missing metadata bucket paths, marks selected pools as decommissioning, queues all buckets, persists `pool.bin` to all pools, and notifies peers to reload pool metadata. `Decommission` then launches serial background routines for the selected pool indices.

`doDecommissionInRoutine` creates a cancelable global context, calls `decommissionInBackground`, and marks the pool failed or complete. A successful pass is followed by `checkAfterDecom`, which scans the source pool to verify no non-ignored versions remain.

`decommissionInBackground` iterates pending buckets. For each bucket it skips already decommissioned entries, runs `decommissionPool`, then removes the bucket from the queue and persists state.

`decommissionPool` creates a bounded worker pool based on `_MINIO_DECOMMISSION_WORKERS` plus one listing worker per erasure set. Each set lists objects with raw quorum-based metadata resolution. Each object entry is expanded into versions sorted oldest first so version stack order can be preserved at the destination. Lifecycle rules can cause expired versions to be skipped or enqueued for expiry. Delete markers are copied as delete markers with versioning forced on. Remote/tiered versions use `DecomTieredObject`. Local data versions are read from the source set and copied through `decommissionObject`.

`decommissionObject` preserves multipart and single-part metadata. Multipart objects are re-created with `NewMultipartUpload`, per-part `PutObjectPart`, original ETags, index callbacks, and `CompleteMultipartUpload`. Single-part objects use `PutObject`. Both paths set `DataMovement` and `SrcPoolIdx` so the destination chooser refuses to write back to the source pool.

After all versions of an object are decommissioned, the source set deletes the exact object prefix with `DeletePrefix`/`DeletePrefixObject`.

## State and Persistence Behavior
`pool.bin` has a 4 byte little-endian header: format and version, then msgp-encoded `poolMeta`. It is saved to every pool, not only the first one, so decommissioning the first pool remains possible.

`poolMeta.dontSave` suppresses writes before initial load is complete. `updateAfter` throttles progress persistence to at most once per duration, used with a 30 second interval in the object loop. Successful bucket completion and terminal status changes save immediately and notify peers.

Terminal states are encoded as booleans inside `PoolDecommissionInfo`: complete, failed, canceled. Resumption excludes complete and canceled pools but resumes failed-in-progress style states that are not terminal complete/canceled.

The pool is considered suspended whenever its `PoolStatus.Decommission` is non-nil, regardless of terminal flags. This means normal write routing avoids the pool after decommission metadata exists and expects completed pools to be removed from the server command line.

## Dependencies and Integration Points
The file depends on bucket lifecycle, versioning, object lock retention, replication config, hash readers, MinIO audit/log/trace systems, raw metadata listing, peer notification reloads, admin pool handlers, and the core object APIs implemented in `erasure-server-pool.go`.

It integrates with `ObjectOptions` fields `DataMovement`, `SrcPoolIdx`, `SkipDecommissioned`, `Versioned`, `DeleteMarker`, `NoAuditLog`, `MTime`, `UserDefined`, and `IndexCB`. It uses `globalNotificationSys.ReloadPoolMeta` to fan out state changes.

## Risks and Edge Cases
Pool suspension is driven by a non-nil decommission field, so cancellation or failure still leaves the pool treated as suspended unless state is otherwise cleared or the code path explicitly handles the terminal condition. This is intentional in the current design but is a high-impact behavior.

`bucketPush` checks `pd.isBucketDecommissioned(b)` while iterating existing queued strings, not the candidate bucket. This preserves de-dup behavior for already queued buckets, but the completed-bucket guard is subtle and worth regression testing.

The source object loop tolerates object/version disappearance and same-source data movement errors as benign races. That prevents false failure during concurrent changes, but it also makes correctness depend on the final `checkAfterDecom` scan.

Lifecycle, object lock, replication, remote-tier, multipart, and delete-marker handling all change migration behavior. These are the highest-risk paths because missing one option can produce wrong version stacks, missing metadata, or duplicate delete markers.

## Test Signals
The direct handwritten test file `erasure-server-pool-decom_test.go` validates `poolMeta.validate` across fresh setup, pool additions/removals, reordered pools, completed decommission states, and pending decommission states. Generated msgp tests cover zero-value codec round trips for decommission state types. There is no direct unit test here for full object migration, lifecycle filtering, remote-tier movement, cancel races, or `checkAfterDecom`; those likely rely on broader integration coverage.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-decom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-decom_gen.go -->
# sources/object-store/minio/cmd/erasure-server-pool-decom_gen.go

## Purpose
This generated file supplies tinylib/msgp encoders, decoders, marshalers, unmarshalers, and size estimators for decommission persistence and status types from `erasure-server-pool-decom.go`. It is the serialization layer used when `pool.bin` is read and written.

## Important APIs, Types, and Functions
The generated methods cover `PoolDecommissionInfo`, `PoolStatus`, `decomError`, `poolMeta`, and `poolSpaceInfo`. For each type, the generated surface is `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`.

`PoolDecommissionInfo` encodes a 16-field map using compact msg keys: `st`, `ss`, `ts`, `cs`, `cmp`, `fl`, `cnl`, `bkts`, `dbkts`, `bkt`, `pfx`, `obj`, `id`, `idf`, `bd`, and `bf`.

`PoolStatus` encodes `id`, `cl`, `lu`, and `dec`; the `dec` field supports nil and lazily allocates `PoolDecommissionInfo` on decode.

`poolMeta` encodes `v` and `pls`. `poolSpaceInfo` uses exported field names `Free`, `Total`, and `Used` because its source fields do not define compact msg tags.

## Control Flow
Decode paths read a map header, loop over keys, switch on `msgp.UnsafeString(field)`, decode known fields, and skip unknown fields. Array fields reuse capacity when possible and allocate when the incoming array is larger. Nested structures delegate to their own generated decode methods.

Encode and marshal paths write fixed map headers and fields in deterministic order. `MarshalMsg` grows the supplied byte slice with `msgp.Require` using `Msgsize` as an upper-bound estimate.

Unmarshal byte-slice paths mirror streaming decode, returning the unused suffix in `o`. This is important for tests that assert no trailing bytes remain after a full decode.

## State and Persistence Behavior
This file does not choose when state is persisted; it defines the binary body that `poolMeta.save` stores after the 4 byte `pool.bin` header. Unknown fields are skipped, which gives some forward compatibility for additive schema changes. Missing fields decode to Go zero values.

Nil handling is significant for `PoolStatus.Decommission`: nil means no decommission state and therefore a pool is not suspended by `poolMeta.IsSuspended`; non-nil means decommission state exists.

## Dependencies and Integration Points
The only direct external dependency is `github.com/tinylib/msgp/msgp`. Runtime integration is through `poolMeta.load` and `poolMeta.save` in the source file, and through generated tests in `erasure-server-pool-decom_gen_test.go`.

## Risks and Edge Cases
Because this is generated code, manual edits would be overwritten and should not be made. Schema key changes in the source struct tags would break compatibility with existing `pool.bin` unless migration handling is added.

The generated code reuses slice capacity. If a value is reused to decode a shorter array, the visible slice length is correct, but callers must not retain stale backing-array references from earlier decodes.

Zero-value decoding is well covered by generated tests, but populated state with queued buckets, nested decommission info, and non-empty strings is not directly asserted in the generated test file.

## Test Signals
`erasure-server-pool-decom_gen_test.go` verifies marshal/unmarshal, reader/writer encode/decode, skip behavior, and allocation benchmarks for every generated type. It is a codec smoke test rather than a semantic persistence test.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-decom_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-decom_gen_test.go -->
# sources/object-store/minio/cmd/erasure-server-pool-decom_gen_test.go

## Purpose
This generated test file verifies tinylib/msgp serialization scaffolding for decommission-related types. It also provides benchmarks for marshal, append-style marshal, unmarshal, streaming encode, and streaming decode.

## Important APIs, Types, and Functions
The file tests `PoolDecommissionInfo`, `PoolStatus`, `decomError`, `poolMeta`, and `poolSpaceInfo`. Each type has the same generated pattern: `TestMarshalUnmarshal...`, `BenchmarkMarshalMsg...`, `BenchmarkAppendMsg...`, `BenchmarkUnmarshal...`, `TestEncodeDecode...`, `BenchmarkEncode...`, and `BenchmarkDecode...`.

The tests use `bytes.Buffer`, `testing`, and `github.com/tinylib/msgp/msgp`. Benchmarks use `b.ReportAllocs`, `b.SetBytes`, `msgp.Nowhere`, and `msgp.NewEndlessReader`.

## Control Flow
Marshal/unmarshal tests create a zero-value instance, call `MarshalMsg(nil)`, call `UnmarshalMsg`, fail if an error occurs, and assert that no bytes are left over. They then call `msgp.Skip` on the encoded bytes and again assert full consumption.

Encode/decode tests encode a zero value to a buffer, compare the encoded length to `Msgsize` only as a warning, decode into a new zero value, and verify reader skip on the encoded buffer.

Benchmarks repeatedly call the generated codec methods against zero-value instances and pre-encoded buffers.

## State and Persistence Behavior
The tests exercise only in-memory serialization. They do not create `pool.bin`, do not validate the 4 byte `pool.bin` header, and do not verify compatibility with historical persisted data. Their main persistence signal is that the current generated msgp body is syntactically self-consistent.

## Dependencies and Integration Points
These tests integrate with the generated code in `erasure-server-pool-decom_gen.go`; they do not call the handwritten decommission state machine. They are normally regenerated by msgp along with the codec file.

## Risks and Edge Cases
All tested values are zero values. That leaves untested populated queued bucket arrays, decommissioned bucket arrays, non-nil nested `PoolStatus.Decommission`, non-empty `CmdLine`, non-zero timestamps, and non-zero counters. Those are exactly the fields used for decommission resume and progress reporting.

The tests log inaccurate `Msgsize` only as a warning, so a size-estimation regression that remains an upper-bound in practice may not fail. If `Msgsize` underestimates badly enough to break `msgp.Require`, the generated code paths would likely fail elsewhere.

## Test Signals
The file is useful as a generation sanity check. Semantic coverage for `poolMeta.validate` lives in `erasure-server-pool-decom_test.go`; semantic coverage for migration behavior is not present in this file.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-decom_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-decom_test.go -->
# sources/object-store/minio/cmd/erasure-server-pool-decom_test.go

## Purpose
This handwritten test file exercises decommission pool metadata validation. It builds temporary two-pool erasure setups and checks whether `poolMeta.validate` asks for metadata updates under different pool membership and decommission-state scenarios.

## Important APIs, Types, and Functions
`prepareErasurePools` creates 32 temporary disks, splits them into two 16-drive endpoint pools, initializes an object layer, and returns the object layer plus directories for cleanup.

`TestPoolMetaValidate` extracts baseline `poolMeta` and `serverPools`, creates a second independent object layer to represent changed pool command lines, builds reduced and reordered pool lists, creates variants where pool 0 has completed or pending decommission, and runs table-driven assertions against `poolMeta.validate`.

## Control Flow
The test creates one initial erasure-pool object layer, defers disk cleanup, then creates a second object layer to simulate a new pool layout. It builds `nmeta1` with completed decommission on pool 0 and `nmeta2` with non-completed decommission on pool 0.

The table covers unchanged layout, changed pool identity, reduced pool count, order change, completed pool still present, pending decommission still present, pending pool removed, completed pool removed, fresh empty metadata, and order change with pending decommission. Each subtest calls `validate` and checks `update` plus error presence.

## State and Persistence Behavior
The test does not write or reload `pool.bin` directly, but it exercises the decision that controls whether a loaded `poolMeta` is accepted as-is or rewritten by `newPoolMeta`. It also verifies that completed decommission state does not force an update while the completed pool remains present; production code logs that the pool should be removed from the command line.

## Dependencies and Integration Points
The test depends on local disk helpers `getRandomDisks`, `mustGetPoolEndpoints`, `initObjectLayer`, `removeRoots`, and on concrete `erasureServerPools` internals. It is closer to an integration test than a pure unit test because it initializes real erasure pool structures.

## Risks and Edge Cases
The table names include some "Invalid" cases where `expectedErr` is still false. This reflects current `validate` behavior: it signals metadata rewrite needs through `update`, and logs completed-pool presence, but it does not reject these layouts with errors.

The test does not validate `poolMeta.load`, `poolMeta.save`, decommission queue behavior, resume markers, object migration, final verification, or cancel/fail/complete API behavior. It also does not assert logged warnings for completed pools left in the command line.

## Test Signals
The strongest signal is that pool membership additions/removals/reordering and decommission state interact without hard errors and produce expected rewrite decisions. This supports startup reconciliation in `Init`, but leaves the migration data path largely untested at this file level.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-decom_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-rebalance.go -->
# sources/object-store/minio/cmd/erasure-server-pool-rebalance.go

## Purpose
This file implements pool rebalance, which moves data out of pools that have less free-space ratio than the deployment-wide goal. It owns `rebalance.bin` state, per-pool stats, start/stop/resume behavior, bucket/object migration, final status updates, audit logging, and trace metrics.

## Important APIs, Types, and Functions
`rebalanceStats` stores initial free/capacity, bucket queues, completed buckets, last bucket/object, object/version/byte counters, a participation flag, and `rebalanceInfo`.

`rebalanceInfo` records start/end time and `rebalStatus`; statuses are `rebalNone`, `rebalStarted`, `rebalCompleted`, `rebalStopped`, and `rebalFailed`.

`rebalanceMeta` stores global stopped time, operation ID, target free-space ratio, and per-pool `rebalanceStats`.

Key methods include `loadRebalanceMeta`, `updateRebalanceStats`, `initRebalanceMeta`, `nextRebalBucket`, `bucketRebalanceDone`, `rebalanceMeta.load/save`, `IsRebalanceStarted`, `IsPoolRebalancing`, `rebalanceBuckets`, `checkIfRebalanceDone`, `listObjectsToRebalance`, `rebalanceBucket`, `saveRebalanceStats`, `rebalanceObject`, `StartRebalance`, and `StopRebalance`.

## Control Flow
`initRebalanceMeta` computes total capacity and free space from `StorageInfo`, stores `PercentFreeGoal`, initializes each pool's stats and bucket queue, and marks pools with below-goal free-space ratio as participating and started. Metadata is saved before `z.rebalMeta` is assigned.

`StartRebalance` exits if no metadata exists or if the operation was stopped. Otherwise it creates a cancelable global context, records the cancel function, snapshots participating started pools, and launches `rebalanceBuckets` only on the leader node for each pool.

`rebalanceBuckets` runs a periodic saver goroutine that writes stats every randomized 5 to 10 seconds and writes terminal status when the worker exits. The main loop fetches the next bucket and calls `rebalanceBucket`; recoverable initialization errors continue, other errors mark the pool failed.

`rebalanceBucket` loads versioning, lifecycle, object lock, and replication config, then starts bounded workers per erasure set. It lists raw object metadata from the source pool, resolves quorum or partial entries, sorts versions oldest first, skips remote tiered versions, applies lifecycle expiry, copies delete markers with `DeleteObject`, copies data versions via `rebalanceObject`, updates stats, and deletes source object versions when all versions are rebalanced.

`checkIfRebalanceDone` stops pool-level work once the current free-space ratio, computed as `(InitFreeSpace + BytesMoved) / InitCapacity`, is within 5 percent of `PercentFreeGoal`.

`StopRebalance` cancels the local context. `saveRebalanceStats` can set `StoppedAt` and writes `rebalance.bin` under a namespace lock.

## State and Persistence Behavior
`rebalance.bin` has a 4 byte little-endian format/version header and msgp-encoded `rebalanceMeta`. It is read and written through the first server pool. `saveRebalanceStats` loads the current persisted state under lock before merging local per-pool stats or stopped time, which reduces overwrite risk between nodes.

`loadRebalanceMeta` tolerates missing config and non-fatal load failures, assigns `z.rebalMeta` on success, and calls `updateRebalanceStats` so a cluster expanded mid-rebalance can add stats entries for new pools.

`StoppedAt` is global operation state; if set, `IsRebalanceStarted` and `IsPoolRebalancing` return false. Per-pool terminal status is stored in each `rebalanceStats.Info`.

## Dependencies and Integration Points
The file depends on lifecycle, object lock, replication, versioning, hash readers, audit logging, trace subscriptions, worker pools, raw metadata listing, shortuuid IDs, peer notification reloads, and the core object APIs in `erasure-server-pool.go`.

It uses `ObjectOptions.DataMovement`, `SrcPoolIdx`, `SkipRebalancing`, `Versioned`, `DeleteMarker`, `NoDecryption`, `NoAuditLog`, `PreserveETag`, `IndexCB`, and `MTime`. Data movement protection is shared with decommission via `errDataMovementSrcDstPoolSame`.

## Risks and Edge Cases
`findIndex` effectively checks whether a requested pool index is in the current stats slice by iterating slice indexes; it does not compare a stored pool identity. This works for append-only expansion but is not robust to arbitrary pool reordering.

Remote/tiered versions are skipped for rebalance, unlike decommission which calls `DecomTieredObject`. That can leave data on the source pool until other mechanisms handle it.

Concurrent object changes are treated leniently: not-found, version-not-found, and same-pool data movement errors can be ignored. Correctness therefore depends on stats, source cleanup, and repeated/listed work rather than strict per-object failure.

`checkIfRebalanceDone` uses moved bytes as an approximation of free space gained. Compression, delete markers, parity math, and concurrent writes can make this an estimate rather than exact disk state.

## Test Signals
Generated codec tests cover zero-value serialization for rebalance types. There is no direct handwritten unit test for rebalance planning, per-bucket migration, stop/resume, goal convergence, remote-tier skipping, or `saveRebalanceStats` locking behavior in the listed files.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-rebalance.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-rebalance_gen.go -->
# sources/object-store/minio/cmd/erasure-server-pool-rebalance_gen.go

## Purpose
This generated file supplies tinylib/msgp serialization code for rebalance state, metric enum values, and per-pool stats. It is the binary body used by `rebalanceMeta.save` and `rebalanceMeta.load` after the `rebalance.bin` header.

## Important APIs, Types, and Functions
Generated methods cover `rebalSaveOpts`, `rebalStatus`, `rebalanceInfo`, `rebalanceMeta`, `rebalanceMetric`, `rebalanceMetrics`, `rebalanceStats`, and `rstats`. Each type gets `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`.

Enum-like types (`rebalSaveOpts`, `rebalStatus`, `rebalanceMetric`) serialize as uint8 values. `rebalanceInfo` uses keys `startTs`, `stopTs`, and `status`. `rebalanceMeta` uses `stopTs`, `id`, `pf`, and `rss`. `rebalanceStats` uses `ifs`, `ic`, `bus`, `rbs`, `bu`, `ob`, `no`, `nv`, `bs`, `par`, and `inf`.

`rebalanceMetrics` encodes as an empty map because it has no fields, but generated code still supports skipping unknown fields on decode.

## Control Flow
Streaming decoders read headers and switch by map key, allocating slices as needed and preserving capacity when possible. Pointer slices such as `PoolStats` and `rstats` support nil elements and lazily allocate `rebalanceStats` values on decode.

Marshalers write deterministic maps or arrays into caller-provided buffers grown with `msgp.Require`. Unknown fields are skipped in both streaming and byte-slice decode paths.

## State and Persistence Behavior
The file defines how operation IDs, stopped time, percent-free goals, bucket queues, completed buckets, counters, participation flags, and pool status are persisted. Missing fields default to zero values, and unknown fields are skipped, allowing additive changes but not semantic migrations.

Nil pointer support in `rebalanceMeta.PoolStats` matters because callers must handle possible nil stats entries defensively. Most handwritten code assumes initialized entries after `initRebalanceMeta` or `updateRebalanceStats`.

## Dependencies and Integration Points
The only direct dependency is `github.com/tinylib/msgp/msgp`. It integrates with `rebalanceMeta.loadWithOpts`, `rebalanceMeta.saveWithOpts`, and the generated test file `erasure-server-pool-rebalance_gen_test.go`.

## Risks and Edge Cases
Manual edits would be overwritten by msgp generation. Any change to msg tags or field types can break compatibility with existing `rebalance.bin` files unless migration logic is added in handwritten load code.

Generated tests use zero values, so populated arrays, nil pointer entries, non-empty bucket queues, and status transitions are not asserted directly. These are core to rebalance resume and progress display.

## Test Signals
The paired generated test file verifies that the generated methods can round-trip and skip zero-value encodings. It does not validate the 4 byte file header, load/save locking, or semantic rebalance behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-rebalance_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-rebalance_gen_test.go -->
# sources/object-store/minio/cmd/erasure-server-pool-rebalance_gen_test.go

## Purpose
This generated test file verifies msgp serialization scaffolding for rebalance-related types and provides codec performance benchmarks.

## Important APIs, Types, and Functions
The file tests `rebalanceInfo`, `rebalanceMeta`, `rebalanceMetrics`, `rebalanceStats`, and `rstats`. It does not include tests for the uint8 enum wrappers visible in the generated codec file.

Each tested type follows the generated pattern of marshal/unmarshal tests, append marshal benchmark, unmarshal benchmark, encode/decode test, encode benchmark, and decode benchmark.

## Control Flow
Tests instantiate zero values, marshal to bytes, unmarshal, assert no trailing bytes, and verify `msgp.Skip` consumes the full encoding. Streaming tests encode to a `bytes.Buffer`, warn if `Msgsize` is smaller than the output, decode into a new zero value, and verify reader skip.

Benchmarks reuse zero values and preencoded buffers to measure allocation and throughput of generated methods.

## State and Persistence Behavior
The tests exercise only msgp bodies. They do not create `rebalance.bin`, do not validate the format/version header, and do not simulate operation state such as started/stopped/completed pools or populated bucket queues.

## Dependencies and Integration Points
The tests depend on `bytes`, `testing`, and `github.com/tinylib/msgp/msgp`. They are generated alongside `erasure-server-pool-rebalance_gen.go` and are primarily a generation sanity check.

## Risks and Edge Cases
Zero-value-only round trips leave major persisted states untested: non-empty `PoolStats`, nil entries inside `PoolStats`, non-empty `Buckets` and `RebalancedBuckets`, non-zero `PercentFreeGoal`, non-empty operation IDs, and non-default `rebalStatus` values.

The test suite treats `Msgsize` inaccuracy as a log warning in streaming tests, so size-estimation drift may not fail unless it breaks actual marshal paths.

## Test Signals
The file confirms syntactic self-consistency of generated rebalance codecs. It provides no behavioral coverage for rebalance selection, migration, stop/resume, save merging, or goal completion.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool-rebalance_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool.go -->
# sources/object-store/minio/cmd/erasure-server-pool.go

## Purpose
This file implements MinIO's multi-pool erasure object layer. It initializes erasure pools, chooses destination pools, routes object and multipart operations, merges listings and scans, handles bucket operations, health and storage info, healing, metadata/tag/tier operations, and delegates decommission and rebalance state checks.

## Important APIs, Types, and Functions
`erasureServerPools` is the central object-layer type. It contains `poolMeta` guarded by `poolMetaMutex`, `rebalanceMeta` guarded by `rebalMu`, deployment identity, distribution algorithm, `serverPools`, decommission cancelers, `S3PeerSys`, and multipart upload cache.

Initialization is handled by `newErasureServerPools`, which validates parity and deployment IDs, waits for erasure formats, creates `erasureSets`, initializes byte pools, global locks, auto-heal, pool metadata, and stale multipart cleanup.

Pool selection and lookup are handled by `getServerPoolsAvailableSpace`, `getAvailablePoolIdx`, `getPoolInfoExistingWithOpts`, `poolsWithObject`, `getPoolIdxExistingWithOpts`, `getPoolIdxNoLock`, and `getPoolIdx`.

Object APIs include `GetObjectNInfo`, `GetObjectInfo`, `PutObject`, `DeleteObject`, `DeleteObjects`, `CopyObject`, listing variants, multipart lifecycle methods, metadata/tag methods, transition/restore, and `DecomTieredObject`.

Operational APIs include `NSScanner`, `Walk`, `HealObjects`, `HealObject`, `Health`, `StorageInfo`, `BackendInfo`, `GetRawData`, and disk lookup helpers.

## Control Flow
Initialization builds all pools from endpoint server pools, enforces consistent deployment ID, populates local-drive maps for non-distributed erasure, creates `poolMeta` with `dontSave`, then repeatedly calls `Init` until backend metadata loads or a non-retriable error occurs. It then initializes the multipart cache and starts a cleanup goroutine.

Writes first try to find an existing object's pool. For new data, `getAvailablePoolIdx` computes weighted available capacity across non-suspended and non-rebalancing pools and randomly chooses a pool proportional to available bytes. Pools above the reserve threshold can be filtered out unless all pools exceed it.

Reads query all pools in multi-pool mode and choose the latest object by modification time, with lowest pool index as a tie-break. `SkipDecommissioned` and `SkipRebalancing` options prevent data-movement callers from reading or writing through pools that should be avoided.

Deletes acquire namespace locks, identify the pool with the latest object, handle delete-marker special cases, optionally delete across all pools with no/read-quorum metadata inconsistencies, and route replication or data movement requests to the correct pool.

Multipart operations preserve upload affinity by searching existing uploads across active pools before creating new uploads. Upload IDs are cached in `mpCache` for prefix-empty multipart listing and cleaned periodically.

Listing and walking merge raw metadata streams across pools and sets. The listing path includes application-specific optimizations for Hadoop/Spark and max-keys=1 prefix probes. `Walk` launches one raw listing channel per set, resolves metadata quorum, merges entries, and emits `ObjectInfo` versions.

Health computes read/write quorum status per pool/set from `StorageInfo`, accounts for maintenance mode and VMware healing behavior, and reports aggregate read/write health.

## State and Persistence Behavior
The file itself owns in-memory coordination state: `poolMeta`, `rebalMeta`, decommission cancelers, rebalance canceler, byte pool cap, local drive map, global object layer assignment, and multipart cache. Durable decommission and rebalance persistence is implemented in the companion files through `pool.bin` and `rebalance.bin`.

`poolMeta` and `rebalMeta` are read on routing paths to avoid suspended or rebalancing pools. This makes persisted admin state directly affect normal S3 operation routing.

Multipart cache entries are local in-memory hints and are removed after configurable stale-upload expiry or when uploads complete/abort. They are not the source of truth for multipart state.

## Dependencies and Integration Points
The file integrates with nearly every object-layer subsystem: storage class parity, endpoint formats, erasure sets, global notification system, bucket metadata, lifecycle evaluation, object lock, tags, namespace locks, S3 peer system, healing, scanner, metrics, admin health endpoints, and decommission/rebalance companion files.

It implements the `ObjectLayer` interface methods used by S3 handlers, admin handlers, health checks, metrics, lifecycle, replication, and site-replication paths.

## Risks and Edge Cases
Multi-pool object lookup is defensive against duplicate objects across pools and serves the latest `ModTime`. That hides some split-brain states but makes clock/order correctness important.

Routing avoids suspended and rebalancing pools for new writes. If all pools are suspended/rebalancing or disk reserve filtering removes all capacity, writes fail with disk full.

Data movement relies on `DataMovement` plus `SrcPoolIdx` to prevent copying back to the same pool. This is critical for both decommission and rebalance.

Several methods loop over all pools and return the first acceptable result. Error precedence can be subtle, especially for delete markers, version-not-found, read quorum, and replication requests.

`CheckAbandonedParts` appears to return inside the first iteration over `errs`, which means it returns the first error value, including nil, without scanning later errors. That may be intentional if first pool is canonical, but it is a risk signal worth review.

## Test Signals
The listed test files do not directly exercise this large object-layer file except through erasure pool setup in `erasure-server-pool-decom_test.go`. Coverage for this file likely comes from broader MinIO object API, healing, listing, multipart, and admin integration tests outside this work item.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-server-pool.go -->
