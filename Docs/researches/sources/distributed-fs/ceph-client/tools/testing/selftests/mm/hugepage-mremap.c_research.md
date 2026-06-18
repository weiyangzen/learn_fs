# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-mremap.c

## Purpose
`hugepage-mremap.c` verifies remapping hugetlb memory with `mremap()`, including a fixed remap over a dummy mapping and interaction with userfaultfd registration. It targets PMD sharing/unshare paths when large sizes are requested.

## Important APIs, types, and functions
The file uses `memfd_create(MFD_HUGETLB)`, `mmap(MAP_HUGETLB | MAP_SHARED | MAP_POPULATE)`, `mremap(MREMAP_MAYMOVE | MREMAP_FIXED)`, `userfaultfd`, `UFFDIO_API`, and `uffd_register()`. Pattern helpers mirror `hugepage-mmap.c`. `register_region_with_uffd()` creates a userfaultfd object, creates and registers an anonymous mapping for missing-page tracking, and skips on permission or unsupported kernels.

## Control flow
`main()` parses an optional length in MiB, maps a hugetlb region at a suggested PUD-aligned address, maps a second dummy hugetlb region to encourage PMD sharing, maps an anonymous destination range, registers userfaultfd-related memory, remaps the original hugetlb mapping to the destination, writes and verifies data, unmaps it, then asserts that a later `mremap()` on the unmapped address fails.

## State and persistence behavior
The test creates transient hugetlb and anonymous mappings and a hugetlb memfd. It deliberately replaces the destination mapping with the remapped hugetlb mapping. No state persists after close/unmap.

## Dependencies and integration points
The test depends on hugetlb availability, userfaultfd permission/configuration, and local `vm_util.h` userfaultfd helpers. It is integrated as a hugetlb/mremap regression test in the MM selftest suite.

## Risks and edge cases
Suggested fixed addresses may not be honored if unavailable, and insufficient hugepages can fail early. The helper's `addr` parameter is overwritten by its own mmap, so userfaultfd registration is best understood as auxiliary coverage rather than registration of `haddr` itself. Userfaultfd restrictions commonly produce skips.

## Test signals
Pass signals are successful fixed remap, intact byte pattern after remap, and expected failure when remapping an already-unmapped region.
