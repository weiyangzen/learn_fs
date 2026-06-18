# Group Research: group_906_linux_sources_os_linux_linux_mm_slab_common_c_50d6b35dc2e9

Scope checked against `Docs/research_subset_a.md`: the listed file is under `sources/os/linux/linux`, which is included in subset A. The source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/slab_common.c -->
# File Research: sources/os/linux/linux/mm/slab_common.c

Common Linux slab allocator infrastructure shared across allocator strategy code. This file owns cache creation/destruction policy, slab cache merging rules, kmalloc cache bootstrap, slab diagnostics, secure free helpers, tracepoint exports, and the generic `kvfree_rcu()` batching implementation.

Key responsibilities:
- Defines global slab allocator state: `slab_state`, `slab_caches`, `slab_mutex`, and the bootstrap `kmem_cache`.
- Implements slab cache merge policy through `SLAB_NEVER_MERGE`, `SLAB_MERGE_SAME`, boot parameters `slab_nomerge`/`slab_merge` and `slub_nomerge`/`slub_merge`, and helpers such as `slab_unmergeable()`, `slab_args_unmergeable()`, and `find_mergeable()`.
- Provides cache creation via `__kmem_cache_create_args()`, including debug flag activation, stack depot setup for `SLAB_STORE_USER`, hardened-usercopy argument validation, alignment calculation, aliasing, and fallback to new cache allocation.
- Supports optional separate kmalloc bucket sets through `kmem_buckets_create()` when `CONFIG_SLAB_BUCKETS` is enabled.
- Provides cache teardown and shrink entry points: `kmem_cache_destroy()`, `kmem_cache_release()`, `slab_kmem_cache_release()`, and `kmem_cache_shrink()`.
- Bootstraps kmalloc caches through `create_boot_cache()`, `create_kmalloc_cache()`, `setup_kmalloc_cache_index_table()`, `new_kmalloc_cache()`, and `create_kmalloc_caches()`.
- Defines kmalloc size metadata: `kmalloc_caches`, optional random kmalloc seed, `kmalloc_size_index`, `kmalloc_info[]`, and `kmalloc_size_roundup()`.
- Provides allocation hardening and diagnostics: `kfree_sensitive()`, `kmem_dump_obj()`, optional `/proc/slabinfo`, unreclaimable slab dumps, freelist randomization sequence setup, and a BPF kfunc to resolve an address to its `kmem_cache`.
- Exports kmem tracepoints for allocation/free events.
- Implements both simple and batched `kvfree_call_rcu()` depending on `CONFIG_KVFREE_RCU_BATCHED`.

Important behavior:
- Cache merging is disabled globally by boot policy or per-cache by debug flags, RCU type-safety, no-leak tracing, failslab, explicit no-merge, in-object object extensions, constructors, hardened-usercopy windows, custom sheaf capacity, or bootstrap negative refcounts.
- Merge candidates must match rounded object size/alignment compatibility and selected flags such as reclaim, DMA, DMA32, and memcg accounting.
- `__kmem_cache_create_args()` fails invalid flags, invalid names/sizes under debug VM checks, impossible hardened-usercopy windows, and invalid custom freelist offsets.
- Aliased caches increment the target cache refcount and expand `object_size`/`inuse` so `kzalloc()` clears the full requested object range.
- Custom freelist offsets are accepted only inside the object, aligned to `freeptr_t`, and paired with `SLAB_TYPESAFE_BY_RCU` or a constructor.
- `kmem_cache_destroy()` waits for cache-related deferred frees before shutdown: `kvfree_rcu_barrier_on_cache()`, optional `rcu_barrier()` for `SLAB_TYPESAFE_BY_RCU` debug frees, and `defer_free_barrier()`.
- Cache destroy decrements merged-cache refcounts under `slab_mutex`; only the final reference performs KASAN shutdown, allocator shutdown, list removal, sysfs/debugfs unlink, and final release.
- If `__kmem_cache_shutdown()` reports remaining objects, the cache is unlinked from allocator lists but not released, avoiding freeing live allocator metadata.
- Kmalloc cache creation builds normal, reclaim, memcg, DMA, and optional randomized kmalloc cache arrays, with architecture/DMA alignment possibly redirecting smaller indices to larger aligned caches.
- With memcg enabled, normal kmalloc caches are marked `SLAB_NO_MERGE`; memcg-specific caches are skipped/aliased when kernel memory accounting is disabled.
- `kmalloc_size_roundup()` reports the actual bucket object size for slab-backed allocations, page-order rounding for larger kmalloc allocations, and preserves zero or too-large requests.
- `/proc/slabinfo` is available under `CONFIG_SLUB_DEBUG`; iteration is serialized by `slab_mutex` and reports active objects, total objects, object size, slabs, tunables, and slabdata.
- `dump_unreclaimable_slab()` uses `mutex_trylock()` to avoid blocking badly in OOM paths and prints non-reclaimable cache usage only if it can safely traverse the cache list.
- `kfree_sensitive()` zeroes the full allocated buffer returned by `ksize()`, not just the originally requested size, then frees it.
- The BPF helper `bpf_get_kmem_cache()` validates the address, resolves its slab with `virt_to_slab()`, and returns the associated cache if present.

