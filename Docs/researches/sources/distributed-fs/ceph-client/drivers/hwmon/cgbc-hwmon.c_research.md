# sources/distributed-fs/ceph-client/drivers/hwmon/cgbc-hwmon.c

Purpose: hwmon child driver for Congatec Board Controller devices. It discovers controller-reported sensors and exposes active temperature, voltage, current, and fan channels with fixed labels.

Important APIs, types, and functions: `cgbc_hwmon_sensor` records hwmon type, active flag, controller index/channel, and label. `cgbc_hwmon_data` links to the parent `cgbc_device_data` and discovered sensor array. `cgbc_hwmon_cmd()` sends board-controller command `0x77`. `cgbc_hwmon_probe_sensors()` asks sensor zero for the total count, then decodes each sensor's type, ID, active bit, and label. `cgbc_hwmon_find_sensor()` maps hwmon type/channel to discovered sensor, including current channels offset after voltage channels. `cgbc_hwmon_read()`, `is_visible()`, and `read_string()` implement hwmon callbacks.

Control flow: as a platform child, probe gets the parent MFD data, allocates driver state, probes the controller sensor table, then registers `cgbc_hwmon`. Visibility hides inactive or unknown sensors. Reads issue a fresh controller command for the sensor index and convert little-endian data bytes into a value; temperatures convert 0.1 degree C units to hwmon millidegrees.

State and persistence: discovered sensor metadata is stored once during probe. Read values are not cached and are fetched from the board controller each time. No writable hardware state is exposed.

Dependencies and integration points: depends on the Congatec MFD core (`linux/mfd/cgbc.h` and `cgbc_command()`), platform-device child creation, hwmon core, and bitfield helpers. Channel labels are compiled in and indexed by controller channel IDs.

Risks: `cgbc_hwmon_read()` and `read_string()` assume visibility has found a sensor; direct callback calls with missing mappings would dereference NULL. Controller channel IDs are decremented, so a returned ID of zero underflows the unsigned channel variable. The static hwmon channel arrays define maximum visible channels; controller firmware returning more valid sensors than arrays support will be ignored. No cache means frequent sysfs polling can generate many controller transactions.

Test signals: test with board controllers returning valid active/inactive temp, voltage, current, and fan entries; unknown type/channel warnings; zero/invalid IDs; and command failures. Verify current channel offset mapping, labels, temperature scaling, and that inactive sensors are hidden.
