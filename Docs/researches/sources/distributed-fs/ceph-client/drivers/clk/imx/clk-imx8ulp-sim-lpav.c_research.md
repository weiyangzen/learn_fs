# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8ulp-sim-lpav.c

## Purpose
Implements the i.MX8ULP LPAV System Integration Module clock provider for HiFi-related gates. It also creates shared regmap infrastructure used by child mux and auxiliary reset devices.

## Important APIs, Types, And Functions
`struct clk_imx8ulp_sim_lpav_data` embeds a spinlock and variable-size onecell clock data. `struct clk_imx8ulp_sim_lpav_gate` describes each HiFi gate. `clk_imx8ulp_sim_lpav_probe()` maps the SIM register block, initializes a regmap with custom lock/unlock callbacks, registers three gate clocks at `SYSCTRL0`, creates an auxiliary `reset` device, registers the clock provider, and populates child OF devices.

## Control Flow
Probe allocates data, stores it as driver data before regmap initialization so lock callbacks can find it, ioremaps the MMIO resource, initializes the regmap, registers the `hifi_core`, `hifi_pbclk`, and `hifi_plat` gates with parent firmware names `core`, `bus`, and `plat`, creates the reset aux device, adds the provider, and populates mux children.

## State And Persistence Behavior
State is volatile: gate bits in `SYSCTRL0`, the shared spinlock, regmap, auxiliary device, child devices, and onecell clock data. There is no persistent metadata.

## Dependencies And Integration Points
Depends on `imx8ulp-clock.h`, auxiliary bus helpers, regmap MMIO, OF platform population, and common-clock gate registration. It coordinates register access with reset/mux users through the same spinlock.

## Risks
The custom regmap lock uses `dev_get_drvdata()`; setting drvdata before regmap init is required. Clock gates access the register directly while reset/mux use regmap, so lock sharing is necessary to avoid RMW races. Child probing depends on successful provider and regmap setup.

## Test Signals
Probe `fsl,imx8ulp-sim-lpav`, verify the three HiFi gates, child mux/reset devices, concurrent reset and clock operations, and audio/HiFi consumers using the LPAV SIM clocks.
