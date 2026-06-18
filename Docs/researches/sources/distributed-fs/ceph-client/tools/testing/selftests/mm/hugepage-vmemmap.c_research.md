# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-vmemmap.c

## Purpose
`hugepage-vmemmap.c` verifies that hugetlb pages expose correct compound head/tail flags through `/proc/kpageflags`, including when hugetlb vmemmap optimization is enabled.

## Important APIs, types, and functions
The test maps one default hugepage with `MAP_HUGETLB`, writes into it, translates a virtual address to a PFN using `/proc/self/pagemap` in `virt_to_pfn()`, and checks `/proc/kpageflags` in `check_page_flags()`. It expects the first base page to include `PAGE_COMPOUND_HEAD | PAGE_HUGE` and subsequent base pages to include `PAGE_COMPOUND_TAIL | PAGE_HUGE` without head flags.

## Control flow
`main()` determines base and huge page sizes, maps one anonymous private hugepage, writes bytes to trigger allocation, resolves the PFN, verifies head/tail flags for all base pages in the hugepage, unmaps with hugepage-aligned length, and exits.

## State and persistence behavior
Only a private anonymous hugepage mapping is allocated and released. The test reads procfs kernel accounting but does not mutate persistent sysctls.

## Dependencies and integration points
Requires enough default hugepages and permission to read `/proc/self/pagemap` and `/proc/kpageflags`, which may be restricted on hardened systems. It uses `vm_util.h` for page-size helpers.

## Risks and edge cases
PFN visibility may be masked for unprivileged users. Hugepage pool exhaustion fails `mmap()`. Kernel flag definitions must match the tested kernel.

## Test signals
Success is a valid PFN plus expected head flag on the first base page and tail flags on every subsequent base page.
