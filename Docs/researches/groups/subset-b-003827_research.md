# subset-b-003827 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/it87.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/it87.c

## Purpose
`it87.c` is a legacy-style hwmon driver for ITE IT87-family LPC Super-I/O environment controllers. It discovers up to two Super-I/O instances at configuration ports `0x2e` and `0x4e`, registers platform devices for the Environment Controller I/O window, and exposes voltage, temperature, fan tachometer, fan PWM, alarm, beep, and VID attributes through hwmon sysfs groups. It supports many chip variants through a feature table rather than separate drivers.

## Important APIs, types, and functions
Key kernel integrations are raw port I/O (`inb`, `outb`, `request_muxed_region`), platform device registration, ACPI resource conflict checking, DMI matching, hwmon sysfs helpers, and VID conversion helpers. `struct it87_devices` records per-chip feature flags and register quirks. `struct it87_sio_data` carries Super-I/O detection results into the platform device. `struct it87_data` is the runtime cache and lock-protected state for one hwmon instance.

Important functions include `it87_find()` for Super-I/O discovery and board pin-mux interpretation, `it87_device_add()` for platform resource creation, `it87_probe()` for EC validation and hwmon registration, `it87_init_device()` for monitor enablement and fan/PWM setup, `it87_update_device()` for periodic register caching, and `it87_resume()` for suspend/resume reinitialization. Sysfs accessors handle voltage (`show_in`, `set_in`), temperature (`show_temp`, `set_temp`, temp type), fan (`show_fan`, `set_fan`, divisors), PWM/manual/automatic fan control, alarms, beeps, intrusion clear, and VID.

## Control flow
Module init registers the platform driver, applies DMI quirks, probes both Super-I/O addresses, and creates platform devices for found chips with nonzero EC base addresses. `it87_find()` first reads the chip ID without entering configuration mode, then conditionally enters config mode, maps IDs to `enum chips`, reads revision and GPIO/pin-mux registers, determines skipped sensors, captures SMBus disable bits, and exits carefully for `FEAT_NOCONF` chips.

At probe time the driver requests the EC I/O subrange, disables overlapping SMBus access if required, validates the environment controller via config/chip ID registers, checks PWM safety, computes enabled voltage/temp/fan masks, initializes monitor registers, then registers conditional hwmon attribute groups. Reads call `it87_update_device()`, which refreshes cached registers at roughly 1.5 second intervals. Writes acquire `it87_lock()`, temporarily disable SMBus if needed, write hardware registers, update cached values, and release through `it87_unlock()`.

## State and persistence
State is mostly hardware-resident. The driver caches sensor values, limits, alarm bits, beep masks, fan control registers, PWM mappings, automatic trip tables, VID, and conversion metadata in `struct it87_data`. Cache validity is time based and invalidated by writes that change sensor routing or monitor semantics. Several writes persist directly in Super-I/O or EC registers until firmware, suspend, reset, or another driver changes them. Resume re-routes VIN7 when needed, restores monitoring setup, validates limits, re-enables tachometers, restarts monitoring, and forces a refresh.

## Dependencies and integration points
The driver depends on x86-style Super-I/O LPC port access, ACPI resource arbitration, DMI board data, and hwmon sysfs ABI compatibility. It integrates with the platform bus only after manual discovery; there is no firmware-enumerated device node. It also coordinates with a possible SMBus interface by temporarily clearing chip-specific SMBus bits in Super-I/O config space while doing EC I/O.

## Risks
The largest risk is hardware side effects from raw Super-I/O access: wrong chip IDs, force-loading, incorrect pin-mux assumptions, or PWM polarity changes can disable fans or touch unrelated functions. `fix_pwm_polarity` is explicitly dangerous. Ignoring ACPI conflicts can race firmware-owned regions. The chip table embeds many undocumented or board-specific assumptions, so regressions can appear only on rare ITE variants. Cache coherency relies on the driver being the only active writer apart from firmware. Automatic fan control trip validation prevents some bad transitions but cannot verify board cooling safety.

