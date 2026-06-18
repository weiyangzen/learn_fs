# subset-b-003830 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947-core.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947-core.c

Purpose: common hwmon core for the LTC2947 power and energy monitor, shared by the I2C and SPI bus wrappers. It exposes voltage, current, power, temperature, energy, alarms, thresholds, reset-history controls, labels, setup, runtime PM, and OF matching.

Important APIs/types/functions: `struct ltc2947_data` stores the regmap, device, computed energy LSB, and GPIO output mode. `ltc2947_core_probe()` is exported for bus drivers. `ltc2947_val_read()` and `ltc2947_val_write()` switch device pages and perform 16, 24, or 48 bit big-endian transfers with sign extension. The hwmon callbacks are `ltc2947_read()`, `ltc2947_write()`, `ltc2947_is_visible()`, and `ltc2947_read_labels()`, backed by sensor-specific helpers for `in`, `curr`, `power`, `temp`, and `energy64`.

Control flow: probe allocates state, calls `ltc2947_setup()`, then registers `devm_hwmon_device_register_with_info()`. Setup clears status, initializes safe power thresholds, optionally configures an external clock and energy scale, applies firmware properties for accumulator polarity, deadband, and GPIO direction, then enables continuous conversion. Reads and writes dispatch by hwmon sensor type, convert raw register values to standard hwmon units, and use page 0 for live/history registers and page 1 for thresholds.

State and persistence behavior: driver state is devm-managed and nonpersistent, but it programs persistent device registers for thresholds, accumulation policy, GPIO mode, and continuous/shutdown state. Historical min/max reset writes sentinel raw values. Suspend sets the shutdown bit; resume performs a dummy wake read, waits, validates control register state, and re-enables continuous mode.

Dependencies and integration points: depends on regmap supplied by the transport driver, hwmon core, clock framework, firmware property APIs, bitfield helpers, and runtime PM exports. It exports `ltc2947_core_probe`, `ltc2947_pm_ops`, and `ltc2947_of_match` for `ltc2947-i2c.c` and `ltc2947-spi.c`.

Risks: all register accesses rely on global page selection, so interleaved accesses from future code would need serialization. Conversion constants and clamp ranges must match the datasheet to avoid threshold overflow, especially on 32 bit systems. GPIO input and output firmware properties are mutually exclusive. Alarm reading intentionally uses one multi-byte transaction, and changing it can break latch semantics.

Test signals: useful tests are build coverage for I2C and SPI modules, DT/property validation for accumulator and GPIO modes, hwmon sysfs read/write checks for thresholds and reset history, suspend/resume wake tests, external clock boundary tests, and regmap fault injection for page-switch and bulk-transfer failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947-i2c.c

Purpose: I2C transport wrapper for the LTC2947 core hwmon driver.

Important APIs/types/functions: defines an 8 bit register, 8 bit value `regmap_config`; `ltc2947_probe()` creates an I2C regmap and calls `ltc2947_core_probe()`; `ltc2947_driver` binds the I2C device id `ltc2947` and the shared OF match table from the core.

Control flow: module registration is via `module_i2c_driver()`. Probe initializes the regmap with `devm_regmap_init_i2c()`, returns regmap errors directly, and delegates all device setup and hwmon registration to the core using `i2c->name`.

State and persistence behavior: no private state beyond the devm regmap. Device register programming, hwmon state, and PM behavior live in the core.

Dependencies and integration points: depends on I2C, regmap, the local `ltc2947.h` interface, `ltc2947_core_probe()`, `ltc2947_of_match`, and `ltc2947_pm_ops`.

Risks: the wrapper assumes plain 8 bit I2C register addressing is sufficient for all core page/register operations. Any core API signature change must be mirrored here and in the SPI wrapper.

Test signals: compile with `CONFIG_SENSORS_LTC2947_I2C`, bind through I2C/OF modalias, verify probe failure on regmap errors, and confirm hwmon files come from the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947-spi.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947-spi.c

Purpose: SPI transport wrapper for the LTC2947 core hwmon driver.

Important APIs/types/functions: defines a regmap with 8 bit registers and 8 bit values; `ltc2947_probe()` creates the SPI regmap and calls `ltc2947_core_probe()`; `ltc2947_driver` binds the `ltc2947` SPI id and shared OF match data.

Control flow: `module_spi_driver()` registers the wrapper. Probe uses `devm_regmap_init_spi()`, returns any regmap initialization failure, then delegates common setup, scaling, sysfs registration, and PM callbacks to the core.

