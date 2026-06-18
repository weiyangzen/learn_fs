# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_metadata_size.rs

Command wrapper for estimating cache metadata size.

CLI:
- Requires either `--nr-blocks NUM` or both `--device-size SIZE` and `--block-size SIZE`.
- `--max-hint-width BYTES`, default 4.
- `--unit`, default sector.
- `--numeric-only[=short|long]`.
- Adds version args.

Runtime behavior:
- Converts device size/block size into cache block count via `div_up`.
- Validates cache block size with `check_cache_block_size`.
- Rejects device size smaller than block size.
- Calls `cache::metadata_size::metadata_size`.
- Formats output as full unit text, short suffix, long unit suffix, or raw numeric value.
