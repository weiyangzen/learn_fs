<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/baggage.go -->
# sources/cloud-native/moby/daemon/internal/otelutil/baggage.go

Purpose: provides helpers for constructing static OpenTelemetry baggage members and baggage values.

Important APIs and types: constant `TriggerKey`, `MustNewBaggage`, and `MustNewMemberRaw`.

Control flow: each helper calls the OTel constructor and logs fatal on error. Comments warn not to use dynamic values.

State and persistence: none.

Dependencies and integration: used by tracing instrumentation for static baggage such as trigger metadata.

Risks: fatal logging exits the process on invalid input, so callers must only pass compile-time/static values.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/baggage.go -->
