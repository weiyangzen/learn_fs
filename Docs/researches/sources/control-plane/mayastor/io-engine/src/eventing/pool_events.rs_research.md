# sources/control-plane/mayastor/io-engine/src/eventing/pool_events.rs

## Purpose
Generates pool event messages from `Lvs` pool objects.

## Important APIs, Types, and Functions
- Implements `Event` for `Lvs`.
- Event category is `Pool`; target is `Lvs::name()`.

## Control Flow and State
Pool lifecycle code calls `Lvs::event(action)` to build a message with current global/default node name and no extra pool metadata beyond target.

No state is stored.

## Dependencies and Integration Points
Depends on `events_api`, `MayastorEnvironment`, and `lvs::Lvs`. Used by pool create/import/destroy related event paths.

## Risks and Test Signals
The event target is pool name, not UUID, so consumers needing stable identity must correlate elsewhere. Tests should assert category, action, target, and node metadata.
