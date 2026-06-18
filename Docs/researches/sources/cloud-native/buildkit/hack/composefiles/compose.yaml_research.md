<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/compose.yaml -->
# sources/cloud-native/buildkit/hack/composefiles/compose.yaml

Purpose: Docker Compose definition for a local BuildKit development stack with optional tracing and metrics.

Important APIs, types, and functions: defines services `buildkit`, `otel-collector`, `jaeger`, `prometheus`, and `grafana`; volumes `buildkit`, `prometheus`, and `grafana`; and configs for BuildKit, OpenTelemetry collector, Prometheus, Grafana, and Grafana datasources. The BuildKit service builds from `../..`, tags `moby/buildkit:local`, runs privileged, maps localhost ports 5000 and 6060, sets OTEL environment, and runs `--save-cache-debug`.

Control flow and state: Compose manages container lifecycle and named volumes. Profiles gate `jaeger` under `tracing` and Prometheus/Grafana under `metrics`. BuildKit depends on the collector, Prometheus depends on BuildKit, and Grafana depends on Prometheus.

Dependencies and integration: consumed by `hack/compose`. It integrates BuildKit debug metrics, OTLP export to collector, Jaeger trace UI on 16686, Prometheus scraping, and Grafana UI on 3000.

Risks and test signals: privileged BuildKit and fixed localhost ports can conflict with existing services. `jaeger:latest` is intentionally fluid and may change behavior. Test with `hack/compose config` and selected `--profile tracing`/`--profile metrics` runs.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/compose.yaml -->
