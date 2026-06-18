# sources/cloud-native/buildkit/util/tracing/tracing.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package tracing; functions/methods StartSpan, hasStacktrace, FinishWithError, ContextWithSpanFromContext, NewTransport; package vars DefaultTransport, DefaultClient.

## Control Flow And Integration Points
The file is 86 lines in tracing and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: BuildKit packages: github.com/moby/buildkit/util/bklog, github.com/moby/buildkit/util/stack; external packages: context, fmt, net/http, net/http/httptrace, github.com/pkg/errors, go.opentelemetry.io/contrib/instrumentation/net/http/httptrace/otelhttptrace, go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp, go.opentelemetry.io/otel/attribute, go.opentelemetry.io/otel/codes, go.opentelemetry.io/otel/propagation, go.opentelemetry.io/otel/trace, go.opentelemetry.io/otel/trace/noop. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.
