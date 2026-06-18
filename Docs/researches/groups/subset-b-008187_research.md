# subset-b-008187 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication.go -->
# sources/object-store/minio/cmd/bucket-replication.go

## Purpose
This file is MinIO server-side bucket replication's central runtime implementation. It decides whether object writes, deletes, metadata updates, heal scans, existing-object resyncs, and active-active proxy reads should be replicated; performs the replication to remote bucket targets; tracks per-target status; and persists retry/resync state. It sits between bucket metadata (`globalBucketMetadataSys`), target clients (`globalBucketTargetSys`), the object layer, replication config/rule evaluation from `internal/bucket/replication`, MinIO admin structures, and replication metrics.

## Important APIs, types, and functions
Key entry points include `getReplicationConfig`, `validateReplicationDestination`, `mustReplicate`, `checkReplicateDelete`, `scheduleReplication`, `scheduleReplicationDelete`, `QueueReplicationHeal`, `getReplicationDiff`, proxy helpers for active-active setups, and `initBackgroundReplication`. `replicateObject` and `replicateDelete` are the high-level worker operations; `ReplicateObjectInfo.replicateObject`, `ReplicateObjectInfo.replicateAll`, `replicateDeleteToTarget`, and `replicateObjectWithMultipart` do target-specific data movement. `ReplicationPool` owns normal workers, large-object workers, MRF workers, resync state, and retry persistence channels. `replicationConfig`, `ResyncDecision`, and `resyncTarget` bridge bucket rule evaluation with reset/existing-object replication decisions.

Constants define internal metadata keys such as `replication-status`, `replication-timestamp`, `replica-status`, `replication-reset`, object-lock timestamp keys, and the SSE-C checksum header. `mustReplicateOptions`, `DeletedObjectReplicationInfo`, `proxyResult`, `replicationPoolOpts`, and `validateReplicationDestinationOptions` carry decision and execution context. The file also defines audit event names like `ReplicateQueued`, `ReplicateExisting`, `ReplicateMRF`, and API names used for internal audit logging.

## Control flow
Normal PUT/metadata paths call `mustReplicate`, which rejects uninitialized object layers, versioning-excluded prefixes, incoming replication requests, and already-replica objects except metadata replication. It loads bucket replication config, builds `replication.ObjectOpts`, filters target ARNs, asks the replication config whether each target should receive the object, and records synchronous mode from the `TargetClient`.

For deletes, `checkReplicateDelete` evaluates versioning, delete markers, version purge status, target status, and replication rules. `scheduleReplication` converts `ObjectInfo` into `ReplicateObjectInfo`, then either calls `replicateObject` inline for synchronous targets or queues it through `ReplicationPool`. `scheduleReplicationDelete` queues a `DeletedObjectReplicationInfo` and immediately marks target stats as pending.

`replicateObject` obtains current replication config, locks `"/[replicate]/"+object` through the object layer namespace lock, fans out target work concurrently, merges target results, updates source object metadata with per-target status and timestamps using `PutObjectMetadata`, updates metrics, emits completion/failure events, and saves failures into MRF. The target-specific fast path (`ReplicateObjectInfo.replicateObject`) always sends data; the heal/resync path (`replicateAll`) first `StatObject`s the target and chooses `replicateNone`, `replicateMetadata`, or `replicateAll` via `getReplicationAction`. Full copies use `putReplicationOpts` and either `minio.Core.PutObject` or `replicateObjectWithMultipart`; metadata-only copies use remote `CopyObject`.

`replicateDelete` follows the same pattern for delete markers and version purges: parse the serialized replicate decision, namespace-lock the object, fan out `replicateDeleteToTarget`, compute aggregate replication/purge status, update stats, save failures into MRF, and update local delete replication state through `DeleteObject`. `replicateDeleteToTarget` handles already-completed markers, target offline state, readiness checks via target `StatObject`, and remote `RemoveObject` with internal replication headers.

