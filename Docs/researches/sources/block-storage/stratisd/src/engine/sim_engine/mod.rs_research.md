# File Research: sources/block-storage/stratisd/src/engine/sim_engine/mod.rs

This module file defines the simulator engine submodule layout.

Public exports:
- Re-exports `SimEngine`.

Internal modules:
- `blockdev`
- `engine`
- `filesystem`
- `keys`
- `pool`
- `shared`

Role in architecture:
- Keeps the simulator implementation private except for the `SimEngine` entry point exposed by `crate::engine`.
