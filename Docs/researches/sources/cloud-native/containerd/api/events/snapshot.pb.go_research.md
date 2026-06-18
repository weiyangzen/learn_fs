# sources/cloud-native/containerd/api/events/snapshot.pb.go

Purpose: generated Go protobuf bindings for snapshot events.

Important APIs/types/functions: `SnapshotPrepare` has `Key`, `Parent`, and `Snapshotter`; `SnapshotCommit` has `Key`, `Name`, and `Snapshotter`; `SnapshotRemove` has `Key` and `Snapshotter`. Each has standard protobuf methods and nil-safe getters.

Control flow: generated descriptor setup and getter access only. `rawDescGZIP` lazily compresses the schema descriptor; `file_events_snapshot_proto_init` registers three messages.

State/persistence: no state beyond serialized event payloads. The gap in field numbers (`snapshotter = 5`) preserves compatibility with earlier schema evolution.

Dependencies/integration: blank-imports containerd API types for fieldpath extension registration; uses protobuf runtime/reflection. Integrates with snapshotter operations and event filters.

Risks/test signals: field number 5 for `snapshotter` should not be compacted. Consumers should handle empty parent on prepare and absent snapshotter in older events. Tests should cover prepare/commit/remove event payloads and fieldpath lookups.