## Test signals
Useful tests are module load/unload on representative IT87 variants; ACPI conflict refusal and `ignore_resource_conflict`; `sensors` output for present/absent channels; sysfs writes for voltage limits, temp type, fan min, PWM enable, PWM duty, and auto trip points; resume after suspend; DMI board quirk disabling PWM2; SMBus disable/restore behavior; and fault-injection for Super-I/O request failures. Hardware validation should include confirming fan speed remains safe when switching PWM modes and that hidden attributes match pin-mux and feature masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/it87.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/jc42.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/jc42.c

## Purpose
`jc42.c` supports JEDEC JC42.4-compliant temperature sensors, commonly found on memory modules. It registers an I2C hwmon device exposing a single temperature channel with input, min, max, critical, hysteresis, and alarm attributes. It also implements legacy I2C address scanning for known JC42-compatible manufacturer/device IDs.

## Important APIs, types, and functions
The driver uses the modern `hwmon_device_register_with_info()` API and `regmap` over I2C. `struct jc42_data` stores the regmap, extended temperature range capability, original config, and current config shadow. `jc42_temp_to_reg()` and `jc42_temp_from_reg()` convert between millidegrees Celsius and JC42 0.0625 C register units. `jc42_read()`, `jc42_write()`, and `jc42_is_visible()` implement hwmon operations. `jc42_detect()` validates scanned devices through capability, config, manufacturer, and device ID registers.

## Control flow
Probe allocates state, creates the big-endian 16-bit regmap, reads capabilities, optionally disables SMBus timeout when the `smbus-timeout-disable` property is present, reads the config register, clears shutdown if necessary, stores the config shadow, and registers hwmon. Runtime reads fetch temperature or alarm registers through regmap. Writes update min/max/critical limits or approximate the closest supported hysteresis by rewriting the config hysteresis field. Remove restores the original configuration except for the user-selected hysteresis.

## State and persistence
The chip stores thresholds and config persistently while powered. The driver keeps a config shadow because hysteresis reads derive from the cached hysteresis bits and writes must preserve unrelated config bits. Suspend sets shutdown, switches the regmap cache to cache-only, marks it dirty, and resume clears shutdown then syncs cached values back to hardware.

## Dependencies and integration points
Dependencies are I2C SMBus word/byte functionality for detection, I2C regmap, firmware properties, OF compatible `jedec,jc-42.4-temp`, and the hwmon core. It scans addresses `0x18` through `0x1f` for legacy probing.

## Risks
Detection must avoid false positives on DIMM EEPROM-adjacent addresses, so unsupported capability/config bits and ID masks are checked tightly. Hysteresis is coarse and chosen by nearest threshold, which can surprise users expecting exact values. Some vendors may not implement the SMBus timeout register, so that path is opt-in. If config lock bits are set, writable sysfs permissions are suppressed.

## Test signals
Test I2C detection for each supported ID family, OF binding probe, locked and unlocked config permission modes, min/max/crit writes, hysteresis rounding, alarm bit reads, shutdown/resume regcache sync, and remove-time restoration of non-hysteresis config bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/jc42.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/k10temp.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/k10temp.c

## Purpose
`k10temp.c` is the AMD Family 10h and newer CPU temperature hwmon driver. It exposes Tctl, optional Tdie, and optional Zen CCD temperatures through PCI device matches on AMD/Hygon northbridge/data-fabric function 3 devices.

## Important APIs, types, and functions
The driver uses PCI probing, CPU feature/model data, AMD SMN access (`amd_smn_read`), hwmon `with_info`, and CPUID helpers. `struct k10temp_data` stores the PCI device, register read callbacks, offset metadata, channel visibility bitmask, Zen CCD offset, and negative-temperature policy. `get_raw_temp()` decodes the reported temperature register. `k10temp_read_temp()` provides input/max/crit/hyst values. `k10temp_is_visible()` hides channels and critical attributes depending on CPU family, HTC support, and discovered CCD validity. `has_erratum_319()` blocks unreliable Family 10h socket cases unless `force=1`.

