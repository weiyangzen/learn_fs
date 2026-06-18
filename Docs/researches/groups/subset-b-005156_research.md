# subset-b-005156 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_ac_power.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_ac_power.c

## Purpose

`axp20x_ac_power.c` registers the ACIN mains power-supply interface for X-Powers AXP20x, AXP22x, and AXP813 PMIC variants. It exposes AC adapter presence, online state, health, and, on ADC-capable AXP20x variants, instantaneous ACIN voltage/current through the Linux power-supply class. AXP813 has a different feature set: it does not expose ACIN ADC channels here, but it exposes writable ACIN path enable, hold voltage, and input-current limit controls.

## Important APIs, Types, And Functions

The central runtime object is `struct axp20x_ac_power`, which stores the parent regmap, registered `power_supply`, optional IIO ACIN voltage/current channels, the AXP813 path-select capability flag, and a flexible IRQ array. `struct axp_data` provides variant data: the `power_supply_desc`, IRQ names, whether ACIN ADC channels are required, and whether `AXP813_ACIN_PATH_CTRL` path selection applies.

`axp20x_ac_power_get_property()` implements `HEALTH`, `PRESENT`, `ONLINE`, `VOLTAGE_NOW`, `CURRENT_NOW`, `VOLTAGE_MIN`, and `INPUT_CURRENT_LIMIT` depending on the active descriptor. It reads `AXP20X_PWR_INPUT_STATUS` for ACIN present/available bits, uses IIO for ADC-backed properties, and decodes AXP813 `VHOLD` and current-limit fields. `axp813_ac_power_set_property()` writes AXP813 `ONLINE`, `VOLTAGE_MIN`, and `INPUT_CURRENT_LIMIT` after range checks. `axp20x_ac_power_irq()` only calls `power_supply_changed()`.

## Control Flow

Probe rejects disabled device-tree nodes, obtains the parent `axp20x_dev`, selects variant data from the OF match, allocates state sized for the IRQ count, optionally gets `acin_v` and `acin_i` IIO channels, registers the power supply, then maps named platform IRQs through the parent regmap IRQ controller and requests them. IRQs are requested after registration because they may fire immediately.

Suspend/resume treats the first IRQ, `ACIN_PLUGIN`, as the wake source when the power-supply device may wake the system. Remaining nested threaded IRQs are explicitly disabled during suspend and re-enabled on resume.

## State And Persistence

The driver keeps minimal cached software state: pointers, capability flags, and virtual IRQ numbers. User-visible values are read live from PMIC registers or IIO channels. AXP813 writes persist in PMIC hardware registers until firmware, another driver, or reset changes them. There is no nonvolatile storage or delayed work.

## Dependencies And Integration Points

The driver depends on the AXP20x MFD parent for regmap and regmap IRQ data, OF compatible strings, IIO channels named `acin_v`/`acin_i` for AXP20x, and the power-supply framework. It integrates via compatibles `x-powers,axp202-ac-power-supply`, `x-powers,axp221-ac-power-supply`, and `x-powers,axp813-ac-power-supply`.

## Risks And Edge Cases

AXP813 field conversion is step-based and truncates unsupported values; callers must use exact supported ranges. `ONLINE` is filtered by ACIN path-select on AXP813, so ACIN can be electrically available while reported offline. IIO channel absence returns probe deferral only for `-ENODEV`; other IIO errors abort probe. Suspend assumes IRQ ordering matches the `axp20x_irq_names[]` array, with plugin first.

## Test Signals

Compile with AXP20x MFD, power-supply, IIO, and PM sleep enabled. Runtime tests should verify AC plug/removal interrupts, ACIN voltage/current scaling on AXP20x, AXP813 writable `online`, `voltage_min`, and `input_current_limit`, and wake-from-suspend only on ACIN insertion. Fault injection should cover regmap read failures and missing IIO channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_ac_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_battery.c

## Purpose

