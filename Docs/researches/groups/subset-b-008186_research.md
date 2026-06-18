# Research: subset-b-008186

Grouped research for MinIO bucket replication handlers, metrics, stats, utilities, generated msgp codecs, and generated/unit tests.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-handlers.go -->
## sources/object-store/minio/cmd/bucket-replication-handlers.go

Purpose: Implements HTTP handlers on `objectAPIHandlers` for bucket replication configuration, replication metrics, replication reset/resync, reset status, and replication credential validation. This is the S3/admin edge for replication control-plane changes and readbacks.

Important APIs: `PutBucketReplicationConfigHandler`, `GetBucketReplicationConfigHandler`, `DeleteBucketReplicationConfigHandler`, `GetBucketReplicationMetricsHandler`, `GetBucketReplicationMetricsV2Handler`, `ResetBucketReplicationStartHandler`, `ResetBucketReplicationStatusHandler`, and `ValidateBucketReplicationCredsHandler`. They depend on `objectAPI.GetBucketInfo`, `checkRequestAuthType`, `globalBucketMetadataSys`, `globalBucketTargetSys`, `globalBucketVersioningSys`, `globalSiteReplicationSys`, `globalReplicationStats`, `globalNotificationSys`, and `globalReplicationPool`.

Control flow: Every handler builds request context, audits through `logger.AuditLog`, extracts `bucket` from mux variables, checks `api.ObjectAPI()`, authorizes with policy actions, and verifies bucket existence before touching replication state. PUT parses XML via `replication.ParseConfig`, validates remote destinations with `validateReplicationDestination`, validates rules with `replicationConfig.Validate`, marshals XML, and writes `bucketReplicationConfig` metadata. GET loads metadata and returns XML. DELETE removes replication metadata, refuses site-replication edits, removes all bucket targets, then deletes `bucketTargetsFile`. Metrics handlers load current clustered bucket stats, merge bandwidth report fields into each ARN stat, and encode either legacy `BucketReplicationStats` or V2 `BucketStats` with uptime. Reset start validates `older-than`, `arn`, and `reset-id`, verifies existing object replication, updates target reset metadata in bucket target config, persists target metadata, starts `globalReplicationPool.Get().resyncer.start`, and returns `ResyncTargetsInfo`. Reset status loads persisted resync metadata and filters by optional ARN. Credential validation checks versioning/object-lock compatibility and performs fake replicated PUT and DELETE operations against each remote target using `minio.Core`.

State and persistence: Persistent changes are made through bucket metadata updates/deletes for replication config and targets. Reset start mutates `BucketTarget` fields `ResetBeforeDate` and `ResetID`, persists them, and triggers resyncer state. Metrics are read from in-memory cluster/node collectors and notification bandwidth reports. Validation creates and deletes a reserved `minioReservedBucket/globalLocalNodeNameHex/deleteme` object on targets as a permission probe.

Dependencies and integration points: Integrates S3 policy actions from `policy`, bucket replication config parsing/validation from `internal/bucket/replication`, object-lock configuration, remote MinIO clients, notification bandwidth reporting, replication pool resync workers, and MinIO error response helpers. Site replication blocks local edits unless the active root credential path is used for PUT; DELETE is fully denied when site replication is enabled.

Risks: Reset date calculation converts a parsed duration to whole days via `int(days/24)`, so sub-day durations collapse to zero days and non-day durations are truncated. Credential validation does real remote calls and relies on `isReplicationPermissionCheck` to distinguish expected policy-denial responses from validation failure. DELETE removes all bucket targets after replication config deletion, which is correct for this API but high blast-radius if authorization or site-replication guards regress. Metrics V1 is deprecated but still shares logic with V2, so stat shape changes can break older clients. Same-target and object-lock validation are critical to avoid unsafe loops or compliance drift.

Test signals: No direct tests in this subset cover these handlers. The strongest nearby signals are utility tests for status/decision behavior and generated codec tests for response/state serialization types. Handler behavior needs integration coverage for auth errors, site-replication denial, remote validation failures, metrics JSON shapes, and resync start/status metadata persistence.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-metrics.go -->
## sources/object-store/minio/cmd/bucket-replication-metrics.go

