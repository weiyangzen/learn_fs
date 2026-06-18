<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/mm/fault.c

## Purpose
Handles OpenRISC page faults, including user faults, kernel faults with exception-table fixups, stack growth, vmalloc page table synchronization, OOM/SIGBUS/SIGSEGV paths, and executable permission checks.

## Important APIs, Types, And Functions
Global `current_pgd[NR_CPUS]` tracks active top-level page tables for low-level handlers. `do_page_fault()` is the main handler. Macros define TLB entry count and address offset helpers.

## Control Flow
Kernel vmalloc faults can copy top-level mappings from `init_mm` without taking locks. User faults enable IRQs, find/expand VMA, validate write/read/execute permissions, call `handle_mm_fault()`, process retry/completed/error results, and signal or die as needed. Kernel faults search exception tables before Oops.

## State And Persistence
May expand VMAs, populate page tables, update current faulting task state, and synchronize `current_pgd` mappings for vmalloc. Signals persist to task pending signal state.

## Dependencies And Integration Points
Called from `entry.S`. Depends on `mmu_context`, exception tables, perf fault events, signal delivery, and vmalloc global mappings.

## Risks
The kernel IRQ reenable test uses `if (regs->sr && (SPR_SR_IEE | SPR_SR_TEE))`, which is broad rather than masking explicitly. Vmalloc fault synchronization assumes two-level page table behavior. Execute permission check uses OpenRISC page-prot bits directly.

## Test Signals
User read/write/exec faults, stack growth, kernel usercopy fixups, vmalloc faults, OOM fault handling, SIGBUS mappings, and SMP current_pgd behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/fault.c -->