State and persistence behavior: no independent runtime state. All programmed thresholds, continuous conversion mode, GPIO configuration, and suspend/resume state are owned by `ltc2947-core.c`.

Dependencies and integration points: integrates Linux SPI, regmap, hwmon through the core, and the shared local header. The driver uses `pm_ptr(&ltc2947_pm_ops)`.

Risks: correctness depends on regmap SPI semantics matching the chip command format; if bus-specific read/write flags are ever required, this simple config will be insufficient. Wrapper/core symbol export mismatches break both build and runtime binding.

Test signals: compile with SPI support, instantiate via SPI id or OF compatible, check regmap initialization and core registration, and run shared LTC2947 hwmon read/write tests over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947.h -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947.h

Purpose: private interface between the LTC2947 common core and its I2C/SPI transport drivers.

Important APIs/types/functions: forward declares `struct regmap`, declares exported `ltc2947_core_probe(struct regmap *map, const char *name)`, exported `ltc2947_of_match[]`, and exported `ltc2947_pm_ops`.

Control flow: no executable logic. It lets each bus wrapper pass its regmap to the shared core and reuse the same OF and PM definitions.

State and persistence behavior: none; this is a declaration-only header.

Dependencies and integration points: included by `ltc2947-i2c.c` and `ltc2947-spi.c`; coupled to symbols implemented in `ltc2947-core.c`.

Risks: any mismatch between declarations and exported core symbols causes compile/link failures. The header intentionally keeps transport wrappers thin, so adding bus-specific behavior should avoid polluting the common API unless required.

Test signals: kernel build/link coverage for both transport modules and modpost symbol export checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2990.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc2990.c

Purpose: hwmon driver for the LTC2990 I2C power/temperature monitor, exposing internal temperature, configurable remote temperature/current/voltage channels, and VCC.

Important APIs/types/functions: `struct ltc2990_data` stores the I2C client and two mode fields. `ltc2990_get_value()` maps logical hwmon attributes to measurement registers and converts raw words to millidegrees, millivolts, or current sense voltage. `ltc2990_attrs_visible()` hides sysfs attributes not enabled by the configured measurement mode.

Control flow: probe checks SMBus byte and word functionality, reads `lltc,meas-mode` from firmware or the existing control register, validates mode bits, writes control mode, triggers acquisition, then registers explicit sysfs attribute groups with hwmon. Reads call `i2c_smbus_read_word_swapped()` per attribute.

State and persistence behavior: only the selected mode is cached in driver memory. Probe writes the control and trigger registers to start continuous acquisition; no suspend/resume or threshold persistence is implemented.

Dependencies and integration points: uses I2C SMBus, firmware property APIs, `hwmon_device_register_with_groups()`, and classic `SENSOR_DEVICE_ATTR_RO` sysfs definitions.

Risks: channel visibility is derived from intersection masks and can be wrong if mode decoding changes. Current outputs are reported as voltage across the shunt rather than board-specific current because no shunt property is modeled. Firmware mode property is required when a fwnode exists.

Test signals: build and probe tests, validation of all eight mode combinations, sysfs visibility checks per mode, conversion tests for signed temperature/current paths, and I2C failure injection for reads and initial writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2990.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2991.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc2991.c

Purpose: modern hwmon driver for the Analog Devices LTC2991 I2C monitor with VCC, up to four channel pairs usable as voltage, current, or temperature inputs, and internal temperature.

Important APIs/types/functions: `struct ltc2991_state` stores regmap, per-pair shunt resistors, and temperature-enable flags. `ltc2991_read_reg()` supports byte and big-endian word reads. `ltc2991_get_voltage()`, `ltc2991_get_curr()`, and `ltc2991_get_temp()` implement unit conversion. The hwmon callbacks are `ltc2991_read()` and `ltc2991_is_visible()`.

Control flow: probe allocates state, initializes an I2C regmap, enables the `vcc` regulator, scans child firmware nodes for pair index, `shunt-resistor-micro-ohms`, and `adi,temperature-enable`, programs V1-V4 and V5-V8 control registers, enables repeat acquisition, triggers all channels, and registers hwmon.

State and persistence behavior: shunt and temperature mode choices are cached in memory and also programmed into device control registers. No writable hwmon thresholds are exposed. The regulator is devm-managed and enabled for the device lifetime.

Dependencies and integration points: uses regmap over I2C, regulator framework, firmware child nodes, hwmon info API, bitops, and OF/I2C device tables.

