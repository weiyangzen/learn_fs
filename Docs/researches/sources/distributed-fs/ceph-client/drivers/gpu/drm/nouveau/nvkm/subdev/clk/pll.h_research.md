# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/pll.h

## Purpose
Declares shared PLL calculation helpers for legacy NV04-style PLLs and GT215-style fractional-capable PLLs.

## Important APIs, types, and functions
Exports `nv04_pll_calc()` and `gt215_pll_calc()` prototypes over opaque `struct nvkm_subdev` and `struct nvbios_pll` inputs.

## Control flow
No runtime flow in this header. Implementations search PLL coefficient ranges and return the closest achievable frequency and coefficient fields.

## State and persistence
No state is stored. Callers pass output coefficient pointers and later program hardware.

## Dependencies and integration points
Used by clock and devinit generations from NV04 through GA100 for core/display/memory PLL calculations.

## Risks
Signature changes affect many architecture-specific clock/devinit files. Callers rely on return-value conventions: positive/zero/negative meanings differ between helper families.

## Test signals
Build coverage and mode-setting/reclock tests that exercise VPLL, memory PLL, and engine PLL calculations.
