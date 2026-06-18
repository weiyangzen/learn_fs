# Research: subset-b-005164

Grouped research for Linux power-supply drivers under `sources/distributed-fs/ceph-client/drivers/power/supply`. Each section is delimited for reconciliation into its source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/rt9756.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/rt9756.c

## Purpose
Richtek RT9756/RT9757/RT9770 I2C charger driver. It exposes a USB charger power supply plus a synthetic battery power supply, controls charger enable, watchdog, operation mode, over-voltage/current thresholds, BC1.2 charger detection, ADC readings, and resets the chip at shutdown.

## Important APIs, Types, and Functions
Core state is `struct rt9756_data`, holding regmap, `regmap_field` handles, two `power_supply_desc` instances, cached charger event flags, sense-resistor values, model ID, and atomic USB type. `struct rt975x_dev_data` abstracts RT9756-family versus RT9770 register maps and init patches. Key functions are `rt9756_probe()`, `rt9756_register_psy()`, `rt9756_psy_get_property()`, `rt9756_psy_set_property()`, `rt9756_get_adc()`, `rt9756_irq_handler()`, and `rt9756_config_batsense_resistor()`.

## Control Flow
Probe selects match data, initializes regmap, bulk-allocates fields, checks Richtek device ID and revision/model, applies an init register patch, configures battery sense resistor scaling, registers the battery and USB power supplies, and requests the threaded IRQ. Runtime property reads either read fields, convert linear-range selectors, trigger one-shot ADC conversion under `adc_lock`, or return cached event/USB-type state. IRQ handling reads interrupt flags, starts BC1.2 detection on VAC insert, clears USB type on UVLO, updates USB type on BC1.2 completion, and notifies the power supply.

## State and Persistence
State is in hardware registers plus volatile driver cache. `chg_evt` stores the last read event flags used for health reporting until charging is enabled via `POWER_SUPPLY_PROP_STATUS`, which clears it. `usb_type` is atomic because it is updated from IRQ and read from property callbacks. No persistent storage is used; shutdown writes `F_REG_RST`.

## Dependencies and Integration Points
Depends on I2C, regmap/regmap-fields, linear ranges, power_supply, firmware properties, sysfs attributes, and an IRQ. Device tree compatible strings are `richtek,rt9756` and `richtek,rt9770`. The charger power supply is linked to its companion battery supply via `supplied_to`. Sysfs attributes `watchdog_timer` and `operation_mode` are attached to the charger power supply.

## Risks and Test Signals
Important risks are ADC timeout cleanup leaving ADC enable bits set on early returns, duplicate `POWER_SUPPLY_PROP_ONLINE` in the property list, unchecked mandatory IRQ availability, and health depending on cached flags rather than immediate status reads. Test with probe on all compatibles, property read/write coverage, BC1.2 IRQ events, shunt-resistor boundary values, sysfs store/show behavior, and shutdown reset observation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/rt9756.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/rx51_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/rx51_battery.c

## Purpose
Nokia RX-51/N900 platform battery driver. It exposes a simple battery power supply backed by IIO ADC channels for VBAT voltage, temperature, and BSI-derived design capacity.

## Important APIs, Types, and Functions
`struct rx51_device_info` stores the device, registered battery, descriptor, and three IIO channels. `rx51_battery_read_adc()` wraps `iio_read_channel_average_raw()`. Conversion helpers are `rx51_battery_read_voltage()`, `rx51_battery_read_temperature()`, and `rx51_battery_read_capacity()`. `rx51_battery_get_property()` maps those readings to power_supply properties.

## Control Flow
Probe allocates state, fills `bat_desc`, obtains `temp`, `bsi`, and `vbat` IIO channels, and registers `rx51-battery`. Property reads synchronously sample the required ADC. Temperature uses a direct table for low raw ADC values and binary search over an inverse lookup table for the rest.

## State and Persistence
The driver keeps no dynamic cached battery state and writes no hardware state. All exported values are computed on demand from ADC readings and fixed conversion tables.

## Dependencies and Integration Points
It is a platform driver matched by `nokia,n900-battery`, depends on IIO consumer channels named by firmware, and integrates only with the power_supply class.

