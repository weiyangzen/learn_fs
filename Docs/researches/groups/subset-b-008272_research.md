# subset-b-008272 Research

Grouped research for RustFS observability metrics collectors, runtime wiring, report conversion, and selected schema descriptor files. Each file section is source-tree aligned and bounded by reconciliation markers for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/bucket_replication.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/bucket_replication.rs

Purpose: converts per-bucket replication and per-target bandwidth snapshots into `PrometheusMetric` values using descriptors from `schema::bucket_replication`. It covers failure bytes/counts, sent bytes/counts, proxied request totals/failures, replication latency, and bandwidth limit/current EWMA.

Important APIs/types: `BucketReplicationTargetStats`, `BucketReplicationBandwidthStats`, `BucketReplicationStats`, `collect_bucket_replication_bandwidth_metrics`, and `collect_bucket_replication_metrics`. The main stats struct is a decoupled DTO with bucket identity, counters/gauges for replication failures and proxied operations, and a `targets` vector for target-specific latency.

Control flow: bandwidth collection returns early for empty input, then emits two metrics per `(bucket,target_arn)`. bucket replication collection returns early for empty input, preallocates `20 + targets.len()` per bucket, emits fixed bucket-labeled metrics, then emits one latency metric per target with labels `bucket`, `operation=object_replication`, `range=all`, and `target_arn`.

State/persistence: pure in-memory conversion; no local persistence. The lifecycle of stale bandwidth series is handled in `scheduler.rs` tombstone logic, not here.

Dependencies/integration: depends on `PrometheusMetric` and bucket replication schema constants/descriptors. Called by the metrics runtime's bucket replication bandwidth task after `stats_collector` snapshots are collected.

Risks: high cardinality from `bucket` and `target_arn`; latency target stats include unused bandwidth fields, so callers must also feed `collect_bucket_replication_bandwidth_metrics` for bandwidth series. The capacity estimate uses `BASE_BUCKET_REPLICATION_METRICS_PER_BUCKET + targets.len()`, matching current latency-only target expansion.

Test signals: unit tests cover non-empty and empty replication detail output, label assertions for bucket and target ARN, proxied PUT and delete tagging metrics, and bandwidth limit/current metrics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/bucket_replication.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster.rs

Purpose: provides cluster-wide capacity and object/bucket count metric conversion. It is the base aggregate cluster collector for raw capacity, usable capacity, used/free bytes, stale/missing capacity observations, object count, and bucket count.

Important APIs/types: `ClusterStats` is a `Debug + Clone + Default` DTO with eight unsigned counters/gauges. `collect_cluster_metrics(&ClusterStats) -> Vec<PrometheusMetric>` is the sole exported collector function.

Control flow: the collector creates a fixed eight-element vector. Each field maps directly to one descriptor in `schema::cluster` through `PrometheusMetric::from_descriptor`, with numeric conversion to `f64` and no labels.

State/persistence: stateless conversion only. It does not read storage or cache data; callers populate `ClusterStats` from `stats_collector::collect_cluster_and_health_stats`.

Dependencies/integration: depends on `report::PrometheusMetric` and `schema::cluster::*`. The scheduler's cluster task combines this output with `collect_cluster_health_metrics` and passes the aggregate vector to `report_metrics`.

Risks: semantic correctness depends on caller-populated capacity values and consistent byte units. Unsigned `u64` to `f64` conversion can lose integer precision for very large byte totals, a common Prometheus client tradeoff. No labels means accidental per-node values would overwrite aggregate semantics.

Test signals: tests assert eight metrics, exact values for raw capacity/used/object/bucket metrics, zero/default behavior, empty label vectors, and default struct field values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_config.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_config.rs

Purpose: exposes storage class parity settings as Prometheus gauges, specifically reduced redundancy storage parity and standard storage parity.

Important APIs/types: `ClusterConfigStats` holds `rrs_parity` and `standard_parity` as `u32`. `collect_cluster_config_metrics` returns two metrics from `CONFIG_RRS_PARITY_MD` and `CONFIG_STANDARD_PARITY_MD`.

Control flow: fixed vector construction with direct field-to-descriptor mapping and no labels. The file is marked `#![allow(dead_code)]`, reflecting that this collector may be available before all runtime sources are wired in every build path.

State/persistence: no persistence or side effects. Runtime configuration is gathered elsewhere, then materialized as this DTO.

Dependencies/integration: depends on `PrometheusMetric` and `schema::cluster_config`. The supplementary cluster metrics scheduler task calls `collect_cluster_config_stats().await`, then emits these metrics only when that optional source returns `Some`.

Risks: zero is both the `Default` value and a possible placeholder for unavailable configuration, so absent data must be represented by not emitting metrics rather than passing defaults where possible. Gauge semantics are appropriate, but descriptor names must remain stable for dashboards.

Test signals: tests verify a two-metric output, expected values for non-default parity, and zero/default no-label behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_erasure_set.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_erasure_set.rs

Purpose: converts per-erasure-set topology, quorum, drive, tolerance, and health snapshots into labeled Prometheus gauges.

Important APIs/types: `ErasureSetStats` carries `pool_id`, `set_id`, set size, parity/data shards, read/write quorum, online/healing drive counts, health, read/write tolerance, and read/write health. `collect_erasure_set_metrics(&[ErasureSetStats])` emits metrics labeled by `pool_id` and `set_id`.

Control flow: preallocates `stats.len() * 12`, iterates each set, converts IDs to strings once, and pushes twelve gauge metrics using descriptors from `schema::cluster_erasure_set`. Labels are cloned across each metric to keep series distinguishable by pool and set.

