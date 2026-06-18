# sources/distributed-fs/ceph-client/tools/lib/zalloc.c

Purpose: Provides zero-allocation and freeing helpers for tools code.

Important APIs/types/functions: `zalloc(size)` returns `calloc(1, size)`. `__zfree(void **ptr)` frees `*ptr` and sets it to NULL.

Control flow: Straight wrappers around libc allocation/free.

State and persistence: Mutates caller pointer in `__zfree()`. Allocated memory is caller-owned.

Dependencies/integration: Includes `<linux/zalloc.h>` for declarations and libc `stdlib.h`.

Risks: `__zfree()` does not check `ptr` before dereference; callers must pass a valid pointer-to-pointer. `zalloc()` returns NULL on allocation failure without diagnostics.

Test signals: Allocate zeroed memory, free normal pointer, free NULL pointee, and invalid pointer-to-pointer avoidance through API usage tests.
