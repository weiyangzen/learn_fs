# sources/control-plane/mayastor/io-engine/src/eventing/mod.rs

## Purpose
Declares the eventing module tree and the small traits used by io-engine domain objects to generate event messages and metadata.

## Important APIs, Types, and Functions
- Module declarations for clone, host, io-engine, nexus child, nexus, pool, replica, and snapshot events.
- `Event` trait creates a plain `EventMessage`.
- `EventWithMeta` creates an `EventMessage` using supplied metadata.
- `EventMetaGen` creates reusable `EventMeta`.

## Control Flow and State
There is no runtime flow here. Implementations in sibling modules attach these traits to domain types such as `Nexus`, `Lvol`, `SnapshotParams`, `CloneParams`, `NvmfSubsystem`, and `Reactor`.

No state or persistence exists in this file.

## Dependencies and Integration Points
Depends on `events_api::event::{EventAction, EventMessage, EventMeta}`. This is the compile-time hub used by environment and storage components before messages are passed to the event transport.

## Risks and Test Signals
Trait visibility is mixed: `Event` is public within the crate API surface, while metadata helpers are crate-private. Tests should cover that all event modules remain compiled and that changes to events-api types propagate through trait signatures.
