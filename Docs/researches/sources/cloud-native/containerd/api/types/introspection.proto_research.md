<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/introspection.proto -->
# sources/cloud-native/containerd/api/types/introspection.proto

## Purpose
Canonical proto definitions for runtime introspection request and response payloads.

## Important APIs and Types
`RuntimeRequest` selects a runtime path and passes runtime options. `RuntimeVersion` reports version/revision. `RuntimeInfo` reports runtime name, version, options, OCI-compatible features, and shim annotations.

## Control Flow
Schema only. Runtime managers interpret requests and return info.

## State and Persistence
Carries runtime configuration and capability metadata at query time. It does not define storage.

## Dependencies and Integration Points
Imports protobuf `Any`. Comments tie `options` to `CreateTaskRequest.options` and point OCI-compatible runtimes to the OCI runtime-spec features document shape.

## Risks
The flexible `Any` fields can drift between runtimes if type contracts are not documented. Feature and annotation semantics need consumer-side validation.

## Test Signals
Runtime introspection integration tests, type-url compatibility tests, and feature decoding tests for OCI-compatible runtimes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/introspection.proto -->
