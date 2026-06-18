# sources/distributed-fs/ceph-client/mm/slab_common.c

## Purpose

`slab_common.c` implements allocator-strategy-independent slab infrastructure for the Ceph client kernel source tree. It owns the global slab cache registry, common cache creation and destruction policy, kmalloc cache bootstrap, slab observability hooks, sensitive-free helpers, and the `kvfree_rcu()` deferred free batching implementation when `CONFIG_KVFREE_RCU_BATCHED` is enabled.

This file does not implement the low-level SLUB allocation algorithm itself. It coordinates common `struct kmem_cache` lifecycle rules and delegates allocator-specific work to functions such as `do_kmem_cache_create()`, `__kmem_cache_shutdown()`, `__kmem_cache_shrink()`, `get_slabinfo()`, and `__kmem_obj_info()` from the local slab implementation.

## Important APIs, Types, and Globals

- `enum slab_state slab_state`: global allocator initialization state. Important milestones include caches becoming usable at `UP` and sysfs-capable cache release after `FULL`.
- `LIST_HEAD(slab_caches)`: global list of all slab caches, protected by `slab_mutex`.
- `DEFINE_MUTEX(slab_mutex)`: serializes cache creation, aliasing, destruction, and `/proc/slabinfo` traversal.
- `struct kmem_cache *kmem_cache`: meta-cache used to allocate `struct kmem_cache` descriptors.
- `kmalloc_caches[NR_KMALLOC_TYPES]`: global kmalloc cache table, including normal, reclaimable, memcg, DMA, and optional randomized variants.
- `kmalloc_size_index[]`: lookup table mapping small allocation sizes to kmalloc cache indexes.
- `struct kmem_cache_args`: cache creation parameters used here for alignment, constructors, usercopy windows, sheaf capacity, and optional custom free-pointer offsets.
- `kmem_buckets`: optional per-caller bucket cache set for dynamic allocations when `CONFIG_SLAB_BUCKETS` is enabled.
- `struct kvfree_rcu_bulk_data`: page-sized bulk array of deferred `kvfree_rcu()` pointers plus an RCU grace-period snapshot.
- `struct kfree_rcu_cpu` and `struct kfree_rcu_cpu_work`: per-CPU state and queued RCU work batches for batched `kvfree_rcu()` reclamation.

Exported or externally visible functions include:

- `kmem_cache_size()`
- `__kmem_cache_create_args()`
- `kmem_buckets_create()`
- `kmem_cache_destroy()`
- `kmem_cache_shrink()`
- `slab_is_available()`
- `kmem_dump_obj()` under `CONFIG_PRINTK`
- `create_boot_cache()` and `create_kmalloc_caches()` during boot
- `kmalloc_size_roundup()`
- `kmalloc_fix_flags()`
- `cache_random_seq_create()` / `cache_random_seq_destroy()` under freelist randomization
- `dump_unreclaimable_slab()` and `/proc/slabinfo` support under `CONFIG_SLUB_DEBUG`
- `kfree_sensitive()`
- `bpf_get_kmem_cache()` under `CONFIG_BPF_SYSCALL`
- `kvfree_call_rcu()`, `kvfree_rcu_barrier()`, `kvfree_rcu_barrier_on_cache()`, and `kvfree_rcu_init()`

## Cache Creation and Merge Control

The cache creation path starts in `__kmem_cache_create_args()`. It normalizes debug flags, initializes stack depot for `SLAB_STORE_USER`, forces no-merge for caches with a specific sheaf capacity, validates caller inputs, clamps hardened-usercopy windows, then attempts aliasing before allocating a new cache descriptor.

Merge policy is controlled by:

- Boot parameters: `slub_nomerge`, `slub_merge`, `slab_nomerge`, and `slab_merge`.
- `SLAB_NEVER_MERGE`: debug, RCU type-safe, leak tracing, failslab, explicit no-merge, and in-object extension flags.
- `SLAB_MERGE_SAME`: flags that must match for merge candidates, such as reclaim, DMA, DMA32, and memcg accounting.
- Constructors and hardened-usercopy windows, which make caches unmergeable.
- Negative `refcount` during bootstrap, which temporarily exempts boot caches from merging.

`find_mergeable()` aligns the requested object size and compares it against existing caches in reverse list order. A cache can be reused only when it is mergeable, large enough, flag-compatible, alignment-compatible, and not meaningfully larger than the requested aligned object. If a match is found, `__kmem_cache_alias()` adds a sysfs alias, increments the cache `refcount`, and expands `object_size`/`inuse` so `kzalloc()` clears enough bytes for the aliased user.

If no alias is available, `create_cache()` allocates a `struct kmem_cache` from the meta-cache, validates optional custom freelist placement, calls `do_kmem_cache_create()`, sets `refcount = 1`, and links the cache into `slab_caches`.

## Boot and kmalloc Cache Setup

`create_boot_cache()` handles early cache creation before full slab services exist. It computes minimum alignment, including the kmalloc guarantee that a power-of-two object is aligned to that size, fills hardened-usercopy arguments when enabled, calls the allocator-specific creation hook, and marks the cache with `refcount = -1` so it cannot be merged during bootstrap.

