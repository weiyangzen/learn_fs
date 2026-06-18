# subset-b-005160 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ingenic-battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/ingenic-battery.c

## Purpose
This platform driver exposes the Ingenic JZ47xx battery voltage ADC as a Linux power-supply battery. It is intentionally small: it reads a single IIO channel named `battery`, consumes design voltage limits from the power-supply battery-info binding, reports current voltage, min/max design voltage, and derives `HEALTH` from whether the sampled voltage is below or above those design limits.

## Important APIs, Types, and Functions
The central state is `struct ingenic_battery`, holding the `struct device`, IIO channel, mutable `power_supply_desc`, registered `power_supply`, and `power_supply_battery_info`. `ingenic_battery_get_property()` implements `POWER_SUPPLY_PROP_HEALTH`, `VOLTAGE_NOW`, `VOLTAGE_MIN_DESIGN`, and `VOLTAGE_MAX_DESIGN`. `ingenic_battery_set_scale()` queries `iio_read_max_channel_raw()` plus available `IIO_CHAN_INFO_SCALE` entries and programs the smallest fractional-log2 scale that can cover the configured maximum battery voltage. `ingenic_battery_probe()` wires the platform device to the power-supply core and validates the mandatory battery-info voltage fields.

## Control Flow
Probe allocates state, gets the `battery` IIO channel, builds a descriptor named `jz-battery`, registers the power supply with `drv_data` and fwnode, reads battery info, validates design min/max voltage, then calls `ingenic_battery_set_scale()`. Property reads are synchronous IIO reads. Health first reads voltage in microvolts, then rewrites the same integer field to a power-supply health enum.

## State and Persistence
The only persistent driver state is the battery-info pointer and selected ADC scale. The ADC scale write persists in the backing IIO provider until changed elsewhere. Runtime voltage and health are not cached.

## Dependencies and Integration Points
The driver depends on an IIO provider that supports processed reads, max raw reads, available scale enumeration, and optional scale writes using `IIO_VAL_FRACTIONAL_LOG2`. It integrates with DT via `ingenic,jz4740-battery` and with the power-supply battery-info parser through the monitored battery fwnode.

## Risks
Scale selection assumes the available scale list is ordered as numerator/exponent pairs and that `max_raw * scale` fits the `u64` calculation. If design voltages are absent or wrong, probe fails or health classification is misleading. `get_property()` returns the IIO read status after using `val->intval`, so callers see an error if the read failed, but any temporary value in `val` is not meaningful.

## Test Signals
Useful checks are successful probe with valid battery-info DT, correct ADC scale selection for several maximum voltages, `VOLTAGE_NOW` matching the IIO channel conversion, and health transitions below min, inside range, and above max. Negative tests should cover missing IIO channel, missing design voltage properties, unsupported scale formats, and scale write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ingenic-battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/intel_dc_ti_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/intel_dc_ti_battery.c

## Purpose
This platform driver exposes battery telemetry for the Intel Dollar Cove TI PMIC coulomb counter on devices where ACPI battery handling is intentionally skipped. Because the PMIC counter is not autonomous across suspend or power-off, it delegates capacity estimation to `adc-battery-helper` and provides synchronized voltage/current samples to that helper.

## Important APIs, Types, and Functions
`struct dc_ti_battery_chip` embeds `struct adc_battery_helper` as its first member, then stores device, PMIC regmap, `VBAT` IIO channel, power supply, and coulomb-counter calibration terms. `dc_ti_battery_get_voltage_and_current_now()` enables the counter at a 15 ms interval, reads VBAT, waits for at least three samples, reads the latched accumulator and sample counter byte-by-byte, disables the counter, applies EEPROM gain and offset correction, and returns uV/uA values. `dc_ti_battery_hw_init()` calibrates the counter, reads PMIC revision, unlocks EEPROM, selects banks, validates trim revision, and loads `cc_gain` and `cc_offset`. Runtime PM operations are the helper suspend/resume callbacks.

## Control Flow
Probe first checks `acpi_quirk_skip_acpi_ac_and_battery()` and defers until ACPI glue provides a `monitored-battery` fwnode. It allocates state, gets the parent `intel_soc_pmic` regmap, obtains the `VBAT` IIO channel, optionally gets a charged GPIO, initializes PMIC hardware/calibration, registers the battery supply, then initializes the ADC helper with the sample callback and charged GPIO.

## State and Persistence
The driver persists EEPROM-derived calibration in `cc_gain` and `cc_offset`. The coulomb counter is normally disabled and only enabled for current sampling, so no long-term Linux-side accumulator is maintained. Capacity state lives in `adc-battery-helper`, while PMIC register state is touched during initialization and each current sample.

## Dependencies and Integration Points
It depends on the Dollar Cove TI PMIC MFD regmap, an IIO `VBAT` channel, the x86 ACPI battery quirk path, `adc-battery-helper`, optional `charged` GPIO, and runtime PM. The power-supply descriptor exposes the helper's standard property set and external-power notification hook.

