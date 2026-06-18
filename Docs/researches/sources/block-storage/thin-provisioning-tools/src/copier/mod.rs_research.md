# File Research: sources/block-storage/thin-provisioning-tools/src/copier/mod.rs

Copier module registry and public re-export surface.

Modules:
- `base`, `batcher`, `report`, `rescue_copier`, `sync_copier`, `wrapper`.
- `test_utils` only under test or `devtools`.

Re-exports:
- Base copier types and traits.
- Copier progress/report helpers.
- `RescueCopier`.
- `SyncCopier`.

This file defines the common copy subsystem surface used by higher-level cache and thin operations.
