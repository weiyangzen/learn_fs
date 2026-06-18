# subset-b-005440 Research

Grouped source research for Linux thermal subsystem core code, Allwinner and generic ADC thermal drivers, NVIDIA Tegra thermal drivers, and the thermal core debug/testing helpers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/sun8i_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/sun8i_thermal.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/sun8i_thermal.c` is the platform thermal sensor driver for Allwinner sun8i/sun50i/sun20i THS blocks. It maps the MMIO THS register bank through regmap, calibrates sensor channels from NVMEM efuse data when available, registers one thermal zone per SoC sensor, and updates those zones from data-ready interrupts. The source was read as a complete 736-line file.

## Important APIs, Types, and Functions

The main data types are `struct ths_thermal_chip`, the SoC-specific operations/data table; `struct ths_device`, the devm-owned driver state; and `struct tsensor`, the per-zone channel object passed as thermal-zone private data. Important functions include `sun8i_ths_probe()`, `sun8i_ths_resource_init()`, `sun8i_ths_register()`, `sun8i_ths_get_temp()`, `sun8i_irq_thread()`, `sun8i_h3_ths_calibrate()`, `sun50i_h6_ths_calibrate()`, `sun8i_h3_thermal_init()`, and `sun50i_h6_thermal_init()`. The thermal API surface is the `ths_ops.get_temp` callback.

## Control Flow

Probe allocates `ths_device`, selects `ths_thermal_chip` via `of_device_get_match_data()`, maps the THS registers, enables/reset clocks as required by the chip descriptor, optionally accesses an SRAM control regmap for H616, and runs calibration. After the IRQ number is obtained, the chip-specific init routine programs acquisition timing, filtering, sampling period, channel enable bits, and data interrupt masks. The driver then registers all configured sensor zones with `devm_thermal_of_zone_register()` and only requests the threaded IRQ at the end to avoid updates before zones exist. Runtime temperature reads fetch a channel register, reject zero as no data yet with `-EAGAIN`, convert raw codes with the chip-specific formula, then apply `ft_deviation`. The IRQ thread acks per-channel status bits through the SoC-specific `irq_ack()` helper and calls `thermal_zone_device_update()` for each registered zone.

## State and Persistence Behavior

State is devm-owned and tied to the platform device lifetime. Calibration values are programmed into hardware registers at probe and are not persisted by the driver; the persistent source is NVMEM efuse data named `calibration`. Thermal zone state is owned by the thermal core. The H616 SRAM field is a one-bit hardware integration setting cleared during init.

## Dependencies and Integration Points

The driver depends on regmap, platform MMIO resources, reset/clock frameworks, NVMEM consumer APIs, optional SRAM regmap lookup through an `allwinner,sram` phandle, IRQ support, Device Tree compatible matching, `devm_thermal_of_zone_register()`, and `devm_thermal_add_hwmon_sysfs()`. Supported compatible strings include `allwinner,sun8i-a83t-ths`, `sun8i-h3-ths`, `sun8i-r40-ths`, `sun50i-a64-ths`, `sun50i-a100-ths`, `sun50i-h5-ths`, `sun50i-h6-ths`, `sun20i-d1-ths`, and `sun50i-h616-ths`.

## Risks and Edge Cases

Calibration is best-effort except for probe deferral; missing NVMEM leaves hardware working but less accurate. `sun8i_ths_resource_init()` calls `clk_set_rate(tmdev->mod_clk, 24000000)` even on chips where `has_mod_clk` is false, so behavior relies on the clock API tolerating the stored value on those platforms. Individual thermal-zone registration failures other than `-EPROBE_DEFER` are ignored, so a bad DT zone can silently reduce coverage. Raw zero readings return `-EAGAIN`, which depends on the thermal core recheck path. H6-style efuse packing for sensor 3 and 12-bit calibration clipping are easy to regress.

## Test Signals

Useful signals are DT binding/probe tests for each compatible, NVMEM-present and NVMEM-missing boot logs, IRQ-driven `thermal_zone_device_update()` behavior, sysfs/hwmon temperature reads after first conversion, calibration register programming checks on H3 and H6/H616 layouts, and suspend/resume or unbind tests that confirm devm cleanup asserts resets and disables clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/sun8i_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/thermal/tegra/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/Kconfig` defines the menu and build-time configuration switches for NVIDIA Tegra thermal drivers. The source was read as a complete 28-line file.

## Important APIs, Types, and Functions

This is a Kconfig fragment rather than C code. It declares `TEGRA_SOCTHERM`, `TEGRA_BPMP_THERMAL`, and `TEGRA30_TSENSOR` under the "NVIDIA Tegra thermal drivers" menu. The menu is available when `ARCH_TEGRA` or `COMPILE_TEST` is enabled.

## Control Flow

There is no runtime control flow. The configuration choices control whether the common SOCTHERM platform driver, BPMP firmware-backed thermal driver, or Tegra30 TSENSOR driver is compiled. `TEGRA_BPMP_THERMAL` depends on `TEGRA_BPMP || COMPILE_TEST`; `TEGRA30_TSENSOR` depends on `ARCH_TEGRA_3x_SOC || COMPILE_TEST`.

## State and Persistence Behavior

Kconfig selections persist only in the kernel build configuration. They affect object inclusion and module availability, not runtime state.

## Dependencies and Integration Points

The file integrates with the parent thermal Kconfig and the Tegra architecture symbols. Its selections are consumed by `drivers/thermal/tegra/Makefile` and by conditional declarations/match entries in the SOCTHERM C sources.

## Risks and Edge Cases

Broad `COMPILE_TEST` coverage is useful but can hide missing runtime dependencies if dependencies are too weak. `TEGRA_SOCTHERM` has no explicit per-SoC dependency here, so the linked descriptor objects depend on architecture-specific symbols in the Makefile and C preprocessor.

## Test Signals

