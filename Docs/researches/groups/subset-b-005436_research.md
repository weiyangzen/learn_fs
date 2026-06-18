# Research: subset-b-005436

This grouped report covers the thermal-driver source files assigned to `subset-b-005436`. Each section preserves the source path in the title and is bounded by reconciliation markers for deterministic split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/armada_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/armada_thermal.c

## Purpose
Marvell EBU Armada thermal sensor platform driver. It supports older legacy DT bindings that map individual MMIO regions and newer syscon-based bindings, exposes thermal zones through the Linux thermal framework, handles SoC-specific calibration formulas, and optionally programs an overheat interrupt threshold for Armada AP/CP devices.

## Important APIs, Types, and Functions
- `struct armada_thermal_priv` stores the device, regmap/syscon, thermal zone name, channel-selection lock, SoC data, overheat IRQ bookkeeping, and current threshold/hysteresis.
- `struct armada_thermal_data` is the SoC descriptor: init callback, temperature conversion coefficients, status bit layout, syscon offsets, DFX IRQ fields, and `cpu_nr`.
- `struct armada_thermal_sensor` binds one thermal-zone instance to a channel id.
- SoC init functions (`armadaxp_init()`, `armada370_init()`, `armada375_init()`, `armada380_init()`, `armada_ap80x_init()`, `armada_cp110_init()`) program reset, calibration, OSR, averaging, and errata settings.
- `armada_select_channel()` serializes channel changes, switches internal/external sensor mode, restarts conversion, and waits for validity.
- `armada_read_sensor()` extracts the sample, optionally sign-extends it, and applies `temp = (b - m * reg) / div` or the inverted variant.
- `armada_get_temp_legacy()` serves tripless legacy zones; `armada_get_temp()` serves OF zones with channel selection and reselects the overheat-source channel.
- `armada_configure_overheat_int()`, `armada_set_overheat_thresholds()`, and the threaded IRQ pair implement hardware critical-threshold interrupt support.
- `armada_thermal_probe()` chooses legacy vs syscon path, registers thermal zones, requests optional IRQs, and iterates all channels.

## Control Flow
Probe matches an OF compatible to a descriptor, allocates private state, and probes in one of two modes. If the parent is not a syscon regmap, the driver creates a small regmap around the old register resource, initializes the sensor, waits for validity, registers one tripless thermal zone, and enables it. In syscon mode it obtains the parent regmap, initializes the hardware, optionally requests a threaded IRQ, then registers one OF thermal zone for the internal channel plus `cpu_nr` external CPU channels. Temperature reads take `update_lock`, switch the hardware mux to the requested channel, read and convert the status register sample, then switch back to the configured interrupt-source channel.

Overheat IRQ setup looks for the first registered zone with a critical trip, selects that channel, writes threshold/hysteresis registers, and enables DFX/server/thermal IRQ bits. The hard IRQ disables the line and wakes the thread. The thread notifies the thermal core, polls once per second until the current temperature falls below `current_threshold - current_hysteresis`, clears the DFX cause by reading it, notifies the core again, and re-enables the IRQ.

## State and Persistence
State is volatile driver and hardware state only. `current_channel` mirrors the selected hardware mux, `interrupt_source` is the channel that should remain selected for overheat detection, and `current_threshold/current_hysteresis` mirror programmed register thresholds. The syscon/MMIO registers persist across reads but are reinitialized at probe. There is no disk persistence.

## Dependencies and Integration Points
The driver depends on platform devices, OF matching, syscon/regmap or MMIO-backed regmap, thermal core APIs, optional platform IRQs, and DT thermal-zone definitions. Legacy mode uses `thermal_tripless_zone_device_register()`. Syscon mode uses `devm_thermal_of_zone_register()`. Overheat handling depends on DFX IRQ registers defined per SoC descriptor.

## Risks and Edge Cases
- Legacy resource fix-up subtracts `syscon_status_off` from the mapped base and rejects mappings that would cross a page boundary; incorrect DT resources fail probe.
- Channel switching is global hardware state; every read must hold `update_lock` and reselect the interrupt source or overheat IRQ routing can become inconsistent.
- `armada_configure_overheat_int()` return value is ignored in the loop, so failed threshold setup only results in missing `overheat_sensor` and a warning.
- Hysteresis conversion intentionally rounds toward the smallest supported value, which favors hardware safety but can increase interrupt frequency.
- Signed-sample and inverted-calibration descriptor fields must match the SoC or reported temperatures will be wrong.
- The threaded IRQ can sleep for long periods while temperature remains above the low threshold.

## Test Signals
Useful tests include DT-compatible probe success for each descriptor, regmap offset checks, temperature conversion fixtures for signed/inverted descriptors, concurrent reads from multiple thermal zones verifying channel reselection, critical trip IRQ simulation verifying disable/poll/clear/re-enable behavior, and legacy binding probe tests for page-boundary validation and tripless zone enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/armada_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/Kconfig

## Purpose
Kconfig menu entries for Broadcom thermal drivers under `drivers/thermal/broadcom`. It declares build-time options for Raspberry Pi/BCM283x sensors, Broadcom STB AVS TMON, Northstar, and Stingray thermal blocks.

## Important APIs, Types, and Functions
This file has no C APIs. The important symbols are `BCM2711_THERMAL`, `BCM2835_THERMAL`, `BRCMSTB_THERMAL`, `BCM_NS_THERMAL`, and `BCM_SR_THERMAL`.

## Control Flow
Configuration dependencies decide which objects the Makefile builds. BCM2711 depends on `THERMAL_OF` and `MFD_SYSCON`; BCM2835 depends on `HAS_IOMEM` and `THERMAL_OF`; Broadcom STB and iProc-family drivers can be enabled for compile testing. Northstar and Stingray default on for `ARCH_BCM_IPROC`.

## State and Persistence
No runtime state exists. The selected config symbols persist only in the kernel build configuration.

## Dependencies and Integration Points
The symbols integrate with the local Makefile and broader thermal, OF, syscon, and architecture configuration menus. `COMPILE_TEST` broadens build coverage.

## Risks and Edge Cases
Incorrect dependencies can allow unusable drivers to be built or hide valid build targets. `default y if ARCH_BCM_IPROC` and `default ARCH_BCM_IPROC` have subtly different expressions but both bias iProc platforms toward including those drivers.

## Test Signals
Kconfig lint, allmodconfig/allyesconfig, and architecture-specific build matrices should verify that each selected symbol pulls only valid dependencies and builds the matching object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/Makefile

## Purpose
Build map for Broadcom thermal drivers. It turns Kconfig symbols into the corresponding object files.

## Important APIs, Types, and Functions
No runtime APIs. Object mappings are `bcm2711_thermal.o`, `bcm2835_thermal.o`, `brcmstb_thermal.o`, `ns-thermal.o`, and `sr-thermal.o`.

## Control Flow
Kbuild expands `obj-$(CONFIG_...)` entries during kernel builds. Enabled symbols compile and link their matching object into the module or built-in image.

## State and Persistence
No runtime state. Build outputs persist in the build tree according to Kbuild.

## Dependencies and Integration Points
This file is consumed by the parent thermal Makefile. It must stay synchronized with symbol names in Broadcom Kconfig and source filenames.

## Risks and Edge Cases
A symbol/object typo silently prevents a selected driver from building or causes build failure. File renames require updates here and in Kconfig.

## Test Signals
Build tests with each Broadcom thermal symbol enabled individually and together should produce the expected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/bcm2711_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/bcm2711_thermal.c

## Purpose
Broadcom BCM2711 AVS ring-oscillator thermal sensor driver. It reads a syscon-backed temperature status register, converts the raw code using thermal-zone slope/offset, registers an OF thermal zone, and exposes hwmon sysfs.

## Important APIs, Types, and Functions
- `struct bcm2711_thermal_priv` holds the regmap and thermal zone.
- `bcm2711_get_temp()` reads `AVS_RO_TEMP_STATUS`, checks validity bits, masks the 10-bit data field, and computes `slope * val + offset`.
- `bcm2711_thermal_probe()` gets the parent syscon regmap, registers zone id 0 with `devm_thermal_of_zone_register()`, and calls `thermal_add_hwmon_sysfs()`.
- OF match supports `brcm,bcm2711-thermal`.

## Control Flow
Probe allocates private data, obtains the parent OF node, converts it to a regmap, registers the thermal zone, stores the zone pointer, and adds hwmon files. Every temperature read performs a regmap read and rejects samples where neither validity bit is set.

## State and Persistence
Runtime state is just private regmap and zone pointers. Calibration is not stored locally; slope and offset come from the thermal zone configuration on each read.

## Dependencies and Integration Points
Depends on `MFD_SYSCON`, OF thermal zones, regmap, platform driver core, and `thermal_hwmon`. The hardware register must be in the parent syscon address space.

## Risks and Edge Cases
- The validity check tests the combined validity mask with `if (!(val & mask))`; this accepts either bit rather than requiring both bits.
- Missing or incorrect parent syscon node fails probe.
- Bad DT slope/offset values directly skew temperature reporting.

