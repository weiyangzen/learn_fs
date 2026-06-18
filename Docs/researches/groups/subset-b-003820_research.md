# subset-b-003820

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adm1031.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adm1031.c

Purpose: Linux hwmon I2C driver for Analog Devices ADM1030/ADM1031 fan controllers and temperature monitors. It exposes fan tachometer readings, PWM control, automatic fan temperature points, temperature limits/offsets, per-sensor alarms, and an update interval through legacy hwmon sysfs attribute groups.

Important APIs/types/functions: `struct adm1031_data` is the per-client cache and contains the I2C client, mutex, chip type, update timing, cached register fields, alarm state, PWM snapshots, and an ADM1030/ADM1031-specific automatic fan channel table. `adm1031_update_device()` refreshes the cached sensor state under `update_lock`. Conversion macros translate register encodings for temperature, fractional extension bits, offsets, fan RPM/divisors, PWM nibbles, and automatic temperature ranges. Store/show callbacks implement `fan*_input`, `fan*_min`, `fan*_div`, `pwm*`, `auto_fan*_channel`, `auto_temp*_min/max/off`, `temp*_input/min/max/crit/offset`, `alarms`, and `update_interval`. `adm1031_detect()`, `adm1031_init_client()`, and `adm1031_probe()` provide I2C detection, device enablement, and hwmon registration.

Control flow: probe allocates state, selects the ADM1030 or ADM1031 auto-channel table from match data, enables tach/PWM monitoring in config registers, reads the chip update rate, builds mandatory and optional sysfs groups, and registers the hwmon device. Reads call `adm1031_update_device()`, which refreshes temperatures, fractional extension registers, limits, auto-temperature registers, config, alarms, fan dividers, tach readings, and PWM nibbles when the cache is stale. Writes parse sysfs input, clamp it to chip ranges, update the cached field, and write the corresponding SMBus byte. Automatic fan mode transitions save manual PWM values, force 33 percent PWM while auto mode is active, and restore manual PWM values when leaving auto mode.

State and persistence: runtime state lives in chip registers and the driver cache. The cache is valid for `update_interval` milliseconds and is invalidated after fan divisor changes. `old_pwm[]` persists the last manual PWM values across automatic/manual mode toggles during driver lifetime. The driver enables monitoring at probe but does not restore previous config on unload.

Dependencies and integration: depends on I2C SMBus byte-data operations, `hwmon-sysfs`, `jiffies`, mutexes, and the I2C hwmon class scanner. It integrates through `module_i2c_driver`, `I2C_CLASS_HWMON`, address scanning at `0x2c..0x2e`, and standard lm-sensors style sysfs names.

Risks: many SMBus read/write helpers return `u8` or ignore write errors, so transient bus failures can be cached as register data or silently missed. Cache coherency is mostly manual; several writes do not invalidate dependent readings. Automatic fan channel mapping is table-driven and easy to regress for ADM1030, where some table entries are invalid. The file uses legacy `sprintf()` sysfs output rather than `sysfs_emit()`.

Test signals: useful checks are `i2cdetect`/manual instantiation on ADM1030 and ADM1031 addresses, `sensors` output for all mandatory and optional attributes, write/readback tests for fan divisors and thresholds, automatic/manual PWM transition tests, update interval rounding tests, and forced alarm-bit verification through mocked SMBus or real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adm1031.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adm1177.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adm1177.c

Purpose: hwmon I2C driver for the Analog Devices ADM1177 hot-swap controller and digital power monitor. It exposes input voltage, current, and programmable current shutdown threshold through the modern `hwmon_device_register_with_info()` interface.

Important APIs/types/functions: `struct adm1177_state` stores the I2C client, shunt resistor value in micro-ohms, alert threshold in microamps, and voltage range mode. `adm1177_read_raw()` performs raw byte receives for conversion samples. `adm1177_write_cmd()` programs continuous voltage/current conversion and range bits. `adm1177_write_alert_thr()` scales a microamp threshold into the 8-bit alert register. `adm1177_read()`, `adm1177_write()`, and `adm1177_is_visible()` implement the hwmon callbacks for `in0_input`, `curr1_input`, and `curr1_max`.

