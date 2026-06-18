# sources/control-plane/mayastor/io-engine/src/eventing/nexus_events.rs

## Purpose
Creates nexus, nexus child, rebuild, pause, state-change, and error event metadata/messages.

## Important APIs, Types, and Functions
- `EventMetaGen for NexusRebuildJob` maps rebuild states to `RebuildStatus` and includes source/destination URI plus error text.
- `EventMetaGen for NexusChild` includes child URI.
- `state_change_event_meta(previous, next)` records nexus state transitions.
- `subsystem_pause_event_meta(status, total_time, error)` records pause status, duration, and optional error.
- Implements `Event` and `EventWithMeta` for `nexus::Nexus`.
- `EventMetaGen for Error` converts nexus errors into event metadata.

## Control Flow and State
Rebuild jobs and nexus operations generate metadata at transition points. Nexus events use category `Nexus`, target as nexus UUID, and either default node metadata or supplied metadata. Pause metadata starts with node and pause status, then optionally adds elapsed duration and error detail.

No state is stored; it reflects caller-provided object state at generation time.

## Dependencies and Integration Points
Depends on nexus types, rebuild state, `VerboseError`, `events_api`, and `MayastorEnvironment`. Called from rebuild and nexus control/data paths.

## Risks and Test Signals
Unknown rebuild states fall back to `RebuildStatus::Unknown`. Error metadata for rebuild uses verbose error chains, while nexus error metadata uses `to_string`, so detail level differs. Tests should cover each rebuild state, pause metadata combinations, state transitions, and category/target correctness.
