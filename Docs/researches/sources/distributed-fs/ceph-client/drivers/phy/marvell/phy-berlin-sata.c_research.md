<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-berlin-sata.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-berlin-sata.c

Purpose: Implements the Marvell Berlin SATA PHY provider for Berlin2 and Berlin2Q SoCs. It exposes one generic PHY per child DT lane and programs host VSA, MBUS, per-port SCR, and vendor-specific PHY registers for SATA Gen3 operation.

Important APIs and types: `struct phy_berlin_priv` holds the MMIO base, clock, spinlock, child PHY descriptors, and SoC-specific PHY base offset. `struct phy_berlin_desc` stores per-lane generic PHY, power-down bit, and lane index. Main callbacks are `phy_berlin_sata_power_on()`, `phy_berlin_sata_power_off()`, and `phy_berlin_sata_phy_xlate()`.

Control flow: Probe maps the SATA register resource, gets the controller clock, counts child nodes, chooses `BG2_PHY_BASE` or `BG2Q_PHY_BASE`, creates child PHYs, and powers them off. Power-on enables the clock, serializes shared VSA accesses with a spinlock, clears the lane power-down bit, configures MBUS request sizes, sets SATA mode, 25 MHz reference, Gen3 maximum speed, 40-bit width, max PLL rate, and controller Gen3 speed. Power-off reverses only the power-down bit.

State and persistence: Runtime state is per-device `priv` plus per-lane descriptors. Hardware register programming persists until power-off, reset, or another consumer changes the PHY. The driver does not store the active mode because it only supports SATA.

Dependencies and integration points: Depends on generic PHY, OF child nodes with `reg`, platform MMIO, and an unnamed clock. It is consumed by SATA controller DT phandles using the lane index.

Risks: Shared VSA address/data access is protected, but `clk_prepare_enable()` return values are ignored. Invalid child `reg` values abort probe after putting the current node. Register programming assumes 25 MHz reference and Gen3 capabilities. Partial power-off does not undo MBUS or speed settings.

Test signals: Build with Berlin SATA PHY enabled, DT probe with both compatible strings, two-lane xlate, SATA link negotiation at 1.5/3/6 Gbps, suspend/resume or remove/reprobe, and register readback of power-down and SCR speed fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-berlin-sata.c -->
