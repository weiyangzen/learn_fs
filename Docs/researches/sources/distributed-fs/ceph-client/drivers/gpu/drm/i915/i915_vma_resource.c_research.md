# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma_resource.c

Purpose: implements refcounted snapshots of VMA binding data so unbind operations can be fenced, deferred, and ordered independently from the live `struct i915_vma`.

Important APIs/functions: exports `i915_vma_resource_alloc/free`, `i915_vma_resource_hold/unhold`, `i915_vma_resource_unbind`, `__i915_vma_resource_init`, `i915_vma_resource_bind_dep_sync`, `i915_vma_resource_bind_dep_await`, `i915_vma_resource_bind_dep_sync_all`, and module init/exit. Internal pieces include `unbind_fence_ops`, `i915_vma_resource_unbind_work`, the software-fence notifier, and an interval tree keyed by unbind range including guard pages.

Control flow: binding initializes a resource snapshot. Unbind publishes `unbind_fence`, optionally takes a wakeref, inserts delayed work into the VM pending-unbind interval tree when dependencies remain, and commits the software fence. When dependencies complete, work rewrites PTEs unless skipped, signals the unbind fence after hold count reaches zero, removes the interval-tree node under `vm->mutex`, releases wakeref and refcounted SG tables, and frees via RCU.

State and persistence: state is volatile kernel memory in a slab cache. The important persistent-in-flight state is `hold_count`, `chain`, `unbind_fence`, `rb`, `vm`, `wakeref`, `bi.pages_rsgt`, range fields, `skip_pte_rewrite`, `immediate_unbind`, and optional TLB pointer.

Dependencies and integration: depends on `i915_sw_fence`, dma fences, interval trees, runtime PM, `i915_vma_ops`, VM `pending_unbind`, and memory-region SG table references. VMA bind paths call the dependency helpers to avoid rebinding over ranges whose PTE teardown is still pending.

Risks: waiting on pending unbinds while holding `vm->mutex` can deadlock worker removal paths, hence `sync_all` deliberately releases the mutex. Interval bounds include cache-color guard expansion; errors there can allow overlapping bind/unbind. Signaling occurs in dma-fence critical paths, so allocations and wakeref acquisition are constrained.

Test signals: exercised by VMA async unbind tests, VM destruction, bind-after-evict workloads, lockdep/prove-locking checks in hold/unhold, and slab module init/exit failure paths.
