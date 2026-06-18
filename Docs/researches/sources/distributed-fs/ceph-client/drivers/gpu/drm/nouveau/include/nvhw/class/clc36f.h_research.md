<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc36f.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc36f.h

Purpose: `clc36f.h` defines the `NVC36F` channel-control class used on GV100-class hardware for non-stall interrupts, memory operations, TLB invalidation/replay cancel, access-counter clearing, and modern semaphore execution.

Important APIs and types: `MEM_OP_A` and `MEM_OP_B` carry targeted TLB invalidation address and replay-cancel target fields. `MEM_OP_C` carries membar type, PDB selection, GPC enable, replay action, ack type, access type or page-table level, PDB aperture/address, and access-counter notify tag fields. `MEM_OP_D` selects the operation: membar, MMU TLB invalidate, targeted invalidate, L2 peer/sysmem invalidate, comptag clean, dirty flush, wait for sys pending reads, or access-counter clear. Semaphore methods use low/high address, low/high payload, and `SEM_EXECUTE` for acquire/release/reduction, TSG switching, WFI, 32/64-bit payload, timestamp, and reduction format.

Control flow: `gv100_fence.c` emits semaphore releases/acquires using `SEM_ADDR_*`, `SEM_PAYLOAD_LO`, and `SEM_EXECUTE`. The fence emit path follows release with a system membar via `MEM_OP_A` through `MEM_OP_D`, then emits `NON_STALL_INTERRUPT`. `nvif/chanc36f.c` uses the memory operation fields for channel-level memory barriers and invalidations.

State and persistence: semaphore release persists fence payloads in memory; acquire waits on persisted memory values. MEM_OP methods cause ordering/cache/MMU side effects rather than persistent software state. TLB and L2 invalidation state affects subsequent GPU memory translations and cache visibility.

Dependencies and integration: included by `gv100_fence.c` and `nvif/chanc36f.c`, with push helpers and Nouveau fence/channel abstractions. It supersedes older `NV906F` semaphore layout for newer GPUs.

Risks: comments explicitly note `MEM_OP_A/B` changed in GP100 and old functionality moved to `MEM_OP_C/D`; mixing generations can produce invalid TLB operations. Targeted invalidation fields are overloaded depending on replay mode, PDB mode, and access type. Missing the required A-C writes before `MEM_OP_D` can make operations use stale operands. Incorrect semaphore payload size or WFI flag can break fence ordering.

Test signals: GV100+ fence emit/sync, channel memory barrier tests, UVM/HMM invalidation paths, replay-cancel scenarios, and access-counter clearing. Runtime regressions include stalled fences, stale page translations, replay storms, non-stall interrupt failures, or GPU faults during memory migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc36f.h -->
