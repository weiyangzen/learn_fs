# Research: subset-b-003836 PMBus hwmon drivers

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2975.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2975.c

Purpose: implements PMBus hwmon support for MPS MP2971, MP2973, and MP2975 multiphase VR controllers. It translates multiple vendor-specific register layouts into the generic PMBus core model, including rail count, virtual phase current readings, VOUT encoding, over/under-voltage thresholds, peak telemetry, SMBALERT masking, and optional regulator registration.

Important APIs, types, and functions: `struct mp2975_data` extends `pmbus_driver_info` with chip id, per-rail max phase counts, VID step, VREF, VOUT max/OV data, and current sense gain. `mp2975_probe()` selects static template info from `mp2975_ddinfo`, detects rail 2, identifies phase topology, detects VID mode, programs direct VOUT format, gathers VREF and threshold scale data, then calls `pmbus_do_probe()`. `mp2975_read_word_data()` and `mp2973_read_word_data()` map PMBus limits, peaks, and per-phase IOUT to vendor registers. `mp2973_write_word_data()` implements a custom 16-bit SMBALERT mask mapping. `mp2975_read_byte_data()` forces `PMBUS_VOUT_MODE` to direct because MP2975 continues reporting VID after direct format is configured.

Control flow: probe obtains match data, allocates private state, copies a PMBus info template, checks rail-2 phase count on page 2, fills `info->pages`, `info->phases`, `info->func`, and optionally regulator count. It then identifies rail-1/rail-2 phase function bits, VID families, current-sense gain, VREF, OV scale, and per-rail direct VOUT formatting before generic PMBus registration. Runtime reads first pass through driver callbacks; unhandled registers return `-ENODATA` so the core can use standard PMBus access, while deliberately unsupported limits return `-ENXIO`.

State and persistence behavior: no persistent kernel state beyond devm-managed `mp2975_data` and PMBus core sensor cache. Probe writes hardware configuration registers to force direct VOUT format, so it changes device runtime configuration. Optional regulator descriptors expose rail control through the core. Reads of phase current combine vendor phase-current bytes with total rail current divided by active phases to avoid under-reporting at light load.

Dependencies and integration points: depends on I2C SMBus byte/word operations, `pmbus.h` helpers, PMBus virtual phase support, optional `CONFIG_SENSORS_MP2975_REGULATOR`, and the generic PMBus core. It integrates with hwmon via `pmbus_do_probe()` and regulator framework through `PMBUS_REGULATOR` descriptors.

Risks and test signals: high risk comes from variant-specific page numbers, phase indexing, and encoded threshold math. Probe writes to page 2 and configuration registers; failures should abort cleanly. Test with MP2971/2973/2975 devices in one- and two-rail configurations, verify `curr*_input` per-phase attributes, VOUT limits, peak history attributes, SMBALERT masking on MP2973, regulator rail count, and that `pmbus_check_*` does not expose the deliberately blocked limit registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2975.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2993.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2993.c

Purpose: supports the MPS MP2993 two-rail multiphase digital VR controller by adapting non-standard voltage/current/temperature limit encodings to PMBus hwmon attributes.

Important APIs, types, and functions: `mp2993_info` declares two pages with direct VIN/VOUT/temperature formats and linear IIN/IOUT/power. `mp2993_identify()` forces VOUT mode on both pages to direct via `mp2993_set_vout_format()`. `mp2993_read_word_data()` rescales VOUT OV/UV limits, VIN readings and limits, and redirects shared over-temperature limits to page 0. `mp2993_write_word_data()` applies inverse scaling for writable limits and rewrites linear11 exponent fields with `mp2993_linear11_exponent_transfer()`.

Control flow: `mp2993_probe()` passes static info to `pmbus_do_probe()`. During PMBus core identification, the driver `identify` callback writes `PMBUS_VOUT_MODE` on page 0 and page 1. Later core register probes and sysfs reads route selected registers through the driver's read/write callbacks; normal telemetry such as READ_IOUT/READ_VOUT returns `-ENODATA` to allow generic core handling, while unknown registers return `-EINVAL`.

State and persistence behavior: the driver has no private allocation and no software cache beyond the PMBus core. It does persistently modify the device VOUT format in hardware during identification. Limit writes change PMBus or vendor-backed limit registers and use fixed exponent conversion for IIN/IOUT over-current limits.

Dependencies and integration points: depends on SMBus byte/word I2C operations, MPS-compatible device tree or I2C IDs, and PMBus core conversion logic. Integration is through `pmbus_do_probe()` with function masks for rail 1 and rail 2 status categories.

Risks and test signals: key risk is scale mismatch, especially VOUT OV/UV conversion using `125/64`, VIN `1/32 V` telemetry, and VIN limit `1/8 V`. Test rail 1 versus rail 2 status/telemetry, over-temperature limits shared on page 0, writable current limits, and that direct VOUT mode is actually set before core capability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2993.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp5023.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp5023.c

Purpose: provides a compact PMBus hwmon driver for the MPS MP5023 hot-swap controller. It is a static adapter that supplies direct-format coefficients and supported sensor/status masks to the PMBus core.

