# sources/distributed-fs/ceph-client/drivers/watchdog/bd9576_wdt.c

## Purpose
This platform watchdog driver supports ROHM BD9576MUF and BD9573MUF PMIC watchdog blocks exposed by the ROHM MFD parent. It configures the hardware watchdog timing window through the parent regmap and feeds/enables the watchdog through firmware-described GPIO lines.

## Important APIs, types, and functions
`struct bd9576_wdt_priv` holds the enable GPIO, ping GPIO, parent regmap, device pointer, and embedded `watchdog_device`. The watchdog ops are `bd9576_wdt_start`, `bd9576_wdt_stop`, and `bd9576_wdt_ping`; the setup helpers are `find_closest_fast`, `find_closest_slow_by_fast`, `find_closest_slow`, and `bd957x_set_wdt_mode`. Probe uses `dev_get_regmap`, `devm_fwnode_gpiod_get`, `device_property_read_u32_array`, `watchdog_init_timeout`, and `devm_watchdog_register_device`.

## Control Flow
Probe allocates private state, obtains the parent regmap and two parent fwnode GPIOs, reads optional `rohm,hw-timeout-ms`, programs slow or window mode, then registers the watchdog. Start asserts the enable GPIO and immediately pulses the ping GPIO. Ping is a high-low pulse. Stop deasserts the enable GPIO. The watchdog core handles software timeout feeding against the programmed `min_hw_heartbeat_ms`/`max_hw_heartbeat_ms`.

## State and Persistence
Persistent runtime state is limited to GPIO descriptors, regmap pointer, and the registered watchdog. Hardware configuration persists in PMIC registers until the parent device or PMIC reset changes it. The driver does not persist state across reboot and uses `watchdog_stop_on_reboot`.

## Dependencies and Integration Points
The driver depends on the ROHM BD957x MFD, regmap, firmware properties, GPIO descriptors, and the watchdog core. Device-tree or firmware must provide `rohm,watchdog-enable`, `rohm,watchdog-ping`, and optional `rohm,hw-timeout-ms` on the parent node.

## Risks and Test Signals
Risks include invalid timing arrays, window-mode feeds that are too early, missing parent GPIO properties, and rounded hardware margins differing from requested values. Test signals should cover one-value and two-value `rohm,hw-timeout-ms`, bad GPIO/regmap probe deferral, start/ping/stop GPIO sequencing, nowayout behavior, and reboot stop handling.
