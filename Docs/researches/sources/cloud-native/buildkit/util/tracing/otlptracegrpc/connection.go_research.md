# sources/cloud-native/buildkit/util/tracing/otlptracegrpc/connection.go

## Purpose
OTLP gRPC connection manager for an existing ClientConn with disconnected state, reconnect loop, stop context, and shutdown handling.

## Important APIs, Types, Functions, Or Configuration
package otlptracegrpc; types Connection; functions/methods NewConnection, StartConnection, LastConnectError, saveLastConnectError, SetStateDisconnected, setStateConnected, Connected, indefiniteBackgroundConnection, connect, ContextWithMetadata, Shutdown, ContextWithStop.

## Control Flow And Integration Points
The file is 219 lines in otlptracegrpc and participates in this package role: BuildKit tracing support. The files adapt OpenTelemetry propagation, exporters, gRPC stats, trace forwarding, resource detection, and protobuf-to-SDK span conversion. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points include OpenTelemetry SDK/exporters, environment variables, appcontext, child process env, gRPC stats handlers, HTTP instrumentation, and BuildKit client tracer delegates. Risks include global detector/resource state, exporter shutdown/deadlock behavior, and compatibility with deprecated Jaeger/env conventions.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: context, math/rand, sync, sync/atomic, time, unsafe, github.com/pkg/errors, google.golang.org/grpc, google.golang.org/grpc/metadata. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.
