# Research: subset-b-008197 MinIO metrics v2 and v3 files

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v2.go -->
# sources/object-store/minio/cmd/metrics-v2.go

Purpose: Implements MinIO's legacy v2 Prometheus metrics surface. It defines the v2 metric data model, builds node, cluster, bucket, and peer metric groups, adapts many internal MinIO subsystems into `MetricV2` records, serializes peer metrics, and exposes v2 HTTP handlers.

Important APIs/types/functions: `MetricNamespace`, `MetricSubsystem`, `MetricName`, `MetricTypeV2`, `MetricDescription`, `MetricV2`, `MetricsGroupV2`, and `MetricsGroupOpts` are the v2 schema. `RegisterRead` wraps a loader in a `cachevalue.Cache` and enforces global dependency gates such as object API, IAM, KMS, site replication, notification, lock server, and background healing. `Get` returns cloned cached metrics to protect cached maps. `getHistogramMetrics` converts `prometheus.HistogramVec` samples into flat `MetricV2` points with `le` labels and a v2 bucket cardinality cap. `collectMetric`, `populateAndPublish`, `ReportMetrics`, `minioNodeCollector`, `minioClusterCollector`, and `minioBucketCollector` bridge MinIO records to Prometheus collectors. `metricsNodeHandler`, `metricsServerHandler`, and `metricsBucketHandler` expose the scrape endpoints.

Control flow: package `init` constructs metric groups for cluster, peer, node, bucket, and bucket-peer contexts, then stores global collector instances. Each group registers a loader. On scrape, the HTTP handler gathers through a fresh Prometheus registry. Collectors call `Get` on each `MetricsGroupV2`; cache misses run the registered loader, while cache hits return the last good snapshot. Cluster and bucket collectors concurrently combine local `ReportMetrics` output with peer metrics from `globalNotificationSys`. Node collection publishes directly and adds the local server label. Histogram metrics are expanded before publication, while non-histograms become gauge or counter `NewConstMetric` values.

State and persistence behavior: The file has no durable persistence, but it is state-heavy. It stores package globals for collectors and peer metric groups. Each metrics group owns a TTL cache that may return the last good value after loader failure. Loaders read live process state, atomics, background scanner counters, IAM refresh counters, KMS state, replication summaries, bucket quotas, data usage backend state, drive/storage info, logger targets, and HTTP counters. Bucket-oriented v2 output caps buckets to `v2MetricsMaxBuckets` to avoid high-cardinality legacy scrapes.

Dependencies and integration points: The code integrates with Prometheus client libraries, msgp generation, `cachevalue`, procfs, madmin realtime metrics, MinIO globals such as `globalHTTPStats`, `globalBucketHTTPStats`, `globalConnStats`, `globalScannerMetrics`, `globalReplicationStats`, `globalBucketTargetSys`, `globalSiteReplicationSys`, `globalNotificationSys`, `globalIAMSys`, `globalAuthNPlugin`, `GlobalKMS`, and object layer calls. It also uses peer APIs through notification system methods for cluster and bucket metrics.

Risks: v2 behavior depends on many mutable globals, so nil or not-yet-initialized subsystems must remain guarded. High cardinality is a known risk, mitigated only for some bucket metrics and histograms. Some labels are built from maps without stable ordering; Prometheus accepts label name/value arrays as paired slices, but order is not deterministic across scrapes. Several loaders intentionally ignore errors or return empty metrics, which preserves scrape availability but can mask missing telemetry. Legacy metric names and types are compatibility-sensitive.

Test signals: `metrics-v2_test.go` covers histogram point count, API label lowercasing, and cumulative bucket values. `metrics-v2_gen_test.go` covers msgp round trips for the serializable v2 types. There is no broad test coverage for every global subsystem loader or HTTP handler path in this file.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v2_gen.go -->
# sources/object-store/minio/cmd/metrics-v2_gen.go

Purpose: Generated msgp serialization code for the v2 metrics schema used to move metrics between MinIO peers and cache/report them efficiently.

