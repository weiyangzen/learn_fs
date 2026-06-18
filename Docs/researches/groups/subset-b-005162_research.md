# subset-b-005162 grouped research

Work item `subset-b-005162` covers Linux power-supply framework files and hardware drivers under `sources/distributed-fs/ceph-client/drivers/power/supply/`. Each section preserves the source path and is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/mt6360_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/mt6360_charger.c

## Purpose
MT6360 charger support registers a USB-type power supply plus an OTG VBUS regulator for the MediaTek/Richtek MT6360 PMU charger block. It exposes charger online/status/type and tunable current/voltage limits through the generic `power_supply` API while driving hardware through the parent MFD regmap.

## Important APIs, Types, and Functions
`struct mt6360_chg_info` owns the device, regmap, copied `power_supply_desc`, regulator device, BC1.2 detection state, USB type cache, and charger-detect work item. Linear charge ranges are encoded in `mt6360_chg_range` and used by getter/setter helpers. Important entry points are `mt6360_charger_probe()`, `mt6360_chg_init_setting()`, `mt6360_chg_irq_register()`, `mt6360_charger_get_property()`, `mt6360_charger_set_property()`, `mt6360_pmu_attach_i_handler()`, and `mt6360_handle_chrdet_ext_evt()`.

## Control Flow
Probe allocates state, initializes `chgdet_lock`, creates autocancel work, reads optional `richtek,vinovp-microvolt`, obtains the parent regmap, applies charger defaults, registers the power supply, registers `attach_i` and `chrdet_ext_evt` IRQs, registers the OTG regulator, then schedules an initial charger-detect work pass. Property reads translate regmap fields into power_supply values. Property writes update the force-sleep bit, charge current, regulation voltage, input current, MIVR, precharge current, or termination current. VBUS events enable or disable BC1.2 detection; attach IRQs decode `USB_STATUS1` and update `psy_usb_type`.

## State and Persistence
State is volatile driver memory plus hardware registers. `pwr_rdy`, `bc12_en`, and `psy_usb_type` cache interrupt-derived state and are protected by `chgdet_lock`. Hardware settings persist only as programmed PMU register values until reset or driver reconfiguration. There is no disk persistence.

## Dependencies and Integration Points
The driver depends on platform/MFD instantiation, parent `regmap`, `linux/power_supply.h`, regulator framework regmap ops, device properties, IRQ names `attach_i` and `chrdet_ext_evt`, and `devm_work_autocancel`. The power-supply descriptor exposes USB type availability for sysfs formatting in `power_supply_sysfs.c`. The OTG regulator is matched as `usb-otg-vbus-regulator`.

## Risks and Test Signals
Risk areas include register field mistakes, especially `mt6360_charger_set_mivr()` updating `MT6360_PMU_CHG_CTRL3` with `MT6360_VMIVR_MASK` while the getter reads `CHG_CTRL6`; BC1.2 race handling around detach/attach; and IRQ trigger assumptions. Test by probing with a DT node, checking sysfs values for online/status/usb_type, writing current/voltage limit attributes, validating VBUS attach/detach uevents, confirming regulator enable/voltage control, and fault-injecting regmap/IRQ failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/mt6360_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/mt6370-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/mt6370-charger.c

## Purpose
The MT6370 charger driver exposes a USB charger power supply and an OTG VBUS regulator for MediaTek/Richtek MT6370 hardware. It manages BC1.2 attach detection, charger limit programming, MIVR recovery behavior, and ADC-assisted charger fault workarounds.

## Important APIs, Types, and Functions
`struct mt6370_priv` stores regmap fields, IIO ADC channels, ordered workqueue, BC1.2 work, MIVR delayed work, IRQ numbers, attach state, USB type, and power-supply/regulator handles. `mt6370_chg_fields` maps logical fields to `regmap_field` definitions and optional `linear_range` converters. Main functions include `mt6370_chg_probe()`, `mt6370_chg_init_rmap_fields()`, `mt6370_chg_init_setting()`, `mt6370_chg_get_property()`, `mt6370_chg_set_property()`, `mt6370_chg_bc12_work_func()`, `mt6370_chg_pwr_rdy_check()`, `mt6370_mivr_handler()`, and `mt6370_chg_mivr_dwork_func()`.

