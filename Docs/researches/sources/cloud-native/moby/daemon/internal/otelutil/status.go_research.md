<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/status.go -->
# sources/cloud-native/moby/daemon/internal/otelutil/status.go

Purpose: records error status on an OpenTelemetry span.

Important APIs and types: `RecordStatus(span trace.Span, err error)`.

Control flow: if `err` is non-nil, records the error and sets span status to `codes.Error` with the error string. Nil errors leave span status unchanged.

State and persistence: mutates span state only.

Dependencies and integration: small helper for daemon tracing instrumentation.

Risks: error messages may include sensitive data if callers pass unredacted errors.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/status.go -->
