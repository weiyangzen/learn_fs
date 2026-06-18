# Research: sources/distributed-fs/ceph-client/mm/slub.c

## Purpose

`slub.c` is the Linux SLUB allocator implementation in the Ceph client source tree snapshot. It is generic kernel memory-management infrastructure, not Ceph-specific logic. Ceph code depends on it indirectly through `kmalloc()`, `kfree()`, `kmem_cache_*()`, `kvmalloc()`, memcg accounting, RCU frees, and slab observability when allocating filesystem metadata, request objects, page-cache support structures, and network-client state.

The file implements allocation and freeing for slab caches with a low-overhead fast path based on per-CPU object arrays called sheaves, a per-NUMA-node sheaf exchange pool called a barn, and node-local partial slab lists for slower paths. It also owns slab object layout calculation, freelist hardening/randomization, debug redzones/poisoning/user tracking, memory-cgroup and allocation-profiling hooks, cache creation/bootstrap, CPU and memory hotplug handling, sysfs/debugfs exposure, and the public kmalloc/kfree/kvmalloc API family.

## Important APIs, Types, and Functions

Core local state and types:

- `struct slab` is the per-slab page metadata used through `page_slab()`, `slab_page()`, `slab_address()`, `slab->freelist`, `slab->inuse`, `slab->objects`, `slab->frozen`, `slab->slab_cache`, and `slab->obj_exts`.
- `struct kmem_cache` describes one slab cache: object size, object stride, freelist offset, alignment, order/object count (`s->oo`, `s->min`), flags, per-node metadata, per-CPU sheaves, constructor, usercopy bounds, stats, and sysfs/debugfs identity.
- `struct kmem_cache_node` contains the per-NUMA-node partial slab list, list lock, partial count, and, under debug, total slab/object counters and full-slab list.
- `struct slub_percpu_sheaves` contains the current CPU's `main`, `spare`, and `rcu_free` sheaves guarded by `local_trylock_t`.
- `struct slab_sheaf` is a variable-size array of object pointers used for fast batched allocation/freeing and for explicit prefill APIs.
- `struct node_barn` stores per-node lists of full and empty sheaves, guarded by a spinlock, to move object batches between CPUs without immediately touching slab partial lists.
- `enum stat_item` defines optional per-CPU SLUB stats such as fast/slow alloc/free, sheaf refill/flush, barn get/put, cmpxchg failures, and order fallback.
- `struct track` records allocation/free call site, stack depot handle, CPU, PID, and time for `SLAB_STORE_USER`.

Primary allocation APIs exported by this file:

- `kmem_cache_alloc_noprof()`, `kmem_cache_alloc_lru_noprof()`, and `kmem_cache_alloc_node_noprof()` allocate one object from a named cache, optionally with an LRU or NUMA node.
- `kmem_cache_alloc_bulk_noprof()` allocates many objects and prefers per-CPU sheaves before refilling from partial or new slabs.
- `kmem_cache_prefill_sheaf()`, `kmem_cache_refill_sheaf()`, `kmem_cache_alloc_from_sheaf_noprof()`, `kmem_cache_return_sheaf()`, and `kmem_cache_sheaf_size()` expose explicit sheaf-based batching to users such as the maple tree code.
- `__kmalloc_noprof()`, `__kmalloc_node_noprof()`, `__kmalloc_node_track_caller_noprof()`, `__kmalloc_cache_noprof()`, `__kmalloc_cache_node_noprof()`, `__kmalloc_large_noprof()`, and `__kmalloc_large_node_noprof()` implement the kmalloc family, including large allocations that bypass slab caches and use the page allocator directly.
- `kmalloc_nolock_noprof()` provides a restricted NMI/raw-spinlock-safe allocator for small kmalloc buckets on configurations that can update slab freelists without sleeping locks.
- `__kvmalloc_node_noprof()`, `kvrealloc_node_align_noprof()`, `kvfree()`, `kvfree_atomic()`, and `kvfree_sensitive()` implement kmalloc-with-vmalloc-fallback allocation and freeing.

