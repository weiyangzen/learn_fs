<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/actions/setup-tracing/action.yml -->
# sources/cloud-native/moby/.github/actions/setup-tracing/action.yml

## Purpose
Starts an OpenTelemetry Collector container for Linux test jobs and exports OTLP endpoint/protocol variables into the GitHub Actions environment so test processes can emit traces.

## Important APIs, Types, And Functions
- Creates `/tmp/reports` with world-writable permissions for trace output.
- Runs `otel/opentelemetry-collector-contrib:0.144.0` on host networking.
- Mounts `otelcol-ci-config.yml` and `/tmp/reports`.
- Uses an inline collector config override to write `/data/otel-trace.jsonl`.
- Discovers the `docker0` IPv4 address and appends `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_PROTOCOL` to `$GITHUB_ENV`.

## Control Flow
The composite action starts the collector in detached mode, computes a container-reachable endpoint, and makes tracing environment variables available to later steps. Test workflows stop the `otelcol` container during report preparation.

## State And Persistence
Runtime state consists of the `otelcol` Docker container and trace files in `/tmp/reports`. Environment state persists within the current job through `$GITHUB_ENV`.

## Dependencies And Integration Points
Used by Linux integration and docker-py jobs. Its collector version must stay aligned with the Windows inline collector setup in `.windows.yml`.

## Risks And Edge Cases
`--net=host` and `docker0` assumptions are Linux-specific. If `docker0` has no IPv4 address or the collector image pull fails, tracing setup fails the job. World-writable reports simplify container writes but are broad permissions.

## Test Signals
Later report steps should find `otel-trace*.jsonl` under `/tmp/reports`, and test processes should be able to export OTLP over HTTP/protobuf.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/actions/setup-tracing/action.yml -->
