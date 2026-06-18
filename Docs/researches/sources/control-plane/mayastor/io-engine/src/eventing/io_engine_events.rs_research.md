# sources/control-plane/mayastor/io-engine/src/eventing/io_engine_events.rs

## Purpose
Creates io-engine and reactor event messages, including shutdown duration metadata and reactor freeze/unfreeze details.

## Important APIs, Types, and Functions
- `io_engine_stop_event_meta(total_time)` produces duration metadata.
- Implements `Event` and `EventWithMeta` for `MayastorEnvironment`.
- Implements `Event` for `Reactor`.

## Control Flow and State
Environment events use category `IoEngineCategory`, action from caller, target as environment name, and node metadata. Stop events can include elapsed shutdown duration. Reactor events use the reactor TID as target and include core number plus current reactor state in metadata.

No persistent state is stored; messages are generated for the event bus.

## Dependencies and Integration Points
Used by environment startup/shutdown and reactor freeze monitor. Depends on `events_api`, `MayastorEnvironment`, and `Reactor`.

## Risks and Test Signals
Reactor target is `tid().to_string()`, which is `0` before the reactor records its TID. Tests should verify shutdown duration metadata, environment target naming, and reactor core/state metadata for each state.
