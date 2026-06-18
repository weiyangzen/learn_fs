# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_check.rs

Command wrapper for validating thin-provisioning metadata.

CLI:
- Flags: `--auto-repair`, `--clear-needs-check-flag`, `--ignore-non-fatal-errors`, `--metadata-snap/-m`, `--quiet`, `--super-block-only`, `--skip-mappings`.
- Options: `--override-mapping-root`, `--override-details-root`.
- Required positional input.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists, is not tiny, and is not XML.
- Parses thin engine options including metadata snapshot.
- Builds `ThinCheckOptions` and calls `thin::check::check`.
- Uses clap conflicts to prevent unsafe combinations such as auto-repair with metadata snapshot or override roots.