Risks: current conversion divides by the configured shunt, so zero is rejected and absent shunts hide current channels. Visibility logic maps voltage channels around temperature and differential modes; off-by-one mistakes can expose invalid readings. All channels are enabled even when some attributes are hidden.

Test signals: DT child-node tests for each pair mode, regulator enable failure tests, sysfs visibility matrix for voltage/current/temp combinations, raw conversion fixtures, and regmap write failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2991.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2992.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc2992.c

Purpose: hwmon and GPIO driver for the LTC2992 dual wide-range power monitor. It reports channel voltage, current, power, history, thresholds, alarms, and GPIO ADC channels while also registering a gpiochip for the four GPIO pins.

Important APIs/types/functions: `struct ltc2992_state` holds client, regmap, gpiochip, GPIO names, mutex, and two shunt values. `ltc2992_read_reg()` and `ltc2992_write_reg()` implement multi-byte big-endian register access. GPIO callbacks include get/set and multiple variants. Hwmon callbacks include `ltc2992_read()`, `ltc2992_write()`, and `ltc2992_is_visible()`.

Control flow: probe creates the regmap, parses child-node shunt resistors for channels 0 and 1, configures GPIO names and chip callbacks, then registers hwmon. Reads dispatch to voltage, GPIO voltage, current, or power helpers; writes set threshold registers or reset history through `LTC2992_CTRLB`.

State and persistence behavior: shunt values and gpiochip metadata live in driver state. Threshold writes and history reset modify device registers. GPIO operations are serialized by `gpio_mutex`; hwmon register accesses otherwise go directly through regmap.

Dependencies and integration points: depends on I2C, regmap, gpio/driver, firmware properties, hwmon, and OF/I2C matching.

Risks: current and power attributes are hidden without shunt configuration, so board data is essential for meaningful output. GPIO polarity is inverted in get/set paths and must match hardware semantics. Multi-byte register assembly is custom and should be protected by tests when changed.

Test signals: gpiochip get/set tests with mocked registers, DT shunt parsing validation, hwmon visibility with and without shunts, threshold write/readback conversion checks, alarm bit mapping checks, and regmap failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2992.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4151.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc4151.c

Purpose: classic sysfs hwmon driver for the LTC4151 high-voltage I2C current and voltage monitor.

Important APIs/types/functions: `struct ltc4151_data` stores client, update mutex, cache validity, last update time, shunt value, and six raw registers. `ltc4151_update_device()` refreshes all registers at most six times per second. `ltc4151_get_value()` converts VIN, ADIN, and SENSE registers.

Control flow: probe checks SMBus byte support, reads optional OF `shunt-resistor-micro-ohms` with a 1000 micro-ohm default, rejects zero, initializes the cache lock, and registers `in1_input`, `in2_input`, and `curr1_input`. Reads refresh the cache when stale and emit converted values.

State and persistence behavior: maintains a jiffies-gated volatile register cache only. No device configuration, thresholds, or persistent writes are performed.

Dependencies and integration points: depends on I2C SMBus byte reads, OF property access, hwmon classic groups, and jiffies caching.

Risks: stale data is intentional for up to HZ/6. Current accuracy depends entirely on the shunt property/default. A read failure aborts the refresh and propagates the error without preserving a valid partial update.

Test signals: probe with default and explicit shunt, zero-shunt rejection, cache refresh interval behavior, conversion checks for all three channels, and SMBus read failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4151.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4215.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc4215.c

Purpose: hwmon driver for the LTC4215 hot-swap controller, exposing input/output voltages, current, power, and alarm bits through classic sysfs attributes.

Important APIs/types/functions: `struct ltc4215_data` stores client, update mutex, cache state, and seven raw registers. `ltc4215_update_device()` caches registers at 10 Hz. Conversion helpers compute voltages, current through a fixed 4 milliohm sense resistor, derived power, and status alarms.

Control flow: probe checks SMBus byte support, allocates state, clears the fault register, and registers sysfs groups. Attribute reads refresh the cache if stale, convert the selected register, or test cached status bits.

State and persistence behavior: the driver keeps a volatile cache and writes the fault register to zero at probe. It has no writable thresholds and no PM hooks.

Dependencies and integration points: uses I2C SMBus byte access, hwmon sysfs attribute groups, jiffies, and fixed board assumptions from the original driver.

Risks: failed register reads are converted to zero during cache refresh instead of returning an error, which can hide bus faults. Current and power calculations assume a fixed sense resistor. Power uses ADIN as output voltage in the derived calculation.

