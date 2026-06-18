# subset-b-005161 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max17042_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max17042_battery.c

Purpose: implements the Maxim MAX17042/MAX17047/MAX17050/MAX17055/MAX77759 fuel-gauge driver, including direct I2C probing and MFD platform-subdevice probing for PMIC variants. It registers a battery power-supply device exposing voltage, capacity, charge, current, temperature, health, and time-to-empty/full data with chip-specific handling for current-sense and voltage-only configurations.

Important APIs/types/functions: `struct max17042_chip` holds the regmap, `power_supply`, chip type, platform data, delayed init work, IRQ, and task period. `max17042_get_property()`, `max17042_set_property()`, and `max17042_property_is_writeable()` implement the power-supply contract. Helper paths include `max17042_get_status()`, `max17042_get_battery_health()`, conversion reads for capacity/current registers, model/POR initialization helpers such as `max17042_init_chip()`, `max17042_init_model()`, `max17042_load_new_capacity_params()`, IRQ handling in `max17042_thread_handler()`, DT/platform/default pdata construction, and shared `max17042_probe()` reached by both I2C and platform drivers.

Control flow: probe validates SMBus word support, chooses the normal or MAX77759 regmap configuration, loads pdata from DT/platform/defaults, applies optional init register writes, disables current-sense behavior when configured, reads MAX77759 task period when needed, registers the battery supply, sets up a threaded alert IRQ when available, programs SOC thresholds, and either schedules POR initialization work or immediately marks initialization complete. Property reads reject with `-EAGAIN` until init completes, then read raw registers and convert to power-supply units. IRQ handling reads and clears alert bits, adjusts SOC thresholds after SOC min/max alerts, and calls `power_supply_changed()`. Suspend disables and enables wake on the IRQ; resume restores it and reprograms SOC thresholds.

State and persistence: runtime state is in `struct max17042_chip` and chip registers. POR/model initialization writes cell characterization and capacity/configuration registers and clears the POR bit, changing persistent gauge state on the device. Writable sysfs power-supply properties only update temperature alert thresholds. Platform/DT thresholds define health policy but are not persisted by the driver.

Dependencies and integration: depends on I2C, regmap, power-supply core, PM sleep, OF/ACPI matching, and `linux/power/max17042_battery.h` platform data definitions. It integrates with MFD-created platform devices for MAX8966/MAX8997/MAX77705/MAX77849-style battery subdevices, direct I2C devices, ACPI `MAX17047`, and DT aliases including `maxim,max77759-fg`.

Risks: initialization is asynchronous, so early consumers see `-EAGAIN`. `max17042_model_data_compare()` calls `memcmp()` with an element count instead of a byte count, so model verification may compare only part of the table. Many POR writes ignore return values, and platform data controls safety-critical limits. Current/capacity unit conversions depend on valid `r_sns` and task-period values. IRQ absence disables SOC alert threshold maintenance. Test signals include build coverage with OF/ACPI/MFD paths, probe on current-sense and voltage-only gauges, POR and non-POR boots, IRQ threshold notifications, suspend/resume wake behavior, temp-alert writes, and health/status conversion around threshold edges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max17042_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max1720x_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max1720x_battery.c

Purpose: implements the Maxim MAX17201/MAX17205 I2C ModelGauge m5 fuel-gauge driver. It exposes the main battery as a power-supply device and exposes the nonvolatile configuration block through read-only NVMEM cells plus temperature sysfs attributes for auxiliary/internal sensors.

Important APIs/types/functions: `struct max1720x_device_info` stores the volatile regmap, ancillary nonvolatile I2C client/regmap, and RSense. `max1720x_battery_get_property()` converts gauge registers into power-supply properties. Conversion helpers translate time, percent, voltage, capacity, signed current, and signed temperature. `max1720x_probe_nvmem()` creates the 0xb ancillary I2C device, reads `nRSense`, registers named NVMEM cells, and prepares the nonvolatile regmap. `max1720x_nvmem_reg_read()` backs NVMEM reads, and `temp_ain1/temp_ain2/temp_int` sysfs attributes read nonvolatile temperature registers.