State/persistence: stateless. The collector does not compute quorum or health; it trusts upstream `stats_collector::collect_erasure_set_stats`.

Dependencies/integration: used by the scheduler's supplementary cluster task. Descriptor label constants `POOL_ID_L` and `SET_ID_L` are imported from schema, reducing drift between schema declarations and emitted labels.

Risks: health fields are encoded as `u8` with comments saying 1 healthy and 0 unhealthy; no validation prevents other values. High pool/set counts increase series count linearly. Schema contains overall erasure-set descriptors that this collector does not emit, so future overall metrics need separate wiring.

Test signals: tests cover one-set output length of twelve, descriptor name/value checks for size and health, `report_metrics` compatibility, and empty-slice behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_erasure_set.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_health.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_health.rs

Purpose: reports cluster drive health counts: offline, online, and total drives.

Important APIs/types: `ClusterHealthStats` has three `u64` fields. `collect_cluster_health_metrics` maps those fields to `HEALTH_DRIVES_OFFLINE_COUNT_MD`, `HEALTH_DRIVES_ONLINE_COUNT_MD`, and `HEALTH_DRIVES_COUNT_MD`.

Control flow: fixed three-metric vector, no labels, direct conversion to `f64`.

State/persistence: no internal state. Upstream collection decides whether a drive is online/offline and computes totals.

Dependencies/integration: depends on `PrometheusMetric` and `schema::cluster_health`. The scheduler combines it with base cluster capacity metrics in the same cluster task.

Risks: caller must ensure `offline + online` equals `drives_count` if dashboards assume that invariant. Defaults produce zero-valued metrics, which can look like an empty healthy cluster if emitted before storage is initialized.

Test signals: tests assert three metrics, non-default offline/online values, and default zero/no-label behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_health.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_iam.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_iam.rs

Purpose: exposes IAM synchronization and plugin authentication service metrics, including sync durations, request/failure counts, age since last authn request, RTTs, and sync success/failure counts.

Important APIs/types: `IamStats` contains ten `u64` fields. `collect_iam_metrics(&IamStats)` returns ten descriptor-backed metrics from `schema::cluster_iam`.

Control flow: fixed vector conversion. Every field maps directly to one metric; there are no labels or conditional branches.

State/persistence: pure DTO conversion. Sync counters and timestamps are maintained by IAM/runtime sources outside this file.

Dependencies/integration: scheduler's supplementary cluster task calls `collect_iam_stats().await`; when it returns `Some`, these metrics are appended with cluster config, erasure set, and usage metrics before reporting.

Risks: mixed units are easy to confuse: duration fields are milliseconds, last authn request ages are seconds, RTT fields are milliseconds, and minute-window counters are counts for the last full minute. Dashboards and alerts must use descriptor help text and names rather than assuming a uniform unit.

Test signals: tests verify ten metrics, exact sync success descriptor/value, `report_metrics` compatibility, and zero/default behavior with empty labels.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_iam.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_usage.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_usage.rs

Purpose: converts cluster-wide and per-bucket usage statistics into Prometheus metrics for bytes, object counts, version counts, delete markers, quotas, and distribution buckets.

Important APIs/types: `ClusterUsageStats` holds aggregate totals plus object-size and version-count distributions. `BucketUsageStats` adds `bucket`, quota, and per-bucket distributions. Exported collectors are `collect_cluster_usage_metrics` and `collect_bucket_usage_metrics`.

Control flow: cluster collection preallocates base four metrics plus distribution lengths, emits total bytes/objects/versions/delete markers, then emits distribution samples labeled by `range`. Bucket collection iterates buckets, emits five bucket-labeled base metrics, then emits object size and version count distribution metrics labeled by `range` and `bucket`.

State/persistence: stateless conversion; persistent usage data and scan snapshots are read in upstream collectors.

Dependencies/integration: depends on `schema::cluster_usage` descriptors and label constants. Used by the supplementary cluster task when `collect_cluster_usage_metric_stats().await` returns a `(cluster_usage, bucket_usage)` pair.

Risks: bucket-level metrics scale by bucket count times distribution buckets. `quota_bytes = 0` is documented as no quota but still emitted, so dashboards must treat zero carefully. Distribution `range` strings are caller-provided and should be normalized to avoid cardinality/label drift.

Test signals: tests assert cluster output count of 11 for four object-size and three version ranges, descriptor presence for total bytes, and bucket output count of seven for one bucket with one distribution bucket each.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_usage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/dial9.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/dial9.rs

Purpose: provides telemetry for the dial9 Tokio runtime tracing subsystem itself. It always reports whether dial9 is enabled and conditionally reports event, bytes-written, rotation, error, CPU overhead, disk usage, and active session metrics.

Important APIs/types: `Dial9Stats`, `collect_dial9_metrics`, and `is_dial9_enabled`. Unlike most collectors in this directory, metrics are built with `PrometheusMetric::new` and hard-coded names rather than schema descriptors.

Control flow: `collect_dial9_metrics` reads the dial9 enabled flag via `is_dial9_enabled`, emits `rustfs_dial9_enabled`, and returns early when disabled. If enabled, it appends four counters and three gauges.

State/persistence: no stored state, but behavior depends on environment/config through `rustfs_config::{ENV_RUNTIME_DIAL9_ENABLED, DEFAULT_RUNTIME_DIAL9_ENABLED}` and `rustfs_utils::get_env_bool`.

