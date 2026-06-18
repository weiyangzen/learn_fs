# subset-b-003828 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm75.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm75.c

## Purpose

`lm75.c` is the Linux hwmon driver for LM75-compatible digital temperature sensors and many register-compatible variants from Analog Devices, AMS, Atmel, Dallas/Maxim, GMT, Microchip, NXP, ST, and TI. It exposes a single temperature channel with input, max, hysteresis, optional alarm, optional label, and chip update interval. Unlike the older sysfs-only hwmon drivers in this group, it uses the hwmon `*_with_info` API and a regmap abstraction so the same core can serve I2C and I3C devices.

## Important APIs, Types, and Functions

`enum lm75_type` is the variant selector shared by I2C IDs, OF match data, and the I3C P3T1755 table. `struct lm75_params` describes per-chip configuration: config register width, set/clear masks, default resolution, limit-register resolution, supported sample times, resolution-per-sample-time mapping, and alarm support. `struct lm75_data` stores the label, regmap, original configuration, active resolution/sample time, chip kind, params, and I3C transfer buffers. The key operations are `lm75_generic_probe()`, `lm75_read()`, `lm75_write_temp()`, `lm75_update_interval()`, custom I2C/I3C regmap bus callbacks, `lm75_detect()`, and PM suspend/resume hooks.

## Control Flow

I2C probe checks SMBus byte and word support, creates a regmap with custom callbacks, and calls `lm75_generic_probe()`. I3C probe creates the matching I3C regmap and passes the I3C ID data to the same generic probe. Generic probe allocates state, records optional firmware label, enables the `vs` regulator, selects device parameters, reads and saves the original config, writes the requested runtime config, installs `lm75_remove()` as a managed cleanup action, registers the hwmon device, and optionally wires an IRQ to `lm75_alarm_handler()` for variants with alarm support. Runtime reads choose the register from the hwmon attribute and use regmap reads; writes clamp and encode limits or update conversion interval/config fields.

## State and Persistence Behavior

The driver caches only driver metadata and policy state: `orig_conf`, `sample_time`, `resolution`, params, and label. Temperature and limit registers are read through regmap; the regmap uses `REGCACHE_MAPLE` but marks temperature and config volatile. On removal or failed managed setup after config change, `lm75_remove()` restores the original config register. Suspend sets `LM75_SHUTDOWN`; resume clears it. There is no file-backed persistence, but the physical chip's threshold and config registers are modified while the driver is bound.

## Dependencies and Integration Points

The file integrates Linux I2C, I3C, regmap, hwmon info API, firmware properties, optional regulator supply `vs`, interrupts, and PM. It depends on `lm75.h` for common min/max and shutdown definitions. Detection is available for legacy I2C class probing and intentionally recognizes only original National LM75/LM75A-style devices because many clones lack strong IDs.

## Risks and Test Signals

Risks include weak legacy detection, per-variant config bit mistakes, endian differences between config and temperature registers, I3C buffer reuse assumptions, and alarm semantics limited to AS6200/TMP112-style status bits. Useful tests cover every ID/match-table mapping, 8/16-bit config register access, limit encoding at clamp boundaries, update interval selection, PCT2075 idle-period writes, regmap cache behavior, IRQ notification, regulator failure, restore-on-remove, and suspend/resume shutdown transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm75.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm75.h -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm75.h

## Purpose

`lm75.h` provides small common helpers for drivers that need classic LM75-format temperature conversion. It defines the supported milli-Celsius range, the shutdown configuration bit, and inline conversions between hwmon milli-Celsius values and the original LM75 two's-complement 0.5-degree register format.

## Important APIs, Types, and Functions

The header exports `LM75_TEMP_MIN`, `LM75_TEMP_MAX`, and `LM75_SHUTDOWN`. `LM75_TEMP_TO_REG(long temp)` clamps input to -55000..125000 milli-Celsius, rounds to nearest 0.5 C with sign-aware offsetting, and returns the encoded value shifted into the LM75 register position. `LM75_TEMP_FROM_REG(u16 reg)` casts to signed 16-bit, divides by 128 using integer division to preserve signed behavior, and returns milli-Celsius in 500 mC increments.

## Control Flow

There is no executable control path beyond inline conversion. Callers include the header, pass user or register values through these helpers, and perform their own bus I/O. The helpers deliberately avoid any device state or locking.

## State and Persistence Behavior

The header holds no state. Its constants encode hardware limits and a config bit used by LM75-like devices. The conversion routines are deterministic and have no side effects.

## Dependencies and Integration Points

