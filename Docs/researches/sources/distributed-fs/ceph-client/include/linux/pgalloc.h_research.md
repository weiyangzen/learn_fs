<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pgalloc.h -->
# sources/distributed-fs/ceph-client/include/linux/pgalloc.h

## Purpose
Provides generic page-table allocation include glue and fallback population macros for kernel page-table levels.

## Important APIs, Types, And Functions
- Includes `<linux/pgtable.h>` and architecture `<asm/pgalloc.h>`.
- `pgd_populate_kernel(addr, pgd, p4d)` defaults to `pgd_populate(&init_mm, pgd, p4d)` when the architecture does not define it.
- `p4d_populate_kernel(addr, p4d, pud)` defaults to `p4d_populate(&init_mm, p4d, pud)` when not defined.

## Control Flow
Architecture or generic MM code includes this header and calls the kernel population helpers while constructing kernel page tables. The fallback helpers route through `init_mm`; architectures can override them when address-aware population is needed.

## State And Persistence
State is page-table hierarchy state in kernel memory, typically under `init_mm` for kernel mappings. This header introduces no independent storage.

## Dependencies And Integration Points
Integrates generic memory-management code with architecture page-table allocators and page-table population routines. It depends on `init_mm`, `pgd_populate()`, and `p4d_populate()` being available from included MM headers.

## Risks And Edge Cases
Risks include using fallback helpers on architectures that require address-specific handling, incorrect page-table level folding assumptions, and modifying kernel mappings without proper synchronization/TLB maintenance in callers.

## Test Signals
Build architectures with and without custom `*_populate_kernel`, boot with folded and non-folded page-table levels, exercise vmalloc/ioremap/kernel mapping setup, and run page-table debug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pgalloc.h -->
