# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/priv.h

## Purpose
Defines the private instmem hardware interface and common instance-object structure used by NV04, NV40, NV50, and firmware-backed implementations.

## Important APIs, Types, and Functions
`struct nvkm_instmem_func` declares lifecycle hooks, direct register accessors, memory allocation/wrapping hooks, zeroing policy, and BAR0 window programming. `struct nvkm_instobj` embeds `nvkm_memory` plus list/preserve/suspend state. The header declares common constructors/destructors and save/load helpers.

## Control Flow, State, and Persistence
The header has no executable control flow. It defines persistent object state used by suspend/resume: `preserve` selects objects to save, while `suspend` stores saved dwords.

## Dependencies and Integration Points
It includes public `subdev/instmem.h` and `core/memory.h`, and is consumed by all instmem backends plus R535 glue.

## Risks and Test Signals
Signature drift breaks chip-specific backends. Save/load state must remain compatible with every `nvkm_memory_func`. Build coverage across NV04/NV40/NV50/GSP configurations and suspend/resume tests are the main signals.
