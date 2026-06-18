<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu.h -->
# sources/distributed-fs/ceph-client/include/linux/percpu.h

## Purpose
Defines the generic per-CPU allocator interface, first-chunk setup data structures, allocation sizing constants, and helpers for translating per-CPU addresses.

## Important APIs, Types, And Functions
- Allocation sizing constants include `PERCPU_MODULE_RESERVE`, `PCPU_MIN_UNIT_SIZE`, `PCPU_MIN_ALLOC_SHIFT`, `PCPU_MIN_ALLOC_SIZE`, `PCPU_BITMAP_BLOCK_SIZE`, `PERCPU_DYNAMIC_SIZE_SHIFT`, `PERCPU_DYNAMIC_EARLY_SIZE`, and `PERCPU_DYNAMIC_RESERVE`.
- Global state declarations: `pcpu_base_addr`, `pcpu_unit_offsets`, `pcpu_chosen_fc`, and `pcpu_fc_names`.
- Topology/setup structures: `struct pcpu_group_info`, `struct pcpu_alloc_info`, and `enum pcpu_fc` for auto/embed/page first chunk modes.
- Boot setup APIs: `pcpu_alloc_alloc_info()`, `pcpu_free_alloc_info()`, `pcpu_setup_first_chunk()`, `pcpu_embed_first_chunk()`, optional `pcpu_populate_pte()`, `pcpu_page_first_chunk()`, and `setup_per_cpu_areas()`.
- Dynamic allocation APIs/macros: `pcpu_alloc_noprof()`, `__alloc_percpu_gfp()`, `__alloc_percpu()`, `__alloc_reserved_percpu()`, `alloc_percpu_gfp()`, `alloc_percpu()`, `alloc_percpu_noprof()`, and `free_percpu()`.
- Address helpers include `per_cpu_ptr_to_phys()`, `pcpu_nr_pages()`, `__is_kernel_percpu_address()`, and `is_kernel_percpu_address()`.

## Control Flow
Early boot builds a `pcpu_alloc_info`, chooses a first-chunk mode, lays out per-CPU units, and calls `pcpu_setup_first_chunk()`. Runtime callers allocate per-CPU objects with type-safe macros, use per-CPU accessors from lower-level headers, and release memory with `free_percpu()`. Allocation hooks wrap profiled allocation paths unless `noprof` is explicitly used.

## State And Persistence
Persistent state includes the per-CPU base address, unit offsets, first chunk, dynamic allocation metadata, reserved module/dynamic areas, and topology grouping. Allocated per-CPU objects persist until freed and have one instance per CPU/unit.

## Dependencies And Integration Points
Includes allocation tagging, memory debug, preemption, SMP, PFN helpers, init, cleanup, scheduler, and architecture percpu definitions. It integrates with slab bootstrap, module loading, CPU hotplug, NUMA-aware placement, and memory profiling.

## Risks And Edge Cases
Risks include under-sizing early dynamic reserve, unit size/alignment errors, incorrect CPU-to-node or CPU-distance callbacks, freeing invalid percpu pointers, using normal pointers for percpu memory, and first-chunk mode incompatibilities with architecture mappings or large-page assumptions.

## Test Signals
Boot on UP/SMP/NUMA, embedded and page first-chunk modes, module percpu allocations, early allocations before slab init, CPU hotplug, `is_kernel_percpu_address()` checks, allocation/free leak detection, and memory profiling/tagging coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu.h -->
