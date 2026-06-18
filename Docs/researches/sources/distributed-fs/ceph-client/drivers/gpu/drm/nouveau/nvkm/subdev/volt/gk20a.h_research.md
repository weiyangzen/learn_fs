# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gk20a.h

## Purpose
Defines shared Tegra GK20A/GM20B voltage coefficient and object structures.

## Important APIs, Types, And Functions
`struct cvb_coef` stores CVB polynomial coefficients. `struct gk20a_volt` embeds `nvkm_volt` and stores the VDD regulator. `gk20a_volt_ctor()` is declared for reuse.

## Control Flow
GM20B and GK20A source files pass chip-specific coefficient arrays into the shared constructor.

## State, Persistence, And Dependencies
No standalone runtime state exists in the header, but it defines the allocated Tegra voltage object layout.

## Integration Points
Integrates Tegra voltage variants with the common GK20A CVB/regulator implementation.

## Risks
Structure changes affect `container_of` and GM20B reuse. Coefficient semantics must match the constructor formulas.

## Test Signals
Compile coverage and successful GK20A/GM20B voltage object construction are the primary signals.
