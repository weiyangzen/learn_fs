# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_repair.rs

Command wrapper for repairing thin metadata into a different device/file.

CLI:
- Required `--input/-i`.
- Required `--output/-o`.
- Optional repair overrides: `--data-block-size`, `--nr-data-blocks`, `--transaction-id`.
- `--quiet`.
- Hidden dummy positional for `lvconvert` compatibility.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists, is not tiny, and output exists/is large enough.
- Parses thin engine options.
- Builds `ThinRepairOptions` with `SuperblockOverrides`.
- Delegates to `thin::repair::repair`.