## Control flow
Probe checks erratum 319, allocates state, always enables Tctl, selects PCI-indexed or SMN temperature register readers based on CPU family/model, discovers supported CCDs for known Zen model ranges, applies model-name-based Tctl offsets to expose Tdie on selected Ryzen/Threadripper CPUs, and registers hwmon. Reads dispatch by channel: Tctl and Tdie come from the current temperature register, CCD channels read SMN per-CCD registers, and critical/hysteresis values come from hardware thermal control when available.

## State and persistence
The driver does not program thresholds or persistent settings. State is runtime-only: callback selection, offset values, CCD visibility, and whether negative values should be displayed for AMD 3255 industrial processors. Hardware registers are read on demand.

## Dependencies and integration points
It integrates with the PCI subsystem, x86 CPU identification, AMD northbridge node numbering, AMD SMN reads, and the hwmon ABI. It also uses PCI config space for older families and HTC capability reporting.

## Risks
Temperature formulas for Zen CCD registers are based on reverse-engineered sources rather than public datasheets. Model-range tables must be maintained for new AMD families. Erratum handling protects known unreliable sensors, but `force` can expose bad data. CCD discovery guards against `0xffffffff` responses, but platform firmware or SMN access failures can still hide valid sensors.

## Test signals
Test probe on representative Family 10h, 15h, 16h, 17h, 19h, and 1Ah systems; erratum 319 blocked and forced paths; Tdie offset models; HTC critical visibility; CCD valid/invalid SMN reads; Hygon PCI IDs; negative-temperature behavior for 3255; and sysfs label visibility only on Zen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/k10temp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/k8temp.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/k8temp.c

## Purpose
`k8temp.c` exposes AMD K8 core temperature sensors through the AMD K8 northbridge miscellaneous PCI function. It supports up to four temperature channels representing core and sensor-place selections.

## Important APIs, types, and functions
The driver uses PCI config-space access, CPUID data, mutex locking, and `devm_hwmon_device_register_with_info()`. `struct k8temp_data` stores an update lock, detected selectable sensor bits, whether core selection is inverted, and a model-specific temperature offset. `k8temp_is_visible()` hides absent core/place channels. `k8temp_read()` selects the requested core/place in `REG_TEMP`, reads the same register as a dword, and converts the value with `TEMP_FROM_REG()`. `is_rev_g_desktop()` implements AMD RevG desktop offset detection.

## Control flow
Probe rejects unsupported early revisions, sets `swap_core_select` and warns for RevF/RevG erratum-sensitive models, applies a 21 C desktop offset for RevG desktop CPUs, tests whether core and place selection bits can be toggled, validates that secondary sensors are plausible, initializes the mutex, and registers four possible hwmon temp channels. Runtime reads serialize selector writes and raw reads under `update_lock`.

## State and persistence
There is no persistent configuration beyond transient selector writes to PCI config register `0xe4`. Runtime state records which dimensions are selectable and whether a temperature offset applies. No cached temperature values are kept.

## Dependencies and integration points
The driver depends on AMD K8 PCI IDs, boot CPU model/stepping, CPUID brand-index decoding, and the hwmon core. It is specific to x86 K8-era hardware and uses PCI config accesses directly.

## Risks
The hardware selector register is shared state; serialized driver access avoids internal races but not external firmware or tooling changes. Erratum #141 means readouts may be wrong on later models even when exposed. Presence detection treats zero raw temperatures as invalid because -49 C is unlikely, which could theoretically hide a valid extreme reading.

## Test signals
Test older unsupported revisions, RevF/RevG warning and core-select inversion, RevG desktop offset, channel visibility when place/core bits are absent, repeated reads for all channels, and comparison against known-good thermal telemetry on real K8 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/k8temp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/kbatt.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/kbatt.c

## Purpose
`kbatt.c` is an auxiliary-bus hwmon driver for the KEBA battery monitoring controller FPGA IP core. It exposes a single voltage-style minimum alarm indicating whether the monitored battery fails a load test.

