# subset-b-003897 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tsl2772.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/tsl2772.c

## Purpose
`tsl2772.c` is an IIO I2C driver for a TAOS/AMS ambient-light and proximity family: TSL2571/2671/2771, TMD2671/2771, TSL2572/2672/2772, TMD2672/2772, and Avago APDS9930. It exposes lux, raw ALS channels, raw proximity, calibration controls, threshold events, and per-device channel layouts.

## Important APIs, Types, And Functions
The core state is `struct tsl2772_chip`, which holds the I2C client, two regulators, ALS/proximity mutexes, cached settings, runtime status, shadow register array, current ALS/proximity samples, lux table, and selected `tsl2772_chip_info`. `tsl2772_defaults()` merges platform data, default settings, default lux coefficients, and firmware properties (`led-max-microamp`, `amstaos,proximity-diodes`). `tsl2772_chip_on()` computes config registers, saturation, gain/time scale, powers the chip, writes all config registers, enables ADC/proximity and optional interrupts, then clears pending interrupts. `tsl2772_get_lux()` reads ALS channels and applies the lux table and gain trim; `tsl2772_get_prox()` reads proximity data after validity checks. IIO hooks include `read_raw`, `write_raw`, `read_avail`, event value/config callbacks, and custom sysfs attributes for target lux, calibration, lux table, and proximity calibration.

## Control Flow
Probe enables `vdd`/`vddio`, waits for boot, verifies the chip ID family nibble, initializes mutexes and channel tables, optionally requests a threaded IRQ, loads defaults, powers the chip on, and registers the IIO device. Direct reads call the appropriate measurement helpers under ALS/proximity locks. Raw writes and sysfs stores update cached settings and call `tsl2772_invoke_change()`, which locks both domains, powers down if active, and rewrites device state. IRQ handling reads status, pushes ALS/proximity threshold events, and clears both interrupt latches.

## State And Persistence
Most user-visible configuration persists only in memory in `settings` and the lux-table array; it is rewritten to hardware on every change, resume, and probe. No nonvolatile storage is used. `tsl2772_chip_status` tracks unknown, working, or suspended state. Last ALS/proximity values are cached, and invalid ALS reads may return the previous lux value. Suspend powers the chip off and disables regulators; resume re-enables supplies and reapplies cached settings.

## Dependencies And Integration Points
The driver depends on SMBus byte/word operations, IIO direct mode/events/sysfs, firmware properties, legacy platform data from `linux/platform_data/tsl2772.h`, regulator bulk APIs, and system sleep PM. Device matching uses I2C IDs and OF compatibles. Interrupt availability controls whether event-capable channel specs are exposed.

## Risks
Configuration changes power-cycle and rewrite the chip, so failures can leave cached state diverged from hardware. The custom lux-table store uses integer parsing and binary copy into a struct array; malformed but numerically valid input deserves boundary testing. `tsl2772_als_calibrate()` appears to test `TSL2772_STA_ADC_VALID` against the control register value rather than the status register, which is a suspicious validation path. Proximity calibration computes `(max << 1) - mean` without explicit range clamping. DT property errors are ignored unless values are syntactically invalid.

## Test Signals
Useful tests include probe with each ID family, regulator failure paths, firmware property parsing, ALS/proximity raw reads with valid/invalid status bits, lux overflow/zero-channel handling, sysfs lux-table replacement, calibration bounds, event enable/threshold period conversions, IRQ event delivery and clear command, suspend/resume reconfiguration, and lock-sensitive concurrent raw writes/events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tsl2772.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tsl4531.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/tsl4531.c

## Purpose
`tsl4531.c` is a small IIO I2C driver for TAOS TSL4531 ambient-light sensors. It exposes one light channel with raw counts, scale, and integration time selection.

## Important APIs, Types, And Functions
`struct tsl4531_data` stores the I2C client, a mutex for integration-time writes, and the cached integration-time selector. `tsl4531_read_raw()` reads `TSL4531_DATA`, returns scale as `1 << int_time`, and maps selector 0/1/2 to 400/200/100 ms. `tsl4531_write_raw()` validates and writes the integration-time selector to `TSL4531_CONFIG`. `tsl4531_check_id()` validates the ID register high nibble against the supported TSL45311/313/315/317 IDs.

