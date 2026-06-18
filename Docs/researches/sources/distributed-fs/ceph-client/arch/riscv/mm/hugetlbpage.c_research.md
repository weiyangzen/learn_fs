<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/hugetlbpage.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/hugetlbpage.c

## Purpose
`hugetlbpage.c` implements RISC-V hugepage support, including Svnapot contiguous PTE mappings when available.

## Important APIs, Types, And Functions
It defines huge PTE lookup/allocation, NAPOT-aware get/clear/set/protect/access flag operations, hugepage valid-size checks, hstate registration, migration support, and CMA order selection.

## Control Flow
Allocation walks pgd/p4d/pud/pmd levels, using PUD/PMD huge mappings or pte-level NAPOT mappings. NAPOT updates use break-before-make: clear all contiguous PTEs, flush the covered range, then install new PTEs. Access flag and write-protect paths merge dirty/young bits from all contiguous entries before rewriting.

## State And Persistence
State is page-table entries and registered hugetlb hstates. Runtime hugepage mappings persist in process page tables; no disk persistence exists.

## Dependencies And Integration Points
It depends on hugetlb core, Svnapot feature detection, RISC-V PTE helpers, TLB flush APIs, huge PMD/PUD sharing, migration, and CMA configuration.

## Risks
NAPOT contiguity requires every PTE in the range to remain consistent. Missing break-before-make can violate the privileged spec. Valid-size logic must match hardware and compiled page-table levels.

## Test Signals
Hugetlb selftests, NAPOT hugepage mapping tests, dirty/young tracking, migration, fork/COW, and gigantic page allocation tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/hugetlbpage.c -->
