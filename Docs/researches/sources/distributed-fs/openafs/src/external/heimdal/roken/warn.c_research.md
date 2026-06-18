# sources/distributed-fs/openafs/src/external/heimdal/roken/warn.c

## Purpose
Implements BSD-style variadic `warn`, a non-terminating warning that includes `errno`.

## Important APIs, Types, And Functions
The exported function is `warn(const char *fmt, ...)`. It builds a `va_list` and calls `vwarn`.

## Control Flow
The wrapper starts variadic argument processing, delegates to `vwarn`, then ends argument processing and returns.

## State And Persistence
Writes a diagnostic to `stderr`; no persistent state is modified.

## Dependencies And Integration Points
Part of the roken err/warn compatibility family and relies on `vwarn` plus `rk_warnerr`.

## Risks And Test Signals
Tests should verify formatting, errno inclusion, no exit, and compile-time consistency with `err.h` prototypes.
