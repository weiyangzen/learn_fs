<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phylib.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phylib.h

Purpose: Declares phylib-internal-but-shared helpers for PHY package management and low-level MMD access used across PHY implementation files and drivers compiled in the PHY subsystem.

Important APIs and types: Forward-declares `struct device_node`, `struct phy_device`, and `struct mii_bus`. Declares package accessors, package-relative C22 and MMD read/write helpers, one-shot package init/probe flags, explicit and devm package join/leave functions, OF package join helpers, and `mmd_phy_read()`/`mmd_phy_write()`.

Control flow: The header itself has no runtime flow. It provides the shared contract implemented by `phy_package.c` and `phy-core.c`, allowing PHY drivers and implementation files to join packages and perform package/global register accesses.

State and persistence: Owns no state. Its functions operate on runtime `phydev->shared`, `mii_bus->shared[]`, and MDIO hardware registers owned by implementation files and callers.

Dependencies and integration points: Included by `phy-core.c`, `phy_package.c`, and package-aware PHY drivers. It bridges package helpers to generic MDIO/MMD helpers without including full implementation details of `struct phy_package_shared`.

Risks: The header exposes unlocked `__phy_package_*` helpers, so callers must follow the same locking expectations as raw `__phy_read()`/`__phy_write()`. Prototype changes can break package-aware drivers. Because the shared package struct is opaque, callers must use accessors and cannot verify internal lifetime except through balanced join/leave calls.

Test signals: Build package-aware PHY drivers; join/leave and devm cleanup paths; direct and package-relative MMD access on C22 and C45 PHY packages; compile tests after signature changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phylib.h -->