## Important APIs, types, and functions
The driver uses the auxiliary bus, KEBA auxiliary device structures from `linux/misc/keba.h`, MMIO helpers, `fsleep()`, mutexes, and the hwmon `with_info` API. `struct kbatt` stores the MMIO base, lock, cached alarm result, and next allowed update time. `kbatt_alarm()` performs the hardware load test and caches the result. `kbatt_read()` returns the alarm value and `kbatt_is_visible()` exposes only `in0_min_alarm`.

## Control flow
Probe obtains the parent-provided I/O resource from `struct keba_batt_auxdev`, maps it with `devm_ioremap_resource()`, initializes the mutex, and registers the hwmon device named `kbatt`. When users read the alarm, `kbatt_alarm()` checks the jiffies throttle; if expired, it writes the battery-test bit, waits 100 ms, reads status, clears the test bit, and delays the next test by up to 10 seconds.

## State and persistence
The driver intentionally caches the alarm result to avoid constantly applying the test load. Hardware control state is restored to load-off after each test. Runtime state is not persistent across driver reloads.

## Dependencies and integration points
It depends on a KEBA parent driver creating auxiliary device `keba.batt` with a valid MMIO resource. It integrates only through hwmon and auxiliary-bus matching.

## Risks
The read path has side effects and can hold the mutex while sleeping for the settle time. If an error or future change skipped the load-off write, the battery could remain under test load. The alarm is stale for up to 10 seconds by design. There is no explicit hardware revision validation in this child driver, so parent resource correctness is critical.

## Test signals
Test auxiliary probe with valid and invalid resources, alarm read when status indicates OK/fail, jiffies throttling, concurrent sysfs reads, load bit clear after reads, and absence of any other exposed hwmon attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/kbatt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/kfan.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/kfan.c

## Purpose
`kfan.c` is an auxiliary-bus hwmon driver for the KEBA fan controller FPGA IP core. It exposes fan fault and optionally fan RPM, plus writable PWM duty control.

## Important APIs, types, and functions
The driver uses auxiliary-bus matching, MMIO `ioread`/`iowrite`, dynamic `hwmon_channel_info`, and the hwmon `with_info` API. `struct kfan` stores the MMIO base, discovered tachometer/regulable capabilities, and per-instance channel config arrays. `kfan_get_fault()` interprets present/blocked status bits. `kfan_count_to_rpm()` converts tachometer counts to RPM. `kfan_set_pwm()` validates and writes duty values, forcing non-regulable controllers to on/off semantics.

## Control flow
Probe maps the KEBA fan resource, reads the status register, records whether tachometer and regulation are supported, builds fan and PWM channel descriptors accordingly, and registers a hwmon device named `kfan`. Runtime reads return fault, RPM, or PWM duty depending on sensor type. Writes are accepted only for `pwm1_input`.

## State and persistence
There is no software cache other than static capability flags read at probe. PWM writes change the hardware control register and persist until hardware reset or another agent writes it. Fault and RPM are read live.

## Dependencies and integration points
The driver depends on a KEBA parent auxiliary device named `keba.fan`, a valid MMIO resource, and a hardware register contract for status/control/tachometer values. It integrates with hwmon using per-instance dynamic channel descriptions.

## Risks
If the tachometer capability changes after probe, channel visibility will not update. Non-regulable fans accept any positive PWM request but coerce it to full on, which is sensible but may surprise userspace. RPM conversion assumes a fixed divider and count model. Fault reporting treats absent fans as faulted and blocked status as faulted only when no tachometer exists.

## Test signals
Test probe with all status bit combinations, channel visibility with/without tachometer, PWM writes at -1/0/1/255/256, non-regulable coercion, count conversion including 0 and 0xffff, and fault behavior for absent and blocked conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/kfan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lan966x-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lan966x-hwmon.c