Control flow: probe allocates device info, initializes the volatile I2C regmap with access/volatile tables and MAPLE cache, probes the ancillary NVMEM address, then registers a `max1720x` battery supply with the extra attribute group. Property reads pull fresh values from volatile registers, convert through RSense for current/capacity, map model IDs from `DEV_NAME`, and use a constant manufacturer string. Health reads status alert bits and writes back selected sticky alert bits so future events can be detected.

State and persistence: driver runtime state is limited to regmaps, the ancillary client, and cached RSense. NVMEM cells are registered read-only and root-only; the driver does not mutate gauge configuration except for clearing status events. If RSense is zero, it warns and uses a runtime default of 10 milliohms.

Dependencies and integration: depends on I2C, regmap access tables/cache, nvmem-provider, power-supply core, and unaligned register reads through regmap bulk operations. DT matching uses `maxim,max17201`; MAX17205 is inferred from the device-name register rather than a separate compatible.

Risks: capacity and current units are only as correct as nonvolatile RSense. `max1720x_nvmem_reg_read()` assumes even offsets/lengths matching its word-size/stride registration. Clearing alert bits in a read path can hide events from another consumer. Model-name reads return `-ENODEV` for unknown low-nibble IDs. Test signals include NVMEM cell reads, ancillary-client cleanup, RSense zero fallback, model ID mapping, status-alert health mapping, and register-cache behavior for volatile versus nonvolatile ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max1720x_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max1721x_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max1721x_battery.c

Purpose: implements 1-Wire support for MAX17211/MAX17215 standalone fuel gauges. It binds to 1-Wire family ID `0x26`, creates a unique battery power-supply name from the slave ROM ID, and reports gauge measurements plus cached manufacturer, model, and serial strings.

Important APIs/types/functions: `struct max17211_device_info` contains the dynamically named `power_supply_desc`, W1 device pointer, regmap, RSense, and cached string buffers. `devm_w1_max1721x_add_device()` is the add-slave entry point. `max1721x_battery_get_property()` handles power-supply reads. `get_string()` and `get_sn_string()` decode nonvolatile string/serial registers. Regmap access tables define valid volatile/nonvolatile W1 register windows.

Control flow: when a W1 slave appears, the driver allocates info, formats `max1721x-<romid>` as the battery name, configures a no-thermal battery descriptor, initializes a W1 regmap, reads RSense with a 10 milliohm fallback, reads manufacturer/device strings or falls back to default names based on `DEVNAME`, reads serial registers, and registers the power supply. Property reads access raw registers through W1 regmap, convert units, and for strings perform a dummy read before returning cached buffers.

State and persistence: runtime state is per-W1-slave and devm-managed through the slave device. Strings and RSense are cached at probe. The driver performs no persistent writes to nonvolatile gauge memory.

Dependencies and integration: depends on Linux W1 family registration, `devm_regmap_init_w1()`, and power-supply core. It exports `MODULE_ALIAS("w1-family-26")` for auto-loading.

Risks: `PRESENT` uses `!(reg & MAX172XX_BAT_PRESENT)` even though the bit comment says battery-connected, so polarity deserves hardware validation. The string buffers may contain embedded NULs or unterminated data if the chip returns unexpected characters, though allocation leaves trailing zeroes. Current conversion divides by RSense and relies on fallback for zero. Test signals include hotplug of multiple W1 gauges, W1 register read failure paths, fallback model/manufacturer naming, serial formatting, and property unit validation against known gauge readings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max1721x_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max77650-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max77650-charger.c

Purpose: implements the MAX77650/MAX77651 charger subdriver. It registers a USB-type power supply exposing charger status, online state, and charge type, configures optional DT input voltage/current limits, and responds to charger/input IRQs by enabling or disabling charging.

