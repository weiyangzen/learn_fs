<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-i2c.c

Purpose: library that exposes PHYs reachable over I2C, commonly inside SFP modules, as an MDIO `mii_bus`.

Important APIs/types/functions: exported `mdio_i2c_alloc` creates a bus over an `i2c_adapter` for `enum mdio_i2c_proto`. Helpers implement default C22/C45 I2C transfers, SMBus-byte fallback, RollBall SFP page/password protocol, and functionality checks.

Control flow: default transfers map MDIO PHY IDs to I2C addresses `phy_id + 0x40`, excluding SFP EEPROM addresses 0x50/0x51. C45 uses one address/write pointer phase then read/write data. SMBus fallback reads/writes high and low bytes under an I2C segment lock. RollBall initializes a password, page-switches to page 3 around each transaction, writes command/data registers, polls for completion, and restores the original page.

State and persistence: the returned bus stores the adapter in `priv`; persistent module state is absent. RollBall temporarily changes SFP page state but restores it under lock.

Dependencies/integration: depends on I2C/SMBus APIs, SFP constants, phylib, and callers that register/free the returned bus. It is library-mode Kconfig, not a standalone device driver.

Risks and test signals: risks include collisions with SFP EEPROM pages, page-restore failures after I2C errors, long RollBall polling delays, SMBus fallback endianness, and unsupported I2C functionality. Tests should mock adapters for default, SMBus-only, and RollBall protocols, including error paths and reserved address filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-i2c.c -->
