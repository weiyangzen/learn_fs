# File Research: sources/block-storage/thin-provisioning-tools/src/commands/era_check.rs

Command wrapper for validating era metadata.

CLI:
- `--ignore-non-fatal-errors`.
- `--quiet`.
- `--super-block-only`.
- Required positional input.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists, is not tiny, and does not look like XML.
- Parses era engine options.
- Builds `EraCheckOptions` and delegates to `era::check::check`.
