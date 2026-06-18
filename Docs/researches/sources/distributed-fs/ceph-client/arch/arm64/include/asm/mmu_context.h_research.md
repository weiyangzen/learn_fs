# sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu_context.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu_context.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu_context.h

### Purpose
`mmu_context.h` implements ARM64 address-space activation, ASID allocation hooks, TCR programming, TTBR switching, CnP behavior, reserved TTBR0 handling, and PAN/UAO-related context helpers.

### Important APIs, Types, And Functions
Important exports include context init/destroy/switch helpers, `cpu_set_reserved_ttbr0()`, `cpu_switch_mm()`, `cpu_replace_ttbr1()`, `init_new_context()`, `destroy_context()`, `activate_mm()`, `switch_mm()`, TCR/TTBR helpers, and ASID generation interfaces.

### Control Flow
On context switch, ARM64 selects or allocates an ASID, writes TTBR/TCR state, performs required barriers, and may install reserved TTBR0 when no userspace table should be active. Exec/fork paths initialize or destroy per-mm context.

### State, Persistence, And Dependencies
State persists in `mm_context_t`, CPU-local active context, ASID allocator state, TTBR registers, and TLBs. It depends on `mmu.h`, `pgtable.h`, CPU capabilities, barriers, and scheduler/MM core.

### Integration Points
Used by scheduler, process creation/destruction, page faults, KPTI, PAN, and any subsystem that switches between user address spaces.

### Risks
Missing barriers around TTBR/TCR updates can expose stale translations. ASID rollover and CnP are concurrency sensitive. Reserved TTBR0 mistakes can expose user mappings in kernel context.

### Test Signals
Run context-switch stress, ASID rollover, KPTI/PAN tests, fork/exec workloads, CPU hotplug, and TLB invalidation selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu_context.h -->