## Purpose
`lan966x-hwmon.c` is a platform hwmon driver for Microchip LAN966x hardware. It exposes one PVT temperature input, one fan tachometer input, and writable PWM duty/frequency controls.

## Important APIs, types, and functions
The driver uses platform resources by name, MMIO regmap, clocks, polynomial temperature conversion, OF matching, devm cleanup actions, and hwmon `with_info`. `struct lan966x_hwmon` stores PVT and fan regmaps plus the enabled clock and clock rate. `lan966x_hwmon_read_temp()` reads and converts the PVT ADC sample through `polynomial_calc()`. `lan966x_hwmon_read_fan()` converts fan pulses per second to RPM. PWM helpers read/write duty and frequency register fields.

## Control flow
Probe enables the clock, records its rate, maps named `pvt` and `fan` resources as regmaps, programs the PVT sensor into continuous sampling mode with a divider targeting about 1.2 MHz, installs a devm cleanup action to disable sampling, and registers the hwmon device. Runtime reads dispatch by hwmon type and attribute. PWM writes validate ranges, convert requested frequency to register units, clamp to the field width, and update regmap bits.

## State and persistence
The driver programs hardware sampling state and PWM registers. The sampling configuration is disabled automatically on device teardown through `devm_add_action_or_reset()`. No sensor-value cache is kept. PWM duty/frequency stay in hardware until rewritten or reset.

## Dependencies and integration points
It requires a device tree compatible `microchip,lan9668-hwmon`, a clock, and two named MMIO resources. It depends on `linux/polynomial.h` for integer conversion of raw PVT ADC counts to millidegrees Celsius.

## Risks
The PVT conversion is a fourth-order polynomial with redistributed integer factors; regression risk is high if term order or scaling is changed. The frequency formula intentionally differs from the datasheet by using `pwm_freq + 1`, so tests should preserve that behavior. Temperature reads can return `-ENODATA` until valid data is latched. Incorrect clock rate or resource names break all conversions.

## Test signals
Test OF probe with missing clock/resources, PVT enable/disable register writes, temperature valid and invalid status, polynomial conversion at raw endpoints, fan RPM conversion, PWM duty boundaries, PWM frequency conversion/clamping, and hwmon permissions for read-only vs writable attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lan966x-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lattepanda-sigma-ec.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lattepanda-sigma-ec.c

## Purpose
`lattepanda-sigma-ec.c` is a DMI-gated platform hwmon driver for the LattePanda Sigma embedded controller. It bypasses the ACPI EC driver because firmware declares the EC disabled and exposes CPU fan RPM plus board and CPU temperatures via direct ACPI EC I/O ports.

## Important APIs, types, and functions
The driver uses DMI matching, module parameters, raw port I/O, I/O region reservation, platform device self-registration, and hwmon `with_info`. `ec_wait_ibf_clear()` and `ec_wait_obf_set()` poll the EC status register. `ec_read_reg()` performs the EC read protocol. `ec_read_reg16()` reads paired high/low registers with a high-byte recheck to avoid rollover corruption. `lps_ec_read()` and `lps_ec_read_string()` implement hwmon operations.

## Control flow
Module init requires an exact LattePanda Sigma DMI and BIOS version 5.27 match unless `force=1` is supplied for vendor/product-only matching. It registers a platform driver and synthetic platform device. Probe reserves ports `0x62` and `0x66`, sanity-checks EC responsiveness by reading fan duty, and registers hwmon. Runtime reads directly poll EC status and read registers for fan RPM or temperatures.

## State and persistence
There is no per-device runtime data and no caching. All sensor values are read on demand. The driver performs no EC writes except command/register selection for reads. I/O port ownership is devm-managed during probe and released with the platform device.

## Dependencies and integration points
It depends on x86 ACPI EC-compatible ports being free, DMI strings matching known hardware, and the BIOS-specific EC register map. It intentionally does not use ACPI global locks because the kernel ACPI EC subsystem is not initialized on this system.

