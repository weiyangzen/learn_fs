<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_mmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_mmu.c

## Purpose
Controls Mali MMU IP blocks for GP and PP pipes: initialization, IRQ fault handling, TLB flush, VM switching, and page-fault recovery.

## Important APIs, types, and functions
Exports `lima_mmu_init()`, `lima_mmu_fini()`, `lima_mmu_resume()`, `lima_mmu_suspend()`, `lima_mmu_flush_tlb()`, `lima_mmu_switch_vm()`, and `lima_mmu_page_fault_resume()`. The `lima_mmu_send_command()` macro writes commands and polls completion/status conditions. IRQ handler is `lima_mmu_irq_handler()`.

## Control flow
Init skips the PP MMU broadcast pseudo-IP, write-tests DTE address masking, registers a shared IRQ, hard-resets the MMU, masks page-fault and bus-error interrupts, installs the empty VM page directory, and enables paging. IRQ logs page faults or bus errors, masks all MMU interrupts, clears status, and notifies the GP or PP scheduler pipe. VM switching stalls the MMU, writes the new page directory, zaps TLB, and disables stall. Page-fault resume hard-resets a fault-active MMU and reinstalls the empty VM.

## State and persistence
MMU state is mostly hardware: DTE page directory address, paging enabled, stall active, interrupt mask/status, and TLB contents. The empty VM belongs to `lima_device`; active VM is selected by scheduler task execution.

## Dependencies and integration points
Depends on Lima VM page-directory DMA, scheduler MMU error callbacks, shared platform IRQs, and MMU register definitions. Device init creates per-processor MMU IPs and optional broadcast MMU pseudo-IP.

## Risks
Fault handling masks interrupts until recovery, so recovery paths must run. VM switch command timeouts can leave the MMU stalled or using the wrong page table. Shared IRQ handling must return `IRQ_NONE` for unrelated interrupts. DTE write test assumes hardware masks low bits to page alignment.

## Test signals
Valid job VM switches, synthetic page faults, read bus errors, TLB flushes, MMU IRQ sharing, page-fault resume, and suspend/resume validate this file. Logs include fault address, bus ID, access type, and command timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_mmu.c -->
