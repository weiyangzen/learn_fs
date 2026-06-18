# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_generate_damage.rs

Development command wrapper for deliberate cache metadata damage generation.

CLI:
- Required command group currently only `--create-metadata-leaks`.
- Leak options: `--expected REFCONT`, `--actual REFCOUNT`, `--nr-blocks NUM`.
- Required output device `--output/-o`.
- Adds version and engine args.

Runtime behavior:
- Parses cache engine options.
- Converts selected command into `DamageOp::CreateMetadataLeaks`.
- Calls `cache::damage_generator::damage_metadata`.
- Uses `process::exit(1)` for impossible/unknown command match fallback.
