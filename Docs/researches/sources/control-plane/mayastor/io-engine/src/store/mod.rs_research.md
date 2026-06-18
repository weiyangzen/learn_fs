# sources/control-plane/mayastor/io-engine/src/store/mod.rs

## Purpose
This module root exposes the persistent-store backend implementation and shared store trait definitions.

## Important APIs, Types, And Functions
It declares `pub mod etcd;` and `pub mod store_defs;`.

## Control Flow
There is no runtime logic. The file controls module visibility for `crate::store::etcd` and `crate::store::store_defs`.

## State, Persistence, And Dependencies
No state is stored here. Persistence behavior lives in `etcd.rs` and `persistent_store.rs`.

## Integration Points
Other modules import store traits and the etcd backend through this module path.

## Risks
Making both modules public exposes low-level backend and trait details crate-wide. Any additional backend must be wired here.

## Test Signals
Compile-level tests/imports are sufficient; functional behavior belongs to child module tests.
