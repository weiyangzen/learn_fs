# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/firmware.c

## Purpose
This file loads NVIDIA firmware blobs and wraps firmware images as NVKM memory objects suitable for DMA or VMM mapping.

## Important APIs, Types, and Functions
Public APIs include `nvkm_firmware_get`, `nvkm_firmware_put`, `nvkm_firmware_load_name`, `nvkm_firmware_load_blob`, `nvkm_firmware_ctor`, and `nvkm_firmware_dtor`. Internal memory methods expose scatterlist, size, physical address, page shift, target, and map behavior.

## Control Flow
Firmware get lowercases the chip name and requests `nvidia/<chip>/<fwname>[-ver].bin` without warning. Blob load copies firmware data and releases the firmware. Firmware constructor copies source bytes into RAM, DMA noncoherent memory, or vmalloc-backed SGT depending on function type, prepares DMA/scatterlist mappings, and constructs an NVKM memory wrapper. Destructor releases allocations and DMA mappings according to type.

## State and Persistence Behavior
State includes firmware name, device, length, image pointer, physical DMA address, scatterlist/table, and embedded NVKM memory object. Loaded blobs store copied data and size.

## Dependencies and Integration Points
It depends on Linux firmware loading, DMA mapping APIs, NVKM device/subdev logging, NVKM memory/VMM mapping, and firmware consumers in subdevs/falcons.

## Risks
Path buffers are fixed size. DMA/SGT constructors must unwind partially built mappings. SGT images use vmalloc pages and must map every page. Tegra devices return non-coherent host target.

## Test Signals
Signals include firmware present/missing paths, versioned names, RAM/DMA/SGT constructors and destructors, VMM mapping of firmware memory, and DMA mapping failure injection.