## Risks and Test Signals
`POWER_SUPPLY_PROP_PRESENT` treats any nonzero return from voltage conversion as present, so negative ADC errors may be reported as present before final `INT_MAX/INT_MIN` filtering. The BSI capacity formula divides by `1024 - capacity`, so a raw value at or above 1024 is hazardous. Test ADC error propagation, raw temperature boundaries, BSI near 1024, and registration failure paths for missing IIO channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/rx51_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/s2mu005-battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/s2mu005-battery.c

## Purpose
Samsung S2MU005 PMIC fuel-gauge driver. It exposes voltage, average voltage, current, average current, capacity, and charging status for the PMIC battery gauge.

## Important APIs, Types, and Functions
`struct s2mu005_fg` holds device, 16-bit little-endian regmap, power supply, and `monout_mutex`. Conversion helpers read PMIC registers: `s2mu005_fg_get_voltage_now()`, `s2mu005_fg_get_voltage_avg()`, `s2mu005_fg_get_current_now()`, `s2mu005_fg_get_current_avg()`, `s2mu005_fg_get_capacity()`, and `s2mu005_fg_get_status()`.

## Control Flow
Probe initializes regmap, mutex, power supply, and a threaded IRQ. Direct properties read dedicated registers. Average voltage/current serialize access to `MONOUTSEL` and `MONOUT` because the monitor output register is multiplexed. IRQ sleeps briefly, then calls `power_supply_changed()`.

## State and Persistence
State is minimal and volatile. No persistent calibration or cached measurement is stored. The only mutable hardware selector is `MONOUTSEL`, protected by a mutex.

## Dependencies and Integration Points
Depends on I2C, regmap, IRQ, mutexes, firmware match data, and power_supply. Matched by `samsung,s2mu005-fuel-gauge`; descriptor is supplied through OF match data.

## Risks and Test Signals
Probe logs mutex and IRQ setup failures but does not return those errors, so a driver can bind without a requested IRQ or with a failed mutex init return path. Status inference depends on signed current conversion and treats `current_now == 0` as not charging regardless of average current. Test register endianness, negative current handling, MONOUT serialization, IRQ-less behavior, and capacity threshold for full status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/s2mu005-battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/samsung-sdi-battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/samsung-sdi-battery.c

## Purpose
Battery-characteristic provider for several Samsung SDI battery packs. It exports `samsung_sdi_battery_get_info()` so other power-supply drivers can obtain static `power_supply_battery_info` profiles by compatible string.

## Important APIs, Types, and Functions
`struct samsung_sdi_battery` pairs a compatible string, human-readable name, and populated `struct power_supply_battery_info`. The file contains OCV-capacity tables, voltage-to-internal-resistance tables for charging and discharging, a placeholder temperature-to-resistance table, and a maintenance-charge table. The sole exported function is `samsung_sdi_battery_get_info()`.

## Control Flow
Callers pass a device and compatible string. The function linearly scans `samsung_sdi_batteries`, returns `-ENODEV` if unmatched, otherwise returns a pointer to the static info and logs the selected battery name/capacity.

## State and Persistence
All data is static read-only table data except the returned pointer to static storage. There is no runtime state, no allocation, and no persistence beyond module lifetime.

## Dependencies and Integration Points
Depends on the power_supply battery-info data model and is exported GPL-only. It is consumed by battery/charger drivers that need boardfile-equivalent battery pack data without duplicating tables.

## Risks and Test Signals
Several comments identify missing or questionable data, especially temperature compensation and some minimum voltage/table choices. Since callers receive static pointers, they must treat data as immutable. Test compatible lookup success/failure, table ordering assumptions for `power_supply_ocv2cap_simple()`, and consumers using every populated field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/samsung-sdi-battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/samsung-sdi-battery.h -->
# sources/distributed-fs/ceph-client/drivers/power/supply/samsung-sdi-battery.h

## Purpose
Small public interface for the Samsung SDI battery profile provider. It lets consumers call `samsung_sdi_battery_get_info()` when `CONFIG_BATTERY_SAMSUNG_SDI` is enabled and receive a harmless `-ENODEV` stub otherwise.

## Important APIs, Types, and Functions
Declares or defines `samsung_sdi_battery_get_info(struct device *dev, const char *compatible, struct power_supply_battery_info **info)`.

## Control Flow
The preprocessor selects the external declaration when the provider is built in or as a module, otherwise compiles an inline stub returning `-ENODEV`.

