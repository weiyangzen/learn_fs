# Research: subset-b-003819

This grouped report covers the hwmon source files assigned to `subset-b-003819`. Each section is bounded by reconciliation markers for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/abituguru.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/abituguru.c

## Purpose
`abituguru.c` is a legacy hwmon platform driver for first-generation Abit uGuru motherboard monitoring hardware at the fixed I/O base `0x00e0`. It exposes voltage, temperature, fan tachometer, alarm, beep/shutdown, and automatic PWM fan-control settings through hwmon-style sysfs attributes.

## Important APIs, Types, And Functions
The central state is `struct abituguru_data`, which stores the platform hwmon device, `update_lock`, I/O address, ready/timeout state, dynamically generated sysfs attributes and names, cached sensor values, cached limit/settings bytes, alarm bytes, and PWM settings. Low-level transactions use `inb_p`, `inb`, and `outb` in `abituguru_wait`, `abituguru_ready`, `abituguru_send_address`, `abituguru_read`, and `abituguru_write`. Probe-time discovery is handled by `abituguru_detect_bank1_sensor_type`, `abituguru_detect_no_bank2_sensors`, and `abituguru_detect_no_pwms`. User ABI handlers include `show_bank1_value`, `store_bank1_setting`, `show_bank1_alarm`, `store_bank1_mask`, `show_bank2_value`, `store_bank2_setting`, `show_pwm_setting`, `store_pwm_setting`, `show_pwm_sensor`, and `store_pwm_enable`. Module entry uses `abituguru_init`, `abituguru_detect`, a synthetic `platform_device`, and `hwmon_device_register`.

## Control Flow
Initialization refuses non-Abit boards unless `force` is set, probes the fixed command/data ports, registers `abituguru_driver`, and allocates a matching platform device with an I/O resource. `abituguru_probe` reads every bank and setting block into memory before creating sysfs attributes. Bank 1 sensor type detection intentionally writes temporary threshold/alarm settings, waits for the controller to raise alarms, then restores the original settings. Fan and PWM counts are inferred from cached setting ranges or overridden by module parameters. Runtime reads call `abituguru_update_device`, which refreshes alarms, bank 1 values/settings, and fan values no more often than once per second. Sysfs stores update the in-memory byte first, write the corresponding uGuru setting block, and roll back the cache on failed writes.

## State And Persistence
The driver keeps a volatile cache in `struct abituguru_data`; the persistent state is the uGuru firmware's own thresholds, alarm masks, and PWM tables. Writes through sysfs change hardware/firmware settings immediately. Probe-time sensor detection temporarily mutates persistent sensor settings and has explicit restore/retry logic because bad settings can affect BIOS behavior. Suspend locks `update_lock` to quiesce transactions; resume revalidates the ready state and unlocks.

## Dependencies And Integration Points
This driver depends on x86-style port I/O, DMI board vendor strings, the platform bus, hwmon sysfs helpers, jiffies, mutexes, and module parameters (`force`, `bank1_types`, `fan_sensors`, `pwms`, `verbose`). It integrates with userspace through manually created sysfs files rather than modern `hwmon_device_register_with_info`.

## Risks And Test Signals
High-risk areas are forced probing of fixed I/O ports, destructive sensor-type detection, incomplete hardware write failures, stale cache behavior after consecutive timeouts, sysfs name buffer accounting, and correctness of conversions between raw bytes and millivolts/millicelsius/RPM. Useful test signals are successful load only on intended DMI systems, stable `name`, `in*`, `temp*`, `fan*`, and `pwm*` sysfs files, restore of original settings after type detection, correct rollback on injected write failures, suspend/resume without overlapping I/O transactions, and no writes to non-existent fan/PWM channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/abituguru.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/abituguru3.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/abituguru3.c

## Purpose
`abituguru3.c` supports later Abit uGuru3 motherboard monitor chips. It exposes voltage, temperature, fan, alarm, mask, and label attributes for known motherboard IDs, but unlike `abituguru.c` it is read-only from sysfs and relies on a static motherboard sensor table.

