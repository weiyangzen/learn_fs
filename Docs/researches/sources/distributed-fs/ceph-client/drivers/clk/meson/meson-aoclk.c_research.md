# sources/distributed-fs/ceph-client/drivers/clk/meson/meson-aoclk.c

## Purpose
Provides shared probe and reset-controller support for Amlogic always-on clock controller drivers. SoC-specific AO files supply `struct meson_aoclk_data`; this helper registers their clocks through the generic Meson syscon clock path and adds reset-controller behavior for AO reset registers.

## Important APIs, Types, And Functions
`meson_aoclk_do_reset()` implements the reset callback by writing one reset bit to `data->reset_reg`, where the actual bit index comes from the SoC reset array. `meson_aoclk_reset_ops` exposes only `.reset`, not separate assert/deassert, matching pulse-style AO reset semantics. `meson_aoclkc_probe()` is the exported probe entry point used by AO platform drivers. It calls `of_device_get_match_data()`, `meson_clkc_syscon_probe()`, allocates `struct meson_aoclk_reset_controller`, obtains the parent syscon regmap, fills `reset_controller_dev`, and registers it with `devm_reset_controller_register()`.

## Control Flow
Probe first validates match data, then delegates clock registration to `meson_clkc_syscon_probe`. After clocks are registered, it recovers the enclosing `struct meson_aoclk_data` with `container_of()` from the matched `meson_clkc_data`, resolves the parent syscon regmap, and registers resets. Reset calls later index `data->reset[id]` and write a single `BIT()` to the AO reset register.

## State And Persistence
The helper owns devm-managed software state for the reset controller and uses the parent syscon regmap for all hardware state. Reset operation is write-only pulse state in hardware; there is no cached reset state or persistent driver-owned storage. Clock state is registered by `meson_clkc_syscon_probe`, not by custom code here.

## Dependencies And Integration Points
Depends on `meson-aoclk.h`, `meson-clkc-utils.h`, `clk-regmap.h`, Linux reset-controller framework, OF match data, platform devices, syscon, and regmap. SoC AO drivers integrate by embedding `struct meson_clkc_data` as the first member of `struct meson_aoclk_data` and passing `.data = &foo.clkc_data` from their OF match table.

## Risks And Edge Cases
The reset path does not bounds-check `id` itself; it relies on reset core respecting `nr_resets`. Incorrect `reset` array content or `num_reset` values will write wrong bits. Probe performs clock registration before reset registration, so a reset-registration failure leaves clocks registered through devm. The helper requires the AO node to have a syscon parent; a missing or non-syscon parent fails probe.

## Test Signals
Build users with `MODULE_IMPORT_NS("CLK_MESON")`, boot a matching AO controller, verify clock provider registration succeeds, and exercise reset phandles from consumers. Negative DT tests should cover missing match data and missing parent syscon. Runtime debug signals include successful reset-controller registration and no invalid regmap errors during AO probe.
