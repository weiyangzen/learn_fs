# sources/control-plane/csi-lib-utils/rpc/common.go

## Purpose

This Go package provides common client-side CSI RPC helpers for querying driver identity, plugin/controller/group-controller capabilities, and probing readiness.

## Important APIs and Flow

`GetDriverName` calls Identity `GetPluginInfo` and rejects an empty name. `PluginCapabilitySet`, `ControllerCapabilitySet`, and `GroupControllerCapabilitySet` are maps keyed by CSI enum types. `GetPluginCapabilities`, `GetControllerCapabilities`, and `GetGroupControllerCapabilities` call the corresponding CSI service, skip nil capability wrappers, and populate set maps. `Probe` calls Identity `Probe` once and treats a missing `ready` field as ready per CSI spec. `ProbeForever` loops once per second, using `probeOnce` with a per-call timeout. It retries only `DeadlineExceeded` and `ready=false`; non-gRPC errors and other gRPC errors are returned.

## State, Dependencies, and Integration

There is no persistent state. Runtime state is the caller's context, gRPC connection, ticker, and transient capability maps. Dependencies include `google.golang.org/grpc`, gRPC status codes, CSI generated Go bindings, and `k8s.io/klog/v2` for contextual logging. It integrates with CSI sidecars and libraries that need standardized driver interrogation.

## Risks and Test Signals

`ProbeForever` can run indefinitely until context cancellation if a driver repeatedly times out or reports unready. Capability helpers intentionally ignore nil entries, which avoids panics but can hide malformed responses. Tests in `common_test.go` cover success, errors, empty names, nil capability entries, missing ready fields, timeout retry, unready retry, and probe-call counts.
