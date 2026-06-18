# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_metadata_size.rs

Command wrapper for estimating thin metadata size.

CLI:
- Required `--block-size/-b SIZE`.
- Required `--pool-size/-s SIZE`.
- Required `--max-thins/-m NUM`.
- `--unit/-u`, default sector.
- `--numeric-only/-n[=short|long]`.
- Adds version args.

Runtime behavior:
- Parses storage-size units to bytes.
- Validates data block size with `check_data_block_size`.
- Rejects pool size smaller than block size.
- Computes `nr_blocks = pool_size / block_size`.
- Calls `thin::metadata_size::metadata_size`.
- Formats output as full unit, short suffix, long suffix, or numeric-only.
