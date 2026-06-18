# sources/cloud-native/buildkit/util/tracing/detect/recorder.go

## Purpose
in-memory trace recorder/exporter that stores spans by TraceID with listener tracking and background garbage collection.

## Important APIs, Types, Functions, Or Configuration
package detect; types TraceRecorder, stubs; functions/methods NewTraceRecorder, Record, gcLoop, gc, ExportSpans, Shutdown; package vars Recorder.

## Control Flow And Integration Points
The file is 165 lines in detect and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, sync, time, github.com/pkg/errors, go.opentelemetry.io/otel/sdk/trace, go.opentelemetry.io/otel/sdk/trace/tracetest, go.opentelemetry.io/otel/trace, golang.org/x/sync/semaphore. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.
