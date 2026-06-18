# sources/distributed-fs/openafs/src/external/heimdal/roken/verrx.c

## Purpose
Implements BSD-style `verrx`, the no-errno variant of `verr`.

## Important APIs, Types, And Functions
The exported function is `verrx(int eval, const char *fmt, va_list ap)`. It delegates to `rk_warnerr` with errno output disabled and then exits.

## Control Flow
The function formats any caller message to `stderr` and immediately terminates with `exit(eval)`.

## State And Persistence
It writes diagnostics and exits the process. No heap or module state is used.

## Dependencies And Integration Points
Used by `errx.c` and callers expecting BSD `errx`/`verrx` behavior in roken portability builds.

## Risks And Test Signals
Subprocess tests should verify no errno suffix is printed, exit code is preserved, program-name prefixing works, and `NULL` messages produce sane output.