## Test Signals
Mock regmap tests should cover valid/invalid status bits, raw-code conversion, syscon lookup failure, thermal zone registration failure, and hwmon registration return handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/bcm2711_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/bcm2835_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/bcm2835_thermal.c

## Purpose
Broadcom BCM2835/2836/2837 temperature sensor driver. It maps TSENS registers, enables a clock, registers an OF thermal zone, optionally initializes hardware when firmware has not done so, exposes hwmon, and provides debugfs register access.

## Important APIs, Types, and Functions
- `struct bcm2835_thermal_data` holds zone, MMIO base, clock, and debugfs directory.
- `bcm2835_thermal_adc2temp()` and `bcm2835_thermal_temp2adc()` convert between ADC code and millicelsius using thermal-zone slope/offset.
- `bcm2835_thermal_get_temp()` reads `TSENSSTAT`, requires `VALID`, masks the 10-bit data field, and converts it.
- `bcm2835_thermal_debugfs()` creates a `bcm2835_thermal/regset` debugfs view.
- `bcm2835_thermal_probe()` maps registers, enables the clock, warns on clock-rate deviations, registers the OF zone, initializes `TSENSCTL` if reset is still asserted, adds hwmon and debugfs.
- `bcm2835_thermal_remove()` removes debugfs recursively.

## Control Flow
Probe verifies OF match, maps resource 0, enables the unnamed clock, registers zone id 0, then checks `TSENSCTL_RSTB`. If the firmware did not enable the block, it reads critical trip temperature, configures bandgap, regulator, reset delay, and threshold ADC, writes control once without and once with reset deasserted. Temperature reads are direct MMIO reads with validity checks.

## State and Persistence
The driver stores mapped register and clock handles, the thermal zone pointer, and debugfs directory. Hardware control register state persists in the sensor until reconfigured or reset.

## Dependencies and Integration Points
Depends on OF address/platform resources, common clock framework, thermal OF bindings for slope/offset and critical trip, debugfs, and `thermal_hwmon`.

## Risks and Edge Cases
- If no critical trip exists and firmware left the block disabled, probe fails because threshold programming requires a critical trip.
- Clock outside 1.92-5 MHz only warns, so marginal hardware timing can persist.
- Debugfs allocation failure is tolerated, but debugfs directory can still exist without a regset.
- Slope/offset are trusted from DT.

## Test Signals
Probe tests should cover firmware-initialized and driver-initialized paths, clock-rate warning path, missing critical trip, invalid `TSENSSTAT`, ADC clamp behavior in `temp2adc()`, and debugfs cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/bcm2835_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/brcmstb_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/brcmstb_thermal.c

## Purpose
Broadcom STB AVS TMON thermal sensor driver. It exposes an OF thermal zone for AVS TMON blocks, supports process-node-specific conversion parameters, and on older 28nm TMON variants supports hardware low/high trip interrupts via `set_trips`.

## Important APIs, Types, and Functions
- `struct avs_tmon_trip` describes enable and threshold fields for low, high, and reset trips.
- `struct brcmstb_thermal_params` carries conversion offset/multiplier and the thermal-zone ops for a compatible.
- `struct brcmstb_thermal_priv` stores MMIO base, device, zone, and conversion params.
- `avs_tmon_code_to_temp()` and `avs_tmon_temp_to_code()` convert between 10-bit hardware codes and millicelsius.
- `brcmstb_get_temp()` reads `AVS_TMON_STATUS`, checks validity, extracts the code, converts, and floors at zero.
- `brcmstb_set_trips()` programs low/high interrupt thresholds and enables/disables interrupt sources.
- `brcmstb_tmon_irq_thread()` reads interrupt temperature, disables the triggered side until the framework moves trip windows, and calls `thermal_zone_device_update()`.
- Match data selects 8nm, 16nm, or 28nm parameter sets.

## Control Flow
Probe loads match data, maps resource 0, registers zone id 0 with the compatible's ops, and optionally requests a threaded IRQ. Temperature polling is a simple status read. For compatibles with `set_trips`, the thermal core calls `brcmstb_set_trips()` to program low and high windows; IRQ thread disables whichever threshold fired and reports an update using the interrupt temperature.

## State and Persistence
Driver state is the MMIO base and thermal zone. Threshold and enable state lives in TMON registers. Conversion parameters are immutable match data.

## Dependencies and Integration Points
Integrates with OF thermal zones, platform IRQs, MMIO resources, and thermal core `set_trips`. The IRQ is optional, so polling-only operation is possible.

## Risks and Edge Cases
- Conversion clamps only negative reported temperature to zero in `get_temp`; threshold conversion still accepts very low values and maps them to max code.
- The 8nm/16nm params omit `set_trips`, so platform DT/thermal policy must not assume hardware window interrupts there.
- IRQ thread depends on the thermal core reprogramming trips after an update; otherwise the relevant interrupt side remains disabled.
- Raw MMIO access uses `__raw_readl/writel`, so ordering expectations are hardware-specific.

## Test Signals
Unit conversion tests should cover min/max/rounding for low vs high trips. Integration tests should verify optional IRQ request, `set_trips(INT_MAX/-INT_MAX)` disable behavior, invalid status handling, and per-compatible ops selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/brcmstb_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/ns-thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/ns-thermal.c

## Purpose
Broadcom Northstar thermal driver. It maps a PVT monitor block, ensures temperature-monitor mode is selected, reads raw status, and converts it with thermal-zone slope/offset.

## Important APIs, Types, and Functions
- `ns_thermal_get_temp()` switches `PVTMON_CONTROL0` to `SEL_TEMP_MONITOR` if needed, reads `PVTMON_STATUS`, and returns `slope * val + offset`.
- `ns_thermal_probe()` maps resource 0 with `of_iomap()`, registers OF thermal zone id 0, and stores the mapping in platform data.
- `ns_thermal_remove()` unmaps the manually mapped I/O region.

## Control Flow
Probe maps the OF node's first resource and registers an OF thermal zone. Reads correct the monitor mode if firmware/test code left it in another mode, then report the converted status value. Remove unmaps the resource.

## State and Persistence
State is the MMIO pointer stored as both zone private data and platform driver data. The monitor mode bit persists in hardware and may be rewritten on reads.

## Dependencies and Integration Points
Uses OF address mapping, platform driver core, and thermal OF slope/offset. It is not devm-managed for mapping, so remove must unmap explicitly.

## Risks and Edge Cases
- `WARN_ON(!pvtmon)` emits a warning and fails probe if mapping is absent.
- No hardware validity bit is checked; all status reads are trusted.
- Mode selection is performed during `get_temp()`, so reads can mutate hardware state.

## Test Signals
Tests should cover failed mapping, thermal zone registration failure cleanup, mode-correction write path, and conversion using DT-provided slope/offset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/ns-thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/sr-thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/sr-thermal.c

## Purpose
Broadcom Stingray thermal driver. It registers one thermal zone per enabled TMON bit in the `brcm,tmon-mask` device property and reports memory-mapped temperature register values directly.

## Important APIs, Types, and Functions
- `struct sr_thermal` stores the remapped register window and fixed array of up to six TMON descriptors.
- `struct sr_tmon` binds a TMON id to its parent private state.
- `sr_get_temp()` reads `regs + id * 4` and returns the value as millicelsius.
- `sr_thermal_probe()` memremaps the resource, reads `brcm,tmon-mask`, flushes each enabled temperature register to zero, and registers OF zones by hardware id.

## Control Flow
Probe allocates the parent structure, gets the memory resource, maps it with `devm_memremap(..., MEMREMAP_WB)`, reads the enabled-sensor mask, then iterates ids 0 through 5. For each set bit it clears the register, initializes the `sr_tmon`, and registers a thermal OF zone using the same id.

## State and Persistence
Runtime state is devm-managed memory and the fixed sensor array. Hardware temperature registers are cleared once during probe.

## Dependencies and Integration Points
Depends on platform resources, generic device properties, OF thermal zones, and the Stingray hardware temperature register layout.

## Risks and Edge Cases
- `devm_memremap()` with write-back semantics is unusual for device registers; ordering/cacheability assumptions should match the hardware block.
- The driver ignores mask bits above `SR_TMON_MAX_LIST`.
- No validity or unit conversion is performed; firmware/hardware must expose values in thermal-framework units.
- `crit_temp` and `max_crit_temp` fields are unused.

## Test Signals
Probe tests should check missing resource, missing mask property, multiple mask bits, per-id zone registration, register flush writes, and readback from each enabled offset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/broadcom/sr-thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/cpufreq_cooling.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/cpufreq_cooling.c

## Purpose
Generic thermal cooling-device implementation for cpufreq policies. It maps cooling states to maximum CPU frequencies, applies the limit through freq QoS, and when the Energy Model is available exposes power-actor callbacks used by the power allocator governor.