Primary free APIs and helpers:

- `kmem_cache_free()`, `kmem_cache_free_bulk()`, `kfree()`, `kfree_nolock()`, `kvfree_rcu_cb()`, `free_large_kmalloc()`, and `___cache_free()` release slab, kmalloc, large kmalloc, KASAN, and RCU callback allocations.
- `slab_free()`, `slab_free_bulk()`, `free_to_pcs()`, `free_to_pcs_bulk()`, `__slab_free()`, and `free_to_partial_list()` are the central free paths after subsystem hooks and validation.
- `build_detached_freelist()` groups bulk-free objects by slab so one synchronized freelist update can free several objects.
- `__kfree_rcu_sheaf()`, `rcu_free_sheaf()`, `flush_rcu_sheaves_on_cache()`, and `flush_all_rcu_sheaves()` batch `kfree_rcu()` slab objects through per-CPU sheaves.

Cache creation, layout, and lifecycle APIs:

- `do_kmem_cache_create()` initializes one `kmem_cache`, applies debug flags, computes layout, initializes nodes, per-CPU sheaves, random freelists, stats, sysfs, and debugfs.
- `calculate_sizes()`, `calculate_order()`, `calc_slab_order()`, `calculate_sheaf_capacity()`, `init_kmem_cache_nodes()`, `init_percpu_sheaves()`, and `init_kmem_cache_node()` define object layout and per-cache runtime structures.
- `allocate_slab()`, `new_slab()`, `alloc_from_new_slab()`, `free_slab()`, `discard_slab()`, `__free_slab()`, `free_partial()`, `__kmem_cache_shutdown()`, `__kmem_cache_release()`, `__kmem_cache_empty()`, and `__kmem_cache_shrink()` manage slab page lifetime.
- `kmem_cache_init()` and `kmem_cache_init_late()` bootstrap the allocator, boot caches, kmalloc caches, randomization, CPU hotplug callbacks, and the per-CPU flush workqueue.

Debug, hardening, and observability APIs:

- Freelist storage is encoded by `freelist_ptr_encode()`, `freelist_ptr_decode()`, `get_freepointer()`, and `set_freepointer()`, with optional `CONFIG_SLAB_FREELIST_HARDENED` XOR obfuscation.
- Debug checking uses `check_slab()`, `check_object()`, `check_pad_bytes()`, `slab_pad_check()`, `on_freelist()`, `alloc_debug_processing()`, `free_debug_processing()`, `validate_slab_cache()`, `print_tracking()`, and `object_err()`.
- `kmem_cache_flags()` and `setup_slub_debug()` parse and apply `slab_debug=` / `slub_debug=` boot configuration.
- `sysfs_slab_add()`, `sysfs_slab_alias()`, `slab_sysfs_init()`, `slab_attr_show()`, and many `*_show`/`*_store` attribute handlers expose cache state and tunables under `/sys/kernel/slab`.
- `debugfs_slab_add()`, `slab_debugfs_show()`, and trace-file handlers expose allocation/free traces for caches with `SLAB_STORE_USER`.
- `get_slabinfo()` feeds `/proc/slabinfo` under debug builds.

## Control Flow

Normal single-object allocation starts in a public wrapper such as `kmem_cache_alloc_noprof()` or `__kmalloc_noprof()`. The kmalloc path maps the requested size to a kmalloc cache with `kmalloc_slab()`, while cache-specific paths already have `struct kmem_cache`. `slab_alloc_node()` then runs `slab_pre_alloc_hook()` for GFP masking, `might_alloc()`, and failslab injection; gives KFENCE a chance to satisfy the request; tries the per-CPU sheaf fast path; and falls back to the slow slab allocator if no object is available.

