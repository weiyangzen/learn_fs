# sources/distributed-fs/ceph-client/lib/zstd/common/allocations.h

Purpose: Supplies small inline allocation wrappers for zstd contexts, honoring optional `ZSTD_customMem` callbacks while defaulting to kernel zstd dependency allocation hooks.

Important APIs/functions:
- `ZSTD_customMalloc(size_t size, ZSTD_customMem customMem)`.
- `ZSTD_customCalloc(size_t size, ZSTD_customMem customMem)`.
- `ZSTD_customFree(void *ptr, ZSTD_customMem customMem)`.

Control flow:
- If a custom allocator exists, malloc/calloc route to it; calloc is emulated with allocation plus `ZSTD_memset`.
- Otherwise wrappers call `ZSTD_malloc`, `ZSTD_calloc`, and `ZSTD_free` from `zstd_deps.h`.
- Free ignores NULL and uses custom free when present.

State and persistence:
- No local state. Allocated memory lifetime is owned by the caller/context.

Dependencies and integration:
- Defines `ZSTD_DEPS_NEED_MALLOC`, includes `zstd_deps.h`, `compiler.h`, and `<linux/zstd.h>`.
- Used by zstd context/dictionary code that supports custom memory hooks.

Risks:
- In this kernel dependency layer, default `ZSTD_malloc`/`calloc` may be NULL stubs unless the build provides allocators; many kernel zstd paths use workspaces instead.
- If `customAlloc` is provided without compatible `customFree`, freeing can be wrong.
- Custom calloc does not check allocation failure before `ZSTD_memset`; current code calls `ZSTD_memset(ptr, 0, size)` unconditionally on custom allocation result.

Test signals:
- Custom allocator unit tests for malloc/calloc/free paths, including allocation failure.
- Workspace-only zstd paths should not rely on default heap allocation.
