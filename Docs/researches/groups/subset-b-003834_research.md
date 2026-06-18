# subset-b-003834 Research

Grouped research for the hwmon PC873xx, PCF8591, PECI, and PMBus source files. Each section preserves the source path expected by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pc87360.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pc87360.c

Purpose: legacy hwmon driver for National Semiconductor PC87360/PC87363/PC87364/PC87365/PC87366 Super-I/O hardware monitors. It discovers the chip at standard Super-I/O ports, creates a synthetic platform device for ISA I/O resources, and exposes fan, PWM, voltage, VID, diode temperature, and thermistor-backed temperature sysfs attributes according to the detected device ID and enabled logical devices.

Important APIs/types/functions: `struct pc87360_data` is the runtime cache and owns I/O bases, locks, channel counts, conversion reference voltage, limit registers, alarm/status registers, and hwmon device pointer. `pc87360_find()` probes Super-I/O config space and records logical device bases plus fan/VID/thermistor config registers. `pc87360_device_add()`, `pc87360_probe()`, `pc87360_remove()`, and the platform driver implement kernel registration. `pc87360_read_value()`/`pc87360_write_value()` serialize banked ISA register access. Conversion macros translate raw fan, PWM, voltage, VID, and temperature registers to hwmon units.

Control flow: module init probes 0x2e and 0x4e, chooses one active logical-device base, registers the platform driver, then adds a platform device with I/O resources after ACPI conflict checks. Probe selects chip capabilities from `devid`, requests regions, initializes locks, reads fan configuration, selects voltage reference, optionally forces channel/monitoring setup through `pc87360_init_device()`, creates sysfs groups per available channel class, and registers hwmon. Reads go through `pc87360_update_device()`, which refreshes cached registers every two seconds, clears write-one-to-clear alarm bits, performs fan divider auto-adjustment, and returns cached values to sysfs show callbacks. Store callbacks parse user values, convert to register format, update cache, and write the relevant banked register under `update_lock`.

State and persistence: persistent runtime state is in `pc87360_data`; global discovery state includes `devid`, `extra_isa[]`, `confreg[]`, `pdev`, and module parameters `init` and `force_id`. Hardware monitoring enable bits, fan divisors, PWM duty, limits, alarm latches, and VID routing persist in device registers until changed or reset. The driver intentionally caches data and invalidates by jiffies interval rather than reading every sysfs access.

Dependencies and integration: depends on platform-device infrastructure, direct port I/O, ACPI resource conflict checks, hwmon and hwmon-sysfs helpers, `hwmon-vid`, mutexes, and Super-I/O conventions. It integrates with userspace through classic hwmon sysfs names and with ISA resource management through platform resources.

Risks: the driver assumes one chip and standard Super-I/O addresses. Banked direct I/O and write-one-to-clear alarm handling require strict locking and correct masks. `init` levels can modify firmware-established monitoring setup. Fan autodivisor rewrites thresholds and divisor bits based on cached readings, so edge cases around overflow, low RPM, and minimum limits need hardware validation. Sysfs group creation is manual and all cleanup depends on matching feature bits.

Test signals: module load/unload on systems with no chip and with supported IDs, ACPI resource conflict behavior, expected hwmon sysfs files per chip variant, two-second cache refresh, writable limit/PWM attributes, fan divisor transitions, VID conversion, alarm clear behavior, and regression builds with the platform driver compiled as module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pc87360.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pc87427.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pc87427.c

Purpose: hwmon driver for the National Semiconductor PC87427 Super-I/O monitor. It supports up to eight fan inputs, four PWM outputs, and six read-only temperature channels, while explicitly noting that voltage channels are not implemented.

Important APIs/types/functions: `struct pc87427_data` stores the banked register cache, enabled channel bitmaps, I/O bases, hwmon device, and one mutex covering both bank selection and cache synchronization. `struct pc87427_sio_data` carries discovered base addresses and wired fan input/output masks from Super-I/O config space to the platform device. `pc87427_find()` identifies device ID 0xf2 and derives wired pins from configuration registers. `pc87427_init_device()` enables fan monitoring if needed and discovers enabled fan, PWM, and temperature channels. Read/write helpers include `pc87427_read8_bank()`, `pc87427_write8_bank()`, `pc87427_readall_fan()`, `pc87427_readall_pwm()`, and `pc87427_readall_temp()`.

Control flow: module init tries Super-I/O ports 0x2e and 0x4e, registers the platform driver, and creates a platform device with I/O resources and platform data. Probe allocates `pc87427_data`, requests FMC/HMC I/O regions, initializes the device, creates sysfs groups only for enabled channels, then registers hwmon. `pc87427_update_device()` refreshes fan, PWM, and temperature caches once per second. Fan minimum writes temporarily disable fan monitoring because the limit registers are read-only while monitoring is enabled. PWM writes enforce manual/off mode and optionally transition off/manual when duty reaches zero or nonzero.

State and persistence: state lives in `pc87427_data` and in hardware banks. `fan_enabled`, `pwm_enabled`, `pwm_auto_ok`, and `temp_enabled` control which sysfs files exist and which registers are refreshed. `pwm_auto_ok` preserves whether automatic control was present at boot, since the driver can return to automatic mode only when firmware configured it first. Status/alarm bits are cleared by writing back read status values during refresh.

Dependencies and integration: depends on direct port I/O, muxed Super-I/O region requests, platform devices, ACPI resource conflict checks, sysfs attribute groups, and hwmon registration. It exposes classic hwmon files such as `fan*_input`, `fan*_min`, `fan*_alarm`, `pwm*`, `pwm*_enable`, and `temp*_input`.

