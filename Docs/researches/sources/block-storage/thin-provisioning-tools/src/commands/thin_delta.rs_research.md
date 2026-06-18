# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_delta.rs

Command wrapper for comparing mappings between two thin devices/snapshots.

CLI:
- `--metadata-snap/-m`.
- `--verbose`.
- First endpoint: `--thin1`/`--snap1` or `--root1`.
- Second endpoint: `--thin2`/`--snap2` or `--root2`.
- Required positional input.
- Adds version and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Manually enforces that both endpoints are provided because of a noted clap group limitation.
- Builds `Snap::DeviceId` or `Snap::RootBlock` for each side.
- Parses thin engine options and calls `thin::delta::delta`.
