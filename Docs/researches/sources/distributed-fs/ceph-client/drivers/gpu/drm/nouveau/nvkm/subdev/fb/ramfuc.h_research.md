<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramfuc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramfuc.h

## Purpose
Helper layer for building PMU memx scripts used by RAM reclocking code. It caches register values, emits masked writes/waits/delays/training commands, and manages script init/execute lifetime.

## Important APIs, Types, And Functions
`struct ramfuc` stores the active `nvkm_memx`, framebuffer, and sequence counter. `struct ramfuc_reg` describes cached register address, stride, mask, force flag, and data. Helpers include `ramfuc_reg()`, `ramfuc_reg2()`, `ramfuc_stride()`, `ramfuc_init()`, `ramfuc_exec()`, `ramfuc_rd32()`, `ramfuc_wr32()`, `ramfuc_mask()`, waits, delays, training, block/unblock, and macro aliases such as `ram_mask()` and `ram_exec()`.

## Control Flow
Generation reclocking code calls `ram_init()` to allocate a memx script, uses cached register helpers to emit writes only when values change or are forced, inserts waits/delays/training operations, and finishes with `ram_exec(exec)` to either run or discard the script.

## State And Persistence
Register cache state is per `ramfuc_reg` and invalidated by sequence number. The active memx command buffer persists between init and exec. Hardware state changes persist only when `nvkm_memx_fini(..., true)` executes the script.

## Dependencies And Integration Points
Depends on framebuffer, PMU memx, and generation RAM scripts (`ramgt215.c`, `ramgf100.c`, `ramgk104.c`). It isolates complex reclocking sequences from direct immediate MMIO writes.

## Risks
Using helpers outside an active `ram->fb`/memx lifetime is invalid. Register caching can skip writes unless `ram_nuke()` forces them. Stride masks must match partition/rank layout or only some memory partitions receive updates.

## Test Signals
Signals include successful script allocation/execution, expected MMIO command traces, stable reclocking with `NvMemExec=1`, and safe dry-run/discard behavior with `NvMemExec=0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramfuc.h -->