## State and Persistence
No state. It only controls build-time linkage behavior.

## Dependencies and Integration Points
Requires `struct device` and `struct power_supply_battery_info` declarations from including contexts. It integrates consumers with the optional `CONFIG_BATTERY_SAMSUNG_SDI` provider.

## Risks and Test Signals
The header has no include guard beyond conditional compilation and assumes required type declarations are already available. Test all build combinations: provider enabled, module, and disabled consumer builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/samsung-sdi-battery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/sbs-battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/sbs-battery.c

## Purpose
Smart Battery System gas-gauge driver for SBS batteries and TI BQ20Z65/BQ20Z75 variants. It exposes rich battery telemetry, identity strings, manufacture date, capacity/energy values, health, presence, and status.

## Important APIs, Types, and Functions
`sbs_data[]` maps power_supply properties to SBS command addresses and ranges. `struct sbs_info` tracks I2C client, power supply, presence GPIO, cached strings, cached chemistry, retry counts, delayed work, mode mutex, and variant flags. Key paths include `sbs_update_presence()`, `sbs_read_word_data()`, `sbs_read_string_data()`, `sbs_get_property()`, `sbs_get_battery_capacity()`, `sbs_status_correct()`, `sbs_external_power_changed()`, and `sbs_suspend()`.

## Control Flow
Probe copies a descriptor, reads firmware/platform retry counts, acquires optional battery-detect GPIO, optionally verifies presence, initializes delayed work, registers the power supply, and requests GPIO IRQ if available. Property reads check GPIO presence when configured, then dispatch to presence/health, string, numeric, capacity-mode, serial, or manufacture-date handlers. External power changes start a short polling loop to detect status changes.

## State and Persistence
Driver state is volatile but includes meaningful caches: `is_present`, `technology`, string buffers, `last_state`, and `poll_time`. Presence changes disable PEC, invalidate cached strings/chemistry, and optionally disable charger broadcasts. It may write BatteryMode capacity mode temporarily and TI manufacturer sleep command on suspend.

## Dependencies and Integration Points
Depends on I2C SMBus word/block access, optional GPIO, OF/platform data, power_supply, delayed work, and SMBus alert callback. Compatible strings include generic SBS and TI variants. Module parameter `force_load` allows binding without detected battery.

## Risks and Test Signals
Global `sbs_serial` is shared across devices. Fallback string reads disable PEC and require byte/I2C-block functions. Capacity reads temporarily switch BatteryMode and rely on `mode_lock`. Presence changes can occur during property reads and trigger `power_supply_changed()`. Test PEC negotiation, no-GPIO and GPIO presence, TI health mapping, block-read fallback, concurrent capacity reads, suspend sleep command, and external-power polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/sbs-battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/sbs-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/sbs-charger.c

## Purpose
SBS smart-charger driver exposing charger status as a mains power supply. It reports battery presence, AC online state, charger status, and simple health from SBS charger status bits.

## Important APIs, Types, and Functions
`struct sbs_info` holds the I2C client, power supply, regmap, optional polling work, and last status register value. `sbs_get_property()` decodes `last_state`. `sbs_check_state()` refreshes the status register and notifies on changes. Probe sets up regmap, power supply, and either IRQ or polling.

## Control Flow
Probe initializes an SMBus-style 8-bit register/16-bit little-endian regmap, reads initial charger status, registers the power supply, then uses threaded IRQ when available or a 500 ms delayed-work polling loop otherwise. IRQ and polling both call `sbs_check_state()`.

## State and Persistence
Only `last_state` is cached. There is no persistent storage or runtime writes to charger configuration.

## Dependencies and Integration Points
Depends on I2C, regmap, power_supply, optional IRQ, and delayed work. It matches `sbs,sbs-charger` or I2C ID `sbs-charger`.

## Risks and Test Signals
Health assignment has an ordering issue: cold sets COLD, then a missing `else` before hot can be overwritten by GOOD when hot is not set. IRQ returns `IRQ_NONE` if status did not change, which can matter on shared lines. Test status bit decoding, polling mode, IRQ mode, cold/hot health, and regmap endianness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/sbs-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/sbs-manager.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/sbs-manager.c

