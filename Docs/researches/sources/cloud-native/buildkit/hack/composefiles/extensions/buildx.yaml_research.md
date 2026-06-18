<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/extensions/buildx.yaml -->
# sources/cloud-native/buildkit/hack/composefiles/extensions/buildx.yaml

Purpose: optional Compose extension that adds a second OpenTelemetry collector config for filtering and debugging Buildx metrics.

Important APIs, types, and functions: extends `otel-collector` command with both the base config and `buildx.yaml`. Defines config `otelcol_buildx_config` inline with a `filter/buildx` processor that keeps metrics whose instrumentation scope is `github.com/docker/buildx`, debug exporter verbosity `detailed`, and a `metrics/buildx` pipeline from OTLP through the filter to debug output.

Control flow and state: declarative Compose override. No persistence except collector logs.

Dependencies and integration: used with the base compose stack to inspect Buildx OTLP metrics without changing the primary config files.

Risks and test signals: the YAML uses collector double-colon path expansion syntax, which depends on collector config support. Debug exporter can be noisy. Test with `docker compose -f compose.yaml -f extensions/buildx.yaml config` and by sending Buildx metrics.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/extensions/buildx.yaml -->