Important APIs, types, and functions: `mp5023_info` is the main artifact. It declares one page, direct format for VIN, VOUT, IOUT, power, and temperature, and direct coefficients for each class. `mp5023_probe()` only calls `pmbus_do_probe(client, &mp5023_info)`. The OF match table exposes `mps,mp5023`.

Control flow: module loading registers an I2C driver. Probe uses no custom detection or register access and immediately delegates to the PMBus core, which probes standard registers and creates hwmon attributes based on the supplied `func[0]` bits.

State and persistence behavior: no private state and no hardware configuration writes. All runtime state is in the generic PMBus core cache and hwmon device.

Dependencies and integration points: depends entirely on `pmbus_core.c` for SMBus access, conversion, status checking, sysfs attributes, and fault handling. It imports the PMBus namespace and integrates with device tree through `mps,mp5023`.

Risks and test signals: risk is limited to coefficient accuracy and function-mask completeness. Test sensor unit scaling for voltage/current/power/temp and verify expected input and temperature status alarms appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp5023.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp5920.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp5920.c

Purpose: supports MP5920-compatible hot-swap controllers with a static PMBus configuration plus a manufacturer model identity check.

Important APIs, types, and functions: `mp5920_info` declares direct format coefficients for VIN, VOUT, IOUT, POUT, and temperature. `mp5920_probe()` checks SMBus read-word support, reads `PMBUS_MFR_MODEL`, requires exactly `MP5920`, then calls `pmbus_do_probe()`.

Control flow: probe validates adapter functionality, reads model block data, rejects unexpected model strings with `dev_err_probe()`, and delegates registration to PMBus core. There are no custom read/write callbacks, so all attributes use standard PMBus registers.

State and persistence behavior: no driver-private mutable state and no persistent hardware writes. The only runtime state is the PMBus core cache and hwmon registration.

Dependencies and integration points: depends on I2C block reads for model validation and PMBus core for telemetry. It supports both OF `mps,mp5920` and I2C ID `mp5920`.

Risks and test signals: model string length is strict (`ret == 6`), so firmware/device variants with padded or altered model blocks may fail to bind. Test model validation, direct coefficient scaling, and expected VIN/VOUT/IOUT/POUT/temp hwmon files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp5920.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp5926.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp5926.c

Purpose: supports MPS MP5926 PMBus devices whose telemetry can be configured for either direct or linear mode, including a VOUT encoding quirk where the chip uses LINEAR11 for output voltage.

Important APIs, types, and functions: `struct mp5926_data` embeds `pmbus_driver_info` and tracks `vout_mode` plus extracted VOUT exponent. `mp5926_probe()` reads `EFUSE_CFG` to decide linear versus direct mode and reads `I_SCALE_SEL` to adjust current-in scaling in direct mode. `mp5926_read_byte_data()` overrides `PMBUS_VOUT_MODE`; `mp5926_read_word_data()` masks/converts `PMBUS_READ_VOUT` mantissa when in linear mode.

Control flow: probe allocates private info, copies the template, inspects EFUSE bit 12, adjusts formats and coefficients, then registers through `pmbus_do_probe()`. During core identification, VOUT mode reads are virtualized so the core sees a compatible mode despite device quirks.

State and persistence behavior: private state is devm-managed and immutable after probe. The driver does not write hardware configuration. Runtime reads depend on cached probe-derived mode and exponent.

Dependencies and integration points: uses PMBus helper access and standard I2C SMBus word reads. It integrates with PMBus core through custom read callbacks and function masks for VIN/VOUT/IIN/PIN/temp/status.

Risks and test signals: mode detection is critical; wrong EFUSE interpretation changes all sensor formats. Test both linear and direct configurations, VOUT exponent extraction from READ_VOUT, current-in coefficient selection by `I_SCALE_SEL`, and alarms for input, temperature, and VOUT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp5926.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp5990.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp5990.c

Purpose: supports MPS MP5990 and MP5998 hot-swap controllers with variant-specific direct coefficients and a VOUT mode quirk similar to MP5926.

Important APIs, types, and functions: `struct mp5990_data` stores copied PMBus info and VOUT mode/exponent. `mp5990_probe()` selects `mp5990_info` or `mp5998_info` from OF/I2C match data, reads `MP5990_EFUSE_CFG`, and switches formats to linear when bit 9 indicates linear VOUT. `mp5990_read_byte_data()` overrides `PMBUS_VOUT_MODE`, while `mp5990_read_word_data()` converts READ_VOUT from LINEAR11 mantissa to what the PMBus core expects.

Control flow: probe allocates per-device info, selects variant, reads VOUT configuration, possibly updates all relevant sensor classes to linear and reads the VOUT exponent. Runtime read callbacks only intercept `PMBUS_VOUT_MODE` and `PMBUS_READ_VOUT`; other registers fall back to generic core access.

State and persistence behavior: no hardware writes. Private state persists for mode-dependent conversions and copied coefficient tables. PMBus core owns cache, sysfs, and status handling.

Dependencies and integration points: uses OF match data for `mps,mp5990`/`mps,mp5998`, I2C ID fallback, and PMBus core. MP5998 enables IIN/POUT and status IOUT in addition to MP5990's smaller mask.

