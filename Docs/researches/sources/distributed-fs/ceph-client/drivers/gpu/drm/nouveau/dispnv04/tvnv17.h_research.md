<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv17.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv17.h

## Purpose
This header defines the shared on-chip NV17/NV4x TV encoder data structures, norm table contract, helper prototypes, interpolation helper, and PTV/TV-encoder register access macros.

## Important APIs, Types, and Functions
Key types are `struct nv17_tv_state`, `enum nv17_tv_norm`, `struct nv17_tv_encoder`, and `struct nv17_tv_norm_params`. It declares norm names, norm parameter table, mode table, state save/load, property/rescaler update functions, and inline `nv_write_ptv`, `nv_read_ptv`, `nv_write_tv_enc`, and `nv_read_tv_enc` helpers.

## Control Flow
Inline accessors write PTV registers directly through NVIF MMIO and access TV encoder indexed registers by writing `NV_PTV_TV_INDEX` then reading or writing `NV_PTV_TV_DATA`. The `get_tv_norm` macro derives the active norm parameters from encoder state.

## State and Persistence Behavior
`nv17_tv_state` persists TV encoder bytes, horizontal/vertical filter coefficient matrices, and selected PTV registers. `nv17_tv_encoder` embeds `nouveau_encoder` and stores current/saved TV state plus user-visible TV properties and pin-detection state.

## Dependencies and Integration Points
It depends on Nouveau encoder structures, DRM display modes, NVIF device access, and register constants from `nvreg.h` through users. `tvnv17.c` and `tvmodesnv17.c` share this header as their internal ABI.

## Risks
The state structures encode fixed register counts (`0x40`, 38 CTV registers, fixed filter dimensions); hardware additions need synchronized updates in save/load and tables. Macro-based register access has no bounds checks. Enum order is part of DRM property values and norm table indexing.

## Test Signals
Build coverage, norm property ordering checks, save/load of all tracked registers, PTV indexed access, and low-definition/HD path table indexing validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv17.h -->
