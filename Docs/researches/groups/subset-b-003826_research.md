# subset-b-003826 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ibmaem.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ibmaem.c

## Purpose

`ibmaem.c` is a legacy hwmon driver for IBM System x Active Energy Manager firmware. It discovers AEM firmware instances through IPMI SMI watcher callbacks and exposes each instance as a platform-backed hwmon device with energy, computed average power, temperature, and power-cap attributes. AEM1 exposes one energy/power meter; AEM2 exposes two energy meters, two computed power meters, two exhaust temperatures, and several power-cap registers.

## Important APIs, Types, and Functions

`struct aem_ipmi_data` owns the IPMI user, target address, completion, transmit message, receive buffer pointer, and BMC device. `struct aem_data` is the per-AEM-instance state: hwmon/platform devices, mutex, refresh validity, firmware version/module handle, IPMI state, cached energy/power-period/temp/power-cap values, dynamic sysfs attributes, and the update callback. Packed request/response structures model AEM find-firmware, find-instance, and read-register commands. `aem_init_ipmi_data()`, `aem_send_message()`, and `aem_msg_handler()` are the IPMI transport layer. `aem_read_sensor()` is the central typed register read helper. `aem_init_aem1_inst()` and `aem_init_aem2_inst()` allocate devices and attributes; `aem_register_bmc()` probes both protocol generations for each BMC. Sysfs show/store functions implement `name`, `version`, `energy*_input`, `power*_average`, `power*_average_interval`, temperatures, and power-cap values.

## Control Flow

Module init registers a platform driver shell and an IPMI SMI watcher. When a BMC appears, a temporary IPMI user probes for AEM1 instance count and AEM2 instance records. Each discovered instance gets a platform device, private IPMI user, hwmon registration, response buffer, and dynamic sensor files. Sensor reads flow from sysfs into `data->update()` or direct energy reads, then into synchronous IPMI requests completed by `aem_msg_handler()`. Power average is computed by reading energy, sleeping for the configured interval, reading energy again, and dividing the delta by elapsed nanoseconds. BMC removal and module exit walk `driver_data.aem_devices` and unregister sysfs, hwmon, IPMI, platform, IDA, and memory state.

## State and Persistence Behavior

All persistent runtime state is in memory per AEM instance. The driver caches sensor values for `REFRESH_INTERVAL`, but energy reads used for power calculation bypass most aggregate caching. `power_period[]` is user-writable sysfs state only and defaults to 1000 ms with a 200 ms minimum. There is no durable storage; firmware state is read-only from this driver except for the query protocol itself.

## Dependencies and Integration Points

The driver integrates IPMI (`ipmi_create_user`, `ipmi_smi_watcher_register`, `ipmi_request_settime`), platform devices, classic hwmon sysfs registration, IDA instance allocation, completions, mutexes, jiffies, and endian conversion helpers. It also declares IBM DMI aliases for autoloading on known System x/Blade platforms.

## Risks and Edge Cases

`aem_read_sensor()` calls `aem_send_message()` but does not check its return before waiting, so address/request failures can degrade into timeout behavior. The IPMI completion is reused without an explicit `reinit_completion()` before every transaction, relying on serialized use and prior completion state. `update_aem1_sensors()` and `update_aem2_sensors()` never set `last_updated` or `valid`, so the intended refresh cache appears ineffective and every sysfs update can hit IPMI. Power average sysfs reads sleep while holding `data->lock`, serializing other sensor access for the interval. Error returns from individual sensor reads in update paths are ignored, which can leave stale values. Dynamic sysfs creation and cleanup are manual, making partial registration failures a risk surface.

## Test Signals

Useful tests include BMC add/remove with zero, AEM1, AEM2, and mixed instances; IPMI timeout, completion-code, bad IANA, and short-response paths; sysfs file cleanup after partial create failure; energy scaling to microjoules; power averaging with interrupted sleep; power interval validation; AEM2 power-cap and temperature scaling; and concurrent sysfs reads during BMC removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ibmaem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ibmpex.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ibmpex.c