## Important APIs, Types, and Functions
- `struct cpufreq_cooling_device` stores current cooling state, max state, EM reference, cpufreq policy, ops, optional idle-time accounting, and `freq_qos_request`.
- Registration exports: `cpufreq_cooling_register()`, `of_cpufreq_cooling_register()`, and `cpufreq_cooling_unregister()`.
- Core callbacks: `cpufreq_get_max_state()`, `cpufreq_get_cur_state()`, and `cpufreq_set_cur_state()`.
- `get_state_freq()` maps thermal state to frequency using EM states when present or the cpufreq table sorted direction otherwise.
- Power allocator callbacks under `CONFIG_THERMAL_GOV_POWER_ALLOCATOR`: `cpufreq_get_requested_power()`, `cpufreq_state2power()`, and `cpufreq_power2state()`.
- Helper functions map frequency/state/power: `get_level()`, `cpu_freq_to_power()`, `cpu_power_to_freq()`, `get_dynamic_power()`, and `em_is_sane()`.

## Control Flow
Registration validates the cpufreq policy, CPU device, and frequency table, allocates private state, calculates `max_level`, installs thermal cooling ops, validates optional EM alignment, and adds a `FREQ_QOS_MAX` request initialized to the frequency for state 0. It then registers a named thermal cooling device, optionally bound to the CPU OF node. Setting a cooling state validates bounds, computes the target frequency, updates the freq QoS max request, and records the new state.

When IPA is enabled and EM is sane, power callbacks estimate current requested power from current frequency and CPU load, convert cooling states to 100-percent-load power, and convert power budgets back to cooling states. SMP uses scheduler utilization; non-SMP tracks idle-time deltas.

## State and Persistence
State is in-memory and tied to the cooling device lifecycle. The effective throttle persists in the cpufreq policy's freq QoS constraints until updated or unregistered. `last_load` is a rolling input for power-to-state conversion.

## Dependencies and Integration Points
Integrates with cpufreq policy/table APIs, freq QoS, thermal cooling devices, OF CPU nodes with `#cooling-cells`, Energy Model/OPP data, scheduler CPU utilization or idle-time accounting, and thermal tracepoints.

## Risks and Edge Cases
- Unsorted cpufreq tables are rejected unless a valid EM is used.
- EM must span exactly `policy->related_cpus` and have the same number of states as cpufreq levels; mismatches disable power callbacks or fail in non-EM sorted-table cases.
- `cpufreq_get_requested_power()` approximates requested power from recent current frequency and load, not hypothetical unconstrained demand.
- `last_load` is normalized to at least one in `power2state()`, so stale/zero load can bias budgets.
- State-to-frequency mapping assumes stable policy frequency table or EM state count after registration.

## Test Signals
Tests should verify state/frequency mapping for ascending and descending tables, rejection of unsorted tables, freq QoS add/update/remove behavior, OF registration only when `#cooling-cells` exists, EM mismatch diagnostics, power callback conversions, offline CPU load handling, and unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/cpufreq_cooling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/cpuidle_cooling.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/cpuidle_cooling.c

## Purpose
Generic thermal cooling-device implementation using cpuidle idle injection. It registers cooling devices from CPU DT `thermal-idle` child nodes and maps thermal state 0..100 to an injected idle ratio.

## Important APIs, Types, and Functions
- `struct cpuidle_cooling_device` stores the idle-inject device and current thermal state.
- `cpuidle_cooling_runtime()` computes run duration from fixed idle duration and requested idle percentage.
- Thermal callbacks `cpuidle_cooling_get_max_state()`, `cpuidle_cooling_get_cur_state()`, and `cpuidle_cooling_set_cur_state()` expose state and update idle injection.
- `__cpuidle_cooling_register()` creates the idle injection device, reads optional `duration-us` and `exit-latency-us`, registers the thermal cooling device, and names it from the first CPU device.
- `cpuidle_cooling_register()` scans each CPU in a cpuidle driver's mask for a `thermal-idle` child node.

## Control Flow
For each CPU in the cpuidle driver's mask, the public registration helper obtains the CPU OF node and its `thermal-idle` child. If present, it registers an idle-injection-backed cooling device for the driver's cpumask. Setting state records the new percentage, reads the idle duration, calculates runtime, updates idle-injection timing, starts injection when transitioning from 0 to nonzero, and stops it when transitioning back to 0.

## State and Persistence
The current cooling state and idle-inject handle are in memory. The injected idle timing lives in the idle-inject subsystem until changed or unregistered after registration failure. There is no explicit unregister API in this file.

## Dependencies and Integration Points
Depends on cpuidle drivers, idle injection, thermal cooling devices, OF CPU nodes, and optional `duration-us`/`exit-latency-us` properties.

## Risks and Edge Cases
- `state` is treated as a percent but `set_cur_state()` does not clamp to max; it relies on thermal core callers.
- `cpuidle_cooling_register()` can encounter multiple CPUs with the same driver cpumask and register more than intended if multiple CPUs expose `thermal-idle` nodes.
- `get_cpu_device(cpumask_first())` is assumed valid before `dev_name()`.
- Registration has no public cleanup path for successful devices in this file.

## Test Signals
Tests should cover runtime formula for 0, 50, and 100 percent, DT property defaults and overrides, idle injection start/stop transitions, failure cleanup paths, and multi-CPU cpumask registration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/cpuidle_cooling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/da9062-thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/da9062-thermal.c

## Purpose
Dialog DA9062/DA9061 PMIC thermal TJUNC driver. It reports a synthetic thermal zone based on the PMIC over-temperature event bit, disables the IRQ during an event, polls until the event clears, and raises thermal updates for a HOT trip at 125C.

## Important APIs, Types, and Functions
- `struct da9062_thermal` stores parent PMIC pointer, delayed work, thermal zone, lock-protected temperature, IRQ, config, and device.
- `da9062_thermal_poll_on()` clears/reads `DA9062AA_EVENT_B`, sets temperature to 125C while `E_TEMP` is asserted or 0C when cleared, updates the thermal zone, requeues or re-enables IRQ.
- `da9062_thermal_irq_handler()` disables the IRQ and queues the work immediately.
- `da9062_thermal_get_temp()` returns the cached temperature under mutex.
- Probe registers a thermal zone with a single HOT trip and requests the named `THERMAL` IRQ.

## Control Flow
Probe reads optional `polling-delay-passive`, clamps it to 1-10 seconds, allocates state, initializes work and mutex, registers/enables the thermal zone, retrieves the PMIC IRQ by name, and requests a threaded IRQ. On IRQ, the handler disables the line and queues work. The work clears and rereads the status bit: if still hot it caches 125C, notifies the core, and requeues after the polling period; otherwise it caches 0C, notifies, and re-enables IRQ.

## State and Persistence
The only temperature state is a cached binary value, protected by `lock`. `pp_tmp` is a module-global polling period that can be changed from DT at probe. Hardware event state persists in PMIC registers.

## Dependencies and Integration Points
Depends on the DA9062 MFD parent, regmap, named platform IRQ, thermal core, delayed work on `system_freezable_wq`, and a fixed HOT trip.

## Risks and Edge Cases
- Temperature is binary, not an actual sensor reading; consumers must interpret it as event state.
- `pp_tmp` is global, so multiple instances would share the last parsed polling period.
- The IRQ is requested with non-devm `request_threaded_irq()`, so remove must free it.
- Work re-enables IRQ only after the event clears or error paths; repeated regmap failures may re-enable without updated cached temperature.

## Test Signals
Tests should simulate IRQ, persistent hot status requeue, clear status re-enable, DT polling bounds, thermal zone enable failure cleanup, IRQ request failure, and remove cancel/free/unregister ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/da9062-thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/db8500_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/db8500_thermal.c

## Purpose
ST-Ericsson DB8500 thermal driver using PRCMU hotmon interrupts. Because no direct PRCMU temperature read API exists, it reports an interpolated pseudo-temperature between programmed low/high thresholds.

## Important APIs, Types, and Functions
- `db8500_thermal_points[]` defines stepped threshold bands from 15C to 100C.
- `struct db8500_thermal_zone` stores the zone, device, current interpolated temperature, and current threshold index.
- `db8500_thermal_update_config()` stops sensing, updates index/interpolated value, programs PRCMU low/high celsius thresholds, and restarts sensing.
- `prcmu_low_irq_handler()` and `prcmu_high_irq_handler()` move the threshold window down or up and update the thermal zone.
- Suspend/resume stop and restart sensing.

## Control Flow
Probe allocates state, requests low and high threaded IRQs by name, registers thermal OF zone id 0, and starts sensing at the lowest threshold band. Low IRQ lowers the band unless already at index 0. High IRQ raises the band until the highest point, then reports one degree above max. Each threshold movement reprograms PRCMU hotmon and notifies the thermal core.

## State and Persistence
`cur_index` and `interpolated_temp` represent the current PRCMU threshold band. PRCMU hotmon register state is external to this driver and is reset on probe/resume.

## Dependencies and Integration Points
Depends on PRCMU functions (`prcmu_config_hotmon()`, start/stop), named platform IRQs, OF thermal zone registration, and system suspend/resume callbacks.

