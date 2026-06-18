# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/flcn.c

## Purpose
Provides debug dump helpers for falcon bootloader and loader descriptor formats.

## Important APIs, types, and functions
Functions include `loader_config_dump()`, `loader_config_v1_dump()`, `flcn_bl_dmem_desc_dump()`, `flcn_bl_dmem_desc_v1_dump()`, and `flcn_bl_dmem_desc_v2_dump()`.

## Control flow, state, and persistence
The helpers log DMA indices, code/data bases, code sizes, entry points, signatures, non-secure/secure code regions, and arguments. They do not mutate firmware data.

## Dependencies and integration points
Depends on `nvfw/flcn.h` and subdev logging. Used by SEC2 ACR low-secure descriptor writers and ACR high-secure bootloader setup.

## Risks and test signals
Formatting mistakes affect diagnostics, not runtime behavior. The dump output is a key test signal when secure firmware fails to load or WPR bootloader data appears wrong.
