# sources/distributed-fs/ceph-client/mm/pgalloc-track.h

## Purpose
`pgalloc-track.h` provides small inline wrappers around page-table allocation helpers that also record which upper-level page-table entries were modified. It is used by walkers or mapping code that need to allocate missing page-table levels and later know whether PGD, P4D, PUD, or PMD entries changed.

## Important APIs, Types, and Functions
The header defines `p4d_alloc_track()`, `pud_alloc_track()`, `pmd_alloc_track()`, and the `pte_alloc_kernel_track()` macro. The functions accept an `mm_struct`, the parent page-table pointer, an address, and a `pgtbl_mod_mask *`. When a missing parent entry is allocated by `__p4d_alloc()`, `__pud_alloc()`, or `__pmd_alloc()`, the wrapper ORs the corresponding `PGTBL_*_MODIFIED` bit into the supplied mask before returning the normal child pointer.

`pte_alloc_kernel_track()` performs the same role for kernel PTE tables: when the PMD is none and `__pte_alloc_kernel()` succeeds, it sets `PGTBL_PMD_MODIFIED`; then it returns `pte_offset_kernel()`. The upper-level helpers are present only under `CONFIG_MMU`; the kernel-PTE macro is defined unconditionally by the header.

## Control Flow
Each helper is a straight-line allocate-if-missing wrapper. It checks whether the parent entry is none, calls the underlying allocator, returns `NULL` on allocation failure, records the modification bit on success, and returns the child table offset for the requested address. No table is allocated and no mask bit is set when the parent entry is already present.

## State and Persistence Behavior
The header owns no state. Persistent effects are the page-table pages installed by the underlying allocation helpers and the caller-owned modification mask. The mask is transient but important to callers that defer cache/TLB synchronization, accounting, or validation until after page-table walking.

## Dependencies and Integration Points
The wrapper depends on core MM page-table types and allocation routines declared by Linux MM headers. It integrates with page-table modification paths that need source-level visibility into which levels changed, commonly code that maps kernel or user ranges through generic page-table walking helpers.

## Risks and Edge Cases
The main risk is mask accuracy. Callers may skip required follow-up work if a wrapper allocates a table but fails to set the right bit. The `pte_alloc_kernel_track()` macro is compact and relies on side effects in a conditional expression, so maintenance changes must preserve short-circuit behavior: failed allocation must return `NULL`, successful allocation must set `PGTBL_PMD_MODIFIED`, and existing PMDs must not set the mask. The helper assumes the caller supplies a valid mask pointer.

## Test Signals
Compile coverage under folded and unfolded page-table configurations is the primary signal. Runtime validation should exercise mapping code that allocates every page-table level from empty parents, verifies the returned child pointers are usable, checks modification-mask bits, and confirms no bits are set when walking already-populated tables. Allocation-failure injection should verify `NULL` return without bogus mask updates.