## Risks
Register ordering matters: the PMIC latches the accumulator when `CC_ACC0` is read, so multi-register reads are intentionally avoided. Division by the sample counter assumes at least one sample was collected. EEPROM is relocked on the normal unsupported-trim path, but write/read errors before `out_relock` can leave the lock restoration best-effort only. Capacity is voltage-estimated, so current readings are momentary and not a full fuel-gauge state.

## Test Signals
Validate probe deferral, ACPI quirk gating, PMIC calibration on A0/A1 trim revisions, unsupported trim fallback, VBAT scaling, signed accumulator conversion, and current polarity. Runtime tests should confirm counter enable/disable writes around reads, helper suspend/resume behavior, and graceful errors on regmap or IIO failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/intel_dc_ti_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ip5xxx_power.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/ip5xxx_power.c

## Purpose
This I2C driver supports Injoinic IP5xxx power-bank controllers. It registers two supplies from one chip: `ip5xxx-battery` for charger/battery telemetry and writable charge settings, and `ip5xxx-boost` for the USB boost converter output. It also replays an initialization sequence after chip shutdown, because the controller may stop responding on I2C when VIN is absent and boost is off.

## Important APIs, Types, and Functions
`struct ip5xxx` contains the regmap, an `initialized` flag, nested `regmap_field` pointers for charger, boost, battery ADC, button, and WLED controls, plus per-chip scaling constants. `struct ip5xxx_regfield_config` describes field locations and unsupported fields for IP51xx and IP5306 families. `ip5xxx_read()` and `ip5xxx_write()` wrap regmap fields and clear `initialized` on bus errors. `ip5xxx_initialize()` disables light-load shutdown, enables load/VIN wake behavior, enables long-press shutdown, enables NTC when present, and configures button behavior. Battery helpers decode charger status, charge type, health, max voltage, ADC voltage/current/open-circuit voltage, and writable current/voltage/status properties. Boost helpers expose online state and undervoltage limit.

## Control Flow
Probe initializes an 8-bit I2C regmap, selects field config from OF match data or defaults to IP51xx, allocates supported regmap fields, copies scaling constants, then registers the battery and boost power supplies with shared driver data. Every get/set property first calls `ip5xxx_initialize()`, making initialization lazy and repeatable after an I2C error or chip power loss.

## State and Persistence
Driver state is mostly field mappings and cached scaling constants. Hardware state includes charge enable, voltage/current selections, boost enable, undervoltage threshold, NTC/button settings, and auto power behavior. The `initialized` boolean is a software cache of whether the wake/policy sequence has succeeded since the last bus error.

## Dependencies and Integration Points
It depends on I2C regmap, regmap-field allocation, OF compatibles for `injoinic,ip5108`, `ip5109`, `ip5207`, `ip5209`, and `ip5306`, and the power-supply core. Unsupported fields are represented by invalid reg ranges and become `NULL`, with accessors returning `-EOPNOTSUPP`.

## Risks
The write paths compute register values with limited range checking, so out-of-range user values can wrap or program unintended bit patterns if the power-supply core does not constrain them. `ip5xxx_setup_reg()` ignores individual field allocation failures, which turns later property access into unsupported-field errors rather than probe failure. ADC conversions are fixed formulas and must match chip variant. Mutable `psy_desc.type` is not used here, but shared state still means battery and boost operations can interleave without a mutex.

## Test Signals
Test both IP51xx and IP5306 field maps, lazy initialization after simulated I2C failures, battery status fallback through `chg_end`, unsupported-property behavior on IP5306 ADC-less fields, writable charge current/voltage/status, boost online and undervoltage writes, and ADC conversion sanity for positive and negative signed raw values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ip5xxx_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ipaq_micro_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/ipaq_micro_battery.c

## Purpose
This platform driver exposes battery and AC state from the HP iPAQ h3xxx Atmel microcontroller companion. It polls the MFD microcontroller every 100 seconds, caches the returned battery fields and thermal sensor value, and registers `main-battery` plus `ac` power supplies.

## Important APIs, Types, and Functions
`struct micro_battery` stores the parent `ipaq_micro`, a private workqueue, delayed update work, and cached AC, chemistry, voltage, temperature, and flag values. `micro_battery_work()` sends synchronous `MSG_BATTERY` and `MSG_THERMAL_SENSOR` messages through `ipaq_micro_tx_msg_sync()`, decodes the response, and requeues itself. `get_capacity()` maps high/low/critical flags to rough 100/50/5 percent values. `get_status()` maps unknown/full/charging flags to power-supply status. `micro_batt_get_property()` and `micro_ac_get_property()` serve cached values.

## Control Flow
Probe allocates state, gets the parent microcontroller object, creates a reclaimable per-CPU workqueue, registers autocancel delayed work, stores driver data, queues the first update almost immediately, then registers battery and AC supplies. Suspend cancels the delayed work synchronously. Resume queues the next update after the normal polling period.

## State and Persistence
All telemetry is cached in `struct micro_battery` and refreshed only by delayed work. There is no register programming or persistent hardware policy in this driver. `micro_batt_power` and `micro_ac_power` are file-scope pointers to devm-registered supplies, so only one instance is effectively expected.

