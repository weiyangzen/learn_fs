# Research: subset-b-005154

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/sequencing/pwrseq-thead-gpu.c -->
## sources/distributed-fs/ceph-client/drivers/power/sequencing/pwrseq-thead-gpu.c

Purpose: this auxiliary-bus power sequencing provider implements the GPU power sequence for the T-HEAD TH1520 Imagination BXM-4-64 GPU. It bridges resources owned by the parent always-on power-domain/clkgen node with resources owned by the GPU consumer node, exposing one power-sequencing target named `gpu-power` and one unit named `gpu-power-sequence`.

Important APIs, types, and functions: `struct pwrseq_thead_gpu_ctx` persists provider state, parent `gpu-clkgen` reset, AON node, and lazily acquired consumer clocks/reset. `pwrseq_thead_gpu_probe()` obtains the parent reset and registers a `pwrseq_device` through `devm_pwrseq_device_register()`. `pwrseq_thead_gpu_match()` accepts only `thead,th1520-gpu` consumers whose `power-domains` phandle points at the provider AON node with domain id `TH1520_GPU_PD`; it then gets `"core"` and `"sys"` clocks and a shared GPU reset from the consumer device. `pwrseq_thead_gpu_enable()` enables clocks, deasserts the clkgen reset, waits one microsecond, and deasserts the GPU reset. `pwrseq_thead_gpu_disable()` asserts GPU reset, asserts clkgen reset, and disables clocks. Module binding is through auxiliary id `th1520_pm_domains.pwrseq-gpu`.

Control flow: probe initializes provider-side resources only. Consumer-side resources are acquired during match, because the GPU clocks and core reset belong to the consumer node rather than the auxiliary provider node. A successful first match pins `consumer_node`; later matching is allowed only for the same device node. Enable follows a hardware ordering constraint: clocks on, parent clkgen reset deassert, delay for at least 32 cycles, GPU reset deassert. Error unwinding reverses partial enable. Disable records the first reset assertion error but always disables clocks.

State and persistence: state is in memory only. Devm handles provider registration and parent reset lifetime. Consumer resources are manually retained after first match and released in remove with `reset_control_put()`, `clk_bulk_put()`, `kfree()`, and `of_node_put()`. There is no runtime persistence, no sysfs state, and no suspend/resume hooks.

Dependencies and integration points: the file depends on the power sequencing provider API, auxiliary bus, common clock framework, reset controller framework, OF phandle parsing, and `dt-bindings/power/thead,th1520-power.h`. The driver assumes the parent device's OF node is the AON power-domain provider and that the GPU node has `core` and `sys` clocks plus a reset compatible with `reset_control_get_shared(dev, NULL)`.

Risks: the match path mutates provider state and does not protect `consumer_node`, `clks`, or `gpu_reset` with an explicit lock, so concurrent match attempts would rely on pwrseq core serialization. A failed `reset_control_deassert(ctx->gpu_reset)` causes clkgen reset assertion and clock disable, but a failed clkgen assertion during disable leaves clocks disabled with an error reported. `measure`-style validation is absent; the one microsecond delay is a reasoned fixed delay from the documented 32-cycle requirement. The provider only supports a single consumer and intentionally rejects other GPU-like nodes.

Test signals: build with the TH1520 PM domain auxiliary device and pwrseq framework enabled. Probe should register `pwrseq-thead-gpu` and match only a `thead,th1520-gpu` node using `TH1520_GPU_PD`. Runtime tests should verify clock prepare/enable count symmetry, reset ordering on a logic analyzer or tracepoints, successful bind of the GPU driver through target `gpu-power`, and error paths by injecting clock/reset failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/sequencing/pwrseq-thead-gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/88pm860x_battery.c -->
## sources/distributed-fs/ceph-client/drivers/power/supply/88pm860x_battery.c

Purpose: this platform power-supply driver monitors the Marvell 88PM860x PMIC battery. It reports battery presence, capacity, voltage, current, and temperature through the Linux power supply class while maintaining a local coulomb-counter and open-circuit-voltage based state-of-charge estimate.

