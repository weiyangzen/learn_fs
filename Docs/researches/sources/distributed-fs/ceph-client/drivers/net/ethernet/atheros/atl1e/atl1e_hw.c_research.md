# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_hw.c

## Purpose
`atl1e_hw.c` implements low-level hardware services for ATL1E/L2E devices: EEPROM/VPD detection and reads, MAC address retrieval/programming, multicast hash setup, MDIO PHY register access, PCIe initialization, PHY advertisement/reset/initialization, MAC/DMA reset, base hardware initialization, link speed/duplex reporting, and autoneg restart.

## Important APIs, types, and functions
EEPROM and identity functions include `atl1e_check_eeprom_exist()`, `atl1e_read_eeprom()`, `atl1e_write_eeprom()`, `atl1e_get_permanent_address()`, `atl1e_read_mac_addr()`, and `atl1e_hw_set_mac_addr()`. `atl1e_check_eeprom_exist()` clears VPD enable in SPI flash control and interprets PCIe capability data; notably it returns `0` when EEPROM exists. `atl1e_get_permanent_address()` triggers TWSI load if EEPROM exists and validates the station address.

PHY access is implemented by `atl1e_read_phy_reg()` and `atl1e_write_phy_reg()`, which program `REG_MDIO_CTRL`, wait for `MDIO_START | MDIO_BUSY` to clear, and return `AT_ERR_PHY` on timeout. `atl1e_phy_setup_autoneg_adv()` derives MII advertisement and 1000T control shadows from `hw->media_type` and `hw->nic_type`. `atl1e_phy_commit()`, `atl1e_phy_init()`, and `atl1e_restart_autoneg()` apply PHY reset/autoneg sequences. `atl1e_reset_hw()` soft-resets MAC/DMA and waits for idle, while `atl1e_init_hw()` initializes PCIe, clears multicast hash, and initializes PHY.

## Control flow and state behavior
Initialization flows through PCIe tweak, multicast hash clear, GPHY reset, PHY debug patch writes, link-change interrupt enable, advertisement setup, and BMCR reset/autoneg restart. `hw->phy_configured` gates repeated initialization; `hw->re_autoneg` requests renegotiation on the next PHY init. Hardware state persists in VPD/EEPROM, station address registers, MDIO registers, and MMIO reset/configuration registers.

## Dependencies and integration points
The file depends on Linux PCI, delay, MII, CRC, and register definitions from `atl1e_hw.h` via `atl1e.h`. It is consumed by main lifecycle code for reset/init/link and by ethtool for EEPROM, register, link, and autoneg operations.

## Risks
`atl1e_write_eeprom()` is a stub that returns true without writing, which makes ethtool EEPROM writes appear successful while doing nothing. `atl1e_check_eeprom_exist()` uses inverted semantics compared with ATL1C, increasing caller confusion risk. MDIO timeout handling logs PCIe linkdown suspicion in `atl1e_phy_commit()` but generally returns coarse driver error constants. PHY init uses hard-coded debug magic values; hardware-revision mistakes can affect link quality or power. `atl1e_read_mac_addr()` returns `AT_ERR_EEPROM` instead of falling back to a random MAC, so caller behavior must handle failure.

## Test signals
Signals include valid MAC retrieval from EEPROM/VPD, no MDIO busy timeouts, successful PHY init and link interrupts, correct speed/duplex from `MII_AT001_PSSR`, stable reset idle detection, multicast hash behavior, ethtool EEPROM read/write truthfulness, and link recovery after advertisement changes.
