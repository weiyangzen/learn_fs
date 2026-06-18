# sources/distributed-fs/ceph-client/drivers/net/phy/bcm7xxx.c

## Purpose
`bcm7xxx.c` supports Broadcom BCM7xxx internal transceivers across 28 nm GPHY/EPHY, 40 nm EPHY, and 16 nm EPHY families. It applies hardware-specific AFE calibration recipes, enables APD/EEE, exposes stats, preserves stats over suspend, implements synthetic MMD access for 28 nm EPHY shadow registers, and registers many internal PHY IDs.

## Important APIs, Types, And Functions
`struct bcm7xxx_phy_priv` stores the per-PHY stats shadow array used by shared Broadcom stat helpers. The main init families are `bcm7xxx_28nm_config_init()`, `bcm7xxx_28nm_ephy_config_init()`, `bcm7xxx_16nm_ephy_config_init()`, and legacy `bcm7xxx_config_init()`. AFE recipes include `bcm7xxx_28nm_d0_afe_config_init()`, `bcm7xxx_28nm_e0_plus_afe_config_init()`, `bcm7xxx_28nm_a0_patch_afe_config_init()`, `bcm7xxx_28nm_ephy_01_afe_config_init()`, and `bcm7xxx_16nm_ephy_afe_config()`.

Other key functions are `bcm7xxx_28nm_ephy_read_mmd()` and `bcm7xxx_28nm_ephy_write_mmd()` for AN/PCS EEE registers, `bcm7xxx_28nm_get_tunable()` and `bcm7xxx_28nm_set_tunable()` for downshift, `bcm7xxx_28nm_suspend()` for stats preservation, and `bcm7xxx_28nm_probe()` for private allocation and optional clock enable. Macro templates build the `phy_driver` table for each process/interface family.

## Control Flow
Probe allocates stats storage sized by `bcm_phy_get_sset_count()`, enables an optional MDIO-device clock, and performs a dummy BMSR read to work around first-MDIO-read failures. For 28 nm GPHYs, config init derives revision/patch from dev flags or PHY ID bits, does a dummy read, selects the appropriate AFE workaround, enables jumbo frames, reads downshift, enables EEE only when downshift is disabled, and enables auto power down. Resume reapplies this full setup and restarts autonegotiation.

For 28 nm EPHYs, init may enter shadow mode 2, program bias trim and TL4 calibration reset for revision 0x01, enable 100TX EEE through shadowed PCS/AN registers, and enable APD through shadow mode 1. The synthetic MMD methods map a small set of standard AN/PCS MMD registers to shadow-mode-2 registers, returning `-EOPNOTSUPP` for unsupported devnum/regnum pairs.

For 16 nm EPHYs, the driver performs a long deterministic PLL/AFE/RCAL calibration sequence, computes adjusted RCAL codes from expansion register data, enables EEE, configures DLL auto power down and clock behavior, and enables APD. Legacy 40 nm/65 nm config enables 64-clock MDIO, toggles shadow mode, writes bias/false-carrier registers, and has an IDDQ suspend recipe.

## State And Persistence
State lives in hardware registers, the private stats shadow, optional clock enable state, and phylib advertised/tunable fields. Suspend snapshots Broadcom stats under `phydev->lock` before generic suspend. Calibration state is not persisted in software; resume replays the recipes.

## Dependencies And Integration Points
The driver uses phylib, Broadcom helper functions in `bcm-phy-lib.h`, Broadcom PHY IDs/flags from `brcmphy.h`, optional clock management, ethtool tunables/stats, and MDIO MMD constants. It integrates with device-tree/platform data through `phydev->dev_flags` for revision/patch and generic PHY internal flags.

## Risks And Edge Cases
Most values are hardware magic from vendor errata; small register or delay changes can affect analog link quality. Shadow mode access must be reset on all error paths to avoid corrupting later MDIO operations. The read_mmd/write_mmd implementation intentionally supports only EEE-related AN/PCS registers. EEE is disabled when downshift is enabled because the combination can prevent link-up; tunable changes restart autoneg. The 16 nm calibration sequence has many unchecked `bcm_phy_write_misc()` calls, so failed MDIO writes may not always abort immediately.

## Test Signals
Validation should cover every macro family: 28 nm GPHY downshift/EEE/APD behavior, 28 nm EPHY synthetic MMD reads for EEE registers, 16 nm EPHY link after resume, legacy suspend IDDQ mode, ethtool stats continuity across suspend, optional clock enable, and known revisions that select each AFE recipe. Link interoperability and analog compliance tests are especially important.
