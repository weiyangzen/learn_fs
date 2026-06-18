# sources/distributed-fs/ceph-client/drivers/clk/meson/meson-clkc-utils.c

## Purpose
Implements common registration utilities for Meson clock-controller drivers. It centralizes OF clock lookup, optional register initialization, per-clock `clk_hw` registration, and probe flows for controllers backed either by a parent syscon regmap or by directly mapped MMIO.

## Important APIs, Types, And Functions
`meson_clk_hw_get()` is the OF clock provider callback. It indexes `struct meson_clk_hw_data` by `clkspec->args[0]`, rejects out-of-range IDs with `ERR_PTR(-EINVAL)`, and returns the selected `clk_hw`. `meson_clkc_init()` reads matched `struct meson_clkc_data`, optionally writes `init_regs` through `regmap_multi_reg_write()`, registers every non-null clock with `devm_clk_hw_register()`, and adds the OF provider with `devm_of_clk_add_hw_provider()`. `meson_clkc_syscon_probe()` obtains the parent syscon regmap. `meson_clkc_mmio_probe()` maps platform resource 0, creates a 32-bit stride-4 regmap, and calls common init.

## Control Flow
Platform drivers call one of the two exported probe helpers. Both resolve a regmap, then call `meson_clkc_init()`. Initialization validates match data, applies static register defaults if present, iterates the sparse hardware clock array, and stops on the first registration failure. OF clock consumers later call back into `meson_clk_hw_get()` for phandle resolution.

## State And Persistence
The utility does not keep global state. Hardware state can be changed by optional init register writes and later by registered clock ops using the same regmap. Registration state is device-managed for platform probes, so clocks and providers are cleaned up with device lifecycle. MMIO regmap lifetime is also devm-managed.

## Dependencies And Integration Points
Depends on Linux CCF, OF device matching, syscon, platform resource mapping, regmap, and local `meson-clkc-utils.h`. It is used by main, AO, and DDR Meson clock controllers. The helper is exported in the `CLK_MESON` namespace for modular drivers.

## Risks And Edge Cases
`meson_clk_hw_get()` assumes one clock cell and uses `args[0]`; incompatible bindings or missing `#clock-cells = <1>` will fail. Sparse arrays are allowed, but a valid in-range ID can return NULL if the SoC did not populate that clock. `meson_clkc_init()` ignores the return value of `regmap_multi_reg_write()`, so failed init writes are not directly reported. MMIO max_register is calculated from resource size minus stride, which assumes a non-empty 4-byte-aligned region.

## Test Signals
Compile drivers using both syscon and MMIO helpers. Probe a syscon-backed controller and a direct-MMIO controller, then verify OF phandle lookups by valid and invalid clock IDs. Fault-injection or debug instrumentation should confirm registration errors stop probe and out-of-range lookup logs `invalid index`.
