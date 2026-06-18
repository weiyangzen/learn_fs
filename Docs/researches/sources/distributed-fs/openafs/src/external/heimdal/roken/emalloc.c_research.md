# sources/distributed-fs/openafs/src/external/heimdal/roken/emalloc.c

Purpose: provides a `malloc()` wrapper that exits on nonzero allocation failure.

Important APIs/types/functions: `emalloc(size_t sz)`.

Control flow: calls `malloc(sz)`, calls `errx(1, ...)` if NULL and `sz != 0`, and otherwise returns the pointer.

State and persistence behavior: returns caller-owned heap memory or terminates the process.

Dependencies and integration points: roken helper for programs that use fatal allocation semantics; depends on BSD err compatibility.

Risks: fatal exit is problematic in reusable library code. Zero-size allocation may return NULL without error, mirroring C library behavior.

Test signals: normal allocation/free, zero-size allocation tolerance, and allocation failure injection.
