# sources/distributed-fs/openafs/src/external/heimdal/roken/warnerr.c

## Purpose
Centralizes diagnostic formatting for roken's BSD err/warn compatibility functions.

## Important APIs, Types, And Functions
The exported function is `rk_warnerr(int doerrno, const char *fmt, va_list ap)`. It uses `getprogname`, `fprintf`, `vfprintf`, `strerror`, and a saved `errno`.

## Control Flow
The function snapshots `errno`, prints the program name if available, inserts separators when either a format or errno text will follow, formats the caller message if present, appends the saved errno text when requested, and ends with a newline.

## State And Persistence
It writes to `stderr` and reads program-name global state. It preserves the displayed errno by saving it before formatting.

## Dependencies And Integration Points
All `warn`, `warnx`, `err`, `errx`, `vwarn`, `verr`, and related wrappers funnel through this function.

## Risks And Test Signals
Formatting to `stderr` can itself change `errno`, but the message uses the saved value. Tests should cover all combinations of program name present/absent, format present/absent, errno enabled/disabled, and variadic formatting failures.