Purpose: Defines in-memory metric primitives used by bucket and site replication stats: transfer rates, queue depth, active worker samples, MRF counters, simple/exponential moving averages, and replication proxy call counters.

Important APIs/types: `rateMeasurement`, `ActiveWorkerStat`, `QStat`, `InQueueMetric`, `queueCache`, `InQueueStats`, `XferStats`, `ReplicationMRFStats`, `SMA`, `proxyStatsCache`, `replProxyAPI`, and `ProxyMetric`. Constructors and methods include `newRateMeasurement`, `updateExponentialMovingAverage`, `newActiveWorkerStat`, `queueCache.update/getBucketStats/getSiteStats`, `newXferStats`, `XferStats.addSize/merge/Clone`, `newSMA`, `SMA.addSample/simpleMovingAvg`, `proxyStatsCache.inc/getBucketStats/getSiteStats`, and `ProxyMetric.add`.

Control flow: Byte increments accumulate atomically in `rateMeasurement.bytesSinceLastWindow`; a ticker in stats calls `updateExponentialMovingAverage`, which swaps the counter, calculates bytes/sec over the elapsed window, and applies `exponentialMovingAverage(beta=0.1)`. `XferStats.addSize` updates the measurement, samples current rate into a 50-sample `SMA`, updates average/peak, and increments `N`. Queue caches hold current bytes/count and histograms per bucket plus site-wide stats, updating histograms periodically. Proxy stats use a switch over `replProxyAPI` to increment success/failure counters for tagging, head, and get proxy operations.

State and persistence: This file owns only process-local state. Histograms come from `github.com/rcrowley/go-metrics`; queue/proxy/transfer counters are protected by mutexes and atomics. The `//go:generate msgp -file $GOFILE` marker makes several exported structs part of the msgp serialization contract, but runtime metric samples are not persisted here.

Dependencies and integration points: `ActiveWorkerStat.update` reads `globalReplicationPool.Get().ActiveWorkers()`. `ReplicationStats` in `bucket-replication-stats.go` drives queue and moving-average tickers. Generated msgp code serializes `ActiveWorkerStat`, `InQueueMetric`, `InQueueStats`, `ProxyMetric`, `QStat`, `ReplicationMRFStats`, `SMA`, and `XferStats` for peer/stat exchange.

Risks: `updateExponentialMovingAverage` divides by `duration.Seconds()` without checking zero duration; ticker use should avoid zero elapsed time, but direct tests/calls could produce infinities. `XferStats.Clone` intentionally omits `sma`, so clones are snapshots rather than writable metrics. Histogram registration names include bucket names, so repeated bucket churn could register many metrics. Queue `incQ/decQ` callers must be balanced; the cache allows negative current counters if decrements exceed increments. Generated serialization omits private fields such as histograms and live measurement internals, so deserialized structs are metric snapshots unless reinitialized.

Test signals: Generated tests in `bucket-replication-metrics_gen_test.go` cover msgp round-trip and benchmarks for all serializable metric structs. There are no hand-written tests in this subset for moving-average math, queue balancing, proxy increments, or active worker sampling.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-metrics_gen.go -->
## sources/object-store/minio/cmd/bucket-replication-metrics_gen.go

Purpose: Generated `tinylib/msgp` codecs for metric structs declared in `bucket-replication-metrics.go`. It provides binary encode/decode, marshal/unmarshal, and size-estimation methods used when replication metrics are exchanged or persisted through msgp-compatible paths.

