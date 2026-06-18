## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gpu.h

### Purpose
`etnaviv_gpu.h` declares the GPU-facing data model and public interfaces shared across Etnaviv submit, scheduler, MMU, perfmon, dump, and platform code.

### Important APIs, Types, And Functions
Key types are `struct etnaviv_chip_identity`, `enum etnaviv_sec_mode`, `struct etnaviv_event`, `enum etnaviv_gpu_state`, and `struct etnaviv_gpu`. Inline register helpers are `gpu_write()`, `gpu_read()`, `gpu_fix_power_address()`, `gpu_write_power()`, and `gpu_read_power()`. The header declares lifecycle, debugfs, submit, recovery, fence wait, object wait, idle wait, and FE-start APIs.

### Control Flow
The header does not implement control flow beyond MMIO helpers. `gpu_read()` performs an extra read for FE register ranges to work around inconsistent reads on some variants. Power-register helpers remap PM register offsets for old GC300 revisions before read/write.

### State, Persistence, And Dependencies
`struct etnaviv_gpu` persists all per-device mutable state: DRM device pointer, workqueue, scheduler, command buffer, events, fences, MMU context, hangcheck fields, MMIO base, IRQ, clocks, reset, and frequency scaling. It depends on Etnaviv command buffer, GEM, MMU, DRM driver structures, and generated common/state register definitions.

### Integration Points
Every Etnaviv GPU submodule includes this header to access identity, locking, events, fences, and MMIO accessors. The exported `etnaviv_gpu_driver` is the platform-driver symbol used by the wider DRM module.

### Risks
Incorrect register helper semantics affect every hardware path. The event count is fixed at `ETNA_NR_EVENTS` and must match hardware event vector usage. Shared structure fields are protected by different locks (`lock`, `sched_lock`, spinlocks), so new callers must respect existing lock ownership.

### Test Signals
Compile coverage across MMU, scheduler, submit, and perfmon catches declaration drift. Runtime signals include FE register reads on affected cores, GC300 power-register access, event bitmap bounds, and lockdep assertions around fields guarded by `gpu->lock`.
