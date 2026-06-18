# Research Report: subset-b-008273

This grouped report covers the RustFS observability metrics schema, metrics sampling bridge, and selected telemetry setup files listed for `subset-b-008273`. Each file section is bounded by reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_iam.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_iam.rs

## Purpose
Defines the metric descriptors for cluster IAM synchronization and plugin authentication metrics. The file is schema-only: it names the IAM Prometheus metrics, their metric type, help text, label set, namespace, and subsystem.

## Important APIs, Types, and Functions
Exports ten `pub static LazyLock<MetricDescriptor>` values: `LAST_SYNC_DURATION_MILLIS_MD`, seven plugin authn service metrics, `SINCE_LAST_SYNC_MILLIS_MD`, `SYNC_FAILURES_MD`, and `SYNC_SUCCESSES_MD`. Every descriptor is built with `new_counter_md`, `MetricName::*`, and `subsystems::CLUSTER_IAM`, with no variable labels.

## Control Flow
Each descriptor is lazily initialized on first use. Initialization calls the shared descriptor factory, which binds the RustFS namespace, counter type, IAM subsystem, and static help text. There is no runtime branching after lazy initialization.

## State and Persistence
The file owns no metric values and persists nothing. State exists only as lazily initialized descriptor metadata. Runtime values come from `collect_iam_stats()` in `stats_collector.rs`, which reads global IAM sync and OIDC plugin authn snapshots.

## Dependencies and Integration Points
Depends on `MetricDescriptor`, `MetricName`, `new_counter_md`, and `subsystems`. The collector side imports these descriptors in `metrics/collectors/cluster_iam.rs` and converts sampled `IamStats` fields into `PrometheusMetric` values with matching names.

## Risks
Several metrics with time-like names are counters even though they represent durations or "seconds since" values, which may confuse Prometheus consumers. Because no labels are declared, collector code must not attach dimensions. Any mismatch between `MetricName::as_str()` and dashboard expectations changes exported metric names.

## Test Signals
There are no direct tests in this file. Indirect coverage exists through descriptor factory tests and collector tests that call `get_full_metric_name()`. Useful additional tests would assert all IAM descriptor names and types against expected Prometheus names.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_iam.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_notification.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_notification.rs

## Purpose
Provides cluster-level notification metric descriptors for asynchronous event delivery. It distinguishes an in-progress gauge from total sent, skipped, and errored event counters.

## Important APIs, Types, and Functions
Exports four `LazyLock<MetricDescriptor>` values: `NOTIFICATION_CURRENT_SEND_IN_PROGRESS_MD`, `NOTIFICATION_EVENTS_ERRORS_TOTAL_MD`, `NOTIFICATION_EVENTS_SENT_TOTAL_MD`, and `NOTIFICATION_EVENTS_SKIPPED_TOTAL_MD`. The first uses `new_gauge_md`; the others use `new_counter_md`. All use `subsystems::NOTIFICATION` and no labels.

## Control Flow
The file has no active control flow beyond lazy descriptor construction. Descriptor creation follows the shared factories and resolves metric names through `MetricName::Notification*`.

## State and Persistence
No runtime values or persistence are managed here. The actual counters and gauges are supplied by notification collector/runtime stats.

## Dependencies and Integration Points
Depends on the common schema entry layer. `metrics/collectors/notification.rs` imports these descriptors and emits `PrometheusMetric` values from notification stats. The names compose to `rustfs_notification_*`.

## Risks
The file only covers aggregate notification metrics; per-target queue and failure metrics live in `notification_target.rs`. Dashboards must combine both files to get full notification visibility. Naming and label-free descriptors make future per-target expansion a breaking metric shape change if done in place.

## Test Signals
No local tests. The main verification path is collector tests or descriptor snapshot checks for full metric names and metric types.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_notification.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_usage.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_usage.rs

## Purpose
Defines metric descriptors for cluster-wide object usage and per-bucket usage. It covers byte totals, object/version/delete-marker counts, bucket counts, quotas, and distribution buckets.

## Important APIs, Types, and Functions
Exports label constants `BUCKET_LABEL` and `RANGE_LABEL`, plus `LazyLock<MetricDescriptor>` descriptors for cluster object metrics under `CLUSTER_USAGE_OBJECTS` and bucket metrics under `CLUSTER_USAGE_BUCKETS`. Distribution metrics declare `range`; per-bucket metrics declare `bucket`; per-bucket distributions declare both `range` and `bucket`.

## Control Flow
Each descriptor is lazily constructed with `new_gauge_md`. There is no behavior besides descriptor metadata creation.

## State and Persistence
No values are stored here. Values are derived in `collect_cluster_usage_metric_stats()` from persisted backend data-usage snapshots loaded through `load_data_usage_from_backend()`, plus per-bucket quota config lookups.

## Dependencies and Integration Points
Used by `metrics/collectors/cluster_usage.rs`, which converts `ClusterUsageStats` and `BucketUsageStats` into Prometheus metrics and applies labels matching these descriptors. Integrated with `MetricName` mappings such as `UsageTotalBytes`, `UsageBucketObjectSizeDistribution`, and `UsageVersionCountDistribution`.

## Risks
Distribution labels must be ordered consistently with collector label insertion. Hidden buckets beginning with `.` are filtered by the collector, not by this schema. Usage data is snapshot-based, so metrics can lag actual object changes. A stale or missing backend usage file causes the collector to return no usage metrics.

## Test Signals
No direct tests in the schema. Collector-level tests check representative full names. Stronger coverage would assert descriptor label sets and all expected distribution labels.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_usage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/descriptor.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/descriptor.rs

## Purpose
Defines `MetricDescriptor`, the common metadata object used by all schema modules to describe exported Prometheus metrics.

