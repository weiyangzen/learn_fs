<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/otelcol-ci-config.yml -->
# sources/cloud-native/moby/otelcol-ci-config.yml

Purpose: OpenTelemetry Collector configuration for CI trace capture. It configures OTLP gRPC on `0.0.0.0:4317`, OTLP HTTP on `0.0.0.0:4318`, a batch processor, and a file exporter with 1-second flush and size rotation below Jaeger upload limits. State is collector output files written by the file exporter. Dependencies are the OpenTelemetry Collector and CI services that upload or inspect the trace file. Risks include open bind addresses in CI context, file rotation losing expected trace chunks, and collector schema drift. Test signal is observability support for test runs, not application behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/otelcol-ci-config.yml -->
