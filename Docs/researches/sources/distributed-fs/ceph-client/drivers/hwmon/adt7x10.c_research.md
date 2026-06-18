# sources/distributed-fs/ceph-client/drivers/hwmon/adt7x10.c

Purpose: common hwmon core for ADT7410/ADT7420/ADT7422 I2C and ADT7310/ADT7320 SPI digital temperature sensors. It provides shared temperature conversion, limit/hysteresis/alarm sysfs behavior, interrupt notification, probe-time configuration, and suspend/resume.

Important APIs/types/functions: `struct adt7x10_data` stores the regmap, active and original config bytes, and whether the first temperature reading is valid. Conversion helpers `ADT7X10_TEMP_TO_REG()` and `ADT7X10_REG_TO_TEMP()` handle milli-Celsius and 13/16-bit register formats. `adt7x10_temp_ready()` polls status until the first conversion is ready. `adt7x10_read()`/`adt7x10_write()` implement hwmon temperature callbacks. `adt7x10_irq_handler()` emits `hwmon_notify_event()` for high, low, and critical alarms. `adt7x10_probe()` is exported to bus wrappers, and `adt7x10_dev_pm_ops` provides suspend/resume.

Control flow: bus-specific drivers create a regmap and call `adt7x10_probe()`. The common probe reads original config, sets continuous conversion, 16-bit resolution, comparator/event mode, normal polarity, and registers a managed restore action if it changed config. It then registers a single temp channel with input, min/max/crit, hysteresis, and alarm attributes. If an IRQ is supplied, it requests a threaded falling-edge handler. Reads wait for conversion readiness once, then read registers. Writes clamp and program limit registers or hysteresis.

State and persistence: `oldconfig` is restored automatically on driver detach if probe changed it. `config` is used for conversion semantics and PM resume. `valid` gates the initial wait for non-stale temperature. Regmap caches nonvolatile registers while temperature/status are volatile in bus wrappers. Suspend writes power-down bits; resume writes the active config.

Dependencies and integration: depends on regmap, hwmon channel-info callbacks, interrupts, devm actions, jiffies/delays, and exported symbols consumed by `adt7310.c` and `adt7410.c`.

Risks: hysteresis is stored as one shared 4-bit delta but presented as multiple absolute hysteresis values; writing max hysteresis affects all hysteresis displays. IRQ handling reports events based on status reads but does not clear or debounce alarms itself. Correct temperature conversion depends on wrappers marking status and temperature volatile and using correct endian bus operations.

Test signals: run shared hwmon reads/writes through both I2C and SPI wrappers, verify first-read timeout behavior, check 13-bit versus 16-bit conversion if resolution config changes, exercise IRQ notifications for low/high/critical, and run suspend/resume with regmap fault injection.
