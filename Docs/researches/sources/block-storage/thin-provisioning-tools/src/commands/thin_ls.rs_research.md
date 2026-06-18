# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_ls.rs

Command wrapper for listing thin volumes in a pool.

CLI:
- `--no-headers`.
- `--metadata-snap/-m`.
- `--format/-o` comma-delimited output fields parsed as `OutputField`.
- Required positional input.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Defaults fields to device ID, mapped blocks, creation time, and snapshotted time.
- Parses thin engine options.
- Builds `ThinLsOptions` and delegates to `thin::ls::ls`.
