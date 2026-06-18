# subset-b-003824 research

Grouped research for hwmon-related Linux drivers under `sources/distributed-fs/ceph-client/drivers/hwmon`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/f71805f.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/f71805f.c

## Purpose
`f71805f.c` is a legacy hwmon driver for Fintek F71805F/FG and F71872F/FG LPC Super-I/O monitoring blocks. It discovers the chip through Super-I/O configuration ports, creates a platform device for the ISA-style I/O region, and exposes voltage, fan, temperature, alarm, and PWM fan-control knobs through classic hwmon sysfs files.

## Important APIs, types, and functions
- `struct f71805f_data` is the runtime cache and synchronization object. It stores the I/O base, chip name, hwmon device pointer, `update_lock`, validity timestamps, voltage/fan/temp values, limit registers, alarm bits, and automatic fan-control points.
- `struct f71805f_sio_data` carries probe-time Super-I/O metadata: chip kind and F71872F function-select bits that decide optional voltage channels.
- Super-I/O helpers `superio_enter()`, `superio_exit()`, `superio_inb()`, `superio_inw()`, and `superio_select()` serialize access to ports `0x2e`/`0x4e` with `request_muxed_region()`.
- Hardware I/O helpers `f71805f_read8()`, `f71805f_write8()`, `f71805f_read16()`, and `f71805f_write16()` access the monitoring register window at `addr + ADDR_REG_OFFSET` and `addr + DATA_REG_OFFSET`. The 16-bit read path intentionally reads the MSB first to latch the LSB.
- Conversion helpers translate raw registers to hwmon units: `in_from_reg()`, `in0_from_reg()`, `fan_from_reg()`, `pwm_freq_from_reg()`, and `temp_from_reg()`, plus inverse setters.
- `f71805f_update_device()` is the central cache refresh path. It refreshes limit/configuration registers every 60 seconds and live readings every second.
- Sysfs show/store callbacks cover voltage limits, fan minimums and targets, PWM duty/frequency/enable, automatic fan points, temperature limits/hysteresis/type, and alarm bits.
- `f71805f_probe()` allocates the data object, claims the I/O subregion, determines channel availability, initializes monitoring, creates sysfs groups, and registers the hwmon device. `f71805f_find()`, `f71805f_device_add()`, `f71805f_init()`, and `f71805f_exit()` implement module discovery and platform-device lifetime.

## Control flow
Module init probes Super-I/O addresses `0x2e` then `0x4e`. `f71805f_find()` checks the Fintek manufacturer ID, optionally honors `force_id`, maps device IDs to `f71805f` or `f71872f`, selects the hardware-monitor logical device, rejects disabled or unaddressed monitors, aligns the I/O base, and returns Super-I/O configuration data. The module then registers a platform driver and adds a single platform device with the I/O resource and platform data.

Probe claims only the address/data register pair inside the 8-byte monitor region, initializes `has_in` according to chip kind and F71872F pin mux settings, calls `f71805f_init_device()` to start monitoring and clear the fan-control latch-full bit, then creates a base attribute group plus optional voltage groups for channels exposed by pin configuration. PWM frequency files are created only for channels configured in PWM mode, and `pwmN` write permission is dynamically enabled only when the fan controller is in manual mode.

Runtime sysfs reads call `f71805f_update_device()` except a few auto-point readers that use the cached values directly. Store callbacks parse user input, clamp or encode it, take `update_lock`, update the matching register, and mirror the new raw value in the cache. Removal unregisters the hwmon device and removes all groups/files that may have been created.

## State and persistence
The driver's persistent external state is the Fintek hardware register set. User writes to limits, PWM settings, fan targets, and auto points immediately program registers and update the in-memory cache. The cache is protected by `update_lock`; live readings expire after one second, while limits/configuration expire after 60 seconds. The driver does not persist settings across reboot itself, but it may change chip state that remains until firmware reset or power cycle.

`pwmN` sysfs writability is stateful: `set_pwm_enable()` removes write permission when switching to automatic mode and restores it when switching to manual mode. A global `pdev` pointer tracks the sole created platform device for module exit.

## Dependencies and integration points
This driver integrates with the platform bus, classic `hwmon_device_register()`, manual `hwmon-sysfs` attributes, LPC/Super-I/O port I/O, ACPI resource conflict checks, and kernel mutex/jiffies helpers. It depends on direct x86-style I/O port access through `outb()`/`inb()` and on Fintek-specific register layouts. The `force_id` module parameter can override device identification.

## Risks
- Direct port I/O and Super-I/O unlock sequences are hardware-sensitive; incorrect probing can conflict with firmware or another Super-I/O driver despite muxed-region use.
- `force_id` can bind the driver to an incompatible Fintek device and cause incorrect register access.
- The manual sysfs creation path has many conditional files. Error cleanup removes broad groups, which is intended but makes partial-creation correctness important.
- Auto-point show functions do not call `f71805f_update_device()`, so they may expose stale values until another path refreshes limits or after writes in the same driver update the cache.
- PWM write permission changes rely on `sysfs_chmod_file()` succeeding. Failure only logs debug messages for some transitions, so user-visible permissions may temporarily disagree with controller mode.
- Fan conversion returns zero for unmeasurable or saturated values; tests should distinguish stopped fans, low limits below detection, and register saturation.

