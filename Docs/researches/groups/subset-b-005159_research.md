# subset-b-005159 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/cpcap-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/cpcap-charger.c

Purpose: implements the Motorola CPCAP PMIC USB charger power-supply driver. It exposes a `usb` supply feeding `battery`, controls CPCAP charger CRM/VUSBC registers, participates in OMAP USB PHY VBUS companion handling, and reads charger voltage/current/VBUS state through IIO channels.

Important APIs/types/functions: `struct cpcap_charger_ddata` holds regmap, IRQ list, IIO channels, delayed works, optional mode GPIOs, USB supply, PHY companion, VBUS flags, and cached status/current/voltage limits. The key callbacks are `cpcap_charger_get_property()`, `cpcap_charger_set_property()`, `cpcap_usb_detect()`, `cpcap_charger_vbus_work()`, `cpcap_charger_irq_thread()`, and `cpcap_charger_probe()`. Conversion helpers map Linux microvolt/microamp values to CPCAP CRM bitfields.

Control flow: probe initializes regmap/IIO/work, registers the `usb` power supply, requests named PMIC IRQs, installs the USB comparator, initializes optional mode GPIOs, and schedules detection. IRQs schedule `detect_work`; detection samples interrupt state and VBUS, checks the battery supply `PRESENT`, clamps charge current to `INPUT_CURRENT_LIMIT`, enables or disables charging, updates `POWER_SUPPLY_STATUS_*`, and emits `power_supply_changed()`. PHY `set_vbus` schedules `vbus_work`, which disables charging and toggles reverse-mode/VBUS boost when the device provides VBUS.

State and persistence: runtime state is in `ddata`; user-set input current and charge voltage are cached only in memory. Hardware state persists only in PMIC registers until reset or shutdown. Shutdown/remove clear the comparator, disable charging, mark discharging, and cancel work.

Dependencies and integration: depends on CPCAP MFD regmap/register definitions, IIO ADC channels named `battdetb`, `battp`, `vbus`, `chg_isense`, and `batti`, OMAP USB PHY companion APIs, optional GPIO descriptors, named platform IRQs, and a separate `"battery"` power supply.

Risks and test signals: this tree contains duplicated `devm_request_threaded_irq()` text in `cpcap_usb_init_irq()`, so compile testing is important. The cable path setter writes `gpio[0]` twice instead of touching both paths; verify intended board wiring. Functional tests should cover plug/unplug IRQs, VBUS boost, absent battery, charge-full retry delay, writable current/voltage properties, missing battery supply deferral behavior, and shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/cpcap-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/cros_charge-control.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/cros_charge-control.c

Purpose: extends ChromeOS ACPI battery power supplies with EC-backed charge-control properties. It translates Linux `charge_behaviour` and charge-control threshold properties to `EC_CMD_CHARGE_CONTROL` versions 1 through 3.

Important APIs/types/functions: `struct cros_chctl_priv` stores the EC device, battery hook, selected command version, selected `power_supply_ext`, mutex, current behavior, and cached thresholds. `cros_chctl_configure_ec()` builds `struct ec_params_charge_control`; `cros_chctl_psy_ext_get_prop()` and `cros_chctl_psy_ext_set_prop()` implement the extension; `cros_chctl_add_battery()` registers it on discovered batteries.

Control flow: probe rejects Framework devices exposing the custom Framework charge-limit command unless the module parameter allows coexistence, discovers supported EC command versions, selects the property set for v1/v2/v3, initializes cached behavior to auto with 0/100 thresholds, sends a known-good EC configuration, and registers an ACPI battery hook. Battery add/remove callbacks register or unregister the power-supply extension.

State and persistence: the driver intentionally does not read EC state back after probe; sysfs values are a driver cache. Changes outside this driver are invisible until a property write synchronizes cached state to the EC. Threshold and behavior state is not persisted by the driver, though EC/firmware may retain its own state.

Dependencies and integration: depends on ChromeOS EC command transport, ACPI battery hooks, the power-supply extension API, DMI matching, and the EC charge-control command ABI. Version 2 exposes only end threshold and mirrors start threshold to either zero or the end threshold.

