# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ttm.h

## Purpose
This header exposes Nouveau TTM manager and SGDMA interfaces used by the BO driver and memory-management setup code.

## Important APIs, Types, and Functions
It defines `nouveau_bdev` to recover `struct nouveau_drm` from a TTM device, declares the VRAM/GART resource-manager function tables, SGDMA TT creation/bind/unbind/destroy helpers, and TTM global and per-device init/release functions.

## Control Flow
The header has no executable flow. It wires TTM callback implementations from `nouveau_ttm.c` and `nouveau_sgdma.c` into the rest of the driver.

## State and Persistence Behavior
No state is stored here. The declared functions operate on `drm->ttm`, TTM BOs, TTM resources, and SGDMA translation tables.

## Dependencies and Integration Points
It depends on TTM device, TTM resource manager, TTM TT, Nouveau DRM, and BO driver infrastructure. It is a shared include for TTM init and BO memory backing.

## Risks
Forward declarations must match TTM callback signatures. The `nouveau_bdev` container conversion assumes `ttm.bdev` remains embedded in `struct nouveau_drm`.

## Test Signals
Build coverage plus BO allocation/bind/unbind tests are sufficient to catch most header contract regressions.
