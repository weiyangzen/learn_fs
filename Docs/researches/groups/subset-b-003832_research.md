# subset-b-003832 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct6683.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/nct6683.c

## Purpose

`nct6683.c` is a standalone Linux hwmon platform driver for Nuvoton NCT6683/NCT6686/NCT6687 embedded-controller hardware monitor blocks reached through Super-I/O configuration ports and EC I/O space. It detects supported Super-I/O IDs at `0x2e` and `0x4e`, creates platform devices for discovered monitor windows, exposes voltages, temperatures, fan tachometers, PWM outputs, beep control, and case-open intrusion status through hwmon sysfs attributes, and starts EC monitoring when necessary.

## Important APIs, Types, and Functions

- `enum kinds`, `nct6683_device_names`, and `nct6683_chip_names` map detected chip IDs to hwmon names and log labels.
- `struct nct6683_data` is the central per-device state: EC base address, Super-I/O register port, chip kind, customer ID, generated attribute groups, sensor source maps, cached readings, fan/PWM presence masks, update timestamp, validity flag, and PM backup state.
- `struct nct6683_sio_data` carries discovery output from module init into `nct6683_probe()`.
- `nct6683_read()`, `nct6683_read16()`, and `nct6683_write()` implement EC page/index/data register access at the requested I/O resource.
- `nct6683_create_attr_group()` instantiates repeated sysfs attributes from local `sensor_device_template` definitions.
- `nct6683_update_device()` refreshes cached voltages, temperatures, fan RPM/minimums, PWM values, and limits once per second under `update_lock`.
- `nct6683_setup_fans()` and `nct6683_setup_sensors()` discover fan/PWM and voltage/temperature channel exposure from EC configuration registers.
- `nct6683_find()` probes Super-I/O configuration space, validates device ID, locates the HWM logical device base address, and enables access if needed.
- `sensors_nct6683_init()` registers the platform driver, probes both possible Super-I/O ports, allocates platform devices, checks ACPI resource conflicts, and attaches I/O resources.

## Control Flow

Module init registers `nct6683_driver`, then scans `0x2e` and `0x4e`. For each supported Super-I/O ID, `nct6683_find()` selects logical device `NCT6683_LD_HWM`, reads the HWM base address, optionally enables the logical device, records the Super-I/O port, and returns the aligned EC address. The init path then allocates a platform device whose I/O resource starts at `address + IOREGION_OFFSET`, allowing `nct6683_probe()` to request only the EC port range it uses.

Probe allocates `struct nct6683_data`, records the platform and Super-I/O metadata, initializes `update_lock`, reads the EC `customer_id`, and rejects unknown board/customer layouts unless the `force` module parameter is set. It starts monitoring through `NCT6683_HWM_CFG`, discovers active fan/PWM and monitor channels, builds only the sysfs groups that have present sensors, adds the fixed "other" group, logs EC firmware version/build information, and registers the hwmon device with `devm_hwmon_device_register_with_groups()`.

Read callbacks call `nct6683_update_device()` and format cached values. Writes are limited: Mitac boards get writable PWM duty via the EC fan configuration request/done handshake; beep and intrusion attributes write Super-I/O control registers; case-open clearing toggles the active-low case-open bit and invalidates the cache.

## State and Persistence Behavior

All runtime state is per-platform-device and protected by `update_lock` for EC/Super-I/O operations that can race with hwmon sysfs reads or writes. Sensor readings are cached for one second using `last_updated` and `valid`. The driver derives channel ordering from the chip's monitor configuration at probe time and keeps `temp_index/temp_src` plus `in_index/in_src` arrays for sysfs-to-register mapping.

There is no file-backed persistence. Hardware configuration changes made through PWM, beep, intrusion clear, and the HWM enable bit persist in device registers according to platform firmware/chip behavior. Under `CONFIG_PM`, suspend caches `NCT6683_HWM_CFG`; resume restores that byte and marks all cached sensor data invalid.

## Dependencies and Integration Points

The driver depends on Linux hwmon sysfs helpers, platform devices/resources, raw I/O port access (`outb_p`, `inb_p`), Super-I/O enter/exit helpers from `linux/nuvoton.h`, ACPI resource conflict checks, mutexes, PM hooks, and devm allocation/registration. It does not share code with `nct6775-core.c`; it is a separate legacy-style hwmon driver with generated sysfs groups.

