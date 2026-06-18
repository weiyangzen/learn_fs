# sources/distributed-fs/ceph-client/drivers/hwmon/fschmd.c

## Purpose
`fschmd.c` is a merged Fujitsu Siemens/Fujitsu hwmon driver for Poseidon, Hermes, Scylla, Heracles, Heimdall, Hades, and Syleus system-monitoring chips at I2C address `0x73`. It exposes voltage, temperature, fan, PWM minimum, alert LED, and a legacy watchdog character device.

## Important APIs, types, and functions
- `enum chips` maps seven chip families to dense table indexes. Large register tables define per-chip voltage, fan, temperature, and watchdog register addresses and sensor counts.
- `struct fschmd_data` contains the I2C client, hwmon device, update and watchdog locks, watchdog miscdevice/list/kref lifetime state, chip kind, cached global/watchdog registers, and raw sensor caches.
- Sysfs callbacks cover scaled voltage reads, temperature input/max/fault/alarm, fan RPM/div/alarm/fault, PWM auto point 1 minimum duty, and `alert_led`.
- Watchdog helpers `watchdog_set_timeout()`, `watchdog_get_timeout()`, `watchdog_trigger()`, and `watchdog_stop()` program watchdog preset/control registers with 2-second or 60-second resolution depending on timeout and chip kind.
- Watchdog file operations implement single-open exclusion, magic-close handling with `V`, keepalive writes, and standard watchdog ioctls.
- `fschmd_dmi_decode()` parses OEM DMI type 185 subtype 19 records to override voltage multipliers, offsets, and reference voltage for newer FSC systems.
- `fschmd_detect()` reads three identification bytes and maps signatures such as `PEG`, `HER`, `SCY`, `HRC`, `HMD`, `HDS`, and `SYL` to I2C board names.
- `fschmd_update_device()` refreshes sensor state every two seconds, resets latched temp/fan alarms when conditions have cleared, and caches voltages.

## Control flow
The I2C driver scans address `0x73`. Detect checks SMBus byte-data support and signature bytes. Probe allocates a non-devm data object because watchdog file descriptors can outlive I2C client removal. It initializes locks/list/kref, stores the client for watchdog operations, seeds hardwired Poseidon temp limits, optionally parses DMI scaling for newer chips, reads immutable revision/global/watchdog registers, and creates sysfs files according to per-chip sensor counts.

For Syleus, probe reads temp/fan status before creating attributes and skips disabled sensors. Poseidon skips unavailable temp-limit and third fan-min/PWM files. After hwmon registration, probe registers one watchdog miscdevice on the first available minor from the legacy watchdog minor list while holding `watchdog_data_mutex`, adds the device to a global list, and sets a default 60-second timeout.

Watchdog open locates the data object by misc minor under a trylock to avoid deadlock with misc registration, enforces single-open, takes a kref, triggers the watchdog, and stores data in `filp->private_data`. Release stops only after a magic close when `nowayout` is false; otherwise it retriggers and logs a critical unexpected-close message. Remove deregisters the miscdevice, stops an open watchdog, removes the global-list entry, nulls `data->client` under `watchdog_lock`, unregisters hwmon, removes sysfs files, and drops the final kref.

## State and persistence
Sensor cache state expires after two seconds and is protected by `update_lock`. Writes to temp limits, fan dividers, PWM minimums, alert LED, and watchdog registers update hardware and local cache. Voltage scaling globals are process-wide and initialized once from DMI or defaults. Watchdog state spans the I2C device and open file descriptors through `kref`; `data->client = NULL` prevents further hardware access after detach. The `nowayout` module parameter controls whether magic close can stop the watchdog.

The driver actively clears latched alarms by writing status registers when readings indicate the alarm condition is gone. This makes reads state-changing.

## Dependencies and integration points
The driver integrates with I2C hwmon scanning, classic manual hwmon sysfs files, DMI table walking, the legacy miscdevice watchdog ABI, watchdog ioctl constants, `uaccess`, `kref`, mutexes, and global module parameters. Userspace sees both hwmon sysfs and `/dev/watchdog*` style misc devices.

## Risks
- Watchdog lifetime is complex: data is manually allocated, referenced by global list and file descriptors, and decoupled from the I2C client on removal. Lock ordering and kref changes are high risk.
- `watchdog_open()` assumes the misc minor always maps to a data object after list traversal. If that invariant is broken, a null dereference would follow.
- Some sysfs reads clear latched alarms, so passive monitoring has side effects.
- DMI voltage scaling is global and reused across devices; unexpected DMI records or multiple board variants could produce wrong voltage units.
- `watchdog_release()` logs through `data->client->dev` even after detach would be dangerous, but removal stops and nulls client only after deregistering and handling open state. This path should remain carefully ordered.
- Many `i2c_smbus_write_byte_data()` calls do not check return values, so hardware I/O failures may leave caches optimistic.
- Syleus disabled sensor filtering happens during creation but removal tries all possible files, which relies on safe missing-file removal.

## Test signals
- Build with `CONFIG_SENSORS_FSCHMD` and watchdog/miscdevice support.
- Detection tests should cover all signature strings and SMBus functionality failure.
- Sysfs tests should validate per-chip sensor counts, Poseidon skipped limit/PWM files, Syleus disabled sensors, DMI voltage scaling, temperature/fan alarm clearing behavior, and fan divider accepted values 2/4/8.
- Watchdog tests should cover single-open behavior, keepalive writes, magic close vs `nowayout`, timeout resolution boundaries, `WDIOC_*` ioctls, misc minor fallback, removal while watchdog is open, and operations after client detach returning `-ENODEV`.