The per-CPU fast path is `alloc_from_pcs()`. It uses `local_trylock()` on `s->cpu_sheaves->lock`, consumes an object from `pcs->main`, and optionally verifies NUMA node locality. If the main sheaf is empty, `__pcs_replace_empty_main()` first swaps in a non-empty spare sheaf, then tries to exchange the empty main sheaf for a full sheaf in the current node's barn, and finally allocates/refills a sheaf from slab pages if GFP context allows. This keeps ordinary allocations away from the central node list lock.

The slow single-object path is `___slab_alloc()`. It first tries a partial slab on the requested or local node with `get_from_partial()`. On NUMA systems, `get_from_any_partial()` may search other nodes according to memory policy and `remote_node_defrag_ratio`. If no partial slab can satisfy the allocation, it calls `new_slab()` and `allocate_slab()` to obtain page allocator memory, initialize slab metadata, build the freelist, install slab object extensions, account VM state, and possibly randomize the freelist. Debug or `CONFIG_SLUB_TINY` caches allocate one object at a time under the node list lock; normal caches can allocate directly from the new slab freelist and place remaining objects on the partial list.

Post-allocation work is centralized in `slab_post_alloc_hook()`. It applies KASAN tags and optional zeroing, calls kmemleak/KMSAN/allocation-profiling hooks, and then charges memory cgroups through `memcg_slab_post_alloc_hook()`. For kmalloc, `kasan_kmalloc()` records the originally requested size after the slab allocation. If debug redzone/original-size tracking is enabled, `alloc_debug_processing()` and `set_orig_size()` preserve the request size and mark object redzones active.

Single-object freeing starts at `kmem_cache_free()` or `kfree()`. These functions derive the owning slab and cache, reject impossible cache mismatches in hardened/debug configurations, emit tracepoints, and call `slab_free()`. `slab_free()` runs memcg and allocation-tag free hooks, calls `slab_free_hook()` for kmemleak, KMSAN, debugobjects, KCSAN, KFENCE, KASAN quarantine, RCU debug delay, and optional init-on-free clearing, then tries to put the object into a per-CPU sheaf if the slab is local and not `pfmemalloc`.

The free fast path is `free_to_pcs()`. It pushes the object into the CPU's main sheaf. If the main sheaf is full, `__pcs_replace_full_main()` swaps with an empty spare, exchanges a full sheaf for an empty one in the node barn, allocates an empty sheaf, or flushes the full main sheaf as a last resort. If the object cannot use per-CPU sheaves, `__slab_free()` updates the slab freelist and counters using `try_cmpxchg_freelist()` when available or `slab_lock()` otherwise. It touches the node partial list only when a full slab becomes partial or a partial slab becomes empty enough to discard.

Bulk allocation and free follow the same concepts but batch aggressively. `kmem_cache_alloc_bulk_noprof()` consumes from per-CPU sheaves through `alloc_from_pcs_bulk()` and falls back to `__kmem_cache_alloc_bulk()`, which refills from partial slabs or new slabs. `kmem_cache_free_bulk()` either uses `free_to_pcs_bulk()` for sheaf-enabled caches or groups objects by slab with `build_detached_freelist()` and calls `slab_free_bulk()`.

Large kmalloc requests bypass the slab cache. `___kmalloc_large_node()` allocates frozen compound pages with `__GFP_COMP`, marks them `PageLargeKmalloc`, charges `NR_SLAB_UNRECLAIMABLE_B`, and applies KASAN/kmemleak/KMSAN hooks. `free_large_kmalloc()` validates the marker, removes hooks/accounting, clears the marker, and returns pages to the page allocator.

Cache creation flows through generic slab code into `do_kmem_cache_create()`. This file applies debug flags, initializes hardening randomness, copies constructor/usercopy/alignment inputs, computes object layout, enables cmpxchg-double fast mode when supported, computes minimum partial-slab retention, allocates per-CPU sheaves, initializes per-node metadata and barns, creates stats, and registers sysfs/debugfs after boot. Shutdown reverses this by flushing all CPU sheaves, waiting for RCU sheaves, shrinking barns, freeing empty partial slabs, and refusing destruction if live objects remain.

