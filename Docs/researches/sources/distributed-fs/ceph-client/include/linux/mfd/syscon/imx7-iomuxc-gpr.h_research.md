# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/imx7-iomuxc-gpr.h

## Purpose

This 48-line header defines i.MX7 IOMUXC GPR offsets and selected bitfields for Ethernet clocking, CSI muxing, and PCIe PHY status/control.

## Important APIs, Types, and Functions

It exports `IOMUXC_GPR0` through `GPR22`, `IMX7D_GPR1_*` IRQ/ENET clock selection/direction masks, `IMX7D_GPR5_CSI_MUX_CONTROL_MIPI`, `IMX7D_GPR12_PCIE_PHY_REFCLK_SEL`, and `IMX7D_GPR22_PCIE_PHY_PLL_LOCKED`.

## Control Flow

No local flow exists. i.MX7 drivers use syscon regmap masked updates and reads to configure ENET clocks, CSI input muxing, and PCIe reference clock/PLL lock handling.

## State and Persistence Behavior

The state persists in IOMUXC GPR hardware registers and affects clock direction/source, camera routing, and PCIe PHY readiness.

## Dependencies and Integration Points

It integrates i.MX7 syscon consumers in Ethernet, media/CSI, and PCIe PHY/controller drivers.

## Risks and Edge Cases

PCIe PLL lock is a status bit, not a configuration bit. ENET clock source and direction masks must be updated atomically to avoid transient wrong clock routing.

## Test Signals

Board boot tests for Ethernet/CSI/PCIe, syscon regmap update tests, and PCIe PLL-lock wait-path tests.
