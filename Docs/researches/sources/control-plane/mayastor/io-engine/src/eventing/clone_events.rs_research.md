# sources/control-plane/mayastor/io-engine/src/eventing/clone_events.rs

## Purpose
Adds event generation for clone lifecycle operations represented by `CloneParams`.

## Important APIs, Types, and Functions
- Implements `Event` for `CloneParams`.
- Builds `EventSource` with node name, source UUID, and clone creation time.

## Control Flow and State
When a clone action occurs, callers invoke `CloneParams::event(action)`. The event category is `Clone`, the target is the clone UUID or empty string, and metadata includes clone source information derived from the current global/default environment node name.

No state is persisted by this file; generated messages are handed to the eventing transport elsewhere.

## Dependencies and Integration Points
Depends on `events_api::event`, `CloneParams`, and `MayastorEnvironment`. Used by clone creation/deletion paths that emit events.

## Risks and Test Signals
Missing optional fields become empty strings, so event consumers must tolerate incomplete metadata. Tests should assert category/action/target mapping and metadata values for complete and partial `CloneParams`.
