# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/perfstat.h

## Purpose

`perfstat.h` declares debug allocation wrappers for NetIDMgr utility code. In debug builds, allocation calls are routed through tracking functions that record source file and line; in non-debug builds, the macros map directly to CRT allocation and string-duplication functions.

## Important APIs, types, and functions

Macros include `PMALLOC`, `PCALLOC`, `PREALLOC`, `PFREE`, `PDUMP`, `PWCSDUP`, and `PSTRDUP`. Debug implementations declared here are `perf_malloc`, `perf_realloc`, `perf_free`, `perf_dump`, `perf_wcsdup`, `perf_strdup`, and `perf_calloc`.

## Control flow

Preprocessor branching on `DEBUG` selects tracked versus direct allocation. Debug macros pass `__FILE__` and `__LINE__` to the allocator. Release builds compile away dump behavior with `PDUMP(f) ((void) 0)`.

## State and persistence behavior

The header does not define storage, but debug implementations likely maintain an in-process allocation ledger. `perf_dump` can persist that ledger to a named file.

## Dependencies and integration points

It depends on `khdefs.h` for export/calling convention macros and on CRT allocation APIs. The AFS plugin uses `PMALLOC`/`PFREE` for dialog state and extension strings, so debug builds can trace leaks across plugin configuration and extension registration paths.

## Risks and edge cases

Because release macros map to CRT `wcsdup` and `strdup`, portability depends on those functions being available. Mixing `PMALLOC` allocations with nonmatching frees outside `PFREE` would undermine debug tracking. Debug source-location tracking can also reveal memory leaks caused by early return paths in plugin dialogs or extension setup.

## Test signals

Debug test signals include no residual entries after dialogs are destroyed and extensions are freed, correct dump output, and clean behavior for zero-size or failed allocations. Release builds should compile without unresolved perf symbols.
