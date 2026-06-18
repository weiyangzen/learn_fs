# sources/distributed-fs/openafs/src/external/heimdal/roken/vwarn.c

## Purpose
Implements BSD-style `vwarn`, printing a warning that includes the current `errno` text.

## Important APIs, Types, And Functions
The exported function is `vwarn(const char *fmt, va_list ap)`, delegating to `rk_warnerr(1, fmt, ap)`.

## Control Flow
No branching is performed locally; all formatting and errno handling happens in `rk_warnerr`.

## State And Persistence
Writes to `stderr` and reads `errno` through `rk_warnerr`.

## Dependencies And Integration Points
Used by `warn.c` and roken's fallback err/warn family. It depends on program-name state for prefixes.

## Risks And Test Signals
Tests should verify errno suffix inclusion, format handling, program-name prefixing, and that the function does not exit.