Important APIs, types, and functions: `struct pm860x_battery_info` stores PMIC I2C handles, IRQs, battery state, capacity inputs, internal resistance, last capacity, startup SOC, presence, and temperature source. `struct ccnt` and static `ccnt_data` accumulate positive and negative coulomb-counter readings. Measurement helpers include `measure_12bit_voltage()`, `measure_vbatt()`, `measure_current()`, `measure_temp()`, and `calc_ocv()`. SOC and capacity logic lives in `calc_soc()`, `calc_ccnt()`, `clear_ccnt()`, `calc_resistor()`, and `calc_capacity()`. Power supply callbacks are `pm860x_batt_get_prop()`, `pm860x_batt_set_prop()`, and `pm860x_external_power_changed()`. IRQ handlers are `pm860x_coulomb_handler()` and `pm860x_batt_handler()`.

Control flow: probe chooses the PM8607 I2C client from the parent MFD chip, reads two IRQ resources, initializes hardware measurement bits, detects battery presence, computes active OCV SOC, optionally restores SOC from RTC-domain registers, registers power supply `battery-monitor`, then requests coulomb and battery attach/remove threaded IRQs. Property reads perform live PMIC conversions: voltage and current read ADC/coulomb registers; capacity first updates accumulated counter data, combines startup SOC with charge/discharge totals, cross-checks OCV while discharging, clamps monotonic discharge behavior, then stores reported SOC back into RTC registers. Charge-full set_property clears the counter and resets SOC to 100.

State and persistence: runtime state is kept in `pm860x_battery_info` and static global `ccnt_data`. Capacity persistence uses PM8607 RTC registers `RTC_MISC2` and `RTC1`; startup compares restored RTC SOC to OCV SOC and rejects it if it differs by more than 15 percentage points. `POWER_UP_LOG` and `BAT_WU_LOG` decide whether a battery wake/removal event invalidated stored SOC. Suspend/resume only toggles the parent chip wakeup flag for the coulomb IRQ when device wakeup is enabled.

Dependencies and integration points: the driver depends on `MFD_88PM860X`, PM860x register helpers, platform data `struct pm860x_power_pdata` for optional capacity/resistance, Linux power supply class, and PM8607 IRQ routing. It integrates with `88pm860x_charger.c` by exposing `battery-monitor`; the charger reads voltage/presence/temp and writes `POWER_SUPPLY_PROP_CHARGE_FULL`. The battery reacts to `external_power_changed` by recalculating internal resistance using charger current changes.

Risks: capacity math combines static global coulomb data with per-device state, so multiple instances would interfere. Several PMIC writes in initialization and threshold adjustment log only by returning from void paths, so failures may silently degrade monitoring. `measure_vbatt()` sleep-mode conversion appears to compute from `*data` instead of the local assembled `ret`, which is a likely defect in the sleep OCV path. `calc_resistor()` temporarily changes charger current and sleeps, making external-power change handling slow and dependent on charger cooperation. Locking protects presence/temp selection but not all capacity fields or `ccnt_data`, so IRQ/property races are possible.

Test signals: test PMIC register read/write error injection, battery attach/remove IRQs, coulomb IRQ accumulation, RTC SOC restore/reject paths, capacity monotonicity during discharge, no-battery behavior returning 100 percent and fake 25 C, and charger charge-full notification clearing counters. Hardware tests should compare reported voltage/current/temp against known ADC inputs and verify RTC SOC survives reboot without battery removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/88pm860x_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/88pm860x_charger.c -->
## sources/distributed-fs/ceph-client/drivers/power/supply/88pm860x_charger.c

Purpose: this platform power-supply driver controls the Marvell 88PM860x charger path and exposes a USB power supply named `usb`. It implements a small charging FSM for precharge, fast charge, discharge, low-voltage poweroff notification, charger over-voltage, temperature gating, and charge-done handling.

Important APIs, types, and functions: `struct pm860x_charger_info` stores PM8607/PM8606 I2C clients, USB power supply, IRQ array, FSM state, online/present/allowed bits, and a mutex. Hardware helpers include `measure_vchg()`, `set_vchg_threshold()`, `set_vbatt_threshold()`, `start_precharge()`, `start_fastcharge()`, `stop_charge()`, and `power_off_notification()`. `set_charging_fsm()` is the central FSM. IRQ handlers cover charger detect, temperature, charge exceptions, charge done, VBAT threshold, and VCHG threshold. `pm860x_usb_get_prop()` exposes `STATUS` and `ONLINE`.