`axp20x_battery.c` implements the battery power-supply driver for AXP209, AXP221, AXP717, and AXP813 PMIC battery/charger blocks. It reports battery presence, charge status, health, voltage/current, capacity, charge current limits, charge voltage limits, and minimum voltage cutoff, with variant-specific register encodings and IIO channel requirements.

## Important APIs, Types, And Functions

`struct axp20x_batt_ps` stores regmap, device, registered battery supply, IIO channels, maximum constant charge current, variant callbacks, and AXP717 thermistor-disable state. `struct axp_data` describes constant-charge-current scaling, register/mask selection, fuel-gauge validity behavior, power-supply descriptor, max-voltage callbacks, IIO setup, and battery-info programming.

Classic AXP20x/22x/813 paths use `axp20x_battery_get_prop()` and `axp20x_battery_set_prop()`. AXP717 uses `axp717_battery_get_prop()` and `axp717_battery_set_prop()` because status, presence, faults, CV voltage, current limit, and poweroff voltage live in different registers. Voltage-limit helpers decode/encode safe CV values; the setters intentionally reject high lithium-unsafe values such as AXP20x 4.36 V, AXP717 4.35/4.4/5.0 V, and AXP22x 4.22/4.24 V. `axp209_set_battery_info()` and `axp717_set_battery_info()` apply firmware battery information after registration.

## Control Flow

Probe rejects disabled OF nodes, allocates state, gets the parent regmap, selects variant data from OF, configures required IIO channels, registers the battery power supply, reads optional `power_supply_battery_info`, applies design voltage/current values, then initializes `max_ccc` from the current hardware setting. There are no local IRQ handlers; state changes are surfaced by polling properties or external power-supply notifications from other drivers.

## State And Persistence

The driver keeps `max_ccc` as policy state used to bound later current writes. Register writes change PMIC charger configuration: charge enable, CV voltage, constant charge current, poweroff/min voltage, and on AXP717 TS-pin disable. AXP717 `HEALTH` reads clear fault bits by writing them back, so health queries have side effects intended to allow recurring faults to reappear.

## Dependencies And Integration Points

The file integrates with the AXP20x MFD regmap, OF match table, IIO channels (`batt_v`, `batt_chrg_i`, and for classic variants `batt_dischrg_i`), and generic power-supply battery-info parsing. AXP717 also reads the firmware property `x-powers,no-thermistor` and expects monitored battery data before disabling the TS pin.

## Risks And Edge Cases

`axp20x_power_probe()` unconditionally refreshes `max_ccc` from the register after applying battery info, which can override the intended firmware-derived software maximum. AXP717 `CONSTANT_CHARGE_CURRENT_MAX` returns the current programmed charge current but also uses that property as the writable current limit, unlike classic variants where current and max-current are distinct. AXP717 current reporting carries a documented unknown offset and is left raw. Missing or invalid fuel-gauge-valid bits can make capacity return `-EINVAL` on AXP22x/813.

## Test Signals

Build coverage should include all compatibles. Runtime tests should verify IIO scaling, capacity-valid behavior, no-battery capacity behavior on classic variants, AXP717 fault-to-health mapping and fault clearing, safe voltage rejection, charge enable/disable through `STATUS`, DT battery-info application, and `x-powers,no-thermistor` behavior on boards without a battery thermistor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_usb_power.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_usb_power.c

## Purpose

`axp20x_usb_power.c` exposes the USB/VBUS input of AXP192, AXP202, AXP221, AXP223, AXP717, and AXP813 PMICs as a USB power supply. It reports VBUS health, presence, online state, voltage/current measurements where supported, input current limits, and USB charger type for variants with BC1.2 detection. Some variants also allow forcing the VBUS input offline.

## Important APIs, Types, And Functions

`struct axp20x_usb_power` stores the parent device/regmap, optional regmap fields, registered supply, variant data, optional IIO channels, delayed VBUS-detection work, DT maximum input current, cached VBUS status, and IRQ array. `struct axp_data` provides descriptor, IRQ names, current-limit table, reg fields, polling requirement, and callbacks for VBUS polling and ADC/IIO setup.

