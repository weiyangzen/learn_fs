<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/metrics.go -->
## sources/cloud-native/buildkit/solver/llbsolver/metrics.go

Purpose: defines OpenTelemetry build completion metrics emitted by llbsolver when build history finalization completes.

Important APIs and types: constants for instrumentation name and attribute keys/values, `buildMetrics`, `newBuildMetrics`, and `(*buildMetrics).recordBuildCompletion`.

Control flow: `newBuildMetrics` uses a no-op meter provider when nil, creates counters `buildkit.builds` and `buildkit.builds.steps`, and histogram `buildkit.build.duration`. `recordBuildCompletion` no-ops for nil receiver/record, records one build with bounded `status` and optional `error_code`, records completed/cached/total/warning step counters by `kind`, and records duration in seconds when both timestamps are present.

State and dependencies: instruments are shared and concurrency-safe through OTEL. No custom persistence. Dependencies are control API records, OTEL metric API, noop provider, and gRPC codes.

Integration points: called from `recordBuildHistory` immediately before emitting the COMPLETE history event.

Risks and test signals: labels intentionally avoid frontend and error message to control cardinality. Missing timestamps skip duration only. `metrics_test.go` covers success, failure codes, step counters, nil safety, and nil provider behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/metrics.go -->
