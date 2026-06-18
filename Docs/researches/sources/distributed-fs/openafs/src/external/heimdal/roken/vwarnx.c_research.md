# sources/distributed-fs/openafs/src/external/heimdal/roken/vwarnx.c

## Purpose
Implements BSD-style `vwarnx`, printing a warning without appending `errno`.

## Important APIs, Types, And Functions
The exported function is `vwarnx(const char *fmt, va_list ap)`, delegating to `rk_warnerr(0, fmt, ap)`.

## Control Flow
The function directly calls the shared warning formatter and returns.

## State And Persistence
It writes to `stderr` but does not mutate process state.

## Dependencies And Integration Points
Used by `warnx.c` and `verrx.c`-style warning paths in the roken fallback err API.

## Risks And Test Signals
Tests should verify no errno suffix, correct prefix, `NULL` format behavior, and non-terminating behavior.
