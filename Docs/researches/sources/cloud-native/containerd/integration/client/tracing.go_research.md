<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/tracing.go -->
# sources/cloud-native/containerd/integration/client/tracing.go

## Purpose
Provides small OpenTelemetry helpers for integration tests that need to capture and validate spans in memory.

## APIs, Types, And Functions
The file defines `newInMemoryExporterTracer` and `validateRootSpan`. It uses `tracetest.InMemoryExporter`, `sdktrace.TracerProvider`, `sdktrace.WithBatcher`, and OpenTelemetry status codes.

## Control Flow And State
`newInMemoryExporterTracer` creates an in-memory exporter and tracer provider with a batcher. `validateRootSpan` scans exported span stubs, considers only root spans whose parent context is invalid, finds a span by expected name, asserts its status code is not `codes.Error`, and fails the test if no matching root span exists.

## Persistence And Integration Points
Span state is held in memory by the exporter for the duration of a test. The helpers integrate instrumented client or daemon code with test assertions without requiring an external collector.

## Risks And Test Signals
Batching can require tests to flush/shutdown the provider before inspecting spans. The helper only checks root span name and non-error status, so it is a coarse signal rather than a full trace-shape validator.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/tracing.go -->