Important APIs/types/functions: `struct max77650_charger_data` stores the parent MFD regmap and device. `max77650_charger_get_property()` maps `STAT_CHG_B` detail fields to power-supply status, online, and charge type. `max77650_charger_set_vchgin_min()` and `max77650_charger_set_ichgin_lim()` apply table-based DT configuration. `max77650_charger_check_status()` handles `CHG` and `CHGIN` IRQs.

Control flow: probe obtains the parent regmap, requests named `CHG` and `CHGIN` IRQs, registers the power supply, applies `input-voltage-min-microvolt` and `input-current-limit-microamp` when present, and enables the charger. IRQ handling reads charger status, disables charging on undervoltage/overvoltage lockout, enables it when input is OK, and ignores transient debounce states. Remove disables charging.

State and persistence: no software state beyond regmap/device pointers. Hardware charger-enable and input-limit bits persist until changed by hardware reset or another driver. DT limit values must match table entries exactly.

Dependencies and integration: integrates with the MAX77650 MFD regmap/register definitions, platform-device IRQ resources, OF match `maxim,max77650-charger`, and the power-supply framework.

Risks: `MAX77650_CHGIN_OKAY` is defined as `0x11` while `CHGIN_DETAILS_BITS()` extracts only a 2-bit value, so the OK case may be unreachable and charging may not be re-enabled from the IRQ path. `MAX77650_CHARGER_CHG_CHARGING()` tests `> 1` on a single bit and may report false even when the bit is set. DT limits reject non-table values instead of rounding. Test signals include IRQ behavior for each CHGIN detail, online/status sysfs reads during active charging, DT limit table validation, and remove-path charger disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max77650-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max77693_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max77693_charger.c

Purpose: implements the Maxim MAX77693 charger platform subdriver. It exposes charger/battery state through a battery-type power supply and configures charger timers, top-off thresholds, constant voltage, system voltage, thermal regulation, battery overcurrent, and input voltage thresholds.

Important APIs/types/functions: `struct max77693_charger` holds the parent `max77693_dev`, registered supply, and DT/default configuration. Property helpers map charger detail, battery detail, online/present, input current limit, and fast-charge current registers. Sysfs attributes `fast_charge_timer`, `top_off_threshold_current`, and `top_off_timer` provide runtime tuning. `max77693_reg_init()` unlocks protected registers and applies safe defaults/DT settings.

Control flow: probe allocates state, parses OF properties or defaults, unlocks charger protection and initializes register fields, creates the three sysfs files, then registers the power supply. Property reads query parent MFD regmap registers and convert bit fields to power-supply enums or microamp values. Sysfs stores parse decimal input, validate/range-map it, and update the relevant register fields. Remove deletes created sysfs files.

State and persistence: configuration values are stored in hardware registers and may persist until PMIC reset. Software caches only the chosen boot configuration values; live sysfs reads fetch hardware state. No IRQ handling is present in this driver, so state changes are observed by polling property reads.

Dependencies and integration: depends on the MAX77693 MFD core/private register definitions, platform bus, power-supply core, regmap, and optional OF charger-node properties.

Risks: manual sysfs file creation has staged cleanup but is more error-prone than attribute groups. Several register writes rely on rounding down user values. The field `batttery_overcurrent` is misspelled but internally consistent. Lack of `power_supply_changed()` notifications means userspace may not get immediate charger-state events. Test signals include DT default validation, sysfs boundary tests, register-unlock failure handling, power-supply property mappings for all detail states, and probe cleanup after each sysfs/register failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max77693_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max77705_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max77705_charger.c

Purpose: implements an I2C charger driver for MAX77705. It exposes a USB power supply with online, present, status, charge type, health, voltage/current, and writable current-limit properties, initializes charger policy from battery info, and handles CHGIN/AICL interrupts.

