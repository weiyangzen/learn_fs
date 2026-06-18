# sources/cloud-native/containerd/api/events/snapshot_fieldpath.pb.go

Purpose: generated string fieldpath accessors for snapshot events.

Important APIs/types/functions: `SnapshotPrepare.Field` exposes `key`, `parent`, and `snapshotter`; `SnapshotCommit.Field` exposes `key`, `name`, and `snapshotter`; `SnapshotRemove.Field` exposes `key` and `snapshotter`.

Control flow: simple path length guard and first-segment switch; returns a field value only when the string is non-empty.

State/persistence: stateless derived access over an event message.

Dependencies/integration: no external imports. Integrates with event matching/filtering for snapshot-related event topics.

Risks/test signals: empty strings are considered undefined, so a valid empty parent cannot be matched as present. Tests should verify filter behavior for root snapshots where parent may be empty.
