# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-axg-pcie.c

Purpose: Implements the AXG PCIe PHY wrapper that programs a small digital control register, coordinates reset, and delegates analog power/init to a named analog PHY.

Important APIs and types: `struct phy_axg_pcie_priv` holds the MMIO regmap, reset array, generic PHY object, and companion analog PHY. The exported behavior is through `phy_axg_pcie_ops`: `.init`, `.exit`, `.power_on`, `.power_off`, and `.reset`.

Control flow: probe maps `MESON_PCIE_REG0`, creates a regmap, gets an exclusive reset array and named `analog`, creates the PHY, and registers a simple provider. Init initializes analog, writes the common reference-clock/two-x1 setup value, then resets the digital block. Power-on powers the analog PHY and clears `MESON_PCIE_POWERDOWN`; power-off powers analog down and sets powerdown. Reset first resets analog, then asserts/deasserts the reset line with 500 us delays.

State and persistence: There is no mutable software state beyond resource pointers. Hardware state is fully reprogrammed by init/power/reset callbacks and reset controller state.

Dependencies and integration: It depends on the generic PHY core, reset arrays, regmap MMIO, and `dt-bindings/phy/phy.h`. Device tree must provide `amlogic,axg-pcie-phy`, reset resources, and an `analog` PHY reference. PCIe host drivers consume it through phandles.

Risks and test signals: Error handling returns immediately on analog failures, so PCIe bring-up should verify probe deferral and rollback through consumer retries. The static `MESON_PCIE_TWO_X1` setup assumes a two x1 topology. Test reset sequencing, analog failure propagation, power-off idempotence, and PCIe enumeration after cold boot and warm reset.
