# sources/distributed-fs/ceph-client/drivers/hwmon/ftsteutates.c

## Purpose
`ftsteutates.c` is an I2C hwmon and watchdog driver for the Fujitsu Technology Solutions Teutates system-monitoring chip, a baseboard management controller at address `0x73`. It exposes sixteen temperature channels, eight fan channels, four voltage inputs, fan-to-temperature source mappings, clearable alarms, and a managed watchdog.

## Important APIs, types, and functions
- `struct fts_data` stores the I2C client, hwmon cache timestamp/valid bit, watchdog device, watchdog resolution, voltage/temp/fan caches, fan source mappings, and alarm/presence bitmasks.
- `fts_read_byte()` and `fts_write_byte()` implement paged register access. The high byte of the 16-bit register selects the page through `FTS_PAGE_SELECT_REG`; the low byte is then read or written.
- `fts_update_device()` refreshes data every two seconds after checking the device-ready bit in `FTS_DEVICE_STATUS_REG`. It reads fan presence, fan alarms, present fan speeds/sources, temperature alarms, all temperature inputs, and all voltages.
- Watchdog functions `fts_wd_set_resolution()`, `fts_wd_set_timeout()`, `fts_wd_start()`, `fts_wd_stop()`, and `fts_watchdog_init()` integrate the chip with the kernel watchdog framework using `devm_watchdog_register_device()`.
- `fts_is_visible()`, `fts_read()`, and `fts_write()` implement the modern `hwmon_ops` API rather than manual sensor attributes.
- `fts_detect()` and `fts_probe()` validate revision, detect-register magic values, I2C address, and BMC device ID before registering hwmon and watchdog.

## Control flow
The I2C driver scans `0x73`. Detect accepts revisions at least `0x2b`, requires detect registers `0x17`, `0x34`, `0x54`, and requires device ID `0x11`. Probe independently rejects non-`0x73` clients and device IDs whose high nibble is not BMC `0x10` or whose low nibble is not Teutates `0x01`. It allocates managed data, reads revision, registers hwmon with `devm_hwmon_device_register_with_info()`, initializes the watchdog, and logs the detected revision.

All hwmon reads call `fts_update_device()` first. Temperature input is decoded as `(raw - 64) * 1000`, fan input as revolutions per second times 60, voltages as raw values scaled to 3300 mV, fan faults from presence bits, and temp faults from zero temperature readings. Writes are limited to clearing temp/fan alarms by writing bit 0 to the channel control register; attempts to write nonzero alarm values return `-EINVAL`.

The watchdog init path reads the current preset. If zero, it configures seconds resolution and defaults to 60 seconds. If nonzero, it reads the control register, derives seconds vs minutes resolution, sets the timeout, and marks the watchdog hardware running.

## State and persistence
The hwmon cache expires every two seconds and is invalidated after alarm-clear writes. The chip can report data not ready; in that case `fts_update_device()` returns `-EAGAIN`. Watchdog timeout and resolution live both in `struct watchdog_device` and chip registers. Starting writes the preset divided by the current resolution, while stopping writes preset zero. Managed registration ties hwmon and watchdog cleanup to the device lifetime.

## Dependencies and integration points
The driver depends on I2C SMBus byte-data operations, the modern hwmon channel-info API, the kernel watchdog framework, jiffies, math helpers, and managed device allocation. It exposes standard hwmon channel types (`temp`, `fan`, `pwm`, `in`) and a standard watchdog device.

## Risks
- Every register access changes the page select register; concurrent non-driver accesses to the chip could observe or disturb page state.
- `fts_update_device()` has no explicit mutex around cache refresh or page-select/read sequences, so concurrent hwmon reads can interleave I2C transactions through the adapter. The I2C core serializes individual transfers, but not the logical page-select plus register operation as a higher-level critical section.
- `data->valid = !!(err & 0x02)` is documented as "Data not ready yet"; if the hardware bit semantics are inverted or unclear, reads may return `-EAGAIN` unexpectedly.
- Alarm writes only support clearing. Userspace writing `1` gets `-EINVAL`, which should be reflected in tests.
- The watchdog resolution bit logic is subtle: timeouts over 255 seconds are rounded up to whole minutes and resolution changes are persisted in hardware.

## Test signals
- Build with `CONFIG_SENSORS_FTSTEUTATES` and watchdog support.
- Detection tests should cover bad revision, bad detect-register magic, wrong address, non-BMC IDs, and unsupported BMC subtypes.
- Hwmon tests should cover ready vs not-ready status, absent fans, invalid fan source mapping, temperature zero fault, alarm clearing, and voltage scaling.
- Watchdog tests should cover stopped hardware default timeout, already-running hardware, seconds/minutes resolution switching, timeout rounding over 255 seconds, max heartbeat, start/stop, and magic-close support through the watchdog core.
