# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gp10b.h

## Purpose
Defines the GP10B clock object layout and accessor used by GP10B clock and devfreq code.

## Important APIs, types, and functions
The header defines `struct gp10b_clk` with embedded `struct nvkm_clk`, Tegra clock pointer, cached current/new rates, and `struct gk20a_devfreq *devfreq`, plus the `gp10b_clk()` container macro.

## Control flow
There is no runtime control flow in the header.

## State and persistence
The structure fields define all persistent GP10B clock driver state. Actual hardware state is managed by the Tegra clock provider referenced by `clk`.

## Dependencies and integration points
Includes `priv.h`, `<linux/clk.h>`, and `gk20a_devfreq.h`. Used by `gp10b.c` and `gk20a_devfreq.c` for chipset-specific state lookup.

## Risks
The object layout is assumed by `container_of()`; changing the embedded base position or devfreq field expectations would break users.

## Test signals
Compile-time coverage and runtime devfreq lookup for GP10B chipset are the primary signals.
