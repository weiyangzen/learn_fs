# Research: sources/compression/xz/src/xz/main.h
## sources/compression/xz/src/xz/main.h

Purpose: Declares process exit-status values and mutators.

Important APIs and types: `enum exit_status_type` matches gzip/bzip2-compatible codes: success 0, error 1, warning 2. `set_exit_status()` records warning/error status, and `set_exit_no_warn()` allows warnings to exit as success.

Control flow and integration: `message_warning()` and `message_error()` update status through this API. `args.c` calls `set_exit_no_warn()` for `--no-warn`. `main.c` reads the final status at shutdown.

State and persistence: State is private to `main.c` and persists for the whole process.

Risks: Only warning and error are valid inputs to `set_exit_status()`; assertions catch misuse in debug builds. Windows signal handling requires synchronized access in `main.c`.

Test signals: Validate that warnings do not override errors, `--no-warn` maps warning-only runs to success, and fatal errors exit immediately.