Control flow: probe allocates state, optionally enables a `vref` regulator, reads firmware properties `shunt-resistor-micro-ohms`, `adi,shutdown-threshold-microamp`, and `adi,vrange-high-enable`, writes the alert threshold when current measurement is configured, starts continuous conversions, and registers the hwmon device. Input reads fetch three bytes and split the packed 12-bit voltage/current fields. Current conversion applies the 105.84 mV shunt full-scale and the configured sense resistor; voltage conversion selects either 26.35 V or 6.65 V full-scale depending on range mode. Threshold writes clamp to the current full-scale and update the alert register.

State and persistence: persistent device state is limited to the command byte and alert threshold register. Driver state caches `alert_threshold_ua` after successful writes and hides current attributes when no shunt resistor property is provided. There is no suspend/resume path or restore of pre-probe command state.

Dependencies and integration: depends on I2C byte/byte-data operations, `math64` scaling, optional regulator consumer support, firmware device properties, and the hwmon channel-info API. It matches `adm1177` I2C IDs and `adi,adm1177` OF nodes.

Risks: `i2c_master_recv()` is accepted as success for any nonnegative return, so short reads are not rejected. Current channels are invisible without a nonzero shunt value, making board description critical. Property and unit mistakes directly affect current and threshold scaling. The optional regulator result is ignored except for deferred probe, so non-defer regulator errors do not block operation.

Test signals: verify with device-tree or ACPI properties for shunt, threshold, and range mode; read `in0_input` and `curr1_input` against known loads; write `curr1_max` at boundary values; test no-shunt visibility; and use I2C fault injection for receive/write failures and probe-defer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adm1177.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adm9240.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adm9240.c

Purpose: hwmon I2C driver for the ADM9240, DS1780, and LM81 register-compatible monitor chips. It reports six scaled voltage inputs, one temperature sensor, two fans with automatic divider handling, alarms, analog output, VID, and chassis intrusion latch state.

Important APIs/types/functions: `struct adm9240_data` stores the regmap, device pointer, cached fan dividers, and VRM. Scaling helpers convert voltage, temperature, fan period, and analog output values. `adm9240_fan_min_write()` chooses a suitable fan clock divider for requested minimum RPM. `adm9240_init_client()` opens limits and starts conversion on cold chips. `adm9240_read()`/`adm9240_write()` dispatch to chip, intrusion, voltage, fan, and temperature handlers. Extra sysfs attributes expose `aout_output` and `cpu0_vid`.

Control flow: detection verifies SMBus byte-data support, checks that the chip address register matches the I2C address, then identifies the vendor ID. Probe creates an 8-bit regmap, initializes limits/start state, reads initial fan dividers, and registers hwmon channels plus extra groups. Voltage reads select input, min, max, or alarm registers and apply per-channel nominal scaling. Fan reads can increase the fan divider on overflow before returning RPM. Intrusion write accepts only `0` and writes the chassis-clear latch. Temperature reads combine integer and half-degree status bits.

State and persistence: most state is in device registers. Regmap marks live measurements, alarms, VID, and analog output volatile. Fan dividers are cached in `data->fan_div[]` and updated when overflow or minimum writes change the hardware divider. `vrm` is selected at probe for VID conversion and persists until driver removal.

Dependencies and integration: depends on I2C hwmon scanning, regmap, `hwmon-vid`, and modern hwmon channel callbacks. It scans addresses `0x2c..0x2f` and supports legacy non-OF board discovery through `detect`.

Risks: fan divider updates in read paths mutate hardware as a side effect, which can surprise tests and concurrent readers. `adm9240_is_visible()` uses `case hwmon_temp` where `hwmon_temp_input` is expected, likely hiding `temp1_input` in modern hwmon semantics. Some `sprintf()` outputs remain. DS1780/LM81 compatibility depends on register behavior not revalidated beyond IDs.

Test signals: check generated hwmon attribute visibility, especially `temp1_input`; exercise cold-start initialization on a reset chip; verify fan overflow causes divider changes and RPM remains sane; write voltage, temperature, fan, analog output, and intrusion attributes; and run regmap/I2C error injection for init and read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adm9240.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ads7828.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ads7828.c

Purpose: hwmon I2C driver for TI ADS7828 12-bit and ADS7830 8-bit 8-channel ADCs. It exposes eight read-only voltage input attributes using either internal or external reference voltage and single-ended or differential command modes.