## Dependencies and Integration Points
The driver depends on the `ipaq-micro` MFD transport and message IDs, the power-supply core, devm work helpers, and system sleep PM. Battery properties are marked `use_for_apm`, reflecting the legacy handheld platform integration.

## Risks
`micro_battery_work()` logs but does not abort when `rx_len < 4`, then still indexes response bytes up to 4, so malformed microcontroller replies can feed stale or invalid data. Thermal sensor response length is not checked. Property reads are unlocked while work updates fields, which is acceptable for simple integer fields but not strongly synchronized. The capacity mapping is coarse and flag-dependent, not coulomb or voltage based.

## Test Signals
Validate message decoding with normal and short replies, periodic requeue, suspend cancel/resume requeue, battery chemistry mapping, status priority for full versus charging, AC online reporting, and behavior when a second battery is reported. Hardware or mocked MFD tests should confirm response endian/scale for voltage and temperature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ipaq_micro_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/isp1704_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/isp1704_charger.c

## Purpose
This platform driver detects charger type through an NXP ISP1704/ISP1707 USB ULPI transceiver and exposes a USB power supply named `isp1704`. It distinguishes dedicated charging ports from USB/CDP-like sources, controls an enable GPIO, and coordinates with the USB gadget pull-up so charger detection can run before enumeration.

## Important APIs, Types, and Functions
`struct isp1704_charger` holds the power supply, mutable descriptor, enable GPIO, `usb_phy`, notifier, work item, model string, present/online flags, and current limit. `isp1704_charger_detect()` drives vendor power-control bits and polls `VDAT_DET`; `isp1704_charger_verify()` rejects PS/2-like false positives; `isp1704_charger_type()` temporarily manipulates ULPI function/OTG registers to distinguish DCP from CDP. `isp1704_charger_work()` handles `USB_EVENT_VBUS` and `USB_EVENT_NONE`, updates type/current, connects or disconnects the gadget, and calls `power_supply_changed()`. `isp1704_test_ulpi()` verifies scratch register access and NXP product IDs.

## Control Flow
Probe obtains the enable GPIO, gets the USB2 PHY by phandle or type, powers the transceiver, validates ULPI access and product ID, registers the power supply, initializes work and USB notifier, disconnects any existing gadget pull-up, powers down if no VBUS, and schedules detection if VBUS is already present on a B-device.

## State and Persistence
The driver caches `present`, `online`, `current_max`, and descriptor `type`. It temporarily saves/restores ULPI function and OTG control state during detection. The enable GPIO and gadget connect state persist across cable events until the next notifier work.

## Dependencies and Integration Points
It depends on USB PHY/OTG notifier events, ULPI register access, optional OF `usb-phy` phandle, a required `nxp,enable` GPIO, USB gadget APIs, and the power-supply core. It matches `nxp,isp1704` and `nxp,isp1707`.

## Risks
The power-supply descriptor type is mutated at runtime, which consumers may not expect if they cache type. A static mutex serializes detection globally across all instances. Notifier work assumes `isp->phy->otg` and possibly `gadget` are valid. Charger detection intentionally disconnects gadget pull-ups and can disrupt pre-existing enumeration. Some ULPI writes ignore return values.

## Test Signals
Exercise probe with valid and invalid ULPI IDs, VBUS insertion/removal, DCP versus CDP/USB detection, current limit clamping before high-speed chirp, gadget disconnect/connect behavior, existing VBUS at probe, enable GPIO transitions, notifier unregister/remove, and failed ULPI access during detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/isp1704_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/lego_ev3_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/lego_ev3_battery.c

## Purpose
This platform driver reports LEGO MINDSTORMS EV3 battery measurements using two IIO channels and a battery-type GPIO. It supports automatic Li-ion pack detection via a rechargeable switch and lets userspace mark an otherwise unknown AA pack as NiMH once during initialization.

## Important APIs, Types, and Functions
`struct lego_ev3_battery` stores voltage/current IIO channels, the rechargeable GPIO, registered supply, technology, and design voltage bounds. `lego_ev3_battery_get_property()` reports technology, voltage, design voltage min/max, current, and system scope. Voltage is calculated as voltage channel times two plus transistor Vce plus an estimated shunt drop from the current channel. Current is calculated from the current channel through the divider and shunt assumptions. `lego_ev3_battery_set_property()` permits only `POWER_SUPPLY_PROP_TECHNOLOGY` from unknown to NiMH and updates design limits. `property_is_writeable()` enforces that one-time policy.

## Control Flow
Probe gets the `voltage` and `current` IIO channels plus a required `rechargeable` GPIO. It samples the GPIO once because the pack cannot change without removal. A true GPIO selects Li-ion with fixed limits; false selects unknown/alkaline-style limits. It registers `lego-ev3-battery` with fwnode and driver data.

## State and Persistence
The chosen technology and design limits persist in memory until driver removal. The one writable path can change unknown to NiMH, but there is no way back to unknown. Measurements are read live from IIO and not cached.

## Dependencies and Integration Points
It depends on two processed IIO channels, a GPIO descriptor from DT, the power-supply core, and the `lego,ev3-battery` compatible. The driver is system-scope only and does not expose charger state.