Risks and test signals: this source snapshot includes a duplicated `ec_dev` declaration in probe, so build testing is a first gate. Behavioral tests should verify EC command payload sizes for v1/v2/v3, threshold ordering checks, negative/out-of-range rejection, Framework guard behavior, battery hotplug extension cleanup, and that writes under the mutex leave cache and EC synchronized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/cros_charge-control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/cros_peripheral_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/cros_peripheral_charger.c

Purpose: exposes ChromeOS EC peripheral charging ports, such as ports that charge detachable peripheral devices, as one battery-like power supply per EC PCHG port.

Important APIs/types/functions: `struct charger_data` tracks EC devices, registered port supplies, and the EC notifier. `struct port_data` caches per-port name, status, capacity, charge type, and `last_update`. `cros_pchg_ec_command()` wraps EC command transfer; `cros_pchg_port_count()`, `cros_pchg_cmd_ver_check()`, `cros_pchg_get_status()`, and `cros_pchg_get_prop()` form the runtime path.

Control flow: probe queries the number of PCHG ports, verifies EC command version 1, bounds the count by `EC_PCHG_MAX_PORTS`, registers `peripheral%d` battery-type supplies, then registers a blocking notifier on the ChromeOS EC event chain. Property reads refresh cached status/capacity/charge type with a 500 ms ratelimit. EC MKBP PCHG device events refresh all ports immediately and call `power_supply_changed()` on changes. Resume also refreshes all ports in case events were lost.

State and persistence: each port keeps only volatile cached state and a jiffies timestamp. There are no writable properties and no persistence. The EC remains authoritative for peripheral charge state.

Dependencies and integration: depends on ChromeOS EC `EC_CMD_PCHG_COUNT`, `EC_CMD_PCHG`, `EC_CMD_GET_CMD_VERSIONS`, EC MKBP event parsing, unaligned little-endian event data, and the platform device named `cros-ec-pchg`.

Risks and test signals: lack of explicit notifier unregister in this file relies on platform/driver lifetime assumptions and should be reviewed against EC notifier ownership. The tree snapshot also shows an extra brace near the notifier path, so compile coverage matters. Test with zero ports, too many ports, unsupported command versions, EC transfer failures, event-driven updates, ratelimited property reads, and suspend/resume event loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/cros_peripheral_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/cros_usbpd-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/cros_usbpd-charger.c

Purpose: exposes ChromeOS EC USB-PD and optional dedicated charger ports as power supplies. It reports online/status/current/voltage/USB type/model/manufacturer and provides global writable external input current/voltage limits.

Important APIs/types/functions: `struct charger_data` owns EC handles, port counts, registered supplies, and notifier. `struct port_data` caches per-port power info and discovery strings. `cros_usbpd_charger_ec_command()` wraps EC transport; `cros_usbpd_charger_get_power_info()` maps EC roles/types to `POWER_SUPPLY_*`; `cros_usbpd_charger_set_ext_power_limit()` sends `EC_CMD_EXTERNAL_POWER_LIMIT`.

Control flow: probe queries USB-PD port count and total charge-port count, validates that at most one dedicated charger follows the USB-PD ports, registers per-port descriptors as USB or mains supplies, and registers for USB-PD EC notifications. Dynamic property reads refresh power info with a 500 ms cache except when MKBP event support makes cached online state authoritative. External power changes and EC notifications refresh every registered port. Resume emits changed notifications and expires port caches.

State and persistence: port state is an in-memory cache. `input_current_limit` and `input_voltage_limit` are module-global cached limits shared across all ports; they are initialized to `EC_POWER_LIMIT_NONE` and updated only after successful EC writes.

Dependencies and integration: depends on ChromeOS EC USB-PD commands, `cros_usbpd_notify`, the power-supply USB type bitmap, and EC discovery/power-info response formats. Dedicated charger ports intentionally expose a smaller property set.