Important APIs/types/functions: `struct ads7828_data` holds the regmap, base command byte, and ADC LSB resolution in microvolts. `ads7828_cmd_byte()` maps hwmon channel numbers to the datasheet command channel encoding. `ads7828_in_show()` issues a regmap read using that command byte and formats millivolts. Probe selects ADS7828 versus ADS7830 via match data and chooses the appropriate 16-bit or 8-bit regmap config.

Control flow: probe allocates state, reads platform data or OF settings, optionally reads a `vref` regulator voltage, clamps reference range, computes sample resolution, initializes regmap, builds the command byte from reference and input-mode flags, performs a dummy read to enable/settle the internal reference when used, and registers eight `in*_input` sysfs attributes.

State and persistence: there is no periodic cache. The command byte and LSB resolution are fixed after probe. The ADC itself is programmed per read by the command byte, while internal reference enablement is triggered by the dummy read and subsequent commands.

Dependencies and integration: depends on I2C regmap, optional regulator consumer support, legacy platform data, OF property `ti,differential-input`, and hwmon sysfs attribute groups. It matches `ti,ads7828` and `ti,ads7830`.

Risks: optional regulator acquisition does not explicitly handle `-EPROBE_DEFER`, because only the non-error path is used; this may skip a late regulator and fall back to internal/default assumptions. External reference validation depends on `regulator_get_voltage()` returning a useful value. Differential mode changes channel semantics but still exposes `in0..in7` without labels. The dummy read ignores errors.

Test signals: instantiate both chip variants, verify 12-bit and 8-bit scaling against known ADC codes, test internal and external reference modes including invalid regulator voltages, confirm channel command ordering, and inspect sysfs output for all eight channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ads7828.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ads7871.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ads7871.c

Purpose: SPI hwmon driver for the TI ADS7871 ADC. It exposes eight read-only single-ended voltage inputs using the device internal reference, oscillator, buffer, and PGA gain of one.

Important APIs/types/functions: `struct ads7871_data` stores the SPI device. `ads7871_read_reg8()`, `ads7871_read_reg16()`, and `ads7871_write_reg8()` build ADS7871 instruction bytes and perform SPI transfers. `voltage_show()` selects a channel through `REG_GAIN_MUX`, polls conversion completion, reads the 16-bit ADC output, and converts it to a `volts * 10000` style integer. Probe configures SPI mode, resets serial/control registers, enables oscillator/reference/buffer bits, verifies the oscillator register readback, and registers eight input attributes.

Control flow: each sysfs read writes the gain/mux register with conversion-start and single-ended bits, checks whether the conversion bit clears after up to two 1 ms sleeps, reads the data registers when ready, shifts away unused bits, scales against a 2.5 V reference, and returns `-ETIMEDOUT` if conversion does not complete.

State and persistence: no software cache is maintained. Probe leaves oscillator/reference/buffer enabled and all conversions are triggered by reads. SPI settings are assigned in probe but the return value from `spi_setup()` is not checked.

Dependencies and integration: depends on SPI helpers `spi_w8r8`, `spi_w8r16`, `spi_write`, hwmon sysfs groups, and delay functions. It registers as a simple `spi_driver` named `ads7871`; board info supplies bus/chip-select data.

Risks: probe ignores errors from several initialization writes and from `spi_setup()`. The readback identity check only verifies one writable register. The driver does not support differential inputs or PGA gains despite hardware support. `msleep_interruptible()` return is ignored inside conversion polling. Output units are unusual for `in*_input`, where hwmon normally expects millivolts.

Test signals: verify SPI mode and max clock with real board info, check oscillator register probe failure paths, compare all channel readings against a known source, force conversion timeout, and run SPI fault injection for initialization and read transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ads7871.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7310.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adt7310.c

Purpose: SPI transport wrapper for ADT7310/ADT7320 digital temperature sensors. It maps the SPI command protocol into a regmap used by the shared ADT7x10 hwmon core.

Important APIs/types/functions: `adt7310_reg_table[]` maps common `ADT7X10_*` logical registers to ADT7310 SPI register numbers. `AD7310_COMMAND()` builds command bytes. SPI helpers read/write 8-bit and 16-bit registers, using big-endian word reads and unaligned big-endian writes. `adt7310_reg_read()` and `adt7310_reg_write()` are custom regmap bus callbacks that select byte or word transactions based on the logical register. `adt7310_regmap_is_volatile()` marks temperature and status volatile. `adt7310_spi_probe()` initializes regmap and delegates to `adt7x10_probe()`.