`create_kmalloc_cache()` allocates a cache descriptor from the meta-cache and creates a boot kmalloc cache with `SLAB_KMALLOC`. `create_kmalloc_caches()` then builds the full `kmalloc_caches` matrix for all enabled cache types:

- normal kmalloc caches;
- reclaim-accounted caches;
- memcg-accounted caches, unless memcg kmem is disabled;
- DMA caches when `CONFIG_ZONE_DMA` is enabled;
- randomized kmalloc caches when configured.

`setup_kmalloc_cache_index_table()` adjusts small-size lookup slots for architectures with larger `KMALLOC_MIN_SIZE`. `__kmalloc_minalign()` factors in DMA cache alignment and unaligned SWIOTLB bounce buffering. Once the kmalloc table is usable, `slab_state` moves to `UP`, and the optional `kmalloc_buckets` descriptor cache is created.

## Cache Destruction, Shrink, and Release

`kmem_cache_destroy()` is the central teardown path. It rejects null or invalid cache pointers, waits for in-flight `kfree_rcu()`/`kvfree_rcu()` objects on the cache, handles `SLAB_TYPESAFE_BY_RCU` debug barriers, drains deferred `kmalloc/kfree_nolock()` work, then takes `cpus_read_lock()` and `slab_mutex`.

The cache `refcount` is decremented under the mutex. If other aliases still reference it, destruction stops after unlocking. When the final reference is removed, the function shuts down KASAN quarantine for the cache, calls `__kmem_cache_shutdown()`, warns if live objects remain outside KUnit slab tests, removes the cache from `slab_caches`, unlinks sysfs/debugfs state, optionally waits another RCU grace period for `SLAB_TYPESAFE_BY_RCU`, and finally releases the cache descriptor through `kmem_cache_release()`.

`kmem_cache_release()` shuts down KFENCE integration and chooses sysfs-aware release once slab state is `FULL`; otherwise it calls `slab_kmem_cache_release()`. `slab_kmem_cache_release()` invokes allocator-specific release, frees the constant cache name, and returns the descriptor to the meta-cache.

`kmem_cache_shrink()` first lets KASAN shrink any quarantined objects, then delegates to `__kmem_cache_shrink()`.

## Deferred Free via kvfree_rcu

The file contains both the simple and batched `kvfree_rcu()` implementations.

Without `CONFIG_KVFREE_RCU_BATCHED`, `kvfree_call_rcu()` either queues `kvfree_rcu_cb` with `call_rcu()` for embedded `rcu_head` users or synchronously waits for a grace period and calls `kvfree()` for the one-argument variant.

With batching enabled, deferred frees are grouped per CPU:

- Bulk channel 0 stores slab/kmalloc pointers freed with `kfree_bulk()`.
- Bulk channel 1 stores vmalloc pointers freed with `vfree()`.
- The fallback linked-list channel stores objects through their embedded `rcu_head` when a bulk page cannot be obtained.

`add_ptr_to_bulk_krc_lock()` records a pointer into the current CPU's active bulk page, allocating or reusing a page-sized `kvfree_rcu_bulk_data` node when allowed. Each bulk node records an RCU grace-period snapshot. If the bulk path fails, `kvfree_call_rcu()` schedules page-cache refill work and either falls back to the embedded-head list or, for the one-argument variant, releases the lock, synchronizes RCU inline, and frees immediately.

`kfree_rcu_monitor()` periodically drains already grace-period-safe batches via `kvfree_rcu_drain_ready()`, attempts to offload remaining records to `kfree_rcu_work`, and rearms itself if pending per-CPU data remains. `kvfree_rcu_queue_batch()` moves active per-CPU channels into one of two `kfree_rcu_cpu_work` slots and queues RCU work on `rcu_reclaim_wq`. `kfree_rcu_work()` runs after the grace period and frees all detached bulk and fallback records.

The implementation also maintains a per-CPU page cache for bulk nodes. `fill_page_cache_func()` refills it, `drain_page_cache()` frees it under shrinker pressure, and `run_page_cache_worker()` schedules refill work with optional backoff after reclaim.

Barriers are explicit:

- `kvfree_rcu_barrier()` flushes RCU sheaves and all per-CPU batched work.
- `kvfree_rcu_barrier_on_cache()` flushes sheaves for a specific slab cache, then currently falls back to the global batched barrier.
- `kfree_rcu_scheduler_running()` starts monitor work for queued per-CPU data once the RCU scheduler is running.
- `kvfree_rcu_init()` allocates the reclaim workqueue, initializes every per-CPU batch/list/work object, validates module parameters, and registers the `slab-kvfree-rcu` shrinker.

## Observability and Diagnostics

`kmem_dump_obj()` identifies whether a pointer belongs to a slab or KFENCE object and prints cache name, object start, data offset, pointer offset, object size, allocation return address, allocation stack, and last free stack when available.