## Risks and Edge Cases
- Temperature is approximate midpoint of threshold bands, not direct sensor data.
- IRQ handlers are threaded but do not use explicit locking around `cur_index`; PRCMU IRQ serialization is assumed.
- The highest band reports only max+1 mC, not actual high temperature.
- Critical behavior relies on DT thermal-zone trips being consistent with the fixed threshold table.

## Test Signals
Tests should drive low/high IRQs across band boundaries, verify PRCMU programming values in Celsius, suspend/resume reset behavior, OF registration failure, and no-op low IRQ at index 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/db8500_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/devfreq_cooling.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/devfreq_cooling.c

## Purpose
Generic thermal cooling-device implementation for devfreq-managed devices. It caps device frequency through dev PM QoS, maps cooling states to OPP/EM frequencies, and optionally exposes power-actor callbacks for the IPA power allocator governor.

## Important APIs, Types, and Functions
- `struct devfreq_cooling_device` stores the thermal cdev, ops, devfreq pointer, current state, fallback frequency table, max state, optional power ops, utilization scaling, capped state, QoS request, and Energy Model domain.
- Core callbacks: `devfreq_cooling_get_max_state()`, `devfreq_cooling_get_cur_state()`, and `devfreq_cooling_set_cur_state()`.
- Power callbacks: `devfreq_cooling_get_requested_power()`, `devfreq_cooling_state2power()`, and `devfreq_cooling_power2state()`.
- Helpers: `get_perf_idx()`, `get_voltage()`, `_normalize_load()`, and `devfreq_cooling_gen_tables()`.
- Exported registration APIs: `of_devfreq_cooling_register_power()`, `of_devfreq_cooling_register()`, `devfreq_cooling_register()`, `devfreq_cooling_em_register()`, and `devfreq_cooling_unregister()`.

## Control Flow
Registration allocates state, installs base callbacks, obtains a non-artificial Energy Model if present, and enables IPA power callbacks when available. Without EM it builds a descending frequency table from OPPs for backward compatibility. It adds a `DEV_PM_QOS_MAX_FREQUENCY` request, registers a named thermal cooling device, and returns it. Setting state maps the state to an EM performance index or fallback frequency and updates the PM QoS max frequency.

Power accounting reads `df->last_status` under the devfreq lock. With `get_real_power`, it looks up voltage and lets the device model compute real power, then adjusts `res_util`. Without real power, it normalizes busy time and scales EM power by utilization. Power-to-state scales the requested budget back to estimated full-use power and chooses the first EM state within budget.

## State and Persistence
The current cooling state, capped state, resource-utilization correction, fallback frequency table, and PM QoS request are in memory. The effective cap persists in the device PM QoS framework until changed or unregistered.

## Dependencies and Integration Points
Integrates with devfreq, OPP, Energy Model, dev PM QoS, thermal OF cooling-device registration, optional `devfreq_cooling_power` callbacks, and thermal tracepoints.

## Risks and Edge Cases
- OPP additions/removals after registration are explicitly not handled.
- `get_perf_idx()` requires exact EM frequency match to `current_frequency / 1000`; mismatch returns `-EAGAIN`.
- Fallback frequency table is only for non-IPA cooling and must be freed on failure/unregister.
- Real-power path depends on valid voltage lookup and device-specific power model.
- `devfreq_cooling_unregister()` unregisters EM perf domain even if this file did not create it, relying on EM API behavior.

## Test Signals
Tests should cover EM and non-EM registration paths, OPP table generation order, PM QoS update values, power callback calculations with normalized load, real-power error paths, unregister cleanup, and `devfreq_cooling_em_register()` behavior when EM registration fails but cooling registration succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/devfreq_cooling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/dove_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/dove_thermal.c

## Purpose
Marvell Dove thermal sensor driver. It initializes the thermal diode registers, registers a tripless thermal zone, and reports temperature from status/control MMIO resources.

## Important APIs, Types, and Functions
- `struct dove_thermal_priv` stores sensor and control MMIO bases.
- `dove_init_sensor()` programs averaging, reference calibration, calibration voltage, resets and enables the sensor, then polls for the first nonzero reading.
- `dove_get_temp()` checks the valid bit in control register 1, extracts the 9-bit sensor sample, and computes temperature with the documented formula.
- Probe maps two resources, initializes hardware, registers/enables a tripless zone, and stores it in drvdata.

## Control Flow
Probe allocates private data, maps sensor and control resources, initializes the sensor, registers `dove_thermal`, enables the thermal zone, and stores the zone pointer. Reads first validate the diode-control status bit, then convert the sample from the sensor register.

## State and Persistence
Driver state is MMIO mappings and the thermal zone pointer. Calibration and enable bits persist in hardware after `dove_init_sensor()`.

## Dependencies and Integration Points
Depends on platform MMIO resources, OF compatible `marvell,dove-thermal`, and the thermal core tripless zone API.

## Risks and Edge Cases
- Initialization polls up to one million tight iterations without sleep.
- A zero sensor value is treated as not ready during init, which could be ambiguous depending on hardware.
- Conversion uses large integer constants; unit mistakes would have large reporting impact.
- No runtime PM or remove-time hardware disable is implemented.

## Test Signals
Tests should cover successful initialization writes, timeout path, invalid status bit returning `-EIO`, conversion fixture values, thermal zone enable failure cleanup, and resource mapping failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/dove_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/gov_bang_bang.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/gov_bang_bang.c

## Purpose
Thermal governor implementing two-point hysteresis control, primarily for binary cooling devices such as fans. It turns cooling on when a trip is crossed upward and off when crossed downward below the hysteresis threshold.

## Important APIs, Types, and Functions
- `bang_bang_set_instance_target()` sets instance target to 0/1, marks it initialized, and updates the cdev without extra checks.
- `bang_bang_trip_crossed()` applies upward/downward target to all instances bound to the crossed trip.
- `bang_bang_manage()` initializes uninitialized instances according to current zone temperature and trip thresholds.
- `bang_bang_update_tz()` clears `governor_data` after cdev binding and resume so initialization is repeated.
- Declares `thermal_gov_bang_bang`.

## Control Flow
The governor reacts to trip-crossing notifications under the thermal-zone lock and directly updates all cooling instances on that trip. On manage, it runs only once per binding/resume epoch and initializes uninitialized non-hot/non-critical trip instances based on whether the current temperature is above the trip descriptor threshold.

## State and Persistence
It uses each thermal instance's `target` and `initialized` state. `tz->governor_data` is used as a boolean "initialization done" flag, reset on bind/resume.

## Dependencies and Integration Points
Depends on thermal core internals (`thermal_core.h`), trip descriptors, thermal instances, and `thermal_cdev_update_nocheck()`.

## Risks and Edge Cases
- Designed for binary cooling; it only expects targets 0 and 1 and logs unexpected existing states.
- Skips HOT and CRITICAL trips, so it must be paired with other critical safety handling.
- Correct hysteresis behavior depends on trip-crossing events and descriptor thresholds from the thermal core.

## Test Signals
Tests should cover upward/downward crossings, initial manage with current temperature above/below threshold, reset after bind/resume, ignored hot/critical trips, and cdev update calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/gov_bang_bang.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/gov_fair_share.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/gov_fair_share.c

## Purpose
Thermal governor that distributes throttling across cooling devices according to trip level and instance weights.

## Important APIs, Types, and Functions
- `get_trip_level()` counts how many trip thresholds are at or below the current temperature and traces the highest crossed trip.
- `fair_share_throttle()` computes each instance target as a fraction of cdev max state using trip level, total trips, and weight share.
- `fair_share_manage()` applies throttling for every non-hot/non-critical valid trip.
- Declares `thermal_gov_fair_share`.

## Control Flow
During manage under the zone lock, the governor computes a global trip level, then for each eligible trip sums instance weights and counts instances. It sets each instance target proportionally. If no weights are configured, it divides evenly by instance count.

## State and Persistence
State is stored in thermal instance `target` fields and cdev state after updates. The governor has no private persistent data.

## Dependencies and Integration Points
Uses thermal core trip descriptors, instance lists, cdev max state, thermal tracepoints, and `thermal_cdev_update_nocheck()`.

## Risks and Edge Cases
- If a trip has zero instances, no updates occur; if total weight is zero, divisor uses instance count.
- The formula uses `tz->num_trips`, so hot/critical trips still affect denominator even though skipped for updates.
- Integer division truncates target states.

## Test Signals
Tests should verify weighted and unweighted distribution, trip-level calculation, no-trip-crossed level zero, hot/critical filtering, and trace/update calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/gov_fair_share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/gov_power_allocator.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/gov_power_allocator.c

## Purpose
Intelligent Power Allocation thermal governor. It uses a fixed-point PID controller to compute a power budget for a thermal zone and divides that budget across cooling devices that implement the power-actor API.

