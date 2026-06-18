# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/priv.h

## Purpose
Defines private voltage callback contracts and shared helper declarations.

## Important APIs, Types, And Functions
`struct nvkm_volt_func` includes oneinit, direct voltage get/set, VID get/set, set-by-ID override, and speedo read callbacks. The header declares common constructors and GPIO/PWM/helper functions.

## Control Flow
Chip files populate the callback table, and common voltage base invokes callbacks through `struct nvkm_volt`.

## State, Persistence, And Dependencies
No runtime state exists in the header; it defines voltage subdev ABI.

## Integration Points
Integrates NV40/GF100/GF117/GK104/Tegra voltage implementations with common voltage parsing and GPIO helpers.

## Risks
Callback changes affect all voltage drivers. Declared PWM helpers are not implemented in this assigned subset, so users must link only available objects.

## Test Signals
Compile coverage across voltage variants and successful voltage object construction are the key signals.
