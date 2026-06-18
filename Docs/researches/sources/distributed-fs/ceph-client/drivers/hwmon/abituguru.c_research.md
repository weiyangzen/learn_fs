# sources/distributed-fs/ceph-client/drivers/hwmon/abituguru.c

## Purpose
`abituguru.c` is a legacy hwmon platform driver for first-generation Abit uGuru motherboard monitoring hardware at the fixed I/O base `0x00e0`. It exposes voltage, temperature, fan tachometer, alarm, beep/shutdown, and automatic PWM fan-control settings through hwmon-style sysfs attributes.

## Important APIs, Types, And Functions
The central state is `struct abituguru_data`, which stores the platform hwmon device, `update_lock`, I/O address, ready/timeout state, dynamically generated sysfs attributes and names, cached sensor values, cached limit/settings bytes, alarm bytes, and PWM settings. Low-level transactions use `inb_p`, `inb`, and `outb` in `abituguru_wait`, `abituguru_ready`, `abituguru_send_address`, `abituguru_read`, and `abituguru_write`. Probe-time discovery is handled by `abituguru_detect_bank1_sensor_type`, `abituguru_detect_no_bank2_sensors`, and `abituguru_detect_no_pwms`. User ABI handlers include bank value/setting/mask/alarm show/store functions and PWM control handlers. Module entry uses `abituguru_init`, `abituguru_detect`, a synthetic `platform_device`, and `hwmon_device_register`.

## Control Flow
Initialization refuses non-Abit boards unless `force` is set, probes the fixed command/data ports, registers `abituguru_driver`, and allocates a matching platform device with an I/O resource. `abituguru_probe` reads every bank and setting block into memory before creating sysfs attributes. Bank 1 sensor type detection intentionally writes temporary threshold/alarm settings, waits for the controller to raise alarms, then restores the original settings. Fan and PWM counts are inferred from cached setting ranges or overridden by module parameters. Runtime reads call `abituguru_update_device`, which refreshes alarms, bank 1 values/settings, and fan values no more often than once per second. Sysfs stores update the in-memory byte first, write the corresponding uGuru setting block, and roll back the cache on failed writes.

## State And Persistence
The driver keeps a volatile cache in `struct abituguru_data`; the persistent state is the uGuru firmware's own thresholds, alarm masks, and PWM tables. Writes through sysfs change hardware/firmware settings immediately. Probe-time sensor detection temporarily mutates persistent sensor settings and has explicit restore/retry logic because bad settings can affect BIOS behavior. Suspend locks `update_lock` to quiesce transactions; resume revalidates the ready state and unlocks.

## Dependencies And Integration Points
This driver depends on x86-style port I/O, DMI board vendor strings, the platform bus, hwmon sysfs helpers, jiffies, mutexes, and module parameters (`force`, `bank1_types`, `fan_sensors`, `pwms`, `verbose`). It integrates with userspace through manually created sysfs files rather than modern `hwmon_device_register_with_info`.

## Risks And Test Signals
High-risk areas are forced probing of fixed I/O ports, destructive sensor-type detection, incomplete hardware write failures, stale cache behavior after consecutive timeouts, sysfs name buffer accounting, and correctness of conversions between raw bytes and millivolts/millicelsius/RPM. Useful test signals are successful load only on intended DMI systems, stable `name`, `in*`, `temp*`, `fan*`, and `pwm*` sysfs files, restore of original settings after type detection, correct rollback on injected write failures, suspend/resume without overlapping I/O transactions, and no writes to non-existent fan/PWM channels.