Important APIs/types: For `ActiveWorkerStat`, `InQueueMetric`, `InQueueStats`, `ProxyMetric`, `QStat`, `ReplicationMRFStats`, `SMA`, and `XferStats`, the file implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`. Field keys use explicit `msg` tags where present (`cq`, `aq`, `pq`, `cr`, `av`, `p`, `n`, proxy counter abbreviations) and Go field names where no tag exists.

Control flow: Each `DecodeMsg`/`UnmarshalMsg` reads a map header, iterates keys, assigns known fields, and skips unknown fields. Nested structs such as `InQueueMetric` decode embedded `QStat`-shaped maps for current/average/max queue values. `MarshalMsg` preallocates using `Msgsize`, appends a map header and field keys, then appends primitive values. `EncodeMsg` streams the same structure to a `msgp.Writer`.

State and persistence: The generated code serializes only exported/tagged data fields. Runtime-only fields in metrics such as histograms, mutexes, `rateMeasurement`, and `SMA.buf/window/idx/prevSMA/filledBuf` are absent or unexported; this preserves the snapshot contract but does not reconstruct live collectors. `XferStats` serializes `Curr`, `Avg`, `Peak`, and `N`, not the moving-average machinery.

Dependencies and integration points: Depends only on `github.com/tinylib/msgp/msgp` and the metric types from package `cmd`. Regeneration is controlled by `//go:generate msgp -file $GOFILE` in the hand-written metrics file.

Risks: Manual edits would be overwritten and can desynchronize from struct tags. Adding/removing fields in the source structs requires regenerating this file and its tests. Because unknown fields are skipped, forward compatibility is tolerant, but missing live internals after decode can surprise code that treats decoded values as active collectors. Map iteration order is irrelevant for decode but can make binary output order for maps unstable where maps exist in other generated files.

Test signals: `bucket-replication-metrics_gen_test.go` contains round-trip encode/decode tests and benchmarks for every type covered here. It verifies no trailing bytes remain and that `msgp.Skip` can skip encoded values.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-metrics_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-metrics_gen_test.go -->
## sources/object-store/minio/cmd/bucket-replication-metrics_gen_test.go

Purpose: Generated msgp tests and benchmarks for replication metric serialization. It verifies generated codecs for metric structs compile, round-trip, and remain skippable.

Important APIs/tests: For each of `ActiveWorkerStat`, `InQueueMetric`, `InQueueStats`, `ProxyMetric`, `QStat`, `ReplicationMRFStats`, `SMA`, and `XferStats`, the file defines `TestMarshalUnmarshal...`, `TestEncodeDecode...`, and benchmarks for marshal, append, unmarshal, encode, and decode.

Control flow: Each marshal/unmarshal test creates a zero-value instance, marshals to bytes, unmarshals into a new value, checks that no bytes remain, and calls `msgp.Skip` on the encoded payload. Encode/decode tests stream through `msgp.Writer`/`Reader` backed by `bytes.Buffer` and verify skip behavior. Benchmarks reset timers and repeatedly exercise each generated method family.

State and persistence: Tests use zero-value structs, so they validate wire-shape mechanics more than realistic non-zero metric content. They do not persist data outside the test process.

Dependencies and integration points: Uses Go `testing`, `bytes`, and `github.com/tinylib/msgp/msgp`. It is generated from the same msgp toolchain as the codec file and acts as a guard that generated methods match current type definitions.

Risks: Zero-value-only generated tests can miss bugs in non-empty maps, nested non-zero counters, float edge cases, and time-varying snapshots. Because this file is generated, local modifications should not be made manually. Benchmarks provide performance signals but no thresholds.

Test signals: This file itself is the serialization test signal for `bucket-replication-metrics_gen.go`; it complements but does not replace behavioral tests for metric math in `bucket-replication-metrics.go`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-metrics_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-stats.go -->
## sources/object-store/minio/cmd/bucket-replication-stats.go

Purpose: Owns the process-local `ReplicationStats` aggregator and cluster aggregation helpers for bucket and site replication metrics. It connects low-level metric primitives to replication events and API-visible stats.