Risks: banked I/O makes the single mutex critical; any unlocked bank access can corrupt reads or writes. The probe enables all wired fans if none were already monitored, changing hardware state. PWM mode conversion maps unsupported register modes to `-EPROTO`, so unusual firmware modes can surface as sysfs read errors. Temperature support assumes 8-bit sensors despite possible 9-bit mode. The global `pdev` and single-chip assumption limit multi-instance behavior.

Test signals: detection at both Super-I/O ports, wired fan/PWM masks matching board pins, sysfs file presence for enabled channels, fan min writes preserving monitoring, PWM manual/off/auto transitions, temperature read-only attributes, alarm clear behavior, and clean unload removing all groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pc87427.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pcf8591.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pcf8591.c

Purpose: I2C hwmon driver for the NXP/Philips PCF8591 8-bit A/D and D/A converter. It exposes analog input channels and the analog output enable/value through hwmon sysfs files.

Important APIs/types/functions: `struct pcf8591_data` stores the current control byte, analog output byte, hwmon device, and update mutex. `pcf8591_probe()` initializes client state, creates sysfs attributes, and registers hwmon. `pcf8591_read_channel()` selects an ADC channel, flushes the stale conversion byte required by the chip protocol, and returns scaled signed or unsigned values based on `input_mode`. `pcf8591_init_client()` programs initial control and DAC output. Module parameter `input_mode` selects one of four PCF8591 analog input programming modes.

Control flow: module init clamps invalid `input_mode` to mode 0 and registers the I2C driver. Probe allocates state, writes the initial control byte with analog output enabled and DAC zero, flushes the first read, creates required inputs 0 and 1 plus optional input 2/3 based on mode, and registers hwmon. Input reads lock `update_lock`, update the channel bits if necessary, flush a stale sample after channel switching, read the actual sample, then convert to 10x units. Output stores update `aout` or the AOEF bit and write the control/output byte over SMBus.

State and persistence: the driver maintains only the cached control byte and DAC output. No periodic cache exists because each input access reads hardware. The selected input mode is a module-global configuration and affects visible sysfs files and signed conversion interpretation. The DAC/control state persists in the device until changed.

Dependencies and integration: depends on I2C SMBus byte and byte-data operations, hwmon registration, sysfs attributes, and kernel integer parsing helpers. It uses the legacy hwmon device registration interface instead of `hwmon_device_register_with_info()`.

Risks: the PCF8591 returns the previous conversion result first, so missing flushes produce off-by-one-channel data. `out0_output_store()` updates `data->aout` without taking `update_lock`, while `out0_enable_store()` and channel reads do lock around control-byte changes. Sysfs cleanup removes the optional group even though optional files are created individually, relying on sysfs tolerance. The module parameter is global, not per device.

Test signals: I2C probe/remove, invalid `input_mode` warning and reset to zero, visible input files for all four modes, signed readings in differential modes, stale-read flushing after channel switches, DAC output writes, output enable toggling, and unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pcf8591.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/peci/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hwmon/peci/Kconfig

Purpose: Kconfig entries for Intel PECI hwmon clients. It defines user-visible CPU temperature and DIMM temperature monitoring modules plus a hidden shared `SENSORS_PECI` symbol.

Important symbols: `SENSORS_PECI_CPUTEMP` builds the generic PECI CPU temperature client, depends on `PECI`, and selects `SENSORS_PECI` and `PECI_CPU`. `SENSORS_PECI_DIMMTEMP` builds the PECI DIMM temperature client with the same dependency and selections. `SENSORS_PECI` is a hidden tristate used as shared hwmon PECI support.

Control flow: enabling either visible symbol causes the corresponding object from the PECI Makefile to build as built-in or module and ensures the PECI CPU auxiliary-device provider is present. Help text declares module names `peci-cputemp` and `peci-dimmtemp`.

State and persistence: no runtime state. The file controls build-time inclusion and module availability.

Dependencies and integration: integrates hwmon PECI clients with the PECI bus and `PECI_CPU` auxiliary-device layer. The selected hidden symbol groups shared hwmon PECI code paths.

Risks: missing `PECI_CPU` selection would prevent auxiliary device matching. Because both clients select shared support, build coverage should include each symbol alone, both together, built-in, and module forms.

Test signals: `olddefconfig`, `modpost` dependency resolution, module names matching help text, and successful builds with `PECI` disabled/enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/peci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/peci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hwmon/peci/Makefile

Purpose: build rules for the PECI hwmon clients.

Important entries: `peci-cputemp-y := cputemp.o` and `peci-dimmtemp-y := dimmtemp.o` define module object composition. `obj-$(CONFIG_SENSORS_PECI_CPUTEMP)` and `obj-$(CONFIG_SENSORS_PECI_DIMMTEMP)` include those modules based on Kconfig state.

Control flow: Kconfig selects determine whether the CPU temperature and DIMM temperature clients are built-in, loadable modules, or omitted. There is no multi-object common library beyond the header-only `common.h`.

State and persistence: no runtime state. The Makefile only maps config symbols to object files.

Dependencies and integration: pairs with `drivers/hwmon/peci/Kconfig` and the parent hwmon build. Module names are derived from `peci-cputemp.o` and `peci-dimmtemp.o`.

Risks: object names must match documented module names and source files. Adding shared C code later would require updating these `*-y` aggregations rather than only adding an `obj-*` line.

Test signals: kernel builds for each config as `m` and `y`, module file names, and no unresolved namespace imports for `PECI_CPU`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/peci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/peci/common.h -->
# sources/distributed-fs/ceph-client/drivers/hwmon/peci/common.h

Purpose: small shared PECI hwmon cache helper header used by CPU and DIMM temperature clients.

Important APIs/types/functions: `PECI_HWMON_UPDATE_INTERVAL` sets a one-second cache interval. `struct peci_sensor_state` stores validity and last-update jiffies. `struct peci_sensor_data` stores a milli-unit sensor value plus update state. `peci_sensor_need_update()` checks validity and staleness. `peci_sensor_mark_updated()` records a successful refresh.

