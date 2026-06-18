<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/plugin/otlp.go -->
# sources/cloud-native/containerd/pkg/tracing/plugin/otlp.go

## Purpose
Containerd plugin registrations for OTLP trace exporting and global tracer provider setup.

## Important APIs, Types, And Functions
Registers otlp TracingProcessorPlugin and tracing InternalPlugin. OTLPConfig, TraceConfig, checkDisabled, newExporter, newTracer, warnTraceConfig, and warnOTLPConfig implement setup.

## Control Flow
Plugin init warns for deprecated config, skips when OTEL_SDK_DISABLED or no OTLP endpoint, validates OTEL_TRACES_EXPORTER, creates HTTP/protobuf or gRPC exporter, collects span processors, sets propagator/tracer provider, and returns a closer for shutdown.

## State And Persistence
Mutates process environment by setting OTEL_SERVICE_NAME to containerd if unset and sets global OpenTelemetry provider/propagator. Exporter sends trace data externally.

## Dependencies And Integration Points
Depends on containerd plugin registry, warning service, deprecation IDs, errdefs, and OpenTelemetry SDK/exporters.

## Risks And Edge Cases
Environment variables dominate config. Unsupported protocols fail with ErrNotImplemented. Deprecated config only warns when warning plugin is available.

## Test Signals
No direct tests in subset; plugin graph/init tests elsewhere should exercise it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/plugin/otlp.go -->