Important APIs/types: `ReplicationStats`, `replStat`, `NewReplicationStats`, `trackEWMA`, `updateMovingAvg`, `ActiveWorkers`, `collectWorkerMetrics`, `collectQueueMetrics`, `Delete`, `UpdateReplicaStat`, `Update`, `GetAll`, `getSRMetricsForNode`, `Get`, `getAllLatest`, `calculateBucketReplicationStats`, `getLatestReplicationStats`, `incQ`, `decQ`, `incProxy`, and `getProxyStats`.

Control flow: Construction creates a metrics registry, queue/proxy/site caches, active-worker histogram, and 2-second tickers for worker and queue collection. `trackEWMA` updates transfer moving averages until `GlobalContext` ends. `Update` translates a `replicatedTargetInfo` and status transition into a `replStat`, updates site-replication stats for completed/failed data replication, then locks the per-bucket cache and updates target counters, failure stats, latency, and large/small transfer rates. `GetAll` clones local bucket stats and overlays queue stats. Cluster paths call `globalNotificationSys.GetClusterAllBucketStats` or `GetClusterBucketStats`, merge per-node queue/proxy/stat maps, update `mostRecentStats`, and return `BucketStats`.

State and persistence: State is in memory: `Cache`, `srStats`, `qCache`, `pCache`, `mrfStats`, `mostRecentStats`, histograms, and tickers. There is no direct disk persistence. `mostRecentStats` acts as a recent non-empty cache for replication stats. Queue counts are atomically incremented/decremented per bucket and site-wide.

Dependencies and integration points: Depends on replication status/type enums, `go-metrics`, global notification fanout, site replication deployment ID lookup, global boot time, `BucketReplicationStats`/`BucketStats` types elsewhere in `cmd`, and metric primitives from `bucket-replication-metrics.go`.

Risks: Tickers are created in `NewReplicationStats`; only worker/queue goroutines are started there, while `trackEWMA` must be started elsewhere or transfer rates will not advance. `updateMovingAvg` assumes `XferRateLrg.measure` and `XferRateSml.measure` are non-nil. Queue counters can go negative if event accounting is unbalanced. Cluster aggregation mutates `mostRecentStats` only for buckets with non-empty replication stats, which can retain stale non-empty data if not invalidated. Some parameters such as `isDeleteRepl`, `isDelMarker`, and `opType` in queue helpers are not used in this file, so callers cannot rely on them changing queue behavior.

Test signals: No direct tests in this subset exercise `ReplicationStats.Update`, cluster aggregation, ticker behavior, or queue/proxy accounting. Serialization tests cover the metric structs used by this file, and utility tests cover the replicated target/status values that feed `Update`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-utils.go -->
## sources/object-store/minio/cmd/bucket-replication-utils.go

Purpose: Provides replication state, decision, resync, and MRF helper types/functions shared by replication handlers, workers, heal paths, delete paths, and stats. It is the core utility layer for composing per-target state into object-level replication metadata.

Important APIs/types: `replicatedTargetInfo`, `replicatedInfos`, `ReplicateDecision`, `ResyncDecision`, `ReplicationState`, `ResyncTargetsInfo`, `ResyncTarget`, `replicationResyncer`, `ResyncStatusType`, `TargetReplicationResyncStatus`, `BucketReplicationResyncStatus`, `MRFReplicateEntry`, and `MRFReplicateEntries`. Key functions include `CompletedSize`, `ReplicationResynced`, `ReplicationStatusInternal`, `ReplicationStatus`, `VersionPurgeStatus`, `VersionPurgeStatusInternal`, `Action`, `TargetReplicationStatus` on `ReplicateObjectInfo` and `ObjectInfo`, `parseReplicateDecision`, `CompositeReplicationStatus`, `CompositeVersionPurgeStatus`, `getReplicationState`, map parsers, `getHealReplicateObjectInfo`, `ObjectInfo.ReplicationState`, `ObjectToDelete.ReplicationState`, `parseSizeFromContentRange`, `extractReplicateDiffOpts`, and `ReplicateObjectInfo.ToMRFEntry`.

