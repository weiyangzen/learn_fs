<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/base.c

## Purpose
Implements common instance-memory object lifecycle, save/restore, allocation wrapper, zeroing fallback, boot object separation, and subdev init/fini/suspend/resume plumbing.

## Important APIs, Types, And Functions
Important APIs include nvkm_instobj_load/save/dtor/ctor/wrap/new, nvkm_instmem_rd32/wr32/boot, nvkm_instmem_fini/init/oneinit/dtor, and nvkm_instmem_ctor.

## Control Flow
instobj_save allocates a suspend buffer and copies memory via kmap or ro32 loop; load restores via kmap or wo32 loop then frees suspend. new delegates to imem->func->memory_new, optionally zeroes if backend lacks zero support, marks preserve, and returns nvkm_memory. boot moves current objects to a boot list for slowpath access. fini optionally calls backend suspend and marks suspended, then backend fini; init resumes if suspended or initializes BAR2 otherwise.

## State, Persistence, Dependencies, And Integration
State includes instobj list/boot list, spinlock, mutex, suspend flag, per-object preserve and suspend buffer, and backend function table. Dependencies are nvkm_memory, nvkm_bar_bar2_init, backend instmem funcs, and memory mapping helpers. Integration points are FIFO/GR/MMU object allocations, BAR2 instance access, and system suspend/resume.

## Risks And Test Signals
Risks: save/load size assumes 32-bit aligned memory; zeroing fallback can be slow; list moves require lock correctness; preserve flag influences suspend behavior. Test signals include instmem allocations with zero flag, suspend/resume restoration, BAR2 init on cold boot, and no list corruption on object destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/base.c -->