## Important APIs, Types, And Functions
`struct abituguru3_sensor_info` describes each logical sensor name, controller port, sensor type, scaling multiplier/divisor, and offset. `struct abituguru3_motherboard_info` maps uGuru3 board IDs and optional DMI names to sensor tables. `struct abituguru3_data` stores hwmon state, I/O address, validity flags, generated sysfs attributes/names, the selected sensor table, 48 alarm bits, 48 values, and 48 setting triplets. The controller protocol is implemented by `abituguru3_wait_while_busy`, `abituguru3_wait_for_read`, `abituguru3_synchronize`, `abituguru3_read`, and `abituguru3_read_increment_offset`. Sysfs callbacks are `show_value`, `show_alarm`, `show_mask`, `show_label`, and `show_name`.

## Control Flow
`abituguru3_init` first checks DMI via `abituguru3_dmi_detect`; if the board is not exactly matched or `force` is set, it falls back to fixed-port manual detection. It then registers a platform driver and synthetic platform device at `ABIT_UGURU3_BASE`. `abituguru3_probe` reads the motherboard ID from the miscellaneous bank, performs a full `abituguru3_update_device`, chooses the matching static motherboard table, dynamically formats sysfs attributes in sensor order, creates them, and registers hwmon. Updates synchronize the protocol state machine for every command, read the alarm bytes, read values and settings for the 32 voltage/temp ports, then read values and 2-byte settings for 16 fan ports. Data is cached for one second.

## State And Persistence
Runtime state is a cache of all 48 ports plus the selected static metadata table. The driver does not provide sysfs stores, so it should not persist user changes to the chip. It still reads persistent alarm/limit masks from the controller. Suspend locks `update_lock` to stop command traffic; resume releases it.

## Dependencies And Integration Points
The driver depends on fixed I/O port access, DMI, platform devices, hwmon sysfs helpers, jiffies, and a large in-driver board table. It uses module parameters `force` and `verbose`. Integration with userspace is via manually generated legacy sysfs attributes such as `in*_input`, `temp*_input`, `fan*_input`, `*_alarm`, `*_label`, and `name`.

## Risks And Test Signals
The main risks are incorrect or incomplete motherboard tables, manual fixed-port probing on unsupported boards, fragile command synchronization, and read-only attributes that may not reflect writable hardware capabilities. Scaling correctness depends on per-board multipliers and offsets. Test signals include DMI table matching, board ID lookup failure reporting, complete sysfs attribute creation for each table entry, no buffer overrun in `sysfs_names`, correct one-second cache refresh, and successful handling of busy/read timeouts without leaving `valid` true after partial refreshes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/abituguru3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/acpi_power_meter.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/acpi_power_meter.c

## Purpose
`acpi_power_meter.c` implements the ACPI 4.0 power meter resource as an hwmon power device. It reads platform power through ACPI control methods, exposes average power, averaging interval, cap, alarm, trip, accuracy, battery flag, identity strings, and domain-device links, and reacts to ACPI notifications.

## Important APIs, Types, And Functions
`struct acpi_power_meter_capabilities` mirrors integer fields from `_PMC`; `struct acpi_power_meter_resource` owns the ACPI device, mutex, hwmon device, capabilities, strings, cached power/cap/interval, trip state, domain device references, and symlink kobject. ACPI method wrappers include `update_avg_interval` (`_GAI`), `update_cap` (`_GHL`), `set_acpi_trip` (`_PTP`), `update_meter` (`_PMM`), `set_cap` (`_SHL`), `set_avg_interval` (`_PAI`), `read_capabilities` (`_PMC`), and `read_domain_devices` (`_PMD`). Modern hwmon integration is via `power_meter_is_visible`, `power_meter_read`, `power_meter_write`, `power_meter_chip_info`, and `hwmon_device_register_with_info`. Extra legacy attributes are grouped under `power_extra_group`.

## Control Flow
Probe obtains the ACPI companion, allocates resource state, optionally waits for ACPI IPMI support on Dell systems, reads capabilities and optional domain devices, registers the hwmon device, and installs an ACPI notify handler. Reads take `resource->lock`, then evaluate the relevant ACPI method or use cached capability data. `update_meter` observes the ACPI sampling time and only refreshes when the cache expires. Notifications rebuild the hwmon device on configuration changes, update cap state on cap changes, set alarm state on capping events, emit sysfs notifications, and generate ACPI netlink events. Remove unregisters notifications, hwmon, symlinks, ACPI device references, strings, and the resource allocation.

