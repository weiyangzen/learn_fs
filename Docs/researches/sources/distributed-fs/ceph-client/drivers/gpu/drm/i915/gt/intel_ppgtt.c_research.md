<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ppgtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ppgtt.c

Purpose: implements shared PPGTT page-table allocation/free helpers, page-directory entry updates, PPGTT creation dispatch, VMA bind/unbind wrappers, page-table stash preallocation/mapping, and base PPGTT initialization.

Important APIs and functions: `alloc_pt()`, `__alloc_pd()`, `alloc_pd()`, and `free_px()` manage page-table/page-directory structures and backing GEM objects. `__set_pd_entry()`, `clear_pd_entry()`, and `release_pd_entry()` write DMA PDE entries and manage use counts. `i915_ppgtt_init_hw()` programs GTT workarounds and enables Gen6/Gen7 PPGTT hardware. `i915_ppgtt_create()` dispatches to Gen6 or Gen8 implementations. `ppgtt_bind_vma()` and `ppgtt_unbind_vma()` implement generic VMA operations using VM callbacks. `i915_vm_alloc_pt_stash()`, `i915_vm_map_pt_stash()`, and `i915_vm_free_pt_stash()` prepare fail-safe page-table allocations. `ppgtt_init()` initializes the common VM fields.

Control flow: page-table allocation creates a wrapper, allocates a VM-specific DMA object, and initializes use counts. Binding ensures the VMA range is allocated once via `vm->allocate_va_range()`, derives PTE flags from read-only and LMEM backing, inserts entries, and issues a write memory barrier. Unbind clears the range only if allocated and invalidates TLB state. Stash allocation computes how many PT/PD objects a range may need at each level, allocates them into two linked lists, maps them under object locks, and frees unused/failed stash entries.

State and persistence: page tables keep an atomic `used` count and a `base` GEM object. Page directories own an entry pointer array and spinlock. VMA resources remember whether page tables have been allocated. The PPGTT VM persists total size, DMA device, LMEM page-table flags, and bind/unbind function pointers.

Dependencies and integration points: depends on GEM LMEM/internal object allocation through VM callbacks, Gen6/Gen8 PPGTT backends, `intel_gtt.h` helper types, tracepoints, and GT hardware init. Used by normal PPGTTs and the migration PPGTT.

Risks: PDE updates must flush CPU cache lines for GPU page walkers. `release_pd_entry()` has a concurrent use-count path protected by spinlock only at the final drop; incorrect atomic ordering can double-free or leak page tables. Stash sizing intentionally overestimates for later misalignment; underestimation would introduce allocation failures in non-failing bind sections. `ppgtt_unbind_vma()` does not clear `allocated`, so page-table allocation state remains for reuse.

Test signals: PPGTT selftests, bind/unbind under memory pressure, page-table stash fault injection, Gen6/Gen8 backend creation tests, TLB invalidation validation, migration VM setup, and concurrent bind/unbind stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ppgtt.c -->