Control flow: SPI probe creates a 16-bit-value regmap with custom callbacks and maple cache, then calls the shared core with the SPI device name, IRQ, and regmap. All hwmon operations, limit programming, interrupt handling, and suspend/resume behavior come from `adt7x10.c`; this file only handles bus-specific encoding.

State and persistence: bus-wrapper state is only the managed regmap. Cached nonvolatile registers are held by regmap. Device configuration state is modified by the common core and restored/powered down through common managed actions and PM ops.

Dependencies and integration: depends on SPI, regmap, unaligned big-endian helpers, and `adt7x10.h`. It exports SPI IDs `adt7310` and `adt7320` and attaches common PM ops through `adt7x10_dev_pm_ops`.

Risks: no OF match table appears in this wrapper, so device-tree binding depends on SPI ID style matching elsewhere. Correctness depends on the logical register mapping staying aligned with `adt7x10.h`. Multi-byte endianness is bus-specific and would break temperature/limit values if changed casually.

Test signals: instantiate both SPI IDs, verify regmap byte and word transactions with a bus analyzer or mocked SPI, compare temperature/limit readbacks through shared hwmon attributes, exercise interrupt delivery through the common core, and run suspend/resume tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7310.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7410.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adt7410.c

Purpose: I2C transport wrapper for ADT7410/ADT7420/ADT7422 digital temperature sensors. It adapts SMBus transactions into the shared ADT7x10 regmap and hwmon implementation.

Important APIs/types/functions: `adt7410_regmap_is_volatile()` marks temperature and status volatile. `adt7410_reg_read()` reads word-swapped values for temperature and temperature limit registers, and byte values for status/config/hysteresis/ID. `adt7410_reg_write()` mirrors this for writes. `adt7410_regmap_config` uses 8-bit register addresses, 16-bit values, maple cache, and `ADT7X10_ID` as the maximum register. `adt7410_i2c_probe()` creates the regmap and calls `adt7x10_probe()`.

Control flow: after I2C match, probe initializes the custom regmap and hands control to the common ADT7x10 core with the I2C client name and IRQ. Runtime sysfs reads/writes, interrupt notifications, config setup, and PM suspend/resume are handled by `adt7x10.c` through this regmap.

State and persistence: this wrapper has no private state beyond the managed regmap. Register cache persists nonvolatile config and limit values during normal operation. Common code rewrites device config to 16-bit continuous comparator mode and restores old config via a devm action.

Dependencies and integration: depends on I2C SMBus byte and word-swapped operations, regmap, `adt7x10.h`, OF compatible strings `adi,adt7410`, `adi,adt7420`, and `adi,adt7422`, and shared PM ops.

Risks: all value semantics depend on the shared logical register constants matching the physical I2C register map, which happens here because ADT7410-style I2C registers line up with the common enum. Bus adapters must support the SMBus operations used. Any regmap cache policy bug could expose stale thresholds or config while temperature/status remain volatile.

Test signals: probe all three IDs through I2C and OF, verify word-swapped temperature and limit values, exercise shared hwmon threshold writes and alarms, confirm IRQ notifications if wired, and run suspend/resume to ensure config power-down and restore work through the I2C regmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7411.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adt7411.c

Purpose: I2C hwmon driver for the ADT7411 temperature sensor plus 8-channel 10-bit ADC. It exposes internal/external temperatures, VDD, auxiliary voltage inputs, threshold registers, alarms, and a few device-specific sampling/reference controls.

Important APIs/types/functions: `struct adt7411_data` stores the I2C client, external temperature mode, cached reference voltage, and cache expiration. `adt7411_read_10_bit()` reads shared LSB/MSB register pairs in the order required by hardware locking. `adt7411_update_vref()` caches either measured VDD or the 2.25 V internal reference. `adt7411_read()`/`adt7411_write()` dispatch standard hwmon voltage and temperature callbacks. `adt7411_is_visible()` hides AIN1 when used as external temperature and hides external temperature when not enabled. Extra attributes `no_average`, `fast_sampling`, and `adc_ref_vdd` toggle config bits.

Control flow: detection verifies manufacturer and device IDs. Probe allocates state, fixes reserved config bits, reads whether external temperature mode is active, starts monitoring, forces the first Vref update, and registers hwmon channels plus extra attributes. Voltage reads route channel 0 through VDD scaling and channels 1-8 through the selected reference. Temperature reads handle 10-bit signed measured values and 8-bit signed thresholds. Writes clamp values to register ranges and program min/max registers.

