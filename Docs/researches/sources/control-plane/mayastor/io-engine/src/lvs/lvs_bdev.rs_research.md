# sources/control-plane/mayastor/io-engine/src/lvs/lvs_bdev.rs

## Purpose
This file wraps SPDK's `lvol_store_bdev` structure, which links an lvol store to its backing bdev.

## Important APIs, types, and functions
`LvsBdev` stores `NonNull<lvol_store_bdev>`. `from_inner_ptr` constructs it from an SPDK pointer. `lvs` returns the `Lvs` store. `lvs_opt` hides stores whose base bdev is no longer present. `name` returns the pool name. `base_bdev` wraps the backing SPDK bdev pointer as `UntypedBdev`. `iter` returns an `LvsBdevIter`.

## Control flow
The wrapper is synchronous and pointer-based: read SPDK struct fields, convert inner pointers into Rust wrappers, and optionally filter invalid/removing stores through `base_bdev_opt`.

## State and persistence behavior
No persistence is performed. The struct is a borrowed view of live SPDK global state and is only valid while SPDK keeps the underlying object alive.

## Dependencies and integration points
It depends on `spdk_rs::libspdk::lvol_store_bdev`, `crate::core::{Bdev, UntypedBdev}`, and LVS iterator/store wrappers. `LvsIter` uses it to enumerate pools.

## Risks and test signals
The file documents the core risk: holding this wrapper across async/reactor progress can leave dangling pointers if the pool is destroyed. `base_bdev` unwraps pointer conversion and will panic on invalid SPDK state. Tests should exercise iteration and filtering of removing stores in controlled SPDK integration tests.