Risks and test signals: risk is variant/mode mismatch. Test MP5990 and MP5998 separately, both direct and linear EFUSE modes, VOUT scaling, IIN/POUT presence on MP5998, and core identification when the datasheet VOUT_MODE behavior is misleading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp5990.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp9941.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp9941.c

Purpose: supports the MPS MP9941 single-rail VR controller by configuring device resolution fields and translating vendor-scaled VIN/IIN/VOUT limit registers.

Important APIs, types, and functions: `struct mp9941_data` tracks copied info and VID resolution. `mp9941_identify()` sets IIN scale, identifies VID resolution, and forces VOUT direct format. `mp9941_read_word_data()` rescales READ_VIN, READ_IIN, VIN OV fault, IIN OC warning, and VOUT UV/rated min/max values. `mp9941_write_word_data()` applies inverse conversions for writable VIN/VOUT/IIN/temp limits.

Control flow: probe allocates private state, copies `mp9941_info`, and delegates to the core. The core invokes `identify`, which writes vendor configuration on pages 0 and 2. Runtime access then routes selected registers through custom conversions and returns `-ENODATA` for standard linear/direct telemetry handled by core.

State and persistence behavior: persistent device configuration is changed at probe: IIN scale and VOUT direct format. The stored VID resolution affects later VOUT limit conversions. The PMBus core handles caching and sysfs.

Dependencies and integration points: uses bitfield helpers, SMBus byte/word access, and PMBus function masks for VIN/VOUT/IIN/IOUT/PIN/POUT/temp/status. Integration is PMBus core only; no regulator descriptors.

Risks and test signals: configuration writes can alter device behavior and require hardware validation. Test VID resolution discovery, 5 mV versus 10 mV scaling, IIN scale writes, VIN and VOUT limits round-trip, and failure recovery when page 2 vendor registers are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp9941.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp9945.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp9945.c

Purpose: supports MPS MP9945 single-phase VR controllers whose VOUT may be VID, direct, or linear16, and normalizes that into direct mV values for PMBus core exposure.

Important APIs, types, and functions: `struct mp9945_data` stores VOUT mode, VID resolution, and VID offset. `mp9945_identify()` reads actual `PMBUS_VOUT_MODE`, reads page-3 vendor registers for VID resolution/offset, then returns to page 0. `mp9945_read_vout()` converts READ_VOUT based on stored mode. Custom read callbacks override VOUT_MODE to direct and convert VOUT OV/UV fault/warn limits.

Control flow: probe allocates copied info, forces page 0 before core probing, and calls `pmbus_do_probe()`. During identify, mode and VID parameters are latched. All later custom reads force page 0 and translate selected VOUT-related registers.

State and persistence behavior: no device configuration writes except page selection. Private state stores mode and VID parameters. Runtime conversion is deterministic from that probe state.

Dependencies and integration points: depends on PMBus core, bitfield helpers, and SMBus access. It exposes VIN/VOUT/IIN/IOUT/PIN/POUT/temp/status masks through the generic hwmon framework.

Risks and test signals: mode-specific conversion is the main risk, particularly VID offset from `MFR_SVID_CFG_R1` and linear16 scaling by `125/64`. Test all three VOUT modes, page restoration to 0, VOUT warning/fault limit conversions, and that core sees direct VOUT mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp9945.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mpq7932.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mpq7932.c

Purpose: supports MPS MPQ7932 and MPQ2286 PMIC/buck regulators as PMBus hwmon devices with optional regulator framework integration.

Important APIs, types, and functions: `struct mpq7932_data` embeds `pmbus_driver_info` and platform data. `mpq7932_probe()` sets page count from match data, configures direct VOUT coefficients, fills per-page VOUT/status/temp function masks, disables capability probing, and optionally attaches regulator descriptors. `mpq7932_write_word_data()` converts VOUT_COMMAND word writes to byte writes. `mpq7932_read_word_data()` fakes VOUT min/max and maps READ_VOUT to byte VOUT_COMMAND reads.

Control flow: OF match data selects one page for MPQ2286 or six pages for MPQ7932. Probe builds per-instance info and platform flags, assigns custom callbacks, then calls `pmbus_do_probe()`. The PMBus core handles hwmon and regulator registration if enabled.

State and persistence behavior: no private mutable state after probe. VOUT_COMMAND writes from sysfs/regulator are real hardware writes but are byte-sized due to device access limitations. Fake min/max allow regulator voltage setting to pass core margin checks.

Dependencies and integration points: depends on PMBus core, optional `CONFIG_SENSORS_MPQ7932_REGULATOR`, and device tree match data. It uses `PMBUS_NO_CAPABILITY` to avoid unsupported capability probing.

Risks and test signals: byte-versus-word access is critical; accidental word access returns remote I/O errors. Test voltage reads/writes, regulator list/set voltage, one-page and six-page variants, and absence of capability command probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mpq7932.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mpq8785.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mpq8785.c

Purpose: supports MPS MPQ8785, MPM3695, MPM3695-25, and MPM82504 step-down converters with variant-specific VOUT handling and optional feedback divider programming.

