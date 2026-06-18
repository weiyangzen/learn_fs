# File Research: sources/cow-pools/bcachefs-tools/src/logging.rs

Configures process-wide logging through `env_logger`.

Behavior:
- Maps verbosity 0/1/2/3+ to warn/info/debug/trace.
- Honors `BCACHEFS_LOG` environment filtering through `parse_env`.
- Controls color via `WriteStyle::Always` or `Never`.
- Formats records as `[LEVEL file:line] message`.
- Uses `owo_colors` to color log level by severity.

Potential concerns:
- Calls `.init()`, which panics if a logger has already been initialized elsewhere in the process.