## Risks
The Li-ion and alkaline/NiMH design voltage constants appear one decimal place larger than typical EV3 pack values if interpreted as microvolts, so downstream behavior depends on whether this source tree intentionally carries that scaling. Measurement formulas hard-code board resistor/transistor assumptions. The technology override is stateful and irreversible until reboot/remove.

## Test Signals
Validate IIO conversion math for voltage and current, GPIO true/false technology selection, one-time NiMH write behavior, rejection of Li-ion overrides, design voltage updates after NiMH selection, missing-channel probe errors, and fwnode registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/lego_ev3_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/lenovo_yoga_c630_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/lenovo_yoga_c630_battery.c

## Purpose
This auxiliary-bus driver exposes battery and USB-C adapter data from the Lenovo Yoga C630 embedded controller. It registers separate adapter and battery power supplies, caches expensive EC battery-status reads for ten seconds, and reacts to EC notifications for battery info, adapter, and status changes.

## Important APIs, Types, and Functions
`struct yoga_c630_psy` stores the EC handle, fwnode, notifier, mutex, supplies, cache timestamp, adapter state, capacity unit mode, static battery info, and dynamic telemetry. `yoga_c630_psy_update_bat_info()` reads presence, unit mode, design capacity/voltage, and full capacity, with 50 ms sleeps matching DSDT behavior. `yoga_c630_psy_maybe_update_bat_status()` refreshes status, remaining capacity, voltage, current, and power under cache control. `yoga_c630_psy_bat_get_property()` maps EC state to charge or energy properties depending on unit mode. `yoga_c630_ec_refresh_bat_info()` can unregister and re-register the battery supply if the EC changes units.

## Control Flow
Probe allocates state, registers the adapter supply first with `supplied_to` pointing at the battery name, reads battery info under the mutex, registers either the mA or mWh battery descriptor, then registers an EC notifier. Notifications call `power_supply_changed()` for relevant supplies and refresh battery info on `LENOVO_EC_EVENT_BAT_INFO`.

## State and Persistence
Static battery data and dynamic telemetry are cached in memory. `last_status_update` throttles EC reads. Unit mode controls which property list is registered; a unit change causes battery supply replacement. There is no persistent write path to the EC.

## Dependencies and Integration Points
It depends on the Yoga C630 EC platform data and read/notifier APIs, auxiliary bus matching through `YOGA_C630_MOD_NAME "." YOGA_C630_DEV_PSY`, mutex cleanup guards, the power-supply core, and fwnode inherited from the parent.

## Risks
`yoga_c630_psy_bat_get_property()` checks `bat_present` before refreshing status, so stale absence can hide a newly inserted battery until an info event. The error path calls `power_supply_unregister(ecbat->bat_psy)` even if registration did not happen, relying on the value being harmless. EC sleeps make property reads slow on cache misses. Power calculation multiplies current in mA by voltage in mV-like units and should be validated for expected power-supply units.

## Test Signals
Test adapter online/USB type, battery present and absent behavior, charge versus energy descriptor selection, cache expiry, EC notification handling, unit-mode re-registration, full/not-charging detection, signed current conversion, and failure paths for EC reads and notifier registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/lenovo_yoga_c630_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/lp8727_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/lp8727_charger.c

## Purpose
This I2C driver supports the TI/National LP8727 micro/mini USB IC with integrated charger. It detects attached power source type, controls DP/DM switch routing, configures charger parameters for AC or USB, and registers `ac`, `usb`, and `main_batt` power supplies.

## Important APIs, Types, and Functions
`struct lp8727_chg` stores device/client pointers, an I2C transfer mutex, registered supplies, platform data, detected device ID, selected charge parameters, IRQ number, delayed debounce work, and debounce duration. `lp8727_init_device()` clears interrupts and enables charge pump, ADC, ID200, interrupts, and charger detection. `lp8727_id_detection()` decodes ID/VBUS interrupt bits into TA, dedicated charger, USB charger, USB downstream, or none, chooses AC/USB charge parameters, and routes DP/DM. `lp8727_delayed_func()` reads interrupt registers after debounce, runs detection, re-enables charger detection, and notifies all supplies. Battery and charger property callbacks report online/status/health plus optional platform callback telemetry.

## Control Flow
Probe checks SMBus block support, parses DT or platform data for debounce and per-source charge params, allocates state, initializes hardware, registers three supplies, and requests a falling-edge threaded IRQ if present. The IRQ schedules delayed work instead of reading registers immediately.

## State and Persistence
Detected source type and active charge parameters persist in `devid` and `chg_param`. Hardware control registers persist switch routing and charger-control values. Battery voltage/capacity/temp/presence are not stored by this driver and are delegated to platform callbacks when present.

## Dependencies and Integration Points
It depends on I2C SMBus block operations, optional OF child nodes with `charger-type`, `eoc-level`, and `charging-current`, legacy `lp8727_platform_data`, IRQ lines, and the power-supply core. The battery descriptor uses `external_power_changed` to write selected charge current/EOC values.

