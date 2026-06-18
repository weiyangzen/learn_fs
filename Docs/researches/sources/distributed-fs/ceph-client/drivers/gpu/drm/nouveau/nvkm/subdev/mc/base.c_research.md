# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/base.c

## Purpose
Provides common MC services for subdevice interrupt masking, reset/enable/disable, unknown register programming, and MC subdevice construction.

## Important APIs, Types, and Functions
Public helpers are `nvkm_mc_unk260`, `nvkm_mc_intr_mask`, `nvkm_mc_reset`, `nvkm_mc_disable`, `nvkm_mc_enable`, `nvkm_mc_enabled`, and `nvkm_mc_new_`. `nvkm_mc_reset_mask` selects reset bits from TOP metadata or static maps.

## Control Flow, State, and Persistence
Reset/enable paths look up the target subdevice, prefer `nvkm_top_reset`, and fall back to `mc->func->reset` entries while respecting `noauto`. Constructors install interrupt leaves through `nvkm_intr_add`, using one or two leaves depending on `intr_nonstall`. Init delegates to the chip hook.

## Dependencies and Integration Points
Depends on `core/option.h`, `subdev/top.h`, `nvkm_intr`, `nvkm_device_subdev`, and chip-specific `nvkm_mc_func` tables.

## Risks and Test Signals
Risks include stale reset masks, ignoring `noauto`, interrupt leaf misconfiguration, and null MC during early calls. Test subdevice reset/enable cycles, TOP-derived reset paths, interrupt block/allow through `nvkm_mc_intr_mask`, and all chip constructors.