## Important APIs, Types, and Functions
`MetricDescriptor` stores `name`, `metric_type`, `help`, `variable_labels`, `namespace`, and `subsystem`. `MetricDescriptor::new()` constructs descriptors. `get_full_metric_name()` returns Prometheus-style `<namespace>_<subsystem>_<name>`. `has_label()` and `get_label_set()` lazily build and query a `HashSet<String>` from `variable_labels`.

## Control Flow
Construction is direct. Full-name generation calls `MetricNamespace::as_str()`, `MetricSubsystem::as_str()`, and `MetricName::as_str()`. Label lookup initializes `label_set` only once, then reuses it.

## State and Persistence
The only mutable state is the private `label_set` cache, which requires `&mut self` to populate. There is no persistence. Because descriptors are generally held in `LazyLock`, callers needing `has_label()` must account for mutable access constraints.

## Dependencies and Integration Points
Used by all schema descriptor modules and by collectors through `PrometheusMetric::from_descriptor`. It depends on the schema entry enums for names, namespaces, subsystems, and metric types.

## Risks
`get_full_metric_name()` always includes namespace and subsystem, so empty or malformed custom subsystem paths can create unexpected names. `MetricSubsystem::as_str()` allocates a `String`; repeated name construction can allocate. The mutable label cache may be awkward for static descriptors if more validation code is added.

## Test Signals
Tests assert full metric names for built-in and custom subsystems, including that metric type prefixes are not inserted. There is no test for `has_label()` caching behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/descriptor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/metric_name.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/metric_name.rs

## Purpose
Centralizes the metric-name vocabulary for RustFS observability. Every schema descriptor points at a `MetricName` variant or uses `MetricName::Custom` for ad hoc names.

## Important APIs, Types, and Functions
`MetricName` is a large enum covering generic counters, byte counters, latency metrics, API request metrics, audit/config/erasure/health/IAM/notification/usage/ILM/replication/scanner/system/process metrics, and `Custom(String)`. `MetricName::as_str()` maps each variant to the final metric-name suffix. `From<String>` and `From<&str>` create `Custom` names.

## Control Flow
The implementation is a single exhaustive `match` in `as_str()`. Descriptor factories call this indirectly through `MetricDescriptor::get_full_metric_name()`. Custom names bypass validation and are returned unchanged.

## State and Persistence
The enum stores no runtime metric values. `Custom(String)` carries caller-provided name state in descriptors. There is no persistence.

## Dependencies and Integration Points
Every schema module imports this enum. Collectors depend on the suffix strings remaining stable because full Prometheus names are composed from namespace, subsystem, and these suffixes.

## Risks
This file is a high-blast-radius naming contract. Typographical changes or duplicate-seeming suffixes can silently break dashboards and alert rules. `Custom` allows invalid Prometheus suffixes unless callers self-police. Some names preserve legacy terminology such as Go routines, and some type semantics are determined outside this file.

## Test Signals
No local tests cover the full mapping. Descriptor tests exercise a few names such as `ApiRequestsTotal` and `TtfbDistribution`. A generated snapshot test for all variant suffixes would be valuable.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/metric_name.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/metric_type.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/metric_type.rs

## Purpose
Defines the small enum representing metric kind: counter, gauge, or histogram.

## Important APIs, Types, and Functions
`MetricType` has variants `Counter`, `Gauge`, and `Histogram`. `as_str()` returns plain text type names. `as_prom()` returns type-specific prefixes with trailing dots, although comments indicate this is an approximation for Prometheus client concepts.

## Control Flow
Both methods are simple matches. The main schema factories embed `MetricType` values into `MetricDescriptor`.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
Used by descriptor factories, descriptors, and downstream conversion to `PrometheusMetric`. Actual exposition type behavior depends on collector/report code, not only this enum.

## Risks
`as_prom()` returns strings like `counter.` and is marked dead code; if used later, the trailing dot contract needs validation. Histograms are not currently wired by the public schema modules in this subset except through the factory test, and some histogram-like descriptors are defined as counters or gauges.

## Test Signals
No tests in this file. The `entry/mod.rs` histogram factory test checks that a histogram descriptor stores `MetricType::Histogram`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/metric_type.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/mod.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/mod.rs

## Purpose
Provides the public entry point for metric schema primitives and shared descriptor factory helpers.

## Important APIs, Types, and Functions
Declares submodules `descriptor`, `metric_name`, `metric_type`, `namespace`, `path_utils`, and `subsystem`. Exports factory functions `new_counter_md`, `new_gauge_md`, and `new_histogram_md`. Each factory accepts a metric name, help text, label slice, and subsystem, then creates a `MetricDescriptor` in the `RustFS` namespace.

## Control Flow
Factories convert labels from `&[&str]` to `Vec<String>`, coerce names and subsystems via `Into`, and call `MetricDescriptor::new()` with the appropriate `MetricType`.

## State and Persistence
No state is owned here. Factories return descriptor values that are usually stored in `LazyLock` statics by schema modules.

## Dependencies and Integration Points
This file is the primary dependency of all schema modules. It hides namespace choice and reduces descriptor boilerplate. `schema/mod.rs` re-exports these factories and primitive types.

## Risks
All factory-created descriptors are forced into the `RustFS` namespace; any future multi-namespace metrics need new APIs. The histogram helper is currently `allow(dead_code)` and may not be exercised by runtime collectors.

## Test Signals
The test validates histogram factory output, labels, namespace, subsystem formatting, full metric name generation, and custom subsystem path formatting.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/namespace.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/namespace.rs

## Purpose
Defines the top-level metric namespace enum.

## Important APIs, Types, and Functions
`MetricNamespace` currently has one variant, `RustFS`. `as_str()` maps it to `rustfs`.

## Control Flow
`as_str()` is a simple match and is called during full metric name construction.