Important APIs/types/functions: `struct max77705_charger_data` is defined in the companion header and stores regmap fields, workqueue, battery info, and `power_supply`. `max77705_chg_get_property()`, `max77705_set_property()`, and `max77705_property_is_writeable()` implement the power-supply interface. `max77705_charger_initialize()` programs protected charger defaults. `max77705_aicl_irq()` reduces input current until AICL clears. `max77705_chgin_irq()` queues work that calls `power_supply_changed()`.

Control flow: probe allocates state, duplicates the regmap IRQ chip descriptor to attach driver data, initializes an I2C regmap at the charger register base, allocates all regmap fields, registers the power supply, installs the regmap IRQ chip, allocates an ordered workqueue and CHGIN work, initializes charger registers using `power_supply_get_battery_info()`, requests CHGIN and AICL threaded IRQs, enables charging, and registers a devm disable action. Property reads map INT_OK/detail fields and regmap fields to status/health/current/voltage values. Writable current properties clamp through `max77705_set_integer()`.

State and persistence: the driver stores battery-info pointer and current register-field handles. Hardware registers hold charger configuration. AICL IRQ handling mutates input-current limit dynamically; disable action clears charger enable on teardown.

Dependencies and integration: depends on MAX77705 private/register-field definitions, regmap IRQ, I2C, devm work helpers, battery-info data from firmware, and power-supply core.

Risks: `max77705_get_status()` returns `POWER_SUPPLY_CHARGE_TYPE_NONE` when charging is disabled, which is a status-property enum mismatch. Several `regmap_read()`/`regmap_field_read()` calls ignore errors in helper functions. AICL decrements the raw current-limit selector without checking for zero underflow. The health path may leave `*value` unchanged for the prequalification battery state. Test signals include regmap IRQ registration, AICL underflow protection, status enum correctness, missing battery-info fallback, property write clamping, CHGIN notification work, and teardown charger disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max77705_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max77759_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max77759_charger.c

Purpose: implements the MAX77759 charger platform driver. It registers a USB power supply, manages charger mode transitions, exposes input/fast-charge/float-voltage limits, provides a fixed 5 V `chgin-otg` regulator for boost mode, tracks a TCPM source power supply, and handles charger IRQs.

Important APIs/types/functions: `struct max77759_charger` stores the regmap, supply, OTG regulator, power-supply notifier, delayed retry work, named IRQs, locks, and current charger mode. Linear-range tables map register selectors to current/voltage units. Key functions include `get_online()`, `get_status()`, `get_charge_type()`, `get_health()`, current/voltage limit getters/setters, `charger_set_mode()`, regulator ops for OTG, `max77759_charger_init()`, `psy_changed()`, `psy_work_item()`, and `max77759_init_irqhandler()`.

Control flow: probe inherits the parent OF node, obtains the `charger` regmap from the parent MFD, initializes locks, registers the power supply, initializes hardware by switching off, applying battery-info/default charge current and float voltage, disabling wireless input and watchdog behind protected-register unlock, registers the OTG regulator, creates delayed work, registers a global power-supply notifier, and requests all named IRQs. TCPM notifier events for `tcpm-source` schedule work that reads source online/current limit and turns charger buck mode on or off with retries. IRQs call `power_supply_changed()`, with a special overcurrent warning for `BAT_OILO`.

State and persistence: protected hardware registers store mode, limits, watchdog/wireless settings, and OTG state. `chg->mode` is the software authority for transition validation and online reporting. Retry counters and TCPM supply pointer are runtime-only and protected by mutexes.

Dependencies and integration: depends on MAX77759 MFD regmap definitions, platform IRQ resources named by the parent, power-supply notifier API, regulator framework, linear-range helpers, devm delayed work, and firmware battery-info data.

Risks: `max77759_charger_get_property()` writes the helper return value into `pval->intval` before checking errors; negative errors briefly become property values though the function returns the error. Mode transitions reject direct charger-to-OTG changes, so external regulator consumers and TCPM notifications must sequence through off. The notifier name match uses substring matching for `tcpm-source`, which could bind unintended supplies. Retry work disables charging on read failures. Test signals include all named IRQ resources, TCPM online/current change flows, retry exhaustion, OTG regulator enable/disable conflicts, battery-info absent defaults, protected-register relock on init failure, and linear-range selector edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max77759_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max77976_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max77976_charger.c

