# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mremap_dontunmap.c

## Purpose

`mremap_dontunmap.c` validates `MREMAP_DONTUNMAP`: page tables move to a destination while the source virtual range remains mapped and faults back to zero pages or, for shmem, still observes backing contents.

## Important APIs, Types, and Functions

The program uses `mremap(MREMAP_DONTUNMAP | MREMAP_MAYMOVE)`, `MREMAP_FIXED`, `memfd_create()`, `ftruncate()`, `mmap()`, and `munmap()`. Helpers are `kernel_support_for_mremap_dontunmap()`, `check_region_contains_byte()`, `mremap_dontunmap_simple()`, `mremap_dontunmap_simple_shmem()`, `mremap_dontunmap_simple_fixed()`, `mremap_dontunmap_partial_mapping()`, and `mremap_dontunmap_partial_mapping_overwrite()`.

## Control Flow

`main()` probes support using a one-page `PROT_NONE` move and exits finished if unsupported. It allocates a page-sized comparison buffer, then runs five cases: simple anonymous move, shared memfd move, fixed-destination overwrite, partial source-range move, and fixed partial overwrite into the beginning of a larger destination.

## State and Persistence Behavior

Mappings are transient. Anonymous source PTEs are expected to be removed after move, causing zero-filled faults on source reads. Shared memfd source still reads original contents because the backing object remains. The global `page_buffer` is used for page-by-page memcmp expectations.

## Dependencies and Integration Points

It depends on `MREMAP_DONTUNMAP`, `memfd_create`, and Linux mm remap behavior. It integrates with page-table movement, fixed remap overwrite semantics, anonymous faulting, and shmem backing behavior.

## Risks and Edge Cases

The shmem case silently returns without a pass result if an older kernel rejects shared `MREMAP_DONTUNMAP` with `EINVAL`, even though the plan is fixed at five. Pointer arithmetic on `void *` relies on GNU extensions. Failure paths dump process maps.

## Test Signals

Success requires destination bytes matching moved source data, anonymous source ranges reading as zero after PTE removal, shmem source retaining data, and untouched destination tail bytes surviving fixed partial overwrite.