## Risks
The direct EC protocol is BIOS-version-specific. Loading with `force=1` on a different EC map can read undefined registers. Busy-wait polling can spin for up to 25 ms on failures. The comment assumes no concurrent firmware EC access; if firmware behavior changes, raw port access could race. No writes are exposed, limiting damage to reads and command traffic.

## Test signals
Test exact DMI acceptance, force-mode acceptance, nonmatching DMI refusal, port request conflicts, EC timeout paths, 16-bit RPM rollover handling, labels and values for all three channels, and behavior on BIOS versions other than 5.27 only with explicit force.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lattepanda-sigma-ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lenovo-ec-sensors.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lenovo-ec-sensors.c

## Purpose
`lenovo-ec-sensors.c` exposes temperature and fan telemetry from Lenovo ThinkStation embedded-controller registers. Supported product families have model-specific channel maps and labels for CPU, DIMM, chassis, PSU, and fan readings.

## Important APIs, types, and functions
The driver uses DMI matching, platform device bundling, raw I/O ports, region reservation, mutex locking, and hwmon sysfs registration. `get_ec_reg()` implements Microchip EMI register access through fixed ports around `0x0900`. `struct ec_sensors_data` stores labels, maps, and the EC mutex. `lenovo_ec_do_read_temp()` converts EC temperature bytes from an offset encoding. `lenovo_ec_do_read_fan()` reads 16-bit fan current/max values. `lenovo_ec_hwmon_read_string()` supplies labels.

## Control flow
Module init checks the DMI table and creates a bundled platform device/driver. Probe allocates state, requests the EMI I/O region, initializes the EC address window, verifies the signature bytes `MCHP`, selects per-family temp/fan maps and hwmon channel info from DMI driver data, and registers the hwmon device. Runtime reads map the public hwmon channel index to an EC channel index, then perform one or two port reads under the mutex.

## State and persistence
The driver maintains only mapping pointers and the mutex. It does not cache sensor values. It writes the EMI application ID/address registers as part of each read transaction, but does not persistently configure thresholds or fan policy. The global `lenovo_ec_chip_info.info` pointer is mutated at probe according to system type.

## Dependencies and integration points
It depends on exact Lenovo DMI product codes, the Microchip EMI I/O window at `0x0900`, and hwmon sysfs. It also assumes a single supported system instance because of global platform device and chip-info state.

## Risks
Raw I/O region lifetime is partly manual: probe calls `request_region()` and module exit releases it, with explicit release on some error paths. The signature check uses `&&` between byte mismatches, which means it rejects only if all four bytes differ; this is weaker than requiring all four bytes to match. DMI driver data is dereferenced after `dmi_first_match()` without a null check, relying on module init gating. Product maps and label arrays must stay aligned with channel info counts.

## Test signals
Test all DMI product-code families, MCHP signature failure paths, region request failure, temp `-ENODATA` for low encoded values, fan input/max reads, label alignment, mutexed concurrent reads, module unload region release, and map bounds against each channel-info table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lenovo-ec-sensors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lineage-pem.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lineage-pem.c

## Purpose
`lineage-pem.c` supports Lineage Compact Power Line power entry modules and converters that are nominally PMBus-like but use nonstandard commands. It exposes voltage, current, power, temperature, fan, status, and alarm sysfs attributes through an I2C hwmon driver.

## Important APIs, types, and functions
The driver uses I2C SMBus block reads, legacy hwmon sysfs attribute groups, jiffies caching, and mutexes. `struct pem_data` stores client pointer, optional attribute groups, cached firmware/data/input/fan strings, feature flags, and cache timing. `pem_read_block()` validates fixed-length SMBus block responses. `pem_update_device()` refreshes cached strings once per second and clears information flags. Conversion helpers decode output voltage/current/temp, input voltage/power, and fan speeds. `pem_probe()` detects optional input and fan support.

## Control flow
Probe checks SMBus capabilities, allocates state, reads firmware revision to prove the device is present, clears flags, builds base attribute groups, probes input string support with two possible lengths, probes fan speed support, and registers hwmon groups. Runtime show callbacks call `pem_update_device()`, then decode cached bytes or alarm bits. The cache refresh reads the mandatory data string, optional input string, optional fan speed string, clears info flags, and marks the cache valid.