## Test signals
- Build coverage with `CONFIG_SENSORS_F71805F` catches hwmon/sysfs API drift and direct I/O helper changes.
- On hardware or emulation, verify Super-I/O detection at both config ports, `force_id` behavior, ACPI conflict rejection, and disabled monitor handling.
- Sysfs tests should check channel presence for F71805F vs F71872F, optional `in4`/`in8` pin-mux channels, `in9`/`in10`, PWM frequency-file creation only in PWM mode, and dynamic `pwmN` writability across `pwmN_enable` transitions.
- Register-level tests should validate unit conversions and clamping for voltage, temperature, fan RPM, PWM frequency, and auto-point settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/f71805f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/f71882fg.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/f71882fg.c

## Purpose
`f71882fg.c` supports a broad family of Fintek Super-I/O hardware monitors including F71808, F71858, F71862, F71868, F71869, F71882, F71889, F8000, F81768D, F81865, F81866, F81966, and F81968-compatible devices. It exposes per-chip voltage, temperature, fan, PWM, beep, alarm, and automatic fan-curve controls through manually-created hwmon sysfs files.

## Important APIs, types, and functions
- `enum chips` enumerates all supported register-compatible variants, and capability tables such as `f71882fg_has_in`, `f71882fg_nr_fans`, `f71882fg_nr_temps`, and beep/alarm support arrays drive sysfs creation.
- `struct f71882fg_data` stores I/O base, chip type, hwmon device, cache timestamps, temperature numbering offset, signed auto-point policy, and raw caches for voltage, fan, temp, beep, PWM, and auto-point registers.
- `f71882fg_read8()`, `f71882fg_read16()`, `f71882fg_write8()`, and `f71882fg_write16()` operate on the ISA-style monitor register window.
- `f71882fg_update_device()` refreshes slow limit/configuration registers every 60 seconds and live status/readings every second, with variant-specific handling for F71858FG 16-bit temperatures, F8000 temperature semantics, and F81866 voltage alarm registers.
- Sysfs helpers implement temperature thresholds and hysteresis, voltage readings and in1 alarm/beep, fan full-speed programming, PWM duty vs RPM mode conversion, automatic PWM channel mapping, interpolation, auto-point PWM/temp/hysteresis, and beep controls.
- `f71882fg_create_sysfs_files()`, `f71882fg_remove_sysfs_files()`, and `f71882fg_create_fan_sysfs_files()` encapsulate the large conditional sysfs matrix.
- Super-I/O discovery is handled by `f71882fg_find()`, which validates manufacturer ID, maps device IDs to chip variants, selects the correct logical device, checks activation, and returns the monitor I/O base as a positive integer.

## Control flow
Module init zeroes `struct f71882fg_sio_data`, probes Super-I/O address `0x2e` then `0x4e`, registers the platform driver, and creates one platform device with the discovered I/O resource. Probe allocates `struct f71882fg_data`, sets the temperature index base for chips whose temp channels start at zero, reads the start register, rejects powered-down or inactive monitors, and creates `name`.

If temperature/voltage monitoring is enabled, probe creates chip-specific temperature attributes, optional temperature beep attributes, voltage input attributes for channels marked present in `f71882fg_has_in`, and in1 alarm/beep attributes where supported. If fan monitoring is enabled, it handles signed auto-point temperature setup, clears the bank select bit on affected chips, reads `pwm_enable`, creates per-fan base files, validates reserved PWM modes, conditionally suppresses unsupported auto-point files, adds variant-specific auto-PWM arrays, and adds limited-function extra fan files for F71808A/F8000. Finally it registers the hwmon class device.

Runtime reads funnel through `f71882fg_update_device()` and then decode raw cached registers. Writes usually reread the controlling register under `update_lock`, update one bitfield or register, write it back, and mirror the cache. On probe failure the driver calls its own remove routine to undo whatever sysfs files were created. Remove reads the start register to decide which groups may exist, unregisters hwmon, removes `name`, and removes the broad set of possible per-feature files for the variant.

## State and persistence
The driver maintains a one-second cache for measurements/status and a 60-second cache for limits, beep masks, PWM mode bits, auto-point registers, and temperature type/hysteresis. User writes persist in the chip register state and update cached copies. `auto_point_temp_signed` is probe-time state derived from chip type or the negative-temperature enable bit. `temp_start` normalizes zero-based vs one-based channel numbering across variants.