Test signals: sysfs reads for voltage/current/power/alarm attributes, cache refresh timing, fault clear on probe, and I2C failure behavior showing zeroed cached values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4222.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc4222.c

Purpose: hwmon driver for the LTC4222 dual hot-swap controller, exposing per-channel source/ADIN voltages, sense current, and fault alarms.

Important APIs/types/functions: `ltc4222_get_value()` reads two-byte ADC registers through regmap and converts 10 bit raw values. `ltc4222_bool_show()` reads fault registers, reports selected fault bits, and clears reported latches. Static `SENSOR_DEVICE_ATTR_2_RO` entries map faults to each channel.

Control flow: probe initializes an I2C regmap, clears both fault registers, then registers classic hwmon sysfs groups. Input reads use regmap bulk reads; alarm reads use regmap reads and update bits to clear latched faults.

State and persistence behavior: no driver cache. The only persistent side effects are clearing fault registers at probe and when alarm files are read.

Dependencies and integration points: depends on I2C regmap, hwmon sysfs groups, bitops, and I2C device id matching.

Risks: reading an alarm is destructive for the reported fault bits. Current assumes a 1 milliohm sense resistor and must be scaled externally for other boards. Register conversion depends on shifting the 16 bit sample by six.

Test signals: regmap conversion tests for ADIN/source/sense, alarm read-and-clear behavior, probe fault clearing, and dual-channel attribute naming/bit mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4222.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4245.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc4245.c

Purpose: hwmon driver for the LTC4245 multi-supply hot-swap controller, reporting four supply rails, currents, derived power, alarms, and optional GPIO ADC readings.

Important APIs/types/functions: `struct ltc4245_data` stores client, cache state, control registers, voltage registers, optional GPIO mode, and cached GPIO ADC values. `ltc4245_update_device()` refreshes control and voltage registers. `ltc4245_update_gpios()` implements round-robin sampling when extra GPIOs are enabled.

Control flow: probe checks SMBus byte support, reads platform data or OF `ltc4245,use-extra-gpios`, clears fault registers, and registers hwmon info callbacks. Reads dispatch by hwmon type, map channels to voltage/current register arrays, handle GPIO channels above the supply channels, and compute power from cached current and voltage.

State and persistence behavior: data is cached for one second. Extra GPIO readings can be marked `-EAGAIN` when stale for more than five seconds. Probe clears fault registers and may reprogram the GPIO register to rotate ADC sampling.

Dependencies and integration points: uses I2C SMBus, hwmon info API, platform data `linux/platform_data/ltc4245.h`, OF property fallback, and jiffies.

Risks: no mutex protects the cache despite comments mentioning locking, so concurrent sysfs reads can race on cached arrays. Failed reads are stored as zero. Optional GPIO channels may return `-EAGAIN` until their turn in the round-robin sampler.

Test signals: visibility with and without extra GPIOs, cache refresh and GPIO staleness behavior, conversion checks for positive and negative rails, fault bit mapping, and I2C failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4245.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4260.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc4260.c

Purpose: hwmon driver for the LTC4260 positive-voltage hot-swap controller, exposing source voltage, ADIN voltage, sense current, and latched fault alarms.

Important APIs/types/functions: `ltc4260_get_value()` converts single-byte source, ADIN, and sense registers. `ltc4260_bool_show()` reports selected fault bits and clears them. The driver uses a simple regmap config over I2C and classic `SENSOR_DEVICE_ATTR_RO` groups.

Control flow: probe initializes I2C regmap, clears the fault register, and registers hwmon sysfs groups. Attribute reads go directly to regmap; alarm reads clear any fault bits they report.

State and persistence behavior: no cache. Probe and alarm reads mutate the fault register. No writable thresholds or PM hooks are present.

Dependencies and integration points: I2C regmap, hwmon sysfs groups, and I2C device id matching.

Risks: alarm sysfs reads are destructive. Current assumes an effective 1 milliohm shunt and the fixed datasheet scaling. The driver exposes no device tree shunt override.

Test signals: probe with regmap failure injection, conversion tests for each register, fault clear at probe, and read-to-clear alarm behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4260.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4261.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc4261.c

Purpose: hwmon driver for the LTC4261 negative-voltage hot-swap controller, exposing two voltage inputs, one current input, and voltage/current alarms.

Important APIs/types/functions: `struct ltc4261_data` stores client, update mutex, validity, timestamp, and ten raw registers. `ltc4261_update_device()` refreshes registers at HZ/4. `ltc4261_get_value()` converts 10 bit ADC fields. `ltc4261_bool_show()` reports and clears fault bits.

