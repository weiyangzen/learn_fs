# subset-b-003894 research

Work item: `subset-b-003894`

Scope: Linux IIO light/proximity/color sensor drivers under `sources/distributed-fs/ceph-client/drivers/iio/light/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/bh1745.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/bh1745.c

## Purpose

`bh1745.c` is an IIO driver for the ROHM BH1745 digital RGB plus clear color sensor. It exposes four `IIO_INTENSITY` channels for red, green, blue, and clear light, with direct raw reads, shared scale and integration-time controls, threshold events, and a triggered buffer. The driver is built around `regmap` and the IIO gain-time-scale helper namespace, so user-visible scale values stay consistent with the selected ADC gain and measurement time.

## Important APIs, Types, And Functions

The central state is `struct bh1745_data`, containing a mutex, `struct regmap *`, parent `struct device *`, an optional trigger pointer, and `struct iio_gts`. Static register access tables define readable, writable, and volatile ranges for `devm_regmap_init_i2c()`.

Important functions are `bh1745_reset()`, `bh1745_power_on()`, `bh1745_power_off()`, `bh1745_get_scale()`, `bh1745_set_scale()`, `bh1745_get_int_time()`, `bh1745_set_int_time()`, `bh1745_read_raw()`, `bh1745_write_raw()`, `bh1745_read_thresh()`, `bh1745_write_thresh()`, `bh1745_read_event_config()`, `bh1745_write_event_config()`, `bh1745_interrupt_handler()`, `bh1745_trigger_handler()`, `bh1745_setup_triggered_buffer()`, `bh1745_init()`, and `bh1745_probe()`. `bh1745_channels[]` declares four 16-bit color channels plus timestamp. `bh1745_info` wires raw access, event callbacks, format callbacks, and availability callbacks into IIO.

## Control Flow

Probe allocates an IIO device, initializes regmap, reads the part ID from `BH1745_SYS_CTRL`, enables the `vdd` regulator, initializes GTS tables, resets the chip, powers RGBC conversion, registers a managed power-off action, sets up a triggered buffer, optionally requests the client IRQ for threshold events, and registers the IIO device. Direct raw reads claim direct mode with `iio_device_claim_direct()`, bulk-read two bytes from the selected color data register, then release direct mode. Scale changes first try to preserve current integration time, but if no gain can realize the requested scale at that time, they search other supported integration-time selections and update both `MODE_CTRL1` and `MODE_CTRL2`. Integration-time writes validate the requested microseconds through GTS and adjust gain to preserve scale as closely as possible.

## State And Persistence

Runtime state is almost entirely hardware-backed: current gain, measurement time, thresholds, interrupt source, and persistence live in chip registers and regmap cache. The mutex serializes scale/time updates and readback calculations. `devm_add_action_or_reset()` ensures `BH1745_CTRL2_RGBC_EN` is cleared when the device is removed or probe unwinds. Threshold values are written directly to high and low threshold register pairs; persistence is stored in `BH1745_PERSISTENCE`. There is no nonvolatile persistence in the driver.

## Dependencies And Integration Points

The driver integrates with I2C, regulator framework, regmap, IIO direct mode, IIO events, triggered buffers, triggers, and `IIO_GTS_HELPER`. It supports OF matching via `rohm,bh1745`. If `client->irq` is present, the driver exposes threshold event delivery from the hardware interrupt line; otherwise direct reads and buffer polling still work.

## Risks And Test Signals

Risk areas include endian handling in `regmap_bulk_read()` and threshold bulk writes, correctness of GTS scale/time migration, and interrupt-source exclusivity because the hardware interrupt register selects one source channel at a time. `bh1745_read_raw()` returns `0` rather than the error from `bh1745_get_int_time()` in one failure path, which is worth review. Useful tests are probe with and without IRQ, sysfs raw reads for all colors, `scale_available` and `integration_time_available`, write/readback of scale and integration time, threshold enable/value/persistence sysfs paths, triggered buffer capture with active scan masks, and removal verifying the RGBC enable bit is cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/bh1745.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/bh1750.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/bh1750.c

## Purpose

`bh1750.c` supports ROHM BH1710, BH1715, BH1721, BH1750, and BH1751 ambient light sensors through the IIO direct-mode interface. It exposes one `IIO_LIGHT` channel with raw count, scale, and integration time. The driver programs the measurement-time register value, issues a one-time high-resolution measurement command, sleeps for conversion, and reads a big-endian 16-bit sample.

## Important APIs, Types, And Functions

`struct bh1750_data` stores the I2C client, mutex, chip variant table, current `mtreg`, and optional reset GPIO. `struct bh1750_chip_info` captures per-variant min/max/default measurement-time register values, conversion factors for time and scale, list increment, and bit masks for high and low integration-time command fields. `bh1750_change_int_time()` validates and writes the high and low MTreg command bytes. `bh1750_read()` powers measurement, sleeps, and reads the result. `bh1750_read_raw()` and `bh1750_write_raw()` implement the IIO ABI. `bh1750_show_int_time_available()` formats supported times. Probe and remove are handled by `bh1750_probe()` and `bh1750_remove()`, with suspend handled by `bh1750_suspend()`.

## Control Flow

Probe checks for plain I2C plus SMBus byte writes, allocates IIO state, selects variant data from the I2C ID, optionally toggles a `reset` GPIO, writes the default integration time, initializes the mutex, and registers the IIO device. A raw read locks the driver, calls `bh1750_read()`, writes `BH1750_ONE_TIME_H_RES_MODE`, waits for `mtreg_to_usec * mtreg` plus margin, and receives two bytes with `i2c_master_recv()`. Integration time writes accept only `val == 0` and pass `val2` in microseconds to `bh1750_change_int_time()`. Remove unregisters the IIO device and powers the chip down under the mutex. Suspend writes power-down, mainly for BH1721 continuous behavior.

## State And Persistence

The only cached mutable setting is `data->mtreg`, which mirrors the measurement-time value written to hardware. Scale is derived from chip constants and `mtreg`; integration time is derived from `mtreg_to_usec * mtreg`. The optional reset GPIO is acquired as managed device state. No register cache or persistence is used beyond the live sensor register state.

## Dependencies And Integration Points

The driver depends on I2C, GPIO descriptors, IIO core/sysfs, and simple sleep PM. OF compatibles are supplied for all supported ROHM variants, but variant selection in probe comes from `i2c_client_get_device_id()` and the I2C ID table. The reset line is optional and named `reset`.

## Risks And Test Signals

Probe initializes integration time before `mutex_init()`, which is safe because no parallel access exists yet but is a notable ordering detail. Tests should cover all variant IDs because bit masks and valid MTreg ranges differ. Validate optional reset GPIO polarity with real board wiring, raw reads after changing integration time, `integration_time_available` formatting for large BH1710/BH1721 ranges, suspend power-down, and remove-time power-down. Fault injection around SMBus writes and `i2c_master_recv()` should propagate errors to sysfs reads and writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/bh1750.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/bh1780.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/bh1780.c

## Purpose

`bh1780.c` is an IIO driver for the ROHM BH1780GLI ambient light sensor. It exposes a single `IIO_LIGHT` channel for raw 16-bit ALS data and a fixed integration time. The driver emphasizes runtime power management because the chip has a significant startup plus measurement delay.

## Important APIs, Types, And Functions

`struct bh1780_data` stores only the I2C client. Low-level helpers `bh1780_write()`, `bh1780_read()`, and `bh1780_read_word()` wrap SMBus register access and prepend the command bit. `bh1780_debugfs_reg_access()` exposes register access for IIO debugfs. `bh1780_read_raw()` handles raw illuminance and integration time. `bh1780_probe()`, `bh1780_remove()`, `bh1780_runtime_suspend()`, and `bh1780_runtime_resume()` implement lifecycle and PM.

## Control Flow

Probe checks SMBus byte functionality, allocates the IIO device, powers the sensor with `BH1780_PON`, waits two milliseconds, marks runtime PM active, reads the part ID/revision, configures autosuspend to five seconds, registers one direct-mode channel, and registers the IIO device. A raw read performs `pm_runtime_get_sync()`, reads `BH1780_REG_DLOW` as a word, and calls `pm_runtime_put_autosuspend()`. Runtime suspend writes `BH1780_POFF`. Runtime resume writes `BH1780_PON` and sleeps for power-on plus the 250 ms measurement interval.

## State And Persistence

There is no cached configuration beyond runtime PM state. The integration time is fixed at 250 ms and reported as `0.250000`. Hardware power state is owned by runtime PM, with autosuspend used to avoid repeatedly paying conversion latency. Register values are not cached in software.

## Dependencies And Integration Points

The driver uses I2C SMBus byte/word transfers, IIO direct mode, debugfs register access via `iio_info`, and runtime PM. It matches `rohm,bh1780gli` and the `bh1780` I2C ID. It has no interrupts, no buffers, and no events.

## Risks And Test Signals

`pm_runtime_get_sync()` return value is ignored in raw reads; tests with PM failures may reveal stale or failed reads. `i2c_check_functionality()` checks only `I2C_FUNC_SMBUS_BYTE`, while word reads are later used, so adapter capability coverage should be checked. Test raw reads before and after autosuspend expiry, runtime suspend/resume sequencing, debugfs register read/write, remove power-off, and probe rollback after ID read or IIO registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/bh1780.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/cm32181.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/cm32181.c

## Purpose

`cm32181.c` drives Capella CM3218, CM32181, and CM32182 ambient light sensors. It exposes a single processed `IIO_LIGHT` illuminance channel with calibration scale and integration time. It converts raw ALS counts to lux using per-device integration-time tables, optional ACPI calibration metadata, and cached register settings.

## Important APIs, Types, And Functions

`struct cm32181_chip` contains the active I2C client, parent device, mutex, cached configurable registers, an initialization bitmap, calibration scale, lux-per-bit constants, and selected integration-time table pointers. ACPI support is in `cm32181_acpi_get_cpm()` and `cm32181_acpi_parse_cpm_tables()`, reading `CPM0` and `CPM1`. Core functions include `cm32181_reg_init()`, `cm32181_read_als_it()`, `cm32181_write_als_it()`, `cm32181_get_lux()`, raw read/write callbacks, `cm32181_probe()`, and sleep PM callbacks.

## Control Flow

Probe allocates an IIO device and handles a special ACPI case where firmware first binds the SMBus Alert Response Address `0x0c`: it clears pending alerts and creates a dummy client for the actual sensor resource. It then fills state, initializes the channel table, reads the hardware ID, chooses CM3218 or CM32181 integration-time tables, sets default command/calibration values, optionally overrides them from ACPI CPM tables, writes all configured registers from `init_regs_bitmap`, and registers the IIO device. Processed reads call `cm32181_get_lux()`, which reads current integration time from the cached command register, reads raw ALS data, scales by lux-per-bit, base integration time, calibration scale, and caps at `0xffff`.

## State And Persistence

`conf_regs[]` is the authoritative software cache for command and threshold/configuration registers written at init and later integration-time changes. `calibscale`, `lux_per_bit`, and `lux_per_bit_base_it` persist only in memory and are restored from defaults or ACPI on probe. Suspend writes `CM32181_CMD_ALS_DISABLE` without updating the cache; resume writes the cached command register to restore pre-suspend configuration.

## Dependencies And Integration Points

The driver depends on I2C SMBus word operations, IIO sysfs attributes, optional ACPI table parsing, OF and ACPI matching, and simple sleep PM. It creates and unregisters a dummy I2C client when ACPI exposes the ARA first. It includes interrupt/regulator headers but does not use IRQs or regulators in this implementation.

## Risks And Test Signals

ACPI CPM parsing is a major compatibility surface: invalid package lengths, mismatched calibration scales, and ARA resource ordering should be tested. `cm32181_write_raw()` for `CALIBSCALE` returns `val` instead of zero, which is a behavioral oddity for IIO write callbacks. Integration-time writes choose the first supported value greater than or equal to the requested `val2`, so tests should confirm this rounding behavior. Validate ID rejection, lux conversion at each integration time, suspend/resume restoring cached config, and `integration_time_available` output for both CM3218 and CM32181 families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/cm32181.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/cm3232.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/cm3232.c

## Purpose

`cm3232.c` is an IIO ambient light driver for the Capella CM3232. It exposes processed lux, calibration scale, and integration time on one `IIO_LIGHT` channel. The driver resets and identifies the sensor during probe, caches the command register, and computes lux from raw ALS counts.

## Important APIs, Types, And Functions

`struct cm3232_chip` stores the I2C client, static ALS info, calibration scale, cached command byte, and last ALS word. `cm3232_als_it_scales[]` maps IIO integration times to command bits. Core functions are `cm3232_reg_init()`, `cm3232_read_als_it()`, `cm3232_write_als_it()`, `cm3232_get_lux()`, `cm3232_read_raw()`, `cm3232_write_raw()`, `cm3232_get_it_available()`, `cm3232_probe()`, `cm3232_remove()`, `cm3232_suspend()`, and `cm3232_resume()`.

## Control Flow

Probe allocates state, sets the default calibration scale, configures the IIO channel, calls `cm3232_reg_init()`, and registers the device. Register init disables and resets the chip, reads the ID register, validates the low byte against `0x32`, then writes the default command. A processed read calculates millilux-per-bit based on current integration time, reads `CM3232_REG_ADDR_ALS`, multiplies by calibration scale, converts millilux to lux, and clamps to `0xffff`. Integration-time writes must exactly match one table entry and update the command register. Suspend sets the disable bit in the cached command and writes it; resume clears it and writes the command with reset asserted.

## State And Persistence

The cached `regs_cmd` field mirrors the command register and is used for integration-time readback and PM restore. `calibscale` is runtime-only and defaults to `100000`. `regs_als` stores the last raw ALS read but is not exported separately. No persistent storage is used.

## Dependencies And Integration Points

The driver uses I2C SMBus byte/word operations, IIO direct mode, a custom sysfs integration-time availability attribute, OF matching with `capella,cm3232`, and simple sleep PM. It is not devm-registered, so remove manually disables ALS and unregisters IIO.

## Risks And Test Signals

The driver has no mutex around command/cache updates, so concurrent sysfs reads and writes can race on `regs_cmd` and `calibscale`. Remove disables hardware before unregistering the IIO device, which may be harmless but is an ordering point to test. Validate ID mismatch, exact integration-time write acceptance, lux conversion and saturation, suspend/resume behavior, and error propagation from all SMBus accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/cm3232.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/cm3323.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/cm3323.c

## Purpose

`cm3323.c` is an IIO color light sensor driver for the Capella CM3323. It exposes raw red, green, blue, and clear intensity channels, with a shared integration-time setting. The driver leaves color conversion to userspace and provides direct register counts.

## Important APIs, Types, And Functions

`struct cm3323_data` stores the I2C client, cached 16-bit configuration register, and a mutex. `cm3323_channels[]` declares four modified `IIO_INTENSITY` channels with per-channel raw data and shared integration time. `cm3323_init()` reads, modifies, and writes the configuration register to enable the sensor and auto force mode. `cm3323_disable()` is a devm cleanup action. `cm3323_set_it_bits()` and `cm3323_get_it_bits()` translate IIO integration-time values through `cm3323_int_time[]`. `cm3323_read_raw()` and `cm3323_write_raw()` implement sysfs access.

## Control Flow

Probe allocates a managed IIO device, initializes the mutex and IIO descriptors, calls `cm3323_init()`, registers a cleanup action that writes shutdown, and then uses `devm_iio_device_register()`. Raw reads lock the mutex and read the selected word-data register from the channel `address`. Integration-time reads return the cached configuration bits translated through the table. Integration-time writes require an exact `(val, val2)` match and write a modified config register.

## State And Persistence

The cached `reg_conf` mirrors the configuration register after init and after integration-time writes. It is used as the only source for integration-time readback. Shutdown is handled through a devm action that writes `CM3323_CONF_SD_BIT`; the cache is not needed afterward. There is no regulator, PM callback, buffer, event, or nonvolatile state.

## Dependencies And Integration Points

The driver uses I2C SMBus word transfers, IIO direct mode, IIO sysfs constant attributes, OF matching via `capella,cm3323`, and devm cleanup. It integrates as a standard I2C driver.

## Risks And Test Signals

The hardware configuration write in `cm3323_init()` clears both shutdown and auto/manual force bits; verify this matches board expectations. The cleanup writes only the shutdown bit rather than preserving other config fields. Tests should cover each color channel raw read, all six integration-time values, invalid integration-time writes, probe failure cleanup, and removal confirming shutdown. SMBus word endianness should be verified against the device datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/cm3323.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/cm3605.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/cm3605.c

## Purpose

`cm3605.c` drives the Capella CM3605 ambient light and proximity sensor as a platform device. The light path is analog: an external IIO ADC channel named `aout` is converted from millivolts to lux. The proximity path is interrupt-based and emits IIO threshold events while toggling expected edge direction in software.

## Important APIs, Types, And Functions

`struct cm3605` stores the parent device, VDD regulator, ASET GPIO, ADC channel, lux range derived from RSET, current event direction, and an LED trigger for the infrared emitter. `cm3605_prox_irq()` pushes proximity events and flips `dir`. `cm3605_get_lux()` reads the ADC and linearly maps voltage to lux. `cm3605_read_raw()` exposes light raw data. `cm3605_probe()`, `cm3605_remove()`, `cm3605_pm_suspend()`, and `cm3605_pm_resume()` manage resources and power.

## Control Flow

Probe reads `capella,aset-resistance-ohms`, maps it to an ALS max range, gets the `aout` IIO channel and validates it is `IIO_VOLTAGE`, enables the `vdd` regulator, acquires the `aset` GPIO as high output, requests the platform IRQ, registers and turns on an LED trigger named `cm3605`, registers two IIO channels, and reports the range. A light read calls `iio_read_channel_processed()`, subtracts a 30 mV dark bias, scales by `als_max / 1550 mV`, and returns an integer lux value. Suspend turns off the LED trigger and regulator; resume re-enables both.

## State And Persistence

Board configuration is represented by the `als_max` range and GPIO/regulator handles. Proximity direction is software state only and toggles after every IRQ because the hardware provides edge behavior through VOUT. The driver does not expose event enable/disable callbacks despite declaring an enable bit in the event spec, so the IRQ is always requested while the device is active.

## Dependencies And Integration Points

The driver integrates with platform firmware properties, regulator framework, GPIO descriptors, IIO consumer API for the ADC, LED triggers for IR LED control, IRQ handling, IIO events, and simple PM. OF matching uses `capella,cm3605`.

## Risks And Test Signals

The event spec advertises enable control but no `read_event_config` or `write_event_config` is implemented, so sysfs event enable behavior should be verified. `cm3605_pm_resume()` turns the LED trigger on even if regulator enable fails. Tests should validate RSET mapping, invalid RSET rejection, ADC channel type rejection, lux conversion around 30 mV and overrange, IRQ event direction toggling, suspend/resume regulator and LED behavior, and error cleanup paths after regulator enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/cm3605.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/cm36651.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/cm36651.c

## Purpose

`cm36651.c` drives the Capella CM36651 combined RGB/clear ambient light and proximity sensor. It exposes raw proximity plus red, green, blue, and clear light channels, integration-time controls, and proximity threshold events. The hardware has separate I2C addresses for color, proximity, and alert response, so the driver creates dummy clients for the latter two.

## Important APIs, Types, And Functions

`struct cm36651_data` stores the main client, proximity dummy client, ARA dummy client, mutex, `vled` regulator, event flags, cached integration times, cached color/proximity control registers, and color values. Key functions are `cm36651_setup_reg()`, `cm36651_read_output()`, `cm36651_irq_handler()`, `cm36651_set_operation_mode()`, `cm36651_read_channel()`, `cm36651_read_int_time()`, `cm36651_write_int_time()`, raw read/write callbacks, proximity threshold event callbacks, and probe/remove.

## Control Flow

Probe enables the `vled` regulator, creates dummy clients for proximity address `0x19` and ARA `0x0c`, initializes the mutex and channel table, writes default CS and PS register settings, places both sensors in shutdown, requests a falling threaded IRQ, and registers the IIO device. Raw reads lock the mutex, enable the relevant sensor mode, wait 50 ms, read the output, and shut the sensor back down unless proximity events remain enabled. Event IRQ handling reads ARA to clear the interrupt and maps returned close/far codes to rising/falling proximity threshold events.

## State And Persistence

`cs_ctrl_regs[]` and `ps_ctrl_regs[]` cache configured control values and thresholds. `flags` tracks whether proximity event mode is enabled. Integration-time arrays are runtime caches but are not initialized from explicit defaults in probe before readback, so default readback depends on zero-initialized values. Threshold writes update both cache and hardware. Remove unregisters IIO, disables the regulator, frees IRQ, and unregisters dummy clients.

## Dependencies And Integration Points

The driver uses I2C SMBus byte/word operations, dummy I2C clients, regulator framework, IIO events/sysfs, and IRQ handling. It matches `capella,cm36651`. The proximity alert path depends on SMBus Alert Response Address semantics.

## Risks And Test Signals

`cm36651_write_int_time()` for light uses `int_time >> 2 * chan->address`, where operator precedence and intended bit placement should be reviewed carefully. Proximity event enable/disable returns `-EINVAL` for already-enabled or already-disabled states through the shared mode helper, which may surprise userspace. Tests should cover dummy client creation failures, register setup rollback, raw reads for all channels, proximity event threshold range checking, ARA interrupt clearing, integration-time write/readback for light and proximity, and remove cleanup ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/cm36651.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/cros_ec_light_prox.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/cros_ec_light_prox.c

## Purpose

`cros_ec_light_prox.c` is an IIO frontend for ChromeOS EC light and proximity motion-sense sensors. It represents one logical light or proximity stream from the EC, plus timestamp, and delegates sampling, buffering, common attributes, and PM to `cros_ec_sensors_core`.

## Important APIs, Types, And Functions

`struct cros_ec_light_prox_state` embeds `struct cros_ec_sensors_core_state` and stores two IIO channel specs. `cros_ec_light_prox_read()` handles raw proximity, processed light, calibration bias, calibration scale, and delegates all other masks to `cros_ec_sensors_core_read()`. `cros_ec_light_prox_write()` handles calibration writes and delegates common writes. `cros_ec_light_prox_probe()` initializes the core, builds channel metadata based on EC motion sensor type, and registers the sensor with core callbacks.

## Control Flow

Probe allocates an IIO device, calls `cros_ec_sensors_core_init()` with capture support, selects channel type from `state->core.type`, populates scan type and sysfs masks, adds a timestamp channel, sets `read_ec_sensors_data` to `cros_ec_sensors_read_cmd`, and calls `cros_ec_sensors_core_register()`. Reads and writes take `core.cmd_lock`, prepare motion-sense host command parameters, and call the EC command helper. Light processed data is already lux from EC firmware; proximity raw data is returned directly.

## State And Persistence

State such as calibration offsets, range, sample frequency, and buffered capture state lives in the embedded EC core state and EC firmware. Writes update `core.calib`, `core.curr_range`, and `core.range_updated` after successful host commands. There is no local hardware register cache.

## Dependencies And Integration Points

The driver depends on ChromeOS EC protocol definitions, `cros_ec_sensors_core`, platform devices named `cros-ec-light` or `cros-ec-prox`, IIO triggered buffers through the core, and `cros_ec_sensors_pm_ops`. It is not a physical bus driver; it binds to EC-created platform devices.

## Risks And Test Signals

Channel count is fixed to one data channel plus timestamp even if EC firmware internally merges multiple sensors. Calibration bias code stores only `calib[0].offset` but reads `calib[idx].offset`, which is fine for one data channel but fragile if expanded. Tests should use EC emulation or hardware to verify processed light, raw proximity, calibration bias/scale host commands, sample-frequency availability, buffered captures, and PM callbacks supplied by the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/cros_ec_light_prox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/gp2ap002.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/gp2ap002.c

## Purpose

`gp2ap002.c` drives Sharp GP2AP002A00F ambient light plus proximity sensors and GP2AP002S00F proximity-only sensors. Proximity uses a register/IRQ path; ambient light on the A00F variant uses an external ADC current channel mapped through a lookup table to lux. Runtime PM powers the sensor and regulators around reads and event usage.

## Important APIs, Types, And Functions

`struct gp2ap002` stores a custom regmap, regulators, optional `alsout` IIO current channel, near/far hysteresis settings from firmware, variant flag, IRQ number, and software event-enable flag. `gp2ap002_prox_irq()` reads proximity state, rewrites hysteresis, pushes rising/falling IIO events, and retriggers VOUT. `gp2ap002_get_lux()` reads the ADC and maps current index to `gp2ap002_illuminance_table[]`. `gp2ap002_init()` writes gain, hysteresis, cycle, operation, and VOUT registers. Event config callbacks toggle runtime PM and `enabled`. Runtime suspend/resume disable/enable IRQ and regulators and reinitialize registers.

## Control Flow

Probe reads the `compatible` property to distinguish A00F from S00F, initializes a custom regmap bus because reads use SMBus word reads with the high byte as data while writes use byte writes, reads board hysteresis properties, optionally acquires and validates `alsout` as `IIO_CURRENT`, configures and enables `vdd` and `vio`, initializes the chip, enables runtime PM, requests the IRQ, sets autosuspend, registers proximity plus optional light channels, and registers IIO. A light read resumes runtime PM, reads ADC current, clamps it to the lookup-table range, returns lux, and autosuspends. Event enable keeps runtime PM active until disabled.

## State And Persistence

Board-specific hysteresis values are persistent only as firmware properties copied into memory. `enabled` is software-only because the hardware cannot be queried for event enable state. Runtime PM state controls regulators and IRQ activation. Register state is rewritten on every runtime resume through `gp2ap002_init()`.

## Dependencies And Integration Points

The driver integrates I2C, a custom regmap bus, regulator framework, IIO consumer API, firmware properties, IRQs, runtime PM, OF matching, and IIO events. It depends on `sharp,proximity-far-hysteresis` and `sharp,proximity-close-hysteresis` properties.

## Risks And Test Signals

`pm_runtime_get_sync()` return values are ignored in raw reads and event enable. Runtime resume leaks the already-enabled VDD if VIO enable fails. The event enable flag is not protected by a mutex. Tests should cover both compatible variants, missing/invalid hysteresis properties, ADC channel type, regulator voltage programming, IRQ hysteresis switching, runtime autosuspend/resume, event enable holding power, and cleanup after each probe failure stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/gp2ap002.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/gp2ap020a00f.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/gp2ap020a00f.c

## Purpose

`gp2ap020a00f.c` is a full-featured IIO driver for the Sharp GP2AP020A00F proximity and ambient light sensor. It supports direct raw reads for clear-light lux, IR light, and proximity, a triggered buffer for all three channels, light threshold events, and proximity rate-of-change events. The file implements an explicit command and operation-mode state machine because proximity detection mode cannot coexist with ALS triggers or events.

## Important APIs, Types, And Functions

`struct gp2ap020a00f_data` holds the I2C client, mutex, scan buffer, `vled` regulator, bit flags, current opmode, IIO trigger, regmap, cached threshold values, IRQ work, and a wait queue for data-ready. Core functions include `gp2ap020a00f_set_operation_mode()`, `gp2ap020a00f_exec_cmd()`, `gp2ap020a00f_write_event_threshold()`, `gp2ap020a00f_alter_opmode()`, `wait_conversion_complete_irq()`, `gp2ap020a00f_read_output()`, `gp2ap020a00f_adjust_lux_mode()`, `gp2ap020a00f_thresh_event_handler()`, `gp2ap020a00f_prox_sensing_handler()`, `gp2ap020a00f_trigger_handler()`, event value/config callbacks, buffer postenable/predisable callbacks, and probe/remove.

## Control Flow

Probe enables the `vled` regulator, initializes regmap, bulk-writes the default register table, initializes lock and wait queue, sets current mode to shutdown, configures triggered buffer support, allocates and registers an IIO trigger, requests the IRQ for the threshold-event handler, and registers the IIO device. Direct raw reads claim direct mode, issue a read command that requires shutdown, wait for an IRQ to set `DATA_READY`, bulk-read the selected output register, shut down, and scale light channels for high-lux mode. Buffered operation enables commands per active scan channel, allocates `scan_bytes`, and uses IRQ work to poll the trigger after threshold-event IRQs. Proximity event enable switches the IRQ handler from threshold-event mode to proximity-sensing mode and requires both proximity thresholds to be nonzero.

## State And Persistence

The operation mode and feature enablement are tracked in `cur_opmode` and `flags`. Threshold values are cached in `thresh_val[]` and mirrored into hardware when events are enabled. High-lux mode is software state that changes hardware ALS range, clears thresholds during transition, and rewrites them scaled when necessary. `DATA_READY` is a transient wait-queue bit. The regulator remains enabled from probe until remove; the driver has no runtime or system PM callbacks.

## Dependencies And Integration Points

The driver uses I2C, regmap, regulator framework, IIO direct mode, events, triggers, triggered buffers, wait queues, IRQ work, threaded IRQs, unaligned helpers, and OF/I2C matching. Its IIO event ABI uses threshold events for light and rate-of-change events for proximity. The probe-time IRQ is required even for `read_raw()` because conversion completion is interrupt-driven.

## Risks And Test Signals

This file has the highest concurrency risk in the set. Freeing and requesting the same IRQ while holding the device mutex during proximity event reconfiguration must be tested against in-flight interrupts. `gp2ap020a00f_read_channel()` overwrites a read error with the shutdown result, potentially hiding a failed read. Buffer allocation happens after enabling hardware; allocation failure leaves prior trigger state to unwind through caller behavior. Tests should cover direct reads while buffers are active returning `-EBUSY`, all command conflict cases, proximity thresholds requiring nonzero values, light high-lux mode transitions and threshold scaling, IRQ handler switching, trigger buffer active scan masks, remove power-off, and regulator/probe failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/gp2ap020a00f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/hid-sensor-als.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/hid-sensor-als.c

## Purpose

`hid-sensor-als.c` is an IIO platform driver for HID sensor hub ambient light usage collections. It exposes any ALS-related HID report fields that are present: intensity, illuminance, color temperature, chromaticity X, and chromaticity Y, plus timestamp. It supports direct raw reads and buffered data pushed from HID callbacks.

## Important APIs, Types, And Functions

`struct als_state` stores HID callbacks, common HID sensor attributes, per-channel HID attribute info, dynamic IIO channel specs, a scan buffer with timestamp, scale and offset metadata, channel count, HID timestamp, and scan mask. `als_read_raw()` reads current values or common attributes. `als_write_raw()` writes sample frequency and hysteresis settings. `als_proc_event()` pushes a complete scan to IIO buffers. `als_capture_sample()` copies HID report fields into the scan buffer. `als_parse_report()` discovers supported usages and adjusts channel bit widths. Probe/remove are `hid_als_probe()` and `hid_als_remove()`.

## Control Flow

Probe retrieves the HID sensor hub device from platform data, parses common attributes, discovers ALS-specific report fields, appends a timestamp channel, installs available scan masks, sets up a HID sensor trigger, registers IIO, and registers HID callbacks. Direct raw reads power the HID sensor on, call `sensor_hub_input_attr_get_raw_value()` for the chosen usage/report ID, and power it off. Buffered capture receives individual samples in `als_capture_sample()` and pushes the assembled scan in `als_proc_event()` when the common `data_ready` flag is set.

## State And Persistence

The dynamic channel list persists for the platform device lifetime and depends on the HID report descriptor. Scale, offset, sample frequency, and hysteresis are represented by HID common attributes rather than local hardware registers. The scan buffer stores the latest captured fields until an event callback pushes them. HID timestamps are converted through `hid_sensor_convert_timestamp()`.

## Dependencies And Integration Points

The driver integrates with HID sensor hub callbacks, `hid-sensor-trigger`, IIO buffer/trigger support, platform IDs `HID-SENSOR-200041` and `HID-SENSOR-LISS-0041`, and `hid_sensor_pm_ops`. It imports the `IIO_HID` namespace.

## Risks And Test Signals

`als_capture_sample()` casts raw data to `u32` or `s64` without checking `raw_len`, relying on HID core guarantees. The same HID illuminance usage feeds both intensity and light channels. Tests should cover report descriptors with each subset of optional channels, signed logical minima, direct reads during power transitions, sample frequency and hysteresis writes, buffer pushes with HID timestamps and fallback timestamps, callback unregister on remove, and scan masks matching discovered channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/hid-sensor-als.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/hid-sensor-prox.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/hid-sensor-prox.c

## Purpose

`hid-sensor-prox.c` is an IIO platform driver for HID human presence, human proximity, and human attention sensors. It exposes discovered HID usages as proximity or attention channels, supports direct raw/processed reads, and pushes buffered samples through HID sensor callbacks.

## Important APIs, Types, And Functions

`struct prox_state` stores HID callbacks, common attributes, per-channel attribute info, channel specs, usage mapping, latest sample array, per-channel scale metadata, scan mask, and channel count. `prox_read_raw()` reads raw/processed values, scale, offset, sample frequency, and hysteresis. `prox_write_raw()` writes sample frequency and hysteresis. `prox_proc_event()` pushes captured data to IIO buffers. `prox_capture_sample()` decodes 1-, 2-, or 4-byte HID sample payloads. `prox_parse_report()` discovers the available HID fields.

## Control Flow

Probe parses common HID attributes, discovers supported proximity/attention usages, builds a compact channel array with scan indexes, sets up a HID trigger, registers the IIO device, and registers sensor hub callbacks. Direct reads power the HID sensor, fetch a raw value from the report ID and usage, multiply human-attention values by 100, and power the sensor off. Buffered samples are stored in `human_presence[]` by usage and pushed when `data_ready` is observed.

## State And Persistence

The channel-to-usage mapping and scale metadata are built once from the HID descriptor. Latest buffered samples live in `human_presence[]`; no local register cache exists. Common attributes hold sample frequency and hysteresis. Offset is always reported as zero.

## Dependencies And Integration Points

The driver depends on HID sensor hub, HID sensor trigger helpers, IIO buffers, platform IDs `HID-SENSOR-200011` and `HID-SENSOR-LISS-0226`, and `hid_sensor_pm_ops`. It imports `IIO_HID`.

## Risks And Test Signals

There is no timestamp channel, so buffer consumers receive only channel samples. `prox_proc_event()` passes `&prox_state->human_presence`, which is an array object pointer; this resolves to the same address but should be kept in mind if refactored. Tests should cover each usage independently, mixed descriptors, attention scaling by 100 in both direct and buffered paths, raw lengths 1/2/4, unsupported raw lengths, sample frequency/hysteresis writes, callback registration failure unwind, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/hid-sensor-prox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/iqs621-als.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/iqs621-als.c

## Purpose

`iqs621-als.c` is an IIO child driver for Azoteq IQS621 and IQS622 ambient light/proximity functions exposed by the IQS62x MFD core. IQS621 exposes ALS range and light threshold events; IQS622 exposes visible/IR intensity plus proximity threshold events. The driver uses the parent regmap and notifier chain.

## Important APIs, Types, And Functions

`struct iqs621_als_private` stores the parent `iqs62x_core`, IIO device, notifier block, mutex, event enable booleans, cached flags, selected IR flag mask, and cached thresholds. `iqs621_als_init()` rewrites thresholds and unmasks parent events after reset. `iqs621_als_notifier()` handles parent events and pushes IIO events. Raw/event callbacks are `iqs621_als_read_raw()`, `iqs621_als_read_event_config()`, `iqs621_als_write_event_config()`, `iqs621_als_read_event_value()`, and `iqs621_als_write_event_value()`. Probe selects channel tables based on product number and registers the notifier.

## Control Flow

Probe gets `iqs62x_core` from the parent device, allocates IIO state, reads initial thresholds, selects IQS621 or IQS622 channel definitions, initializes the mutex, registers a blocking notifier with the parent, arranges devm notifier cleanup, and registers IIO. Event-enable writes read current flags first, update the global event mask in the parent register, and cache enable booleans. Parent notifications compare new and old light/range/proximity flags, emit rising or falling IIO events, update cached flags, and reinitialize thresholds/masks after system reset events.

## State And Persistence

Threshold values are cached in driver state and written to the parent regmap. Event enable state is kept as booleans; parent event mask bits are the hardware-facing state. `als_flags` and `ir_flags` cache previous notifier state to detect transitions. After a parent reset, `iqs621_als_init()` restores thresholds and unmasks enabled events.

## Dependencies And Integration Points

The driver depends on the IQS62x MFD core, parent regmap, parent notifier chain, IIO events, and platform device alias `iqs621-als`. It has no direct bus binding; the MFD creates the platform child.

## Risks And Test Signals

The proximity event threshold selection changes `ir_flags_mask` based on value range, so switching between touch and prox thresholds should be tested with enabled events. Parent reset handling must restore all cached thresholds and event masks. Tests should cover IQS621 and IQS622 channel layouts, raw reads from flags/UI output registers, event enable combinations for light and range sharing the ALS mask, proximity enable on IQS622, threshold read/write scaling, notifier transition detection, and unregister failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/iqs621-als.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/isl29018.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/isl29018.c

## Purpose

`isl29018.c` drives Intersil ISL29018, ISL29023, and ISL29035 ambient light sensors, with optional IR and proximity channels depending on variant. It exposes processed illuminance, raw IR, raw proximity for ISL29018, calibration scale, illuminance scale, integration time, and a custom proximity ambient-IR suppression sysfs attribute.

## Important APIs, Types, And Functions

`struct isl29018_chip` contains regmap, mutex, variant type, calibration scale, integration-time index, active scale, proximity scheme, suspend flag, and VCC regulator. Core routines include `isl29018_set_integration_time()`, `isl29018_set_scale()`, `isl29018_read_sensor_input()`, `isl29018_read_lux()`, `isl29018_read_ir()`, `isl29018_read_proximity_ir()`, raw read/write callbacks, sysfs availability callbacks, `isl29018_chip_init()`, probe, suspend, and resume. `isl29018_chip_info_tbl[]` maps variants to channel tables, info structs, and regmap configs.

## Control Flow

Probe determines variant from I2C or ACPI data, initializes default calibration, integration time, and scale, enables VCC, sets a cleanup action, initializes regmap, runs chip init, and registers IIO. Chip init optionally validates ISL29035 device ID and clears brownout, clears TEST and COMMAND1 registers per the application note, waits, then writes default scale and integration time. Reads lock the mutex, reject if suspended, issue one-shot ALS/IR/prox commands, wait 100 ms, read data LSB/MSB, and convert as needed. Proximity scheme 0 subtracts ambient IR in software, while scheme 1 returns on-chip ambient-rejected data.

## State And Persistence

Scale, integration-time index, calibration scale, and proximity scheme are cached in memory and mirrored into command registers where applicable. Suspend sets `suspended = true` and disables VCC; resume reenables VCC, reinitializes registers from cached state, and clears `suspended`. No runtime PM or interrupts are used.

## Dependencies And Integration Points

The driver uses I2C, regmap with volatile register configuration, regulator framework, IIO sysfs attributes, OF and ACPI matching, and simple sleep PM. Variant-specific channels hide proximity for ISL29023/ISL29035.

## Risks And Test Signals

Lux conversion multiplies count by scale and calibration using integer arithmetic; high values can overflow ordinary `int` depending on count and scale. Reads hold the mutex across `msleep(100)`, serializing all sysfs operations. Tests should cover all three variants, ISL29035 ID and brownout clearing, scale/integration-time table transitions, calibration scale, proximity scheme attribute, suspend read/write returning `-EBUSY`, resume restoring settings, and regulator cleanup on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/isl29018.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/isl29028.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/isl29028.c

## Purpose

`isl29028.c` drives ISL29028 and ISL29030 concurrent ambient light and proximity sensors. It exposes processed ALS lux, raw IR intensity, raw proximity, ALS scale selection, and proximity sampling frequency. Runtime PM autosuspends the device by clearing the configure register when idle.

## Important APIs, Types, And Functions

`struct isl29028_chip` stores a mutex, regmap, proximity sampling frequency, proximity enable state, lux scale, and ALS/IR mode. `isl29028_find_prox_sleep_index()`, `isl29028_set_proxim_sampling()`, `isl29028_enable_proximity()`, `isl29028_set_als_scale()`, `isl29028_set_als_ir_mode()`, `isl29028_read_als_ir()`, `isl29028_read_proxim()`, `isl29028_als_get()`, `isl29028_ir_get()`, raw read/write callbacks, `isl29028_clear_configure_reg()`, probe/remove, and runtime PM callbacks are the main routines.

## Control Flow

Probe initializes regmap, default proximity frequency `20 Hz`, lux scale `2000`, clears test registers, clears the configure register, sets up IIO, enables runtime PM with two-second autosuspend, and registers the device. Reads and writes call `pm_runtime_resume_and_get()`, lock the mutex, perform the requested operation, unlock, and autosuspend on success. ALS/IR reads switch mode as needed, enable conversion, wait 100 ms, and read the two ALSIR bytes. Proximity reads lazily enable proximity and wait for the first sample based on the configured sampling period.

## State And Persistence

`enable_prox` and `als_ir_mode` are caches that avoid redundant hardware setup. `lux_scale` and proximity sample frequency are software caches mirrored to `CONFIGURE`. Suspend and remove call `isl29028_clear_configure_reg()`, which disables ALS/proximity and resets those caches; resume relies on the next read to re-enable the needed function.

## Dependencies And Integration Points

The driver uses I2C regmap with maple cache, IIO sysfs const attributes, runtime PM, and OF/I2C matching for `isil,isl29028` and `isil,isl29030` plus a backward-compatible `isl,isl29028`.

## Risks And Test Signals

In `isl29028_write_raw()`, the autosuspend put is skipped when an operation returns an error after PM resume, which can leak a runtime PM reference. Raw read has a similar early return before the PM put on operation error. Tests should specifically cover invalid write masks and values after runtime resume. Also test all proximity sampling frequencies, ALS scale values 125 and 2000, mode transitions between ALS and IR, autosuspend clearing configure state, remove cleanup, and regmap error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/isl29028.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/isl29125.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/isl29125.c

## Purpose

`isl29125.c` drives the Intersil ISL29125 RGB light sensor. It exposes red, green, and blue intensity channels with raw reads, shared scale selection, and a triggered buffer. The driver switches `CONF1` between single-color modes, RGB mode, and power-down mode as direct reads, buffered operation, suspend, and remove require.

## Important APIs, Types, And Functions

`struct isl29125_data` stores the I2C client and cached `conf1` register value. `isl29125_channels[]` declares three 16-bit modified intensity channels plus timestamp. `isl29125_read_data()` selects the color mode, waits for conversion readiness, reads the selected data word, and restores `conf1`. `isl29125_read_raw()` handles direct raw and scale. `isl29125_write_raw()` changes the sensing range bit in `conf1`. `isl29125_trigger_handler()` collects active channels into a timestamped scan. Buffer setup callbacks switch RGB mode on and return to power-down. Probe/remove/suspend/resume handle lifecycle.

## Control Flow

Probe allocates IIO state, reads and validates the device ID `0x7d`, initializes `conf1` to power-down plus high sensing range, clears status, sets up a triggered buffer, and registers IIO. Direct raw reads claim direct mode, call `isl29125_read_data()`, and release direct mode. Scale writes accept only the two advertised micro-scale values and set or clear `ISL29125_MODE_RANGE`. The trigger handler iterates active channels, reads each color's data register without changing mode, places samples in scan order, pushes a timestamped buffer, and notifies trigger completion. Buffer postenable enables RGB conversion mode; predisable powers down.

## State And Persistence

The cached `conf1` byte is the driver's only local state. It preserves the selected sensing range and current mode bits across sysfs writes, buffer enable/disable, suspend, and resume. There is no mutex, regulator, or regmap cache. Remove unregisters IIO, cleans up the triggered buffer, and powers the sensor down. Suspend powers down; resume writes the cached `conf1`.

## Dependencies And Integration Points

The driver uses I2C SMBus operations, IIO direct mode, triggered buffers, trigger consumers, and simple PM. It matches the `isl29125` I2C ID. It does not use regmap or OF matching in this file.

## Risks And Test Signals

Direct reads and triggered buffer reads share the same `CONF1` mode register, so direct-mode claiming is important to test. The trigger handler assumes RGB mode has already been enabled by buffer setup; direct register reads outside RGB mode would not be equivalent. Failed channel reads skip the push but still complete the trigger. Tests should cover raw reads for all colors, both scale values from `scale_available`, invalid scale writes, buffer enable/disable mode sequencing, active scan masks, suspend/resume during idle and buffer use, remove cleanup, and I2C read/write errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/isl29125.c -->