PWM state is multi-dimensional. `pwm_enable` encodes automatic/manual and PWM/RPM mode in two bits per fan; F8000 uses special thermostat semantics. In RPM mode, some sysfs PWM values are presented as 0..255 percentages but stored as target RPM or inverse encoded auto-point values. The driver does not save state across reboot.

## Dependencies and integration points
The file integrates with platform devices, classic hwmon registration, manual hwmon sysfs attributes, direct LPC/Super-I/O port I/O, ACPI resource conflict checks, and module parameter parsing. It depends heavily on Fintek device IDs, logical-device numbers, and per-variant register compatibility tables. Userspace integration is the standard hwmon sysfs ABI, including legacy compatibility choices such as `temp#_alarm` naming for max alarms.

## Risks
- The chip-variant matrix is large; incorrect capability tables or removal counts can expose nonexistent registers or leave sysfs files behind.
- `force_id` can override detection and make the driver use the wrong register layout.
- F8000, F71858FG, and F81866A have special temperature/alarm register semantics; regressions there are easy if common paths are simplified.
- Several writes return `-EROFS` or `-EINVAL` based on current mode bits. Tests must cover mode-dependent writability, not only parsing.
- Auto-point mapping can be disabled when controlled by raw digital data. Users may see fan controls without auto-point controls depending on hardware state.
- `show_pwm_auto_point_channel()` shifts by a value derived from register mapping; invalid mappings are screened in sysfs creation for some chips but remain a class of hardware-state risk.
- Removal uses broad array removals, while creation may skip files for reserved modes or unsupported mappings. The kernel tolerates missing removes, but maintainers should be cautious changing attribute arrays.

## Test signals
- Compile with `CONFIG_SENSORS_F71882FG` and run sparse/smatch-style checks for table bounds and signed/unsigned conversions.
- Hardware tests should cover at least one standard F7188x, F71858FG, F8000, and F81866-family path.
- Probe tests should validate Super-I/O manufacturer/device detection, disabled logical-device handling, ACPI conflicts, powered-down/inactive start-register states, and `force_id`.
- Sysfs tests should verify variant-specific channel counts, F8000 temp max/hyst semantics, F81866 in/temp beep bit numbering, reserved PWM mode skipping, beep mask writes, and mode-dependent PWM writes.
- Conversion tests should cover fan register zero, `FAN_MIN_DETECT`, fan full-speed scaling, signed auto-point temperatures, and RPM-mode auto-point PWM inverse encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/f71882fg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/f75375s.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/f75375s.c

## Purpose
`f75375s.c` is an I2C hwmon driver for Fintek F75373, F75375, and F75387 hardware monitoring chips. It exposes four voltage inputs, two temperature channels, two fan tachometers, fan limits/targets, and PWM control modes through classic sysfs attributes.

## Important APIs, types, and functions
- `struct f75375_data` stores the hwmon device, chip kind, cache validity and timestamps, voltage limits, fan readings and limits, PWM mode/enable state, fan timer, and signed 11-bit temperature readings used by F75387.
- I2C helpers `f75375_read8()`, `f75375_read16()`, `f75375_write8()`, `f75375_write16()`, and `f75375_write_pwm()` wrap SMBus byte-data access. F75387 writes PWM through `F75375_REG_FAN_EXP`, while older chips use the PWM duty register.
- `f75375_update_device()` refreshes limit registers every 60 seconds and measurement registers every two seconds. It merges F75387 temperature LSB registers for signed 11-bit temperature values.
- Mode helpers `duty_mode_enabled()` and `auto_mode_enabled()` normalize the driver-visible `pwm_enable` values.
- Store callbacks enforce mode restrictions: `set_fan_target()` refuses automatic mode and F75387 duty mode, `set_pwm()` refuses automatic or speed modes, `set_pwm_enable_direct()` programs chip-specific fan timer bits, and `set_pwm_mode()` toggles PWM/DC mode where supported.
- `f75375_init()` derives initial mode state from hardware or applies optional `struct f75375s_platform_data` defaults.
- `f75375_detect()` validates vendor ID `0x1934`, chip IDs, and fills the I2C board info name.

## Control flow
The I2C core scans addresses `0x2d` and `0x2e` for class `I2C_CLASS_HWMON`. Detect reads vendor/chip/version registers and selects the chip name. Probe checks SMBus byte-data functionality, allocates data, records the matched chip kind, creates the fixed attribute group, makes `pwmN_mode` writable for chips other than F75373, registers hwmon, and calls `f75375_init()`.

At runtime, all show callbacks call `f75375_update_device()`, then convert cached values to hwmon units. Store callbacks parse input, validate against current mode and chip kind, lock `update_lock`, write the relevant register, and update the cache. Remove unregisters hwmon and removes the fixed group.

## State and persistence
The data cache has separate slow and fast refresh periods. Hardware register writes persist in the chip until reset or firmware changes them. `pwm_enable[]` and `pwm_mode[]` are initialized either from existing hardware state or platform data, then updated by sysfs writes. F75387 mode changes deliberately refuse transitions that would toggle duty-mode state because that is considered dangerous.

