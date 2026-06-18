# File Research: sources/cow-pools/bcachefs-tools/linux/mempool.c

Implements Linux mempool semantics: create/init/exit/destroy, resize, allocate, free, and standard slab/kmalloc/page alloc/free callbacks. Pools preallocate a minimum reserve and wait on a waitqueue when both direct allocation and reserve removal fail.

Debug poisoning hooks are conditionally present; KASAN hooks are disabled. Allocations intentionally add no-retry/nowarn behavior and avoid `__GFP_ZERO`.