## State and persistence
The driver caches telemetry for one second. It does not expose writes except the internal clear-info-flags SMBus command during refresh and probe. Optional feature detection persists in `input_length` and `fans_supported` for the life of the driver.

## Dependencies and integration points
It depends on direct I2C access to the PEM, with the file comments recommending use behind a PCA9541 I2C master selector. It does not use the PMBus subsystem because the commands and telemetry format are nonstandard.

## Risks
Fixed-length block reads can fail on devices with variant firmware formats. Clearing info flags after each refresh may acknowledge transient conditions before another monitor reads them. Optional input detection has asymmetric fallback: it tries the 4-byte form first and the 5-byte form only after an error, not after an all-zero successful 4-byte response. Alarm attributes are always exposed even when some measurement groups are absent.

## Test signals
Test firmware read failure, block length mismatch, cache refresh throttling, optional input 4-byte and 5-byte detection, fan support detection, alarm bit decoding, conversion formulas for voltage/current/power/temp/fan values, and behavior behind an I2C mux/master selector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lineage-pem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm63.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm63.c

## Purpose
`lm63.c` supports National/TI LM63, LM64, and LM96163 I2C temperature sensors with integrated fan monitoring/control. It exposes local and remote temperatures, fan tachometer data, PWM control, automatic fan-control lookup-table points, alarms, update interval, and LM96163-specific TruTherm mode.

## Important APIs, types, and functions
The driver uses I2C SMBus byte access, legacy hwmon sysfs groups, OF and I2C ID matching, mutexes, and jiffies caches. `struct lm63_data` is the central cache for configuration, fan counts, PWM registers, lookup-table temperatures/PWM values, temp limits, alarms, conversion rates, and chip-specific flags. `lm63_update_device()` refreshes core sensor registers according to `update_interval`; `lm63_update_lut()` refreshes LUT registers every five seconds. Conversion macros/functions cover fan counts, 8-bit temps, signed/unsigned 11-bit remote temps, hysteresis, and LUT resolution.

## Control flow
I2C detection validates manufacturer/chip IDs and reserved register bits at allowed addresses. Probe allocates data, determines chip kind, applies the LM64 remote offset, initializes chip config through `lm63_init_client()`, conditionally adds fan and LM96163-specific attribute groups, and registers hwmon. Runtime sysfs reads refresh caches then format values. Writes update fan minimum, PWM duty, PWM mode, LUT points, temperature limits, conversion rate, hysteresis, and TruTherm mode under `update_lock`.

## State and persistence
The driver mirrors many hardware registers in RAM and writes user changes directly to the device. It preserves LUT and sensor caches with timed invalidation. Automatic mode is allowed only if LUT trip points look monotonic. Some chip settings, such as LM63 remote critical limit, are treated as effectively read-only unless variant rules say otherwise.

## Dependencies and integration points
Dependencies are I2C byte data functionality, optional OF compatibles, and hwmon sysfs ABI names for fan/PWM/temp attributes. The driver supports address scanning at `0x18`, `0x4c`, and `0x4e`.

## Risks
The code uses many legacy sysfs attributes and variant-dependent register interpretations. LUT monotonicity is checked before switching to automatic mode, but invalid values can still be written while in manual mode. Remote unsigned/high-resolution modes depend on LM96163 config bits. Several reads assume SMBus operations succeed and cache raw byte results, so transport errors may appear as values in some paths.

## Test signals
Test detection for LM63/LM64/LM96163 IDs and addresses, standby-to-operational transition, tachometer attribute visibility, fan min writes, manual/automatic PWM transitions with bad and good LUTs, LUT cache refresh, LM96163 high-resolution and TruTherm behavior, update interval rounding, alarm bits, and remote temperature signed/unsigned conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm63.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm70.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm70.c

