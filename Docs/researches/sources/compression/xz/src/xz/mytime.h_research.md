# Research: sources/compression/xz/src/xz/mytime.h
## sources/compression/xz/src/xz/mytime.h

Purpose: Declares timing and flush-timeout functions.

Important APIs: Exports mutable `opt_flush_timeout`, optional SIGTSTP handler, start-time setter, elapsed-time getter, flush-time setter, and `poll()` timeout getter.

Control flow and integration: `args.c` sets `opt_flush_timeout`; `coder.c`, `message.c`, `file_io.c`, and `signals.c` consume the timing API.

State and persistence: State is private to `mytime.c` except for the exported timeout option.

Risks: The header documents "start time is also stored as the time of the first flush"; implementation currently sets operation start while first flush scheduling is updated when input is seen, so readers should verify behavior before relying on that wording.

Test signals: Build with and without `USE_SIGTSTP_HANDLER`; verify flush timeout integration with nonblocking reads.