Boot flow is two-stage. `kmem_cache_init()` creates bootstrap `kmem_cache_node` and `kmem_cache` caches before ordinary kmalloc is available, bootstraps them into real caches, creates kmalloc caches, initializes kmalloc sheaves after kmalloc can allocate sheaf storage, initializes freelist randomization, and registers CPU hotplug callbacks. `kmem_cache_init_late()` creates the per-CPU flush workqueue and initializes random state for freelist randomization.

## State and Persistence Behavior

This file maintains volatile kernel memory allocator state only. It does not persist data to disk, but it strongly affects the lifetime and reuse of all slab-backed kernel objects, including objects used by Ceph and other filesystems.

Important runtime state includes:

- Per-cache geometry: `object_size`, `size`, `inuse`, `offset`, `align`, `red_left_pad`, `oo`, `min`, `min_partial`, `allocflags`, `sheaf_capacity`, and flags such as `SLAB_ACCOUNT`, `SLAB_TYPESAFE_BY_RCU`, `SLAB_RED_ZONE`, `SLAB_POISON`, `SLAB_STORE_USER`, `SLAB_KMALLOC`, `__CMPXCHG_DOUBLE`, and `SLAB_OBJ_EXT_IN_OBJ`.
- Per-slab state: page allocator order, `PageSlab`/`PageLargeKmalloc` flags, owning cache, encoded free object chain, object/in-use counters, frozen state, partial-list flag, pfmemalloc state, object extension pointer, and optional RCU callback state.
- Per-CPU state: active/spare/RCU sheaves for each cache, deferred NMI-safe free lists, per-CPU stats, and flush work items.
- Per-node state: partial slab lists, debug full slab lists, counts, and barn full/empty sheaf pools.
- Debug metadata stored beside objects: redzones, poison bytes, free pointers, allocation/free tracks, original kmalloc request size, KASAN metadata, and optional slab object extensions.
- Accounting and profiling state: VM node counters, memcg object extension vectors, allocation-profiling codetag references, kmemleak state, KMSAN/KASAN state, KFENCE allocations, and slabinfo/sysfs/debugfs counters.

State transitions are carefully constrained by locks and atomic updates. The per-CPU sheaf lock protects only that CPU's object-pointer arrays. The barn lock protects full/empty sheaf exchange lists. The node `list_lock` protects partial/full slab lists and counts. Slab freelist/counter updates use cmpxchg-double where supported or the slab bit lock otherwise. `slab_mutex` protects global cache-list and cache metadata changes, and CPU/memory hotplug callbacks synchronize with it.

Debug corruption handling can intentionally change persistence of objects. When consistency checks fail during allocation, `alloc_debug_processing()` marks the slab full and frozen, clears the freelist, and leaks existing objects instead of risking further freelist corruption. Hardened or debug `kmem_cache_free()` similarly leaks objects with invalid slab/cache ownership rather than freeing the wrong memory.

## Dependencies

This file depends on broad Linux MM, debugging, and architecture support:

- Page allocator and page metadata: frozen page allocation/freeing, compound order, page flags, node/page accounting, `page_slab()`, `virt_to_slab()`, `virt_to_page()`, and `page_to_nid()`.
- Core slab definitions from `slab.h` and `internal.h`: `struct kmem_cache`, kmalloc bucket tables, slab cache lists, cache creation glue, merge/unmerge rules, `cache_has_sheaves()`, slab object extension helpers, and shared slab APIs.
- Architecture atomic and locking primitives: `try_cmpxchg_freelist()`, `system_has_freelist_aba()`, bit spinlocks, local locks, spinlocks, IRQ save/restore, lockdep, wait-type overrides, and PREEMPT_RT constraints.
- NUMA and policy: `numa_mem_id()`, `numa_node_id()`, `mempolicy_slab_node()`, zonelists, cpusets, node masks, memoryless node handling, and `slab_strict_numa`.
- Memory checkers and debuggers: KASAN, KMSAN, KFENCE, kmemleak, debugobjects, KCSAN, stack depot, KUnit slab error tracking, failslab, and fault injection.
- Memory accounting: memcg slab accounting, `struct slabobj_ext`, allocation profiling codetags, VM node counters, and reclaim accounting.
- RCU and hotplug: `call_rcu()`, `rcu_barrier()`, `irq_work`, CPU hotplug state callbacks, memory hotplug notifiers, and workqueues.
- Observability and control: tracepoints under `trace/events/kmem.h`, sysfs/kobject/kset APIs, debugfs/seq_file, `/proc/slabinfo` integration in common slab code, boot/core parameters, and ratelimited printk warnings.

