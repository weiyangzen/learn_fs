<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu.c

### Purpose
`ivpu_mmu.c` programs and services the VPU SMMU-like MMU block. It allocates context descriptor, stream table, command queue, and event queue memory; resets/enables the MMU; installs context descriptors; invalidates TLBs; and handles MMU event and global-error interrupts.

### Important APIs, Types, And Functions
Public APIs are `ivpu_mmu_init()`, `ivpu_mmu_enable()`, `ivpu_mmu_disable()`, `ivpu_mmu_cd_set()`, `ivpu_mmu_cd_clear()`, `ivpu_mmu_invalidate_tlb()`, `ivpu_mmu_irq_evtq_handler()`, `ivpu_mmu_irq_gerr_handler()`, `ivpu_mmu_evtq_dump()`, `ivpu_mmu_discard_events()`, and `ivpu_mmu_disable_ssid_events()`. Key internal helpers allocate the CDTAB/STRTAB/CMDQ/EVTQ, write CR0/IRQ control registers, enqueue MMU commands (`CFGI_ALL`, `TLBI_NH_ASID`, `TLBI_NSNH_ALL`, `SYNC`), link stream table entries to the CD table, and translate event/error codes to strings.

### Control Flow
Initialization checks hardware ID registers, initializes the MMU mutex, allocates coherent tables/queues, links stream IDs 0 and 3 to the context descriptor table, then enables the MMU. Enable resets command/event queues, disables CR0, writes cache/shareability and table/queue base registers, enables command queue, invalidates configuration and TLBs, enables event queue and ATS checking, enables MMU interrupts, then sets SMMU enable. Context descriptor changes write CD table entries, flush cache when needed, and issue CFGI/SYNC if the MMU is on. Event IRQ handling drains EVTQ entries, maps SSIDs to `file_priv`, marks contexts with `has_mmu_faults`, sets `faults_detected`, and queues context abort work; global or reserved context faults trigger PM recovery.

### State, Persistence, And Dependencies
MMU state is in `vdev->mmu`: coherent tables, queues, producer/consumer indices, a lock, and `on`. Hardware register state persists until power/reset. Dependencies include register IO macros, DMA coherent memory, cache flushing when force snoop is disabled, `ivpu_mmu_context` page table roots, `vdev->context_xa`, PM recovery, hardware diagnostics, and VPU address-space constants.

### Integration Points
`ivpu_mmu_context.c` calls CD set/clear and TLB invalidation after map/unmap/protection changes. PM calls enable/disable around resume/suspend. Job/context abort logic calls `ivpu_mmu_disable_ssid_events()` and `ivpu_mmu_discard_events()`. Interrupt handlers call the EVTQ and GERROR paths from the hardware IRQ layer.

### Risks
Register sequencing and queue synchronization are fragile. A missed write memory barrier or cache flush can make the MMU consume stale commands or descriptors. Bounds checks use `ssid > IVPU_MMU_CDTAB_ENT_COUNT`, which allows `ssid == count` even though valid indices are normally `0..count-1`; callers should not pass out-of-range SSIDs. `ivpu_mmu_disable_ssid_events()` ignores return values from command queue writes/sync, so fault-event suppression failures may be only indirectly visible. Any event queue desynchronization can block new MMU interrupts until events are discarded.

### Test Signals
Test with boot/resume MMU enable, context map/unmap followed by successful firmware access, TLB invalidation after remap and read-only changes, injected user-context faults causing only that context to abort, injected global/reserved faults causing recovery, GERROR interrupt logging, suspend/resume cycles, force-snoop on/off paths, and stress submissions that churn context descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu.c -->