Control flow: probe gathers IRQ resources, selects PM8607 and PM8606 clients from the parent MFD chip, initializes VCHG thresholds, registers USB power supply with `supplied_to = "battery-monitor"`, initializes online/allowed from `STATUS_2`, runs the FSM, and requests seven threaded IRQs. The FSM queries the `battery-monitor` power supply for `VOLTAGE_NOW` and `PRESENT`, then transitions among init, discharge, precharge, and fastcharge based on charger online state, battery presence, temperature/exception permission, and voltage thresholds. Charge-done interrupts mark fast charge complete, verify that USB is still physically online via PM8607 status, then notify the battery supply with `CHARGE_FULL` if voltage is above threshold.

State and persistence: all state is volatile in `pm860x_charger_info`; no on-disk or RTC persistence is used here. PMIC register state persists according to hardware behavior: charge mode, current limits, thresholds, preregulator settings, and PM8606 over-temp recovery bits are programmed as side effects. There are no suspend/resume hooks.

Dependencies and integration points: the driver depends on `MFD_88PM860X`, `BATTERY_88PM860X`, PM860x register helpers, and the power supply framework. It requires both PM8607 and companion PM8606 I2C clients. It is hard-wired to the battery power supply name `battery-monitor`, and the battery driver is expected to implement voltage, presence, temperature, and charge-full property handling.

Risks: probe loops over `ARRAY_SIZE(info->irq)` when requesting IRQs even though only `irq_nums` valid entries may have been populated; missing platform IRQ resources could leave zero or stale IRQ values requested. `set_charging_fsm()` calls register-writing charge functions while holding `info->lock`, and several IRQ handlers call into the FSM after dropping or while around locks; deadlock risk is low but latency can be high. The FSM ignores return values from `start_precharge()`, `start_fastcharge()`, and `stop_charge()`, so failed PMIC programming may leave software state ahead of hardware state. The charger/battery name coupling is brittle.

Test signals: validate platform resource counts for all seven IRQ names, charger plug/unplug transitions, precharge-to-fastcharge voltage threshold crossing, charge-done notification ordering during USB unplug races, temperature IRQ gating below -10 C and above 40 C, VCHG over-voltage/recovery thresholds, and PM8606 over-temp flag clearing. Power supply sysfs should show `usb/online` matching PMIC `STATUS2_CHG` and `usb/status` matching FSM charge states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/88pm860x_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/power/supply/Kconfig

Purpose: this Kconfig file defines the Linux power supply class menu and the selectable battery, charger, fuel-gauge, and power-source drivers under `drivers/power/supply`. It gates compilation, dependency visibility, and helper selection for all drivers in this subsystem.

Important APIs, types, and functions: the file is declarative Kconfig rather than C. The top-level `menuconfig POWER_SUPPLY` enables the class. `POWER_SUPPLY_DEBUG` adds debug compilation, `POWER_SUPPLY_HWMON` exposes sensors as hwmon, and `ADC_BATTERY_HELPER` is a silent helper. Relevant symbols for this subset include `BATTERY_88PM860X`, `CHARGER_88PM860X`, and `AB8500_BM`. `BATTERY_88PM860X` depends on `MFD_88PM860X`; `CHARGER_88PM860X` depends on both `MFD_88PM860X` and `BATTERY_88PM860X`; `AB8500_BM` is bool and depends on `AB8500_CORE`, `AB8500_GPADC`, built-in `IIO`, and `OF`, and selects `THERMAL` plus `THERMAL_OF`.

Control flow: Kconfig evaluation controls which Makefile object rules become active. Many entries are tristate modules, while some platform data or shared data options are bool. Dependencies constrain menu visibility and prevent impossible link combinations, such as the 88PM860x charger without the matching battery monitor. `select` is used for helper subsystems like `REGMAP_I2C`, `AUXILIARY_BUS`, `THERMAL`, and `THERMAL_OF` when a driver requires them.

State and persistence: there is no runtime state. Configuration state persists in kernel `.config`, generated headers, and module build decisions. Because `AB8500_BM` is bool, its five-object battery-management group is built into the kernel rather than as separate modules when selected.

Dependencies and integration points: this file integrates with `drivers/power/supply/Makefile`, generated `include/generated/autoconf.h`, Kbuild, and subsystem menus for MFD, IIO, OF, ACPI, USB, extcon, thermal, hwmon, and regmap. It documents expected module names in help text for many drivers.