## Important APIs, Types, and Functions
- `struct power_actor` stores requested, maximum, granted, extra, and weighted requested power per actor.
- `struct power_allocator_params` stores PID state, sustainable power, selected trips, actor counts/weights, and actor buffer.
- Fixed-point helpers `mul_frac()` and `div_frac()` implement FRAC_BITS arithmetic.
- `estimate_sustainable_power()`, `estimate_pid_constants()`, and `get_sustainable_power()` initialize or refresh thermal-zone power parameters.
- `pid_controller()` computes the next total power range from current temperature, control temperature, PID terms, and sustainable power.
- `divvy_up_power()` splits budget by weighted requested power and redistributes capped surplus.
- `allocate_power()` collects actor power requests, runs PID, assigns grants, and traces results.
- `get_governor_trips()` selects switch-on and control trips.
- `allow_maximum_power()` resets targets below switch-on and refreshes actor stats.
- `check_power_actors()`, `allocate_actors_buffer()`, `power_allocator_update_weight()`, and `power_allocator_update_tz()` manage actor eligibility and buffers.
- Governor hooks: bind, unbind, manage, and update.

## Control Flow
Bind allocates params, selects first/last passive or last active trip, verifies that all cooling devices on the control trip are power actors, allocates an actor buffer, creates `tzp` if missing, estimates PID constants if possible, resets PID state, and stores params in `tz->governor_data`. Manage checks the switch-on trip: below it, PID state resets and actors are allowed maximum power; above it, actor requested/max powers are collected, a PID budget is computed against `trip_max->temperature`, budget is split by weighted demand, and each actor's `power2state()` result becomes its target. Update handles cdev bind/unbind and weight changes by resizing buffers and recomputing total weight.

## State and Persistence
PID integral and previous error persist in `governor_data` while bound. `tz->tzp` may be allocated and modified, including `sustainable_power` and PID constants exposed through thermal-zone parameters. Actor buffer contents are per-manage temporary data.

## Dependencies and Integration Points
Requires cooling devices with `get_requested_power`, `state2power`, and `power2state`. It depends on thermal core trip descriptors, instance weights, thermal tracepoints, zone passive delay, and optional sysfs-updatable thermal zone parameters.

## Risks and Edge Cases
- Binding fails if any cdev on the control trip lacks power-actor callbacks.
- Sustainable power may be estimated from cooling devices' minimum powers; this is functional but may be suboptimal.
- PID constants are estimated only when threshold delta is nonzero; bad trip configuration can leave weak defaults.
- `power_allocator_update_tz()` assumes `params->trip_max` has a descriptor when bind/unbind events arrive.
- Integer fixed-point and budget clamping can truncate small effects.
- Actor count can change after binding; buffer resize failures leave actor state reset.

