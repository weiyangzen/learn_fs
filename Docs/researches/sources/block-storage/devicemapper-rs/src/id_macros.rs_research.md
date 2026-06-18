# File Research: sources/block-storage/devicemapper-rs/src/id_macros.rs

## Purpose
Defines macros for restricted device-mapper string identifier types.

## Key Macros
`str_check!` validates ASCII, non-empty, maximum-length strings. `str_id!` generates borrowed unsized and owned identifier types with `new`, `as_bytes`, `ToOwned`, `Display`, `AsRef`, `Borrow`, and `Deref`.

## Behavior
Borrowed identifiers are created by unsafe transparent cast from `str` after validation. Owned identifiers validate at construction and deref by re-validating invariant-held inner strings.

## Tests/Notes
Tests cover empty and overlong rejection, bytes, ownership conversion, display, and deref behavior.