Important APIs/types/functions: Implements `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `MetricDescription`, `MetricName`, `MetricNamespace`, `MetricSubsystem`, `MetricTypeV2`, `MetricV2`, `MetricsGroupOpts`, and `MetricsGroupV2`. Map fields in `MetricV2` are encoded as MessagePack maps. `MetricsGroupV2` intentionally serializes only `cacheInterval` and `metricsGroupOpts`, not the runtime cache, matching the `msg:"-"` tag on `metricsCache`.

Control flow: Each marshal function reserves space with `msgp.Require`, writes a fixed map header and fields, and recursively marshals nested metric descriptions/options. Each unmarshal function reads a map header, switches on field names, fills typed fields, clears reused maps before repopulating them, and skips unknown fields for forward compatibility. `Msgsize` provides upper-bound sizing for allocation reuse.

State and persistence behavior: This file is stateless generated code, but it defines the wire/disk shape of v2 metrics and options. Reused receiver maps are cleared during unmarshal, reducing stale-entry risk. Unknown fields are skipped, allowing newer senders to interoperate with older readers as long as required fields remain compatible.

Dependencies and integration points: Generated by `github.com/tinylib/msgp` from `metrics-v2.go` directives. It is coupled to the exact field names of the v2 metrics structs and to MinIO's peer metrics transport paths that call msgp marshal/unmarshal methods.

Risks: Manual edits would be overwritten by regeneration and may desynchronize generated behavior from struct definitions. Adding or renaming fields in `metrics-v2.go` requires regenerating this file and its generated tests. Wire compatibility depends on stable field names such as `Description`, `VariableLabels`, and `metricsGroupOpts`.

Test signals: `metrics-v2_gen_test.go` exercises marshal/unmarshal and `msgp.Skip` for all generated types plus allocation/throughput benchmarks.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v2_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v2_gen_test.go -->
# sources/object-store/minio/cmd/metrics-v2_gen_test.go

Purpose: Generated tests and benchmarks for msgp serialization of MinIO v2 metric types.

Important APIs/types/functions: Contains `TestMarshalUnmarshalMetricDescription`, `TestMarshalUnmarshalMetricV2`, `TestMarshalUnmarshalMetricsGroupOpts`, and `TestMarshalUnmarshalMetricsGroupV2`, plus marshal, append, and unmarshal benchmarks for each type. Tests use `msgp.Skip` to verify the emitted message can be skipped cleanly.

Control flow: Each test marshals a zero-value type, unmarshals into the same receiver, verifies no trailing bytes remain, then checks that `msgp.Skip` also consumes the full encoded buffer. Benchmarks repeatedly marshal into fresh or reused buffers and repeatedly unmarshal a prebuilt buffer.

State and persistence behavior: No persistent state. The tests implicitly validate zero-value serialization, map creation/clearing paths, and the generated ability to consume a complete message without leftover bytes.

Dependencies and integration points: Depends on `github.com/tinylib/msgp/msgp` and the generated methods from `metrics-v2_gen.go`. It is regenerated with the msgp output and should track the serializable v2 metrics structs.

Risks: The tests are shallow by design: they use zero values and do not assert semantic equality for populated metric labels, histograms, cache intervals, or dependency flags. They catch broken generated encoders/decoders but not schema compatibility issues with non-empty production data.

Test signals: These tests are themselves the test signal for the generated file. Benchmarks provide performance regression visibility for peer metric serialization.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v2_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v2_test.go -->
# sources/object-store/minio/cmd/metrics-v2_test.go

Purpose: Unit tests for v2 histogram conversion in `getHistogramMetrics`.

Important APIs/types/functions: `TestGetHistogramMetrics_BucketCount` builds a `prometheus.HistogramVec`, records observations across several API labels, and checks that conversion emits one point per configured bucket plus one `+Inf` point per API label. `TestGetHistogramMetrics_Values` validates cumulative bucket counts and optional lowercasing of the `api` label.

Control flow: Tests create histograms, observe values with short ticker delays to exercise channel-based collection, call `getHistogramMetrics`, filter returned `MetricV2` values by API label, sort by the `le` label, and compare expected labels and counts.

State and persistence behavior: No persistent state. The tests rely on in-memory Prometheus histograms and fresh metric vectors per test. They indirectly test that `getHistogramMetrics` drains the collection channel and includes the synthetic `+Inf` sample.

Dependencies and integration points: Depends on Prometheus client histograms and the v2 metric descriptors from `metrics-v2.go`. It verifies compatibility behavior used by S3 and bucket TTFB v2 metrics.

Risks: The sort comparator appears to compare `a.VariableLabels["le"]` with itself instead of `b.VariableLabels["le"]`, so ordering checks may not be as deterministic as intended. The tests do not cover `limitBuckets=true` behavior or bucket-name capping, which is one of the v2 cardinality safeguards.

Test signals: Provides focused regression coverage for histogram expansion, API label casing compatibility, and cumulative count extraction.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-api.go -->
# sources/object-store/minio/cmd/metrics-v3-api.go

Purpose: Defines v3 API and bucket API metrics for S3 HTTP requests, TTFB histograms, rejected requests, and network byte counters.

Important APIs/types/functions: Metric descriptors include `apiRejected*`, `apiRequests*`, `apiRequestsTTFBSecondsDistribution`, and `apiTraffic*` variants. `loadAPIRequestsHTTPMetrics`, `loadAPIRequestsTTFBMetrics`, and `loadAPIRequestsNetworkMetrics` populate node-level S3 metrics. `loadBucketAPIHTTPMetrics` and `loadBucketAPITTFBMetrics` populate bucket-scoped metrics for explicitly requested buckets.

Control flow: Node HTTP metrics read `globalHTTPStats.toServerHTTPStats(false)`, set global rejection and queue counters with `type=s3`, then iterate per-API maps for inflight, totals, errors, 4xx, 5xx, and canceled counts. TTFB loaders call `MetricValues.SetHistogram`, renaming the `api` label to `name`. Bucket HTTP metrics first require a non-empty bucket list, read bucket connection stats and per-bucket HTTP stats, and set labels `bucket`, `name`, and `type`.

State and persistence behavior: Stateless loader code over live counters. Histogram state lives in global Prometheus histogram vectors. Bucket metrics are request-filtered in v3 rather than globally capped as in v2.

Dependencies and integration points: Uses `MetricValues`, `NewCounterMD`, `NewGaugeMD`, `SetHistogram`, `globalHTTPStats`, `globalBucketHTTPStats`, `globalBucketConnStats`, `globalConnStats`, `httpRequestsDuration`, and `bucketHTTPRequestsDuration`. Consumed by v3 metric group registration and `metrics-v3-handler.go`.

Risks: Label naming changes from v2 (`api` to `name`) can affect dashboards. Bucket traffic descriptor help text appears swapped relative to variable names: sent descriptor says received and received descriptor says sent. Bucket metrics produce nothing if the v3 handler does not pass bucket filters.

Test signals: No direct tests in this subset. Indirect coverage may come from generic v3 metric group tests elsewhere and v2 histogram tests for shared histogram conversion concepts.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-audit.go -->
# sources/object-store/minio/cmd/metrics-v3-audit.go

Purpose: Exposes v3 audit logger target metrics for failed messages, queue length, and total sent messages.

Important APIs/types/functions: Defines `auditFailedMessages`, `auditTargetQueueLength`, `auditTotalMessages`, and label `target_id`. `loadAuditMetrics` reads `logger.CurrentStats()` and stores three metrics per target in `MetricValues`.

Control flow: On scrape, the loader iterates the current audit stats map. For each target id it builds the `target_id` label pair and sets failed, queue, and total values.

State and persistence behavior: The loader is stateless; state is maintained by the logger subsystem. Queue length is a gauge-like live value, while totals and failures are counters since process start.

Dependencies and integration points: Depends on `github.com/minio/minio/internal/logger` and the v3 metrics framework. It integrates with audit webhook/logging targets and is surfaced by the v3 collection tree.

Risks: Target ids become labels, so a deployment with many dynamic audit targets could increase cardinality. The cache parameter is unused, so every scrape reads current logger stats directly.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-audit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-bucket-replication.go -->
# sources/object-store/minio/cmd/metrics-v3-bucket-replication.go

Purpose: Exposes v3 bucket-level replication metrics for failed bytes/counts, proxied replication target requests, sent bytes/counts, and upload latency distributions.

Important APIs/types/functions: Defines descriptor constants for last-hour, last-minute, total failed, sent, proxied get/head/tagging, delete tagging, latency, and labels `bucket`, `operation`, and `targetArn`. `loadBucketReplicationMetrics` is a `BucketMetricsLoaderFn`. It uses `SetHistogramValues` for latency buckets.

Control flow: The loader returns immediately when site replication is enabled because bucket replication stats are not applicable in that mode. It gets data usage from `metricsCache`, builds latest bucket replication stats with `globalReplicationStats.Load().getAllLatest`, then iterates only requested buckets. For each target ARN with replication usage it sets failure windows, proxy counters, sent counters, total failures, and upload latency histogram values.

State and persistence behavior: It is stateless but depends on cached data usage and live replication stats. Bucket output is constrained by the v3 handler's requested bucket list. Metrics represent a mix of process lifetime counters and recent window gauges.

Dependencies and integration points: Depends on `metricsCache.dataUsageInfo`, `globalSiteReplicationSys`, `globalReplicationStats`, `BucketReplicationStats`, and v3 bucket metric group handling. It complements cluster replication metrics in `metrics-v3-replication.go`.

Risks: `globalReplicationStats.Load()` is used without an explicit nil check in this file, so loader safety depends on replication stats being initialized before this metric group is active. Site replication mode suppresses these metrics entirely. Label `targetArn` can produce high cardinality when many replication targets exist.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-bucket-replication.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cache.go -->
# sources/object-store/minio/cmd/metrics-v3-cache.go

Purpose: Provides shared v3 metrics caches for expensive or cross-subsystem data used by metrics loaders.

Important APIs/types/functions: `metricsCache` groups caches for data usage, erasure-set health, local drive metrics, memory metrics, CPU metrics, cluster drive metrics, and node online/offline counts. `newMetricsCache` constructs them. `storageMetrics` carries `madmin.StorageInfo`, iostat-derived metrics, and drive counts. `getDiffStats` and `getDriveIOStatMetrics` derive per-second disk I/O rates from sampled `madmin.DiskIOStats`.

Control flow: Each `new*Cache` returns a `cachevalue.NewFromFunc` with a one-minute TTL and `ReturnLastGood`. Data usage and health call object-layer methods if initialized. CPU and memory call `collectLocalMetrics` for the local node. Drive metrics sample `LocalStorageInfo`, compute drive counts, sample current disk I/O stats, compare with the previous sample under a mutex, store rate metrics when enough time elapsed, then update the previous sample.

State and persistence behavior: No durable persistence. Runtime state includes previous drive I/O samples and refresh timestamps captured by the drive cache closure, plus cached last-good values across all caches. First drive scrape lacks rate metrics because there is no prior sample.

Dependencies and integration points: Integrates with object layer, madmin realtime metrics, cachevalue, health APIs, storage info helpers, and global node identity. It is injected into v3 `MetricsGroup` loaders by the v3 collection setup.

Risks: Caches intentionally hide transient failures by returning last good data, which improves scrape stability but can make stale metrics look fresh. Some loaders ignore cache errors. Drive I/O rate math assumes monotonic disk counters and positive sample duration. `GlobalContext` is used inside cache loaders even when a scrape context is supplied.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cluster-config.go -->
# sources/object-store/minio/cmd/metrics-v3-cluster-config.go

Purpose: Exposes cluster storage-class parity configuration as v3 metrics.

Important APIs/types/functions: Defines `configRRSParity`, `configStandardParity`, their gauge descriptors, and `loadClusterConfigMetrics`.

Control flow: The loader retrieves cached cluster drive metrics from `c.clusterDriveMetrics`. On success it reads `storageInfo.Backend.StandardSCParity` and `RRSCParity` and sets both gauges. On error it logs with `metricsLogIf` and returns nil to keep collection alive.

State and persistence behavior: Stateless; values come from cached cluster storage info refreshed by `metrics-v3-cache.go`.

Dependencies and integration points: Depends on `metricsCache.clusterDriveMetrics`, storage info backend parity fields, and the v3 metrics group framework. It mirrors some v2 storage class metrics in a smaller v3 module.

Risks: If storage info is stale or unavailable, parity metrics can be stale or absent. There is no explicit object-layer guard here beyond the cache returning zero values when not initialized.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cluster-config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cluster-erasure-set.go -->
# sources/object-store/minio/cmd/metrics-v3-cluster-erasure-set.go

Purpose: Exposes v3 erasure-set health, quorum, tolerance, and drive counts at cluster scope.

Important APIs/types/functions: Defines metric names for overall write quorum, overall health, per-set read/write quorum, online/healing drives, health, read/write tolerance, and read/write health. Labels are `pool_id` and `set_id`. `b2f` converts booleans to Prometheus numeric values. `loadClusterErasureSetMetrics` populates all values.

Control flow: The loader obtains cached `HealthResult` from `c.esetHealthResult`, sets overall write quorum and overall health, then iterates each `ESHealth` record. It emits per-pool/set quorum and drive gauges, converts set health to 1/0, computes read tolerance as healthy drives minus read quorum, and write tolerance as healthy plus healing drives minus write quorum. Negative tolerance flips the corresponding health gauge to 0.

State and persistence behavior: Stateless over cached health state. Values are live health snapshots refreshed through `metricsCache` with last-good behavior.

Dependencies and integration points: Depends on object-layer health via `newESetHealthResultCache`, `HealthResult.ESHealth`, and v3 metric descriptors. These metrics integrate with cluster health dashboards and alerting.

Risks: The loader ignores the cache error return, so zero-value health can be emitted if the cache cannot load and has no last-good value. Tolerance calculations are simple and depend on accurate `HealthyDrives`, `HealingDrives`, and quorum fields.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cluster-erasure-set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cluster-health.go -->
# sources/object-store/minio/cmd/metrics-v3-cluster-health.go

Purpose: Exposes v3 cluster health rollups for drive counts, node counts, and raw/usable capacity.

Important APIs/types/functions: Defines drive health descriptors (`drives_offline_count`, `drives_online_count`, `drives_count`), node descriptors (`nodes_offline_count`, `nodes_online_count`), and capacity descriptors (`capacity_raw_total_bytes`, `capacity_raw_free_bytes`, `capacity_usable_total_bytes`, `capacity_usable_free_bytes`). Loaders are `loadClusterHealthDriveMetrics`, `loadClusterHealthNodeMetrics`, and `loadClusterHealthCapacityMetrics`.

Control flow: Drive and capacity loaders fetch `c.clusterDriveMetrics`; drive loader emits cached online/offline/total counts, capacity loader computes totals from cached `storageInfo.Disks` with helper functions. Node loader fetches `c.nodesUpDown` and emits peer online/offline counts.

State and persistence behavior: Stateless over the shared metrics cache. Values can be last-good snapshots for up to the cache policy and depend on the notification system and object-layer storage info.

Dependencies and integration points: Depends on `metricsCache.clusterDriveMetrics`, `metricsCache.nodesUpDown`, storage capacity helper functions, and `globalNotificationSys.GetPeerOnlineCount()` through the cache. Complements erasure-set-specific health metrics.

Risks: Cache errors are ignored in these loaders, which favors scrape continuity but can emit zero values if no cached value exists. Capacity helpers depend on correct disk state classification.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cluster-health.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cluster-iam.go -->
# sources/object-store/minio/cmd/metrics-v3-cluster-iam.go

Purpose: Exposes v3 IAM and external auth plugin health/sync metrics.

Important APIs/types/functions: Defines metrics for IAM sync duration, time since last sync, sync successes/failures, plugin auth request totals/failures, last success/failure seconds, and average/max successful RTT. `loadClusterIAMMetrics` populates all values.

Control flow: The loader reads IAM atomics from `globalIAMSys`, gets plugin auth metrics from `globalAuthNPlugin.Metrics()`, computes milliseconds since last sync if a last sync timestamp exists, and stores all values in `MetricValues`.

State and persistence behavior: Stateless loader over global atomics and plugin state. Counters are process-lifetime values and timing gauges reflect current wall-clock deltas.

Dependencies and integration points: Depends on `globalIAMSys`, `globalAuthNPlugin`, `sync/atomic`, and v3 metric descriptors. It is a v3 replacement for IAM metrics in the v2 monolithic file.

Risks: The loader assumes `globalIAMSys` and `globalAuthNPlugin` are initialized by the metric group dependency setup. Several descriptors use `NewCounterMD` for values that behave like gauges or durations, so metric type semantics should be reviewed before dashboard or alert changes.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cluster-iam.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cluster-notification.go -->
# sources/object-store/minio/cmd/metrics-v3-cluster-notification.go

Purpose: Exposes cluster-level notification subsystem metrics for current sends, sent events, failed events, and skipped events.

Important APIs/types/functions: Defines `notificationCurrentSendInProgress`, `notificationEventsErrorsTotal`, `notificationEventsSentTotal`, `notificationEventsSkippedTotal`, descriptors, and `loadClusterNotificationMetrics`.

Control flow: The loader returns nil if `globalEventNotifier` is absent. Otherwise it gets target-list stats and sets four aggregate metrics.

State and persistence behavior: Stateless over notification target-list state. Current send in progress is a live value; total, error, and skipped event values are process-lifetime counters.

Dependencies and integration points: Depends on `globalEventNotifier.targetList.Stats()` and v3 metrics infrastructure. It surfaces cluster notification health separately from per-target logger/audit webhook metrics.

Risks: `notificationCurrentSendInProgressMD` is declared as a counter even though the value is a current in-progress count and should conceptually be a gauge. This type mismatch can affect Prometheus semantics.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cluster-notification.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cluster-usage.go -->
# sources/object-store/minio/cmd/metrics-v3-cluster-usage.go

Purpose: Exposes v3 cluster and bucket usage metrics sourced from MinIO's data usage scan results.

Important APIs/types/functions: Cluster metrics include since-last-update seconds, total bytes, object count, versions count, delete marker count, bucket count, object size distribution, and version count distribution. Bucket metrics include bucket total bytes, objects, versions, delete markers, quota, object size distribution, and object version count distribution. Loaders are `loadClusterUsageObjectMetrics` and `loadClusterUsageBucketMetrics`.

Control flow: Both loaders retrieve `DataUsageInfo` from `c.dataUsageInfo`, log and stop on errors, and return no metrics until `LastUpdate` is non-zero. The cluster loader aggregates usage across all buckets and merges histograms before setting metrics. The bucket loader iterates every usage bucket, retrieves quota from `globalBucketQuotaSys`, emits per-bucket counters/gauges, and emits per-bucket histogram bins.

State and persistence behavior: Stateless over cached data usage, which is derived from backend-scanner persisted usage data. Usage values reflect the last scanner update, not necessarily current object store state. Quota lookup is live per bucket.

Dependencies and integration points: Depends on `metricsCache.dataUsageInfo`, `loadDataUsageFromBackend`, `globalBucketQuotaSys`, and v3 metric descriptors. Scanner metrics also use the same data usage cache for last activity.

Risks: Bucket loader emits all buckets in `DataUsageInfo`, which can be high cardinality compared with v3 bucket-specific API metrics. `usageSinceLastUpdateSeconds` is set with `float64(time.Since(...))` in bucket loader, which represents nanoseconds, while the cluster loader uses `.Seconds()` and the metric name says seconds; this inconsistency is a correctness risk. Quota lookup errors skip the whole bucket's usage metrics.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-cluster-usage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-handler.go -->
# sources/object-store/minio/cmd/metrics-v3-handler.go

Purpose: Implements the HTTP server for v3 metrics, including path-based collector selection, listing mode, bucket path parsing, authentication wrapping, and Prometheus handler options.

Important APIs/types/functions: `metricsV3Server` holds a Prometheus registry, promhttp options, auth wrapper, and `metricsV3Collection`. `newMetricsV3Server` constructs metric groups and initializes global collector path listing once. `metricDisplay` formats descriptor metadata. `listMetrics` returns JSON or markdown-table text for metrics under a path. `handle` maps request paths to gatherers and injects bucket filters. `ServeHTTP` parses mux path variables and query parameters, wraps tracing, and applies auth.

Control flow: Server construction creates a registry and metric group collection. Request handling extracts `pathComps`, detects `?list`, and parses `/bucket/.../<bucket>` paths by stripping the final bucket component from the collector path. Non-list requests collect all descendant paths and gatherers. For bucket metric groups, the handler sets the requested bucket list under a group lock for the duration of collection. If no matching gatherers or listing data exist, it returns 404. Otherwise it delegates to `promhttp.HandlerFor`.

State and persistence behavior: Runtime state includes a registry, metric group collection, promhttp options, global collector path cache guarded by `sync.Once`, and temporary bucket lists stored in bucket metric groups under locks. There is no durable persistence.

Dependencies and integration points: Depends on `newMetricGroups`, `metricsV3Collection`, `MetricsGroup.LockAndSetBuckets`, mux route variables, Prometheus promhttp, OpenMetrics environment config, tracing context, and the auth middleware supplied by the caller.

Risks: Bucket selection by last path component assumes bucket names do not require additional path escaping in this route. `listMetrics` checks request `Content-Type` instead of `Accept`, which may surprise clients asking for JSON. Bucket metric groups return nothing unless buckets are explicitly supplied. `MaxRequestsInFlight` is set to 2, so slow collectors can throttle concurrent scrapes.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-ilm.go -->
# sources/object-store/minio/cmd/metrics-v3-ilm.go

Purpose: Exposes v3 ILM expiration, transition, and lifecycle scanner counters.

Important APIs/types/functions: Defines metrics for pending expiry tasks, active/pending transition tasks, missed immediate transition tasks, and versions scanned. `loadILMMetrics` populates these values.

Control flow: The loader checks `globalExpiryState` before setting pending expiry tasks, checks `globalTransitionState` before setting transition gauges/counter, and always sets lifecycle versions scanned from `globalScannerMetrics.lifetime(scannerMetricILM)`.

State and persistence behavior: Stateless over global lifecycle worker state and scanner counters. Metrics are process runtime values.

Dependencies and integration points: Depends on global expiry/transition state and scanner metrics. It separates ILM telemetry from the larger v2 scanner/ILM block.

Risks: When expiry or transition state is nil, corresponding metrics are omitted rather than emitted as zero. Consumers must handle absent series during startup or disabled subsystems.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-ilm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-logger-webhook.go -->
# sources/object-store/minio/cmd/metrics-v3-logger-webhook.go

Purpose: Exposes v3 metrics for system and audit logger webhook targets.

Important APIs/types/functions: Defines `webhookQueueLength`, `webhookTotalMessages`, `webhookFailedMessages`, labels `name` and `endpoint`, and `loadLoggerWebhookMetrics`.

Control flow: The loader appends `logger.SystemTargets()` and `logger.AuditTargets()`, then for each target sets failed messages, queue length, and total messages with target name and endpoint labels.

State and persistence behavior: Stateless over logger target stats. Queue length is live, totals/failures are process-lifetime counters.

Dependencies and integration points: Depends on MinIO internal logger target APIs and v3 metrics descriptors. It integrates with alerting on webhook delivery backlog or failures.

Risks: Endpoint values are labels and may include high-cardinality or sensitive deployment details. Target health/online status is not exposed here, unlike the legacy v2 webhook metrics that included online state.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-logger-webhook.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-replication.go -->
# sources/object-store/minio/cmd/metrics-v3-replication.go

Purpose: Exposes v3 cluster replication queue, worker, transfer-rate, and recent backlog metrics.

Important APIs/types/functions: Defines descriptors for average/current/max active workers, average/current/max data transfer rate, last-minute queued bytes/count, average/max queued bytes/count, and recent backlog count. `loadClusterReplicationMetrics` populates them.

Control flow: The loader loads `globalReplicationStats`; if nil it returns without metrics. It gets a node queue summary, emits queued byte/count gauges for average, max, and current windows, emits active worker gauges, emits transfer rate gauges if transfer stats exist, and emits recent backlog count from MRF stats.

State and persistence behavior: Stateless over replication stats. Values reflect in-memory rolling summaries and process-lifetime or recent-window state maintained by the replication subsystem.

Dependencies and integration points: Depends on `globalReplicationStats.Load()`, queue summary types, and v3 metrics infrastructure. It complements per-bucket replication metrics.

Risks: Transfer rate metrics are omitted when `XferStats` is empty. Metric names differ from v2 in some places, such as `*_data_transfer_rate`, which may require dashboard migration.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-replication.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-scanner.go -->
# sources/object-store/minio/cmd/metrics-v3-scanner.go

Purpose: Exposes v3 scanner progress and activity metrics.

Important APIs/types/functions: Defines scanner metrics for bucket scans started/finished, directories scanned, objects scanned, versions scanned, and last activity seconds. `loadClusterScannerMetrics` populates them.

Control flow: The loader reads lifetime counters from `globalScannerMetrics`, treating started scans as completed bucket-drive scans plus active drives. It retrieves cached data usage and sets last activity as seconds since `LastUpdate` if available, logging cache errors.

State and persistence behavior: Stateless over global scanner counters and cached data usage. Last activity reflects data usage update time, which may be zero or stale if scanner data has not been captured.

Dependencies and integration points: Depends on `globalScannerMetrics`, `metricsCache.dataUsageInfo`, and scanner metric constants shared with other MinIO subsystems.

Risks: If `LastUpdate` is zero but cache retrieval succeeds, `time.Since` would produce a very large value; unlike usage loaders, this file does not explicitly skip zero `LastUpdate`. The comment says "cluster webhook", which is stale and could confuse maintainers.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-scanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-system-cpu.go -->
# sources/object-store/minio/cmd/metrics-v3-system-cpu.go

Purpose: Exposes v3 node CPU metrics for load, load percentage, user/system/nice/steal percentages, and average idle/iowait resource metrics.

Important APIs/types/functions: Defines CPU descriptor constants and `loadCPUMetrics`. The loader reads cached `madmin.CPUMetrics` and `resourceMetricsMap`.

Control flow: The loader retrieves `c.cpuMetrics`. If load stats exist, it sets 1-minute load and load percent rounded to two decimals. If time stats exist, it computes total CPU time and sets user/system/nice/steal percentages rounded to two decimals. It then looks up CPU idle and iowait averages in `resourceMetricsMap[cpuSubsystem]`.

State and persistence behavior: Stateless loader over one-minute cached CPU metrics and global resource metrics map. Values are current sampled percentages, not cumulative counters.

Dependencies and integration points: Depends on `metricsCache.cpuMetrics`, madmin CPU collection, `resourceMetricsMap`, `getResourceKey`, and CPU resource constants. It is part of system/node v3 metrics.

Risks: Division by zero is possible if `CPUCount` or total CPU time is zero, though upstream metrics likely populate them. Cache errors are ignored. Values are rounded, which is useful for display but loses precision.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-system-cpu.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-system-drive.go -->
# sources/object-store/minio/cmd/metrics-v3-system-drive.go

Purpose: Exposes v3 node drive metrics for capacity, inode counts, health, API error/latency counters, drive counts, and iostat-derived throughput/latency/utilization.

Important APIs/types/functions: Defines drive label constants `drive`, `pool_index`, `set_index`, `drive_index`, and `api`; drive health values offline/online/healing; capacity/error/latency/count/iostat descriptors; `getCurrentDriveIOStats`; `MetricValues.setDriveBasicMetrics`, `setDriveAPIMetrics`, `setDriveIOStatMetrics`; and `loadDriveMetrics`.

Control flow: `getCurrentDriveIOStats` collects local disk metrics for the local node and maps disk path to I/O stats. `loadDriveMetrics` retrieves cached `storageMetrics`, iterates disks, builds stable labels including pool/set/drive indexes, emits basic capacity/inode/health values, emits cached iostat rate values if available, emits API error and last-minute latency values, then sets aggregate offline/online/total drive counts.

State and persistence behavior: Loader is stateless, but iostat values depend on state maintained in `newDriveMetricsCache`: previous disk counters and refresh time. Health is encoded as 0 offline, 1 online, 2 healing.

Dependencies and integration points: Depends on madmin disk metrics, object-layer local storage info through the cache, drive metrics in `madmin.Disk`, and v3 metrics framework. It is the detailed node-level counterpart to cluster health drive counts.

Risks: First scrape after startup lacks iostat rates. Disk path labels can be high-cardinality or expose host path details. I/O errors are computed as availability minus timeout errors; unexpected counter semantics could produce negative values. The help text includes "microseconds" but the metric name uses `micros`, so consumers should not infer seconds.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-system-drive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-system-memory.go -->
# sources/object-store/minio/cmd/metrics-v3-system-memory.go

Purpose: Exposes v3 node memory metrics.

Important APIs/types/functions: Defines descriptors for total, used, free, buffers, cache, used percentage, shared, and available memory. `loadMemoryMetrics` populates values from cached `madmin.MemInfo`.

Control flow: The loader retrieves `c.memoryMetrics`, logs and returns the error if cache retrieval fails, then sets all memory gauges. Used percentage is calculated as `Used * 100 / Total`.

State and persistence behavior: Stateless over one-minute cached memory metrics. Values reflect madmin local host memory collection.

Dependencies and integration points: Depends on `metricsCache.memoryMetrics`, madmin memory collection, and v3 metrics framework.

Risks: Division by zero is possible if `Total` is zero. Unlike many other loaders, this one returns the cache error after logging, which can affect the metric group's collect error path. Metric units are bytes for most values but percentage for `used_perc`.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-system-memory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-system-network.go -->
# sources/object-store/minio/cmd/metrics-v3-system-network.go

Purpose: Exposes v3 internode network metrics for distributed erasure deployments.

Important APIs/types/functions: Defines `internodeErrorsTotal`, `internodeDialErrorsTotal`, `internodeDialAvgTimeNanos`, `internodeSentBytesTotal`, and `internodeRecvBytesTotal` descriptors. `loadNetworkInternodeMetrics` populates them.

Control flow: The loader reads connection stats from `globalConnStats.toServerConnStats()` and RPC stats from `rest.GetRPCStats()`. It emits metrics only if `globalIsDistErasure` is true.

State and persistence behavior: Stateless over process-global connection and RPC counters. The emitted counters are process lifetime values and dial average is a live aggregate.

Dependencies and integration points: Depends on `globalConnStats`, `globalIsDistErasure`, and internal REST RPC stats. It complements API traffic metrics, which cover S3 bytes.

Risks: Single-node or non-distributed configurations emit no internode series, so dashboards must tolerate absent metrics. Dial average duration is converted directly to float64 nanoseconds; naming makes units clear but consumers must not treat it as seconds.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-system-network.go -->
