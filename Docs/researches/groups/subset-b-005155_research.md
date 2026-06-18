# Research Report: subset-b-005155

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_charger.c

## Purpose
`ab8500_charger.c` is the AB8500/AB8505 charger-management driver. It exposes AC and USB charger power supplies, controls charger voltage/current registers, handles charger watchdogs and AB8500 hardware errata, and acts as the component master for the AB8500 battery-management stack (`ab8500_fg`, `ab8500_btemp`, and `ab8500_chargalg`).

## Important APIs, Types, And Functions
- `struct ab8500_charger` is the central runtime state: AB8500 parent, ADC channels, VDDADC regulator, AC/USB `ux500_charger` instances, charger flags, USB notifier state, workqueue, locks, and delayed works.
- `struct ab8500_charger_info` stores per-source connection, online, measured voltage/current, CV state, and watchdog-expired state.
- `ab8500_charger_ac_en()` and `ab8500_charger_usb_en()` are the `ux500_charger` enable callbacks used by the charge algorithm. They validate requested voltage/current, set AB8500 registers, manage the LED, VDDADC regulator, and online state.
- `ab8500_charger_set_current()` steps current register values up/down to avoid supply or battery transients. `ab8500_charger_set_vbus_in_curr()` applies USB source, platform, USB-stack, and low-VBAT limits.
- `ab8500_charger_detect_chargers()`, `ab8500_charger_detect_usb_type()`, `ab8500_charger_read_usb_type()`, and `ab8500_charger_max_usb_curr()` detect AC/VBUS presence and map USB link status to allowed input current.
- `ab8500_charger_ac_get_property()` and `ab8500_charger_usb_get_property()` implement power-supply properties for health, present, online, voltage, current, CV state, and USB VBUS collapse.
- `ab8500_charger_probe()` allocates state, gets IIO ADCs and `vddadc`, registers power supplies, requests IRQs, parses battery-management data, registers the USB notifier, and creates the component-master match.
- `ab8500_charger_bind()` creates the ordered workqueue, performs startup charger detection, queues attach/type work, and binds the child battery-management components.

## Control Flow
Probe initializes hardware registers, power-supply descriptors, interrupts, USB notifier, and component matching. Binding creates the workqueue, detects already-present AC/USB sources, and binds the fuel gauge, battery-temperature, and charge-algorithm components.

AC plug/unplug IRQs queue `ac_work`, which re-reads charger status and updates the AC power supply. USB VBUS and USB-link IRQs queue USB detection work. USB link status is decoded into a maximum input current; unrecognized or ACA chargers may delay attach to allow enumeration. USB PHY notifier events update a temporary USB state/current, then delayed work applies configured/suspend/resume/reset behavior.

The charge algorithm calls the `ux500_charger` operations to enable/disable charging, kick the watchdog, re-check abnormal disable, or update output current. Enabling charging writes max voltage, input current, output current, and control registers. Disabling charging clears control/current registers, cancels voltage polling, and handles early AB8500 watchdog errata.

Periodic and delayed work handles VBAT threshold current reduction, hardware-failure recovery checks, USB charger-not-ok polling, thermal-protection status, VBUS drop-end retry, charger-attached debounce, and old AB8500 watchdog kicking.

## State And Persistence
Runtime state is in-memory only. Persistent hardware state is represented by AB8500 registers written during probe, enable/disable, watchdog, backup-battery setup, and USB-current-limit adjustment. `charger_connected`, `charger_online`, `wd_expired`, thermal/failure flags, USB input-current limits, `autopower`, and `vbus_detected` drive user-visible power-supply values. No file-backed persistence exists; suspend flushes/cancels work and resume reschedules needed recovery checks.

## Dependencies And Integration Points
The driver depends on ABX500/AB8500 MFD register access, IIO ADC channels (`main_charger_v`, `main_charger_c`, `vbus_v`, `usb_charger_c`), `vddadc` regulator, USB PHY notifier, platform IRQ names, OF compatible `stericsson,ab8500-charger`, `ab8500_bm_data`, and the `ux500_charger` API from AB8500 charge algorithm code. It supplies `ab8500_chargalg`, `ab8500_fg`, and `ab8500_btemp`, and it registers component drivers for the AB8500 battery-management stack.