## Purpose
Driver for SBS Smart Battery System Managers, including LTC1760. It exposes manager AC/charge-type properties, multiplexes access to up to four downstream smart batteries at address 0x0b, optionally provides GPIOs for battery presence, and forwards SMBus alerts to child battery drivers.

## Important APIs, Types, and Functions
`struct sbsm_data` tracks the manager client, I2C mux, power supply, selected channel, GPIO chip, LTC1760 capability flag, supported batteries, and last alert states. Key functions are `sbsm_probe()`, `sbsm_select()`, `sbsm_get_property()`, `sbsm_set_property()`, `sbsm_alert()`, `sbsm_gpio_setup()`, and `sbsm_do_alert()`.

## Control Flow
Probe validates address 0x0a and SMBus word support, reads supported battery mask, creates a locked I2C mux with one adapter per present battery, registers optional GPIO chip, and registers the manager mains power supply. Property reads query AC present and charge battery bits. LTC1760 supports writable fast/trickle charge type through the TURBO bit. Alerts compare current state against cached state and call child drivers' `alert()` callback under the selected mux child adapter.

## State and Persistence
`cur_chan`, `supported_bats`, `last_state`, and `last_state_cont` are volatile caches. The manager writes BATSYSSTATE to select a downstream battery and writes LTC TURBO for charge type.

## Dependencies and Integration Points
Depends on I2C, i2c-mux, GPIO provider APIs, power_supply, and firmware properties. Compatible strings are `sbs,sbs-manager` and `lltc,ltc1760`.

## Risks and Test Signals
Correct mux channel numbering is critical because `chan` is encoded directly into SMB_BAT bits. Alert forwarding walks child devices at address 0x0b and assumes child drivers implement alert. Test multi-battery mux access, LTC1760 charge-type writes, optional GPIO registration, AC-change notifications, and alert propagation to `sbs-battery`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/sbs-manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/sc2731_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/sc2731_charger.c

## Purpose
Spreadtrum SC2731 PMIC switch-charger driver. It exposes a USB charger power supply, configures termination current/voltage from battery info, and starts/stops charging in response to USB PHY charger-current notifications.

## Important APIs, Types, and Functions
`struct sc2731_charger_info` contains parent regmap, USB PHY, notifier, power supply, work item, lock, charging flag, register base, and current limit. Core functions include `sc2731_charger_hw_init()`, `sc2731_charger_work()`, `sc2731_charger_usb_change()`, `sc2731_charger_start_charge()`, `sc2731_charger_stop_charge()`, and property get/set callbacks.

## Control Flow
Probe gets the parent regmap and register base, registers `sc2731_charger`, initializes hardware termination settings, obtains the USB PHY, registers a notifier, and checks initial charger state. USB notifications store the notified current limit and schedule work. Work serializes with the lock, sets input and charge current, starts charging when limit is nonzero, or stops charging when limit becomes zero.

## State and Persistence
`charging` and `limit` are volatile software state. Hardware registers hold module enable, CC enable, power-down, current limit, charge current, and termination settings. No persistent storage is used.

## Dependencies and Integration Points
Depends on platform-device probing below a PMIC regmap parent, USB PHY notifier/current API, power_supply battery-info helpers, workqueue, mutex, and DT `reg` plus `phys`.

## Risks and Test Signals
`platform_set_drvdata()` is missing, yet remove uses `platform_get_drvdata()`, which can break notifier unregister. Hardware init falls back to default termination values when battery info is absent. Test notifier registration/removal, initial USB-present detection, set/get properties while not charging, current limit bucket mapping, and module disable on init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/sc2731_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/sc27xx_fuel_gauge.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/sc27xx_fuel_gauge.c

## Purpose
Spreadtrum SC27XX PMIC fuel-gauge driver. It exposes battery presence, voltage/current, OCV, boot voltage, capacity, charge counter, health, and calibration controls using PMIC FGU registers, NVMEM calibration, IIO channels, and battery-info OCV/resistance tables.

## Important APIs, Types, and Functions
`struct sc27xx_fgu_data` stores regmap, battery power supply, base, mutex, detect GPIO, IIO channels, calibration constants, battery tables, capacity state, boot voltage, and coulomb-counter state. Key functions are `sc27xx_fgu_hw_init()`, `sc27xx_fgu_get_boot_capacity()`, `sc27xx_fgu_get_capacity()`, `sc27xx_fgu_capacity_calibration()`, `sc27xx_fgu_interrupt()`, `sc27xx_fgu_bat_detection()`, suspend/resume callbacks, and property get/set callbacks.