Under `CONFIG_SLUB_DEBUG`, this file registers `/proc/slabinfo` with a seq-file iterator over `slab_caches`. It emits cache object counts, object size, objects per slab, pages per slab, tunables, and slab totals. `dump_unreclaimable_slab()` is used from memory-pressure paths and uses `mutex_trylock()` to avoid sleeping indefinitely while still avoiding unsafe list traversal.

The file exports kmem tracepoints for `kmalloc`, `kmem_cache_alloc`, `kfree`, and `kmem_cache_free`. It also exposes `bpf_get_kmem_cache()` as a BPF kfunc, mapping a valid kernel virtual address to the owning slab cache when possible.

`kmalloc_fix_flags()` detects GFP flags invalid for slab allocation, masks them out, emits a warning and stack trace, and returns the sanitized flags. `kfree_sensitive()` obtains the allocated size with `ksize()`, unpoisons the range for KASAN, zeroes the entire allocated object with `memzero_explicit()`, and then frees it.

## Dependencies and Integration Points

Major dependencies include:

- Local allocator hooks from `mm/slab.h` and `mm/internal.h`.
- RCU internals from `../kernel/rcu/rcu.h` and trace events from `trace/events/rcu.h`.
- KASAN, KFENCE, kmemleak, stack depot, debugfs, sysfs, procfs, and tracepoint infrastructure.
- DMA alignment and SWIOTLB state for kmalloc minimum alignment.
- Memcg configuration for `SLAB_ACCOUNT` and kmalloc cgroup caches.
- Shrinker infrastructure for reclaiming deferred RCU free queues and cached bulk pages.
- CPU hotplug read locking around final cache teardown.

For a Ceph client kernel, this file is part of the general memory-management substrate used by Ceph and every other in-kernel subsystem. Ceph-specific objects allocated through `kmalloc()`, `kmem_cache_alloc()`, or `kfree_rcu()` rely on the lifecycle, accounting, debugging, and deferred-free semantics defined here.

## State and Persistence Behavior

The state is entirely in-kernel and runtime-only. There is no disk persistence. Persistent-looking names are exposed through procfs/sysfs/debugfs for observability, but the underlying cache descriptors, kmalloc tables, aliases, per-CPU RCU queues, cached bulk pages, workqueue items, and shrinker registrations exist only for the current boot.

Concurrency rules are central:

- `slab_mutex` protects `slab_caches` and cache refcounts.
- `cpus_read_lock()` prevents unsafe CPU hotplug interactions during destruction.
- Per-CPU `kfree_rcu_cpu.lock` protects deferred-free queues and cached bulk pages.
- RCU grace-period snapshots prevent premature freeing.
- Workqueues and delayed work move freeing out of allocation/free hot paths.
- Atomic counters summarize queued deferred-free objects for scheduling and shrinker decisions.

## Risks and Edge Cases

- Cache merging changes `object_size` and `inuse`; any flag or metadata that changes object layout must keep caches unmergeable.
- Incorrect hardened-usercopy windows are fail-closed by zeroing `usersize`/`useroffset`, which avoids unsafe copies but can silently remove intended usercopy allowances after warnings.
- Duplicate cache names are only warnings under `CONFIG_DEBUG_VM`; they can confuse userspace tools such as `slabtop`.
- Destroying a cache with live objects triggers warnings and skips descriptor release when allocator shutdown reports an error.
- `SLAB_TYPESAFE_BY_RCU` caches require careful RCU barriers because object reuse and slab-page lifetime are decoupled.
- `kvfree_rcu()` one-argument calls can still free inline after `synchronize_rcu()` on fallback; module teardown must ensure such callers have returned before destroying dependent caches.
- The batched `kvfree_rcu()` code trades memory for throughput through per-CPU bulk pages. Under pressure, the shrinker drains cached pages and queues, while refill backoff reduces reclaim interference.
- `kfree_sensitive()` clears the full allocated buffer, not just the caller-requested size, which is security-friendly but can be expensive for oversized kmalloc buckets.
- `kmalloc_fix_flags()` keeps the kernel running after bad GFP usage, but the warning indicates caller code should be corrected.

## Test Signals

Useful validation signals for changes touching this file include:

- Boot success through slab initialization, including `slab_state` reaching `UP` and later full sysfs/proc visibility.
- `/proc/slabinfo` formatting and stable traversal under `CONFIG_SLUB_DEBUG`.
- kmalloc cache creation for normal, reclaim, memcg, DMA, and randomized cache configurations.
- Cache aliasing behavior with and without `slab_nomerge`/`slab_merge` boot parameters.
- KASAN/KFENCE/kmemleak runs around cache creation, destruction, quarantine shutdown, and `kfree_sensitive()`.
- RCU torture or targeted `kfree_rcu()`/`kvfree_rcu()` stress with `CONFIG_KVFREE_RCU_BATCHED`, including barrier and shrinker paths.
- Memory pressure tests that invoke the `slab-kvfree-rcu` shrinker and `dump_unreclaimable_slab()`.
- BPF kfunc tests for `bpf_get_kmem_cache()` address validation.
- KUnit slab tests, especially paths where `slab_in_kunit_test()` suppresses live-object warnings.