It depends only on kernel `minmax.h` for `clamp_val()` and `types.h` for fixed-width integer types. It is included by `lm75.c`; older or adjacent hwmon drivers can also include it when they emulate the same register format.

## Risks and Test Signals

The main risk is applying these helpers to variants with different resolution or register layout. They are correct for classic 0.5 C LM75 encoding, not for the higher-resolution paths handled locally in `lm75.c`. Test signals are boundary conversions at -55000, 125000, zero, negative half-step rounding, positive half-step rounding, and sign preservation in `LM75_TEMP_FROM_REG()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm75.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm77.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm77.c

## Purpose

`lm77.c` drives National Semiconductor LM77 temperature sensors and thermal window comparators over I2C. It exposes the local temperature, min/max/critical thresholds, hysteresis values, and three temperature alarm bits through legacy hwmon sysfs attribute groups.

## Important APIs, Types, and Functions

`enum temp_index` maps cached temperature slots for input, critical, min, max, and hysteresis. `temp_regs[]` maps those logical slots to chip registers. `struct lm77_data` stores the I2C client, `update_lock`, cache validity timestamp, decoded temperatures in milli-Celsius, and cached alarm bits. `lm77_read_value()` and `lm77_write_value()` hide the chip's mixed byte/word register access. `lm77_update_device()` refreshes the cache every 1.5 seconds. Sysfs callbacks include `temp_show()`, `temp_store()`, `temp_hyst_show()`, `temp_hyst_store()`, and `alarm_show()`. Probe initializes the chip and registers `lm77_groups`.

## Control Flow

Detection first verifies SMBus byte and word support. Because the chip has no ID register, `lm77_detect()` validates address cycling, sign-bit patterns, unused config bits, and undefined registers 0x06/0x07 returning the last read value. Probe allocates state, initializes the mutex, clears shutdown mode via `lm77_init_client()`, and registers the hwmon sysfs group. At runtime, read callbacks call `lm77_update_device()`, which locks, refreshes all temperature registers and alarm bits when stale, and then serves cached values. Store callbacks parse user input, clamp to chip range, encode to register units, update the local cache, and write the hardware register while holding `update_lock`.

## State and Persistence Behavior

The driver maintains a volatile per-client cache with a 1.5-second lifetime. Threshold writes immediately change chip registers and mirror the new value into the cache. Hysteresis is represented by the device as a relative value but exposed as derived absolute hysteresis points, so `temp_hyst_store()` computes the relative register value from the current critical threshold. No original configuration is restored on remove; probe only clears shutdown if needed.

## Dependencies and Integration Points

The driver integrates I2C class probing, SMBus byte/word operations, hwmon sysfs helpers, managed allocation, and kernel mutex/jiffies cache timing. It is a legacy sysfs-style hwmon driver rather than a `hwmon_chip_info` implementation.

## Risks and Test Signals

Risks include false positives from heuristic detection, lack of read-error propagation in cache refresh, stale threshold assumptions when computing hysteresis, and no restore of shutdown state. Useful tests include detection rejection for invalid cycling/config/sign bits, shutdown clearing, all temperature clamp and conversion boundaries, hysteresis math for min/max/critical paths, alarm bit mapping from low three temperature register status bits, and concurrent sysfs reads/writes under `update_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm77.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm78.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm78.c

## Purpose

`lm78.c` supports LM78 and LM79 hardware monitoring chips over either I2C or ISA. It exposes seven voltage inputs with limits, one temperature channel with limits, three fan tachometers with minimums/divisors, VID/VRM-derived CPU voltage, and alarm bits. The file also contains ISA discovery/registration code and duplicate-interface suppression so a single physical chip is not bound through both ISA and I2C.

## Important APIs, Types, and Functions

`enum chips` distinguishes LM78 and LM79 behavior. `struct lm78_data` stores the optional I2C client, ISA address/name, per-device ISA lock, update cache, voltage/fan/temp/VID/alarm registers, and chip type. Conversion helpers encode voltage, fan, temperature, and fan divisor values. The main shared bus operations are `lm78_read_value()` and `lm78_write_value()`, which dispatch to SMBus or ISA port I/O. Important control functions are `lm78_i2c_detect()`, `lm78_alias_detect()`, `lm78_i2c_probe()`, `lm78_init_device()`, `lm78_update_device()`, `lm78_isa_found()`, `lm78_isa_device_add()`, and module init/exit.

## Control Flow