## State And Persistence
Capabilities and identity strings are stored in memory after `_PMC`; model, serial, and OEM strings are dynamically allocated. Average power is cached according to firmware sampling time. Cap, interval, and trip setters persist through firmware ACPI methods, not local files. Domain device links hold ACPI device references until removed. Resume refreshes capabilities but does not fully rebuild all domain links.

## Dependencies And Integration Points
The file depends on ACPI evaluation, ACPI platform devices, optional ACPI IPMI readiness, DMI gating for hardware power caps, hwmon channel APIs, sysfs attribute groups, kobjects, and ACPI netlink events. The `force_cap_on` module parameter can expose cap controls even when hardware safety is unknown.

## Risks And Test Signals
Risks include firmware returning malformed packages, unsafe software power capping, unregister/register races during notification rebuilds, stale domain links after configuration changes, units mismatches, and partial resume refresh. Test signals include valid `_PMC` parsing of 14 fields, correct visibility based on capability flags and DMI cap policy, cap/interval range enforcement, sampling-time cache behavior, sysfs notifications for events `0x80` through `0x84`, proper cleanup of `_PMD` symlinks and references, and no use-after-free across notification-driven hwmon re-registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/acpi_power_meter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ad7314.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ad7314.c

## Purpose
`ad7314.c` is a compact SPI hwmon driver for Analog Devices AD7314, ADT7301, and ADT7302 digital temperature sensors. It exposes a single `temp1_input` attribute.

## Important APIs, Types, And Functions
`enum ad7314_variant` distinguishes register formats. `struct ad7314_data` stores the SPI device and a cacheline-aligned 16-bit receive buffer. `ad7314_spi_read` performs a two-byte `spi_read` and converts the big-endian word with `be16_to_cpu`. `ad7314_temperature_show` validates variant-specific leading-zero bits, masks and sign-extends the raw temperature field, and emits millidegrees Celsius. `ad7314_probe` allocates state and registers the hwmon group with `devm_hwmon_device_register_with_groups`. Device binding is through `spi_device_id` entries and `module_spi_driver`.

## Control Flow
On probe the driver does not configure the chip; it only stores the SPI device and creates the hwmon device. Each sysfs read synchronously performs one SPI transfer. For AD7314, bits `14:5` are treated as a signed 10-bit temperature with 0.25 degree C LSB. For ADT7301/ADT7302, bits `13:0` are treated as a signed 14-bit value with 31.25 millidegree C LSB. Invalid leading zero fields return `-EIO`.

## State And Persistence
There is no persistent configuration and no periodic cache. The only state is the device pointer and the latest raw receive buffer. Reads do not alter sensor configuration.

## Dependencies And Integration Points
The file depends on SPI core APIs, hwmon sysfs helpers, endian helpers, sign extension, and static SPI IDs. It integrates with userspace through `temp1_input` named under the SPI modalias.

## Risks And Test Signals
Risk is concentrated in variant-specific bit interpretation, byte order, and invalid-read detection. There is no locking, so correctness assumes one-at-a-time sysfs show execution or harmless overwrites of the receive buffer. Test signals include correct negative temperature sign extension, expected millidegree scaling for all three IDs, SPI error propagation, `-EIO` on nonzero leading bits, and successful devm cleanup on device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ad7314.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ad7414.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ad7414.c

## Purpose
`ad7414.c` is an I2C hwmon driver for the Analog Devices AD7414 temperature sensor. It exposes current temperature, high/low temperature limits, and min/max alarm bits.

## Important APIs, Types, And Functions
`struct ad7414_data` holds the I2C client, mutex, cache validity, next update jiffies, raw temperature word, and high/low limit bytes. Conversion helpers are `ad7414_temp_from_reg`, `ad7414_read`, and `ad7414_write`. The cache refresher is `ad7414_update_device`. Sysfs callbacks include `temp_input_show`, `max_min_show`, `max_min_store`, and `alarm_show`. `ad7414_probe` verifies SMBus functionality, powers the chip up by clearing configuration bit 7, and registers the hwmon group.