Purpose: implements an I2C charger driver for the Maxim MAX77976. It detects the chip ID/revision, configures charger buck mode, and registers a USB power supply with status, charge type, health, online, charge-current, input-current, model, and manufacturer properties.

Important APIs/types/functions: `struct max77976` stores the client, regmap, and regmap fields. Field definitions cover version/revision, input-good, battery/charger detail states, mode, charge current, protected-write bits, and input current. `max77976_get_property()`, `max77976_set_property()`, and `max77976_property_is_writeable()` implement power-supply behavior. `max77976_detect()` validates chip identity, and `max77976_configure()` unlocks protected fields and sets charger-buck mode.

Control flow: probe allocates state, initializes regmap and all regmap fields, reads and validates chip ID plus version/revision, writes protection and mode configuration, and registers the power supply. Property reads use regmap fields for enum mapping and integer conversions. Writable current properties clamp requested microamp values to supported ranges and write scaled selectors.

State and persistence: software state is minimal and devm-managed. Hardware mode/current settings persist until PMIC reset or another writer changes them. No IRQ, workqueue, or cached status state is maintained.

Dependencies and integration: depends on I2C, regmap fields, OF/I2C matching, and power-supply core. It is standalone rather than an MFD subdriver.

Risks: `max77976_get_integer()` clamps `regval * mult`, which reports selector zero as the minimum even if hardware selector zero could mean a lower/special value. Setters silently clamp out-of-range current requests instead of rejecting them. The driver unlocks charge protection but does not relock after configuration. It has no change notifications. Test signals include chip ID mismatch, version/revision read failures, writeability and current-bound tests, mode register verification, and property mappings across all documented charger/battery detail values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max77976_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max8903_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max8903_charger.c

Purpose: implements a GPIO-driven MAX8903 USB/adapter charger driver. It registers one power supply whose type changes between mains, USB, and battery depending on DC/USB input GPIO state, and reports status/online/health from charger and fault pins.

Important APIs/types/functions: `struct max8903_data` stores all GPIO descriptors, live `usb_in`/`ta_in`/`fault` state, and the mutable `power_supply_desc`. `max8903_setup_gpios()` acquires optional and required GPIOs, sets initial CEN/DCM output levels, and samples initial input state. IRQ handlers `max8903_dcin()`, `max8903_usbin()`, and `max8903_fault()` update state on GPIO edges. `max8903_get_property()` exposes status, online, and health.

Control flow: probe allocates state, sets up GPIOs, initializes the supply descriptor type from sampled input state, registers the power supply, and requests threaded edge IRQs for DC, USB, and fault pins when present. DC/USB IRQs update input booleans, enable/disable the charger via CEN depending on remaining power sources, switch DCM for DC preference, update the descriptor type, and call `power_supply_changed()` if type changes. Fault IRQ updates the health flag.

State and persistence: all state is runtime GPIO state plus output lines driven by the driver. There is no register persistence. The descriptor type is mutated after registration to reflect the active source.

Dependencies and integration: depends on gpiod descriptors, IRQs from GPIOs, OF compatible `maxim,max8903`, and power-supply core. Correct GPIO polarity flags in firmware are central to behavior.

Risks: `cen` is acquired unconditionally even though the comment says CEN is compulsory only when DOK is present, so USB-only designs still need a CEN GPIO. Fault changes do not call `power_supply_changed()`, so health updates may not notify userspace. Mutating `psy_desc.type` at runtime is unusual and can surprise consumers caching type. Test signals include DC-only/USB-only/both-present DTs, GPIO active-low polarity, CEN/DCM output behavior during plug/unplug, fault health notifications, and initial-state detection before IRQs fire.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max8903_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max8925_power.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max8925_power.c