## Risks
Several helper reads ignore return values and use the output byte regardless, so I2C failures can be misclassified. Battery property cases with missing callbacks return success without setting `val`, which can leak stale data to callers. `lp8727_parse_dt()` does not guard failed `of_property_read_string()` before `strcmp()`. The source detection state is IRQ/work driven and may be stale until an interrupt arrives.

## Test Signals
Validate register init, IRQ debounce, ID 0x5 and 0xB flows, DCP/USB/downstream routing, charge parameter writes on external-power change, absent IRQ polling behavior, DT parsing including malformed child nodes, high-temperature health mapping, and I2C error handling in detection helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/lp8727_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/lp8788-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/lp8788-charger.c

## Purpose
This platform driver is the charger subdevice for the TI LP8788 MFD. It exposes charger input status and battery telemetry, applies optional platform-defined charger register settings, reads battery voltage/temperature through IIO channels, handles MFD IRQ resources, and provides charger diagnostic sysfs attributes.

## Important APIs, Types, and Functions
`struct lp8788_charger` stores the parent `struct lp8788`, charger and battery supplies, charger work, IIO channels, mapped IRQs, and platform data. Charger callbacks report online and input current. Battery callbacks decode `LP8788_CHG_STATUS` into status, health, presence, voltage, capacity, temperature, charge current, and termination voltage. `lp8788_update_charger_params()` writes validated charger-register parameters from platform data. `lp8788_irq_register()` maps named IRQ resources through the parent IRQ domain and installs a threaded handler. Sysfs attributes expose textual charger state, EOC time, and EOC level.

## Control Flow
Probe gets parent MFD data, stores charger platform data, applies charger params, sets up optional IIO channels named by platform data, registers the charger and battery supplies, and registers IRQs. IRQ threads notify both supplies for input/state/EOC/battery-low/no-battery events and optionally schedule `charger_work` to call a platform `charger_event()` callback when input state changes.

## State and Persistence
The driver caches IRQ mappings and IIO channel pointers, but most status is read live from LP8788 registers. Platform charger parameter writes persist in hardware registers. The work item has no periodic behavior; it is event driven.

## Dependencies and Integration Points
It depends on the LP8788 MFD register helpers, MFD IRQ domain and named resources, optional `lp8788_charger_platform_data`, IIO channels for VBATT and battery temperature, sysfs attribute groups, and the power-supply core.

## Risks
Some property helpers ignore `lp8788_read_byte()` return values, so failed reads can convert uninitialized data. Capacity is a simple VBATT/max-vbatt percentage unless maintenance state reports 100 percent, not a true fuel-gauge estimate. `lp8788_charger_event()` assumes platform data and callback are valid when scheduled. IRQ setup can partially map IRQs before failure and returns warning-only from probe, so systems may run without notifications.

## Test Signals
Test platform parameter validation/write ranges, charger online and current calculations, all charger-state mappings, no-battery/bad-battery health, IIO voltage/temp reads and missing-channel errors, capacity clamping, sysfs output strings, IRQ mapping/freeing, and platform charger-event callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/lp8788-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/lt3651-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/lt3651-charger.c

## Purpose
This platform driver exposes an Analog Devices/Linear Technology LT3651 charger using GPIO status pins. It reports charger status, AC online state, and battery/charger health, and it requests GPIO IRQs when possible so userspace receives power-supply change events without polling.

## Important APIs, Types, and Functions
`struct lt3651_charger` stores the registered supply descriptor and three GPIOs: required `lltc,acpr`, optional `lltc,fault`, and optional `lltc,chrg`. `lt3651_charger_get_property()` maps `chrg` to charging/not-charging, `acpr` to online, and `fault` plus `chrg` to good, overheat, dead, unknown, or unspecified health. `lt3651_charger_irq()` only calls `power_supply_changed()`.

## Control Flow
Probe allocates state, obtains GPIOs, builds a descriptor named from the OF node, registers the mains supply, then attempts to translate each available GPIO to an IRQ and request rising/falling edge notification. IRQ failures are warned but not fatal. The driver matches deprecated `lltc,ltc3651-charger` and current `lltc,lt3651-charger` compatibles.

## State and Persistence
There is no cached telemetry and no hardware programming. All properties read the GPIOs live. The only persistent state is registered IRQ subscriptions and the descriptor name.

## Dependencies and Integration Points
It depends on gpiolib descriptor names with the legacy `lltc,` prefixes, optional GPIO IRQ support, an OF node, and the power-supply core. It is a simple status translator rather than a charger controller.

## Risks
The descriptor name uses `pdev->dev.of_node->name`, so non-OF instantiation would dereference a null OF node. GPIO polarity must be described correctly in firmware or status/health invert. If GPIO IRQ mapping is unavailable, userspace must poll. Health inference from `fault` and `chrg` depends on LT3651 pin semantics and optional `chrg` presence.

## Test Signals
Test all GPIO combinations, optional missing `fault`/`chrg`, IRQ request success/failure, power_supply_changed on edge interrupts, non-OF probe handling if relevant, and correct active polarity from device tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/lt3651-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ltc2941-battery-gauge.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/ltc2941-battery-gauge.c