Control flow: PECI clients call `peci_sensor_need_update()` before expensive PECI transactions and call `peci_sensor_mark_updated()` after storing a new value. The helper is inline and header-only.

State and persistence: cache state is embedded by callers in per-sensor structures. Values survive across hwmon read callbacks until the one-second interval expires or the device is removed.

Dependencies and integration: depends on Linux types, `jiffies`, and `time_after()` availability through included kernel headers in users. It is included by both `cputemp.c` and `dimmtemp.c`.

Risks: the comment parameter names mention `sensor`, while functions take `state`; this is cosmetic. The helper does not include `<linux/jiffies.h>` itself, so users must already include it. Cache interval is fixed for all PECI sensors.

Test signals: compile coverage through both PECI drivers, repeated hwmon reads reusing cached values within HZ, and refresh after the interval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/peci/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/peci/cputemp.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/peci/cputemp.c

Purpose: auxiliary-bus hwmon client exposing Intel CPU package, DTS, control/throttle/Tjmax, and per-core temperatures over PECI. It supports several Xeon generations through per-generation resolved-core register locations and PECI revision expectations.

Important APIs/types/functions: `struct peci_cputemp` stores the PECI device, hwmon name, generation info, cached target/die/DTS/core temperatures, core labels, and core mask. `struct cpu_info` carries the resolved-core register, minimum PECI revision, and fixed-point conversion function. `update_temp_target()`, `get_die_temp()`, `get_dts()`, and `get_core_temp()` implement sensor reads. `init_core_mask()` reads platform-specific PCI/endpoint PCI registers to discover active cores. `cputemp_read()`, `cputemp_read_string()`, and `cputemp_is_visible()` implement `hwmon_ops`.

Control flow: the auxiliary driver matches names such as `peci_cpu.cputemp.hsx`, allocates private state, warns on unexpectedly low PECI revision, optionally resolves core mask and labels, then registers a hwmon device with static channel descriptors. Reads dispatch by channel: die uses `peci_temp_read()` plus Tjmax, DTS uses `PECI_PCS_THERMAL_MARGIN` plus Tcontrol, target channels read `PECI_PCS_TEMP_TARGET`, and core channels read `PECI_PCS_MODULE_TEMP` for each visible core. Per-sensor cache helpers prevent repeated PECI transactions within one second.

State and persistence: all values are runtime caches in `peci_cputemp`. `core_mask` determines which of the 64 possible core channels are visible. Target temperature values share one cache state; die, DTS, and each core have separate cache states. No values are persisted outside device lifetime.

Dependencies and integration: depends on auxiliary bus, PECI device APIs, PECI CPU namespace, hwmon info API, bitmaps, bitfields, jiffies, and unit constants. It imports namespace `PECI_CPU` and is instantiated by the PECI CPU layer rather than by direct I2C/platform discovery.

Risks: incorrect generation data can hide cores or read the wrong PCI/endpoint config register. Failure to resolve cores is non-fatal, so package sensors may work while per-core channels are absent. DTS error codes are filtered by range; hardware or firmware changes in encoded errors would need review. Visibility exposes a large static descriptor with dynamic hiding, so channel indexes must stay aligned with labels.

Test signals: auxiliary matching for all listed generations, hwmon labels `Die`, `DTS`, `Tcontrol`, `Tthrottle`, `Tjmax`, per-core label creation, package and core temperature reads, cache behavior, low PECI revision warning, and operation when core resolution fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/peci/cputemp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/peci/dimmtemp.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/peci/dimmtemp.c

Purpose: auxiliary-bus hwmon client exposing DIMM temperatures and threshold limits through PECI for multiple Intel server CPU generations. It discovers populated DIMMs dynamically and registers channels only after memory training data is usable.

Important APIs/types/functions: `struct peci_dimmtemp` stores the PECI device, generation info, delayed detection work, per-DIMM cached temperature/threshold data, labels, DIMM bitmap, and retry counter. `struct dimm_info` defines channel-rank count, DIMM index count, minimum PECI revision, and threshold-read callback. `get_dimm_temp()`, `update_thresholds()`, `get_dimm_thresholds()`, `check_populated_dimms()`, `create_dimm_temp_info()`, and generation-specific `read_thresholds_*()` functions implement detection and reads. `dimmtemp_read()`, `dimmtemp_read_string()`, and `dimmtemp_is_visible()` implement `hwmon_ops`.

Control flow: probe allocates private state, binds generation data from the auxiliary-device ID, warns on low PECI revision, initializes autocancel delayed work, and calls `create_dimm_temp_info()`. Detection reads `PECI_PCS_DDR_DIMM_TEMP` for each channel rank; `-EINVAL` marks empty ranks, empty or not-ready results cause delayed retry every five seconds, and repeated all-empty results eventually return no-device without failing probe. Once populated DIMMs are known, labels such as `DIMM A1` are allocated and hwmon is registered. Temperature reads use PCS DDR DIMM temperature; threshold reads use platform-specific PCI, endpoint PCI, or MMIO paths.

State and persistence: `dimm_mask` controls visible channels. Per-DIMM temperature and threshold values are cached for one second using `common.h` helpers. `no_dimm_retry_count` persists across delayed retries to distinguish early boot from truly empty memory. No persistent storage is written.

Dependencies and integration: depends on auxiliary bus, devm delayed work helpers, PECI CPU APIs, hwmon info API, bitmaps, bitfields, workqueues, and units. It imports namespace `PECI_CPU` and is instantiated by PECI CPU generation devices.

Risks: detection intentionally defers on ambiguous boot-time states, so hwmon registration may appear later than probe. The fixed maximum array is based on HSX maximums; a defensive `WARN_ONCE` protects unsupported larger layouts. Generation-specific threshold address formulas are brittle and must track CPU uncore documentation. `adm` style threshold reads may return `-ENODATA` when endpoint address discovery fails, affecting max/crit attributes while temperature reads still work.