## State and Persistence
No runtime state or persistence.

## Dependencies and Integration Points
Used by `MetricDescriptor` and all factory-created descriptors. It fixes the first segment of exported metric names.

## Risks
The one-namespace design is simple but inflexible. Adding another namespace later requires updating factories or adding new factory variants; otherwise everything remains `rustfs_*`.

## Test Signals
No local tests. Descriptor tests indirectly verify `RustFS` maps to `rustfs`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/namespace.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/path_utils.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/path_utils.rs

## Purpose
Normalizes subsystem path strings into Prometheus metric-name segments.

## Important APIs, Types, and Functions
`format_path_to_metric_name(path: &str) -> String` trims leading `/` characters and replaces `/` and `-` with `_`.

## Control Flow
The function is a pure string transformation. `MetricSubsystem::as_str()` calls it for built-in and custom subsystem paths.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
Used only by `subsystem.rs`. It controls the subsystem segment in `MetricDescriptor::get_full_metric_name()`.

## Risks
The normalization does not validate Prometheus identifier characters beyond slash and dash replacement. Spaces, dots, uppercase letters, or other punctuation in custom subsystem paths pass through unchanged.

## Test Signals
Tests cover leading slash trimming and slash/dash replacement for API, network, bucket, and cluster examples.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/path_utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/subsystem.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/subsystem.rs

## Purpose
Defines metric subsystems, their canonical URL-like paths, and convenience constants used by descriptor modules.

## Important APIs, Types, and Functions
`MetricSubsystem` enumerates API, bucket, system, debug, cluster, ILM, audit, replication, notification, scanner, and `Custom(String)` subsystems. `path()` returns canonical path strings, `as_str()` normalizes paths into metric-name segments, `from_path()` parses known paths, `new()` creates custom paths, and `Display` writes the path. The nested `subsystems` module exposes constants such as `API_REQUESTS`, `SYSTEM_DRIVE`, and `CLUSTER_IAM`.

## Control Flow
`path()` and `from_path()` are large matches over known paths. Unknown paths become `Custom`. Full metric-name generation calls `as_str()`, which uses `format_path_to_metric_name()`.

## State and Persistence
No runtime values. Custom subsystem variants store a path string inside descriptors.

## Dependencies and Integration Points
Every schema file depends on these subsystem constants. Collectors and dashboards depend on the normalized path names, for example `/system/network/internode` becomes `system_network_internode`.

## Risks
New schema modules must add both enum variants and constants or use `Custom`, which may reduce consistency. Unknown paths are silently accepted as custom, so path typos can create new metric families instead of failing. The `CLUSTER_BASE_PATH` constant is present but not central to descriptor construction.

## Test Signals
Tests validate formatting for common and custom paths and full descriptor name generation with built-in and custom subsystems.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/subsystem.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/ilm.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/ilm.rs

## Purpose
Defines lifecycle management metric descriptors for expiry and transition queues, backpressure, compensation, and versions scanned.

## Important APIs, Types, and Functions
Exports nine `LazyLock<MetricDescriptor>` values. Queue depth and active/running values are gauges; missed, full, send-timeout, compensation scheduled, and versions scanned values are counters. All use `subsystems::ILM` and no labels.

## Control Flow
Only lazy descriptor initialization. Descriptor type choices are encoded in factory calls.

## State and Persistence
No values are stored. Runtime data comes from `collect_ilm_metric_stats()`, which reads `GLOBAL_ExpiryState`, `GLOBAL_TransitionState`, and `global_metrics().report()`.

## Dependencies and Integration Points
Used by `metrics/collectors/ilm.rs` to expose `IlmStats`. It integrates with lifecycle runtime state in `rustfs_ecstore` through the stats collector.

## Risks
Because all descriptors are unlabeled, bucket-specific or rule-specific ILM visibility is not represented here. Counter/gauge semantics need to stay aligned with collector values, especially compensation running versus compensation scheduled.

## Test Signals
No direct tests. Existing collector tests or snapshot checks should validate full names and types.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/ilm.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/mod.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/mod.rs

## Purpose
Acts as the schema module index and re-export layer for RustFS metrics descriptors and primitives.

## Important APIs, Types, and Functions
Declares schema modules for audit, bucket, replication, cluster, system, node, notification, request, scanner, and entry primitives. Re-exports `MetricDescriptor`, `MetricName`, `MetricType`, `MetricNamespace`, `MetricSubsystem`, `subsystems`, and descriptor factories.

## Control Flow
No runtime control flow. Compilation makes all modules available and re-exported items are used throughout collectors and crate-level APIs.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
This module is imported by collectors and other observability code as the public schema surface. It connects many descriptor files to shared entry primitives.

## Risks
Adding a schema file without adding it here can leave descriptors inaccessible to collectors. Broad re-exports make it easy for downstream modules to depend on internal naming contracts. Duplicate concepts exist between node/process resource schemas and system process schemas, so module naming must remain clear.

## Test Signals
No direct tests. Build coverage is the primary signal: missing module declarations or broken re-exports fail compilation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/node_bucket.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/node_bucket.rs

## Purpose
Defines simple per-bucket node/API usage descriptors for bucket bytes, object count, and quota.

## Important APIs, Types, and Functions
Exports private `BUCKET_LABEL` and three `LazyLock<MetricDescriptor>` values: `BUCKET_USAGE_BYTES_MD`, `BUCKET_OBJECTS_TOTAL_MD`, and `BUCKET_QUOTA_BYTES_MD`. They use `MetricName::Custom` suffixes and `subsystems::BUCKET_API`, each labeled by `bucket`.

## Control Flow
Lazy descriptor construction only.

## State and Persistence
No values or persistence. Collector data comes from storage bucket lists, backend data usage, and quota config.

