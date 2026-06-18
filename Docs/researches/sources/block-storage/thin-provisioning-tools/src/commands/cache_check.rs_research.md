# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_check.rs

Clap command wrapper for `cache_check`.

CLI:
- Flags: `--auto-repair`, `--clear-needs-check-flag`, `--ignore-non-fatal-errors`, `--quiet`, `--super-block-only`, `--skip-hints`, `--skip-discards`, `--skip-mappings`.
- Positional input metadata device/file.
- Adds version, verbose, and hidden engine-selection args.

Runtime behavior:
- Builds report and parses log level.
- Validates input exists, is a file/block device, is at least one block, and does not look like XML.
- Parses cache `EngineOptions`.
- Constructs `CacheCheckOptions` and delegates to `cache::check::check`.
- Converts errors through shared `to_exit_code`.