Test signals: delayed retry behavior during early boot, no-DIMM handling after retry limit, label and visibility for populated DIMMs, per-generation threshold reads, cache refresh after HZ, and successful module unload canceling delayed work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/peci/dimmtemp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/Kconfig

Purpose: PMBus hwmon configuration menu. It enables the PMBus core, generic PMBus support, and a large list of chip-specific drivers including every PMBus source in this work item.

Important symbols: `PMBUS` is the menuconfig and core module gate depending on `I2C`. Relevant entries here include `SENSORS_ACBEL_FSG032`, `SENSORS_ADM1266`, `SENSORS_ADM1275`, `SENSORS_ADP1050`, `SENSORS_ADP1050_REGULATOR`, `SENSORS_APS_379`, `SENSORS_BEL_PFE`, `SENSORS_BPA_RS600`, `SENSORS_CRPS`, `SENSORS_DELTA_AHE50DC_FAN`, `SENSORS_FSP_3Y`, `SENSORS_HAC300S`, `SENSORS_IBM_CFFPS`, `SENSORS_DPS920AB`, and `SENSORS_INA233`. `SENSORS_ADM1266` selects `CRC8` and depends on `GPIOLIB`; `SENSORS_IBM_CFFPS` depends on `LEDS_CLASS`.

Control flow: when `PMBUS` is enabled, the nested symbols determine which chip drivers build. Optional regulator integration for ADP1050/LTP8800 depends on both the sensor driver and `REGULATOR`.

State and persistence: no runtime state. This file controls compile-time inclusion, module availability, and dependency closure.

Dependencies and integration: integrates hwmon PMBus drivers with I2C, GPIO, LED, CRC, and regulator subsystems where needed. Help text documents module names consumed by users and packaging.

Risks: dependency mistakes cause build or probe failures only for selected configurations, especially optional GPIO/LED/regulator features. The menu is long, so Makefile/Kconfig drift is a common maintenance risk.

Test signals: `olddefconfig`, randconfig/allmodconfig builds, module names matching help text, and targeted builds for drivers with extra dependencies such as ADM1266 and IBM CFFPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/Makefile

Purpose: object selection for PMBus core, generic PMBus, and chip-specific PMBus hwmon drivers.

Important entries: `obj-$(CONFIG_PMBUS) += pmbus_core.o` builds the common PMBus implementation. The listed work-item drivers map from config symbols to objects such as `acbel-fsg032.o`, `adm1266.o`, `adm1275.o`, `adp1050.o`, `aps-379.o`, `bel-pfe.o`, `bpa-rs600.o`, `crps.o`, `delta-ahe50dc-fan.o`, `dps920ab.o`, `fsp-3y.o`, `hac300s.o`, `ibm-cffps.o`, and `ina233.o`.

Control flow: Kconfig symbol states determine whether each object is omitted, built-in, or built as a module. Most chip objects are single-source modules that call into `pmbus_core`.

State and persistence: no runtime state; this is build metadata.

Dependencies and integration: pairs with `pmbus/Kconfig` and parent hwmon Makefiles. The file must stay synchronized with config names and source file names so module builds resolve correctly.

Risks: stale object lines lead to selected drivers not building or renamed source files not being referenced. Common core must be available for every chip module importing namespace `PMBUS`.

Test signals: build coverage with each listed `CONFIG_SENSORS_*` as module and built-in, `modpost` namespace import resolution, and generated module filenames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/acbel-fsg032.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/acbel-fsg032.c

Purpose: PMBus driver for AcBel FSG032 power supplies. It verifies manufacturer/model strings, declares supported PMBus telemetry, and exposes firmware revision through debugfs.

Important APIs/types/functions: `acbel_fsg032_info` declares one PMBus page with voltage, current, power, temperature, fan, and status capabilities. `acbel_fsg032_probe()` reads `PMBUS_MFR_ID` and `PMBUS_MFR_MODEL` and then calls `pmbus_do_probe()`. `acbel_fsg032_debugfs_read()` reads manufacturer command `ACBEL_MFR_FW_REVISION` and formats up to three bytes; `acbel_fsg032_init_debugfs()` creates `fw_version`.

Control flow: I2C/OF matching binds the driver, probe rejects non-ACBEL/non-FSG032 devices, PMBus core creates hwmon files from `acbel_fsg032_info`, then debugfs is attached under the PMBus debugfs directory if available.

State and persistence: no private long-lived state beyond PMBus core state. Debugfs reads query hardware each time.

Dependencies and integration: depends on I2C SMBus block reads, PMBus core, debugfs, OF matching, and hwmon PMBus status mapping.

Risks: block data is treated as a C string only after setting `buf[rc]`, so model/manufacturer validation depends on returned lengths being within the SMBus block buffer. Debugfs output is intentionally short and may truncate longer firmware revisions. Probe does not explicitly check adapter functionality before block reads.

Test signals: model/manufacturer rejection, hwmon files for declared capabilities, debugfs `fw_version`, and failure injection for SMBus block reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/acbel-fsg032.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/adm1266.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/adm1266.c

Purpose: PMBus driver for Analog Devices ADM1266 cascadable super sequencer. Beyond voltage monitoring, it registers GPIO inputs, debugfs sequencer state, NVMEM blackbox records, and writes the chip RTC.

Important APIs/types/functions: `struct adm1266_data` embeds `pmbus_driver_info`, `gpio_chip`, NVMEM config/device, debugfs directory, I2C client, shared DMA-safe block buffers, and a buffer mutex. `adm1266_pmbus_block_xfer()` implements a combined PMBus block write/read protocol with optional PEC CRC validation. `adm1266_config_gpio()`, `adm1266_gpio_get()`, `adm1266_gpio_get_multiple()`, and `adm1266_gpio_dbg_show()` expose GPIO/PDIO status. `adm1266_config_nvmem()` and `adm1266_nvmem_read_blackbox()` expose fault blackbox data. `adm1266_set_rtc()` programs current seconds into `ADM1266_SET_RTC`.