The resync path starts with `replicationConfig.Resync`/`resync`, where reset IDs and reset-before timestamps decide whether an object target needs re-replication. `replicationResyncer.start` persists pending status, stores it in memory, and starts `resyncBucket`. `resyncBucket` walks all object versions, filters with `getHealReplicateObjectInfo`, feeds per-object workers by hash, replicates objects or deletes, probes target state, emits trace events, and increments per-target resync stats.

Active-active proxy helpers (`getProxyTargets`, `proxyHeadToRepTarget`, `proxyGetToReplicationTarget`, `proxyTaggingToRepTarget`, `proxyGetTaggingToRepTarget`) let a node that does not yet have an object fetch HEAD/GET/tagging results from replication targets, while avoiding loops using proxy request headers and `disableProxy`.

## State and persistence behavior
The file mutates object metadata by adding reserved replication status, timestamp, reset, delete replication, and object-lock/tagging timestamp fields. Remote replication writes use minio-go internal options to preserve version IDs, ETags, source modtimes, replication status, and replication request markers.

`ReplicationPool` stores bounded in-memory queues for normal, large-object, MRF replica, and MRF save work. Worker counts resize dynamically in auto mode and use deterministic hashing so the same bucket/object tends to land on the same worker. MRF state is persisted as msgp with a 4-byte format/version header under `.minio.sys/buckets/.replication/mrf/<node>.bin` through local drives. Resync metadata is persisted as msgp with a header under the bucket metadata replication directory as `resync.bin`. On restart or leader acquisition, `loadResync` reloads bucket resync state and resumes failed/started/pending resyncs. The pool also periodically persists resync status and periodically reloads MRF entries to queue healing.

## Dependencies and integration points
Major dependencies include `globalBucketTargetSys` for target clients and liveness, `globalBucketVersioningSys` for prefix-aware versioning exclusions, `globalBucketObjectLockSys` for object-lock destination checks, `globalBucketMonitor` for bandwidth throttling, `globalReplicationStats` for queue and transfer metrics, `globalSiteResyncMetrics`, `globalTrace`, `globalLeaderLock`, and object-layer APIs such as `GetObjectNInfo`, `PutObjectMetadata`, `DeleteObject`, `Walk`, namespace locks, and drive I/O. It integrates heavily with `minio-go` client/core APIs, `madmin` target/config structures, `internal/bucket/replication`, `internal/crypto`, `internal/hash`, `internal/event`, and generated msgp types for MRF/resync payloads.

## Risks and edge cases
Replication correctness depends on carefully preserving object metadata, object-lock timestamps, encryption mode, checksums, part sizes, and version IDs. Small mistakes can cause duplicate versions, missed metadata, or failed legal-hold/retention propagation. Queue overflow falls back to MRF, but `mrfRetryLimit`, `mrfMaxEntries`, full save channels, or local-drive write failures can drop or delay retry records. `replicateObjectWithMultipart` must abort failed remote uploads and handle SSE-C actual/encrypted sizes correctly. Resync cancellation uses a shared channel, so concurrent resyncs need careful reasoning. Active-active proxying must avoid loops and stale target reads. Some status updates intentionally treat `PreconditionFailed` as success/no-op, which is safe only if target-side version semantics are correct.

## Test signals
This file is directly tested by `bucket-replication_test.go`, especially `replicationConfig.Resync` and `replicationConfig.resync` around existing-object replication and reset IDs. Generated msgp tests indirectly exercise persisted stat structures used by the pool. Much of the network, queue, MRF, proxy, delete, object-lock, checksum, and multipart behavior relies on broader MinIO integration tests and runtime paths rather than focused unit coverage in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication_test.go -->
# sources/object-store/minio/cmd/bucket-replication_test.go

## Purpose
This test file validates the decision logic for replication resync, especially existing-object replication and reset behavior. It focuses on pure state transitions in `replicationConfig.Resync` and the lower-level `replicationConfig.resync` wrapper rather than performing live object-layer or remote-target replication.

## Important APIs, types, and functions
The file defines a baseline `configs` slice containing one enabled replication rule with delete marker replication, delete replication, existing object replication, and replica modifications enabled. `replicationConfigTests` feeds `TestReplicationResync`, which calls `replicationConfig.Resync(ctx, info, dsc, tgtStatuses)`. `replicationConfigTests2` feeds `TestReplicationResyncwrapper`, which calls `replicationConfig.resync(info, dsc, tgtStatuses)` directly with explicit remote target metadata.