Control flow: probe checks SMBus byte support, validates the status register can be read, allocates state, clears faults, and registers sysfs groups. Reads refresh the cache, convert selected registers, or read latched fault bits from the cache and clear them on the device.

State and persistence behavior: maintains a mutex-protected volatile cache. Faults are cleared at probe and on alarm reads. A refresh failure invalidates the cache and returns the bus error.

Dependencies and integration points: uses I2C SMBus, hwmon classic groups, jiffies, and I2C device id matching.

Risks: voltage alarm bits are shared by chip design and exposed on both voltage channels, which consumers must interpret carefully. Current assumes 1 milliohm shunt scaling. Alarm reads are destructive.

Test signals: status-read probe guard, cache refresh failure handling, shared voltage alarm mapping, fault read-and-clear behavior, and conversion checks for voltage/current.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4261.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4282.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc4282.c

Purpose: full hwmon, clock provider, and debugfs driver for the LTC4282 high-current hot-swap controller. It exposes VDD/VSOURCE/GPIO voltage channels, current, power, energy metering, limits, history, alarms, labels, configurable clocks, and fault-log debugfs files.

Important APIs/types/functions: `struct ltc4282_state` stores regmap, `clk_hw`, cached VDD/VSOURCE state, sense resistor scaling, voltage full-scale data, power max, and energy enable state. Core helpers convert word/byte ADC values, cache shared VDD/VSOURCE registers, reset history, read/clear alarms, and handle energy math. `ltc4282_setup()`, `ltc428_clks_setup()`, and `ltc4282_gpio_setup()` configure firmware-driven behavior.

Control flow: probe creates regmap, issues a soft reset, waits 3.2 seconds, configures clock input/output, reads EEPROM defaults, applies firmware overrides for sense resistor, VIN mode, current limit, divider, GPIO modes, and retry settings, programs safe maximum limits, registers hwmon, then creates debugfs fault-log files. Hwmon callbacks dispatch by type to read/write helpers and visibility rules.

State and persistence behavior: device EEPROM defaults are read but runtime configuration is programmed into volatile registers. Shared VDD/VSOURCE monitoring requires cached history and threshold values when switching enabled channels. Energy enable state is cached and controls `energy64` reads. Debugfs and hwmon alarm paths may clear logged bits.

Dependencies and integration points: uses I2C regmap, hwmon, common clock framework/provider APIs, debugfs, firmware properties, math overflow helpers, bitfields, and OF matching.

Risks: scaling formulas are overflow-sensitive and include 32 bit safeguards. VDD and VSOURCE share hardware registers, so cache sync bugs can lose limits/history. Probe reset has a long fixed delay. Firmware property combinations for GPIO2/GPIO3 ADC muxing can conflict. Alarm/debugfs reads clear log bits.

Test signals: property matrix tests for VIN/current/divider/GPIO modes, clock input boundary and output-rate tests, energy conversion overflow fixtures, VDD/VSOURCE enable cache-sync tests, debugfs fault-log clear behavior, suspendless reset timing checks, and regmap failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc4282.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltq-cputemp.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltq-cputemp.c

Purpose: platform hwmon driver for the Lantiq VR9 v1.2 CPU temperature sensor.

Important APIs/types/functions: `ltq_cputemp_enable()` and `ltq_cputemp_disable()` manipulate `CGU_TEMP_PD` in `CGU_GPHY1_CR`. `ltq_read()` extracts the 9 bit temperature field and converts it to millidegrees. `ltq_hwmon_ops` exposes a single `temp1_input` plus chip thermal-zone registration.

Control flow: probe rejects non-VR9 v1.2 SoCs, registers a devm cleanup action to disable the sensor, enables it, then registers hwmon with info callbacks.

State and persistence behavior: no driver-private state. The driver toggles a SoC CGU bit for the device lifetime and clears it on cleanup.

Dependencies and integration points: depends on Lantiq SoC helpers from `<lantiq_soc.h>`, platform/OF matching, and hwmon thermal zone registration.

Risks: direct CGU register access is SoC-specific and probe is guarded only by `ltq_soc_type()`. The enable/disable bit name suggests power-down semantics, so hardware documentation is needed when changing polarity. No locking is used around CGU read-modify-write.

Test signals: build on Lantiq targets, probe rejection on other SoCs, register bit set/clear validation, and conversion tests for raw extremes covering -38 C to 154 C.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltq-cputemp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/macsmc-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/macsmc-hwmon.c