Risks and test signals: this source snapshot includes duplicated local declarations in `cros_usbpd_charger_power_changed()`. Because input limits are global, multi-instance behavior should be reviewed. Test unsupported command fallbacks, dedicated-port count validation, EC failure handling, USB type mapping, limit clearing with negative values, uevent generation on type/status changes, and resume cache invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/cros_usbpd-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/cw2015_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/cw2015_battery.c

Purpose: implements an I2C/regmap fuel-gauge driver for CellWise CW2013/CW2015 chips, exposing a `cw2015-battery` supply with capacity, voltage, status, time-to-empty, charge counters, and derived current.

Important APIs/types/functions: `struct cw_battery` stores regmap, workqueue, power supply, optional battery profile, cached readings, counters, poll interval, and alert level. `cw_init()` wakes/configures the gauge, uploads profile data when needed, and checks flash contents. `cw_get_soc()`, `cw_get_voltage()`, and `cw_get_time_to_empty()` read gauge registers. `cw_bat_work()` is the periodic polling path.

Control flow: probe parses `cellwise,battery-profile` and `cellwise,monitor-interval-ms`, initializes regmap, calls `cw_init()`, registers the power supply, retrieves optional battery info, creates an ordered workqueue, and schedules polling. The worker wakes/reset-recovers the gauge if sleeping, updates SoC/voltage/supply status/time-to-empty, notifies on changed values, and reschedules. Suspend cancels polling; resume schedules an immediate refresh.

State and persistence: battery profile and alert threshold can be written into gauge flash/config; runtime readings and stuck/error counters live in memory. The driver derives status from `power_supply_am_i_supplied()`, uses hysteresis to suppress charge/discharge spikes, resets after invalid SoC for 40 seconds, and resets if SoC is stuck while charging for 30 minutes.

Dependencies and integration: depends on I2C regmap, firmware properties, power-supply battery-info metadata, workqueues, and external charger supplies for `am_i_supplied`.

Risks and test signals: the source has suspicious config update code using `reg_val |= ~CW2015_ATHD(...)`, which can set unrelated bits, and duplicated log output in the worker. Test profile upload/replacement, no-profile behavior, invalid SoC reset, stuck-charge reset, voltage scaling, time-to-empty validity, suspend/resume, and missing battery-info fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/cw2015_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/da9030_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/da9030_battery.c

Purpose: controls the Dialog DA9030 PMIC battery charger and exposes a battery power supply using PMIC ADC results, platform battery metadata, thresholds, PMIC notifier events, and optional debugfs diagnostics.

Important APIs/types/functions: `struct da9030_charger` stores PMIC master device, ADC snapshot, delayed monitor work, platform battery info, charge thresholds, charge setpoints, notifier, callbacks, and debugfs handle. `da9030_charger_check_state()` enforces charge enable/disable policy. `da9030_battery_get_property()` reports model/status/health/technology/design voltage/current/voltage. `da9030_battery_event()` handles PMIC events.

Control flow: probe validates platform data and charge setpoints, converts thresholds to register units, initializes PMIC ADC/threshold registers, starts periodic monitor work, registers a DA903x notifier for charger detect, VBAT monitor, charge over-current, and temperature events, registers the power supply, and creates debugfs. The monitor updates PMIC state, starts charging when a charger is present and VBAT is below the start threshold, stops charging on removal/full/voltage/temperature faults, and updates VBAT thresholds for restart/low handling.

State and persistence: runtime state tracks ADC readings, fault bits, charger detect, and whether charging is enabled. Threshold and ADC control writes program PMIC registers; no driver-owned persistent storage exists. Platform callbacks may trigger board-specific low/critical responses.

Dependencies and integration: depends on DA903x MFD register access/notifiers, platform data `da9030_battery_info`, Linux power-supply core, delayed work, and optional debugfs.

Risks and test signals: this snapshot duplicates `POWER_SUPPLY_PROP_VOLTAGE_MIN_DESIGN` in the property list and debugfs labels use some mismatched conversion helpers. Tests should cover platform-data rejection, notifier registration failures, charger plug/unplug events, thermal/voltage fault shutdown, monitor rescheduling, low/critical callbacks, debugfs reads, and remove-time charger disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/da9030_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/da9052-battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/da9052-battery.c