## Test Signals
Tests should cover trip selection for one/two/no passive trips, bind failure for non-power actors, PID output clamping, integral cutoff behavior, budget division and surplus redistribution, weight updates, switch-on below-threshold maximum-power path, and cleanup of allocated `tzp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/gov_power_allocator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/gov_step_wise.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/gov_step_wise.c

## Purpose
Default step-wise thermal governor. It adjusts cooling-device targets incrementally based on whether the zone is above a trip threshold and the current thermal trend.

## Important APIs, Types, and Functions
- `get_target_state()` computes the next target from current cdev state, instance lower/upper limits, initialization state, trend, and throttle boolean.
- `thermal_zone_trip_update()` applies `get_target_state()` to every instance on a trip descriptor and marks cdevs for update.
- `step_wise_manage()` processes every eligible trip and then updates all cdevs.
- Declares `thermal_gov_step_wise`.

## Control Flow
Manage runs under the thermal-zone lock. For each non-hot/non-critical valid trip, it computes whether the zone should throttle and asks thermal core for the trend. Targets increase by one when heating above threshold, decrease carefully when cooling, and deactivate when below threshold and already at lower limit. After target assignment, it walks all instances and updates cooling devices.

## State and Persistence
Thermal instance `target` and `initialized` fields retain state between manage calls. Cdev `updated` is cleared under the cdev guard when a new target requires update.

## Dependencies and Integration Points
Uses thermal core internals, min/max helpers, trends from `get_tz_trend()`, cdev ops, scoped cooling-device guards, and thermal tracepoints.

## Risks and Edge Cases
- Behavior depends heavily on trend classification; noisy sensors can cause oscillating state steps.
- Initial unthrottled instances return `THERMAL_NO_TARGET`.
- HOT and CRITICAL trips are ignored for governor throttling.
- The code calls cdev `get_cur_state()` without checking return value.

## Test Signals
Tests should cover uninitialized and initialized paths, raising/dropping trends above and below thresholds, clamp to lower/upper, `THERMAL_NO_TARGET` deactivation, and two-phase update of all cdevs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/gov_step_wise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/gov_user_space.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/gov_user_space.c

## Purpose
Thermal governor that notifies userspace about trip crossings via uevents rather than applying cooling policy itself.

## Important APIs, Types, and Functions
- `user_space_bind()` emits a one-time info message recommending thermal netlink.
- `user_space_trip_crossed()` creates `NAME`, `TEMP`, `TRIP`, and `EVENT` environment variables and sends `KOBJ_CHANGE`.
- Declares `thermal_gov_user_space`.

## Control Flow
On bind, the governor logs once. On every trip crossing under the zone lock, it allocates four strings, sends a kobject uevent on the thermal-zone device, and frees the strings.

## State and Persistence
No governor-private state. It uses current thermal-zone fields at event time.

## Dependencies and Integration Points
Integrates with thermal core trip-crossing notifications, kobject uevents, sysfs device model, and userspace listeners.

## Risks and Edge Cases
- `kasprintf()` failures are not checked before passing the environment array to `kobject_uevent_env()`.
- It does not throttle; system safety depends on firmware, critical trips, or userspace policy responsiveness.
- Uevents can be lossy under userspace pressure.

## Test Signals
Tests should verify uevent environment contents, trip id mapping, upward/downward crossing delivery, bind log behavior, and allocation-failure robustness if fault injection is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/gov_user_space.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/hisi_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/hisi_thermal.c

## Purpose
HiSilicon thermal sensor driver for HI6220 and HI3660-style tsensors. It abstracts SoC-specific register layouts and temperature conversion through ops, registers OF thermal zones, programs passive-threshold alarms, and handles alarm IRQs.

## Important APIs, Types, and Functions
- `struct hisi_thermal_sensor` stores parent data, thermal zone, IRQ name, sensor id, and passive threshold.
- `struct hisi_thermal_ops` defines get/enable/disable/irq/probe hooks per SoC.
- `struct hisi_thermal_data` stores ops, sensor array, platform device, clock, base registers, and sensor count.
- Conversion helpers implement HI6220 and HI3660 step-to-temperature and temperature-to-step formulas.
- HI6220/HI3660 helpers program lag, threshold, interrupt enable/clear, reset, and sensor selection fields.
- `hisi_thermal_register_sensor()` registers OF zone and records first passive trip as `thres_temp`.
- `hisi_thermal_alarm_irq_thread()` clears hardware interrupt, reads temperature, logs alarm/stop, and updates zone when still above threshold.
- Probe maps registers, runs SoC probe, registers each sensor, requests IRQs, enables hardware, and enables thermal zones.

## Control Flow
OF match chooses HI6220 or HI3660 ops. The SoC probe allocates one sensor and sets its hardware id/IRQ name. Generic probe maps MMIO, registers each sensor as a thermal zone, scans trips for the passive threshold, requests the platform IRQ, enables the sensor using SoC register programming, and enables the zone. The IRQ thread clears the alarm, reads current temperature, and updates the thermal zone if temperature is still above the configured passive threshold.

## State and Persistence
State includes the chosen ops, sensor id, threshold temperature from DT thermal trips, and clock state for HI6220. Hardware lag/threshold/interrupt registers persist until disabled or reprogrammed. Suspend disables sensors; resume re-enables them.

## Dependencies and Integration Points
Depends on OF thermal zones, platform IRQ, MMIO, common clock for HI6220, and thermal PM callbacks. It uses passive trip definitions from DT as hardware alarm thresholds.

## Risks and Edge Cases
- Probe retrieves `platform_get_irq(pdev, 0)` inside the sensor loop, so multi-sensor expansion would need per-sensor IRQ handling.
- `hisi_trip_walk_cb()` leaves `thres_temp` zero if no passive trip exists, causing threshold programming at 0 mC.
- `hisi_thermal_resume()` ORs return values, which may obscure the first specific failure.
- Only one sensor is currently configured per supported SoC despite constants for more sensors.

## Test Signals
Tests should cover HI6220 and HI3660 conversion formulas, passive trip discovery, missing passive trip behavior, IRQ clear/update path above and below threshold, suspend/resume register operations, and clock enable/disable failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/hisi_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/imx8mm_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/imx8mm_thermal.c

## Purpose
NXP i.MX8MM/i.MX8MP TMU driver. It registers one or two thermal zones, loads OCOTP calibration from nvmem when available, programs TMU calibration registers, enables probes, and reports temperature readings.

## Important APIs, Types, and Functions
- `struct thermal_soc_data` provides sensor count, TMU version, and get-temp callback.
- `struct tmu_sensor` binds a hardware id and zone to the parent TMU.
- `struct imx8mm_tmu` stores MMIO base, clock, SoC data, and flexible sensor array.
- `imx8mm_tmu_get_temp()` reads V1 `TRITSR` temperature0, ignores invalid V bit due to erratum, and checks range.
- `imx8mp_tmu_get_temp()` checks per-probe ready bits, reads signed V2 fields for sensor0/1, and checks range.
- `imx8mm_tmu_probe_set_calib_v1()` and `_v2()` parse nvmem calibration data and program TASR/TCALIV/TRIM registers.
- `imx8mm_tmu_probe()` maps resources, enables clock, disables monitor, registers zones, loads calibration, enables V2 probes, and enables monitor.

## Control Flow
Probe loads match data, allocates a parent struct sized for `num_sensors`, maps registers, enables the clock, disables the TMU, registers each sensor as an OF thermal zone and hwmon, then applies calibration. V1 expects a 32-bit `calib` cell. V2 reads a 16-byte cell and either applies trim fields or default 25C binary codes for blank sample hardware. V2 selects all probes before enabling the monitor. Remove disables the TMU and clock.

## State and Persistence
Driver state is MMIO base, clock, SoC descriptor, and sensor array. Calibration register values persist in hardware while powered. Thermal zone private data points to each `tmu_sensor`.

## Dependencies and Integration Points
Depends on platform MMIO, clocks, OF matching, nvmem cells, thermal OF zones, and `thermal_hwmon`. DTs without `nvmem-cells` are allowed for compatibility but produce less accurate readings.

## Risks and Edge Cases
- V1 ignores validity bit intentionally due to erratum; range checks are the only stale/invalid-sample guard.
- V2 negative handling computes magnitude for signed values but does not negate it, which should be scrutinized against hardware encoding.
- Missing calibration is nonfatal, risking inaccurate readings on old DTs.
- V2 calibration requires exactly 16 bytes; any other length fails probe.

## Test Signals
Tests should cover V1/V2 get-temp paths, ready-bit `-EAGAIN`, range rejection, no-nvmem compatibility warning, blank V2 calibration defaults, exact-length V2 calibration parsing, multi-zone registration, and clock cleanup on failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/imx8mm_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/imx91_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/imx91_thermal.c

## Purpose
NXP i.MX91 TMU driver. It initializes trim, clock divider, power-up delay, resolution, periodic measurement mode, runtime PM, a thermal zone with hardware trip programming, and a threaded threshold IRQ.

## Important APIs, Types, and Functions
- `struct imx91_tmu` stores MMIO base, clock, device, and thermal zone.
- `imx91_tmu_start()` and `imx91_tmu_enable()` control measurement start/stop and module enable through set/clear aliases.
- `imx91_tmu_to_mcelsius()` and `_from_mcelsius()` convert fixed-point 1/64C register units.
- `imx91_tmu_get_temp()` reads signed 16-bit `DATA0`.
- `imx91_tmu_set_trips()` programs comparator threshold 1 for the high trip and enables its interrupt.
- `imx91_init_from_nvmem_cells()` reads `trim1` and `trim2`; probe falls back to defaults if absent/invalid.
- IRQ top half checks `THR1_IF`, clears/disables it, and wakes the thread; thread updates the thermal zone.
- Runtime PM callbacks disable/enable the TMU and clock.

## Control Flow
Probe maps registers, gets/enables clock, disables and stops the TMU, loads trim or default trim, computes a divider for a 4 MHz conversion clock, programs power-up delay, resolution, periodic measurement mode, and 25 Hz period, enables the TMU, installs a cleanup action, enables runtime PM, registers the thermal zone and hwmon, requests the IRQ, and runtime-suspends the device. Thermal mode changes acquire/release runtime PM, configure threshold mode as greater-or-equal, and start/stop measurements. `set_trips()` disables threshold IRQ, writes the high threshold, clears stale flag, and re-enables the IRQ.

## State and Persistence
State is MMIO/clock/device/zone pointers and runtime PM usage count. Hardware trim, divider, period, resolution, threshold, and interrupt bits persist while powered.

## Dependencies and Integration Points
Depends on nvmem, clocks, runtime PM, platform IRQ, thermal OF zone callbacks (`get_temp`, `change_mode`, `set_trips`), and hwmon sysfs.

## Risks and Edge Cases
- `set_trips()` rejects `high >= 125000`; callers passing `INT_MAX` to disable high trips will get `-EINVAL`.
- Clock divider computation assumes rate at least 4 MHz; lower rates can underflow unsigned `div`.
- Fallback trim values permit operation but may reduce accuracy.
- IRQ remains disabled after firing until thermal core calls `set_trips()` again.
- Runtime PM get/put balance depends on thermal mode transitions.

## Test Signals
Tests should verify trim nvmem and fallback paths, divider boundary values, temperature conversion for negative and positive 16-bit values, `set_trips()` programming and high-limit rejection, IRQ top/thread behavior, runtime suspend/resume, and mode enable/disable PM balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/imx91_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/imx_sc_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/imx_sc_thermal.c

## Purpose
NXP i.MX System Controller thermal driver. It exposes multiple firmware-managed resource temperatures as OF thermal zones by issuing SCU MISC GET_TEMP RPCs.

## Important APIs, Types, and Functions
- Global `thermal_ipc_handle` stores the SCU IPC handle.
- `struct imx_sc_sensor` stores thermal zone and SCU resource id.
- Packed request/response structs define the `IMX_SC_MISC_FUNC_GET_TEMP` RPC payload.
- `imx_sc_thermal_get_temp()` builds an SCU RPC for the sensor's resource id and converts celsius/tenths to millicelsius.
- `imx_sc_thermal_probe()` gets the SCU handle, iterates match-data resource ids until `-1`, registers available OF thermal zones, and adds hwmon sysfs.

## Control Flow
Probe obtains the firmware IPC handle and resource-id array from OF match data. For each resource id, it allocates a sensor and attempts to register a thermal OF zone using that resource id as the zone id. `-ENODEV` from registration means no DT thermal-zone description and is skipped; other errors abort probe. Reads synchronously call SCU firmware and return the reported temperature.

## State and Persistence
State is per-sensor resource id and thermal zone. The IPC handle is global. Temperatures are not cached.

## Dependencies and Integration Points
Depends on i.MX SCU firmware IPC, DT resource bindings, thermal OF zones, hwmon sysfs, and firmware-provided resource identifiers.

## Risks and Edge Cases
- Global IPC handle assumes a single SCU context.
- Firmware call latency/failure directly affects thermal reads.
- Zone ids are SCU resource ids, not dense indices; DT thermal maps must match.
- Sensors without DT zones are silently skipped after freeing their allocation.

## Test Signals
Tests should mock SCU RPC success/failure, skipped `-ENODEV` zones, resource iteration termination, temperature conversion with negative tenths, and hwmon addition for registered zones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/imx_sc_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/imx_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/imx_thermal.c

## Purpose
Legacy Freescale/NXP i.MX6/i.MX7 tempmon thermal driver. It reads calibration/temperature-grade data, programs tempmon measurement and alarm registers, registers a thermal zone with passive and critical trips, optionally registers legacy cpufreq cooling, and manages runtime/system PM.

## Important APIs, Types, and Functions
- `struct thermal_soc_data` captures register offsets, masks, shifts, and version-specific fields for i.MX6Q, i.MX6SX, and i.MX7D.
- `struct imx_thermal_data` stores device, cpufreq policy/cooling device, zone, tempmon regmap, calibration coefficients `c1/c2`, trip temperatures, alarm/last temperature, IRQ state, clock, SoC data, and temp grade.
- `imx_init_calib()` derives conversion coefficients from OCOTP calibration.
- `imx_init_temp_grade()` derives max/passive/critical trip temperatures from fuse grade.
- `imx_get_temp()` runtime-resumes hardware, validates sample completion, converts raw measurements, adjusts i.MX6Q alarm between passive and critical trips, and re-enables IRQ when below alarm.
- `imx_set_alarm_temp()` and `imx_set_panic_temp()` program hardware thresholds.
- `imx_change_mode()` manages runtime PM and IRQ enable state.
- `imx_set_trip_temp()` allows changing passive trip temperature and alarm.
- `imx_thermal_register_legacy_cooling()` creates cpufreq cooling if CPU node lacks `#cooling-cells`.
- Probe initializes regmaps, calibration, sensor state, cooling, clock, zone, measurement frequency, alarm, runtime PM, IRQ, and zone enable.

## Control Flow
Probe obtains the tempmon syscon regmap and SoC match data, clears i.MX6SX stale IRQ state, reads calibration/temp-grade from nvmem or legacy `fsl,tempmon-data`, initializes hardware to a known powered-down state, registers legacy cpufreq cooling if needed, enables the thermal clock, registers the thermal zone with two trips, configures 10 Hz measurement and alarm thresholds, powers the sensor, enables runtime PM, enables the thermal zone, and requests the alarm IRQ. Alarm top half disables the IRQ and wakes the thread; the thread updates the thermal zone. Temperature reads resume hardware, convert sample, update dynamic alarm for i.MX6Q, and re-enable IRQ once temperature falls below the programmed alarm.

