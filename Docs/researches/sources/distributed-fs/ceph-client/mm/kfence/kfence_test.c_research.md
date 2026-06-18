# sources/distributed-fs/ceph-client/mm/kfence/kfence_test.c

## Purpose

`kfence_test.c` is the KUnit suite for KFENCE. It forces or waits for guarded allocations, triggers representative memory-safety bugs, captures console report output via the printk tracepoint, and verifies both reports and allocator integration behavior.

## Important APIs, Types, and Functions

Important test infrastructure includes `observed`, `probe_console()`, `report_available()`, `struct expect_report`, `report_matches()`, `setup_test_cache()`, `test_cache_destroy()`, `test_alloc()`, and `test_free()`. Test cases cover OOB read/write, UAF, nofault UAF, double free, invalid free address, canary corruption, aligned kmalloc gaps, cache shrink/destroy, bulk free, init-on-free, constructors, `__GFP_ZERO`, invalid pool access, `SLAB_TYPESAFE_BY_RCU`, `krealloc()`, and bulk allocation.

## Control Flow

Suite initialization registers a console tracepoint probe. Each test clears observed report state and optionally selects a private kmem_cache variant by checking for the `-memcache` suffix. `test_alloc()` loops until it obtains a KFENCE allocation matching the requested placement policy or returns a non-KFENCE allocation for negative cases, yielding so the sampling gate can open. Faulting tests perform a bad read/write/free and then call `report_matches()` to compare the report title and address line. Test exit destroys any custom cache; suite exit unregisters the tracepoint and synchronizes.

## State and Persistence Behavior

Test state is transient: `observed` stores the two report lines of interest, `test_cache` owns an optional kmem_cache for the current case, and `test->priv` selects cache-backed variants. The suite intentionally reads live KFENCE global state, pool address, and sampling interval.

## Dependencies and Integration Points

The suite depends on KUnit, printk trace events, KFENCE internals, slab/kmalloc APIs, RCU, copy-from-kernel-nofault behavior, `kmalloc_caches`, and arch-specific address translation via optional `arch_kfence_test_address()`. The Makefile disables frame-pointer omission and sibling-call optimization to keep stack matching stable.

## Risks and Edge Cases

Tests are timing-sensitive because they wait for sampled allocations. Console matching is intentionally partial because symbol offsets and module suffixes vary. Some tests skip or soften expectations for slow sample intervals, init-on-free config, and difficulty reacquiring the same guarded object.

## Test Signals

The file itself is the primary signal: `kunit.py run kfence` or kernel KUnit execution should pass both kmalloc and memcache variants, with no stray reports in negative cases. Stable report matching validates report formatting and stack trimming in `report.c`.