Purpose: implements power-supply support for the MAX8925 PMIC. It registers separate AC, USB, and battery supplies, controls charger enable/current bits through the parent PMIC, reads battery/charger measurements through the ADC subclient, and handles PMIC charger IRQs.

Important APIs/types/functions: `struct max8925_power_info` stores parent chip, GPM/ADC I2C clients, supplies, online flags, platform configuration, and optional board `set_charger()` callback. `__set_charger()` toggles charger disable bit and board callback. `start_measure()` triggers ADC commands and reads 12-bit results. `max8925_ac_get_prop()`, `max8925_usb_get_prop()`, and `max8925_bat_get_prop()` expose supply properties. `max8925_charger_handler()` handles charger IRQs. `max8925_init_charger()` requests IRQs, samples boot state, disables charging, and programs top-off/fast-charge configuration.

Control flow: probe obtains platform/DT charger data from the parent, allocates state, registers AC/USB/battery supplies, copies platform settings, and initializes charger hardware/IRQs. IRQ handling reacts to adapter insert/remove, overvoltage, temp range, system-low, done, top-off, timer fault, and reset events, enabling/disabling charging as needed. Property reads query online flags, ADC voltage/current, and charger status register bits.

State and persistence: online flags and battery-present state are in memory and updated by IRQs/boot sampling. Charger enable, top-off threshold, and fast-charge current are hardware register state. Board-level charger callbacks may have side effects outside the PMIC.

Dependencies and integration: depends on the MAX8925 MFD core, platform data or DT child `charger` node, parent GPM/ADC I2C clients, manually requested PMIC IRQs, and power-supply core.

Risks: `REQUEST_IRQ` logs failures but does not abort, so the driver may run with partial event coverage. `max8925_deinit_charger()` frees an IRQ range regardless of which requests succeeded. ADC helper ignores write/read return values and can return stale zero-derived values. Battery current property comment says mA while power-supply convention expects microamps. Test signals include IRQ request failures, DT/platform pdata parsing, boot state detection, ADC conversion sanity, remove cleanup with partial IRQs, and charger enable/disable callback ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max8925_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max8971_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max8971_charger.c

Purpose: implements an I2C charger driver for MAX8971. It registers a USB power supply with status, charge type, USB type, health, online/present, charge/input current controls, model/manufacturer, sysfs timer/top-off attributes, IRQ handling, and optional extcon-driven charger-type configuration.

Important APIs/types/functions: `struct max8971_data` stores regmap fields, extcon notifier/work, USB type, timer/top-off cached values, and presence. `max8971_get_property()`, `max8971_set_property()`, and `max8971_property_is_writeable()` implement the power-supply interface. `max8971_update_config()` unlocks protected registers and applies timer/top-off/restart settings. Attribute group `max8971_groups` exposes fast-charge timer, top-off current, and top-off timer. `max8971_extcon_evt_worker()` maps extcon charger types to current limits. `max8971_interrupt()` handles charger reset/presence IRQs.

Control flow: probe initializes regmap/regmap fields, registers the supply with attribute group, masks AICL IRQ, requests the threaded IRQ, optionally locates an extcon through the OF graph, registers an extcon notifier, and schedules initial charger-type work. IRQ handling reads/clears interrupt state, updates `present`, reapplies config after chip reset, and notifies the power supply. Extcon work sets USB type and charge/input current limits under charger-protection unlock. Resume wakes the IRQ thread to refresh state.

State and persistence: `present`, `usb_type`, and requested timer/top-off values are cached. Hardware registers hold current limits and timer/top-off configuration but may reset on plug events, so the IRQ path reapplies cached config. Extcon state is external.

Dependencies and integration: depends on I2C, regmap fields, extcon, OF graph links to a connector/charger detector, devm delayed work, PM resume hook, and power-supply core.