## Control Flow
Probe allocates the IIO device, validates ID, writes normal operating mode, configures the default 400 ms integration time, sets one direct-mode channel, and registers the IIO device. Remove unregisters IIO and powers the device down. System suspend writes powerdown; resume writes normal mode.

## State And Persistence
The only mutable software state is `int_time`. It is cached after successful writes but is not reinitialized on resume beyond normal mode, so integration-time hardware state relies on chip retention across sleep or on prior configuration not being reset by power loss. There is no runtime PM or regulator handling.

## Dependencies And Integration Points
The driver uses SMBus byte and word accesses, IIO direct-mode callbacks, a static `integration_time_available` sysfs attribute, I2C ID matching, and simple sleep PM.

## Risks
Raw data uses `i2c_smbus_read_word_data()` without byte swapping; correctness depends on the device and SMBus adapter returning the layout expected by existing ABI. Resume does not rewrite `TSL4531_CONFIG`. There is no locking around reads versus integration-time writes, so a read may race with config changes. There is no OF table in this copy, only I2C IDs.

## Test Signals
Test ID rejection, probe default writes, raw read error propagation, all three supported integration times, invalid write values, remove/suspend powerdown, resume normal-mode write, and behavior after suspend where config may have been lost.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tsl4531.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/us5182d.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/us5182d.c

## Purpose
`us5182d.c` supports the UPISEMI USD/US5182D proximity and ambient-light sensor. It exposes ALS raw/scale, proximity raw, proximity threshold events, oneshot or continuous operation, dark-current tuning, and runtime/system power management.

## Important APIs, Types, And Functions
`struct us5182d_data` stores the client, lock, glass attenuation factor, dark-gain values, dark thresholds, proximity thresholds, event enable flags, current opmode, power mode, enable caches, and `upisemi,continuous` policy. `us5182d_set_opmode()` writes CFG0 mode bits and commits via `US5182D_REG_MODE_STORE`. `us5182d_als_enable()` and `us5182d_px_enable()` coordinate ALS/proximity modes, especially in oneshot mode where enabling one disables the other. `us5182d_read_value()` serializes reads, triggers oneshot if needed, resumes runtime PM for continuous mode, reads ALS or proximity, then autosuspends. Scale writes update ALS gain and dark threshold registers. Event callbacks maintain high/low threshold caches and enable/disable hardware thresholds.

## Control Flow
Probe checks chip ID, optionally registers a low-triggered threaded IRQ, reads firmware properties, resets/configures the chip, writes dark-current compensation values, enables runtime PM, and registers IIO. Raw reads go through `us5182d_read_value()`. Event enable forces continuous power and proximity mode, programs threshold registers, and disables thresholds with sentinel values when events are turned off. IRQ reads CFG0 to determine rising/falling proximity state, pushes an IIO threshold event, and clears the PX IRQ bit.

## State And Persistence
Thresholds, event-enable flags, opmode, power mode, and ALS/proximity enabled flags are software caches. Hardware mode changes must be stored through `MODE_STORE`, but the driver does not persist settings across full reset beyond reinitializing defaults at probe. Runtime suspend sets CFG0 shutdown for continuous mode; oneshot mode leaves power handling to the measurement trigger. Platform properties can override glass coefficient, dark threshold table, dark gains, and default continuous mode.

## Dependencies And Integration Points
The driver uses SMBus byte/word access, IIO events/sysfs/direct mode, IRQ threads, firmware properties, runtime PM/autosuspend, system sleep PM, ACPI, OF, and I2C device IDs.

## Risks
Event enabling changes `power_mode` and can leave the device continuous if error paths are not carefully tested. Scale changes perform multiple I2C writes under a lock but do not use runtime PM explicitly. The dark-threshold pointer may point to static defaults or property-backed storage; invalid property lengths fall back silently. The comment still says "To do: Interrupt support" even though IRQ handling exists. Word endianness assumptions and threshold disable sentinels are hardware-sensitive.

