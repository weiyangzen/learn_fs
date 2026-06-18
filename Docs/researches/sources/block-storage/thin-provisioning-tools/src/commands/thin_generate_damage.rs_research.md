# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_generate_damage.rs

Development command wrapper for damaging thin metadata.

CLI command group:
- `--create-metadata-leaks` with `--expected`, `--actual`, `--nr-blocks`.
- `--override` with at least one superblock override.

Override options:
- `--mapping-root`.
- `--details-root`.
- `--metadata-snap`.
- Required `--output/-o`.
- Adds version and engine args.

Runtime behavior:
- Parses thin engine options.
- Builds `DamageOp::CreateMetadataLeaks` or `DamageOp::OverrideSuperblock`.
- Delegates to `thin::damage_generator::damage_metadata`.
