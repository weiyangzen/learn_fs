# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/Kbuild

## Purpose
This Kbuild fragment lists the NVIF object files included in the Nouveau build.

## Important APIs, Types, and Functions
It populates `nvif-y` with object, client, connector, device, display, driver, event, FIFO, head, memory, MMU, output, timer, VMM, channel class, and usermode class object files.

## Control Flow
There is no runtime control flow. The build system includes this fragment to compile the NVIF layer into the driver.

## State and Persistence Behavior
No runtime state exists. Build state is the ordered object list assigned to `nvif-y`.

## Dependencies and Integration Points
It is consumed by the parent Nouveau Kbuild and mirrors source modules under `nvif/`.

## Risks
Missing an object here causes unresolved symbols or silent feature loss. Adding a source without updating the fragment will not compile it.

## Test Signals
Kernel build coverage and link-time symbol checks validate this file.
