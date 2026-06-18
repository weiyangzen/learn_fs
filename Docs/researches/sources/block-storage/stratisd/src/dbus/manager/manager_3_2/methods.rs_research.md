# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_2/methods.rs

Manager r2 pool start/stop/refresh methods.

Key behavior:
- `start_pool_method()`:
  - Parses pool UUID.
  - Converts optional `UnlockMethod` to `TokenUnlockMethod`.
  - Calls `engine.start_pool`.
  - Registers filesystems, then pool/blockdevs, for the started pool.
  - Emits locked-pools signal if encrypted and stopped-pools signal after start.
  - Returns pool path, blockdev paths, and filesystem paths.
- `stop_pool_method()`:
  - Resolves pool UUID from object path.
  - Captures current blockdev/filesystem UUIDs.
  - Calls `engine.stop_pool`.
  - Unregisters filesystem/blockdev paths that disappeared from engine state, even on partial stop/error paths.
  - On stopped/partial, unregisters pool object and emits stopped-pools signal.
  - Emits locked-pools signal when stopped encrypted pool still has unlock info.
  - Distinguishes identity, stopped, partial, and error.
- `refresh_state_method()` calls `engine.refresh_state()`.

Filesystem/block-storage relevance:
- Handles dynamic D-Bus object lifecycle when pools are stopped/started.
- Carefully reconciles partial teardown state with registered object paths.
