# sources/control-plane/mayastor/io-engine/src/eventing/replica_events.rs

## Purpose
Creates replica and replica-child state event messages.

## Important APIs, Types, and Functions
- Implements `Event` for `Lvol`, producing `Replica` category messages.
- `state_change_event_meta(previous, next)` records `ChildState` transitions.
- Implements `EventWithMeta` for `NexusChild`, using the child UUID as target.

## Control Flow and State
Replica events derive pool name, pool UUID, and replica name from the `Lvol` and use the logical volume UUID as target. Nexus child state events use supplied metadata and target the child UUID or an empty string.

No state is stored.

## Dependencies and Integration Points
Depends on `events_api`, `LogicalVolume`, LVS lvol traits, `ChildState`, `NexusChild`, and `MayastorEnvironment`. Used by replica lifecycle and nexus child state transitions.

## Risks and Test Signals
`NexusChild::get_uuid()` may be absent, leading to empty target. Tests should cover replica metadata values, child state transition metadata, and missing UUID behavior.
