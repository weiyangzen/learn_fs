# sources/distributed-fs/ceph-client/drivers/phy/st/phy-spear1310-miphy.c

Purpose: SPEAr1310 MiPHY provider for PCIe/SATA-capable PHY instances, with implemented initialization for PCIe mode.

Important APIs, types, and functions: `struct spear1310_miphy_priv` stores PHY ID, selected mode, misc syscon, and PHY pointer. `spear1310_miphy_pcie_init()` programs PLL ratio and port-specific PCIe/SATA config bits; `spear1310_miphy_pcie_exit()` clears them. `spear1310_miphy_xlate()` reads one mode cell (`SATA` or `PCIE`).

Control flow: probe obtains `misc` syscon and `phy-id`, creates one PHY, and registers custom xlate. Init checks selected mode and only performs PCIe programming when mode is `PCIE`; SATA mode returns success without register writes. Exit similarly only clears PCIe.

State and persistence: selected mode is stored in `priv->mode` after xlate, and PHY ID selects port-specific bit positions. Hardware state persists in misc syscon registers.

Dependencies and integration points: generic PHY, syscon/regmap, SPEAr1310 PCIe/SATA controller glue, DT `phy-id` and mode phandle cell.

Risks: SATA mode is accepted but not configured by this driver; that may reflect external SATA setup but can confuse consumers. A single `priv->mode` means conflicting consumers can overwrite mode. Macro-generated bit masks depend on valid ID 0..2.

Test signals: PCIe init/exit register readback for each ID, invalid ID handling, DT xlate mode validation, and SATA consumer behavior to confirm whether no-op is intended.
