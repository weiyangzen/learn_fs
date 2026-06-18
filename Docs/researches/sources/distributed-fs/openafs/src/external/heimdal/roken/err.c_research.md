# sources/distributed-fs/openafs/src/external/heimdal/roken/err.c

Purpose: implements the BSD `err()` wrapper where the platform lacks one or roken supplies its own.

Important APIs/types/functions: `err(int eval, const char *fmt, ...)`.

Control flow: starts a varargs list, delegates to `verr(eval, fmt, ap)`, and ends the list. `verr()` is expected to print the message, include errno text, and exit with `eval`.

State and persistence behavior: no local persistent state; process exits through `verr()`.

Dependencies and integration points: part of roken err/warn portability family, used by fatal allocation helpers and command-line tools.

Risks: behavior depends on the linked `verr()` implementation. Because it exits, it must not be used in recoverable library flows.

Test signals: formatted output includes errno text, exit status is preserved, and varargs forwarding works with null and non-null formats.
