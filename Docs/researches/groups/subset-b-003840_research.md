# Research: subset-b-003840

This grouped report covers five Winbond/Nuvoton hwmon drivers under `sources/distributed-fs/ceph-client/drivers/hwmon/`. Each section is source-tree aligned and wrapped for reconciliation into its per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83627hf.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/w83627hf.c

## Purpose

`w83627hf.c` is a legacy Linux hwmon driver for Winbond/Nuvoton Super-I/O monitoring devices in the W83627 family: W83627HF, W83627THF, W83697HF, W83637HF, and W83687THF. It exposes voltage inputs, fan tachometers, fan divisors, temperature channels, beep/alarm controls, PWM controls, VID/VRM reporting, and chip-specific optional channels through sysfs and `hwmon_device_register()`. Unlike pure I2C hwmon drivers, this one discovers a Super-I/O logical device, creates a platform device over an ISA I/O port region, and performs direct port I/O against the hardware monitor register/data window.

## Important APIs, Types, and Functions

The driver is organized around `struct w83627hf_data`, which stores the platform I/O base, chip type/name, hwmon device pointer, low-level register lock, update cache lock, cache validity timestamp, cached sensor registers, alarm/beep masks, PWM state, sensor type configuration, VID/VRM state, and suspend-only saved registers. `struct w83627hf_sio_data` carries Super-I/O address and chip type from discovery to probe.

The low-level register helpers are `superio_enter()`, `superio_exit()`, `superio_select()`, `superio_inb()`, and `superio_outb()` for configuration space, plus `w83627hf_read_value()` and `w83627hf_write_value()` for runtime monitoring registers. Banked registers are handled by `w83627hf_set_bank()` and `w83627hf_reset_bank()`, with word-sized LM75-style temperature accesses for banked temperature registers.

Core lifecycle functions are `w83627hf_find()`, `w83627hf_device_add()`, `sensors_w83627hf_init()`, `w83627hf_probe()`, `w83627hf_remove()`, and `sensors_w83627hf_exit()`. Runtime refresh is centralized in `w83627hf_update_device()`. Initialization and resume behavior live in `w83627hf_init_device()`, `w83627hf_suspend()`, and `w83627hf_resume()`. Sysfs handlers are implemented with `DEVICE_ATTR_*` and `SENSOR_DEVICE_ATTR_*` helpers for voltages, fans, temperatures, beeps, alarms, PWM duty/frequency, PWM enable mode, VID, and VRM.

## Control Flow

Module initialization probes Super-I/O ports `0x2e` and `0x4e`. `w83627hf_find()` enters Super-I/O configuration mode, reads or overrides the device ID via `force_id`, selects the hardware monitor logical device, reads and aligns the base address, enables the logical device when needed, and records the detected chip type. `sensors_w83627hf_init()` then registers the platform driver and creates a single platform device with an I/O resource at `base + WINB_REGION_OFFSET`.

`w83627hf_probe()` reserves the I/O resource, allocates `w83627hf_data`, initializes locks, calls `w83627hf_init_device()`, primes fan minima/divisors, creates the common sysfs group, conditionally adds chip-specific attributes, and finally registers the hwmon device. Optional attributes depend heavily on chip type: missing VINs are hidden, fan3/temp3 are absent on W83697HF, PWM3 and PWM frequency support vary, and VID/VRM files are only created when a valid VID path exists.

Every read-style sysfs callback calls `w83627hf_update_device()` unless it reports driver-internal state such as `vrm`. The update path refreshes at most once every 1.5 seconds, reads voltage limits, fan counts and minima, PWM values and frequencies, PWM enable modes, temperatures and limits, fan divisors, alarms, and beep masks into the cache, and marks the cache valid. Store callbacks parse sysfs input, clamp/convert units, update the cache under `update_lock`, and write affected hardware registers.

## State and Persistence Behavior

State is mostly volatile hardware register state mirrored in `w83627hf_data`. The cache is protected by `update_lock`; individual port transactions and bank switches are protected by `lock`. Limit writes, fan divisor changes, PWM changes, beep masks, temperature sensor type changes, and VRM values update the in-memory copy immediately. The driver preserves user-facing fan minimum RPM across divisor changes by converting the old register count back to RPM, changing the divisor bits, and writing a new fan-min register value.

