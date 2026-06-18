# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gm20b.c

## Purpose
Provides GM20B Tegra voltage tables by selecting CVB coefficients and minimum voltage from SoC speedo ID.

## Important APIs, Types, And Functions
`gm20b_volt_new()` chooses between `gm20b_cvb_coef` and `gm20b_na_cvb_coef`, validates `gpu_speedo_id`, allocates `gk20a_volt`, and calls `gk20a_volt_ctor()`.

## Control Flow
Construction maps speedo IDs to minimum voltage, uses the non-automotive coefficient table for speedo ID >= 1, otherwise the base table, and builds regulator-backed VID entries.

## State, Persistence, And Dependencies
State is the shared `gk20a_volt` object plus selected coefficient-derived VID table and Tegra regulator pointer.

## Integration Points
Depends on Tegra device data, GK20A voltage constructor, Linux regulator APIs, and SoC speedo IDs.

## Risks
Unsupported speedo IDs return `-EINVAL`. Correct voltage behavior depends on accurate speedo-to-vmin table and coefficient set selection.

## Test Signals
Signals include expected computed voltage table per speedo ID, no unsupported-speedo errors on known boards, and successful regulator voltage changes.