## Control Flow
Probe gets the parent regmap, allocates all regmap fields, obtains all IIO ADC channels, registers the OTG regulator, registers the power supply, creates the attach mutex and ordered workqueue, sets up work items, initializes hardware, requests three named IRQs, then samples power-ready state. UVP events call `mt6370_chg_pwr_rdy_check()`, which feeds `POWER_SUPPLY_PROP_ONLINE` back into the driver's setter. The setter updates `attach` and queues BC1.2 work. Attach IRQs mark BC1.2 complete and queue work to decode USB type. MIVR IRQs hold a wake reference, mask the IRQ, delay 200 ms, read MIVR state and IBUS, optionally toggle CFO, then re-enable IRQ.

## State and Persistence
Driver state is volatile and guarded by `attach_lock` for attach/USB-type transitions. Regmap fields hold current hardware configuration. Workqueue ordering serializes BC1.2 state transitions. There is no persistent storage, but DT/regulator settings and hardware register defaults are reapplied on probe.

## Dependencies and Integration Points
The driver integrates with regmap, regmap_field, IIO, regulator, GPIO parsing for an optional OTG enable GPIO, power_supply, platform IRQs, and workqueues. It exports USB type values to the core sysfs layer and uses `power_supply_changed()` for notification propagation.

## Risks and Test Signals
Risk areas include property-map/range mistakes, MIVR IRQ masking not being restored on unexpected paths, reliance on ordered workqueue lifetime, IIO channel indexing, and BC1.2 state loops through `power_supply_set_property()`. Tests should exercise attach/detach, SDP/CDP/DCP detection, writable limit attributes, OTG regulator voltage/current/enable behavior, MIVR IRQ handling under low IBUS, and probe deferral/error paths for regmap/IIO/IRQ resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/mt6370-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/olpc_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/olpc_battery.c

## Purpose
This driver exposes OLPC XO AC and battery information from the OLPC embedded controller through the generic power_supply class. It supports older and newer EC protocols, XO-1 and XO-1.5 battery property sets, raw EEPROM access, EC error visibility, and EC wake sources for suspend.

## Important APIs, Types, and Functions
`struct olpc_battery_data` stores the AC and battery power supplies, serial buffer, and protocol endian flags. AC status comes from `olpc_ac_get_prop()`. Battery helpers include `olpc_bat_get_status()`, `olpc_bat_get_health()`, `olpc_bat_get_mfr()`, `olpc_bat_get_tech()`, design-charge/voltage helpers, `ecword_to_cpu()`, and `olpc_bat_get_property()`. Probe and PM entry points are `olpc_battery_probe()` and `olpc_battery_suspend()`.

## Control Flow
Probe allocates state, queries `EC_FIRMWARE_REV`, derives protocol flags from DT and EC revision, checks battery status once, registers `olpc_ac`, selects XO-1 or XO-1.5 battery property arrays, then registers `olpc_battery` with extra sysfs groups. Every battery property read first fetches EC battery status, rejects most properties if no battery is present, and then issues specific `olpc_ec_cmd()` calls for voltage, current, SOC, temperature, ACR, EEPROM manufacturer/type, serial, or error code. Suspend maps power-supply wakeup settings onto EC SCI wake sources.

## State and Persistence
The driver caches only the serial string and protocol flags. Battery measurements, presence, health, and AC status are read live from the EC. The binary `eeprom` sysfs file reads directly from EC EEPROM address range 0x20-0x7f and does not cache. There is no write path or persistent kernel-side state.

## Dependencies and Integration Points
It depends on `olpc_ec_cmd()`, `olpc_ec_wakeup_*()` helpers, Open Firmware compatibles `olpc,xo1-battery`, `olpc,xo1.5-battery`, and `olpc,xo1.75-ec`, and the power_supply core. Extra attributes are attached through `power_supply_config.attr_grp`.

## Risks and Test Signals
Risks include EC protocol/revision mismatches, endian conversion mistakes, stale EC last-known data after battery removal, and global mutation of the static `olpc_bat_desc` property pointer during probe. Tests should verify EC command scaling formulas, absent-battery behavior returning `-ENODEV`, XO-1 vs XO-1.5 property visibility, EEPROM/error sysfs reads, wakeup source programming in suspend, and old EC revision rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/olpc_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/pf1550-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/pf1550-charger.c

## Purpose
The PF1550 charger driver registers separate mains charger and battery power supplies for NXP/Freescale PF1550 PMIC charger hardware. It exposes online, battery status, charge type, health, presence, model, and manufacturer while configuring safe charger defaults from DT and monitored-battery data.

