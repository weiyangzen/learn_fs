# sources/distributed-fs/openafs/src/external/heimdal/roken/verr.c

## Purpose
Implements BSD-style `verr` for platforms lacking `err.h` support.

## Important APIs, Types, And Functions
The exported function is `verr(int eval, const char *fmt, va_list ap)`. It delegates formatting to `rk_warnerr` with errno output enabled, then exits with `eval`.

## Control Flow
There is no recovery path: print program name, message, and saved errno text through `rk_warnerr`, then call `exit(eval)`.

## State And Persistence
It reads `errno` indirectly in `rk_warnerr`, writes to `stderr`, and terminates the process.

## Dependencies And Integration Points
Works with `err.c`, `warnerr.c`, `getprogname`, and roken's fallback `err.h` surface.

## Risks And Test Signals
This function is process-terminating, so unit tests need subprocess isolation. Signals include correct exit status, stderr prefix, errno preservation, `NULL` format handling, and compatibility with native `verr`.