Initialization may modify hardware. For W83627HF, it rewrites I2C subclient/address registers to reduce conflicts. If `init` is true, temp2/temp3 channels are enabled when disabled, monitoring is started, and VBAT monitoring is enabled. VID is read once at startup through chip-specific mechanisms, including GPIO5 for W83627THF and Super-I/O VID registers for W83687THF. With power management enabled, suspend caches SCFG1/SCFG2 and current limits; resume restores limits, fan minima, temperature limits, VRM/OVT configuration, and sensor configuration, then invalidates the cache.

## Dependencies and Integration Points

The driver depends on platform device infrastructure, ISA port I/O (`inb_p`, `outb_p`), ACPI resource conflict checks, hwmon sysfs conventions, `hwmon-vid` helpers, jiffies-based cache expiry, mutexes, and optional PM callbacks. It integrates through module parameters `force_i2c`, `init`, and `force_id`, the hwmon sysfs ABI, platform resources, and Super-I/O logical device registers. The source shares register layout concepts with `w83781d.c` but implements a Super-I/O/platform-only path.

## Risks

The highest-risk area is direct hardware mutation during probe and init: enabling logical devices, altering I2C addresses, enabling temperature channels, and starting monitoring can conflict with firmware assumptions or another driver. Register banking requires strict serialization; missing `lock` coverage around bank switches would corrupt accesses, though this file consistently routes runtime register I/O through locked helpers. Error cleanup is uneven: `w83627hf_probe()` removes the common and optional groups on failure, but many optional files are created individually and are not all explicitly removed unless they belong to the optional group array; this matches old hwmon style but is fragile. Fan divisor bit packing is chip-dependent and easy to regress. The `temp_type_store()` default path logs invalid input but still returns `count`, so userspace may see a successful write even though no hardware change occurred. The single global `pdev` means the module models only one discovered chip instance.

## Test Signals

Useful validation signals include successful module load with detection at `0x2e` or `0x4e`, expected `name` output for each chip ID, stable sysfs attribute presence/absence per chip type, `sensors` output matching known voltage/fan/temp channels, no ACPI resource conflict warnings, and correct restoration after suspend/resume. Targeted tests should exercise fan divisor writes while checking `fan*_min` RPM stability, PWM mode/frequency writes, beep mask and beep enable bit preservation, temp type writes for valid and invalid values, cache refresh behavior across the 1.5 second window, and forced `force_id`/`init=0` behavior on systems or emulators where touching real Super-I/O hardware is controlled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83627hf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83773g.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/w83773g.c

## Purpose

`w83773g.c` is a compact modern hwmon driver for the Nuvoton W83773G SMBus temperature sensor. The chip exposes one local temperature channel and two remote temperature channels. The driver publishes temperature inputs, remote fault bits, remote offset calibration values, and chip update interval through the generic `devm_hwmon_device_register_with_info()` interface.

## Important APIs, Types, and Functions

The driver uses the generic hwmon callback model instead of hand-written sysfs files. `w83773_info` declares one chip channel with `HWMON_C_REGISTER_TZ | HWMON_C_UPDATE_INTERVAL` and three temp channels: local input only, then two remote channels with input, fault, and offset. `w83773_ops` supplies `w83773_is_visible()`, `w83773_read()`, and `w83773_write()`. The only persistent driver data is a `struct regmap *` stored as client data and passed as hwmon private data.

Register access is abstracted through `regmap_read()` and `regmap_write()` using an 8-bit register/8-bit value `regmap_config`. Conversion helpers include `temp_of_local()`, which converts a signed 8-bit local register to millidegrees Celsius, and `temp_of_remote()`, which combines a signed high byte and fractional low bits into 0.125 degree C units. `get_local_temp()`, `get_remote_temp()`, `get_fault()`, `get_offset()`, `set_offset()`, `get_update_interval()`, and `set_update_interval()` implement the hardware operations behind the hwmon callbacks.

## Control Flow

The I2C driver matches either the `w83773g` I2C ID or the `nuvoton,w83773g` OF compatible. `w83773_probe()` creates a devm-managed regmap, writes the conversion-rate register to `0x05` to select 2 Hz conversions, stores the regmap as client data, and registers the hwmon device with declarative channel info. There is no custom detect routine or address scan list in this file, so binding is expected to be explicit through board data, device tree, or I2C device instantiation.

At runtime, hwmon core invokes `w83773_is_visible()` to expose read-only temp inputs/faults, read-write remote offsets, and read-write chip update interval. `w83773_read()` dispatches chip update interval reads to `get_update_interval()`, local channel input reads to `get_local_temp()`, remote channel input reads to `get_remote_temp(channel - 1)`, remote faults to `get_fault(channel - 1)`, and offsets to `get_offset(channel - 1)`. `w83773_write()` allows only update interval and remote offset writes.