Purpose: exposes Dialog DA9052 PMIC battery state using PMIC status registers, charger-end/current registers, ADC voltage/temperature readings, and fixed voltage-capacity lookup tables.

Important APIs/types/functions: `struct da9052_battery` holds PMIC pointer, power supply, USB current notifier, charger type, status, and health. `da9052_bat_check_status()` interprets DCIN/VBUS selection/detect and charge-end flags. `da9052_bat_read_capacity()` interpolates capacity from voltage and temperature lookup tables. `da9052_bat_irq()` handles PMIC IRQs; `da9052_USB_current_notifier()` updates USB current limit.

Control flow: probe allocates state, initializes defaults, applies platform `use_for_apm`, requests TBAT/DCIN/VBUS/CHGEND IRQs, and registers `da9052-bat`. Property reads check battery presence via temperature threshold, reject most properties when battery is illegal, then read or derive status, online, health, voltage, current, capacity, temperature, and technology. IRQs update status/full state and notify the supply.

State and persistence: status, charger type, and health are cached in memory and refreshed on reads/IRQs. The USB current notifier writes DA9052 current-limit registers, so current-limit changes persist in PMIC state until changed/reset. Capacity is derived each read rather than stored.

Dependencies and integration: depends on DA9052 MFD core, regmap IRQ virqs, PMIC ADC helpers, platform data, and power-supply registration.

Risks and test signals: this tree has duplicated `da9052_reg_read()` in the USB current notifier and a temperature table index branch that appears logically unreachable/reversed for some ranges. Test IRQ request/free unwind, battery absent/illegal path, DCIN/VBUS priority, charge-end current comparison, capacity interpolation at table boundaries, USB current-limit validation, and unit consistency for voltage/current/temp properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/da9052-battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/da9150-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/da9150-charger.c

Purpose: provides DA9150 charger support through two power supplies, `da9150-usb` and `da9150-battery`, reporting charger input measurements, battery charge state, charger limits, health, and OTG/VBUS transitions.

Important APIs/types/functions: `struct da9150_charger` stores DA9150 core pointer, USB/battery supplies, currently online supply, USB PHY notifier/work, and IIO channels. Measurement callbacks read `CHAN_VBUS`, `CHAN_IBUS`, `CHAN_TJUNC`, and `CHAN_VBAT`; battery callbacks decode DA9150 status and charge-control registers. IRQ handlers cover `CHG_STATUS`, `CHG_TJUNC`, `CHG_VFAULT`, and `CHG_VBUS`.

Control flow: probe gets IIO channels, registers both supplies, samples initial VBUS state to decide which supply is online, optionally registers a USB2 PHY notifier for OTG boost switching, and requests charger IRQs. IRQs notify relevant supplies and update `supply_online` on VBUS changes. USB PHY ID events schedule work that switches DA9150 buck control between OTG and charging modes.

State and persistence: `supply_online` and last USB event are volatile driver state. Charge/OTG mode writes update DA9150 PMIC registers. Remove frees IRQs, unregisters the USB notifier, and cancels OTG work.

Dependencies and integration: depends on DA9150 MFD register helpers, DA9150 register definitions, IIO channels, Linux USB PHY notifier APIs, named platform IRQs, and the power-supply core.

Risks and test signals: this source snapshot duplicates a `POWER_SUPPLY_PROP_ONLINE` case and `remove()` frees IRQs without checking negative lookups. `cancel_work_sync()` is called even when no USB PHY initialized `otg_work`, so review init assumptions. Test missing IIO channels, each IRQ path, VBUS state transitions, OTG notifier cleanup, battery present/health mappings, and unit conversion from mV/mA/milli-Celsius to power-supply units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/da9150-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/da9150-fg.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/da9150-fg.c