Batched `kvfree_rcu()` behavior:
- When batching is disabled, `kvfree_call_rcu()` either queues a normal `call_rcu()` callback or synchronously waits for a grace period for the one-argument/headless form.
- When batching is enabled, each CPU owns a `kfree_rcu_cpu` with bulk pointer pages, fallback `rcu_head` lists, two RCU work batches, delayed monitor work, and a small page cache for bulk nodes.
- The batched implementation has three channels: slab-pointer bulk frees, vmalloc-pointer bulk frees, and fallback linked-list frees through embedded `rcu_head`.
- Bulk nodes store pointers plus RCU grace-period snapshots; reclamation checks `poll_state_synchronize_rcu_full()` before freeing.
- Slab bulk frees use `kfree_bulk()`, vmalloc bulk frees call `vfree()` per record, and fallback list frees recover the original pointer from `head->func`.
- The allocator first tries `kfree_rcu_sheaf()` for same-NUMA slab objects when allowed, then records pointers into per-CPU bulk nodes, then falls back to embedded-head lists, then finally synchronously frees only for headless calls that cannot be queued.
- The monitor work drains already-ready objects directly, queues RCU work for the rest, and rearms itself when current batches are still busy.
- `kvfree_rcu_barrier()` flushes RCU sheaves, forces per-CPU pending objects into work batches, waits for monitor work, and flushes all per-CPU RCU work.
- `kvfree_rcu_barrier_on_cache()` additionally flushes cache-specific sheaves before falling back to the global batched barrier.
- The `slab-kvfree-rcu` shrinker counts queued objects plus cached bulk pages, backs off page-cache refill during pressure, drains cached pages, and invokes monitor reclaim work.

Dependencies:
- Uses core slab interfaces from `internal.h` and `slab.h`, allocator-specific hooks such as `do_kmem_cache_create()`, `__kmem_cache_shutdown()`, `__kmem_cache_shrink()`, `get_slabinfo()`, and cache release callbacks.
- Integrates with KASAN, KFENCE, kmemleak, stack depot, hardened usercopy, debug objects, SLUB debug, sysfs, debugfs, procfs, tracepoints, and BPF/BTF kfunc support.
- Relies on RCU internals, `rcu_work`, grace-period snapshot APIs, shrinkers, workqueues, hrtimers, per-CPU data, raw spinlocks, local IRQ control, and `kfree_bulk()`/`vfree()` backends.
- Depends on architecture and DMA alignment helpers, DMA bounce/SWIOTLB state, memcg kernel memory accounting, NUMA node checks, and kmalloc index/size conventions.
- Exports public APIs and symbols used across the kernel: cache sizing/creation/destruction/shrink, kmalloc cache arrays, sensitive free, slab object diagnostics, tracepoints, and RCU-deferred free barriers.

Notable risks:
- Cache merging changes object layout expectations; merge exclusion flags must include every feature that adds per-object metadata or alters usercopy/freelist semantics.
- Updating `object_size` and `inuse` on merged aliases is necessary for zeroing correctness, but it also means later aliases can affect shared cache metadata.
- Destroy sequencing is subtle because cache lifetime intersects with merged refcounts, KASAN quarantine, deferred no-lock frees, RCU-deferred frees, sysfs/debugfs lifetime, and `SLAB_TYPESAFE_BY_RCU` grace periods.
- `kmem_cache_destroy()` can intentionally leave an unlinked cache unreleased when objects remain; callers that assume immediate destruction can leak cache state until the underlying bug is fixed.
- Boot cache creation uses negative refcounts to prevent early merging, then later kmalloc cache setup transitions caches into normal use.
- Architecture alignment changes can alias multiple kmalloc indices to one larger cache, which affects internal fragmentation and bucket expectations.
- The batched `kvfree_rcu()` path is concurrency-heavy: correctness depends on per-CPU locking, grace-period snapshots, debug-object queue/unqueue state, workqueue flushing, and fallback behavior under memory pressure.
- Headless `kvfree_rcu()` is restricted to sleepable context because its fallback may call `synchronize_rcu()` inline.
- The bulk-node page cache trades allocation avoidance for memory retention; the shrinker and backoff flags are important under reclaim pressure.
- `kmem_dump_obj()` and BPF cache lookup depend on virtual-address validity and slab metadata still being meaningful, so they are diagnostic aids rather than general object lifetime proofs.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/slab_common.c -->