## Purpose

`ibmpex.c` exposes IBM PowerExecutive BMC temperature and power sensors through hwmon. It discovers supported BMCs through IPMI, filters firmware sensor names for power and temperature signatures, creates classic hwmon sysfs attributes for current, lowest, and highest values, and provides a write-only reset for high/low history.

## Important APIs, Types, and Functions

`struct ibmpex_bmc_data` holds per-BMC hwmon state, IPMI transport fields, cached firmware version, sensor count, and an array of `struct ibmpex_sensor_data`. Each sensor stores whether it is exported, three cached values, a multiplier, and three `sensor_device_attribute_2` entries. `ibmpex_ver_check()`, `ibmpex_query_sensor_count()`, `ibmpex_query_sensor_name()`, `ibmpex_query_sensor_data()`, and `ibmpex_reset_high_low_data()` implement the PowerExecutive command set. `ibmpex_find_sensors()` classifies sensor names and creates attributes. `ibmpex_update_device()` refreshes all active sensors under a mutex. `ibmpex_msg_handler()` completes synchronous IPMI requests.

## Control Flow

Module init registers an IPMI SMI watcher. On BMC registration, the driver allocates `ibmpex_bmc_data`, creates an IPMI user, initializes the command message, checks the PowerExecutive version, registers the BMC device with hwmon, links the BMC into the global list, and discovers sensors. Discovery queries the count, reads each name, identifies names starting with `pwr` or `tem`, chooses units, and creates three attributes per exported sensor. Sysfs reads call `ibmpex_update_device()`, which refreshes active sensors every two seconds by querying data and extracting current/low/high fields at fixed offsets. BMC removal reverses attribute creation, unregisters hwmon and IPMI, and frees names and arrays.

## State and Persistence Behavior

The driver caches sensor data in `values[3]` with `valid` and `last_updated` gating. Sensor names are not retained beyond classification; generated sysfs attribute names are dynamically allocated and freed. The high/low reset write sends a firmware command and does not parse user input. There is no persistent storage outside BMC-maintained high/low state.

## Dependencies and Integration Points

It depends on IPMI SMI watcher and user APIs, classic hwmon sysfs helpers, mutexes, jiffies, endian extraction, and BMC device driver data. The hwmon device is registered against the BMC device itself rather than an extra platform device. IBM System x DMI aliases support module autoloading.

## Risks and Edge Cases

IPMI waits use `wait_for_completion()` without timeout, so a lost response can block probe or sysfs reads indefinitely. Completion state is not reinitialized per transaction. `ibmpex_send_message()` return values are ignored in query helpers. `ibmpex_msg_handler()` copies received payload into a fixed `IPMI_MAX_MSG_LENGTH` buffer without clamping to that buffer, trusting IPMI message bounds. The reset-high-low store ignores user value and always returns success after sending. Dynamic sysfs names are limited by a fixed 32-byte allocation but generated names fit current formats. Unsupported sensor names are silently skipped, so firmware naming changes can hide sensors.

## Test Signals

Test version-check rejection, sensor-count errors, malformed sensor names, power multiplier selection for version 1 versus version 2 and watt signatures, sysfs cleanup on mid-discovery failure, high/low reset command emission, stale cache reuse within two seconds, sensor data short-read handling, and BMC disappearance during active sysfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ibmpex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ibmpowernv.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ibmpowernv.c

## Purpose

`ibmpowernv.c` exports IBM PowerNV OPAL platform sensors as hwmon attributes. It translates OPAL device-tree sensor nodes into hwmon names for fan, temperature, voltage, power, current, and energy sensors, reads values through OPAL firmware, and optionally exposes sensor-group enable controls.

## Important APIs, Types, and Functions

