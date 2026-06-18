# File Research: sources/block-storage/thin-provisioning-tools/src/utils/hashvec.rs

## Purpose
Implements `HashVec<T>`, a compact associative container that maps `u32` logical indexes to dense vector slots while preserving value iteration over insertion order.

## Main Components
- `map: HashMap<u32, u32>` maps external indexes to positions in `entries`.
- `entries: Vec<T>` stores values densely.
- `Default` delegates to `new()`.
- `new()` and `with_capacity()` construct empty containers.
- `insert()` updates an existing index in place or appends a new value and stores its vector position.
- `get()` and `get_mut()` access by external index.
- `len()`, `is_empty()`, `reserve()`, and `values()` expose collection utilities.

## Behavior
Updating an existing key replaces the existing vector element and does not change iteration order or length. Inserting a new key appends to `entries`, so `values()` iterates in first-insertion order, not key order.

## Research Notes
`T: Clone` is required for the whole impl because `insert()` uses `value.clone()` in the update branch before moving `value` in the insertion branch. The map index type is fixed to `u32`, with a TODO noting possible parameterization.
