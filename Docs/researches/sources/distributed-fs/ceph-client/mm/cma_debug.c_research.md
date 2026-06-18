# sources/distributed-fs/ceph-client/mm/cma_debug.c

Purpose: Implements the debugfs interface for Contiguous Memory Allocator areas. It exposes `/sys/kernel/debug/cma/<area>/` controls and counters that let developers inspect CMA capacity, bitmap state, used pages, maximum clear bitmap chunk, and manually allocate or free CMA pages for testing.

Important APIs, types, and functions: `struct cma_mem` tracks debugfs-triggered allocations in an hlist. `cma_debugfs_get()`, `cma_used_get()`, and `cma_maxchunk_get()` back read-only debugfs files. `cma_alloc_mem()` calls `cma_alloc()`, records the allocation, and `cma_free_mem()` releases tracked allocations through `cma_release()`. `cma_debugfs_add_one()` creates the per-CMA directory, files, per-range bitmap directories, and backward-compatible symlinks. `cma_debugfs_init()` installs the root debugfs tree at `late_initcall`.

Control flow: initialization walks global `cma_areas[]`; each area gets `alloc`, `free`, `count`, `order_per_bit`, `used`, `maxchunk`, and `ranges/<n>/` entries. Writes to `alloc` allocate the requested page count and push a `cma_mem` entry onto `cma->mem_head`. Writes to `free` pop tracked entries until the requested count is released. Partial frees are supported only when `order_per_bit == 0`.

State and persistence: The debug-only allocation ledger lives in memory under each `struct cma` and is protected by `mem_head_lock`. CMA availability and bitmap reads use `cma->lock`. State is not persistent across boot and is meant for diagnostics.

Dependencies and integration: Depends on `linux/debugfs.h`, CMA internals from `cma.h`, CMA globals (`cma_area_count`, `cma_areas`), bitmap helpers, and debugfs u32 array support.

Risks: Debugfs write interfaces can intentionally consume CMA memory; misuse can perturb production memory behavior. Partial-release behavior is constrained by bitmap granularity. Debugfs creation errors are mostly ignored, matching debugfs convention but reducing observability of setup failures.

Test signals: Enable CMA and debugfs, verify each CMA area appears, compare `used`/`maxchunk` against allocations, write counts to `alloc` and `free`, and inspect `ranges/*/bitmap`. Stress with multiple writers to exercise `mem_head_lock` and CMA locking.
