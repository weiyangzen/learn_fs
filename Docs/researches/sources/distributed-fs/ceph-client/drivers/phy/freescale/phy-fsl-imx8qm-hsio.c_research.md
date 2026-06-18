# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8qm-hsio.c

## Purpose
Generic PHY provider for i.MX8QM/i.MX8QXP HSIO SerDes lanes. It maps lane phandles to PCIe or SATA PHY modes, selects the correct register windows and clocks per lane/controller, controls reset sequencing, configures refclk pad routing, and polls readiness/PLL lock.

## Important APIs, types, and functions
- `struct imx_hsio_priv` holds shared PHY/CTRL/MISC regmaps, base MMIO, `hsio_cfg`, refclk pad policy, lane array, and `open_cnt`.
- `struct imx_hsio_lane` carries lane index, controller index, offsets, type, selected `phy_mode`, clock bulk data, and its `struct phy`.
- `imx_hsio_init()` resolves lane type from phandle args and fetches/enables five named clocks for the selected PCIe/SATA topology.
- `imx_hsio_power_on()` serializes shared pre-configuration, dispatches to PCIe or SATA power-on, then polls lane PLL lock.
- `imx_hsio_set_mode()` writes HSIO protocol mode and optional PCIe RC/EP device type; `imx_hsio_set_speed()` toggles LTSSM enable.
- `imx_hsio_xlate()` consumes three OF args: lane index, PHY type, and controller index.

## Control flow
Probe maps base plus named `phy`, `ctrl`, and `misc` resources into regmaps, reads `fsl,hsio-cfg` and `fsl,refclk-pad-mode`, creates one PHY per hardware lane, and registers a custom xlate. Init assigns offsets/clocks based on lane topology. First power-on programs shared mux/refclk bits, then per-mode reset paths run: PCIe toggles APB clock and waits for `PM_REQ_CORE_RST` to clear; SATA enables EPCS bits and waits for PMA ready. Both then wait for lane TX PLL lock.

## State and persistence
The driver persists no data outside hardware. Runtime state includes lane mode/type/offsets, enabled clocks, and shared `open_cnt`. The mutex protects shared MISC mux state and `open_cnt`.

## Dependencies and integration points
Uses `dt-bindings/phy/phy.h`, `dt-bindings/phy/phy-imx8-pcie.h`, generic PHY, bulk clk APIs, platform MMIO, and regmap MMIO. Consumers are PCIe and SATA controller nodes that pass HSIO lane parameters via PHY phandles.

## Risks and test signals
Risks include underflowing `open_cnt` if power-off is unbalanced, stale lane configuration if a lane phandle is translated multiple ways, unchecked `devm_platform_ioremap_resource_byname()` error pointers before regmap init, and topology-specific clock-name mistakes. Test by booting all supported HSIO configs, PCIe RC/EP mode setting, SATA link bring-up, repeated bind/unbind/power cycles, and fault-injecting missing named resources/clocks.
