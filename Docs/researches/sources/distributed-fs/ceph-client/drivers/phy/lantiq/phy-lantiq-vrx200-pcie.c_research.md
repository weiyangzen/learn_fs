# sources/distributed-fs/ceph-client/drivers/phy/lantiq/phy-lantiq-vrx200-pcie.c

## Purpose
PCIe PHY provider for Lantiq VRX200/ARX300 SoCs. It programs 16-bit PHY registers for 36 MHz reference mode, controls endian configuration, resets PCIe/PHY, enables PDI/PHY clocks, waits for PLL status, and applies modulation workarounds.

## Important APIs, types, and functions
- `struct ltq_vrx200_pcie_phy_priv` stores PHY/regmap/RCU regmap, clocks, resets, endian property data, and selected mode.
- `ltq_vrx200_pcie_phy_xlate()` accepts one mode argument but only implements `LANTIQ_PCIE_PHY_MODE_36MHZ`.
- `ltq_vrx200_pcie_phy_common_setup()` and `pcie_phy_36mhz_mode_setup()` write PLL/TX/RX tuning.
- `ltq_vrx200_pcie_phy_wait_for_pll()` polls PLL status.
- `ltq_vrx200_pcie_phy_apply_workarounds()` toggles load-enable slices and repeated TX modulation sequences.

## Control flow
Probe maps PHY MMIO as an 8-bit-register/16-bit-value regmap, gets RCU syscon and endian properties, clocks and resets, creates one PHY, and registers custom xlate. Init sets AHB endian, resets PHY and PCIe. Power-on enables PDI clock, writes setup, enables PHY clock, waits for PLL, and applies workarounds. Power-off disables clocks; exit asserts resets.

## State and persistence
Selected mode is cached but only 36 MHz is supported. Hardware registers store all runtime state. No persistent storage.

## Dependencies and integration points
Generic PHY, regmap MMIO, syscon/regmap, clk, reset, device properties, and Lantiq PHY dt-binding constants. Consumed by PCIe controller.

## Risks and test signals
Risks include unsupported DT modes returning errors, many setup writes without error checking, PLL timeout, and endian property misconfiguration. Test 36 MHz mode, unsupported mode rejection, big/little-endian DT, PLL timeout, and PCIe link training.