State and persistence: `vref_cached` is refreshed once per second according to `next_update`; bit-control writes force a refresh by setting `next_update = jiffies`. Device configuration persists in registers and is not restored on removal. No suspend path is implemented despite a file TODO mentioning power-down mode.

Dependencies and integration: depends on SMBus byte-data transfers, jiffies, hwmon channel-info callbacks, and legacy I2C address scanning at `0x48`, `0x4a`, and `0x4b`.

Risks: reference caching means voltage scaling can be briefly stale after VDD/reference changes. Several control attributes are nonstandard. Reserved-bit handling is critical and only done during initialization. External temperature mode changes visibility and alarm meaning for AIN1. The driver uses legacy `sprintf()` in the bit attributes.

Test signals: verify ID detection, external temperature mode visibility, all AIN/VDD scaling paths, threshold write/readback, Vref cache refresh after `adc_ref_vdd`, reserved-bit initialization, and alarm/fault bit mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7411.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7462.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adt7462.c

Purpose: legacy hwmon I2C driver for the ADT7462 multi-channel monitor/fan controller. It exposes up to four temperatures, thirteen voltage inputs, eight fans, four PWMs, alarms, labels, and automatic PWM temperature-control points.

Important APIs/types/functions: `struct adt7462_data` is the central cache for sensor values, limits, PWM config, pin config, voltage scaling, fan enable bits, alarms, and timestamps. Register selector helpers `ADT7462_REG_VOLT*()` return valid registers only when pin configuration exposes that channel as voltage. `voltage_label()`, `voltage_multiplier()`, `temp_enabled()`, and `temp_label()` derive user-visible channels from pin config. `adt7462_update_device()` refreshes live sensors every 2 seconds and limits/settings every 60 seconds. Many show/store callbacks implement voltage, temperature, fan, PWM, force-full-speed, auto channel, hysteresis, and point temperature attributes.

Control flow: probe allocates state, initializes the mutex, logs the detected chip, and registers one large sysfs group. The first read populates pin config, sensors, limits, and PWM settings. Show callbacks call `adt7462_update_device()`, then return zero for channels not enabled by pin/fan configuration. Store callbacks parse and clamp input, update the cached register field, and write a byte to the selected register. PWM auto-channel writes convert hwmon bitmasks into the device channel selector encoding.

State and persistence: two cache validity flags separate fast-changing sensors from slow-changing limits. Hardware pin configuration controls which voltage/temperature channels are meaningful. Writes update both cache and hardware but do not always force a full refresh. Device register changes persist after module removal.

Dependencies and integration: depends on I2C SMBus byte operations, hwmon-sysfs legacy attributes, mutexes, jiffies, and `log2` helpers. It scans `0x58` and `0x5c` and verifies vendor/device/revision IDs before binding.

Risks: `adt7462_update_device()` performs many SMBus reads without checking negative return values, so errors can be stored as unsigned cached data. Attribute visibility is not dynamic; disabled channels return `0` or `N/A` instead of being hidden. PWM range writes require exact table values for `pwm*_auto_point2_temp`. Legacy `sprintf()` is used throughout.

Test signals: use real or emulated SMBus registers to cover pin-config combinations, validate labels and scaling for all voltage channels, verify fan enable behavior, write PWM auto settings including invalid masks, force I2C read failures during cache refresh, and run `sensors` to inspect the large sysfs surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7462.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7470.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adt7470.c

Purpose: hwmon I2C driver for the ADT7470 thermal monitor and fan controller. It exposes ten temperature channels, four fan tachometers with min/max limits, four PWM controls, alarm masks, automatic temperature-to-PWM controls, and a background temperature acquisition thread.

Important APIs/types/functions: `struct adt7470_data` stores regmap, mutex, sensor/limit caches, probed temperature count, alarms, PWM state, and the `auto_update` kthread. `adt7470_read_temperatures()` temporarily forces PWM manual mode, starts temperature collection, waits long enough for the configured number of sensors, restores PWM config, and optionally probes how many sensors are present. `adt7470_update_sensors()` and `adt7470_update_limits()` populate separate caches. `adt7470_read()`/`adt7470_write()` implement modern hwmon callbacks, while extra sysfs attributes expose alarm mask, temperature sensor count, auto-update interval, force PWM max, and auto points.