`enum sensors` indexes global `sensor_groups[]`, each of which accumulates a hwmon attribute group. `struct sensor_data` stores an OPAL sensor id, hwmon index, OPAL index, type, label, sysfs name, attribute object, and optional group data. `struct sensor_group_data` stores group id, mutex, and enabled state. `show_sensor()`, `show_label()`, `show_enable()`, and `store_enable()` implement sysfs operations. Parsing helpers include `get_sensor_type()`, `parse_opal_node_name()`, `get_sensor_index_attr()`, and `convert_opal_attr_name()`. `populate_attr_groups()` counts attributes, while `create_device_attrs()` allocates and fills the final attribute arrays.

## Control Flow

Probe allocates `platform_data`, stores it as driver data, counts sensors and optional labels/min/max/group controls from `/ibm,opal/sensors` and `ibm,opal-sensor-group` nodes, allocates attribute arrays per sensor type, then walks the sensor tree again to populate `sensor_data` entries. Legacy node names such as `cooling-fan#2-data` are parsed into indexed hwmon attributes; newer nodes fall back to sequential `*_input` naming. Reads call `opal_get_sensor_data_u64()`, then scale temperature to millidegrees and power input to microwatts. Group enable writes serialize on a per-group mutex and call `sensor_group_enable()`.

## State and Persistence Behavior

Driver state is devm-managed for the platform device lifetime. Global `sensor_groups[]` holds mutable counters and hwmon index state during probe. Per-group enable state is cached in memory after successful OPAL calls and defaults false until the first matching sensor enables the group during attribute creation. Sensor values are not cached by this driver.

## Dependencies and Integration Points

The driver is PowerNV/OPAL-specific and depends on Open Firmware device tree parsing, OPAL sensor calls, OPAL sensor-group control, PowerPC CPU/PIR mapping helpers for labels, platform driver matching by `opal-sensor`, and devm hwmon group registration. It bridges firmware sensor metadata into the standard hwmon sysfs ABI.

## Risks and Edge Cases

`of_find_node_by_path("/ibm,opal/sensors")` is not checked before child iteration, so missing OPAL sensor nodes rely on iterator behavior. `sensor_groups[]` is global mutable state; repeated probe/unbind cycles or multiple devices could inherit stale counts or indices. Group discovery increments attribute counts once per group and later creates enable attributes once per type/group, so malformed phandles can skew counts. OPAL errors from reads are returned directly to sysfs. Labels are truncated to fixed buffers. Compatibility with newer device trees depends on `sensor-type` strings exactly matching `sensor_groups[].name`.

## Test Signals

Validate legacy and new device-tree naming, label formatting with `ibm,pir` and `ibm,chip-id`, min/max attribute creation, group enable toggling and mutex behavior, OPAL read error propagation, unit scaling for temperature and power, missing sensor-id fallback to `sensor-data`, and reprobe behavior to detect stale global group state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ibmpowernv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/iio_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/iio_hwmon.c

## Purpose

`iio_hwmon.c` is a bridge driver that exposes IIO consumer channels through the hwmon sysfs ABI. It dynamically creates `*_input` and optional `*_label` attributes for voltage, temperature, current, power, and relative-humidity IIO channels.

## Important APIs, Types, and Functions

`struct iio_hwmon_state` stores the acquired IIO channel array, channel count, hwmon attribute group, group pointer array, and attribute pointer array. `iio_hwmon_read_val()` obtains channel type and reads processed values, using `iio_read_channel_processed_scale(..., 1000)` for power so milliwatts become microwatts. `iio_hwmon_read_label()` delegates labels to `iio_read_channel_label()`. `iio_hwmon_probe()` acquires all channels, counts them, allocates dynamic sensor attributes, names them with hwmon prefixes, and registers a hwmon device.

## Control Flow

Probe calls `devm_iio_channel_get_all()`, deferring if no IIO provider is ready. It counts channels until the sentinel `indio_dev` is null, allocates room for input plus label attributes, and iterates each channel. Supported IIO types map to hwmon prefixes: voltage to `in`, temperature to `temp`, current to `curr`, power to `power`, and relative humidity to `humidity`. For each channel it creates a read-only input attribute and probes for a label using a temporary page buffer; if a label is available it adds a read-only label attribute. The hwmon name comes from the firmware node path with dashes replaced by underscores, or `iio_hwmon` without firmware metadata.

