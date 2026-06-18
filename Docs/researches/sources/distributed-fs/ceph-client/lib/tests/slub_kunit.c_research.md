## sources/distributed-fs/ceph-client/lib/tests/slub_kunit.c

### Purpose
This KUnit suite exercises SLUB allocator debugging and hardening behavior. It deliberately corrupts redzones, poisoned free objects, freelist pointers, kmalloc redzones, leak accounting, kfree_rcu destruction, krealloc zeroing, and optional nolock allocation from perf overflow context, then checks reported slab error counts.

### Important APIs, types, and functions
`test_kmem_cache_create()` wraps `kmem_cache_create()` with `SLAB_NO_USER_FLAGS` and sets `SLAB_SKIP_KFENCE` to avoid KFENCE intercepting the same corruption. `slab_errors` is exposed to KUnit through `kunit_add_named_resource()` in `test_init()`. Core cases use `validate_slab_cache()`, `kmem_cache_alloc/free/destroy()`, `kasan_disable_current()`/`kasan_enable_current()`, `__kmalloc_cache_noprof()`, `alloc_hooks()`, `kfree_rcu()`, workqueues, `krealloc(... | __GFP_ZERO)`, and optionally perf event overflow callbacks with `kmalloc_nolock()`/`kfree_nolock()`.

### Control flow
Each test creates a purpose-specific cache, performs allocation/free/corruption sequence, calls validation or destruction, and asserts expected `slab_errors`. Non-KASAN-only tests corrupt freed-object metadata and data bytes. RCU tests skip when built-in because module lifetime constraints make `kfree_rcu()` unsuitable. Workqueue destruction repeatedly schedules delayed cache destruction after `kfree_rcu()`. The perf test creates a pinned hardware counter, enables callbacks during heavy allocate/free loops, then checks no slab errors unless allocations failed and the test skips.

### State and persistence
`slab_errors` is reset per test in suite init. Static `resource` and optional static `objects[]` are suite/test support state. Caches, workqueues, perf events, and allocations are intended to be destroyed or freed within each case, though some tests intentionally trigger leak or destroy diagnostics.

### Dependencies and integration points
The suite reaches into allocator internals via `../mm/slab.h`, uses KUnit bug support, mm/slab APIs, KASAN controls, RCU, workqueues/delays, and optional perf events. It integrates as suite `slub_test`.

### Risks and edge cases
The suite intentionally writes out of bounds and after free with KASAN disabled around selected operations; incorrect guard handling could crash the test kernel. Expected error counts are tightly coupled to SLUB validation internals. Some cases skip depending on KASAN, built-in/module mode, workqueue allocation, cache creation, perf support, or allocation failures.

### Test signals
Signals include exact `slab_errors` counts after corruption/repair sequences, zero-error expectations for valid RCU and krealloc paths, skip reasons for unsupported modes, and optional stress of nolock allocation in perf overflow context.