## Control Flow
Probe allocates state, initializes the mutex, reads the configuration register, clears shutdown if possible, and registers attributes. Runtime show paths call `ad7414_update_device`, which refreshes `TEMP`, `T_HIGH`, and `T_LOW` when the 1.5-second cache has expired or is invalid. Limit stores parse millidegrees, clamp to `-40000..85000`, round to whole degrees, update the cache under lock, and write the selected limit register.

## State And Persistence
The driver caches sensor and limit registers in memory. Limit writes persist in the device registers. The cache is marked valid even if individual refresh reads fail, leaving previous values in place for failed fields. No suspend/resume hooks are present.

## Dependencies And Integration Points
The driver depends on I2C SMBus byte and word reads, hwmon sysfs groups, OF compatible `ad,ad7414`, and the I2C device ID table. It integrates through `temp1_input`, `temp1_max`, `temp1_min`, `temp1_max_alarm`, and `temp1_min_alarm`.

## Risks And Test Signals
Risks include setting `valid` after partial read failures, ignoring the return value from `ad7414_write` in limit stores, whole-degree rounding of user limits, and alarm-bit interpretation from the raw temperature word. Test signals include successful functionality rejection on adapters lacking byte/word SMBus support, config shutdown bit cleared at probe, correct signed temperature conversion, limit clamping/rounding, and alarm bits tracking datasheet-defined status bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ad7414.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ad7418.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ad7418.c

## Purpose
`ad7418.c` supports Analog Devices AD7416, AD7417, and AD7418 temperature monitor/ADC chips. Depending on variant, it exposes temperature limit attributes and zero, one, or four voltage ADC inputs.

## Important APIs, Types, And Functions
`enum chips` selects `ad7416`, `ad7417`, or `ad7418`. `struct ad7418_data` stores the I2C client, chip type, mutex, number of ADC channels, cache state, three temperature registers, and up to four ADC values. `ad7418_update_device` is the main refresh path. Sysfs callbacks are `temp_show`, `adc_show`, and `temp_store`; conversion uses `LM75_TEMP_FROM_REG` and `LM75_TEMP_TO_REG` from `lm75.h`. `ad7418_init_client` clears shutdown/mode bits and resets `CONF2` for ADC-capable variants. Probe selects the attribute group from match data.

## Control Flow
Probe verifies SMBus byte and word support, reads match data, sets `adc_max`, initializes the chip, and registers the variant-specific hwmon group. Updates run every 1.5 seconds. The update path reads and masks the current configuration, switches the mux to temperature, waits, reads temperature/current/hysteresis/OS registers, then iterates ADC channels by writing channel-select bits to the config register, delaying, and reading the ADC register. It attempts to restore the old configuration afterward.

## State And Persistence
The cache stores raw temperature and ADC registers. Temperature limit stores write device registers and update cache. The driver mutates the chip's channel-selection bits during reads; normal operation depends on restoring the previous config. There is no separate persistent storage and no suspend/resume implementation.

## Dependencies And Integration Points
Dependencies are I2C SMBus byte/word operations, `lm75.h` conversion macros, OF match data (`adi,ad7416`, `adi,ad7417`, `adi,ad7418`), and hwmon sysfs groups. Userspace sees `temp1_*` and variant-dependent `in*_input` files.

## Risks And Test Signals
Risks include failure to restore configuration after an abort, using `i2c_smbus_write_word_swapped` to restore a byte configuration register, unchecked write return values in `temp_store`, channel mux side effects, and stale cache after errors. Test signals include per-variant attribute visibility, correct ADC millivolt scaling, temperature limit read/write round trips, abort path marking `valid=false`, and preservation of the original config across update cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ad7418.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adc128d818.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adc128d818.c

## Purpose
`adc128d818.c` is an I2C hwmon driver for the TI ADC128D818 system monitor. It reports up to eight voltage inputs, optional local temperature, min/max limits, and latched alarms, with operation-mode-dependent attribute visibility.

