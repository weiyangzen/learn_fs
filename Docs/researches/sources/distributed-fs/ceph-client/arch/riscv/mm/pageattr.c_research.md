<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/pageattr.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/pageattr.c

## Purpose
`pageattr.c` implements RISC-V kernel page attribute changes, including set_memory APIs, direct-map validity changes, huge linear mapping splitting, and page presence queries.

## Important APIs, Types, And Functions
`struct pageattr_masks` carries set/clear masks. Walk callbacks update P4D/PUD/PMD/PTE leaves. `split_linear_mapping()` and helpers split huge mappings down to smaller tables when partial permission changes are needed. Public APIs include `set_memory_rw_nx`, `set_memory_ro`, `set_memory_rw`, `set_memory_x`, `set_memory_nx`, direct-map helpers, debug pagealloc mapping, and `kernel_page_present()`.

## Control Flow
`__set_memory()` builds masks, locks `init_mm`, translates vmalloc/module pages to linear aliases when needed, splits linear huge mappings for the affected physical pages, walks page tables to apply masks on both aliases, unlocks, and flushes either all TLBs on 64-bit or the specific range on 32-bit.

## State And Persistence
It mutates kernel page-table entries and direct-map present/permission bits. Effects persist until changed again.

## Dependencies And Integration Points
It integrates with `set_memory` users, modules/BPF, STRICT_KERNEL_RWX, DEBUG_PAGEALLOC, vmalloc metadata, page table walking, and TLB flush APIs.

## Risks
Kernel and linear aliases must stay permission-consistent. Splitting huge mappings requires memory allocation and barriers before publishing tables. Full TLB flushes are used because split mappings can exceed requested ranges.

## Test Signals
Module text permission tests, BPF JIT permission transitions, debug pagealloc, strict RWX checks, `kernel_page_present()` tests, and vmalloc alias tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/pageattr.c -->
