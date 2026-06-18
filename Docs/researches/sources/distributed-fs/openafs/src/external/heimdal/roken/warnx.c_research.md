# sources/distributed-fs/openafs/src/external/heimdal/roken/warnx.c

## Purpose
Implements BSD-style variadic `warnx`, a non-terminating warning that omits `errno`.

## Important APIs, Types, And Functions
The exported function is `warnx(const char *fmt, ...)`. It wraps `vwarnx`.

## Control Flow
Starts a `va_list`, calls `vwarnx`, ends the `va_list`, and returns.

## State And Persistence
The function writes to `stderr` through shared warning helpers and does not alter persistent state.

## Dependencies And Integration Points
Part of roken's err/warn compatibility API and depends on `warnerr.c` for actual formatting.

## Risks And Test Signals
Tests should cover formatted output, no errno suffix, no process exit, and declaration compatibility in fallback builds.