## Dependencies and integration points
The driver uses the I2C subsystem, `module_i2c_driver()`, classic `hwmon_device_register()`, manual hwmon sysfs attributes, optional platform data from `<linux/f75375s.h>`, and SMBus byte-data transactions. It exports a standard hwmon ABI for in, temp, fan, and pwm files.

## Risks
- `set_fan_target()` and `set_pwm()` check `data->pwm_enable[nr]` before taking `update_lock`; stale cached mode could briefly disagree with hardware if another agent changes registers.
- `f75375_write16()` returns early after a failed high-byte write but most callers ignore write errors, so hardware write failures may only partially update state or leave the cache optimistic.
- F75387 uses signed 11-bit temperatures and different fan-timer bit positions; mistakes in kind handling will produce wrong units or unsafe fan mode writes.
- The driver exposes all fixed attributes regardless of board wiring; absent sensors may read as chip-defined defaults rather than being hidden.
- F75373 does not support DC mode, so tests must verify `pwmN_mode` write permissions and `-EINVAL` for unsupported values.

## Test signals
- Build with `CONFIG_SENSORS_F75375S` and test against I2C adapters with and without `I2C_FUNC_SMBUS_BYTE_DATA`.
- Detection tests should cover vendor mismatch, unknown chip IDs, and names for F75373/F75375/F75387.
- Sysfs tests should cover voltage/temp conversion and clamping, fan RPM zero/saturation cases, `pwm_enable` values 0..4, F75373 DC-mode rejection, and F75387 duty-mode transition rejection.
- Platform-data tests should confirm initial PWM enable/duty application only when the configured mode allows direct PWM writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/f75375s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/fam15h_power.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/fam15h_power.c

## Purpose
`fam15h_power.c` is a PCI hwmon driver for AMD Family 15h/16h northbridge function 4 devices. It exposes processor power limit, current socket power on supported Family 15h models, and accumulated compute-unit average power when the CPU advertises accumulated power MSR support.

## Important APIs, types, and functions
- `struct fam15h_power_data` stores the PCI device, fixed-point TDP scaling values, dynamically assembled hwmon attribute group, accumulated power MSR state per compute unit, online compute-unit flags, and the averaging interval.
- `power1_input_show()` reads D18F5 `REG_TDP_RUNNING_AVERAGE` and `REG_TDP_LIMIT3`, handles Carrizo-or-later bitfield widths, and reports current power in microwatts.
- `power1_crit_show()` reports processor TDP-derived critical power in microwatts.
- `do_read_registers_on_cu()` reads `MSR_F15H_CU_PWR_ACCUMULATOR` and `MSR_F15H_PTSC` on a representative CPU for a compute unit.
- `read_registers()` builds a cpumask containing one online CPU per compute unit and uses `on_each_cpu_mask()` under `cpus_read_lock()` to sample MSRs.
- `power1_average_show()` takes two MSR snapshots separated by `power_period` milliseconds, handles accumulator wrap, divides by PTSC delta, and sums online compute-unit power.
- `fam15h_power_init_attrs()` conditionally includes attributes based on CPU family/model and `X86_FEATURE_ACC_POWER`.
- `should_load_on_this_node()` avoids duplicate hwmon registration on secondary nodes when northbridge capability bits indicate it should not load.
- `tweak_runavg_range()` applies a BIOS workaround by changing running-average range from `0xe` to `0x9` on affected devices, and resume reapplies it.

## Control flow
The PCI driver matches AMD Family 15h and 16h northbridge function 4 device IDs. Probe first calls `tweak_runavg_range()` for every node because the counters cooperate across MCM nodes. It then filters duplicate nodes with `should_load_on_this_node()`, allocates data, initializes TDP/scaling data and attributes, saves the PCI device pointer, and registers a managed hwmon device with the generated groups.

If accumulated power is supported, initialization reads CPUID `0x80000007` ECX for sample ratio, reads the max CU accumulator MSR, sets a default 10 ms averaging interval, and samples initial registers. `power1_average` reads block for the configured interval using `schedule_timeout_interruptible()` before returning a computed average.

## State and persistence
Most state is derived from PCI config space and CPU MSRs at read time. `power1_average_interval` is mutable driver state in milliseconds, constrained to 1..1000, and affects subsequent `power1_average` reads. `tweak_runavg_range()` writes PCI config space and is re-run on resume. Accumulator snapshots are stored in `fam15h_power_data` only as transient samples.

## Dependencies and integration points
The driver depends on the PCI core, AMD northbridge function layout, x86 CPU topology helpers, CPUID feature bits, MSR access, CPU hotplug read locking, scheduler timeouts, and managed hwmon registration. It exports the standard power hwmon ABI: `power1_crit`, optionally `power1_input`, `power1_average`, and `power1_average_interval`.

