# sources/distributed-fs/ceph-client/drivers/net/phy/realtek/realtek_hwmon.c

Purpose: Adds optional hwmon temperature sensor support for Realtek RTL822x PHYs. It exposes current temperature and configured maximum temperature through a devm-registered hwmon device and clears the over-temperature alarm during initialization.

Important APIs and functions: `rtl822x_hwmon_init()` is the exported local initializer declared in `realtek.h`. Internal helpers include `rtl822x_hwmon_get_temp()` for signed 10-bit half-degree conversion and `rtl822x_hwmon_read()` for `hwmon_temp_input` and `hwmon_temp_max`. Static `hwmon_ops`, channel info, and chip info describe a read-only temperature channel.

Control flow: Init clears alarm bits in vendor MMD2 register `RTL822X_VND2_TSALRM`, then registers a hwmon device with `phydev` as driver data. Reads fetch raw sensor data from `RTL822X_VND2_TSRR` for input or `RTL822X_VND2_TSSR` shifted by six for maximum threshold, convert from signed 10-bit units at 0.5 degrees C to millidegrees C, and return `-EINVAL` for unsupported attributes.

State and persistence: No private state is allocated. The hwmon device is devm-managed under the PHY MDIO device. Hardware temperature/alarm/threshold state persists in vendor MMD registers; software exposes it read-only.

Dependencies and integration: Depends on the hwmon subsystem, phylib MMD accessors, Realtek main driver calling `rtl822x_hwmon_init()`, and Kconfig preventing impossible built-in/module dependencies.

Risks and test signals: Risks include ignoring negative MDIO read errors because raw reads are masked or shifted directly, signed conversion mistakes around bit 9, and stale threshold/alarm semantics across chip variants. Test hwmon registration, temp input and max reads for positive and negative raw values, MDIO read-error handling, alarm clear on init, and build/runtime behavior with hwmon disabled.
