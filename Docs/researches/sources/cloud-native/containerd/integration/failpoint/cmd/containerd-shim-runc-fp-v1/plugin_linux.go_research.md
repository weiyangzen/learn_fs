# sources/cloud-native/containerd/integration/failpoint/cmd/containerd-shim-runc-fp-v1/plugin_linux.go

## Purpose

This Linux shim plugin wraps the runc task ttrpc service with failpoint evaluation driven by OCI annotations. It lets tests inject errors into specific shim task API calls such as `Shutdown`.

## Important APIs, Types, And Functions

- `failpointPrefixKey` is the annotation prefix `io.containerd.runtime.v2.shim.failpoint.`.
- `init` registers a `plugins.TTRPCPlugin` named `task`.
- `taskServiceWithFp` stores parsed failpoints and the real task service.
- `UnaryServerInterceptor` evaluates a failpoint based on the ttrpc method basename before calling the underlying method.
- `newFailpointFromOCIAnnotation` reads `config.json` from the shim bundle and parses prefixed annotations.

## Control Flow

During plugin init, the code obtains the event publisher and shutdown service, reads failpoints from the OCI spec, constructs the normal runc task service, and returns `taskServiceWithFp`. The interceptor extracts the method name from `info.FullMethod`, evaluates a configured failpoint if present, then invokes the real ttrpc method. Registration still exposes the normal task service API.

## State And Persistence Behavior

Failpoint state is initialized from OCI annotations and then held in memory. Individual `Failpoint` objects may mutate internally as they are evaluated. The annotations are persisted in the bundle `config.json` generated for the shim.

## Dependencies And Integration Points

It integrates with containerd plugin registry, shim publisher/shutdown services, runc task service, OCI spec reading, ttrpc interceptors, and internal failpoint syntax.

## Risks And Edge Cases

The shim working directory must be the bundle directory so `config.json` resolves correctly. Annotation method names must match ttrpc method basenames. Invalid failpoint syntax fails shim plugin initialization.

## Test Signals

The skipped shutdown retry test and other failpoint runtime tests use this plugin to simulate shim task API failures deterministically.
