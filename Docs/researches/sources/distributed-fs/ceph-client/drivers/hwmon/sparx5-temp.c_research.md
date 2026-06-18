
# sources/distributed-fs/ceph-client/drivers/hwmon/sparx5-temp.c

Purpose: platform hwmon driver for the Microchip Sparx5 SoC temperature sensor. It exposes a single temperature input and registers the channel as eligible for thermal-zone use.

Important APIs, types, and functions: `struct s5_hwmon` stores the MMIO base and enabled clock. `s5_temp_enable()` programs the conversion cycle field from the clock rate and sets the enable bit. `s5_read()` checks the valid bit in `TEMP_STAT`, extracts the 12-bit raw temperature, applies the documented linear conversion, and returns millidegrees. `s5_is_visible()` exposes only `temp1_input`.

Control flow, state, and persistence: probe allocates state, maps MMIO resource 0, enables the clock with `devm_clk_get_enabled()`, enables the sensor, and registers hwmon info. No software cache is maintained; every read hits MMIO.

Dependencies and integration points: uses platform devices, OF compatible `microchip,sparx5-temp`, MMIO accessors, clock framework, bitfield helpers, and hwmon thermal-zone registration flag.

Risks and test signals: reads return `-EAGAIN` until hardware marks data valid. Conversion depends on clock rate and register specification. Test invalid MMIO/clock probe paths, cycle field programming, valid-bit gating, raw-to-millidegree conversion at low/mid/high raw values, and integration with thermal zone registration.