Risks: dependency drift here can produce link failures or runtime probe failures if a driver uses a subsystem not expressed in Kconfig. `select` can force subsystems on without their own dependencies being met if used carelessly; the AB8500 entry handles this partly by requiring `IIO = y`. The large single menu increases merge-conflict risk and makes alphabetical or subsystem grouping mistakes easy. Help text typos do not affect builds but can mislead users about module names or hardware support.

Test signals: run Kconfig dependency checks through representative configs: minimal `POWER_SUPPLY=n`, 88PM860x battery only, 88PM860x battery plus charger, and AB8500 built-in with OF/IIO/thermal. Build tests should confirm enabled symbols produce the objects named in Makefile and disabled symbols leave no unresolved references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/Makefile -->
## sources/distributed-fs/ceph-client/drivers/power/supply/Makefile

Purpose: this Kbuild file maps power-supply Kconfig symbols to compiled objects. It builds the core `power_supply.o`, optional helper objects, and one object per battery/charger/fuel-gauge driver, including the subset drivers.

Important APIs, types, and functions: this is declarative Kbuild. `subdir-ccflags-$(CONFIG_POWER_SUPPLY_DEBUG) := -DDEBUG` enables debug messages. `power_supply-y` combines core pieces, conditionally adding sysfs and LED trigger support. Relevant object mappings are `obj-$(CONFIG_BATTERY_88PM860X) += 88pm860x_battery.o`, `obj-$(CONFIG_CHARGER_88PM860X) += 88pm860x_charger.o`, and `obj-$(CONFIG_AB8500_BM) += ab8500_bmdata.o ab8500_charger.o ab8500_fg.o ab8500_btemp.o ab8500_chargalg.o`.

Control flow: Kbuild expands each `obj-$(CONFIG_...)` according to generated config values. Tristate symbols produce built-in or module objects; bool symbols produce only built-in participation. The AB8500 battery-management symbol pulls multiple cooperating compilation units into the same built-in group.

State and persistence: no runtime state exists. Build state appears in generated object files and module artifacts. The Makefile ordering can matter for built-in link ordering and initialization availability.

Dependencies and integration points: the file depends on Kconfig symbols from the sibling Kconfig and on the source files being present with matching names. It integrates with subsystem-wide Kbuild and module installation. `power_supply-y` composition integrates power supply core, sysfs, LEDs, and hwmon support.

Risks: stale object mappings cause selected drivers to silently not build or obsolete files to be referenced. Multi-object groupings like AB8500 can hide intra-group link dependencies and require all companion files to remain buildable together. Debug flags affect every file in the directory, so enabling `POWER_SUPPLY_DEBUG` can alter logging volume broadly.

Test signals: run `make drivers/power/supply/` or targeted object builds for `88pm860x_battery.o`, `88pm860x_charger.o`, and the AB8500 object group under matching configs. Confirm module names and built-in object lists match Kconfig help and that no object is orphaned by `rg '^obj-\\$'` comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500-bm.h -->
## sources/distributed-fs/ceph-client/drivers/power/supply/ab8500-bm.h

Purpose: this header centralizes AB8500 battery-management register offsets, bit constants, shared configuration structures, and cross-file function declarations. It is the contract between AB8500 charger, fuel gauge, battery temperature, charging algorithm, and battery data code.

Important APIs, types, and functions: register constants cover AB8500 system control, USB/ULPI, charger status/control, main and USB charger control, gas gauge, interrupt, RTC, OTP, AB8505 power-cut, and AB8540 USB power-path registers. Shared data types include `struct ab8500_fg_parameters`, `struct ab8500_maxim_parameters`, `struct ab8500_bm_capacity_levels`, `struct ab8500_bm_charger_parameters`, and `struct ab8500_bm_data`. Exports include global `ab8500_bm_data`, charger USB state notification, fuel-gauge access/current-measurement helpers, DT battery-info probe/remove helpers, and platform-driver externs for AB8500 FG, btemp, and chargalg.

Control flow: the header has no executable flow, but it defines how runtime files coordinate. `ab8500_bm_data` provides parameters read by AB8500 components. Fuel-gauge instantaneous-current helpers are used by btemp to identify battery resistance. `ab8500_bm_of_probe()` and remove are called by components that own a power supply and need battery info from device tree. The external platform-driver declarations allow a higher-level AB8500 battery-management registration unit to register cooperating subdrivers.

