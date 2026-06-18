# sources/distributed-fs/openafs/src/external/heimdal/roken/win32_alloc.c

## Purpose
Provides Windows allocator wrapper functions so binaries built with roken can share one allocation/free family across executable and DLL boundaries.

## Important APIs, Types, And Functions
Exports `rk_calloc`, `rk_free`, `rk_malloc`, `rk_strdup`, and `rk_wcsdup`. The file undefines allocator/string-dup macros before calling the real C runtime functions.

## Control Flow
Every wrapper directly delegates to the corresponding CRT allocator or duplicator and returns its result.

## State And Persistence
Heap allocations are created or freed in the CRT heap selected by the roken binary. No module globals exist.

## Dependencies And Integration Points
`roken.h.in` maps `calloc`, `malloc`, `free`, `realloc`, `strdup`, and `wcsdup` to roken wrappers on MSVC unless `ROKEN_NO_DEFINE_ALLOCATORS` is set. This file supplies most of those wrappers.

## Risks And Test Signals
The design relies on all participating code including the same roken header policy. Mixing native `free` with `rk_malloc` can still fail if callers bypass macros. Tests should cover allocation/free across DLL boundaries, `strdup` and `wcsdup`, null-free behavior, and builds with allocator remapping disabled.