Dependencies/integration: exported from `collectors/mod.rs`. It is not wired into the shown scheduler tasks, so integration likely depends on a separate dial9 runtime or future metrics task.

Risks: tests are environment-sensitive because detailed metric count depends on the enabled env/config value. Hard-coded metric descriptors bypass centralized schema, raising drift risk in naming/help/type conventions.

Test signals: tests cover default stat values, non-empty enabled flag output, and a value-populated path without asserting full count because dial9 may be disabled.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/dial9.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/ilm.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/ilm.rs

Purpose: reports Information Lifecycle Management task and scan metrics: expiry pending tasks, transition active/pending tasks, immediate transition misses, queue backpressure, compensation scheduling/running, and versions scanned.

Important APIs/types: `IlmStats` has nine `u64` fields. `collect_ilm_metrics(&IlmStats)` returns a nine-metric vector using descriptors from `schema::ilm`.

Control flow: direct fixed vector creation with no labels or conditional branches.

State/persistence: no local state. ILM scheduler/task state is collected elsewhere and passed in as a snapshot.

Dependencies/integration: the metrics scheduler's background workflow task calls `collect_ilm_metric_stats().await`; when present, ILM metrics are emitted together with scanner metrics.

Risks: several fields distinguish different transition enqueue/backpressure states; if upstream naming changes, descriptor mapping must stay semantically aligned. Default zero values can hide absence of ILM instrumentation if optional source handling is bypassed.

Test signals: tests assert nine metrics, representative pending/scanned values, and default zero/no-label behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/ilm.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/mod.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/mod.rs

Purpose: declares and re-exports all metrics collector modules and their public DTOs/functions, forming the main collector facade for `crate::metrics`.

Important APIs/types: module declarations include audit, bucket, bucket replication, cluster, cluster config, erasure set, health, IAM, usage, dial9, ILM, node, notification, notification target, replication, request, resource, scanner, CPU/drive/memory/network/process collectors, and feature-gated GPU. Re-exports expose each collector's stats type and collection function.

Control flow: compile-time module wiring only. `system_gpu` is included and re-exported under `#[cfg(feature = "gpu")]`.

State/persistence: no runtime state.

Dependencies/integration: `metrics/mod.rs` re-exports `collectors::*`, and `scheduler.rs` imports most collector functions/types through this facade. This file is the compatibility surface for code that expects `rustfs_obs::metrics::collectors::X` or `rustfs_obs::metrics::X`.

Risks: missing a re-export can make an implemented collector inaccessible to the scheduler or downstream crates. Feature-gated GPU paths must stay symmetric between `mod` declaration and `pub use`. Broad facade exports can preserve old APIs but also expand compile dependencies.

Test signals: no local tests; compile-time coverage comes from modules importing exported collector symbols, especially `scheduler.rs`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/node.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/node.rs

Purpose: emits per-node/per-disk capacity metrics for storage disks: total, used, and free bytes.

Important APIs/types: `DiskStats` contains `server`, `drive`, `total_bytes`, `used_bytes`, and `free_bytes`. `collect_node_metrics(&[DiskStats])` emits three metrics per disk.

Control flow: returns an empty vector for empty input. For each disk, clones server and drive labels as `Cow` values, then emits total/used/free descriptors with `server` and `drive` labels.

State/persistence: stateless conversion. Disk discovery and capacity observation happen in upstream stats collection.

Dependencies/integration: uses `schema::node_disk` descriptors. The node/disk scheduler task combines this output with detailed system drive metrics and aggregate drive count metrics.

Risks: label values include drive paths and server endpoints; changing formatting will create new Prometheus series. There is overlap with `system_drive.rs`, so dashboards should distinguish simple node disk capacity from richer system drive telemetry.

Test signals: tests cover two-disk output count, exact label/value matches, empty input, label presence on all metrics, and default DTO values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/notification.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/notification.rs

Purpose: converts aggregate notification subsystem counters/gauges into Prometheus metrics for current sends, error events, sent events, and skipped events.

Important APIs/types: `NotificationStats` with four `u64` fields and `collect_notification_metrics(&NotificationStats)`.

Control flow: fixed four-metric vector, no labels, direct mapping to descriptors from `schema::cluster_notification`.

State/persistence: stateless. Runtime notification counters are obtained through `rustfs_notify::notification_metrics_snapshot` in the scheduler.

Dependencies/integration: scheduler notification task builds `NotificationStats` from the snapshot, appends target-specific metrics from `notification_target.rs`, and reports the combined vector.

Risks: aggregate counts are unlabeled, so multiple notification subsystems would need explicit target-level metrics for attribution. Default zero output should not be emitted as a substitute for unavailable notification state unless intentionally desired.

Test signals: tests check four metrics, representative sent/error values, `report_metrics` compatibility, and default zero/no-label behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/notification.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/notification_target.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/notification_target.rs

Purpose: emits per-notification-target delivery metrics: failed messages, queue length, and total messages.

Important APIs/types: `NotificationTargetStats` carries `failed_messages`, `queue_length`, `target_id`, `target_type`, and `total_messages`. `collect_notification_target_metrics(&[NotificationTargetStats])` emits three metrics per target.

Control flow: returns empty for no targets. For each target, allocates owned `target_id` and `target_type` labels and emits failed, queue, and total descriptors with both labels.

State/persistence: stateless conversion; target queues/counters live in the notification subsystem.

Dependencies/integration: uses `schema::notification_target` descriptors and label constants. The scheduler obtains snapshots via `rustfs_notify::notification_target_metrics().await` and maps them into this DTO.