## State and Persistence Behavior

There is no sensor value cache or writable state. All attributes are devm-managed and values are read live from the IIO channel on each sysfs access. The temporary label buffer is explicitly freed before hwmon registration.

## Dependencies and Integration Points

The driver binds platform devices compatible with `iio-hwmon`, consumes IIO channels through the IIO consumer API, and exposes them using classic hwmon sysfs groups. It relies on unit compatibility between IIO processed values and hwmon units, with an explicit power conversion.

## Risks and Edge Cases

Unsupported IIO channel types abort probe entirely rather than skipping only that channel. The comment notes that IIO and hwmon base-unit assumptions need verification for new channel types. Label detection calls `iio_read_channel_label()` during probe and later again during sysfs reads; providers with transient label errors may expose no label. Attribute numbering is per type and order-dependent on the IIO channel list. A device with zero channels registers an empty hwmon group.

## Test Signals

Test probe deferral, supported type naming and numbering, unsupported type rejection, power scaling from milliwatts to microwatts, label presence and absence, firmware-node-derived hwmon name sanitization, and live propagation of IIO provider read errors through sysfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/iio_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ina209.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ina209.c

## Purpose

`ina209.c` drives the TI/Burr Brown INA209 bidirectional current and power monitor. It exposes shunt voltage, bus voltage, power, current, warning/critical limits, alarms, peak history, and update interval through classic hwmon sysfs attributes.

## Important APIs, Types, and Functions

`struct ina209_data` stores the I2C client, update mutex, cache validity, last update time, all 0x17 register values, original configuration/calibration for restore, and update interval. `ina209_update_device()` refreshes every register under lock. `ina209_from_reg()` and `ina209_to_reg()` convert raw register values to and from hwmon units. `ina209_interval_from_reg()` and `ina209_reg_from_interval()` translate ADC configuration to update interval. Sysfs handlers implement value, alarm, history reset, and interval access. `ina209_init_client()` programs default configuration and calibration based on the optional `shunt-resistor` property, and `ina209_restore_conf()` restores original device settings on failure or remove.

## Control Flow

Probe verifies SMBus word support, allocates state, reads original calibration/configuration, determines shunt resistance from firmware or calibration, writes default configuration, writes calibration for 1 mA current LSB, clears status, and registers the hwmon group. Sysfs reads call `ina209_update_device()`, which bulk-reads all chip registers if the cache is invalid or older than the configured interval. Writable limit attributes parse user values, convert and clamp them, write the target register, and update the cache. History reset writes `1` to selected peak registers and invalidates the cache. Remove restores original configuration and calibration.

## State and Persistence Behavior

The driver caches all chip registers in memory and refreshes them on demand. It intentionally changes chip configuration and calibration during driver lifetime, then restores the original values on remove or hwmon registration failure. User-written limits persist in the chip until changed or reset by external events; the cache mirrors successful writes.

## Dependencies and Integration Points

It depends on the I2C SMBus word-data API with swapped endianness, classic hwmon attribute groups, device-tree `ti,ina209` matching, the optional `shunt-resistor` property, mutexes, jiffies, and standard hwmon units.

## Risks and Edge Cases

Several I2C writes ignore return status after conversion, so sysfs stores may report success even if the hardware write failed. `ina209_update_device()` reads all registers for any attribute, increasing latency and failure probability. Interval conversion is compact but non-obvious and should be checked against ADC bit encodings. History reset accepts any parsed value and resets regardless of whether the value is `1`. Restore on remove can overwrite changes made by another master while the driver was bound. The `shunt-resistor` fallback derives from original calibration and can be inaccurate if firmware used unusual scaling.

## Test Signals