## Test Signals
Test chip-ID rejection, default and firmware-property initialization, oneshot reads, continuous runtime PM reads, ALS scale writes and dark-threshold updates, proximity threshold programming, event enable/disable with both directions, IRQ direction decoding, suspend/resume in both power modes, and failure unwinding after partial init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/us5182d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/vcnl4000.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/vcnl4000.c

## Purpose
`vcnl4000.c` is a multi-device Vishay/Capella IIO driver for VCNL4000, VCNL4010/4020, VCNL4040, VCNL4200, CM36672P, and CM36686-compatible sensors. It supports ambient light, proximity, threshold events, VCNL4010 buffered proximity capture, runtime PM, and variant-specific integration time, persistence, oversampling, and LED-current controls.

## Important APIs, Types, And Functions
`struct vcnl4000_data` stores the client, variant ID, revision, scales, interrupt-enable state, chip spec, main mutex, VCNL4200-style per-channel timing locks, and `near_level`. `struct vcnl4000_chip_spec` supplies per-variant channels, info callbacks, init, measurement, power, IRQ, trigger-buffer hooks, interrupt register, timing tables, and lux scale. `vcnl4000_init()` validates legacy byte-register devices; `vcnl4200_init()` validates VCNL4040/4200 IDs and configures 16-bit proximity. `vcnl4000_measure()` starts on-demand byte-register conversions and polls ready bits; `vcnl4200_measure()` rate-limits word-register reads using per-channel `last_measurement`.

## Control Flow
Probe selects `chip_spec` from the I2C ID, enables `vdd/vio/vled`, initializes the variant, powers the chip, registers optional VCNL4010 triggered buffer support, registers IRQ support when available, registers IIO, and enables runtime autosuspend. Raw reads resume runtime PM, call the variant measurement hook, and autosuspend. VCNL4010 direct reads/writes refuse access when periodic mode is active for event or buffer capture. VCNL4040/4200 event callbacks read/write word threshold and persistence registers. IRQ handlers push threshold events and, for VCNL4010 data-ready IRQs, poll the IIO trigger.

## State And Persistence
Runtime state is mostly hardware-backed; software caches include `al_scale`, `ps_scale`, `als_int`, `ps_int`, `near_level`, and VCNL4200 sample timing. Runtime suspend calls variant power-off except when VCNL4040/4200 interrupts are enabled, preserving event monitoring. Remove disables runtime PM, unregisters IIO, marks suspended, and powers down. No nonvolatile configuration is stored.

## Dependencies And Integration Points
The driver integrates with IIO direct mode, events, ext_info, triggered buffers, triggers, runtime PM, regulators, OF/I2C matching, SMBus byte/word/swapped word operations, and firmware property `proximity-near-level`.

## Risks
The shared chip-spec table has variant-sensitive correctness requirements; an incorrect `num_channels`, timing table, or interrupt register affects ABI and reads. VCNL4010 has explicit conflicts between direct reads, threshold capture, and buffered mode; missed direct-mode claims can cause races. VCNL4040 event-config code appears to read event status bits from config registers for proximity direction enable, which is subtle and should be checked against the datasheet. Runtime suspend intentionally stays powered with interrupts enabled, so power tests must account for wake/event behavior.

## Test Signals
Test all variant probe IDs, regulator failures, legacy on-demand polling timeout, VCNL4200 timing delays, raw light/proximity reads and scales, VCNL4010 sample frequency and buffer enable/disable conflicts, VCNL4010 threshold IRQ clearing, VCNL4040/4200 threshold value/period/config callbacks, runtime autosuspend with and without interrupts, and OF compatible data mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/vcnl4000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/vcnl4035.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/vcnl4035.c

## Purpose
`vcnl4035.c` supports the Vishay VCNL4035 ambient-light sensor, exposing ALS raw data, white-channel intensity, integration time, calculated scale, threshold event parameters, optional IRQ-triggered events, and an optional triggered buffer.

