# File Research: sources/block-storage/stratisd/src/engine/strat_engine/liminal/mod.rs

This is the liminal module declaration and public re-export surface.

Key responsibilities:
- Declares submodules:
  - `device_info`
  - `identify`
  - `liminal`
  - `setup`
- Re-exports:
  - `DeviceSet`
  - `find_all`
  - `LiminalDevices`

Important behavior:
- The `liminal` submodule uses `#[allow(clippy::module_inception)]` because the module and file share the same name.

Tests:
- No local tests in this file.