## State and Persistence
Global static `trips[]` stores passive/critical trip definitions and is modified at probe and by `set_trip_temp()`. Per-device state tracks calibration coefficients, temp grade, alarm temperature, last temp, IRQ enable, cpufreq cooling, and runtime PM state. Hardware alarm/measurement registers persist while powered.

## Dependencies and Integration Points
Depends on syscon/regmap, nvmem or legacy OCOTP regmap, clocks, runtime PM, platform IRQs, thermal core, optional cpufreq cooling APIs, OF thermal/cooling bindings, and device PM callbacks.

## Risks and Edge Cases
- Static `trips[]` is shared across instances, so multiple devices would share mutable trip temperatures.
- `imx_get_temp()` and `imx_set_trip_temp()` return without `pm_runtime_put()` on some error paths after successful resume.
- Legacy cpufreq cooling is only registered when CPU0 lacks `#cooling-cells`.
- Calibration math is fuse-sensitive; invalid or all-ones data fails probe.
- Dynamic alarm switching for i.MX6Q is subtle and tied to passive/critical trip ordering.
- IRQ re-enable depends on reads occurring after temperature drops below alarm.

## Test Signals
Tests should cover nvmem and legacy calibration paths, each SoC register layout, temp-grade trip selection, conversion formulas, passive trip sysfs update bounds, IRQ disable/thread/update/re-enable flow, runtime PM error paths, legacy cpufreq cooling registration, suspend/resume, and i.MX6SX stale interrupt clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/imx_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/Kconfig

## Purpose
Top-level Kconfig entries for Intel thermal drivers. It defines Intel x86 thermal feature symbols, includes the INT340x ACPI submenu, and describes dependencies for package DTS, SoC DTS, Quark DTS, PMIC, PCH, TCC cooling, PowerClamp, and HFI thermal support.

## Important APIs, Types, and Functions
No runtime APIs. Key symbols include `INTEL_POWERCLAMP`, `X86_THERMAL_VECTOR`, `INTEL_TCC`, `X86_PKG_TEMP_THERMAL`, `INTEL_SOC_DTS_IOSF_CORE`, `INTEL_SOC_DTS_THERMAL`, `INTEL_QUARK_DTS_THERMAL`, `INTEL_BXT_PMIC_THERMAL`, `INTEL_PCH_THERMAL`, `INTEL_TCC_COOLING`, and `INTEL_HFI_THERMAL`.

## Control Flow
Kconfig dependency resolution selects helper libraries and exposes user-selectable drivers. The file enters an `ACPI INT340X thermal drivers` menu and sources `drivers/thermal/intel/int340x_thermal/Kconfig`.

## State and Persistence
No runtime state. Symbol selections persist in kernel config.

## Dependencies and Integration Points
Integrates with x86 CPU vendor support, local APIC thermal vectors, PCI, ACPI, NET/THERMAL_NETLINK, IOSF, powercap/RAPL, ACPI thermal libraries, and Intel TCC helper code.

## Risks and Edge Cases
Wrong dependencies can expose drivers on platforms without required firmware interfaces. Several symbols select helper subsystems, so dependency changes affect build footprint.

## Test Signals
Kconfig/build testing should cover x86 and COMPILE_TEST-style matrices where applicable, allmodconfig, module/built-in combinations, and submenu symbol propagation to Makefile targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/Makefile

## Purpose
Kbuild object map for Intel thermal drivers. It links selected Intel thermal modules and the `int340x_thermal/` subdirectory.

## Important APIs, Types, and Functions
No runtime APIs. It maps config symbols to objects such as `intel_tcc.o`, `intel_powerclamp.o`, `x86_pkg_temp_thermal.o`, `intel_soc_dts_iosf.o`, `intel_soc_dts_thermal.o`, `intel_quark_dts_thermal.o`, `intel_bxt_pmic_thermal.o`, `intel_pch_thermal.o`, `intel_tcc_cooling.o`, `therm_throt.o`, `intel_hfi.o`, and the int340x directory.

## Control Flow
Kbuild includes object files according to `CONFIG_*` values. `CONFIG_INT340X_THERMAL` descends into the int340x thermal subdirectory.

## State and Persistence
No runtime state. Build outputs persist in the build tree.

## Dependencies and Integration Points
Must remain synchronized with top-level Intel Kconfig, source filenames, and subdirectory Makefiles.

## Risks and Edge Cases
Object mapping typos break builds or omit selected drivers. Directory descent for `INT340X_THERMAL` must match submenu dependencies.

## Test Signals
Per-symbol build tests, allmodconfig, and module install checks should verify each configured object is produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/Kconfig

## Purpose
Kconfig definitions for ACPI INT340x thermal support. It defines the main `INT340X_THERMAL` feature, ACPI thermal relationship helper `ACPI_THERMAL_REL`, optional INT3406 display thermal driver, and `PROC_THERMAL_MMIO_RAPL`.

## Important APIs, Types, and Functions
No runtime APIs. Main symbols are `INT340X_THERMAL`, `ACPI_THERMAL_REL`, `INT3406_THERMAL`, and `PROC_THERMAL_MMIO_RAPL`.

## Control Flow
When `INT340X_THERMAL` is selected, it pulls in thermal netlink, ACPI relationship parsing, ACPI fan, ACPI thermal library, Intel SoC DTS IOSF core, Intel TCC, ACPI platform profile, and optional processor thermal MMIO RAPL if powercap is enabled. Additional options are visible only inside the `if INT340X_THERMAL` block.

## State and Persistence
No runtime state. Selections persist in kernel config.

## Dependencies and Integration Points
Integrates ACPI thermal firmware objects (INT3400 master and INT3401-INT340B slaves), userspace policy daemons such as thermald, display thermal management, ACPI fan, platform profile, and Intel processor thermal modules.

## Risks and Edge Cases
The main symbol has broad `select` behavior; selecting it can force several ACPI/Intel subsystems into the build. Missing dependencies for optional display or RAPL pieces would surface at build time.

## Test Signals
Kconfig tests should verify symbol visibility and selected dependencies for `INT340X_THERMAL`, with and without `POWERCAP`, and with `ACPI_VIDEO` for INT3406.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/Makefile

## Purpose
Kbuild map for ACPI INT340x thermal drivers and related processor thermal components.

## Important APIs, Types, and Functions
No runtime APIs. `INT340X_THERMAL` builds `int3400_thermal.o`, `int340x_thermal_zone.o`, `int3402_thermal.o`, `int3403_thermal.o`, `processor_thermal_device.o`, `int3401_thermal.o`, PCI processor thermal variants, RFIM/mailbox/workload/power-floor/SOC-slider components, and platform temperature control. Optional symbols build `processor_thermal_rapl.o`, `int3406_thermal.o`, and `acpi_thermal_rel.o`.

## Control Flow
Kbuild expands all `obj-$(CONFIG_...)` lines based on selected INT340x symbols. Many implementation files are compiled together under the single main symbol.

## State and Persistence
No runtime state. Build artifacts persist in the build directory.

## Dependencies and Integration Points
Must align with int340x Kconfig and all listed source files. It wires the ACPI relationship helper into the same subdirectory build.

## Risks and Edge Cases
The broad object list under `INT340X_THERMAL` means build failures in one component affect the whole feature. Renames or symbol splits need careful Makefile updates.

## Test Signals
Build tests should cover `INT340X_THERMAL` alone, with `PROC_THERMAL_MMIO_RAPL`, with `INT3406_THERMAL`, and with `ACPI_THERMAL_REL` selected indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/acpi_thermal_rel.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/acpi_thermal_rel.c

## Purpose
ACPI thermal relationship helper and misc character device. It parses ACPI `_TRT`, `_ART`, and `PSVT` relationship tables for in-kernel consumers and exposes them to userspace through ioctl calls on `acpi_thermal_rel`.

## Important APIs, Types, and Functions
- Global `acpi_thermal_rel_handle` points to the ACPI device containing relationship tables.
- `acpi_thermal_rel_open()`/`release()` implement simple exclusive-open handling under a spinlock.
- Exported parsers `acpi_parse_trt()` and `acpi_parse_art()` evaluate ACPI methods, extract package entries, optionally instantiate referenced ACPI devices, skip malformed entries, and return allocated arrays.
- Static `acpi_parse_psvt()` parses version-2 `PSVT`, supports integer or string control-knob limit fields, validates source/target devices, and returns allocated entries.
- `get_single_name()` converts ACPI handles to 4-character names for userspace payloads.
- `fill_trt()`, `fill_art()`, and `fill_psvt()` convert parsed kernel structures into user ABI unions and copy them to userspace.
- `acpi_thermal_rel_ioctl()` handles count, length, and data ioctls for TRT/ART/PSVT.
- `acpi_thermal_rel_misc_device_add()` and `_remove()` register/deregister the misc device and are exported.

