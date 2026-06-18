# sources/distributed-fs/ceph-client/drivers/power/supply/max1721x_battery.c

Purpose: implements 1-Wire support for MAX17211/MAX17215 standalone fuel gauges. It binds to 1-Wire family ID `0x26`, creates a unique battery power-supply name from the slave ROM ID, and reports gauge measurements plus cached manufacturer, model, and serial strings.

Important APIs/types/functions: `struct max17211_device_info` contains the dynamically named `power_supply_desc`, W1 device pointer, regmap, RSense, and cached string buffers. `devm_w1_max1721x_add_device()` is the add-slave entry point. `max1721x_battery_get_property()` handles power-supply reads. `get_string()` and `get_sn_string()` decode nonvolatile string/serial registers. Regmap access tables define valid volatile/nonvolatile W1 register windows.

Control flow: when a W1 slave appears, the driver allocates info, formats `max1721x-<romid>` as the battery name, configures a no-thermal battery descriptor, initializes a W1 regmap, reads RSense with a 10 milliohm fallback, reads manufacturer/device strings or falls back to default names based on `DEVNAME`, reads serial registers, and registers the power supply. Property reads access raw registers through W1 regmap, convert units, and for strings perform a dummy read before returning cached buffers.

State and persistence: runtime state is per-W1-slave and devm-managed through the slave device. Strings and RSense are cached at probe. The driver performs no persistent writes to nonvolatile gauge memory.

Dependencies and integration: depends on Linux W1 family registration, `devm_regmap_init_w1()`, and power-supply core. It exports `MODULE_ALIAS("w1-family-26")` for auto-loading.

Risks: `PRESENT` uses `!(reg & MAX172XX_BAT_PRESENT)` even though the bit comment says battery-connected, so polarity deserves hardware validation. The string buffers may contain embedded NULs or unterminated data if the chip returns unexpected characters, though allocation leaves trailing zeroes. Current conversion divides by RSense and relies on fallback for zero. Test signals include hotplug of multiple W1 gauges, W1 register read failure paths, fallback model/manufacturer naming, serial formatting, and property unit validation against known gauge readings.
