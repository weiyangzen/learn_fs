# sources/distributed-fs/openafs/src/external/heimdal/roken/realloc.c

## Purpose
Provides roken's allocator wrapper `rk_realloc`, mainly to normalize behavior and support macro remapping of `realloc` through `roken.h`.

## Important APIs, Types, And Functions
The only function is `rk_realloc(void *ptr, size_t size)`. It undefines any `realloc` macro before including/using libc allocation so the wrapper can call the real allocator.

## Control Flow
If `ptr` is `NULL`, the function delegates to `malloc(size)`. Otherwise it delegates to `realloc(ptr, size)`.

## State And Persistence
The persistent state is heap memory managed by the C runtime. The function may move or free the old allocation exactly as `realloc` would.

## Dependencies And Integration Points
On MSVC builds, `roken.h.in` can map `realloc` to `rk_realloc` so all roken-linked binaries share the same allocator family. This file is a small but important part of that ABI boundary.

## Risks And Test Signals
Semantics are intentionally libc-like, including implementation-defined handling of `size == 0`. Test signals are compile coverage with allocator macro remapping, successful `NULL` allocation, resize preservation, and cross-DLL allocation/free consistency on Windows.