## Dependencies and Integration Points
Used by `metrics/collectors/bucket.rs`, which emits per-bucket metrics. It overlaps conceptually with `cluster_usage.rs` per-bucket descriptors but uses different names under the bucket API subsystem.

## Risks
Custom metric names bypass enum-level naming review. Hidden bucket filtering is handled by collectors, not descriptor schema. There is potential dashboard confusion between bucket API usage metrics and cluster usage bucket metrics.

## Test Signals
No schema tests. Bucket collector tests check representative names and labels.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/node_bucket.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/node_disk.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/node_disk.rs

## Purpose
Defines node-scoped disk capacity descriptors for total, used, and free bytes.

## Important APIs, Types, and Functions
Exports private labels `SERVER_LABEL` and `DRIVE_LABEL`, and three `LazyLock<MetricDescriptor>` descriptors using `MetricName::Custom("disk_*_bytes")` and `MetricSubsystem::new("/node")`.

## Control Flow
Only lazy initialization. The custom subsystem `/node` normalizes to the metric segment `node`.

## State and Persistence
No metric values or persistence. Values are populated by `collect_disk_stats()` via storage admin `storage_info`.

## Dependencies and Integration Points
Used by `metrics/collectors/node.rs`, which attaches `server` and `drive` labels. This schema is distinct from `system_drive.rs`, which exports richer drive metrics under `/system/drive`.

## Risks
The custom `/node` subsystem is not a built-in enum variant, so typos would be unchecked. Label ordering must match collector code. There is overlapping disk capacity visibility with `system_drive.rs`.

## Test Signals
Collector tests check generated names for node disk metrics. There are no local schema tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/node_disk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/notification_target.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/notification_target.rs

## Purpose
Defines per-notification-target queue, success, and permanent failure descriptors.

## Important APIs, Types, and Functions
Exports label constants `TARGET_ID` and `TARGET_TYPE`, a private two-label array, and three `LazyLock<MetricDescriptor>` descriptors: failed messages counter, queue length gauge, and total messages counter. All use `subsystems::NOTIFICATION`.

## Control Flow
Lazy descriptor construction only.

## State and Persistence
No values or persistence. The notification target collector supplies per-target values and labels.

## Dependencies and Integration Points
Used by notification target collector code and shares the `notification` subsystem with aggregate notification descriptors. Label constants provide a stable contract for target dimensions.

## Risks
High-cardinality `target_id` values can affect Prometheus cardinality if many targets exist or IDs are unstable. Collectors must always provide both labels in the declared order.

## Test Signals
No direct tests. Collector tests should assert label presence and full metric names.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/notification_target.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/process_resource.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/process_resource.rs

## Purpose
Defines a small legacy/simple process-resource schema for CPU percent, resident memory bytes, and uptime seconds under a custom `/process` subsystem.

## Important APIs, Types, and Functions
Exports `PROCESS_CPU_PERCENT_MD`, `PROCESS_MEMORY_BYTES_MD`, and `PROCESS_UPTIME_SECONDS_MD`, all gauges with no labels and `MetricName::Custom` suffixes.

## Control Flow
Only lazy descriptor initialization.

## State and Persistence
No state. Values are populated by `collect_process_stats()` from `snapshot_process_resource_and_system()`.

## Dependencies and Integration Points
Used by `metrics/collectors/resource.rs`. It overlaps with richer descriptors in `system_process.rs`, which include CPU total, memory, IO, status, and descriptor counts.

## Risks
Custom names and custom subsystem mean this schema sits outside the strongly enumerated subsystem set. Overlap with system process metrics can produce parallel names with similar semantics but different metric families.

## Test Signals
Resource collector tests check representative metric names and values. No schema-local tests exist.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/process_resource.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/replication.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/replication.rs

## Purpose
Defines site-level replication worker, queue, transfer-rate, and backlog descriptors.

## Important APIs, Types, and Functions
Exports thirteen gauge descriptors for averages, current values, last-minute queue values, maxima, data transfer rates, and recent backlog count. All use `MetricName::Replication*`, no labels, and `subsystems::REPLICATION`.

## Control Flow
Lazy construction only. Runtime aggregation and conversion are outside this schema.

## State and Persistence
No values are stored. `collect_replication_stats()` reads `GLOBAL_REPLICATION_STATS`, site metrics, bucket bandwidth reports, and bucket target stats to build `ReplicationStats`.

## Dependencies and Integration Points
Used by `metrics/collectors/replication.rs`. It complements bucket-replication schemas outside this subset that expose per-bucket and per-target replication details.

## Risks
All descriptors are gauges, including max values that reset with process lifetime. Missing global replication stats return defaults, so dashboards must distinguish zero from unavailable where possible. Data-transfer-rate aggregation depends on runtime statistics shape.

## Test Signals
Collector tests assert representative full names such as current and average active workers. No schema-local tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/replication.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/request.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/request.rs

## Purpose
Defines API request, rejection, latency distribution, and traffic descriptors.

## Important APIs, Types, and Functions
Exports label constants `NAME_LABEL`, `TYPE_LABEL`, and `LE_LABEL`. Rejection metrics are counters labeled by `type`. Waiting, incoming, and in-flight request metrics are gauges. Total, error, 4xx/5xx, canceled, TTFB distribution, sent bytes, and received bytes are counters. The TTFB distribution descriptor uses `name`, `type`, and `le`.

## Control Flow
Descriptors are lazily created using either `subsystems::API_REQUESTS` or `MetricSubsystem::ApiRequests`, which are equivalent.

## State and Persistence
No values here. Request collector code reads request stats and builds labeled Prometheus metrics, including histogram-bucket-like values for TTFB.

