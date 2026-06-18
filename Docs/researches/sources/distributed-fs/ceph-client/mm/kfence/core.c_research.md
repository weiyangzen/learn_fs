# sources/distributed-fs/ceph-client/mm/kfence/core.c

## Purpose

`core.c` implements KFENCE's guarded-object allocator, sampling gate, metadata lifecycle, guard-page protection, canary checking, debugfs views, initialization, shutdown handling, and page-fault classification. It is the allocator-side half of KFENCE.

## Important APIs, Types, and Functions

Important global state includes `kfence_enabled`, `disabled_by_warn`, `kfence_sample_interval`, `__kfence_pool`, `kfence_metadata`, `kfence_metadata_init`, `kfence_freelist_lock`, `kfence_freelist`, `kfence_allocation_key`, `kfence_allocation_gate`, `alloc_covered[]`, `stack_hash_seed`, and `counters[]`. Key public functions are `kfence_alloc_pool_and_metadata()`, `kfence_init()`, `kfence_shutdown_cache()`, `__kfence_alloc()`, `kfence_ksize()`, `kfence_object_start()`, `__kfence_free()`, and `kfence_handle_page_fault()`. Core internal functions include `kfence_init_pool()`, `kfence_guarded_alloc()`, `kfence_guarded_free()`, `metadata_update_state()`, `set_canary()`, `check_canary()`, `toggle_allocation_gate()`, and `kfence_init_late()`.

## Control Flow

Boot allocates pool and metadata unless sampling is disabled or KASAN hardware tags are active. Pool initialization marks object pages as slab pages, protects guard pages, initializes metadata, randomizes the freelist, and publishes `kfence_metadata` only after success. Sampling uses a delayed work item to periodically open the allocation gate and optionally enable a static key. `__kfence_alloc()` filters incompatible sizes/zones/caches, advances the gate, records a stack hash, skips covered sources when the pool is mostly full, and calls `kfence_guarded_alloc()`. Guarded allocation removes metadata from the freelist, chooses left or right placement in the object page, stores metadata and stack state, sets canaries, initializes memory/constructors, and updates counters. Free validates the exact object address, reports invalid/double frees, checks and restores canaries/guard-page protection, handles init-on-free, and either returns metadata to the freelist or marks zombie allocations during cache shutdown. Page faults inside the KFENCE pool are classified as redzone OOB, object-page UAF, or invalid, reported through `kfence_report_error()`, then unprotected so execution can proceed or the selected fault policy can trigger.

## State and Persistence Behavior

KFENCE keeps a fixed pool and metadata array for the lifetime of the kernel once initialized. Object metadata tracks state, address, size, cache pointer, one temporarily unprotected page, stack tracks, allocation coverage hash, and optional memcg object extensions. Counters and debugfs output persist until reboot. Runtime module parameters can disable or re-enable sampling if initialization resources remain available.

## Dependencies and Integration Points

The file integrates with slab allocation/free hooks, architecture page-protection helpers from `asm/kfence.h`, KASAN enablement checks, KCSAN scoped-access assertions, stack tracing, RCU for `SLAB_TYPESAFE_BY_RCU`, memcg object extensions, panic/reboot notifiers, debugfs, static keys, irq work, and report handling in `report.c`.

## Risks and Edge Cases

Important risks include recursive allocation while reporting, page-protection failures, races with cache destruction, RCU delayed frees, debugfs iteration over changing metadata, use-after-free faults racing with reallocation, and late enablement allocation failures. `KFENCE_WARN_ON()` disables KFENCE after internal invariants fail. Coverage skipping is probabilistic because it uses a counting Bloom filter over stack hashes.

## Test Signals

Signals include KFENCE KUnit tests, debugfs `kfence/stats` and `kfence/objects`, OOB/UAF/invalid-free/corruption reports, sampling interval changes through module parameters, cache shutdown zombie accounting, panic-time canary checks when enabled, and boot/late-enable logs showing pool address and object count.