Build matrix coverage for `ARCH_TEGRA`, `COMPILE_TEST`, modular builds, and per-driver disabled/enabled combinations verifies this file. `make oldconfig` and `make menuconfig` should expose help text and dependencies as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thermal/tegra/Makefile

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/Makefile` maps Tegra thermal Kconfig symbols to kernel objects. The source was read as a complete 10-line file.

## Important APIs, Types, and Functions

The key build targets are `tegra-soctherm.o`, `tegra-bpmp-thermal.o`, and `tegra30-tsensor.o`. The composite `tegra-soctherm-y` includes `soctherm.o` and `soctherm-fuse.o`, then conditionally adds `tegra114-soctherm.o`, `tegra124-soctherm.o`, `tegra132-soctherm.o`, and `tegra210-soctherm.o`.

## Control Flow

There is no runtime flow. Kbuild evaluates `obj-$(CONFIG_...)` and `tegra-soctherm-$(CONFIG_ARCH_TEGRA_..._SOC)` to build the proper object set.

## State and Persistence Behavior

State is the generated build graph and module composition. The file does not create runtime or persistent state.

## Dependencies and Integration Points

It integrates the Tegra thermal Kconfig symbols with kbuild. It also matches conditional externs in `soctherm.h` and `of_match_table` entries in `soctherm.c`, ensuring descriptors exist only for selected SoC families.

## Risks and Edge Cases

If a compatible is enabled in `soctherm.c` without the matching descriptor object in this Makefile, link failures or missing runtime matches result. Conversely, descriptor objects compiled without matching C preprocessor entries add dead code.

## Test Signals

Kernel build tests for each Tegra architecture symbol and module/static configurations are the primary signal. `nm` or module object inspection can verify the composite contains the expected descriptor symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm-fuse.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm-fuse.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm-fuse.c` computes Tegra SOCTHERM calibration words from SoC efuse fields. The common SOCTHERM driver calls it during probe before enabling raw sensors. The source was read as a complete 166-line file.

## Important APIs, Types, and Functions

The exported internal helpers are `tegra_calc_shared_calib()` and `tegra_calc_tsensor_calib()`. `div64_s64_precise()` is a local rounding helper used to avoid coarse truncation in fixed-point calibration math. It consumes `struct tegra_soctherm_fuse`, `struct tsensor_shared_calib`, and per-sensor `struct tegra_tsensor` metadata from `soctherm.h`.

## Control Flow

`tegra_calc_shared_calib()` reads the SoC common fuse register through `tegra_fuse_readl()`, extracts base CP/FT and shift CP/FT fields using the descriptor masks, optionally reads a spare realignment register for pre-Tegra210 layouts, sign-extends shift fields, and computes actual cold-point and factory-test temperatures. `tegra_calc_tsensor_calib()` reads each sensor fuse, derives actual sensor CP/FT values, calculates slope/intercept (`therma`, `thermb`) adjusted by sample and pdiv ratios, applies per-sensor correction coefficients, and packs the result into `SENSOR_CONFIG2_THERMA/THERMB` bitfields.

## State and Persistence Behavior

The file has no persistent state. It reads immutable fuse values and returns computed calibration words to the caller, which stores them in the driver's `tegra->calib[]` array and later writes sensor registers.

## Dependencies and Integration Points

It depends on `soc/tegra/fuse.h`, `div64_s64()`, `sign_extend32()`, and layout constants shared in `soctherm.h`. The SoC descriptor files provide masks, shifts, nominal FT temperatures, sensor fuse offsets, correction coefficients, pdiv values, and sampling parameters.

## Risks and Edge Cases

Fuse bitfield definitions are hardware ABI. A mask/shift error corrupts all temperatures for an SoC. The code performs signed fixed-point divisions where `delta_sens` and `delta_temp` must be valid; malformed fuses could cause invalid slopes. The `shifted_cp` path sign-extends from `val` after masking/extracting, so this logic should be reviewed carefully for each fuse layout. Rounding changes can alter thermal behavior and trip timing.

## Test Signals

Strong signals include boot-time calibration values compared against vendor tables, unit tests with known fuse vectors for Tegra114/124/132/210 layouts, sensor temperature sanity under ambient conditions, and probe failure coverage for `tegra_fuse_readl()` errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm-fuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm.c` is the common NVIDIA Tegra SOCTHERM thermal management driver for Tegra114/124/132/210-era SoCs. It calibrates and enables TSENSOR channels, registers thermal zones for CPU/GPU/MEM/PLLX groups, programs hardware thermal shutdown and throttle trips, manages over-current interrupt domains, exposes debugfs register dumps, and handles suspend/resume reinitialization. The source was read as a complete 2292-line file.

## Important APIs, Types, and Functions

The core private types are `struct tegra_soctherm`, `struct tegra_thermctl_zone`, `struct soctherm_throt_cfg`, `struct soctherm_oc_cfg`, and `struct soctherm_oc_irq_chip_data`. Important functions include `tegra_soctherm_probe()`, `soctherm_init()`, `enable_tsensor()`, `tegra_thermctl_get_temp()`, `tegra_thermctl_set_trips()`, `tegra_thermctl_set_trip_temp()`, `thermtrip_program()`, `throttrip_program()`, `tegra_soctherm_set_hwtrips()`, `soctherm_thermal_isr_thread()`, `soctherm_edp_isr_thread()`, `soctherm_oc_int_init()`, `soctherm_init_hw_throt_cdev()`, `tegra_soctherm_throttle()`, `soctherm_clk_enable()`, `soctherm_suspend()`, and `soctherm_resume()`. Its thermal-zone ops are `get_temp`, `set_trip_temp`, and `set_trips`.

## Control Flow

Probe matches a SoC descriptor, allocates `tegra_soctherm`, maps SOCTHERM plus CAR or CCROC registers, gets reset and clocks, computes shared and per-sensor calibration via `soctherm-fuse.c`, enables clocks, parses optional `nvidia,thermtrips` and `throttle-cfgs`, initializes raw sensors, pdiv/hotspot registers, and hardware throttling, then registers one thermal zone per sensor group. For each zone it immediately programs hardware trips from the DT thermtrips property or thermal critical trip fallback and optional hot-trip throttle binding. Interrupt setup creates a nested IRQ domain for over-current alarms and requests threaded thermal/EDP IRQs. Runtime thermal IRQs disable asserted level interrupts in the hard handler, clear expected status bits in the thread, and update the affected thermal zones. Over-current IRQs clear OC status, re-enable configured OC alarms, and dispatch nested IRQs when clients enabled them. Suspend disables clocks; resume reenables clocks, reinitializes hardware, and reprograms trips for each zone.

## State and Persistence Behavior

Driver state is devm-managed except debugfs and global OC IRQ chip data. Calibration words are computed at probe and stored in `tegra->calib[]`; hardware registers are reprogrammed on probe and resume. Thermal zones and cooling devices are registered with the thermal core. The `throt_cfgs` array captures parsed DT throttle configuration and cooling-device handles. Hardware stats registers are enabled and visible through debugfs but are not persisted across reset, suspend, or driver reload.

## Dependencies and Integration Points

The driver depends on MMIO resources named `soctherm-reg`, `car-reg`, or `ccroc-reg`, Tegra reset/clock providers, Tegra fuse reads, thermal core internals through `../thermal_core.h`, Device Tree thermal zone registration, cooling-device binding, IRQ domains, debugfs, and SoC descriptor tables from `tegra114/124/132/210-soctherm.c`. DT properties include `nvidia,thermtrips`, `throttle-cfgs`, `nvidia,priority`, CPU/GPU throttle fields, and OC alarm parameters.

## Risks and Edge Cases

Hardware trip programming is safety-critical: bad threshold grain, sign extension, group masks, or thermtrip parsing can prevent shutdown or cause false shutdown. `tegra_soctherm_set_hwtrips()` uses one `temperature` variable for both thermtrip and throttle programming; if a hot trip differs from the critical/thermtrip value, throttle behavior may not match policy expectations. Missing or invalid throttle DT leaves hardware throttling disabled but probe continues. `soctherm_interrupts_init()` returns success if either platform IRQ lookup fails, so systems without IRQ resources rely on polling/set_trips behavior. Global `soc_irq_cdata` assumes one active SOCTHERM instance. Debugfs register reads depend on live clocks/registers. Race safety around trip programming relies on disabling per-group interrupts and `thermctl_lock`.

## Test Signals

Test with real Tegra114/124/132/210 DTs should verify zone registration, sysfs temperatures, critical trip programming, hot-trip throttle binding, OC nested IRQ mapping, debugfs `soctherm/reg_contents`, suspend/resume reprogramming, and module remove clock cleanup. Fault-injection signals include missing resources, bad throttle-cfg nodes, fuse-read failures, missing IRQs, and thermal zone update events after synthetic register status changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm.h` is the shared contract between the common Tegra SOCTHERM driver, its fuse-calibration helper, and per-SoC descriptor files. The source was read as a complete 162-line file.