## State and Persistence Behavior

The driver keeps no explicit cache and no mutex. Reads go directly to the device through regmap, relying on regmap/I2C serialization. Probe sets a hardware conversion rate and user writes persist in chip registers until hardware reset or another actor changes them. `set_offset()` clamps requested offsets to `[-127825, 127825]` millidegrees, quantizes them to 125 mC units, and writes high then low bytes. `set_update_interval()` clamps intervals to 62-16000 ms and converts to the chip's rate encoding with `__fls()` math.

## Dependencies and Integration Points

The file depends on I2C, regmap, devm resource management, the generic hwmon info API, and optional Open Firmware matching. It integrates with the hwmon ABI names generated by the core, not with legacy `SENSOR_DEVICE_ATTR` definitions. `HWMON_C_REGISTER_TZ` indicates thermal-zone registration support through hwmon core. The driver has no PM hooks, no IRQ path, and no module parameters.

## Risks

The remote-channel helpers assume they are called only for channels 1 and 2. The declared visibility enforces that through hwmon channel info, but callback changes must preserve the `channel - 1` indexing invariant. The signed math in `temp_of_remote()` and `set_offset()` is sensitive: high-byte sign extension must happen before shifting, and low-byte quantization must not fabricate unsupported fractional precision. `get_fault()` reports only bit 2 of the status register, so any broader fault semantics in the hardware are intentionally ignored. Probe always writes the conversion rate to 2 Hz, which is simple but overwrites firmware-configured rates.

## Test Signals

Validation should check explicit I2C/OF binding, successful regmap initialization, `temp1_input`, `temp2_input`, and `temp3_input` readings, remote fault reporting when a remote diode is absent, offset round-trips at negative, zero, positive, and clamp boundary values, and `update_interval` quantization across 62 ms, 125 ms, 1000 ms, and 16000 ms requests. Fault injection with regmap/I2C errors should confirm that callback errors propagate to sysfs reads and writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83773g.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83781d.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/w83781d.c

## Purpose

`w83781d.c` is a large legacy hwmon driver for Winbond W83781D, W83782D, W83783S, and Asus AS99127F monitoring chips. It supports both I2C/SMBus devices and, when `CONFIG_ISA` is enabled, an ISA/platform interface to similar hardware at `0x290`. It exposes voltage inputs, fan tachometers and divisors, temperature channels including LM75-like subclients, alarms, beep masks, PWM outputs, PWM2 enable, temperature sensor type controls, VID/VRM reporting, and chip-specific optional sysfs groups.

## Important APIs, Types, and Functions

`struct w83781d_data` is the central state object. It stores the I2C client or ISA address, hwmon device, locks, chip type, optional ISA name, cache fields, two secondary `lm75` I2C clients for external temperature channels, raw voltage/fan/temp/PWM/alarm/beep registers, fan divisors, sensor type encodings, VID, and VRM.

Low-level access is split by bus. `w83781d_read_value_i2c()` and `w83781d_write_value_i2c()` handle banked SMBus registers and LM75 subclients for bank 1/2 temperature registers. Under `CONFIG_ISA`, `w83781d_read_value_isa()` and `w83781d_write_value_isa()` perform port I/O; `w83781d_read_value()` and `w83781d_write_value()` wrap either backend under `data->lock`. Detection and lifecycle functions include `w83781d_detect()`, `w83781d_detect_subclients()`, `w83781d_probe()`, `w83781d_remove()`, `w83781d_isa_found()`, `w83781d_isa_register()`, `w83781d_isa_probe()`, `sensors_w83781d_init()`, and `sensors_w83781d_exit()`.

Sysfs is generated through macros such as `sysfs_in_offsets()`, `sysfs_temp_offsets()`, `IN_UNIT_ATTRS`, `FAN_UNIT_ATTRS`, and `TEMP_UNIT_ATTRS`. `w83781d_create_files()` conditionally creates groups based on chip type and whether the instance is ISA.

## Control Flow

Module init registers the ISA device first, if enabled and detected, then registers the I2C driver. This ordering lets I2C detection avoid binding to the same physical chip through two interfaces. I2C detection verifies SMBus byte-data support, rejects reset-state chips, checks vendor IDs and address registers, determines chip type from `WCHIPID`, and calls `w83781d_alias_detect()` when an ISA instance exists. Probe allocates state, initializes locks, records match data, creates LM75-like dummy subclients for secondary temperature channels, initializes the chip, creates sysfs files, and registers the hwmon device.