State and persistence: the main state contract is `struct ab8500_bm_data`, which holds a pointer to `power_supply_battery_info`, intervals, safety timers, backup battery settings, capacity scaling flags, charger limits, thermal hysteresis, and pointers to immutable parameter tables. RTC and gas-gauge constants support persistent hardware features, but persistence is implemented in C files.

Dependencies and integration points: this header depends on Linux kernel types and the power supply class. It codifies AB8500/AB8505/AB8540 hardware register interfaces consumed by `ab8500_bmdata.c`, `ab8500_btemp.c`, `ab8500_chargalg.c`, and companion charger/fuel-gauge files. It also integrates with DT battery bindings through `power_supply_battery_info`.

Risks: the header name guard `_AB8500_CHARGER_H_` does not match the filename, which is harmless but confusing. Many constants are raw register encodings; incorrect reuse across AB8500 cuts can program unsupported values. Since `ab8500_bm_data` is an extern mutable global, component ordering and shared updates must be disciplined. Structure field unit conventions mix seconds, microamps, microvolts, percent, and register encodings, so callers need careful unit handling.

Test signals: compile every AB8500 object together under `CONFIG_AB8500_BM=y`, validate no stale extern declarations remain, and use sparse or review checks for unit correctness. Hardware/emu tests should confirm register constants match AB8500 cut-specific documentation and that DT-provided battery data populates `ab8500_bm_data.bi` before consumers use it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500-bm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500-chargalg.h -->
## sources/distributed-fs/ceph-client/drivers/power/supply/ab8500-chargalg.h

Purpose: this header defines the charger abstraction consumed by the AB8500 charging algorithm. It lets the algorithm operate over AC and USB charger power supplies through a common `ux500_charger` interface.

Important APIs, types, and functions: `psy_to_ux500_charger(x)` converts a mains or USB `power_supply` to its driver data. `struct ux500_charger_ops` contains callbacks for `enable`, `check_enable`, `kick_wd`, and `update_curr`. `struct ux500_charger` wraps a `power_supply`, callback table, maximum output voltage/current, watchdog refresh value, and enabled flag.

Control flow: the header has no executable code. At runtime, `ab8500_chargalg.c` discovers external power supplies, uses `psy_to_ux500_charger()` for mains/USB supplies, and calls these ops to enable/disable charging, verify hardware enable state, kick the charger watchdog, and adjust charge current during maximization.

State and persistence: charger state is per `struct ux500_charger`, owned by the concrete charger driver. The charging algorithm reads `max_out_*` constraints and updates hardware through ops; it does not persist this structure beyond pointers cached in its own device state.

Dependencies and integration points: the file depends on the power supply class. It is tightly integrated with AB8500 charger implementations that expose mains/USB supplies with `struct ux500_charger` as `drv_data`. The comment explicitly limits `psy_to_ux500_charger()` use to `POWER_SUPPLY_TYPE_MAINS` and `POWER_SUPPLY_TYPE_USB`.

Risks: the macro is a raw cast-like retrieval with no runtime type validation; using it on the wrong power supply type would corrupt assumptions. Callback pointers are optional, so callers must continue checking for null ops. Unit expectations for voltage/current are microvolts and microamps; mismatched units would directly affect charger hardware programming.

Test signals: compile users with concrete charger drivers, verify mains/USB power supplies set `drv_data` to `struct ux500_charger`, and exercise algorithm paths for enable, disable, watchdog, check-enable, and current update with missing-op cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500-chargalg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_bmdata.c -->
## sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_bmdata.c

Purpose: this file supplies default AB8500 battery-management data and helpers for filling missing device-tree battery information. It exports the global `ab8500_bm_data` consumed by the AB8500 battery temperature, charger, fuel gauge, and charging algorithm components.

Important APIs, types, and functions: default tables include `ocv_cap_tbl`, `temp_to_batres_tbl_thermistor`, and two-phase `ab8500_maint_charg_table`. Default parameter structures include `cap_levels`, `fg`, `ab8500_maxi_params`, and `chg`. The exported `ab8500_bm_data` sets safety timers, temperature polling intervals, backup battery voltage/current register values, fuel-gauge resistor, capacity levels, charger limits, maximization parameters, and fuel-gauge parameters. `ab8500_bm_of_probe()` calls `power_supply_get_battery_info()` and fills defaults for missing capacity, voltage, current, maintenance charging, thermal alert, resistance, BTI, OCV, and temperature thresholds. `ab8500_bm_of_remove()` releases battery info.

