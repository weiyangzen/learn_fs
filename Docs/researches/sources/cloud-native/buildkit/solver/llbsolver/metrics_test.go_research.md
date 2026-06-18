<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/metrics_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/metrics_test.go

Purpose: verifies OTEL build metric registration and observations.

Important APIs and types: helpers `newTestMetrics`, `collect`, `findCounterPoint`, `attrsContain`, and tests `TestRecordBuildCompletion_Success`, `TestRecordBuildCompletion_FailureGRPCCodes`, `TestRecordBuildCompletion_StepCounters`, `TestRecordBuildCompletion_NilSafe`, and `TestNewBuildMetrics_NilProviderUsesNoop`.

Control flow: tests use an SDK manual reader to synchronously collect metric data, then assert build counters by attributes, absence of `error_code` on success, histogram count/sum/status, failure code labels for several gRPC codes, step counter values by kind, nil receiver/record no panic, and nil provider creates usable noop metrics.

State and dependencies: test-only meter provider/manual reader. Depends on OTEL SDK metricdata, testify, control API records, gRPC status codes, and timestamppb.

Integration points: protects metrics emitted from build history completion finalizer.

Risks and test signals: strong coverage for bounded labels and values. It does not test concurrent metric recording, relying on OTEL API guarantees.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/metrics_test.go -->
