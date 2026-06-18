# sources/cloud-native/moby/contrib/otel/otelcol.yaml

## Purpose
Configures OpenTelemetry Collector to receive Moby traces and export them to Jaeger and Aspire.

## APIs, Types, And Functions
The config declares an OTLP receiver over gRPC on 4317 and HTTP on 4318, OTLP exporters for `jaeger:4317` and `aspire-dashboard:18889`, and a traces pipeline connecting receiver to both exporters.

## Control Flow, State, And Integration
At runtime the collector accepts trace signals, routes them through the traces pipeline, and forwards them to the configured backends. State is in-memory collector processing and backend storage.

## Risks And Test Signals
Risks include endpoint mismatches, TLS option syntax errors, and backend protocol incompatibility. Integration is with the companion Compose stack and Moby tracing configuration.
