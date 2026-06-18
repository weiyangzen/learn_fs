## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/Kbuild

### Purpose
This Kbuild fragment defines the top-level NVKM engine objects that are always part of the Nouveau build and includes every engine-family subdirectory build fragment.

### Important APIs, types, and functions
It adds `nvkm/engine/falcon.o` and `nvkm/engine/xtensa.o` to `nvkm-y`, then includes Kbuild fragments for BSP, CE, cipher, device, display, DMA, FIFO, GR, MPEG, MSENC, MSPDEC, MSPPP, MSVLD, NVENC, NVDEC, SEC, SEC2, SW, VIC, and VP.

### Control flow
There is no runtime control flow. The build system evaluates this file to determine which objects become part of the `nvkm` built-in object list.

### State and persistence behavior
The file owns build state only: the object list and the inclusion order. Runtime state is introduced by the compiled engine source files.

### Dependencies
It depends on the kernel Kbuild `nvkm-y` convention and the existence of all included `$(src)/nvkm/engine/*/Kbuild` files.

### Integration points
This is the root build integration point for engine code used by the Nouveau DRM driver. Removing or reordering includes changes which engine constructors and symbols are available to `device/base.c`.

### Risks
Missing includes or object entries cause link failures or silently omit hardware support. Because engine families export constructors referenced from the device chipset table, build coverage must stay synchronized with `base.c`.

### Test signals
Full Nouveau builds across common configs, link-time symbol resolution for all constructors used in `device/base.c`, and build tests after adding new engine directories are the primary signals.