Risks: target IDs may include user or configuration-derived strings, so cardinality and stability matter. Queue length is a gauge while failed/total are counters; resets on process restart are expected.

Test signals: test verifies three metrics for one webhook target and asserts `target_id`/`target_type` labels on total message output.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/notification_target.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/replication.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/replication.rs

Purpose: reports cluster-wide replication queue, worker, transfer-rate, and backlog metrics.

Important APIs/types: `ReplicationStats` includes averages, current values, last-minute queued bytes/count, maximums, and recent backlog count. `collect_replication_metrics(&ReplicationStats)` emits thirteen metrics.

Control flow: fixed vector construction with no labels. Integer fields are converted to `f64`; rate/average fields already use `f64` or signed averages for queued bytes/count.

State/persistence: no local state. Historical averages and maximums are maintained by upstream replication monitoring.

Dependencies/integration: used in the scheduler's bucket replication bandwidth task after bandwidth/detail stats are collected. This places global replication metrics on the same interval as bucket replication bandwidth by default.

Risks: `average_queued_bytes` and `average_queued_count` are signed `i64`; negative values would be emitted if upstream produces them. Mixed metric semantics in one struct require careful descriptor maintenance. No labels means multi-site/target-specific replication must be represented elsewhere.

Test signals: tests assert thirteen outputs, exact active/current and average active worker values, `report_metrics` compatibility, and default zero/no-label behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/replication.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/request.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/request.rs

Purpose: converts API request snapshots into labeled metrics for request counts, in-flight requests, errors, cancellations, TTFB distribution buckets, and traffic bytes.

Important APIs/types: `ApiRequestStats` carries endpoint `name`, request `req_type`, counts, `ttfb_distribution: Vec<(String, f64)>`, and sent/received bytes. `collect_request_metrics(&[ApiRequestStats])` emits per-endpoint metrics.

Control flow: iterates stats, emitting six metrics labeled by `name` and `type`, then one TTFB distribution metric per `(le,value)` labeled by `name`, `type`, and `le`, then traffic sent/received metrics labeled only by `type`.

State/persistence: pure conversion. Request counters/latency buckets are maintained by API instrumentation outside this file.

Dependencies/integration: uses `schema::request` descriptors. This collector is exported by `collectors/mod.rs`; it is not directly visible in the shown scheduler tasks, so it may be used by HTTP handlers or another scrape path.

Risks: traffic metrics omit the API `name` label while request counters include it; this is intentional if traffic is aggregated by type but can surprise dashboards. Histogram/distribution values are reported through descriptor type semantics, so callers must pass cumulative bucket values if Prometheus histogram expectations apply.

Test signals: tests check a one-endpoint output count of twelve, exact total and in-flight values, `report_metrics` compatibility, and empty input behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/request.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/resource.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/resource.rs

Purpose: exposes simple RustFS process resource metrics: CPU percent, resident memory bytes, and uptime seconds.

Important APIs/types: `ResourceStats` and `collect_resource_metrics`. This is a compact process-resource collector separate from richer process/system collectors.

Control flow: returns a fixed three-metric vector using descriptors from `schema::process_resource`. CPU remains `f64`; memory and uptime convert from `u64`.

State/persistence: stateless. The scheduler obtains values through `collect_process_metric_bundle` and emits these at the resource interval.

Dependencies/integration: used by the system monitoring scheduler task when `now >= next_resource_run`, alongside full process metrics from `system_process.rs`.

Risks: CPU percentage is documented as possibly exceeding 100 on multi-core systems; alerts should not assume a 0-100 range. Some metrics overlap conceptually with process-specific schema metrics, so duplicate dashboard panels should use the intended namespace.

Test signals: tests cover normal values, zero/default values, CPU above 100, descriptor-name matches, `report_metrics` compatibility, and default field values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/resource.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/scanner.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/scanner.rs

Purpose: converts background scanner telemetry into a large fixed metric set covering scan totals, active paths, concurrency queues, throttle/yield configuration, bitrot cycle settings, current-cycle progress, last-cycle summary, failures, and partial-cycle reasons.

Important APIs/types: `ScannerStats` contains numerous fields for cumulative scan counts, current queue/active counts, boolean config, current cycle, last cycle, and partial reason counters. `collect_scanner_metrics(&ScannerStats)` emits 68 metrics. `bool_metric_value` converts booleans to 1.0/0.0.

Control flow: fixed vector literal maps each stat field to a schema descriptor. Most metrics are unlabeled. `SCANNER_PARTIAL_CYCLES_BY_REASON_MD` is emitted four times with `reason` labels `unknown`, `runtime`, `objects`, and `directories`.

State/persistence: no local state. It reports scanner runtime state supplied by `stats_collector::collect_scanner_metric_stats`.

Dependencies/integration: used by the scheduler background workflow task, combined with optional ILM metrics. It depends heavily on `schema::scanner` descriptor coverage.

Risks: large fixed mapping is easy to desynchronize when `ScannerStats` or schema evolves. Numeric enums (`current_scan_mode`, `last_cycle_result`, `last_cycle_partial_reason`) need external documentation. A default struct emits 68 zero metrics, which may mask disabled/unavailable scanner collection if optional source checks are not preserved.

Test signals: unusually strong tests assert 68 metrics, many exact descriptor/value pairs, labeled partial reasons, and default zero behavior including reason label validation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/scanner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_cpu.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_cpu.rs

Purpose: emits system CPU metrics and process CPU metrics. System metrics include average idle/iowait, load average, load percentage, nice, steal, system, and user percentages; process metrics include usage and utilization.