The fixture types are MinIO production types: `ObjectInfo`, `replicationConfig`, `ReplicateDecision`, `replicateTargetDecision`, `madmin.BucketTargets`, `madmin.BucketTarget`, and replication status constants from `internal/bucket/replication`.

## Control flow
`TestReplicationResync` loops over high-level cases where config may be nil, existing object replication may be enabled, versioning may be absent/suspended, and object replication status may be completed. It checks only the boolean `ResyncDecision.mustResync()` result.

`TestReplicationResyncwrapper` exercises the lower-level target overlay. Cases cover pending, failed, unset, and completed replication statuses; reset-in-progress with old reset metadata; reset ID changes; reset completion; and object `ModTime` relative to `ResetBeforeDate`. Each case constructs target ARN `arn1`, a target decision map, optional reset metadata in `UserDefined`, and expected resync eligibility.

## State and persistence behavior
The tests are table-driven and in-memory. They do not persist resync metadata or create MRF files. They model persisted state only through `ObjectInfo.UserDefined[xhttp.MinIOReplicationResetStatus]`, `ReplicationStatusInternal`, and remote target `ResetID`/`ResetBeforeDate` fields.

## Dependencies and integration points
The tests depend on the replication rule engine enough to call `Resync`, but most cases bypass full rule evaluation by calling `resync` with a prepared `ReplicateDecision`. They use `UTCNow`, `nullVersionID`, `xhttp.MinIOReplicationResetStatus`, and `madmin.BucketTargets` to represent the same metadata shapes produced by bucket replication code and admin target configuration.

## Risks and gaps
Coverage is narrow and valuable: it guards the reset/existing-object decision matrix. It does not test remote client behavior, queue overflow, MRF persistence, multipart replication, delete replication execution, active-active proxying, or actual object metadata mutation. Some cases use current time, which is acceptable for coarse day/month offsets but still makes the table less deterministic than fixed timestamps. The tests also assume a single target ARN and do not cover multi-target mixed reset states.

## Test signals
The strongest signal is that pending/failed/unset statuses and changed reset IDs produce `mustResync == true`, while completed objects without an active/new reset do not. The wrapper tests confirm backward-compatible reset metadata (`xhttp.MinIOReplicationResetStatus`) remains part of the decision logic.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-stats.go -->
# sources/object-store/minio/cmd/bucket-stats.go

## Purpose
This file defines bucket-level replication statistics, queue summaries, transfer-rate summaries, and rolling replication latency/count windows. These structures back MinIO's replication monitoring and admin responses, and they are serialized by the generated msgp code in `bucket-stats_gen.go`.

## Important APIs, types, and functions
`ReplicationLatency` wraps `LastMinuteHistogram` for upload latency by object size class and exposes `merge`, `getUploadLatency`, and `update`. `ReplicationLastMinute` and `ReplicationLastHour` track short rolling counters with `addsize`, `getTotal`, `merge`, and `forwardTo`.

`BucketStatsMap` is a timestamped map of bucket names to `BucketStats`. `BucketStats` combines uptime, current replication stats, queue stats, and proxy stats. `BucketReplicationStats` is the bucket aggregate, containing per-target `Stats`, completed replica totals, failed timed stats, queue state, and deprecated pending/failed fields kept for compatibility. `BucketReplicationStat` is the per-target record with replicated/replica size and count, failure metrics, latency, bandwidth limits, current bandwidth, and large/small transfer-rate trackers.

`RMetricName` enumerates `Large`, `Small`, and `Total`. `ReplQNodeStats` packages node name, uptime, active worker stats, node and target transfer summaries, queue stats, and MRF stats. `ReplicationStats.getNodeQueueStats` and `getNodeQueueStatsSummary` build per-bucket and site-wide queue/transfer snapshots. `ReplicationQueueStats` wraps node summaries plus uptime.

