# File Research: sources/cow-pools/bcachefs-tools/src/commands/format.rs

This file implements `bcachefs format` / `mkfs` argument parsing and high-level format orchestration.

Design:
- Uses manual parsing instead of clap because device-specific options are positional/sticky and dynamic C options are parsed through generated option tables.

Parsing supports:
- Filesystem options from the C option table.
- Device options that apply to subsequent device paths.
- `--replicas`
- `--encrypted`
- `--passphrase_file`
- `--no_passphrase`
- `--fs_label` / `-L`
- `--uuid` / `-U`
- `--superblock_size`
- `--version`
- `--source`
- `--no_initialize`
- `--force`, `--quiet`, `--verbose`, and help.

High-level flow:
- Parses arguments into `FormatConfig`.
- Prompts or reads passphrase when encryption requires it.
- Loads the bcachefs module opportunistically to detect kernel metadata version.
- Chooses requested/current/kernel-compatible metadata version.
- Disables initialization for version mismatch or `BCACHEFS_KERNEL_ONLY`.
- Builds C `format_opts` and deferred string options.
- Builds `format_util::DevOpts` for each device.
- Checks multipath components and opens devices.
- Calls `format_util::format()`.
- Prints superblock unless quiet.
- Optionally opens the new filesystem and initializes it, including copying from `--source`.

Validation:
- Rejects missing devices.
- Rejects dangling device-specific options.
- Rejects incompatible `--source`/`--no_initialize`.
- Requires `--encrypted` for passphrase file usage.
