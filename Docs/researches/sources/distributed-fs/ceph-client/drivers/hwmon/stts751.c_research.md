
# sources/distributed-fs/ceph-client/drivers/hwmon/stts751.c

Purpose: I2C hwmon driver for ST STTS751 temperature sensors. It provides temperature input, min/max event limits, therm critical limit and hysteresis, alarm flags, update interval, and SMBus alert support.

Important APIs, types, and functions: `struct stts751_priv` stores client, locks, config, interval/resolution, cached temperatures and alarms, timestamps, and notification flags. `stts751_update_temp()` performs high-low-high reads to avoid torn conversions. `stts751_update_alert()` handles status bits that clear on read and maintains a cache across conversion intervals. `stts751_alert()` reacts to SMBus alerts with sysfs notifications and uevents. Store handlers update limits, hysteresis, therm threshold, and conversion interval.

Control flow, state, and persistence: detection validates manufacturer, product, reserved bits, and timeout register shape. Probe optionally sets `smbus-timeout-disable`, reads revision/config/limits, clears STOP and event-disable bits, then registers hwmon groups. Runtime state is protected by `access_lock`; hardware thresholds persist in device registers.

Dependencies and integration points: uses SMBus byte data, I2C alert protocol, hwmon sysfs, device properties, `find_closest_descending()`, and OF compatible `st,stts751`.

Risks and test signals: alarm flags clear on status reads, making cache timing important. Interval changes also adjust resolution in a conservative order. Test alert handling, sysfs poll wakeups, limit clamping, hysteresis relative to therm, invalid conversion-rate rejection, update interval to resolution mapping, and communication failure fallback that asserts both alarms.
