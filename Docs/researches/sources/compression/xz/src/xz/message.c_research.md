# Research: sources/compression/xz/src/xz/message.c
## sources/compression/xz/src/xz/message.c

Purpose: Handles diagnostics, verbosity, progress display, help/version/filter-help output, liblzma return-code messages, and memory/filter reporting.

Important APIs and functions: Public API includes `message_init()`, verbosity setters/getter, `message_set_files()`, `message_filename()`, progress start/update/end, `message()`, `message_warning()`, `message_error()`, `message_fatal()`, `message_bug()`, `message_signal_handler()`, `message_strm()`, `message_mem_needed()`, `message_filters_show()`, `message_try_help()`, `message_version()`, `message_help()`, and `message_filters_help()`. Progress helpers compute percentage, size/ratio, speed, elapsed time, ETA, and positions via `lzma_get_progress()`.

Control flow: `main.c` initializes messages before parsing and processing. Each file calls `message_filename()`, then `coder_run()` starts progress with the active `lzma_stream`, periodically calls `message_progress_update()`, and ends progress. Diagnostics call `vmessage()`, which blocks signals and flushes any active progress line before printing. Help, version, and filter-help functions print to stdout and exit.

State and persistence: Static state tracks current file index/total, verbosity, current filename, whether filenames/progress have printed, terminal-based automatic progress mode, progress stream pointer, passthrough flag, expected input size, signal-triggered update flag or polling timestamp. No persistent storage is written.

Dependencies and integration points: Uses `mytime.c` for elapsed timing, `hardware.c` for memlimit display, `main.c` for exit status, `signals.c` for output atomicity, liblzma progress and filter string APIs, `tuklib` wrapping/multibyte/nonprint helpers, `opt_mode`, `opt_robot`, and `stdin_filename`.

Risks: Progress state assumes one active coder at a time and a valid `lzma_stream` until `message_progress_end()`. `SIGALRM` paths must reset update flags before scheduling the next alarm. Help text wrapping is translation-sensitive. Robot version output is machine-readable and should not be casually changed. `message_mem_needed()` reports the generic hard mode limit, so callers must choose context carefully.

Test signals: Exercise verbosity levels, quiet twice, progress on TTY and non-TTY, SIGALRM/SIGUSR1/SIGINFO progress trigger, passthrough progress, diagnostics during active progress, all `lzma_ret` mappings, memlimit formatting below/above MiB and disabled, help/long-help/filter-help wrapping, robot version output, and translation-width fallbacks.
