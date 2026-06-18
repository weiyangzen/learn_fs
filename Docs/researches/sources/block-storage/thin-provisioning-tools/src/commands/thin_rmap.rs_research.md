# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_rmap.rs

Command wrapper for reverse-mapping data-device block ranges to thin mappings.

CLI:
- Required repeated `--region BLOCK_RANGE`, parsed as `start..end`.
- Required positional input.
- Adds version and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Converts `RangeU64` helper values into `std::ops::Range<u64>`.
- Parses thin engine options.
- Builds `ThinRmapOptions` and calls `thin::rmap::rmap`.

Notable detail: comments note clap cannot place the positional after multiple `--region` arguments in the desired style.