## Risks
- `ab8500_charger_ac_check_enable()` calls `ab8500_charger_ac_en(&di->usb_chg, ...)`; the AC enable callback uses `to_ab8500_charger_ac_device_info()`, so passing the USB member can produce an invalid container pointer. This is a high-risk bug in the abnormal AC re-enable path.
- Hardware errata paths are complex: old AB8500 watchdog kicking, no-overshoot bits, VDDADC regulator behavior, invalid charger forcing, and VBUS collapse retry can regress if register ordering or delays change.
- Suspend returns `-EAGAIN` if current stepping is in progress; tests need to cover active step-up/step-down during PM.
- USB current limiting merges platform max, USB enumeration current, link-derived current, low-VBAT derating, and collapse-derived limits. Incorrect precedence can overdraw weak USB sources or undercharge.
- Many IRQ handlers defer state reads to workqueues. Race coverage matters around disconnect while enable, delayed attach, and queued VBUS drop-end work.

## Test Signals
- Probe on AB8500 and AB8505 variants should verify optional AC charger behavior, IIO channel acquisition, IRQ-name coverage, `ab8500_bm_of_probe()` parsing, and component binding.
- Exercise AC and USB plug/unplug IRQs, USB link-status changes, USB PHY current notifications, invalid charger states, ACA wait paths, and startup-with-VBUS-present.
- Validate power-supply properties for health, present, online, current/voltage, CV indicator, watchdog-expired, thermal, not-ok, and VBUS-collapse states.
- Test current stepping boundaries, low-VBAT USB derating around `VBAT_TRESH_IP_CUR_RED`, VBUS collapse retry, and disable paths.
- Suspend/resume tests should cover pending work, active current stepping, watchdog errata, main/USB hardware-failure flags, and VBUS drop-end recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_fg.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_fg.c

## Purpose
`ab8500_fg.c` is the AB8500 fuel-gauge driver. It exposes an `ab8500_fg` battery power supply, estimates capacity using the AB8500 coulomb counter and voltage/OCV tables, handles low-battery and overvoltage interrupts, provides instantaneous-current helpers for sibling AB8500 drivers, and registers as a component in the AB8500 battery-management stack.

## Important APIs, Types, And Functions
- `struct ab8500_fg` stores voltage/current measurements, accumulated charge, capacity state, calibration state, charge/discharge state machines, completions, AB8500 parent, IIO battery-voltage channel, power supply, workqueue, and coulomb-counter lock.
- `struct ab8500_fg_battery_capacity`, `struct ab8500_fg_avg_cap`, and `struct ab8500_fg_cap_scaling` hold filtered and display-scaled capacity state.
- `ab8500_fg_get()` returns the first fuel-gauge instance for sibling drivers such as `ab8500_btemp`.
- `ab8500_fg_inst_curr_start()`, `ab8500_fg_inst_curr_started()`, `ab8500_fg_inst_curr_done()`, `ab8500_fg_inst_curr_finalize()`, and `ab8500_fg_inst_curr_blocking()` provide instantaneous-current measurement using the CCEOC IRQ and completions.
- `ab8500_fg_coulomb_counter()` starts/stops and configures AB8500 coulomb-counter sampling.
- `ab8500_fg_algorithm_charging()`, `ab8500_fg_algorithm_discharging()`, and `ab8500_fg_algorithm_calibrate()` are the main capacity state machines.
- `ab8500_fg_get_property()` exposes voltage, current, energy, charge, capacity, and capacity level.
- `ab8500_fg_external_power_changed()` consumes status/technology/temp from external supplies that supply this battery.
- `ab8500_fg_probe()`, `ab8500_fg_bind()`, `ab8500_fg_unbind()`, and `ab8500_fg_remove()` manage registration and component lifecycle.

## Control Flow
Probe gets the AB8500 parent and `main_bat_v` IIO channel, optional line impedance, creates an ordered workqueue, initializes delayed/instant works, programs low-battery/overvoltage/BATT_OK/power-cut registers, registers the battery power supply, requests fuel-gauge IRQs, disables CCEOC until instantaneous-current reads need it, creates sysfs attributes, marks calibration pending, and adds the instance to the global list.

Component bind initializes capacity from parsed battery info, starts the coulomb counter, and queues the first periodic algorithm pass. External power changes inspect supplying power supplies for battery status, technology, and temperature; status changes switch charging/discharging/full flags and queue algorithm work.

