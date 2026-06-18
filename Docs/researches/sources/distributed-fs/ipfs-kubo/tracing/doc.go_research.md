## sources/distributed-fs/ipfs-kubo/tracing/doc.go

Purpose: package-level documentation for Kubo tracing, describing experimental status, OpenTelemetry environment variables, exporter choices, Jaeger example setup, and span naming conventions.

Important content: documents `OTEL_TRACES_EXPORTER` values `otlp`, `zipkin`, and `file`, common OTLP/Zipkin/file env vars, an example Jaeger all-in-one Docker command, and the convention `<Component>.<Span>` with examples like `Gateway.Request`.

State and persistence: documentation only; it describes trace export side effects such as writing JSON traces to `OTEL_EXPORTER_FILE_PATH`.

Dependencies and integration points: links package behavior to OpenTelemetry SDK environment-variable conventions and the global tracer provider.

Risks and test signals: because tracing is marked experimental, docs may drift from actual exporter support in Boxo tracing or OpenTelemetry defaults. No tests are present in this file.