Purpose: implements the DA9150 fuel-gauge power supply by reading/writing fuel-gauge QIF attributes over the DA9150 Core2Wire interface and reporting capacity, average current/voltage, full charge, and temperature.

Important APIs/types/functions: `struct da9150_fg` stores DA9150 core, I/O mutex, power supply, optional delayed polling work, update interval, warning/critical SoC thresholds, and cached SoC. `da9150_fg_read_attr_sync()` and `da9150_fg_write_attr_sync()` serialize QIF sync transactions. Property callbacks convert QIF `SOC_PCT`, `IAVG`, `UAVG`, `FCC_MAH`, and `NTCAVG`.

Control flow: probe enables QIF, registers `da9150-fg`, logs firmware version, parses platform/DT update interval and SoC thresholds, configures initial SoC limit events, optionally starts polling work, and requests the `FG` IRQ. Polling compares current SoC to cached SoC and notifies on change. The IRQ reads fuel-gauge event status, reprograms charge/discharge thresholds around warning/critical levels when SoC events fire, clears QIF status, and returns.

State and persistence: cached SoC and threshold values are volatile. QIF writes program fuel-gauge event limits in hardware. DT properties `dlg,update-interval`, `dlg,warn-soc-level`, and `dlg,crit-soc-level` seed runtime behavior.

Dependencies and integration: depends on DA9150 MFD QIF helpers, platform IRQs, optional OF properties, delayed-work autocancel, mutex serialization, and power-supply registration.

Risks and test signals: this snapshot duplicates a temperature callback call in `da9150_fg_get_prop()`. QIF read/write helpers log sync failures but often return a value or void rather than propagating errors. Test QIF timeout behavior, zero shunt/gain division safety, threshold validation, IRQ threshold reconfiguration, polling interval changes, resume flush behavior, and property unit conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/da9150-fg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ds2760_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/ds2760_battery.c

Purpose: implements a 1-Wire DS2760 battery monitor/fuel-gauge driver. It exposes raw 1-Wire SRAM through a bin attribute and registers a battery power supply with voltage, current, charge, temperature, capacity, time-to-empty, and writable charge calibration properties.

Important APIs/types/functions: `struct ds2760_device_info` caches raw SRAM, converted readings, capacity estimates, charge status, power supply descriptor, monitor workqueue, and PM notifier. `w1_ds2760_io()` serializes 1-Wire read/write with the bus mutex. `ds2760_battery_read_status()` refreshes cached values and computes capacity. `ds2760_battery_update_status()` derives charging/full/discharging state.

Control flow: `w1_ds2760_add_slave()` allocates state, applies module parameters and OF overrides, writes PMOD/rated-capacity/current-accumulator values when requested, registers the battery, starts an ordered monitor workqueue, and registers a PM notifier. Reads use `cache_time` to avoid frequent full SRAM access, then convert raw register fields and interpolate active-full/empty capacity over temperature. External power changes reschedule a near-term monitor update.

State and persistence: cached readings live in memory. PMOD, rated capacity, active-full, and current-accumulator writes can be copied/recalled through DS2760 EEPROM blocks, so calibration changes persist in the pack. PM events force status unknown and refresh after resume.

Dependencies and integration: depends on the 1-Wire subsystem, W1 family registration, OF properties, module parameters, power-supply external supply detection, PM notifier chain, and bin sysfs attributes.

Risks and test signals: write paths directly program battery EEPROM and need careful validation. Error handling treats short 1-Wire reads as status read failure but some write helpers cannot know actual bytes written. Test cache expiration, full first read vs partial later reads, EEPROM writes, PMOD/device-tree overrides, external power status transitions, full-counter behavior, suspend/resume notifier behavior, and bin attribute bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ds2760_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ds2780_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/ds2780_battery.c

Purpose: exposes Maxim/Dallas DS2780 1-Wire fuel-gauge data through a platform battery driver, with sysfs controls for PMOD, sense resistor, RSGAIN, PIO, and user/parameter EEPROM blocks.