## Important APIs, Types, And Functions
`struct vcnl4035_data` stores the client, regmap, cached ALS integration selector, persistence, thresholds, and optional data-ready trigger. `vcnl4035_init()` validates device ID, powers ALS on, enables the white channel, applies default integration/persistence/thresholds, and caches them. `vcnl4035_read_raw()` wraps raw reads in runtime PM and uses `vcnl4035_read_info_raw()`, which claims direct mode before reading ALS or white data. Event callbacks read/write cached threshold and persistence state and update registers. Trigger ops enable/disable ALS interrupt bits, and the consumer handler pushes ALS data with timestamps.

## Control Flow
Probe creates a 16-bit little-endian cached regmap, initializes IIO direct-mode channels, runs hardware init, optionally creates a trigger/buffer/IRQ when `client->irq` is present, registers IIO, and enables runtime autosuspend. The IRQ thread checks interrupt flags; when threshold bits are set, it pushes an IIO light threshold event and polls the trigger. Runtime resume syncs regcache, powers ALS on, and waits one integration cycle.

## State And Persistence
Thresholds, persistence, and integration-time selector are cached in `vcnl4035_data` and in regmap cache. Runtime suspend disables ALS and marks the regcache dirty; resume syncs cached configuration and re-enables ALS. No persistent storage is used. Without IRQ, event config callbacks are not exposed, but raw direct reads remain available.

## Dependencies And Integration Points
The driver depends on regmap with 8-bit registers/16-bit little-endian values, IIO events, triggers, triggered buffers, runtime PM/autosuspend, I2C/OF matching, and direct-mode arbitration.

## Risks
Integration-time writes use `val / 100` directly against the mask, so unsupported positive values such as 150 ms can produce unintended selector writes unless upper layers constrain inputs. The scale calculation is derived from cached `als_it_val`; stale cache would affect ABI output. IRQ handler returns `IRQ_NONE` when flags are absent, which is correct for shared/spurious IRQs but needs board-level testing. Regcache sync errors in runtime resume are ignored before power-on result is checked.

## Test Signals
Test ID mismatch, default register writes, raw ALS and white reads with direct-mode contention, integration-time valid/invalid writes, scale for each selector, threshold ordering validation, persistence power-of-two validation, IRQ event/trigger path, buffer scan-mask validation, runtime suspend/resume regcache restoration, and no-IRQ probe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/vcnl4035.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/veml3235.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/veml3235.c

## Purpose
`veml3235.c` is an IIO driver for the Vishay VEML3235 ambient-light sensor. It exposes raw ALS and white-channel intensity plus shared integration time and scale controls based on the IIO gain-time-scale helper.

## Important APIs, Types, And Functions
`struct veml3235_data` stores the client, device, regmap, regmap fields for integration time, gain, and ID, and an `iio_gts` table. `veml3235_get_it()/set_it()` translate between hardware selectors and microsecond integration times; changing integration time computes a replacement gain with `iio_gts_find_new_gain_by_gain_time_min()` to preserve scale where possible. `veml3235_set_scale()` finds a gain/time pair for a requested scale. `veml3235_read_raw()` reads ALS or white data and returns current integration time or scale.

## Control Flow
Probe initializes a cached little-endian 16-bit regmap, allocates regmap fields, enables `vdd`, sets up IIO metadata, logs unknown IDs, initializes GTS tables, sets default gain x1 and 100 ms integration, powers the chip on, registers a shutdown action, and registers IIO. Runtime suspend/resume helpers shut down or power on the sensor, although runtime PM is only wired in driver PM ops and not explicitly enabled in probe.

## State And Persistence
Hardware configuration is represented by regmap fields and regmap cache. Defaults are reprogrammed at probe. The shutdown action powers off on device teardown. There is no nonvolatile persistence. Because runtime PM is not enabled in probe, runtime callbacks generally depend on external PM usage rather than normal autosuspend.

## Dependencies And Integration Points
The driver depends on regmap access tables, regmap fields, `IIO_GTS_HELPER`, regulator `vdd`, I2C/OF matching, and IIO direct-mode callbacks. It imports the `IIO_GTS_HELPER` namespace.

## Risks
ID mismatch is informational rather than fatal, so compatible misbindings may still register. Runtime PM callbacks exist without probe enabling runtime PM. Gain selector handling intentionally avoids reserved gain combinations; GTS table changes must preserve that mapping. Reads are not guarded by runtime resume or direct-mode claims.

