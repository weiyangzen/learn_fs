# File Research: sources/block-storage/thin-provisioning-tools/src/commands/era_repair.rs

Command wrapper for rebuilding era binary metadata to another device/file.

CLI:
- Required `--input/-i`.
- Required `--output/-o`.
- `--quiet`.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists, is not tiny, and output exists/is large enough.
- Parses era engine options.
- Builds `EraRepairOptions` and delegates to `era::repair::repair`.
