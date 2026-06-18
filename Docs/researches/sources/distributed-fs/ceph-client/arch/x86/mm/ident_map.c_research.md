# sources/distributed-fs/ceph-client/arch/x86/mm/ident_map.c

## Purpose
Builds and frees identity-mapping page tables for the compressed and regular x86 kernel.

## Important APIs, Types, And Functions
Public functions are `kernel_ident_mapping_init()` and `kernel_ident_mapping_free()`. Internal helpers allocate/populate/free P4D, PUD, PMD, and PTE levels using callbacks in `struct x86_mapping_info`.

## Control Flow
Mapping initialization adds `info->offset` to the requested physical range, defaults and masks page-table flags, walks PGD/P4D/PUD/PMD levels, allocates missing tables through `info->alloc_pgt_page()`, optionally uses 1 GiB PUD leaf mappings when allowed and range-aligned, and otherwise creates PMD leaf mappings. Freeing recurses through present non-leaf entries and calls `info->free_pgt_page()`.

## State And Persistence
Mutates caller-provided page-table pages. Allocation/free ownership is delegated to `x86_mapping_info` callbacks and context.

## Dependencies And Integration Points
Used during early boot, decompression, kexec, or other identity-map setup paths. Depends on page-table folding, `__pa()`, page-table flags, 5-level paging detection, and PTI shadow suppression via `_PAGE_NOPTISHADOW`.

## Risks
Leaf mapping selection must never overwrite existing mappings or map beyond requested boundaries. Offset arithmetic and folded P4D/PGD behavior are subtle. Allocation failure must stop cleanly without leaking partially allocated tables to callers that free them.

## Test Signals
Identity-map creation for aligned/unaligned ranges, overlapping existing mappings, 4-level and 5-level paging, direct 1 GiB mappings, PMD mappings, allocation failure injection, and free of mixed leaf/non-leaf trees.