The charging path configures accumulator samples, waits for conversion completion or `force_full`, integrates accumulated charge, clamps to design capacity, refreshes voltage/current, and checks reporting thresholds. The discharging path starts with voltage-based initialization, recovery detection, low/high-current mode selection, coulomb-counter integration during high-current discharge, and voltage-based capacity in low-current or wakeup paths. Calibration uses AB8500 internal offset calibration registers and IRQ completion.

Interrupts either complete instantaneous-current waits, queue accumulator reads, queue low-battery debounce, or queue overvoltage recovery checks. PM suspend flushes work and may disable the fuel gauge when not charging; resume moves non-charging systems into wakeup recalculation.

## State And Persistence
Capacity, filtering windows, scaling data, low-battery counters, and algorithm state are in RAM. User writes to the custom `battery/charge_now` sysfs attribute can inject a user capacity that is accepted only within configured limits; `charge_full` can update maximum mAh. Hardware state is maintained through AB8500 gas-gauge, RTC, charger, low-battery, BATT_OK, and AB8505 power-cut registers. There is no durable storage, so estimates are rebuilt from voltage/current and battery info after probe.

## Dependencies And Integration Points
The driver depends on ABX500 register APIs, AB8500 register definitions, IIO `main_bat_v`, `ab8500_bm_data`, power-supply battery-info OCV/resistance helpers, component framework, and AB8500 IRQ names (`NCONV_ACCU`, `BATT_OVV`, `LOW_BAT_F`, `CC_INT_CALIB`, `CCEOC`). It supplies `ab8500_chargalg` and `ab8500_usb`, and gets charging status, battery technology, and temperature from external power supplies. Public helper declarations are in `ab8500-bm.h`.

## Risks
- Instantaneous-current helpers keep `cc_lock` locked across start/finalize and temporarily enable CCEOC IRQ. Callers must always finalize or unwind correctly, or the coulomb counter and IRQ state can be left inconsistent.
- Capacity estimation mixes coulomb-counter integration, voltage compensation, OCV tables, line impedance, current thresholds, and display scaling; small unit or sign mistakes can cause user-visible capacity jumps.
- Low-battery handling deliberately reports 0% only after IRQ/debounce, while other calculations clamp to at least 1%; shutdown behavior depends on this distinction.
- Several sysfs writes return `count` even after invalid input paths in AB8505 power-cut attributes, which can hide rejected settings from userspace.
- The global list and `ab8500_fg_get()` assume the first instance is the primary fuel gauge; multi-instance behavior is only lightly supported.

## Test Signals
- Validate property reads for normal, full, unknown-battery, overvoltage, low-battery, charging, and discharging states.
- Exercise CCEOC two-stage completion, timeout paths, accumulator conversion IRQs, calibration IRQ, and disabling CCEOC after reads.
- Simulate external power-supply status transitions: discharging, charging, full, not charging, battery technology known/unknown, and temperature updates.
- Test low-current and high-current discharge transitions, recovery timing, startup initialization, wake-from-suspend recalculation, and capacity scaling around maintenance/full.
- Verify AB8505 power-cut sysfs attributes read/write correct registers and reject out-of-range values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_fg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/acer_a500_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/acer_a500_battery.c

## Purpose
`acer_a500_battery.c` is a platform battery driver for the Acer Iconia Tab A500. It reads battery telemetry from the parent embedded-controller regmap named `KB930`, exposes it through the power-supply class, and polls capacity periodically to emit change notifications.

## Important APIs, Types, And Functions
- `struct a500_battery` stores delayed polling work, registered `power_supply`, parent EC `regmap`, and cached capacity.
- `ec_data[]` maps EC registers to `POWER_SUPPLY_PROP_CAPACITY`, `VOLTAGE_NOW`, `CURRENT_NOW`, `CHARGE_FULL_DESIGN`, and `TEMP`.
- `a500_battery_update_capacity()` reads and clamps capacity to 100%.
- `a500_battery_get_status()` derives charging/discharging/full from cached capacity and `power_supply_am_i_supplied()`.
- `a500_battery_unit_adjustment()` converts EC units to power-supply units: mV/mA/mAh-style values to micro units, Kelvin deci-units to Celsius deci-degrees, and presence to boolean.
- `a500_battery_get_property()` serves all exposed properties.
- `a500_battery_poll_work()` polls capacity every 30 seconds and calls `power_supply_changed()` only when capacity changes.