## Dependencies and Integration Points
Used by `metrics/collectors/request.rs`. The descriptor names come from `MetricName::Api*` variants. Full names compose under `rustfs_api_requests_*`.

## Risks
The TTFB distribution is built with `new_counter_md` rather than `new_histogram_md`; that may be intentional for bucket counters but can surprise consumers expecting histogram metadata. Label ordering and cardinality for `name` and `type` are critical. Several metrics split by API name can grow with endpoint variety.

## Test Signals
Request collector tests check representative names and labels. The entry-level histogram factory test does not cover this TTFB descriptor.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/request.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/scanner.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/scanner.rs

## Purpose
Defines the scanner metric surface for lifetime counters, current activity, concurrency, throttling configuration, current cycle stats, last cycle stats, failure/partial counters, and partial-cycle reasons.

## Important APIs, Types, and Functions
Exports many `LazyLock<MetricDescriptor>` values under `subsystems::SCANNER`. Lifetime scan counts and failed/partial cycles are counters. Activity gauges cover last activity, active paths, concurrency, throttle settings, cycle budgets, current/last cycle counters encoded as gauges, scan modes, result codes, rates, and durations. `SCANNER_PARTIAL_CYCLES_BY_REASON_MD` has a `reason` label.

## Control Flow
The file is static schema only. Descriptor types and help text encode the metric contract. Runtime mapping occurs in `collect_scanner_metric_stats()` and `metrics/collectors/scanner.rs`.

## State and Persistence
No local state or persistence. Runtime scanner values come from `rustfs_common::metrics::global_metrics().report()` and are transformed in `stats_collector.rs`.

## Dependencies and Integration Points
Used heavily by `metrics/collectors/scanner.rs`, which imports nearly every descriptor and emits values from `ScannerStats`. The schema integrates with `HealScanMode` through numeric mode code descriptions in help text, but the conversion code lives in `stats_collector.rs`.

## Risks
The surface is broad, so collector/schema drift is likely when adding scanner fields. Many current-cycle counts are gauges because they describe an in-progress cycle rather than process lifetime counters. Numeric enum encodings for modes/results/partial reasons need external documentation or dashboard annotations. Only the reason-specific partial-cycle metric uses a label.

## Test Signals
No direct schema tests. `stats_collector.rs` has tests for scanner cycle age, scan-mode mapping, fallback started counts, and rate calculations. Collector tests should verify all descriptors are emitted with correct names and reason labels.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/scanner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_cpu.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_cpu.rs

## Purpose
Defines host CPU metric descriptors for average idle, I/O wait, load, load percentage, nice, steal, system, and user time/usage.

## Important APIs, Types, and Functions
Exports eight no-label gauge descriptors under `subsystems::SYSTEM_CPU`, each backed by a `MetricName::SysCPU*` variant.

## Control Flow
Lazy descriptor initialization only.

## State and Persistence
No values. `collect_system_cpu_and_memory_stats()` builds `CpuStats` from a `sysinfo::System` snapshot, with some fields currently set to zero where sysinfo does not supply the exact Linux CPU time dimension.

## Dependencies and Integration Points
Used by `metrics/collectors/system_cpu.rs`. That collector also emits process CPU usage/utilization using descriptors from `system_process.rs`.

## Risks
Some descriptor names imply CPU time categories, but the current stats collector maps `system` to global CPU usage and `user`, `nice`, `steal`, `iowait` to zero. Consumers should treat these as best-effort until richer platform data is added.

## Test Signals
No local schema tests. Collector tests and stats-collector tests can verify stable output shape.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_cpu.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_drive.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_drive.rs

## Purpose
Defines detailed system drive descriptors for capacity, capacity-observation state, inode counts, errors, queueing/latency, health, aggregate online/offline counts, and iostat-like rates.

## Important APIs, Types, and Functions
Exports label constants `DRIVE_LABEL`, `SERVER_LABEL`, `POOL_INDEX_LABEL`, `SET_INDEX_LABEL`, `DRIVE_INDEX_LABEL`, and `API_LABEL`. `ALL_DRIVE_LABELS` includes drive/pool/set/drive-index. Capacity, inode, waiting IO, latency, health, count, and iostat values are gauges; timeout, I/O, and availability errors are counters. Capacity observation state adds a `state` label, and API latency adds an `api` label.

## Control Flow
Descriptors are lazily initialized. Some label slices are built by concatenating arrays at initialization time.

## State and Persistence
No values here. `collect_disk_and_system_drive_stats()` reads storage admin `storage_info`, computes online/offline counts, capacity observation states (`live`, `stale`, `missing`), and derives utilization percentage from used/total bytes. Many iostat/error/inode fields currently default to zero.

## Dependencies and Integration Points
Used by `metrics/collectors/system_drive.rs`, which must attach all drive labels and any extra `state` or `api` labels. Integrates with storage topology fields such as pool/set/drive indexes through collector/stat DTOs.

## Risks
There is a potential label contract mismatch to watch: `ALL_DRIVE_LABELS` omits `server`, while collector helpers may provide server/drive labels. If descriptor labels and collector labels diverge, Prometheus output can be inconsistent. Many fields are placeholders until storage/iostat sources are wired. The help text contains a micro sign in one string; encoding should remain UTF-8.

## Test Signals
Collector tests check representative drive names and counts. `stats_collector.rs` tests cover online/offline state interpretation and capacity observation state indirectly through count behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_drive.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_gpu.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_gpu.rs

## Purpose
Defines the GPU memory usage metric descriptor for the RustFS process.

## Important APIs, Types, and Functions
Exports `PROCESS_GPU_MEMORY_USAGE_MD`, a no-label gauge using `MetricName::ProcessGpuMemoryUsage` under `subsystems::SYSTEM_GPU`.

## Control Flow
Lazy descriptor initialization only.

