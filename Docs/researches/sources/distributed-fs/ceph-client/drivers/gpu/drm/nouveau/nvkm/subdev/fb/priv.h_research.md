<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/priv.h

## Purpose
Private framebuffer subdevice interface. It defines the generation function table consumed by `base.c` and declares shared tile, init, RAM, VPR, vidmem, and constructor helpers.

## Important APIs, Types, And Functions
`struct nvkm_fb_func` contains lifecycle hooks, sysmem flush-page init, vidmem sizing, VPR scrub hooks, tile operations, RAM construction, and clkgate packs. It declares `nvkm_fb_ctor()`, `nvkm_fb_new_()`, BIOS RAM-type lookup, legacy tile helpers, GF100/GM/GV/GP/GA helpers, R535 constructor, and vidmem/VPR operations.

## Control Flow
This header routes compile-time dependencies. Generation files fill `nvkm_fb_func` instances; `base.c` calls the hooks in lifecycle order; R535 wrappers use the same table to provide host-driver-backed RAM information.

## State And Persistence
No direct state is stored, but the function table controls persistent hardware state such as RAM object construction, tile programming, remapper/page setup, VPR unlock, and sysmem flush-page programming.

## Dependencies And Integration Points
Depends on NVKM framebuffer public types, BIOS, thermal clkgate packs, RAM constructors, and generation helpers. It is the central private contract for all files in `subdev/fb`.

## Risks
Hook semantics are broad and generation-specific. A wrong function pointer can corrupt framebuffer setup on only one architecture, and optional hooks require callers to preserve NULL checks.

## Test Signals
Compiler diagnostics catch missing declarations. Runtime probe, init, VPR scrub, vidmem sizing, and tile/comptag behavior across generations validate table wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/priv.h -->
