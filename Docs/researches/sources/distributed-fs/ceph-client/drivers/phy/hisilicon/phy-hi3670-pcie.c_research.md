# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi3670-pcie.c

## Purpose
Kirin 970/Hi3670 PCIe PHY provider. It coordinates sysctrl/crgctrl/pmctrl syscons, local PHY MMIO, several clocks, PLL programming, IO/ref gating, controller PERST, eye-parameter programming, and NoC power state for PCIe bring-up.

## Important APIs, types, and functions
- `struct hi3670_pcie_phy` holds regmaps, clocks, MMIO base, device, and five eye parameters.
- `hi3670_pcie_get_resources_from_pcie()` obtains the parent PCIe driver's `kirin_pcie_apb` regmap at PHY init time.
- `kirin_pcie_clk_ctrl()` sequences five clocks with rollback on failure.
- `hi3670_pcie_allclk_ctrl()`, `hi3670_pcie_pll_init()`, and `hi3670_pcie_pll_ctrl()` configure and lock FNPLL.
- `hi3670_pcie_phy_power_on()` runs CMOS power, clock/reset, PLL, PERST, pipe clock, eye tuning, and NoC power release.
- `hi3670_pcie_phy_power_off()` disables OE/allclk and drops CMOS power, but intentionally does not disable all clocks due a documented SError risk.

## Control flow
Probe gets global syscon regmaps by compatible, clocks, MMIO, and eye params, then creates a built-in PHY provider. `init()` is not hardware init; it defers APB regmap discovery until the PCIe controller is probed. `power_on()` performs the actual hardware sequence and polls PLL/pipe/NoC status. Failure after clocks are enabled rolls back only through `kirin_pcie_clk_ctrl(false)`.

## State and persistence
State is cached clock/regmap pointers and eye parameters. Hardware state remains in syscon/MMIO registers. No persistent storage exists. There is an intentional power-off asymmetry for critical clocks.

## Dependencies and integration points
Uses generic PHY, clk, regmap/syscon, platform bus lookup, PCIe controller regmap integration, and built-in platform driver registration. It is tightly coupled to the `pcie-kirin` driver registering `kirin_pcie_apb`.

## Risks and test signals
Risks include deferred APB lookup ordering, the `is_pipe_clk_stable()` loop condition depending on active-low semantics, clock leak by design on power-off, and many register writes without rollback. Test PCIe controller probe ordering, link training, suspend/resume/power-off behavior, NoC idle transitions, and custom eye params.
