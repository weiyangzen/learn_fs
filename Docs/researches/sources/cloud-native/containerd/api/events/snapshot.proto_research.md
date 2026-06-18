# sources/cloud-native/containerd/api/events/snapshot.proto

Purpose: protobuf schema for snapshot lifecycle events.

Important APIs/types/functions: defines `SnapshotPrepare`, `SnapshotCommit`, and `SnapshotRemove`. Common fields are `key` and `snapshotter`; prepare also carries `parent`, commit carries final `name`. Fieldpath generation is enabled.

Control flow: declarative only. Snapshot service code emits these messages around snapshot prepare, commit, and removal operations.

State/persistence: message field numbers are persistent API state. `snapshotter = 5` indicates reserved/legacy numbering space and must remain stable.

Dependencies/integration: imports `types/fieldpath.proto`; generated Go uses package `events`. Used by event publication, filtering, and snapshotter-specific consumers.

Risks/test signals: key/name semantics differ between active snapshot keys and committed snapshot names; tests should ensure consumers do not confuse them. Compatibility testing should preserve field numbers.
