# `sources/distributed-fs/ceph-client/drivers/hwmon/menf21bmc_hwmon.c` Research

Purpose: this platform hwmon child driver exposes five voltage rails monitored by the MEN 14F021P00 BMC: 3.3 V, 5 V, 12 V, standby 5 V, and VBAT. It reports input, minimum, maximum, and label attributes for each rail.

Important APIs, types, and functions: `struct menf21bmc_hwmon` stores validity, parent I2C client, last update, current input values, and fixed min/max arrays. `menf21bmc_hwmon_update()` refreshes input values once per second. `menf21bmc_hwmon_get_volt_limits()` reads static min/max limits at probe. `label_show()`, `in_show()`, `min_show()`, and `max_show()` back manually declared `SENSOR_DEVICE_ATTR_RO()` attributes.

Control flow: probe obtains the parent BMC I2C client, reads all min/max limits, and registers the hwmon device with static attribute groups. Input reads refresh current values if stale or invalid; min/max reads return cached probe-time limits.

State and persistence: current inputs are cached for up to one second; min/max limits are cached for the device lifetime. Hardware/BMC commands provide persistent values. There are no writes from this driver.

Dependencies and integration points: depends on a platform device created by the MEN BMC core, an I2C parent client, SMBus word reads at command ranges `0x40`, `0x50`, and `0x60`, and legacy hwmon groups.

Risks and test signals: the driver assumes BMC word values are already in hwmon units and does not byte-swap or scale. Tests should cover probe failure when any limit read fails, one-second input cache behavior, each command address mapping, parent I2C lookup, correct label strings, and static min/max caching after input refresh.