Risks: `fast_charge_timer_store()` subtracts 3 from an unsigned `hours`, then stores in `int`, so small inputs rely on wraparound behavior before disabling. Extcon worker returns without calling `power_supply_changed()`, so USB type/current changes may not notify. `present` is only updated by IRQ, so initial state before an interrupt may be false. Test signals include extcon states for SDP/DCP/CDP/FAST/SLOW, IRQ reconfiguration after reset, sysfs boundary values, resume-triggered state refresh, and writable current clamp behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max8971_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max8997_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max8997_charger.c

Purpose: implements a MAX8997/MAX8966 battery-control platform subdriver. It exposes basic battery status, presence, and charger-online properties and optionally controls the parent charger regulator in response to MUIC extcon charger-type events.

Important APIs/types/functions: `struct charger_data` stores parent `max8997_dev`, registered battery supply, optional charger regulator, MUIC extcon, notifier, and work item. `max8997_battery_get_property()` reads `STATUS4` bits for full/charging/discharging, detected battery, and DC input. `max8997_battery_extcon_evt_worker()` maps extcon charger types to regulator current limits and enables/disables the regulator. Probe configures EOC and timeout registers from platform data.

Control flow: probe requires parent platform data, programs end-of-charge current and fast-charge timeout fields, allocates state, registers the battery supply, temporarily points the child OF node at the parent to get an optional `charger` regulator, obtains the `max8997-muic` extcon, and if both regulator and extcon are present, registers work/notifier handling. Extcon events schedule work that sets current limit to 450 mA for SDP, 650 mA for other charger classes, or disables the regulator when disconnected.

State and persistence: no cached battery state is kept; status is read from parent I2C registers. EOC/timeout and regulator current/enable state are hardware or regulator-framework state. Work items are devm-managed.

Dependencies and integration: depends on MAX8997 MFD register helpers, platform data, regulator consumer API, extcon MUIC device named `max8997-muic`, devm work helpers, and power-supply core.

Risks: hard-coded extcon lookup by name limits multi-instance support. If the optional regulator is absent, extcon control is skipped but extcon acquisition failures still abort probe. Register update return values are handled for initial config but regulator errors only log in work. Test signals include platform-data validation, EOC/timeout boundary programming, optional regulator absent/defer cases, extcon current-limit transitions, and `STATUS4` bit mapping for full/present/online.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max8997_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max8998_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max8998_charger.c

Purpose: implements the MAX8998/LP3974 battery-control platform subdriver. It reports basic battery presence, charger online state, and charging status, and programs charger end-of-charge, restart, and timeout thresholds from parent platform data.

Important APIs/types/functions: `struct max8998_battery_data` stores the parent PMIC device and battery supply. `max8998_battery_get_property()` reads `STATUS2` to expose `PRESENT`, `ONLINE`, and `STATUS`. `max8998_battery_probe()` validates platform data and writes `CHGR1`/`CHGR2` fields for EOC, restart level, and full timeout.

Control flow: probe requires parent platform init data, allocates state, validates EOC range or leaves it unchanged, maps restart values of 100/150/200 mV, disabled, or unchanged to register bits, maps timeout values of 5/6/7 hours, disabled, or unchanged, then registers the battery supply. Property reads always fetch fresh PMIC status over the parent I2C helper.

State and persistence: the driver caches no dynamic charger status. Charger thresholds are stored in PMIC registers and can remain until PMIC reset. Platform data is the only configuration source.

Dependencies and integration: depends on MAX8998 MFD helper functions, platform device data, and power-supply core. Matching is platform ID `max8998-battery`.

Risks: some `max8998_update_reg()` calls in the restart/timeout switch are not checked immediately; later failures may be missed. No extcon/regulator control or notifications are implemented. Probe fails when platform data is absent, so DT-only systems need parent translation. Test signals include valid/invalid platform settings, unchanged/disabled sentinel values, property bit mappings, I2C update failures, and module autoload through platform alias.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max8998_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/mm8013.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/mm8013.c

Purpose: implements a Mitsumi MM8013 fuel-gauge driver. It validates the device through the battery-ID register and exposes capacity, charge, current, cycle count, health, presence, status, temperature, time estimates, and voltage through a battery power supply.