## Control flow
Rolling metrics are updated incrementally. `ReplicationLastHour.addsize` advances a 60-slot ring by minute and clears stale slots through `forwardTo`; `getTotal` advances to the current minute before summing. `ReplicationLatency.update` adds a duration into a histogram keyed by object size. `BucketReplicationStats.Clone` shallow-copies scalar fields, deep-copies the target map, clones transfer trackers, and attempts to copy error-count maps.

Queue summaries read `ReplicationStats.Cache` under an `RLock`, use `qCache` for queue counters, and combine `XferStats` for large/small/total bandwidth. Per-target summaries are created first, then node-level averages and peaks are derived. The site summary merges large and small transfer stats across buckets and exposes a total.

## State and persistence behavior
The file itself holds no global state, but the types are mutable and are stored in `ReplicationStats.Cache`, qCache, and MRF counters elsewhere. Most fields are exported and have JSON/msgp tags, making them part of admin API and persisted/binary serialization compatibility. Deprecated pending/failed fields remain in structures and msgp schema, so removing or changing them would affect old clients or stored records.

## Dependencies and integration points
The code depends on `madmin` for timed error stats, active worker and queue/MRF structures defined elsewhere in `cmd`, `XferStats`, `RTimedMetrics`, `InQueueMetric`, `ProxyMetric`, `LastMinuteHistogram`, `lastMinuteLatency`, and global symbols like `globalLocalNodeName`, `globalBootTime`, and `globalReplicationStats`. The `//go:generate msgp -file $GOFILE` directive ties this file directly to `bucket-stats_gen.go` and `bucket-stats_gen_test.go`.

## Risks and edge cases
Compatibility risk is high because field names and msgp keys are wire/persistence contracts. The ring-window logic depends on minute timestamps and must correctly clear stale slots after long idle periods. Transfer summary averaging divides by a target count only when large or small peaks exist; consumers should expect missing map entries when there has been no traffic. `BucketReplicationStats.Clone` appears intended to deep-copy `Failed.ErrCounts`, but the `if s.Failed.ErrCounts == nil` condition means it only copies when the destination map is nil, which deserves scrutiny if `TimedErrStats` map aliasing matters.

## Test signals
Serialization tests in `bucket-stats_gen_test.go` cover msgp marshal/unmarshal, stream encode/decode, skip, and benchmark paths for all exported msgp-enabled types. There are no focused tests here for rolling-window math, transfer-rate aggregation, clone aliasing, or JSON compatibility in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-stats_gen.go -->
# sources/object-store/minio/cmd/bucket-stats_gen.go

## Purpose
This generated file implements tinylib/msgp serialization for the replication statistics types declared in `bucket-stats.go`. It provides fast binary `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` methods used for persistence, RPC/admin payload caching, or internal binary transport of bucket stats.

## Important APIs, types, and functions
The generated methods cover `BucketReplicationStat`, `BucketReplicationStats`, `BucketStats`, `BucketStatsMap`, `RMetricName`, `ReplQNodeStats`, `ReplicationLastHour`, `ReplicationLastMinute`, `ReplicationLatency`, and `ReplicationQueueStats`.

The schema includes per-target stat fields such as `ReplicatedSize`, `ReplicaSize`, `FailStats`, `Failed`, `ReplicatedCount`, nested `Latency.UploadHistogram`, `BandWidthLimitInBytesPerSecond`, `CurrentBandwidthInBytesPerSecond`, short msg keys `lt` and `st` for large/small transfer stats, and deprecated pending/failed counters. Bucket-level schemas include `Stats`, `QStat`, `QueueStats.Nodes`, `ProxyStats`, and `Timestamp`. Node queue stats serialize `NodeName`, `Uptime`, `ActiveWorkers`, `QStats`, and `MRFStats`; notably, the current generated schema does not serialize `XferStats` or `TgtXferStats` despite those fields existing in `ReplQNodeStats`.