## Purpose
`lm70.c` is an SPI hwmon driver for LM70 and compatible temperature sensors including TMP121/TMP122/TMP125, LM71, and LM74. It exposes one read-only `temp1_input` sysfs attribute.

## Important APIs, types, and functions
The driver uses the SPI bus, OF and SPI ID match data, mutexes, legacy hwmon group registration, and `spi_write_then_read()`. `struct lm70` stores the SPI device, lock, and chip type. `temp1_input_show()` performs the SPI read and converts raw two-byte temperature data according to the selected chip format. `lm70_probe()` validates SPI mode, allocates state, and registers hwmon groups.

## Control flow
Probe obtains chip match data, rejects non-mode-0 SPI configurations, assumes 8-bit words, initializes the mutex, stores state, and registers hwmon with the SPI modalias as the device name. Reads lock interruptibly, read two bytes without a transmit buffer, combine them into a signed 16-bit raw value, select the chip-specific bit shift/sign-extension/resolution formula, and return millidegrees Celsius.

## State and persistence
There is no cached state beyond chip type and SPI pointer. The device is read-only from this driver. No hardware configuration is programmed.

## Dependencies and integration points
It depends on board/OF/SPI enumeration identifying the correct compatible, SPI mode 0 signaling, and the hwmon sysfs group API. It uses `spi_write_then_read()` to satisfy DMA-safe buffer requirements.

## Risks
Wrong chip match data yields incorrect scaling or sign handling. The probe does not configure max speed, bits per word, or other SPI parameters beyond mode validation, so board data must be correct. `mutex_lock_interruptible()` can make reads return `-ERESTARTSYS`.

## Test signals
Test each compatible's raw-to-millidegree conversion including negative values, SPI mode rejection, SPI transfer errors, interruptible lock behavior, OF and SPI ID matching, and stable output formatting for `temp1_input`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm70.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm73.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm73.c

## Purpose
`lm73.c` is an I2C hwmon driver for TI LM73 temperature sensors. It exposes temperature input, min/max limits, min/max alarm bits, and update interval controls.

## Important APIs, types, and functions
The driver uses I2C SMBus byte/word access, legacy hwmon sysfs attribute groups, OF matching, and a mutex. `struct lm73_data` stores the I2C client, lock, and cached control register. `temp_show()` and `temp_store()` convert between millidegrees Celsius and the LM73 left-justified 0.25 C register representation. `convrate_show()` and `convrate_store()` map update interval requests to the resolution/conversion-rate bits. `maxmin_alarm_show()` reads alarm bits from the control register.

## Control flow
Detection first uses byte reads to avoid confusing other devices, checks reserved bits in control/config registers, verifies the low ID byte, then verifies the full word ID. Probe allocates state, reads the control register, registers hwmon groups, and logs the sensor name. Runtime temperature reads use swapped word SMBus access; limit writes clamp to the device range and write swapped words. Conversion-rate writes update the cached control register and hardware under the mutex.

## State and persistence
The driver caches only the control register for conversion-rate display and updates it when alarm reads or rate writes occur. Limit registers and control bits live in hardware. No periodic cache is used for temperatures.

## Dependencies and integration points
It depends on I2C adapters supporting SMBus byte and word data, optional OF compatible `ti,lm73`, and hwmon sysfs. Legacy address scanning covers `0x48`, `0x49`, `0x4a`, `0x4c`, `0x4d`, and `0x4e`.

## Risks
`convrate_store()` masks `data->ctrl` with `LM73_CTRL_TO_MASK`, preserving only the timeout bit and clearing other control bits; this may be intended for resolution bits but is a fragile register update pattern. Detection still performs a word read after byte checks, which can affect unusual devices at scanned addresses. Cached control state can be stale until alarm read or rate write.

## Test signals
Test detection against real and false-positive devices, temperature conversions at min/max and negative values, min/max limit writes with clamping, alarm bit reads updating cached control, conversion-rate boundary selection, OF probe, and SMBus error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm73.c -->