Important APIs, types, and functions: `mpq8785_info` supplies base coefficients. `mpq8785_probe()` copies info, selects chip from OF/I2C data, adjusts VOUT coefficients and callbacks by variant, optionally writes `PMBUS_VOUT_SCALE_LOOP` from `mps,vout-fb-divider-ratio-permille`, then calls `pmbus_do_probe()`. `mpq8785_identify()` interprets VOUT_MODE; `mpq8785_read_byte_data()` reports VID as direct for MPQ8785; `mpm82504_read_word_data()` sign-extends temperature.

Control flow: probe variant switch configures either direct VOUT for MPM variants or identify/read-byte override for MPQ8785. Optional property validation checks against chip-specific maximum mask before writing scale-loop. Generic core handles all remaining telemetry.

State and persistence behavior: no software state beyond copied PMBus info. Probe may persistently write feedback-divider scale to hardware if the device property is present.

Dependencies and integration points: uses PMBus core, OF/device properties, and I2C match data. It exposes VIN/VOUT/IOUT/temp and status bits through core hwmon attributes.

Risks and test signals: property validation and VOUT_MODE override are key. Test each compatible, with and without `mps,vout-fb-divider-ratio-permille`, invalid divider values, MPQ8785 VID-as-direct identification, and MPM82504 negative temperature readings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mpq8785.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pim4328.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pim4328.c

Purpose: supports Flex/PIM4006, PIM4328/BMR455, and PIM4820 power interface modules by mapping manufacturer-specific input telemetry and status bits into generic PMBus hwmon attributes.

Important APIs, types, and functions: `struct pim4328_data` stores chip id and PMBus info. `pim4328_probe()` validates `PMBUS_MFR_MODEL` against the I2C ID table, sets platform flags, and fills functions by variant. `pim4328_read_word_data()` maps per-phase VIN/IIN reads to manufacturer registers. `pim4328_read_byte_data()` augments `PMBUS_STATUS_BYTE` using variant-specific manufacturer status registers.

Control flow: probe requires SMBus byte/block support, reads model block, matches the detected device, allocates platform data with `PMBUS_NO_CAPABILITY | PMBUS_NO_WRITE_PROTECT`, and configures virtual phases or direct coefficients. PMBus core then discovers attributes, including per-phase labels where `PMBUS_PHASE_VIRTUAL` is used.

State and persistence behavior: no hardware writes except normal PMBus core actions; capability and write-protect probing are disabled. Private state stores detected variant for status mapping.

Dependencies and integration points: uses PMBus coefficients command for PIM4328/PIM4820 direct modes via `PMBUS_USE_COEFFICIENTS_CMD`. Integrates with PMBus virtual phase support and core status checking.

Risks and test signals: status translation can produce false alarms if manufacturer bit definitions are wrong. Test model detection, mismatch notice, per-phase VIN/IIN attributes on PIM4006/PIM4328, coefficient command path, and status-byte augmentation for input UV, output UV, over-temperature, and input faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pim4328.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pli1209bc.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pli1209bc.c

Purpose: supports the Vicor PLI1209BC digital supervisor, exposing page-1 BCM telemetry and optional VOUT regulator control while avoiding known capability-probing problems.

Important APIs, types, and functions: `pli1209bc_plat_data` disables capability probing. `pli1209bc_read_word_data()` rescales READ_POUT, and returns zero for READ_VOUT/temperature when status indicates power-good-not. `pli1209bc_info` defines two pages but only page 1 function bits, direct coefficients, write delay, and optional regulator descriptor `vout2`.

Control flow: probe assigns platform data and calls `pmbus_do_probe()`. PMBus core sees two pages but only builds hwmon attributes for page 1. Selected reads are intercepted for power scaling and off-state invalid-data suppression.

State and persistence behavior: no private allocation. The driver sets a 250 us write delay consumed by PMBus core access timing. Regulator state, if enabled, is handled by PMBus core operations.

Dependencies and integration points: depends on PMBus core, optional `CONFIG_SENSORS_PLI1209BC_REGULATOR`, and regulator framework. It imports `linux/pmbus.h` platform flags and PMBus namespace.

Risks and test signals: returning zero for off-state VOUT/temp hides invalid data but may be interpreted as a real zero. Test page-1-only attribute exposure, off/on BCM behavior, READ_POUT scaling, write delay effects, and regulator enable/voltage paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pli1209bc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pm6764tr.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pm6764tr.c

Purpose: supports ST PM6764TR digital controllers, mainly by exposing a manufacturer-specific VMON reading through the PMBus virtual VMON register.

Important APIs, types, and functions: `pm6764tr_read_word_data()` maps `PMBUS_VIRT_READ_VMON` to vendor register `0xD4`. `pm6764tr_info` sets one page with linear VIN/temp/current/power, VID VOUT, VMON support, and status masks. `pm6764tr_probe()` delegates to `pmbus_do_probe()`.

Control flow: no custom identify. During core attribute discovery, `PMBUS_HAVE_VMON` causes the core to check/read the virtual VMON register, which this driver maps to the vendor register. Other reads fall back to core through `-ENODATA`.

