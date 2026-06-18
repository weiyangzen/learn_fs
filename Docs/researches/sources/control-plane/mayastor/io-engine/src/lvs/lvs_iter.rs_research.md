# sources/control-plane/mayastor/io-engine/src/lvs/lvs_iter.rs

## Purpose
This file provides iterators over SPDK lvol stores by walking SPDK's global lvol-store-bdev list.

## Important APIs, types, and functions
`LvsBdevIter` holds the current `lvol_store_bdev` pointer and a `list_removing` flag. `LvsIter` wraps `LvsBdevIter` and yields `Lvs` stores rather than the backing bdev wrapper.

## Control flow
`LvsBdevIter::new` starts at `vbdev_lvol_store_first`. Each `next` returns the current wrapper and advances through `vbdev_lvol_store_next`. `LvsIter::next` either yields every store, including removing ones, or filters through `lvs_opt` so stores without base bdevs are hidden.

## State and persistence behavior
The iterator stores only live raw pointer cursor state. It does not persist data and must be treated as a synchronous view over SPDK global state.

## Dependencies and integration points
It depends on SPDK FFI list functions and `LvsBdev`. `Lvs::iter` and `Lvs::iter_all` expose these iterators to pool listing/export flows.

## Risks and test signals
The raw pointer cursor can become invalid if the SPDK list changes during iteration. Filtering behavior is important for export/removal paths: normal iteration hides removing pools, while `iter_all` includes them. Integration tests should cover both modes and pool cleanup during removal.
