# File Research: sources/block-storage/thin-provisioning-tools/src/commands/era_restore.rs

Command wrapper for converting era XML metadata to binary.

CLI:
- Required `--input/-i`.
- Required `--output/-o`.
- `--quiet`.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input and output paths.
- Parses era engine options.
- Builds `EraRestoreOptions` and delegates to `era::restore::restore`.