`axp20x_usb_power_get_property()` handles classic variants. It decodes `AXP20X_PWR_INPUT_STATUS`, `AXP20X_VBUS_IPSOUT_MGMT`, optional VBUS-valid fields, BC-detect fields, IIO or raw ADC values, and current-limit table selectors. `axp717_usb_power_get_property()` handles AXP717-specific status, fault, voltage-limit, current-limit, USB type, and voltage readings. Setters validate Vhold/current ranges, clamp to `input-current-limit-microamp`, disable BC1.2 before manual current writes to avoid races, and use either table selectors or AXP717 linear register formulas.

## Control Flow

Probe selects variant data, allocates state sized for IRQs, allocates mandatory and optional regmap fields, parses the DT maximum input current, initializes delayed work, enables VBUS monitoring and ADC/IIO channels when present, enables BC1.2 detection when available, registers the power supply, requests named regmap IRQs, and starts polling for variants needing it. IRQ handlers signal `power_supply_changed()` and debounce VBUS polling by 50 ms.

## State And Persistence

The driver caches `old_status` and `online` for polling decisions. Hardware state persists in PMIC registers: monitor enable, ADC enable, BC1.2 enable, Vhold, current limits, and optional VBUS disable. AXP717 health reads clear VBUS/VSYS fault bits by writing the fault register.

## Dependencies And Integration Points

It depends on the AXP20x MFD parent, regmap fields, regmap IRQs, IIO or raw AXP ADC access, `devm_delayed_work_autocancel()`, power-supply USB type support, and OF compatibles for six PMIC variants. It also integrates with firmware through `input-current-limit-microamp`.

## Risks And Edge Cases

AXP221/223/813 polling only runs while offline; wrong cached `online` state can delay change reporting. Current-limit tables contain `-1` unsupported entries, so setting `-1` is explicitly rejected and reads clamp out-of-range selectors to the table maximum. `ONLINE` writeability is intentionally exposed only when the register bit disables VBUS, because older variants interpret the bit oppositely. AXP717 raw ADC conversion uses `% AXP717_ADC_DATA_MASK`, which is unusual for masking and worth testing. Manual current writes disable BC detection until cable status changes re-enable it.

## Test Signals

Tests should cover plug/removal IRQs, debounce/poll behavior on AXP221/223/813, BC1.2 type mapping, current-limit clamping to DT maximum, VBUS disable on AXP813, AXP717 overvoltage health clearing, IIO and non-IIO ADC paths, and suspend/resume wake behavior with only `VBUS_PLUGIN` as wake IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_usb_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp288_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/axp288_charger.c

## Purpose

`axp288_charger.c` is the native charger driver for the AXP288 PMIC used on Intel Bay Trail and Cherry Trail tablets. It exposes the charger as a USB power supply, manages constant charge current/voltage and input-current limits, reacts to charger-type and OTG extcon events, and applies hardware initialization and device-specific DMI quirks.

## Important APIs, Types, And Functions

`struct axp288_chrg_info` contains the parent regmap/IRQ controller, registered USB supply, mutex, charger and OTG extcon notifier state, current/voltage limits, cached input/op/backend registers, and a validity timestamp. `axp288_charger_set_cc()`, `axp288_charger_set_cv()`, `axp288_charger_set_vbus_inlmt()`, `axp288_charger_vbus_path_select()`, and `axp288_charger_enable_charger()` are the core register writers.

`axp288_charger_usb_update_property()` refreshes `AXP20X_PWR_INPUT_STATUS`, `AXP20X_PWR_OP_MODE`, and `AXP20X_CHRG_BAK_CTRL` with `iosf_mbi_block_punit_i2c_access()` held, then caches the result for 60 seconds. `axp288_charger_usb_get_property()` reports presence/online, health, current/voltage settings, and input-current limit. `axp288_charger_extcon_evt_worker()` maps SDP/CDP/DCP or HP Type-C DMI quirks to a current limit and enables charging.

## Control Flow