## Integration Points

The most important integration point is the public allocator API. Nearly all kernel subsystems, including the Ceph client, use `kmalloc`, `kfree`, `kmem_cache_create`, `kmem_cache_alloc`, `kmem_cache_free`, `kvmalloc`, and `kvfree` through declarations in `include/linux/slab.h`. This file supplies the concrete SLUB implementation behind those wrappers.

`slab_common.c` integrates with this file for generic cache creation, aliasing, destruction, `/proc/slabinfo`, RCU free batching, and sysfs/debugfs release. It calls `do_kmem_cache_create()`, `sysfs_slab_alias()`, `sysfs_slab_unlink()`, `sysfs_slab_release()`, `debugfs_slab_release()`, `get_slabinfo()`, `__kfree_rcu_sheaf()`, and `flush_all_rcu_sheaves()`.

Boot integration comes from `mm_init.c` and `init/main.c`, which call `kmem_cache_init()` and `kmem_cache_init_late()`. The allocator must be functional before most subsystems initialize, so bootstrap paths cannot assume ordinary kmalloc, sysfs, debugfs, or all hotplug machinery is available.

Maple tree code uses the explicit sheaf prefill API to batch node allocations. That API is unusual because callers receive a `struct slab_sheaf` and then draw guaranteed objects from it without falling back to the cache once it empties.

Filesystem and distributed-client relevance is indirect but critical. Ceph's inode, request, capability, snap, messenger, bio, and page-cache helper allocations eventually pass through these paths. SLUB memcg accounting, allocation failure behavior, `GFP_NOFS`/reclaim flags, init-on-free/init-on-alloc, KASAN/KFENCE, and node locality all affect how filesystem allocations behave under pressure.

The sysfs interface exposes cache layout and tunables such as `min_partial`, `remote_node_defrag_ratio`, `failslab`, `skip_kfence`, `shrink`, and validation triggers. Debugfs allocation/free traces integrate with `SLAB_STORE_USER` and stack depot to identify leak and churn sites.

## Risks and Edge Cases

The most important correctness risk is synchronization between three caching layers: per-CPU sheaves, per-node barns, and slab partial lists. Objects can move between them during allocation, free, CPU hotplug, RCU callback execution, shrink, or cache shutdown. Missing a flush, returning a sheaf to the wrong node, or racing a list transition can hide live objects or expose freed objects.

Freelist/counter updates are subtle. The lockless path must atomically update `slab->freelist` and packed counters; the fallback path must disable interrupts or rely on PREEMPT_RT rules while using `slab_lock()`. Partial-list manipulation must happen only for full-to-partial and partial-to-empty transitions, and frozen/corrupt slabs must stay out of normal list management.

Debug features change object layout and fast-path eligibility. Redzones, poisoning, store-user tracking, KASAN metadata, original-size storage, and slab object extensions all alter `s->inuse`, `s->offset`, `s->size`, and mergeability. Regressions here can produce false corruption reports, real buffer overrun masking, or incompatible cache merging.

`kmalloc_nolock()` and `kfree_nolock()` have strict context limits. They intentionally skip some hooks and are unsupported for large kmalloc or architectures/configurations needing sleeping or preemptible locks. Misusing them for ordinary kmalloc objects can confuse kmemleak/KFENCE bookkeeping; using them on unsupported contexts can fail without retry semantics.

