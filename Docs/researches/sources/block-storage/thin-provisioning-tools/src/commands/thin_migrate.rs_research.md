# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_migrate.rs

Command wrapper for migrating a thin volume from one pool/destination to another.

CLI:
- `--source-dev DEVICE`.
- Hidden `--delta-id THIN_ID`.
- Destination: `--dest-dev DEVICE` or `--dest-file FILE`.
- Optional `--buffer-size-meg`.
- Hidden `--zero-dest`.
- `--quiet`.
- Adds verbose, version, and engine args, though this wrapper does not pass parsed engine options to migrate.

Runtime behavior:
- Manually requires source and destination.
- Converts buffer megabytes to sectors by multiplying by 2048.
- Builds `thin::migrate::ThinMigrateOptions` and calls `migrate::migrate`.