## State and Persistence
No values or persistence. Values are sampled by the GPU collector, which integrates with platform-specific GPU discovery.

## Dependencies and Integration Points
Used by `metrics/collectors/system_gpu.rs`. The metric name composes under `rustfs_system_gpu_gpu_memory_usage`.

## Risks
GPU availability is platform and driver dependent. A no-label descriptor cannot distinguish multiple GPUs. Missing GPU data should be handled by the collector rather than this schema.

## Test Signals
No schema tests. GPU collector tests or platform-gated integration tests are the relevant coverage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_gpu.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_memory.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_memory.rs

## Purpose
Defines host memory metric descriptors for total, used, used percentage, free, buffers, cache, shared, and available memory.

## Important APIs, Types, and Functions
Exports eight no-label gauge descriptors under `subsystems::SYSTEM_MEMORY`, backed by `MetricName::Mem*` variants.

## Control Flow
Only lazy construction.

## State and Persistence
No values. `collect_system_cpu_and_memory_stats()` refreshes `sysinfo::System` memory data and maps it into `MemoryStats`. Buffers, cache, and shared are currently zeroed by the stats collector.

## Dependencies and Integration Points
Used by `metrics/collectors/system_memory.rs`, which also emits process resident/virtual memory descriptors from `system_process.rs`.

## Risks
Some fields are placeholders on the current sysinfo-based implementation, so dashboards must distinguish zero from actual kernel-reported zero. Units are bytes except `used_perc`.

## Test Signals
No direct tests. Collector-level tests can validate output shape; stats collector code is simple and indirectly covered by build/tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_memory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_network.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_network.rs

## Purpose
Defines internode network metric descriptors for failed calls, dial failures, average dial time, and bytes sent/received between peers.

## Important APIs, Types, and Functions
Exports five descriptors under `subsystems::SYSTEM_NETWORK_INTERNODE`. Error and byte totals are counters; average dial time is a gauge. All are unlabeled.

## Control Flow
Lazy descriptor initialization only.

## State and Persistence
No values. `collect_internode_network_stats()` reads `global_internode_metrics().snapshot()`.

## Dependencies and Integration Points
Used by `metrics/collectors/system_network.rs`. The stats collector wraps internode metrics into `NetworkStats`.

## Risks
Unlabeled aggregate metrics do not identify peer nodes or endpoints. Counters are process-lifetime values from the global runtime. Average dial time semantics depend on the internode metrics implementation.

## Test Signals
No schema-local tests. Collector tests should verify names and counter/gauge typing.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_network.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_network_host.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_network_host.rs

## Purpose
Defines host-wide network I/O descriptors for aggregate and per-interface byte transfer metrics.

## Important APIs, Types, and Functions
Exports `HOST_NETWORK_IO_MD` and `HOST_NETWORK_IO_PER_INTERFACE_MD`, both no-label gauges under `subsystems::SYSTEM_NETWORK_HOST`.

## Control Flow
Lazy descriptor construction only.

## State and Persistence
No values. `collect_host_network_stats()` uses `sysinfo::Networks::new_with_refreshed_list()` to collect total received/transmitted bytes and per-interface tuples.

## Dependencies and Integration Points
Used by `metrics/collectors/system_network_host.rs`, which adds direction/interface labels at emission time even though this schema declares no labels.

## Risks
The descriptors currently declare empty label sets, but the collector appears to distinguish received/transmitted and per-interface values through labels. That mismatch should be tested because descriptor label metadata may not reflect emitted metric cardinality. Host counters are not process-specific.

## Test Signals
No schema tests. Collector tests should specifically validate label metadata and emitted label sets for aggregate versus per-interface metrics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_network_host.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_process.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_process.rs

## Purpose
Defines detailed process metrics under the system process subsystem: locks, CPU, runtime, file descriptors, process IO, syscalls, memory, process status, disk IO, and migrated process-level resource metrics.

## Important APIs, Types, and Functions
Exports many no-label descriptors. Counters include CPU total seconds, IO byte totals, and syscall totals. Gauges include locks, routine count, start time, uptime, descriptor limits/open count, resident/virtual memory, CPU usage/utilization, disk IO, and status. `PROCESS_STATUS_MD` encodes status as numeric categories.

## Control Flow
Only lazy descriptor construction. Runtime values are sampled from `snapshot_process_resource_and_system()` and converted in `collect_process_metric_bundle()`.

## State and Persistence
No values or persistence. Process metrics are process-lifetime snapshots/counters from OS and runtime sources.

## Dependencies and Integration Points
Used by `metrics/collectors/system_process.rs`, plus CPU, memory, drive, and GPU collectors import selected process-level descriptors for co-located output. It overlaps with `process_resource.rs` for simplified process resource metrics.

## Risks
`ProcessGoRoutineTotal` preserves a Go-oriented name even though this is RustFS; dashboards should understand it as a runtime task/thread equivalent only if collector semantics match. Numeric status codes need stable documentation. Some descriptors are gauges even for monotonic-looking values where OS snapshots may reset at process restart.

## Test Signals
Collector tests exercise process metric output. There are no schema-local tests for all names or type choices.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/schema/system_process.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/stats_collector.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/stats_collector.rs

## Purpose
Implements the sampling and transformation bridge between RustFS runtime/storage/system sources and the DTO structs consumed by metrics collectors. Unlike schema files, this module contains active runtime logic, fallback paths, warnings, and testable helper behavior.

