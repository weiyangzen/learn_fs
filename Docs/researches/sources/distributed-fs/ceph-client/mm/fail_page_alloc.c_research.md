# sources/distributed-fs/ceph-client/mm/fail_page_alloc.c

## Purpose
`fail_page_alloc.c` implements page allocator fault injection. It decides when page allocations should fail based on global fault-injection policy, allocation order, and GFP flag filters, allowing kernel error paths to be exercised deliberately.

## Important APIs, types, and functions
The file-scope `fail_page_alloc` object contains `struct fault_attr attr`, `ignore_gfp_highmem`, `ignore_gfp_reclaim`, and `min_order`. Defaults ignore highmem allocations, ignore direct-reclaim allocations, and inject only for order 1 or higher. `setup_fail_page_alloc()` parses the `fail_page_alloc=` boot parameter. `should_fail_alloc_page()` is the exported decision point and is marked with `ALLOW_ERROR_INJECTION(..., TRUE)`. With fault-injection debugfs enabled, `fail_page_alloc_debugfs()` creates tunables under `fail_page_alloc`.

## Control flow
`should_fail_alloc_page()` returns false when the allocation order is below `min_order`, `__GFP_NOFAIL` is set, the highmem filter matches, or the direct-reclaim filter matches. It translates `__GFP_NOWARN` into `FAULT_NOWARN`, then calls `should_fail_ex()` with a size weight of `1 << order`. The debugfs init path creates the base fault-attribute directory and adds booleans for reclaim/highmem filters plus a `min-order` u32 knob.

## State and persistence
State lives in the global fault attributes and debugfs-exposed filter fields. Boot parameters initialize the fault policy early; debugfs updates adjust it at runtime. No per-allocation state is persisted.

## Dependencies and integration points
This code depends on `linux/fault-inject.h`, debugfs, error-injection infrastructure, and the page allocator's call site for `should_fail_alloc_page()`. It reflects allocator semantics by respecting `__GFP_NOFAIL` and optionally avoiding highmem or reclaimable contexts.

## Risks and test signals
Misconfigured injection can make broad kernel paths fail, so default filters are conservative. The size weight must stay consistent with order semantics, and `__GFP_NOFAIL` must never be failed. Useful signals include booting with `fail_page_alloc=` parameters, modifying debugfs knobs, observing expected allocation failures without warnings when `__GFP_NOWARN` is present, and running MM error-path or fstest workloads under injection.