## Control Flow
INT3400 or another caller registers the misc device with an ACPI handle. Userspace opens the nonseekable char device, then issues ioctls. Count/length ioctls parse the relevant ACPI table and return a scalar. Data ioctls parse the table, allocate ABI-sized arrays, translate handles to ACPI single names, copy fields, and copy to userspace. Kernel drivers can call `acpi_parse_trt()`/`acpi_parse_art()` directly and free the returned arrays.

## State and Persistence
The misc device has global open count/exclusive state and a global ACPI handle. Parsed table data is allocated per call and freed by caller or fill helper. No table data is cached.

## Dependencies and Integration Points
Depends on ACPI evaluation/extraction, miscdevice, file operations, copy_to_user/put_user, platform ACPI device creation through `acpi_fetch_acpi_dev()`, and the ABI definitions in `acpi_thermal_rel.h`.

## Risks and Edge Cases
- The misc device/global handle design assumes one active relationship provider; multiple INT3400-like devices would overwrite the handle.
- `ACPI_THERMAL_GET_PSVT_LEN` computes `length` even if parse fails and only frees `psvts` on success.
- `fill_*` ioctls copy data to user buffers without a user-provided size, relying on callers to query length first.
- `acpi_parse_art()` subtracts one for revision without first checking package count; malformed empty packages are risky.
- PSVT string parsing truncates overlong strings and stores type info in a field the spec calls reserved.

## Test Signals
Tests should cover valid and malformed TRT/ART/PSVT packages, bad entry skipping and count adjustment, string vs integer PSVT limit, source/target ACPI device lookup failures, ioctl count/len/data behavior, exclusive open semantics, copy_to_user fault injection, and register/deregister lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/acpi_thermal_rel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/acpi_thermal_rel.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/acpi_thermal_rel.h

## Purpose
Header defining the ACPI thermal relationship ioctl ABI and in-kernel data structures for ART, TRT, and PSVT thermal relationship tables.

## Important APIs, Types, and Functions
- Ioctl numbers: `ACPI_THERMAL_GET_TRT_LEN`, `GET_ART_LEN`, `GET_TRT_COUNT`, `GET_ART_COUNT`, `GET_TRT`, `GET_ART`, `GET_PSVT_LEN`, `GET_PSVT_COUNT`, and `GET_PSVT`.
- Kernel structs `struct art`, `struct trt`, and `struct psvt` mirror parsed ACPI table entries with ACPI handles and numeric fields.
- User ABI unions `union art_object`, `union trt_object`, and `union psvt_object` replace handles with 8-byte source/target name fields and expose fixed-size u64 layouts.
- Kernel prototypes expose misc-device registration and ART/TRT parsers.

## Control Flow
The header is included by the relationship driver and INT3400 thermal code. Userspace ioctl command numbers must match the char-device implementation. Kernel users call parser prototypes when `__KERNEL__` is defined.

## State and Persistence
No state. It defines packed layouts and ioctl constants that form a persistent ABI.

## Dependencies and Integration Points
Depends on ACPI handle types, `asm/ioctl.h`, and the misc-device implementation. The struct layouts are coupled to ACPI method package formats and userspace thermal daemons.

## Risks and Edge Cases
- ABI layout changes would break userspace; unions intentionally expose fixed u64 arrays.
- `ACPI_LIMIT_STR_MAX_LEN` is 8, so string limits are short and must be truncated consistently.
- `control_knob_type` borrows a reserved PSVT field for type metadata.
- Comment typo "usrspace" is harmless but signals old ABI surface.

## Test Signals
Compile tests should validate header inclusion in kernel and userspace-style contexts. ABI tests should check structure sizes, ioctl numbers, packed layout, and compatibility with `acpi_thermal_rel.c` copy logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/acpi_thermal_rel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3400_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3400_thermal.c

## Purpose
ACPI INT3400 master thermal driver. It negotiates thermal policy UUIDs with firmware through `_OSC`, parses ACPI relationship tables, registers a fake-temperature thermal zone for notifications, exposes policy/data sysfs files, registers the relationship misc device, handles ACPI notifications, and supports ODVP/production-mode metadata.

## Important APIs, Types, and Functions
- `struct int3400_thermal_priv` stores ACPI/platform devices, thermal zone, ART/TRT arrays, supported/current UUID state, relationship misc registration result, data vault, ODVP data, OS UUID mask, production mode, and dynamic ODVP attributes.
- UUID arrays enumerate active, passive, critical, adaptive performance, emergency, virtual sensor, cooling mode, and duty-cycling policies.
- Sysfs handlers: `available_uuids_show()`, `current_uuid_show/store()`, `imok_store()`, `production_mode_show()`, and dynamic ODVP attributes.
- `int3400_thermal_run_osc()` executes ACPI `_OSC` for a UUID/capability bit and validates firmware response.
- `set_os_uuid_mask()` uses the newer OS capability UUID path for active/passive/critical policies.
- `int3400_thermal_get_uuids()` evaluates `IDSP` and builds supported UUID bitmap.
- `evaluate_odvp()` evaluates `ODVP`, allocates values and per-index sysfs files.
- `int3400_notify()` maps ACPI events to thermal events and emits uevents.
- `int3400_thermal_change_mode()` enables/disables the selected policy via `_OSC` and refreshes ODVP.
- Probe wires all pieces together; remove unwinds them.

## Control Flow
Probe requires an ACPI companion, allocates private state, reads supported UUIDs if `IDSP` exists, parses ART/TRT tables with device creation, stores drvdata, optionally captures GDDV data vault, evaluates ODVP, registers a tripless fake thermal zone, registers the ACPI relationship misc device, creates UUID and optional IMOK/data-vault sysfs, installs an ACPI notify handler, and initializes production mode sysfs if `DCFG` exists. Users select a current UUID via sysfs or set an OS UUID capability mask. Thermal mode changes run `_OSC` to enable/disable the selected policy and then refresh ODVP. ACPI notifications generate thermal uevents for table change, keep-alive, or ODVP change.

## State and Persistence
Private state tracks current UUID index or OS UUID mask, supported UUID bitmap, parsed ART/TRT arrays, ODVP values, production mode, and optional data vault. Firmware policy enablement persists in ACPI/firmware after `_OSC` until changed. The thermal zone always reports fake 20C.

## Dependencies and Integration Points
Depends on ACPI methods (`IDSP`, `_OSC`, `_ART`, `_TRT`, `GDDV`, `ODVP`, `IMOK`, `DCFG`), the ACPI relationship helper, thermal zone/uevent APIs, sysfs/bin attributes, ACPI notify handlers, and userspace policy daemons such as thermald.

## Risks and Edge Cases
- UUID matching in `current_uuid_store()` uses only a 7-character prefix, allowing ambiguous/partial inputs if prefixes collide.
- Fake temperature means the zone is an event/control endpoint, not a real sensor.
- Several `kasprintf()` calls in notify are unchecked before uevent.
- Error unwinding has many sysfs/misc/thermal steps; missing optional IMOK group removal is tolerated but should be reviewed.
- Global misc-device relationship helper limits multiple INT3400 instances.
- ODVP dynamic sysfs creation must clean up partially created attributes on failure.

## Test Signals
Tests should cover missing and malformed `IDSP`, UUID sysfs read/write, `_OSC` success/failure, OS UUID mask enable/disable, ART/TRT parse failures as nonfatal, GDDV data-vault creation, ODVP creation/update/cleanup, ACPI notification uevents, production-mode sysfs, and probe error unwinding at each stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3400_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3401_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3401_thermal.c

## Purpose
ACPI INT3401 processor thermal reporting device driver. It is a small platform wrapper that allocates processor thermal private state and delegates lifecycle and PM operations to shared processor thermal helpers.

## Important APIs, Types, and Functions
- `int3401_device_ids[]` matches ACPI `INT3401`.
- `int3401_add()` allocates `struct proc_thermal_device`, calls `proc_thermal_add()`, and stores drvdata.
- `int3401_remove()` calls `proc_thermal_remove()`.
- PM callbacks delegate to `proc_thermal_suspend()` and `proc_thermal_resume()` when sleep PM is enabled.
- Platform driver name is `int3401 thermal`.

## Control Flow
On probe, the driver allocates managed private data and lets the common processor thermal layer set up sensors, trips, and cooling/controls. Remove retrieves private data and delegates teardown. Suspend/resume pass through to common processor thermal callbacks.

## State and Persistence
This wrapper owns only the allocated `proc_thermal_device` pointer stored in platform drvdata. All substantive state belongs to the shared processor thermal implementation.

## Dependencies and Integration Points
Depends on ACPI platform matching, `processor_thermal_device.h`, `int340x_thermal_zone.h`, thermal core, and the common processor thermal helper implementation built by the same int340x Makefile.

## Risks and Edge Cases
- Probe behavior and failures are entirely determined by `proc_thermal_add()`.
- The wrapper has no OF/DT fallback and only matches `INT3401`.
- PM callback availability depends on `CONFIG_PM_SLEEP`.

## Test Signals
Tests should verify allocation failure, `proc_thermal_add()` error propagation, drvdata setup, remove delegation, and suspend/resume delegation under PM_SLEEP builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3401_thermal.c -->