Module init registers ISA first, then I2C. ISA probing manually requests each I/O port in the 8-byte window, checks aliasing behavior and address-register semantics, rejects known Winbond/ITE lookalikes, reads chip ID, then creates a platform device. I2C detection checks config/address registers, rejects Winbond IDs, identifies LM78/LM79, and calls `lm78_alias_detect()` while holding the ISA cache lock if an ISA instance exists. Probe for either bus allocates state, initializes/start monitoring, and registers the same hwmon attribute group. Runtime sysfs reads call `lm78_update_device()`, which refreshes the cache every 1.5 seconds. Writes update cached values and hardware registers under `update_lock`; fan divisor writes preserve the displayed fan minimum by converting it through the old and new divisors.

## State and Persistence Behavior

Per-device state is volatile but mirrors hardware limit registers. The cache has a 1.5-second lifetime. `lm78_init_device()` starts monitoring and seeds fan minimum values. ISA state uses a global `pdev` and `isa_address` because only one ISA instance is supported. There is no managed restoration of original chip config; writes to limits, divisors, and monitoring start persist in the physical chip until changed.

## Dependencies and Integration Points

The file integrates I2C, optional ISA platform devices and port I/O, hwmon sysfs groups, hwmon VID conversion, module init ordering, mutexes, and jiffies. Conditional `CONFIG_ISA` blocks provide no-op alternatives when ISA support is absent.

## Risks and Test Signals

Risks include ISA probing side effects, global single-ISA assumptions, heuristic I2C detection, silent SMBus/port read failures becoming cached byte values, and duplicate binding if alias detection misses a device. Tests should exercise I2C-only, ISA-only, and combined systems; known false-positive rejection; LM79 VID bit handling; fan divisor preservation; fan3 fixed divisor behavior; module init unwind paths; and sysfs conversion/clamping for voltage, fan, and temperature attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm78.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm80.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm80.c

## Purpose

`lm80.c` drives LM80 and LM96080 I2C hardware monitor chips. It exposes seven voltage channels with min/max limits, two fans with minimums and divisors, one temperature channel with hot/OS thresholds and hysteresis, and combined/per-channel alarms through legacy hwmon sysfs attributes.

## Important APIs, Types, and Functions

`enum temp_index`, `enum in_index`, and `enum fan_index` define two-dimensional cache indexes for temperature, voltage, and fan data. `struct lm80_data` stores the I2C client, update mutex, error flag, cache timestamp, voltage/fan/temp registers, fan divisors, and alarm bits. `lm80_init_client()` resets most chip state, selects 11-bit temperature resolution, and starts monitoring. `lm80_update_device()` refreshes the cache every two seconds and returns `ERR_PTR()` on read failure. Sysfs callbacks handle voltage, fan, fan divisor, temperature, and alarm attributes. `lm80_detect()` distinguishes LM96080 by manufacturer/device IDs and LM80 by 6-bit address mirroring.

## Control Flow

Probe allocates state, initializes the mutex, resets/starts the chip, reads fan minimums, and registers the hwmon group. On each sysfs read, `lm80_update_device()` reinitializes the client first if the previous update failed, then reads all voltage input/limits, fan input/minimums, temperature MSB plus resolution register low bits, temperature thresholds, fan divisors, and alarms. If any read returns an error, it marks the cache invalid, sets `error`, and propagates the negative status through `ERR_PTR()`. Store callbacks parse input, clamp/encode to register units, update the cache, and write the relevant register while holding `update_lock`. Fan divisor writes preserve fan minimum RPM across divisor changes.

## State and Persistence Behavior

The cache is valid for two seconds. The `error` flag triggers a chip reinitialization on the next update, making read failures more intrusive than in many older hwmon drivers. Probe reset intentionally changes device configuration except watchdog values and last conversion values. Limit, fan divisor, and threshold writes persist in device registers.

## Dependencies and Integration Points

The driver uses I2C SMBus byte operations, hwmon sysfs helpers including two-index sensor attributes, managed hwmon registration, mutexes, and jiffies. Detection is class-based at 0x28-0x2f. It does not use regmap or the newer hwmon info API.

## Risks and Test Signals

Risks include destructive reset-on-probe/read-error behavior, false positives from LM80 address mirroring, partial update failure leaving stale user-visible cache, and fan divisor/minimum edge cases around zero/255 tach values. Tests should cover LM96080 ID detection and conversion-rate unused-bit rejection, LM80 mirroring detection, every abort path in `lm80_update_device()`, automatic reinitialization after errors, 11-bit temperature composition from temp/resolution registers, and sysfs conversions for voltage, fan RPM/divisors, thresholds, and alarm bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm80.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm83.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm83.c

