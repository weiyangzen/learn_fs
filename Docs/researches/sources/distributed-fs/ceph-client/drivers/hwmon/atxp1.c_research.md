# sources/distributed-fs/ceph-client/drivers/hwmon/atxp1.c

Purpose: I2C hwmon/sysfs driver for the Attansic ATXP1 chip, providing CPU VID voltage control and two GPIO data registers. The chip is not autodetected and must be instantiated explicitly.

Important APIs, types, and functions: `atxp1_data` stores the I2C client, cache mutex, one-second validity state, cached register bytes, and detected VRM version. `atxp1_update_device()` reads VID, CPU VID, GPIO1, and GPIO2 via SMBus byte reads. `cpu0_vid_show()`/`cpu0_vid_store()` convert between millivolts and VID register values using `hwmon-vid`. `gpio1_show/store()` and `gpio2_show/store()` expose hex GPIO values. Probe checks `vid_which_vrm()` for VRM 9.0/9.1 support and registers `atxp1_groups`.

Control flow: module_i2c_driver registers an `atxp1` I2C driver. Probe allocates state, checks the CPU VRM, initializes the update mutex, and registers hwmon attributes. Reads refresh the register cache if stale. Writes parse user input, write changed register values over SMBus, and invalidate the cache.

State and persistence: register values are cached for up to one second in `data->reg`. Writes persist in the hardware until changed externally or reset. CPU VID writes are stepped one VID code at a time to improve stability and enable ATXP1 output with `ATXP1_VIDENA`.

Dependencies and integration points: depends on explicit I2C device instantiation, SMBus byte-data operations, hwmon group registration, `hwmon-vid` VRM conversion helpers, and sysfs attributes. There is no device-tree match table or automatic detection.

Risks: changing CPU VID is inherently risky and can destabilize hardware. `atxp1_update_device()` does not check negative SMBus read errors before assigning to `u8` cache fields. `last_updated` is never updated in the function, so cache validity does not actually throttle reads despite the intended design. GPIO2 write log incorrectly says GPIO1. Unsupported VRM versions refuse probe.

Test signals: instantiate on known ATXP1 hardware at supported addresses, verify VID conversion and stepped writes with safe values, verify GPIO masks and cache invalidation after writes, and test SMBus error behavior. Static tests should catch the missing `last_updated = jiffies` update and misleading GPIO2 log.
