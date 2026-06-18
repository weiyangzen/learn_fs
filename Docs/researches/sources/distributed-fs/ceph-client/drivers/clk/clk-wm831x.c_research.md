# sources/distributed-fs/ceph-client/drivers/clk/clk-wm831x.c

## Purpose
`clk-wm831x.c` is a platform CCF driver for the Wolfson WM831x PMIC clock block. It exposes three clocks from the parent MFD device: a 32.768 kHz crystal clock, an FLL clock that is supported only in AUTO frequency mode, and a `clkout` output buffer that can select either FLL or crystal as parent.

## Important APIs, Types, And Functions
`struct wm831x_clk` stores the parent `struct wm831x *`, three `clk_hw` objects, and a cached `xtal_ena` flag read once at probe. `wm831x_xtal_is_prepared()` and `wm831x_xtal_recalc_rate()` expose the OTP/InstantConfig-controlled crystal state. FLL support is implemented by `wm831x_fll_is_prepared()`, `wm831x_fll_prepare()`, `wm831x_fll_unprepare()`, `wm831x_fll_recalc_rate()`, `wm831x_fll_determine_rate()`, `wm831x_fll_set_rate()`, and `wm831x_fll_get_parent()`. Output support is implemented by `wm831x_clkout_is_prepared()`, `wm831x_clkout_prepare()`, `wm831x_clkout_unprepare()`, `wm831x_clkout_get_parent()`, and `wm831x_clkout_set_parent()`.

## Control Flow
Probe retrieves the PMIC core from the parent device, allocates driver state, reads `WM831X_CLOCK_CONTROL_2` to cache whether the crystal is enabled, then registers `xtal`, `fll`, and `clkout` as device-managed `clk_hw` objects. The FLL has two possible parents by name (`xtal`, `clkin`) but AUTO mode always reports the crystal parent. FLL rate determination selects the nearest value from eight predefined AUTO rates. `set_rate` accepts only exact table entries and refuses changes while the FLL is enabled because the CCF init data marks the clock `CLK_SET_RATE_GATE`.

`fll_prepare` sets `WM831X_FLL_ENA` and sleeps 2-3 ms for the new frequency to take effect; `fll_unprepare` clears the same bit. `clkout_prepare` and `clkout_unprepare` unlock protected PMIC registers, update `WM831X_CLKOUT_ENA`, and relock. `clkout_set_parent` updates the `WM831X_CLKOUT_SRC` bit to select between FLL and crystal.

## State And Persistence
Persistent state lives in WM831x PMIC registers accessed through the MFD register API: `FLL_CONTROL_1`, `CLOCK_CONTROL_1`, `CLOCK_CONTROL_2`, and `FLL_CONTROL_5`. The crystal enable state is not writable here and is cached once because it is controlled by OTP/InstantConfig. The FLL enable bit, FLL AUTO frequency index, clkout enable bit, and clkout parent bit are mutable hardware state. The driver has no explicit remove callback; devm clock registrations are released with the platform device.

## Dependencies And Integration Points
The driver depends on the WM831x MFD core for register reads, writes, bit updates, and protected register locking. It integrates with CCF as a platform driver named `wm831x-clk` and publishes clocks named `xtal`, `fll`, and `clkout`. It expects any external `clkin` parent to be registered elsewhere by name and relies on MFD platform-device creation for probe.

## Risks
The FLL implementation only supports AUTO mode; manual FLL configurations recalc to 0 and log an error. `wm831x_fll_is_prepared()` returns true on register-read failure, which prevents rate changes but can hide hardware access problems as a conservative enabled state. `clkout_set_parent()` writes protected clock control bits without unlocking, unlike prepare/unprepare, so whether it works depends on MFD/register policy for that field. FLL rate selection uses `abs()` on differences involving unsigned long request values coerced through integer arithmetic, which is acceptable for the small table but fragile if expanded. Names are fixed and not OF-provider based, so multiple WM831x instances could collide in the global clock namespace.

## Test Signals
Useful tests include platform probe from the WM831x MFD, xtal rate reporting based on `WM831X_XTAL_ENA`, FLL nearest-rate selection for all eight AUTO frequencies, exact-match rejection in `set_rate`, `-EPERM` when changing FLL rate while enabled, and the 2-3 ms enable delay. Register-level tests should verify clkout enable/disable performs unlock/update/lock and parent selection toggles `WM831X_CLKOUT_SRC`. Integration tests should check consumers can resolve `xtal`, `fll`, and `clkout` by name and that manual FLL mode is reported as unsupported.
