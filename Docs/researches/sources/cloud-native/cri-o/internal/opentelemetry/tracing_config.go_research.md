# sources/cloud-native/cri-o/internal/opentelemetry/tracing_config.go

Purpose: configures CRI-O OpenTelemetry tracing and exposes the package tracer.

Important APIs/types/functions: `tracingServiceName`, package-level `tracer`, `Tracer()`, and `InitTracing(ctx, collectorAddress, samplingRate)`.

Control flow: `InitTracing` reads hostname, builds a resource with service name, host name, and process PID, creates an insecure OTLP/gRPC trace exporter, chooses a parent-based sampler with either `NeverSample` or `TraceIDRatioBased(samplingRate/1_000_000)`, installs a batch span processor and tracer provider globally, installs trace-context plus baggage propagators globally, and returns gRPC interceptor options using that provider/propagator.

State and persistence behavior: mutates OpenTelemetry global tracer provider and global text-map propagator. It opens exporter state that callers must shut down through the returned `TracerProvider`.

Dependencies and integration points: uses OpenTelemetry SDK, OTLP trace gRPC exporter, grpc instrumentation options, semantic conventions, and CRI-O callers that instrument gRPC server/client handling.

Risks: global provider mutation affects the whole process. `WithInsecure` assumes collector transport is trusted or local. Sampling rate units are parts per million, so config validation must prevent surprising values.

Test signals: no local test in this subset; integration should verify hostname failures, exporter creation errors, sampling-rate boundaries, global propagation, and provider shutdown.