## Important APIs, Types, and Functions
`struct pf1550_charger` owns the parent PF1550 data, two power-supply handles, delayed work items for VBUS/charger/battery sense events, IRQ numbers, and configured voltage/current/thermal limits. Key helpers are `pf1550_get_charger_state()`, `pf1550_get_charge_type()`, `pf1550_get_battery_health()`, `pf1550_get_present()`, `pf1550_get_online()`, the three delayed work handlers, `pf1550_charger_irq_handler()`, `pf1550_charger_get_property()`, `pf1550_dt_parse_dev_info()`, `pf1550_reg_init()`, and `pf1550_charger_probe()`.

## Control Flow
Probe obtains parent MFD data/regmap, creates autocancel delayed work items, registers `pf1550-charger` and `pf1550-battery`, requests five platform IRQs, parses DT/default battery info, then initializes registers. IRQs are classified by stored virtual IRQ array and either log immediate conditions or schedule delayed sensing. Sensing work reads status registers, logs decoded charger/battery/VBUS events, and calls `power_supply_changed()` on VBUS attach/detach paths.

## State and Persistence
Runtime state is in the PF1550 registers and the `pf1550_charger` configuration fields. DT properties `nxp,min-system-microvolt` and `nxp,thermal-regulation-celsius`, plus `monitored-battery` constant charge voltage, are applied at probe. No userspace write path is provided.

## Dependencies and Integration Points
The driver depends on the PF1550 MFD header/regmap definitions, platform IRQ ordering, `power_supply_get_battery_info()`, and `devm_delayed_work_autocancel()`. It uses common sysfs/power_supply formatting for two descriptors and relies on the core for property visibility and uevents.

## Risks and Test Signals
Risk areas include exact PF1550 status-code mapping, delayed-work notification asymmetry, validation of supported voltage/thermal settings, and `power_supply_get_battery_info()` handling: `pf1550_reg_init()` turns charging on when battery info lookup fails, which should be checked against platform expectations. Tests should cover DT bounds, monitored battery data, IRQ scheduling, register write errors, status/health/presence sysfs values, and VBUS uevents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/pf1550-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/pm8916_bms_vm.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/pm8916_bms_vm.c

## Purpose
This Qualcomm PM8916 VM-BMS driver exposes a simple battery power supply backed by the PMIC voltage-monitoring BMS block. It reports status, health, current battery voltage, and last open-circuit voltage while working around hardware state-machine limitations during suspend/resume.

## Important APIs, Types, and Functions
`struct pm8916_bms_vm_battery` stores the device, battery power supply, battery info, regmap/base register, last OCV/time, and current VBAT. Important functions are `pm8916_bms_vm_battery_probe()`, `pm8916_bms_vm_battery_get_property()`, `pm8916_bms_vm_fifo_update_done_irq()`, `pm8916_bms_vm_battery_suspend()`, and `pm8916_bms_vm_battery_resume()`.

## Control Flow
Probe gets the parent regmap and `reg` base, validates peripheral type, configures S1/S2 sample intervals and FIFO length, enables BMS, reads boot/resume OCV, registers the battery power supply, loads monitored-battery info, and requests the `fifo` IRQ. FIFO IRQ reads two voltage samples, uses the last sample as VBAT scaled by 300 uV units, then sends `power_supply_changed()`. Status is derived from `power_supply_am_i_supplied()`. Suspend unlocks secure access and forces S3 OCV/sleep mode; resume reads fresh OCV and returns hardware to normal mode.

## State and Persistence
`last_ocv` and `last_ocv_time` are cached in RAM and invalidated for property reads after 180 seconds. `vbat_now` is updated by FIFO IRQs. Battery design bounds come from `power_supply_get_battery_info()` and are used to derive health. No persistent storage is written.

## Dependencies and Integration Points
The file depends on Qualcomm SPMI/regmap peripheral layout, a `qcom,pm8916-bms-vm` DT node with `reg`, `monitored-battery`, a named `fifo` IRQ, power_supply supplier relationships, and platform suspend/resume callbacks.

## Risks and Test Signals
Risks include endian/width assumptions in `regmap_bulk_read()` into `u16`/`unsigned int`, stale OCV exposure, missing error handling after resume OCV read before using `tmp`, and health decisions when battery-info voltage fields are absent. Tests should validate peripheral type rejection, FIFO voltage scaling, OCV expiry, supplier-derived charging status, suspend/resume register writes, and IRQ-triggered uevents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/pm8916_bms_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/pm8916_lbc.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/pm8916_lbc.c