## Important APIs, Types, and Functions
Public collection functions include `collect_cluster_and_health_stats`, `collect_cluster_stats`, `collect_cluster_health_stats`, `collect_bucket_stats`, `collect_bucket_replication_bandwidth_stats`, `collect_bucket_replication_detail_stats`, `collect_replication_stats`, `collect_disk_stats`, `collect_system_cpu_and_memory_stats`, `collect_system_cpu_and_memory_stats_with`, `collect_system_cpu_stats`, `collect_system_memory_stats`, `collect_disk_and_system_drive_stats`, `collect_system_drive_stats`, `collect_process_metric_bundle`, `collect_process_resource_and_system_stats`, `collect_process_stats`, `collect_process_system_stats`, `collect_host_network_stats`, `collect_internode_network_stats`, `collect_cluster_config_stats`, `collect_erasure_set_stats`, `collect_iam_stats`, `collect_cluster_usage_metric_stats`, `collect_ilm_metric_stats`, and `collect_scanner_metric_stats`. Important helpers include `disk_is_online_for_metrics`, `disk_capacity_observation_state`, `derive_erasure_set_quorum_shape`, `apply_erasure_set_health`, scanner mode/rate helpers, and `ProcessMetricBundle`.

## Control Flow
Most collectors resolve a global object store or runtime singleton, return defaults/empty values when unavailable, then map external snapshots into collector DTOs. Storage-based collectors use `StorageAdminApi::storage_info()` or `backend_info()`. Usage collectors load persisted data-usage snapshots and optionally fall back to bucket listing. Replication collectors read `GLOBAL_REPLICATION_STATS`. System collectors use `sysinfo` and `rustfs_io_metrics`. Scanner and ILM collectors read `global_metrics()` and lifecycle globals.

## State and Persistence
The module owns no long-lived mutable state, but it reads persisted data usage from the backend and quota configuration from bucket metadata. It also reads process-lifetime global counters for replication, lifecycle, scanner, internode networking, and IAM. Many failures are converted to empty/default stats and logged with structured `warn!` events rather than propagated.

## Dependencies and Integration Points
This file is a central integration point for `rustfs_ecstore`, `rustfs_storage_api`, `rustfs_iam`, `rustfs_common::metrics`, `rustfs_io_metrics`, `sysinfo`, `chrono`, tracing, and all collector stats structs. Collectors call these functions to obtain data and then apply schema descriptors.

## Risks
Default-on-error behavior can make unavailable data look like zero unless collectors or dashboards expose scrape health separately. Some system fields are placeholders due to source limitations. Online drive classification is policy-heavy and must match operational expectations. Usage metrics depend on stored snapshots and do not trigger rescans. Label and field semantics must stay aligned with schema files and collectors.

## Test Signals
The module has focused unit tests for drive online classification, erasure quorum derivation, health application, scanner cycle age, scan-mode mapping, bucket-scan started fallback, and rate calculation. Integration tests are still needed for storage/IAM/replication/global metric availability and failure logging paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/stats_collector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/dial9.rs -->
# sources/object-store/rustfs/crates/obs/src/telemetry/dial9.rs

## Purpose
Integrates `dial9_tokio_telemetry` with RustFS runtime construction, including environment-driven configuration, trace output directory validation, rotating writer setup, and session guard handling.

## Important APIs, Types, and Functions
`Dial9Config` stores enabled state, output directory, file prefix, max file size, rotation count, optional S3 settings, and sampling rate. `Dial9Config::from_env()` reads `rustfs_config` environment keys via `rustfs_utils` helpers and clamps sampling rate. `base_path()` combines output directory and prefix. `Dial9SessionGuard` wraps an optional `TelemetryGuard`, validates setup in `new()`, exposes `is_active()`, `shutdown()`, and `set_guard()`. Module functions `init_session()`, `is_enabled()`, and `build_traced_runtime()` provide the public flow.

## Control Flow
If disabled, `new()` logs a disabled state and returns `Ok(None)`. If enabled, it creates the output directory asynchronously and falls back to disabled on directory creation failure. `build_traced_runtime()` is synchronous runtime-building code: it rejects disabled mode, reloads config, creates the output directory, constructs a `RotatingWriter` with total rotation budget, and wraps a Tokio builder with `TracedRuntime::builder().with_task_tracking(true)`.

## State and Persistence
Trace data is persisted to rotating files under `output_dir` with `file_prefix`. The guard keeps the underlying telemetry guard alive so drop can flush. S3 fields are parsed but reserved for future use in this implementation.

## Dependencies and Integration Points
Depends on `dial9_tokio_telemetry`, `rustfs_config`, `rustfs_utils`, Tokio, and the crate's `TelemetryError`. It is intended to be called by the runtime builder and broader telemetry initialization.

## Risks
`init_session()` only validates directory setup; the actual active guard is attached later through runtime construction. `build_traced_runtime()` errors when disabled, so callers must check `is_enabled()`. Sampling and S3 settings are currently parsed but not passed to the dial9 library. File-size multiplication by rotation count should be watched for extreme env values.

## Test Signals
Tests cover default config values, base path construction, and default disabled detection when the environment variable is absent. Additional tests could cover clamping, env parsing, and runtime writer failure paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/dial9.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/filter.rs -->
# sources/object-store/rustfs/crates/obs/src/telemetry/filter.rs

## Purpose
Builds `tracing_subscriber::EnvFilter` instances for local, file, and OTLP logging while suppressing noisy dependencies under non-verbose configurations.

## Important APIs, Types, and Functions
Private helpers include `is_verbose_level`, `is_level_token`, `rust_log_requests_verbose`, `should_suppress_noisy_crates`, `directive_applies_to_target`, `effective_level_for_target`, and `should_demote_http_request_logs`. The exported crate-internal `build_env_filter(logger_level, default_level)` chooses the base directive from `default_level`, `RUST_LOG`, or `logger_level`, then appends `off` directives for `hyper`, `tonic`, `h2`, `reqwest`, and `tower` when appropriate. It may demote `rustfs::server::http` to WARN for info/warn defaults.

