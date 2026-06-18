# sources/cloud-native/nydus/src/logger.rs

## Purpose
`logger.rs` centralizes logging setup and formatting for Nydus binaries using `flexi_logger`, colored console output, optional file output, optional rotation, runtime log-level control, and panic logging.

## Important APIs, Types, And Functions
`log_level_to_verbosity` maps `LevelFilter` to a numeric verbosity. `get_file_name` shortens source file paths around `/src/`. `opt_format` formats file logs and non-colored output; info logs omit file/line, while other levels include them. `colored_opt_format` applies terminal colors. `setup_logging` configures file or stderr logging, optional rotation by size, max log level, and `log_panics` backtrace hook.

## Control Flow
Callers pass optional log path, log level, and rotation size. For file logging, the code builds a `FileSpec` from the provided path without canonicalization, preserves explicit suffixes to avoid flexi_logger adding `.log`, resolves relative parent directories against current working directory, starts a trace-level flexi logger with `opt_format`, and optionally enables timestamped compressed rotation. Without a file path, it starts colored console logging. In both cases it sets the global max log level and installs a panic hook.

## State And Persistence
The logger installs a global logging backend and panic hook. With file logging, it appends to the target file and may create rotated compressed logs. With console logging, output is emitted to stderr/stdout according to flexi_logger behavior. Log level can later be changed by API glue through `log::set_max_level`.

## Dependencies And Integration Points
It depends on `flexi_logger`, `log`, `log_panics`, current working directory resolution, and Nydus error macros from `nydus_api`. It is re-exported by `lib.rs` and used by `nydus-image` and `nydusd`.

## Risks
Rust logging can only be initialized once per process; tests avoid calling `setup_logging` directly. Path parsing rejects non-UTF-8 stems/extensions. Rotation size multiplication can overflow for extremely large MB values. Formatting intentionally hides file/line for info logs, which can reduce diagnosability. `get_file_name` uses string searches and can produce surprising prefixes for unusual paths.

## Test Signals
Unit tests cover verbosity mapping, file-name shortening, formatting behavior for info/debug/warn/error and missing file info, and path component extraction for rotation setup. They do not initialize the global logger, avoiding one-time logger conflicts.
