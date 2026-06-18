# File Research: sources/cow-pools/bcachefs-tools/src/commands/scrub.rs

## Purpose
Implements `bcachefs scrub`, which starts checksum/data scrub operations through a filesystem ioctl and displays per-device progress, corrected errors, and uncorrected errors.

## Main Interfaces
- CLI struct: `Cli`
- Command export: `CMD = typed_cmd!("scrub", ...)`
- Key types/functions:
  - `ScrubDev`
  - `start_scrub`
  - `read_data_event`
  - `sigint_handler`
  - `scrub`

## Behavior
- Supports `--metadata` to scrub only btree metadata; otherwise scrubs all data types.
- Opens a mounted filesystem or device through `BcachefsHandle`.
- Reads sysfs device list and determines whether the handle targets a specific device or the whole filesystem.
- Starts one scrub operation per target device via `BCH_IOCTL_DATA_OP_scrub`.
- Reads fixed-size progress events from returned fds.
- Prints a live table with checked, corrected, uncorrected, total, percent, and current rate/status.
- Rewrites progress lines in place using ANSI cursor movement.
- Handles SIGINT by setting an atomic flag and exits with bit `1`.
- Sets exit code bit `2` if any errors were corrected and bit `4` if any uncorrected errors were found.

## Dependencies and Coupling
- Uses `bch_ioctl_data` and raw ioctl number `BCH_IOCTL_DATA_NR = 10`.
- Uses manual raw parsing for blocklisted `bch_ioctl_data_event` layout.
- Uses sysfs helpers `fs_get_devices` and `sysfs_path_from_fd`.
- Uses human-format helpers for bytes/sectors.

## Important Implementation Notes
- `DATA_EVENT_SIZE` is fixed at 128 bytes, matching the packed C event layout documented in the file.
- Progress rate is computed from sector delta and elapsed nanoseconds.
- Non-progress event types keep the device active and print zero rate.
- Closing/removing `progress_fd` marks a device complete or offline depending on returned status.

## Risks and Edge Cases
- Manual event parsing is ABI-sensitive.
- `libc::signal` installs a simple handler; only atomic store is performed, which is appropriate.
- Terminal line rewriting assumes a terminal-like output even when stdout is redirected.
