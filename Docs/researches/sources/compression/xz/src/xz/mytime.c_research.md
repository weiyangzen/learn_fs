# Research: sources/compression/xz/src/xz/mytime.c
## sources/compression/xz/src/xz/mytime.c

Purpose: Provides portable millisecond timing for progress reporting, SIGTSTP pause accounting, and `--flush-timeout` scheduling.

Important APIs and functions: Exports `opt_flush_timeout`, `mytime_set_start_time()`, `mytime_get_elapsed()`, `mytime_set_flush_time()`, `mytime_get_flush_timeout()`, and optional `mytime_sigtstp_handler()`. Internal `mytime_now()` chooses `GetTickCount64()`, `clock_gettime()`, or `gettimeofday()` depending on platform and threading configuration.

Control flow: `coder_run()` calls `mytime_set_start_time()` just before processing a file. `message.c` calls `mytime_get_elapsed()` for progress. `io_read()` calls `mytime_set_flush_time()` when first input arrives after a flush and uses `mytime_get_flush_timeout()` as the `poll()` timeout for nonblocking input. Optional SIGTSTP handling shifts `start_time` forward by stopped duration.

State and persistence: Static `start_time` and `next_flush` live for the process. `opt_flush_timeout` is set by `args.c`. There is no external persistence.

Dependencies and integration points: Uses `signals_block()`/`signals_unblock()` when SIGTSTP handler support makes `start_time` asynchronously mutable. Reads `opt_mode` to make flush timeouts compression-only.

Risks: `gettimeofday()` fallback is not monotonic, so wall-clock changes can affect progress/flush timing. SIGTSTP handling uses `SIGSTOP` and has documented POSIX caveats. Very large timeout values are capped to `INT_MAX` for `poll()`.

Test signals: Cover timing backends by platform, flush timeout disabled/enabled, immediate timeout, large timeout cap, compression-only behavior, progress elapsed after start, and SIGTSTP pause adjustment where supported.
