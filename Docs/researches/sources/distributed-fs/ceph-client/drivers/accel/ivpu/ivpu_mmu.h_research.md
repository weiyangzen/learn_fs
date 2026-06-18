<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu.h

### Purpose
`ivpu_mmu.h` defines MMU management state and the driver-internal API for MMU lifecycle, context descriptor installation, TLB invalidation, and interrupt handling.

### Important APIs, Types, And Functions
`struct ivpu_mmu_cdtab`, `struct ivpu_mmu_strtab`, and `struct ivpu_mmu_queue` describe coherent MMU resources. `struct ivpu_mmu_info` groups these resources with the mutex and `on` flag. Exported functions cover init/enable/disable, CD set/clear, TLB invalidation, EVTQ/GERROR interrupt service, event dump/discard, and per-SSID event suppression.

### Control Flow
The header has no executable flow. Its API is called during device init/resume/suspend, BO mapping, context teardown, and IRQ processing.

### State, Persistence, And Dependencies
The state structure is owned by `struct ivpu_device`. It depends on DMA addresses, mutexes, and `struct ivpu_mmu_pgtable` from the context layer.

### Integration Points
`ivpu_mmu_context.c`, PM, IRQ, and job recovery are the principal consumers. The `on` flag gates invalidation and descriptor updates while the device is suspended.

### Risks
Callers must respect the MMU lock and runtime state. Adding fields to `ivpu_mmu_info` requires careful initialization because the MMU is active across runtime PM transitions.

### Test Signals
Compile and runtime signals include clean init/fini, no lockdep warnings during map/unmap/interrupt paths, correct MMU re-enable after resume, and successful fault recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu.h -->
