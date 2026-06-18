# File Research: sources/block-storage/stratisd/src/engine/mod.rs

This is the public module facade for the `engine` subsystem.

Exports:
- Core traits:
  - `BlockDev`
  - `Engine`
  - `Filesystem`
  - `KeyActions`
  - `Pool`
  - `Report`
- Shared helpers:
  - `total_allocated`
  - `total_used`
- Simulator:
  - `SimEngine`
- Real Stratis engine items:
  - process/keyring/device-mapper setup helpers;
  - static header types;
  - `StratEngine`, `StratKeyActions`, `StratPool`;
  - constants and cache/integrity helpers.
- Lock/table structures:
  - read/write guards, shared/exclusive guards, `Table`.
- Engine action/type vocabulary:
  - UUIDs, identifiers, action enums, diffs, encryption info, integrity specs, stopped/locked pool info, udev events, unlock methods, and defaults.

Module declarations:
- Imports macros with `#[macro_use]`.
- Defines internal modules:
  - `engine`
  - `shared`
  - `sim_engine`
  - `strat_engine`
  - `structures`
  - `types`

Role in architecture:
- This file is the stable import surface for the rest of stratisd. Most callers use `crate::engine::{...}` re-exports rather than reaching into submodules directly.