## Purpose
The PM8916 LBC driver controls the Qualcomm linear battery charger and exposes it as a USB power supply. It configures charger-safe voltage/current limits, reports USB online state and programmed charge limits, allows runtime charge current writes, and mirrors USB VBUS state through extcon.

## Important APIs, Types, and Functions
`struct pm8916_lbc_charger` stores extcon, charger power supply, battery info, regmap, four peripheral base registers, online state, and charge limit fields. Core functions are `pm8916_lbc_charger_probe()`, `pm8916_lbc_charger_probe_dt()`, `pm8916_lbc_charger_configure()`, `pm8916_lbc_charger_get_property()`, `pm8916_lbc_charger_set_property()`, and `pm8916_lbc_charger_state_changed_irq()`.

## Control Flow
Probe reads four `reg` entries, validates CHGR/BAT_IF/USB/MISC peripheral types, checks charger option, parses safe voltage/current DT values and writes safe registers, registers the power supply, loads battery info, allocates/registers extcon, requests `usb_vbus` IRQ, reads initial VBUS state, and configures charger max voltage/current from battery info and safe limits. IRQ reads USB real-time status, updates `online`, syncs extcon `EXTCON_USB`, and emits `power_supply_changed()`. The only writable property is constant charge current.

## State and Persistence
Online state and configured limits are cached in memory and reflected in PMIC registers. DT properties `qcom,fast-charge-safe-voltage` and `qcom,fast-charge-safe-current` define upper bounds; monitored-battery voltage sets the requested maximum. State is not persisted beyond PMIC/register lifetime.

## Dependencies and Integration Points
Dependencies include parent regmap, extcon provider, named IRQ `usb_vbus`, DT `reg` array of four peripheral bases, safe charge DT properties, monitored battery data, and the power_supply class. Extcon creates a secondary integration path for USB cable state.

## Risks and Test Signals
Risk areas include register type/order assumptions, clamping math for current/voltage, ignoring `dev_err_probe()` return when an external charger is detected, and proceeding after DT parse errors because probe logs but does not return on `pm8916_lbc_charger_probe_dt()` failure. Tests should cover type mismatch, invalid DT bounds, current write clamping, extcon/online updates, initial VBUS read, and register write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/pm8916_lbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/pmu_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/pmu_battery.c

## Purpose
This legacy Apple PMU battery driver exposes PMU AC status and one power_supply battery per PMU battery slot. It adapts global PMU battery structures into standard power_supply properties.

## Important APIs, Types, and Functions
`struct pmu_battery_dev` embeds a dynamic descriptor, pointer to `struct pmu_battery_info`, name buffer, and registered power supply. Main functions are `pmu_bat_init()`, `pmu_bat_exit()`, `pmu_get_ac_prop()`, `pmu_bat_get_model_name()`, and `pmu_bat_get_property()`.

## Control Flow
Module init creates a synthetic platform device, registers `pmu-ac`, then loops over `pmu_battery_count` to allocate per-battery descriptors named `PMU_battery_N` and register each battery power supply. Property reads directly inspect global `pmu_power_flags` and per-slot `pmu_batteries[]`. Exit unregisters all registered batteries, frees wrappers, unregisters AC, and removes the platform device.

## State and Persistence
The driver keeps per-registration wrapper objects in the `pbats` array. Battery values are live global PMU state maintained outside this file. No persistent storage or hardware programming is performed here.

## Dependencies and Integration Points
It depends on classic PowerMac PMU/ADB globals and constants from `linux/pmu.h`, platform device helpers, and the power_supply core. It uses non-devm registration because it is module-init based.

## Risks and Test Signals
Risk areas include partial registration cleanup when allocation stops early, assuming global PMU arrays are valid for module lifetime, and reporting AC online when no batteries exist. Tests should cover zero-battery systems, multiple battery registration, unit conversions mWh-to-uWh/mA-to-uA/mV-to-uV, model-name decoding, and cleanup after mid-loop registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/pmu_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/power_supply.h -->
# sources/distributed-fs/ceph-client/drivers/power/supply/power_supply.h

## Purpose
This private header declares internal interfaces shared by the power_supply core, sysfs, LED trigger, and hwmon implementation files. It centralizes optional feature stubs so core code can call sysfs/LED/hwmon helpers regardless of configuration.