Test register conversion for signed shunt/current, bus voltage reserved-bit preservation, power scaling, warning and critical limit clamping, alarm bit mapping, history reset masks, update interval round trips, shunt-resistor zero rejection, restore-on-remove behavior, and I2C read/write failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ina209.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ina238.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ina238.c

## Purpose

`ina238.c` supports TI INA228/INA237/INA238/INA700/INA780 and Silergy SQ52206 power monitors. It exposes shunt and bus voltage, current, power, optional peak power, optional 64-bit energy, die temperature, writable limits, and alarm flags through modern `hwmon_ops`.

## Important APIs, Types, and Functions

`struct ina238_config` describes per-chip capabilities, voltage/current format, temperature resolution, defaults, power factor, bus voltage LSB, and optional fixed current LSB. `struct ina238_data` stores the chosen config, I2C client, regmap, shunt/gain, voltage LSBs, current LSB, power LSB, and energy LSB. Low-level helpers read 24-bit, 40-bit, and signed 20-bit fields. `ina238_read_in()`, `ina238_read_curr()`, `ina238_read_power()`, `ina238_read_energy()`, and `ina238_read_temp()` implement hwmon reads. Matching write helpers program voltage, current, power, and temperature limits. `ina238_is_visible()` hides optional features based on chip config.

## Control Flow

Probe identifies the chip from match data, initializes regmap, determines current scaling either from fixed-chip configuration or from `shunt-resistor` and `ti,shunt-gain`, writes a fixed shunt calibration for external-shunt chips, applies gain bits in CONFIG, writes ADC defaults, configures alert polarity, computes bus voltage, power, and energy scale factors, then registers hwmon with `ina238_chip_info`. Sysfs reads dispatch through `ina238_read()` by sensor type and convert raw register values into hwmon units. Writes clamp user values to safe ranges, scale into register units, and write limit registers.

## State and Persistence Behavior

The driver does not cache measurements. It writes device configuration at probe and leaves it active while bound. Scaling state is computed once from properties and per-chip config. Regmap handles 16-bit register access, while 24-bit and 40-bit measurement registers are read directly with SMBus block reads.

## Dependencies and Integration Points

It depends on I2C, regmap, the modern hwmon info API, firmware properties `shunt-resistor`, `ti,shunt-gain`, and `ti,alert-polarity-active-high`, and OF/I2C match tables for TI and Silergy variants. It integrates optional energy and peak-power attributes through visibility gating.

## Risks and Edge Cases

For 24-bit power reads, values are treated as unsigned and clamped to `LONG_MAX`; very large values can saturate. The hwmon `energy64` path casts the `long *` read argument to `s64 *`, matching the intended ABI but worth verifying on supported architectures. External-shunt accuracy depends entirely on correct shunt and gain properties. Limit writes intentionally clamp broad ranges, which can hide invalid user values. Mixed regmap and direct SMBus block reads must remain consistent with adapter capabilities. The probe error message has a typo in "resister" but behavior is unaffected.

## Test Signals

Test per-chip visibility for energy and peak power, 16-bit versus signed 20-bit conversion, shunt/bus/current limit round trips, temperature resolution conversion, alert polarity setup, invalid shunt and gain rejection, SQ52206 bus-voltage and power-factor scaling, block-read short transfer handling, and saturation behavior for large power/energy values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ina238.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ina2xx.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ina2xx.c

## Purpose

`ina2xx.c` is the shared hwmon driver for TI INA219/INA220/INA226/INA230/INA231/INA234/INA260 and Silergy SY24655 current and power monitors. It exposes voltage, current, power, optional alerts/limits, optional update interval, optional average power, and writable shunt resistance for external-shunt devices.

## Important APIs, Types, and Functions

