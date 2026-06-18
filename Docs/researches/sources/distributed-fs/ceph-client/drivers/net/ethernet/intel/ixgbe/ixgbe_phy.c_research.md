# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_phy.c

## Purpose
`ixgbe_phy.c` implements generic ixgbe PHY, MDIO, MII bus, SFP/QSFP module, I2C EEPROM, link advertisement, PHY reset, overtemperature, and copper PHY power support. It is the hardware-facing layer that identifies PHY types, reads and writes MDIO/I2C registers with the required synchronization, programs link capabilities, validates optical modules, and exposes an MDIO bus to the kernel.

## Important APIs and functions
PHY identity and reset are handled by `ixgbe_identify_phy_generic`, `ixgbe_probe_phy`, `ixgbe_get_phy_id`, `ixgbe_get_phy_type_from_id`, `ixgbe_reset_phy_generic`, and `ixgbe_reset_phy_nl`. MDIO register access is split into unlocked MDI transactions (`ixgbe_read_phy_reg_mdi`, `ixgbe_write_phy_reg_mdi`) and locked wrappers (`ixgbe_read_phy_reg_generic`, `ixgbe_write_phy_reg_generic`) that acquire `hw->phy.phy_semaphore_mask`.

MII bus integration is provided by `ixgbe_mii_bus_init` and its Clause 22/45 read/write helpers. X550EM_A gets special handlers that include `IXGBE_GSSR_TOKEN_SM` and `IXGBE_GSSR_PHY0_SM`, and `ixgbe_x550em_a_has_mii` ensures only the first SoC function registers the shared MDIO bus.

Link setup and capability logic is in `ixgbe_setup_phy_link_generic`, `ixgbe_setup_phy_link_speed_generic`, `ixgbe_get_copper_link_capabilities_generic`, `ixgbe_get_copper_speeds_supported`, `ixgbe_check_phy_link_tnx`, and `ixgbe_setup_phy_link_tnx`. Module handling is in `ixgbe_identify_module_generic`, `ixgbe_identify_sfp_module_generic`, `ixgbe_identify_qsfp_module_generic`, and `ixgbe_get_sfp_init_sequence_offsets`.

I2C support includes combined 16-bit operations (`ixgbe_read_i2c_combined_generic_int`, `ixgbe_write_i2c_combined_generic_int`), EEPROM helpers (`ixgbe_read_i2c_eeprom_generic`, `ixgbe_read_i2c_sff8472_generic`, `ixgbe_write_i2c_eeprom_generic`), byte operations with locked and unlocked variants, and bit-banged primitives for start, stop, clock/data transitions, ACK polling, and bus clear.

## Control flow
PHY identification first sets a default semaphore mask based on LAN ID, then either probes a management-selected PHY address or scans all possible addresses. A successful probe uses `mdio45_probe`, reads PHY IDs, maps known IDs to ixgbe PHY types, and falls back to copper or generic PHY based on extended PMA abilities.

Generic reset identifies the PHY if needed, skips reset for no PHY, overtemperature shutdown, or management firmware veto, writes `MDIO_CTRL1_RESET`, then polls for self-clear or X550EM external-t PHY alarm completion. NL PHY reset performs a reset, retrieves EEPROM offsets for the SFP init sequence, then interprets EEPROM control/data/delay records to program PHY PMA/PMD registers.

Link setup reads supported speeds, filters advertised speeds through `hw->phy.autoneg_advertised`, writes 10G/5G/2.5G/1G/100M advertisement registers, and restarts autoneg unless management veto is active. TNX setup follows a similar path with TNX-specific registers.

SFP/QSFP identification reads EEPROM identifiers and capability bytes, derives `hw->phy.sfp_type`, sets `sfp_setup_needed` when the module changes, detects multispeed fiber, assigns a vendor-specific `hw->phy.type`, and enforces Intel optics policy unless device capabilities or `allow_unsupported_sfp` permit otherwise. I2C read/write paths acquire the SW/FW semaphore when requested, bit-bang device address, register offset, data and ACKs, retry on failure, and clear the bus before retrying.

## State and persistence
The file updates `hw->phy.phy_semaphore_mask`, `hw->phy.mdio.prtad`, `hw->phy.id`, `hw->phy.revision`, `hw->phy.type`, `hw->phy.sfp_type`, `hw->phy.sfp_setup_needed`, `hw->phy.multispeed_fiber`, `hw->phy.speeds_supported`, and `hw->phy.autoneg_advertised`. It also stores the registered `mii_bus` in `adapter->mii_bus`. Hardware state persists in MDIO, MSCA/MSRWD, I2CCTL, PHY control, AN advertisement, EEPROM, and module EEPROM registers until hardware reset or later driver writes.

## Dependencies and integration points
This file depends on Linux PCI, delay, iopoll, scheduler, MDIO/MII bus APIs, ixgbe MMIO helpers, `hw->mac.ops` for SW/FW semaphore and media/capability callbacks, `hw->eeprom.ops.read`, and netdev/device-managed allocation via the adapter backpointer. It integrates with probe/open/reset paths, ethtool link settings, module detection, thermal/sysfs support through PHY/module data, and board-specific MAC operation tables.

## Risks and edge cases
The main risks are hardware timeouts, semaphore contention, management firmware vetoes, unsupported or misidentified optics, and bus lockups. I2C operations have side effects on shared module buses and rely on exact timing and ACK behavior. `ixgbe_reset_phy_nl` interprets EEPROM data blocks and can fail on corrupt offsets or bad control words. X550EM_A MDIO bus ownership is topology-specific and assumes fixed root ports. Unsupported SFP enforcement can intentionally reject working third-party optics unless override is enabled.

## Test signals
Tests and lab validation should include PHY discovery across known IDs, absence of PHY on fiber media, MDIO Clause 22/45 reads through the registered bus, SW/FW semaphore contention, SFP/QSFP insert/remove and vendor policy handling, corrupted or missing EEPROM offset handling, I2C NACK and stuck-bus recovery, autoneg advertisement for 100M/1G/2.5G/5G/10G, management-veto reset suppression, overtemperature behavior, and copper PHY low-power transitions.