## Control Flow
Probe allocates state, gets the parent `KB930` regmap, registers the `ec-battery` power supply using the parent firmware node, initializes delayed polling, and schedules the first poll after one second. Property reads either return derived status/technology/capacity or read an EC register and apply unit conversion. Remove and suspend cancel the delayed work; resume restarts it.

## State And Persistence
The only driver-owned state is cached capacity and the delayed-work schedule. All persistent telemetry is owned by the EC. The driver does not write EC registers and does not persist capacity across reprobe. Presence is inferred from the design-capacity register being non-zero.

## Dependencies And Integration Points
The driver depends on a parent platform device exposing `dev_get_regmap(parent, "KB930")`, the power-supply framework, firmware-node propagation from the parent, and external supplies for `power_supply_am_i_supplied()`. It registers as platform driver alias `acer-a500-iconia-battery`.

## Risks
- If the EC returns transient register-read errors, property reads return `-ENODATA`; polling silently ignores failed capacity updates.
- Status is derived from cached capacity, so a stale cached value after read failures can affect full/charging/discharging reporting.
- Presence uses `CHARGE_FULL_DESIGN` as a proxy. A malformed EC value can make a disconnected battery appear present or hide a connected one.
- Unit conversion assumes specific EC units; a parent regmap variant with different units would report incorrect values.

## Test Signals
- Mock regmap reads for all EC registers, including failed reads, capacity over 100%, zero design capacity, and temperature conversion.
- Verify poll work emits `power_supply_changed()` only on capacity changes and is canceled/restarted across suspend/resume/remove.
- Exercise supplied/not-supplied status with capacity below 100 and full status at 100.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/acer_a500_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/act8945a_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/act8945a_charger.c

## Purpose
`act8945a_charger.c` is a power-supply driver for the Active-semi ACT8945A PMIC charger. It reports charger status, charge type, battery health, capacity level, maximum current, model, and manufacturer from PMIC registers and optional GPIOs, and updates supply type on IRQ-driven state changes.

## Important APIs, Types, And Functions
- `struct act8945a_charger` stores the `power_supply`, mutable descriptor, parent regmap, IRQ work, init gate, and optional `lbo`/`chglev` GPIOs.
- `act8945a_get_charger_state()`, `act8945a_get_charge_type()`, `act8945a_get_battery_health()`, `act8945a_get_capacity_level()`, and `act8945a_get_current_max()` decode PMIC status/config/state registers into power-supply properties.
- `act8945a_enable_interrupt()` enables charger, input, temperature, and timer interrupt outputs and clears/arms status bits.
- `act8945a_set_supply_type()` mutates `desc.type` between mains, USB, and battery based on input-present and ACIN state.
- `act8945a_status_changed()` schedules work after initialization; `act8945a_work()` refreshes supply type and calls `power_supply_changed()`.
- `act8945a_charger_config()` reads DT properties, claims GPIOs, requests the LBO GPIO IRQ, and programs charger OVP/precondition/total timeout bits.

## Control Flow
Probe gets the parent regmap, configures charger registers from OF properties, obtains the main PMIC IRQ, initializes the descriptor and current supply type, registers the power supply, requests the PMIC IRQ, initializes work, enables charger interrupts, and sets `init_done`. IRQs from the PMIC and optional low-battery GPIO schedule work that refreshes descriptor type and notifies userspace.

Property reads synchronously read ACT8945A registers and optional GPIO levels. Charge state bits select charging, full, not charging, discharging, charge type, and current limit. Health distinguishes suspended charging, input present with temp/timer/overvoltage fault, and good states.

## State And Persistence
Driver state is minimal: `init_done`, mutable `desc.type`, GPIO descriptors, and pending work. Hardware configuration is persisted in ACT8945A registers until reset: OVP threshold, precondition timeout, total timeout, suspended-charging preservation, and interrupt enables. No software persistence exists.

## Dependencies And Integration Points
The driver depends on a parent regmap for ACT8945A registers, OF properties (`active-semi,input-voltage-threshold-microvolt`, `active-semi,precondition-timeout`, `active-semi,total-timeout`), optional GPIOs (`active-semi,lbo`, `active-semi,chglev`), `of_irq_get()`, and the power-supply framework.

