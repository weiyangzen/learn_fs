# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-cygnus-pcie.c

Purpose: Provides generic PHY power control for up to two Broadcom Cygnus PCIe PHYs sharing one configuration register.

Important APIs and types: `enum cygnus_pcie_phy_id` names PCIe0/PCIe1. `struct cygnus_pcie_phy_core` owns the shared base, mutex, and two child PHY records. `cygnus_pcie_power_config()` toggles per-PHY IDDQ bits and is wrapped by power-on/off `phy_ops`.

Control flow: probe requires child nodes, maps the shared register block, initializes a mutex, iterates available child nodes, reads each `reg` id, rejects invalid or duplicate ids, creates a child PHY, and registers a simple OF provider. Power-on clears the relevant IDDQ bit and waits 50 ms for SerDes stabilization. Power-off sets the bit.

State and persistence: Software state is the child id/core mapping. Hardware state is the IDDQ bit in the shared PCIe config register. The mutex serializes read-modify-write access for both PHYs.

Dependencies and integration: It depends on OF child-node binding, generic PHY, MMIO, and platform driver matching `brcm,cygnus-pcie-phy`. PCIe host nodes consume child PHY phandles.

Risks and test signals: Invalid or duplicated child `reg` properties abort probe. Test both PHY ids, concurrent power operations, missing child nodes, invalid ids, and PCIe link training after the 50 ms analog stabilization delay.
