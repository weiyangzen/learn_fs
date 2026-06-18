# sources/cloud-native/moby/daemon/internal/distribution/transport.go

## Purpose
Builds registry HTTP transports with request modifiers and OpenTelemetry instrumentation.

## APIs, Control Flow, and Integration
`newTransport` wraps the base round tripper with Docker distribution `transport.NewTransport` to apply headers/auth modifiers, then wraps that with `otelhttp.NewTransport` so trace context is propagated.

## State, Dependencies, and Risks
No state. Risks include modifier ordering being determined by caller-provided order and observability wrapping changing transport type/behavior. This helper is used by `newRepository` for both unauthenticated ping and authenticated repository operations.
