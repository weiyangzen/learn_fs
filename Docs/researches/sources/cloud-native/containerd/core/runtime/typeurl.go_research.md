<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/typeurl.go -->
# sources/cloud-native/containerd/core/runtime/typeurl.go

## Purpose
Registers common OCI runtime-spec and feature types with containerd's typeurl system.

## Important APIs, Types, And Functions
- `init()` registers `specs.Spec`, `specs.Process`, `specs.LinuxResources`, `specs.WindowsResources`, and `features.Features` under the `types.containerd.io` prefix with the OCI runtime-spec major version.

## Control Flow
Registration runs at package initialization. The major version is derived from `specs.VersionMajor`.

## State And Persistence
Mutates global typeurl registration state. No local state is kept.

## Dependencies And Integration Points
Enables `typeurl.Any` fields in runtime create/update options to serialize and deserialize OCI spec/resource types. Integrates with runtime services and shim protocols.

## Risks And Edge Cases
Registration names depend on the OCI runtime-spec major version. Missing registration would break decoding of runtime option payloads.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/typeurl.go -->