## Important APIs, Types, and Functions
It forward-declares `struct power_supply`, exposes internal `power_supply_property_is_writeable()`, `power_supply_has_property()`, and `power_supply_ext_has_property()`, defines `struct power_supply_ext_registration`, and provides `power_supply_for_each_extension()` with a lockdep assertion on `extensions_sem`. It conditionally declares or stubs `power_supply_init_attrs()`, `power_supply_uevent()`, `power_supply_attr_groups`, sysfs extension links, LED trigger helpers, and hwmon helpers.

## Control Flow
There is no runtime control flow beyond inline stubs. Compile-time configuration selects real helper declarations for `CONFIG_SYSFS`, `CONFIG_LEDS_TRIGGERS`, and `CONFIG_POWER_SUPPLY_HWMON`, or no-op fallbacks that let `power_supply_core.c` build without feature-specific code.

## State and Persistence
The only state shape introduced here is `power_supply_ext_registration`, which links extension metadata, owning device, and extension data into a power_supply list. The header stores no state itself and has no persistence behavior.

## Dependencies and Integration Points
It depends on `linux/lockdep.h` and public power_supply types. The extension macro assumes callers hold `psy->extensions_sem`; misuse can trigger lockdep. This header is the internal contract among `power_supply_core.c`, `power_supply_sysfs.c`, `power_supply_leds.c`, and `power_supply_hwmon.c`.

## Risks and Test Signals
Risks include list iteration without the extension semaphore, stubs masking missing feature behavior, and declaration drift with the public power_supply API. Build coverage should include combinations of sysfs, LED triggers, and hwmon enabled/disabled; runtime lockdep should cover extension registration and property paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/power_supply.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_core.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_core.c

## Purpose
`power_supply_core.c` implements the universal Linux power_supply class. It handles class registration, power_supply device registration/unregistration, property get/set dispatch, supplier relationships, battery-info parsing, notifications, extension registration, hwmon/sysfs/LED/thermal integration, and helper lookup/interpolation routines.

## Important APIs, Types, and Functions
Major exported APIs include `power_supply_register()`, `devm_power_supply_register()`, `power_supply_unregister()`, `power_supply_changed()`, `power_supply_get_property()`, `power_supply_set_property()`, direct get/set variants, supplier lookup helpers, `power_supply_get_battery_info()`, `power_supply_put_battery_info()`, OCV/resistance interpolation helpers, extension register/unregister, notifier register/unregister, and `power_supply_get_drvdata()`. Internal state is class-level `power_supply_class`, `power_supply_notifier`, and `power_supply_dev_type`.

## Control Flow
Class init initializes sysfs attributes and registers the `power_supply` class. Registration allocates `struct power_supply`, binds device metadata and config, checks supplies, optionally parses battery info for battery devices, initializes locks/work, adds the device, initializes wakeup/thermal/LED/hwmon integration, increments use count, marks initialized, and queues a delayed change event after parent probe has settled. `power_supply_changed()` marks a changed flag under spinlock, holds a wake reference, and schedules work. The worker updates sysfs groups if needed, propagates external-power changes to supplied devices, updates LEDs, calls notifiers, and emits uevents.

## State and Persistence
Persistent kernel state is per-device: descriptor pointer, driver data, supplier arrays, extension list, battery info, changed flags, wakeup source, thermal zone, hwmon resources, and LED triggers. Battery info is parsed from firmware nodes or static Samsung tables and managed with devm allocations. No disk persistence exists.

## Dependencies and Integration Points
The core integrates with the device model class API, fwnode/OF references, notifiers, PM wakeup, sysfs, thermal, hwmon, LED triggers, and optional Samsung SDI battery tables. Drivers in this subset call `devm_power_supply_register()`, `power_supply_changed()`, `power_supply_get_battery_info()`, `power_supply_am_i_supplied()`, and property dispatch helpers.

## Risks and Test Signals
Risk areas include lifecycle races around `use_cnt`, deferred registration, extension semaphore ordering, supplier probe deferral, dynamic sysfs/hwmon refresh, battery-info parsing error cleanup, and OCV/resistance interpolation assumptions about sorted tables. Tests should cover registration failure unwinds, sysfs/hwmon/LED optional configs, extension conflicts, supplier phandle deferral, absent monitored-battery nodes, uevent behavior during removal, and KUnit-style interpolation/property helper cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_hwmon.c