Important APIs/types: `CpuStats`, `ProcessCpuStats`, `collect_cpu_metrics`, and `collect_process_cpu_metrics`. Process collection accepts optional static-label slices, typically process PID/name labels from scheduler.

Control flow: `collect_cpu_metrics` returns eight descriptor-backed metrics. `collect_process_cpu_metrics` creates usage and utilization metrics, extends labels when supplied, and returns both.

State/persistence: stateless conversion. System data comes from `stats_collector::collect_system_cpu_and_memory_stats_with`; process CPU comes from `ProcessMetricBundle`.

Dependencies/integration: scheduler's system monitoring task emits system CPU at `system_interval` and process CPU at the same system-monitoring pass, while simple resource CPU is emitted at the resource interval.

Risks: process labels must remain low-cardinality; scheduler intentionally uses PID and executable name. CPU units and multi-core semantics differ between `usage` and `utilization`; consumers should read descriptor help.

Test signals: tests assert eight system CPU metrics with `rustfs_system_cpu_` prefix, default zeros, two process CPU metrics, values for usage/utilization, and label propagation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_cpu.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_drive.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_drive.rs

Purpose: emits detailed per-drive telemetry, aggregate drive counts, and process disk I/O metrics.

Important APIs/types: `DriveDetailedStats`, `DriveCountStats`, `ProcessDiskStats`, `collect_drive_detailed_metrics`, `collect_drive_count_metrics`, and `collect_process_disk_metrics`. Detailed stats include capacity, observation state/age, inodes, errors, waiting I/O, latency, health, read/write rates, awaits, and utilization.

Control flow: detailed collection uses an inner `push_drive_metric` helper to attach `drive` and `server` labels. It emits 23 metrics per drive, including three one-hot `capacity_observation_state` samples for `live`, `stale`, and `missing`. Drive count emits three unlabeled metrics. Process disk emits one metric twice with `direction=read/write` plus optional process labels.

State/persistence: stateless conversion. Observation freshness and disk I/O rates are computed upstream.

Dependencies/integration: the scheduler node/disk task combines detailed drive, aggregate count, and simpler node disk metrics. The system monitoring task emits process disk I/O as part of process labels.

Risks: drive paths/server labels drive series cardinality and churn. The capacity observation state is a caller-provided `&'static str`; unrecognized values result in all three known states being 0. Process disk metric uses one descriptor with a direction label.

Test signals: tests assert 23 detailed metrics for one drive, exact total bytes, and three drive count metrics with offline value. Process disk behavior is indirectly used by scheduler/system tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_drive.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_gpu.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_gpu.rs

Purpose: optional GPU collector for process GPU memory usage through NVML. It is feature-gated in `collectors/mod.rs` and used by scheduler only under `#[cfg(feature = "gpu")]`.

Important APIs/types: `GpuStats`, `GpuError`, `GpuCollector`, `GpuCollector::new`, `GpuCollector::collect`, and `collect_gpu_metrics`. `GpuError` uses `thiserror::Error` for init/device/process-not-found variants.

Control flow: `new` initializes NVML and stores the monitored PID. `collect` reads device index 0, iterates running compute processes, returns memory bytes for matching PID, maps unavailable memory to 0, logs a warning if process stats are unavailable, returns device error when no GPU device is found, and otherwise returns zero usage when the process is not listed. `collect_gpu_metrics` emits one process GPU memory metric with caller labels.

State/persistence: stores an NVML handle and PID inside `GpuCollector`; no persistent files.

Dependencies/integration: depends on `nvml_wrapper`, `sysinfo::Pid`, `tracing`, and `schema::system_gpu`. Scheduler initializes the collector inside each system interval pass, which may be expensive but isolates failures.

Risks: only device index 0 is inspected, so multi-GPU processes may be underreported. NVML availability and permissions can fail. `ProcessNotFound` exists but current `collect` returns zero instead of that error for absent process.

Test signals: tests cover default stats and display formatting for all error variants, but not real NVML collection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_gpu.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_memory.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_memory.rs

Purpose: emits system memory metrics and process memory metrics.

Important APIs/types: `MemoryStats` includes total, used, used percentage, free, buffers, cache, shared, and available bytes. `ProcessMemoryStats` includes resident and virtual memory. Exported collectors are `collect_memory_metrics` and `collect_process_memory_metrics`.

Control flow: system memory returns eight descriptor-backed metrics. Process memory creates resident and virtual metrics and extends optional labels.

State/persistence: stateless conversion. Values are sourced from sysinfo-backed collection in `stats_collector` and process metric bundles.

Dependencies/integration: scheduler's system monitoring task emits system memory with CPU/network/disk process metrics and labels process memory with PID/name.

Risks: Linux memory concepts such as buffers/cache/shared/available may vary by platform and sysinfo behavior. There is overlap between process memory metrics emitted here and full process stats in `system_process.rs`, so descriptor naming must avoid duplicate incompatible samples.

Test signals: tests assert eight system metrics with `rustfs_system_memory_` prefix, default zeros, two process memory metrics, and optional label propagation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_memory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_network.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_network.rs

Purpose: emits internode network metrics for RustFS cluster communication: failed internode calls, dial errors, average dial time, sent bytes, and received bytes.

Important APIs/types: `NetworkStats` and `collect_network_metrics`.

Control flow: fixed five-metric vector with no labels. All fields are direct conversions from the DTO.

State/persistence: no local state. Upstream `collect_internode_network_stats` provides optional snapshots.

Dependencies/integration: scheduler runs an internode/system network task at `system_interval`; if optional stats exist and metrics are non-empty, it reports them.