The ISA flow requests individual ports during detection, validates ISA mirror behavior, checks configuration/vendor/address registers, identifies W83781D/W83782D, then creates a platform device. `w83781d_isa_probe()` reserves the runtime I/O range, allocates state, chooses chip type/name, initializes the chip, creates the same sysfs groups with ISA-specific omissions, adds a manual `name` attribute, and registers hwmon.

Runtime sysfs reads call `w83781d_update_device()`. The cache refreshes every 1.5 seconds or when invalid. It reads voltage values and limits, fan counts and minima, PWM values and PWM2 enable where supported, main and subclient temperatures and limits, VID/fan divisors, alarms from either real-time or interrupt registers depending on chip type, and beep mask registers. Store callbacks update limits, fan minima, fan divisors, beep masks, PWM values, PWM2 enable, sensor type registers, and internal VRM.

## State and Persistence Behavior

The driver's cache is volatile and guarded by `update_lock`; bus/bank operations are guarded by `lock`. Hardware register changes from sysfs persist in the chip until reset or external modification. `w83781d_init_device()` can optionally reset the chip with `reset=1`, but comments warn that this loses BIOS fan divider and sensor type setup. With `init=1`, it disables power-on abnormal beep, enables temp2/temp3 where applicable, starts monitoring, initializes sensor type cache, selects VRM, and seeds fan minima.

I2C subclient addresses may be forced by `force_subclients`, otherwise they are read from the chip. The driver explicitly registers dummy devices for these addresses and unregisters them on remove or probe failure. Fan divisor writes preserve the visible fan minimum by converting through RPM before and after divisor changes. `vrm` is purely driver state and is not written to hardware.

## Dependencies and Integration Points

The file integrates with I2C class-based hwmon scanning, optional OF compatible matching, optional ISA platform support, hwmon sysfs ABI, `hwmon-vid`, LM75-style temperature register conventions, jiffies cache timing, and legacy I/O port access. It uses module parameters `force_subclients`, `reset`, and `init`. It also coordinates with `w83781d_data_if_isa()` and `w83781d_alias_detect()` to prevent duplicate I2C/ISA binding.

## Risks

This driver has significant legacy complexity. Dual I2C/ISA access to one chip is dangerous; alias detection reduces but cannot eliminate risk if registers differ during comparison or firmware changes them concurrently. I2C bank switching and subclient translation depend on locking and correct bank resets. `w83781d_create_files()` documents that it does no cleanup on partial failure, so callers must remove all groups; this is fragile because errors can happen after only some groups were created. Optional chip-specific sysfs permissions, especially `temp3_alarm`, differ by kind and are easy to regress. Reset/init can alter BIOS-provided thermal configuration. Some invalid sensor type writes log an error but return success count. Manual dummy subclient lifecycle uses non-devm APIs and must stay balanced.

## Test Signals

Test signals include successful I2C detection for each supported chip ID, no duplicate binding when ISA and I2C aliases are both visible, correct creation of chip-specific attribute groups, working forced and auto subclient addresses, sane temp2/temp3 LM75 reads through dummy clients, fan divisor writes preserving `fan*_min`, beep mask preservation of global enable, PWM2 enable toggling both PWM and beep-config bits, and `reset=1`/`init=1` behavior. ISA builds should validate port probing, resource reservation, manual `name`, and removal without dangling platform or dummy devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83781d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83791d.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/w83791d.c

## Purpose

`w83791d.c` is a legacy I2C hwmon driver for the Winbond W83791D. It exposes a broad motherboard-monitoring surface: ten voltage inputs, five fan tachometers, three temperature channels, five PWM outputs, Smart Fan I target/tolerance controls for PWM1-3, alarms, individual and global beep controls, VID/VRM reporting, and conditional fan/PWM 4-5 attributes when those pins are not used as GPIO.

## Important APIs, Types, and Functions

The main state object, `struct w83791d_data`, stores the hwmon device, cache lock, cache timestamp/valid flag, raw voltage/fan/temp/PWM registers, fan divisors, PWM enable modes, target temperatures, tolerances, alarm and beep masks, global beep enable, VID, and VRM. Access helpers `w83791d_read()` and `w83791d_write()` are thin SMBus byte-data wrappers.

