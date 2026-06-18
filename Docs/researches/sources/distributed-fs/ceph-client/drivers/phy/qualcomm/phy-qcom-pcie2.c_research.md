# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-pcie2.c

## Purpose
This legacy Qualcomm PCIe2 PHY driver provides a generic PHY and fixed-rate pipe clock for controllers using the `qcom,pcie2-phy` binding. It programs PARF/PCS registers for refclock selection, TX amplitude/de-emphasis, RX equalization, reset release, and pipe clock enablement.

## Important APIs, Types, and Functions
`struct qcom_phy` holds the device, MMIO base, two regulators (`vdda-vp`, `vdda-vph`), resets (`phy`, `pipe`), and pipe clock. `qcom_pcie2_phy_init()` deasserts the PHY reset and enables regulators. `qcom_pcie2_phy_power_on()` performs the analog/PCS programming sequence and polls `PCIE20_PARF_PHY_STTS`. `qcom_pcie2_phy_power_off()` asserts software reset and disables the pipe clock/reset. `phy_pipe_clksrc_register()` registers a 250 MHz fixed-rate pipe clock source using `clock-output-names`.

## Control Flow
Probe allocates state, maps resource 0, registers the pipe clock source, gets the two regulators, gets the unnamed pipe clock, gets the named `phy` and `pipe` resets, creates the PHY, and registers a simple provider. Init deasserts `phy_reset`, then enables regulators. Power-on programs refclock control bits, asserts PHY software reset, writes swing/de-emphasis/EQ/termination values, disables loopback, deasserts software reset, deasserts pipe reset, sets and enables the pipe clock at 250 MHz, then polls until the status bit clears. Power-off reverses the pipe side and reasserts software reset; exit disables regulators and asserts `phy_reset`.

## State and Persistence
The driver has no dynamic software state beyond resource handles. Hardware programming happens on every power-on. The fixed clock provider persists for the life of the device and is consumed by GCC/PCIe clock topology.

## Dependencies and Integration Points
It depends on Linux PHY, reset, regulator, platform MMIO, iopoll, and clock-provider APIs. The device tree must provide MMIO, `clock-output-names`, two regulators, an unnamed pipe clock, and named resets. The PCIe controller consumes the PHY and pipe clock through DT.

## Risks and Edge Cases
`readl_poll_timeout(..., 1000, 10)` uses a 10 microsecond timeout with a 1000 microsecond sleep interval, which is unusual and may be too short or misleading. If `clk_prepare_enable(pipe_clk)` fails after pipe reset deassertion, the code returns without reasserting `pipe_reset`. The init error message says "pipe reset" when deasserting `phy_reset`. Register magic values are hard-coded and not SoC-specific beyond the single compatible string.

## Test Signals
Expected signals include pipe clock provider registration, successful regulator/reset sequencing, status polling completion, and PCIe link training. Negative tests should exercise missing `clock-output-names`, missing supplies/resets, pipe clock enable failure, and timeout handling.