Control flow: probe allocates state, initializes a 17-page voltage-output PMBus descriptor, populates CRC table, initializes the block buffer mutex, registers GPIOs, sets RTC, registers read-only NVMEM, calls `pmbus_do_probe()`, then creates debugfs `sequencer_state`. GPIO reads use status block commands; debugfs pin detail uses block transfers for GPIO and PDIO config; blackbox NVMEM reads refresh the full backing buffer when offset zero is read.

State and persistence: driver state includes GPIO names, NVMEM backing memory, PMBus info, block buffers, and debugfs entries. Hardware state includes RTC, sequencer state, blackbox records, GPIO/PDIO configuration, and voltage monitor state. NVMEM is read-only and caches records in `dev_mem` after refresh.

Dependencies and integration: depends on PMBus core, I2C raw transfers, SMBus block access, CRC8, GPIO library, debugfs, NVMEM provider, and timekeeping. Kconfig selects CRC8 and requires GPIOLIB.

Risks: `adm1266_gpio_get_multiple()` resets `*bits` before PDIO processing and uses an unusual upper bound expression with `ADM1266_PDIO_STATUS`, so multi-get behavior deserves scrutiny. Block transfer length and PEC calculations rely on returned block count. Blackbox cell size is 2048 while individual records are 64 bytes and record count comes from hardware. Probe failure in RTC/NVMEM/GPIO prevents PMBus monitoring.

Test signals: GPIO registration and status reads, debugfs sequencer state and pin debug output, PEC-enabled block transfer CRC rejection, NVMEM blackbox reads, RTC write success, and hwmon voltage channels across 17 pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/adm1266.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/adm1275.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/adm1275.c

Purpose: PMBus hwmon driver for Analog Devices ADM1075/ADM1272/ADM1273/ADM1275/ADM1276/ADM1278/ADM1281/ADM1293/ADM1294 and SQ24905C hot-swap controllers/digital power monitors.

Important APIs/types/functions: `struct adm1275_data` stores chip ID, feature booleans, and embedded `pmbus_driver_info`. Coefficient tables provide direct-format scaling for voltage, current, power, and temperature by chip/range. `adm1275_read_word_data()`, `adm1275_write_word_data()`, and `adm1275_read_byte_data()` implement virtual PMBus attributes, peak/min history, sample averaging, VAUX mapping, and manufacturer-specific status translation. `adm1275_read_samples()`, `adm1275_write_samples()`, and `adm1275_write_pmon_config()` control PMON averaging while disabling/re-enabling conversions. `adm1275_probe()` validates manufacturer/model, reads config, selects features and coefficients, handles DT properties, and calls PMBus core.

Control flow: probe requires SMBus byte and block support, reads `PMBUS_MFR_ID` and model, maps detected model to `adm1275_id`, chooses byte or word config reads, reads PMON/device config, allocates private data, reads `shunt-resistor-micro-ohms`, builds the PMBus descriptor, then switches by chip variant. The switch sets capability bits, enables default VOUT/TEMP on chips where needed, sets current/power/voltage coefficient indexes, and applies optional `adi,power-sample-average` and `adi,volt-curr-sample-average`. PMBus core later calls driver hooks for virtual history, status, and sampling attributes.

State and persistence: runtime state is feature flags plus PMBus coefficients in `adm1275_data`. Hardware state can be changed by enabling VOUT/TEMP monitoring, modifying PMON sample averaging, clearing peak/min history, and writing IOUT fault limit aliases. Shunt resistor and averaging properties are read at probe and persist in the driver info.

Dependencies and integration: depends on PMBus core, I2C SMBus byte/word/block operations, OF properties, bitfields, log2 helpers, and direct-format PMBus coefficient support.

Risks: variant logic is dense and config-dependent; wrong coefficient index or shunt scaling gives incorrect physical units. Some chips expose VOUT through VAUX-style manufacturer commands, so `have_vout` and status mapping must stay consistent. Sample averaging accepts powers of two only; invalid DT properties fail probe. `adm1275_write_pmon_config()` attempts to re-enable conversions even if config writes fail, which is correct but makes error ordering important.

Test signals: probe for every ID, manufacturer/model mismatch handling, coefficient/unit validation with known shunts, VOUT/TEMP enablement on ADM1272/1278 family, virtual peak/min read/reset files, sample averaging DT properties and sysfs writes, VAUX status mapping, and PMBus status fault translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/adm1275.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/adp1050.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/adp1050.c

Purpose: PMBus hwmon driver for Analog Devices ADP1050/ADP1051/ADP1055 digital power-supply controllers and LTP8800 modules, with optional regulator registration for LTP8800-style output.

Important APIs/types/functions: static `pmbus_driver_info` instances describe one-page capabilities and linear formats for each compatible. `adp1050_probe()` retrieves match data from I2C/OF tables and calls `pmbus_do_probe()`. When `CONFIG_SENSORS_ADP1050_REGULATOR` is enabled, `PMBUS_REGULATOR_ONE("vout")` is attached to `ltp8800_info`.

Control flow: matching by I2C ID or OF compatible supplies the correct info structure. Probe rejects missing match data and otherwise delegates all runtime operations to PMBus core.

State and persistence: no private mutable state. Static capability descriptors define visible sensors and optional regulator metadata for the lifetime of the module.

Dependencies and integration: depends on PMBus core, I2C matching, OF matching, and optionally the regulator framework. It imports namespace `PMBUS`.

Risks: static descriptors are shared and should not be mutated per device. Variant capability differences are encoded only in `func[0]`; missing status bits or wrong temperature channel selection would surface as absent or invalid hwmon attributes. Optional regulator support changes ABI when enabled.

