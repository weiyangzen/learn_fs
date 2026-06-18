# sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303_mdio.c

Purpose: MDIO transport wrapper for LAN9303/LAN9354 managed-mode switches. It maps LAN9303 32-bit registers onto paired 16-bit MDIO accesses and provides direct nested PHY operations.

Important APIs/types/functions: `PHY_ADDR()` and `PHY_REG()` translate offsets; `lan9303_mdio_read()`/`write()` implement custom regmap callbacks under nested `mdio_lock`; `lan9303_mdio_phy_read()`/`write()` use nested mdiobus helpers. Registered as an `mdio_driver`.

Control flow: probe allocates state, creates custom regmap with shared register tables, stores drvdata, sets `chip.dev`, chooses direct MDIO PHY ops, and calls `lan9303_probe()`. Remove/shutdown delegate to core helpers and shutdown clears drvdata.

State and persistence: wrapper stores `mdio_device` and shared chip. Hardware and core state hold configuration; the wrapper has no cache beyond the regmap object.

Dependencies and integration: MDIO device infrastructure, PHY/mdiobus helpers, nested MDIO locking, regmap custom callbacks, LAN9303 core. OF matches `"smsc,lan9303-mdio"` and `"microchip,lan9354-mdio"`.

Risks and test signals: risks are 32-bit access tearing, bad PHY/register translation, weak low-level read/write error propagation, and lock nesting. Test byte-order/chip-id reads, PHY reads on user ports, no lockdep warnings, and LAN9303/LAN9354 matches.