## Important APIs, Types, and Functions

The header defines register offsets and masks for thermal control, sensor temperature readbacks, pdiv/hotspot programming, and fuse offsets. It declares `struct tegra_tsensor_group`, `struct tegra_tsensor_configuration`, `struct tegra_tsensor`, `struct tsensor_group_thermtrips`, `struct tegra_soctherm_fuse`, `struct tsensor_shared_calib`, and `struct tegra_soctherm_soc`. It also declares `tegra_calc_shared_calib()` and `tegra_calc_tsensor_calib()` and conditionally declares `tegra114_soctherm`, `tegra124_soctherm`, `tegra132_soctherm`, and `tegra210_soctherm`.

## Control Flow

There is no executable flow. At build time it gives descriptor files a common structure layout and lets `soctherm.c` consume the descriptors uniformly. At runtime the objects described here drive sensor enabling, temperature register selection, pdiv/hotspot setup, trip programming, and fuse conversion.

## State and Persistence Behavior

The header defines state layout, not storage. Per-SoC files instantiate mostly `const` tables; the common driver stores pointers to those tables and mutable arrays such as `thermtrips`.

## Dependencies and Integration Points

It integrates with Tegra DT binding IDs, Tegra fuse register offsets, the common SOCTHERM MMIO programming model, and Kconfig-controlled SoC object inclusion. `soctherm-fuse.c` relies on the `SENSOR_CONFIG2_*` bit layout declared here.

## Risks and Edge Cases

Changing structure fields, masks, or register offsets affects multiple SoCs. Sensor group IDs must stay aligned across Tegra114 and Tegra124 binding constants, and the common driver asserts that equivalence. Threshold masks and `bptt` values must match hardware bit widths or trip programming/debugfs decoding will be wrong.

## Test Signals

Compile coverage across all supported Tegra SoC symbols is the first signal. Runtime signal comes from successful probe and plausible temperatures for every descriptor that includes this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra-bpmp-thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra-bpmp-thermal.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra-bpmp-thermal.c` is the firmware-backed thermal driver for Tegra SoCs where the BPMP coprocessor owns thermal sensing, notably Tegra186-compatible systems. It registers thermal zones for BPMP-reported sensors and forwards temperature/trip requests over MRQ_THERMAL. The source was read as a complete 328-line file.

## Important APIs, Types, and Functions

Key types are `struct tegra_bpmp_thermal` and `struct tegra_bpmp_thermal_zone`. Important functions are `tegra_bpmp_thermal_probe()`, `__tegra_bpmp_thermal_get_temp()`, `tegra_bpmp_thermal_set_trips()`, `tegra_bpmp_thermal_get_num_zones()`, `tegra_bpmp_thermal_trips_supported()`, `bpmp_mrq_thermal()`, `tz_device_update_work_fn()`, and `tegra_bpmp_thermal_remove()`. Thermal ops are selected with or without `.set_trips` depending on BPMP ABI support.

## Control Flow

Probe obtains the parent BPMP handle, queries whether `CMD_THERMAL_SET_TRIP` is supported, queries the number of zones, allocates a zone pointer array, and iterates every BPMP zone index. It probes each zone by requesting a temperature; errors other than `-EAGAIN` skip that zone. Successfully mapped zones are registered through `devm_thermal_of_zone_register()`, get a work item for updates, and are retained in `tegra->zones`. Finally the driver registers an MRQ handler. Runtime `.get_temp` sends `CMD_THERMAL_GET_TEMP`; `.set_trips` sends `CMD_THERMAL_SET_TRIP`. BPMP host-trip notifications are validated, matched to a zone index, acknowledged, and converted to `thermal_zone_device_update()` from process context via workqueue.

## State and Persistence Behavior

The driver maintains an in-memory list of registered zones and the BPMP handle. Trip state is persistent only inside BPMP firmware/hardware after `SET_TRIP` requests. Work items are per-zone and scheduled on BPMP notifications. Remove unregisters the MRQ handler but does not explicitly flush pending work in this file.

## Dependencies and Integration Points

It depends on `soc/tegra/bpmp.h`, BPMP ABI structures, parent device driver data, Device Tree thermal-zone registration, and the thermal core. It matches `nvidia,tegra186-bpmp-thermal`.

## Risks and Edge Cases

Powergated sensors can return `-EAGAIN` and are still registered, so users may see transient read failures. Zones not described in DT are skipped unless probe defers. Firmware ABI errors are collapsed to `-EINVAL`, limiting diagnostics. Pending work after MRQ unregister should be considered when changing remove paths. If BPMP does not support host trips, the driver intentionally omits `.set_trips`, so interrupt-driven updates may be reduced.

## Test Signals

Useful tests include BPMP ABI query success/failure, systems with unsupported `SET_TRIP`, powergated-zone reads returning `-EAGAIN`, MRQ host-trip notification delivery, zone registration count matching firmware, and remove/unbind tests with no later MRQ callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra-bpmp-thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra114-soctherm.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra114-soctherm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra114-soctherm.c` supplies Tegra114-specific SOCTHERM descriptor data for the common driver. The source was read as a complete 209-line file.

