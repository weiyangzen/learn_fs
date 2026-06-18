<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/Kbuild

## Purpose
Build manifest for the nouveau NVKM framebuffer subdevice and VRAM/RAM support files. It enumerates generation-specific framebuffer wrappers, RAM constructors, RAM timing calculators, and R535/GSP integration.

## Important APIs, Types, And Functions
The file does not define C APIs. It adds objects for `base.o`, legacy NV04/NV1x/NV2x/NV3x/NV4x, NV50/GT215/MCP, Fermi through Blackwell framebuffer wrappers, `r535.o`, common `ram.o`, generation RAM implementations, and type-specific timing calculators (`sddr2`, `sddr3`, `gddr3`, `gddr5`).

## Control Flow
Kbuild concatenates all `nvkm-y +=` entries into the NVKM object set. Runtime selection is done elsewhere through chipset function tables; this manifest only ensures the referenced implementations are linked.

## State And Persistence
No runtime state is stored. Build inclusion determines which constructor symbols and helper functions are available to the device table.

## Dependencies And Integration Points
Integrated by the parent nouveau NVKM build. The ordering groups framebuffer wrappers first, R535 support next, common RAM core next, then RAM generation/type helpers.

## Risks
Missing an object here produces link failures or absent chipset support even when source files exist. Adding a new wrapper without its RAM helper can leave function-table references unresolved.

## Test Signals
Kernel build/link coverage is the primary signal. Runtime probe coverage across GPU generations confirms that selected `*_fb_new()` and `*_ram_new()` symbols were linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/Kbuild -->