## Purpose
This I2C driver supports LTC2941/LTC2942/LTC2943/LTC2944 battery gas gauges. It exposes accumulated charge, charge thresholds, voltage, temperature, and current according to chip capabilities, periodically detects charge-register changes, and disables continuous ADC conversion during shutdown for ADC-capable chips.

## Important APIs, Types, and Functions
`struct ltc294x_info` stores the I2C client, power supply, descriptor, delayed work, chip ID, last charge register, sense resistor, and computed `Qlsb` conversion. `ltc294x_read_regs()` and `ltc294x_write_regs()` implement multi-byte I2C access. Conversion helpers translate between register counts and uAh, accounting for negative sense-resistor orientation. `ltc294x_reset()` sets prescaler, scan/monitor mode, and ALCC disabled. Getters decode charge thresholds/current charge/counter, voltage by chip family, current by sense resistor, and temperature. Setters write charge thresholds and safely update accumulated charge by shutting down the analog section temporarily.

## Control Flow
Probe reads OF match chip type and node name, requires `lltc,resistor-sense`, reads optional `lltc,prescaler-exponent`, computes `Qlsb`, distinguishes LTC2941 versus LTC2942 from status, trims property count by chip capability, registers autocancel delayed work, programs control mode, registers the battery supply, and starts 10-second polling. Suspend cancels delayed work; resume restarts it. Shutdown disables ADC scan for non-LTC2941 devices.

## State and Persistence
The driver caches conversion constants and last observed charge register. Charge thresholds and charge-now writes persist in gauge registers. Polling state is delayed work only; the hardware accumulator continues operating independently.

## Dependencies and Integration Points
It depends on I2C combined transfers and SMBus block writes, OF properties for sense resistor and prescaler, power-supply writable properties, PM sleep hooks, and device compatibles for each LTC294x variant.

## Risks
`ltc294x_get_voltage()` computes from `datar` even if the read failed before returning the error. `of_property_read_u32()` is used for a signed `s32 r_sense`, which makes negative sense orientation questionable through unsigned DT parsing. Current conversion divides by `r_sense`; a zero value is not explicitly rejected. The descriptor name comes from `np->name`, so missing OF would be unsafe in this implementation.

## Test Signals
Validate chip identification, property counts per chip, Qlsb conversion for prescaler and sense resistor values, negative-current orientation, charge threshold and charge-now writes, polling change events, suspend/resume, shutdown ADC disable, and failed I2C read/write propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ltc2941-battery-gauge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ltc4162-l-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/ltc4162-l-charger.c

## Purpose
This I2C/regmap driver supports LTC4162-L, LTC4162-F, LTC4162-S, and LTC4015 charger controllers. It exposes charger status, charge type, health, input telemetry, charge current/voltage limits, input current limit, die temperature, and termination current, plus sysfs controls for raw telemetry, forced telemetry, and ship mode.

## Important APIs, Types, and Functions
`struct ltc4162l_chip_info` provides per-chip names, voltage conversion callbacks, die-temperature callback, current/voltage resolutions, and telemetry-mask bits. `struct ltc4162l_info` stores client, regmap, charger supply, chip info, RSNSB/RSNSI resistor values, and cached cell count. State decoders map charger-state and charge-status registers to power-supply status, charge type, and health. Conversion helpers read VBAT/VCHARGE differently for LTC4162 lithium/LiFePO4/lead-acid, LTC4015 lead-acid encodings, IBAT/IIN through resistor values, input voltage, die temperature, input-current DAC, and termination threshold. Setters program max charge current, max charge voltage, input current target, and C-over-X termination current.

## Control Flow
Probe verifies SMBus word-data support, allocates state, selects chip info from I2C/OF match, initializes a 16-bit little-endian cached regmap, requires nonzero `lltc,rsnsb-micro-ohms` and `lltc,rsnsi-micro-ohms`, optionally seeds cell count from `lltc,cell-count`, duplicates the descriptor to set the chip-specific name, registers the mains supply with sysfs groups, disables limit alerts, enables charger-state and charge-status alerts, and clears pending alerts. SMBus alert callbacks clear alerts and notify the power supply.

## State and Persistence
Cell count is cached after the first successful hardware read or from firmware. Writable properties persist in controller registers. Regmap caches nonvolatile writable registers and treats status registers as volatile. Sysfs writes can force telemetry and arm ship mode; those are direct hardware state changes.

## Dependencies and Integration Points
It depends on I2C SMBus word transactions, regmap with 16-bit little-endian values and maple cache, OF/device properties for sense resistors, SMBus alert support, power-supply writable properties, and per-chip compatible data.

## Risks
The generic `ltc4162l_set_property()` always calls `ltc4162l_set_vcharge()` rather than the chip-info `set_vcharge` callback, so LTC4015 writable charge-voltage behavior may not match its getter/conversion table. Several conversions require a nonzero detected cell count and return `-EBUSY` or invalid values while the chip has not determined cells. Sysfs `arm_ship_mode` is a powerful persistent control. Unit conversions depend directly on correct resistor properties.

## Test Signals
Test all four chip-info paths, chemistry and cell-count conversions, writable current/voltage/input-limit/termination properties, zero and invalid resistor DT values, SMBus alert notification, forced telemetry and ship-mode sysfs behavior, regmap cache/volatile behavior, and the LTC4015 charge-voltage setter path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ltc4162-l-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/macsmc-power.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/macsmc-power.c

