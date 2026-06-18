# sources/distributed-fs/openafs/src/external/heimdal/roken/erealloc.c

Purpose: provides a `realloc()` wrapper that exits on nonzero allocation failure.

Important APIs/types/functions: `erealloc(void *ptr, size_t sz)`.

Control flow: calls `realloc(ptr, sz)`, calls `errx(1, ...)` if NULL and `sz != 0`, and returns the new pointer otherwise.

State and persistence behavior: mutates heap ownership exactly like `realloc()`: on success the old pointer is invalid, on zero-size behavior depends on the C library, and on failure this wrapper exits.

Dependencies and integration points: roken fatal allocation helper used by utilities that avoid explicit allocation error handling.

Risks: callers lose recoverability on memory pressure. As with any `realloc`, assigning directly to the original pointer is only safe because this wrapper exits on failure.

Test signals: grow/shrink behavior, NULL-as-malloc behavior, zero-size behavior, and failure injection.