## Purpose
This file bridges power_supply properties into the hwmon subsystem. It creates a hwmon device for supplies that expose voltage, current, power, or temperature properties and performs unit conversion between power_supply and hwmon conventions.

## Important APIs, Types, and Functions
`struct power_supply_hwmon` stores the backing power_supply and a bitmap of supported power_supply properties. Mapping helpers convert hwmon attrs to power_supply properties for voltage, current, power, and two temperature channels. Main callbacks are `power_supply_hwmon_is_visible()`, `power_supply_hwmon_read()`, `power_supply_hwmon_write()`, `power_supply_hwmon_read_string()`, `power_supply_add_hwmon_sysfs()`, and `power_supply_remove_hwmon_sysfs()`.

## Control Flow
When the core adds hwmon, this file opens a devres group, allocates state and a bitmap, populates supported properties via `power_supply_has_property()`, sanitizes the hwmon name by replacing dashes with underscores, and calls `devm_hwmon_device_register_with_info()`. Visibility maps hwmon attributes to power_supply properties and marks attributes writable only when both the power_supply property is writable and hwmon allows writes. Reads call `power_supply_get_property()` then convert uV/uA to mV/mA and tenths-C to milli-C. Writes reverse those conversions and call `power_supply_set_property()`.

## State and Persistence
State is devm-managed under a devres group keyed by `power_supply_add_hwmon_sysfs()`, allowing removal/recreation when extensions change property availability. No persistent state is stored.

## Dependencies and Integration Points
It depends on `linux/hwmon.h`, power_supply property helpers, bitmap allocation, overflow helpers, and the private header. The core invokes add/remove during registration and extension updates.

## Risks and Test Signals
Risks include property enum bitmap sizing, unit conversion overflow, mismatch between visible/writeable attributes and driver capabilities, and missing labels when no temp input exists. Tests should verify hwmon files for supplies with each property class, write conversions for voltage/current/temp limits, name sanitization, extension-triggered rebuild, and overflow error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_leds.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_leds.c

## Purpose
This optional companion file creates LED triggers for power_supply devices and updates them when supply state changes. Battery supplies get charging/full-oriented triggers; non-battery supplies get an online trigger.

## Important APIs, Types, and Functions
`struct power_supply_led_trigger` wraps `struct led_trigger` with a backpointer to the power_supply. Key functions are `power_supply_register_led_trigger()`, `power_supply_unregister_led_trigger()`, `power_supply_update_bat_leds()`, `power_supply_create_bat_triggers()`, `power_supply_update_gen_leds()`, `power_supply_create_gen_triggers()`, `power_supply_update_leds()`, `power_supply_create_triggers()`, and `power_supply_remove_triggers()`.

## Control Flow
During power_supply registration the core calls `power_supply_create_triggers()`. Battery devices register five triggers based on the supply name; non-battery devices register one `%s-online` trigger. On `power_supply_changed()` work, the core calls `power_supply_update_leds()`. Battery LED updates read `POWER_SUPPLY_PROP_STATUS` and set solid, off, blink, or multicolor orange/green patterns for full, charging, or other states. Non-battery updates read `ONLINE` and switch the online trigger.

## State and Persistence
Trigger objects and names are dynamically allocated and freed at unregister. LED state is external to the driver and updated from current power_supply properties; no persistent data is kept.

## Dependencies and Integration Points
This file depends on `CONFIG_LEDS_TRIGGERS`, LED trigger APIs, multicolor trigger support calls, and power_supply property reads. It is wired into `power_supply_core.c` through private header declarations.

## Risks and Test Signals
Risks include allocation/unwind correctness when one of several battery triggers fails, property-read failures silently leaving stale LED state, and assumptions that status/online properties exist for all supplies. Tests should cover registration/unregistration leak checks, trigger names, activation sync callback, status transitions, non-battery online transitions, and configs without LED trigger support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_sysfs.c

## Purpose
This file implements sysfs and uevent formatting for the power_supply class. It maps enum properties to attribute names, text labels, writable modes, parsing, dynamic visibility, extension links, and `POWER_SUPPLY_*` uevent variables.

## Important APIs, Types, and Functions
`struct power_supply_attr` binds property names, lower-case sysfs attribute names, device attributes, and optional text tables. Important functions include `power_supply_init_attrs()`, `power_supply_format_property()`, `power_supply_show_property()`, `power_supply_store_property()`, `power_supply_attr_is_visible()`, `power_supply_uevent()`, enum helpers for charge behavior/types, and sysfs extension link add/remove helpers.