Test signals: matching all compatibles, `pmbus_do_probe()` success, visible attributes per variant, optional regulator registration under regulator-enabled builds, and no match-data path returning `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/adp1050.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/aps-379.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/aps-379.c

Purpose: PMBus driver for Sony APS-379 power supplies. It compensates for nonstandard VOUT encoding and hides invalid or undocumented command data.

Important APIs/types/functions: `aps_379_read_byte_data()` fakes `PMBUS_VOUT_MODE` as linear exponent -4. `aps_379_read_vout()` reads raw `PMBUS_READ_VOUT`, sign-extends the linear11 mantissa, and clamps it for PMBus core consumption. `aps_379_read_word_data()` rejects invalid limit/rating commands and maps `PMBUS_READ_VOUT`. `aps_379_probe()` verifies SMBus functionality and checks `PMBUS_MFR_MODEL`.

Control flow: probe verifies byte/word/block SMBus support, reads model, rejects unsupported devices, and delegates to `pmbus_do_probe()` with one-page capabilities for VOUT, IOUT, input/output power, temperature, and fan. PMBus core calls the read hooks to obtain VOUT mode/value and to suppress misleading limits.

State and persistence: no private state. All behavior is encoded in static PMBus info and read hooks.

Dependencies and integration: depends on I2C SMBus operations, PMBus core, OF/I2C IDs, and linear data-format support.

Risks: the hard-coded VOUT exponent assumes all APS-379 units use the same scale. Masking invalid commands with `-ENXIO` changes which hwmon limit files are available. Model validation is case-insensitive prefix matching and depends on returned block data being correctly terminated before logging.

Test signals: model rejection, VOUT value scaling against known readings, absence of invalid limit files, fan/temp/power attributes, and block/word SMBus functionality checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/aps-379.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/bel-pfe.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/bel-pfe.c

Purpose: PMBus driver for BEL PFE1100 and PFE3000 power supplies.

Important APIs/types/functions: `pfe_driver_info[]` contains static PMBus descriptors for `pfe1100` and `pfe3000`. `pfe_plat_data` sets `PMBUS_SKIP_STATUS_CHECK` to tolerate devices that report communication errors for `VOUT_MODE`. `pfe_pmbus_probe()` stores platform data, resets PFE3000 to page zero, and calls `pmbus_do_probe()`.

Control flow: I2C ID matching passes the model enum. Probe applies the PMBus platform flag before core probing. PFE3000 receives an explicit `PMBUS_PAGE` write to avoid probe failure from an unexpected current page. The PMBus core creates attributes for one PFE1100 page or seven PFE3000 pages with per-page capability masks.

State and persistence: no private allocated state. Probe writes page zero on PFE3000 and assigns `client->dev.platform_data` to a static structure.

Dependencies and integration: depends on PMBus core and I2C. Multi-page PFE3000 integration relies on PMBus core page management.

Risks: writing `client->dev.platform_data` mutates device state before probe. `PMBUS_SKIP_STATUS_CHECK` is necessary but broad; it can hide real status read problems during probing. PFE3000 page reset assumes page command is safe and accepted.

Test signals: PFE1100 and PFE3000 probe, status-check skipping around `VOUT_MODE`, page-zero reset before probe, expected attributes on pages 0/1/2/4/5/6, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/bel-pfe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/bpa-rs600.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/bpa-rs600.c

Purpose: PMBus driver for BluTek BPA-RS600/BPD-RS600 power supplies. It handles several firmware/spec deviations while exposing voltage, current, power, temperature, and fan telemetry.

Important APIs/types/functions: `bpa_rs600_read_byte_data()` masks out non-existent fan2 bits from `PMBUS_FAN_CONFIG_12`. `bpa_rs600_read_vin()` rewrites unsigned mantissa VIN encodings into a representation the PMBus core can decode. `bpa_rs600_read_pin_max()` corrects a known bad 1640 W `MFR_PIN_MAX` value to 700 W. `bpa_rs600_read_word_data()` rejects invalid undocumented limits and routes special reads. `bpa_rs600_probe()` checks SMBus capability and validates model block data against supported IDs.

Control flow: probe verifies adapter support, reads `PMBUS_MFR_MODEL`, matches against the ID table, and calls PMBus core. During hwmon reads, the PMBus core delegates selected byte/word commands to driver hooks for correction or rejection.

State and persistence: no private state. Corrected values are computed on demand from hardware reads.

Dependencies and integration: depends on PMBus core, I2C SMBus byte/word/block operations, OF/I2C matching, and PMBus linear encoding semantics.

Risks: corrections are firmware-specific; future firmware could use different encodings. The fan2 mask assumes only one physical fan despite PMBus config reporting two. Invalid command filtering removes limits and virtual attributes to avoid bad data, so users may see fewer files than generic PMBus probing would expose.

Test signals: model validation for both IDs, fan config masking, VIN correction on high mantissa bit, `MFR_PIN_MAX` bad-value correction, invalid limit suppression, and hwmon readings for declared capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/bpa-rs600.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/crps.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/crps.c

Purpose: PMBus driver for Intel Common Redundant Power Supply model `03NK260` / `intel_crps185`.

Important APIs/types/functions: `crps_info` declares one default-linear PMBus page with input/output voltage, current, power, temperature, fan, and status capabilities. `crps_probe()` reads `PMBUS_MFR_MODEL`, validates exact length and string, runs `pmbus_do_probe()`, and reports failures through `dev_err_probe()`.

Control flow: OF/I2C matching binds the driver, probe validates model identity, PMBus core creates hwmon attributes from the descriptor, and all subsequent sensor reads use standard PMBus core behavior.

State and persistence: no private state. The only stateful action is PMBus core registration.

Dependencies and integration: depends on I2C, OF matching, PMBus core, and standard PMBus linear formats.

Risks: exact model length/string matching rejects compatible units with alternate manufacturer strings. No explicit adapter functionality check is performed before block read. The descriptor assumes default linear formats for all sensors.

Test signals: successful probe with model `03NK260`, rejection of other models, hwmon attributes for all declared sensors, and error paths for failed model read and failed PMBus probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/crps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/delta-ahe50dc-fan.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/delta-ahe50dc-fan.c

Purpose: PMBus driver for the integrated fan-control module in the Delta AHE-50DC Open19 power shelf.

Important APIs/types/functions: `ahe50dc_fan_write_byte()` blocks `PMBUS_CLEAR_FAULTS` to avoid hardware output glitches. `ahe50dc_fan_read_word_data()` restricts reads to supported commands and remaps virtual page 1 temperature 1 to manufacturer command `0xd0`. `ahe50dc_fan_info` declares two virtual pages with direct-format fan, temperature, and VIN coefficients. `ahe50dc_fan_data` sets `PMBUS_NO_CAPABILITY` because the device returns misleading capability data.

Control flow: probe installs platform data and delegates to PMBus core. PMBus core uses two virtual pages: page 0 for VIN, temps, fans, and fan status; page 1 for remapped fourth temperature. Write-byte and read-word hooks filter unsafe or unsupported operations.

State and persistence: no private runtime state. The driver intentionally avoids sending clear-faults writes that could disturb hardware outputs.

Dependencies and integration: depends on PMBus core, I2C, OF/I2C matching, and direct-format PMBus conversion coefficients.

Risks: blackholing `CLEAR_FAULTS` means generic PMBus fault clearing will report unsupported and faults may remain latched elsewhere. Unsupported commands returning `-EOPNOTSUPP`/`-ENODATA` are deliberate to avoid confusing `0xffff` reads. Direct coefficients are hard-coded from observed device behavior.

Test signals: no `CLEAR_FAULTS` SMBus write on fault-clearing requests, virtual temp4 mapping, supported command reads only, fan speed/control attributes, and operation with `PMBUS_NO_CAPABILITY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/delta-ahe50dc-fan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/dps920ab.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/dps920ab.c

