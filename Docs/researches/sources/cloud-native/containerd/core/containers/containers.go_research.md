# sources/cloud-native/containerd/core/containers/containers.go

Purpose: core container metadata model and storage interface.

Important APIs/types: `Container` captures namespace-scoped `ID`, mutable `Labels`, `Image`, runtime `Spec`, optional `SnapshotKey`, immutable `Runtime`, `Snapshotter`, and `SandboxID`, timestamps, and typed `Extensions`. `RuntimeInfo` holds runtime name and typed options. `Store` defines CRUD and filtered list operations.

Control flow and state: no implementation, only contracts. Comments document mutability rules that store implementations must enforce: ID/runtime/snapshotter/sandbox identity fields are immutable while labels/image/spec/snapshot key are mutable.

Dependencies and integration: uses `context.Context`, timestamps, and `typeurl.Any` for runtime options, OCI specs, and extensions. Store implementations are provided elsewhere, commonly metadata-backed services.

Risks: invariants are comment-level in this file; enforcement depends on backing stores. Typeurl payload compatibility matters for persisted specs/options. Partial updates rely on implementation-specific fieldpath handling.

Test signals: none in this file. Tests should target store implementations for immutability, namespace isolation, fieldpath updates, and extension round-trips.
