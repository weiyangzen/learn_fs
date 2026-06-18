## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/bsp/Kbuild

### Purpose
This Kbuild fragment builds the NVKM BSP engine implementation for G84-era hardware.

### Important APIs, types, and functions
It adds `nvkm/engine/bsp/g84.o` to `nvkm-y`, making `g84_bsp_new()` available to the chipset table.

### Control flow
There is no runtime control flow; Kbuild appends one object file.

### State and persistence behavior
Only build state is affected. Runtime state comes from the compiled Xtensa-backed BSP engine.

### Dependencies
It depends on `engine/Kbuild` including this file and on `g84.c` compiling with the shared engine/xtensa infrastructure.

### Integration points
`device/base.c` references `g84_bsp_new()` for G84/G86/G92/G94/G96/GT200-era chipsets that expose the BSP video engine.

### Risks
Dropping this object breaks link or runtime support for legacy BSP acceleration. Adding newer BSP implementations requires extending this fragment and the chipset table together.

### Test signals
Kernel build and probe on G84-class GPUs with BSP constructor paths enabled are the main signals.