Purpose: PMBus driver for Delta DPS920AB power supplies. It verifies manufacturer/model strings, masks unsupported commands, exposes supported telemetry, allows fan command writes, and creates debugfs files for manufacturer ID/model.

Important APIs/types/functions: `struct dps920ab_data` stores duplicated manufacturer strings for debugfs. `dps920ab_read_word_data()` whitelists supported PMBus reads and returns `-ENXIO` for unsupported commands. `dps920ab_write_word_data()` allows only `PMBUS_FAN_COMMAND_1`. `dps920ab_info` declares one linear-format page. `dps920ab_init_debugfs()` creates `mfr_id` and `mfr_model` files.

Control flow: probe allocates private data, reads and validates `PMBUS_MFR_ID == "DELTA"` and model prefix `DPS-920AB`, stores strings, calls `pmbus_do_probe()`, then initializes debugfs under the PMBus root. PMBus core calls read/write hooks to prevent unsupported register access.

State and persistence: private state is only debugfs string storage. Hardware fan command writes persist in the PSU until changed. Unsupported commands are not cached.

Dependencies and integration: depends on PMBus core, I2C SMBus block/word operations, OF/I2C matching, and debugfs seq-file helpers.

Risks: whitelisting is conservative and may hide valid commands added by newer firmware. Manufacturer/model length checks are strict. Debugfs creation is optional after PMBus probe; missing debugfs does not affect hwmon.

Test signals: manufacturer/model rejection, visible hwmon files for declared capabilities, unsupported read suppression, fan command write success and other writes rejected, debugfs string files, and probe cleanup through devm allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/dps920ab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/fsp-3y.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/fsp-3y.c

Purpose: PMBus driver for FSP/3Y-Power YM-2151E and YH-5151E hot-swap power supplies. It handles nonstandard page numbering, required page-settle delays, and YH-5151E VOUT format variation.

Important APIs/types/functions: `struct fsp3y_data` embeds per-device PMBus info, detected chip ID, current real page, and `vout_linear_11` flag. `page_log_to_page_real()` maps logical PMBus pages to device-specific real page values. `set_page()` writes `PMBUS_PAGE` and waits 20-30 ms after changes. `fsp3y_read_byte_data()` fakes `VOUT_MODE` when needed. `fsp3y_read_word_data()` whitelists supported reads and performs linear11 VOUT conversion. `fsp3y_detect()` reads `PMBUS_MFR_MODEL`.

Control flow: probe allocates private data, detects the actual model, warns if configured I2C ID disagrees, reads current page, copies the static descriptor for that model, detects YH-5151E VOUT mode behavior, and calls PMBus core. All byte/word reads call `set_page()` first, translating PMBus logical pages to hardware pages and delaying after page changes.

State and persistence: state includes current real page and VOUT encoding mode in `fsp3y_data`. Hardware page selection changes during reads. Sensor values are not cached by this driver.

Dependencies and integration: depends on PMBus core, I2C SMBus byte/word/block operations, sleep/delay helpers, and direct model IDs. It imports namespace `PMBUS`.

Risks: page changes are timing-sensitive; reducing the delay can return wrong-page data. The whitelist excludes untested commands even if the device responds. VOUT format is detected per device by `VOUT_MODE == 0xff`; if firmware changes that indicator, scaling may break. Probe requires model block reads.

Test signals: model detection for both supported PSUs, logical-to-real page mapping, page delay behavior under repeated reads, YH-5151E linear11 fallback, unsupported command rejection, and visible attributes per page.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/fsp-3y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/hac300s.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/hac300s.c