State and persistence behavior: no private state and no hardware writes.

Dependencies and integration points: depends on PMBus core virtual register semantics and VID conversion for VOUT. Integrates through I2C and OF `st,pm6764tr`.

Risks and test signals: confirm that VMON maps to the intended rail and uses voltage-in class scaling. Test VMON sysfs attributes, VOUT VID conversion, and normal VIN/IIN/PIN/IOUT/POUT/temp status exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pm6764tr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pmbus.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pmbus.c

Purpose: implements the generic PMBus I2C driver used for devices that do not need a dedicated chip driver. It dynamically identifies page count, VOUT format, supported sensors, and status register availability, then delegates all runtime behavior to the PMBus core.

Important APIs, types, and functions: `struct pmbus_device_info` holds preset page count and platform flags. `pmbus_find_sensor_groups()` probes standard PMBus read/status registers and fills `info->func[]`. `pmbus_identify()` discovers pages, VOUT_MODE, rejects unsupported direct-mode coefficient handling, and calls sensor probing. `pmbus_probe()` allocates `pmbus_driver_info`, optional platform data, assigns `identify`, and calls `pmbus_do_probe()`.

Control flow: match data supplies one page, dynamic pages, or platform flags. If pages are unspecified, the driver tests PAGE support by setting successive pages up to the PMBus maximum. It clears faults, reads VOUT_MODE, sets voltage-out format for VID/direct/linear where possible, and probes standard telemetry groups before core registration.

State and persistence behavior: allocated `pmbus_driver_info` and optional platform data are devm-managed. Page detection changes the device PAGE register and clears faults. No per-device private state is retained outside PMBus core data.

Dependencies and integration points: uses `pmbus_check_*`, `pmbus_set_page()`, `pmbus_clear_faults()`, and `pmbus_do_probe()` from the core. The large I2C ID table maps many simple PMBus devices to generic handling and flags such as `PMBUS_SKIP_STATUS_CHECK`.

Risks and test signals: dynamic probing can perturb device fault state and may reject direct-mode devices that need coefficients. Test generic devices with/without PAGE, one-page skip/status flags, VID VOUT mode, and that unsupported direct coefficient cases fail with `-ENODEV` rather than exposing wrong units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pmbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pmbus.h -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pmbus.h

Purpose: defines the internal PMBus driver contract shared by `pmbus_core.c`, the generic driver, and chip-specific hwmon drivers. It centralizes standard and virtual register IDs, status bits, sensor classes, formats, capability flags, regulator helper macros, callback hooks, and exported helper prototypes.

Important APIs, types, and functions: `enum pmbus_regs` lists standard PMBus commands and virtual registers for history, VMON, fan/PWM, and sample controls. `struct pmbus_driver_info` is the main integration object: pages, phases, formats, coefficients, function masks, callbacks, regulator descriptors, custom attribute groups, and timing delays. Function masks such as `PMBUS_HAVE_VIN`, `PMBUS_HAVE_STATUS_VOUT`, `PMBUS_PHASE_VIRTUAL`, and `PMBUS_PAGE_VIRTUAL` drive core attribute generation. Regulator macros create `regulator_desc` entries bound to PMBus regulator ops.

Control flow: chip drivers fill `pmbus_driver_info` and pass it to `pmbus_do_probe()`. The core uses callback return conventions: `-ENODATA` means fall back to standard PMBus access, while other negative errors mean the register should be treated as unavailable or failed. Virtual registers must be implemented by chip callbacks unless the core supplies default fan target handling.

State and persistence behavior: this header has no state, but it defines how state is represented: per-page formats and coefficients, per-phase masks, cached core data reached through exported helpers, and access/write/page-change delays consumed by the core.

Dependencies and integration points: includes Linux bitops, cleanup guard support, and regulator descriptors. It exports PMBus namespace helpers for SMBus access, cache clearing, page setting, fault clearing, fan control, driver-info retrieval, locking, and debugfs directory discovery.

Risks and test signals: callback semantics and unit formats are easy to misuse. Test by building multiple chip drivers against the header, verifying namespace exports, virtual-register behavior, write-protection effects, regulator descriptor macros, and guard-based PMBus locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pmbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pmbus_core.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pmbus_core.c

Purpose: implements the shared PMBus hwmon core: SMBus access serialization, page/phase handling, sensor caching, data-format conversion, dynamic hwmon sysfs attribute creation, alarms, fault clearing, PEC/write-protect handling, thermal zone registration, optional regulator operations, IRQ/SMBALERT processing, and debugfs exposure.

Important APIs, types, and functions: `struct pmbus_data` stores device state, flags, PMBus revision, VOUT exponents, driver info, generated attribute groups, sensor list, lock, regulator work, current page/phase, VOUT margins, and access backoff. Exported helpers include `pmbus_set_page()`, `pmbus_read_word_data()`, `pmbus_write_word_data()`, `pmbus_check_*_register()`, `pmbus_clear_faults()`, `pmbus_get_driver_info()`, `pmbus_update_fan()`, locks, and `pmbus_do_probe()`. Conversion functions handle linear, direct, VID, and IEEE754 formats in both directions.

