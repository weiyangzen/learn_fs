# sources/distributed-fs/ceph-client/include/linux/mmu_context.h

## Purpose
`mmu_context.h` provides generic wrappers and defaults around architecture MMU context handling. It includes architecture context headers and supplies fallbacks for IRQ-off MM switching, leaving an mm, task CPU masks, pointer untagging masks, and page-table DMA compatibility.

## Important APIs, Types, And Functions
Important defaults are `switch_mm_irqs_off` aliasing `switch_mm`, no-op `leave_mm()`, `task_cpu_possible_mask()`, `task_cpu_possible()`, `task_cpu_fallback_mask()`, `mm_untag_mask()`, and `arch_pgtable_dma_compat()`. Architectures can override these before including or through their `asm/mmu_context.h`/`asm/mmu.h`.

## Control Flow And State
The header itself stores no state. Scheduler and architecture code call `switch_mm_irqs_off()` when interrupts are disabled if an architecture needs a distinct implementation. CPU placement code uses task CPU possible/fallback masks for heterogeneous systems. `mm_untag_mask()` supplies an address-mask default for architectures without tagged user pointers, and `arch_pgtable_dma_compat()` defaults to permitting DMA compatibility.

## Dependencies And Integration Points
Dependencies are architecture `mmu_context.h` and `mmu.h`. Integration points include scheduler context switching, TLB/MMU context loading, CPU hotplug and heterogeneous CPU placement, housekeeping CPU fallback, tagged-address architectures, and DMA/IOMMU checks involving page tables.

## Risks And Test Signals
Risks include architecture fallbacks being too permissive, switching an mm with incorrect IRQ assumptions, wrong possible CPU masks on heterogeneous systems, failure to clear pointer tags, and DMA incompatibility hidden by the default true return. Test signals include architecture builds, context-switch stress, CPU hotplug and affinity tests, tagged-pointer syscall/MM tests, and DMA mapping tests on architectures with special page-table constraints.