Important APIs/types/functions: `struct ds2780_device_info` links the platform power supply to the parent 1-Wire device. `ds2780_battery_io()` delegates to the W1 DS2780 slave helper. Measurement helpers convert voltage, temperature, current/current-average, accumulated charge, relative capacity, status, and remaining active absolute charge. EEPROM helpers store and recall after writes.

Control flow: probe constructs a battery descriptor named from the platform device, attaches the DS2780 sysfs attribute group, and registers the supply. Property reads synchronously access 1-Wire registers and convert units. Sysfs stores validate simple ranges, write control/calibration registers, and persist register or EEPROM block changes where appropriate.

State and persistence: almost no measurement state is cached; reads go to the device. PMOD, sense resistor conductance, RSGAIN, and EEPROM bin writes persist to DS2780 EEPROM. PIO writes alter the special-feature register but are not copied to EEPROM in this path.

Dependencies and integration: depends on platform devices created by the W1 DS2780 slave layer, `w1_ds2780_io()`, `w1_ds2780_eeprom_cmd()`, DS2780 register definitions, power-supply core, and sysfs/bin attribute plumbing.

Risks and test signals: sense resistor zero is rejected, but integer division in current/charge scaling loses precision. This source snapshot includes an extra brace near `ds2780_get_control_register()`, so compile tests are required. Functional tests should cover all property reads, EEPROM bin offset/count behavior, PMOD/RSGAIN validation, sense resistor persistence, PIO writes, and 1-Wire error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ds2780_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ds2781_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/ds2781_battery.c

Purpose: provides the Maxim/Dallas DS2781 1-Wire fuel-gauge power-supply driver. It mirrors the DS2780-style interface while using DS2781 register definitions and status logic that consults whether the battery is externally supplied.

Important APIs/types/functions: `struct ds2781_device_info` stores device pointers and battery descriptor. `ds2781_battery_io()` delegates to W1 DS2781 helpers. `ds2781_get_voltage()`, `ds2781_get_temperature()`, `ds2781_get_current()`, `ds2781_get_accumulated_current()`, `ds2781_get_capacity()`, and `ds2781_get_status()` implement property reads. Sysfs attributes manage PMOD, sense resistor, RSGAIN, PIO, and EEPROM blocks.

Control flow: probe creates a battery descriptor with the DS2781 property set and sysfs group, then registers the power supply. Each property read performs W1 register access and conversion. Status reads capacity/current and uses `power_supply_am_i_supplied()` to distinguish charging/not-charging/full from discharging. Sysfs writes update registers and persist calibration/control values through DS2781 EEPROM copy/recall commands.

State and persistence: measurement data is not cached in driver state. PMOD, sense resistor conductance, RSGAIN, and bin EEPROM writes persist in the gauge. PIO writes affect the special-feature register. The external supply relationship affects reported status but is not stored.

Dependencies and integration: depends on W1 DS2781 slave helpers and register definitions, platform-device binding, sysfs/bin attributes, and the power-supply core including external supply detection.

Risks and test signals: this snapshot contains a doubled opening brace in `ds2781_get_control_register()` and an extra closing brace at file end, so compile testing is mandatory. Test negative/sign extension in voltage/temp/current conversions, EEPROM store/recall failures, sense resistor zero, status transitions with/without external power, sysfs validation, and bin attribute read/write offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ds2781_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ds2782_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/ds2782_battery.c

Purpose: implements an I2C fuel-gauge driver for Maxim/Dallas DS2782 and DS2786 chips, exposing status, capacity, voltage, current, and temperature through the power-supply class.

Important APIs/types/functions: `struct ds278x_info` holds I2C client, battery descriptor, selected ops table, delayed work, sense resistor value for DS2786, cached capacity, and cached status. `struct ds278x_battery_ops` selects chip-specific current/voltage/capacity conversion functions. `ds278x_read_reg()` and `ds278x_read_reg16()` wrap SMBus register reads.

Control flow: probe allocates a unique IDA number for the supply name, validates DS2786 platform data, selects the ops table from the I2C ID, initializes default full status/capacity, registers the battery, initializes delayed work, and starts one-second polling. Polling recomputes status/capacity and emits `power_supply_changed()` on change. Suspend cancels polling; resume restarts it.