Probe first requires `acpi_quirk_skip_acpi_ac_and_battery()` so native drivers do not conflict with selected ACPI battery/AC drivers. It rejects devices where `AXP20X_CC_CTRL` is zero, allocates state, obtains the charger extcon `axp288_extcon`, optionally obtains an OTG host extcon (`INT3496:00` or `intel-int3496`), initializes charger hardware, registers the power supply, registers extcon work/notifiers, schedules initial cable and OTG processing, and requests all charger IRQs.

## State And Persistence

The driver caches charger register state and invalidates it on property writes, IRQs, and extcon changes. Hardware writes persist in AXP288 registers: temperature thresholds, charge-output behavior, termination current, OCV calibration disable, Vhold or HP vbus-path enable, charge CC/CV, charger enable, and VBUS input-current limit. `max_cc` and `max_cv` are initialized from firmware-provided register values and cap later user writes.

## Dependencies And Integration Points

Dependencies include the AXP20x MFD/regmap IRQ core, Intel IOSF MBI arbitration, x86 ACPI quirks, extcon charger-type provider `axp288_extcon`, optional USB-host extcon, DMI matching for HP Pavilion x2 Type-C variants, and the power-supply framework.

## Risks And Edge Cases

The driver intentionally uses native mode only on systems opted out of ACPI AC/battery. Incorrect ACPI quirk detection can cause duplicate or missing power supplies. Extcon charger-type detection can be in progress; the worker returns without changing limits until a type is known. OTG host mode forces reported present/online to false and disables VBUS path, so extcon ID errors can block charging. Cached state can be stale for up to 60 seconds unless invalidated. HP Type-C DMI behavior hardcodes 3 A and enables VBUS path at probe.

## Test Signals

Test charger registration on supported AXP288 systems, rejection when ACPI drivers should own the device, SDP/CDP/DCP current-limit mapping, HP Pavilion x2 Type-C behavior, OTG host attach/detach VBUS path control, all nine charger IRQs, P-unit I2C blocking/unblocking on error paths, and sysfs writes for CC, CV, and input-current limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp288_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp288_fuel_gauge.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/axp288_fuel_gauge.c

## Purpose

`axp288_fuel_gauge.c` is the native AXP288 battery fuel-gauge driver for Intel tablet-class systems. It reports battery status, presence, health, voltage, OCV, capacity, low-capacity alert threshold, technology, and, unless disabled by module parameter, charge/current values derived from coulomb-counter and IIO channels.

## Important APIs, Types, And Functions

`struct axp288_fg_info` stores regmap, six IRQs, three IIO channels, registered battery supply, mutex, static initial state, and cached measurement registers. `fuel_gauge_update_registers()` is the main refresh path: it blocks P-unit I2C access, reads input status and capacity, reads battery voltage IIO, reads OCV, optionally reads charge/discharge current and 15-bit coulomb-counter/design-capacity words, then caches results for 60 seconds.

`fuel_gauge_get_status()` derives charging, discharging, and full states from VBUS validity, fuel-gauge valid/capacity bits, charge direction, discharge current, and the `no_current_sense_res` mode. `fuel_gauge_get_property()` maps cached values to power-supply units. `fuel_gauge_set_property()` writes the low-capacity alert threshold. `axp288_fuel_gauge_read_initial_regs()` validates fuel-gauge enable/configuration, determines max design voltage, reads initial battery presence, and reads low-capacity threshold.

## Control Flow

Probe requires the native-driver ACPI quirk, applies DMI no-battery exclusions for mini PCs and HDMI sticks, allocates state, maps platform IRQs to virtual regmap IRQs, obtains global IIO channels by name because x86 lacks normal device/channel maps, validates initial PMIC state with IOSF P-unit access blocked, optionally removes current-related properties when `no_current_sense_res` is set, registers the battery supply, and requests threaded IRQs.

## State And Persistence