Control flow: `pmbus_do_probe()` validates SMBus functionality, allocates core state, initializes common chip behavior, runs chip identify, validates pages and VOUT modes, optionally reads direct coefficients, creates dynamic hwmon attributes based on `info->func[]`, registers hwmon groups, regulators, IRQ handler, and debugfs entries. Runtime sysfs reads lock the client, refresh cached sensor values as needed, convert units, and emit values. Writes convert userspace units back to PMBus register format and invalidate cache. Alarm reads check status registers, clear latched bits if possible, and can compare live values against limits.

State and persistence behavior: sensor readings are cached per `pmbus_sensor` until invalidated or marked update-on-read. The core tracks current page/phase to avoid redundant PAGE/PHASE writes and enforces access/write/page-change delays. It may clear PMBus faults, write write-protect settings from module parameter `wp`, enable PEC, mask SMBALERT sources, and notify regulators asynchronously. Device-managed allocations clean up on detach; debugfs root exists module-wide.

Dependencies and integration points: integrates with Linux I2C/SMBus, hwmon, hwmon-sysfs, thermal framework, debugfs, regulator framework, workqueues, IRQ subsystem, and PMBus platform data flags. Chip drivers supply `pmbus_driver_info` and optional callbacks/custom groups; the core supplies the common user-visible ABI.

Risks and test signals: broad blast radius. Critical risks include unit conversion errors, callback fallback semantics, page/phase races, clearing latched faults while probing, write-protect handling, regulator status mapping, IRQ notification correctness, and debugfs lifetime. Test with devices using each format, virtual registers, phases, fans/PWM, samples, regulators, PEC, write-protected devices, SMBALERT IRQ, and chips with status-byte-only versus status-word support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pmbus_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pxe1610.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pxe1610.c

Purpose: supports Infineon PXE1610, PXE1110, and PXM1310 multipage controllers with VID VOUT conversion based on VOUT_MODE parameters.

Important APIs, types, and functions: `pxe1610_identify()` reads `PMBUS_VOUT_MODE` on up to three pages and maps mode parameter 1 to VR12 and 2 to VR13. If a later page is unsupported it truncates `info->pages`. `pxe1610_probe()` forces page 0, verifies manufacturer ID `XP`, copies the static info, and calls `pmbus_do_probe()`.

Control flow: probe checks byte/word/block SMBus support, sets PAGE to 0 because the device may not boot there, validates MFR_ID, then delegates. The identify callback decides per-page VRM version before the PMBus core creates VID-scaled VOUT attributes.

State and persistence behavior: no private mutable state beyond copied info. Probe writes PAGE register to 0 but does not otherwise configure hardware.

Dependencies and integration points: depends on PMBus core VID conversion and I2C block reads. Exposes three potential pages with VIN/VOUT/IIN/IOUT/PIN/POUT/temp/status masks.

Risks and test signals: failure to start on page 0 or unknown VOUT mode rejects the device. Test manufacturer validation, one/two/three-page variants, VR12/VR13 VOUT scaling, and page truncation when later VOUT_MODE reads fail or contain unsupported parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pxe1610.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/q54sj108a2.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/q54sj108a2.c

Purpose: supports Delta Q54SJ108A2, Q54SN120A1, and Q54SW120A7 DC/DC modules with normal PMBus hwmon telemetry plus a custom debugfs interface for module operations, blackbox history, flash key, and response settings.

Important APIs, types, and functions: `q54sj108a2_info` declares one-page PMBus telemetry. `struct q54sj108a2_data` stores client and debugfs entry indices. `q54sj108a2_probe()` validates manufacturer ID, model, and revision before calling `pmbus_do_probe()`, then creates debugfs files under the PMBus debugfs directory. `q54sj108a2_debugfs_read()` reads PMBus standard and vendor blackbox registers; `q54sj108a2_debugfs_write()` unlocks write protect and performs commands such as clear fault, store default, response writes, blackbox erase, and offset set.

Control flow: probe first ensures SMBus byte/word/block support and rejects non-Delta or unsupported model/revision devices. After core hwmon registration, it allocates debugfs state and creates a file per command. Debugfs operations use `file->private_data` indices to dispatch to command-specific SMBus operations.

State and persistence behavior: hwmon state is generic PMBus core state. Debugfs writes can persistently alter module configuration (`STORE_DEFAULT_ALL` after flash key), clear faults, erase blackbox data, change PMBus operation and fault responses, and disable write protection. Debugfs directory removal is not explicitly registered in this driver, relying on debugfs hierarchy/device lifetime behavior.

Dependencies and integration points: integrates with PMBus core, PMBus debugfs root via `pmbus_get_debugfs_dir()`, Linux debugfs, I2C SMBus block/byte/word operations, and OF/I2C matching.

Risks and test signals: debugfs write surface is powerful and must be tested carefully. Risks include off-by-one lengths in debugfs read formatting, persistent flash writes, blackbox erase, and missing cleanup if debugfs parent is absent. Test manufacturer/model/revision validation, hwmon attribute creation, every debugfs read/write command, write-protect unlock behavior, and behavior when PMBus debugfs root is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/q54sj108a2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/stef48h28.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/stef48h28.c

