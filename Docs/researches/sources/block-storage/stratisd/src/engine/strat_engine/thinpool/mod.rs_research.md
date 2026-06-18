# File Research: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/mod.rs

## Purpose
Defines the thinpool module structure and public re-exports.

## Main Components
Declares modules:
- `dm_structs`
- `filesystem`
- `mdv`
- `thinids`
- `thinpool`

Publicly re-exports:
- `StratFilesystem`
- `ThinPool`
- `ThinPoolSizeParams`
- `DATA_BLOCK_SIZE`

Conditionally re-exports `ThinPoolStatusDigest` for tests.

## Research Notes
This is the module boundary for thinpool internals. External strat-engine code imports the main thinpool and filesystem types through this file rather than directly from submodules.
