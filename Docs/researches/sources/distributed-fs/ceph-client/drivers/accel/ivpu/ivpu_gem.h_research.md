## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_gem.h

### Purpose
`ivpu_gem.h` defines the ivpu buffer-object structure and declares BO/GEM creation, binding, ioctl, and diagnostic helpers.

### Important APIs, Types, And Functions
`struct ivpu_bo` embeds `drm_gem_shmem_object`, tracks the owning MMU context, BO list node, VPU VA `drm_mm_node`, flags, job status, context ID, and MMU-mapped state. Inline helpers convert GEM to ivpu BO, get CPU VADDR/size/cache mode/device, determine snooping/read-only/resident/mappable state, and convert between CPU and VPU addresses within a BO.

### Control Flow
The inline address conversion helpers validate that the address lies within the BO range before returning a translated pointer/address. Snooping depends on global forced snoop or cached BO mode.

### State, Persistence, And Dependencies
The structure persists for each GEM object until final put. It depends on DRM GEM shmem, DRM MM, ivpu driver structures, and UAPI flags.

### Integration Points
Every firmware, IPC, job, and memory path that allocates or translates device-visible memory uses this header.

### Risks
`cpu_to_vpu_addr()` returns `u32`, so callers must be aware of address ranges and truncation expectations. `ivpu_bo_vaddr()` is valid only for vmapped/mappable BOs. `job_status` is meaningful only for command buffers.

### Test Signals
Compile and runtime tests should verify address conversion boundaries, cache/snoop flag behavior, read-only mapping propagation, BO residency status, and safe use of unmapped BO virtual addresses.