Risks: average dial time is in nanoseconds while other values are counts/bytes, so descriptor units matter. Unlabeled aggregate output cannot distinguish peers or endpoints; detailed peer metrics would require a separate collector.

Test signals: tests assert five metrics, all names containing `internode`, `report_metrics` compatibility, and default zero/no-label behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_network.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_network_host.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_network_host.rs

Purpose: emits host-wide network I/O totals and per-interface counters.

Important APIs/types: `HostNetworkStats` with total received/transmitted and `per_interface: Vec<(String,u64,u64)>`. `collect_host_network_metrics` accepts optional labels but scheduler passes `None` because interface counters are host-wide.

Control flow: preallocates two total metrics plus two per interface. Total metrics share `HOST_NETWORK_IO_MD` with `direction=received/transmitted`. Per-interface metrics use `HOST_NETWORK_IO_PER_INTERFACE_MD` with `interface` and `direction`, plus optional labels.

State/persistence: stateless. Network counters come from host collection in `stats_collector`.

Dependencies/integration: called by `collect_system_monitoring_metrics`. The scheduler comment explicitly avoids process labels for interface counters.

Risks: interface names can churn in containerized environments and create new series. Optional labels are powerful but dangerous if used with process-specific labels for host-wide values.

Test signals: test verifies four metrics for one interface and asserts the dedicated `rustfs_system_network_host_` prefix.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_network_host.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_process.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_process.rs

Purpose: emits detailed RustFS process metrics and provides process attribute collection for labels.

Important APIs/types: `ProcessAttributes`, `ProcessAttributeError`, `ProcessStatusType`, `ProcessStats`, `collect_process_metrics`, and `collect_process_attributes`. `ProcessAttributes::current` and `from_pid` query sysinfo for PID/name/path/cmd. `ProcessStatusType` normalizes `sysinfo::ProcessStatus`.

Control flow: `collect_process_metrics` creates seventeen descriptor-backed process metrics plus a status metric labeled with the debug string of `ProcessStatusType`. `from_pid` refreshes only the requested process, errors when unavailable, and joins command args into a string. `to_labels` returns four labels: PID, executable name, executable path, and command.

State/persistence: no persistent state, but it queries live process metadata via sysinfo. Scheduler uses a smaller label set through `current_process_metric_labels`, currently PID and executable name, with fallback on error.

Dependencies/integration: system monitoring scheduler emits full process metrics at the resource interval and uses process attributes for process CPU/memory/disk/GPU labels.

Risks: full `process_command` and executable path can be high-cardinality or sensitive if used as labels; scheduler avoids them in its current helper. Status metric uses a numeric value plus string label, so value/label conventions must stay stable.

Test signals: tests assert eighteen metrics, representative uptime/file descriptor/status values, default metric count, current process attribute collection, status conversion, and label formatting.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_process.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/config.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/config.rs

Purpose: centralizes public environment variable names and default intervals for metrics collection categories.

Important APIs/types: constants for default, cluster, bucket, node, resource, audit, notification, and bucket replication bandwidth intervals. Defaults are `Duration` values: 60s cluster/node, 300s bucket, 15s resource/audit/notification, and 30s replication bandwidth.

Control flow: constants only; parsing is implemented in `scheduler.rs`.

State/persistence: no state. Values are compile-time defaults used by runtime configuration.

Dependencies/integration: `scheduler.rs` imports these constants into `configured_metrics_runtime_config`, combines them with primary/legacy env var parsing, and exposes effective values in runtime snapshots.

Risks: the global `DEFAULT_METRICS_INTERVAL` is marked dead code but the env key is used as a fallback in scheduler parsing. Changing names breaks deployment configuration. Bucket default is intentionally longer due to cost and should not be casually reduced.

Test signals: no local tests; scheduler snapshot tests indirectly validate interval propagation when using fixed configs, and env parsing logic is concentrated in scheduler.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/mod.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/mod.rs

Purpose: top-level metrics module facade for RustFS observability. It declares metrics submodules and re-exports the collector, config, reporting, and runtime scheduler APIs.

Important APIs/types: modules `collectors`, `config`, `report`, `scheduler`, `schema`, and `stats_collector`. Re-exports include `PrometheusMetric`, `report_metrics`, collector/config items, and scheduler runtime controller/status types and init functions.

Control flow: compile-time module organization only.

State/persistence: no state.

Dependencies/integration: downstream code can import metrics APIs from `crate::metrics::*` instead of individual submodules. Scheduler runtime types exported here are likely used by service status/admin endpoints.

Risks: broad `pub use collectors::*` and `pub use config::*` make many internals part of the crate API. Removing or renaming exports can break downstream modules even if implementation still exists. `stats_collector` is declared but not publicly glob-re-exported here.

Test signals: no local tests; compile-time usage across the crate validates the facade.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/report.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/report.rs

Purpose: defines the intermediate `PrometheusMetric` representation and the `report_metrics` bridge that registers/describes metrics through the `metrics` crate macros.

Important APIs/types: `PrometheusMetric` with name/type/help/labels/value, constructors `new`, `new_owned`, `from_descriptor`, and label builders `with_label`, `with_label_owned`, `with_labels`. `report_metrics(&[PrometheusMetric])` emits to the global metrics recorder. Static `NAME_CACHE` and `HELP_CACHE` intern dynamic names/help as leaked `'static` strings.

Control flow: `report_metrics` interns name/help, describes the metric based on `MetricType`, converts labels to owned `(String,String)` pairs, then records counters using `absolute(metric.value as u64)`, gauges with `set`, and histograms with `record`.

