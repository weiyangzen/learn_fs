
# sources/distributed-fs/ceph-client/drivers/hwmon/smpro-hwmon.c

Purpose: platform hwmon driver for Ampere Altra SMPro logical sensors. It exposes SoC, VRD, DIMM, and RCA temperature, voltage, current, and power channels with labels.

Important APIs, types, and functions: `struct smpro_hwmon` wraps the parent regmap. `struct smpro_sensor` maps each channel to a main register, optional extension register, and label. `smpro_read_temp()`, `smpro_read_in()`, `smpro_read_curr()`, and `smpro_read_power()` read regmap values and scale them into hwmon units. `smpro_read_string()` returns channel labels. `smpro_is_visible()` hides unavailable temperature channels when their register reads as `0xffff`.

Control flow, state, and persistence: probe allocates state, fetches the parent regmap, and registers with `devm_hwmon_device_register_with_info()`. There is no cache; each read queries the SMPro regmap. Threshold registers are read-only from this driver.

Dependencies and integration points: depends on a parent platform/MFD driver named `smpro-hwmon` that exposes a regmap. It uses hwmon info API, regmap, bit helpers, and fixed SMPro register contracts.

Risks and test signals: `smpro_is_visible()` only actively suppresses missing temperature channels; voltage/current/power channels are always visible even if platform firmware does not implement them. Temperature values use `sign_extend32(value, 8)`, so tests should verify signed register handling. Test register error propagation, label ordering, unavailable DIMM temperatures, and power aggregation from whole watt plus milliwatt registers.
