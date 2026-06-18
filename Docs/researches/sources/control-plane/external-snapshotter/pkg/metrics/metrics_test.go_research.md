# sources/control-plane/external-snapshotter/pkg/metrics/metrics_test.go

## Purpose
This file is the unit and integration-style test coverage for the snapshot controller metrics manager. It starts a real HTTP metrics endpoint on an ephemeral localhost port, drives `MetricsManager` operations, scrapes Prometheus output, decodes metric families, and verifies latency histograms, in-flight operation gauges, process start metrics, and volume group snapshot metric labels.

## Important APIs, Types, And Functions
- `fakeOpStatus` implements `OperationStatus` by returning `Success`, `Failure`, or `Unknown` from a local status map. Tests use it to control the `operation_status` label without depending on production status types.
- `initMgr` constructs `NewMetricsManager`, registers `/metrics` via `PrepareMetricsPath`, listens on `localhost:0`, and serves the handler in a goroutine.
- `shutdown` wraps `http.Server.Shutdown`.
- `TestNew`, `TestDropNonExistingOperation`, `TestRecordMetricsForNonExistingOperation`, `TestDropOperation`, `TestUnknownStatus`, `TestRecordMetrics`, and `TestConcurrency` validate operation lifecycle recording.
- `TestInFlightMetric` lowers `inFlightCheckInterval`, starts and completes operations, and scrapes `snapshot_controller_operations_in_flight`.
- `verifyMetric`, `verifyInFlightMetric`, `containsMetrics`, and `sortMfs` are test assertions over scraped Prometheus payloads. `verifyMetric` decodes text into `client_model.MetricFamily` values before comparing.
- `TestProcessStartTimeMetricExist` verifies that the registry exposes `process_start_time_seconds` with a positive timestamp-like value.
- `TestRecordVolumeGroupSnapshotMetrics` and `TestRecordVolumeGroupSnapshotMetricsForPreProvisioned` validate the `snapshot_type` label for dynamic and pre-provisioned group snapshot operations.

## Control Flow
Most tests call `initMgr`, derive `srvAddr`, start one or more operations with `OperationStart`, optionally sleep to place observations in expected histogram buckets, then call `RecordMetrics`, `RecordVolumeGroupSnapshotMetrics`, or `DropOperation`. The tests scrape the live HTTP endpoint and compare the decoded metrics against expected histogram/counter records. `TestConcurrency` starts several operations, then records or drops them from goroutines under a `sync.WaitGroup`, exercising internal synchronization. `TestInFlightMetric` starts operations without recording them to confirm that the background in-flight updater reports outstanding operations, then records one and starts a batch of 50 more to verify gauge movement.

## State And Persistence Behavior
State under test is in-memory metrics state inside `MetricsManager`: active operation cache entries, Prometheus registry collectors, operation latency observations, and the in-flight gauge. There is no filesystem persistence. The tests intentionally use a live HTTP server to observe exported state as Prometheus clients would. They rely on sleeps of 100 ms, 300 ms, 500 ms, and 1100 ms to create stable lower bounds for histogram sums and buckets.

## Dependencies And Integration Points
The tests integrate with Go `net/http`, ephemeral TCP listeners, Prometheus `expfmt`, Prometheus `client_model/go`, Kubernetes UID types, and the production metrics manager APIs. They are sensitive to the registry contents exposed by `PrepareMetricsPath` and to the production labels `driver_name`, `operation_name`, `operation_status`, and `snapshot_type`.

## Risks And Edge Cases
- The tests are time-sensitive. Slow or heavily loaded test environments can still pass because sample sums are checked as greater-than-or-equal, but bucket boundaries assume sleeps land above minimum thresholds.
- `sortMfs` declares a `sortedMfs` slice but returns it without populating from `mfs`; this makes `containsMetrics` vulnerable to empty sorted slices and indexing assumptions. If this code is currently passing, it is worth reviewing because the helper appears logically defective.
- HTTP response bodies are read but not explicitly closed in helpers and some tests, which is acceptable for short unit tests but can accumulate resources in larger runs.
- `TestProcessStartTimeMetricExist` checks the gauge value inside the loop for non-target metric families, so a non-gauge metric with no gauge could be risky if registry composition changes.
- The expected metric text is intentionally verbose and tightly coupled to bucket boundaries and label rendering.

## Test Signals
This file is itself test signal. It covers no-op drop/record behavior, successful drop-and-rerecord, nil status fallback to `Unknown`, concurrent record/drop calls, in-flight gauge tracking, process-start metric exposure, and group snapshot metric labeling for dynamic and pre-provisioned operations.
