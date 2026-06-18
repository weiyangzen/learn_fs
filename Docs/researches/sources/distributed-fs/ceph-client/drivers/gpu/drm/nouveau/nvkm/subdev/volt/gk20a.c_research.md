# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gk20a.c

## Purpose
Implements Tegra GK20A regulator-backed voltage tables computed from CVB coefficients and GPU speedo.

## Important APIs, Types, And Functions
`gk20a_volt_get_cvb_voltage()`, `gk20a_volt_get_cvb_t_voltage()`, `gk20a_volt_calc_voltage()`, `gk20a_volt_vid_get()`, `gk20a_volt_vid_set()`, `gk20a_volt_set_id()`, `gk20a_volt_ctor()`, and `gk20a_volt_new()` are important.

## Control Flow
Constructor reads the default regulator voltage, stores the Tegra VDD regulator, computes one VID entry per CVB coefficient using speedo and a fixed temperature point, and clamps to minimum voltage. Set paths call Linux regulator APIs directly.

## State, Persistence, And Dependencies
State is `struct gk20a_volt`, regulator pointer, computed VID table, and Tegra speedo data. Voltage is persisted only in the regulator hardware state.

## Integration Points
Depends on `core/tegra.h`, Linux regulator API, common voltage base, and SoC speedo data.

## Risks
The table uses fixed coefficients and -10 C calculation assumptions. `regulator_set_voltage()` uses 1.2 V as max bound for all entries.

## Test Signals
Signals include computed VID debug table, regulator voltage readback, and DVFS pstate changes successfully adjusting voltage.