Important lifecycle functions are `w83791d_detect()`, `w83791d_detect_subclients()`, `w83791d_probe()`, `w83791d_remove()`, `w83791d_init_client()`, and `w83791d_update_device()`. The I2C driver uses `I2C_CLASS_HWMON`, the `normal_i2c` address list, and legacy detect/probe callbacks. Sysfs handlers are organized through arrays of `sensor_device_attribute` for input, fan, PWM, temp, beep, and alarm attributes, then grouped in `w83791d_group` and `w83791d_group_fanpwm45`.

## Control Flow

I2C detection verifies SMBus byte-data support, checks the config register reset bit, validates Winbond vendor ID and address register, switches to vendor-ID high-byte bank state, confirms W83791D chip ID `0x71` and vendor `0x5c`, then sets board info type. Probe allocates state, initializes `update_lock`, optionally configures and reserves temperature subclient addresses via devm dummy devices, initializes the chip, primes `fan_min[]`, creates the base sysfs group, conditionally creates the fan/PWM 4-5 group based on GPIO register bit `0x10`, and registers hwmon.

Runtime reads call `w83791d_update_device()`, which refreshes every three seconds. It reads all voltage values and limits, fan counts and limits, fan divisor bitfields across multiple registers plus VBAT high bits, PWM duty values, PWM enable modes, Smart Fan target and tolerance values, signed and fractional temperature registers, alarm registers, beep control registers and global beep bit, and VID. Store callbacks update voltage limits, fan minima, fan divisors, PWM duty, PWM enable mode, Smart Fan target/tolerance, temperature limits, beep bits/masks/global enable, and internal VRM.

## State and Persistence Behavior

The driver uses no extra transaction lock beyond the I2C adapter's own serialization; cache and read-modify-write sequences are protected by `update_lock`. Hardware state is persistent until chip reset. `reset=1` writes the config reset bit after saving beep config; `init=1` performs softer initialization by disabling abnormal and global beeps, enabling temp2/temp3 monitoring, and starting monitoring. Both are off by default to preserve BIOS setup. Fan divisor stores preserve user-visible fan minimum RPM across divisor changes. Beep writes re-read the affected byte before changing one bit so adjacent beep settings are not lost.

## Dependencies and Integration Points

The driver depends on I2C SMBus byte-data operations, legacy I2C class scanning, hwmon sysfs registration, `hwmon-vid`, devm dummy I2C devices for subclient address reservation, jiffies cache timing, and module parameters `force_subclients`, `reset`, and `init`. It integrates with the hwmon ABI through manual sysfs attributes and with motherboard firmware through conservative default initialization.

## Risks

The file contains dense bitfield packing for fan divisors, PWM enable, beep masks, tolerances, and target values. Regressions in masks or shifts can silently alter unrelated hardware controls. `w83791d_remove()` unregisters only the base sysfs group and does not remove `w83791d_group_fanpwm45` when it was created, which is a lifecycle risk visible from this source. Probe creates devm dummy subclients without storing handles, so they act as address reservations rather than active register clients. `store_beep()` coerces any nonzero value to one instead of rejecting values greater than one, which is permissive compared with some hwmon stores. Reset/init can override BIOS thermal and beep setup. Because there is no regmap or explicit per-register error handling, failed SMBus reads can enter cached fields as negative values truncated to unsigned types.

## Test Signals

Important tests include detection rejection on wrong vendor/chip/address, attribute presence for ten inputs and conditional fan/PWM 4-5, fan divisor writes for all five fans with fan minimum preservation, PWM enable mode round-trips for modes 1-3, Smart Fan target/tolerance writes preserving unrelated bits, temp2/temp3 fractional conversion, global and per-channel beep mask interactions, VRM/VID reporting, and removal after conditional group creation. Fault-injection tests should simulate SMBus read/write failures to expose the lack of propagated errors in many paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83791d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83792d.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/w83792d.c

## Purpose

`w83792d.c` is a legacy I2C hwmon driver for the Winbond W83792AD/D monitoring chip. It exposes nine voltage inputs with extra low-bit resolution, up to seven fans, three temperature channels, seven PWM/DC outputs, PWM enable modes, PWM/DC mode controls, chassis intrusion status and reset, thermal cruise targets, Smart Fan I/II tolerances, Smart Fan II temperature points and duty levels, and alarm reporting.

## Important APIs, Types, and Functions