## Important APIs, Types, And Functions
`struct adc128_data` stores the I2C client, reference voltage in mV, mutex, operation mode, cache state, normalized 12-bit voltage values/limits, normalized 9-bit temperature values/limits, and alarm latch. `adc128_update_device` refreshes input, temperature, and alarm registers. Sysfs callbacks are `adc128_in_show`, `adc128_in_store`, `adc128_temp_show`, `adc128_temp_store`, and `adc128_alarm_show`. Visibility is controlled by `adc128_is_visible`. Detection uses `adc128_detect`; hardware setup uses `adc128_init_client`; probe handles regulator and Device Tree mode selection.

## Control Flow
The I2C detect path checks manufacturer/device IDs and unused bits. Probe obtains optional `vref`; without it the driver uses the internal 2.56 V reference, otherwise it enables external reference mode and scales by the regulator voltage. It reads or validates `ti,mode`, resets the chip, writes advanced config if needed, starts monitoring, and registers attributes. Runtime updates refresh visible voltage channels once per second, skip temperature in mode 1, OR new alarm bits into the software latch, and invalidate the cache on read failure. Alarm reads clear the reported bit in the software copy after returning it.

## State And Persistence
The driver maintains a one-second cache and a software-latched alarm byte. Limit stores write device registers and immediately update cached normalized values. Probe resets the chip to defaults, so pre-existing hardware configuration can be overwritten during driver binding. The selected mode and reference behavior persist in chip registers after initialization.

## Dependencies And Integration Points
Dependencies include I2C SMBus byte/word operations, regulator consumer APIs, OF property `ti,mode`, hwmon sysfs groups, and `I2C_CLASS_HWMON` address scanning. Userspace gets mode-dependent `in*_input`, `in*_min`, `in*_max`, `in*_alarm`, `temp1_input`, `temp1_max`, `temp1_max_hyst`, and `temp1_max_alarm`.

## Risks And Test Signals
Risks include destructive reset at probe, unchecked write return values in limit stores, alarm bit overlap where `temp1_max_alarm` shares bit 7 with `in7_alarm`, external reference scaling mistakes, and mode visibility mismatches. Test signals include correct rejection of invalid `ti,mode`, regulator fallback behavior, attribute visibility for modes 0 through 3, one-second cache refresh, software alarm clear-after-read behavior, and correct 12-bit/9-bit normalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adc128d818.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adcxx.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adcxx.c

## Purpose
`adcxx.c` is an SPI hwmon driver for National Semiconductor ADCxxS converter families. It exposes raw analog input channels scaled to millivolts using a writable reference value.

## Important APIs, Types, And Functions
`struct adcxx` stores the hwmon device pointer, mutex, channel count, and reference voltage. `adcxx_show` performs the SPI conversion read and scales the 12-bit raw value by `reference`. `adcxx_min_show`, `adcxx_max_show`, and `adcxx_max_store` expose reference range metadata. `adcxx_name_show` emits the SPI modalias. Probe manually creates `name`, `in_min`, `in_max`, and as many `inN_input` files as the matched channel count, then registers hwmon.

## Control Flow
Probe derives channel count from the SPI ID (`adcxx1s`, `adcxx2s`, `adcxx4s`, `adcxx8s`), initializes a default 3300 mV reference, creates the relevant sysfs files under lock, and calls `hwmon_device_register`. For single-channel devices, reads use `spi_read`; multi-channel devices send the channel index shifted into the command byte with `spi_write_then_read`. Remove unregisters hwmon and removes the same files.

## State And Persistence
The only mutable state is the in-memory reference voltage set through `in_max`; it is not written to hardware and is lost when the device unbinds. There is no sample cache. Each `in*_input` read triggers a fresh SPI transfer.

## Dependencies And Integration Points
The driver depends on SPI synchronous transfer APIs, legacy manual sysfs file management, hwmon registration, and SPI device IDs. Userspace controls scaling through `in_max`, reads fixed `in_min` as zero, and reads `in0_input` through `in7_input` depending on variant.