State/persistence: process-local caches store interned strings forever. This avoids lifetime issues for metrics macros but can grow if metric names/help are unbounded.

Dependencies/integration: all collectors return `PrometheusMetric`; scheduler calls `report_metrics` after each collection batch.

Risks: counter values are cast to `u64`, truncating floats and wrapping/saturating semantics depending on Rust cast behavior for invalid values; callers should supply non-negative whole counter values. Dynamic metric names can leak memory through intern caches. Histogram handling records values rather than explicit bucket counts, so distribution collectors must align with `metrics` crate semantics.

Test signals: test verifies `from_descriptor` generates full Prometheus names for counter/gauge/histogram descriptor cases.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/report.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/scheduler.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/scheduler.rs

Purpose: initializes and supervises the background metrics runtime. It parses intervals, exposes runtime status/controller snapshots, and spawns asynchronous collection loops for cluster, bucket, node/disk, replication, audit, notification, background workflow, system/process, and internode network metrics.

Important APIs/types: `MetricsRuntimeServiceState`, cancellation/shutdown enums, interval/status/desired/controller snapshots, `MetricsRuntimeController`, `MetricsRuntimeConfig`, `init_metrics_runtime`, `init_metrics_collectors`, `metrics_runtime_status_snapshot`, and `metrics_runtime_controller_snapshot`. Replication bandwidth tombstone helpers manage zero emission for removed `(bucket,target_arn)` series.

Control flow: configuration parsing prioritizes primary env, legacy env, default env, legacy default, then hard-coded default. `init_metrics_runtime` captures config and spawns ten Tokio tasks. Each task uses `tokio::select!` between interval ticks and cancellation token. Collection tasks gather stats through `stats_collector` or external crates, convert through collectors, and call `report_metrics`. System monitoring uses deadlines to multiplex resource/system intervals on one loop.

State/persistence: no persistent files. Runtime state lives in spawned tasks, cancellation token status, process-local tombstone maps/sets, sysinfo `System`, and interned metric caches in `report.rs`.

Dependencies/integration: integrates with `rustfs_audit`, `rustfs_notify`, `rustfs_ecstore`, `rustfs_utils`, `tokio`, `tokio_util`, `sysinfo`, `tracing`, collectors, schema descriptors, and stats collection functions.

Risks: all tasks are spawned without handles, so cancellation is token-based only. First `tokio::time::interval` tick fires immediately, which is usually desired but can create startup load. Tombstone logic depends on monitor availability to avoid expiring/removing series during outages. GPU collector initialization happens during system intervals when feature-enabled. Large collector batches can block a task until collection/reporting completes.

Test signals: tests cover status disabled/running/stopping snapshots, controller reconciliation idempotence, deadline advancement including missed intervals, and replication bandwidth tombstone creation, zero metrics, expiry, live-key revival, and monitor-unavailable behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/scheduler.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/audit.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/audit.rs

Purpose: defines audit target metric descriptors and shared status/result label constants.

Important APIs/types: constants `RESULT`, `STATUS`, `SUCCESS`, and `FAILURE`; private `TARGET_ID`; descriptors `AUDIT_FAILED_MESSAGES_MD`, `AUDIT_TARGET_QUEUE_LENGTH_MD`, and `AUDIT_TOTAL_MESSAGES_MD`.

Control flow: each descriptor is a `LazyLock<MetricDescriptor>` initialized through `new_counter_md` or `new_gauge_md` with `subsystems::AUDIT` and `target_id` label.

State/persistence: descriptors are lazily initialized process-wide. No mutable state after initialization.

Dependencies/integration: audit collector uses these descriptors to convert audit target snapshots, and scheduler obtains raw snapshots from `rustfs_audit::audit_target_metrics`.

Risks: `TARGET_ID` is private while descriptors include it, so collectors in other modules cannot import the label constant from schema and may duplicate the string unless specifically designed around it. Public `RESULT/STATUS/SUCCESS/FAILURE` are not used in this file's descriptors, suggesting broader audit schema usage or leftovers.

Test signals: no local tests; collector tests and compile-time descriptor use provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/audit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/bucket.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/bucket.rs

Purpose: defines bucket API metric descriptors for bucket-scoped traffic, request counts, error counts, cancellation counts, in-flight requests, and TTFB distribution.

Important APIs/types: descriptors include `BUCKET_API_TRAFFIC_SENT_BYTES_MD`, `BUCKET_API_TRAFFIC_RECV_BYTES_MD`, `BUCKET_API_REQUESTS_IN_FLIGHT_MD`, `BUCKET_API_REQUESTS_TOTAL_MD`, `BUCKET_API_REQUESTS_CANCELED_MD`, `BUCKET_API_REQUESTS_4XX_ERRORS_MD`, `BUCKET_API_REQUESTS_5XX_ERRORS_MD`, and `BUCKET_API_REQUESTS_TTFB_SECONDS_DISTRIBUTION_MD`.

Control flow: each descriptor is lazily built using `new_counter_md`, `new_gauge_md`, or `new_histogram_md` with `subsystems::BUCKET_API`. Labels include combinations of `bucket`, `name`, `type`, and histogram `le`.

State/persistence: lazy descriptor initialization only.

Dependencies/integration: used by the bucket API collector outside this work item and by any request/bucket reporting path that wants bucket-scoped API metrics.

