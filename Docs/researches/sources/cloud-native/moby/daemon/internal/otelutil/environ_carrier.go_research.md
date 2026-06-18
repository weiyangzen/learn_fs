<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/environ_carrier.go -->
# sources/cloud-native/moby/daemon/internal/otelutil/environ_carrier.go

Purpose: implements an OpenTelemetry text-map carrier for propagating trace context through environment variables.

Important APIs and types: `EnvironCarrier`, `Get`, `Set`, `Keys`, `Environ`, and `PropagateFromEnvironment`.

Control flow: supports only `traceparent` and `tracestate` keys. `Environ` emits uppercase `TRACEPARENT`/`TRACESTATE` entries for non-empty values. `PropagateFromEnvironment` reads those env vars.

State and persistence: carrier stores two strings in memory and serializes to environment entries.

Dependencies and integration: used when daemon code needs to pass trace context to child processes.

Risks: unsupported keys are silently ignored. It does not parse or validate trace context values.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/environ_carrier.go -->