## Risks And Test Signals
Risks include absence of reference range validation, no explicit masking of unused ADC bits before scaling, manual sysfs cleanup correctness, and shared mutex use during remove versus reads. Test signals include correct number of channel files per ID, SPI error propagation, scaling with default and user-provided references, successful cleanup after partial file creation failure, and correct command byte generation for multi-channel devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adcxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adm1025.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adm1025.c

## Purpose
`adm1025.c` supports Analog Devices ADM1025/ADM1025A and Philips NE1619 sensor chips. It reports six scaled voltage channels, two temperature channels, alarms, CPU VID, and a writable VRM selector, with optional `in4` visibility depending on pin configuration.

## Important APIs, Types, And Functions
`struct adm1025_data` stores the I2C client, dynamic group list, mutex, two-second cache, raw voltage and temperature values/limits, combined alarms, VID, and VRM. Conversion macros `IN_FROM_REG`, `IN_TO_REG`, `TEMP_FROM_REG`, and `TEMP_TO_REG` implement register scaling. `adm1025_update_device` refreshes all readings and status registers. Sysfs handlers cover voltage, temperature, limits, `alarms`, per-channel `alarm`, `cpu0_vid`, and `vrm`. `adm1025_detect`, `adm1025_init_client`, and `adm1025_probe` implement detection, startup, and hwmon registration.

## Control Flow
The detect function checks SMBus byte support, unused status/config bits, chip ID high nibble, manufacturer ID, and address constraints for NE1619. Probe initializes the chip, sets the base attribute group, conditionally adds the `in4` group if pin 11 is not VID4, and registers hwmon. Initialization sets default high limits when registers contain zero to avoid spurious alarms, selects VRM with `vid_which_vrm`, and starts conversions. Runtime updates read all voltage values/limits, temperature values/limits, two status bytes, and VID bits into cache.

## State And Persistence
The driver keeps a two-second cache. Limit writes update hardware registers and cached bytes. Initialization may persistently alter high-limit registers that are zero and enable monitoring. `vrm` is only local driver state for VID conversion and is not written to the chip.

## Dependencies And Integration Points
Dependencies are I2C SMBus byte operations, `hwmon-vid`, hwmon sysfs groups, and `I2C_CLASS_HWMON` scanning at addresses `0x2c..0x2e`. It integrates with userspace through legacy sysfs attributes rather than modern hwmon ops.

## Risks And Test Signals
Risks include no error checks in `adm1025_update_device` for individual SMBus reads, unchecked writes in store paths, probe-time changes to default limits, and dynamic `in4`/VID4 interpretation. Test signals include reliable detection for ADM1025 versus NE1619, monitoring start, zero high-limit fixups, correct voltage scaling table, optional `in4` group visibility, VID conversion under changed `vrm`, and sane alarms from combined status bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adm1025.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adm1026.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adm1026.c

## Purpose
`adm1026.c` is a large legacy I2C hwmon driver for the Analog Devices ADM1026. It exposes 17 voltage inputs, up to 8 fan tachometers, up to 3 temperature channels, PWM/automatic fan controls, alarm and GPIO masks, GPIO state/configuration-derived VID, VRM selection, and an analog output DAC.

## Important APIs, Types, And Functions
`struct adm1026_data` stores the I2C client, dynamic attribute groups, mutex, fast and slow cache timestamps, voltage/fan/temp/PWM/DAC/GPIO/alarm/config caches, decoded fan divisors, GPIO config, and VRM. `adm1026_read_value` and `adm1026_write_value` abstract register access and intentionally ignore EEPROM-space writes. `adm1026_update_device` has a fast one-second sensor refresh and a slow five-minute configuration refresh. Store/show functions cover voltage limits including special `in16` negative scaling, fan min/divisors, temperature limits/offsets/thermal points, `temp_crit_enable`, DAC, `cpu0_vid`, `vrm`, `alarms`, `alarm_mask`, `gpio`, `gpio_mask`, `pwm*`, and automatic PWM points. Probe and setup use `adm1026_detect`, `adm1026_init_client`, `adm1026_fixup_gpio`, and `adm1026_probe`.

