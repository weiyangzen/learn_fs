# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_dump.rs

Clap command wrapper for `cache_dump`.

CLI:
- `--repair` / `-r` to repair while dumping.
- `--output` / `-o FILE` for XML output, otherwise stdout.
- Positional input metadata device/file.
- Adds version and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Parses cache engine options.
- Builds `CacheDumpOptions` and calls `cache::dump::dump`.
- Uses a simple report only for validation/errors.
