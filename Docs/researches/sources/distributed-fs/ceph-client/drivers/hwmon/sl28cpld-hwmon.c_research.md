
# sources/distributed-fs/ceph-client/drivers/hwmon/sl28cpld-hwmon.c

Purpose: platform hwmon driver for the Kontron SL28 CPLD fan counter. It exposes one read-only fan input.

Important APIs, types, and functions: `struct sl28cpld_hwmon` stores the parent regmap and register offset from the device property `reg`. `sl28cpld_hwmon_read()` reads the fan register, interprets the high bit as an x8 scale flag, extracts the 7-bit count with `FIELD_GET()`, and converts a one-second, two-pulse-per-revolution counter to RPM. The hwmon chip info declares only `HWMON_F_INPUT`.

Control flow, state, and persistence: probe requires a parent device and parent regmap, reads the child offset from firmware properties, then registers `sl28cpld_hwmon`. No state is cached or persisted by the driver.

Dependencies and integration points: integrates as an OF platform child compatible `kontron,sl28cpld-fan` under an MFD or parent exposing a regmap. Uses hwmon info API, regmap, platform device helpers, and property API.

Risks and test signals: a missing parent, regmap, or `reg` property fails probe. Conversion assumes 1000 ms counter period and two pulses per revolution. Test both scaled and unscaled register values, invalid property paths, and regmap read error propagation.