## Test Signals
Test regmap access limits, ID read logging, regulator failure, GTS initialization, default gain/time writes, raw ALS/white reads, integration-time changes with gain preservation, scale writes across all supported pairs, invalid scale/time rejection, shutdown action, and runtime suspend/resume if PM is enabled externally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/veml3235.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/veml6030.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/veml6030.c

## Purpose
`veml6030.c` supports Vishay VEML6030, VEML6035, and VEML7700 ambient-light sensors. It exposes ALS and white-channel raw data, processed lux for ALS, shared scale/integration-time controls through IIO GTS, threshold events for IRQ-capable variants, power-save defaults, and triggered-buffer capture.

## Important APIs, Types, And Functions
`struct veml6030_data` holds the I2C client, regmap, regmap fields, selected `veml603x_chip`, and `iio_gts`. The chip descriptor selects channels, reg fields, max scale, hardware init, and info setup. `veml6030_set_it()` preserves scale by finding a new gain for a changed integration time. `veml6030_set_scale()` chooses gain/time selectors for a requested scale. `veml6030_process_als()` computes processed lux from raw ALS, max scale, and total gain. Event helpers handle high/low thresholds and persistence periods. `veml6030_set_info()` exposes event callbacks only when an IRQ is present; VEML7700 is forced to no-IRQ info.

## Control Flow
Probe requires plain I2C, creates a cached 16-bit little-endian regmap, enables `vdd`, obtains chip match data, chooses IIO channels/info, initializes regmap fields, runs variant hardware init, registers a triggered buffer, and registers IIO. Hardware init shuts ALS down, writes default config, PSM, thresholds, powers on, installs shutdown action, and clears stale interrupt status. IRQ handler reads `ALS_INT`, rejects spurious interrupts, and pushes rising/falling threshold events. Trigger handler reads active scan channels and timestamps them.

## State And Persistence
Gain/time state lives in hardware selectors and regmap cache; GTS derives available scales and current scale. Thresholds and persistence are hardware-backed. Runtime suspend shuts ALS down; runtime resume powers ALS on, but probe does not explicitly enable runtime PM. No nonvolatile state exists. Event availability depends on IRQ at probe.

## Dependencies And Integration Points
The driver integrates regmap, regmap fields, regulators, IIO events/sysfs, IIO triggered buffers, `IIO_GTS_HELPER`, I2C/OF matching, and optional IRQs. It imports the GTS helper namespace.

## Risks
The no-runtime-PM-enable pattern means PM callbacks may not run in normal autosuspend scenarios. `veml6030_write_interrupt_config()` shuts down ALS and updates interrupt plus shutdown bits in one call; incorrect bit composition would leave ALS off or interrupts disabled. Persistence parsing has special-case second values for long periods. VEML6035 and VEML6030 share channel definitions but use different gain fields and scales, so match-data correctness is critical.

## Test Signals
Test all compatibles and I2C IDs, plain-I2C rejection, regulator failure, GTS scale/time availability, integration-time gain preservation, scale writes, processed lux math, threshold read/write, persistence available strings per integration time, IRQ/no-IRQ info selection, spurious and real IRQs, triggered-buffer active scan reads, hardware init defaults, and runtime suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/veml6030.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/veml6040.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/veml6040.c

## Purpose
`veml6040.c` is a direct-mode IIO driver for the Vishay VEML6040 RGBW light sensor. It exposes raw red, green, blue, and clear intensity channels with a shared integration-time control.

## Important APIs, Types, And Functions
`struct veml6040_data` stores the I2C client and regmap. `veml6040_read_raw()` reads channel data registers or decodes the integration-time selector from the config register. `veml6040_write_raw()` maps a requested millisecond integration time to a config selector. `veml6040_read_avail()` reports the supported integration-time list. `veml6040_shutdown_action()` sets the shutdown bit during managed teardown.

## Control Flow
Probe verifies plain I2C support, allocates IIO, initializes a 16-bit little-endian regmap, enables `vdd`, writes initial auto-measurement config at 40 ms with shutdown cleared, registers a managed shutdown action, and registers IIO. There is no remove function beyond devm cleanup.

