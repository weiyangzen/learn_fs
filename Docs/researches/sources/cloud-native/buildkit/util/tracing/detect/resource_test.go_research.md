# sources/cloud-native/buildkit/util/tracing/detect/resource_test.go

## Purpose
test coverage for the adjacent package behavior, using table tests, integration sandboxes, or worker execution helpers depending on package.

## Important APIs, Types, Functions, Or Configuration
package detect; functions/methods TestResource; tests TestResource.

## Control Flow And Integration Points
The file is 39 lines in detect and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: testing, github.com/stretchr/testify/require, go.opentelemetry.io/otel. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestResource.