Measurements are cached for 60 seconds and invalidated on fuel-gauge IRQs or `external_power_changed()`. The only normal writable user state is `CAPACITY_ALERT_MIN`, persisted in `AXP288_FG_LOW_CAP_REG`. The module parameter `no_current_sense_res` changes the property surface and capacity source for the lifetime of the module.

## Dependencies And Integration Points

Dependencies include AXP20x MFD regmap/IRQ, Intel IOSF MBI, ACPI quirk helpers, DMI quirk matching, IIO channels named `axp288-chrg-curr`, `axp288-chrg-d-curr`, and `axp288-batt-volt`, and power-supply external-power notifications from the charger.

## Risks And Edge Cases

No-battery DMI matching is essential because some headless systems falsely report a battery. `fuel_gauge_desc.num_properties` is mutated globally when `no_current_sense_res` is set; this is acceptable for a single driver instance but risky for hypothetical mixed instances. Capacity-invalid bits only log an error and still return masked capacity. Missing platform IRQs are skipped during mapping, but the request loop later requests all six `info->irq[]` entries, so zero/uninitialized IRQ values are a risk if firmware omits entries. Current sign depends on charge-direction state and separate charge/discharge IIO channels.

## Test Signals

Tests should cover DMI no-battery exclusions, probe deferral for missing IIO channels, `no_current_sense_res` property count and capacity source, 15-bit valid-bit failures, low-capacity threshold writes, full-status heuristics near 90-100 percent, external-power invalidation, all six fuel-gauge IRQs, and IOSF unblock behavior after read failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp288_fuel_gauge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/bd71828-power.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/bd71828-power.c

## Purpose

`bd71828-power.c` implements AC and battery power-supply support for ROHM BD71815, BD71828, and BD72720 PMIC charger blocks. It reports DC input online/voltage/current limit and battery status, health, voltage, temperature, current, and charge behavior. The driver is shared across chips by a register-table abstraction.

## Important APIs, Types, And Functions

`struct pwr_regs` maps logical charger/battery registers to chip-specific addresses and masks. `struct bd71828_power` holds regmap, chip type, device, AC/battery supplies, selected register table, sense-resistor-derived current factor, and chip-specific callbacks for temperature and battery insertion.

Important helpers include `bd7182x_read16_himask()`/`bd7182x_write16()` for big-endian 16-bit PMIC registers, `bd71828_get_vbat()`, `bd71828_get_current_ds_adc()`, `bd71815_get_temp()`, `bd71828_get_temp()`, and `bd71828_charge_status()`. AC properties are implemented by `bd71828_charger_get_property()` and `bd71828_charger_set_property()`. Battery properties are implemented by `bd71828_battery_get_property()` and `bd71828_battery_set_property()`.

## Control Flow

Probe selects the correct regmap (`wrap-map` for BD72720), chooses register table and callbacks by platform device ID, reads the charger sense resistor property `rohm,charger-sense-resistor-micro-ohms` or defaults to 30 mOhm, initializes hardware, registers AC and battery supplies, requests chip-specific named IRQs, and enables wakeup. Hardware init optionally writes DCIN collapse limit, detects battery insertion using chip-specific CONF bits, enables watchdog auto mode, sets low-battery alarm threshold, and applies a BD71815 relax-state mask.

## State And Persistence

The driver has no measurement cache. Values are read directly from PMIC registers. Persistent hardware writes include DCIN collapse limit, battery-insertion latch clearing, watchdog auto mode, low-battery alarm threshold, BD71815 relax mask, AC input current limit, and battery charge enable/disable. Current scaling is software state derived from board sense resistance.

## Dependencies And Integration Points

It depends on ROHM MFD headers/regmap, platform IDs `bd71815-power`, `bd71828-power`, and `bd72720-power`, power-supply `CHARGE_BEHAVIOUR` support, fwnode board property for sense resistor, and named platform IRQ resources supplied by the parent MFD. The AC supply declares `bd71828_bat` as a supplicant.

## Risks And Edge Cases