## Risks
- `devm_gpiod_get_optional()` may return `NULL`, but the code calls `gpiod_to_irq(charger->lbo_gpio)` and `gpiod_get_value()` paths without explicit NULL handling for optional GPIO absence.
- The descriptor `type` is mutated at runtime. Consumers that cache type may not observe changes as expected, and tests should confirm power-supply core behavior.
- `act8945a_set_supply_type()` is declared `unsigned int` but returns negative regmap errors; this type mismatch can obscure failures.
- Health decoding collapses several disabled/input-present states into overheat, safety timer, or overvoltage based on status bits; incorrect PMIC bit interpretation would mislead charging policy.
- LBO IRQ request failures are logged as info and ignored, reducing notification quality without failing probe.

## Test Signals
- Regmap tests for each charger state: disabled, EOC with/without CHGDAT, fast, precharge, input present/absent, temp fault, timer fault, and suspended charging.
- GPIO tests for LBO and CHGLEV combinations in capacity-level and current-max calculations.
- Probe tests for DT defaults and all supported OVP/precondition/total-timeout values.
- IRQ tests should verify no notifications before `init_done`, work scheduling after PMIC/LBO IRQs, and clean `cancel_work_sync()` on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/act8945a_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/adc-battery-helper.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/adc-battery-helper.c

## Purpose
`adc-battery-helper.c` is a reusable helper for simple ADC/fuel-gauge drivers that can measure battery voltage and current accurately but need software OCV/capacity estimation. It exports common power-supply properties, polling work, status/capacity calculation, internal-resistance adaptation, external-power handling, and suspend/resume helpers.

## Important APIs, Types, And Functions
- `adc_battery_helper_properties[]` exports the common property list: status, voltage now, voltage OCV, current now, capacity, present, and scope.
- `adc_battery_helper_init()` wires the helper to a registered power supply, a combined voltage/current getter, optional charge-finished GPIO, validates battery-info requirements, seeds internal resistance, and starts polling.
- `adc_battery_helper_work()` is the core polling loop: samples voltage/current, computes OCV, updates moving averages, determines supplied/status/capacity, optionally updates internal resistance, reschedules itself, and notifies on status changes.
- `adc_battery_helper_get_property()` returns helper-backed properties while holding the helper mutex and calls the driver getter for fresh `VOLTAGE_NOW`/`CURRENT_NOW`.
- `adc_battery_helper_external_power_changed()` accelerates the next poll after a settle delay.
- `adc_battery_helper_suspend()` and `adc_battery_helper_resume()` stop and restart helper work.

## Control Flow
Initialization validates that `battery_info` contains factory internal resistance, constant charge voltage, and an OCV table. It seeds the resistance moving average from battery info and immediately starts work. The work function samples current and voltage via the driver callback, estimates OCV as `volt - current * resistance`, averages OCV over an eight-sample window, reads supplied state, computes status, computes capacity from OCV unless full, then uses current/voltage deltas to refine internal resistance when conditions are suitable. It polls every five seconds for the initial 30 polls, then every 30 seconds.

## State And Persistence
State is held in `struct adc_battery_helper`: OCV and resistance moving-average arrays, indexes, poll counters, current voltage/current, capacity, status, and supplied flag. There is no persistent storage; all estimates restart from battery-info factory resistance on probe/resume. Work is devm-managed and canceled automatically on device teardown.

## Dependencies And Integration Points
The helper depends on the power-supply framework, `power_supply_batinfo_ocv2cap()`, `power_supply_am_i_supplied()`, optional charge-finished GPIO, `system_percpu_wq`, devm mutex/work helpers, and a client-supplied `get_voltage_and_current_now()` callback. Known users in the same directory include `ug3105_battery.c` and `intel_dc_ti_battery.c`.

## Risks
- The header requires `struct adc_battery_helper` to be the first member of client driver data when using callbacks directly; violating this causes invalid casts in get-property and PM helpers.
- The helper calls the client getter under `help->lock`; client callbacks must avoid re-entering helper property paths or creating lock inversions.
- OCV calculation assumes current sign and resistance units match helper expectations. A client with reversed current polarity will bias capacity.
- Internal resistance adaptation relies on current/voltage deltas and outlier rejection. Devices with noisy ADCs may never update resistance or may drift slowly.
- Work reschedules even after a sample read failure, but notification only tracks status changes, not capacity changes; clients needing capacity-change uevents may need extra signaling.

