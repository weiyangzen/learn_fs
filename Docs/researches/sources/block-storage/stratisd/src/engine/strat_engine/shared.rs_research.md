# File Research: sources/block-storage/stratisd/src/engine/strat_engine/shared.rs

## Purpose
Provides small shared helpers used across strat-engine code.

## Main Components
- `merge(origin, snap)` constructs merged filesystem metadata when reverting an origin filesystem to a snapshot.
- `shift_allocation_offset()` maps an offset transformation over allocation-like items and collects `StratisResult<Vec<T>>`.

## Behavior
`merge()` preserves origin identity fields such as name, UUID, creation timestamp, origin reference, and merge flag, while taking the snapshot thin ID, size, and size limit. This models snapshot merge semantics where the original filesystem identity remains but its underlying thin device state is replaced by the snapshot state.

`shift_allocation_offset()` is generic over borrowed input values and a fallible mapper. It centralizes the pattern of converting a collection of allocation records after an offset adjustment.

## Research Notes
Although small, `merge()` encodes a key metadata invariant: snapshot reversion should not create a new user-visible filesystem identity.