## Purpose
This Apple Silicon platform driver exposes battery and AC adapter telemetry from the Apple SMC. It dynamically builds power-supply property lists based on available SMC keys, supports charge behavior controls, estimates energy from charge using a nominal cell voltage, and reacts to SMC power events including critical battery shutdown triggers.

## Important APIs, Types, and Functions
`struct macsmc_power` stores device/SMC pointers, mutable battery and AC descriptors, registered supplies, identity strings, feature flags for charge limit/inhibit/force-discharge mechanisms, cell data, notifier, critical work, and shutdown guards. `macsmc_battery_get_status()` combines SMC keys for charger presence/capability, AC current, full state, charge limits, and no-charge flags. Charge behavior helpers read/write `CH0I`, `CHTE`, or `CH0C`. `macsmc_battery_get_property()` maps many SMC keys to standard battery properties, including manufacture date parsing and BE-swapped `B0RM`. `macsmc_power_critical_work()` initiates hardware-protection or orderly shutdown on low voltage or SMC empty flags. `macsmc_power_event()` maps predicted SMC event IDs to supply changes or critical work.

## Control Flow
Probe gets the parent `apple_smc`, allocates state, sets up autocancel critical work, detects battery and AC presence from fundamental keys, builds battery properties and feature flags, resets charge inhibitors to auto, reads identity strings/cell count, registers battery if possible, builds AC properties based on available keys, registers AC if possible, and registers a blocking notifier with the SMC event chain. Remove unregisters the notifier.

## State and Persistence
Identity strings, feature flags, cell count, nominal voltage, and shutdown guard booleans are cached. The driver writes persistent SMC charge-behavior keys at probe and when userspace changes `CHARGE_BEHAVIOUR`. It does not cache telemetry; most properties read SMC keys live.

## Dependencies and Integration Points
It depends on the Apple SMC MFD API, SMC key naming macros, blocking notifier chain, power-supply charge-behavior support, reboot/hardware-protection APIs, and Apple Silicon firmware key availability. AC and battery registration are independent so one can succeed if the other fails.

## Risks
Event IDs are described as predicted, so notifications may miss or over-report firmware changes. Probe resets optimized charging/inhibitor keys, which changes firmware policy. Critical shutdown logic depends on SMC voltage/empty flags and must avoid duplicate shutdowns. Energy values are approximated from a fixed nominal cell voltage. Dynamic property arrays have hard limits and rely on accurate key probing.

## Test Signals
Test systems with battery only, AC only, and both supplies; key absence on newer firmware; status decisions for no charger, limited charging, BMS busy, full, and inhibited cases; charge-behavior get/set across old and new keys; critical event handling; manufacture date parsing; and notifier cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/macsmc-power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max14577_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max14577_charger.c

## Purpose
This platform driver controls the charger block in Maxim MAX14577 and MAX77836 MFD devices. It initializes safe charger defaults from device-tree data, reports charger/battery status through the power-supply core, and exposes a sysfs knob for the fast-charge timer.

## Important APIs, Types, and Functions
`struct max14577_charger` stores device, parent MFD, registered supply, and charger platform data. `maxim_get_charger_type()` normalizes MUIC charger-type register values across MAX14577 and MAX77836. `max14577_get_charger_state()`, `max14577_get_charge_type()`, `max14577_get_online()`, and `max14577_get_battery_health()` read MFD registers to report status, charge type, online, and health. Initialization helpers program fast-charge timer, constant voltage, EOC current, fast-charge current, charger detect mode, battery charger enable, auto-stop, and OVP threshold. `fast_charge_timer` sysfs show/store maps between hours and register bits.

## Control Flow
Probe allocates state, gets parent MFD data, parses required DT properties (`maxim,constant-uvolt`, `fast-charge-uamp`, `eoc-uamp`, `ovp-uvolt`), initializes charger registers, creates the sysfs file, registers the power supply, and validates compile-time current constants. Remove deletes the sysfs file.

## State and Persistence
The driver persists charger policy in hardware registers at probe and when sysfs changes the fast-charge timer. It does not cache runtime telemetry. Battery presence is always reported as true because the chip lacks a battery-present bit.

## Dependencies and Integration Points
It depends on the parent MAX14577/MAX77836 MFD regmap and register definitions, OF charger node properties, helper tables from `max14577.h`, sysfs, and the power-supply core. The descriptor is named `max14577-charger` and has type `BATTERY` despite reporting charger-like properties.

## Risks
Probe requires all charger DT properties and fails otherwise. Several initialization writes before later validation can leave partial hardware state if a later step fails. Online classification treats downstream ports as offline but several special chargers as online. TODOs note incomplete full, dead-battery, and charger timer handling. Sysfs allows disabling or changing the fast-charge timer after probe.

## Test Signals
Validate DT parsing failures, MAX14577 versus MAX77836 current/EOC mappings, constant voltage gap handling, OVP values, charger type decoding including reserved/dead-battery values, status/health reads, sysfs timer show/store, cleanup on power-supply registration failure, and parent regmap error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max14577_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max14656_charger_detector.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max14656_charger_detector.c