Control flow: a component with a registered power supply calls `ab8500_bm_of_probe()` during setup. The helper obtains DT battery info into `bm->bi`, applies safe defaults when fields are absent or sentinel-valued, and sets `bm->temp_hysteresis`. Later AB8500 components read `bm->bi` and the static defaults through the global `ab8500_bm_data`. Remove releases the `power_supply_battery_info` allocation/reference.

State and persistence: `ab8500_bm_data` is global mutable state for the AB8500 BM subsystem. Its `bi` pointer is populated from device tree at runtime. The default OCV/resistance/maintenance tables are static data. No data is written to persistent storage in this file, but its defaults govern persistent hardware behavior such as fuel-gauge, power-cut, and maintenance charging in companion files.

Dependencies and integration points: the file depends on Linux power supply battery-info helpers and OF battery bindings. It includes `ab8500-bm.h` for shared structures and constants. It directly affects `ab8500_btemp.c` battery identification/temperature behavior and `ab8500_chargalg.c` charge limits, safety timers, maintenance phases, and thermal thresholds.

Risks: `if (bi->charge_term_current_ua) bi->charge_term_current_ua = 200000;` appears inverted relative to the surrounding "fill missing defaults" pattern and may overwrite valid nonzero termination currents while leaving zero unchanged. The global singleton makes multiple AB8500 instances unsafe. Defaults for unknown batteries enable conservative operation but can mask incomplete DT data. Unit mistakes in DT values would propagate to charger programming.

Test signals: test DT with complete battery data and with each field omitted to verify defaults. Confirm maintenance table fallback, OCV table fallback, thermal threshold sentinels, and resistance table selection. Add focused tests or review for `charge_term_current_ua` semantics because it directly controls end-of-charge detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_bmdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_btemp.c -->
## sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_btemp.c

Purpose: this AB8500 component measures battery temperature and battery identification resistance, exposes a power supply named `ab8500_btemp`, and notifies dependent fuel-gauge/charging algorithm components when temperature or battery presence changes.

Important APIs, types, and functions: `struct ab8500_btemp` stores device, AB8500 parent, thermal zone, IIO BATCTRL channel, fuel-gauge pointer, shared BM data, power supply, event bits, temperature range thresholds, workqueue, delayed work, and initialization state. Measurement helpers include `ab8500_btemp_read_batctrl_voltage()`, `ab8500_btemp_batctrl_volt_to_res()`, `ab8500_btemp_get_batctrl_res()`, and `ab8500_btemp_id()`. Periodic behavior is in `ab8500_btemp_periodic_work()` and `ab8500_btemp_periodic()`. IRQ handlers cover battery removal and temperature threshold bands. Power-supply callbacks are `ab8500_btemp_get_property()` and `ab8500_btemp_external_power_changed()`.

Control flow: probe gets the AB8500 parent, resolves thermal zone `battery-thermal`, obtains IIO channel `bat_ctrl`, initializes deferrable periodic work, reads `AB8500_BTEMP_HIGH_TH` to set high-temperature threshold, registers the `ab8500_btemp` power supply, requests five named IRQs, adds the device to a local list, and joins the component framework. Bind creates the workqueue and starts periodic measurement. Periodic work identifies the battery on first run by measuring BATCTRL while the fuel gauge performs an instantaneous current measurement, reads temperature from the thermal zone, filters changes to avoid jumps, calls `power_supply_changed()`, and reschedules based on charger connection state.

State and persistence: state is in memory only: event bits for battery removal and temperature zones, filtered current/previous temperature, charger connection flags, and initialized flag. The code uses static fallback values inside measurement functions for previous ADC/temperature readings. No RTC or nonvolatile persistence is used. Suspend stops periodic work; resume restarts it.

Dependencies and integration points: the driver depends on AB8500 MFD APIs, abx500 register access, component framework, power supply class, thermal framework, IIO consumer API, and fuel-gauge instantaneous-current helpers declared in `ab8500-bm.h`. It supplies `ab8500_chargalg` and `ab8500_fg` and watches external mains/USB supplies to choose faster polling while charging.

Risks: `ab8500_btemp_get_temp()` initializes local `temp` to 0 and compares it to thresholds in event branches, so event-adjusted returns may not behave as intended and usually fall back to `bat_temp`. Static previous ADC/temperature values are shared across instances. Battery ID failure only warns during periodic work and still marks initialized once a temperature update is accepted. Workqueue is created in component bind, so external callbacks before bind must not assume it exists. Remove calls `component_del()` but does not remove the list node, which could matter if the list is used elsewhere.

