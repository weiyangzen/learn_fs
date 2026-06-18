# File Research: sources/block-storage/thin-provisioning-tools/src/commands/era_dump.rs

Command wrapper for dumping era metadata to XML.

CLI:
- `--logical` to fold unprocessed write sets into final era array.
- `--repair/-r`.
- Optional `--output/-o`.
- Required positional input.
- Adds version and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Parses era engine options.
- Builds `EraDumpOptions` and calls `era::dump::dump`.