## Important APIs, Types, and Functions

There are no functions. The file defines Tegra114 thermtrip/threshold masks, `tegra114_tsensor_config`, four `tegra_tsensor_group` objects for CPU/GPU/PLL/MEM, the `tegra114_tsensors[]` sensor table, `tegra114_soctherm_fuse`, and the exported `const struct tegra_soctherm_soc tegra114_soctherm`.

## Control Flow

The common `soctherm.c` probe selects `tegra114_soctherm` for compatible `nvidia,tegra114-soctherm`. It then iterates these tables to calculate calibration, enable raw sensors, register group zones, program pdiv/hotspot offsets, decode temperature registers, and configure thermtrip/throttle thresholds.

## State and Persistence Behavior

The file owns static const descriptor state only. Runtime state is allocated by `soctherm.c`; hardware persistence is limited to register programming based on these constants.

## Dependencies and Integration Points

It depends on Tegra114 thermal DT binding IDs and the shared structures in `soctherm.h`. It integrates with `CONFIG_ARCH_TEGRA_114_SOC` through the Makefile/header and common OF match table.

## Risks and Edge Cases

Descriptor errors directly affect thermal safety. Fuse offsets, correction coefficients, pdiv values, hotspot differences, and threshold masks must match Tegra114 silicon. The file uses 8-bit threshold grain behavior (`TEGRA114_BPTT = 8`, `thresh_grain = 1000`), unlike Tegra210, so copying masks between SoCs would be hazardous.

## Test Signals

Probe on Tegra114 hardware should show four thermal zones and eight raw sensors. Temperature plausibility, debugfs register decoding, thermtrip programming for each group, and calibration comparison with vendor BSP values are primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra114-soctherm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra124-soctherm.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra124-soctherm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra124-soctherm.c` provides Tegra124-specific SOCTHERM tables for the common driver. The source was read as a complete 223-line file.

## Important APIs, Types, and Functions

The file is data-only. It defines Tegra124 thermtrip and thermctl masks, `tegra124_tsensor_config`, CPU/GPU/PLL/MEM group descriptors, eight sensor descriptors, `tegra124_soctherm_fuse`, and exported `tegra124_soctherm`.

## Control Flow

When `soctherm.c` matches `nvidia,tegra124-soctherm`, the common probe consumes these tables to compute fuse calibration, configure sensors, set pdiv/hotspot values, register thermal zones by binding ID, and program hardware trips.

## State and Persistence Behavior

All owned state is static descriptor data. Runtime state lives in the common driver, and hardware register state is reconstructed from this data at probe/resume.

## Dependencies and Integration Points

The file uses `dt-bindings/thermal/tegra124-soctherm.h` IDs and the SOCTHERM shared header. Its fuse descriptor references `FUSE_TSENSOR_COMMON` and spare realignment register `0x1fc` as described by `soctherm-fuse.c`.

## Risks and Edge Cases

The pre-Tegra210 fuse common-register layout and spare realignment field are fragile. Per-sensor alpha/beta coefficients differ across otherwise similar CPU/mem sensors, so table edits can produce local sensor bias. Group IDs are shared with Tegra132/210 descriptors, making binding compatibility important.

## Test Signals

Build with `CONFIG_ARCH_TEGRA_124_SOC`, boot on Tegra124, confirm four groups and eight sensors, compare ambient temperatures by group, inspect debugfs pdiv/hotspot/thermtrip values, and verify thermtrip thresholds use 1000 mC grain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra124-soctherm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra132-soctherm.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra132-soctherm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra132-soctherm.c` provides Tegra132 SOCTHERM descriptor data, including the flag that routes CPU throttling through CCROC. The source was read as a complete 223-line file.

## Important APIs, Types, and Functions

This descriptor-only file defines Tegra132 masks, `tegra132_tsensor_config`, CPU/GPU/PLL/MEM group descriptors, `tegra132_tsensors[]`, `tegra132_soctherm_fuse`, and exported `tegra132_soctherm` with `.use_ccroc = true`.

## Control Flow

The common driver selects this descriptor for `nvidia,tegra132-soctherm`. The `.use_ccroc` flag changes probe resource mapping from `car-reg` to `ccroc-reg` and changes throttle programming to use CCROC CPU-local pulse skipper configuration.

## State and Persistence Behavior

The file stores static tables only. Runtime `tegra_soctherm` state and CCROC/SOCTHERM register programming are derived from the tables and recreated on resume.

## Dependencies and Integration Points

It depends on Tegra124 thermal binding IDs, shared SOCTHERM structures, the pre-Tegra210 fuse layout, and `CONFIG_ARCH_TEGRA_132_SOC`. The common driver uses this file's `.use_ccroc` to decide register resources and throttle paths.

## Risks and Edge Cases

Tegra132 is close to Tegra124 but not identical. Incorrect `.use_ccroc`, CCROC resource availability, or CPU throttle level values can break hardware throttling. The sensor table is mutable rather than `const`, unlike adjacent descriptors, so accidental runtime writes would be possible if introduced.

