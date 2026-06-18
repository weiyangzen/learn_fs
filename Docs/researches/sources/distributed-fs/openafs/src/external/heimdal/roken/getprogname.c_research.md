# sources/distributed-fs/openafs/src/external/heimdal/roken/getprogname.c

Purpose: fallback support for retrieving the process program name.

Important APIs/types/functions: optionally defines global `const char *__progname`; implements `getprogname(void)` when unavailable.

Control flow: returns the `__progname` pointer.

State and persistence behavior: uses process-global `__progname`, which must be set elsewhere by startup or roken support code.

Dependencies and integration points: used by err/warn style diagnostics and tools expecting BSD `getprogname()`.

Risks: may return NULL or stale data if `__progname` is not initialized. Global state is not owned by this file.

Test signals: program-name initialization path, fallback build without native `getprogname`, and diagnostic users that consume the returned pointer.