Control flow: probe creates regmap, starts the chip by setting config bits, registers hwmon channels and extra groups, and launches a kthread. The thread periodically calls `adt7470_read_temperatures()` under the lock to keep temperature data fresh. User reads refresh cached sensors every 5 seconds and limits every 60 seconds. Writes clamp values, update cache, and write regmap registers. Removal stops the kthread.

State and persistence: sensor and limit caches are timestamped independently. `num_temp_sensors = -1` triggers automatic probing; users can override it through sysfs. PWM mode and frequency changes persist in hardware. The background thread is process state that must stop cleanly on remove.

Dependencies and integration: depends on I2C, regmap, kthreads, hwmon channel callbacks, and legacy extra groups. It scans `0x2c`, `0x2e`, and `0x2f` after vendor/device/revision verification.

Risks: temperature acquisition deliberately changes PWM mode temporarily, so failures during the sequence could leave PWM config altered despite restore checks. `auto_update_interval` accepts zero, which can create a busy update thread. The `hwmon_fan_div` capability is advertised but `adt7470_fan_read()` does not implement it. Several extra attributes use legacy `sprintf()`.

Test signals: verify kthread startup/removal, temperature probing with 0-10 sensors, PWM config restoration after interrupted reads, cache refresh timing, alarm mask write/readback, `auto_update_interval=0` behavior, fan min/max conversions, and hwmon attribute visibility including the advertised fan divisor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7470.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7475.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adt7475.c

Purpose: hwmon I2C driver for the ADT7473, ADT7475, ADT7476, and ADT7490 thermal monitor/fan-controller family. It exposes voltage inputs, temperature sensors, tachometers, PWM controls, automatic fan-control points, alarms, optional VID, and board-configurable pin functions.

Important APIs/types/functions: `struct adt7475_data` stores the I2C client, lock, feature flags, config registers, alarm bitmap, voltage/temp/tach/PWM caches, PWM channel/control state, VRM, and dynamic attribute groups. Conversion helpers handle two temperature encodings, tach/RPM, voltage attenuation, PWM frequencies, smoothing, and auto ranges. `load_config*()`, `load_attenuators()`, `adt7475_set_pwm_polarity()`, and `adt7475_fan_pwm_config()` consume firmware properties and child `pwms` data. `adt7475_update_limits()` reads stable settings; `adt7475_update_measure()` reads alarms and live measurements with extension bits.

Control flow: detection checks Analog Devices IDs and distinguishes family members by device IDs and address/revision. Probe initializes feature masks per chip variant, applies pin-function and attenuator properties, derives optional features (`pwm2`, `fan4`, extra inputs, VID), normalizes disabled PWM channels to manual 0 percent, applies PWM polarity and child PWM configuration, starts monitoring for relevant chips, assembles only the applicable attribute groups, registers hwmon, and reads limits once. Runtime reads refresh measurements every two seconds. Store callbacks update cached fields and write corresponding registers.

State and persistence: limits are read once at probe and kept in cache unless a sysfs write changes them. Live measurements are cached for two seconds. Firmware-derived pin and attenuator configuration is written into device registers and persists in hardware. Optional attribute groups reflect probe-time feature detection only.

Dependencies and integration: depends on I2C SMBus, hwmon-sysfs, `hwmon-vid`, OF/fwnode helpers, PWM binding flags, and the matching devicetree binding for `adi,adt7473/7475/7476/7490`.

Risks: many write helpers ignore SMBus write failures. Firmware property parsing has complex variant-specific behavior; a wrong pin-function or attenuator property changes both hardware configuration and sysfs visibility. The code returns success without changing manual PWM when users write `pwm*` while not in manual mode, which can confuse callers. The file has a nonstandard `pwm_use_point2_pwm_at_crit` attribute and a misspelled `HYSTERSIS` enum/API surface. Legacy `sprintf()` is used.

Test signals: test all four chip IDs or emulated variants, OF pin-function and attenuator combinations, child `pwms` parsing with three and four cells, PWM polarity, optional group creation, voltage scaling with bypassed attenuators, temperature encoding modes, tach min writes, alarm bits including ADT7490 status4, and I2C write-failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7475.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7x10.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adt7x10.c

