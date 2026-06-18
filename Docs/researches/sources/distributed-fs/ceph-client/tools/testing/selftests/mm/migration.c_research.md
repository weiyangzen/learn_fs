# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/migration.c

## Purpose

`migration.c` stress-tests page migration entries by moving pages between NUMA nodes while other threads or processes continuously access the same memory. It covers private/shared anonymous pages, THPs, and hugetlb pages.

## Important APIs, Types, and Functions

The fixture records worker thread/process arrays, available task CPUs, and two NUMA nodes. `migrate()` loops for `RUNTIME` seconds calling `move_pages(..., MPOL_MF_MOVE_ALL)` and alternates target nodes. `access_mem()` repeatedly performs a forced read and cancellation point. Test cases use `pthread_create()`, `fork()`, `prctl(PR_SET_PDEATHSIG)`, `madvise(MADV_HUGEPAGE)`, and `MAP_HUGETLB`.

## Control Flow

Fixture setup locates at least two NUMA nodes and allocates worker arrays. Each test maps a 2 MiB region, initializes it, starts concurrent access from threads for private mappings or forked processes for shared mappings, runs `migrate()` between nodes, then cancels threads or kills child processes. THP tests align the address and request huge pages; hugetlb tests use `MAP_HUGETLB`.

## State and Persistence Behavior

State is transient mapped memory and live worker tasks. `move_pages()` changes physical NUMA placement of pages. Child processes use `PR_SET_PDEATHSIG` to reduce orphan risk. The mappings are not explicitly unmapped in each test body, relying on process teardown.

## Dependencies and Integration Points

It depends on libnuma, multiple NUMA nodes, sufficient CPUs, optional transparent hugepage support, and hugetlb reservations for hugetlb cases. It integrates with kernel migration entry wait paths at PTE and PMD levels.

## Risks and Edge Cases

Migration is best-effort; `migrate()` tolerates up to `MAX_RETRIES` positive failures before failing. Systems without enough NUMA nodes/threads skip. Hugetlb allocation failures are hard assertion failures. Long runtime and concurrent readers make this intentionally stress-oriented and timing-sensitive.

## Test Signals

Each case passes if repeated migration succeeds for the runtime while concurrent access continues without faulting or hanging. Harness timeouts are set to twice the migration runtime.
