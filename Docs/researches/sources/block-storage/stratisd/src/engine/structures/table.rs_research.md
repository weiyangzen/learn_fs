# File Research: sources/block-storage/stratisd/src/engine/structures/table.rs

## Purpose

This file implements `Table<U, T>`, a bidirectional name/UUID-indexed container used throughout the engine to store named objects while allowing O(1) lookup by either `Name` or UUID-like key.

Internally it keeps:

- `name_to_uuid: HashMap<Name, U>`
- `items: HashMap<U, (Name, T)>`

`U` must implement `AsUuid`, which provides the copy/hash/equality traits expected by the table.

## Public Types

- `Table<U, T>`: main container.
- `Iter<'a, U, T>`: immutable iterator yielding `(&Name, &U, &T)`.
- `IterMut<'a, U, T>`: mutable iterator yielding `(&Name, &U, &mut T)`.
- `IntoIter<U, T>`: owning iterator yielding `(Name, U, T)`.

`IntoIterator` is implemented for owned, shared, and mutable references to `Table`.

`FromIterator<(Name, U, T)>` builds a table by repeated insertion.

`Debug` renders as a debug map keyed by `(name_string, uuid)`.

## Main API

- `is_empty()`
- `len()`
- `iter()`
- `iter_mut()`
- `contains_name(name)`
- `contains_uuid(uuid)`
- `get_by_name(name) -> Option<(U, &T)>`
- `get_by_uuid(uuid) -> Option<(Name, &T)>`
- `get_mut_by_name(name) -> Option<(U, &mut T)>`
- `get_mut_by_uuid(uuid) -> Option<(Name, &mut T)>`
- `remove_by_name(name) -> Option<(U, T)>`
- `remove_by_uuid(uuid) -> Option<(Name, T)>`
- `insert(name, uuid, item) -> Option<Vec<(Name, U, T)>>`

Lookups by UUID clone the `Name` for return. Lookups by name return the UUID by copy.

## Insert Semantics

`insert()` keeps the two maps consistent while allowing replacement by name, UUID, or both.

It can displace:

- no item, when both name and UUID are new
- one item, when inserting the same name or same UUID
- one item, when replacing the same `(name, uuid)` pair
- two items, when the new item uses the name of one existing item and the UUID of another

When two items are displaced, the item displaced by matching name is returned first. The method contains assertions documenting invariants between both maps.

## Invariants

The intended invariant is:

- every `items` entry has a matching `name_to_uuid[name] == uuid`
- every `name_to_uuid` entry has a matching `items[uuid].0 == name`
- both maps have the same length
- there are no stale name or UUID entries after insertion/removal

The test helper `table_invariant()` checks exactly these relationships.

## Test Coverage

Tests cover:

- removing an existing item by UUID and verifying name lookup is also removed
- inserting the same `(name, uuid)` pair and receiving the old item
- inserting a new UUID under an existing name
- inserting a new name under an existing UUID
- inserting a pair that collides with one existing name and a different existing UUID, returning two displaced items in documented order

The tests use `PoolUuid` as the UUID type and a `TestThing` payload with random data to verify the correct item is retained or displaced.

## Integration Notes

`Table` is used by `ThinPool` to store filesystems by `FilesystemUuid` and `Name`, and by `AllOrSomeLock` to expose name/UUID-addressable pools. Its removal and displacement behavior is important for code that temporarily removes an object, mutates metadata, and reinserts it under a new name.

## Correctness Notes

- Operations are intended to be O(1), with name lookup requiring one extra map hop to the UUID-keyed map.
- Rename is intentionally modeled as remove and reinsert.
- `insert()` does not reject collisions; callers must inspect displaced items or validate uniqueness before calling when replacement is not acceptable.
