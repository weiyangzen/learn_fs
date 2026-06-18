# sources/control-plane/mayastor/io-engine/src/eventing/host_events.rs

## Purpose
Builds metadata and event messages for host initiator events against NVMe-oF subsystems, nexus targets, and replica targets.

## Important APIs, Types, and Functions
- `HostTargetMeta` adds target details to existing event metadata.
- Implementations for `Nexus` and `Lvol` tag target type and UUID.
- `EventMetaGen for NvmfSubsystem` adds subsystem NQN metadata.
- `EventWithMeta for NvmfController` adds host initiator NQN and produces `HostInitiator` events.

## Control Flow and State
Target code starts with metadata from a subsystem or target, then host controller event creation adds initiator host NQN and emits a message with empty target field and host initiator category. Nexus and Lvol target metadata helpers mutate existing `EventMeta` only when a source is present.

No state is stored.

## Dependencies and Integration Points
Depends on `events_api`, `Nexus`, `LogicalVolume`, `Lvol`, `NvmfSubsystem`, `NvmfController`, and `MayastorEnvironment`. Used by NVMe-oF connect/disconnect and host event paths.

## Risks and Test Signals
Metadata enrichment silently does nothing if `meta.source` is absent. Replica target data uses `Lvol::uuid`, while nexus uses `Nexus::uuid`. Tests should cover source-present/source-absent metadata, target type strings, and host NQN population.
