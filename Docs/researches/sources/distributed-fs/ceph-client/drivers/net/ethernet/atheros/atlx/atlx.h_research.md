# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atlx.h

Purpose: `atlx.h` is the shared hardware definition header for Attansic/Atheros Ethernet drivers. It centralizes common error codes, speed/duplex/media constants, PCI/PM/VPD/SPI/TWSI/MDIO/MAC/WOL/register offsets, PHY bit definitions, wake flags, and a shared SPI flash command descriptor used by `atlx.c` and concrete drivers such as `atl2.c`.

Important APIs/types/functions: it is primarily macro data rather than callable code. Important groups include `REG_MASTER_CTRL`, `REG_MDIO_CTRL`, `REG_MAC_CTRL`, `REG_RX_HASH_TABLE`, `REG_WOL_CTRL`, interrupt/mask-related constants, MII advertisement and PHY status constants, WOL flags such as `ATLX_WUFC_MAG`, and `struct atlx_spi_flash_dev`. It also defines canonical speed values and error codes (`ATLX_ERR_PHY`, `ATLX_ERR_PHY_SPEED`, `ATLX_ERR_PHY_RES`) consumed by hardware helper functions.

Control flow: the constants guide reset, PHY MDIO transactions, MAC configuration, multicast filtering, EEPROM/SPI probing, WOL setup, link speed detection, and feature toggling in implementation files. For example, the `REG_MDIO_CTRL` bit fields encode read/write transactions; `REG_MAC_CTRL` bits govern TX/RX enablement, VLAN stripping, promiscuous/all-multicast modes, duplex, CRC, padding, and broadcast acceptance.

State and persistence: no state is stored in the header, but many constants address persistent or semi-persistent hardware areas: PCI power-management registers, VPD, SPI flash, TWSI, MAC station address, and WOL state. The header also defines the hardware vocabulary for runtime state stored in driver-private structures.

Dependencies and integration points: `atlx.h` depends only on basic Linux module/types headers and is included by both shared helper code and L2-specific code. It bridges netdev/PHY concepts to raw register bits and therefore must match hardware documentation closely.

Risks: the header contains a placeholder `TWSI_CTRL_SMB_SLV_ADDR` macro with a FIXME and no value, which would be unsafe if used in expressions. Any incorrect bit mask here affects multiple drivers. Because the header is broad and hardware-facing, test signals are mostly integration tests on real devices: MDIO read/write completion, MAC enable/disable, multicast hash acceptance, WOL wake, SPI/VPD reads, and link speed resolution.
