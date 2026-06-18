# sources/control-plane/mayastor/io-engine/src/eventing/snapshot_events.rs

## Purpose
Generates snapshot event messages from `SnapshotParams`.

## Important APIs, Types, and Functions
- Implements `Event` for `SnapshotParams`.
- Metadata includes parent ID, create time, and entity ID through `with_snapshot_data`.
- Target is the snapshot UUID or an empty string.

## Control Flow and State
Snapshot lifecycle code calls `SnapshotParams::event(action)` after preparing or loading snapshot parameters. Optional fields default to empty strings in the event message.

No state is stored here.

## Dependencies and Integration Points
Depends on `events_api`, `ISnapshotDescriptor`, `MayastorEnvironment`, and `SnapshotParams`. Used by snapshot create/delete/reporting paths.

## Risks and Test Signals
Missing optional metadata is silently represented as empty strings. Tests should assert target UUID, category, action, and metadata for complete and incomplete snapshot params.
