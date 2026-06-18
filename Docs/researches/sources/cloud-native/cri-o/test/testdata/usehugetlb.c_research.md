<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/usehugetlb.c -->
# sources/cloud-native/cri-o/test/testdata/usehugetlb.c

Purpose: C helper for tests that need a process holding a huge page.

Important flow: registers a SIGTERM handler, mmaps one 2 MiB anonymous private huge page with `MAP_HUGETLB`, sleeps for 100 seconds, then unmaps during cleanup. On mmap or unmap failure it prints an error and exits nonzero.

State and integration: consumes host huge page resources while running and releases them on normal termination/SIGTERM. Risks include requiring configured huge pages and privileges/cgroup allowances, simplistic signal handling, and `NULL` fd argument style for `mmap`. Test signal is resource accounting or hugetlb cgroup behavior while the process is alive.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/usehugetlb.c -->