## Purpose

`lm83.c` is a regmap-backed hwmon driver for National LM83 and LM82 temperature sensors. LM83 reports local plus three remote temperatures; LM82 is a reduced variant with one external channel modeled as channel 2. The driver exposes temperature inputs, max limits, a shared critical limit, alarm/fault bits, and combined chip alarms through the hwmon info API.

## Important APIs, Types, and Functions

`enum chips` selects LM83 versus LM82 visibility. Register arrays map channel indexes to temperature, max, status, alarm, critical, and fault bits. `struct lm83_data` stores the regmap and chip type. Custom regmap callbacks `lm83_regmap_reg_read()` and `lm83_regmap_reg_write()` perform SMBus byte I/O; writes remap readable register addresses to the chip's separate write addresses so regmap caching remains coherent. `lm83_temp_read()`, `lm83_temp_write()`, `lm83_chip_read()`, `lm83_is_visible()`, and the `lm83_hwmon_ops` implement hwmon behavior.

## Control Flow

Detection validates SMBus byte support, rejects impossible status/config bits, verifies National manufacturer ID, and maps chip ID 0x03 to LM83 and 0x01 to LM82. Probe allocates state, initializes regmap with maple cache and volatile status/input registers, records match data, and registers the hwmon info device. Runtime reads go directly through regmap: inputs and limits are signed 8-bit Celsius values scaled to milli-Celsius; alarms read the appropriate status register and bit; chip alarms combine the two status bytes. Writes clamp milli-Celsius to signed byte range and write either a per-channel max limit or the shared critical register.

## State and Persistence Behavior

There is no explicit polling cache in driver state. Regmap caches nonvolatile configuration/limit registers and treats current temperatures and status registers as volatile. Threshold writes modify chip registers and regmap state. The driver does not start/stop monitoring or restore previous limits.

## Dependencies and Integration Points

The file integrates I2C, regmap custom register I/O, hwmon info API, managed allocation/registration, and class detection over the LM83 address set. Its visibility function is an important integration point because the static channel-info table describes four channels while LM82 hides channels 1 and 3.

## Risks and Test Signals

Risks include LM82 revision 0x03 being indistinguishable from LM83 and therefore intentionally reported as LM83, mistakes in read-to-write address remapping, and channel visibility bugs for the reduced LM82. Tests should verify volatile/cache behavior, write-address translations for config/high/TCRIT registers, signed temperature conversion boundaries, LM82 hidden-channel sysfs absence, channel-specific alarm/fault bit mapping, and detection rejection for invalid status/config/manufacturer/chip IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm83.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm85.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm85.c

## Purpose

`lm85.c` supports a family of multi-sensor fan-control chips: LM85/LM96000, ADM1027, ADT7463/ADT7468, and SMSC EMC6D100/102/103 variants. It exposes voltage inputs, temperatures, fan tachometers, PWM outputs, automatic fan-control zones, VID/VRM, and alarms through legacy hwmon sysfs groups, with groups selected dynamically by chip capability.

## Important APIs, Types, and Functions

`enum chips` identifies chip families. Conversion tables and helpers handle voltage scaling, extended ADC bits, fan tachometer periods, temperature offsets, PWM frequency maps, auto-zone range maps, zone selectors, and hysteresis. `struct lm85_zone` and `struct lm85_autofan` model automatic fan-control state. `struct lm85_data` stores the I2C client, selected attribute groups, frequency map, chip type, optional VID5 mode, update cache timestamps, sensor registers, extended ADC nibbles, VID/VRM, alarms, ADT7468 config, autofan config, and zone config. Central functions include `lm85_read_value()`, `lm85_write_value()`, `lm85_update_device()`, many sysfs show/store callbacks, `lm85_init_client()`, `lm85_is_fake()`, `lm85_detect()`, and `lm85_probe()`.

## Control Flow

Detection reads company/verstep IDs, maps National/Analog/SMSC variants, and rejects Winbond WPCD377I devices that emulate LM96000 IDs but return all-zero/all-0xff monitoring values. Probe allocates data, selects a PWM frequency map, initializes VRM, starts monitoring if needed, warns about locked/not-ready config bits, builds the attribute-group list, detects ADT7463/68 VID5 mode, and registers hwmon. Runtime reads call `lm85_update_device()`, which has two refresh horizons: fast readings every 1.5 seconds and configuration every 60 seconds. Fast refresh reads extended ADC bits in the required chip-specific order, live voltages/fans/temperatures/PWMs/alarms, ADT7468 config, and SMSC extra channels. Slow refresh reads voltage/fan/temp limits and automatic fan-control configuration. Store callbacks update cached fields and write hardware while holding `update_lock`.

