# File Research: sources/block-storage/thin-provisioning-tools/src/thin/damage_generator.rs

This devtool file creates controlled thin metadata damage.

Key elements:
- `SuperblockOverrides` can override `mapping_root`, `details_root`, and `metadata_snapshot`.
- `override_superblock()` reads the superblock, applies requested root/snapshot overrides, and writes it back.
- `DamageOp` supports:
  - `CreateMetadataLeaks { nr_blocks, expected_rc, actual_rc }`
  - `OverrideSuperblock(SuperblockOverrides)`
- `ThinDamageOpts` carries engine options, selected operation, and output path.
- `damage_metadata()` opens the output metadata writable, reads the superblock and metadata space map root, then dispatches to either metadata leak creation or superblock override.

Interactions:
- Uses devtools `create_metadata_leaks()`.
- Uses `EngineBuilder`, `SMRoot`, `unpack`, and thin superblock helpers.
- Compiled only when devtools are enabled via `thin/mod.rs`.

Risks and notes:
- This intentionally corrupts metadata and should only be used for test/dev workflows.
- It directly writes superblock root fields without validating the resulting metadata graph.
