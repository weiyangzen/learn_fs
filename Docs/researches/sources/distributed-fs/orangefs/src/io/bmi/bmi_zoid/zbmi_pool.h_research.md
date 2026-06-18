# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zbmi_pool.h

## Purpose

`zbmi_pool.h` declares the fixed shared-memory pool wrapper used by the ZOID BMI server. It hides the dlmalloc mspace implementation behind four functions for initialization, teardown, allocation, and free.

## Important APIs

- `zbmi_pool_init(void *start, size_t len)` initializes the allocator over a caller-provided memory range.
- `zbmi_pool_fini(void)` destroys allocator state.
- `zbmi_pool_malloc(size_t bytes)` allocates bytes from the initialized pool.
- `zbmi_pool_free(void *mem)` frees a pointer previously returned by `zbmi_pool_malloc`.

## Control flow

The header has no runtime control flow. The expected lifecycle is strict: initialize once with the expected shared-memory region, allocate/free while the server is active, then finalize before the backing memory is unmapped.

## State and persistence behavior

The header declares operations over hidden process-local state in `zbmi_pool.c`. The backing storage is supplied by the caller, so memory lifetime is external: callers must not unmap or reuse the region while the pool is active.

## Dependencies and integration points

The declarations use `size_t` but the header does not include `<stddef.h>` itself. In current usage, `server.c` includes system and BMI headers before `zbmi_pool.h`, so `size_t` is already available. The header is included by `server.c` and implemented by `zbmi_pool.c`.

## Risks and edge cases

- Missing `<stddef.h>` makes the header fragile if included first in a new translation unit.
- The API does not expose initialization failure, usable capacity, or ownership checks.
- The API accepts any pointer in `zbmi_pool_free`; invalid pointers are handled only by dlmalloc's runtime checks, which may abort.
- The single hidden pool means this interface cannot manage multiple independent shared-memory regions without modification.

## Test signals

A compile test should include `zbmi_pool.h` first to reveal the missing `size_t` include. Runtime tests should validate the lifecycle, alignment, exhaustion, free/reuse behavior, and invalid-order calls around init/fini.