## Control flow
Each `DecodeMsg` reads a map header, loops over keys, switches on `msgp.UnsafeString(field)`, decodes known fields, and skips unknown fields. `UnmarshalMsg` mirrors this for byte slices and returns leftover bytes. `EncodeMsg` and `MarshalMsg` write fixed map headers and fields in a generated order. Pointer fields such as `XferRateLrg` and `XferRateSml` explicitly support nil encoding/decoding. Maps and slices allocate or reuse capacity based on encoded lengths. `ReplicationLastHour` enforces an encoded `Totals` array length of exactly 60 and returns `msgp.ArrayError` otherwise. `RMetricName` serializes as a string alias.

## State and persistence behavior
The generated key names and map sizes are a binary compatibility contract. Unknown keys are skipped, giving some forward compatibility, but encode paths write a fixed set of keys. Nil pointer handling preserves absent transfer trackers. The `Msgsize` methods are upper-bound estimates used for preallocation and tests warn if stream encoding exceeds them.

## Dependencies and integration points
This file depends on `github.com/tinylib/msgp/msgp` and on all nested types having compatible msgp methods, including `RTimedMetrics`, `madmin.TimedErrStats`, `LastMinuteHistogram`, `lastMinuteLatency`, `AccElem`, `ActiveWorkerStat`, `InQueueMetric`, `ReplicationMRFStats`, `ProxyMetric`, and `XferStats`. It must be regenerated whenever msgp-relevant fields in `bucket-stats.go` change.

## Risks and edge cases
Manual edits would be overwritten and should not be made. Schema drift is the central risk: adding fields to `bucket-stats.go` without regenerating leaves them unserialized, as visible with some queue transfer summary maps. Fixed map sizes mean old decoders can skip unknown fields only if a regenerated encoder includes them as extra map entries; old generated code will not emit new fields. Array length validation for `ReplicationLastHour` protects structure integrity but rejects malformed/older payloads with a different window size. Nil pointer values for transfer stats must be expected by consumers after decode.

## Test signals
`bucket-stats_gen_test.go` contains generated marshal/unmarshal, encode/decode, skip, and benchmark coverage for all types in this file. Those tests validate round-trip mechanics for zero-value instances and size estimates, but they do not validate semantic preservation of populated stats, map aliasing, backward compatibility with older payloads, or missing-field expectations.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-stats_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-stats_gen_test.go -->
# sources/object-store/minio/cmd/bucket-stats_gen_test.go

## Purpose
This generated test file verifies tinylib/msgp generated serialization methods for replication stats types. It is mechanical coverage for binary round trips, skip behavior, allocation/performance benchmarks, and `Msgsize` estimate sanity.

## Important APIs, types, and functions
For each generated type, the file includes `TestMarshalUnmarshal<Type>`, `TestEncodeDecode<Type>`, and benchmarks for `MarshalMsg`, append-style `MarshalMsg`, `UnmarshalMsg`, `EncodeMsg`, and `DecodeMsg`. The covered types are `BucketReplicationStat`, `BucketReplicationStats`, `BucketStats`, `BucketStatsMap`, `ReplQNodeStats`, `ReplicationLastHour`, `ReplicationLastMinute`, `ReplicationLatency`, and `ReplicationQueueStats`.

## Control flow
Each marshal/unmarshal test creates a zero-value instance, calls `MarshalMsg(nil)`, calls `UnmarshalMsg`, asserts no leftover bytes, then uses `msgp.Skip` to assert the encoded value can be skipped cleanly. Each encode/decode test stream-encodes the zero value into a `bytes.Buffer`, warns if the buffer exceeds `Msgsize`, decodes with `msgp.Decode`, then stream-skips with `msgp.NewReader(&buf).Skip()`. Benchmarks repeatedly execute the same generated paths with `ReportAllocs` and byte counts where relevant.

## State and persistence behavior
The tests are stateless and use only in-memory buffers. They represent the persistence contract indirectly: if generated methods cannot encode, decode, unmarshal, or skip their own zero-value payloads, persisted stats and any binary exchange using these methods would fail.

## Dependencies and integration points
The file depends on `bytes`, `testing`, and `github.com/tinylib/msgp/msgp`. It integrates directly with methods generated in `bucket-stats_gen.go` and with all nested msgp-enabled fields in the replication stats type graph.