Important APIs/types/functions: `struct mm8013_chip` stores the I2C client and regmap. `mm8013_checkdevice()` writes a BATID command and accepts two known battery-ID values. `mm8013_get_property()` maps word registers and flag bits into power-supply properties. `mm8013_regmap_config` uses 8-bit registers, 16-bit little-endian values, and single SMBus word transfers.

Control flow: probe checks SMBus word support, allocates state, initializes regmap, validates the device ID, and registers the `mm8013` battery supply. Property reads are direct register reads with simple unit conversion: mAh-like registers multiplied by 1000, currents converted from signed values and negated, voltage multiplied by 1000, temperature converted from decikelvin to decidegrees Celsius, and time estimates returning `-ENODATA` for `U16_MAX`.

State and persistence: the driver keeps no cached measurement state. It writes `0x0008` to `REG_BATID` during detection but otherwise only reads gauge state.

Dependencies and integration: depends on I2C SMBus word transfers, regmap, OF compatible `mitsumi,mm8013`, and power-supply core.

Risks: device detection depends on unclear BATID behavior and only accepts two IDs. Current sign is inverted, so validation against hardware convention is important. `PRESENT` is inferred from positive temperature, which can be false for invalid/very cold readings. Status gives discharging priority over charging/full flags. Test signals include BATID variants, SMBus capability failure, health flag priority, current sign/unit checks, `U16_MAX` time estimates, and little-endian regmap reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/mm8013.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/mp2629_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/mp2629_charger.c

Purpose: implements the Monolithic Power Systems MP2629 charger subdriver under the MP2629 MFD. It registers separate USB and battery power supplies, exposes ADC-backed input/battery measurements, supports writable charger/input/precharge/termination limits, reports faults/status, and provides a battery impedance-compensation sysfs attribute.

Important APIs/types/functions: `struct mp2629_charger` stores parent regmap, regmap fields, mutex, USB/battery supplies, IIO ADC channels, and latest fault. `mp2629_read_adc()`, `mp2629_get_prop()`, and `mp2629_set_prop()` centralize ADC and field conversions. `mp2629_charger_battery_get_prop()` and `_set_prop()` implement battery properties. `mp2629_charger_usb_get_prop()` and `_set_prop()` implement USB properties. `mp2629_irq_handler()` handles status/fault interrupts. `batt_impedance_compensation_show/store()` expose an extra sysfs control.

Control flow: probe obtains the parent MFD regmap and IRQ, allocates regmap fields, obtains all named IIO channels, registers a devm disable action, registers USB and battery power supplies, enables charging, disables watchdog, initializes the mutex, requests the threaded IRQ, and enables input-source/charging-change interrupts. Battery capacity is estimated as battery voltage divided by charge voltage limit. IRQ handling locks state, reads fault register and records/logs faults if present, otherwise reads status and notifies the relevant supply for input-source or charging changes.

State and persistence: `fault` is cached after a fault interrupt and used for health until another interrupt clears/overwrites it. Limit settings and impedance compensation are hardware register state. ADC values are read live from IIO channels. The devm disable action clears charge-control bits on teardown.

Dependencies and integration: depends on MP2629 MFD parent data, regmap fields, IIO consumer channels named for battery/system/input voltage/current, platform IRQ, sysfs attribute groups, and power-supply core.

Risks: USB power supply is registered without `drv_data`, but getters retrieve state from `psy->dev.parent`; this depends on parent device layout. Charge status/type compares shifted 2-bit values against `0x10`/`0x11`, making some cases unreachable after shifting. `fault` is not cleared when a later zero-fault interrupt is handled, so health can remain stale. Capacity estimation from voltage ratio is crude. Test signals include all IIO channels present, writable limit boundary tests, IRQ fault and status notifications, stale fault clearing, impedance sysfs parsing/rounding, and charge-type/status mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/mp2629_charger.c -->