Test signals: verify deferred probing until `battery-thermal` exists, IIO read fallback behavior, battery identification with in-range and out-of-range BTI resistance, IRQ event to power-supply property changes, filtered temperature ramp behavior, charger connect/disconnect polling interval changes, suspend/resume work cancellation, and AB8500 cut-specific handling for unreliable temperature IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_btemp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_chargalg.c -->
## sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_chargalg.c

Purpose: this AB8500 component implements the central battery charging state machine. It observes battery, btemp, fuel-gauge, AC charger, and USB charger power supplies, exposes `ab8500_chargalg` status/health, and controls charger enable/current/voltage, watchdog kicking, safety timers, end-of-charge, recharge, maintenance charging, and fault states.

Important APIs, types, and functions: core state is `struct ab8500_chargalg`, containing charge status, EOC counter, maintenance flag, hysteresis, current state, charger-current maximization state, charger connection data, battery data, shared BM data, `ux500_charger` pointers for AC/USB, event bits, workqueue/work items, hrtimers, and kobject. Enums define charger type and 26 state/init-state values. Major helpers include timer callbacks, `ab8500_chargalg_state_to()`, charger enable/update/watchdog wrappers, `ab8500_chargalg_stop_charging()`, `hold_charging()`, `start_charging()`, `check_temp()`, `check_charger_voltage()`, `end_of_charge()`, current maximization helpers, external power-supply data collection, `ab8500_chargalg_algorithm()`, periodic/watchdog/instant work functions, and power-supply get_property.

Control flow: probe initializes timers and work, registers power supply `ab8500_chargalg` supplied to `ab8500_fg`, sets `prev_conn_chg = -1` for startup detection, and joins the component framework. Bind creates an ordered workqueue and schedules immediate algorithm execution. Each algorithm pass collects properties from all supplying power supplies, updates event bits and cached charger/battery data, checks EOC/temp/charger voltage/connection, prioritizes fault conditions, then executes the state machine. Normal charging starts the active AC or USB charger with battery-info voltage/current, starts the safety timer, initializes current maximization, and reports charging. Full detection moves to maintenance A/B if supported or waits for recharge. Fault states stop or reduce charging until corresponding event bits clear. Watchdog work periodically kicks the active charger while online.

State and persistence: all algorithm state is volatile. Hrtimers persist pending safety and maintenance deadlines in memory. Battery parameters come from global `ab8500_bm_data.bi`, typically populated from DT by companion setup. Hardware charger state is programmed through `ux500_charger_ops`. Suspend cancels periodic work and watchdog work; resume restarts watchdog if online and queues immediate periodic work.

Dependencies and integration points: this file depends on component framework, hrtimers, workqueues, power supply class, AB8500 MFD data, shared AB8500 BM data, and `struct ux500_charger` ops from `ab8500-chargalg.h`. It assumes external AC/USB power supplies expose `struct ux500_charger` as drvdata and report present/online/health/voltage/current properties. It also consumes battery and btemp/fuel-gauge properties such as capacity, temperature, voltage, average current, instant current, and technology.

Risks: the state machine has many event bits updated opportunistically from external power supplies; missing properties can leave stale data. No explicit mutex protects `di` fields across power-supply callbacks, workqueue, timers, and suspend/resume, relying heavily on ordered work and callback context. Current maximization currently lowers or resets current on collapse/high battery current but does not visibly implement step-up in the read code, so its name may exceed behavior. End-of-charge depends on average current being positive and below threshold for 10 consecutive passes; incorrect sign or missing current data prevents full detection. Because unknown battery charging is controlled by global policy, bad technology reporting can disable charging.

Test signals: exercise state transitions for no charger, AC precedence over USB, normal charge, EOC to maintenance A/B, maintenance timer expiry, recharge restart, battery removed, unknown battery policy, safety timer expiry, watchdog expiry, charger-not-ok, over-voltage, hardware thermal protection, and battery temp low/high/under/over. Verify AC/USB ops receive clamped microvolt/microamp values, watchdog kicks every six seconds while online, suspend/resume cancels and restarts work correctly, and power-supply `STATUS`/`HEALTH` matches events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_chargalg.c -->