## Test Signals
- Unit-style tests with fake getter values should cover charging, discharging, not charging, full via GPIO, full via OCV threshold, low-battery resistance-skip, charger plug/unplug skip, and getter failures.
- Validate moving average behavior for OCV and resistance windows, initial fast polling versus steady polling, and external-power settle timing.
- Probe validation should fail when battery-info resistance, constant charge voltage, or OCV table is absent.
- Confirm suspend cancels work and resume restarts with reset OCV averaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/adc-battery-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/adc-battery-helper.h -->
# sources/distributed-fs/ceph-client/drivers/power/supply/adc-battery-helper.h

## Purpose
`adc-battery-helper.h` declares the public interface and state structure for the ADC battery helper. It lets simple battery drivers embed the helper, expose the standard helper-backed property list, and reuse common get-property, external-power, and PM callbacks.

## Important APIs, Types, And Functions
- `ADC_BAT_HELPER_MOV_AVG_WINDOW_SIZE` fixes OCV and internal-resistance moving-average windows at eight samples.
- `adc_battery_helper_get_func` is the required combined voltage/current callback. The combined callback is intentional so clients can sample voltage and current close together.
- `struct adc_battery_helper` contains the power-supply pointer, optional charge-finished GPIO, delayed work, mutex, callback, OCV/resistance sample arrays, poll counters/indexes, last voltage/current, capacity, status, and supplied flag.
- `adc_battery_helper_properties[]` and `ADC_HELPER_NUM_PROPERTIES` describe the exported property list contract.
- `adc_battery_helper_init()`, `adc_battery_helper_get_property()`, `adc_battery_helper_external_power_changed()`, `adc_battery_helper_suspend()`, and `adc_battery_helper_resume()` are the exported helper functions.

## Control Flow
Client drivers embed `struct adc_battery_helper`, register their power supply, call `adc_battery_helper_init()`, and either use the helper callbacks directly or delegate selected properties to them. The PM and property helpers assume they can retrieve the helper from driver data.

## State And Persistence
The header defines only in-memory state. Persistence is left to the client device and battery-info firmware data. The moving average arrays and counters are reset by helper initialization/resume logic in the C file.

## Dependencies And Integration Points
The header forward-declares `struct power_supply` and `struct gpio_desc`, includes mutex and workqueue types, and relies on power-supply property enums through users including power-supply headers before or through the C implementation. It is intended for local power-supply drivers in the same subsystem.

## Risks
- The comment states the helper must be the first member of client data for direct callback use. This is an ABI-like layout contract not enforced by the compiler.
- `ADC_HELPER_NUM_PROPERTIES` must stay synchronized with `adc_battery_helper_properties[]`; the C file uses `static_assert()` to catch mismatches.
- The callback signature uses plain `int *volt` and `int *curr`; clients must honor microvolt and microampere units expected by the implementation.

## Test Signals
- Build coverage catches property-count mismatches through the C file static assertion.
- Client-driver tests should verify driver data layout, unit conventions, and direct callback use for get-property and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/adc-battery-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/adp5061.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/adp5061.c

## Purpose
`adp5061.c` is an I2C power-supply driver for the Analog Devices ADP5061 programmable linear battery charger. It exposes charger status and capacity-level information, plus writable charger configuration properties for input current limit, voltage thresholds, charge voltage/current, precharge current, weak threshold, and termination current.

## Important APIs, Types, And Functions
- `struct adp5061_state` stores the I2C client, regmap, and registered power supply.
- Register/bit macros define ADP5061 configuration and status fields.
- Lookup tables map register indexes to current/voltage values for input current, termination voltage, charge current, weak/min voltage thresholds, precharge current, and end current.
- `adp5061_get_array_index()` selects the nearest lower supported table index for a requested value.
- `adp5061_get_status()` bulk-reads adjacent status registers.
- Per-property helpers (`adp5061_get_input_current_limit()`, `adp5061_set_input_current_limit()`, `adp5061_get_max_voltage()`, `adp5061_set_max_voltage()`, etc.) translate between power-supply units and register fields.
- `adp5061_get_property()`, `adp5061_set_property()`, and `adp5061_prop_writeable()` implement the power-supply contract.
- `adp5061_probe()` creates an 8-bit regmap over I2C and registers the `adp5061` USB-type power supply.

## Control Flow
Probe allocates state, initializes regmap, stores client data, and registers the power supply. There is no IRQ or polling path; all status/configuration is read or written synchronously through power-supply property callbacks. Read callbacks query status or config registers and map hardware codes to power-supply enums/units. Write callbacks clamp or quantize requested values to supported table entries and call `regmap_update_bits()`.