## State and Persistence Behavior

The driver has a substantial volatile cache split between fast readings and slow configuration. Sysfs writes immediately update the hardware and the matching cache field. Automatic fan-control state persists in chip registers; the driver preserves user intent for `zone.max_desired` so changing a zone minimum can recompute range without cumulative drift. There is no restore-on-remove. ADT7468 has special state interpretation for 64-degree offset mode and global high-frequency PWM mode.

## Dependencies and Integration Points

The driver uses I2C SMBus byte operations, hwmon sysfs attributes, hwmon VID helpers, OF match data, jiffies/mutexes, and dynamic attribute groups. It integrates multiple chip-specific register layouts without regmap, including word-like two-byte fan registers read/written as adjacent byte operations.

## Risks and Test Signals

Risks include silent I2C read/write failures because many accessors ignore negative statuses, complex per-chip extended-bit ordering, ADT7468 offset and high-frequency PWM side effects, dynamic group omissions, and automatic fan-control register coupling. Tests should cover each chip ID mapping, fake LM96000 rejection, update intervals, ADM/EMC extended ADC decoding, EMC6D100 extra voltages/alarms, VID5 hiding of in4, EMC6D103S omission of minctl/temp_off groups, PWM enable/zone/frequency conversions, temperature offset mode, and range recomputation when auto temp min/max are written.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm85.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm87.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm87.c

## Purpose

`lm87.c` drives National LM87 and Analog ADM1024 monitoring chips. It exposes a pin-mux-dependent set of voltages, temperatures, fan tachometers, VID/VRM, alarms, and an analog output. The driver assumes firmware or platform data configured the channel mode, but device tree and platform data can override mux choices.

## Important APIs, Types, and Functions

Channel-mode bits `CHAN_NO_FAN()`, `CHAN_TEMP3`, `CHAN_VCC_5V`, and `CHAN_NO_VID` determine which sysfs groups exist. `struct lm87_data` stores update cache, original config, channel mode, voltage scaling, temperature/fan/voltage/analog-output registers, alarm/VID/VRM state, and dynamic attribute groups. `lm87_update_device()` refreshes all visible channel data every second. Store/show callbacks cover voltage limits, temperature limits/criticals, fan minimum/divisor, alarms, VID/VRM, and `aout_output`. `lm87_detect()`, `lm87_init_client()`, `lm87_restore_config()`, and `lm87_probe()` implement detection, channel setup, config preservation, and registration.

## Control Flow

Detection checks SMBus byte support, rejects config bit 7, then identifies LM87 by National company/revision range or ADM1024 by Analog company/revision pattern. Probe allocates state, stores it in client data, initializes the mutex, then calls `lm87_init_client()`. Initialization reads channel mode or builds it from DT properties (`has-temp3`, `has-in6`, `has-in7`) and optional `vcc` regulator voltage, writes the channel register when firmware data requests it, saves original config, registers a managed restore action, initializes limit registers if monitoring was not running, and starts monitoring. Probe then fills voltage scale factors and appends attribute groups according to mux state before registering hwmon with the I2C client as drvdata.

## State and Persistence Behavior

The cache is valid for one second. The original config register is restored on driver detach through `devm_add_action()`, but channel-mode writes and limit initialization are not fully restored. Voltage scale for in2 depends on whether VCC is treated as 5 V. Fan divisor writes preserve the displayed fan minimum by converting through the old divisor and restoring the equivalent threshold after updating divisor bits. The analog output register is user-writable and cached.

## Dependencies and Integration Points

The driver integrates I2C SMBus byte operations, hwmon sysfs groups, hwmon VID helpers, optional regulator lookup, OF properties, platform data, managed cleanup, mutexes, and jiffies. Dynamic sysfs group construction is central because fan1/fan2 may instead be in6/in7, temp3 may replace in0/in5, and VID may be disabled.

## Risks and Test Signals

Risks include changing channel mode from firmware descriptions, incomplete restoration of channel/limit side effects, read-error values flowing into unsigned caches, and mux-dependent alarm naming where temp3 shares alarm/critical behavior with external temperature paths. Tests should cover DT and platform-data channel selection, optional 5 V scale detection, all dynamic group combinations, config restore on probe failure/remove, first-start limit initialization, fan divisor preservation, analog output clamp/rounding, VID group suppression, and LM87/ADM1024 detection rejection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm87.c -->