## Control Flow
Detection checks SMBus byte support and company/version registers, accepting exact ADM1026 and some generic steppings. Probe allocates state, initializes VRM, reads current config, decodes GPIO/fan configuration, optionally applies module-parameter GPIO overrides, sets safe automatic PWM minimum, enables monitoring, initializes fan divisors, chooses either the `in8/in9` group or `temp3` group based on `CFG1_AIN8_9`, and registers hwmon. Runtime fast updates read voltage/fan/temp/PWM/DAC/status/GPIO values. Slow updates read limits, fan divisors, thermal settings, masks, config registers, and GPIO configuration.

## State And Persistence
The driver caches hardware state aggressively. Most sysfs stores write device registers and update local cache. Module parameters (`gpio_input`, `gpio_output`, `gpio_inverted`, `gpio_normal`, `gpio_fan`) can permanently reprogram GPIO/fan-pin behavior at probe. Enabling PWM auto mode writes config bits and PWM register values, with fallback to full-speed PWM when disabling or switching modes. The driver intentionally does not initialize most limits/zones beyond enabling monitoring.

## Dependencies And Integration Points
Dependencies include I2C SMBus byte access, `hwmon-vid`, legacy hwmon sysfs groups, module parameter arrays, and address scanning at `0x2c..0x2e`. Userspace integration is broad and legacy: many attributes are manually enumerated, and group selection reflects mutually exclusive `temp3` versus `in8/in9` hardware mode.

## Risks And Test Signals
Risks include unchecked SMBus read/write failures, register bit packing mistakes for alarms/GPIO16, module-parameter GPIO reconfiguration, fan divisor changes altering min thresholds, multiple `pwm2/pwm3` attributes sharing single PWM hardware state, special negative `in16` scaling, and stale config cached for five minutes. Test signals include correct group selection from `CFG1_AIN8_9`, GPIO override behavior, alarm and GPIO mask round trips, fan divisor/min fixup correctness, safe full-speed PWM transitions, VID from GPIO11-15, and cache refresh separation between fast readings and slow config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adm1026.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adm1029.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/adm1029.c

## Purpose
`adm1029.c` is an I2C hwmon driver for the rare Analog Devices ADM1029. It reports three temperature channels, two fan tachometers, fan minimums, and writable fan divisors.

## Important APIs, Types, And Functions
`struct adm1029_data` stores the I2C client, mutex, two-second cache, temperature registers, fan count/min registers, and fan divisor config bytes. `adm1029_update_device` refreshes all cached registers. Sysfs callbacks are `temp_show`, `fan_show`, `fan_div_show`, and `fan_div_store`. Detection is in `adm1029_detect`, startup in `adm1029_init_client`, and registration in `adm1029_probe`.

## Control Flow
The detect function checks SMBus byte support, manufacturer ID `0x41`, documented bits in `TEMP_DEVICES_INSTALLED`, `NB_FAN_SUPPORT`, and revision high nibble. Probe allocates state, initializes the chip by setting config bit `0x10`, verifies it stuck, and registers the fixed attribute group. Runtime updates refresh temperature, fan/min, and fan divisor registers every two seconds. Fan speed is reported as zero for invalid count/divisor states; otherwise it is computed from the tach count and divisor. `fan_div_store` accepts only divisors 1, 2, and 4 and rewrites the top two config bits.

## State And Persistence
The driver stores only a two-second cache. The only writable exposed hardware state is the fan divisor register. Initialization persists the config enable bit. Fan minimums are read-only in this driver.

## Dependencies And Integration Points
Dependencies are I2C SMBus byte access, legacy hwmon sysfs groups, and `I2C_CLASS_HWMON` scanning over `0x28..0x2f`. Userspace sees `temp[1-3]_input/min/max`, `fan[1-2]_input/min`, and `fan[1-2]_div`.

## Risks And Test Signals
Risks include no error handling in the update cache for failed reads, limited fan divisor values, possible divide-by-zero if unexpected config encodings appear, and returning success from `adm1029_init_client` only after a soft verification. Test signals include detection rejection for unsupported revisions, config bit enable verification, correct fan speed formula for valid counts, zero output for invalid/no fan readings, and `fan_div_store` rejecting unsupported divisors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/adm1029.c -->