## Test Signals

Validation should include CCROC resource mapping, CPU/GPU throttle configuration from DT, debugfs output for CCROC path, temperature plausibility for all groups, and suspend/resume trip reprogramming on Tegra132 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra132-soctherm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra210-soctherm.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra210-soctherm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra210-soctherm.c` supplies Tegra210 SOCTHERM descriptor data, including wider threshold fields and a mutable thermtrips table. The source was read as a complete 232-line file.

## Important APIs, Types, and Functions

The file defines Tegra210 thermtrip masks with 9-bit thresholds, `tegra210_tsensor_config`, CPU/GPU/PLL/MEM group descriptors, `tegra210_tsensors[]`, `tegra210_soctherm_fuse`, `tegra210_tsensor_thermtrips[]`, and exported `tegra210_soctherm`.

## Control Flow

The common SOCTHERM driver uses this descriptor for `nvidia,tegra210-soctherm`. Probe uses the Tegra210 fuse layout, computes calibration, initializes eight raw sensors, registers four thermal groups, parses DT thermtrips into the provided thermtrips array, and programs 500 mC-grain thresholds using `bptt = 9`.

## State and Persistence Behavior

Most state is static descriptor data. `tegra210_tsensor_thermtrips[]` is mutable so `soctherm_thermtrips_parse()` can store DT-provided group shutdown temperatures. Hardware register state is not persistent and is recreated on probe/resume.

## Dependencies and Integration Points

It uses Tegra124 thermal binding IDs for group numbering, Tegra fuse layout constants, shared SOCTHERM structures, and `CONFIG_ARCH_TEGRA_210_SOC`. It integrates with the common driver's thermtrip parser through `.thermtrips`.

## Risks and Edge Cases

Tegra210 has different thermtrip bit positions, 9-bit threshold fields, and 500 mC grain. Using older masks would corrupt shutdown thresholds. The initial thermtrips table uses sentinel IDs equal to `TEGRA124_SOCTHERM_SENSOR_NUM`; parser behavior depends on replacing entries with valid IDs.

## Test Signals

Boot tests should confirm thermtrips parsed from DT, debugfs threshold decoding at 500 mC granularity, plausible calibrated temperatures, hot-trip throttling, and correct behavior with and without `nvidia,thermtrips`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra210-soctherm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra30-tsensor.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra30-tsensor.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra30-tsensor.c` is the dedicated Tegra30 thermal sensor driver. It reads Tegra fuse calibration, enables two TSENSOR channels, registers thermal zones, converts hardware counters to temperatures, and programs interrupt/emergency shutdown thresholds. The source was read as a complete 678-line file.

## Important APIs, Types, and Functions

Key types are `struct tegra_tsensor`, `struct tegra_tsensor_channel`, `struct tegra_tsensor_calibration_data`, and `struct trip_temps`. Important functions include `tegra_tsensor_probe()`, `tegra_tsensor_nvmem_setup()`, `tegra_tsensor_hw_enable()`, `tegra_tsensor_hw_disable()`, `tegra_tsensor_register_channel()`, `tegra_tsensor_get_temp()`, `tegra_tsensor_temp_to_counter()`, `tegra_tsensor_set_trips()`, `tegra_tsensor_enable_hw_channel()`, `tegra_tsensor_disable_hw_channel()`, `tegra_tsensor_isr()`, and suspend/resume handlers.

## Control Flow

Probe allocates state, gets IRQ/MMIO/clock/reset, reads fuse calibration and ATE version, enables hardware, registers two thermal zones if DT provides them, programs channel thresholds, enables channels, and finally requests the threaded IRQ to avoid a race with threshold setup. Temperature reads poll `CURRENT_VALID`, read the current counter, reject overflow, and apply linear plus quadratic calibration. `set_trips` programs the high threshold into TH1 because low breaches are unsupported. Channel enable programs hot and critical thresholds from thermal trips or defaults, enables DVFS and emergency thermal reset interrupts, then enables the thermal zone. The ISR clears per-channel status and updates zones when interrupt bits are set. Suspend disables zones/channels then hardware; resume re-enables hardware and channels.

## State and Persistence Behavior

Calibration coefficients are computed once from fuses and stored in `ts->calib`. `swap_channels` is set for older ATE versions. Channel threshold registers and enable bits are volatile and reprogrammed on resume. Thermal-zone state is maintained by the core.

## Dependencies and Integration Points

The driver depends on Tegra fuse APIs, `tegra_sku_info.revision`, clock/reset frameworks, MMIO polling, threaded IRQs, Device Tree thermal zone registration, and hwmon thermal sysfs. It matches `nvidia,tegra30-tsensor`.

## Risks and Edge Cases

Invalid or old fuse data can disable probe (`ATE < 8`) or trigger channel remapping (`ATE <= 21`). Counter-valid polling can return errors if hardware is not ready. Quadratic conversion and inverse counter calculation must avoid invalid square-root inputs. The emergency shutdown trip is intentionally programmed 5 C above the critical thermal-zone trip, so policy changes should preserve that safety margin.

## Test Signals

Useful tests include fuse vectors for ATE versions, temperature plausibility on both channels, DTs with zero/one/two thermal zones, interrupt-triggered updates, TH1/TH2/TH3 register programming, suspend/resume, and missing/invalid calibration error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra30-tsensor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/testing/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thermal/testing/Makefile

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/testing/Makefile` builds the thermal core testing facility. The source was read as a complete 7-line file.

## Important APIs, Types, and Functions

The Makefile creates `thermal-testing.o` when `CONFIG_THERMAL_CORE_TESTING` is enabled. The composite object contains `command.o` and `zone.o`.

## Control Flow

There is no runtime flow here. Kbuild uses the config symbol to include or omit the debugfs testing module.

## State and Persistence Behavior

The file only affects build outputs. Runtime testing state is implemented by `command.c` and `zone.c`.

## Dependencies and Integration Points

It integrates `drivers/thermal/testing` into the kernel thermal build and depends on the Kconfig symbol being defined elsewhere.

## Risks and Edge Cases

If new testing source files are added without updating `thermal-testing-y`, module functionality will be incomplete. If the Kconfig symbol is enabled without debugfs support, the C files must still compile according to their own dependencies.

## Test Signals

Build `CONFIG_THERMAL_CORE_TESTING=m/y` and confirm the resulting object contains symbols from both command and zone handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/testing/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/testing/command.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/testing/command.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/testing/command.c` is the command parser and module entry for the thermal core debugfs testing facility. It exposes `/sys/kernel/debug/thermal-testing/command` so developers can create, modify, register, and unregister synthetic thermal zones. The source was read as a complete 211-line file.