## Risks and gaps
Because the tests use zero values, they do not exercise populated maps, slices, nested transfer stats, timed error maps, nil versus non-nil transfer pointers, non-empty timestamps, fixed 60-slot `ReplicationLastHour` payloads with values, unknown-field skip compatibility, or malformed payload rejection. They are useful as generation smoke tests, not semantic tests for replication metrics. As generated code, local manual edits are risky and should be replaced by regeneration from `bucket-stats.go`.

## Test signals
Passing tests indicate basic generated method consistency: self-produced bytes decode without leftovers, skip can traverse payloads, and stream encode/decode works for zero values. Benchmarks provide allocation and throughput baselines for the generated serializers.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-stats_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-targets.go -->
# sources/object-store/minio/cmd/bucket-targets.go

## Purpose
This file implements MinIO's in-memory bucket remote target subsystem. It stores bucket-to-target configuration, constructs minio-go clients for remote targets, validates target reachability and versioning, tracks endpoint health and latency, manages bandwidth limits, and supplies target clients to bucket replication and site replication code.

## Important APIs, types, and functions
`BucketTargetSys` is the main subsystem. It owns `arnRemotesMap` from target ARN to `TargetClient`, `targetsMap` from bucket to configured `madmin.BucketTarget` entries, a health-check map, an anonymous health client, and an ARN error/reload map. `TargetClient` embeds `*minio.Client` and stores target bucket, storage class, sync replication mode, proxy-disable flag, ARN, reset ID, endpoint, and secure flag.

Key methods include `NewBucketTargetSys`, `SetTarget`, `RemoveTarget`, `UpdateAllTargets`, `set`, `ListTargets`, `ListBucketTargets`, `GetRemoteTargetClient`, `GetRemoteBucketTargetByArn`, `getRemoteTargetClient`, `getRemoteARN`, `getRemoteARNForPeer`, `generateARN`, and `parseBucketTargetConfig`. Health behavior is handled by `initHC`, `isOffline`, `markOffline`, `heartBeat`, `reloadHealthCheckers`, and `healthStats`.

## Control flow
Targets are loaded from bucket metadata through `set`/`UpdateAllTargets`, which build remote minio-go clients and update bandwidth throttles. Admin additions use `SetTarget`: validate target type, create a client, confirm remote bucket existence/access, require source and target versioning for replication targets, perform a short liveness probe, reject duplicate target endpoints/ARNs, then update maps and throttling under lock.

Replication paths call `GetRemoteTargetClient`; if a client is absent, a deferred lazy refresh may reload bucket target config from metadata if no refresh is already in progress and the last refresh is old enough. Listing methods merge configured targets with current health stats so admin responses include online state, downtime, last online time, and latency.

The heartbeat goroutine periodically snapshots endpoints, calls anonymous `Alive`, computes offline duration and latency stats, then swaps the health map. A separate reload goroutine periodically rebuilds the health map from current target configs to remove stale endpoints.

## State and persistence behavior
This file primarily manages in-memory state protected by `sync.RWMutex` and separate health/error mutexes. Persistent target configuration lives in bucket metadata and is parsed by `parseBucketTargetConfig`, including optional decryption when metadata indicates SSE-S3 encryption. Bandwidth limits are applied to `globalBucketMonitor`, but the limits originate from persisted target config.

## Dependencies and integration points
The subsystem integrates with `madmin.BucketTarget(s)`, minio-go clients and credentials, `globalRemoteTargetTransport`, `globalBucketVersioningSys`, `globalBucketMetadataSys`, `globalBucketMonitor`, KMS-backed metadata decryption, replication config checks in `RemoveTarget`, and site replication peer lookups. Replication execution in `bucket-replication.go` depends on this file for `TargetClient` lookup, offline checks, sync-mode flags, storage class, proxy settings, reset IDs, and target buckets.

