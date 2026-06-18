<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/kasan_init.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/kasan_init.c

## Purpose
`kasan_init.c` builds RISC-V KASAN shadow mappings from early boot through final swapper page tables.

## Important APIs, Types, And Functions
It defines early temporary page-table roots and helpers to populate pgd/p4d/pud/pmd/pte levels, clear early shadow entries, shallow-populate vmalloc/module shadow, create a temporary mapping, `kasan_early_init()`, `kasan_swapper_init()`, `kasan_populate_early_vm_area_shadow()`, and `kasan_init()`.

## Control Flow
Early init maps the entire KASAN shadow to shared early shadow pages at all enabled page-table levels. Swapper init mirrors this into final page tables. Final `kasan_init()` switches to a temporary page table, clears early shadow for the KASAN range, populates fixmap/vmalloc/modules/linear/kernel shadow ranges with real pages or shallow page tables, makes the early shadow page read-only, restores swapper SATP, flushes TLBs, and calls generic KASAN init.

## State And Persistence
Runtime state is KASAN shadow page-table mappings and initialized shadow memory. Temporary pgd/p4d/pud arrays are boot-only.

## Dependencies And Integration Points
It depends on memblock allocation, RISC-V page-table level flags, fixmap, `pt_ops`, KASAN generic initialization, VMALLOC shadow support, module/BPF address ranges, and TLB flushes.

## Risks
KASAN shadow must live at a fixed address across Sv39/Sv48/Sv57. Shared page-table levels with kernel mapping require temporary copies before clearing. Incorrect shallow population can break vmalloc KASAN or leak writable early shadow pages.

## Test Signals
KASAN boot tests on Sv39/Sv48/Sv57, vmalloc KASAN tests, module/BPF allocation tests, and memory error detection selftests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/kasan_init.c -->
