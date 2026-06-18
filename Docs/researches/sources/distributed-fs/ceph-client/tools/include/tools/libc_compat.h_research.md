# sources/distributed-fs/ceph-client/tools/include/tools/libc_compat.h

## Purpose
Provides libc compatibility shims for tool builds on platforms missing newer libc APIs.

## Important APIs, Types, and Functions
Conditionally defines `reallocarray(void *ptr, size_t nmemb, size_t size)` when `COMPAT_NEED_REALLOCARRAY` is set. The function uses `check_mul_overflow()` before calling `realloc()`.

## Control Flow, State, and Persistence
The shim computes `nmemb * size`, returns `NULL` on overflow, and otherwise delegates to `realloc()`. It keeps no state; allocation state is owned by libc.

## Dependencies and Integration
Depends on `<stdlib.h>` and `<linux/overflow.h>`, including `unlikely()` and overflow helpers. It integrates with BPF/perf tools that want `reallocarray()` semantics without requiring a specific libc baseline.

## Risks and Test Signals
Risks include relying on `errno` behavior not explicitly set on overflow, name collision if libc already declares `reallocarray()`, and allocator semantics for zero-sized requests. Test signals include overflow cases near `SIZE_MAX`, successful growth preserving contents, and builds with and without `COMPAT_NEED_REALLOCARRAY`.
