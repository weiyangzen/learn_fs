# File Research: sources/block-storage/thin-provisioning-tools/src/thin/mod.rs

This file declares the thin module tree.

Always included modules:
- `block_time`, `check`, `delta`, `delta_visitor`, `device_detail`, `dump`, `human_readable_format`, `ir`, `ls`, `metadata`, `metadata_repair`, `metadata_size`, `migrate`, `repair`, `restore`, `rmap`, `runs`, `shrink`, `superblock`, `trim`, `xml`

Feature-gated devtools modules:
- `metadata_generator`
- `damage_generator`
- `stat`

Interactions:
- Central module index for the thin-provisioning implementation.
- Determines which dev-only files are compiled behind the `devtools` feature.
