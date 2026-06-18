# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_restore.rs

Command wrapper for converting cache XML metadata to binary metadata.

CLI:
- Required `--input/-i FILE`.
- Required `--output/-o FILE`.
- `--metadata-version` restricted to 1 or 2, default 2.
- `--omit-clean-shutdown`.
- `--quiet`.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists and output exists/is large enough.
- Parses cache engine options.
- Builds `CacheRestoreOptions` and calls `cache::restore::restore`.
