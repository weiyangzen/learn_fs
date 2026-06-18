# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/vexia_atla10_ec.c

Purpose: I2C power-supply class driver for the embedded controller on the Vexia EDU ATLA 10 9V tablet. It reimplements the useful ACPI battery access path for firmware that exposes LPSS I2C as PCI and therefore cannot use the broken ACPI battery device directly.

Important APIs/types/functions: key data types are packed `atla10_ec_battery_state`, `atla10_ec_battery_info`, and runtime `atla10_ec_data`. `atla10_ec_cmd()` reads EC SMBus blocks, `atla10_ec_update()` caches battery state for five seconds, `atla10_ec_psy_get_property()` implements power-supply properties, `atla10_ec_external_power_changed()` schedules a delayed refresh, and `atla10_ec_probe()` reads design info and registers `atla10_ec_battery`. The I2C ID is `vexia_atla10_ec`.

Control flow: probe allocates driver data, initializes mutex and autocancel delayed work, reads static battery info command `0x88`, then registers a battery `power_supply`. Property reads lock `update_lock`, refresh command `0x87` if the cache is invalid or stale, translate ACPI battery status bits into Linux status values, convert little-endian mAh/mV/mA/temperature fields into sysfs units, clamp `charge_now` to `charge_full` to hide an EC full-battery bug, and report fixed min design voltage and LiPo technology. External power changes wait 0.5 seconds, invalidate the cache, and notify userspace.

State and persistence: runtime state is an in-memory cache of battery info/state, `valid`, `last_update`, delayed work, and mutex. The EC owns true hardware state; the driver has no disk persistence. Cached dynamic state persists only until staleness timeout, external-power notification, or driver removal.

Dependencies/integration: depends on I2C SMBus block reads, power_supply core, delayed work, mutex guard helpers, byte-order conversion, and board instantiation from `other.c` using `x86_i2c_client_info`. The `supplied-from` relationship is supplied via the board software node, not by this driver.

Risks: `atla10_ec_cmd()` requires the EC to return exactly the expected block length; partial or longer reads fail as `-EIO`. Temperature conversion divides centi-degrees by 10 for power-supply deci-degree units, which assumes EC units are exactly centi-Celsius. `current_now` sign depends only on the discharging bit. The cache improves performance but can obscure rapid EC changes for up to five seconds except after external-power callbacks.

Test signals: verify probe reads command `0x88`, sysfs properties return expected units and negative discharge current, full-battery `charge_now` is clamped, external charger plug/unplug triggers delayed `power_supply_changed()`, SMBus read-length errors propagate, and repeated property reads within five seconds avoid extra EC traffic.
