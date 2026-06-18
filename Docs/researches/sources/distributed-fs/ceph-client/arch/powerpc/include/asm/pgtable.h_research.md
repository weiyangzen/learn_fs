<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable.h

## Purpose
This top-level PowerPC pgtable header selects MMU-family page-table definitions and exposes generic architecture hooks for page protections, PTE access, and memory-management integration.

## Important APIs, Types, And Functions
It includes page and type headers, selects Book3S or nohash pgtable backends, and supplies common wrappers/macros used by generic MM such as page protection transforms, PTE/PFN conversions, pgd/p4d/pud/pmd walking helpers, cacheability helpers, and architecture feature declarations. The exact exported surface depends heavily on Book3S vs nohash and 32-bit vs 64-bit configuration.

## Control Flow
Most behavior is inline and configuration-selected. Generic MM code enters this header's helpers during page faults, mmap/mprotect, swap, unmap, IO remapping, and TLB/cache maintenance.

## State And Persistence Behavior
It owns little direct state but defines how VMAs and page tables encode persistent protections, PFNs, swap entries, and hardware-specific status bits.

## Dependencies And Integration Points
It integrates the PowerPC MMU family headers with Linux generic MM. It depends on page geometry, pgtable type definitions, cache/TLB helpers, and backend-specific Book3S/nohash files.

## Risks And Edge Cases
Because it is a selector and aggregation point, Kconfig combinations can expose conflicting helpers. Backend-specific permission, hugepage, and endian semantics must remain isolated behind common generic-MM names.

## Test Signals
Cross-build representative Book3S hash/radix and nohash configs, run MM selftests, page-table debug, swap, hugeTLB, mprotect, IO remap, and cache/TLB coherency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable.h -->
