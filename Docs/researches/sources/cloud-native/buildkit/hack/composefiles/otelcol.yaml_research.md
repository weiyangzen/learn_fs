<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/otelcol.yaml -->
# sources/cloud-native/buildkit/hack/composefiles/otelcol.yaml

Purpose: OpenTelemetry collector config for local BuildKit tracing and metrics ingestion.

Important APIs, types, and functions: configures an OTLP receiver on `0.0.0.0:4317`, an OTLP exporter to `jaeger:4317` with insecure TLS and retry max elapsed time 1 minute, a `nop` exporter, trace pipeline `otlp -> otlp/jaeger`, metrics pipeline `otlp -> nop`, and low-noise collector telemetry.

Control flow and state: declarative collector routing. Traces are forwarded to Jaeger when the tracing profile runs; metrics are accepted but dropped unless an extension overrides behavior.

Dependencies and integration: mounted into `otel-collector` by `compose.yaml`. BuildKit points `OTEL_EXPORTER_OTLP_ENDPOINT` at this service.

Risks and test signals: collector starts even when Jaeger profile is not active but trace export will fail until Jaeger is reachable. Metrics are intentionally dropped by default. Test via collector startup logs and Jaeger trace visibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/otelcol.yaml -->
