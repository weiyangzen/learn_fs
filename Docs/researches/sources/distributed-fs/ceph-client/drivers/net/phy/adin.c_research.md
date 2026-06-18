# sources/distributed-fs/ceph-client/drivers/net/phy/adin.c

## Purpose
Implements the Analog Devices ADIN1200 and ADIN1300 industrial Ethernet PHY driver. It handles interface-mode setup, RGMII/RMII board properties, downshift, EDPD, fast link-down, clock output, MDI/MDIX control, interrupts, statistics, Clause 45-over-Clause 22 access, soft reset, and ethtool cable diagnostics.

## Important APIs, Types, and Functions
The driver registers two `struct phy_driver` entries matching `PHY_ID_ADIN1200` and `PHY_ID_ADIN1300`. Important private types are `adin_cfg_reg_map`, `adin_clause45_mmd_map`, `adin_hw_stat`, and `adin_priv`. Key functions include `adin_config_init`, `adin_config_rgmii_mode`, `adin_config_rmii_mode`, `adin_config_clk_out`, `adin_config_zptm100`, `adin_config_aneg`, `adin_read_status`, `adin_soft_reset`, `adin_get_tunable`, `adin_set_tunable`, `adin_read_mmd`, `adin_write_mmd`, `adin_phy_config_intr`, `adin_phy_handle_interrupt`, and the cable-test pair `adin_cable_test_start` and `adin_cable_test_get_status`.

## Control Flow and State
Probe allocates `adin_priv` to accumulate ethtool counters. `config_init` sets `mdix_ctrl` to auto, programs RGMII or RMII according to `phydev->interface`, enables default downshift and EDPD, configures optional clock output, and applies the low common-mode impedance property. Autoneg setup clears diagnostic clock mode, enables linking, applies requested MDI/MDIX mode, then delegates to `genphy_config_aneg`. Status reads update MDI/MDIX from control/status registers before `genphy_read_status`. Cable test disables normal linking, starts cable diagnostics in vendor MMD registers, polls for completion, then reports pair result and fault length through ethtool netlink.

## Dependencies and Integration Points
Depends on phylib Clause 22 access, vendor MMD access, generic PHY helpers, ethtool tunables and cable-test reporting, device properties such as `adi,rx-internal-delay-ps`, `adi,tx-internal-delay-ps`, `adi,fifo-depth-bits`, `adi,phy-output-clock`, `adi,phy-output-reference-clock`, and `adi,low-cmode-impedance`. It exposes MDIO device table entries for module autoloading.

## Risks and Test Signals
Risks include unsupported board-property values silently falling back to defaults, wrong RGMII delay or RMII FIFO depth, Clause 45 translation gaps returning `-EINVAL`, counter accumulation double-counting if hardware counters are not clear-on-read as assumed, and cable diagnostics leaving normal link state disabled on error. Test signals include RGMII/RMII mode bring-up, ethtool tunable get/set, interrupt-driven link changes, `ethtool --cable-test`, suspend/resume, and MMD EEE register access through the custom read/write callbacks.
