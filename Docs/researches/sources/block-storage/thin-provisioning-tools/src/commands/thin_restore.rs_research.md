# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_restore.rs

Command wrapper for converting thin XML metadata to binary metadata.

CLI:
- Required `--input/-i`.
- Required `--output/-o`.
- Optional overrides: `--data-block-size`, `--nr-data-blocks`, `--transaction-id`.
- `--quiet`.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input and output.
- Parses thin engine options.
- Builds `ThinRestoreOptions` with superblock overrides.
- Delegates to `thin::restore::restore`.