Purpose: PMBus driver for Hi-Tron HAC300S PSUs. It fakes `VOUT_MODE` and strips linear11 exponents because the device does not follow PMBus VOUT linear16 expectations.

Important APIs/types/functions: `struct hac300s_data` embeds a per-device PMBus info copy and the detected VOUT exponent. `hac300s_probe()` reads `PMBUS_READ_VOUT` to derive the exponent, sets `PMBUS_NO_CAPABILITY`, and calls PMBus core. `hac300s_read_byte_data()` returns the stored exponent for `PMBUS_VOUT_MODE`. `hac300s_read_word_data()` reads VOUT-related commands and returns only the linear11 mantissa.

Control flow: probe checks SMBus byte/word support, reads VOUT once, extracts exponent bits, copies static info, installs platform data, and registers PMBus. PMBus core later calls hooks for VOUT mode and VOUT reads while other commands fall through to core/default behavior or `-ENODATA`.

State and persistence: the detected exponent is stored per device. Hardware state is not modified by the driver.

Dependencies and integration: depends on PMBus core, I2C, OF/I2C matching, bitfield helpers, and PMBus linear conversion.

Risks: the exponent is inferred at probe and assumed stable. Clearing exponent bits for all VOUT limit and read commands assumes the same encoding across those registers. `PMBUS_NO_CAPABILITY` bypasses device capability reporting, so the static descriptor must be accurate.

Test signals: VOUT scaling against known values, VOUT limit reads, probe error when initial VOUT read fails, absence of capability reads, and hwmon files for declared sensors/statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/hac300s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ibm-cffps.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ibm-cffps.c

Purpose: PMBus driver for IBM Common Form Factor power supplies. It supports CFFPS1/CFFPS2 variants, manufacturer-specific status mapping, 12V current-share monitoring, debugfs maintenance files, input history retrieval, and LED control.

Important APIs/types/functions: `struct ibm_cffps` stores version, I2C client, input-history buffer, debugfs entry indexes, LED name/state, and LED class device. `ibm_cffps_read_byte_data()` and `ibm_cffps_read_word_data()` merge manufacturer-specific fault bits into standard PMBus status and expose virtual VMON from `CFFPS_12VCS_VOUT_CMD`. Debugfs handlers read max power, CCIN, firmware version, on/off config, and long input history via raw I2C transfer. LED callbacks write `CFFPS_SYS_CONFIG_CMD`. `ibm_cffps_probe()` detects unknown variants from CCIN/MFR ID, runs PMBus probe, then optionally registers LED and debugfs.

Control flow: probe determines variant from I2C/OF match or auto-detection, sets PMBus platform flags `PMBUS_SKIP_STATUS_CHECK | PMBUS_NO_CAPABILITY`, calls `pmbus_do_probe()` with version-specific descriptors, then allocates optional private state. LED class registration writes initial LED off. Debugfs files use PMBus locks and page selection before raw SMBus/I2C commands. Input history uses raw I2C because the payload exceeds SMBus block length.

State and persistence: PMBus core owns hwmon state after probe. Optional state includes LED brightness/blink mode and cached input-history bytes for debugfs reads. Hardware LED state and on/off config persist in PSU registers. Debugfs compatibility symlink preserves old naming.

Dependencies and integration: depends on PMBus core lock/page helpers, I2C raw transfer, debugfs, LED class, OF/I2C matching, bitfields, and manufacturer PMBus commands. Kconfig requires `LEDS_CLASS`.

Risks: optional allocation failure after PMBus probe silently disables LED/debugfs but leaves hwmon working. Auto-detection relies on CCIN version/revision and manufacturer prefixes. Debugfs write to `on_off_config` accepts one raw byte from userspace. Raw input-history transfer must hold PMBus lock and page zero to avoid racing with core operations.

Test signals: cffps1/cffps2 auto-detection, status bit mapping from `STATUS_MFR_SPECIFIC`, VMON reading, LED on/off/blink behavior, debugfs files and input history, operation without debugfs/LED allocation, and PMBus lock correctness under concurrent reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ibm-cffps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ina233.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ina233.c

Purpose: PMBus driver for Texas Instruments INA233 power monitor. It configures calibration from shunt/current properties and exposes voltage, current, power, and shunt voltage monitoring.

Important APIs/types/functions: `calculate_coef()` derives direct-format PMBus coefficients from `Current_LSB` while managing integer precision and PMBus `m/R` limits. `ina233_read_word_data()` implements virtual VMON by reading manufacturer shunt voltage command `MFR_READ_VSHUNT` and scaling it to the VIN coefficient domain. `ina233_probe()` allocates a per-device `pmbus_driver_info`, reads `shunt-resistor` and `ti,maximum-expected-current-microamp` properties or defaults, computes coefficients, writes `MFR_CALIBRATION`, and calls PMBus core.

Control flow: probe builds the PMBus descriptor dynamically because current/power coefficients depend on board shunt and expected current. It validates nonzero shunt and minimum current, computes `current_lsb`, current and power coefficients, computes calibration as specified, rejects values exceeding 0x7fff, writes calibration, then registers PMBus. Virtual VMON reads are served through the driver hook.

State and persistence: per-device state is the allocated PMBus info and coefficients. Hardware state is modified by writing `MFR_CALIBRATION`; that calibration affects subsequent current/power measurements.

Dependencies and integration: depends on PMBus core, I2C SMBus word writes/reads, device properties, direct PMBus format support, and OF/I2C matching.

Risks: incorrect board properties produce wrong current/power units or invalid calibration. The default shunt and max-current assumptions may not match hardware. Coefficient scaling is integer-only and clamps to PMBus limits; precision-sensitive cases need validation. Calibration write failure aborts probe.

Test signals: property parsing, zero/too-small validation, calibration value bounds, current/power coefficient checks against datasheet examples, virtual shunt voltage scaling, and hwmon readings after calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ina233.c -->