## State And Persistence
Configuration is hardware-backed in `VEML6040_CONF_REG`; the driver does not cache integration time. The shutdown action powers the sensor down on driver detach. No runtime PM or persistent storage is used.

## Dependencies And Integration Points
The driver uses regmap, regulator `vdd`, IIO direct mode/read_avail/write_raw, I2C/OF IDs, and plain I2C adapter capability checks.

## Risks
`read_raw()` returns integration time as an integer number of milliseconds rather than the more common seconds-plus-microseconds format used by many IIO light drivers; this may be intentional for this ABI but should be checked. There is no direct-mode claim around raw reads. There is no scale output, event support, or PM suspend/resume. The shutdown action ignores errors.

## Test Signals
Test I2C capability failure, regmap setup failure, regulator failure, initial config write, all RGBW raw reads, integration-time read/write for all six values, invalid integration times, shutdown action behavior, and OF/I2C matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/veml6040.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/veml6046x00.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/veml6046x00.c

## Purpose
`veml6046x00.c` supports Vishay VEML6046X00 RGBIR color sensors. It exposes raw red, green, blue, and IR intensity channels with shared integration time and scale, active-force direct reads, continuous buffered capture, runtime PM, and regulator-backed power control.

## Important APIs, Types, And Functions
`struct veml6046x00_data` stores the regmap, optional IIO trigger pointer, and regmap fields for interrupt enable, mode, trigger, integration time, and persistence. The integration-time table maps directly to register selectors. Scale is a combined hardware gain and photodiode-size mapping through `veml6046x00_gain_pd` and `veml6046x00_it_gains`. `veml6046x00_single_read()` resumes the device, sets active-force mode, triggers a measurement, waits integration time plus margin, polls the vendor-required two-byte interrupt register for data-ready, claims direct mode, bulk-reads one channel, and autosuspends.

## Control Flow
Probe initializes an 8-bit regmap, allocates regmap fields, enables `vdd`, writes a known active-force configuration and default thresholds, clears interrupts, registers a shutdown action, enables runtime PM/autosuspend, validates the part ID non-fatally, sets IIO metadata, registers a triggered buffer, drops the initial runtime PM reference, and registers IIO. Buffer preenable switches to continuous mode and resumes PM; postdisable returns to active-force mode and autosuspends. Trigger handler bulk-reads all four channels and pushes a timestamped scan.

## State And Persistence
Integration time, gain/PD, mode, trigger, thresholds, and power bits are hardware state accessed via regmap fields. Runtime suspend sets both power-off bits; resume clears both. The initial setup uses default thresholds and active-force mode. No nonvolatile persistence exists.

## Dependencies And Integration Points
The driver uses regmap, regmap fields, little-endian bulk I/O, IIO direct mode and triggered buffers, runtime PM with autosuspend, regulator `vdd`, OF/I2C matching, and standard IIO intensity modifiers.

## Risks
The part ID check only logs unknown IDs and still registers. Direct reads rely on a two-step data-ready poll and can return `-EAGAIN`; callers need retry coverage. Single reads and buffers change the same mode/trigger fields, so direct-mode and buffer interactions are important. Scale availability depends on current integration time. Error paths in buffer postdisable can leave runtime PM references or mode state unexpected if not tested.

## Test Signals
Test setup register writes, ID read logging, runtime PM reference balance, every integration time and scale entry, invalid scale/time rejection, active-force direct reads including timeout, data-ready error handling, buffer preenable/postdisable mode transitions, trigger bulk scan order and endianness, shutdown action, and suspend/resume power bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/veml6046x00.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/veml6070.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/veml6070.c

## Purpose
`veml6070.c` supports the Vishay VEML6070 UVA sensor, which uses two I2C addresses. It exposes raw UV intensity, processed UV index, and integration-time controls derived from the external RSET resistor.

## Important APIs, Types, And Functions
`struct veml6070_data` stores the primary and dummy I2C clients, cached command byte, mutex, RSET value in kohms, and a computed four-entry integration-time table. `veml6070_calc_it()` reads `vishay,rset-ohms`, validates the supported range, and computes integration times. `veml6070_read()` clears shutdown, waits one integration period plus margin, reads MSB from the second address and LSB from the first, then restores shutdown. `veml6070_to_uv_index()` scales raw values by RSET and integration-time selector and maps them into UVI bands.

