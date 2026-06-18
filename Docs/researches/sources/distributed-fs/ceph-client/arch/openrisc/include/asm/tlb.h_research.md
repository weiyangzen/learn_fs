<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/tlb.h

## Purpose
Adapts generic Linux TLB gather code for OpenRISC.

## Important APIs, Types, And Functions
Includes `linux/pagemap.h` and `asm-generic/tlb.h`. The comment records that OpenRISC lacks an efficient `flush_tlb_range()`, so broad mm flushes are preferred in generic gathering.

## Control Flow
No local code. Generic mmu_gather paths use this header when freeing page tables and unmapping memory.

## State And Persistence
No state. TLB state is controlled by `tlbflush.h` and `mm/tlb.c`.

## Dependencies And Integration Points
Integrates OpenRISC with generic memory-management page-table teardown.

## Risks
Performance risk from broad flushes. Correctness depends on the OpenRISC flush implementations invalidating both data and instruction TLB entries.

## Test Signals
Page unmap/remap tests, mmap/munmap stress, and TLB shootdown behavior under SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/tlb.h -->