State and persistence: cached `status` and `capacity` are volatile. No writable properties or persistent driver-managed calibration are exposed. DS2786 requires platform `rsns` to convert current.

Dependencies and integration: depends on I2C SMBus byte/word reads, IDA allocation, optional platform data from `linux/ds2782_battery.h`, delayed-work autocancel, and power-supply registration.

Risks and test signals: this source snapshot duplicates `POWER_SUPPLY_PROP_VOLTAGE_NOW` in the property list. Conversion constants and integer division should be checked for DS2782 and DS2786 separately, especially sense resistor handling. Test missing DS2786 platform data, IDA cleanup on probe failures, SMBus read errors, polling notifications, suspend/resume, and boundary capacity values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ds2782_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/generic-adc-battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/generic-adc-battery.c

Purpose: implements a generic IIO-backed battery power-supply driver. It exposes status plus whichever of voltage/current/power/temperature channels are present on the device.

Important APIs/types/functions: `struct gab` holds the power supply descriptor, optional IIO channels, delayed status work, cached status, and optional `charged` GPIO. `gab_read_channel()` reads processed IIO values and scales them by 1000. `gab_work()` derives status from external supply state and the optional charge-finished GPIO. `gab_probe()` dynamically builds the property list from available IIO channels.

Control flow: probe allocates state, builds a descriptor named after the device, tries to acquire standard IIO channels `voltage`, `current`, `power`, and `temperature`, requires at least one channel, registers the power supply, sets up delayed work, optionally requests an IRQ on the `charged` GPIO, and schedules an immediate status check. External power changes and charged-GPIO interrupts schedule status work. Suspend cancels work and marks status unknown; resume reschedules with a small jitter.

State and persistence: only current status is cached. Channel readings are pulled from IIO on demand. There are no writable properties and no persistence.

Dependencies and integration: depends on platform/OF compatible `adc-battery`, IIO consumer channels, optional GPIO descriptor/IRQ, `power_supply_am_i_supplied()`, and devm delayed-work helpers.

Risks and test signals: the driver assumes all processed IIO channel units should be multiplied by 1000, which must match provider conventions for voltage/current/power/temp. Optional charged GPIO handling checks `IS_ERR()` incompletely after `devm_gpiod_get_optional()`. Test dynamic property enumeration, no-channel probe failure, each channel read, external-supply status transitions, charged IRQ jitter, and suspend/resume behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/generic-adc-battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/goldfish_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/goldfish_battery.c

Purpose: exposes the Goldfish emulator battery and AC adapter MMIO interface as Linux power supplies named `battery` and `ac`.

Important APIs/types/functions: `struct goldfish_battery_data` holds the MMIO base, IRQ, spinlock, and two power supplies. Register offsets define interrupt status/enable and all battery/AC properties. `goldfish_ac_get_property()` and `goldfish_battery_get_property()` read MMIO registers directly. `goldfish_battery_interrupt()` handles status-change interrupts.

Control flow: probe maps the platform MMIO resource, gets the IRQ, registers AC and battery supplies, requests a shared IRQ, then enables battery and AC interrupt bits. Property reads perform `readl()` from the corresponding emulator register. The IRQ handler takes a spinlock, reads and masks interrupt status, calls `power_supply_changed()` for battery and/or AC, and returns handled only when a known bit was set.

State and persistence: state is emulator-owned MMIO. The driver caches only pointers and has no writable properties or persistent storage.

Dependencies and integration: depends on platform resources, OF compatible `google,goldfish-battery`, ACPI ID `GFSH0001`, MMIO accessors, shared IRQ registration, and power-supply core registration.

Risks and test signals: property values are trusted exactly as emulator registers provide them, so unit/enumeration correctness depends on the virtual device contract. Test MMIO mapping failures, missing IRQ, AC and battery property reads, interrupt status clearing, simultaneous battery/AC events, shared IRQ `IRQ_NONE` behavior, OF and ACPI matching, and that interrupt enable is written after supplies are registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/goldfish_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/gpio-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/gpio-charger.c

