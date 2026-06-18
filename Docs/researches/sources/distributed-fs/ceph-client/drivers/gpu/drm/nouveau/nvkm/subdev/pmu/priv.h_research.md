# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/priv.h

## Purpose
Defines private PMU function-table contracts and cross-chip helper declarations for Nouveau's nvkm PMU implementations.

## Important APIs, Types, And Functions
`struct nvkm_pmu_func` contains falcon, firmware image, lifecycle, interrupt, mailbox, init-message, and PGO/B callbacks. `struct nvkm_pmu_fwif` ties firmware version/loaders to function tables and optional ACR descriptors.

## Control Flow
Chip files populate these tables; PMU base construction selects a fwif, loads firmware when needed, and dispatches subdev operations through the selected callbacks.

## State, Persistence, And Dependencies
No runtime state is stored in the header, but it describes the persistent fields that `struct nvkm_pmu` and firmware interface tables use.

## Integration Points
Integrated by all PMU chip files, ACR secure firmware code, GT215 mailbox code, GF100/GM200 no-firmware loaders, and the exported constructors in PMU base.

## Risks
ABI changes here affect every PMU implementation. Callback omissions are meaningful and must match the base code's null checks.

## Test Signals
Compile-time coverage is primary; runtime signals are each chip path successfully selecting compatible callback sets.
