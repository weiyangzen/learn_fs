<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dpt.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dpt.c

### Purpose
`i915_dpt.c` implements i915 display page tables (DPT) as a specialized `i915_address_space` backed by a GEM object. It allocates the page-table object, writes gen8 PTEs into an iomapped GGTT pin, binds display VMAs into the DPT, and exposes lifecycle callbacks to shared display code.

### Important APIs, Types, And Functions
The key type is private `struct intel_dpt`, embedding `struct i915_address_space` plus the backing GEM object, GGTT VMA, and iomem pointer. Public functions are `i915_dpt_to_vm()`, `i915_dpt_pin_to_ggtt()`, `i915_dpt_unpin_from_ggtt()`, `i915_dpt_offset()`, and `i915_display_dpt_interface`. Internal helpers include `i915_vm_to_dpt()`, `dpt_insert_page()`, `dpt_insert_entries()`, `dpt_clear_range()`, `dpt_bind_vma()`, `dpt_unbind_vma()`, `dpt_cleanup()`, `i915_dpt_create()`, `i915_dpt_destroy()`, `i915_dpt_suspend()`, and `i915_dpt_resume()`.

### Control Flow
Creation sizes the DPT object from the target object size or explicit page count, allocates contiguous LMEM first, stolen memory if GGTT aperture exists, or shmem on non-LMEM platforms, sets cache level to uncached, initializes an address space with DPT class and GGTT PTE encoder, and marks the object as DPT. Pinning takes runtime PM, increments pending framebuffer pin accounting, locks the object with ww retry handling, pins it into GGTT, maps it with `i915_vma_pin_iomap()`, stores the VMA/iomem, marks the object dirty, and drops PM/accounting refs. Binding writes PTEs for VMA backing pages and marks both global and local bind flags because DPT has one PTE space. Destroy clears `is_dpt` and drops the VM reference; cleanup drops the object ref.

### State, Persistence, And Dependencies
Persistent DPT state includes the embedded VM, backing object, pinned VMA, iomap pointer, `vm->total`, DPT flag, PTE encoder, bind/unbind ops, and object `is_dpt` marker. Dependencies include GEM internal/LMEM/stolen/shmem allocation, GGTT pin/iomap helpers, i915 address-space init, gen8 PPGTT definitions, display restore pending pin accounting, runtime PM, and suspend/resume GGTT VM helpers.

### Integration Points
Shared display DPT code calls `i915_display_dpt_interface.create/destroy/suspend/resume`. Framebuffer/display code pins DPTs to GGTT, obtains offsets for hardware programming, and unpins them during teardown. Debugfs object description treats DPT VMAs as a distinct VMA type.

### Risks
`dpt_clear_range()` is empty, so unbind does not scrub PTEs; correctness depends on DPT lifetime and rebind behavior. PTE_READ_ONLY is ignored in `dpt_insert_entries()` with a warning that callers must not let users override read-only access. Pin/unpin balance for both iomap and VMA refs is critical. Allocation fallback changes memory domain and cache behavior. The DPT object is marked dirty after pinning because display hardware reads it.

### Test Signals
Tests should cover LMEM, stolen, and shmem allocation fallback; cache-level failure unwind; GGTT pin/iomap failure unwind; bind entries with LMEM/read-only flags; DPT offset reporting; suspend/resume callbacks; pin/unpin reference balance; and display scanout using DPT-backed framebuffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dpt.c -->
