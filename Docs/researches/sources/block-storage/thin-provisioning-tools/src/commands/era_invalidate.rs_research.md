# File Research: sources/block-storage/thin-provisioning-tools/src/commands/era_invalidate.rs

Command wrapper for listing blocks changed since a given era.

CLI:
- `--metadata-snapshot`.
- Required `--written-since ERA`.
- Optional `--output/-o`.
- Required positional input.
- Adds version and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Parses era engine options, including metadata snapshot flag.
- Builds `EraInvalidateOptions` with threshold from `--written-since`.
- Calls `era::invalidate::invalidate`.