Purpose: Apple Silicon SMC hwmon platform driver that dynamically exposes temperature, voltage, current, power, and fan sensors described by device tree child nodes.

Important APIs/types/functions: `struct macsmc_hwmon` owns dynamic channel info arrays and sensor/fan collections. `macsmc_hwmon_read_key()` decodes SMC key data types including IEEE-754 float, 48.16 fixed point, and integer formats. `macsmc_hwmon_create_sensor()` and `macsmc_hwmon_create_fan()` parse DT keys. Hwmon callbacks handle read, write, visibility, and labels.

Control flow: probe requires an OF hwmon node from the parent Apple SMC MFD, allocates state, walks child nodes by prefixes `current-`, `fan-`, `power-`, `temperature-`, and `voltage-`, validates SMC keys, builds dynamic hwmon config arrays, then registers `macsmc_hwmon`. Reads fetch SMC keys live and scale to hwmon units; fan target writes optionally switch fans to manual mode.

State and persistence behavior: sensor metadata and labels are devm-managed. Values are not cached. Fan manual state is tracked per fan and writes to SMC mode/target keys persist in controller state until reset or a write of zero returns to automatic mode.

Dependencies and integration points: integrates with the Apple SMC MFD API, OF child-node schemas, hwmon core, platform bus, and the unsafe module parameter `fan_control`.

Risks: fan control is intentionally gated because the SMC does not sanity-check target speeds. Float conversion clamps overflow/underflow and must remain careful. Bad or missing DT key definitions silently reduce sensor count, and probe fails if no valid sensors remain.

Test signals: DT parsing tests for each sensor prefix, SMC key type conversion fixtures, label visibility checks, fan min/max/target/mode behavior with `fan_control` off and on, and probe failure when all keys are invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/macsmc-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max1111.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/max1111.c

Purpose: SPI hwmon driver for Maxim MAX1110/MAX1111/MAX1112/MAX1113 low-power multichannel 8 bit ADCs, with legacy SharpSL channel export.

Important APIs/types/functions: `struct max1111_data` stores SPI device, hwmon device, prebuilt `spi_message`, transfers, buffers, mutex, channel select shift, and LSB scale. `max1111_read()` builds the command byte, performs `spi_sync()`, validates returned framing bits, and returns the sample. `show_adc()` scales raw values to millivolts.

Control flow: probe configures SPI mode 0 and 8 bits per word, chooses scale and selector shift by chip id, initializes the reusable transfer, creates sysfs groups for channels 0-3 and optionally 4-7, then registers hwmon. Remove unregisters hwmon and removes both groups.

State and persistence behavior: the reusable SPI message and buffers are protected by `drvdata_lock`. No device configuration persists beyond each command. Under `CONFIG_SHARPSL_PM`, a global pointer exposes `max1111_read_channel()`.

Dependencies and integration points: depends on SPI, classic hwmon/sysfs, optional SharpSL PM integration, and SPI device ids.

Risks: manual sysfs group management must stay balanced on error and remove paths. The global SharpSL pointer supports only one active device. Raw frame validation rejects unexpected status bits and may expose wiring/timing issues as `-EINVAL`.

Test signals: probe/remove error unwinding, channel set for each chip variant, SPI transfer framing tests, concurrent read locking, and SharpSL exported read behavior when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max1111.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max127.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/max127.c

Purpose: I2C hwmon driver for the MAX127 8 channel ADC with per-channel configurable range and polarity.

Important APIs/types/functions: `struct max127_data` stores the I2C client and per-channel control bytes. `max127_select_channel()` sends a control byte, `max127_read_channel()` reads the two-byte conversion, and `max127_process_raw()` converts unipolar or bipolar 12 bit samples to millivolts. Hwmon callbacks expose input, min, and max.

Control flow: probe initializes each control byte with start bit and channel select, then registers hwmon. Reads select a channel, read raw data, and convert using the cached control byte. Writes to min and max mutate the cached control byte to choose bipolar/unipolar and half/full range for future conversions.

State and persistence behavior: range/polarity state is driver-local and not preserved across unbind or reboot. Device channel selection occurs per read; no thresholds are programmed in hardware.

Dependencies and integration points: uses raw I2C transfers rather than SMBus helpers, hwmon info API, and I2C device id binding.

Risks: there is no mutex around `ctrl_byte`, so concurrent sysfs writes/reads can race channel configuration. Min/max files are configuration controls rather than hardware limits. Two-message conversion timing relies on device behavior after channel select.