## Control Flow
Probe acquires regmap/base/calibration resistance, IIO channels, battery-detect GPIO, registers the battery power supply, initializes hardware, installs disable cleanup, requests FGU and GPIO IRQs, and sets drvdata. Hardware init loads battery info, OCV table, resistance table, NVMEM calibration, enables FGU/RTC clock, clears interrupts, programs low-voltage and coulomb delta thresholds, computes boot capacity, and seeds the coulomb counter. Runtime capacity is initial capacity plus coulomb-counter delta with OCV-based calibration.

## State and Persistence
The PMIC user area stores boot mode and last capacity across non-first power-on. Driver state caches `init_cap`, `init_clbcnt`, `alarm_cap`, `min_volt`, `boot_volt`, tables, and calibration factors. Writable properties can save capacity, adjust calibration baseline, or change total capacity.

## Dependencies and Integration Points
Depends on PMIC regmap, NVMEM cell `fgu_calib`, IIO channels `bat-temp` and `charge-vol`, battery-detect GPIO, power_supply battery-info tables, and charger supplies named `sc2731_charger`, `sc2720_charger`, `sc2721_charger`, or `sc2723_charger`.

## Risks and Test Signals
Capacity correctness depends on calibration resistance, NVMEM data, OCV table ordering, and charger status lookup by fixed names. `sc27xx_fgu_get_status()` iterates all charger names and returns the last successful status, not the first. Test first and warm boot paths, user-area writes, NVMEM failures, low-voltage IRQ calibration, suspend interrupt enable/disable, GPIO presence IRQ, and writable property effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/sc27xx_fuel_gauge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/smb347-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/smb347-charger.c

## Purpose
Summit SMB345/SMB347/SMB358 charger driver. It exposes mains and/or USB power supplies, configures charger current/voltage/temperature behavior, handles charger interrupts, and registers a fixed 5 V USB VBUS regulator for OTG mode.

## Important APIs, Types, and Functions
`struct smb347_charger` stores regmap, mains/USB supplies, regulator, online state, configuration limits, thermal limits, feature flags, and enable polarity. Lookup tables convert hardware selectors for fast/precharge/termination/input/compensation currents. Important functions include `smb347_probe()`, `smb347_hw_init()`, `smb347_interrupt()`, `smb347_get_property()`, `smb347_irq_init()`, `smb347_usb_vbus_regulator_enable()`, and DT/battery-info parsing helpers.

## Control Flow
Probe parses firmware properties, registers enabled power supplies, overlays battery-info constraints, programs hardware while configuration writes are enabled, initializes IRQ support when available, and registers the USB VBUS regulator. Interrupts read STAT/IRQSTAT registers, report charger errors, termination/taper, timeout, and under-voltage input changes, then update online state and notify supplies. Regulator enable disables charging, optionally toggles INOK polarity, enables OTG, and restores current limit.

## State and Persistence
`mains_online`, `usb_online`, `irq_unsupported`, and `usb_vbus_enabled` are volatile software state. Hardware config registers are writable only when `CMD_A_ALLOW_WRITE` is set; comments describe volatile RAM mirrored from nonvolatile defaults after POR, but the driver itself does not persist new NVM settings.

## Dependencies and Integration Points
Depends on I2C, regmap with cache, power_supply, regulator framework, DT binding constants, firmware properties, optional IRQ, and battery-info data. Compatible strings support `summit,smb345`, `summit,smb347`, and `summit,smb358`.

## Risks and Test Signals
IRQs are disabled around property reads and write-window changes, so deadlock/latency should be checked. OTG regulator enable intentionally disables charging and may require platform-specific INOK toggling. Current conversion floors to supported table entries. Test mains-only, USB-only, dual-supply, no-IRQ, IRQ, OTG enable/disable, thermal limits from battery info, and remove/shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/smb347-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/stc3117_fuel_gauge.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/stc3117_fuel_gauge.c

