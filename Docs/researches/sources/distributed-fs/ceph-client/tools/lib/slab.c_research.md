# sources/distributed-fs/ceph-client/tools/lib/slab.c

Purpose: Provides small user-space implementations of kernel allocation helpers `kmalloc()`, `kfree()`, and `kmalloc_array()` for tools code.

Important APIs/types/functions: Globals `kmalloc_nr_allocated` and `kmalloc_verbose` track allocation count and optional debug printing. `kmalloc(size, gfp)` uses `malloc()`. `kmalloc_array(n, size, gfp)` uses `calloc()`. `kfree(p)` releases with `free()`.

Control flow: Allocation returns `NULL` unless `gfp` includes `__GFP_DIRECT_RECLAIM`. Successful allocation increments `kmalloc_nr_allocated`; `kfree()` decrements for non-NULL pointers. `__GFP_ZERO` triggers explicit zeroing after allocation, although `calloc()` already zeroes arrays.

State and persistence: Allocation count is process-global and updated with userspace RCU atomics (`uatomic_inc/dec`). Allocated memory belongs to callers and must be freed with `kfree()`.

Dependencies/integration: Includes `<urcu/uatomic.h>`, `<linux/slab.h>`, `<linux/gfp.h>`, libc `malloc/calloc/free`, and `stdio/string` for verbose output and zeroing.

Risks: `kmalloc()` calls `memset(ret, 0, size)` without checking `ret`, so `__GFP_ZERO` plus allocation failure dereferences `NULL`. `kmalloc_array()` does not guard integer overflow in `n * size` before the redundant `memset()`. Allocation count increments even if `malloc()`/`calloc()` returns `NULL`. Only `__GFP_DIRECT_RECLAIM` allocation mode is accepted.

Test signals: Test allocation/free count under success and failure injection, `__GFP_ZERO`, missing reclaim flag, null free, `kmalloc_array()` overflow-sized inputs, and verbose output.