## Purpose
This I2C driver supports the Maxim MAX14656/AL32 USB charger detector. It identifies the attached charger type from status registers, updates the power-supply type dynamically, and reports online/model/manufacturer properties.

## Important APIs, Types, and Functions
`struct max14656_chip` stores the I2C client, detector power supply, mutable descriptor, delayed IRQ work, IRQ number, and online flag. Register helpers perform SMBus byte and block reads/writes. `max14656_hw_init()` verifies vendor ID, enables ADC, configures interrupt polarity/edge behavior and low-power mode, unmasks interrupts, and logs revision. `max14656_irq_worker()` block-reads registers, checks VBUS-valid and charger-type bits, maps charger types through `chg_type_props[]` to `POWER_SUPPLY_TYPE_USB`, `USB_CDP`, `USB_DCP`, or unknown, updates `online`, and notifies the supply.

## Control Flow
Probe requires a valid IRQ and SMBus byte support, allocates state, fills a descriptor named `max14656`, initializes hardware, registers the power supply, sets up autocancel delayed work, requests the IRQ on falling edge, enables IRQ wake, and schedules an initial delayed detection after two seconds. The IRQ schedules detection after 100 ms.

## State and Persistence
The online flag and descriptor type are cached from the latest worker run. Hardware initialization persists interrupt and ADC control settings. There is no writeable power-supply property.

## Dependencies and Integration Points
It depends on I2C SMBus byte/block operations, a valid interrupt line, wake-capable IRQ support, devm delayed work, OF compatible `maxim,max14656`, and the power-supply core.

## Risks
`max14656_irq_worker()` does not check the block-read return value before decoding the buffer, so I2C failures can use stale stack data. The descriptor type is mutated at runtime. `enable_irq_wake()` return value is ignored and there is no remove-time disable. Probe collapses several initialization/register failures into `-ENODEV` or `-EINVAL`, reducing diagnostics.

## Test Signals
Validate vendor/revision ID detection, initial two-second detection, IRQ-triggered 100 ms detection, all charger type mappings, no-VBUS/offline behavior, block-read failure handling, IRQ wake behavior, and property reads for online/model/manufacturer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max14656_charger_detector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max17040_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/max17040_battery.c

## Purpose
This I2C/regmap fuel-gauge driver supports MAX17040, MAX17041, MAX17043, MAX17044, MAX17048, MAX17049, MAX17058, MAX17059, and the MAX77836 battery alias. It reports voltage, capacity, alert threshold, status from suppliers, and optional temperature, with either low-SOC/SOC interrupts or periodic polling.

## Important APIs, Types, and Functions
`struct chip_data` captures chip-specific reset command, VCELL conversion factors, alert support, RCOMP width, and SOC alert capability. `struct max17040_chip` stores client, regmap, work, battery supply, chip data, optional temp IIO channel, cached SOC, alert threshold, double-SOC quirk, and RCOMP value. Helpers reset the chip, program low-SOC and SOC alerts, program RCOMP, convert raw VCELL to microvolts, read SOC/version, parse OF data, and handle SOC-change versus low-SOC alerts. `max17040_get_property()` exposes online/present, voltage, capacity, capacity-alert-min, supplier status, and IIO temperature.

## Control Flow
Probe checks SMBus byte support, initializes a big-endian 16-bit regmap with stride 2, chooses chip ID from I2C or OF data, parses optional `maxim,double-soc`, `maxim,alert-low-soc-level`, and `maxim,rcomp`, gets optional `temp` IIO channel, registers the battery, reads version, resets older MAX17040/41 chips, writes RCOMP, configures low-SOC and SOC alerts if IRQ/capability allow, otherwise starts deferrable polling work. Suspend disables SOC alert or cancels polling and enables IRQ wake if allowed; resume reverses that.

## State and Persistence
The driver caches last SOC to suppress unchanged uevents, low-SOC threshold, quirk state, and RCOMP. Hardware alert thresholds, SOC alert enable, RCOMP, and reset state persist in gauge registers. Polling uses `system_power_efficient_wq`.

## Dependencies and Integration Points
It depends on I2C regmap, OF match data/properties, optional IIO temp channel, power-supply supplier lookup for status, optional IRQ wakeup, PM sleep hooks, and Maxim gauge register semantics.

## Risks
`max17040_get_vcell()`, `max17040_get_soc()`, and alert handling ignore regmap read errors and may report derived values from uninitialized locals. `max17040_set_property()` updates `low_soc_alert` even if the hardware write fails. Older chips are reset during probe, which can disturb accumulated model state. The optional temp channel uses `devm_iio_channel_get()` and treats only `-ENODEV` as absent.

## Test Signals
Test all chip-data conversions, double-SOC threshold bounds, RCOMP length parsing, low-SOC and SOC interrupt handling, fallback polling and uevent suppression, supplier status forwarding, optional temp conversion, suspend/resume wake behavior, MAX17040/41 reset path, and regmap error propagation in property reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/max17040_battery.c -->
