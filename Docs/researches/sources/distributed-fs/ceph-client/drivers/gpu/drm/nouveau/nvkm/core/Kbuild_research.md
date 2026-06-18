# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/Kbuild

## Purpose
This Kbuild fragment lists the NVKM core object files compiled into Nouveau.

## Important APIs, Types, and Functions
It assigns `nvkm-y` entries for client, engine, enum, event, firmware, gpuobj, interrupt, ioctl, memory, memory manager, object, proxy object, option parsing, RAM hash table, subdevice, and user event support.

## Control Flow
There is no runtime control flow. It controls build composition for NVKM core services.

## State and Persistence Behavior
No runtime state exists. Build state is the object list.

## Dependencies and Integration Points
It is included by `nvkm/Kbuild`; many listed objects are prerequisites for subdev and engine code.

## Risks
Omitting a core object causes link errors or missing backend functionality. Adding a source without Kbuild integration leaves code unused.

## Test Signals
Build and link coverage are the primary signals.
