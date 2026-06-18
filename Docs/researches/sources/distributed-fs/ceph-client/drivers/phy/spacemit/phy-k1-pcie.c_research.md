# sources/distributed-fs/ceph-client/drivers/phy/spacemit/phy-k1-pcie.c

Purpose: SpacemiT K1 PCIe and PCIe/USB3 combo PHY provider. It supports combo port A in PCIe or USB3 mode and PCIe-only ports B/C, including shared receiver/driver termination calibration.

Important APIs, types, and functions: `struct k1_pcie_phy` stores registers, private PLL clock, lane count, type, and PMU regmap for the combo PHY. Global `k1_phy_rterm` caches calibration results. `k1_pcie_phy_pll_prepare()` is a private clock `.prepare` callback that programs USB or PCIe PLL settings and polls `PLL_READY`. `k1_pcie_phy_init_pcie()` applies RX/TX termination and recalibration per lane; `k1_pcie_phy_init_usb()` selects USB3 mode. `k1_pcie_combo_phy_calibrate()` temporarily powers combo PCIe resources to get termination values. `k1_pcie_combo_phy_xlate()` requires one argument, `PHY_TYPE_PCIE` or `PHY_TYPE_USB3`, and enforces single use.

Control flow: non-port-A probes defer until global calibration is valid. Probe maps registers, deasserts the PHY reset permanently, calibrates combo port if applicable, determines lane count from `num-lanes`, creates the PHY, registers a private PLL clock, and registers an OF provider using either combo xlate or simple xlate. Init selects USB or PCIe path, then enables the private PLL clock. Exit disables it. Calibration clears an APMU hold-reset bit, reuses existing calibration when `R_TUNE_DONE` is set, otherwise enables PCIe app clocks/resets, polls `PCIE_RCAL_RESULT`, saves RX/TX rterm bits, and unwinds resources.

State and persistence: global static calibration state is shared by all instances and persists for module lifetime. Per-instance state includes selected combo type, lane count, and private PLL clock. Hardware state includes PMU combo mux, reset deassertion, PLL programming, lane termination, and refclock mode.

Dependencies and integration points: generic PHY, clock provider API, syscon/regmap APMU, reset/clock bulk APIs, DT phy type bindings, PCIe and USB3 controller consumers. Controller drivers must provide associated app clocks/resets for calibration and manage their own operational clocks/resets.

Risks: global `k1_phy_rterm` assumes one K1 SoC calibration domain and no hot-unplug multi-device ambiguity. Port B/C cannot probe before combo calibration, so missing port A DT causes permanent deferral. `k1_combo_phy_sel()` uses a compact boolean expression that is easy to misread. PHY reset is deasserted and left deasserted by design, which must match controller expectations.

Test signals: probe ordering with port A and B/C, PCIe link training on one- and two-lane ports, USB3 operation through combo xlate, repeated probe deferral, private PLL lock timeout behavior, and validation that calibration values are applied to all PCIe lanes.
