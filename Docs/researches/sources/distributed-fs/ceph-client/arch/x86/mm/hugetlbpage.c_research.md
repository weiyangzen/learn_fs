# sources/distributed-fs/ceph-client/arch/x86/mm/hugetlbpage.c

## Purpose
Provides x86 architecture hooks for HugeTLB page-size validation and CMA order selection.

## Important APIs, Types, And Functions
On x86-64, `arch_hugetlb_valid_size()` accepts PMD-sized huge pages and PUD-sized huge pages when `X86_FEATURE_GBPAGES` is present. With contiguous allocation, `gigantic_pages_init()` registers the PUD-sized hstate. `arch_hugetlb_cma_order()` returns the gigantic-page order when supported.

## Control Flow
Feature checks gate 1 GiB huge-page support. The initcall adds the gigantic hstate at arch init time when runtime allocation is possible.

## State And Persistence
Mutates HugeTLB global hstate registration during init. No per-page state is directly managed here.

## Dependencies And Integration Points
Integrates HugeTLB core with x86 page-table levels and CPU feature discovery. Depends on `hugetlb_add_hstate()` and `boot_cpu_has()`.

## Risks
Incorrect size validation could expose unsupported mappings. 1 GiB support must follow hardware capability and allocation configuration.

## Test Signals
Boot and HugeTLB tests with/without `X86_FEATURE_GBPAGES`, PMD and PUD huge-page reservation/allocation, CMA order selection, and 32-bit build coverage.
