# sources/distributed-fs/ceph-client/arch/arc/mm/mmap.c

Purpose: provides ARC-specific mmap placement and page protection mapping.

Important APIs/functions: `arch_get_unmapped_area()` enforces shared mapping alignment for VIPT cache alias avoidance. `protection_map` maps Linux `VM_*` access combinations to ARC user PTE protections and is exported through `DECLARE_VM_GET_PAGE_PROT`.

Control flow: fixed mappings are accepted only if shared mappings satisfy `SHMLBA` alignment relative to file offset. Non-fixed requests validate size, try a caller-specified aligned address if available, then call `vm_unmapped_area()` with `align_offset = pgoff << PAGE_SHIFT`.

State and persistence: no persistent state; reads `current->mm` and VMA layout.

Dependencies and integration: depends on generic mmap helpers, ARC cache aliasing constraints, and ARC PTE protection definitions.

Risks: wrong alignment can cause VIPT aliasing coherency bugs for shared mappings. Protection map choices intentionally make private writable mappings read-only until fault/COW handling; changing them affects mm semantics.

Test signals: mmap alignment tests for `MAP_SHARED`, `MAP_FIXED` rejection, randomized mmap placement, executable/writable protection checks, and cache aliasing stress on VIPT systems.