## Risks
- `power1_average_show()` can block sysfs reads for up to one second by design; tests and userspace pollers must account for that.
- If CPUs go offline between the two samples, the code skips compute units not online in the second sample; averages can change abruptly around hotplug.
- Division by `tdelta` assumes PTSC advanced; unusual platform behavior could risk divide errors or invalid readings.
- Attribute availability depends on boot CPU family/model and feature bits, while PCI IDs include Family 16h devices. Wrong gating can expose unsupported registers or hide valid ones.
- `tweak_runavg_range()` mutates PCI config space as a firmware workaround; regressions can alter power management behavior.
- `power1_input_show()` uses bitfield widths that differ for Carrizo-or-later; incorrect model detection changes sign extension and scaling.

## Test signals
- Build on x86 with relevant PCI/MSR headers and verify no attribute-array sizing issues in `fam15h_power_init_attrs()`.
- Hardware tests should compare `power1_crit` against expected processor TDP scaling and validate `power1_input` on pre-Carrizo and Carrizo-or-later Family 15h models.
- Accumulated-power tests should read `power1_average` at multiple intervals, around CPU hotplug events, and with interrupted sleeps.
- Resume tests should confirm `REG_TDP_RUNNING_AVERAGE` is retweaked when needed.
- Negative tests should cover non-primary northbridge nodes and CPUs lacking `X86_FEATURE_ACC_POWER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/fam15h_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/fschmd.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/fschmd.c

## Purpose
`fschmd.c` is a merged Fujitsu Siemens/Fujitsu hwmon driver for Poseidon, Hermes, Scylla, Heracles, Heimdall, Hades, and Syleus system-monitoring chips at I2C address `0x73`. It exposes voltage, temperature, fan, PWM minimum, alert LED, and a legacy watchdog character device.

## Important APIs, types, and functions
- `enum chips` maps seven chip families to dense table indexes. Large register tables define per-chip voltage, fan, temperature, and watchdog register addresses and sensor counts.
- `struct fschmd_data` contains the I2C client, hwmon device, update and watchdog locks, watchdog miscdevice/list/kref lifetime state, chip kind, cached global/watchdog registers, and raw sensor caches.
- Sysfs callbacks cover scaled voltage reads, temperature input/max/fault/alarm, fan RPM/div/alarm/fault, PWM auto point 1 minimum duty, and `alert_led`.
- Watchdog helpers `watchdog_set_timeout()`, `watchdog_get_timeout()`, `watchdog_trigger()`, and `watchdog_stop()` program watchdog preset/control registers with 2-second or 60-second resolution depending on timeout and chip kind.
- Watchdog file operations implement single-open exclusion, magic-close handling with `V`, keepalive writes, and standard watchdog ioctls.
- `fschmd_dmi_decode()` parses OEM DMI type 185 subtype 19 records to override voltage multipliers, offsets, and reference voltage for newer FSC systems.
- `fschmd_detect()` reads three identification bytes and maps signatures such as `PEG`, `HER`, `SCY`, `HRC`, `HMD`, `HDS`, and `SYL` to I2C board names.
- `fschmd_update_device()` refreshes sensor state every two seconds, resets latched temp/fan alarms when conditions have cleared, and caches voltages.

## Control flow
The I2C driver scans address `0x73`. Detect checks SMBus byte-data support and signature bytes. Probe allocates a non-devm data object because watchdog file descriptors can outlive I2C client removal. It initializes locks/list/kref, stores the client for watchdog operations, seeds hardwired Poseidon temp limits, optionally parses DMI scaling for newer chips, reads immutable revision/global/watchdog registers, and creates sysfs files according to per-chip sensor counts.

For Syleus, probe reads temp/fan status before creating attributes and skips disabled sensors. Poseidon skips unavailable temp-limit and third fan-min/PWM files. After hwmon registration, probe registers one watchdog miscdevice on the first available minor from the legacy watchdog minor list while holding `watchdog_data_mutex`, adds the device to a global list, and sets a default 60-second timeout.

Watchdog open locates the data object by misc minor under a trylock to avoid deadlock with misc registration, enforces single-open, takes a kref, triggers the watchdog, and stores data in `filp->private_data`. Release stops only after a magic close when `nowayout` is false; otherwise it retriggers and logs a critical unexpected-close message. Remove deregisters the miscdevice, stops an open watchdog, removes the global-list entry, nulls `data->client` under `watchdog_lock`, unregisters hwmon, removes sysfs files, and drops the final kref.

## State and persistence
Sensor cache state expires after two seconds and is protected by `update_lock`. Writes to temp limits, fan dividers, PWM minimums, alert LED, and watchdog registers update hardware and local cache. Voltage scaling globals are process-wide and initialized once from DMI or defaults. Watchdog state spans the I2C device and open file descriptors through `kref`; `data->client = NULL` prevents further hardware access after detach. The `nowayout` module parameter controls whether magic close can stop the watchdog.

The driver actively clears latched alarms by writing status registers when readings indicate the alarm condition is gone. This makes reads state-changing.

## Dependencies and integration points
The driver integrates with I2C hwmon scanning, classic manual hwmon sysfs files, DMI table walking, the legacy miscdevice watchdog ABI, watchdog ioctl constants, `uaccess`, `kref`, mutexes, and global module parameters. Userspace sees both hwmon sysfs and `/dev/watchdog*` style misc devices.

## Risks
- Watchdog lifetime is complex: data is manually allocated, referenced by global list and file descriptors, and decoupled from the I2C client on removal. Lock ordering and kref changes are high risk.
- `watchdog_open()` assumes the misc minor always maps to a data object after list traversal. If that invariant is broken, a null dereference would follow.
- Some sysfs reads clear latched alarms, so passive monitoring has side effects.
- DMI voltage scaling is global and reused across devices; unexpected DMI records or multiple board variants could produce wrong voltage units.
- `watchdog_release()` logs through `data->client->dev` even after detach would be dangerous, but removal stops and nulls client only after deregistering and handling open state. This path should remain carefully ordered.
- Many `i2c_smbus_write_byte_data()` calls do not check return values, so hardware I/O failures may leave caches optimistic.
- Syleus disabled sensor filtering happens during creation but removal tries all possible files, which relies on safe missing-file removal.

## Test signals
- Build with `CONFIG_SENSORS_FSCHMD` and watchdog/miscdevice support.
- Detection tests should cover all signature strings and SMBus functionality failure.
- Sysfs tests should validate per-chip sensor counts, Poseidon skipped limit/PWM files, Syleus disabled sensors, DMI voltage scaling, temperature/fan alarm clearing behavior, and fan divider accepted values 2/4/8.
- Watchdog tests should cover single-open behavior, keepalive writes, magic close vs `nowayout`, timeout resolution boundaries, `WDIOC_*` ioctls, misc minor fallback, removal while watchdog is open, and operations after client detach returning `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/fschmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ftsteutates.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ftsteutates.c

