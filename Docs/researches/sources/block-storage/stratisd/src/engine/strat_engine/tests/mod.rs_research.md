# File Research: sources/block-storage/stratisd/src/engine/strat_engine/tests/mod.rs

## Purpose
Defines the strat-engine test-support module layout.

## Main Components
Exports or declares:
- `pub mod crypt`
- private `logger`
- `pub mod loopbacked`
- `pub mod real`
- private `util`
- `pub use util::FailDevice`

## Behavior
The module exposes public harnesses for encryption, loopbacked tests, real-device tests, and the `FailDevice` test utility while keeping logger and general cleanup internals private.

## Research Notes
This is a module index only, but it determines which test utilities are available to sibling test modules.
