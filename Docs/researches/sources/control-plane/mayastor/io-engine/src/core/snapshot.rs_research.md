# sources/control-plane/mayastor/io-engine/src/core/snapshot.rs

## Purpose
Defines snapshot and clone parameter models, snapshot listing descriptors, LVS extended attribute names, and descriptor access traits shared by replica backends.

## Important APIs, Types, and Functions
- `SnapshotParams` stores entity, parent, transaction, name, UUID, create time, and discarded flag.
- `CloneParams` stores clone name/UUID, source UUID, and creation time.
- `SnapshotInfo` and `SnapshotDescriptor` bundle backend snapshot object plus generic metadata.
- `PropXattrs`, `SnapshotXattrs`, and `CloneXattrs` map logical properties to LVS xattr C strings.
- `ISnapshotDescriptor` abstracts snapshot parameter getters/setters and is implemented for `SnapshotParams`.
- Re-exports `LvolSnapshotOps`.

## Control Flow and State
`prepare` constructors validate required string inputs and add `chrono::Utc::now()` timestamps. Backend code stores and retrieves fields via xattrs. Snapshot descriptors combine a boxed `SnapshotOps` implementation with collected metadata for list responses. `discarded_snapshot` models deferred delete when clones still reference a snapshot.

State in this file is data only. Persistence occurs when backends write the named xattrs to LVS/LVM metadata.

## Dependencies and Integration Points
Used by replica backend traits, LVS snapshot implementation, LVM module, NVMf admin snapshot command decoding, and eventing. Depends on `serde`, `chrono`, `strum`, and backend traits.

## Risks and Test Signals
Several getters clone strings, and validation is limited to non-empty fields. `BrokenEntityId` documents an xattr representation mismatch. Tests should cover xattr names, prepare validation, discarded snapshot propagation, clone metadata round trips, and backend compatibility for snapshot UUID and entity ID fields.