Purpose: provides static PMBus hwmon support for the ST STEF48H28 controller/eFuse.

Important APIs, types, and functions: `stef48h28_info` declares one page, direct formats for voltage/current/power/temperature, direct coefficients, and a broad function mask including VIN, VOUT, IIN, IOUT, PIN, POUT, TEMP1/TEMP2, and related statuses. `stef48h28_probe()` delegates to `pmbus_do_probe()`.

Control flow: module registers an I2C driver with OF and I2C IDs. Probe has no custom detection or callbacks; the PMBus core handles attribute creation and SMBus runtime access.

State and persistence behavior: no private state, no hardware configuration writes, and no custom persistence behavior.

Dependencies and integration points: depends on PMBus core for conversion, status, sysfs, and fault handling. Device tree compatible is `st,stef48h28`.

Risks and test signals: risk centers on coefficient correctness and whether all declared sensors/status registers exist on hardware. Test direct scaling for all classes, TEMP2 exposure, and alarms for input/output/current/temperature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/stef48h28.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/stpddc60.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/stpddc60.c

Purpose: supports STPDDC60/BMR481 controllers with custom handling for mixed VID and LINEAR VOUT encodings and relative VOUT fault-offset registers.

Important APIs, types, and functions: `stpddc60_get_offset()` converts absolute VOUT limit requests into 50 mV offset codes relative to VID VOUT_COMMAND. `stpddc60_adjust_linear()` rewrites linear11 values to a fixed exponent. `stpddc60_read_byte_data()` forces VOUT_MODE to linear. `stpddc60_read_word_data()` maps READ_VOUT to manufacturer register and masks linear11 mantissas. `stpddc60_write_word_data()` handles VOUT fault offsets and fixed-exponent limit writes. Probe validates MFR_MODEL, assigns callbacks, calls core, then marks VOUT fault limits update-on-read.

Control flow: probe verifies SMBus support and model, assigns custom callbacks into static info, registers with PMBus core, and updates core sensor flags for VOUT OV/UV fault limits. Runtime reads/writes intercept VOUT and selected limit registers; other accesses fall back to core.

State and persistence behavior: no private allocation. Writes to VOUT OV/UV limits persist as vendor offset bytes, not absolute PMBus values. `pmbus_set_update()` forces limit attributes to be reread because the hardware stores limits relative to current VOUT_COMMAND.

Dependencies and integration points: depends on PMBus core, virtual update flags, and I2C SMBus block/model validation. Integrates with standard hwmon attributes for VIN/VOUT/IOUT/POUT/temp/status.

Risks and test signals: VOUT limit conversion can be surprising when requested limits cross the current VOUT. Test VOUT read scaling, OV/UV limit write/read round-trips, fixed-exponent rewriting for other limits, model validation for `stpddc60` and `bmr481`, and update-on-read after changing VOUT_COMMAND.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/stpddc60.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tda38640.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tda38640.c

Purpose: supports Infineon TDA38640 PMBus controllers, with optional regulator support and a workaround for SVID mode where OPERATION control must be represented through ON_OFF_CONFIG polarity.

Important APIs, types, and functions: `struct tda38640_data` embeds PMBus info and `en_pin_lvl`. `svid_mode()` performs a raw I2C transfer to read MTP offset `0x44`, detects SVID mode, and infers enable-pin level from STATUS_BYTE and ON_OFF_CONFIG. `tda38640_read_byte_data()` maps ON_OFF_CONFIG polarity to `PB_OPERATION_CONTROL_ON`; `tda38640_write_byte_data()` maps OPERATION writes back to ON_OFF_CONFIG polarity. Optional regulator descriptor uses `PMBUS_REGULATOR_ONE_NODE`.

Control flow: probe copies static info. If regulator support is enabled and DT property `infineon,en-pin-fixed-level` is present, it detects SVID mode; only then does it install OPERATION read/write callbacks. Registration proceeds through `pmbus_do_probe()`.

State and persistence behavior: private state stores inferred enable-pin level. In SVID workaround mode, regulator enable/disable operations can write both OPERATION and ON_OFF_CONFIG polarity, changing persistent device behavior.

Dependencies and integration points: depends on PMBus core, optional regulator framework, device tree property parsing, and a raw I2C transfer for MTP reads. It exposes standard linear PMBus telemetry for one page.

Risks and test signals: SVID-mode enable mapping is subtle; incorrect `en_pin_lvl` inverts regulator state. Test with and without the DT property, SVID and non-SVID modes, regulator enable/disable/is_enabled, and normal hwmon telemetry/status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tda38640.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tps25990.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tps25990.c

Purpose: supports TI TPS25990 eFuse devices with direct-format telemetry, manufacturer-specific history/average/min/peak registers, configurable sample count, custom write-protect mapping, RIMON-dependent current/power scaling, VMON VAUX, and optional regulator integration.