RCU and `SLAB_TYPESAFE_BY_RCU` paths are easy to break. `slab_free_hook()` may delay reuse for RCU debug or KASAN quarantine; `__kfree_rcu_sheaf()` batches frees and must coordinate with `flush_all_rcu_sheaves()` so barriers do not miss pending objects. `SLAB_TYPESAFE_BY_RCU` slabs may defer page freeing with `call_rcu()`.

Memcg and allocation profiling object extensions can recurse into kmalloc. The code masks GFP bits, uses `__GFP_NO_OBJ_EXT`, avoids storing extension vectors in their own cache, and may place extensions in leftover slab space or inside object padding. Errors can leak slabs, lose accounting, or report inaccurate allocation tags.

NUMA behavior trades locality against fragmentation. Remote partial-slab defragmentation, memoryless nodes, cpuset/mempolicy changes, per-node barns, and strict NUMA static keys all influence where objects come from. Fast paths assume sheaves are mostly local and verify only in some node-requested cases.

Bootstrapping has little margin for failure. Early `kmem_cache_node` and `kmem_cache` creation happens before normal allocation infrastructure is available; kmalloc sheaves are enabled only after kmalloc caches exist. Failures after partial setup require careful unwind through `__kmem_cache_release()`.

Observability paths can be expensive or racy by design. Sysfs counts scan partial/full lists under locks and sometimes approximate large lists. Debug validation flushes CPU sheaves first and then walks slabs; this is useful for diagnostics but can perturb allocator state and performance.

## Test Signals

Useful validation signals for this file include:

- Boot and early init: successful boot through `kmem_cache_init()` and `kmem_cache_init_late()`, presence of kmalloc caches, correct SLUB boot log line, and no panic in `bootstrap_kmalloc_sheaves()`.
- Generic allocator coverage: `kmalloc`/`kfree`, `kmem_cache_alloc`/`kmem_cache_free`, node-specific allocation, zero-size allocation, large kmalloc, `kvmalloc` fallback, `krealloc`/`kvrealloc`, bulk alloc/free, and explicit sheaf users such as maple tree.
- Memory pressure: slab allocation failure, order fallback, reclaimable/unreclaimable slab counters, `slab_out_of_memory()` warnings, `kmem_cache_shrink()`, cache destruction with live objects, and empty partial-slab discard.
- Concurrency: heavy multi-CPU allocation/free churn, CPU hotplug flushes, memory hotplug add/remove, remote frees across NUMA nodes, barn exchange contention, cmpxchg-double failure stats, and PREEMPT_RT lock-context coverage.
- Debug/hardening: boot with `slab_debug=FZPU`, redzone overrun detection, poison validation, double-free detection, invalid cache free warnings, store-user stack traces, KUnit slab error counting, failslab injection, and freelist randomization/hardening enabled.
- Sanitizers and instrumentation: KASAN quarantine and invalid-free reports, KMSAN initialization behavior, KFENCE allocation/free interception, kmemleak tracking, KCSAN access assertions, debugobjects checks, and allocation profiling codetag accounting.
- Memcg: charged `SLAB_ACCOUNT` caches, post-allocation charge failure rollback, obj_ext allocation failure, cgroup slab stats, and slab extension cleanup during slab free.
- RCU: `kfree_rcu()` stress, `kvfree_rcu_barrier()`, `flush_all_rcu_sheaves()`, `SLAB_TYPESAFE_BY_RCU` cache teardown, and `CONFIG_SLUB_RCU_DEBUG` delayed reuse.
- Observability: `/sys/kernel/slab/<cache>/` attributes, stat reset via writing `0`, `validate` and `shrink` stores, `remote_node_defrag_ratio`, debugfs `alloc_traces`/`free_traces`, `/proc/slabinfo`, and kmem tracepoints.
- Filesystem-facing workloads: Ceph or network-filesystem mount/use under memory pressure, metadata-heavy directory operations, mmap/page-cache workloads, reclaim paths using `GFP_NOFS`, and teardown while slab debug, memcg, and sanitizers are enabled.