`bd71815_get_temp()` computes `t = 200 - raw` but never assigns `*temp`, so the returned temperature value appears uninitialized for BD71815. `bd71828_battery_props[]` lists `POWER_SUPPLY_PROP_HEALTH` twice. `bd71828_init_hardware()` return value is ignored in probe, so hardware initialization failures may not abort registration. `bd7182x_get_irqs()` stops at the first failed IRQ request, so optional/missing IRQ naming must match exactly. Current direction is taken from the first byte read and reused across both instantaneous and average current reads.

## Test Signals

Tests should cover all three chip IDs, big-endian ADC conversions, sense-resistor scaling, BD72720 wrap-map access, charge-state-to-status/health mapping, AC input-current read/write boundaries, charge behavior toggling, battery insertion latch behavior, IRQ name coverage per chip, and the BD71815 temperature path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/bd71828-power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/bd99954-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/bd99954-charger.c

## Purpose

`bd99954-charger.c` is the I2C power-supply driver for the ROHM BD99954 charger. It programs a complete charging profile from firmware and generic battery information, exposes charger and battery-adjacent telemetry through one USB power supply, and handles the BD99954 interrupt hierarchy by acknowledging all active unmasked subinterrupts and refreshing cached charger state.

## Important APIs, Types, And Functions

`struct bd9995x_device` stores the I2C client, regmap, allocated `regmap_field` array from the header, chip ID/revision, parsed initialization data, cached `struct bd9995x_state`, and a mutex. `struct bd9995x_init_data` holds register-selector values for VSYS regulation, input-current limits, trickle/pre/fast charge currents, charge voltages, recharge voltage, overvoltage limit, and termination current.

`bd9995x_power_supply_get_property()` maps cached charge state and live regmap fields to power-supply properties. `bd9995x_get_chip_state()` reads charge-state and input-status fields and derives `online` from VCC or VBUS detection. `bd9995x_fw_probe()` reads `power_supply_battery_info` and ROHM DT properties, converts microvolt/microamp values to register selectors using `linear_range_get_selector_low_array()`, and stores the selectors. `bd9995x_hw_init()` resets the chip, writes a known charging configuration, unmasks interrupt groups, and caches initial state.

## Control Flow

Probe allocates state, initializes a paged 16-bit little-endian regmap with range-window mapping through `MAP_SET`, allocates every regmap field, verifies `BD99954_ID`, reads revision, registers the power supply early so battery-info parsing can use it, parses firmware values, resets and initializes hardware, registers a reset action for cleanup, and requests the active-low threaded IRQ.

The IRQ thread reads `INT0_STATUS` and `F_INT0_SET`, masks `INT0`, acknowledges active unmasked top-level bits, walks active substatus groups `INT1_STATUS` through `INT7_STATUS`, acknowledges active unmasked subbits, restores the top-level mask, refreshes chip state, and calls `power_supply_changed()`.

## State And Persistence

The cached state contains online, charger state, VBAT/VSYS status, and VBUS/VCC status. Hardware is reset at probe and again by devm cleanup, so the driver intentionally overwrites bootloader configuration. Programmed values persist in charger registers while the device remains powered. There are no writable power-supply properties in this driver.

## Dependencies And Integration Points

The C file depends heavily on `bd99954-charger.h` for register addresses, field IDs, field definitions, charge-state constants, interrupt masks, status bits, and manufacturer/IRQ names. Runtime dependencies include I2C, regmap field APIs, linear range helpers, firmware properties, generic power-supply battery info, and OF compatible `rohm,bd99954`.

## Risks And Edge Cases

The driver only supports chip ID `BD99954_ID` although the header defines BD99955/BD99956 IDs. It resets hardware at probe, which can surprise systems expecting firmware-preserved charger state. Missing required ROHM DT properties abort probe. Unsupported battery-info values are rounded down with a warning when possible, which may undercharge or lower current versus the requested profile. `bd9995x_get_prop_batt_current()` reports only positive `IBATP_VAL`, so discharge sign is not represented. IRQ recovery can permanently disable useful notifications if top-level unmask restore fails.

## Test Signals