## Important APIs, Types, and Functions

The exported global is `struct dentry *d_testing`. Important local pieces are `enum tt_commands`, `tt_command_strings[]`, `tt_command_exec()`, `tt_command_process()`, `tt_command_write()`, `thermal_testing_init()`, and `thermal_testing_exit()`. It calls zone helpers declared in `thermal_testing.h`: `tt_add_tz()`, `tt_del_tz()`, `tt_zone_add_trip()`, `tt_zone_reg()`, `tt_zone_unreg()`, and `tt_zone_cleanup()`.

## Control Flow

Module init creates the `thermal-testing` debugfs directory and a write-only `command` file. Writes are single-shot (`*ppos` must be zero), capped at 15 bytes plus NUL, copied from userspace, trimmed, split on optional `:`, matched against known command strings, and dispatched to the zone layer. Module exit removes the debugfs root and asks the zone layer to unregister/free all templates.

## State and Persistence Behavior

The file owns only the debugfs root pointer. Test-zone state lives in `zone.c` and is volatile; it disappears at module unload or reboot.

## Dependencies and Integration Points

It depends on debugfs, module init/exit, and the thermal testing zone API. It is meant for controlled test environments and uses debugfs rather than sysfs ABI.

## Risks and Edge Cases

The command buffer is deliberately small; invalid or too-long commands fail with `-EINVAL` or `-E2BIG`. Commands requiring an argument pass `NULL` when no colon is present; the zone helpers must reject that safely. `debugfs_create_dir()` errors are only checked with `IS_ERR`, and init returns 0 even if debugfs creation fails, which is normal for debug-only facilities but affects test availability.

## Test Signals

Manual debugfs tests should cover `addtz`, `deltz:<id>`, `tzaddtrip:<id>`, `tzreg:<id>`, and `tzunreg:<id>`, invalid commands, oversized writes, nonzero offset writes, and module unload cleanup after registered zones exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/testing/command.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/testing/thermal_testing.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/testing/thermal_testing.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/testing/thermal_testing.h` is the small internal header shared by the thermal testing command and zone modules. The source was read as a complete 11-line file.

## Important APIs, Types, and Functions

It declares the shared debugfs root `d_testing` and the zone-management functions `tt_add_tz()`, `tt_del_tz()`, `tt_zone_add_trip()`, `tt_zone_reg()`, `tt_zone_unreg()`, and `tt_zone_cleanup()`.

## Control Flow

There is no runtime flow. The declarations let `command.c` dispatch debugfs commands to `zone.c`.

## State and Persistence Behavior

The header does not own state. It exposes state owned by `command.c` and functions managing state in `zone.c`.

## Dependencies and Integration Points

The file requires `struct dentry` to be visible to C users that include it after debugfs headers. It forms the internal ABI of `thermal-testing.o`.

## Risks and Edge Cases

Because this is an internal header, signature drift between command and zone code will be caught at compile time. It has no include guard, but the small declarations are harmless in current usage; adding definitions would require a guard.

## Test Signals

Compilation of `command.o` and `zone.o` together validates this file. Runtime command dispatch confirms the prototypes remain correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/testing/thermal_testing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/testing/zone.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/testing/zone.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/testing/zone.c` implements synthetic thermal-zone templates for thermal core testing. It lets debugfs commands create templates, add editable trip templates, register a real `test_tz` thermal zone from a template, update its temperature, and clean everything up. The source was read as a complete 447-line file.

## Important APIs, Types, and Functions

The main private types are `struct tt_thermal_zone`, `struct tt_trip`, and `struct tt_work`. Public functions are `tt_add_tz()`, `tt_del_tz()`, `tt_zone_add_trip()`, `tt_zone_reg()`, `tt_zone_unreg()`, and `tt_zone_cleanup()`. Key helpers include `tt_zone_get_temp()`, `tt_zone_register_tz()`, `tt_zone_unregister_tz()`, `tt_get_tt_zone()`, `tt_put_tt_zone()`, and workqueue callbacks that create/remove debugfs files.

## Control Flow

`tt_add_tz()` allocates a template, assigns an ID, initializes locks/list/IDA, and schedules work to create `tzN` debugfs files. `tt_zone_add_trip()` gets a referenced template, allocates a trip, assigns a trip ID, appends it under the zone lock, and schedules debugfs files for `trip_N_temp` and `trip_N_hyst`. `tt_zone_reg()` copies trip templates into a temporary array, registers a thermal zone named `test_tz`, stores the initial temperature, and enables the zone. Writes to the template `temp` debugfs file update `tz_temp` and call `thermal_zone_device_update()`. Deletion refuses referenced templates, unregisters an active thermal zone, removes the template from the global list, and schedules debugfs removal/freeing.

## State and Persistence Behavior

All state is in memory: global `tt_thermal_zones`, global IDA, per-template trip IDA/list, debugfs dentries, current template temperature, registered-zone current temperature, and a `refcount` protecting async work/deletion. No state survives unload or reboot.

## Dependencies and Integration Points

It depends on debugfs, IDA, lists, mutex guards, workqueues, and the thermal zone registration API. It integrates with `command.c` through `thermal_testing.h` and with the thermal core by registering real test zones using `thermal_zone_device_register_with_trips()`.

## Risks and Edge Cases

Most debugfs mutations are deferred to workqueue context to avoid manipulating debugfs from debugfs write operations. This makes reference counting important: missed `tt_put_tt_zone()` calls could block deletion, while premature deletion could race async work. Trip templates are copied at registration, so later template trip-file writes do not update an already registered zone's trip array unless the thermal core sysfs files for that zone are used. `tt_int_set()` rejects values below `THERMAL_TEMP_INVALID`, but casts from `u64` to `int`, so very large writes can wrap.

## Test Signals