## Control Flow
Probe allocates IIO, computes integration times, enables `vdd`, creates a managed dummy client at the second address, writes default IT x1 plus reserved and shutdown bits, installs dummy-client unregister cleanup, and registers IIO. Raw and processed reads share the same measurement helper under a mutex. Integration-time writes update the cached command and write it to the primary address.

## State And Persistence
The command byte is cached in memory and written to hardware for integration-time changes and read shutdown transitions. Integration-time options are derived from firmware resistor data at probe. The sensor is normally left in shutdown between reads. There is no runtime PM, system sleep PM, or nonvolatile persistence.

## Dependencies And Integration Points
The driver uses two I2C addresses on the same adapter, a regulator, firmware property `vishay,rset-ohms`, IIO direct-mode callbacks, and I2C/OF matching.

## Risks
Correct operation requires the second dummy I2C address to be free and present. Read comments conflict with register-name comments about MSB/LSB address naming, so hardware byte order deserves regression coverage. Long integration times block reads under the mutex with `msleep()`. ACK/interrupt support is explicitly not implemented. There is no suspend hook, relying on shutdown-after-read behavior.

## Test Signals
Test RSET min/max validation and default, integration-time table generation, dummy-client allocation failure, default command write, raw read byte ordering, shutdown restoration after read errors, UV index boundaries for all integration times, integration-time writes and invalid values, regulator failure, and cleanup unregistering the dummy client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/veml6070.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/veml6075.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/veml6075.c

## Purpose
`veml6075.c` supports the Vishay VEML6075 UVA/UVB sensor. It exposes compensated UVA and UVB raw intensity, channel responsivity scale, processed UV index, and shared integration-time control using active-force measurements.

## Important APIs, Types, And Functions
`struct veml6075_data` stores the client, regmap, and a mutex protecting integration-time changes and measurement triggering. `veml6075_request_measurement()` reads config, clears shutdown, sets trigger, sleeps 1.5x integration time, then sets shutdown again while leaving data readable. `veml6075_uva_comp()` and `veml6075_uvb_comp()` apply open-air visible/IR compensation coefficients and clamp to 16 bits. `veml6075_read_uv_direct()` measures, reads compensation channels, reads UVA or UVB, applies compensation, and returns an integer. `veml6075_read_uvi()` reads both UV channels, compensates them, applies integration-time-adjusted responsivity, and returns micro UV index.

## Control Flow
Probe creates a 16-bit little-endian regmap with explicit readable/writable register filters, initializes the mutex and IIO channels, enables `vdd`, writes default 100 ms active-force shutdown config, and registers IIO. Raw UVA/UVB and processed UVI reads each trigger fresh measurements under the mutex. Integration-time writes search the supported millisecond list and update config bits under the same mutex.

## State And Persistence
The device is configured for active-force mode and left in shutdown between reads. Integration time is hardware state in the config register and protected by the mutex. No runtime PM, system sleep PM, ID validation, or nonvolatile persistence is present.

## Dependencies And Integration Points
The driver uses regmap, regulator `vdd`, IIO intensity/UVINDEX channels, I2C/OF matching, mutex guards, and fixed open-air coefficients/responsivity from the datasheet.

## Risks
There is no device-ID read despite defining `VEML6075_CMD_ID`, so misbound devices can register if regmap writes work. Measurements sleep synchronously for up to 1.2 s at 800 ms integration. The UVI calculation uses fixed open-air coefficients and may not suit covered sensors without calibration hooks. Scale values are hard-coded comments/outputs. Error paths after triggering may leave shutdown handling dependent on where the failure occurred.

## Test Signals
Test regmap readability/writability, regulator failure, default config write, all integration-time reads/writes and invalid values, raw UVA/UVB compensation with clamp behavior, UVI math for each integration time, mutex serialization between reads and writes, measurement failure paths, and OF/I2C matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/veml6075.c -->