## Risks and Edge Cases

- Unknown customer IDs are rejected unless `force=1` because register layout and scaling vary by board vendor; forced mode can expose misleading or unsafe controls.
- The Intel customer path hides several limit attributes because their register encoding/location is unknown.
- PWM writes are only writable for Mitac boards, but the visibility decision depends solely on the probed customer ID.
- EC access uses raw port I/O and a page/index/data protocol; missing locking in future paths would corrupt register selection.
- `nct6683_find()` can forcibly enable EC access if firmware left the logical device disabled, and warns that data may be unusable.
- Dynamic sysfs visibility depends on fixed template ordering; adding or reordering attributes requires matching the index arithmetic in `*_is_visible()` functions.
- `show_temp16()` converts by integer-dividing before multiplying, which intentionally reports in 0.5 degree steps but discards lower bits in a way tests should pin down.

## Test Signals

Useful test signals include Super-I/O detection for all supported IDs, rejection of unsupported IDs and unknown customer IDs without `force`, ACPI conflict skip behavior, EC HWM enable behavior, generated attribute counts for sparse fan/PWM/monitor configurations, Intel-vs-non-Intel visibility differences, one-second cache refresh behavior, Mitac PWM write sequencing, intrusion clear toggling, beep enable read/write, and suspend/resume restoration of `NCT6683_HWM_CFG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct6683.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct6694-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/nct6694-hwmon.c

## Purpose

`nct6694-hwmon.c` is the hwmon child driver for the Nuvoton NCT6694 USB-attached multifunction controller. It exposes voltage, temperature, fan, and PWM channels through the modern `hwmon_ops` interface while delegating USB command transport to the parent NCT6694 MFD device via `nct6694_read_msg()` and `nct6694_write_msg()`.

## Important APIs, Types, and Functions

- `struct nct6694_hwmon_control` mirrors the HWMON control payload containing enable bitmaps and PWM frequency registers.
- `struct nct6694_hwmon_alarm` mirrors voltage, temperature, and fan limit/alarm configuration plus `smi_ctrl`.
- `struct nct6694_pwm_control` holds manual PWM enable/value fields for the PWM command module.
- `union nct6694_hwmon_rpt` represents single report-channel reads for voltage, temperature, fan, PWM, or status bytes.
- `struct nct6694_hwmon_data` stores the parent `struct nct6694`, mutex, cached enable/frequency control block, and reusable report/message buffers.
- `nct6694_in_read/write()`, `nct6694_temp_read/write()`, `nct6694_fan_read/write()`, and `nct6694_pwm_read/write()` implement type-specific hwmon attributes.
- `nct6694_read()`, `nct6694_write()`, and `nct6694_is_visible()` are the hwmon operation dispatchers.
- `nct6694_hwmon_init()` reads initial enable/frequency state, reads the alarm block, selects realtime interrupt/alarm mode, and writes it back.
- `nct6694_hwmon_probe()` allocates state and buffers, initializes the mutex, initializes hardware policy, and registers `nct6694_chip_info`.

## Control Flow

The platform probe obtains the parent MFD state from `pdev->dev.parent`, allocates one shared report buffer and one shared command payload union, stores the parent pointer, and initializes `data->lock`. `nct6694_hwmon_init()` reads the hardware monitor control block, then reads the alarm block, changes `smi_ctrl` to realtime mode, and writes the updated alarm block.

After registration, hwmon core calls `nct6694_is_visible()` to expose fixed permissions for every declared channel. Enable attributes are read from the cached `hwmon_en` bitmaps. Input/alarm reads build `struct nct6694_cmd_header` values for either the report module (`NCT6694_RPT_MOD`) or the HWMON/PWM command modules and serialize the transaction under `data->lock`. Writes either edit `hwmon_en` and write the full control block, or read-modify-write the full alarm/PWM-control structure before returning.

## State and Persistence Behavior

The enable state and PWM frequency bytes are cached in `data->hwmon_en` after probe and updated in memory before each successful control write. Limit and manual PWM structures are not long-term cached; they are read into `data->msg` for each read-modify-write path. Report data in `data->rpt` is a temporary shared buffer. The mutex serializes these buffers and parent command traffic for this child driver. Persistent effects live in the NCT6694 device firmware/configuration; the driver itself has no disk persistence and no PM callbacks.

## Dependencies and Integration Points

The file integrates with the NCT6694 MFD interface from `<linux/mfd/nct6694.h>`, platform driver binding via `MODULE_ALIAS("platform:nct6694-hwmon")`, Linux hwmon channel-info registration, bitfield helpers, endian helpers for fan limit/report values, and devm allocation. It assumes the parent MFD owns USB transport and command framing beyond the child driver-provided command headers.

## Risks and Edge Cases

- `nct6694_temp_write()` for `hwmon_temp_max_hyst` calls `nct6694_read_msg()` but does not check `ret` before using and writing `data->msg->hwmon_alarm`, so a failed read can propagate stale buffer contents.
- Enable writes update the cached `hwmon_en` before the device write result is known; if `nct6694_write_msg()` fails, memory and hardware state can diverge.
- Every limit update writes a full alarm block, so stale or concurrent state outside this driver could be overwritten if the parent has other clients changing the same block.
- `nct6694_is_visible()` exposes all declared channels regardless of enable bits; disabled channels appear with `*_enable=0` rather than being hidden.
- Temperature input conversion sign-extends an 11-bit value built from `msb` and three high bits of `lsb`; any firmware format change would silently corrupt readings.
- PWM frequency is clamped to 100-25000 Hz and quantized through an 8-bit register, so round-trip reads may not equal the requested value.

## Test Signals

Tests should cover init command ordering, realtime alarm mode write, visibility modes for each attribute, voltage scaling/clamping, signed temperature conversion and hysteresis encoding, fan big-endian values, PWM duty/frequency conversions, enable-bit updates for channels above and below bit 8, failed parent read/write paths including cache divergence, and concurrent sysfs reads/writes proving `data->lock` protects the shared buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct6694-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct6775-core.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/nct6775-core.c

## Purpose

`nct6775-core.c` is the shared hwmon implementation for the NCT6106/NCT6116/NCT6775/NCT6776/NCT6779/NCT679x family. It contains the chip-specific register tables, conversion helpers, cache refresh logic, sysfs attribute implementations, automatic fan-control handling, temperature source discovery, and the exported `nct6775_probe()` entry point used by both the platform/LPC frontend and the BMC-oriented I2C frontend.

## Important APIs, Types, and Functions

- `DEFAULT_SYMBOL_NAMESPACE "HWMON_NCT6775"` namespaces exported helpers for frontends.
- Per-chip register arrays and label tables define voltage, fan, PWM, alarm, beep, temperature, TSI, and Smart Fan register layouts for all supported variants.
- Conversion helpers include `fan_from_reg8/13/16/rpm()`, `fan_to_reg()`, `in_from_reg()`, `in_to_reg()`, `tsi_temp_from_reg()`, and PWM step-time conversion.
- Dynamic sysfs generation is handled by `sensor_device_template`, `sensor_device_attr_u`, `sensor_template_group`, and `nct6775_add_template_attr_group()`.
- `nct6775_reg_is_word_sized()` tells regmap frontends which logical registers require two byte accesses.
- `nct6775_update_device()` refreshes cached voltage, fan, PWM, temperature, TSI, alarm, and beep state with a 1.5-second cache window.
- `nct6775_update_pwm()` and `nct6775_update_pwm_limits()` collect fan-control mode, duty, target, tolerance, weight, and automatic curve data.
- Store callbacks such as `store_fan_min()`, `store_pwm_enable()`, `store_pwm_temp_sel()`, `store_auto_pwm()`, and `store_temp_type()` perform validated read-modify-write updates through `nct6775_write_value()`.
- `add_temp_sensors()` and the discovery loops in `nct6775_probe()` map hardware temperature source IDs into fixed and dynamic hwmon temp channels.
- `nct6775_probe()` initializes the regmap, selects the per-kind register map, discovers sensors, runs hardware and frontend initialization, creates attribute groups, and registers the hwmon device.

## Control Flow

Frontend drivers allocate and partially initialize `struct nct6775_data`, including `kind`, `driver_data`, optional `read_only`, and optional `driver_init`, then call `nct6775_probe()`. The core creates a regmap with frontend-supplied bus callbacks and initializes generic state such as `update_lock`, the chip name, bank cache, and default voltage scaling.

The large `switch (data->kind)` fills `struct nct6775_data` with chip-specific register pointers, feature counts, conversion functions, masks, labels, and limits. After that, the probe path determines all available voltage inputs by count, discovers temperature sources by reading `REG_TEMP_SOURCE`, opportunistically assigns unmonitored fan-control sources to available temperature monitor registers, adds alternate temperature registers, detects nonzero TSI temperature channels, starts monitoring/VBAT/temp inputs in `nct6775_init_device()`, then calls the frontend's `driver_init()` to detect bus-specific fan/PWM/VID/other state.

Once initialized, the core seeds fan divider/minimum state, creates repeated PWM, voltage, fan, temp, and optional TSI temp sysfs groups, and registers hwmon. Normal sysfs reads go through `nct6775_update_device()`, which refreshes all cache groups under `update_lock` when stale. Store paths validate input, update the cache, and write hardware through regmap. In read-only I2C mode, visibility is reduced by `nct6775_attr_mode()` but many store functions still exist behind permissions stripped by the mode.

## State and Persistence Behavior

`struct nct6775_data` is the core state object and is intentionally large: it stores constant per-kind register pointers, per-device feature masks, current register bank, cached readings, cached limits, fan divider state, temperature mappings, alarm/beep bitfields, and automatic fan-control tables. Cache validity is based on `last_updated` plus `valid`; failures during refresh return `ERR_PTR(err)` without updating the valid timestamp.

Writes change device registers and cached state but are not persisted outside hardware/firmware behavior. Some stores intentionally preserve related settings, such as fan min values when changing dividers and PWM floor enable bits in `REG_TEMP_SEL`. The core has no PM callbacks; platform PM support lives in `nct6775-platform.c`, while I2C mode is read-only and has no suspend/resume restoration.

## Dependencies and Integration Points

The core depends on `nct6775.h` for `struct nct6775_data`, shared constants, and inline regmap helpers. It integrates Linux hwmon sysfs conventions, regmap, mutex locking, `LM75_TEMP_FROM_REG/TO_REG`, `sysfs_emit`, nospec array indexing for user-selected temperature sources, and exported symbols consumed by `nct6775-platform.c` and `nct6775-i2c.c`.

## Risks and Edge Cases

- The per-kind switch is dense and pointer-heavy; a missing register pointer can hide attributes at best or dereference null in a path not guarded by visibility at worst.
- Many visibility callbacks depend on exact template ordering and hard-coded modulo arithmetic.
- Temperature source discovery changes hardware source registers for unmonitored fan-control sensors, which is helpful but can surprise firmware assumptions.
- `nct6775_update_device()` performs a large number of regmap operations under one mutex; slow or failing transports can block all sysfs access.
- Fan divider auto-selection changes hardware and fan-min encoding based on observed readings; tests need to cover boundary values and preservation of alarms.
- Several Smart Fan modes have chip-specific semantics, especially critical point enable/disable, `sf3` limited to NCT6775, and `sf4` requiring monotonic trip points.
- Alarm and beep bit mapping is indirect for temperatures because source registers, not fixed channel indexes, determine the bits.
- Frontends must provide correct word-size behavior and bank selection; otherwise the core's 16-bit temperature/fan handling breaks.

## Test Signals

High-value tests include per-kind probe table sanity, no-null register coverage for visible attributes, temperature source mapping with duplicates/invalid sources/alternate registers, TSI detection, cache refresh success and error propagation, read-only permission stripping, fan min/divider edge cases, all PWM enable modes and trip-point validation, temperature type writes, alarm/beep bit mapping, auto point read/write including critical points, and frontend integration tests through both direct platform and I2C regmap callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct6775-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct6775-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/nct6775-i2c.c

## Purpose

`nct6775-i2c.c` is the read-only I2C frontend for the shared NCT6775-family hwmon core. It targets systems, commonly BMCs, that access the Nuvoton Super-I/O monitor block through a backdoor I2C interface while the host may still use the normal LPC interface. Its design deliberately avoids modifying chip state except for the I2C-local bank-select register.

## Important APIs, Types, and Functions

- `nct6775_i2c_read()` implements the regmap `.reg_read` callback: select bank if needed, read the low register byte, and optionally read the following byte for word-sized logical registers.
- `nct6775_i2c_write()` is a dummy regmap `.reg_write` callback that logs skipped writes and returns success to avoid disturbing host LPC usage.
- `nct6775_i2c_of_match` and `nct6775_i2c_id` map compatible strings and I2C IDs to `enum kinds`.
- `nct6775_i2c_probe_init()` is the core `driver_init` hook; it supplies conservative fan/PWM presence masks and augments TSI channels from device tree.
- `nct6775_i2c_regmap_config` exposes 16-bit logical registers and 16-bit values through custom callbacks.
- `nct6775_i2c_probe()` allocates `struct nct6775_data`, sets read-only mode and driver hooks, and calls `nct6775_probe()`.

## Control Flow

I2C probe allocates core state, obtains the matched chip kind from OF or ID matching, sets `data->read_only = true`, stores the `i2c_client` in `driver_data`, assigns `nct6775_i2c_probe_init()` as the post-core initialization hook, and enters the shared `nct6775_probe()` path. During core reads, the regmap callback keeps `data->bank` synchronized with the high byte of the logical register and issues SMBus byte reads for one or two consecutive register offsets.

After the core has performed its generic sensor discovery, `nct6775_i2c_probe_init()` sets fans 1 and 2, fan mins 1 and 2, and PWM 1 and 2 as present because the I2C interface cannot inspect all Super-I/O control registers needed for pin detection. It also reads optional `nuvoton,tsi-channel-mask` from device tree and ORs those bits into `have_tsi_temp` to compensate for early BMC boot cases where automatic TSI detection has no readings yet.

## State and Persistence Behavior

The frontend maintains only the shared core state and an I2C bank cache in `data->bank`. It is intentionally read-only: sysfs write permissions are stripped by the core using `data->read_only`, and any accidental core write reaches `nct6775_i2c_write()`, which logs and returns success without touching hardware. The only hardware state changed by reads is bank selection for the I2C interface. There is no suspend/resume handling and no persistence outside normal core cache behavior.

## Dependencies and Integration Points

The file depends on Linux I2C/SMBus byte-data operations, OF matching, regmap custom callbacks, hwmon class matching (`I2C_CLASS_HWMON`), and the exported `HWMON_NCT6775` namespace from the core. Device tree can provide both chip compatible data and `nuvoton,tsi-channel-mask`.

## Risks and Edge Cases

- The dummy write callback returns success, so any core path that accidentally remains writable in read-only mode would appear successful while not changing hardware.
- Fan and PWM presence is guessed as channels 1 and 2; systems whose BMC wiring differs may expose useless or misleading attributes.
- Word-size detection must match the core exactly or SMBus reads will combine the wrong bytes.
- The bank cache is stored in shared core state and assumes serialized core access through `update_lock`; future direct regmap use outside that locking would need care.
- TSI mask augmentation trusts device-tree data and can expose channels that never produce valid readings.
- Because the host can manipulate the LPC side concurrently, I2C readings can change underneath the BMC and should be treated as observational.

## Test Signals

Tests should cover OF and legacy I2C ID matching for every kind, bank switching only when the high byte changes, one-byte versus word-sized reads, SMBus error propagation, dummy write logging/no-op behavior, read-only sysfs permissions, default fan/PWM masks, `nuvoton,tsi-channel-mask` augmentation, and integration with `nct6775_probe()` for at least one older and one newer chip kind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct6775-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct6775-platform.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/nct6775-platform.c

## Purpose

`nct6775-platform.c` is the platform/LPC frontend for the shared NCT6775-family hwmon core. It discovers Nuvoton Super-I/O monitor devices through configuration ports, decides whether to access hardware directly or through ASUS ACPI WMI methods on selected boards, provides regmap callbacks for those access modes, detects board-specific fan/PWM/VID/intrusion capabilities, handles suspend/resume restoration, and creates platform devices that call into `nct6775_probe()`.

## Important APIs, Types, and Functions

- `struct nct6775_sio_data` carries Super-I/O port, logical device, kind, access mode, and polymorphic Super-I/O callbacks.
- `enum sensor_access` selects direct I/O port access or ASUS WMI access.
- `nct6775_asuswmi_evaluate_method()`, `nct6775_asuswmi_read()`, and `nct6775_asuswmi_write()` wrap ASUS `WMBD` ACPI calls.
- `superio_*` and `superio_wmi_*` implement direct and WMI-backed Super-I/O register operations.
- `nct6775_reg_read/write()` and `nct6775_wmi_reg_read/write()` are regmap callbacks for HWM register access.
- `nct6775_find()` detects supported Super-I/O device IDs, reads the HWM I/O base, enables the logical device if needed, and unlocks newer HM I/O mapping.
- `nct6775_check_fan_inputs()` inspects many chip-specific pinmux registers to determine `has_fan`, `has_fan_min`, and `has_pwm`.
- `nct6775_platform_probe_init()` reads VID/fan debounce/platform feature state and adds the platform-only "other" attribute group.
- `nct6775_suspend()` and `nct6775_resume()` preserve VBAT, fan dividers, SIO enable, limits, and cached thresholds across sleep.
- `sensors_nct6775_platform_init()` handles DMI board matching, access-mode selection, platform device creation, ACPI conflict checks, and driver registration.

## Control Flow

Module init registers the platform driver, checks DMI vendor/name for ASUS boards in the two allowlists, and if matched attempts to find an ASUS WMI ACPI device by UID. If WMI read of the chip ID succeeds, subsequent access uses WMBD methods; otherwise it uses direct Super-I/O and HWM I/O ports.

For each Super-I/O configuration port, the init path fills direct callbacks, calls `nct6775_find()`, and, if a chip is found, allocates a platform device. Direct access devices receive an I/O resource at `address + IOREGION_OFFSET` after ACPI conflict checking. WMI access devices skip I/O resources and swap the callback table to WMI operations. Platform probe allocates `struct nct6775_data`, chooses the direct or WMI regmap config, stores `nct6775_platform_probe_init()` as `driver_init`, and invokes the shared core.

The platform init hook enters Super-I/O configuration mode, optionally reads CPU VID, optionally enables fan debounce based on the module parameter, calls `nct6775_check_fan_inputs()` to populate presence masks, exits Super-I/O mode, and adds `cpu0_vid`, intrusion, and beep-enable attributes. PM resume re-enters Super-I/O mode, restores enable/mapping state, rewrites cached limits and selected control registers, then invalidates the core cache.

## State and Persistence Behavior

Platform state is split between `struct nct6775_sio_data` in platform data and `struct nct6775_data` owned by the core. The frontend stores direct HWM I/O base in `data->addr`, Super-I/O port in `data->sioreg`, the selected access callbacks in platform data, and PM backup values in core fields such as `vbat`, `fandiv1`, `fandiv2`, and `sio_reg_enable`. Direct regmap access caches the currently selected register bank in `data->bank`; WMI access records the bank but relies on ACPI calls rather than raw bank-select I/O.

Hardware changes include enabling logical devices, enabling HM I/O mappings on newer chips, fan debounce configuration, case-open clear toggles, and all writable core hwmon controls. These persist only as chip/firmware state. The driver keeps no disk state.

## Dependencies and Integration Points

The file integrates raw I/O port access, `request_muxed_region()` for Super-I/O configuration ports, platform device/resource management, ACPI resource conflict checks, ACPI `WMBD` method evaluation, DMI board matching, hwmon VID conversion, Linux PM ops, regmap custom callbacks, and the exported NCT6775 core namespace.

## Risks and Edge Cases

- DMI allowlists for ASUS WMI routing are large and require maintenance; unsupported boards fall back to direct access and may conflict with firmware.
- `force_id` can override detected chip IDs and route the core through an incompatible register map.
- Super-I/O probing may forcibly enable the HWM logical device when disabled, with a warning that sensors may be unusable.
- Fan/PWM presence detection is highly chip- and pinmux-specific; mistakes expose missing channels or hide valid ones.
- WMI methods return limited error detail and are globally tied to the selected `asus_acpi_dev`.
- PM resume writes many cached limits back to hardware; stale cache or failed intermediate writes can leave partial restoration.
- Direct and WMI regmap callbacks depend on correct `nct6775_reg_is_word_sized()` behavior for two-byte registers.
- Platform-only "other" attributes share core alarm/beep helpers and require correct bit-map tables from the core.

## Test Signals

Tests should cover Super-I/O ID matching, `force_id`, zero-base rejection, logical-device enable behavior, ACPI resource conflicts, ASUS DMI/WMI access selection for both UIDs, WMI read/write error propagation, direct banked register reads/writes, fan/PWM pin detection for representative chip families, fan debounce parameter effects, VID visibility, intrusion clear behavior, platform probe with both access modes, and suspend/resume restoration including failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct6775-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct6775.h -->
# sources/distributed-fs/ceph-client/drivers/hwmon/nct6775.h

## Purpose

`nct6775.h` is the shared interface and state definition for the NCT6775-family hwmon core and its frontends. It defines supported chip kinds, PWM operating modes, shared maximum channel counts, the large `struct nct6775_data` state object, inline regmap access helpers, exported core function prototypes, shared sysfs helpers, bank/config register constants, and alarm/beep bit layout constants.

## Important APIs, Types, and Functions

- `enum kinds` enumerates all supported chips from `nct6106` through `nct6799`.
- `enum pwm_enable` defines sysfs-visible fan-control modes: `off`, `manual`, `thermal_cruise`, `speed_cruise`, `sf3`, and `sf4`.
- `NUM_TEMP`, `NUM_TEMP_FIXED`, `NUM_TSI_TEMP`, `NUM_REG_ALARM`, `NUM_REG_BEEP`, `NUM_FAN`, and `NUM_IN` size the core arrays.
- `struct nct6775_data` is the shared per-device contract between frontends and core, combining frontend input, per-chip register pointers, feature masks, cached readings, fan/PWM control caches, alarm/beep state, PM backup state, regmap pointer, read-only flag, and optional frontend initialization hook.
- `nct6775_read_value()` and `nct6775_write_value()` wrap `regmap_read()` and `regmap_write()` while presenting `u16` values to the core.
- `nct6775_update_device()`, `nct6775_reg_is_word_sized()`, and `nct6775_probe()` are exported core entry points used by frontend modules.
- `nct6775_show_alarm()`, `nct6775_show_beep()`, and `nct6775_store_beep()` let platform-only attributes reuse core alarm/beep handling.
- `nct6775_write_temp()` hides 8-bit versus 16-bit temperature register differences from store callbacks.
- `nct6775_attr_mode()` strips write bits when a frontend sets `read_only`.
- `nct6775_add_attr_group()` appends generated groups while preserving the NULL terminator required by hwmon registration.

## Control Flow

Frontend drivers allocate `struct nct6775_data`, set initial fields such as `kind`, `driver_data`, `driver_init`, `read_only`, and possibly `addr`/`sioreg`, then call `nct6775_probe()`. The core fills most of the register pointer fields and feature masks based on `kind`, initializes `regmap`, and later uses the inline wrappers for all register access. Platform-only code can call exported alarm/beep helpers after adding its own attribute group.

## State and Persistence Behavior

The header does not implement persistence itself, but it defines every cache and backup field that controls persistence-like behavior in the driver family. `valid` and `last_updated` describe the sensor cache. `bank` caches selected register bank. `vbat`, `fandiv1`, `fandiv2`, and `sio_reg_enable` are used by platform PM restore. `read_only` is a frontend policy bit used to hide writable sysfs modes rather than changing core store function code.

## Dependencies and Integration Points

The header depends on Linux `types.h` and assumes includers also provide regmap and device/sysfs declarations as needed. It is included by `nct6775-core.c`, `nct6775-platform.c`, and `nct6775-i2c.c`. Its exported symbols are namespaced by the core module, and frontends import `HWMON_NCT6775`.

## Risks and Edge Cases

- `struct nct6775_data` mixes frontend-owned fields, core-owned caches, register pointer tables, and PM state; ownership mistakes can be hard to spot.
- Fixed maximum array sizes must stay aligned with all chip-specific register tables in the core.
- `nct6775_add_attr_group()` returns `-ENOBUFS` if group capacity is exceeded; adding a new generated group requires increasing `groups[7]`.
- `nct6775_attr_mode()` only changes permissions; any direct call to store helpers can still attempt writes.
- Word-size decisions live in the core, so the inline register helpers rely on frontends and the core agreeing on logical register width.
- Alarm and beep base constants encode sysfs bit layout assumptions used across core and platform attributes.

## Test Signals

Useful checks include compile coverage for all three includers, group-capacity tests when adding attributes, read-only permission checks, regmap helper error propagation, `nct6775_write_temp()` behavior for 8-bit and word-sized registers, stable sizes for all cached arrays, and consistency of alarm/beep base constants with every `ALARM_BITS` and `BEEP_BITS` table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct6775.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct7363.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/nct7363.c

## Purpose

`nct7363.c` is an I2C hwmon driver for Nuvoton NCT7363/NCT7362 fan controller devices. It configures pin function, PWM enable, and fan tachometer enable state from device-tree child nodes, then exposes up to sixteen fan inputs with minimum/alarm attributes and up to sixteen PWM duty controls through the modern hwmon `read/write/is_visible` interface.

## Important APIs, Types, and Functions

- Register macros such as `NCT7363_REG_FUNC_CFG_BASE()`, `NCT7363_REG_FANINX_HVAL()`, `NCT7363_REG_FANINX_HL()`, and `NCT7363_REG_FSCPXDUTY()` encode the fan/PWM register layout.
- `struct nct7363_data` stores the regmap plus `fanin_mask` and `pwm_mask` discovered from firmware.
- `fan_from_reg()` converts the 13-bit tach count to RPM and treats zero/all-ones as stopped or invalid.
- `nct7363_read_fan()` reads current RPM, minimum RPM, or latch/status alarm bits.
- `nct7363_write_fan()` writes fan minimum thresholds after converting RPM to tach count.
- `nct7363_read_pwm()` and `nct7363_write_pwm()` expose PWM duty registers as 0-255 values.
- `nct7363_is_visible()` delegates to fan/PWM visibility helpers that check the firmware-provided masks.
- `nct7363_init_chip()` writes pin function configuration and enable registers according to the masks.
- `nct7363_present_pwm_fanin()` parses each device-tree child node's `pwms` phandle and `tach-ch` array.
- `nct7363_regmap_is_volatile()` marks live status, fan value/limit, and PWM registers volatile under a maple regcache.
- `nct7363_probe()` initializes regmap, parses children, configures hardware, and registers hwmon.

## Control Flow

I2C probe allocates data and initializes an 8-bit register/8-bit value regmap with single-byte operations and a maple cache. It iterates each child node below the device-tree node. For each child, it parses the first `pwms` entry, marks that PWM channel present, reads the `tach-ch` byte array, validates every channel is below sixteen, and ORs those tach channels into `fanin_mask`.

After parsing firmware, `nct7363_init_chip()` builds a 32-bit pin-function bitmap where each PWM and fan input contributes a pair-bit selection. It writes four function configuration bytes, then writes two PWM-enable bytes and two fanin-enable bytes. Registration with `devm_hwmon_device_register_with_info()` exposes all declared hwmon channels, while `is_visible` hides channels not set in the masks.

Fan reads use `regmap_bulk_read()` of high and low bytes. The current-value path intentionally reads the high byte first because the hardware latches the low byte synchronously after the high-byte access. PWM reads and writes are direct single-register operations.

## State and Persistence Behavior

Driver state is small and mostly static after probe: `fanin_mask` and `pwm_mask` represent firmware-described channel topology, and `regmap` owns register access/cache state. There is no periodic software cache beyond regmap. Probe writes device configuration registers, so pin function and enable state persist in hardware until changed by reset, firmware, or another driver. Fan limits and PWM duty writes persist in device registers. The driver has no PM callbacks or file-backed persistence.

## Dependencies and Integration Points

The driver depends on I2C core, OF child-node parsing, PWM phandle conventions (`pwms` with `#pwm-cells`), a custom `tach-ch` property, regmap with volatile register classification, and Linux hwmon info/ops registration. It binds to `nuvoton,nct7363` and `nuvoton,nct7362` compatible strings.

## Risks and Edge Cases

- If a child node lacks `pwms` or `tach-ch`, probe fails immediately; partial configurations are not tolerated.
- Duplicate child nodes/channels are silently collapsed by ORing masks, so firmware mistakes may be hard to diagnose.
- `nct7363_write_fan()` rejects `val <= 0`, so users cannot disable a fan minimum alarm by writing zero.
- The alarm register macro uses `NCT7363_REG_LSRS(channel)`, which maps by `channel / 8`; tests should verify the status register range and bit mapping for channels 0-15.
- Pin function writes are derived entirely from device tree and can reconfigure pins away from board firmware expectations.
- Regcache volatility must include every register whose value changes asynchronously; missing one would return stale RPM, alarms, or PWM state.

## Test Signals

Tests should cover valid and invalid device-tree child parsing, bounds for PWM and tach channels, duplicate channel behavior, pin-function byte generation, enable-register writes, high-byte-first fan read ordering, 13-bit fan count conversion including zero/all-ones, fan minimum write clamping, PWM duty range checks, alarm bit extraction for both status bytes, visibility masks, and regmap error propagation from bulk and single-register operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct7363.c -->
