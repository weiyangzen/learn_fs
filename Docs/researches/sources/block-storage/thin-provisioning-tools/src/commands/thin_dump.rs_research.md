# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_dump.rs

Command wrapper for dumping thin metadata.

CLI:
- Flags: `--quiet`, `--repair/-r`, `--skip-mappings`.
- Options: `--data-block-size`, repeated `--dev-id`, `--format xml|human_readable`, `--metadata-snap[=BLOCKNR]`, `--nr-data-blocks`, `--output/-o`, `--transaction-id`.
- Required positional input.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Parses thin engine options.
- Collects selected device IDs if provided.
- Builds `ThinDumpOptions`, including repair overrides and output format.
- Delegates to `thin::dump::dump`.