Test signals: raw conversion fixtures for all range/polarity modes, min/max write behavior, I2C short-transfer handling, and concurrent access stress if locking is added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max127.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max16065.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/max16065.c

Purpose: classic sysfs hwmon driver for MAX16065/MAX16066/MAX16067/MAX16068/MAX16070/MAX16071 system managers and monitors with multiple ADC channels, nonvolatile fault registers, optional secondary limits, and optional current sensing.

Important APIs/types/functions: `struct max16065_data` stores chip type, groups, cache, ranges, raw ADC values, limits, current sense state, and fault bytes. Conversion helpers map 10 bit ADCs and 8 bit limits to millivolts and current. `max16065_update_device()` refreshes ADCs and faults. Limit, input, current, and alarm sysfs handlers implement reads, writes, and clear-on-read faults.

Control flow: probe checks SMBus byte and word support, determines chip capabilities from match data, reads secondary limit mode, scale registers, and initial limits, builds the applicable attribute-group list, configures current attributes if enabled, then registers hwmon. Reads refresh a one-second cache; writes update hardware limit registers under the mutex.

State and persistence behavior: ADC/fault data is cached for one second. Limits are cached in millivolts and written to device registers. Fault registers are nonvolatile and reported alarms are cleared by writing the selected bit back.

Dependencies and integration points: depends on I2C SMBus, hwmon sysfs groups, jiffies caching, and chip id match data for variant capabilities.

Risks: cached ADC values store negative error codes and are checked on read, but partial refreshes can mix old and error data. Attribute visibility is derived from channel count/range and secondary capability. Fault alarm reads are destructive. Current reporting depends on current-control gain interpretation.

Test signals: variant matrix for channel count/current/secondary groups, scale and limit conversion tests, alarm clear behavior, cache refresh timing, current gain/range tests, and I2C error propagation from ADC and setup reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max16065.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max1619.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/max1619.c

Purpose: hwmon driver for the MAX1619 local/remote temperature sensor with limits, alarms, fault status, update interval control, detection, and regmap caching.

Important APIs/types/functions: `get_alarms()` reads status/config together and normalizes the OVERT polarity. `max1619_temp_read/write()` handle temperature values, limits, alarms, and fault. `max1619_chip_read/write()` expose update interval and aggregate alarms. Custom regmap bus callbacks translate logical readable registers to separate write addresses.

Control flow: detection validates config, conversion rate, status reserved bits, manufacturer id, and chip id. Probe initializes custom regmap, programs 2 Hz conversion rate, starts conversions, and registers hwmon info callbacks. Runtime reads and writes go through regmap with volatile status/temp registers and cached writable limit registers.

State and persistence behavior: regmap cache stores nonvolatile-ish writable registers via maple cache; volatile measurements are read live. Probe changes conversion rate and clears standby. Limit and update interval writes persist in device registers.

Dependencies and integration points: I2C class HWMON autodetect, OF optional match, regmap custom bus/cache, hwmon info API, and util `find_closest_descending()`.

Risks: custom write offset mapping is easy to break because device write addresses differ from read addresses. Alarm polarity depends on config bit normalization. Update interval write chooses closest supported descending value.

Test signals: autodetect positive/negative cases, regmap write-address mapping tests, update interval selection tests, alarm polarity fixtures, and temp limit clamp tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max1619.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max1668.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/max1668.c

Purpose: hwmon driver for MAX1668/MAX1805/MAX1989 multi-channel remote temperature sensors with limits, alarms, fault detection, autodetect, and optional read-only mode.

Important APIs/types/functions: `struct max1668_data` stores regmap and channel count. `max1668_read()` handles temperature, min/max limits, min/max alarms, and remote diode fault. `max1668_write()` updates limits. Custom regmap bus callbacks implement shifted write addresses. The `read_only` module parameter changes limit file permissions.

Control flow: detect validates Maxim manufacturer id and device id, filling the I2C type. Probe checks SMBus byte support, creates custom cached regmap, derives channel count from match data, then registers hwmon. Visibility hides channels above the variant count and hides writes when `read_only` is set.

State and persistence behavior: channel count and regmap live in driver state. Limits are written to chip registers and may be cached by regmap; temperatures/status registers are volatile.

Dependencies and integration points: I2C HWMON class scanning, regmap custom bus/cache, hwmon info API, module parameter infrastructure, and I2C device ids.

Risks: status-bit mapping differs for local and remote channels. Fault reporting checks both global status and a 127 C sentinel. The shifted write address mapping must match the chip command protocol.