Control flow: Target results are collected in `replicatedInfos`; helper methods skip empty targets, build internal `arn=status;` strings, calculate completed bytes only for newly completed targets, and collapse target states with failure precedence, all-completed success, otherwise pending. `ReplicateDecision` stores per-target replicate/synchronous choices, stringifies them as comma-separated key/value records, and parses them back. `ReplicationState` builds target maps from metadata strings and computes composite object status, including backward-compatible single-status strings and replica timestamp precedence. Heal replication converts old single-target metadata to the newer per-target form, evaluates delete/object replication decisions, detects existing-object resync, and returns `ReplicateObjectInfo`. Resync status types and metadata structs describe per-target reset progress. MRF entries distill failed replication work into disk-storable bucket/object/retry records.

State and persistence: This file defines persisted metadata formats rather than doing most persistence directly. Internal replication status strings, version purge strings, reset metadata headers, resync binary metadata constants (`.replication/resync.bin`, format/version 1), and MRF metadata constants (`.replication/mrf`, format/version 1) are compatibility-sensitive. `BucketReplicationResyncStatus` and MRF types are serialized by generated msgp code.

Dependencies and integration points: Uses MinIO replication enums/config, crypto SSEC detection, HTTP content-range parsing, madmin replication diff options, bucket versioning, replication decision functions (`mustReplicate`, `checkReplicateDelete`), target reset headers, and object/delete metadata types from package `cmd`.

Risks: Metadata string parsing relies on delimiter formats; malformed strings silently yield empty/partial maps in several paths. `parseReplicateDecision` uses `strings.Split(p, "=")` instead of a two-field split, so unexpected `=` characters inside values would invalidate the decision. `getReplicationState` writes into `prevState.ResetStatusesMap` without ensuring it is non-nil; callers must provide initialized maps when resync timestamps may be recorded. Composite status failure precedence is simple and intentional, but any new status values default to pending unless map length is zero. Backward compatibility branches for single-status metadata must be preserved during refactors. MRF entries keep `versionID` and size in unexported fields, so generated serialization only stores bucket, object, and retry count.

Test signals: `bucket-replication-utils_test.go` covers completed-size accounting, internal status string generation, composite replication status, action selection, and replicate-decision parse round trips. Generated tests cover msgp serialization for resync, decision, state, and MRF structs. Gaps remain around heal replication, content-range parsing, reset metadata maps, version purge composition, and malformed metadata variants.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-utils_gen.go -->
## sources/object-store/minio/cmd/bucket-replication-utils_gen.go

Purpose: Generated `tinylib/msgp` codecs for replication utility and resync/MRF structs declared in `bucket-replication-utils.go`.

Important APIs/types: Implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `BucketReplicationResyncStatus`, `MRFReplicateEntries`, `MRFReplicateEntry`, `ReplicateDecision`, `ReplicationState`, `ResyncDecision`, `ResyncStatusType`, `ResyncTarget`, `ResyncTargetDecision`, `ResyncTargetsInfo`, and `TargetReplicationResyncStatus`.

Control flow: Struct codecs read/write msgp maps with compact field tags where configured. Map-bearing types (`BucketReplicationResyncStatus.TargetsMap`, `MRFReplicateEntries.Entries`, decision maps, replication state maps) allocate or clear maps on decode before filling entries. Unknown fields are skipped. Enum-like `ResyncStatusType` is encoded as an integer. Nested resync target/status values delegate to their own generated methods.

State and persistence: This file is the binary compatibility layer for persisted resync metadata, MRF metadata, and internal replication state snapshots. Only exported/tagged fields are serialized. Unexported operational fields such as `MRFReplicateEntry.versionID`, `MRFReplicateEntry.sz`, and `TargetReplicationResyncStatus.Error` are intentionally excluded.

Dependencies and integration points: Depends on `github.com/tinylib/msgp/msgp` and the MinIO replication package for map values of `replication.StatusType`. Regenerated from `bucket-replication-utils.go` by the msgp generator.

Risks: Generated map encode order follows Go map iteration, so byte-for-byte deterministic output is not guaranteed for maps even though decoded values should be equivalent. Struct/tag changes require regeneration and test updates. Excluding unexported fields is important for privacy/runtime state, but code that expects version IDs or object sizes from decoded MRF entries will not get them. Manual edits are fragile and should be avoided.

