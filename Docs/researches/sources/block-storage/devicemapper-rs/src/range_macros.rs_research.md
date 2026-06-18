# File Research: sources/block-storage/devicemapper-rs/src/range_macros.rs

## Purpose
Generates strongly-typed numeric wrappers for storage units/ranges.

## Key Macros
`range_u64!`, `range_u128!`, `range!`, arithmetic macros for add/sub/mul/div/rem, `checked_add!`, `sum!`, `serde_macro!`, `display!`, `debug_macro!`, and `deref!`.

## Behavior
Generated types are tuple structs with default/order/hash/copy semantics, arithmetic with same-type and primitive RHS values, `Sum`, deref to inner numeric type, serde numeric serialization, and checked addition.

## Tests/Notes
Tests instantiate `Units` and verify derivations, display/debug, sum, arithmetic, checked overflow, and remainder/division behavior.
