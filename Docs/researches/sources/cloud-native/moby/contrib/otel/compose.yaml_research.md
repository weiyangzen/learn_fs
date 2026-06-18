# sources/cloud-native/moby/contrib/otel/compose.yaml

## Purpose
Defines a local OpenTelemetry observation stack for Moby development.

## APIs, Types, And Functions
The Compose project `moby-otel` defines services for Jaeger all-in-one, Aspire dashboard, and OpenTelemetry Collector. It exposes Jaeger UI on 16686, Aspire dashboard on 18888, and OTLP HTTP on 4318.

## Control Flow, State, And Integration
Compose starts the tracing backends, makes the collector depend on dashboards, and uses a develop watch rule to sync and restart the collector when `otelcol.yaml` changes. State is service containers and collected trace data.

## Risks And Test Signals
Risks include `latest` image drift, unsecured dashboard access, host port conflicts, and collector config syntax issues. Integration is with Moby OTLP HTTP trace emission.