Risks: help strings for traffic sent/recv appear swapped in wording: sent bytes help says bytes received, and recv bytes help says bytes sent. Histogram descriptor includes `le`, but `report_metrics` records histogram values through the metrics crate rather than exporting fixed bucket samples, so schema/collector semantics should be checked together.

Test signals: no local schema tests; bucket collector tests elsewhere likely assert descriptor-derived names and label behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/bucket.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/bucket_replication.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/bucket_replication.rs

Purpose: defines descriptor schema and label constants for bucket replication metrics: failures, latency, proxied operations, replicated bytes/count, and bandwidth.

Important APIs/types: label constants `BUCKET_L`, `OPERATION_L`, `TARGET_ARN_L`, and `RANGE_L`; descriptors for last-hour/last-minute failures, total failures, sent bytes/count, proxied GET/HEAD/PUT/tagging/delete-tagging totals/failures, latency, bandwidth limit, and current bandwidth.

Control flow: each descriptor is a `LazyLock<MetricDescriptor>` built with `new_counter_md` or `new_gauge_md`. Most metrics are bucket-labeled; latency includes bucket, operation, range, and target ARN; bandwidth includes bucket and target ARN. Two proxied PUT metric names are constructed via local string constants and `MetricName::from`.

State/persistence: lazy immutable descriptors only.

Dependencies/integration: consumed by `collectors/bucket_replication.rs` and by scheduler tombstone zero metrics. Uses `subsystems::BUCKET_REPLICATION`.

Risks: high-cardinality `target_arn` labels must be stable. Some last-minute/hour failure descriptors are gauges while total failures/sent/proxied operations are counters; callers must respect time-window semantics. Descriptor count is large, increasing maintenance risk when adding new proxied operations.

Test signals: collector tests assert several descriptor-derived metric names and labels, including bandwidth and delete-tagging metrics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/bucket_replication.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster.rs

Purpose: defines base cluster aggregate metric descriptors for capacity and object/bucket counts.

Important APIs/types: eight gauge descriptors: raw total capacity, usable total capacity, used bytes, free bytes, stale capacity drives, missing capacity drives, objects total, and buckets total.

Control flow: each `LazyLock` calls `new_gauge_md` with either `MetricName::Custom(...)` for capacity/count names and no labels, using `subsystems::CLUSTER_BASE_PATH`.

State/persistence: lazy descriptor initialization only.

Dependencies/integration: consumed by `collectors/cluster.rs`, then reported by the scheduler cluster task.

Risks: descriptors use custom metric names rather than dedicated enum variants for these aggregate names, so string stability is critical. All metrics are gauges; object and bucket totals are current snapshots, not monotonic counters. No labels means these must represent whole-cluster values.

Test signals: cluster collector tests validate descriptor-derived names and values for representative metrics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_config.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_config.rs

Purpose: defines metric descriptors for cluster storage-class parity configuration.

Important APIs/types: `CONFIG_RRS_PARITY_MD` and `CONFIG_STANDARD_PARITY_MD`, both gauges with no labels under `subsystems::CLUSTER_CONFIG`.

Control flow: lazy descriptor construction through `new_gauge_md` and `MetricName::ConfigRRSParity` / `MetricName::ConfigStandardParity`.

State/persistence: lazy immutable descriptors only.

Dependencies/integration: consumed by `collectors/cluster_config.rs`, conditionally emitted by the scheduler's supplementary cluster task when config stats are available.

Risks: configuration metrics are gauges but represent static/effective config; if config reloads are supported, upstream must refresh values. Absence should be modeled by not emitting rather than emitting default zero.

Test signals: collector tests validate output count and values for both parity descriptors.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_erasure_set.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_erasure_set.rs

Purpose: defines descriptors and labels for erasure set topology, quorum, drive count, tolerance, and health metrics.

Important APIs/types: label constants `POOL_ID_L` and `SET_ID_L`; descriptors for set size, parity, data shards, overall write quorum, overall health, read/write quorum, online/healing drive count, health, read/write tolerance, and read/write health.

Control flow: descriptors are `LazyLock<MetricDescriptor>` values built with `new_gauge_md`. Most descriptors include `[POOL_ID_L, SET_ID_L]`; overall descriptors are unlabeled.

State/persistence: lazy immutable descriptor initialization only.

Dependencies/integration: per-set descriptors are used by `collectors/cluster_erasure_set.rs`. Overall descriptors are defined but not emitted by that collector in the reviewed code.

Risks: comment for `SET_ID_L` says "pool ID", a documentation copy/paste issue. Overall descriptors without collector wiring can confuse maintainers expecting all schema entries to be emitted. Health values are numeric gauges, so conventions must be documented.

Test signals: erasure set collector tests validate size/health descriptors and label-producing collection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_erasure_set.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_health.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_health.rs

Purpose: defines cluster drive health count descriptors.

Important APIs/types: `HEALTH_DRIVES_OFFLINE_COUNT_MD`, `HEALTH_DRIVES_ONLINE_COUNT_MD`, and `HEALTH_DRIVES_COUNT_MD`, all gauges with no labels under `subsystems::CLUSTER_HEALTH`.

Control flow: lazy descriptor construction through `new_gauge_md` and `MetricName` enum variants for offline, online, and total drive counts.

State/persistence: lazy immutable descriptors only.

Dependencies/integration: used by `collectors/cluster_health.rs`; scheduler emits these with base cluster metrics.

Risks: all metrics are unlabeled cluster-wide snapshots. Consumers may infer total from offline+online, but schema exposes total separately and upstream must keep values consistent.

Test signals: cluster health collector tests validate count and representative values, plus default no-label zero behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_health.rs -->