Exercise the full command flow: add zone, add trips, change template trip values, register, write `temp`, observe thermal core notifications/trip crossing, unregister, delete, and unload. Race-oriented tests should delete while async debugfs work is pending and attempt deletion while references are held.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/testing/zone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal-generic-adc.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal-generic-adc.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/thermal-generic-adc.c` is a generic thermal sensor driver that reads an IIO ADC channel and exposes the value as a thermal zone, optionally converting ADC readings through a Device Tree lookup table. It also registers an IIO temperature channel that reads back the thermal value. The source was read as a complete 230-line file.

## Important APIs, Types, and Functions

The core state type is `struct gadc_thermal_info`. Important functions are `gadc_thermal_probe()`, `gadc_thermal_get_temp()`, `gadc_thermal_adc_to_temp()`, `gadc_thermal_read_linear_lookup_table()`, `gadc_iio_register()`, and `gadc_thermal_read_raw()`. The thermal ops provide `.get_temp`; the IIO info provides `.read_raw`.

## Control Flow

Probe requires a DT node, obtains IIO channel `sensor-channel`, reads optional `temperature-lookup-table`, registers thermal zone index 0 through `devm_thermal_of_zone_register()`, adds hwmon sysfs, then registers a direct-mode IIO device exposing processed temperature. Runtime temperature reads call `iio_read_channel_processed()`, then either return the raw processed value as milliCelsius or interpolate between lookup-table pairs. The IIO read path calls back into the thermal get-temp path.

## State and Persistence Behavior

State is devm-managed and device-lifetime scoped. The lookup table is copied from DT into memory. No persistent state is written.

## Dependencies and Integration Points

The driver depends on IIO consumer/provider APIs, Device Tree property parsing, thermal zone registration, hwmon thermal sysfs, and platform-driver matching on `generic-adc-thermal`. It assumes lookup-table entries are alternating temperature and ADC values.

## Risks and Edge Cases

Lookup-table ordering matters: the conversion loop assumes ADC values are ordered so `val >= adc` finds the correct bracket. Without a lookup table, non-temperature IIO channels trigger only a notice and raw processed readings are treated as milliCelsius. Odd-length tables fail probe. Interpolation divides by `adc_lo - adc_hi`, so duplicate ADC values would be dangerous if not prevented by data quality.

## Test Signals

Test with no table and IIO_TEMP channels, no table and non-temperature ADC channels, valid descending/ascending table examples matching driver expectation, odd-length table rejection, boundary clamping to first/last temperature, thermal sysfs reads, and IIO processed reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal-generic-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_core.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_core.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/thermal_core.c` is the central Linux thermal subsystem implementation. It registers the thermal class, governors, thermal zones, and cooling devices; runs the zone update loop; handles trip crossing, polling, hardware trip windows, critical shutdown, cdev binding, PM transitions, hwmon/debug/netlink integration, and exported registration APIs. The source was read as a complete 1921-line file.

## Important APIs, Types, and Functions

Major exported APIs include `thermal_register_governor()`, `thermal_unregister_governor()`, `thermal_zone_device_set_policy()`, `thermal_zone_device_enable()`, `thermal_zone_device_disable()`, `thermal_zone_device_update()`, `thermal_cooling_device_register()`, `thermal_of_cooling_device_register()`, `devm_thermal_of_cooling_device_register()`, `thermal_cooling_device_unregister()`, `thermal_cooling_device_update()`, `thermal_zone_get_crit_temp()`, `thermal_zone_device_register_with_trips()`, `thermal_tripless_zone_device_register()`, `thermal_zone_device_unregister()`, `thermal_zone_get_zone_by_name()`, `thermal_pm_prepare()`, and `thermal_pm_complete()`. Important internal functions include `thermal_set_governor()`, `__thermal_zone_device_update()`, `thermal_zone_handle_trips()`, `thermal_trip_crossed()`, `thermal_bind_cdev_to_trip()`, `thermal_zone_init_complete()`, and `thermal_init()`.

## Control Flow

`thermal_init()` initializes debugfs/netlink, creates the `thermal_events` workqueue, registers built-in governors from the linker table, and registers the thermal class. Zone registration validates inputs, allocates a flexible `thermal_zone_device` with trip descriptors, initializes trip lists, binds a governor, creates sysfs/hwmon/thresholds, registers the device, adds the zone to `thermal_tz_list`, binds existing cooling devices, performs an initial update, emits notifications, and creates debugfs state. The update loop locks the zone, reads temperature, handles transient and repeated read failures, updates trace/netlink state, moves trip descriptors between high/reached/invalid lists, notifies userspace/debugfs, invokes critical or hot callbacks, sets hardware low/high trip windows, lets thresholds adjust them, calls the governor `manage()` hook, updates debug stats, and schedules polling if needed. Cooling-device registration validates ops, allocates IDs/state, registers the class device, creates debugfs, adds it to `thermal_cdev_list`, and binds it to existing zones. Unregister paths unbind instances, remove debugfs/hwmon/sysfs, unregister devices, wait for release completions, and free IDs/memory. PM prepare marks zones suspended and cancels polling; PM complete queues immediate resume work that reinitializes zones and updates governors.

## State and Persistence Behavior

Global runtime state includes IDAs for zone/cdev IDs, `thermal_tz_list`, `thermal_cdev_list`, `thermal_governor_list`, `def_governor`, suspend state, and the workqueue. Per-zone state includes trip descriptors and sorted lists, mode, temperatures, passive count, governor data, thermal instances, polling work, user thresholds, and debugfs data. Per-cdev state includes current maximum state, thermal instance bindings, sysfs/debugfs state, and stats. None of this is file-persistent; it is rebuilt at boot/module load.

## Dependencies and Integration Points

The core integrates with Linux device class/sysfs, IDA, workqueues, PM notifications, reboot/hardware protection, hwmon (`thermal_hwmon.h`), generic netlink, tracepoints, threshold support, debugfs, Device Tree helper APIs in other files, and governor implementations declared through `THERMAL_GOVERNOR_DECLARE()`. Drivers in this subset call into this file through thermal-zone and cooling-device APIs.

## Risks and Edge Cases

