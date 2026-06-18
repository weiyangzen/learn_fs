<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/provider.go -->
# sources/cloud-native/moby/daemon/internal/otelutil/provider.go

Purpose: creates an OpenTelemetry tracer provider for Docker with BuildKit's exporter detection and baggage copying.

Important APIs and types: `NewTracerProvider(ctx, allowNoop)`.

Control flow: attempts to detect a span exporter. On detection failure, returns noop only when allowed; otherwise it proceeds with the possibly nil/none exporter path. If noop is allowed and exporter is explicitly none, returns noop. Otherwise builds an SDK provider with default resource, sync recorder, batch exporter, and baggage-copy span processor.

State and persistence: returns provider and shutdown function; no package state.

Dependencies and integration: depends on BuildKit tracing detection, OTel SDK, baggagecopy processor, and Docker logging.

Risks: behavior when exporter detection fails and `allowNoop` is false depends on downstream exporter value. Sync recorder plus batcher must be shut down by caller.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/provider.go -->
