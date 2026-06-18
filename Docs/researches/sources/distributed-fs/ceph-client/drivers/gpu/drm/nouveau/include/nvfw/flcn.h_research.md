
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/flcn.h

## Purpose
Defines generic falcon bootloader and loader configuration descriptors used when loading NVIDIA falcon microcode.

## Important APIs, types, and functions
- `struct loader_config` and packed `loader_config_v1` describe DMA indexes, code/data/overlay DMA bases, sizes, entry points, and arguments.
- `struct flcn_bl_dmem_desc`, packed `flcn_bl_dmem_desc_v1`, and packed `flcn_bl_dmem_desc_v2` describe bootloader DMEM layout, signatures, secure/non-secure code regions, data regions, and optional argc/argv.
- Dump prototypes exist for loader and bootloader descriptor versions.

## Control flow
No executable flow is present. Firmware loader code selects the descriptor version required by the target falcon/firmware image, fills or parses it, and optionally dumps it for diagnostics.

## State and persistence
The structs represent transient DMEM descriptors and persistent firmware blob layout. No driver state is declared here.

## Dependencies and integration points
Includes `core/os.h` and forward declares `struct nvkm_subdev`. It is consumed by NVKM falcon firmware bootstrap code and works with the ACR descriptors in `acr.h`.

## Risks
Packed 64-bit descriptor versions must match firmware ABI exactly. Confusing 32-bit and 64-bit DMA base variants can boot from wrong addresses. Secure and non-secure code offsets/sizes are security-sensitive.

## Test signals
Falcon boot on GPUs using each descriptor version, debug dumps, and failure injection for bad code/data sizes are useful signals.