## Control Flow
Class init lowercases all property names and prepares the global attribute array. Attribute visibility checks whether the power_supply has the property through descriptor, battery info, or extensions, and adds owner-write mode when writeable. Reads call `power_supply_format_property()`, which fetches values, formats enums/text/string/int properties, and for USB type/charge modes shows available choices with the active value bracketed. Writes parse text labels or integers and call `power_supply_set_property()`. Uevent generation adds the supply name/type and then formats every property, tolerating absent-battery style errors.

## State and Persistence
The global attribute table is initialized once and marked `__ro_after_init`. Extension links are sysfs links under an `extensions` group. No persistent storage is used.

## Dependencies and Integration Points
It depends on the private power_supply header, string helpers, sysfs/device attributes, extension registration from the core, and the public enum value ordering in `linux/power_supply.h`. It provides `power_supply_attr_groups` and `power_supply_uevent` to `power_supply_core.c`.

## Risks and Test Signals
Risks include enum/text table drift, exposing driver-reported unavailable enum values, partial uevent omissions on transient errors, write parsing accepting raw integers for enums, and extension property conflicts. Tests should cover attribute visibility for descriptor/battery-info/extension properties, text formatting with spaces escaped, write parsing, uevents during removal, absent battery errors, and charge type/behavior available-value helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/qcom_battmgr.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/qcom_battmgr.c

## Purpose
`qcom_battmgr.c` implements the Qualcomm PMIC GLINK battery manager power-supply driver. It registers battery, USB, wireless, and on some variants AC supplies, translates power_supply property reads/writes into PMIC GLINK requests, handles asynchronous firmware replies/notifications, and supports variant-specific firmware protocols for SC8280XP/X1E80100 and SM8350/SM8550-style platforms.

## Important APIs, Types, and Functions
Important state structs are `qcom_battmgr`, `qcom_battmgr_info`, `qcom_battmgr_status`, and source-specific AC/USB/wireless caches. Message/request structs encode PMIC GLINK protocol payloads. Main functions include `qcom_battmgr_probe()`, `qcom_battmgr_request()`, property update helpers, `qcom_battmgr_bat_get_property()`, USB/WLS/AC get-property callbacks, charge-control setters, `qcom_battmgr_notification()`, variant callbacks `qcom_battmgr_sc8280xp_callback()` and `qcom_battmgr_sm8350_callback()`, `qcom_battmgr_callback()`, `qcom_battmgr_enable_worker()`, and `qcom_battmgr_pdr_notify()`.

## Control Flow
Probe chooses a variant from the parent compatible, initializes charge-control thresholds from nvmem, registers variant-appropriate power supplies, allocates a PMIC GLINK client, and registers it. PDR service-up notifications set `service_up` and schedule notification enable work. Property reads reject access while service is down, serialize firmware requests with `lock`, send a request, wait up to one second for callback completion, then return cached decoded values. SC8280XP/X1E80100 batch status/info/time requests; SM8350/SM8550 use property-specific request maps. Firmware notifications invalidate info or call `power_supply_changed()` on the affected supply.

## State and Persistence
The driver caches firmware-reported battery info, status, AC/USB/wireless source values, charge-control thresholds, service state, last request error, and completion. Charge-control defaults can be read from nvmem cells (`charge_limit_en`, `charge_limit_end`, `charge_limit_delta`), and runtime writes send firmware commands then update cached thresholds. No filesystem persistence is performed.

## Dependencies and Integration Points
The driver depends on auxiliary bus binding `pmic_glink.power-supply`, PMIC GLINK owner BATTMGR, PDR service state callbacks, nvmem cells for charge limits, OF compatible-to-variant mapping, the power_supply class, and supplier relationships via `supplied_to = "battery"` for source supplies. It integrates with sysfs through distinct property arrays per variant and with uevents through `power_supply_changed()`.

## Risks and Test Signals
Risk areas include firmware protocol length validation, request timeout handling, callback completion on malformed messages, variant property-map gaps where unmapped properties default to zero, integer unit conversions and capacity percentage overflow avoidance, returning success from charge threshold setters even if firmware request failed, and service-up races. Tests should mock PMIC GLINK replies for both protocol families, verify each property mapping and unit, test notifications, PDR down/up behavior, timeout/error propagation, charge threshold clamping/nvmem init, and power_supply registration per compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/qcom_battmgr.c -->
