# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_writeback.rs

Command wrapper for cache writeback.

CLI:
- Required `--metadata-device`, `--origin-device`, and `--fast-device`.
- Optional sector offsets for origin and fast devices.
- Optional `--buffer-size-meg`.
- Optional `--retry-count`, default 0.
- Flags: `--quiet`, `--no-metadata-update`, `--list-failed-blocks`.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates metadata, origin, and fast device paths.
- Parses cache engine options.
- Runs a full `cache_check` first; on failure reports that metadata needs `cache_check`/possibly `cache_repair` and returns `DATAERR`.
- Converts buffer megabytes to sectors by multiplying by 2048.
- Delegates to `cache::writeback::writeback`.
