# File Research: sources/block-storage/thin-provisioning-tools/src/cache/mod.rs

Cache module declaration file.

Always exported:
- `check`, `dump`, `hint`, `ir`, `mapping`, `metadata_size`, `repair`, `restore`, `superblock`, `writeback`, `xml`.

Feature-gated under `devtools`:
- `metadata_generator`.
- `damage_generator`.

This file defines module availability boundaries for production versus development commands.
