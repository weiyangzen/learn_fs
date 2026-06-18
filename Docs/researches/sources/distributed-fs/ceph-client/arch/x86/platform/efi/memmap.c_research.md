<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/memmap.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/memmap.c

## Purpose
`memmap.c` contains common EFI memory-map allocation, replacement, splitting, and insertion helpers used by x86 EFI setup and later memory-map modifications. It abstracts early memblock allocation versus late page allocation and updates EFI descriptors around inserted attribute ranges.

## Important APIs, types, and functions
Important functions are `efi_memmap_alloc()`, `efi_memmap_install()`, `efi_memmap_split_count()`, and `efi_memmap_insert()`. Internal helpers allocate via `memblock_phys_alloc()` or `alloc_pages()` and free through memblock or page allocator based on map flags.

## Control flow
`efi_memmap_alloc()` computes size from entry count and current descriptor size/version, selects slab/page allocation when available or memblock early allocation otherwise, records allocation flags, and returns a physical map address. `efi_memmap_install()` unmaps the current map, initializes the new map using existing mapping mode, and frees the old storage unless EFI paravirtual mode bypasses replacement. Split/count and insert helpers determine how many descriptors are needed when a target range bisects existing descriptors, then copy and split descriptors while OR-ing requested attributes into covered portions.

## State and persistence behavior
The helpers update `struct efi_memory_map_data` and, through `efi_memmap_install()`, replace global `efi.memmap`. Allocation flags encode whether old storage is freed through memblock or normal pages. Inserted maps preserve descriptor size/version and only alter descriptor ranges/attributes.

## Dependencies and integration points
It depends on generic EFI memmap internals, memblock, page allocator, early/late mapping functions, EFI page alignment, and callers such as EFI quirks, runtime virtual-mode setup, and memory reservation code.

## Risks and edge cases
Inserted ranges must be EFI-page aligned; otherwise the function warns and returns. Buffer sizing must include all possible split descriptors, normally computed by `efi_memmap_split_count()`. `efi_memmap_install()` intentionally does not switch early/late mapping modes, so callers must pass compatible data.

## Test signals
EFI memmap replacement during boot, adding attributes that split descriptors into two or three pieces, late allocation after slab availability, paravirtual EFI bypass, and leak/failure checks on allocation or install errors are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/memmap.c -->
