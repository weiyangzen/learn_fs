# sources/distributed-fs/ceph-client/drivers/power/supply/rt5033_battery.c

Purpose: implements a small Richtek RT5033 fuel-gauge driver. It registers an I2C battery power supply that reports voltage, average voltage, open-circuit voltage, battery presence, capacity, and status.

Important APIs, types, and functions: `struct rt5033_battery` stores the I2C client, fuel-gauge regmap, and registered power supply. `rt5033_battery_get_watt_prop()` selects high/low fuel-gauge voltage registers and converts 12-bit values to microvolts. `rt5033_battery_get_capacity()` reads SOC high byte as percentage-like capacity. `rt5033_battery_get_present()` checks the fuel-gauge config battery-present bit. `rt5033_battery_get_status()` obtains charging status from a supplier power supply rather than local fuel-gauge state.

Control flow: probe checks SMBus byte functionality, allocates state, creates an 8-bit regmap over the I2C fuel gauge address, stores client data, and registers `rt5033-battery` with fwnode and driver data. All property reads are synchronous regmap reads or supplier property lookups.

State and persistence behavior: the driver maintains no persistent state and no periodic cache. It is a read-only power supply surface over hardware fuel-gauge registers. Status is dynamically inherited from the charger supplier when available; otherwise UNKNOWN is returned.

Dependencies and integration points: depends on I2C, regmap, RT5033 private register definitions, and the power-supply supplier mechanism. It binds by I2C ID `rt5033-battery` or OF compatible `richtek,rt5033-battery`.

Risks: most `regmap_read()` return values are ignored, so failed reads can leave uninitialized local values. Capacity uses only the SOC high byte and ignores any fractional low byte. Supplier status lookup can report UNKNOWN if the charger supply is absent or not linked in DT. Test signals include I2C functionality rejection, regmap init failure, supplier status linkage, voltage conversion against known register samples, present-bit polarity, and behavior when reads fail.
