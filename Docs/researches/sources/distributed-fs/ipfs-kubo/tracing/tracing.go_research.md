## sources/distributed-fs/ipfs-kubo/tracing/tracing.go

Purpose: constructs Kubo's OpenTelemetry tracer provider and provides a helper for consistently named spans.

Important APIs/types/functions: `shutdownTracerProvider` extends `traceapi.TracerProvider` with `Shutdown`. `noopShutdownTracerProvider` wraps a no-op provider when no exporters are configured. `NewTracerProvider` calls Boxo `tracing.NewSpanExporters(ctx)`, adds each exporter as a batcher, merges default resource data with service name `Kubo` and service version from `version.CurrentVersionNumber`, and returns an SDK tracer provider. `Span` starts spans using global tracer name `Kubo` and span name `component.span`.

State and persistence: runtime state is the created tracer provider and exporter pipelines. Exporters may persist or send traces depending on environment configuration.

Dependencies and integration points: depends on Boxo tracing exporter discovery, Kubo version package, OpenTelemetry SDK/resource/semconv, global `otel` tracer registry, and noop provider.

Risks and test signals: errors from exporter construction or resource merging propagate. If no exporters are configured, callers still get a provider with a no-op `Shutdown`, simplifying lifecycle code. Span naming is string-concatenated and can produce odd names if callers pass empty component/span strings.