## State And Persistence
The driver keeps no cached charger state. Hardware registers are the source of truth and preserve configuration until chip reset or external change. Software state is limited to regmap and power-supply handles.

## Dependencies And Integration Points
The driver depends on I2C, regmap, power-supply class, and the `adp5061` I2C device ID. The power supply is typed as USB and exposes standard charger properties. It has no OF match table in this file, only an I2C ID table.

## Risks
- `adp5061_get_chg_type()` returns `POWER_SUPPLY_STATUS_UNKNOWN` for out-of-range charge-type values, which is a status enum used as a charge-type value; this can confuse userspace.
- Table quantization always rounds down to the prior supported value. This is conservative for current/voltage limits but should be documented in tests.
- Several status enum states beyond the first four are collapsed to unknown or discharging; LDO mode and battery-detection behavior may need more precise mapping.
- No IRQ handling means userspace relies on polling property files or external notifications.
- The file has no remove-specific behavior because devm resources are used; this is fine but leaves no explicit hardware shutdown.

## Test Signals
- Regmap tests for every readable/writable property should verify unit conversion, masking, clamping at max voltage/current, and nearest-lower table selection.
- Status tests should cover no battery, battery monitor off, critical/low/normal battery status, charging phases, complete, timer expiry, LDO mode, and unknown values.
- Writeability tests should match exactly the properties accepted by `adp5061_set_property()`.
- Probe tests should cover regmap initialization failure and power-supply registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/adp5061.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/apm_power.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/apm_power.c

## Purpose
`apm_power.c` bridges the power-supply subsystem to legacy APM emulation. It selects a main battery, converts power-supply status/capacity/time properties into `struct apm_power_info`, and installs itself as the global `apm_get_power_status` callback.

## Important APIs, Types, And Functions
- `main_battery` caches the selected power supply during a status query; `apm_mutex` serializes selection and reporting.
- `struct find_bat_param` tracks explicit `use_for_apm`, maximum charge battery, maximum energy battery, and fallback battery candidates.
- `find_main_battery()` and `__find_main_battery()` select the reporting battery, preferring `desc->use_for_apm`, then largest charge/energy capacity, then a fallback last battery.
- `do_calculate_time()` computes minutes to full/empty from energy, charge, or voltage quantities and current.
- `calculate_time()` tries energy, charge, then voltage sources.
- `calculate_capacity()` computes percent from energy, charge, or voltage full/empty/current values.
- `apm_battery_apm_get_power_status()` fills APM AC line status, battery status/flag/life, time units, and time remaining.

## Control Flow
Module init assigns `apm_get_power_status`. Each APM query locks the mutex, scans registered power supplies for a main battery, reads status, derives AC line state, gets or computes capacity, maps capacity/status to APM battery status, and obtains time from native time-to-full/empty properties or calculated fallbacks. Module exit clears the global callback if it is still installed.

## State And Persistence
There is no persistent state. `main_battery` is recalculated on each query under `apm_mutex`, so hotplugged batteries can be reflected. The global callback pointer is process-wide kernel state changed at module load/unload.

## Dependencies And Integration Points
The file depends on `linux/apm-emulation.h`, the power-supply class, and power-supply drivers exposing standard battery properties. It is a compatibility layer rather than a hardware driver.

## Risks
- Selection heuristics can choose an arbitrary battery when several batteries expose incomplete or incomparable energy/charge data.
- Calculations assume compatible units and signs across current, energy, charge, and voltage properties. Incorrect current sign can invert time estimates.
- `do_calculate_time()` uses `POWER_SUPPLY_PROP_CHARGE_EMPTY` as the fallback design property in the energy path, which looks suspicious and may reduce fallback accuracy.
- Capacity/time fallbacks may return `-1`; downstream APM consumers must tolerate unknown values.
- The global `apm_get_power_status` hook can conflict with another provider if load ordering changes, though exit only clears if it still owns the hook.

## Test Signals
- Use fake power supplies to cover explicit `use_for_apm`, largest charge, largest energy, mixed charge/energy with voltage comparison, and no battery.
- Verify APM mappings for charging, not charging, full, discharging, unknown status, high/low/critical thresholds, and AC line state.
- Exercise native time-to-full/empty paths and calculated energy/charge/voltage fallback paths, including zero current and missing properties.
- Module unload should leave `apm_get_power_status` untouched if another provider replaced it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/apm_power.c -->
