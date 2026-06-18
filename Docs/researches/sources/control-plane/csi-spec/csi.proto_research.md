# sources/control-plane/csi-spec/csi.proto

## Purpose

This generated proto file is the CSI v1 gRPC API contract. It defines services, messages, enums, annotations for alpha APIs and secrets, and all request/response shapes used between container orchestrators and storage plugins.

## Important APIs and Flow

Services are `Identity`, `Controller`, `GroupController`, alpha `SnapshotMetadata`, and `Node`. Identity exposes plugin info, capabilities, and readiness probe. Controller covers volume lifecycle, publish/unpublish, validation, listing, capacity, capabilities, snapshots, expansion, alpha get-volume/get-snapshot, and modify-volume. GroupController covers group snapshot capabilities and group snapshot create/delete/get. SnapshotMetadata streams allocated or changed block metadata. Node covers staging, publishing, stats, expansion, capabilities, and node info.

Core messages include `PluginCapability`, `VolumeCapability`, `CapacityRange`, `Volume`, `TopologyRequirement`, `Topology`, controller publish/validate/list/capability messages, `Snapshot`, node publish/stage/stat messages, `VolumeCondition`, group snapshot structures, and block metadata structures. Custom protobuf options mark secret fields (`csi_secret`) and alpha enums, fields, messages, methods, and services.

## State, Dependencies, and Integration

The file has no runtime state itself, but it defines persistent wire compatibility. Dependencies are protobuf compiler support, gRPC generators, `google.protobuf.Timestamp`, wrappers, and descriptor extensions. It integrates with generated Go bindings in `lib/go/csi`, external CSI implementations, Kubernetes sidecars, and docs generated from `spec.md`.

## Risks and Test Signals

Field numbers and service/method names are compatibility-critical and must not be changed casually. Secret annotations are important because COs and plugins must avoid logging sensitive maps. Alpha annotations warn that APIs can change. Risks include generated file drift from `spec.md`, line-length formatting failures, and breaking generated bindings. Test signals are top-level `make`, clean git diff in CI, and downstream CSI conformance/sanity tests.