Test signals: detection for all supported ids, channel visibility per variant, read-only permission checks, limit write/readback through regmap offset mapping, and alarm/fault bit fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max1668.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max197.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/max197.c

Purpose: platform hwmon driver for MAX197/MAX199 8 channel ADCs using board-supplied conversion callbacks.

Important APIs/types/functions: `struct max197_data` stores platform data, hwmon device, mutex, range limit, scaling flag, and per-channel control bytes. Range helper functions manipulate bipolar and full-range bits. Sysfs handlers expose `inN_input`, `inN_min`, and `inN_max`.

Control flow: probe requires platform data and a `convert()` callback, chooses chip limit/scaling by platform id, initializes control bytes, creates a manual sysfs group, and registers hwmon. Reads call the board callback under mutex and optionally scale raw MAX197 values. Min/max writes update cached polarity/range bits.

State and persistence behavior: per-channel range/polarity is driver-local and protected by a mutex. Hardware conversion is delegated to platform data; no threshold registers exist.

Dependencies and integration points: platform bus, `linux/platform_data/max197.h`, classic hwmon/sysfs, board-specific convert callback, and platform device ids.

Risks: no platform data means no device. The convert callback is trusted for I/O and raw format. Manual sysfs and hwmon registration require balanced cleanup. Min/max files configure conversion mode, not alarm thresholds.

Test signals: probe rejection for missing platform data/callback, MAX197 vs MAX199 scaling behavior, range write state transitions, mutex-protected concurrent reads/writes, and cleanup on hwmon registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max197.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max31722.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/max31722.c

Purpose: SPI hwmon driver for MAX31722/MAX31723 digital thermometer/thermostats, exposing one temperature input.

Important APIs/types/functions: `struct max31722_data` stores hwmon device, SPI device, and cached config mode. `max31722_set_mode()` writes the config register with continuous or standby mode. `max31722_temp_show()` reads a little-endian 16 bit temperature register and converts 12 bit samples at 62.5 millidegrees per bit.

Control flow: probe allocates state, sets continuous conversion with 12 bit resolution, registers hwmon groups, and falls back to standby on registration failure. Remove unregisters hwmon and attempts standby. Suspend and resume switch standby/continuous via simple PM ops.

State and persistence behavior: cached mode mirrors the config register. Probe/resume leave the chip converting; remove/suspend put it in standby.

Dependencies and integration points: SPI helpers, classic hwmon groups, PM sleep ops, and SPI device ids.

Risks: `spi_w8r16()` return handling casts through `ssize_t` and then little-endian conversion; changes must preserve signed temperature interpretation. Remove cannot recover if standby write fails. Only temperature input is exposed, not thermostat thresholds.

Test signals: SPI config write tests, temperature conversion fixtures including negative values, PM suspend/resume mode transitions, and probe error path verifying standby.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max31722.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max31730.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/max31730.c

Purpose: hwmon driver for the MAX31730 four-channel temperature sensor, including channel enable, offsets for remote channels, limits, alarms, fault status, autodetect, and PM stop/resume.

Important APIs/types/functions: `struct max31730_data` stores client, original/current config, offset enable mask, and channel enable mask. `max31730_read()` handles input, min/max limits, enable state, offset, faults, and alarms. `max31730_write()` updates limits, channel enables, and offsets. `max31730_write_config()` preserves cached config while forcing normal range.

Control flow: probe checks SMBus support, caches channel/offset/config registers, stops conversions if all channels are disabled or clears stop otherwise, registers a devm cleanup action to restore original config, and registers hwmon. Detection validates manufacturer/revision and reserved low nibbles in temperature registers. PM suspend sets STOP; resume clears it.

State and persistence behavior: original config is restored on driver removal. Channel enables and offset enables are cached and updated on writes. Limit and offset writes update device registers. Suspend/resume changes the STOP bit.

Dependencies and integration points: I2C SMBus byte/word operations, I2C class HWMON detection, OF match, hwmon info API, devm cleanup actions, and PM ops.

Risks: `temp_min` uses one shared register while visibility makes remote channels read-only for min. Offset is not valid for channel 0. Enabling/disabling channels updates cached state but config STOP behavior is only set at probe and PM. Detection depends on reserved low bits being zero.

Test signals: autodetect positive/negative cases, config restore on remove, PM STOP bit transitions, channel enable read/write, offset clamp/baseline behavior, shared min limit semantics, and temperature conversion fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max31730.c -->