`struct w83792d_data` holds the hwmon device, cache lock, cache validity/timestamp, raw input/limit registers, `low_bits` for voltage resolution, fan counts/minima/divisors, temperature registers, PWM registers, PWM enable modes, alarms, chassis state, thermal cruise/tolerance arrays, and Smart Fan II point/level tables. `w83792d_read_value()` and `w83792d_write_value()` wrap SMBus byte-data operations; comments note that the driver only accesses bank 0, so no explicit bank-switch lock is used.

Key lifecycle functions are `w83792d_detect()`, `w83792d_detect_subclients()`, `w83792d_probe()`, `w83792d_remove()`, `w83792d_init_client()`, and `w83792d_update_device()`. Attribute declarations are static `SENSOR_DEVICE_ATTR` and `SENSOR_DEVICE_ATTR_2` entries grouped into a base `w83792d_group` plus four optional fan groups for fan/PWM 4-7 depending on GPIO/pin configuration.

## Control Flow

The I2C driver performs legacy class scanning over addresses `0x2c` through `0x2f`. Detection requires SMBus byte-data support, a non-reset config register, matching Winbond vendor/address registers, and chip ID `0x7a` with vendor `0x5c`. Probe allocates state, initializes `update_lock`, reserves optional subclient addresses from the chip or `force_subclients`, initializes hardware, primes fan minimum registers, creates the base sysfs group, inspects GPIO enable and pin registers to decide which fan/PWM 4-7 groups to expose, and registers the hwmon device.

`w83792d_init_client()` optionally resets the chip when `init=1`, clears a VID input bit so users may edit VIN0/VIN1 limits, configures temp2/temp3 by masking their config registers, and starts monitoring. `w83792d_update_device()` refreshes every three seconds, reads all voltage values/limits plus low-bit registers, fan counts/minima, PWM values and enable modes, temperature values and limits, fan divisors, alarms, chassis status, thermal cruise targets, tolerances, Smart Fan II temperature points, and Smart Fan II duty levels.

Store callbacks perform unit conversion and read-modify-write updates for voltage limits, fan minima/divisors, temp limits, PWM duty low nibbles, PWM enable modes, PWM/DC mode, chassis intrusion reset, thermal cruise target, tolerance nibbles, Smart Fan II point values, and Smart Fan II level values.

## State and Persistence Behavior

Cached state is guarded by `update_lock` and refreshed lazily. Most writes update both cache and hardware immediately. The intrusion alarm clear path writes the chassis-clear bit and invalidates the cache to force the next read to observe hardware. Fan divisor stores preserve visible fan minimum RPM. Voltage input reads combine high byte plus two low bits for VIN0-VIN6, while limit reads/writes use coarser register units. PWM duty is exposed as 0-255 but stored in a 4-bit field shifted into the low nibble, while the high bits retain mode/control state.

The driver uses devm dummy I2C devices for subclient address reservation but does not keep client pointers. It has no PM callbacks and no explicit persistent software state beyond the in-memory cache and VRM-free chip configuration.

## Dependencies and Integration Points

Dependencies include I2C SMBus byte-data support, legacy hwmon class scanning, manual hwmon sysfs registration, jiffies timing, devm allocation/resource cleanup, and the `force_subclients` and `init` module parameters. The optional fan groups integrate hardware pin mux state into sysfs surface: fan4/fan5 depend on GPIO enable bits, while fan6/fan7 depend on pin register bits.

## Risks

The most important risks are bitfield correctness and lifecycle cleanup. `w83792d_remove()` removes all optional fan groups unconditionally, which is safe for absent groups but should remain aligned with probe. `w83792d_init_client()` modifies VIN0/VIN1 limit policy and temp config registers even when not doing a full reset, so module load can alter firmware-configured behavior. Several SMBus read/write wrappers return raw errors but most callers store results into unsigned fields without propagating failures. PWM duty/mode share a register, making mask preservation critical. Smart Fan II level indexing and nibble placement are easy to regress because sysfs indices are one-based while arrays are zero-based. Optional fan exposure depends on hardware pin state at probe and will not adapt dynamically after pin configuration changes.

## Test Signals

Validation should cover detection paths, base and optional sysfs group creation for different GPIO/pin states, voltage input low-bit scaling, voltage limit scaling, fan divisor writes for all seven fans with `fan*_min` preservation, PWM duty and PWM/DC mode bit preservation, PWM enable mode mapping between sysfs modes and register encodings, intrusion alarm clear and cache invalidation, Smart Fan I target/tolerance writes, Smart Fan II point/level round-trips, and module removal after every optional group combination. Error-injection tests should verify behavior under negative SMBus returns, since many paths currently do not surface errors cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83792d.c -->
