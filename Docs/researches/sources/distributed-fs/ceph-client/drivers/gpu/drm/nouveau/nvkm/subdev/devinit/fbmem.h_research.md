# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/fbmem.h

## Purpose
Provides framebuffer aperture mapping and direct read/write helpers used by legacy devinit memory-size/type probing.

## Important APIs, types, and functions
Defines NV04/NV10 PFB register constants and inline helpers `fbmem_init()`, `fbmem_fini()`, `fbmem_peek()`, `fbmem_poke()`, and `fbmem_readback()`.

## Control flow
Helpers map BAR1 framebuffer memory write-combined, perform atomic page mappings for individual offsets, issue 32-bit reads/writes, enforce a write memory barrier, and compare readback patterns.

## State and persistence
No private state beyond the returned `io_mapping`. Writes affect framebuffer memory and PFB configuration registers controlled by callers.

## Dependencies and integration points
Depends on device resource address/size callbacks and Linux `io_mapping` APIs. Used by NV04/NV05/NV10/NV20 memory init probes.

## Risks
Pattern writes happen before normal memory manager setup, so offsets and mapping size must be valid. Atomic WC mappings and barriers are required to avoid stale or reordered readback.

## Test signals
Legacy memory-size detection, successful BAR1 mapping, and correct RAM amount/width reporting on NV04-NV2x hardware.