## Control Flow
The key branch is precedence: forced `default_level` wins, then `RUST_LOG`, then configured logger level. Suppression is skipped if the effective configuration requests debug/trace or target-only verbose directives. Target effective level resolution chooses the most specific and latest matching directive.

## State and Persistence
No persisted state. Reads process environment variable `RUST_LOG` at filter construction time.

## Dependencies and Integration Points
Used by `telemetry/local.rs` and likely other telemetry setup modules to keep log filtering consistent. Depends on `tracing_subscriber::EnvFilter` and `LevelFilter`.

## Risks
EnvFilter directive precedence is subtle. Appending suppressions can override broad directives, so helper logic must correctly detect explicit verbose intent. HTTP log demotion deliberately avoids falling back to `logger_level` when `RUST_LOG` only sets unrelated targets.

## Test Signals
The file has extensive unit tests for verbosity detection, `RUST_LOG` parsing, suppression decisions, HTTP demotion, injected suppressions, verbose `RUST_LOG` preservation, RUST_LOG precedence, target-only directives, and avoiding accidental HTTP log promotion.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/filter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/guard.rs -->
# sources/object-store/rustfs/crates/obs/src/telemetry/guard.rs

## Purpose
Defines `OtelGuard`, the RAII owner for observability runtime resources, and implements ordered shutdown for tracing, metrics, logging, profiling, cleanup tasks, and non-blocking log writers.

## Important APIs, Types, and Functions
Type aliases `ProfilingAgent` and `MemoryProfilingAgent` are feature/platform gated. `format_guard_shutdown_stderr_message()` builds fallback diagnostics. `OtelGuard` stores optional `SdkTracerProvider`, `SdkMeterProvider`, `SdkLoggerProvider`, profiling agents, cleanup task handle, file tracing worker guard, and stdout worker guard. `Debug` reports only presence flags.

## Control Flow
`Drop` shuts resources down in a deliberate order: tracer provider, meter provider, profiling agents, cleanup task abort, logger provider, file tracing guard, and stdout guard. Provider shutdown failures are logged through tracing when a dispatcher exists, or printed to stderr otherwise. Logger provider failures always go to stderr after logger shutdown becomes unreliable.

## State and Persistence
The guard owns runtime handles but does not persist state. Dropping worker guards flushes buffered logs. Aborting the cleanup task stops future log cleanup passes.

## Dependencies and Integration Points
Constructed by telemetry initialization paths such as local logging and OTLP setup. Depends on OpenTelemetry SDK providers, tracing appender worker guards, optional Pyroscope, and Tokio task handles.

## Risks
Drop-time operations must remain non-panicking. Shutdown logging depends on dispatcher availability and resource order. Aborting cleanup means in-flight cleanup work may stop abruptly, which is acceptable for shutdown but should not be used for normal rotation control.

## Test Signals
Unit test verifies the stderr fallback shutdown message is actionable and includes resource/error data. More integration coverage would require fake providers or feature-gated profiling paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/guard.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/local.rs -->
# sources/object-store/rustfs/crates/obs/src/telemetry/local.rs

## Purpose
Implements local logging initialization for stdout-only and rolling-file modes, including JSON formatting, request-id promotion, optional stdout mirroring, directory hardening, fallback behavior, and background log cleanup.

## Important APIs, Types, and Functions
`RequestIdJsonFormat<T>` wraps the JSON formatter to add top-level `request_id` and `request-id` fields from the active span scope. `span_scope_request_id()` scans formatted span fields from root to current span. `build_json_log_layer()` creates a JSON tracing layer with RFC3339 time, target, thread, file/line, current span, span list, and optional span events. `init_local_logging()` chooses file or stdout mode. `init_stdout_only()` registers stdout JSON logging. `init_file_logging_internal()` prepares rolling files, optional stdout mirror, and cleanup. `ensure_dir_permissions()` tightens Unix permissions to 0755. `should_fallback_to_stdout()`, `format_file_logging_fallback_warning()`, and `emit_file_logging_fallback_warning()` handle recoverable file setup failures. `spawn_cleanup_task()` builds a `LogCleaner` and periodically runs it in `spawn_blocking`.

## Control Flow
If no log directory is configured, initialization immediately installs stdout JSON logging and returns an `OtelGuard` with a stdout worker guard. If a log directory is configured, file setup creates the directory, tightens permissions, selects rotation, opens a size-capped `RollingAppender`, installs file and optional stdout layers, then starts cleanup. Permission-like file setup failures fall back to stdout; other errors are returned. Cleanup loops on a Tokio interval and records success/failure counters.

## State and Persistence
In file mode, logs persist as rolling files in the configured directory. Cleanup persists side effects by deleting/compressing old files according to config. Runtime state is held by `OtelGuard`: worker guards and cleanup task handle. The module also toggles observability metric enablement and increments startup/cleanup counters.

## Dependencies and Integration Points
Depends on `OtelConfig`, `OtelGuard`, `LogCleaner`, rolling appender, `build_env_filter`, `metrics`, `tracing_subscriber`, `tracing_appender`, `serde_json`, Tokio, and `rustfs_config` defaults. It is a central local backend for crate telemetry initialization.

## Risks
`tracing_subscriber::init()` can only be called once per process, so tests and callers must avoid double initialization. Request-id extraction depends on JSON-formatted span fields; malformed fields skip promotion. File fallback only handles permission-like errors, while invalid filenames and other setup failures return errors. Cleanup interval defaults and file matching must align with rolling filename format to avoid deleting active logs.

## Test Signals
Tests cover invalid filename errors without panic, permission-denied fallback decisions, actionable fallback warning messages, parseable ANSI-free JSON logs, stable JSON shape across ANSI settings, request-id promotion from current span, and parent request-id promotion from nested recovery-monitor spans.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/local.rs -->