Important APIs, types, and functions: `tps25990_base_info` defines formats, coefficients, virtual register callbacks, and optional regulator descriptor. `tps25990_probe()` reads `ti,rimon-micro-ohms` or uses a default, copies info, adjusts current and power coefficients with `tps25990_set_m()`, and calls `pmbus_do_probe()`. `tps25990_read_word_data()` maps PMBus virtual history registers to vendor min/peak/avg registers, rescales 8-bit limits, maps VIREF to IIN OC fault, and exposes samples. `tps25990_write_word_data()` implements inverse conversions and global history reset. Byte callbacks map standard write-protect to `TPS25990_MFR_WRITE_PROTECT`.

Control flow: core probes one page and virtual registers based on function masks. All min/max/average/history/sample accesses enter driver callbacks; standard telemetry and status use generic PMBus reads. Probe-time coefficient adjustment makes each instance match its board RIMON value.

State and persistence behavior: no private state after copied info. Writes can change PMBus limits, VIREF over-current cutoff, sample averaging count, reset min/avg/peak history, and manufacturer write-protect state. Coefficients are per-instance runtime data, not global.

Dependencies and integration points: depends on PMBus core virtual registers, device property API, bitfield helpers, optional `CONFIG_SENSORS_TPS25990_REGULATOR`, and direct coefficients. It exposes VMON through VAUX and sample controls through PMBus core sample attributes.

Risks and test signals: scaling is dense and board-dependent. Test default and DT-provided RIMON, current/power units, 8-bit limit shift conversions, VIN OV fault and IIN OC fault round-trips, history reset behavior, sample count powers of two, write protect lock/unlock, VAUX VMON, and regulator registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tps25990.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tps40422.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tps40422.c

Purpose: provides static PMBus hwmon support for TI TPS40422 two-page controllers.

Important APIs, types, and functions: `tps40422_info` declares two pages, linear VIN/VOUT/temperature formats, and per-page VOUT, TEMP2, IOUT, and status masks. `tps40422_probe()` delegates directly to `pmbus_do_probe()`.

Control flow: the I2C driver binds by ID and calls the PMBus core without custom detection or callbacks. The core creates page-suffixed VOUT/current/temp attributes based on the two identical function masks.

State and persistence behavior: no private state and no custom hardware writes.

Dependencies and integration points: depends entirely on PMBus core for access, conversions, status, and sysfs. It has I2C ID matching but no OF table in this source.

Risks and test signals: low driver complexity; risk is function mask accuracy. Test two-page attribute creation, TEMP2 naming, IOUT status alarms, and linear VOUT conversion on both rails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tps40422.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tps53679.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tps53679.c

Purpose: supports a family of TI multiphase VR controllers including TPS53647/667/676/679/681/685/688 and BMR474, adapting VID modes, phase counts, chip identity checks, and TPS53681 total-current behavior.

Important APIs, types, and functions: `tps53679_info` is copied per device and includes per-phase IOUT masks. `tps53679_identify_mode()` maps VOUT_MODE protocol parameters to VR12/VR13 VID versions. `tps53679_identify_chip()` validates PMBus revision and IC_DEVICE_ID. Variant identify functions adjust pages, formats, and phase counts. `tps53681_read_word_data()` uses PHASE `0x80` for total page-0 READ_IOUT.

Control flow: probe selects chip ID from match data, copies base info, and switches variant-specific pages/identify/read callbacks. Core calls identify during common init. TPS53676 reads a user-data block to count active phases on rail A/B; TPS53681/685 perform stricter chip ID validation.

State and persistence behavior: no private state beyond copied `pmbus_driver_info`. There are no configuration writes except normal PMBus page/phase access by core. Identified phase counts and VRM versions persist in the copied info for conversion and attribute creation.

Dependencies and integration points: depends on PMBus core VID conversion, I2C block reads for identity/phase data, OF and I2C match tables, and PMBus virtual phase support for per-phase IOUT attributes.

Risks and test signals: family variants differ significantly. Test each supported ID, strict chip-ID failures, VR12/VR13 mode mapping, TPS53676 phase discovery, TPS53681 total READ_IOUT override, per-phase current attributes, and TPS53685 linear VOUT plus page-1 input telemetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tps53679.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tps546d24.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tps546d24.c

Purpose: provides PMBus hwmon support for the TI TPS546D24 buck converter with a small probe-time VOUT_MODE correction.

Important APIs, types, and functions: `tps546d24_info` declares one page, linear formats for VIN/VOUT/temp/IOUT, and function masks for VIN/IIN/IOUT/VOUT/temp/status. `tps546d24_probe()` reads `PMBUS_VOUT_MODE`; if bit 7 is set, it writes the register back with that bit cleared before calling `pmbus_do_probe()`.

Control flow: probe performs the VOUT_MODE cleanup first, then delegates all discovery and runtime handling to the PMBus core. There are no custom callbacks.

State and persistence behavior: probe may persistently modify `PMBUS_VOUT_MODE` by clearing bit 7. No software-private state exists.

Dependencies and integration points: depends on SMBus byte reads/writes and PMBus core. Supports OF compatible `ti,tps546d24` and I2C ID matching.

Risks and test signals: clearing bit 7 assumes it is safe and required for core linear VOUT interpretation. Test devices with bit 7 set and clear, VOUT scaling after modification, and standard current/temperature/status attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/tps546d24.c -->
