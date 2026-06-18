# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_hw.h

## Purpose
Defines the ATL1E/L1E hardware contract used by the Atheros Attansic L1E Ethernet driver. The file is almost entirely declarative: it exposes hardware helper prototypes, PCI/MMIO register offsets, bit masks, interrupt masks, PHY register fields, WOL fields, DMA queue controls, RSS fields, descriptor base-address registers, and MAC statistic register ranges consumed by `atl1e_main.c`, `atl1e_hw.c`, ethtool support, and module option handling.

## Important APIs, Types, and Functions
The exported prototypes are the hardware abstraction surface: `atl1e_reset_hw`, `atl1e_init_hw`, `atl1e_read_mac_addr`, `atl1e_phy_commit`, `atl1e_get_speed_and_duplex`, `atl1e_auto_get_fc`, multicast helpers `atl1e_hash_mc_addr` and `atl1e_hash_set`, MDIO helpers `atl1e_read_phy_reg` and `atl1e_write_phy_reg`, EEPROM helpers, power-saving helpers, `atl1e_phy_init`, `atl1e_force_ps`, and `atl1e_restart_autoneg`.

The important register families are PCI power/capability and VPD registers (`REG_PM_CTRLSTAT`, `REG_DEVICE_CTRL`, `REG_VPD_CAP`, `REG_VPD_DATA`), SPI/TWSI flash registers (`REG_SPI_FLASH_CTRL`, opcode registers, `REG_TWSI_CTRL`), global MAC/GPHY control (`REG_MASTER_CTRL`, `REG_GPHY_CTRL`, `REG_IDLE_STATUS`, `REG_MDIO_CTRL`, `REG_PHY_STATUS`), MAC programming (`REG_MAC_CTRL`, `REG_MAC_STA_ADDR`, `REG_RX_HASH_TABLE`, `REG_MTU`, `REG_WOL_CTRL`), descriptor/DMA/RX-page programming (`REG_DESC_BASE_ADDR_HI`, `REG_TPD_BASE_ADDR_LO`, `REG_HOST_RXF*`, `REG_DMA_CTRL`, `REG_MB_TPD_PROD_IDX`), interrupt status/mask definitions (`REG_ISR`, `REG_IMR`, `IMR_NORMAL_MASK`, `ISR_TX_EVENT`, `ISR_RX_EVENT`), and PHY/MII-specific fields (`MII_AT001_*`).

## Control Flow and State
There is no runtime control flow in this header. Its state model is hardware-backed: driver state persists in MMIO registers, PHY registers, EEPROM/VPD/SPI contents, descriptor rings referenced by DMA base-address registers, interrupt status bits, and MAC statistic counters. Some definitions encode multi-register state: the MAC address spans two station-address words, multicast filtering spans two hash table registers, RX pages have high/low base plus valid/write-offset registers, and WOL pattern state spans control and length registers.

## Dependencies and Integration Points
Includes `linux/types.h` and `linux/mii.h`, forward-declares `struct atl1e_adapter` and `struct atl1e_hw`, and is included through the ATL1E driver headers. It integrates with the PCI core through config-space offsets, with the Linux netdev stack through speed/duplex/VLAN/checksum semantics, with MDIO/MII helper definitions, and with the DMA API by defining 32-bit low/high address programming contracts.

## Risks
This file is a hardware ABI. Incorrect offsets, masks, shifts, or interrupt grouping can produce silent packet loss, broken DMA, unhandled interrupts, invalid PHY negotiation, bad WOL behavior, or register writes to reserved locations. Several definitions are shared assumptions with `atl1e_main.c`; for example `IMR_NORMAL_MASK` controls which interrupts the ISR can observe, and `REG_HOST_RXF*_PAGE*` arrays in the main file rely on these offsets matching the hardware page layout. The single high-address register model means 64-bit DMA support is deliberately constrained elsewhere; any future change to DMA masks must honor this register layout.

## Test Signals
Useful signals are compile coverage for `atl1e_main.c`, `atl1e_hw.c`, and ethtool code; probe/open on supported L1E/L2E devices; link negotiation at 10/100/1000; interrupt storms or missing RX/TX completions; register dump comparisons against known hardware; WOL suspend/resume tests; multicast/promiscuous filtering; VLAN stripping/insertion; and DMA traffic tests across ring wrap and reset paths.