Test signals: `bucket-replication-utils_gen_test.go` round-trips and benchmarks every generated type in this file. Behavioral correctness of the underlying decisions and composite status rules is covered separately by `bucket-replication-utils_test.go`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-utils_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-utils_gen_test.go -->
## sources/object-store/minio/cmd/bucket-replication-utils_gen_test.go

Purpose: Generated msgp tests and benchmarks for replication utility serialization, including resync metadata, MRF entries, replication decisions, and replication state.

Important APIs/tests: For `BucketReplicationResyncStatus`, `MRFReplicateEntries`, `MRFReplicateEntry`, `ReplicateDecision`, `ReplicationState`, `ResyncDecision`, `ResyncTarget`, `ResyncTargetDecision`, `ResyncTargetsInfo`, and `TargetReplicationResyncStatus`, the file defines marshal/unmarshal tests, encode/decode tests, and benchmarks. It also benchmarks append-style marshaling.

Control flow: Tests use the standard msgp generated pattern: marshal a zero-value value, unmarshal into a new value, assert no trailing bytes, verify `msgp.Skip`, then repeat through streaming encode/decode. Benchmarks repeatedly execute each codec path after resetting timers.

State and persistence: Tests do not create persistent files. They validate the generated binary contract mechanically, but mostly with zero-value instances rather than populated resync maps or MRF entries.

Dependencies and integration points: Uses `testing`, `bytes`, and `github.com/tinylib/msgp/msgp`. It protects the generated codec file from compile-time and basic runtime regressions after msgp regeneration.

Risks: Zero-value round trips do not validate non-empty maps, timestamp values, enum variants, or excluded fields. Generated benchmarks do not enforce performance budgets. The file should be regenerated, not hand-edited.

Test signals: Provides broad serialization smoke coverage for `bucket-replication-utils_gen.go`; it should be paired with hand-written tests for metadata semantics, resync workflows, and MRF retry behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-utils_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-utils_test.go -->
## sources/object-store/minio/cmd/bucket-replication-utils_test.go

Purpose: Hand-written unit tests for central replication utility semantics: per-target result aggregation, decision string parsing, and composite replication status.

Important APIs/tests: `TestReplicatedInfos` exercises `replicatedInfos.CompletedSize`, `ReplicationStatusInternal`, `ReplicationStatus`, and `Action`. `TestParseReplicateDecision` exercises string round-tripping through `ReplicateDecision.String` and `parseReplicateDecision`. `TestCompositeReplicationStatus` exercises `ReplicationState.CompositeReplicationStatus`.

Control flow: Table-driven fixtures cover empty target lists, completed single-target replication, mixed completed/failed targets, pending/failed targets, empty decision strings, one and multiple target decisions, and composite states with missing metadata, valid per-target pending/failed/completed strings, malformed status strings, and backward-compatible `REPLICA` status.

State and persistence: The tests are pure in-memory and do not interact with bucket metadata, object layers, or resync files. They construct helper structs directly.

Dependencies and integration points: Uses Go `testing` and MinIO replication enum constants. These tests guard behavior consumed by replication workers, stats updates, object metadata updates, and handlers that report composite state.

Risks: `TestParseReplicateDecision` parses `test.expDsc.String()` rather than the raw `test.dsc`, so the invalid-format fixture does not actually exercise invalid input. The tests do not cover version purge status composition, reset status maps, `getReplicationState`, `getHealReplicateObjectInfo`, content-range parsing, or MRF conversion. Map string order from `ReplicateDecision.String` can be nondeterministic for multi-target maps, though the test compares parsed maps rather than raw strings.

Test signals: Strong signal for the most important status aggregation rules: failures dominate, all targets completed yields completed, empty state yields empty, and newly completed targets contribute size. It also documents expected backward compatibility for single-string replica status.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-replication-utils_test.go -->