`struct ina2xx_config` captures chip defaults, alert support, internal-shunt status, average-power support, update-interval support, calibration, shifts, divisors, bus-voltage LSB, power factor, and current shift. `struct ina2xx_data` stores config, chip id, shunt resistance, computed current/power LSBs, regmap, and client. `ina2xx_get_value()` converts raw registers. `ina2xx_read_init()` reads values and reinitializes the chip if calibration was lost after reset. Alert helpers program `INA226_MASK_ENABLE` and `INA226_ALERT_LIMIT`. `ina2xx_read()` and `ina2xx_write()` dispatch modern hwmon operations, while `ina2xx_is_visible()` gates features by chip. `ina2xx_init()` configures regulator, shunt scaling, alerts, SY24655 accumulation, and calibration.

## Control Flow

Probe selects config from match data, initializes regmap with cache and volatile register definitions, optionally enables the `vs` regulator, initializes chip registers, then registers hwmon with or without the extra `shunt_resistor` sysfs group depending on internal-shunt status. Measurement reads dispatch by hwmon type. Current input is derived from shunt voltage so it remains meaningful even if the chip current register depends on calibration. Power input uses `ina2xx_read_init()` so a zero reading can trigger calibration-register verification and regcache sync. Alert limit writes disable alert functions first, write the limit, then enable the selected alert mask only for nonzero limits.

## State and Persistence Behavior

The driver maintains computed scaling in memory and writes configuration/calibration into the chip at probe and during reset recovery. Regmap cache stores writable register state and is marked dirty/synced if calibration loss is detected. The `shunt_resistor` sysfs attribute changes software scaling only; it does not rewrite the fixed calibration register. SY24655 average power uses an accumulator register configured to clear after read.

## Dependencies and Integration Points

Dependencies include I2C, regmap with maple cache, optional regulator enable, modern hwmon APIs, firmware properties `shunt-resistor` and `ti,alert-polarity-active-high`, and I2C/OF match data. The driver provides a common ABI over multiple related register layouts.

## Risks and Edge Cases

`ina226_alert_to_reg()` clamps shunt alert values with a formula that should be regression-tested because units differ between shunt voltage and current-derived limits. Reset recovery only triggers when the measured register reads zero; real zero power/current readings cause an extra calibration check. Writes to `shunt_resistor` are protected by the hwmon device lock but alter scaling for all future reads without touching hardware. Alert programming clears all alert functions before setting one, so only one alert function is active at a time. Regulator absence is accepted only for `-ENODEV`; other regulator errors block probe.

## Test Signals

Test all chip variants for visible attributes, shunt scaling and invalid resistor rejection, regulator failure paths, calibration-loss recovery, current derivation from shunt voltage, alert limit enable/disable and alarm reads, update interval conversion for INA226-like chips, SY24655 average-power block read and zero sample count, and internal-shunt INA260 behavior without shunt sysfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ina2xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ina3221.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ina3221.c

## Purpose

`ina3221.c` drives the TI INA3221 triple-channel current and voltage monitor. It exposes bus voltage, shunt voltage, current, warning/critical current limits, alert flags, per-channel enable controls, labels, shunt resistor configuration, summation current/voltage channels, averaging samples, and update interval.

## Important APIs, Types, and Functions

`struct ina3221_input` stores per-channel label, shunt resistor, disconnected status, and summation-disable flag. `struct ina3221_data` stores PM device, regmap, regmap fields, inputs, cached CONFIG, summation resistor/control, and single-shot mode. Conversion helpers translate CONFIG to intervals, intervals to conversion times, and raw shunt registers to signed values. `ina3221_read_in()`, `ina3221_read_curr()`, `ina3221_write_chip()`, `ina3221_write_curr()`, and `ina3221_write_enable()` implement hwmon behavior. DT parsing is in `ina3221_probe_from_dt()` and `ina3221_probe_child_from_dt()`. Runtime PM suspend/resume saves config, powers down, resets, syncs cache, and restores summation control.

## Control Flow