Purpose: common hwmon core for ADT7410/ADT7420/ADT7422 I2C and ADT7310/ADT7320 SPI digital temperature sensors. It provides shared temperature conversion, limit/hysteresis/alarm sysfs behavior, interrupt notification, probe-time configuration, and suspend/resume.

Important APIs/types/functions: `struct adt7x10_data` stores the regmap, active and original config bytes, and whether the first temperature reading is valid. Conversion helpers `ADT7X10_TEMP_TO_REG()` and `ADT7X10_REG_TO_TEMP()` handle milli-Celsius and 13/16-bit register formats. `adt7x10_temp_ready()` polls status until the first conversion is ready. `adt7x10_read()`/`adt7x10_write()` implement hwmon temperature callbacks. `adt7x10_irq_handler()` emits `hwmon_notify_event()` for high, low, and critical alarms. `adt7x10_probe()` is exported to bus wrappers, and `adt7x10_dev_pm_ops` provides suspend/resume.

Control flow: bus-specific drivers create a regmap and call `adt7x10_probe()`. The common probe reads original config, sets continuous conversion, 16-bit resolution, comparator/event mode, normal polarity, and registers a managed restore action if it changed config. It then registers a single temp channel with input, min/max/crit, hysteresis, and alarm attributes. If an IRQ is supplied, it requests a threaded falling-edge handler. Reads wait for conversion readiness once, then read registers. Writes clamp and program limit registers or hysteresis.

State and persistence: `oldconfig` is restored automatically on driver detach if probe changed it. `config` is used for conversion semantics and PM resume. `valid` gates the initial wait for non-stale temperature. Regmap caches nonvolatile registers while temperature/status are volatile in bus wrappers. Suspend writes power-down bits; resume writes the active config.

Dependencies and integration: depends on regmap, hwmon channel-info callbacks, interrupts, devm actions, jiffies/delays, and exported symbols consumed by `adt7310.c` and `adt7410.c`.

Risks: hysteresis is stored as one shared 4-bit delta but presented as multiple absolute hysteresis values; writing max hysteresis affects all hysteresis displays. IRQ handling reports events based on status reads but does not clear or debounce alarms itself. Correct temperature conversion depends on wrappers marking status and temperature volatile and using correct endian bus operations.

Test signals: run shared hwmon reads/writes through both I2C and SPI wrappers, verify first-read timeout behavior, check 13-bit versus 16-bit conversion if resolution config changes, exercise IRQ notifications for low/high/critical, and run suspend/resume with regmap fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7x10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7x10.h -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adt7x10.h

Purpose: shared header that defines the logical register namespace and exported entry points used by the ADT7x10 common core and its I2C/SPI bus wrappers.

Important APIs/types/functions: the register enum defines `ADT7X10_TEMPERATURE`, `ADT7X10_STATUS`, `ADT7X10_CONFIG`, `ADT7X10_T_ALARM_HIGH`, `ADT7X10_T_ALARM_LOW`, `ADT7X10_T_CRIT`, `ADT7X10_T_HYST`, and `ADT7X10_ID`. `adt7x10_probe(struct device *dev, const char *name, int irq, struct regmap *regmap)` is the common probe entry used by `adt7310.c` and `adt7410.c`. `adt7x10_dev_pm_ops` exposes shared suspend/resume operations for bus drivers.

Control flow: bus wrappers include this header, translate their physical registers into the logical enum where needed, create a regmap that understands these logical addresses, and call `adt7x10_probe()`. The common core then uses only this logical register namespace and the provided regmap.

State and persistence: the header stores no state, but it defines the ABI between wrapper and core. Any change to enum order or meaning changes which physical registers the wrappers read/write and therefore affects cached config, limits, status, and temperature values.

Dependencies and integration: depends on `linux/pm.h` for PM declarations and forward declarations of `struct device` and `struct regmap` from including C files. It is internal to the hwmon driver cluster rather than a user-visible UAPI header.

Risks: because the enum is positional, wrappers that use lookup tables, such as the SPI wrapper, depend on every value remaining stable. Adding registers requires updates in both common code and bus regmap callbacks. A mismatch can silently redirect writes to thresholds or config registers.

Test signals: build-test both `adt7310` and `adt7410` after enum/API changes, verify shared probe symbol linkage under modular builds, and run common hwmon attribute tests over both transports to catch logical-register mapping regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adt7x10.h -->