Purpose: provides a generic charger power-supply driver for hardware that reports online/charge status through GPIOs and optionally selects charge-current limits through a GPIO bitfield.

Important APIs/types/functions: `struct gpio_charger` stores optional online and charge-status GPIOs, current-limit GPIO array, sorted mapping table, cached current limit, IRQs, wake state, and descriptor. `set_charge_current_limit()` maps a requested current to the nearest safe mapping entry and drives GPIOs. `gpio_charger_get_property()` and `gpio_charger_set_property()` expose online/status/current limit.

Control flow: probe accepts platform data or firmware node configuration, acquires optional unnamed online GPIO and `charge-status` GPIO, initializes current-limit mapping from `charge-current-limit-gpios` and `charge-current-limit-mapping`, builds the property list only for available features, determines the charger type, registers the supply, requests edge IRQs for status GPIOs, initializes wakeup, and stores driver data. GPIO IRQs simply notify the power supply. Suspend enables wake on the online IRQ when allowed; resume disables wake and notifies.

State and persistence: current limit and wake-enabled state are cached in memory. GPIO output levels program board hardware but are not persisted by the driver. Firmware/platform data supplies names, type, supplicants, and mapping/defaults.

Dependencies and integration: depends on GPIO descriptor APIs, firmware properties or `gpio_charger_platform_data`, optional OF compatible `gpio-charger`, power-supply core, and device wakeup support.

Risks and test signals: `gpio_charger_get_type()` can warn with an uninitialized string when the `charger-type` property is absent. Suspend only handles `irq`, not `charge_status_irq`, for wake. Test property-list combinations, sorted mapping validation, default limit fallback, current-limit rounding safety, GPIO polarity, IRQ notification, wakeup enable/disable, and platform-data vs firmware-node paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/gpio-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/huawei-gaokun-battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/huawei-gaokun-battery.c

Purpose: implements adapter and battery power supplies for Huawei Matebook E Go systems using the Gaokun EC auxiliary device. It reports EC battery/adapter data and exposes Huawei smart/adaptive charge controls.

Important APIs/types/functions: `struct gaokun_psy` stores EC pointer, notifier, adapter/battery supplies, cached battery status/info blocks, strings, charge state, online state, and presence. `gaokun_psy_get_adp_property()` reports USB-C adapter online/type. `gaokun_psy_get_bat_property()` reports status, presence, technology, cycle count, voltage/current/charge/capacity, thresholds, and strings. Sysfs attributes are `battery_adaptive_charge` and `smart_charge_delay`.

Control flow: probe registers adapter and battery supplies, attaches smart-charge sysfs groups to the battery supply, initializes presence/info/vendor/model/serial caches, and registers for EC notifications. Battery property reads refresh cached status if present and cache time expired. Smart-charge threshold setters read the EC smart-charge buffer, adjust start/end ordering, and write it back. EC notifications refresh adapter or battery caches and emit `power_supply_changed()` for relevant events.

State and persistence: cached EC data is valid for `CACHE_TIME` milliseconds. Smart-charge enable, delay, and thresholds are persisted/owned by EC firmware after setter calls. The driver mutates the model string by forcing byte 14 to `A` as a local fixup.

Dependencies and integration: depends on the Gaokun EC platform API, auxiliary bus matching, notifier registration, power-supply core, little-endian packed EC data layouts, and EC smart-charge helper functions.

Risks and test signals: this snapshot duplicates the battery-present check in `gaokun_psy_get_bat_property()`. Threshold setters can overflow/underflow when asked to set start above 99 or end below 1 because they adjust the opposite threshold by plus/minus one without explicit bounds checks. Test absent battery, cache expiration, EC event ordering/delays, smart-charge sysfs parsing, threshold boundaries, string reads/model fixup, notifier unregister, and EC read/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/huawei-gaokun-battery.c -->