Probe allocates regmap and regmap fields, initializes default shunt values, parses optional DT children, builds the initial CONFIG value, disables disconnected channels, computes whether summation is valid, enables runtime PM, and increments the PM refcount once for each connected channel. HWMON reads check channel enable state before reading measurements; in single-shot mode, reads rewrite CONFIG and poll conversion-ready before reading. Channel enable writes adjust runtime PM refcounts around CONFIG updates. Current reads convert shunt voltage to mA using the channel or summation shunt resistor. Current limit writes convert mA to shunt-voltage limit registers. Debugfs exposes read-only summation-disable booleans.

## State and Persistence Behavior

The cached `reg_config` is the authoritative software copy for channel enables, averaging, conversion times, and power mode. Runtime PM active state and channel enable bits jointly determine whether measurements are valid. Per-channel shunt resistor sysfs writes update software scaling and recompute whether summation can be exposed. Suspend marks regcache dirty and cache-only after powering down; resume resets the chip and restores cached state.

## Dependencies and Integration Points

The driver depends on I2C, regmap/regmap_field, runtime PM, OF child-node properties (`reg`, `label`, `shunt-resistor-micro-ohms`, `ti,summation-disable`, `ti,single-shot`), debugfs, and modern hwmon operations including `read_string`.

## Risks and Edge Cases

Runtime PM reference accounting is tied to enabled channels; mismatches during probe failure, remove, or repeated enable writes can leave the device powered unexpectedly or suspended while enabled. `ina3221_is_enabled()` treats summation channels differently and returns enabled based on valid equal shunt resistors rather than runtime PM. Shunt resistor sysfs writes are not explicitly synchronized with simultaneous reads. Single-shot reads trigger conversions by rewriting CONFIG, which can race with users changing samples/update interval or enables. Summation requires equal shunt resistors among included channels, so one sysfs write can make summation attributes return `-ENODATA`.

## Test Signals

Test DT parsing for disconnected and labeled channels, invalid child `reg`, shunt property bounds, summation disable/equal-resistor behavior, runtime PM refcounts across enable toggles and remove, single-shot conversion-ready timeout, samples and update interval round trips, current limit conversion for individual and sum channels, alarm behavior for disabled channels, suspend/resume register restoration, and debugfs creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ina3221.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/intel-m10-bmc-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/intel-m10-bmc-hwmon.c

## Purpose

`intel-m10-bmc-hwmon.c` exposes telemetry from Intel MAX 10 BMC managed FPGA boards as hwmon attributes. It is table-driven for N3000, D5005, N5010, and N6000 board layouts, mapping board-specific BMC register offsets to temperature, voltage, current, and power channels with labels and threshold attributes.

## Important APIs, Types, and Functions

`struct m10bmc_sdata` describes one sensor channel: input, max, critical, hysteresis, min register offsets, multiplier, and label. `struct m10bmc_hwmon_board_data` maps hwmon sensor types to board tables and channel-info arrays. `struct m10bmc_hwmon` stores the parent MAX 10 BMC handle, selected board data, sanitized hwmon name, and chip info. `find_sensor_data()` selects a table entry. `do_sensor_read()` reads via `m10bmc_sys_read()`, handles invalid sentinel values, and applies scaling. `m10bmc_hwmon_read()` maps hwmon attributes to register offsets and computes hysteresis values. `m10bmc_hwmon_read_string()` returns labels. Probe selects board data from platform id driver data and registers hwmon.

## Control Flow

The MFD core instantiates a platform device with an id such as `n6000bmc-hwmon`. Probe retrieves the parent `intel_m10bmc`, picks board data from the id table, sets `hw->chip.info` and ops, sanitizes the board name, and registers the hwmon device. Reads are dispatched by hwmon core using the board-specific channel metadata. Unsupported attributes have zero register offsets and return `-EOPNOTSUPP`. Hysteresis attributes read both threshold and hysteresis registers and return threshold minus hysteresis.

## State and Persistence Behavior

The driver holds only devm-managed immutable table pointers and parent device references. It does not cache sensor values or write thresholds. Sensor validity is determined at read time. All board-specific behavior is encoded in static tables and channel-info arrays.

