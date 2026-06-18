# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma_resource.h

Purpose: defines the VMA resource snapshot ABI shared by VMA bind/unbind code and GTT backend operations.

Important APIs/types: defines `struct i915_page_sizes`, `struct i915_vma_bindinfo`, and `struct i915_vma_resource`; declares allocation, refcount, hold/unhold, unbind, dependency sync/await, and module lifecycle functions. Inline helpers wrap dma-fence references and initialize/finalize resource snapshots.

Control flow: callers allocate first, initialize under the VM lock with immutable bind data, pass to backend `bind_vma`, and later publish unbind. `i915_vma_resource_init()` copies pages, page-size metadata, readonly/lmem bits, region, ops, private data, address range, and guard size; it also optionally takes a reference on `pages_rsgt` for async-capable backing storage.

State and persistence: all fields represent in-flight kernel state, not disk state. `bi` can be discarded after bind, while range, ops, fence, and TLB fields persist until unbind completion. Under error-capture builds it also records the memory region.

Dependencies and integration: integrates with dma-fence, `i915_sw_fence`, runtime PM, i915 scatterlist reference counting, VM address spaces, and backend `i915_vma_ops`. The header is included by both VMA implementation and page-table backends.

Risks: `vm` is explicitly non-refcounted and cleared after unbind, so users must respect fence/resource lifetime. `i915_vma_resource_fini()` assumes a single hold remains. Missing `pages_rsgt` disables safe async object-destruction support.

Test signals: compile-time users validate structure layout. Runtime coverage comes from async unbind, capture-error, and selftest paths that initialize resources from live VMAs.