Tests should verify regmap paging/endian behavior, chip-ID rejection, firmware value-to-selector conversion and rounding, hardware reset completion timeout, initialization field writes, power-supply property units, VCC/VBUS online derivation, battery temperature-to-health mapping, interrupt masking/ack/unmask sequencing, and cleanup reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/bd99954-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/bd99954-charger.h -->
# sources/distributed-fs/ceph-client/drivers/power/supply/bd99954-charger.h

## Purpose

`bd99954-charger.h` is the register and bitfield contract for the BD99954 charger driver. It defines chip IDs, command/register addresses across the paged extended register space, the full `enum bd9995x_fields` used to index the driver’s `regmap_field` array, field-to-register mappings, charge-state constants, status bits, interrupt masks, reset bits, and battery-temperature state encodings.

## Important APIs, Types, And Data

The most important exported data is `static const struct reg_field bd9995x_reg_fields[]`. Its indexes must match `enum bd9995x_fields`, ending at `F_MAX_FIELDS`, because the C file allocates one `regmap_field` for every array entry and later uses symbolic IDs such as `F_CHGSTM_STATE`, `F_VBUS_VCC_STATUS`, `F_ITERM_SET`, `F_INT0_SET`, and `F_CHIP_ID`.

Register constants cover base commands such as `PROTECT_SET` and `MAP_SET`, extended charger/status/config registers from `0x100` upward, ADC/measurement registers, interrupt set/status registers, OTP/SMBus/debug registers, and special debug windows at `0x214`/`0x21A`. The header also defines `CHGSTM_*` charger states, `STATUS_*` VBAT/VSYS and VBUS/VCC bits, `INT0_ALL` through `INT7_ALL` masks, `ALLRST`/`OTPLD` reset bits, and `ROOM`/`HOT*`/`COLD*`/`BATT_OPEN` battery-temperature codes.

## Control Flow

The header has no runtime control flow. Its definitions drive the C file’s initialization, property reads, and IRQ handling. Probe allocates fields from `bd9995x_reg_fields[]`; hardware init writes fields selected by the enum; IRQ handling uses `INT*_ALL` masks and `INT*_STATUS` addresses; property getters interpret `CHGSTM_*`, `STATUS_*`, and battery-temperature codes.

## State And Persistence

This file stores no state. It describes persistent hardware registers and volatile status/interrupt fields. The distinction between `INT*_SET` field entries and `INT*_STATUS` field entries matters: the C driver writes mask registers and separately acknowledges status registers. Reset bits in `SYSTEM_CTRL_SET` control hardware reset and OTP reload persistence.

## Dependencies And Integration Points

The header depends only on `<linux/regmap.h>` for `struct reg_field` and `REG_FIELD()`, but it is tightly coupled to `bd99954-charger.c`. Any enum reorder, register address change, or field-range correction must be reviewed with every `rmap_fields[F_*]` use in the C file.

## Risks And Edge Cases

The file is a dense hardware map; off-by-one bit ranges or enum/array mismatches would compile but program or read the wrong hardware fields. A suspicious mapping appears in the VBUS functional-control block: several `F_VBUS_*` fields are mapped to `VCC_UCD_FCTRL_SET` rather than `VBUS_UCD_FCTRL_SET`, which may be intentional silicon aliasing or a copy/paste error. The enum includes fields for BD99955/BD99956-related capability, but the C driver currently rejects non-BD99954 IDs. Interrupt masks include sparse bit ranges, so blindly assuming 16 valid bits for every INT group would be wrong.

## Test Signals

Static validation should check `ARRAY_SIZE(bd9995x_reg_fields) == F_MAX_FIELDS`, every field used by the C file has an initializer, field ranges fit 16-bit register values, and interrupt mask constants align with the `F_INT*_SET` field widths. Runtime tests should read chip ID/revision, exercise reset bits, confirm charge-state decoding, verify VBUS/VCC detection bits, and trigger representative INT1-INT7 events to confirm masks and status acknowledgements target the correct registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/bd99954-charger.h -->