## Purpose
STMicroelectronics STC3117 fuel-gauge driver. It initializes the gauge from battery info and shunt-resistor properties, keeps chip RAM state with CRC, periodically refreshes measurements, and exposes battery status, voltage, current, OCV, average current, capacity, temperature, and presence.

## Important APIs, Types, and Functions
`union stc3117_internal_ram` models the 16-byte RAM area with testword, HRSOC, config values, SOC, state, and CRC. `struct stc3117_data` stores regmap, delayed work, power supply, battery parameters, config values, and latest measurements. Key functions are `stc3117_probe()`, `stc3117_init()`, `stc3117_set_para()`, `stc3117_task()`, `stc3117_get_battery_data()`, `ram_read()`, `ram_write()`, and `fuel_gauge_update_work()`.

## Control Flow
Probe initializes regmap, CRC table, power supply, reads `shunt-resistor-micro-ohms` and battery info, calls `stc3117_init()`, creates delayed work, and schedules it immediately. Init validates device ID, computes CC/VM config values, validates RAM testword/CRC, programs OCV/SOC tables and configuration, restores SOC when valid, and stores a new CRC. The periodic task refreshes measurements, repairs invalid RAM, handles battery failure/POR, restarts the gauge if needed, updates state, writes HRSOC/SOC/CRC, and reschedules after 2 seconds.

## State and Persistence
Persistent-ish state lives in the STC3117 internal RAM and is guarded by CRC8. Software caches latest measurements in `struct stc3117_data` for property reads. There is no separate kernel mutex around property reads versus update work.

## Dependencies and Integration Points
Depends on I2C, regmap, power_supply battery-info, devm delayed work, CRC8 helpers, and firmware `shunt-resistor-micro-ohms`. Compatible string is `st,stc3117`.

## Risks and Test Signals
Bulk register reads ignore return values in some paths, signed current conversion appears to treat raw 16-bit values as unsigned, and property reads race with update work. `power_supply_put_battery_info()` is not called after reading battery info. Test RAM CRC recovery, POR/BATFAIL paths, work cancellation, signed current interpretation, missing battery info, shunt scaling, and concurrent sysfs reads during update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/stc3117_fuel_gauge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/surface_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/surface_battery.c

## Purpose
Microsoft Surface battery driver using the Surface System Aggregator Module. It maps SSAM battery status/static/dynamic requests to power_supply properties for Surface devices with BAT1 and Surface Book BAT2 batteries.

## Important APIs, Types, and Functions
`struct spwr_bix` and `struct spwr_bst` mirror ACPI `_BIX` and `_BST` payloads. `struct spwr_battery_device` stores the SSAM device, power supply descriptor, delayed update work, event notifier, mutex-protected cached `sta`, `bix`, `bst`, timestamp, and alarm threshold. Important functions include `spwr_battery_register()`, `spwr_battery_get_property()`, `spwr_notify_bat()`, `spwr_battery_update_bix_unlocked()`, `spwr_battery_update_bst_unlocked()`, alarm sysfs handlers, and resume/remove callbacks.

## Control Flow
Probe selects match data, initializes the battery object/notifier, validates `_STA`, loads `_BIX` and `_BST`, initializes the alarm to design warning capacity when present, selects charge or energy property sets based on power unit, registers the power supply, and registers an SSAM notifier. Property reads refresh `_BST` if the cache expired, reject non-present batteries except `PRESENT`, and convert little-endian SSAM fields into power_supply units. SSAM events refresh static or dynamic state and notify the power supply; external power changes schedule a delayed refresh for EC update latency.

## State and Persistence
The driver caches EC state for `cache_time` milliseconds under `lock`. `alarm` is stored in software and programmed to EC via `_BTP`. No disk persistence is used; state is reloaded from SSAM/EC on probe and resume.

## Dependencies and Integration Points
Depends on SSAM request/notifier APIs, power_supply, delayed work, sysfs attributes, jiffies cache timing, and unaligned little-endian access helpers. Device IDs match BAT/SAM and BAT/KIP instances.

## Risks and Test Signals
Event registration must use instance 0 and manually filter event instance IDs. Unit changes after registration are only warned via `WARN_ON`. Cached `_BST` can temporarily serve stale values. Test present/absent battery behavior, both mW and mA power-unit property sets, alarm read/write, SSAM event handling, external-power delayed refresh, resume recheck, and notifier unregister/work cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/surface_battery.c -->