## Purpose
`ftsteutates.c` is an I2C hwmon and watchdog driver for the Fujitsu Technology Solutions Teutates system-monitoring chip, a baseboard management controller at address `0x73`. It exposes sixteen temperature channels, eight fan channels, four voltage inputs, fan-to-temperature source mappings, clearable alarms, and a managed watchdog.

## Important APIs, types, and functions
- `struct fts_data` stores the I2C client, hwmon cache timestamp/valid bit, watchdog device, watchdog resolution, voltage/temp/fan caches, fan source mappings, and alarm/presence bitmasks.
- `fts_read_byte()` and `fts_write_byte()` implement paged register access. The high byte of the 16-bit register selects the page through `FTS_PAGE_SELECT_REG`; the low byte is then read or written.
- `fts_update_device()` refreshes data every two seconds after checking the device-ready bit in `FTS_DEVICE_STATUS_REG`. It reads fan presence, fan alarms, present fan speeds/sources, temperature alarms, all temperature inputs, and all voltages.
- Watchdog functions `fts_wd_set_resolution()`, `fts_wd_set_timeout()`, `fts_wd_start()`, `fts_wd_stop()`, and `fts_watchdog_init()` integrate the chip with the kernel watchdog framework using `devm_watchdog_register_device()`.
- `fts_is_visible()`, `fts_read()`, and `fts_write()` implement the modern `hwmon_ops` API rather than manual sensor attributes.
- `fts_detect()` and `fts_probe()` validate revision, detect-register magic values, I2C address, and BMC device ID before registering hwmon and watchdog.

## Control flow
The I2C driver scans `0x73`. Detect accepts revisions at least `0x2b`, requires detect registers `0x17`, `0x34`, `0x54`, and requires device ID `0x11`. Probe independently rejects non-`0x73` clients and device IDs whose high nibble is not BMC `0x10` or whose low nibble is not Teutates `0x01`. It allocates managed data, reads revision, registers hwmon with `devm_hwmon_device_register_with_info()`, initializes the watchdog, and logs the detected revision.

All hwmon reads call `fts_update_device()` first. Temperature input is decoded as `(raw - 64) * 1000`, fan input as revolutions per second times 60, voltages as raw values scaled to 3300 mV, fan faults from presence bits, and temp faults from zero temperature readings. Writes are limited to clearing temp/fan alarms by writing bit 0 to the channel control register; attempts to write nonzero alarm values return `-EINVAL`.

The watchdog init path reads the current preset. If zero, it configures seconds resolution and defaults to 60 seconds. If nonzero, it reads the control register, derives seconds vs minutes resolution, sets the timeout, and marks the watchdog hardware running.

