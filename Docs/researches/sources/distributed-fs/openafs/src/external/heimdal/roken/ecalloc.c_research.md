# sources/distributed-fs/openafs/src/external/heimdal/roken/ecalloc.c

Purpose: provides an allocation wrapper like `calloc()` that terminates the process on allocation failure.

Important APIs/types/functions: `ecalloc(size_t number, size_t size)`.

Control flow: calls `calloc(number, size)`, and if it returns NULL for a nonzero product, calls `errx(1, ...)`; otherwise returns the pointer.

State and persistence behavior: returns heap memory owned by the caller. On failure, process state ends via `errx`.

Dependencies and integration points: uses roken export macros and BSD `errx()`. Intended for code paths that prefer fatal allocation failure over error plumbing.

Risks: `number * size` can overflow in the diagnostic and zero/nonzero check, so huge overflowed requests could be mishandled depending on `calloc()` behavior. Fatal exit is unsuitable for library paths that must report errors.

Test signals: successful zeroed allocation, zero-size behavior, and failure injection verifying fatal diagnostic paths.
