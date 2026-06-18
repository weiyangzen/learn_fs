## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/cipher/Kbuild

### Purpose
This Kbuild fragment builds the legacy G84 cipher engine implementation.

### Important APIs, types, and functions
It appends `nvkm/engine/cipher/g84.o` to `nvkm-y`, making `g84_cipher_new()` and related static class behavior part of the NVKM object.

### Control flow
There is no runtime flow; Kbuild includes one object file.

### State and persistence behavior
Only build composition is affected.

### Dependencies
It depends on `engine/Kbuild` including this file and `g84.c` compiling with engine/fifo/gpuobj support.

### Integration points
`device/base.c` references `g84_cipher_new()` for G84/G86/G92/G94/G96/GT200-era chipsets.

### Risks
Removing the object breaks legacy cipher engine constructor availability. Adding another cipher generation requires this build file and chipset table updates.

### Test signals
Nouveau build/link checks and probe on G84-class hardware with cipher engine enabled validate this fragment.
