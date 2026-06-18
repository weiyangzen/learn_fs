# sources/distributed-fs/coda/coda-src/util/util.c

## Purpose
Implements general Coda utility functions for hashing strings, timestamped logging, fd/stderr printing, hostname lookup/comparison, and simple process detachment.

## Important APIs, Types, And Functions
Globals define debug levels used by logging macros. Functions include `HashString`, `PrintTimeStamp`, `LogMsg`, `fdprint`, `eprint`, `hostname`, `UtilHostEq`, and `UtilDetach`.

## Control Flow
`HashString()` accumulates a reverse string hash modulo table size plus one. `PrintTimeStamp()` tracks date boundaries for up to five FILE pointers and emits date/time prefixes. `LogMsg()` filters by debug level, timestamps, formats, and flushes. `UtilHostEq()` resolves two names and compares their first addresses. `UtilDetach()` forks once and calls `setsid()` in the child.

## State And Persistence
Debug-level globals and static timestamp history are process-local. No durable state is written. `UtilDetach()` changes process/session state.

## Dependencies And Integration Points
Depends on C/POSIX runtime, resolver APIs, `util.h`, and `coda_string`. Many Coda components use `LogMsg` and the debug globals.

## Risks
`HashString()` returns 1..size and divides by `size`, so size zero is invalid and bucket users must expect one-based output. `PrintTimeStamp()` tracks only five files. `eprint()` reuses a variadic argument list by restarting it correctly, but duplicates output to stdout and stderr. `UtilHostEq()` uses legacy `gethostbyname()`.

## Test Signals
Hash empty and numeric strings, log around date boundaries and more than five files, compare host aliases/IPs, call detach in a supervised process, and verify debug-level filtering.
