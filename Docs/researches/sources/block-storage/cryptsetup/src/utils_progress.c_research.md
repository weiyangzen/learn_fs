# File Research: sources/block-storage/cryptsetup/src/utils_progress.c

## Purpose
Progress reporting utility for wipe and long-running data operations. Supports human terminal progress and JSON progress output.

## Time And Unit Helpers
- `time_diff()` computes microsecond deltas between `timeval` values.
- `bytes_to_units()` converts byte counts into MiB/GiB/TiB/PiB/EiB display units.
- `time_to_human_string()` formats ETA/time as minutes, hours, or days depending on duration.

## Human Progress
- `tools_time_progress()` throttles updates according to `frequency` or defaults to frequent single-line terminal updates.
- `log_progress()` prints percentage, ETA, written amount, and speed.
- `log_progress_final()` prints total time, written amount, and average speed.
- `tools_clear_line()` clears the current terminal line for in-place progress updates.

## JSON Progress
- `tools_time_progress_json()` computes speed/ETA and calls `log_progress_json()`.
- JSON fields include device, bytes written, device size, speed bytes/sec, ETA milliseconds, and elapsed milliseconds.

## Public Callback
`tools_progress()` is the callback passed to libcryptsetup wipe operations:
- Emits JSON if requested.
- Emits human progress only outside batch mode.
- Checks interruption with `check_signal()`.
- Clears the line and prints the configured interrupt message when interrupted.

## Device Name Helper
`tools_get_device_name()` returns a loop backing file path if the device is loop-backed; otherwise it returns the original device string and hands ownership of any allocated backing path to the caller.

## Notes
Progress state is carried in `struct tools_progress_params`, defined in `cryptsetup.h`.