## Risks and edge cases
Map concurrency is guarded but spread across multiple mutexes, so changes must respect lock ownership. Health defaults missing endpoints to online and starts async initialization, which avoids blocking but can briefly allow work to target an unproven endpoint. `markRefreshInProgress` only initializes when the ARN is absent, which deserves scrutiny because existing entries may not be marked as updating. Removing replication targets is disallowed while referenced by active replication config, preventing orphaned rules. Target credentials and decrypted metadata are sensitive. Duplicate endpoint checks happen per target type and may not catch every semantic duplicate if URL forms differ.

## Test signals
No direct test file is included in this subset. Behavior is indirectly exercised by replication destination validation, admin bucket-target APIs, and replication workflows. Areas needing focused tests include lazy refresh, heartbeat state transitions, duplicate detection, encrypted config parsing, and removal protection when replication rules reference a target ARN.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-targets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-versioning-handler.go -->
# sources/object-store/minio/cmd/bucket-versioning-handler.go

## Purpose
This file implements the S3-compatible HTTP handlers for PUT and GET Bucket Versioning. It parses/validates versioning XML, enforces MinIO constraints from site replication, object lock, and bucket replication, persists the bucket versioning config, triggers site-replication metadata hooks, and returns the current config.

## Important APIs, types, and functions
`bucketVersioningConfig` names the persisted metadata object (`versioning.xml`). `maxBucketVersioningConfigSize` caps request XML at 1 MiB. `objectAPIHandlers.PutBucketVersioningHandler` handles writes, and `objectAPIHandlers.GetBucketVersioningHandler` handles reads.

## Control flow
The PUT handler creates request context and audit logging, extracts the bucket from mux vars, verifies the object layer is initialized, authorizes `policy.PutBucketVersioningAction`, parses XML with `versioning.ParseConfig(io.LimitReader(...))`, then enforces three state constraints: site replication must not be enabled if the new config disables versioning; object-lock buckets cannot suspend versioning or exclude prefixes; and buckets with replication config cannot suspend bucket-wide versioning. It marshals the parsed config back to XML, updates bucket metadata via `globalBucketMetadataSys.Update`, base64-encodes the XML, sends a site-replication bucket metadata hook, and returns success headers.

The GET handler checks initialization and `policy.GetBucketVersioningAction`, verifies the bucket exists, loads current config through `globalBucketVersioningSys.Get`, marshals it to XML, and writes an XML success response.

## State and persistence behavior
PUT persists versioning XML in bucket metadata under `versioning.xml`. The returned `updatedAt` timestamp is propagated into the site-replication hook. GET is read-only. The handler does not directly mutate object versions, but versioning state affects object write/delete semantics, replication eligibility, object-lock legality, and prefix-exclusion behavior elsewhere.

## Dependencies and integration points
The handlers integrate with the object layer, bucket metadata system, `versioning` config parser, auth/policy checks, object-lock config, `getReplicationConfig`, `globalSiteReplicationSys`, audit logging, mux routing, API error conversion, and XML response helpers. The PUT handler's constraints protect assumptions used by `bucket-replication.go` and object-lock enforcement.

## Risks and edge cases
The 1 MiB limit constrains parser resource use. Constraint ordering matters for returned API errors. Prefix exclusions are a MinIO extension; object lock forbids them because they can effectively suspend versioning for a prefix. Replication forbids bucket-wide suspension because replication depends on version IDs, but the handler permits prefix exclusions unless object lock blocks them. Site replication requires versioning to remain enabled cluster-wide. Failures in the site replication hook are logged with `replLogIf` after metadata persistence, so hook failure does not roll back local config.

## Test signals
No direct tests are included in this subset. Expected coverage should come from S3 API handler tests, auth tests, object-lock/versioning integration tests, and site-replication metadata tests. Useful edge tests would cover malformed XML, oversized bodies, object-lock prefix exclusions, replication-config suspension rejection, and hook behavior after persistence.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-versioning-handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-versioning.go -->
# sources/object-store/minio/cmd/bucket-versioning.go

## Purpose
This file defines the lightweight bucket versioning subsystem wrapper. It centralizes reads of bucket versioning configuration and exposes convenience predicates used by object, delete, replication, and handler paths.

