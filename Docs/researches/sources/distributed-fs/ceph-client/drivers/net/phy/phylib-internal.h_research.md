<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phylib-internal.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phylib-internal.h

Purpose: Declares private phylib interfaces shared between implementation files but not exposed as the primary public PHY API.

Important APIs and types: Forward-declares `struct mdio_device` and `struct phy_device`; exposes `mdio_bus_type` and `mdio_bus_class`; declares internal helpers `phy_supported_speeds()`, `of_set_phy_supported()`, `of_set_phy_eee_broken()`, `of_set_phy_timing_role()`, `phy_speed_down_core()`, `phy_check_downshift()`, `mdiobus_register_device()`, `mdiobus_unregister_device()`, and `genphy_c45_read_eee_adv()`.

Control flow: The header has no executable flow. It forms the compile-time contract that lets `phy.c`, `phy-core.c`, `phy_device.c`, `phy_led_triggers.c`, and package/device registration code call helpers that remain internal to the PHY library implementation.

State and persistence: Owns no state. The declared bus/class globals are defined elsewhere and persist for the phylib module lifetime after `phy_init()`.

Dependencies and integration points: Included by implementation files needing cross-file internal helpers. It intentionally avoids pulling in heavy headers by using forward declarations.

Risks: Prototype drift between this header and implementations can break multiple phylib objects. Because these helpers are internal, moving declarations to public headers would widen ABI/API surface unintentionally. Bus/class globals must remain initialized before users rely on them.

Test signals: Full phylib build coverage; module init/exit for bus/class availability; compile tests after changing helper signatures or moving internal functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phylib-internal.h -->
