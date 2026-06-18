<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ram.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ram.h

## Purpose
Private RAM subsystem declarations for the framebuffer code. It exposes common RAM construction/destruction, generation RAM constructors, probe helpers, reclocking hooks, and memory-type timing calculators.

## Important APIs, Types, And Functions
Declares `nvkm_ram_ctor()`, `nvkm_ram_new_()`, `nvkm_ram_del()`, `nvkm_ram_init()`, `nv50_ram_ctor()`, GF100/GK104 constructors and reclocking hooks, FBP probing helpers, GM/GP probing/init helpers, memory-type calculators, and all legacy/generation `*_ram_new()` entry points.

## Control Flow
No runtime code exists. It lets framebuffer wrappers choose the correct `ram_new` hook and lets generation implementations share common constructors and probing functions.

## State And Persistence
No state is stored; declarations operate on `struct nvkm_ram`, whose state is managed by `ram.c` and generation implementations.

## Dependencies And Integration Points
Includes `priv.h` and connects `Kbuild`-linked RAM files to framebuffer function tables. It is the compile-time map of RAM support across NV04 through Pascal-era helpers.

## Risks
Signature drift affects many wrappers. Exporting internal reclocking helpers requires generation files to respect preconditions such as initialized function tables and parsed BIOS data.

## Test Signals
Build coverage across all linked RAM files and runtime probe/reclocking coverage validate the declaration surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ram.h -->
