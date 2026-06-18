# sources/cloud-native/buildkit/util/tracing/transform/span.go

## Purpose
OTLP ResourceSpans to sdktrace.ReadOnlySpan adapter, including span context, parent, kind, attributes, links, events, status, resource, and dropped counts.

## Important APIs, Types, Functions, Or Configuration
package transform; types readOnlySpan; functions/methods Spans, Name, SpanContext, Parent, SpanKind, StartTime, EndTime, Attributes, Links, Events, Status, InstrumentationScope, InstrumentationLibrary, Resource, DroppedAttributes, DroppedLinks, DroppedEvents, ChildSpanCount, statusCode, links, spanEvents, spanKind; package vars _.

## Control Flow And Integration Points
The file is 272 lines in transform and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: time, go.opentelemetry.io/otel/attribute, go.opentelemetry.io/otel/codes, go.opentelemetry.io/otel/sdk/instrumentation, go.opentelemetry.io/otel/sdk/resource, go.opentelemetry.io/otel/sdk/trace, go.opentelemetry.io/otel/trace, go.opentelemetry.io/proto/otlp/common/v1, go.opentelemetry.io/proto/otlp/resource/v1, go.opentelemetry.io/proto/otlp/trace/v1. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.