## Dependencies and Integration Points

It depends on the Intel MAX 10 BMC MFD core (`m10bmc_sys_read` and `struct intel_m10bmc`), platform-device id matching, modern hwmon info APIs, and the `INTEL_M10_BMC_CORE` namespace. It provides the hwmon child function of the larger MAX 10 BMC device stack.

## Risks and Edge Cases

Table and `HWMON_CHANNEL_INFO` ordering must match exactly; a mismatch would read the wrong register or label. All attributes are globally visible as read-only through `.visible = 0444`, so unsupported attributes rely on read-time `-EOPNOTSUPP` rather than visibility suppression. The firmware invalid sentinel `0xdeadbeef` maps to `-ENODATA`; real data with that raw value would be hidden. Multipliers are board-table-specific and must match firmware units. Hysteresis subtraction can produce negative values if firmware reports unexpected ordering.

## Test Signals

Test each platform id selects the right board table, channel counts match channel-info arrays, labels match expected board documentation, invalid sentinel returns `-ENODATA`, unsupported zero-offset thresholds return `-EOPNOTSUPP`, multiplier scaling for temperature and power, hysteresis subtraction, and parent MFD read failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/intel-m10-bmc-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/isl28022.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/isl28022.c

## Purpose

`isl28022.c` drives the Renesas ISL28022 power monitor. It exposes bus voltage, shunt voltage, current, and power through modern hwmon operations, configures the chip for continuous shunt/bus conversion, and derives scaling from firmware-provided shunt resistor, shunt range, and averaging properties.

## Important APIs, Types, and Functions

`struct isl28022_data` stores regmap, shunt resistance in micro-ohms, gain, and averaging sample count. `isl28022_read_in()`, `isl28022_read_current()`, and `isl28022_read_power()` convert raw register values to hwmon units. `isl28022_is_visible()` exposes read-only channels. `isl28022_read_properties()` validates `shunt-resistor-micro-ohms`, `renesas,shunt-range-microvolt`, and `renesas,average-samples`. `isl28022_config()` writes CONFIG and CALIB registers. A debugfs `shunt_voltage` file prints raw shunt voltage in microvolts.

## Control Flow

Probe verifies required SMBus byte and word functionality, allocates data, reads and validates properties, initializes regmap with big-endian 16-bit values and maple cache, writes the operating configuration and calibration, creates debugfs, and registers hwmon. Reads dispatch by hwmon type: bus voltage uses the bus register in fixed 60 V range, shunt voltage sign-extends according to configured gain range, current uses the current register scaled by gain and shunt, and power uses the power register scaled by gain and shunt with `LONG_MAX` saturation.

## State and Persistence Behavior

Configuration is computed once at probe and written to the chip. There is no measurement cache or writable hwmon state. Regmap cache exists but most registers are marked volatile. Firmware properties determine all scaling for the driver lifetime.

## Dependencies and Integration Points

The driver depends on I2C SMBus, regmap, hwmon info APIs, debugfs, firmware properties, and OF/I2C matching for `renesas,isl28022`. It is registered with `I2C_CLASS_HWMON`.

## Risks and Edge Cases

`isl28022_is_volatile_reg()` returns true even for the default case, effectively making all registers volatile despite a switch. The error message for invalid shunt resistance names `renesas,shunt-resistor-microvolt`, which does not match the actual property. Bus voltage conversion assumes fixed 60 V mode and simply masks low bits. Sign handling for shunt/current is implemented manually per gain and should be checked against datasheet encodings. `average-samples` accepts powers of two through 128 only. Debugfs raw shunt output multiplies the raw register by 10 without the same sign/range handling as hwmon shunt voltage.

## Test Signals

Test property defaults, invalid shunt range and shunt minimums, invalid average sample values, CONFIG bit construction for every gain and average, calibration writes, bus/shunt/current/power scaling, negative shunt/current readings, I2C/regmap failure propagation, debugfs output, and hwmon visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/isl28022.c -->