## State and persistence
The hwmon cache expires every two seconds and is invalidated after alarm-clear writes. The chip can report data not ready; in that case `fts_update_device()` returns `-EAGAIN`. Watchdog timeout and resolution live both in `struct watchdog_device` and chip registers. Starting writes the preset divided by the current resolution, while stopping writes preset zero. Managed registration ties hwmon and watchdog cleanup to the device lifetime.

## Dependencies and integration points
The driver depends on I2C SMBus byte-data operations, the modern hwmon channel-info API, the kernel watchdog framework, jiffies, math helpers, and managed device allocation. It exposes standard hwmon channel types (`temp`, `fan`, `pwm`, `in`) and a standard watchdog device.

## Risks
- Every register access changes the page select register; concurrent non-driver accesses to the chip could observe or disturb page state.
- `fts_update_device()` has no explicit mutex around cache refresh or page-select/read sequences, so concurrent hwmon reads can interleave I2C transactions through the adapter. The I2C core serializes individual transfers, but not the logical page-select plus register operation as a higher-level critical section.
- `data->valid = !!(err & 0x02)` is documented as "Data not ready yet"; if the hardware bit semantics are inverted or unclear, reads may return `-EAGAIN` unexpectedly.
- Alarm writes only support clearing. Userspace writing `1` gets `-EINVAL`, which should be reflected in tests.
- The watchdog resolution bit logic is subtle: timeouts over 255 seconds are rounded up to whole minutes and resolution changes are persisted in hardware.

## Test signals
- Build with `CONFIG_SENSORS_FTSTEUTATES` and watchdog support.
- Detection tests should cover bad revision, bad detect-register magic, wrong address, non-BMC IDs, and unsupported BMC subtypes.
- Hwmon tests should cover ready vs not-ready status, absent fans, invalid fan source mapping, temperature zero fault, alarm clearing, and voltage scaling.
- Watchdog tests should cover stopped hardware default timeout, already-running hardware, seconds/minutes resolution switching, timeout rounding over 255 seconds, max heartbeat, start/stop, and magic-close support through the watchdog core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ftsteutates.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/g760a.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/g760a.c

## Purpose
`g760a.c` is a compact I2C hwmon driver for the GMT G760A fan speed PWM controller. It exposes one writable PWM output, one fan tachometer input, and one fan alarm bit.

## Important APIs, types, and functions
- `enum g760a_regs` names the three chip registers: set count, actual count, and fan status.
- `struct g760a_data` stores the I2C client, update mutex, board parameters (`clk` and `fan_div`), and cached register values.
- `rpm_from_cnt()` converts tachometer count to RPM with `clk * 30 / (cnt * div)`, returning zero for count zero.
- `PWM_FROM_CNT()` and `PWM_TO_CNT()` invert the chip count encoding where `0xff` stops the fan and hwmon PWM uses 0..255 duty-style values.
- `g760a_update_client()` refreshes the three registers at most once per second.
- Sysfs callbacks implement `fan1_input`, `fan1_alarm`, and `pwm1`.
- `g760a_probe()` verifies SMBus byte-data support, allocates managed data, sets default clock/divider values, and registers a managed hwmon device with static groups.

## Control flow
Probe is invoked for an explicitly instantiated I2C device ID `g760a`. It requires `I2C_FUNC_SMBUS_BYTE_DATA`, allocates state, initializes `update_lock`, sets defaults of 32768 Hz clock and fan divider 2, and registers hwmon groups. Runtime reads call `g760a_update_client()` and decode cached registers. `pwm1_store()` refreshes the cache, parses/clamps 0..255, converts to count, writes `G760A_REG_SET_CNT`, and updates the cache.

## State and persistence
The driver caches all three registers for one jiffy interval of one second (`HZ`) and protects refresh and writes with `update_lock`. Board parameters are currently fixed defaults and are not loaded from firmware or platform data. PWM writes persist in the chip register; there is no driver-level persistence across reboot.

## Dependencies and integration points
The driver integrates with the I2C core, SMBus byte-data access, managed hwmon registration with static `ATTRIBUTE_GROUPS`, mutexes, and jiffies. It exposes standard hwmon sysfs names but does not implement auto-detection or firmware configuration.

## Risks
- The default clock and divider may be wrong for boards wired differently, causing incorrect RPM calculations.
- `g760a_update_client()` stores negative SMBus errors into `u8` cache fields because it does not check read return values. A transient I2C error can be misreported as a valid raw value.
- `g760a_write_value()` errors are ignored by `pwm1_store()`, so sysfs can report success after a failed hardware write.
- `fan1_input` reports zero when the low-RPM status bit is set, even if `act_cnt` contains a nonzero value.

## Test signals
- Build with `CONFIG_SENSORS_G760A` and instantiate a dummy I2C client.
- Sysfs tests should verify PWM inversion, clamping, alarm bit decoding, low-RPM zero behavior, and cache refresh after one second.
- Fault-injection tests should cover SMBus read/write failures, because the current code does not propagate them.
- Board-level validation should compare RPM output against known clock/divider wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/g760a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/g762.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/g762.c

