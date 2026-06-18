# sources/distributed-fs/openafs/src/external/heimdal/roken/errx.c

Purpose: implements the BSD `errx()` wrapper that exits with a formatted message but without errno text.

Important APIs/types/functions: `errx(int eval, const char *fmt, ...)`.

Control flow: starts varargs, delegates to `verrx(eval, fmt, ap)`, and ends varargs. `verrx()` handles output and exit.

State and persistence behavior: no local state; terminates process through `verrx()`.

Dependencies and integration points: roken err compatibility function used by `emalloc()`, `ecalloc()`, and `erealloc()`.

Risks: fatal semantics are unsuitable for library code that should return errors. Output behavior depends on `verrx()` and global program name state.

Test signals: formatted output without errno suffix, exit status, and varargs forwarding.
