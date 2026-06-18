# sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-pcie.c

Purpose: Provides a small Renesas R-Car Gen3 PCIe PHY driver for R8A77980, controlling the PHY power-down bit in the PCIe PHY control register.

Important APIs/types/functions: `struct rcar_gen3_phy` stores the generic PHY, spinlock, and MMIO base. `rcar_gen3_phy_pcie_modify_reg()` serializes read-modify-write updates. PHY ops are `r8a77980_phy_pcie_power_on()` and `_power_off()`.

Control flow: Probe requires DT, maps MMIO, allocates state, initializes the spinlock, enables runtime PM, creates the PHY, registers a simple OF provider, and leaves power control to consumers. Power-on clears `PHY_CTRL_PHY_PWDN`; power-off sets it. Remove disables runtime PM.

State and persistence: Runtime state is only the MMIO base and lock. The power-down bit persists in hardware until the next power op or reset. Runtime PM is enabled for phy-core management, but there are no custom PM callbacks.

Dependencies and integration points: Depends on generic PHY, platform MMIO, OF, spinlocks, and runtime PM. PCIe controller nodes consume this PHY through OF.

Risks: The driver supports only the R8A77980 register layout. Any new compatible with a different offset or bit would need match data rather than reusing this file blindly. Error paths correctly disable runtime PM, so future resource additions should preserve that balance.

Test signals: Probe `renesas,r8a77980-pcie-phy`, verify provider registration, power-cycle through the PCIe host, inspect `PHY_CTRL_PHY_PWDN` transitions, and remove/unbind to confirm runtime PM disable.