## Purpose
`g762.c` is an I2C hwmon driver for GMT G761/G762/G763 fan controller chips. It supports open-loop PWM/DC output, closed-loop RPM targets, tachometer readings, fan fault/alarm reporting, fan clock divisors, pulses per revolution, gear mode, startup voltage, PWM polarity, optional device-tree clock handling, and platform-data configuration.

## Important APIs, types, and functions
- `struct g762_data` stores the I2C client, optional external clock, internal-clock flag, update mutex, clock frequency, cached register values, and cache timestamp.
- Register bit macros decode `FAN_CMD1` and `FAN_CMD2`, including output mode, closed/open loop, clock divisor, PWM polarity, pulses per revolution, gear multiplier, startup voltage, failure detection, and G761 internal clock.
- `rpm_from_cnt()` and `cnt_from_rpm()` convert between controller counts and RPM using clock frequency, pulses per revolution, clock divisor, and gear multiplier. Count `0xff` means stop.
- `g762_update_client()` reads all six controller registers at most once per second and returns an `ERR_PTR()` on I2C read failure.
- `do_set_*()` helpers update individual hardware parameters: clock frequency, PWM/DC mode, fan divisor, gear mode, pulses, open/closed-loop enable, polarity, raw PWM, target RPM, and startup voltage.
- Device-tree helpers under `CONFIG_OF` enable and manage the input clock, support G761 internal-clock mode when no clock is provided, and import `fan_gear_mode`, `pwm_polarity`, and `fan_startv`.
- `g762_pdata_prop_import()` imports the same configuration from `struct g762_platform_data`.
- Sysfs callbacks expose `fan1_input`, `fan1_alarm`, `fan1_fault`, `fan1_target`, `fan1_div`, `fan1_pulses`, `pwm1`, `pwm1_mode`, and `pwm1_enable`.

## Control flow
Probe requires SMBus byte-data support, allocates managed state, stores the client, and initializes `update_lock`. It then enables/configures the clock from device tree, calls `g762_fan_init()` to read current registers and enable fan-fail/out-of-control detection, imports device-tree properties, imports platform data if present, and registers managed hwmon groups.

Runtime reads go through `g762_update_client()` and convert cached values. Writes parse user input and call a `do_set_*()` helper, which refreshes the cache if needed, modifies the relevant bitfield under `update_lock`, writes the register, and invalidates the cache. `pwm1_enable` maps hwmon values 1 and 2 to open-loop/manual and closed-loop/automatic; value 0 is rejected because the chip does not natively support a no-control full-speed mode. When switching to open-loop, the driver writes `SET_CNT = 254` if it was `255` to work around a chip behavior where the fan may not rotate from stopped count in PWM mode.

## State and persistence
The register cache expires after one second and is invalidated after writes. `clk_freq` is driver-side board configuration used in RPM math and is not written to the chip. Device-tree clock enablement is managed with a devm cleanup action that disables and puts the clock on teardown. Configuration writes change chip registers and remain until reset or another agent changes them.

## Dependencies and integration points
The driver integrates with I2C SMBus byte-data, classic hwmon sysfs attribute groups, optional OF matching for `gmt,g761`, `gmt,g762`, and `gmt,g763`, common clock framework APIs, platform data from `<linux/platform_data/g762.h>`, and managed hwmon registration.

## Risks
- Clock frequency is central to RPM conversion. Missing/wrong DT clocks, G761 internal-clock assumptions, or platform-data values produce wrong fan speeds and targets.
- `G762_GEARMULT_FROM_REG()` returns `1 << bits`, so the reserved `11b` encoding becomes 8 even though comments describe only 1/2/4. If hardware can expose that value, RPM math may be wrong.
- `fan1_input_show()` treats the out-of-control bit with reverse logic based on comments; polarity mistakes would invert zero-vs-RPM reporting.
- Several setters write registers after modifying cached values and invalidate the cache, but some return paths may leave cache fields changed if writes fail.
- Device-tree and platform-data imports both run; platform data can override DT-derived properties if both are present.
- The open-loop workaround changes `SET_CNT` as a side effect of `pwm1_enable`, which tests must expect.

## Test signals
- Build with and without `CONFIG_OF` to cover both helper implementations.
- Probe tests should cover SMBus functionality failure, missing/bad clocks, G761 internal clock without `clocks`, managed clock cleanup, and platform-data import.
- Sysfs tests should validate allowed values for `pwm1_mode`, `pwm1_enable`, `fan1_div`, `fan1_pulses`, `fan1_target`, `pwm1`, and invalid-value rejection.
- Conversion tests should cover `cnt == 0xff`, zero RPM target, clock divisors 1/2/4/8, pulses 2/4, gear modes 0/1/2, and rounding behavior.
- Hardware tests should verify failure and out-of-control detection bits, especially the documented active-low OOC semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/g762.c -->
