<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/introspection.pb.go -->
# sources/cloud-native/containerd/api/types/introspection.pb.go

## Purpose
Generated Go bindings for runtime introspection messages used to query runtime/shim identity, configuration, features, and annotations.

## Important APIs and Types
`RuntimeRequest` has `RuntimePath` and runtime-specific `Options *anypb.Any`. `RuntimeVersion` has `Version` and `Revision`. `RuntimeInfo` has `Name`, `Version`, `Options`, `Features`, and `Annotations map[string]string`.

## Control Flow
No business logic. Initialization builds descriptors for three messages and the generated annotation map entry. Accessors are nil-safe.

## State and Persistence
The messages carry runtime discovery state but do not persist it. `Options` corresponds to task create options; `Features` is expected to carry OCI-compatible runtime feature data; annotations describe shim metadata.

## Dependencies and Integration Points
Depends on protobuf `Any` and runtime/reflection. Used by containerd runtime managers and CRI paths that query shim/runtime capabilities.

## Risks
`Any` fields require known type URLs and version-compatible decoding. Feature payloads need clear schema expectations, especially for OCI runtime feature documents. Annotation maps have nondeterministic marshal order without deterministic settings.

## Test Signals
Runtime info query tests, `Any` decoding tests for runc/runtime options and features, map serialization tests where deterministic output matters, and backward-compatibility tests for older shims.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/introspection.pb.go -->
