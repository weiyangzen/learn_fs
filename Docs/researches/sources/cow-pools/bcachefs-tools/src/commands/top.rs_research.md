# File Research: sources/cow-pools/bcachefs-tools/src/commands/top.rs

Implements `bcachefs top`, a live performance counter viewer with one-shot/non-interactive output, an interactive TUI, per-device I/O rates, and tracepoint drill-down for selected counters.

Major components:
- `read_counters` builds a flexible `bch_ioctl_query_counters` buffer and issues `BCH_IOCTL_QUERY_COUNTERS`.
- `read_device_io` parses `dev-*/io_done` JSON into read/write byte totals by device and data type.
- Formatting routes counters through `fmt_counter`, converting sector counters to bytes when appropriate.
- `TopState` stores baseline, mount-time, and previous samples for rate/total/mount columns.
- `TraceView` creates a per-process tracefs instance, filters the selected `bcachefs:<counter>` tracepoint to the current filesystem name, tails `trace_pipe`, and supports pause, scrollback, and stacktrace triggers.

Interactive behavior:
- Base page lists active persistent counters whose value changed since mount.
- Devices page lists per-device read/write totals and rates.
- Enter on a counter starts live trace view if tracefs is available and permissions allow it.
- Sampling is deliberately decoupled from keypresses so scrolling does not reset rate calculations.

Non-interactive behavior:
- Takes an initial baseline sample, sleeps `delay`, then prints `count` frames.
- Defaults to one frame for `--once` or non-terminal stdout.

Notable implementation details:
- Trace instance path is `instances/bcachefs-top-<pid>`.
- `Drop` disables the trace event and removes the tracefs instance.
- Non-blocking trace reads are bounded to avoid a hot tracepoint hanging the UI.
- Counter display uses `COUNTERS` metadata from bindgen, including stable IDs and sector flags.

Potential concerns:
- `read_counters` trusts kernel-returned `actual_nr` for reading the same allocation; if a buggy kernel returns more than requested, the vector read could go beyond the initialized counter region.
- Trace setup assumes generated tracepoint names match persistent counter names exactly.