This file is concurrency-sensitive: list locks, per-zone locks, cdev locks, completion ordering, and PM work replacement must remain consistent. Repeated temperature read failures back off then disable a zone, which can be dangerous if a zone has critical trips. Trip list relocation must correctly handle invalid trips, hysteresis, and dynamic trip temperature changes. Governor unregister assumes zones have valid governor pointers in list iteration. Binding creates sysfs links/files and must unwind exactly. `thermal_zone_get_zone_by_name()` returns a raw pointer without taking a device reference. PM prepare/complete interactions wait for in-flight resume work to avoid stale locks.

## Test Signals

Thermal core tests should cover zone/cdev registration/unregistration, duplicate and failed cdev binding, all trip types crossing upward/downward, hysteresis and dynamic trip updates, polling and `-EAGAIN` recheck behavior, governor switching and unregister, cooling-device max-state shrink, PM prepare/complete, critical trip hardware protection, hwmon/debugfs/netlink notifications, and the thermal testing module's synthetic zones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_core.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_core.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/thermal_core.h` is the private thermal subsystem header shared across core, sysfs, governors, debugfs, thresholds, and helper modules. It defines the internal thermal-zone, trip, governor, and instance structures that back the public thermal APIs. The source was read as a complete 309-line file.

## Important APIs, Types, and Functions

Key types are `struct thermal_attr`, `struct thermal_trip_attrs`, `struct thermal_trip_desc`, `struct thermal_governor`, `struct thermal_zone_device`, and `struct thermal_instance`. It defines state flags `TZ_STATE_FLAG_SUSPENDED`, `TZ_STATE_FLAG_RESUMING`, `TZ_STATE_FLAG_INIT`, `TZ_STATE_FLAG_EXIT`, the `THERMAL_NO_TARGET` sentinel, default governor selection macros, governor linker-table macros, iteration helpers, guards for zone locking, `trip_to_trip_desc()`, and prototypes for thermal core/sysfs/helper functions.

## Control Flow

The header contributes no executable flow by itself. It shapes how `thermal_core.c` moves trips among lists, how governors are declared and discovered, how sysfs/debugfs access shared state, and how cooling devices bind to trips.

## State and Persistence Behavior

It defines in-memory runtime state layout. `struct thermal_zone_device` contains device identity, completions, trip lists, temperatures, delays, ops, governor data, locks, poll work, state flags, optional debugfs state, user thresholds, and a flexible array of trip descriptors. `struct thermal_instance` describes one cdev-to-trip binding.

## Dependencies and Integration Points

It includes public `linux/thermal.h`, cleanup guards, device APIs, thermal netlink, thresholds, and debugfs headers. It is intentionally private: platform drivers normally include `linux/thermal.h`, while subsystem internals and `soctherm.c` use this header for helper access.

## Risks and Edge Cases

Structure changes can affect many thermal subsystem files. Lock guard semantics are embedded here; misuse can deadlock or unlock incorrectly. The default governor macro depends on exactly one Kconfig default. Flexible array and `__counted_by(num_trips)` require registration allocation to stay aligned. Trip descriptor list membership must stay consistent with `threshold`.

## Test Signals

Compile coverage for all thermal governors, sysfs, debugfs, thresholds, and platform drivers catches many issues. Runtime registration/unregistration and lockdep tests are important after changing structures or guard definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/thermal_debugfs.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/thermal_debugfs.c` implements debugfs observability for the thermal subsystem. It records cooling-device state transitions/residency and thermal-zone mitigation episodes/trip statistics under `/sys/kernel/debug/thermal`. The source was read as a complete 968-line file.

## Important APIs, Types, and Functions

Important types are `struct thermal_debugfs`, `struct cdev_debugfs`, `struct cdev_record`, `struct tz_debugfs`, `struct tz_episode`, and `struct trip_stats`. Public functions called by the core include `thermal_debug_init()`, `thermal_debug_cdev_add()`, `thermal_debug_cdev_state_update()`, `thermal_debug_cdev_remove()`, `thermal_debug_tz_add()`, `thermal_debug_tz_trip_up()`, `thermal_debug_tz_trip_down()`, `thermal_debug_update_trip_stats()`, `thermal_debug_tz_remove()`, and `thermal_debug_tz_resume()`.

## Control Flow

Initialization creates `thermal/cooling_devices` and `thermal/thermal_zones` debugfs directories. Cooling-device add allocates a debug object, initializes hash buckets for transitions and durations, records the initial state, and creates files for `trans_table`, `time_in_state_ms`, `clear`, and `total_trans`. State updates compute old-state residency, create/update transition records keyed by old/new state, update current state, and increment totals. Thermal-zone add allocates per-zone episode state and a `mitigations` seq file. Trip-up starts an episode if needed, records crossed trip IDs and start timestamps. Trip-down finds the trip in the active stack, closes its duration, and closes the episode when the last active trip drops. Periodic update stats maintain max, min, and running average temperatures. Resume closes any in-progress mitigation episode so post-resume handling starts cleanly.

## State and Persistence Behavior

All state is debug-only, in memory, and attached to the cdev or thermal zone. Cooling-device records are hash lists of transition counts and state residency durations. Thermal-zone records are a list of mitigation episodes with flexible per-trip stats. Removing a cdev/zone detaches the pointer under the object lock, frees lists, removes debugfs directories, and frees memory. State is not persistent across reboot, unregister, or debugfs removal.

## Dependencies and Integration Points

It depends on debugfs, seq_file helpers, ktime, lists, mutexes, and thermal core private structures. It is called synchronously from core registration, cdev state updates, trip crossing paths, zone updates, unregister, and resume.

## Risks and Edge Cases

Debugfs must not destabilize thermal control. Allocation failures are intentionally tolerated by leaving debugfs absent. Lock ordering with thermal zone/cdev locks matters when clearing debugfs pointers. The trip-crossed stack can see reordered or dynamically changed trips; the code handles missing downward matches by ignoring them. Cooling transition IDs pack two 16-bit states, so extremely large state IDs could truncate in display logic. The cdev clear path resets records but leaves current state/timestamp behavior important for later duration accounting.

## Test Signals

Signals include debugfs tree creation, cooling-device transition table and residency output after cdev state changes, clear-file behavior, mitigation episode output after synthetic trip crossings, unregister cleanup with no use-after-free under lockdep/KASAN, and resume closing active mitigation episodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/thermal_debugfs.c -->