## Important APIs, types, and functions
`BucketVersioningSys` is stateless. `Enabled(bucket)`, `Suspended(bucket)`, `PrefixEnabled(bucket, prefix)`, and `PrefixSuspended(bucket, prefix)` call `Get` and delegate to `versioning.Versioning` methods. `Get(bucket)` reads versioning config from `globalBucketMetadataSys.GetVersioningConfig`, except for the MinIO metadata bucket and its prefixes, where it returns a default empty XMLNS config. `NewBucketVersioningSys` returns a new wrapper.

## Control flow
All predicate methods load config on demand. If `Get` returns an error, they call `logger.CriticalIf(GlobalContext, err)` and continue to call the method on the returned config pointer. `Get` special-cases `minioMetaBucket` and names with that prefix so internal metadata operations are not driven by ordinary bucket metadata versioning settings.

## State and persistence behavior
The wrapper stores no state and does not cache. Persistence lives in bucket metadata, written by `bucket-versioning-handler.go` and read through `globalBucketMetadataSys`. Prefix-aware versioning is a MinIO extension represented inside the `versioning.Versioning` object.

## Dependencies and integration points
This subsystem is used throughout replication and object handling. In this subset, `bucket-replication.go` uses `PrefixEnabled`, `PrefixSuspended`, and `Suspended` to skip replication for excluded prefixes and to set delete options. `bucket-targets.go` uses `Enabled` to validate replication source buckets. The HTTP handler uses `Get` for GET Bucket Versioning.

## Risks and edge cases
Because predicate methods log critical errors but then dereference `vc`, callers rely on `GetVersioningConfig` returning a non-nil default config even on many errors. Any change to that contract could panic. The metadata-bucket prefix check uses `strings.HasPrefix(bucket, minioMetaBucket)`, which intentionally covers internal metadata names but must not collide with user bucket names unexpectedly. Lack of caching keeps behavior fresh but may make hot paths dependent on metadata-system performance.

## Test signals
No direct tests are included in this subset. Behavior is indirectly covered by versioning handler tests, object API tests, and replication tests that depend on prefix enablement/suspension.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-versioning.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/build-constants.go -->
# sources/object-store/minio/cmd/build-constants.go

## Purpose
This file declares build-time identity constants for the MinIO server binary. The variables are defaults for development builds and are intended to be overridden by linker flags generated by `buildscripts/gen-ldflags.go`.

## Important APIs, types, and functions
The file exports mutable package variables for `GOPATH`, `GOROOT`, `Version`, `ReleaseTag`, `CommitID`, `ShortCommitID`, `CopyrightYear`, `MinioReleaseTagTimeLayout`, `MinioReleaseBaseURL`, `MinioReleaseURL`, `MinioStoreName`, `MinioUAName`, `MinioBannerName`, and `MinioLicense`. It also defines unexported `minioOSARCH` from `runtime.GOOS + "-" + runtime.GOARCH`.

## Control flow
There is no runtime control flow beyond package initialization. `minioOSARCH` is computed at init time, and `MinioReleaseURL` is built from the release base URL, OS/architecture string, and `SlashSeparator` from elsewhere in `cmd`.

## State and persistence behavior
The variables are process-global build metadata. They are not persisted by this file, but their values appear in server banners, user agents, release/update URLs, diagnostics, and target client app info. Because they are variables rather than constants, linker flags can replace them at build time.

## Dependencies and integration points
The only direct import is `runtime`. Other files consume these variables; in this subset, `bucket-targets.go` uses `ReleaseTag` in the replication target client app info. Build scripts are responsible for injecting real version, commit, and copyright metadata.

## Risks and edge cases
Development defaults such as `DEVELOPMENT.GOGET` are safe for local builds but unsuitable for release provenance if linker flags fail. `MinioReleaseURL` depends on `SlashSeparator` being initialized and on the runtime OS/architecture naming matching MinIO's release path conventions. Since these are globals, tests or packages that mutate them can affect later tests unless restored.

## Test signals
No direct tests are included. Validation is usually covered by build/release pipelines and runtime checks that inspect version output, update URLs, or user-agent strings.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/build-constants.go -->
